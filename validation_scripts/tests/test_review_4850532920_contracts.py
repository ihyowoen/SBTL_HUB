from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4840844831_contracts as prior_contracts


class TestReview4850532920Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            prior_contracts.TestReview4840844831Contracts().base_spec()
        )

    def confirmation_point(self, effect):
        return {
            "measurable_event_or_metric": "Project Alpha production milestone",
            "interpretation_effect": effect,
        }

    def test_direct_effect_measurement_attachments_are_rejected(self):
        for effect in (
            "Project Alpha production was weakened under the current demand outlook",
            "Project Alpha production was confirmed under the current demand outlook",
        ):
            with self.subTest(effect=effect):
                self.assertFalse(
                    lineage._valid_confirmation_point(
                        self.confirmation_point(effect)
                    )
                )

    def test_complete_v3_spec_rejects_direct_effect_measurement_bypass(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [self.confirmation_point(
            "Project Alpha production was weakened under the current demand outlook"
        )]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("interpretation effect" in message for message in messages),
            messages,
        )

    def test_direct_transitive_interpretation_effects_remain_valid(self):
        for effect in (
            "The filing weakened the current demand outlook",
            "The milestone confirmed the adoption thesis",
            "Project Alpha capacity results weakened the demand outlook",
        ):
            with self.subTest(effect=effect):
                self.assertTrue(
                    lineage._valid_confirmation_point(
                        self.confirmation_point(effect)
                    )
                )

    def test_object_first_passive_interpretation_effect_remains_valid(self):
        self.assertTrue(
            lineage._valid_confirmation_point(
                self.confirmation_point(
                    "The current demand outlook was weakened by the filing"
                )
            )
        )


if __name__ == "__main__":
    unittest.main()
