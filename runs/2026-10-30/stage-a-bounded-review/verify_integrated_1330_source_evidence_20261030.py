#!/usr/bin/env python3
"""Independent no-loss and evidence-bound audit for the integrated Stage A JSON."""
from __future__ import annotations

import collections
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORK = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "STAGE_A_REASSESSMENT_LEDGER_1330_20261027.source.csv"
INTEGRATED = WORK / "STAGE_A_1330_SOURCE_INTEGRATED_EVIDENCE_OVERLAY_20261030.json"
QC = WORK / "STAGE_A_1330_INTEGRATED_EVIDENCE_INDEPENDENT_QC_20261030.json"


def main() -> None:
    raw = SOURCE.read_bytes()
    source_sha = hashlib.sha256(raw).hexdigest()
    assert source_sha == "5e78420916b0c1d70ff56bf928779cd969b94fbb15dd4119c841872997486116"
    with SOURCE.open(encoding="utf-8-sig", newline="") as fh:
        original = list(csv.DictReader(fh))
    data = json.loads(INTEGRATED.read_text(encoding="utf-8"))
    rows = data["source_rows"]
    assert len(rows) == len(original) == 1330
    assert len({x["candidate_id"] for x in rows}) == 1330
    for i, (src, out) in enumerate(zip(original, rows)):
        assert out["source_row_index"] == i == int(src["source_row_index"])
        assert out["candidate_id"] == src["candidate_id"]
        for old, new in [("headline_raw", "headline_raw"),
                         ("primary_url", "primary_url_original"),
                         ("stage_a_pool", "original_stage_a_pool"),
                         ("assessment_status", "original_assessment_status"),
                         ("economic_event_cluster_id", "original_economic_event_cluster_id"),
                         ("promotion_reassessment_status", "original_individual_0_1P_result")]:
            assert src[old] == out[new], (i, old)
        assert int(src["decision_news_value_score"]) == out["metadata_score_original_not_selection_decision"]
        assert not out["new_native_strict_pass"]
        expected_native = ("PREVIOUS_0_1P_INDIVIDUAL_REVIEW_PRESERVED" if
                           src["promotion_reassessment_status"] else "NATIVE_INDIVIDUAL_0_1P_PENDING")
        assert out["native_0_1P_state"] == expected_native
        assert sorted(set(out["evidence_artifacts"])) == out["evidence_artifacts"]
        assert sorted(set(out["provisional_case_package_ids_NOT_FORMAL_CLUSTER"])) == out["provisional_case_package_ids_NOT_FORMAL_CLUSTER"]
        assert sorted(set(out["group_subject_case_ids_NOT_ASSIGNED_PER_SOURCE"])) == out["group_subject_case_ids_NOT_ASSIGNED_PER_SOURCE"]
        actual_files = sorted({x["artifact"] for x in out["evidence_reference_details"]})
        assert actual_files == out["evidence_artifacts"]
        if out["group_subject_case_ids_NOT_ASSIGNED_PER_SOURCE"]:
            assert any(x["mapping_certainty"] == "GROUP_CASES_NOT_ALLOCATION_TO_EACH_SOURCE_ID"
                       for x in out["evidence_reference_details"])
    pool = collections.Counter(x["original_stage_a_pool"] for x in rows)
    assert pool == {"candidate_review_pool": 636, "watchlist_context_pool": 658,
                    "existing_reinforcement": 28, "strict_passed_spec": 8}
    original_reviewed = sum(x["native_0_1P_state"].startswith("PREVIOUS") for x in rows)
    assert original_reviewed == 45
    source_ids_with_evidence = {x["candidate_id"] for x in rows if x["evidence_artifacts"]}
    assert len(source_ids_with_evidence) == 83
    first_tier = collections.Counter(x["additional_evidence_scope"] for x in rows)
    assert first_tier["NO_ADDITIONAL_EVIDENCE_ON_THIS_ID"] == 1247
    old_25 = {x["candidate_id"] for x in rows if any(
        e["artifact"] == "STAGE_A_25_SOURCE_TO_CASE_EDGES_20261029.csv"
        for e in x["evidence_reference_details"])}
    new_65 = {x["candidate_id"] for x in rows if any(
        e["artifact"] not in {"STAGE_A_25_SOURCE_TO_CASE_EDGES_20261029.csv",
                              "STAGE_A_FIVE_PRIMARY_CASES_EVENT_CUSTODY_20261030.json"}
        for e in x["evidence_reference_details"])}
    fresh_6 = {x["candidate_id"] for x in rows if any(
        e["artifact"] == "STAGE_A_FIVE_PRIMARY_CASES_EVENT_CUSTODY_20261030.json"
        for e in x["evidence_reference_details"])}
    assert (len(old_25), len(new_65), len(fresh_6)) == (25, 65, 6)
    assert len(old_25 & new_65) == 13
    assert not (fresh_6 & (old_25 | new_65))
    assert len(old_25 | new_65 | fresh_6) == 83

    q = json.loads((WORK / "STAGE_A_103_SOURCE_HIGH_METADATA_NON_DECISION_INVENTORY_20261030.json")
                   .read_text(encoding="utf-8"))
    high_ids = {x["candidate_id"] for x in q["queue"]}
    assert len(high_ids) == 103
    assert len(high_ids & source_ids_with_evidence) == 49
    assert len(high_ids - source_ids_with_evidence) == 54
    assert all(next(x for x in rows if x["candidate_id"] == sid)["native_0_1P_state"]
               == "NATIVE_INDIVIDUAL_0_1P_PENDING" for sid in high_ids)
    assert all(next(x for x in rows if x["candidate_id"] == sid)["original_stage_a_pool"]
               == "candidate_review_pool" for sid in high_ids)

    status = {
        "qc_result": "PASS_1330_ID_SOURCE_EVIDENCE_RECONCILIATION_ONLY_NOT_NATIVE_STAGE_A_PASS",
        "original_source_csv_sha256": source_sha,
        "integrated_overlay_sha256": hashlib.sha256(INTEGRATED.read_bytes()).hexdigest(),
        "source_id_order_preserved": True,
        "original_pool_status_and_score_preserved": True,
        "original_economic_cluster_and_prior_0_1P_preserved": True,
        "1330_unique_original_source_ids": len(rows),
        "original_45_previously_reviewed": original_reviewed,
        "original_1285_native_0_1P_pending_unchanged": 1330 - original_reviewed,
        "linked_evidence_source_ids": len(source_ids_with_evidence),
        "source_ids_without_incremental_evidence": first_tier["NO_ADDITIONAL_EVIDENCE_ON_THIS_ID"],
        "prior_25_case_ids": len(old_25),
        "oct30_existing_65_ids": len(new_65),
        "prior_oct29_oct30_intersection": len(old_25 & new_65),
        "fresh_6_ids": len(fresh_6),
        "high_103_metadata_ids_with_any_evidence": 49,
        "high_103_metadata_ids_without_any_evidence": 54,
        "every_group_subject_case_explicitly_nonfinal": True,
        "new_native_strict_promotions": 0,
        "native_stage_a_artifact_contract": "NOT_EXECUTED_SOURCE_UNIVERSE_NOT_ADJUDICATED",
        "native_stage_a_lineage_contract": "NOT_EXECUTED_SOURCE_UNIVERSE_NOT_ADJUDICATED",
        "full_1676_git_blob_checked_elsewhere": "07a91714e56be2a8bfad10ab63822f0c5cb3f06e",
    }
    with QC.open("x", encoding="utf-8") as fh:
        json.dump(status, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"INTEGRATED QC FAIL: {exc}", file=sys.stderr)
        raise
