from __future__ import annotations

import copy
import unittest

from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4861791404_contracts as v3_contracts
from validation_scripts.tests import test_review_4862131806_contracts as related_contracts


class TestReview4868539997Contracts(unittest.TestCase):
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

    def test_conditional_on_and_dependent_on_do_not_bind_dependent_effects(self):
        for effect in (
            "Project Alpha production weakened conditional on the current demand outlook strengthened",
            "Project Alpha production weakened dependent on the current demand outlook strengthened",
        ):
            with self.subTest(effect=effect):
                self.assertFalse(lineage._has_bound_interpretation_effect(effect))
                self.assertFalse(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_complete_v3_rejects_conditional_binding_bypasses(self):
        for effect in (
            "Project Alpha production weakened conditional on the current demand outlook strengthened",
            "Project Alpha production weakened dependent on the current demand outlook strengthened",
        ):
            with self.subTest(effect=effect):
                spec = self.base_v3_spec()
                spec["next_confirmation_points"] = [self.confirmation_point(effect)]
                messages = []
                self.assertFalse(
                    lineage.validate_stage_a_v3_override(
                        spec, spec["spec_id"], messages
                    )
                )

    def test_leading_conditional_phrases_preserve_real_main_effects(self):
        for effect in (
            "Conditional on Project Alpha production improving, "
            "the current demand outlook would strengthen",
            "Dependent on Project Alpha production improving, "
            "the current demand outlook would strengthen",
        ):
            with self.subTest(effect=effect):
                self.assertTrue(lineage._has_bound_interpretation_effect(effect))
                self.assertTrue(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_named_nominal_execution_anchors_are_item_specific(self):
        for assertion in (
            "Project Alpha launch",
            "Project Alpha start",
            "Project Alpha award",
            "프로젝트 알파 출시",
            "프로젝트 알파 착수",
            "프로젝트 알파 수주",
        ):
            with self.subTest(assertion=assertion):
                self.assertTrue(related.item_specific_lineage_assertion(assertion))

    def test_strict_related_accepts_named_nominal_execution_anchors(self):
        fixture = related_contracts.TestReview4862131806Contracts()
        for assertion in (
            "Project Alpha launch",
            "Project Alpha start",
            "Project Alpha award",
        ):
            with self.subTest(assertion=assertion):
                fixture._assert_strict_success(assertion)

    def test_bare_execution_role_words_remain_rejected(self):
        fixture = related_contracts.TestReview4862131806Contracts()
        for assertion in ("launch", "start", "award"):
            with self.subTest(assertion=assertion):
                self.assertFalse(related.item_specific_lineage_assertion(assertion))
                fixture._assert_strict_failure(assertion)


if __name__ == "__main__":
    unittest.main()
