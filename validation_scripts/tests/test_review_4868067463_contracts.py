from __future__ import annotations

import copy
import unittest

from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4861791404_contracts as v3_contracts
from validation_scripts.tests import test_review_4862131806_contracts as related_contracts


class TestReview4868067463Contracts(unittest.TestCase):
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

    def test_given_and_contingent_clauses_do_not_bind_metric_effects(self):
        for effect in (
            "Project Alpha production weakened given that the current demand outlook improved",
            "Project Alpha production weakened contingent on the current demand outlook improved",
        ):
            with self.subTest(effect=effect):
                self.assertFalse(lineage._has_bound_interpretation_effect(effect))
                self.assertFalse(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_complete_v3_rejects_given_and_contingent_bypasses(self):
        for effect in (
            "Project Alpha production weakened given that the current demand outlook improved",
            "Project Alpha production weakened contingent on the current demand outlook improved",
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

    def test_leading_given_and_contingent_clauses_keep_real_main_effects(self):
        for effect in (
            "Given that Project Alpha production improves, "
            "the current demand outlook would strengthen",
            "Contingent on Project Alpha production improving, "
            "the current demand outlook would strengthen",
        ):
            with self.subTest(effect=effect):
                self.assertTrue(lineage._has_bound_interpretation_effect(effect))
                self.assertTrue(
                    lineage._valid_confirmation_point(self.confirmation_point(effect))
                )

    def test_fiscal_and_calendar_year_spans_are_temporal(self):
        for assertion in (
            "fiscal year 2026 revenue",
            "calendar year 2027 margin",
        ):
            with self.subTest(assertion=assertion):
                temporal_indexes = related._assertion_temporal_token_indexes(
                    assertion.split()
                )
                self.assertTrue({0, 1, 2}.issubset(temporal_indexes))
                self.assertFalse(
                    related.item_specific_lineage_assertion(assertion)
                )

    def test_strict_related_rejects_fiscal_year_only_assertions(self):
        fixture = related_contracts.TestReview4862131806Contracts()
        for assertion in (
            "Fiscal year 2026 revenue",
            "calendar year 2027 margin",
        ):
            with self.subTest(assertion=assertion):
                fixture._assert_strict_failure(assertion)

    def test_named_fiscal_year_assertions_remain_valid(self):
        fixture = related_contracts.TestReview4862131806Contracts()
        for assertion in (
            "Project Alpha Fiscal year 2026 revenue",
            "Project Alpha calendar year 2027 margin",
        ):
            with self.subTest(assertion=assertion):
                self.assertTrue(related.item_specific_lineage_assertion(assertion))
                fixture._assert_strict_success(assertion)


if __name__ == "__main__":
    unittest.main()
