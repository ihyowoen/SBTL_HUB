from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4840844831_contracts as prior_contracts


class TestReview4849975002Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(prior_contracts.TestReview4840844831Contracts().base_spec())

    def test_measurement_prose_does_not_bind_outlook_to_metric_direction(self):
        self.assertFalse(
            lineage._valid_confirmation_point({
                "measurable_event_or_metric": "Project Alpha capacity 100 MW",
                "interpretation_effect": (
                    "The outlook report says Project Alpha capacity increased"
                ),
            })
        )

    def test_object_first_semantic_effect_remains_valid(self):
        self.assertTrue(
            lineage._valid_confirmation_point({
                "measurable_event_or_metric": "Project Alpha capacity 100 MW",
                "interpretation_effect": "The demand outlook would materially decrease",
            })
        )

    def test_specific_additional_data_center_capacity_effect_passes(self):
        self.assertTrue(
            lineage._valid_confirmation_point({
                "measurable_event_or_metric": "Project Alpha capacity 100 MW",
                "interpretation_effect": (
                    "Additional data center capacity would confirm the adoption outlook"
                ),
            })
        )

    def test_generic_structured_effect_placeholder_still_fails(self):
        self.assertFalse(
            lineage._valid_confirmation_point({
                "measurable_event_or_metric": "Project Alpha capacity 100 MW",
                "interpretation_effect": "additional data needed",
            })
        )

    def test_complete_v3_spec_rejects_measurement_prose_bypass(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "Project Alpha capacity 100 MW",
            "interpretation_effect": (
                "The outlook report says Project Alpha capacity increased"
            ),
        }]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("interpretation effect" in message for message in messages), messages
        )

    def test_complete_v3_spec_accepts_specific_structured_effect(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "Project Alpha capacity 100 MW",
            "interpretation_effect": (
                "Additional data center capacity would confirm the adoption outlook"
            ),
        }]
        messages = []
        self.assertTrue(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages),
            messages,
        )


if __name__ == "__main__":
    unittest.main()
