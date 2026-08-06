import unittest

from validation_scripts import related_lifecycle_check as related


class TestReview4871397803Contracts(unittest.TestCase):
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

    def test_comparative_period_acronyms_are_not_entities(self):
        for assertion in (
            "YOY profit decline",
            "QOQ EBITDA improvement",
            "TTM capex reduction",
            "YTD throughput growth",
        ):
            with self.subTest(assertion=assertion):
                self._assert_strict_failure(assertion)

    def test_real_acronym_and_named_period_subjects_remain_valid(self):
        for assertion in (
            "SBTL profit decline",
            "Project Alpha YOY profit decline",
            "Tesla QOQ EBITDA improvement",
        ):
            with self.subTest(assertion=assertion):
                self._assert_strict_success(assertion)

    def test_generic_korean_class_modifiers_are_not_identifiers(self):
        for assertion in (
            "대형 공장 수율 개선",
            "신설 공장 수율 개선",
            "주요 프로젝트 처리량 증가",
        ):
            with self.subTest(assertion=assertion):
                self._assert_strict_failure(assertion)

    def test_named_korean_class_bound_subjects_remain_valid(self):
        for assertion in (
            "울산 공장 수율 개선",
            "새만금 프로젝트 처리량 증가",
            "삼성 공장 수율 개선",
            "제1 공장 수율 개선",
        ):
            with self.subTest(assertion=assertion):
                self._assert_strict_success(assertion)


if __name__ == "__main__":
    unittest.main()
