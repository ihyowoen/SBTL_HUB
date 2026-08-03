from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


related = ROOT / "validation_scripts/related_lifecycle_check.py"
replace_once(
    related,
    """import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any
""",
    """import argparse
import csv
import ipaddress
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
""",
    "add URL parsing imports",
)
replace_once(
    related,
    """    return len(content_tokens) >= minimum_content_tokens


def validate_follow_up_chronology_justification(
""",
    """    return len(content_tokens) >= minimum_content_tokens


def _valid_http_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    text = value.strip()
    try:
        parsed = urlparse(text)
        host = parsed.hostname
    except ValueError:
        return False
    if parsed.scheme not in {\"http\", \"https\"} or not host:
        return False
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        pass
    labels = host.rstrip(\".\").split(\".\")
    if len(labels) < 2:
        return False
    return all(
        bool(re.fullmatch(r\"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\", label))
        for label in labels
    )


def validate_follow_up_chronology_justification(
""",
    "add strict HTTP URL validation",
)
replace_once(
    related,
    """    for url in source_urls:
        if not isinstance(url, str) or not url.strip().startswith((\"https://\", \"http://\")):
            return set(), \"follow-up chronology evidence_source_urls must contain HTTP(S) URLs\"
""",
    """    for url in source_urls:
        if not _valid_http_url(url):
            return set(), (
                \"follow-up chronology evidence_source_urls must contain parseable \"
                \"HTTP(S) URLs with a real host\"
            )
""",
    "validate chronology URL hosts",
)
replace_once(
    related,
    """    if related != dedupe(related):
        errors.append(\"related contains duplicate IDs\")
    for target in related:
        resolved_target = by_id.get(target)
        if resolved_target is card:
            errors.append(\"related contains self-reference\")
        elif resolved_target is None:
            errors.append(f\"dangling related ID: {target}\")
""",
    """    if related != dedupe(related):
        errors.append(\"related contains duplicate IDs\")
    resolved_edge_aliases: dict[int, str] = {}
    for target in related:
        resolved_target = by_id.get(target)
        if resolved_target is card:
            errors.append(\"related contains self-reference\")
        elif resolved_target is None:
            errors.append(f\"dangling related ID: {target}\")
        else:
            resolved_identity = id(resolved_target)
            previous_alias = resolved_edge_aliases.get(resolved_identity)
            if previous_alias is not None:
                errors.append(
                    \"related aliases resolve to duplicate target: \"
                    f\"{previous_alias}, {target}\"
                )
            else:
                resolved_edge_aliases[resolved_identity] = target
""",
    "dedupe resolved Related targets",
)

stage = ROOT / "validation_scripts/stage_lineage_contract_check.py"
replace_once(
    stage,
    """def _contains_generic_target_fragment(value):
    text = _normalized_text(value)
    # Exact evidence targets may legitimately name a concrete residual unknown.
    # Keep generic evidence scaffolding fail-closed while allowing contextual
    # uncertainty that is qualified by a source class and named metric/claim.
    return any(
        fragment in text
        for fragment in STAGE_A_GENERIC_OVERRIDE_FRAGMENTS
        if fragment != 'unknown'
    )
""",
    """def _contains_generic_target_fragment(value):
    text = ' '.join(_normalized_text(value).replace(':', ' ').replace(';', ' ').split())
    if not text:
        return True
    # Match generic evidence scaffolds as complete placeholder semantics, not
    # substrings inside concrete claims such as \"additional data center capacity\".
    patterns = (
        r'(?:more|further) evidence(?: (?:on|for|needed|required)\\b.*)?',
        r'more data(?: (?:on|for|needed|required)\\b.*)?',
        r'additional data(?: (?:on|for|needed|required|to confirm)\\b.*)?',
        r'(?:additional|further) confirmation(?: (?:on|for|needed|required)\\b.*)?',
        r'(?:needs confirmation|confirmation needed|to be confirmed|tbd)',
        r'(?:official source|company material|media report)(?:s)?(?: for confirmation)?',
    )
    return any(re.fullmatch(pattern, text) for pattern in patterns)
""",
    "scope generic evidence matching",
)

