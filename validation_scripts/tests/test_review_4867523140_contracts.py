from __future__ import annotations

import unittest

from validation_scripts import related_lifecycle_check as related
from validation_scripts.tests import test_review_4862131806_contracts as related_contracts


class TestReview4867523140Contracts(unittest.TestCase):
    def test_split_fiscal_and_quarter_markers_are_temporal(self):
        cases = {
            ("fy", "2026", "revenue"): {0, 1},
            ("fiscal", "2026", "revenue"): {0, 1},
            ("q", "1", "revenue"): {0, 1},
        }
        for tokens, expected in cases.items():
            with self.subTest(tokens=tokens):
                self.assertEqual(
                    expected,
                    related._assertion_temporal_token_indexes(list(tokens)),
                )

    def test_split_period_plus_role_is_not_item_specific(self):
        for assertion in (
            "FY 2026 revenue",
            "Fiscal 2026 revenue",
            "Q 1 revenue",
        ):
            with self.subTest(assertion=assertion):
                self.assertFalse(related.item_specific_lineage_assertion(assertion))

    def test_strict_related_rejects_split_period_only_assertions(self):
        fixture = related_contracts.TestReview4862131806Contracts()
        for assertion in (
            "FY 2026 revenue",
            "Fiscal 2026 revenue",
            "Q 1 revenue",
        ):
            with self.subTest(assertion=assertion):
                fixture._assert_strict_failure(assertion)

    def test_named_split_period_assertions_remain_valid(self):
        fixture = related_contracts.TestReview4862131806Contracts()
        for assertion in (
            "Project Alpha FY 2026 revenue",
            "Project Alpha Fiscal 2026 margin",
            "Project Alpha Q 1 capacity",
        ):
            with self.subTest(assertion=assertion):
                fixture._assert_strict_success(assertion)


if __name__ == "__main__":
    unittest.main()
