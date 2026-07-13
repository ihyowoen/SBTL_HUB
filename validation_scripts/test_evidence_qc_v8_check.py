#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CHECKER = Path(__file__).with_name("evidence_qc_v8_check.py")


def source(url: str, owner: str):
    return {
        "source_name": owner,
        "source_url": url,
        "source_quote": "body quote",
        "source_quote_status": "body_quote_verified",
        "evidence_role": "secondary_event_evidence",
        "supports": ["fact"],
        "source_owner_id": owner,
        "source_origin_type": "independent_media_or_trade_press",
    }


def run_checker(payload: dict):
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as handle:
        json.dump(payload, handle)
        path = handle.name
    return subprocess.run([sys.executable, str(CHECKER), path], text=True, capture_output=True)


class EvidenceQcV8CheckTests(unittest.TestCase):
    def test_repeated_claim_rows_same_url_are_informational(self):
        card = {
            "source_spec_id": "SPEC_TEST_001",
            "signal": "high",
            "source_diversity_status": "PASS_MULTI_SOURCE",
            "source_evidence_entry_count": 3,
            "source_unique_url_count": 2,
            "source_independent_owner_count": 2,
            "source_independence_ledger": [
                {"source_owner": "owner-a", "is_independent": True},
                {"source_owner": "owner-b", "is_independent": True},
            ],
            "source_discovery_ledger": [{"query": "same event"}],
            "urls": ["https://a.example/article-a", "https://b.example/article-b"],
            "fact_sources": [
                source("https://a.example/article-a", "owner-a"),
                source("https://a.example/article-a", "owner-a"),
                source("https://b.example/article-b", "owner-b"),
            ],
        }
        result = run_checker({"evidence_complete_and_source_claim_covered": [card]})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("fake_diversity: 0", result.stdout)
        self.assertIn("claim_row_url_reuse_info: 1", result.stdout)

    def test_inflated_declared_unique_url_count_fails(self):
        card = {
            "source_spec_id": "SPEC_TEST_002",
            "signal": "mid",
            "source_diversity_status": "HOLD_NEEDS_SOURCE_AUGMENTATION",
            "source_evidence_entry_count": 2,
            "source_unique_url_count": 2,
            "source_independent_owner_count": 1,
            "urls": ["https://a.example/article-a"],
            "fact_sources": [
                source("https://a.example/article-a", "owner-a"),
                source("https://a.example/article-a", "owner-a"),
            ],
        }
        result = run_checker({"needs_source_augmentation": [card]})
        self.assertEqual(result.returncode, 1)
        self.assertIn("declared source_unique_url_count=2, actual=1", result.stdout)

    def test_pass_multi_source_requires_two_owners(self):
        card = {
            "source_spec_id": "SPEC_TEST_003",
            "signal": "high",
            "source_diversity_status": "PASS_MULTI_SOURCE",
            "source_evidence_entry_count": 2,
            "source_unique_url_count": 2,
            "source_independent_owner_count": 1,
            "source_independence_ledger": [
                {"source_owner": "same-owner", "is_independent": True},
            ],
            "source_discovery_ledger": [{"query": "same event"}],
            "urls": ["https://a.example/article-a", "https://b.example/article-b"],
            "fact_sources": [
                source("https://a.example/article-a", "same-owner"),
                source("https://b.example/article-b", "same-owner"),
            ],
        }
        result = run_checker({"evidence_complete_and_source_claim_covered": [card]})
        self.assertEqual(result.returncode, 1)
        self.assertIn("requires >=2 independent source owners", result.stdout)


if __name__ == "__main__":
    unittest.main()