test = ROOT / "validation_scripts/tests/test_review_4842310205_contracts.py"
test.write_text('''"""Regression coverage for Codex review 4842310205."""\n\nfrom __future__ import annotations\n\nimport copy\nimport io\nimport sys\nimport unittest\nfrom contextlib import redirect_stdout\nfrom pathlib import Path\n\nsys.path.insert(0, str(Path(__file__).resolve().parents[1]))\n\nfrom validation_scripts import related_lifecycle_check as related\nfrom validation_scripts import stage_lineage_contract_check as lineage\nfrom validation_scripts.tests.test_review_4840844831_contracts import (\n    TestReview4840844831Contracts,\n)\nfrom validation_scripts.tests.test_review_4841890896_contracts import (\n    TestReview4841890896Contracts,\n)\n\n\nclass TestReview4842310205Contracts(unittest.TestCase):\n    def base_spec(self):\n        return TestReview4840844831Contracts().base_spec()\n\n    def run_stage_a(self, spec):\n        stream = io.StringIO()\n        with redirect_stdout(stream):\n            result = lineage.check_stage_a({\"strict_passed_spec\": [spec]})\n        return result, stream.getvalue()\n\n    def test_concrete_additional_data_center_target_passes(self):\n        spec = copy.deepcopy(self.base_spec())\n        spec[\"evidence_needed_for_stage_b\"] = [{\n            \"source_or_document_class\": \"SEC filing\",\n            \"exact_claim_or_metric\": \"additional data center capacity for Project Alpha\",\n        }]\n        result, output = self.run_stage_a(spec)\n        self.assertEqual(result, 0, output)\n\n    def test_generic_additional_data_placeholder_still_fails(self):\n        spec = copy.deepcopy(self.base_spec())\n        spec[\"evidence_needed_for_stage_b\"] = [{\n            \"source_or_document_class\": \"SEC filing\",\n            \"exact_claim_or_metric\": \"additional data needed\",\n        }]\n        result, output = self.run_stage_a(spec)\n        self.assertEqual(result, 1)\n        self.assertIn(\"evidence_needed_for_stage_b entries must identify\", output)\n\n    def test_placeholder_chronology_url_does_not_waive_inversion(self):\n        parent, child = TestReview4841890896Contracts().provisional_cards(True)\n        child[\"related_lineage\"][\"follow_up_date_precedes_predecessor_justification\"][\"evidence_source_urls\"] = [\"https://...\"]\n        by_id = {\"PARENT_FINAL\": parent, \"CHILD_FINAL\": child}\n        provisional_by_id, ambiguous = related.build_provisional_target_index([parent, child])\n        errors, _ = related.check_card(\n            child,\n            by_id,\n            require_contract=True,\n            allow_provisional_related=True,\n            provisional_by_id=provisional_by_id,\n            ambiguous_provisional_ids=ambiguous,\n        )\n        self.assertIn(\n            \"follow-up chronology evidence_source_urls must contain parseable HTTP(S) URLs with a real host\",\n            errors,\n        )\n        self.assertIn(\n            \"follow-up date precedes provisional predecessor PARENT_SPEC\",\n            errors,\n        )\n\n    def test_http_scheme_without_host_is_rejected(self):\n        self.assertFalse(related._valid_http_url(\"https://\"))\n        self.assertFalse(related._valid_http_url(\"https://...\"))\n        self.assertTrue(related._valid_http_url(\"https://example.com/filing\"))\n\n    def test_aliases_resolving_to_same_related_card_are_rejected(self):\n        parent = {\n            \"id\": \"PARENT_FINAL\",\n            \"card_id\": \"PARENT_ALIAS\",\n            \"date\": \"2026-08-01\",\n        }\n        child = {\n            \"id\": \"CHILD_FINAL\",\n            \"date\": \"2026-08-02\",\n            \"related\": [\"PARENT_FINAL\", \"PARENT_ALIAS\"],\n            \"related_lineage\": {\n                \"status\": \"PASS\",\n                \"relation_type\": \"program_lineage\",\n                \"related_ids\": [\"PARENT_FINAL\", \"PARENT_ALIAS\"],\n                \"reason\": \"Both aliases refer to the same intended program predecessor.\",\n                \"same_event_checked\": True,\n                \"earliest_same_event_date_checked\": True,\n            },\n        }\n        by_id = {\n            \"PARENT_FINAL\": parent,\n            \"PARENT_ALIAS\": parent,\n            \"CHILD_FINAL\": child,\n        }\n        errors, _ = related.check_card(child, by_id, require_contract=True)\n        self.assertIn(\n            \"related aliases resolve to duplicate target: PARENT_FINAL, PARENT_ALIAS\",\n            errors,\n        )\n\n\nif __name__ == \"__main__\":\n    unittest.main()\n''', encoding="utf-8")
