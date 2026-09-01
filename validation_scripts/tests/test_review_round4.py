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
                "fact_sources": [
                    {
                        "source_url": "https://example.com/news/2026/project-update",
                        "evidence_role": "primary_event_evidence",
                    }
                ],
                "related_evidence_review": {
                    "status": "PASS",
                    "same_event_checked": True,
                    "relation_type": "new_unrelated_event",
                },
                "date_role": {
                    "representative_date": "2026-09-01",
                    "representative_date_type": "event_date",
                },
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
                    "source_url": "https://example.com/newsroom",
                    "source_owner_id_normalized": "owner_b",
                    "evidence_role": "independent_confirmation",
                    "supports": ["fact"],
                },
            ]
        }
        measure = source_audit_measure(card)
        self.assertEqual(measure["usable_source_count"], 1)
        self.assertEqual(measure["owner_count"], 1)
        self.assertEqual(measure["domain_count"], 1)

    def test_evidence_validator_blocks_listing_endpoint_as_multi_source(self):
        card = {
            "id": "CARD-1",
            "urls": [
                "https://example.com/newsroom/article-one",
                "https://example.com/newsroom",
            ],
            "fact_sources": [
                {
                    "source_url": "https://example.com/newsroom/article-one",
                    "source_owner_id_normalized": "owner_a",
                    "evidence_role": "primary_event_evidence",
                    "supports": ["fact"],
                },
                {
                    "source_url": "https://example.com/newsroom",
                    "source_owner_id_normalized": "owner_b",
                    "evidence_role": "independent_confirmation",
                    "supports": ["fact"],
                },
            ],
            "source_audit": {
                "source_diversity_measure": {
                    "usable_source_count": 2,
                    "owner_count": 2,
                    "domain_count": 1,
                },
                "source_diversity_status": "PASS_MULTI_SOURCE",
                "source_diversity_required": True,
                "augmentation_required": False,
            },
        }
        completed, report = run_json(
            [str(SCRIPTS / "evidence_qc_v8_check.py")],
            {"cards": [card]},
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(report["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
