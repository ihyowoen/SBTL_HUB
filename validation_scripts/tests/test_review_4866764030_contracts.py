from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4861676549_contracts as prior_contracts


class TestReview4866764030Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            prior_contracts.TestReview4861676549Contracts().base_v3_spec()
        )

    @staticmethod
    def confirmation_point(effect):
        return {
            "measurable_event_or_metric": "Project Alpha production milestone",
            "interpretation_effect": effect,
        }

    def test_even_though_is_a_concessive_clause_boundary(self):
        effect = (
            "Project Alpha production weakened even though "
            "the current demand outlook improved"
        )
        self.assertFalse(lineage._has_bound_interpretation_effect(effect))
        self.assertFalse(
            lineage._valid_confirmation_point(self.confirmation_point(effect))
        )
        self.assertFalse(lineage._valid_confirmation_point(effect))

    def test_complete_v3_rejects_even_though_measurement_bypass(self):
        spec = self.base_v3_spec()
        effect = (
            "Project Alpha production weakened even though "
            "the current demand outlook improved"
        )
        spec["next_confirmation_points"] = [self.confirmation_point(effect)]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("interpretation effect" in message for message in messages),
            messages,
        )

    def test_completed_interpretation_effect_before_concession_remains_valid(self):
        effect = (
            "The filing weakened the current demand outlook even though "
            "Project Alpha production improved"
        )
        self.assertTrue(lineage._has_bound_interpretation_effect(effect))
        self.assertTrue(
            lineage._valid_confirmation_point(self.confirmation_point(effect))
        )

    def test_lettered_item_class_targets_are_exact(self):
        for value in (
            "Project A revenue",
            "Project A's revenue",
            "Plant A inventory",
            "Facility B safety data",
            "Site C capacity",
            "Unit D output",
        ):
            with self.subTest(value=value):
                self.assertTrue(lineage._structured_exact_target(value))

    def test_generic_owner_plus_letter_remains_neutral(self):
        for value in (
            "Company A revenue",
            "Issuer A margin",
            "Government A revenue",
            "Agency B capacity",
        ):
            with self.subTest(value=value):
                self.assertFalse(lineage._structured_exact_target(value))

    def test_lettered_item_without_substantive_target_still_fails(self):
        for value in ("Project A", "Plant B", "Facility C"):
            with self.subTest(value=value):
                self.assertFalse(lineage._structured_exact_target(value))

    def test_complete_v3_accepts_lettered_project_targets(self):
        spec = self.base_v3_spec()
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "official filing",
            "exact_claim_or_metric": "Project A revenue",
        }]
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "Project A capacity",
            "interpretation_effect": "would strengthen the demand outlook",
        }]
        messages = []
        self.assertTrue(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages),
            messages,
        )


if __name__ == "__main__":
    unittest.main()
