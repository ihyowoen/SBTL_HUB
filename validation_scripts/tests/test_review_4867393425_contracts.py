from __future__ import annotations

import unittest

from validation_scripts import related_lifecycle_check as related
from validation_scripts.tests import test_review_4862131806_contracts as related_contracts


class TestReview4867393425Contracts(unittest.TestCase):
    def test_number_first_quarter_labels_are_temporal_tokens(self):
        for token in ("1q", "1q2026", "3qfy26", "4qfy2026"):
            with self.subTest(token=token):
                self.assertEqual(
                    {0}, related._assertion_temporal_token_indexes([token, "revenue"])
                )

    def test_number_first_quarter_plus_role_is_not_item_specific(self):
        for assertion in (
            "1Q revenue",
            "1Q2026 revenue",
            "3QFY26 revenue",
            "4QFY2026 revenue",
        ):
            with self.subTest(assertion=assertion):
                self.assertFalse(
                    related.item_specific_lineage_assertion(assertion)
                )

    def test_strict_related_rejects_number_first_quarter_only_assertions(self):
        fixture = related_contracts.TestReview4862131806Contracts()
        for assertion in (
            "1Q revenue",
            "1Q2026 revenue",
            "3QFY26 revenue",
            "4QFY2026 revenue",
        ):
            with self.subTest(assertion=assertion):
                fixture._assert_strict_failure(assertion)

    def test_named_number_first_quarter_assertions_remain_valid(self):
        fixture = related_contracts.TestReview4862131806Contracts()
        for assertion in (
            "Project Alpha 1Q revenue",
            "Project Alpha 1Q2026 margin",
            "Project Alpha 3QFY26 capacity",
            "Project Alpha 4QFY2026 forecast",
        ):
            with self.subTest(assertion=assertion):
                fixture._assert_strict_success(assertion)


if __name__ == "__main__":
    unittest.main()
