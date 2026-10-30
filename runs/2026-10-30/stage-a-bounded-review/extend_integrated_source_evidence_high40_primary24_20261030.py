#!/usr/bin/env python3
"""Create-only V3 overlay: 24 additional high-score IDs receive bounded primary links.

Crucially none of these evidence links alters a native 0.1P decision, a formal
economic-event cluster, a Full card, or the original collector's 1,330 IDs.
"""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE / "STAGE_A_1330_SOURCE_INTEGRATED_EVIDENCE_OVERLAY_V2_20261030.json"
PACK = HERE / "STAGE_A_HIGH40_PRIMARY_LINKED_CASES_ADDENDUM_20261030.json"
OUT = HERE / "STAGE_A_1330_SOURCE_INTEGRATED_EVIDENCE_OVERLAY_V3_20261030.json"
PARENT_SHA256 = "bf3f1e5a8ad1eeb3c2accd36d2132507400152c2c3767562b6745151c0575834"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"create-only violation: {OUT}")
    assert sha256(PARENT) == PARENT_SHA256, "V2 parent SHA changed"
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    pack = json.loads(PACK.read_text(encoding="utf-8"))
    assert len(parent["source_rows"]) == 1330
    assert parent["unique_source_ids_with_any_bounded_or_triage_evidence"] == 97
    assert parent["high_metadata_60_plus_without_any_linked_additional_evidence"] == 40
    assert pack["native_0_1P_promotions"] == 0
    assert pack["source_ledger_sha256"] == parent["original_csv_sha256"]

    index: dict[str, dict] = {}
    cases = pack["cases"]
    assert len(cases) == 22
    for case in cases:
        for required in (
            "case_id", "source_ids", "event_date", "date_role", "primary_source_owner",
            "primary_source_url", "body_reference", "bounded_evidence", "must_not_claim",
            "full_relation", "bounded_route", "remaining_native_gate"
        ):
            assert case.get(required), f"missing {required}: {case.get('case_id')}"
        assert case["primary_source_url"].startswith("https://")
        for sid in case["source_ids"]:
            assert sid not in index, f"source ID in multiple competing cases: {sid}"
            index[sid] = case
    assert len(index) == 24

    out = copy.deepcopy(parent)
    out["artifact_type"] = "STAGE_A_INTEGRATED_EVIDENCE_OVERLAY_V3_CREATE_ONLY_BOUNDED_PRIMARY24"
    out["parent_overlay_sha256"] = PARENT_SHA256
    out["additional_high40_primary24_pack_sha256"] = sha256(PACK)
    out["new_primary_source_ids_after_previous_checkpoint"] = len(index)
    out["oct30_new_primary_source_ids"] += len(index)
    out["unique_source_ids_with_any_bounded_or_triage_evidence"] += len(index)
    out["high_metadata_60_plus_with_some_case_or_triage_evidence"] += len(index)
    out["high_metadata_60_plus_without_any_linked_additional_evidence"] -= len(index)
    out["source_evidence_artifact_file_count"] += 1
    out["review_evidence_scope_counts"]["NO_ADDITIONAL_EVIDENCE_ON_THIS_ID"] -= len(index)
    out["review_evidence_scope_counts"]["BOUNDED_CASE_SOURCE_EVIDENCE"] += len(index)

    observed: set[str] = set()
    for row in out["source_rows"]:
        sid = row["candidate_id"]
        if sid not in index:
            continue
        assert row["original_stage_a_pool"] == "candidate_review_pool", sid
        assert row["metadata_score_original_not_selection_decision"] >= 60, sid
        assert row["native_0_1P_state"] == "NATIVE_INDIVIDUAL_0_1P_PENDING", sid
        assert row["additional_evidence_scope"] == "NO_ADDITIONAL_EVIDENCE_ON_THIS_ID", sid
        assert not row["provisional_case_package_ids_NOT_FORMAL_CLUSTER"], sid
        case = index[sid]
        row["additional_evidence_scope"] = "BOUNDED_CASE_SOURCE_EVIDENCE"
        row["provisional_case_package_ids_NOT_FORMAL_CLUSTER"] = [case["case_id"]]
        row["evidence_artifacts"] = [PACK.name]
        row["evidence_reference_details"] = [{
            "evidence": "OCT30_24_HIGH_SCORE_SOURCE_IDS_ISSUER_OR_GOVERNMENT_BOUNDED_REVIEW",
            "artifact": PACK.name,
            "tier": "BOUNDED_CASE_PRIMARY_OR_GOVERNMENT_OR_ISSUER_RNS",
            "case_ids": [case["case_id"]],
            "event_units": [],
            "mapping_certainty": "PROVISIONAL_SOURCE_TO_CASE_NOT_NATIVE_0_1P_EVENT_ID",
        }]
        observed.add(sid)
    assert observed == set(index)
    counts = Counter(r["additional_evidence_scope"] for r in out["source_rows"])
    assert dict(counts) == out["review_evidence_scope_counts"]
    high = [r for r in out["source_rows"] if r["original_stage_a_pool"] == "candidate_review_pool" and r["metadata_score_original_not_selection_decision"] >= 60]
    assert len(high) == 103
    assert sum(r["additional_evidence_scope"] != "NO_ADDITIONAL_EVIDENCE_ON_THIS_ID" for r in high) == 87
    assert out["unique_source_ids_with_any_bounded_or_triage_evidence"] == 121
    assert out["original_formal_pending_0_1P_unchanged"] == 1285
    assert out["new_promotions"] == 0
    OUT.open("x", encoding="utf-8").write(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({
        "overlay_sha256": sha256(OUT), "pack_sha256": sha256(PACK),
        "original_ids": len(out["source_rows"]), "linked_any": 121,
        "high_60plus_linked": 87, "high_60plus_unlinked": 16,
        "native_0_1P_pending_unchanged": 1285, "new_promotions": 0,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
