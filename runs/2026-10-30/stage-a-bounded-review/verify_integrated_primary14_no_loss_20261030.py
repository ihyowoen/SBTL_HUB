#!/usr/bin/env python3
"""Independent immutable-field and exact 14-row-delta test for Stage A V2 evidence."""

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
V1 = ROOT / "STAGE_A_1330_SOURCE_INTEGRATED_EVIDENCE_OVERLAY_20261030.json"
V2 = ROOT / "STAGE_A_1330_SOURCE_INTEGRATED_EVIDENCE_OVERLAY_V2_20261030.json"
PACK = ROOT / "STAGE_A_ADDITIONAL_14_HIGH_SOURCE_PRIMARY_EVENT_REVIEW_20261030.json"
QC = ROOT / "STAGE_A_1330_PRIMARY14_ADDITIVE_INDEPENDENT_QC_20261030.json"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if QC.exists():
        raise FileExistsError("create-only QC exists")
    a = json.loads(V1.read_text(encoding="utf-8"))
    b = json.loads(V2.read_text(encoding="utf-8"))
    pack = json.loads(PACK.read_text(encoding="utf-8"))
    ids = set(pack["source_ids"])
    assert len(ids) == 14 and sha(V1) == b["parent_overlay_sha256"]
    assert sha(PACK) == b["additive_primary14_pack_sha256"]
    assert [r["candidate_id"] for r in a["source_rows"]] == [r["candidate_id"] for r in b["source_rows"]]
    assert len(b["source_rows"]) == 1330 and len(ids) == 14
    changed = []
    mutable = {"additional_evidence_scope", "provisional_case_package_ids_NOT_FORMAL_CLUSTER", "evidence_artifacts", "evidence_reference_details"}
    for old, new in zip(a["source_rows"], b["source_rows"]):
        if old == new:
            continue
        changed.append(old["candidate_id"])
        assert old["candidate_id"] in ids
        assert {k: v for k, v in old.items() if k not in mutable} == {k: v for k, v in new.items() if k not in mutable}
        assert old["additional_evidence_scope"] == "NO_ADDITIONAL_EVIDENCE_ON_THIS_ID"
        assert new["additional_evidence_scope"] == "BOUNDED_CASE_SOURCE_EVIDENCE"
        assert new["native_0_1P_state"] == "NATIVE_INDIVIDUAL_0_1P_PENDING"
    assert set(changed) == ids and len(changed) == 14
    counts = Counter(r["original_stage_a_pool"] for r in b["source_rows"])
    assert dict(counts) == a["original_pool_counts"] == b["original_pool_counts"]
    assert (counts["candidate_review_pool"],counts["watchlist_context_pool"],counts["existing_reinforcement"],counts["strict_passed_spec"]) == (636,658,28,8)
    assert b["original_formal_individually_reviewed_0_1P"] == 45
    assert b["original_formal_pending_0_1P_unchanged"] == 1285
    assert b["original_csv_sha256"] == a["original_csv_sha256"]
    assert b["unique_source_ids_with_any_bounded_or_triage_evidence"] == 97
    assert b["high_metadata_60_plus_with_some_case_or_triage_evidence"] == 63
    assert b["high_metadata_60_plus_without_any_linked_additional_evidence"] == 40
    assert b["new_promotions"] == 0
    report = {
        "qc_result": "PASS_ADDITIVE_14_ID_NO_LOSS_EVIDENCE_ONLY_NOT_NATIVE_0_1P",
        "old_overlay_sha256": sha(V1),
        "new_overlay_sha256": sha(V2),
        "new_14_case_pack_sha256": sha(PACK),
        "original_source_ids": 1330,
        "exact_additive_source_ids": sorted(ids),
        "changed_source_rows_only": 14,
        "all_immutable_fields_and_prior_formal_statuses_equal": True,
        "prior_individual_review": 45,
        "formal_pending": 1285,
        "evidence_linked": 97,
        "high_metadata_60_plus_with_evidence": 63,
        "high_metadata_60_plus_without_evidence": 40,
        "new_strict_promotions": 0,
        "stage_a_native_artifact_contract": "NOT_EXECUTED",
        "stage_a_native_lineage_contract": "NOT_EXECUTED"
    }
    QC.open("x", encoding="utf-8").write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
