from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4861676549_contracts as prior_contracts


class TestReview4861791404Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            prior_contracts.TestReview4861676549Contracts().base_v3_spec()
        )

    def test_bare_plural_metric_and_event_roles_are_not_named_subjects(self):
        for value in (
            "revenues",
            "margins",
            "approvals",
            "capacities",
            "launches",
            "statuses",
        ):
            with self.subTest(value=value):
                self.assertFalse(lineage._structured_exact_target(value))

    def test_named_plural_roles_remain_valid(self):
        for value in (
            "Project Alpha revenues",
            "Project Alpha margins",
            "Project Alpha approvals",
            "Plant 1 revenues",
            "Project A launches",
        ):
            with self.subTest(value=value):
                self.assertTrue(lineage._structured_exact_target(value))

    def test_period_qualified_roles_without_named_subject_are_rejected(self):
        for value in (
            "2027 revenues",
            "Q2 launches",
        ):
            with self.subTest(value=value):
                self.assertFalse(lineage._structured_exact_target(value))

    def test_complete_v3_rejects_bare_plural_role_target_bypass(self):
        spec = self.base_v3_spec()
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "official filing",
            "exact_claim_or_metric": "revenues",
        }]
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "margins",
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

    def test_plural_role_normalization_does_not_create_subjects_after_modifiers(self):
        for value in (
            "official revenues",
            "company margins",
            "project approvals",
            "documents launches",
        ):
            with self.subTest(value=value):
                self.assertFalse(lineage._structured_exact_target(value))


if __name__ == "__main__":
    unittest.main()
