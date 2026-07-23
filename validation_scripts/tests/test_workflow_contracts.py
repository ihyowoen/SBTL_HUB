#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from card_audit_utils import (
    canonical_domain,
    canonical_url,
    is_landing_page,
    load_owner_registry,
    source_audit_measure,
    source_owner,
)
from date_role_freshness_check import check_card as check_date_card
from related_lifecycle_check import check_card
from recompute_source_audit_metadata import recompute
from run_workflow_contract_suite import validate_scope


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

    def test_conditional_syndication_registry(self):
        payload = {
            "rules": [
                {
                    "owner_id": "bloomberg_syndication",
                    "domains": ["theedgemalaysia.com"],
                    "requires_metadata_contains_any": ["bloomberg"],
                }
            ]
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "owners.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            registry = load_owner_registry(path)
            syndicated = {
                "source_url": "https://theedgemalaysia.com/node/1",
                "source_owner_id_normalized": "bloomberg_syndication",
            }
            independent = {
                "source_url": "https://theedgemalaysia.com/node/2",
                "source_origin_type": "independent_media",
            }
            self.assertEqual(source_owner(syndicated, registry), "bloomberg_syndication")
            self.assertEqual(source_owner(independent, registry), "theedgemalaysia.com")

    def test_blank_source_url_is_not_counted_as_diversity(self):
        card = {
            "fact_sources": [
                {
                    "source_url": "https://example.com/article",
                    "evidence_role": "primary_event_evidence",
                    "supports": ["fact"],
                },
                {
                    "source_url": "",
                    "evidence_role": "secondary_event_evidence",
                    "supports": ["fact"],
                },
            ]
        }
        measure = source_audit_measure(card, {})
        self.assertEqual(measure["source_evidence_entry_count"], 2)
        self.assertEqual(measure["source_unique_url_count"], 1)
        self.assertEqual(measure["source_unique_domain_count"], 1)
        self.assertEqual(measure["source_independent_owner_count"], 1)
        self.assertEqual(measure["visible_source_url_count"], 1)
        self.assertEqual(measure["missing_visible_source_url_count"], 1)
        self.assertNotIn("https://", measure["canonical_urls"])
        self.assertNotIn("", measure["canonical_domains"])
        self.assertNotIn("", measure["independent_owners"])


class SourceAuditRecomputeTest(unittest.TestCase):
    def test_recompute_preserves_rejected_discovery_rows(self):
        card = {
            "source_spec_id": "TEST",
            "fact_sources": [
                {
                    "source_name": "Official",
                    "source_url": "https://example.gov/article",
                    "source_quote": "Body quote",
                    "source_quote_status": "official_material_quote_verified",
                    "evidence_role": "primary_event_evidence",
                    "supports": ["fact"],
                    "source_origin_type": "government_primary",
                    "claim": "Event occurred",
                }
            ],
            "source_discovery_ledger": [
                {
                    "source_url": "https://media.example/rejected",
                    "outcome": "rejected_wrong_event",
                    "reason": "different event",
                }
            ],
        }
        _, updated, _ = recompute(card, {}, True)
        outcomes = [row.get("outcome") for row in updated["source_discovery_ledger"]]
        self.assertIn("used_in_fact_sources", outcomes)
        self.assertIn("rejected_wrong_event", outcomes)
        used = next(
            row for row in updated["source_discovery_ledger"]
            if row.get("outcome") == "used_in_fact_sources"
        )
        self.assertEqual(used["source_domain"], "example.gov")


class DateRoleContractTest(unittest.TestCase):
    def test_valid_date_role(self):
        card = {
            "date": "2026-07-01",
            "related_lineage": {
                "relation_type": "distinct_follow_up",
                "fresh_follow_up_anchor": "commissioning",
            },
            "date_role": {
                "representative_date": "2026-07-01",
                "event_date": "2026-07-01",
                "publication_dates": ["2026-07-02"],
                "earliest_same_event_date_checked": True,
                "event_date_source_url": "https://example.com/article",
                "event_date_source_quote": "commissioned on July 1",
            },
        }
        self.assertEqual(check_date_card(card, True), [])

    def test_follow_up_requires_anchor(self):
        card = {
            "date": "2026-07-01",
            "related_lineage": {"relation_type": "distinct_follow_up"},
            "date_role": {
                "representative_date": "2026-07-01",
                "event_date": "2026-07-01",
                "publication_dates": ["2026-07-02"],
                "earliest_same_event_date_checked": True,
                "event_date_source_url": "https://example.com/article",
                "event_date_source_quote": "event date",
            },
        }
        self.assertTrue(
            any(
                "fresh_follow_up_anchor" in error
                for error in check_date_card(card, True)
            )
        )


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
        self.child["related_lineage"]["same_event_checked"] = True
        self.child["related_lineage"]["earliest_same_event_date_checked"] = True
        errors, _ = check_card(self.child, self.by_id, True)
        self.assertEqual(errors, [])

    def test_strict_contract_requires_review_flags(self):
        errors, _ = check_card(self.child, self.by_id, True)
        self.assertTrue(any("same_event_checked" in error for error in errors))

    def test_duplicate_cannot_publish(self):
        self.child["related_lineage"]["relation_type"] = "same_event_duplicate"
        errors, _ = check_card(self.child, self.by_id, True)
        self.assertTrue(any("may not use" in error for error in errors))

    def test_non_cardable_relation_rejected_before_publish_state(self):
        child = deepcopy(self.child)
        child.pop("state")
        child.pop("publish_ready")
        child["related_lineage"]["relation_type"] = "same_event_duplicate"
        child["related_lineage"]["same_event_checked"] = True
        child["related_lineage"]["earliest_same_event_date_checked"] = True
        by_id = {self.parent["id"]: self.parent, child["id"]: child}
        errors, _ = check_card(child, by_id, True)
        self.assertTrue(any("validated new-card output" in error for error in errors))

    def test_unrelated_must_not_have_related(self):
        self.child["related_lineage"]["relation_type"] = "new_unrelated_event"
        errors, _ = check_card(self.child, self.by_id, True)
        self.assertTrue(any("empty related" in error for error in errors))


class SuiteScopeTest(unittest.TestCase):
    def write_json(self, directory: str, name: str, payload) -> str:
        path = Path(directory) / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        return str(path)

    def test_scope_requires_all_requested_ids_to_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            cards = self.write_json(
                tmp,
                "cards.json",
                {"cards": [{"id": "A"}, {"id": "B"}]},
            )
            ids = self.write_json(tmp, "ids.json", ["A", "MISSING"])
            result = validate_scope(cards, ids)
            self.assertEqual(result["status"], "FAIL")
            self.assertEqual(result["json"]["matched_card_count"], 1)
            self.assertEqual(result["json"]["missing_ids"], ["MISSING"])

    def test_scope_rejects_zero_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            cards = self.write_json(tmp, "cards.json", {"cards": [{"id": "A"}]})
            ids = self.write_json(tmp, "ids.json", ["MISSING"])
            result = validate_scope(cards, ids)
            self.assertEqual(result["status"], "FAIL")
            self.assertEqual(result["json"]["matched_card_count"], 0)
            self.assertTrue(any("zero cards" in error for error in result["json"]["errors"]))

    def test_scope_rejects_empty_id_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            cards = self.write_json(tmp, "cards.json", {"cards": [{"id": "A"}]})
            ids = self.write_json(tmp, "ids.json", [])
            result = validate_scope(cards, ids)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("empty" in error for error in result["json"]["errors"]))

    def test_scope_passes_when_all_ids_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            cards = self.write_json(
                tmp,
                "cards.json",
                {"cards": [{"id": "A"}, {"id": "B"}]},
            )
            ids = self.write_json(tmp, "ids.json", ["A", "B"])
            result = validate_scope(cards, ids)
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["json"]["requested_id_count"], 2)
            self.assertEqual(result["json"]["matched_card_count"], 2)


if __name__ == "__main__":
    unittest.main()
