import unittest

from validation_scripts import related_lifecycle_check as related


class TestLatestRelatedSubjectRegressions(unittest.TestCase):
    @staticmethod
    def _strict_follow_up(assertion):
        parent = {"id": "PARENT", "date": "2026-04-01", "related": []}
        child = {
            "id": "CHILD",
            "date": "2026-07-01",
            "related": ["PARENT"],
            "publish_ready": True,
            "related_lineage": {
                "status": "PASS",
                "relation_type": "distinct_follow_up",
                "related_ids": ["PARENT"],
                "reason": "The verified development changes the predecessor assessment.",
                "same_event_checked": True,
                "earliest_same_event_date_checked": True,
                "fresh_follow_up_anchor_class": "data_financial_anchor",
                "fresh_follow_up_anchor": assertion,
                "incremental_fact_vs_predecessor": assertion,
                "changed_judgment_vs_predecessor": assertion,
            },
        }
        return child, {"PARENT": parent, "CHILD": child}

    def _assert_failure(self, assertion):
        self.assertFalse(related.item_specific_lineage_assertion(assertion))
        child, by_id = self._strict_follow_up(assertion)
        errors, warnings = related.check_card(child, by_id, require_contract=True)
        self.assertEqual([], warnings)
        self.assertIn(
            "distinct_follow_up requires item-specific fresh_follow_up_anchor",
            errors,
        )

    def _assert_success(self, assertion):
        self.assertTrue(related.item_specific_lineage_assertion(assertion))
        child, by_id = self._strict_follow_up(assertion)
        errors, warnings = related.check_card(child, by_id, require_contract=True)
        self.assertEqual([], warnings)
        self.assertEqual([], errors)

    def test_standalone_fiscal_period_terms_are_not_entities(self):
        for assertion in (
            "FY profit decline",
            "CY EBITDA improvement",
            "YOY yield decline",
        ):
            with self.subTest(assertion=assertion):
                self._assert_failure(assertion)

    def test_concrete_labels_with_comparative_scopes_remain_valid(self):
        for assertion in (
            "Project A YOY profit decline",
            "Plant 1 YOY profit decline",
            "Facility 2 QOQ EBITDA improvement",
        ):
            with self.subTest(assertion=assertion):
                self._assert_success(assertion)

    def test_unseen_single_token_company_names_are_supported(self):
        for assertion in (
            "Panasonic capex reduction",
            "Ford profit decline",
            "Toyota yield improvement",
        ):
            with self.subTest(assertion=assertion):
                self._assert_success(assertion)

    def test_title_case_modifier_pairs_do_not_become_entities(self):
        for assertion in (
            "First Ever profit decline",
            "Extraordinary Novel capex reduction",
        ):
            with self.subTest(assertion=assertion):
                self._assert_failure(assertion)

    def test_recurring_period_adjectives_scope_named_metrics(self):
        for assertion in (
            "Tesla quarterly profit",
            "Project Alpha monthly throughput",
            "Plant 1 weekly yield",
        ):
            with self.subTest(assertion=assertion):
                self._assert_success(assertion)

    def test_spelled_out_percentages_are_measured_values(self):
        for assertion in (
            "Plant 1 yield 95 percent",
            "Tesla yield 95 percentage",
            "울산 공장 수율 95 퍼센트",
        ):
            with self.subTest(assertion=assertion):
                self._assert_success(assertion)


if __name__ == "__main__":
    unittest.main()
