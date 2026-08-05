from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4866764030_contracts as prior_contracts


class TestReview4866897921Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            prior_contracts.TestReview4866764030Contracts().base_v3_spec()
        )

    @staticmethod
    def confirmation_point(effect):
        return {
            "measurable_event_or_metric": "Project Alpha production milestone",
            "interpretation_effect": effect,
        }

    def test_leading_dependent_clause_uses_following_main_clause(self):
        for effect in (
            "Although Project Alpha production weakened, "
            "the current demand outlook would strengthen",
            "Even though Project Alpha production weakened, "
            "the current demand outlook would weaken",
            "Despite Project Alpha production weakening, "
            "the adoption thesis would strengthen",
            "If Project Alpha production weakens, "
            "the current demand outlook would strengthen",
        ):
            with self.subTest(effect=effect):
                self.assertTrue(lineage._has_bound_interpretation_effect(effect))
                self.assertTrue(
                    lineage._valid_confirmation_point(
                        self.confirmation_point(effect)
                    )
                )

    def test_trailing_dependent_clause_keeps_prefix_semantics(self):
        for effect in (
            "Project Alpha production weakened even though "
            "the current demand outlook improved",
            "Project Alpha production weakened if "
            "the current demand outlook improved",
        ):
            with self.subTest(effect=effect):
                self.assertFalse(lineage._has_bound_interpretation_effect(effect))
                self.assertFalse(
                    lineage._valid_confirmation_point(
                        self.confirmation_point(effect)
                    )
                )

        valid = (
            "The filing weakened the current demand outlook even though "
            "Project Alpha production improved"
        )
        self.assertTrue(lineage._has_bound_interpretation_effect(valid))

    def test_leading_dependent_clause_without_main_effect_fails(self):
        for effect in (
            "Although Project Alpha production weakened, "
            "Project Beta capacity improved",
            "If Project Alpha production weakens, "
            "Project Beta capacity improves",
        ):
            with self.subTest(effect=effect):
                self.assertFalse(lineage._has_bound_interpretation_effect(effect))
                self.assertFalse(
                    lineage._valid_confirmation_point(
                        self.confirmation_point(effect)
                    )
                )

    def test_leading_marker_without_clause_separator_fails_closed(self):
        effect = (
            "Although Project Alpha production weakened "
            "the current demand outlook would strengthen"
        )
        self.assertFalse(lineage._has_bound_interpretation_effect(effect))
        self.assertFalse(
            lineage._valid_confirmation_point(self.confirmation_point(effect))
        )

    def test_complete_v3_accepts_leading_concession_main_effect(self):
        spec = self.base_v3_spec()
        effect = (
            "Although Project Alpha production weakened, "
            "the current demand outlook would strengthen"
        )
        spec["next_confirmation_points"] = [self.confirmation_point(effect)]
        messages = []
        self.assertTrue(
            lineage.validate_stage_a_v3_override(
                spec, spec["spec_id"], messages
            ),
            messages,
        )

    def test_complete_v3_rejects_leading_concession_without_main_effect(self):
        spec = self.base_v3_spec()
        effect = (
            "Although Project Alpha production weakened, "
            "Project Beta capacity improved"
        )
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


if __name__ == "__main__":
    unittest.main()
