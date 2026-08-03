"""Regression coverage for the latest unresolved PR233 review threads."""

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


class TestLatestPR233ReviewContracts(unittest.TestCase):
    def base_spec(self):
        return TestReview4840844831Contracts().base_spec()

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def test_invalid_and_out_of_range_url_ports_are_rejected(self):
        self.assertFalse(related._valid_http_url("https://example.com:bad/filing"))
        self.assertFalse(related._valid_http_url("https://example.com:99999/filing"))
        self.assertTrue(related._valid_http_url("https://example.com:443/filing"))

    def test_provisional_aliases_resolving_to_same_target_are_rejected(self):
        parent = {
            "id": "PARENT_FINAL",
            "draft_id": "PARENT_DRAFT",
            "source_spec_id": "PARENT_SPEC",
            "date": "2026-08-01",
        }
        child = {
            "id": "CHILD_FINAL",
            "date": "2026-08-02",
            "related": [],
            "related_candidate_spec_ids": ["PARENT_DRAFT", "PARENT_SPEC"],
            "related_lineage": {
                "status": "PASS",
                "relation_type": "program_lineage",
                "related_ids": [],
                "related_candidate_spec_ids": ["PARENT_DRAFT", "PARENT_SPEC"],
                "reason": "Both aliases identify the same predecessor program.",
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

    def test_terminal_punctuation_does_not_hide_generic_target(self):
        for value in ("additional data.", "more evidence.", "confirmation needed!"):
            spec = copy.deepcopy(self.base_spec())
            spec["evidence_needed_for_stage_b"] = [{
                "source_or_document_class": "SEC filing",
                "exact_claim_or_metric": value,
            }]
            result, output = self.run_stage_a(spec)
            self.assertEqual(result, 1, (value, output))

    def test_concrete_additional_data_target_still_passes(self):
        spec = copy.deepcopy(self.base_spec())
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "SEC filing",
            "exact_claim_or_metric": "additional data center capacity for Project Alpha",
        }]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 0, output)


if __name__ == "__main__":
    unittest.main()
