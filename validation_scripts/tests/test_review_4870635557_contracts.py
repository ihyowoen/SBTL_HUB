import unittest

from validation_scripts import related_lifecycle_check as related


class TestReview4870635557Contracts(unittest.TestCase):
    """Regressions for metric specificity and concrete entity labels."""

    @staticmethod
    def _strict_follow_up(assertion):
        parent = {
            "id": "PARENT",
            "date": "2026-04-01",
            "related": [],
        }
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

    def _assert_strict_failure(self, assertion):
        self.assertFalse(related.item_specific_lineage_assertion(assertion))
        child, by_id = self._strict_follow_up(assertion)
        errors, warnings = related.check_card(child, by_id, require_contract=True)
        self.assertEqual([], warnings)
        self.assertIn(
            "distinct_follow_up requires item-specific fresh_follow_up_anchor",
            errors,
        )
        self.assertIn(
            "distinct_follow_up requires item-specific incremental_fact_vs_predecessor",
            errors,
        )
        self.assertIn(
            "distinct_follow_up requires item-specific changed_judgment_vs_predecessor",
            errors,
        )

    def _assert_strict_success(self, assertion):
        self.assertTrue(related.item_specific_lineage_assertion(assertion))
        child, by_id = self._strict_follow_up(assertion)
        errors, warnings = related.check_card(child, by_id, require_contract=True)
        self.assertEqual([], warnings)
        self.assertEqual([], errors)

    def test_metric_nouns_without_a_development_fail(self):
        assertions = (
            "Tesla profit",
            "Tesla capex",
            "Acme yield",
            "Project A profit",
            "Plant 1 capex",
        )
        for assertion in assertions:
            with self.subTest(assertion=assertion):
                self._assert_strict_failure(assertion)

    def test_scoped_or_developed_metric_assertions_pass(self):
        assertions = (
            "Tesla profit increased",
            "Tesla Q2 profit 10%",
            "Tesla FY2026 profit",
            "Project Alpha Q2 EBITDA",
            "Project A capex reduced",
            "Plant 1 yield 95%",
            "Acme profit guidance",
            "SBTL 영업이익 증가",
        )
        for assertion in assertions:
            with self.subTest(assertion=assertion):
                self._assert_strict_success(assertion)

    def test_concrete_numbered_entity_judgment_changes_pass(self):
        assertions = (
            "Project A outlook weakened",
            "Plant 1 outlook weakened",
            "Facility 2 risk increased",
            "공장 1 전망 약화",
        )
        for assertion in assertions:
            with self.subTest(assertion=assertion):
                self._assert_strict_success(assertion)

    def test_generic_judgment_changes_without_subject_still_fail(self):
        assertions = (
            "outlook weakened",
            "risk increased",
            "전망 약화",
        )
        for assertion in assertions:
            with self.subTest(assertion=assertion):
                self._assert_strict_failure(assertion)


if __name__ == "__main__":
    unittest.main()
