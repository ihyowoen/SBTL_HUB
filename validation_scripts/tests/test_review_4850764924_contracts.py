from __future__ import annotations

# Regression lock for review 4850764924.
import copy
import unittest

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4840844831_contracts as prior_contracts


class TestReview4850764924Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            prior_contracts.TestReview4840844831Contracts().base_spec()
        )

    def confirmation_point(self, effect):
        return {
            "measurable_event_or_metric": "Project Alpha production milestone",
            "interpretation_effect": effect,
        }

    def test_introductory_comma_does_not_hide_parenthetical_measurement_subject(self):
        for effect in (
            "In 2025, Project Alpha production, in the northern manufacturing facility, was weakened under the current demand outlook",
            "In 2025, Project Alpha production, in the northern manufacturing facility, was confirmed under the current demand outlook",
        ):
            with self.subTest(effect=effect):
                self.assertFalse(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_complete_v3_spec_rejects_introductory_comma_bypass(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [self.confirmation_point(
            "In 2025, Project Alpha production, in the northern manufacturing facility, was weakened under the current demand outlook"
        )]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("interpretation effect" in message for message in messages),
            messages,
        )

    def test_all_exact_metric_subjects_are_rejected_when_merely_attached(self):
        metrics = (
            "EBITDA", "profit", "utilization", "yield", "throughput",
            "capex", "opex",
        )
        for metric in metrics:
            effect = f"Project Alpha {metric} was weakened under the current demand outlook"
            with self.subTest(metric=metric):
                self.assertFalse(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_complete_v3_spec_rejects_exact_metric_attachment_bypass(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [self.confirmation_point(
            "Project Alpha EBITDA was weakened under the current demand outlook"
        )]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("interpretation effect" in message for message in messages),
            messages,
        )

    def test_metric_qualifiers_inside_interpretation_objects_remain_valid(self):
        for effect in (
            "The outlook for Project Alpha capacity would weaken",
            "The demand outlook regarding Project Alpha EBITDA would weaken",
        ):
            with self.subTest(effect=effect):
                self.assertTrue(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_separate_reported_measurement_event_remains_rejected(self):
        self.assertFalse(
            lineage._valid_confirmation_point(self.confirmation_point(
                "The outlook report says Project Alpha capacity increased"
            ))
        )

    def test_introductory_comma_with_valid_parenthetical_transitive_effect_passes(self):
        self.assertTrue(
            lineage._valid_confirmation_point(self.confirmation_point(
                "In 2025, the filing, from the northern manufacturing facility, weakened the current demand outlook"
            ))
        )


if __name__ == "__main__":
    unittest.main()
