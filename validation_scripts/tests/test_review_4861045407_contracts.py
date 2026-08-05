from __future__ import annotations

import copy
import unittest

from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4860866998_contracts as prior_contracts


class TestReview4861045407Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            prior_contracts.TestReview4860866998Contracts().base_v3_spec()
        )

    def confirmation_point(self, effect):
        return {
            "measurable_event_or_metric": "Project Alpha production milestone",
            "interpretation_effect": effect,
        }

    def test_inflected_predicates_are_not_item_specific_subjects(self):
        for value in (
            "official approved",
            "company launched",
            "corporate completed",
            "project qualified",
        ):
            with self.subTest(value=value):
                self.assertFalse(lineage._structured_exact_target(value))

    def test_named_inflected_predicate_targets_remain_valid(self):
        for value in (
            "Project Alpha was approved",
            "Project Alpha launched",
            "Project Alpha completed construction",
            "Project Alpha 2027 approved",
        ):
            with self.subTest(value=value):
                self.assertTrue(lineage._structured_exact_target(value))

    def test_complete_v3_rejects_generic_inflected_predicate_targets(self):
        spec = self.base_v3_spec()
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "official filing",
            "exact_claim_or_metric": "company launched",
        }]
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "official approved",
            "interpretation_effect": "would weaken the demand outlook",
        }]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )

    def test_three_token_entity_only_assertions_fail(self):
        for value in (
            "Project Alpha Beta",
            "Company Alpha Beta",
            "Alpha Beta Holdings",
            "프로젝트 알파 베타",
        ):
            with self.subTest(value=value):
                self.assertFalse(related.item_specific_lineage_assertion(value))

    def test_substantive_concise_assertions_remain_valid(self):
        for value in (
            "commissioning",
            "Permit entered force",
            "Commercial operations began",
            "August supply agreement",
        ):
            with self.subTest(value=value):
                self.assertTrue(related.item_specific_lineage_assertion(value))

    def test_numeric_parentheticals_do_not_hide_measurement_subject(self):
        for effect in (
            "Project Alpha production, up 10%, was weakened under the current demand outlook",
            "Project Alpha production, down 5%, was confirmed under the current demand outlook",
            "Project Alpha production, 10% higher, was weakened under the current demand outlook",
        ):
            with self.subTest(effect=effect):
                self.assertFalse(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_complete_v3_rejects_numeric_parenthetical_bypass(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [self.confirmation_point(
            "Project Alpha production, up 10%, was weakened under the current demand outlook"
        )]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("interpretation effect" in message for message in messages),
            messages,
        )

    def test_numeric_parenthetical_with_own_outlook_is_not_folded(self):
        text = "Project Alpha production, 10% lower outlook, remained stable"
        self.assertEqual(
            lineage._preserve_parenthetical_subject_modifiers(text),
            text,
        )


if __name__ == "__main__":
    unittest.main()
