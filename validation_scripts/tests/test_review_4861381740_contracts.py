from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4861267953_contracts as prior_contracts


class TestReview4861381740Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            prior_contracts.TestReview4861267953Contracts().base_v3_spec()
        )

    def confirmation_point(self, effect):
        return {
            "measurable_event_or_metric": "Project Alpha production milestone",
            "interpretation_effect": effect,
        }

    def test_plural_source_class_nouns_are_neutral_target_modifiers(self):
        for value in (
            "filings revenue",
            "documents revenue",
            "datasets margin",
            "reports EBITDA",
            "transcripts capacity",
        ):
            with self.subTest(value=value):
                self.assertFalse(lineage._structured_exact_target(value))

    def test_plural_source_class_with_real_subject_or_date_remains_valid(self):
        for value in (
            "filings Project Alpha revenue",
            "documents Project Alpha launch date",
            "reports Project Alpha 2027 revenue",
        ):
            with self.subTest(value=value):
                self.assertTrue(lineage._structured_exact_target(value))

    def test_complete_v3_rejects_plural_source_class_only_targets(self):
        spec = self.base_v3_spec()
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "official filings",
            "exact_claim_or_metric": "filings revenue",
        }]
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "documents revenue",
            "interpretation_effect": "would weaken the demand outlook",
        }]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )

    def test_temporal_parenthetical_preserves_measurement_subject(self):
        for effect in (
            "Project Alpha production, after a 10% decline, was weakened under the current demand outlook",
            "Project Alpha production, before a 10% decline, was confirmed under the current demand outlook",
        ):
            with self.subTest(effect=effect):
                self.assertFalse(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_complete_v3_rejects_temporal_parenthetical_bypass(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [self.confirmation_point(
            "Project Alpha production, after a 10% decline, was weakened under the current demand outlook"
        )]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("interpretation effect" in message for message in messages),
            messages,
        )

    def test_valid_interpretation_effect_with_temporal_parenthetical_remains_valid(self):
        effect = "The filing, after publication, weakened the current demand outlook"
        self.assertTrue(
            lineage._valid_confirmation_point(self.confirmation_point(effect))
        )


if __name__ == "__main__":
    unittest.main()
