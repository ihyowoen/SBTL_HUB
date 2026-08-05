import unittest

from validation_scripts import related_lifecycle_check as related


class TestReview4862131806Contracts(unittest.TestCase):
    """Focused regressions for the two Related assertion review findings."""

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
                "reason": "The new verified data materially changes the predecessor assessment.",
                "same_event_checked": True,
                "earliest_same_event_date_checked": True,
                "fresh_follow_up_anchor_class": "data_financial_anchor",
                "fresh_follow_up_anchor": assertion,
                "incremental_fact_vs_predecessor": assertion,
                "changed_judgment_vs_predecessor": assertion,
            },
        }
        return child, {"PARENT": parent, "CHILD": child}

    def test_neutral_words_do_not_become_follow_up_subjects(self):
        assertions = (
            "the Q2 revenue",
            "official Q2 revenue",
            "company 2026 revenue",
        )
        for assertion in assertions:
            with self.subTest(assertion=assertion):
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

    def test_full_related_data_financial_roles_are_accepted(self):
        assertions = (
            "Project Alpha Q2 operating data",
            "Project Alpha Q2 shipment",
            "Project Alpha Q2 price",
            "Project Alpha Q2 inventory",
            "Project Alpha Q2 utilisation",
            "Project Alpha Q2 utilization",
            "Project Alpha Q2 safety data",
            "Project Alpha Q2 market data",
        )
        for assertion in assertions:
            with self.subTest(assertion=assertion):
                self.assertTrue(related.item_specific_lineage_assertion(assertion))
                child, by_id = self._strict_follow_up(assertion)
                errors, warnings = related.check_card(child, by_id, require_contract=True)
                self.assertEqual([], warnings)
                self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
