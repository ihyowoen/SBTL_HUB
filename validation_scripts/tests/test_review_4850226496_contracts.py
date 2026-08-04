from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4840844831_contracts as prior_contracts


class TestReview4850226496Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            prior_contracts.TestReview4840844831Contracts().base_spec()
        )

    def test_effect_first_percentage_adoption_movement_is_measurement(self):
        for effect in (
            "10% increase in Project Alpha adoption",
            "A 10 percent decrease in Project Alpha adoption",
        ):
            with self.subTest(effect=effect):
                self.assertFalse(
                    lineage._valid_confirmation_point({
                        "measurable_event_or_metric": "Project Alpha adoption 10%",
                        "interpretation_effect": effect,
                    })
                )

    def test_complete_v3_spec_rejects_effect_first_adoption_bypass(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "Project Alpha adoption 10%",
            "interpretation_effect": "10% increase in Project Alpha adoption",
        }]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("interpretation effect" in message for message in messages),
            messages,
        )

    def test_forward_percentage_adoption_movement_remains_rejected(self):
        self.assertFalse(
            lineage._valid_confirmation_point({
                "measurable_event_or_metric": "Project Alpha adoption 10%",
                "interpretation_effect": "Project Alpha adoption increased by 10%",
            })
        )

    def test_semantic_adoption_effects_remain_valid(self):
        self.assertTrue(
            lineage._valid_confirmation_point({
                "measurable_event_or_metric": "Project Alpha adoption 10%",
                "interpretation_effect": "The filing would raise adoption probability",
            })
        )
        self.assertTrue(
            lineage._valid_confirmation_point({
                "measurable_event_or_metric": "Project Alpha capacity 100 MW",
                "interpretation_effect": "The milestone would confirm adoption",
            })
        )


if __name__ == "__main__":
    unittest.main()
