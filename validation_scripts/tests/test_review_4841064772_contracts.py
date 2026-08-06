from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_review_4840844831_contracts import (
    TestReview4840844831Contracts,
)

# Locks the semantic-type and concise structured-target regressions from review 4841064772.


class TestReview4841064772Contracts(unittest.TestCase):
    def base_spec(self):
        return TestReview4840844831Contracts().base_spec()

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def test_every_narrative_field_requires_item_specific_string(self):
        for field in lineage.STAGE_A_V3_NARRATIVE_FIELDS:
            with self.subTest(field=field):
                spec = copy.deepcopy(self.base_spec())
                spec[field] = False
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 1)
                self.assertIn(f"{field} must be item-specific narrative text", output)

    def test_unrelated_container_is_not_narrative_content(self):
        spec = copy.deepcopy(self.base_spec())
        spec["changed_judgment"] = {"status": "present"}
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn("changed_judgment must be item-specific narrative text", output)

    def test_baseline_expectation_changed_requires_item_specific_narrative(self):
        for invalid_value in (True, False, 0):
            with self.subTest(invalid_value=invalid_value):
                spec = copy.deepcopy(self.base_spec())
                spec["baseline_expectation_changed"] = invalid_value
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 1)
                self.assertIn(
                    "baseline_expectation_changed must be item-specific narrative text",
                    output,
                )

    def test_concise_structured_evidence_targets_pass(self):
        targets = (
            {
                "source_or_document_class": "SEC filing",
                "exact_claim_or_metric": "Project Alpha 2027 revenue",
            },
            {
                "source_or_document_class": "금감원 공시",
                "exact_claim_or_metric": "알파 프로젝트 2027년 매출",
            },
        )
        for target in targets:
            with self.subTest(target=target):
                spec = copy.deepcopy(self.base_spec())
                spec["evidence_needed_for_stage_b"] = [target]
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 0, output)

    def test_generic_structured_target_still_fails(self):
        spec = copy.deepcopy(self.base_spec())
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "official source",
            "exact_claim_or_metric": "more evidence",
        }]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn("source/document class and an exact claim", output)

    def test_concise_structured_confirmation_point_passes(self):
        spec = copy.deepcopy(self.base_spec())
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "Project Alpha 2027 revenue",
            "interpretation_effect": "confirm thesis",
        }]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 0, output)


if __name__ == "__main__":
    unittest.main()
