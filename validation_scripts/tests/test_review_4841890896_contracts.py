"""Regression coverage for Codex review 4841890896.

The suite preserves substantive uncertainty language while keeping placeholder
text fail-closed, and permits only target-specific evidence-backed chronology
exceptions for final or provisional predecessor edges.
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


class TestReview4841890896Contracts(unittest.TestCase):
    def base_spec(self):
        return TestReview4840844831Contracts().base_spec()

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def test_contextual_unknown_in_uncertainty_narrative_passes(self):
        spec = copy.deepcopy(self.base_spec())
        spec["remaining_uncertainty"] = (
            "The named customer's volume remains unknown pending the August filing."
        )
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 0, output)

    def test_placeholder_only_unknown_still_fails(self):
        spec = copy.deepcopy(self.base_spec())
        spec["remaining_uncertainty"] = "unknown"
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn("must be item-specific narrative text", output)

    def provisional_cards(self, with_exception: bool):
        parent = {
            "id": "PARENT_FINAL",
            "draft_id": "PARENT_SPEC",
            "date": "2026-08-10",
        }
        lineage_obj = {
            "status": "PASS",
            "relation_type": "distinct_follow_up",
            "related_ids": [],
            "related_candidate_spec_ids": ["PARENT_SPEC"],
            "reason": "The retrospective finding changes the judgment on the same project.",
            "fresh_follow_up_anchor_class": "data_financial_anchor",
            "fresh_follow_up_anchor": "The filing retrospectively identifies the earlier operating event.",
            "incremental_fact_vs_predecessor": "The filing discloses a previously unknown customer-volume change.",
            "changed_judgment_vs_predecessor": "The project scale assessment is now lower.",
            "same_event_checked": True,
            "earliest_same_event_date_checked": True,
        }
        if with_exception:
            lineage_obj["follow_up_date_precedes_predecessor_justification"] = {
                "applied": True,
                "predecessor_identifiers": ["PARENT_SPEC"],
                "representative_date_basis": "The card date represents the operating event disclosed retrospectively.",
                "reason": "The later filing creates the distinct changed judgment even though the represented operating event occurred earlier.",
                "evidence_source_urls": ["https://example.com/filing"],
            }
        child = {
            "id": "CHILD_FINAL",
            "draft_id": "CHILD_SPEC",
            "date": "2026-08-01",
            "related": [],
            "related_candidate_spec_ids": ["PARENT_SPEC"],
            "related_lineage": lineage_obj,
        }
        return parent, child

    def run_provisional(self, with_exception: bool):
        parent, child = self.provisional_cards(with_exception)
        by_id = {"PARENT_FINAL": parent, "CHILD_FINAL": child}
        provisional_by_id, ambiguous = related.build_provisional_target_index([parent, child])
        return related.check_card(
            child,
            by_id,
            require_contract=True,
            allow_provisional_related=True,
            provisional_by_id=provisional_by_id,
            ambiguous_provisional_ids=ambiguous,
        )

    def test_provisional_date_inversion_without_justification_fails(self):
        errors, _ = self.run_provisional(False)
        self.assertIn(
            "follow-up date precedes provisional predecessor PARENT_SPEC",
            errors,
        )

    def test_evidence_backed_provisional_chronology_exception_passes(self):
        errors, warnings = self.run_provisional(True)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_malformed_chronology_exception_does_not_waive_invariant(self):
        parent, child = self.provisional_cards(True)
        child["related_lineage"]["follow_up_date_precedes_predecessor_justification"]["evidence_source_urls"] = []
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
            "follow-up chronology justification requires evidence_source_urls[]",
            errors,
        )
        self.assertIn(
            "follow-up date precedes provisional predecessor PARENT_SPEC",
            errors,
        )


if __name__ == "__main__":
    unittest.main()
