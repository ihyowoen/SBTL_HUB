"""Regression coverage for Codex review 4842187150."""

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


class TestReview4842187150Contracts(unittest.TestCase):
    def base_spec(self):
        return TestReview4840844831Contracts().base_spec()

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def test_structured_contextual_unknown_evidence_target_passes(self):
        spec = copy.deepcopy(self.base_spec())
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "SEC filing",
            "exact_claim_or_metric": "named customer volume remains unknown",
        }]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 0, output)

    def test_free_text_contextual_unknown_evidence_target_passes(self):
        spec = copy.deepcopy(self.base_spec())
        spec["evidence_needed_for_stage_b"] = [
            "SEC filing named customer volume remains unknown"
        ]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 0, output)

    def test_generic_evidence_scaffolding_still_fails(self):
        spec = copy.deepcopy(self.base_spec())
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "SEC filing",
            "exact_claim_or_metric": "more evidence on adoption",
        }]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn("evidence_needed_for_stage_b entries must identify", output)

    def run_provisional_card(self, parent, child):
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

    def test_chronology_exception_rejected_for_program_lineage(self):
        parent, child = TestReview4841890896Contracts().provisional_cards(True)
        child["related_lineage"]["relation_type"] = "program_lineage"
        errors, _ = self.run_provisional_card(parent, child)
        self.assertIn(
            "follow-up chronology justification is only valid for an inverted distinct_follow_up",
            errors,
        )

    def test_chronology_exception_rejected_without_inversion(self):
        parent, child = TestReview4841890896Contracts().provisional_cards(True)
        child["date"] = "2026-08-11"
        errors, _ = self.run_provisional_card(parent, child)
        self.assertIn(
            "follow-up chronology justification requires at least one covered date inversion",
            errors,
        )

    def test_chronology_exception_for_covered_inversion_still_passes(self):
        errors, warnings = TestReview4841890896Contracts().run_provisional(True)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])


if __name__ == "__main__":
    unittest.main()
