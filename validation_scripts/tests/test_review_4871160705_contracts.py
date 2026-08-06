import unittest

from validation_scripts import related_lifecycle_check as related


class TestReview4871160705Contracts(unittest.TestCase):
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

    def test_sentence_initial_modifiers_are_not_entity_subjects(self):
        for assertion in (
            "Unexpected capex reduction",
            "Severe profit decline",
            "Historic throughput growth",
            "Dramatic yield improvement",
            "Sudden EBITDA decline",
            "Record capex reduction",
            "Unexpected Novel capex reduction",
        ):
            with self.subTest(assertion=assertion):
                self._assert_failure(assertion)

    def test_positive_entity_signals_remain_supported(self):
        for assertion in (
            "Tesla capex reduction",
            "Acme profit improvement",
            "Tesla's capex reduction",
            "SBTL 영업이익 개선",
            "Project Alpha throughput growth",
            "Plant 1 yield decline",
            "Panasonic Energy capex reduction",
        ):
            with self.subTest(assertion=assertion):
                self._assert_success(assertion)


if __name__ == "__main__":
    unittest.main()
