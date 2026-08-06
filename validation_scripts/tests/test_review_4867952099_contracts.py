from __future__ import annotations

import copy
import unittest

from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4861791404_contracts as v3_contracts
from validation_scripts.tests import test_review_4862131806_contracts as related_contracts


class TestReview4867952099Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(
            v3_contracts.TestReview4861791404Contracts().base_v3_spec()
        )

    @staticmethod
    def confirmation_point(effect):
        return {
            "measurable_event_or_metric": "Project Alpha production milestone",
            "interpretation_effect": effect,
        }

    def test_condition_that_and_supposing_do_not_bind_metric_effects(self):
        for effect in (
            "Project Alpha production weakened on condition that the current demand outlook improved",
            "Project Alpha production weakened supposing that the current demand outlook improved",
        ):
            with self.subTest(effect=effect):
                self.assertFalse(lineage._has_bound_interpretation_effect(effect))
                self.assertFalse(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_complete_v3_rejects_condition_that_bypass(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [self.confirmation_point(
            "Project Alpha production weakened on condition that "
            "the current demand outlook improved"
        )]
        messages = []
        self.assertFalse(
            lineage.validate_stage_a_v3_override(
                spec, spec["spec_id"], messages
            )
        )

    def test_leading_condition_that_keeps_real_main_effect(self):
        for effect in (
            "On condition that Project Alpha production improves, "
            "the current demand outlook would strengthen",
            "Supposing that Project Alpha production improves, "
            "the current demand outlook would strengthen",
        ):
            with self.subTest(effect=effect):
                self.assertTrue(lineage._has_bound_interpretation_effect(effect))
                self.assertTrue(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_adjacent_fiscal_modifiers_are_temporal(self):
        cases = (
            ("fiscal q1 revenue", {0, 1}),
            ("calendar q2 revenue", {0, 1}),
            ("fiscal first quarter revenue", {0, 1, 2}),
            ("fy q3 revenue", {0, 1}),
        )
        for assertion, expected_indexes in cases:
            with self.subTest(assertion=assertion):
                tokens = assertion.split()
                self.assertTrue(
                    expected_indexes.issubset(
                        related._assertion_temporal_token_indexes(tokens)
                    )
                )
                self.assertFalse(
                    related.item_specific_lineage_assertion(assertion)
                )

    def test_strict_related_rejects_adjacent_fiscal_period_only_assertions(self):
        fixture = related_contracts.TestReview4862131806Contracts()
        for assertion in (
            "Fiscal Q1 revenue",
            "calendar Q2 revenue",
            "Fiscal first quarter revenue",
            "FY Q3 revenue",
        ):
            with self.subTest(assertion=assertion):
                fixture._assert_strict_failure(assertion)

    def test_named_adjacent_fiscal_period_assertions_remain_valid(self):
        fixture = related_contracts.TestReview4862131806Contracts()
        for assertion in (
            "Project Alpha Fiscal Q1 revenue",
            "Project Alpha calendar Q2 margin",
            "Project Alpha Fiscal first quarter capacity",
            "Project Alpha FY Q3 revenue",
        ):
            with self.subTest(assertion=assertion):
                self.assertTrue(related.item_specific_lineage_assertion(assertion))
                fixture._assert_strict_success(assertion)


if __name__ == "__main__":
    unittest.main()
