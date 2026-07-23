#!/usr/bin/env python3
"""Apply the third Codex review fixes to PR #207 exactly once."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one replacement target, found {count}")
    target.write_text(text.replace(old, new), encoding="utf-8")


def insert_before(path: str, marker: str, block: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if block in text:
        return
    count = text.count(marker)
    if count != 1:
        raise RuntimeError(f"{path}: expected one insertion marker, found {count}")
    target.write_text(text.replace(marker, block + marker), encoding="utf-8")


# Shared exact-scope contract.
insert_before(
    "validation_scripts/card_audit_utils.py",
    "def dedupe(values: Iterable[str]) -> list[str]:\n",
    '''def card_identifier(card: dict[str, Any]) -> str:\n    return str(card.get("id") or card.get("card_id") or "").strip()\n\n\ndef select_scoped_cards(\n    cards: Iterable[dict[str, Any]],\n    selected_ids: set[str] | None,\n) -> tuple[list[dict[str, Any]], dict[str, Any]]:\n    rows = list(cards)\n    if selected_ids is None:\n        return rows, {\n            "applied": False,\n            "status": "NOT_APPLIED",\n            "requested_count": None,\n            "matched_count": len(rows),\n            "missing_ids": [],\n            "errors": [],\n        }\n\n    requested = {str(value).strip() for value in selected_ids if str(value).strip()}\n    available = {card_identifier(card) for card in rows if card_identifier(card)}\n    matched = requested & available\n    missing = sorted(requested - available)\n    errors: list[str] = []\n    if not requested:\n        errors.append("ID scope is empty")\n    elif not matched:\n        errors.append("ID scope matched zero cards")\n    if missing:\n        errors.append(f"ID scope has {len(missing)} unmatched ID(s)")\n\n    selected_rows = [card for card in rows if card_identifier(card) in matched]\n    return selected_rows, {\n        "applied": True,\n        "status": "PASS" if not errors else "FAIL",\n        "requested_count": len(requested),\n        "matched_count": len(matched),\n        "missing_ids": missing,\n        "errors": errors,\n    }\n\n\n''',
)

# Evidence QC: direct scope enforcement, invalid URL flags, no domain/owner ordering.
replace_once(
    "validation_scripts/evidence_qc_v8_check.py",
    '''    load_owner_registry,\n    source_audit_measure,\n    usable_sources,\n)\n''',
    '''    load_owner_registry,\n    select_scoped_cards,\n    source_audit_measure,\n    usable_sources,\n)\n''',
)
replace_once(
    "validation_scripts/evidence_qc_v8_check.py",
    '''    rows = cards(load(args.input))\n    selected_ids = load_ids(args.id_file)\n    if selected_ids is not None:\n        rows = [\n            card for card in rows\n            if str(card.get("id") or card.get("card_id") or "") in selected_ids\n        ]\n    names = (\n        "landing_page", "fake_diversity", "weak_corroboration", "url_desync",\n        "invalid_source_diversity_status", "missing_source_discovery_ledger",\n        "domain_owner_semantics", "resolution_mismatch",\n    )\n    flags = {name: [] for name in names}\n    reuse = []\n''',
    '''    rows = cards(load(args.input))\n    selected_ids = load_ids(args.id_file)\n    rows, scope = select_scoped_cards(rows, selected_ids)\n    names = (\n        "invalid_id_scope", "invalid_source_url", "landing_page",\n        "fake_diversity", "weak_corroboration", "url_desync",\n        "invalid_source_diversity_status", "missing_source_discovery_ledger",\n        "resolution_mismatch",\n    )\n    flags = {name: [] for name in names}\n    for message in scope["errors"]:\n        flags["invalid_id_scope"].append(("<id-scope>", message))\n    reuse = []\n''',
)
replace_once(
    "validation_scripts/evidence_qc_v8_check.py",
    '''        measure = source_audit_measure(card, registry)\n        source_urls = [source.get("source_url") for source in sources if source.get("source_url")]\n''',
    '''        measure = source_audit_measure(card, registry)\n        if measure["missing_source_url_count"]:\n            flags["invalid_source_url"].append(\n                (cid, f"{measure['missing_source_url_count']} usable source row(s) lack a durable HTTP(S) URL")\n            )\n        if measure["missing_visible_source_url_count"]:\n            flags["invalid_source_url"].append(\n                (cid, f"{measure['missing_visible_source_url_count']} visible source row(s) lack a durable HTTP(S) URL")\n            )\n        source_urls = [source.get("source_url") for source in sources if source.get("source_url")]\n''',
)
replace_once(
    "validation_scripts/evidence_qc_v8_check.py",
    '''        if measure["source_unique_domain_count"] < measure["source_independent_owner_count"]:\n            flags["domain_owner_semantics"].append(\n                (cid, "unique domain count cannot be below independent owner count")\n            )\n''',
    "",
)
replace_once(
    "validation_scripts/evidence_qc_v8_check.py",
    '''            resolved_urls = {\n                canonical_url(str(entry.get("source_url", "")))\n                for entry in entries if isinstance(entry, dict)\n            }\n''',
    '''            resolved_urls = {\n                value\n                for entry in entries\n                if isinstance(entry, dict)\n                and (value := canonical_url(str(entry.get("source_url", ""))))\n            }\n''',
)
replace_once(
    "validation_scripts/evidence_qc_v8_check.py",
    '''    report = {\n        "cards_checked": len(rows),\n''',
    '''    report = {\n        "id_scope": scope,\n        "cards_checked": len(rows),\n''',
)

# Related validator: enforce exact ID scope directly.
replace_once(
    "validation_scripts/related_lifecycle_check.py",
    '''from card_audit_utils import ALLOWED_RELATION_TYPES, dedupe, parse_date\n''',
    '''from card_audit_utils import (\n    ALLOWED_RELATION_TYPES, dedupe, parse_date, select_scoped_cards,\n)\n''',
)
replace_once(
    "validation_scripts/related_lifecycle_check.py",
    '''    selected = load_ids(args.new_id_file)\n    rows = cards if selected is None else [card for card in cards if card.get("id") in selected]\n\n    findings = []\n''',
    '''    selected = load_ids(args.new_id_file)\n    rows, scope = select_scoped_cards(cards, selected)\n\n    findings = []\n    if scope["errors"]:\n        findings.append({\n            "id": "<id-scope>",\n            "source_spec_id": None,\n            "errors": scope["errors"],\n            "warnings": [],\n        })\n''',
)
replace_once(
    "validation_scripts/related_lifecycle_check.py",
    '''    report = {\n        "status": "PASS" if error_count == 0 else "FAIL",\n''',
    '''    report = {\n        "id_scope": scope,\n        "status": "PASS" if error_count == 0 else "FAIL",\n''',
)

# Date validator: enforce exact ID scope directly.
replace_once(
    "validation_scripts/date_role_freshness_check.py",
    '''from card_audit_utils import parse_date\n''',
    '''from card_audit_utils import parse_date, select_scoped_cards\n''',
)
replace_once(
    "validation_scripts/date_role_freshness_check.py",
    '''    selected = load_ids(args.id_file)\n    if selected is not None:\n        rows = [card for card in rows if str(card.get("id", "")) in selected]\n\n    findings = []\n''',
    '''    selected = load_ids(args.id_file)\n    rows, scope = select_scoped_cards(rows, selected)\n\n    findings = []\n    if scope["errors"]:\n        findings.append({\n            "id": "<id-scope>",\n            "errors": scope["errors"],\n        })\n''',
)
replace_once(
    "validation_scripts/date_role_freshness_check.py",
    '''    result = {\n        "status": "PASS" if not findings else "FAIL",\n''',
    '''    result = {\n        "id_scope": scope,\n        "status": "PASS" if not findings else "FAIL",\n''',
)

# Recompute helper: only preserve complete bounded exceptions and skip invalid resolution URLs.
replace_once(
    "validation_scripts/recompute_source_audit_metadata.py",
    '''        if isinstance(value, dict) and value.get("allowed") is True and value.get("reason"):\n            return deepcopy(value)\n''',
    '''        if (\n            isinstance(value, dict)\n            and value.get("allowed") is True\n            and value.get("reason")\n            and (value.get("mitigation") or value.get("scope_limits"))\n        ):\n            return deepcopy(value)\n''',
)
replace_once(
    "validation_scripts/recompute_source_audit_metadata.py",
    '''    for index, source in enumerate(usable_sources(card)):\n        grouped[canonical_url(str(source.get("source_url", "")))].append((index, source))\n''',
    '''    for index, source in enumerate(usable_sources(card)):\n        canonical = canonical_url(str(source.get("source_url", "")))\n        if not canonical:\n            continue\n        grouped[canonical].append((index, source))\n''',
)

# Add focused regression tests without disturbing the existing test module.
test_path = ROOT / "validation_scripts/tests/test_review_round2.py"
if not test_path.exists():
    test_path.write_text(r'''#!/usr/bin/env python3
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
            [sys.executable, str(SCRIPTS / script), str(cards_path), "--new-id-file", str(ids_path), *extra],
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
        for script, ids, extra in (
            ("evidence_qc_v8_check.py", ["Z"], ()),
            ("related_lifecycle_check.py", ["A", "Z"], ("--require-contract",)),
            ("date_role_freshness_check.py", [], ("--require-date-role",)),
        ):
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
    def test_strict_recompute_rejects_incomplete_legacy_exception(self):
        card = {
            "source_spec_id": "TEST",
            "fact_sources": [
                {
                    "source_name": "Official",
                    "source_url": "https://agency.gov/article",
                    "source_quote": "official statement",
                    "source_quote_status": "official_material_quote_verified",
                    "evidence_role": "primary_event_evidence",
                    "source_origin_type": "government_primary",
                    "supports": ["fact"],
                }
            ],
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
            "fact_sources": [
                {
                    "source_name": "Official",
                    "source_url": "https://agency.gov/article",
                    "source_quote": "official statement",
                    "source_quote_status": "official_material_quote_verified",
                    "evidence_role": "primary_event_evidence",
                    "source_origin_type": "government_primary",
                    "supports": ["fact"],
                }
            ],
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
''', encoding="utf-8")

print("PR #207 review round 2 patches applied")
