from __future__ import annotations

import copy
import unittest

from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4861791404_contracts as v3_contracts
from validation_scripts.tests import test_review_4862131806_contracts as related_contracts


class TestReview4868891584Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            v3_contracts.TestReview4861791404Contracts().base_v3_spec()
        )

    @staticmethod
    def confirmation_point(effect):
        return {
            "measurable_event_or_metric": "Project Alpha production milestone",
            "interpretation_effect": effect,
        }

    def test_dependent_causal_suffix_is_not_a_standalone_effect(self):
        effect = (
            "Project Alpha production weakened because the current demand "
            "outlook strengthened"
        )
        self.assertFalse(lineage._has_bound_interpretation_effect(effect))
        self.assertFalse(lineage._valid_confirmation_point(self.confirmation_point(effect)))

    def test_complete_v3_rejects_dependent_causal_suffix_bypass(self):
        effect = (
            "Project Alpha production weakened because the current demand "
            "outlook strengthened"
        )
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [self.confirmation_point(effect)]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )

    def test_leading_causal_clause_preserves_the_real_main_effect(self):
        effect = (
            "Because Project Alpha production weakened, the current demand "
            "outlook would strengthen"
        )
        self.assertTrue(lineage._has_bound_interpretation_effect(effect))
        self.assertTrue(lineage._valid_confirmation_point(self.confirmation_point(effect)))

    def test_related_accepts_named_financial_and_operating_metrics(self):
        fixture = related_contracts.TestReview4862131806Contracts()
        for assertion in (
            "Project Alpha Q2 EBITDA",
            "Project Alpha FY2026 profit",
            "Project Alpha 2026 capex",
            "Project Alpha 2026 opex",
            "Project Alpha Q2 yield",
            "Project Alpha Q2 throughput",
        ):
            with self.subTest(assertion=assertion):
                fixture._assert_strict_success(assertion)

    def test_financial_roles_without_a_concrete_subject_remain_rejected(self):
        fixture = related_contracts.TestReview4862131806Contracts()
        for assertion in (
            "Q2 EBITDA",
            "FY2026 profit",
            "2026 capex",
        ):
            with self.subTest(assertion=assertion):
                fixture._assert_strict_failure(assertion)


if __name__ == "__main__":
    unittest.main()
