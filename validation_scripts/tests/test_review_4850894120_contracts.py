from __future__ import annotations

# Regression lock for review 4850894120.
import copy
import unittest

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4850764924_contracts as prior_contracts


class TestReview4850894120Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            prior_contracts.TestReview4850764924Contracts().base_v3_spec()
        )

    def confirmation_point(self, effect):
        return {
            "measurable_event_or_metric": "Project Alpha production milestone",
            "interpretation_effect": effect,
        }

    def test_conjunctions_inside_qualified_interpretation_objects_pass(self):
        for effect in (
            "The outlook for Project Alpha revenue and margin would weaken",
            "The demand outlook regarding Project Alpha EBITDA or margin would weaken",
        ):
            with self.subTest(effect=effect):
                self.assertTrue(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_unqualified_or_reported_conjunction_bridges_remain_rejected(self):
        for effect in (
            "The outlook and Project Alpha revenue would weaken",
            "The outlook report says Project Alpha revenue and margin increased",
        ):
            with self.subTest(effect=effect):
                self.assertFalse(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_consecutive_parentheticals_do_not_hide_measurement_subject(self):
        for effect in (
            "Project Alpha production, in the northern facility, under the Beta program, was weakened under the current demand outlook",
            "Project Alpha production, in the northern facility, under the Beta program, was confirmed under the current demand outlook",
        ):
            with self.subTest(effect=effect):
                self.assertFalse(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_complete_v3_spec_rejects_consecutive_parenthetical_bypass(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [self.confirmation_point(
            "Project Alpha production, in the northern facility, under the Beta program, was weakened under the current demand outlook"
        )]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("interpretation effect" in message for message in messages),
            messages,
        )

    def test_consecutive_parentheticals_preserve_valid_transitive_effect(self):
        self.assertTrue(
            lineage._valid_confirmation_point(self.confirmation_point(
                "The filing, from the northern facility, under the Beta program, weakened the current demand outlook"
            ))
        )

    def test_causal_clauses_do_not_bind_metric_effects_to_later_outlook(self):
        for effect in (
            "Project Alpha production weakened because the current demand outlook improved",
            "Project Alpha production weakened as the current demand outlook improved",
            "Project Alpha production weakened since the current demand outlook improved",
        ):
            with self.subTest(effect=effect):
                self.assertFalse(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_complete_v3_spec_rejects_causal_clause_bypass(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [self.confirmation_point(
            "Project Alpha production weakened because the current demand outlook improved"
        )]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("interpretation effect" in message for message in messages),
            messages,
        )

    def test_valid_effect_before_causal_detail_remains_valid(self):
        self.assertTrue(
            lineage._valid_confirmation_point(self.confirmation_point(
                "The filing weakened the current demand outlook because production declined"
            ))
        )

    def test_outlook_parenthetical_does_not_hide_measurement_subject(self):
        for effect in (
            "Project Alpha production, under the prior outlook, was weakened under the current demand outlook",
            "Project Alpha production, under the prior outlook, was confirmed under the current demand outlook",
        ):
            with self.subTest(effect=effect):
                self.assertFalse(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_complete_v3_spec_rejects_outlook_parenthetical_bypass(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [self.confirmation_point(
            "Project Alpha production, under the prior outlook, was weakened under the current demand outlook"
        )]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("interpretation effect" in message for message in messages),
            messages,
        )

    def test_outlook_parenthetical_preserves_valid_transitive_effect(self):
        self.assertTrue(
            lineage._valid_confirmation_point(self.confirmation_point(
                "The filing, under the prior outlook, weakened the current demand outlook"
            ))
        )

    def test_parenthetical_with_own_effect_remains_a_clause_boundary(self):
        text = "Project Alpha production, under an outlook that weakened, remained stable"
        self.assertEqual(
            lineage._preserve_parenthetical_subject_modifiers(text),
            text,
        )


if __name__ == "__main__":
    unittest.main()
