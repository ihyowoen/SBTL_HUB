from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4840844831_contracts as prior_contracts

# Review 4849677091: directional metric words require interpretation binding.


class TestReview4849359963Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(prior_contracts.TestReview4840844831Contracts().base_spec())

    def test_free_text_confirmation_requires_interpretation_effect(self):
        self.assertFalse(
            lineage._valid_confirmation_point(
                "Project Alpha production capacity milestone"
            )
        )

    def test_supported_interpretation_effect_inflections_pass(self):
        values = (
            "Project Alpha production capacity milestone would confirm adoption",
            "Project Alpha production capacity milestone strengthens the thesis",
            "Project Alpha production capacity milestone weakened the thesis",
            "Project Alpha production capacity milestone invalidated the thesis",
            "Project Alpha production capacity milestone revised the outlook",
        )
        for value in values:
            with self.subTest(value=value):
                self.assertTrue(lineage._valid_confirmation_point(value))

    def test_complete_term_collision_does_not_create_effect(self):
        self.assertFalse(
            lineage._valid_confirmation_point(
                "Project Alpha production capacity milestone remained unchanged"
            )
        )

    def test_metric_direction_does_not_count_as_interpretation_effect(self):
        values = (
            "Project Alpha production capacity decreased by 10%",
            "Project Alpha production capacity increased to 100 MW",
            "Project Alpha production capacity held at 100 MW",
            "Project Alpha production capacity changed by 10%",
        )
        for value in values:
            with self.subTest(value=value):
                self.assertFalse(lineage._valid_confirmation_point(value))

    def test_direction_bound_to_interpretation_object_passes(self):
        values = (
            "Project Alpha production capacity decreased by 10%, lowering the outlook",
            "Project Alpha production capacity increased to 100 MW, raising adoption probability",
            "The thesis would change if Project Alpha production capacity fell by 10%",
            "Project Alpha 생산 용량 감소는 전망을 하향할 것이다",
        )
        for value in values:
            with self.subTest(value=value):
                self.assertTrue(lineage._valid_confirmation_point(value))

    def test_complete_v3_spec_rejects_metric_direction_only_confirmation(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [
            "Project Alpha production capacity decreased by 10%"
        ]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("interpretation effect" in message for message in messages), messages
        )

    def test_generic_confirmation_scaffolds_still_fail(self):
        for value in (
            "additional data needed to confirm adoption",
            "more evidence required for approval",
            "confirmation needed for production",
        ):
            with self.subTest(value=value):
                self.assertFalse(lineage._valid_confirmation_point(value))

    def test_complete_v3_spec_rejects_metric_only_confirmation(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [
            "Project Alpha production capacity milestone"
        ]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("interpretation effect" in message for message in messages), messages
        )

    def test_complete_v3_spec_accepts_measurable_effect_confirmation(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [
            "Publication of additional data center capacity for Project Alpha would confirm adoption"
        ]
        messages = []
        self.assertTrue(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages),
            messages,
        )
        self.assertEqual(messages, [])


if __name__ == "__main__":
    unittest.main()
