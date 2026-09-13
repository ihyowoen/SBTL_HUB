#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = "5147e5bfbe7cadbf03782ef68805444227afaf1e"
BASE_BLOB = "79e1b89ca89b55c24bd8b2c1fa6924a3d85f13c9"
FULL_PATH = ROOT / "data/cards.full.json"
STAGE_B_PATH = ROOT / "runs/2026-09-10/sep9-r1-current-main-production-r1/stages/stage-b.json"
MANIFEST_PATH = ROOT / "direct-adds/2026-09-13-pr371-canonical-provenance/direct-add.json"
EXPECTED_COUNT = 1615
TARGET_IDS = [
    "2026-09-08_GL_03",
    "2026-09-02_EU_05",
    "2026-09-02_CN_01",
    "2026-09-08_CN_01",
    "2026-09-08_KR_04",
    "2026-09-09_GL_01",
    "2026-09-09_CN_01",
    "2026-09-08_GL_04",
    "2026-09-08_EU_02",
    "2026-09-09_EU_01",
    "2026-09-09_EU_02",
    "2026-09-09_GL_02",
    "2026-09-09_US_01",
    "2026-09-09_GL_03",
    "2026-09-10_EU_01",
    "2026-09-07_CN_02",
]
A004_ID = "2026-09-02_CN_01"
A007_ID = "2026-09-08_CN_01"
A012_ID = "2026-09-09_CN_01"


def fail(message: str) -> None:
    raise SystemExit(f"PR374 materialization blocked: {message}")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def base_json():
    raw = subprocess.check_output(
        ["git", "-C", str(ROOT), "show", f"{BASE_SHA}:data/cards.full.json"],
        text=True,
    )
    return json.loads(raw.lstrip("\ufeff"))


def card_map(doc):
    cards = doc.get("cards")
    if not isinstance(cards, list):
        fail("canonical cards must be an array")
    out = {}
    for card in cards:
        if not isinstance(card, dict) or not isinstance(card.get("id"), str):
            fail("malformed canonical card")
        if card["id"] in out:
            fail(f"duplicate card id {card['id']}")
        out[card["id"]] = card
    return out


def source_by_id(card, source_id: str):
    rows = card.get("fact_sources")
    if not isinstance(rows, list):
        fail(f"{card['id']}: fact_sources must be an array")
    matches = [row for row in rows if isinstance(row, dict) and row.get("source_id") == source_id]
    if len(matches) != 1:
        fail(f"{card['id']}: expected exactly one fact source {source_id}, got {len(matches)}")
    return matches[0]


def discovery_by_url(card, url: str):
    rows = card.get("source_discovery_ledger")
    if not isinstance(rows, list):
        fail(f"{card['id']}: source_discovery_ledger must be an array")
    matches = [row for row in rows if isinstance(row, dict) and row.get("canonical_url") == url]
    if len(matches) != 1:
        fail(f"{card['id']}: expected exactly one discovery row for {url}, got {len(matches)}")
    return matches[0]


def changed_fields(before: dict, after: dict):
    keys = set(before) | set(after)
    return sorted(key for key in keys if before.get(key) != after.get(key))


def assert_eq(actual, expected, label: str):
    if actual != expected:
        fail(f"{label}: expected {expected!r}, got {actual!r}")


