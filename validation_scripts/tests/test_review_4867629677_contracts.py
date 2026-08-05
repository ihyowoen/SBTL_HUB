from __future__ import annotations

import copy
import unittest

from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4861791404_contracts as v3_contracts
from validation_scripts.tests import test_review_4862131806_contracts as related_contracts


class TestReview4867629677Contracts(unittest.TestCase):
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

    def test_provided_and_assuming_conditions_do_not_bind_metric_effects(self):
        for effect in (
            "Project Alpha production weakened provided that the current demand outlook improved",
            "Project Alpha production weakened providing that the current demand outlook improved",
            "Project Alpha production weakened assuming the current demand outlook improved",
            "Project Alpha production weakened assuming that the current demand outlook improved",
        ):
            with self.subTest(effect=effect):
                self.assertFalse(lineage._has_bound_interpretation_effect(effect))
                self.assertFalse(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_leading_provided_condition_keeps_real_main_effect(self):
        effect = (
            "Provided that Project Alpha production improves, "
            "the current demand outlook would strengthen"
        )
        self.assertTrue(lineage._has_bound_interpretation_effect(effect))
        self.assertTrue(
            lineage._valid_confirmation_point(self.confirmation_point(effect))
        )

    def test_complete_v3_rejects_provided_condition_bypass(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [self.confirmation_point(
            "Project Alpha production weakened provided that "
            "the current demand outlook improved"
        )]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(
                spec, spec["spec_id"], messages
            )
        )

    def test_numbered_project_and_program_labels_are_concrete_subjects(self):
        for assertion in (
            "Project 1 Q2 revenue",
            "Program 2 Q2 revenue",
            "Programme 3 FY2026 margin",
            "프로젝트 4 2분기 매출",
            "프로그램 5 2026년 매출",
        ):
            with self.subTest(assertion=assertion):
                self.assertTrue(related.item_specific_lineage_assertion(assertion))

    def test_strict_related_accepts_numbered_project_and_program_labels(self):
        fixture = related_contracts.TestReview4862131806Contracts()
        for assertion in (
            "Project 1 Q2 revenue",
            "Program 2 Q2 revenue",
            "Programme 3 FY2026 margin",
        ):
            with self.subTest(assertion=assertion):
                fixture._assert_strict_success(assertion)

    def test_generic_numbered_owners_do_not_become_concrete_subjects(self):
        fixture = related_contracts.TestReview4862131806Contracts()
        for assertion in (
            "Company 1 Q2 revenue",
            "Issuer 2 Q2 revenue",
            "Entity 3 FY2026 margin",
        ):
            with self.subTest(assertion=assertion):
                self.assertFalse(related.item_specific_lineage_assertion(assertion))
                fixture._assert_strict_failure(assertion)


if __name__ == "__main__":
    unittest.main()
