from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4840844831_contracts as prior_contracts


class TestReview4850038388Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(prior_contracts.TestReview4840844831Contracts().base_spec())

    def test_project_qualifier_inside_outlook_object_passes(self):
        self.assertTrue(
            lineage._valid_confirmation_point({
                "measurable_event_or_metric": "Project Alpha capacity 100 MW",
                "interpretation_effect": (
                    "The demand outlook for Project Alpha would decrease"
                ),
            })
        )

    def test_complete_v3_spec_accepts_project_qualified_outlook(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "Project Alpha capacity 100 MW",
            "interpretation_effect": (
                "The demand outlook for Project Alpha would decrease"
            ),
        }]
        messages = []
        self.assertTrue(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages),
            messages,
        )

    def test_inflected_metric_direct_effect_is_rejected(self):
        self.assertFalse(
            lineage._valid_confirmation_point({
                "measurable_event_or_metric": "Project Alpha capacity 100 MW",
                "interpretation_effect": (
                    "Project Alpha production capacity weakened by 10%"
                ),
            })
        )

    def test_complete_v3_spec_rejects_inflected_metric_bypass(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "Project Alpha capacity 100 MW",
            "interpretation_effect": (
                "Project Alpha production capacity weakened by 10%"
            ),
        }]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("interpretation effect" in message for message in messages), messages
        )

    def test_inflected_direct_effect_bound_to_outlook_passes(self):
        self.assertTrue(
            lineage._valid_confirmation_point({
                "measurable_event_or_metric": "Project Alpha capacity 100 MW",
                "interpretation_effect": (
                    "Project Alpha capacity results weakened the demand outlook"
                ),
            })
        )

    def test_auxiliary_direct_effect_without_measurement_context_passes(self):
        self.assertTrue(
            lineage._valid_confirmation_point({
                "measurable_event_or_metric": "Project Alpha capacity 100 MW",
                "interpretation_effect": "The thesis would be weakened",
            })
        )

    def test_measurement_report_bypass_remains_rejected(self):
        self.assertFalse(
            lineage._valid_confirmation_point({
                "measurable_event_or_metric": "Project Alpha capacity 100 MW",
                "interpretation_effect": (
                    "The outlook report says Project Alpha capacity increased"
                ),
            })
        )


if __name__ == "__main__":
    unittest.main()
