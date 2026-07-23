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

from card_audit_utils import select_scoped_cards, source_audit_measure
from recompute_source_audit_metadata import HOLD, recompute


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def run_validator(script: str, cards, ids, *extra: str):
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        cards_path = tmp_path / "cards.json"
        ids_path = tmp_path / "ids.json"
        write_json(cards_path, cards)
        write_json(ids_path, ids)
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / script),
                str(cards_path),
                "--new-id-file",
                str(ids_path),
                *extra,
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        return completed, json.loads(completed.stdout)


class ExactScopeTest(unittest.TestCase):
    def test_scope_accepts_exact_and_rejects_empty_zero_partial(self):
        cards = [{"id": "A"}, {"id": "B"}]
        rows, exact = select_scoped_cards(cards, {"A", "B"})
        self.assertEqual(exact["status"], "PASS")
        self.assertEqual(len(rows), 2)

        _, empty = select_scoped_cards(cards, set())
        self.assertEqual(empty["status"], "FAIL")
        self.assertIn("ID scope is empty", empty["errors"])

        _, zero = select_scoped_cards(cards, {"Z"})
        self.assertEqual(zero["status"], "FAIL")
        self.assertIn("ID scope matched zero cards", zero["errors"])

        rows, partial = select_scoped_cards(cards, {"A", "Z"})
        self.assertEqual([row["id"] for row in rows], ["A"])
        self.assertEqual(partial["status"], "FAIL")
        self.assertEqual(partial["missing_ids"], ["Z"])

    def test_each_scoped_validator_fails_bad_scope(self):
        cards = {"cards": [{"id": "A", "related": [], "date": "2026-07-01"}]}
        cases = (
            ("evidence_qc_v8_check.py", ["Z"], ()),
            ("related_lifecycle_check.py", ["A", "Z"], ("--require-contract",)),
            ("date_role_freshness_check.py", [], ("--require-date-role",)),
        )
        for script, ids, extra in cases:
            completed, report = run_validator(script, cards, ids, *extra)
            self.assertNotEqual(completed.returncode, 0, script)
            self.assertEqual(report["id_scope"]["status"], "FAIL", script)


class DomainOwnerSemanticsTest(unittest.TestCase):
    def test_multiple_owners_may_share_one_domain(self):
        card = {
            "fact_sources": [
                {
                    "source_url": "https://records.example/doc/1",
                    "source_owner_id_normalized": "court_a",
                    "evidence_role": "primary_event_evidence",
                    "supports": ["fact"],
                },
                {
                    "source_url": "https://records.example/doc/2",
                    "source_owner_id_normalized": "court_b",
                    "evidence_role": "primary_event_evidence",
                    "supports": ["fact"],
                },
            ]
        }
        measure = source_audit_measure(card, {})
        self.assertEqual(measure["source_unique_domain_count"], 1)
        self.assertEqual(measure["source_independent_owner_count"], 2)

    def test_evidence_validator_accepts_owners_above_domains(self):
        urls = ["https://records.example/doc/1", "https://records.example/doc/2"]
        sources = [
            {
                "source_name": "Court A",
                "source_url": urls[0],
                "source_owner_id_normalized": "court_a",
                "source_quote": "order one",
                "source_quote_status": "official_material_quote_verified",
                "evidence_role": "primary_event_evidence",
                "supports": ["fact"],
            },
            {
                "source_name": "Court B",
                "source_url": urls[1],
                "source_owner_id_normalized": "court_b",
                "source_quote": "order two",
                "source_quote_status": "official_material_quote_verified",
                "evidence_role": "primary_event_evidence",
                "supports": ["fact"],
            },
        ]
        card = {
            "id": "CARD",
            "signal": "mid",
            "urls": urls,
            "fact_sources": sources,
            "source_diversity_status": "PASS_MULTI_SOURCE",
            "source_evidence_entry_count": 2,
            "source_unique_url_count": 2,
            "source_unique_domain_count": 1,
            "source_independent_owner_count": 2,
            "source_discovery_ledger": [{"outcome": "used_in_fact_sources"}],
            "source_url_resolution": {
                "supporting_fact_source_count": 2,
                "resolution_entries": [{"source_url": url} for url in urls],
            },
        }
        completed, report = run_validator(
            "evidence_qc_v8_check.py", {"cards": [card]}, ["CARD"]
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(report["total_flags"], 0)


class BoundedExceptionTest(unittest.TestCase):
    @staticmethod
    def source():
        return {
            "source_name": "Official",
            "source_url": "https://agency.gov/article",
            "source_quote": "official statement",
            "source_quote_status": "official_material_quote_verified",
            "evidence_role": "primary_event_evidence",
            "source_origin_type": "government_primary",
            "supports": ["fact"],
        }

    def test_strict_recompute_rejects_incomplete_legacy_exception(self):
        card = {
            "source_spec_id": "TEST",
            "fact_sources": [self.source()],
            "single_source_exception": {
                "allowed": True,
                "reason": "legacy reason only",
            },
        }
        _, updated, _ = recompute(card, {}, True)
        self.assertEqual(updated["source_diversity_status"], HOLD)
        self.assertFalse(updated["single_source_exception"]["allowed"])

    def test_strict_recompute_preserves_complete_exception(self):
        card = {
            "source_spec_id": "TEST",
            "fact_sources": [self.source()],
            "single_source_exception": {
                "allowed": True,
                "reason": "bounded official source",
                "mitigation": "no market-performance expansion",
            },
        }
        _, updated, _ = recompute(card, {}, True)
        self.assertEqual(
            updated["source_diversity_status"],
            "PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION",
        )


if __name__ == "__main__":
    unittest.main()
