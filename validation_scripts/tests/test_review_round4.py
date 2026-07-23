#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

from card_audit_utils import canonical_url, is_landing_page, source_audit_measure


STAGE_B_TOP_LEVEL = {
    "lineage_integrity_status": "PASS",
    "stage_a_validity_guard_applied": True,
    "strict_gate_metadata_preserved": True,
    "execution_anchor_metadata_preserved": True,
    "superseded_lineage_mixed": False,
    "manual_integrated_rule_mixed": False,
    "previous_run_output_mixed": False,
}


def run_json(command: list[str], payload) -> tuple[subprocess.CompletedProcess[str], dict]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "input.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, *command, str(path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        return completed, json.loads(completed.stdout)


class SingularStageBArtifactTest(unittest.TestCase):
    def test_noncompliant_singular_draft_card_is_collected_and_blocked(self):
        payload = {
            **STAGE_B_TOP_LEVEL,
            "draft_card": {"source_spec_id": "SPEC-1"},
        }
        completed, report = run_json(
            [str(SCRIPTS / "stage_artifact_contract_check.py"), "B"],
            payload,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(report["item_count"], 1)
        self.assertEqual(report["status"], "BLOCKED_STAGE_OUTPUT_SCHEMA_NONCOMPLIANT")
        missing = {row["field"] for row in report["findings"]}
        self.assertTrue({"fact_sources", "related_evidence_review", "date_role"} <= missing)

    def test_compliant_singular_draft_card_passes(self):
        payload = {
            **STAGE_B_TOP_LEVEL,
            "draft_card": {
                "source_spec_id": "SPEC-1",
                "fact_sources": [],
                "related_evidence_review": {},
                "date_role": {},
            },
        }
        completed, report = run_json(
            [str(SCRIPTS / "stage_artifact_contract_check.py"), "B"],
            payload,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(report["item_count"], 1)
        self.assertEqual(report["status"], "PASS")


class DurableEvidenceEndpointTest(unittest.TestCase):
    def test_search_listing_and_category_endpoints_are_rejected(self):
        invalid = (
            "https://example.com/search?q=storage",
            "https://example.com/newsroom",
            "https://example.com/category/storage",
            "https://example.com/news/page/2",
            "https://example.com/tag/battery",
        )
        for url in invalid:
            self.assertTrue(is_landing_page(url), url)
            self.assertEqual(canonical_url(url), "", url)

    def test_article_paths_below_collection_roots_remain_valid(self):
        valid = (
            "https://example.com/newsroom/2026/project-financing-closes",
            "https://example.com/news/2026/07/project-update",
            "https://example.com/press-releases/company-signs-contract",
        )
        for url in valid:
            self.assertFalse(is_landing_page(url), url)
            self.assertTrue(canonical_url(url), url)

    def test_listing_source_is_excluded_from_diversity_counts(self):
        card = {
            "fact_sources": [
                {
                    "source_url": "https://example.com/newsroom/article-one",
                    "source_owner_id_normalized": "owner_a",
                    "evidence_role": "primary_event_evidence",
                    "supports": ["fact"],
                },
                {
                    "source_url": "https://example.org/category/storage",
                    "source_owner_id_normalized": "owner_b",
                    "evidence_role": "secondary_event_evidence",
                    "supports": ["fact"],
                },
            ]
        }
        measure = source_audit_measure(card, {})
        self.assertEqual(measure["source_unique_url_count"], 1)
        self.assertEqual(measure["source_unique_domain_count"], 1)
        self.assertEqual(measure["source_independent_owner_count"], 1)
        self.assertEqual(measure["missing_source_url_count"], 1)
        self.assertEqual(measure["missing_visible_source_url_count"], 1)

    def test_evidence_validator_blocks_listing_endpoint_as_multi_source(self):
        article = "https://example.com/newsroom/article-one"
        listing = "https://example.org/category/storage"
        card = {
            "id": "CARD",
            "signal": "mid",
            "urls": [article, listing],
            "fact_sources": [
                {
                    "source_name": "Article",
                    "source_url": article,
                    "source_owner_id_normalized": "owner_a",
                    "source_quote": "article quote",
                    "source_quote_status": "body_quote_verified",
                    "evidence_role": "primary_event_evidence",
                    "supports": ["fact"],
                },
                {
                    "source_name": "Category page",
                    "source_url": listing,
                    "source_owner_id_normalized": "owner_b",
                    "source_quote": "listing text",
                    "source_quote_status": "body_quote_verified",
                    "evidence_role": "secondary_event_evidence",
                    "supports": ["fact"],
                },
            ],
            "source_diversity_status": "PASS_MULTI_SOURCE",
            "source_evidence_entry_count": 2,
            "source_unique_url_count": 1,
            "source_unique_domain_count": 1,
            "source_independent_owner_count": 1,
            "source_discovery_ledger": [{"outcome": "used_in_fact_sources"}],
            "source_url_resolution": {
                "supporting_fact_source_count": 2,
                "resolution_entries": [{"source_url": article}],
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cards.json"
            path.write_text(json.dumps({"cards": [card]}), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "evidence_qc_v8_check.py"),
                    str(path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            report = json.loads(completed.stdout)
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(report["flags"]["landing_page"], 1)
        self.assertGreater(report["flags"]["invalid_source_diversity_status"], 0)


if __name__ == "__main__":
    unittest.main()
