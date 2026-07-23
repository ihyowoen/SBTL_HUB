#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from card_audit_utils import canonical_domain, canonical_url, is_landing_page
from related_lifecycle_check import check_card


class AuditUtilsTest(unittest.TestCase):
    def test_canonical_url_removes_tracking_and_mobile_prefix(self):
        self.assertEqual(
            canonical_url("https://m.Example.com/a/?utm_source=x&b=2"),
            "https://example.com/a?b=2",
        )

    def test_domain_and_owner_are_distinct_concepts(self):
        domains = {
            canonical_domain("https://pv-magazine-india.com/a"),
            canonical_domain("https://ess-news.com/b"),
            canonical_domain("https://business-standard.com/c"),
        }
        owners = {"pv_magazine_group", "business-standard.com"}
        self.assertEqual(len(domains), 3)
        self.assertEqual(len(owners), 2)

    def test_landing_page(self):
        self.assertTrue(is_landing_page("https://example.com/"))
        self.assertFalse(is_landing_page("https://example.com/2026/07/article"))


class RelatedContractTest(unittest.TestCase):
    def setUp(self):
        self.parent = {"id": "2026-05-01_US_01", "date": "2026-05-01", "related": []}
        self.child = {
            "id": "2026-07-01_US_01",
            "date": "2026-07-01",
            "state": "publish_ready",
            "publish_ready": True,
            "related": [self.parent["id"]],
            "related_lineage": {
                "status": "PASS",
                "relation_type": "distinct_follow_up",
                "related_ids": [self.parent["id"]],
                "reason": "contract followed by commissioning",
                "fresh_follow_up_anchor": "commissioning",
                "related_candidate_spec_ids": [],
            },
        }
        self.by_id = {self.parent["id"]: self.parent, self.child["id"]: self.child}

    def test_valid_follow_up(self):
        errors, _ = check_card(self.child, self.by_id, True)
        self.assertEqual(errors, [])

    def test_duplicate_cannot_publish(self):
        self.child["related_lineage"]["relation_type"] = "same_event_duplicate"
        errors, _ = check_card(self.child, self.by_id, True)
        self.assertTrue(any("may not use" in error for error in errors))

    def test_unrelated_must_not_have_related(self):
        self.child["related_lineage"]["relation_type"] = "new_unrelated_event"
        errors, _ = check_card(self.child, self.by_id, True)
        self.assertTrue(any("empty related" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
