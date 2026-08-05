from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4861676549_contracts as prior_contracts


class TestReview4861881600Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            prior_contracts.TestReview4861676549Contracts().base_v3_spec()
        )

    def confirmation_point(self, effect):
        return {
            "measurable_event_or_metric": "Project Alpha production milestone",
            "interpretation_effect": effect,
        }

    def test_bare_period_parentheticals_preserve_measurement_subject(self):
        for period in (
            "Q2",
            "FY2026",
            "2026",
            "second quarter",
            "2분기",
        ):
            for verb in ("weakened", "confirmed"):
                effect = (
                    f"Project Alpha production, {period}, was {verb} "
                    "under the current demand outlook"
                )
                with self.subTest(period=period, verb=verb):
                    self.assertFalse(
                        lineage._valid_confirmation_point(
                            self.confirmation_point(effect)
                        )
                    )
                    self.assertFalse(lineage._valid_confirmation_point(effect))

    def test_complete_v3_rejects_bare_period_subject_bypass(self):
        for effect in (
            "Project Alpha production, Q2, was weakened under the current demand outlook",
            "Project Alpha production, FY2026, was confirmed under the current demand outlook",
        ):
            with self.subTest(effect=effect):
                spec = self.base_v3_spec()
                spec["next_confirmation_points"] = [self.confirmation_point(effect)]
                messages = []
                self.assertFalse(
                    lineage.validate_stage_a_v3_override(
                        spec, spec["spec_id"], messages
                    )
                )
                self.assertTrue(
                    any("interpretation effect" in message for message in messages),
                    messages,
                )

    def test_transitive_effects_with_bare_period_parentheticals_remain_valid(self):
        for effect in (
            "The filing, Q2, weakened the current demand outlook",
            "The filing, FY2026, confirmed the current demand outlook",
            "The filing, 2분기, strengthened the adoption thesis",
        ):
            with self.subTest(effect=effect):
                self.assertTrue(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )
                self.assertTrue(lineage._valid_confirmation_point(effect))

    def test_nonperiod_bare_parentheticals_are_not_overpreserved(self):
        for effect in (
            "Project Alpha production, Project Beta, weakened the current demand outlook",
            "Project Alpha production, Q2 outlook, weakened the current demand outlook",
            "Project Alpha production, latest period, weakened the current demand outlook",
        ):
            with self.subTest(effect=effect):
                preserved = lineage._preserve_parenthetical_subject_modifiers(effect)
                self.assertIn(",", preserved)


if __name__ == "__main__":
    unittest.main()
