from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_or_assert(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    old_count = text.count(old)
    new_count = text.count(new)
    if old_count == 1 and new_count == 0:
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        return
    if old_count == 0 and new_count == 1:
        return
    raise SystemExit(
        f"{label}: expected one old or one applied state, found old={old_count}, new={new_count}"
    )


related = ROOT / "validation_scripts/related_lifecycle_check.py"
related_text = related.read_text(encoding="utf-8")
if "parsed.port" not in related_text:
    raise SystemExit("validate chronology URL port: applied state missing")

replace_or_assert(
    related,
    '''                    "ambiguous provisional related ID",
                    "dangling provisional related ID",
                ))
''',
    '''                    "ambiguous provisional related ID",
                    "dangling provisional related ID",
                    "provisional related aliases resolve to duplicate target",
                ))
''',
    "invalidate duplicate resolved provisional aliases",
)
related_text = related.read_text(encoding="utf-8")
for required in (
    "resolved_provisional_aliases: dict[int, str] = {}",
    "provisional related aliases resolve to duplicate target:",
):
    if required not in related_text:
        raise SystemExit(f"provisional alias dedupe: missing applied state {required}")

stage = ROOT / "validation_scripts/stage_lineage_contract_check.py"
stage_text = stage.read_text(encoding="utf-8")
if "Normalize ordinary punctuation" not in stage_text or "re.sub" not in stage_text:
    raise SystemExit("generic target punctuation normalization: applied state missing")

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
        self.assertIn(
            "program_lineage requires at least one final or allowed provisional related ID",
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

original_workflow = '''name: Workflow contract validation

on:
  pull_request:
    paths:
      - "docs/RELATED_LIFECYCLE_CONTRACT.md"
      - "docs/SOURCE_AUDIT_CONTRACT.md"
      - "docs/llm_prompts/v1/**"
      - "validation_data/source_owner_registry.json"
      - "validation_scripts/**"
      - "scripts/lean_cards.mjs"
      - ".github/workflows/lean-cards.yml"
      - ".github/workflows/workflow-contract-validation.yml"
  push:
    branches:
      - agent/workflow-contract-related-source-audit
    paths:
      - "docs/RELATED_LIFECYCLE_CONTRACT.md"
      - "docs/SOURCE_AUDIT_CONTRACT.md"
      - "docs/llm_prompts/v1/**"
      - "validation_data/source_owner_registry.json"
      - "validation_scripts/**"
      - "scripts/lean_cards.mjs"
      - ".github/workflows/lean-cards.yml"
      - ".github/workflows/workflow-contract-validation.yml"

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Compile validators
        run: python -m compileall -q validation_scripts

      - name: Run workflow-contract and exporter regression tests
        run: python -m unittest discover -s validation_scripts/tests -v

      - name: Verify prompt overlays
        run: python validation_scripts/apply_prompt_contract_overlays.py --check
'''
(ROOT / ".github/workflows/workflow-contract-validation.yml").write_text(
    original_workflow,
    encoding="utf-8",
)
(ROOT / ".github/workflows/apply-pr233-review-4842556549.yml").unlink(missing_ok=True)
Path(__file__).unlink()
