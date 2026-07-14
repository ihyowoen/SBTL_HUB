#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CHECKER = Path(__file__).with_name("validate_search_before_delete.py")


def audit(**overrides):
    payload = {
        "claim_gap_id": "G1",
        "original_claim": "Original claim",
        "affected_fields": ["summary"],
        "full_existing_source_packet_checked": True,
        "cited_source_refetch_attempted": True,
        "official_or_primary_search_attempted": True,
        "independent_tier1_tier2_search_attempted": True,
        "search_queries": ["same event original claim"],
        "searched_urls": ["https://example.com/article"],
        "source_discovery_result": "not_found_after_bounded_search",
        "recovered_sources": [],
        "recovered_quotes": [],
        "claim_repair_before_deletion_check": "PASS",
        "final_claim_disposition": "deleted_after_search",
        "final_disposition_reason": "No same-event support found.",
    }
    payload.update(overrides)
    return payload


def run_checker(payload: dict):
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as handle:
        json.dump(payload, handle)
        path = handle.name
    return subprocess.run([sys.executable, str(CHECKER), path], text=True, capture_output=True)


class SearchBeforeDeleteTests(unittest.TestCase):
    def test_negative_reference_row_can_point_to_complete_audit(self):
        payload = {
            "claim_search_audits": [audit()],
            "revise_blocked_evidence_gap": [
                {"claim_gap_id": "G1", "decision": "delete unsupported sentence"}
            ],
        }
        result = run_checker(payload)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS_SEARCH_BEFORE_DELETE_AUDIT", result.stdout)

    def test_evidence_qc_hold_bucket_requires_audit_without_heuristic_text(self):
        payload = {
            "needs_source_augmentation": [
                {"id": "x", "state": "needs_source_augmentation"}
            ]
        }
        result = run_checker(payload)
        self.assertEqual(result.returncode, 1)
        self.assertIn("negative/reduction outcome lacks a valid claim-level", result.stdout)

    def test_reduction_keywords_do_not_match_inside_benign_words(self):
        payload = {
            "metadata": {
                "notes": "Stakeholder threshold discussion mentions blockchain context."
            }
        }
        result = run_checker(payload)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_supported_results_require_recovered_sources_and_quotes(self):
        payload = {
            "claim_search_audits": [
                audit(
                    source_discovery_result="supported_and_narrowed",
                    final_claim_disposition="narrowed_after_search",
                    recovered_sources=[],
                    recovered_quotes=[],
                )
            ]
        }
        result = run_checker(payload)
        self.assertEqual(result.returncode, 1)
        self.assertIn("recovered_sources: must be a non-empty list", result.stdout)
        self.assertIn("recovered_quotes: must be a non-empty list", result.stdout)

    def test_supported_results_pass_with_recovered_evidence(self):
        payload = {
            "claim_search_audits": [
                audit(
                    source_discovery_result="supported_and_restored",
                    final_claim_disposition="restored",
                    recovered_sources=[{"url": "https://example.com/article"}],
                    recovered_quotes=["Body-level quote supporting the claim."],
                )
            ]
        }
        result = run_checker(payload)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
