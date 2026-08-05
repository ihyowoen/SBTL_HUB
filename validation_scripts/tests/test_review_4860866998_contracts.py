from __future__ import annotations

import copy
import unittest

from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4840844831_contracts as prior_contracts


class TestReview4860866998Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(prior_contracts.TestReview4840844831Contracts().base_spec())

    def test_generic_modifiers_do_not_make_exact_targets_item_specific(self):
        for value in (
            "official revenue",
            "company revenue",
            "corporate capacity",
            "project launch",
            "current margin",
        ):
            with self.subTest(value=value):
                self.assertFalse(lineage._structured_exact_target(value))

    def test_named_numeric_and_predicate_targets_remain_valid(self):
        for value in (
            "Project Alpha revenue",
            "Project Alpha 2027 revenue",
            "Project Alpha was approved",
            "Project Alpha launch date",
        ):
            with self.subTest(value=value):
                self.assertTrue(lineage._structured_exact_target(value))

    def test_complete_v3_rejects_generic_modifier_targets(self):
        spec = self.base_v3_spec()
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "official filing",
            "exact_claim_or_metric": "company revenue",
        }]
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "official revenue",
            "interpretation_effect": "would weaken the demand outlook",
        }]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages)
        )

    def test_entity_only_follow_up_assertions_fail(self):
        for value in ("Project Alpha", "Company Beta", "프로젝트 알파"):
            with self.subTest(value=value):
                self.assertFalse(related.item_specific_lineage_assertion(value))

    def test_substantive_follow_up_assertions_pass(self):
        for value in (
            "DOE approved Project Alpha eligibility on 2026-08-04",
            "The August filing added 6 GWh of contracted volume",
            "The judgment changed from announced target to financed execution",
        ):
            with self.subTest(value=value):
                self.assertTrue(related.item_specific_lineage_assertion(value))


if __name__ == "__main__":
    unittest.main()
