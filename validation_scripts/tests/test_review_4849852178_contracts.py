from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4840844831_contracts as prior_contracts


class TestReview4849852178Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(prior_contracts.TestReview4840844831Contracts().base_spec())

    def test_structured_metric_direction_only_effect_fails(self):
        self.assertFalse(
            lineage._valid_confirmation_point({
                "measurable_event_or_metric": "Project Alpha capacity 100 MW",
                "interpretation_effect": "capacity increased",
            })
        )

    def test_structured_direction_bound_to_outlook_passes(self):
        self.assertTrue(
            lineage._valid_confirmation_point({
                "measurable_event_or_metric": "Project Alpha capacity 100 MW",
                "interpretation_effect": "would lower the current demand outlook",
            })
        )

    def test_support_metric_noun_does_not_count_as_effect(self):
        self.assertFalse(
            lineage._valid_confirmation_point(
                "Project Alpha customer support volume increased by 10%"
            )
        )

    def test_ambiguous_direct_terms_require_verbal_or_object_binding(self):
        passing = (
            "Project Alpha capacity milestone would confirm adoption",
            "Project Alpha capacity results support the thesis",
            "Project Alpha thesis would be confirmed by the capacity filing",
        )
        for value in passing:
            with self.subTest(value=value):
                self.assertTrue(lineage._valid_confirmation_point(value))

    def test_modifiers_between_direction_and_outlook_are_allowed(self):
        self.assertTrue(
            lineage._valid_confirmation_point(
                "Project Alpha capacity milestone would lower the current demand outlook"
            )
        )

    def test_numeric_metric_bridge_does_not_bind_to_later_outlook(self):
        self.assertFalse(
            lineage._valid_confirmation_point(
                "Project Alpha capacity increased by 10 percent and the outlook remained available"
            )
        )

    def test_complete_v3_spec_rejects_structured_metric_direction_bypass(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "Project Alpha capacity 100 MW",
            "interpretation_effect": "capacity increased",
        }]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("interpretation effect" in message for message in messages), messages
        )


if __name__ == "__main__":
    unittest.main()
