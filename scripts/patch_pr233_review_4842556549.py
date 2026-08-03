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
    '''    try:
        parsed = urlparse(text)
        host = parsed.hostname
    except ValueError:
        return False
    if parsed.scheme not in {"http", "https"} or not host:
        return False
''',
    '''    try:
        parsed = urlparse(text)
        host = parsed.hostname
        port = parsed.port
    except ValueError:
        return False
    if parsed.scheme not in {"http", "https"} or not host:
        return False
    if port is not None and not (1 <= port <= 65535):
        return False
''',
    "validate chronology URL port",
)
replace_once(
    related,
    '''    valid_provisional_edge = False
    resolved_provisional_targets: list[tuple[str, dict[str, Any]]] = []
    if allow_provisional_related and provisional:
''',
    '''    valid_provisional_edge = False
    resolved_provisional_targets: list[tuple[str, dict[str, Any]]] = []
    resolved_provisional_aliases: dict[int, str] = {}
    if allow_provisional_related and provisional:
''',
    "track provisional target identities",
)
replace_once(
    related,
    '''                else:
                    resolved_provisional_targets.append((target, resolved_target))
            valid_provisional_edge = bool(normalized_provisional) and not any(
                message.startswith((
                    "related_candidate_spec_ids",
                    "ambiguous provisional related ID",
                    "dangling provisional related ID",
                ))
''',
    '''                else:
                    resolved_identity = id(resolved_target)
                    previous_alias = resolved_provisional_aliases.get(resolved_identity)
                    if previous_alias is not None:
                        errors.append(
                            "provisional related aliases resolve to duplicate target: "
                            f"{previous_alias}, {target}"
                        )
                    else:
                        resolved_provisional_aliases[resolved_identity] = target
                        resolved_provisional_targets.append((target, resolved_target))
            valid_provisional_edge = bool(normalized_provisional) and not any(
                message.startswith((
                    "related_candidate_spec_ids",
                    "ambiguous provisional related ID",
                    "dangling provisional related ID",
                    "provisional related aliases resolve to duplicate target",
                ))
''',
    "deduplicate resolved provisional targets",
)

stage = ROOT / "validation_scripts/stage_lineage_contract_check.py"
replace_once(
    stage,
    '''def _contains_generic_target_fragment(value):
    text = ' '.join(_normalized_text(value).replace(':', ' ').replace(';', ' ').split())
    if not text:
        return True
''',
    '''def _contains_generic_target_fragment(value):
    text = ' '.join(_normalized_text(value).replace(':', ' ').replace(';', ' ').split())
    text = re.sub(r'[\\s\\.,!?;:。！？，]+$', '', text)
    if not text:
        return True
''',
    "normalize terminal punctuation in generic targets",
)

test = ROOT / "validation_scripts/tests/test_review_4842556549_contracts.py"
test.write_text('''"""Regression coverage for Codex review 4842556549.

The suite validates URL authorities including ports, deduplicates provisional
aliases after resolution, and normalizes punctuation before generic-target
matching.
"""

from __future__ import annotations

import copy
import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_review_4840844831_contracts import (
    TestReview4840844831Contracts,
)
from validation_scripts.tests.test_review_4841890896_contracts import (
    TestReview4841890896Contracts,
)


class TestReview4842556549Contracts(unittest.TestCase):
    def base_spec(self):
        return TestReview4840844831Contracts().base_spec()

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def test_invalid_or_out_of_range_ports_are_rejected(self):
        self.assertFalse(related._valid_http_url("https://example.com:bad/filing"))
        self.assertFalse(related._valid_http_url("https://example.com:99999/filing"))
        self.assertTrue(related._valid_http_url("https://example.com:8443/filing"))

    def test_invalid_port_does_not_waive_chronology_inversion(self):
        parent, child = TestReview4841890896Contracts().provisional_cards(True)
        justification = child["related_lineage"][
            "follow_up_date_precedes_predecessor_justification"
        ]
        justification["evidence_source_urls"] = ["https://example.com:bad/filing"]
        by_id = {"PARENT_FINAL": parent, "CHILD_FINAL": child}
        provisional_by_id, ambiguous = related.build_provisional_target_index([parent, child])
        errors, _ = related.check_card(
            child,
            by_id,
            require_contract=True,
            allow_provisional_related=True,
            provisional_by_id=provisional_by_id,
            ambiguous_provisional_ids=ambiguous,
        )
        self.assertIn(
            "follow-up chronology evidence_source_urls must contain parseable HTTP(S) URLs with a real host",
            errors,
        )
        self.assertIn(
            "follow-up date precedes provisional predecessor PARENT_SPEC",
            errors,
        )

    def test_provisional_aliases_resolving_to_same_target_are_rejected(self):
        parent = {
            "id": "PARENT_FINAL",
            "draft_id": "PARENT_DRAFT",
            "source_spec_id": "PARENT_SPEC",
            "date": "2026-08-01",
        }
        child = {
            "id": "CHILD_FINAL",
            "draft_id": "CHILD_DRAFT",
            "date": "2026-08-02",
            "related": [],
            "related_candidate_spec_ids": ["PARENT_DRAFT", "PARENT_SPEC"],
            "related_lineage": {
                "status": "PASS",
                "relation_type": "program_lineage",
                "related_ids": [],
                "related_candidate_spec_ids": ["PARENT_DRAFT", "PARENT_SPEC"],
                "reason": "Both provisional aliases refer to the same predecessor.",
                "same_event_checked": True,
                "earliest_same_event_date_checked": True,
            },
        }
        by_id = {"PARENT_FINAL": parent, "CHILD_FINAL": child}
        provisional_by_id, ambiguous = related.build_provisional_target_index([parent, child])
        errors, _ = related.check_card(
            child,
            by_id,
            require_contract=True,
            allow_provisional_related=True,
            provisional_by_id=provisional_by_id,
            ambiguous_provisional_ids=ambiguous,
        )
        self.assertIn(
            "provisional related aliases resolve to duplicate target: PARENT_DRAFT, PARENT_SPEC",
            errors,
        )

    def test_generic_targets_with_terminal_punctuation_fail(self):
        for target in ("additional data.", "more evidence.", "confirmation needed,"):
            with self.subTest(target=target):
                spec = copy.deepcopy(self.base_spec())
                spec["evidence_needed_for_stage_b"] = [{
                    "source_or_document_class": "SEC filing",
                    "exact_claim_or_metric": target,
                }]
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 1)
                self.assertIn("evidence_needed_for_stage_b entries must identify", output)

    def test_concrete_target_with_terminal_punctuation_passes(self):
        spec = copy.deepcopy(self.base_spec())
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "SEC filing",
            "exact_claim_or_metric": "additional data center capacity for Project Alpha.",
        }]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 0, output)


if __name__ == "__main__":
    unittest.main()
''', encoding="utf-8")
