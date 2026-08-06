from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4840844831_contracts as prior_contracts


class TestReview4850163550Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            prior_contracts.TestReview4840844831Contracts().base_spec()
        )

    def test_percentage_based_adoption_movement_is_measurement(self):
        self.assertFalse(
            lineage._valid_confirmation_point({
                "measurable_event_or_metric": "Project Alpha adoption 10%",
                "interpretation_effect": "Project Alpha adoption increased by 10%",
            })
        )
        self.assertFalse(
            lineage._valid_confirmation_point({
                "measurable_event_or_metric": "Project Alpha adoption 20%",
                "interpretation_effect": (
                    "Project Alpha adoption decreased from 30% to 20%"
                ),
            })
        )

    def test_complete_v3_spec_rejects_percentage_adoption_bypass(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "Project Alpha adoption 10%",
            "interpretation_effect": "Project Alpha adoption increased by 10%",
        }]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("interpretation effect" in message for message in messages),
            messages,
        )

    def test_semantic_adoption_effects_remain_valid(self):
        self.assertTrue(
            lineage._valid_confirmation_point({
                "measurable_event_or_metric": "Project Alpha adoption 10%",
                "interpretation_effect": "The filing would raise adoption probability",
            })
        )
        self.assertTrue(
            lineage._valid_confirmation_point({
                "measurable_event_or_metric": "Project Alpha capacity 100 MW",
                "interpretation_effect": "The milestone would confirm adoption",
            })
        )

    def test_inflected_substantive_target_predicates_are_recognized(self):
        for target in (
            "Project Alpha was approved",
            "Project Alpha launched",
            "Project Alpha was awarded",
            "Project Alpha was completed",
            "Project Alpha is being qualified",
        ):
            with self.subTest(target=target):
                self.assertTrue(lineage._structured_exact_target(target))

    def test_free_text_evidence_accepts_completed_event_targets(self):
        self.assertTrue(
            lineage._valid_evidence_target(
                "SEC filing Project Alpha was approved"
            )
        )
        self.assertTrue(
            lineage._valid_evidence_target(
                "official Project Alpha launched"
            )
        )

    def test_completed_event_target_keeps_complete_v3_spec_valid(self):
        spec = self.base_v3_spec()
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "SEC filing",
            "exact_claim_or_metric": "Project Alpha was approved",
        }]
        messages = []
        self.assertTrue(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages),
            messages,
        )

    def test_predicate_boundaries_do_not_match_unapproved_substrings(self):
        self.assertFalse(
            lineage._structured_exact_target("Project Alpha unapproved rumor")
        )
        self.assertFalse(
            lineage._valid_evidence_target(
                "official Project Alpha unapproved rumor"
            )
        )

    def test_base_and_inflected_predicates_both_remain_supported(self):
        for target in (
            "Project Alpha launch",
            "Project Alpha launches",
            "Project Alpha launched",
            "Project Alpha launching",
        ):
            with self.subTest(target=target):
                self.assertTrue(lineage._structured_exact_target(target))


if __name__ == "__main__":
    unittest.main()
