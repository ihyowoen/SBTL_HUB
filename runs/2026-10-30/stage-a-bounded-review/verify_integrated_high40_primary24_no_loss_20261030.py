#!/usr/bin/env python3
"""Independent source-ID/parent invariance QC of the create-only V3 overlay."""

import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE / "STAGE_A_1330_SOURCE_INTEGRATED_EVIDENCE_OVERLAY_V2_20261030.json"
PACK = HERE / "STAGE_A_HIGH40_PRIMARY_LINKED_CASES_ADDENDUM_20261030.json"
V3 = HERE / "STAGE_A_1330_SOURCE_INTEGRATED_EVIDENCE_OVERLAY_V3_20261030.json"
OUT = HERE / "STAGE_A_1330_PRIMARY24_ADDENDUM_INDEPENDENT_QC_20261030.json"


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    if OUT.exists():
        raise FileExistsError(f"create-only violation: {OUT}")
    v2 = json.loads(PARENT.read_text())
    v3 = json.loads(V3.read_text())
    pack = json.loads(PACK.read_text())
    old = {r["candidate_id"]: r for r in v2["source_rows"]}
    new = {r["candidate_id"]: r for r in v3["source_rows"]}
    assert len(old) == len(new) == 1330 and set(old) == set(new)
    assert [r["candidate_id"] for r in v2["source_rows"]] == [r["candidate_id"] for r in v3["source_rows"]]
    linked = {sid for c in pack["cases"] for sid in c["source_ids"]}
    assert len(linked) == 24 and linked.issubset(old)
    allowed_new_values = {
        "additional_evidence_scope", "provisional_case_package_ids_NOT_FORMAL_CLUSTER",
        "evidence_artifacts", "evidence_reference_details"
    }
    for sid, row in new.items():
        base = old[sid]
        assert row.keys() == base.keys(), sid
        changed = {key for key in row if row[key] != base[key]}
        assert changed == (allowed_new_values if sid in linked else set()), (sid, changed)
        for key in (
            "original_stage_a_pool", "original_assessment_status", "metadata_score_original_not_selection_decision",
            "original_economic_event_cluster_id", "original_individual_0_1P_result", "native_0_1P_state",
            "primary_url_original", "headline_raw", "candidate_id", "source_row_index", "new_native_strict_pass"
        ):
            assert row[key] == base[key], (sid, key)
        if sid in linked:
            assert base["additional_evidence_scope"] == "NO_ADDITIONAL_EVIDENCE_ON_THIS_ID"
            assert row["additional_evidence_scope"] == "BOUNDED_CASE_SOURCE_EVIDENCE"
            assert row["native_0_1P_state"] == "NATIVE_INDIVIDUAL_0_1P_PENDING"
            assert row["evidence_artifacts"] == [PACK.name]
    assert v3["original_csv_sha256"] == v2["original_csv_sha256"] == pack["source_ledger_sha256"]
    assert v3["parent_overlay_sha256"] == sha256(PARENT)
    assert v3["additional_high40_primary24_pack_sha256"] == sha256(PACK)
    assert v3["unique_source_ids_with_any_bounded_or_triage_evidence"] == 121
    assert v3["high_metadata_60_plus_with_some_case_or_triage_evidence"] == 87
    assert v3["high_metadata_60_plus_without_any_linked_additional_evidence"] == 16
    assert v3["original_formal_pending_0_1P_unchanged"] == 1285
    assert v3["new_promotions"] == 0
    assert v3["review_evidence_scope_counts"] == dict(Counter(r["additional_evidence_scope"] for r in new.values()))
    high = [r for r in new.values() if r["original_stage_a_pool"] == "candidate_review_pool" and r["metadata_score_original_not_selection_decision"] >= 60]
    assert len(high) == 103
    assert sum(r["additional_evidence_scope"] != "NO_ADDITIONAL_EVIDENCE_ON_THIS_ID" for r in high) == 87
    # Issuer-source event convergence must not masquerade as native clustering.
    assert "TWO_DISTINCT_EVENTS" in next(c["bounded_route"] for c in pack["cases"] if c["case_id"].startswith("KEMPOWER_CANADIAN"))
    # For the 3 exact Full matches, verify identity and original-government/issuer URL.
    full = json.loads((HERE.parents[2] / "data/cards.full.json").read_text())
    cards = {c["id"]: c for c in full["cards"]}
    assert "Limondale" in cards["2026-06-11_GL_01"]["title"]
    assert "R3 Lithium" in cards["2026-09-10_US_02"]["title"]
    assert "Nova Scotia" in cards["2026-09-16_GL_02"]["title"]
    assert cards["2026-09-16_GL_02"]["urls"] == [next(c["primary_source_url"] for c in pack["cases"] if c["case_id"].startswith("NOVA_SCOTIA"))]
    assert cards["2026-09-10_US_02"]["urls"] == [next(c["primary_source_url"] for c in pack["cases"] if c["case_id"].startswith("R3_LITHIUM"))]
    assert cards["2026-09-22_KR_01"]["title"].startswith("포스코퓨처엠"), "L&F is a separate supplier"

    output = {
        "artifact_type": "STAGE_A_V3_BOUNDED_PRIMARY24_INDEPENDENT_NO_LOSS_QC",
        "status": "PASS_BOUNDED_LEDGER_INTEGRITY_ONLY_NOT_NATIVE_STAGE_A",
        "original_csv_sha256": pack["source_ledger_sha256"],
        "parent_v2_sha256": sha256(PARENT), "addendum_sha256": sha256(PACK), "v3_sha256": sha256(V3),
        "source_id_count": len(new), "source_id_order_preserved": True, "changed_existing_baseline_fields": 0,
        "new_bounded_evidence_links": len(linked), "event_cases": len(pack["cases"]),
        "evidence_linked_id_total": 121, "high_60plus_total": 103,
        "high_60plus_evidence_linked": 87, "high_60plus_unlinked": 16,
        "native_individually_reviewed_total_unchanged": 45,
        "native_individual_review_pending_total_unchanged": 1285,
        "formal_strict_pass_total_unchanged": 8,
        "new_native_stage_a_strict_passes": 0,
        "full_cards_untouched": True,
        "native_stage_a_artifact_contract_executed": False,
        "native_stage_a_lineage_contract_executed": False,
        "next_bottleneck": "16 remaining >=60 metadata IDs without primary-linked bounded review, then all lower-score review/watch records and formal source-by-source 0.1P",
    }
    OUT.open("x", encoding="utf-8").write(json.dumps(output, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
