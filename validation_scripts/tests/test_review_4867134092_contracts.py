from __future__ import annotations

import copy
import unittest

from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4861791404_contracts as v3_contracts
from validation_scripts.tests import test_review_4862131806_contracts as related_contracts


class TestReview4867134092Contracts(unittest.TestCase):
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

    def test_korean_suffix_dependent_clause_keeps_following_main_clause(self):
        cases = (
            (
                "프로젝트 알파 생산이 약화되었음에도 불구하고, 현재 수요 전망은 강화된다",
                "현재 수요 전망은 강화된다",
            ),
            (
                "프로젝트 알파 생산이 약화된 경우, 현재 수요 전망은 강화된다",
                "현재 수요 전망은 강화된다",
            ),
            (
                "프로젝트 알파 생산이 약화되지 않으면; 현재 수요 전망은 강화된다",
                "현재 수요 전망은 강화된다",
            ),
        )
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(
                    expected,
                    lineage._independent_clause_for_conditional_or_concessive(value),
                )

    def test_korean_suffix_concession_with_real_outlook_effect_passes(self):
        effect = (
            "프로젝트 알파 생산이 약화되었음에도 불구하고, "
            "현재 수요 전망은 강화된다"
        )
        self.assertTrue(lineage._has_bound_interpretation_effect(effect))
        self.assertTrue(
            lineage._valid_confirmation_point(self.confirmation_point(effect))
        )

    def test_korean_suffix_main_clause_is_resplit_for_trailing_condition(self):
        effect = (
            "프로젝트 알파 생산이 약화된 경우, "
            "Project Beta production weakened if the current demand outlook improved"
        )
        self.assertFalse(lineage._has_bound_interpretation_effect(effect))
        self.assertFalse(
            lineage._valid_confirmation_point(self.confirmation_point(effect))
        )

    def test_complete_v3_accepts_korean_suffix_main_effect(self):
        spec = self.base_v3_spec()
        effect = (
            "프로젝트 알파 생산이 약화되었음에도 불구하고, "
            "현재 수요 전망은 강화된다"
        )
        spec["next_confirmation_points"] = [self.confirmation_point(effect)]
        messages = []
        self.assertTrue(
            lineage.validate_stage_a_v3_override(
                spec, spec["spec_id"], messages
            ),
            messages,
        )

    def test_plural_related_roles_are_normalized(self):
        fixture = related_contracts.TestReview4862131806Contracts()
        for assertion in (
            "Project Alpha Q2 margins",
            "Project Alpha Q2 costs",
            "Project Alpha Q2 volumes",
            "Project Alpha Q2 capacities",
            "Project Alpha Q2 forecasts",
        ):
            with self.subTest(assertion=assertion):
                fixture._assert_strict_success(assertion)

    def test_plural_roles_do_not_create_generic_subjects(self):
        fixture = related_contracts.TestReview4862131806Contracts()
        for assertion in (
            "Q2 margins",
            "official Q2 costs",
            "companies' Q2 volumes",
        ):
            with self.subTest(assertion=assertion):
                fixture._assert_strict_failure(assertion)


if __name__ == "__main__":
    unittest.main()