def main() -> None:
    base = base_json()
    full = load_json(FULL_PATH)
    if len(base.get("cards", [])) != EXPECTED_COUNT or len(full.get("cards", [])) != EXPECTED_COUNT:
        fail(f"expected {EXPECTED_COUNT} cards in base and working canonical")
    if base.get("total") != EXPECTED_COUNT or full.get("total") != EXPECTED_COUNT:
        fail("canonical total mismatch")

    base_map = card_map(base)
    cards = card_map(full)
    if set(TARGET_IDS) - set(cards):
        fail(f"missing target ids: {sorted(set(TARGET_IDS) - set(cards))}")

    stage_b_hash = hashlib.sha256(STAGE_B_PATH.read_bytes()).hexdigest()
    if len(stage_b_hash) != 64:
        fail("invalid Stage B SHA-256")

    # Every deferred card receives the exact corrected Stage B artifact hash.
    for card_id in TARGET_IDS:
        card = cards[card_id]
        lineage = card.get("stage_b_lineage")
        if not isinstance(lineage, dict):
            fail(f"{card_id}: stage_b_lineage missing")
        assert_eq(lineage.get("artifact"), "stage-b.json", f"{card_id} stage_b_lineage.artifact")
        assert_eq(lineage.get("artifact_sha256"), "PENDING", f"{card_id} stale artifact hash precondition")
        lineage["artifact_sha256"] = stage_b_hash

    # A004: source publication dates and pv magazine group owner normalization.
    a004 = cards[A004_ID]
    assert_eq(a004.get("source_spec_id"), "STD26_0909_A_004", "A004 source_spec_id")
    s2 = source_by_id(a004, "STD26_0909_A_004-S2")
    s3 = source_by_id(a004, "STD26_0909_A_004-S3")
    assert_eq(s2.get("published"), "2026-09-02", "A004 S2 old publication date")
    assert_eq(s3.get("published"), "2026-09-02", "A004 S3 old publication date")
    s2["published"] = "2026-09-08"
    s3["published"] = "2026-09-08"
    s2["source_owner_id_normalized"] = "pv_magazine_group"
    s3["source_owner_id_normalized"] = "pv_magazine_group"
    a004_date = a004.get("date_role")
    if not isinstance(a004_date, dict):
        fail("A004 date_role missing")
    a004_date["source_publication_dates"] = ["2026-09-02", "2026-09-08"]
    a004_date["publication_dates"] = ["2026-09-02", "2026-09-08"]
    a004_measure = a004.get("source_diversity_measure")
    if not isinstance(a004_measure, dict):
        fail("A004 source_diversity_measure missing")
    assert_eq(a004_measure.get("unique_urls"), 3, "A004 unique_urls")
    assert_eq(a004_measure.get("unique_domains"), 3, "A004 unique_domains")
    assert_eq(a004_measure.get("independent_owner_count"), 3, "A004 stale owner count")
    a004_measure["independent_owner_count"] = 2

    # A012: pv magazine tax article was published Sep 1, while event representative date remains Sep 9.
    a012 = cards[A012_ID]
    assert_eq(a012.get("source_spec_id"), "STD26_0909_A_012", "A012 source_spec_id")
    a012_s2 = source_by_id(a012, "STD26_0909_A_012-S2")
    assert_eq(a012_s2.get("published"), "2026-09-09", "A012 S2 old publication date")
    a012_s2["published"] = "2026-09-01"
    a012_date = a012.get("date_role")
    if not isinstance(a012_date, dict):
        fail("A012 date_role missing")
    a012_date["source_publication_dates"] = ["2026-09-01", "2026-09-09"]
    a012_date["publication_dates"] = ["2026-09-01", "2026-09-09"]
    assert_eq(a012.get("date"), "2026-09-09", "A012 representative card date")

    # A007: collapse Mining.com/Reuters and Reuters to one Reuters reporting chain;
    # the generic Reuters trade article remains checked but cannot support visible rare-earth claims.
    a007 = cards[A007_ID]
    assert_eq(a007.get("source_spec_id"), "STD26_0909_A_007", "A007 source_spec_id")
    a007_s1 = source_by_id(a007, "STD26_0909_A_007-S1")
    a007_s2 = source_by_id(a007, "STD26_0909_A_007-S2")
    a007_s1["source_owner_id_normalized"] = "reuters"
    a007_s1["role"] = "production-card evidence source"
    a007_s2["source_owner_id_normalized"] = "reuters"
    a007_s2["role"] = "checked_not_used_for_visible_claims"
    a007_s2["evidence_role"] = "checked_not_used_for_visible_claims"
    a007_s2["claim_use"] = "checked_not_used_for_visible_claims"
    a007_s2["supports"] = []
    a007_s2["visible_claim_support"] = []

    claim_map = a007.get("claim_map")
    if not isinstance(claim_map, list) or len(claim_map) != 1 or not isinstance(claim_map[0], dict):
        fail("A007 claim_map must contain exactly one claim")
    assert_eq(
        claim_map[0].get("supported_by_source_ids"),
        ["STD26_0909_A_007-S1", "STD26_0909_A_007-S2"],
        "A007 stale claim support",
    )
    claim_map[0]["supported_by_source_ids"] = ["STD26_0909_A_007-S1"]

    reuters_url = "https://www.reuters.com/world/asia-pacific/chinas-exports-up-25-yy-august-imports-surge-282-2026-09-08/"
    discovery_by_url(a007, reuters_url)["visible_fields_supported"] = []

    a007["source_diversity_status"] = "PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION"
    a007["source_diversity_measure"] = {
        "unique_urls": 2,
        "unique_domains": 2,
        "independent_owner_count": 1,
    }
    a007["source_synthesis_applied"] = False
    a007["source_synthesis_fields"] = []
    a007["source_synthesis_audit"] = {
        "status": "PASS_SINGLE_SOURCE_BOUNDED",
        "primary_or_official_controls_operative_facts": True,
        "independent_confirmation_used": False,
        "conflicts_explicitly_resolved": True,
    }
    a007["single_source_exception"] = {
        "allowed": True,
        "reason": "The Mining.com page is a Reuters-syndicated report; the second Reuters URL is not an independent owner or rare-earth-specific confirmation.",
        "mitigation": "Treat the two URLs as one Reuters reporting chain and limit the card to the attributed August customs figures and explicitly bounded interpretation.",
        "scope_limits": [
            "No independent-owner corroboration is claimed.",
            "The general Reuters trade article is retained as checked but not used for visible rare-earth claims.",
            "Re-verify against a durable GACC commodity table when available.",
        ],
    }

    # No card may drift outside the bounded target set, and each target must match an explicit allowlist.
    actual_by_id = {}
    expected_special = {
        A004_ID: {"date_role", "fact_sources", "source_diversity_measure", "stage_b_lineage"},
        A007_ID: {
            "claim_map",
            "fact_sources",
            "single_source_exception",
            "source_discovery_ledger",
            "source_diversity_measure",
            "source_diversity_status",
            "source_synthesis_applied",
            "source_synthesis_audit",
            "source_synthesis_fields",
            "stage_b_lineage",
        },
        A012_ID: {"date_role", "fact_sources", "stage_b_lineage"},
    }
    for card_id, before in base_map.items():
        after = cards.get(card_id)
        if after is None:
            fail(f"unexpected deleted card {card_id}")
        fields = changed_fields(before, after)
        if fields:
            actual_by_id[card_id] = fields
    assert_eq(set(actual_by_id), set(TARGET_IDS), "exact changed-card set")
    for card_id in TARGET_IDS:
        expected = expected_special.get(card_id, {"stage_b_lineage"})
        assert_eq(set(actual_by_id[card_id]), expected, f"{card_id} changed-field allowlist")

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    full["updated"] = now
    full["total"] = len(full["cards"])
    FULL_PATH.write_text(json.dumps(full, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    updates = []
    for card_id in TARGET_IDS:
        spec = cards[card_id].get("source_spec_id")
        if not isinstance(spec, str) or not spec:
            fail(f"{card_id}: source_spec_id missing")
        if card_id == A004_ID:
            reason = "Carry the #373 A004 source-publication correction and pv magazine group owner normalization into canonical, then bind the exact corrected Stage B artifact hash."
            evidence = "PR #373 corrected A004 Stage B/C: S2 and S3 publication dates are 2026-09-08 and both normalize to pv_magazine_group; representative event date remains 2026-09-02."
        elif card_id == A007_ID:
            reason = "Carry the #373 A007 Reuters syndication correction into canonical and bind the exact corrected Stage B artifact hash."
            evidence = "PR #373 established 2 URLs / 2 domains / 1 Reuters owner; the Mining.com Reuters-syndicated article supports the visible rare-earth claim while the generic Reuters trade article is checked but excluded from visible-claim support."
        elif card_id == A012_ID:
            reason = "Carry the #373 A012 source-publication correction into canonical and bind the exact corrected Stage B artifact hash."
            evidence = "PR #373 corrected A012-S2 to publication date 2026-09-01 while preserving the 2026-09-09 representative event date."
        else:
            reason = f"Rebind {card_id} / {spec} canonical Stage B lineage from PENDING to the exact corrected Stage B artifact SHA-256 merged through #373."
            evidence = "The #373 remediation recertified the run-bound Stage B/C artifacts; this bounded update changes only canonical stage_b_lineage.artifact_sha256 and does not alter event identity, content, evidence claims, dates, or Related state."
        updates.append({
            "id": card_id,
            "change_type": "correction",
            "changed_fields": actual_by_id[card_id],
            "reason": reason,
            "evidence_review_summary": evidence,
        })

    manifest = {
        "schema": "manual_direct_add_v2",
        "status": "PASS",
        "direct_add_id": "PR371_CANONICAL_PROVENANCE_REBIND_20260913_R1",
        "review_mode": "already_reviewed_bounded_direct_add",
        "formal_full_run_claimed": False,
        "base_main_commit_sha": BASE_SHA,
        "base_full_blob_sha": BASE_BLOB,
        "expected_before": EXPECTED_COUNT,
        "expected_after": EXPECTED_COUNT,
        "output_updated": now,
        "operations": {"add": [], "update": TARGET_IDS, "id_migration": []},
        "editorial_attestation": {
            "policy_version": "EMBEDDED_NEWS_VALUE_SELECTION_V4",
            "additions": [],
            "updates": updates,
        },
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "PASS_MATERIALIZED",
        "stage_b_sha256": stage_b_hash,
        "updated_ids": TARGET_IDS,
        "changed_fields": actual_by_id,
        "output_updated": now,
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
