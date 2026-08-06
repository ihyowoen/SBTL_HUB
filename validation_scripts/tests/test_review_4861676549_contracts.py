from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4861534917_contracts as prior_contracts


class TestReview4861676549Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            prior_contracts.TestReview4861534917Contracts().base_v3_spec()
        )

    def confirmation_point(self, effect):
        return {
            "measurable_event_or_metric": "Project Alpha production milestone",
            "interpretation_effect": effect,
        }

    def test_plural_generic_possessive_owners_are_not_named_subjects(self):
        for value in (
            "companies' revenue",
            "issuers’ revenue",
            "businesses' margin",
            "projects’ capacity",
        ):
            with self.subTest(value=value):
                self.assertFalse(lineage._structured_exact_target(value))

    def test_item_specific_plural_possessive_subjects_remain_valid(self):
        for value in (
            "Alpha Companies' revenue",
            "Project Alpha issuers’ margin",
            "Beta Businesses' capacity",
        ):
            with self.subTest(value=value):
                self.assertTrue(lineage._structured_exact_target(value))

    def test_complete_v3_rejects_plural_generic_possessive_target_bypass(self):
        spec = self.base_v3_spec()
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "official filing",
            "exact_claim_or_metric": "companies' revenue",
        }]
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "issuers’ revenue",
            "interpretation_effect": "would weaken the demand outlook",
        }]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )

    def test_safe_temporal_parentheticals_preserve_measurement_subject(self):
        for effect in (
            "Project Alpha production, as of Q2, was weakened under the current demand outlook",
            "Project Alpha production, for Q2, was confirmed under the current demand outlook",
            "Project Alpha production, as of 2026, was weakened under the current demand outlook",
            "Project Alpha production, for the second quarter, was confirmed under the current demand outlook",
        ):
            with self.subTest(effect=effect):
                self.assertFalse(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )
                self.assertFalse(lineage._valid_confirmation_point(effect))

    def test_complete_v3_rejects_temporal_parenthetical_subject_bypass(self):
        for effect in (
            "Project Alpha production, as of Q2, was weakened under the current demand outlook",
            "Project Alpha production, for Q2, was confirmed under the current demand outlook",
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

    def test_valid_transitive_effects_with_temporal_parentheticals_pass(self):
        for effect in (
            "The filing, as of Q2, weakened the current demand outlook",
            "The filing, for Q2, confirmed the current demand outlook",
        ):
            with self.subTest(effect=effect):
                self.assertTrue(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )
                self.assertTrue(lineage._valid_confirmation_point(effect))

    def test_nonperiod_as_and_for_clauses_are_not_overpreserved(self):
        for effect in (
            "Project Alpha production, as demand improved, weakened the current demand outlook",
            "Project Alpha production, for Project Beta, weakened the current demand outlook",
        ):
            with self.subTest(effect=effect):
                preserved = lineage._preserve_parenthetical_subject_modifiers(effect)
                self.assertIn(",", preserved)


if __name__ == "__main__":
    unittest.main()
