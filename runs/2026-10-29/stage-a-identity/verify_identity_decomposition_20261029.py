#!/usr/bin/env python3
"""Independent read-only QC for the 2026-10-29 Stage A identity overlay."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[2].parent
SOURCE = BASE / "STAGE_A_REASSESSMENT_LEDGER_1330_20261027.source.csv"
PREVIOUS = BASE / "stagea_reconciliation_20261028" / "STAGE_A_1285_IDENTITY_PENDING_QUEUE_20261028.csv"
GRAPH = HERE / "STAGE_A_15_CASE_EVENT_DECOMPOSITION_V2_20261029.json"
EDGES = HERE / "STAGE_A_25_SOURCE_TO_CASE_EDGES_V2_20261029.csv"
OVERLAY = HERE / "STAGE_A_1330_SOURCE_NO_LOSS_IDENTITY_OVERLAY_V2_20261029.csv"
RECEIPT = HERE / "STAGE_A_15_CASE_IDENTITY_GRAPH_QC_RECEIPT_V2_20261029.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csv_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def run():
    original = csv_rows(SOURCE)
    old_pending = csv_rows(PREVIOUS)
    overlay = csv_rows(OVERLAY)
    edges = csv_rows(EDGES)
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert sha(SOURCE) == receipt["input_sha256"][SOURCE.name]
    assert sha(PREVIOUS) == receipt["input_sha256"][PREVIOUS.name]
    assert len(original) == len(overlay) == 1330
    original_ids = [r["candidate_id"] for r in original]
    assert original_ids == [r["candidate_id"] for r in overlay]
    assert len(original_ids) == len(set(original_ids))
    assert all(o["original_pool"] == r["stage_a_pool"] for r, o in zip(original, overlay))
    assert all(o["original_gate_status"] == r["assessment_status"] for r, o in zip(original, overlay))
    assert all(o["original_reassessment_status"] == r["promotion_reassessment_status"] for r, o in zip(original, overlay))
    assert all(o["original_metadata_score_not_final_rank"] == r["decision_news_value_score"] for r, o in zip(original, overlay))
    assert all(o["original_date_role_sha256_not_reclassified"] == hashlib.sha256(r["date_role"].encode("utf-8")).hexdigest() for r, o in zip(original, overlay))
    assert all(o["original_related_prepass_sha256_not_reclassified"] == hashlib.sha256(r["related_prepass"].encode("utf-8")).hexdigest() for r, o in zip(original, overlay))
    prior_pending_ids = {r["candidate_id"] for r in old_pending}
    assert len(prior_pending_ids) == 1285
    assert all(r["formal_0_1P_new_pass"] == "false" for r in overlay)
    assert all(r["baseline_source_row_unchanged"] == "true" for r in overlay)
    ev_states = Counter(r["incremental_identity_research_state"] for r in overlay)
    assert ev_states == Counter({
        "EVIDENCE_BOUND_CASE_LINK_RESEARCHED_BUT_0_1P_PENDING": 25,
        "UNREVIEWED_0_1P_PENDING": 1260,
        "PRIOR_0_1P_SCOPE_UNCHANGED": 45,
    })
    mapped = {r["original_source_id"]: r for r in edges}
    assert len(mapped) == len(edges) == 25
    assert set(mapped) <= prior_pending_ids
    assert len(graph["packages"]) == 15
    all_units = {}
    grouped_ids = set()
    for package in graph["packages"]:
        for unit in package["underlying_units"]:
            key = unit["event_unit_id"]
            assert key.startswith(package["package_id"] + "::")
            assert key not in all_units
            all_units[key] = unit
        sids = package["original_source_ids"]
        assert sorted(sids) == sorted([package["representative_observation_id_for_review_not_final_article"]] + package["support_observation_ids"])
        for sid in sids:
            assert sid not in grouped_ids
            grouped_ids.add(sid)
            assert mapped[sid]["provisional_case_package_id"] == package["package_id"]
            assert set(mapped[sid]["underlying_event_unit_ids_from_package_owner_not_article_claimed"].split("|")) == {u["event_unit_id"] for u in package["underlying_units"]}
        assert package["formal_stage_a_0_1p_status"] == "HOLD_NOT_NATIVE_ADJUDICATED"
        assert package["lexical_matches_are_not_same_event_or_related_pass"] is True
        assert package["final_independent_card_count"] is None
    assert grouped_ids == set(mapped)
    assert len(all_units) == 27
    assert {r["evidence_bound_case_package_id"] for r in overlay if r["evidence_bound_case_package_id"]} == {p["package_id"] for p in graph["packages"]}
    for p in (GRAPH, EDGES, OVERLAY):
        assert sha(p) == receipt["output_sha256"][p.name]
    assert receipt["new_strict_promotions"] == 0
    assert receipt["native_stage_a_artifact_contract"].startswith("NOT_EXECUTED")
    assert receipt["native_stage_a_lineage_contract"].startswith("NOT_EXECUTED")
    print(json.dumps({"independent_qc": "PASS", "original": len(original_ids), "pending": len(prior_pending_ids), "case_links": len(mapped), "packages": len(graph["packages"]), "event_units": len(all_units), "formal_promotions": 0}))


if __name__ == "__main__":
    run()
