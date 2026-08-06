from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4861791404_contracts as v3_contracts


class TestReview4869541592Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            v3_contracts.TestReview4861791404Contracts().base_v3_spec()
        )

    def ordinary_v3_spec(self):
        spec = self.base_v3_spec()
        spec["format_risk_tags"] = []
        spec["anchor_classes"] = ["data_financial_anchor"]
        spec["execution_anchor_type"] = None
        spec["execution_anchor_strength"] = None
        return spec

    def test_ordinary_candidate_accepts_complete_v3_override(self):
        spec = self.ordinary_v3_spec()
        messages = []
        lineage.validate_stage_a_spec(spec, 0, messages)
        self.assertEqual([], messages)

    def test_ordinary_candidate_rejects_dual_execution_and_v3_routes(self):
        spec = self.ordinary_v3_spec()
        spec["execution_anchor_type"] = "official_filing"
        spec["execution_anchor_strength"] = "strong"
        messages = []
        lineage.validate_stage_a_spec(spec, 0, messages)
        self.assertTrue(
            any(
                "exactly one complete execution or v3_non_execution path" in message
                for message in messages
            ),
            messages,
        )

    def test_ordinary_candidate_rejects_incomplete_v3_override(self):
        spec = self.ordinary_v3_spec()
        spec["changed_judgment"] = ""
        messages = []
        lineage.validate_stage_a_spec(spec, 0, messages)
        self.assertTrue(
            any(
                "incomplete V3 override package missing changed_judgment" in message
                for message in messages
            ),
            messages,
        )

    def test_since_period_modifier_preserves_main_effect(self):
        self.assertTrue(
            lineage._has_bound_interpretation_effect(
                "The results since 2025 would strengthen the current demand outlook"
            )
        )

    def test_when_reduced_status_modifier_preserves_main_effect(self):
        self.assertTrue(
            lineage._has_bound_interpretation_effect(
                "The filing when complete would strengthen the current demand outlook"
            )
        )

    def test_since_and_when_real_dependent_clauses_remain_excluded(self):
        for value in (
            "Project Alpha production weakened since the current demand outlook improved",
            "Project Alpha production weakened when the current demand outlook improved",
        ):
            with self.subTest(value=value):
                self.assertFalse(lineage._has_bound_interpretation_effect(value))

    def test_leading_since_and_when_clauses_preserve_independent_effect(self):
        for value in (
            "Since Project Alpha production improved, the current demand outlook would strengthen",
            "When Project Alpha production improves, the current demand outlook may strengthen",
        ):
            with self.subTest(value=value):
                self.assertTrue(lineage._has_bound_interpretation_effect(value))


if __name__ == "__main__":
    unittest.main()
