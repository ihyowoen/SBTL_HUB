from __future__ import annotations

import copy
import unittest

from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4861791404_contracts as v3_contracts
from validation_scripts.tests import test_review_4862131806_contracts as related_contracts


class TestReview4867268734Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            v3_contracts.TestReview4861791404Contracts().base_v3_spec()
        )

    def test_composite_period_plus_bare_role_is_not_item_specific(self):
        for assertion in (
            "FY2026 revenue",
            "H1 revenue",
            "first quarter revenue",
            "2분기 매출",
            "2026년 매출",
        ):
            with self.subTest(assertion=assertion):
                self.assertFalse(
                    related.item_specific_lineage_assertion(assertion)
                )

    def test_strict_related_rejects_composite_period_only_assertions(self):
        fixture = related_contracts.TestReview4862131806Contracts()
        for assertion in (
            "FY2026 revenue",
            "H1 revenue",
            "first quarter revenue",
            "2분기 매출",
            "2026년 매출",
        ):
            with self.subTest(assertion=assertion):
                fixture._assert_strict_failure(assertion)

    def test_named_composite_period_assertions_remain_valid(self):
        fixture = related_contracts.TestReview4862131806Contracts()
        for assertion in (
            "Project Alpha FY2026 revenue",
            "Project Alpha H1 margin",
            "Project Alpha first quarter revenue",
            "Project Alpha 2분기 매출",
            "Project Alpha 2026년 매출",
        ):
            with self.subTest(assertion=assertion):
                fixture._assert_strict_success(assertion)

    def test_item_specific_plural_exact_targets_pass_prior_gate(self):
        for target in (
            "Project Alpha capacities",
            "Project Alpha margins",
            "Project Alpha approvals",
            "Project Alpha launches",
            "Project A capacities",
            "Project Alpha's capacities",
        ):
            with self.subTest(target=target):
                self.assertTrue(lineage._structured_exact_target(target))

    def test_plural_exact_target_normalization_does_not_create_subjects(self):
        for target in (
            "capacities",
            "official capacities",
            "company margins",
            "documents launches",
        ):
            with self.subTest(target=target):
                self.assertFalse(lineage._structured_exact_target(target))

    def test_complete_v3_accepts_item_specific_plural_targets(self):
        spec = self.base_v3_spec()
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "official filing",
            "exact_claim_or_metric": "Project Alpha capacities",
        }]
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "Project Alpha capacities",
            "interpretation_effect": (
                "The filing would strengthen the current demand outlook"
            ),
        }]
        messages = []
        self.assertTrue(
            lineage.validate_stage_a_v3_override(
                spec, spec["spec_id"], messages
            ),
            messages,
        )


if __name__ == "__main__":
    unittest.main()
