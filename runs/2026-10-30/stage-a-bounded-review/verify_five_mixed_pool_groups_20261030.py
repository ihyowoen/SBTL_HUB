#!/usr/bin/env python3
"""Read-only scope QC for five repeated-URL cross-pool evidence reviews.

This does not run or substitute for complete Stage A native contract/lineage QC.
"""

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE_SHA = "5e78420916b0c1d70ff56bf928779cd969b94fbb15dd4119c841872997486116"
FULL_BLOB = "07a91714e56be2a8bfad10ab63822f0c5cb3f06e"
PART_NAMES = [
    "market_structure_competition", "supply_demand_price_utilisation",
    "technology_performance_safety", "cashflow_asset_value",
    "law_policy_market_access", "systemic_scale",
    "persistence_irreversibility", "decision_urgency_actionability",
]
CEILINGS = dict(zip(PART_NAMES, (25, 25, 20, 10, 10, 5, 3, 2)))
TECH_CEILINGS = {
    "not_applicable": 0,
    "company_target_or_unsupported_claim": 4,
    "laboratory_unvalidated": 7,
    "pilot_precommercial": 11,
    "independent_test_or_customer_qualification": 15,
    "commercial_scale_or_long_duration_field": 20,
    "material_failure_evidence": 20,
}


def blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def band(score):
    if score >= 85:
        return "critical_structural_85_100"
    if score >= 70:
        return "high_decision_value_70_84"
    if score >= 55:
        return "material_industry_signal_55_69"
    if score >= 40:
        return "standard_monitoring_40_54"
    if score >= 25:
        return "context_reinforcement_25_39"
    return "low_independent_value_0_24"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source-ledger", type=Path, required=True)
    p.add_argument("--full", type=Path, required=True)
    p.add_argument("--receipt-path", type=Path)
    args = p.parse_args()

    assert hashlib.sha256(args.source_ledger.read_bytes()).hexdigest() == SOURCE_SHA
    assert blob_sha(args.full.read_bytes()) == FULL_BLOB
    with args.source_ledger.open(encoding="utf-8-sig", newline="") as stream:
        source_rows = list(csv.DictReader(stream))
    assert len(source_rows) == 1330
    source_by_id = {r["candidate_id"]: r for r in source_rows}
    assert len(source_by_id) == 1330
    assert json.loads(args.full.read_text(encoding="utf-8"))["total"] == 1676
    graph = json.loads((HERE / "STAGE_A_1330_SOURCE_URL_OBSERVATION_EQUIVALENCE_20261030.json").read_text(encoding="utf-8"))
    review = json.loads((HERE / "STAGE_A_FIVE_MIXED_POOL_SOURCE_GROUPS_CASE_ADJUDICATION_20261030.json").read_text(encoding="utf-8"))
    assert graph["original_source_ids"] == review["original_population"] == 1330
    assert review["source_baseline_sha256"] == SOURCE_SHA
    assert review["full_git_blob"] == FULL_BLOB
    assert graph["mixed_pool_repeated_url_groups"] == review["mixed_pool_groups_detected_in_full_source_graph"] == 14
    assert len(graph["all_1330_source_url_observation_assignments"]) == 1330
    all_groups = {g["source_url_observation_group_id"]: g for g in graph["all_repeat_url_source_groups"] if g["mixed_original_pool"]}
    selected = review["source_observation_groups"]
    assert len(selected) == review["mixed_pool_groups_with_source_body_evidence_in_this_file"] == 5
    selected_ids = [g["group_id"] for g in selected]
    assert len(set(selected_ids)) == 5
    assert set(selected_ids).issubset(all_groups)
    ids = set()
    for item in selected:
        matching = all_groups[item["group_id"]]
        assert item["source_ids"] == matching["source_ids"]
        assert item["source_url"] == matching["query_aware_url"]
        assert item["original_pools"] == matching["source_row_original_pools"]
        assert item["original_scores"] == matching["source_row_original_scores"]
        assert item["linked_claim_ids"]
        for source_id, pool, score in zip(item["source_ids"], item["original_pools"], item["original_scores"]):
            source = source_by_id[source_id]
            assert source["economic_event_cluster_id"] == "", source_id
            assert source["stage_a_pool"] == pool and int(source["decision_news_value_score"]) == score
            ids.add(source_id)
    assert len(ids) == review["unique_source_ids_covered_in_this_file"] == 10

    cases = review["cases"]
    assert len(cases) == review["economically_distinct_claims_reconstructed_in_this_file"] == 6
    cases_by_id = {c["case_id"]: c for c in cases}
    assert len(cases_by_id) == len(cases)
    case_group_count = Counter(c["source_observation_group_id"] for c in cases)
    assert sorted(case_group_count.values()) == [1, 1, 1, 1, 2]
    for item in selected:
        assert set(item["linked_claim_ids"]) == {c["case_id"] for c in cases if c["source_observation_group_id"] == item["group_id"]}
    for case in cases:
        group = next(x for x in selected if x["group_id"] == case["source_observation_group_id"])
        assert case["source_ids"] == group["source_ids"]
        assert case["execution_credibility_gate"]["status"] in ("PASS", "REVIEW", "FAIL")
        assert case["independent_cardability_gate"]["status"] in ("PASS", "REVIEW", "FAIL")
        assert case["publication_urgency"]["status"] in ("immediate", "near_term", "monitor")
        dv = case["decision_value"]
        assert dv["original_metadata_scores"] == group["original_scores"]
        parts = dv["decision_value_breakdown"]
        assert set(parts) == set(PART_NAMES)
        assert all(isinstance(parts[k], int) and 0 <= parts[k] <= CEILINGS[k] for k in PART_NAMES)
        assert sum(parts.values()) == dv["provisional_reassessed_score"]
        assert dv["classification"] == band(dv["provisional_reassessed_score"])
        assert dv["systemic_scale_denominator"] is None and dv["denominator_gap"]
        assert parts["systemic_scale"] <= 2
        assert parts["technology_performance_safety"] <= TECH_CEILINGS[dv["technology_evidence_level"]]
        assert dv["policy_stage"] is None
        if dv["novelty_cap_basis"] in ("company_target_without_validation_or_effect", "routine_progression_no_material_uncertainty"):
            assert dv["provisional_reassessed_score"] <= 54
        assert case["before_after"]["prior_state"] and case["before_after"]["new_verified_fact"]
        assert case["related_prepass"]["status"] == "HOLD"
        assert case["evidence"] and case["evidence_needed_for_stage_b"]

    china = next(x for x in selected if x["group_id"] == "SOURCE_URL_OBSERVATION_fc68908b1bcbea62")
    assert len(china["linked_claim_ids"]) == 2 and set(china["linked_claim_ids"]) == {
        "RONBAY_BIJIE_LFP_PHASE1_START_20260922", "HUNAN_YUNENG_WENGAN_LFP_EIA_PUBLIC_NOTICE_20260918"
    }
    assert review["formal_new_strict_promotions"] == 0
    assert review["native_stage_a_validator_status"].startswith("NOT_EXECUTED")
    assert len(all_groups) - len(selected) == 9
    receipt = {
        "scope_qc_status": "PASS_NOT_NATIVE_STAGE_A_PASS",
        "original_source_ids_preserved": 1330,
        "selected_mixed_pool_groups": 5,
        "original_source_ids_bounded_case_reviewed": 10,
        "distinct_case_claims": 6,
        "two_China_stages_separated": True,
        "remaining_mixed_pool_groups": 9,
        "formal_new_strict_promotions": 0,
        "formal_unadjudicated_original_source_ids_still": 1285,
        "original_source_sha256": SOURCE_SHA,
        "locked_full_git_blob": FULL_BLOB,
        "evidence_json_sha256": hashlib.sha256((HERE / "STAGE_A_FIVE_MIXED_POOL_SOURCE_GROUPS_CASE_ADJUDICATION_20261030.json").read_bytes()).hexdigest(),
        "source_graph_json_sha256": hashlib.sha256((HERE / "STAGE_A_1330_SOURCE_URL_OBSERVATION_EQUIVALENCE_20261030.json").read_bytes()).hexdigest(),
        "native_stage_a_contract_check": "NOT_EXECUTED_VALID_FULL_UNIVERSE_ARTIFACT_ABSENT",
        "native_stage_a_lineage_check": "NOT_EXECUTED_VALID_FULL_UNIVERSE_ARTIFACT_ABSENT",
    }
    if args.receipt_path:
        with args.receipt_path.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(receipt, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
