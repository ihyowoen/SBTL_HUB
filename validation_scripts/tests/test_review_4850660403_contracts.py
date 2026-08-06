from __future__ import annotations

# Regression lock for review 4850660403.
import copy
import unittest

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4840844831_contracts as prior_contracts


class TestReview4850660403Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            prior_contracts.TestReview4840844831Contracts().base_spec()
        )

    def confirmation_point(self, effect):
        return {
            "measurable_event_or_metric": "Project Alpha production milestone",
            "interpretation_effect": effect,
        }

    def test_parenthetical_measurement_subjects_are_rejected(self):
        for effect in (
            "Project Alpha production, in the northern manufacturing facility, was weakened under the current demand outlook",
            "Project Alpha production, in the northern manufacturing facility, was confirmed under the current demand outlook",
        ):
            with self.subTest(effect=effect):
                self.assertFalse(
                    lineage._valid_confirmation_point(
                        self.confirmation_point(effect)
                    )
                )

    def test_complete_v3_spec_rejects_parenthetical_subject_bypass(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [self.confirmation_point(
            "Project Alpha production, in the northern manufacturing facility, was weakened under the current demand outlook"
        )]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("interpretation effect" in message for message in messages),
            messages,
        )

    def test_in_measurement_attachments_are_rejected(self):
        for effect in (
            "Project Alpha production was weakened in the current demand outlook",
            "Project Alpha production was confirmed in the current demand outlook",
        ):
            with self.subTest(effect=effect):
                self.assertFalse(
                    lineage._valid_confirmation_point(
                        self.confirmation_point(effect)
                    )
                )

    def test_complete_v3_spec_rejects_in_attachment_bypass(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [self.confirmation_point(
            "Project Alpha production was weakened in the current demand outlook"
        )]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("interpretation effect" in message for message in messages),
            messages,
        )

    def test_parenthetical_direct_transitive_effect_remains_valid(self):
        self.assertTrue(
            lineage._valid_confirmation_point(
                self.confirmation_point(
                    "The filing, from the northern manufacturing facility, weakened the current demand outlook"
                )
            )
        )

    def test_adversative_comma_clause_remains_separate(self):
        self.assertTrue(
            lineage._valid_confirmation_point(
                self.confirmation_point(
                    "Project Alpha production increased, but the filing weakened the current demand outlook"
                )
            )
        )


if __name__ == "__main__":
    unittest.main()
