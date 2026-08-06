import unittest

from validation_scripts import related_lifecycle_check as related


class TestReview4871316119Contracts(unittest.TestCase):
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
        self.assertIn("distinct_follow_up requires item-specific fresh_follow_up_anchor", errors)

    def _assert_success(self, assertion):
        self.assertTrue(related.item_specific_lineage_assertion(assertion))
        child, by_id = self._strict_follow_up(assertion)
        errors, warnings = related.check_card(child, by_id, require_contract=True)
        self.assertEqual([], warnings)
        self.assertEqual([], errors)

    def test_unknown_hangul_modifiers_do_not_become_entities(self):
        for assertion in (
            "대폭 설비투자 감축",
            "급격히 영업이익 감소",
            "예상보다 수율 하락",
            "이례적으로 처리량 증가",
        ):
            with self.subTest(assertion=assertion):
                self._assert_failure(assertion)

    def test_positive_korean_entity_signals_remain_supported(self):
        for assertion in (
            "에코프로비엠 설비투자 감축",
            "율촌화학 영업이익 감소",
            "울산 공장 수율 개선",
            "새만금 프로젝트 처리량 증가",
            "산업통상자원부 전망 개선",
        ):
            with self.subTest(assertion=assertion):
                self._assert_success(assertion)


if __name__ == "__main__":
    unittest.main()
