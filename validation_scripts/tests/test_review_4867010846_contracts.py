from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4861791404_contracts as prior_contracts


class TestReview4867010846Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            prior_contracts.TestReview4861791404Contracts().base_v3_spec()
        )

    @staticmethod
    def confirmation_point(effect):
        return {
            "measurable_event_or_metric": "Project Alpha production milestone",
            "interpretation_effect": effect,
        }

    def test_medial_concession_is_removed_without_losing_main_clause(self):
        for effect in (
            "The filing, although late, would strengthen the current demand outlook",
            "The filing, even though delayed, would confirm the adoption thesis",
            "The filing; despite the delay; would weaken the current demand outlook",
        ):
            with self.subTest(effect=effect):
                self.assertTrue(lineage._has_bound_interpretation_effect(effect))
                self.assertTrue(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_leading_concession_main_clause_is_resplit_for_trailing_condition(self):
        for effect in (
            "Although unrelated facts changed, Project Alpha production weakened if the current demand outlook improved",
            "Even though unrelated facts changed, Project Alpha production confirmed unless the adoption thesis changes",
            "Despite unrelated facts changing, Project Alpha capacity weakened until the demand outlook improves",
        ):
            with self.subTest(effect=effect):
                self.assertFalse(lineage._has_bound_interpretation_effect(effect))
                self.assertFalse(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_leading_concession_with_real_main_clause_effect_still_passes(self):
        for effect in (
            "Although unrelated facts changed, the filing would strengthen the current demand outlook",
            "Even though production weakened, the milestone confirmed the adoption thesis",
        ):
            with self.subTest(effect=effect):
                self.assertTrue(lineage._has_bound_interpretation_effect(effect))
                self.assertTrue(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_medial_concession_does_not_hide_later_trailing_condition(self):
        effect = (
            "The filing, although late, Project Alpha production weakened "
            "if the current demand outlook improved"
        )
        self.assertFalse(lineage._has_bound_interpretation_effect(effect))
        self.assertFalse(
            lineage._valid_confirmation_point(self.confirmation_point(effect))
        )

    def test_complete_v3_accepts_real_main_effect_and_rejects_nested_bypass(self):
        valid = self.base_v3_spec()
        valid["next_confirmation_points"] = [self.confirmation_point(
            "The filing, although late, would strengthen the current demand outlook"
        )]
        valid_messages = []
        self.assertTrue(
            lineage.validate_stage_a_v3_override(
                valid, valid["spec_id"], valid_messages
            ),
            valid_messages,
        )

        invalid = self.base_v3_spec()
        invalid["next_confirmation_points"] = [self.confirmation_point(
            "Although unrelated facts changed, Project Alpha production weakened "
            "if the current demand outlook improved"
        )]
        invalid_messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(
                invalid, invalid["spec_id"], invalid_messages
            )
        )
        self.assertTrue(
            any("interpretation effect" in message for message in invalid_messages),
            invalid_messages,
        )


if __name__ == "__main__":
    unittest.main()
