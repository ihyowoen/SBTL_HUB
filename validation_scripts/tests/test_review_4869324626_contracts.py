from __future__ import annotations

import copy
import unittest

from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4861791404_contracts as v3_contracts
from validation_scripts.tests import test_review_4862131806_contracts as related_contracts


class TestReview4869324626Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            v3_contracts.TestReview4861791404Contracts().base_v3_spec()
        )

    def test_numbered_entity_labels_are_exact_target_subjects(self):
        for value in (
            "Project 1 revenue",
            "Program 2 capex",
            "Facility 2 output",
        ):
            with self.subTest(value=value):
                self.assertTrue(lineage._structured_exact_target(value))

    def test_complete_v3_accepts_numbered_entity_targets(self):
        spec = self.base_v3_spec()
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "official filing",
            "exact_claim_or_metric": "Project 1 revenue",
        }]
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "Facility 2 output",
            "interpretation_effect": "would strengthen the current demand outlook",
        }]
        messages = []
        self.assertTrue(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages),
            messages,
        )

    def test_temporal_noun_modifiers_preserve_main_effect(self):
        for value in (
            "The filing after review would strengthen the current demand outlook",
            "Project Alpha after-tax profit would strengthen the current demand outlook",
            "The filing before publication may weaken the current demand outlook",
        ):
            with self.subTest(value=value):
                self.assertTrue(lineage._has_bound_interpretation_effect(value))

    def test_once_and_whenever_suffixes_do_not_supply_the_effect(self):
        for value in (
            "Project Alpha production weakened once the current demand outlook improved",
            "Project Alpha production weakened whenever the current demand outlook improved",
        ):
            with self.subTest(value=value):
                self.assertFalse(lineage._has_bound_interpretation_effect(value))

    def test_leading_once_clause_preserves_the_independent_main_clause(self):
        for value in (
            "Once Project Alpha production improved, the current demand outlook would strengthen",
            "Whenever Project Alpha production improves, the current demand outlook may strengthen",
        ):
            with self.subTest(value=value):
                self.assertTrue(lineage._has_bound_interpretation_effect(value))

    def test_generic_forecast_sentiment_and_confidence_are_not_related_subjects(self):
        fixture = related_contracts.TestReview4862131806Contracts()
        for assertion in (
            "forecast worsened",
            "sentiment improved",
            "confidence reduced",
        ):
            with self.subTest(assertion=assertion):
                fixture._assert_strict_failure(assertion)

    def test_named_forecast_sentiment_and_confidence_remain_valid(self):
        fixture = related_contracts.TestReview4862131806Contracts()
        for assertion in (
            "Project Alpha forecast worsened",
            "Project Alpha sentiment improved",
            "Project Alpha confidence reduced",
        ):
            with self.subTest(assertion=assertion):
                fixture._assert_strict_success(assertion)


if __name__ == "__main__":
    unittest.main()
