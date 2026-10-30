#!/usr/bin/env python3
"""Independent read-only QA of the nine source-group triage records.

Formal native Stage A pass is explicitly out of scope.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE_SHA = "5e78420916b0c1d70ff56bf928779cd969b94fbb15dd4119c841872997486116"
FULL_BLOB = "07a91714e56be2a8bfad10ab63822f0c5cb3f06e"
PART_LIMITS = {
    "market_structure_competition": 25, "supply_demand_price_utilisation": 25,
    "technology_performance_safety": 20, "cashflow_asset_value": 10,
    "law_policy_market_access": 10, "systemic_scale": 5,
    "persistence_irreversibility": 3, "decision_urgency_actionability": 2,
}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source-ledger", required=True, type=Path)
    p.add_argument("--full", required=True, type=Path)
    p.add_argument("--receipt-path", type=Path)
    args = p.parse_args()
    assert hashlib.sha256(args.source_ledger.read_bytes()).hexdigest() == SOURCE_SHA
    raw = args.full.read_bytes()
    assert hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == FULL_BLOB
    assert json.loads(raw)["total"] == 1676
    with args.source_ledger.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 1330
    by_source = {row["candidate_id"]: row for row in rows}
    assert len(by_source) == 1330
    graph = json.loads((HERE / "STAGE_A_1330_SOURCE_URL_OBSERVATION_EQUIVALENCE_20261030.json").read_text(encoding="utf-8"))
    five = json.loads((HERE / "STAGE_A_FIVE_MIXED_POOL_SOURCE_GROUPS_CASE_ADJUDICATION_20261030.json").read_text(encoding="utf-8"))
    nine_path = HERE / "STAGE_A_NINE_REMAINING_MIXED_POOL_GROUPS_EVIDENCE_TRIAGE_20261030.json"
    nine = json.loads(nine_path.read_text(encoding="utf-8"))
    groups = {g["source_url_observation_group_id"]: g for g in graph["all_repeat_url_source_groups"] if g["mixed_original_pool"]}
    assert len(groups) == nine["mixed_pool_group_total"] == 14
    selected_five = {g["group_id"] for g in five["source_observation_groups"]}
    selected_nine = {g["source_url_observation_group_id"] for g in nine["triage_records"]}
    assert len(selected_five) == 5 and len(selected_nine) == 9
    assert selected_five.isdisjoint(selected_nine) and selected_five | selected_nine == set(groups)
    all_source_ids = set()
    for entry in nine["triage_records"]:
        g = groups[entry["source_url_observation_group_id"]]
        assert entry["original_source_ids"] == g["source_ids"]
        assert entry["source_url"] == g["query_aware_url"]
        assert entry["original_pools"] == g["source_row_original_pools"]
        assert entry["original_metadata_scores"] == g["source_row_original_scores"]
        assert entry["formal_related_prepass_status"] == "HOLD"
        assert entry["formal_stage_a_disposition"] == "HOLD_ORIGINAL_ID_UNADJUDICATED"
        for source_id, pool, score in zip(entry["original_source_ids"], entry["original_pools"], entry["original_metadata_scores"]):
            original = by_source[source_id]
            assert original["stage_a_pool"] == pool
            assert int(original["decision_news_value_score"]) == score
            assert not original["economic_event_cluster_id"]
            all_source_ids.add(source_id)
        j = entry["bounded_four_judgments_not_native_pass"]
        assert j["execution_credibility_gate"] in ("PASS", "REVIEW", "FAIL")
        assert j["independent_cardability_gate"] in ("PASS", "REVIEW", "FAIL")
        assert j["publication_urgency"] in ("immediate", "near_term", "monitor")
        breakdown = j["decision_value_breakdown"]
        assert set(breakdown) == set(PART_LIMITS)
        assert all(isinstance(v, int) and 0 <= v <= PART_LIMITS[k] for k, v in breakdown.items())
        score = sum(breakdown.values())
        assert score == j["decision_news_value_score_provisional"]
        assert j["systemic_scale_denominator"] is None and j["denominator_gap"] and breakdown["systemic_scale"] <= 2
        assert breakdown["technology_performance_safety"] <= (4 if j["technology_evidence_level"] == "company_target_or_unsupported_claim" else 0)
        if j["novelty_cap_basis"] in ("repeated_announcement_no_new_fact", "unsupported_political_rhetoric"):
            assert score <= 39
        if j["novelty_cap_basis"] == "company_target_without_validation_or_effect":
            assert score <= 54
        assert entry["evidence_gap"] and entry["related_and_date_role_hold"]
        assert entry["source_owner_evidence"]
    assert len(all_source_ids) == nine["remaining_nine_groups_touched_source_ids"] == 18
    assert len({sid for group in groups.values() for sid in group["source_ids"]}) == nine["original_source_ids_in_all_mixed_pool_groups"] == 28
    assert nine["formal_original_0_1P_unadjudicated_count_remains"] == 1285
    assert nine["formal_strict_promotions"] == 0 and nine["not_native_pass"] is True
    receipt = {
        "result": "PASS_SCOPED_TRIAGE_NOT_NATIVE_PASS",
        "source_id_universe": 1330,
        "full_card_count": 1676,
        "mixed_pool_groups_total": 14,
        "previously_bounded_groups": 5,
        "newly_triaged_group_count": 9,
        "all_mixed_pool_original_source_ids_accounted": 28,
        "new_triage_original_source_ids": 18,
        "original_formally_unadjudicated_still": 1285,
        "new_formal_strict_promotions": 0,
        "review_json_sha256": hashlib.sha256(nine_path.read_bytes()).hexdigest(),
        "full_git_blob_verified": FULL_BLOB,
        "original_source_sha256_verified": SOURCE_SHA,
        "formal_native_contract": "NOT_EXECUTED_COMPLETE_STAGE_A_ARTIFACT_MISSING",
        "formal_native_lineage": "NOT_EXECUTED_COMPLETE_STAGE_A_ARTIFACT_MISSING",
    }
    if args.receipt_path:
        with args.receipt_path.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(receipt, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
