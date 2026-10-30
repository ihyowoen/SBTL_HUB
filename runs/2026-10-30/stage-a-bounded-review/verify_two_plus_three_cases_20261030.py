#!/usr/bin/env python3
"""Independent read-only QC of five case packages / eight original Source IDs.

Never emits a Stage A native or strict promotion result; this is a scoped
integrity and bounded-four-judgment checker only.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE_SHA = "5e78420916b0c1d70ff56bf928779cd969b94fbb15dd4119c841872997486116"
FULL_BLOB = "07a91714e56be2a8bfad10ab63822f0c5cb3f06e"
SCORE_FIELDS = {
    "market_structure_competition": 25,
    "supply_demand_price_utilisation": 25,
    "technology_performance_safety": 20,
    "cashflow_asset_value": 10,
    "law_policy_market_access": 10,
    "systemic_scale": 5,
    "persistence_irreversibility": 3,
    "decision_urgency_actionability": 2,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-ledger", required=True, type=Path)
    ap.add_argument("--full", required=True, type=Path)
    a = ap.parse_args()
    src = a.source_ledger.read_bytes()
    full = a.full.read_bytes()
    assert hashlib.sha256(src).hexdigest() == SOURCE_SHA
    assert hashlib.sha1(b"blob " + str(len(full)).encode() + b"\0" + full).hexdigest() == FULL_BLOB
    ledger = list(csv.DictReader(src.decode("utf-8-sig").splitlines()))
    assert len(ledger) == 1330
    ids = [r["candidate_id"] for r in ledger]
    assert len(set(ids)) == 1330
    by_id = {r["candidate_id"]: r for r in ledger}
    full_cards = json.loads(full)["cards"]
    assert len(full_cards) == 1676

    first = json.loads((HERE / "STAGE_A_NIO_NYSERDA_BOUNDED_0_1P_REVIEW_20261030.json").read_text(encoding="utf-8"))
    second = json.loads((HERE / "STAGE_A_THREE_MORE_64_POINT_CANDIDATES_BOUNDED_REVIEW_20261030.json").read_text(encoding="utf-8"))
    first_source_ids = [r["candidate_id"] for r in first["source_row_disposition_delta"]]
    second_source_ids = [sid for c in second["cases"] for sid in c["source_ids"]]
    all_source_ids = first_source_ids + second_source_ids
    assert len(first_source_ids) == 5 and len(second_source_ids) == 3
    assert len(all_source_ids) == len(set(all_source_ids)) == 8
    assert set(all_source_ids) <= set(ids)
    assert all(by_id[s]["stage_a_pool"] == "candidate_review_pool" for s in all_source_ids)
    assert all(by_id[s]["assessment_status"] == "REVIEW_HOLD" for s in all_source_ids)
    assert all(by_id[s]["decision_news_value_score"] == "64" for s in all_source_ids)
    assert all(not by_id[s]["economic_event_cluster_id"] for s in all_source_ids)
    assert len(first["cases"]) == 2 and len(second["cases"]) == 3
    assert first["baseline"]["formal_unadjudicated_source_ids_after"] == 1285
    assert second["formal_unadjudicated_original_id_count_unchanged"] == 1285
    assert sum(not r["economic_event_cluster_id"] for r in ledger) == 1285

    for c in first["cases"]:
        s = c["decision_value"]
        vals = s["decision_value_breakdown"]
        assert set(vals) == set(SCORE_FIELDS)
        assert all(isinstance(vals[k], int) and 0 <= vals[k] <= SCORE_FIELDS[k] for k in SCORE_FIELDS)
        assert sum(vals.values()) == s["manual_reassessed_score"]
        assert (vals["systemic_scale"] <= 2 or s["systemic_scale_denominator"] is not None)
        assert vals["technology_performance_safety"] == 0
        assert len(c["original_source_rows"]) == c["source_count"]
        assert all(by_id[r["candidate_id"]]["source_row_index"] == str(r["source_row_index"]) for r in c["original_source_rows"])
    for c in second["cases"]:
        score = c["decision_value"]
        vals = score["decision_value_breakdown"]
        assert set(vals) == set(SCORE_FIELDS)
        assert all(isinstance(vals[k], int) and 0 <= vals[k] <= SCORE_FIELDS[k] for k in SCORE_FIELDS)
        assert sum(vals.values()) == score["reassessed_provisional_score"]
        assert (vals["systemic_scale"] <= 2 or score["systemic_scale_denominator"] is not None)
        assert score["prior_metadata_score"] == 64
        assert vals["technology_performance_safety"] == 0
        assert c["source_ids"] == [c["source_ids"][0]]
        assert by_id[c["source_ids"][0]]["source_row_index"] == str(c["original_source_row_index"])
        assert c["source_owner_evidence"] and all(p["url"].startswith("https://") for p in c["source_owner_evidence"])
        assert c["execution_credibility_gate"]["status"] in ("PASS", "REVIEW", "FAIL")
        assert c["independent_cardability_gate"]["status"] in ("PASS", "REVIEW", "FAIL")
        assert c["publication_urgency"]["status"] in ("immediate", "near_term", "monitor")
    assert first["formal_stage_a_strict_promotions"] == 0 if "formal_stage_a_strict_promotions" in first else first["baseline"]["formal_unadjudicated_source_ids_after"] == 1285
    assert second["formal_stage_a_strict_promotions"] == 0
    assert first["native_validation"]["stage_artifact_contract_check_A"].startswith("NOT_EXECUTED")
    assert second["native_stage_a_contract_status"].startswith("NOT_EXECUTED")
    assert len(first["cases"][1]["economic_actions"]) == 8
    assert sum(a["mw"] for a in first["cases"][1]["economic_actions"]) == 950
    print(json.dumps({
        "status": "PASS_SCOPED_EIGHT_SOURCE_FIVE_CASE_QC_NOT_NATIVE_STAGE_A_PASS",
        "source_universe_unique": len(set(ids)),
        "original_formal_0_1P_pending": 1285,
        "bounded_researched_source_ids": all_source_ids,
        "bounded_source_count": len(all_source_ids),
        "bounded_case_count": len(first["cases"]) + len(second["cases"]),
        "strict_promotions": 0,
        "native_stage_a_artifact": "NOT_EXECUTED",
        "source_sha256": SOURCE_SHA,
        "full_blob": FULL_BLOB,
        "two_cases_sha256": hashlib.sha256((HERE / "STAGE_A_NIO_NYSERDA_BOUNDED_0_1P_REVIEW_20261030.json").read_bytes()).hexdigest(),
        "three_cases_sha256": hashlib.sha256((HERE / "STAGE_A_THREE_MORE_64_POINT_CANDIDATES_BOUNDED_REVIEW_20261030.json").read_bytes()).hexdigest()
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
