"""Regression coverage for the latest PR #233 semantic-validation review."""

from __future__ import annotations

import copy
import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_review_4840844831_contracts import (
    TestReview4840844831Contracts,
)


class TestReview4841207046FollowupContracts(unittest.TestCase):
    def base_spec(self):
        return TestReview4840844831Contracts().base_spec()

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def test_placeholder_semantic_variants_fail(self):
        for placeholder in (
            "not disclosed",
            "information unavailable",
            "아직 정보 없음",
            "세부 자료 미공개",
        ):
            with self.subTest(placeholder=placeholder):
                spec = copy.deepcopy(self.base_spec())
                for field in lineage.STAGE_A_V3_NARRATIVE_FIELDS:
                    spec[field] = placeholder
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 1)
                self.assertIn("must be item-specific narrative text", output)

    def test_bare_number_is_not_exact_or_measurable_target(self):
        for field, entry in (
            ("evidence_needed_for_stage_b", {
                "source_or_document_class": "SEC filing",
                "exact_claim_or_metric": "99",
            }),
            ("next_confirmation_points", {
                "measurable_event_or_metric": "99",
                "interpretation_effect": "confirm thesis",
            }),
        ):
            with self.subTest(field=field):
                spec = copy.deepcopy(self.base_spec())
                spec[field] = [entry]
                result, _ = self.run_stage_a(spec)
                self.assertEqual(result, 1)

    def test_explicit_year_and_qualified_metric_still_pass(self):
        spec = copy.deepcopy(self.base_spec())
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "SEC filing",
            "exact_claim_or_metric": "2027 revenue",
        }]
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "2027",
            "interpretation_effect": "confirm thesis",
        }]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 0, output)

    def test_source_and_effect_terms_require_complete_word_matches(self):
        invalid_cases = (
            ("evidence_needed_for_stage_b", {
                "source_or_document_class": "unofficial rumor",
                "exact_claim_or_metric": "2027 revenue",
            }),
            ("next_confirmation_points", {
                "measurable_event_or_metric": "2027 revenue",
                "interpretation_effect": "unchanged",
            }),
        )
        for field, entry in invalid_cases:
            with self.subTest(field=field):
                spec = copy.deepcopy(self.base_spec())
                spec[field] = [entry]
                result, _ = self.run_stage_a(spec)
                self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
