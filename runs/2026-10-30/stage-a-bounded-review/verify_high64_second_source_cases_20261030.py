#!/usr/bin/env python3
"""Read-only original-corpus QC of 8 new source-backed Stage A subject reviews.

PASS confirms coverage, source identities, evidence annotations and numerical
discipline for this bounded file. It is NOT native Stage A contract or lineage QC.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEDGER_SHA = "5e78420916b0c1d70ff56bf928779cd969b94fbb15dd4119c841872997486116"
FULL_SHA = "07a91714e56be2a8bfad10ab63822f0c5cb3f06e"
DIMENSIONS = [
    "market_structure_competition", "supply_demand_price_utilisation",
    "technology_performance_safety", "cashflow_asset_value",
    "law_policy_market_access", "systemic_scale",
    "persistence_irreversibility", "decision_urgency_actionability"
]
CAPS = [25, 25, 20, 10, 10, 5, 3, 2]
TECH_CAPS = {"not_applicable": 0, "company_target_or_unsupported_claim": 4,
             "pilot_precommercial": 11, "commercial_scale_or_long_duration_field": 20}


def blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\x00" + data).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source-ledger", type=Path, required=True)
    p.add_argument("--full", type=Path, required=True)
    p.add_argument("--receipt-path", type=Path)
    a = p.parse_args()
    ledger_bytes = a.source_ledger.read_bytes()
    full_bytes = a.full.read_bytes()
    assert hashlib.sha256(ledger_bytes).hexdigest() == LEDGER_SHA
    assert blob_sha(full_bytes) == FULL_SHA
    src = list(csv.DictReader(ledger_bytes.decode("utf-8-sig").splitlines()))
    assert len(src) == 1330
    by_id = {r["candidate_id"]: r for r in src}
    assert len(by_id) == 1330
    full_cards = json.loads(full_bytes)["cards"]
    assert len(full_cards) == 1676
    full_ids = {c["id"] for c in full_cards}
    data_path = HERE / "STAGE_A_NEXT_HIGH64_PRIMARY_CASE_REVIEW_20261030.json"
    data = json.loads(data_path.read_text(encoding="utf-8"))
    assert data["original_source_sha256"] == LEDGER_SHA
    assert data["locked_full_git_blob"] == FULL_SHA
    assert data["source_universe"] == 1330
    assert data["score_dimension_order"] == DIMENSIONS
    cases = data["source_case_records"]
    assert len(cases) == 9 == data["distinct_economic_or_reporting_acts"]
    assert len({c["case_id"] for c in cases}) == 9
    ids = set()
    for c in cases:
        assert c["original_source_ids"] and c["before_after"]
        assert c["event_actor_asset"] and c["event_date_role"]
        assert c["remaining_primary_gap"] and c["related_prepass"].startswith("HOLD")
        assert c["formal_0_1P_disposition"] == "HOLD_NOT_NATIVE"
        assert c["execution_gate_provisional"] in ("PASS", "REVIEW", "FAIL")
        assert c["independent_cardability_gate_provisional"] in ("PASS", "REVIEW", "FAIL")
        assert c["publication_urgency_provisional"] in ("monitor", "near_term", "immediate")
        assert c["primary_evidence"] and all(x["owner"] and x["url"].startswith("https://") and x["supports"] for x in c["primary_evidence"])
        scores = c["eight_scores"]
        assert len(scores) == 8 and all(isinstance(v, int) and 0 <= v <= cap for v, cap in zip(scores, CAPS))
        assert sum(scores) == c["news_value_score_provisional"]
        assert scores[2] <= TECH_CAPS[c["technology_evidence_level"]]
        assert scores[5] <= 2  # absent reliable denominator
        assert set(c["full_baseline_candidate_ids"]).issubset(full_ids)
        for sid in c["original_source_ids"]:
            assert sid in by_id and by_id[sid]["economic_event_cluster_id"] == ""
            assert by_id[sid]["stage_a_pool"] in ("candidate_review_pool", "watchlist_context_pool")
            ids.add(sid)
    assert len(ids) == data["all_original_source_ids_associated"] == 11
    q = json.loads((HERE / "STAGE_A_103_SOURCE_HIGH_METADATA_NON_DECISION_INVENTORY_20261030.json").read_text(encoding="utf-8"))
    high_ids = {r["candidate_id"] for r in q["queue"]}
    assert len(high_ids) == 103
    assert len(ids & high_ids) == data["new_64_metadata_source_ids_deeper_reviewed"] == 9
    assert {int(by_id[sid]["decision_news_value_score"]) for sid in ids & high_ids} == {64}
    assert len(ids - high_ids) == 2
    assert {by_id[sid]["decision_news_value_score"] for sid in ids - high_ids} == {"26", "44"}
    assert set(next(c for c in cases if c["case_id"] == "GREENERY_AMR_LTO_MASS_SUPPLY_202608")["original_source_ids"]) == set(next(c for c in cases if c["case_id"] == "GREENERY_KEPCO_SMART_CABINET_AWARD_2026_UNDATED")["original_source_ids"])
    assert next(c for c in cases if c["case_id"] == "CATL_DHL_EU_FREIGHT_MOU_20260914")["actual_event_date"] == "2026-09-14"
    assert next(c for c in cases if c["case_id"] == "ADVAIT_HITHIUM_UPTO1GWH_MSA_20260918")["actual_event_date"] == "2026-09-18"
    assert next(c for c in cases if c["case_id"] == "KEYANG_ANSAN_PROPERTY_SALE_20260918")["independent_cardability_gate_provisional"] == "FAIL"
    assert data["original_newly_strict_promoted"] == 0 and data["scope_not_native_pass"]
    previous = json.loads((HERE / "STAGE_A_FIVE_MIXED_POOL_SOURCE_GROUPS_CASE_ADJUDICATION_20261030.json").read_text(encoding="utf-8"))
    earlier_ids = set()
    for g in previous["source_observation_groups"]:
        earlier_ids.update(g["source_ids"])
    nine = json.loads((HERE / "STAGE_A_NINE_REMAINING_MIXED_POOL_GROUPS_EVIDENCE_TRIAGE_20261030.json").read_text(encoding="utf-8"))
    for x in nine["triage_records"]:
        earlier_ids.update(x["original_source_ids"])
    assert not (ids & earlier_ids), "high-score cases accidentally double-counted cross-pool set"
    assert len(earlier_ids) == 28
    first = json.loads((HERE / "STAGE_A_NIO_NYSERDA_BOUNDED_0_1P_REVIEW_20261030.json").read_text(encoding="utf-8"))
    second = json.loads((HERE / "STAGE_A_THREE_MORE_64_POINT_CANDIDATES_BOUNDED_REVIEW_20261030.json").read_text(encoding="utf-8"))
    old_first_ids = {r["candidate_id"] for c in first["cases"] for r in c["original_source_rows"]}
    old_second_ids = {sid for c in second["cases"] for sid in c["source_ids"]}
    prior_eight = old_first_ids | old_second_ids
    assert len(prior_eight) == 8
    assert not (prior_eight & earlier_ids)
    assert not (prior_eight & ids)
    assert len(prior_eight | earlier_ids | ids) == 47
    assert data["native_artifact_contract_check"].startswith("NOT_EXECUTED")
    assert data["native_lineage_contract_check"].startswith("NOT_EXECUTED")
    receipt = {
      "qc_status": "PASS_SCOPED_HIGH64_CASE_EVIDENCE_NOT_NATIVE_PASS",
      "source_universe_count": 1330,
      "full_card_count": 1676,
      "new_source_ids_associated": len(ids),
      "new_metadata64_source_ids_researched": len(ids & high_ids),
      "new_nonhigh_corresponding_source_ids": len(ids - high_ids),
      "subject_cases": data["distinct_subjects"],
      "distinct_claim_events": len(cases),
      "all_mixed_pool_original_ids_prior_first_level": len(earlier_ids),
      "previous_other_high64_bounded_ids": len(prior_eight),
      "cumulative_original_ids_touched_or_triaged": len(prior_eight | earlier_ids | ids),
      "high_metadata60_plus_total": len(high_ids),
      "previous_high_metadata_source_ids_deeper": 9,
      "cumulative_high_metadata_source_ids_deeper": 18,
      "high_metadata_source_ids_remaining": 85,
      "original_formal_unadjudicated_remains": 1285,
      "new_formal_strict_promotions": 0,
      "source_sha256": LEDGER_SHA,
      "full_git_blob_sha": FULL_SHA,
      "review_json_sha256": hashlib.sha256(data_path.read_bytes()).hexdigest(),
      "formal_native_stage_a_contract": "NOT_EXECUTED_INCOMPLETE_FULL_UNIVERSE_ARTIFACT",
      "formal_native_stage_a_lineage": "NOT_EXECUTED_INCOMPLETE_FULL_UNIVERSE_ARTIFACT"
    }
    if a.receipt_path:
        with a.receipt_path.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(receipt, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
