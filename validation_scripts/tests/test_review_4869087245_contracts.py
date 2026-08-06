from __future__ import annotations

import copy
import unittest

from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4861791404_contracts as v3_contracts
from validation_scripts.tests import test_review_4862131806_contracts as related_contracts


class TestReview4869087245Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            v3_contracts.TestReview4861791404Contracts().base_v3_spec()
        )

    def test_numbers_do_not_replace_an_exact_target_subject(self):
        for value in (
            "source 2026 revenue",
            "entity 2026 margin",
            "2026 revenue",
        ):
            with self.subTest(value=value):
                self.assertFalse(lineage._structured_exact_target(value))

    def test_named_numeric_exact_targets_remain_valid(self):
        for value in (
            "Project Alpha 2026 revenue",
            "Project Alpha FY2026 margin",
            "Plant 1 Q2 capacity",
            "Project A 2026 launch",
        ):
            with self.subTest(value=value):
                self.assertTrue(lineage._structured_exact_target(value))

    def test_complete_v3_rejects_number_only_target_bypass(self):
        spec = self.base_v3_spec()
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "official filing",
            "exact_claim_or_metric": "source 2026 revenue",
        }]
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "entity 2026 margin",
            "interpretation_effect": "would weaken the demand outlook",
        }]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )
        self.assertTrue(
            any("exact claim, metric, stage, or date" in message for message in messages),
            messages,
        )
        self.assertTrue(
            any("measurable events or metrics" in message for message in messages),
            messages,
        )

    def test_generic_change_predicates_are_not_related_subjects(self):
        fixture = related_contracts.TestReview4862131806Contracts()
        for assertion in (
            "outlook worsened",
            "risk reduced",
            "probability improved",
        ):
            with self.subTest(assertion=assertion):
                fixture._assert_strict_failure(assertion)

    def test_named_change_assertions_remain_valid(self):
        fixture = related_contracts.TestReview4862131806Contracts()
        for assertion in (
            "Project Alpha outlook worsened",
            "Project Alpha risk reduced",
            "Project Alpha probability improved",
        ):
            with self.subTest(assertion=assertion):
                fixture._assert_strict_success(assertion)


if __name__ == "__main__":
    unittest.main()
