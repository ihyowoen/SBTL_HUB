#!/usr/bin/env python3
"""Independent no-loss, stage distinction and numerical check for a bounded source review.

Does not constitute Stage A 0.1P native contract/lineage approval.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE_SHA = "5e78420916b0c1d70ff56bf928779cd969b94fbb15dd4119c841872997486116"
FULL_BLOB = "07a91714e56be2a8bfad10ab63822f0c5cb3f06e"
PARTS = ["market_structure_competition", "supply_demand_price_utilisation", "technology_performance_safety", "cashflow_asset_value", "law_policy_market_access", "systemic_scale", "persistence_irreversibility", "decision_urgency_actionability"]
CAPS = (25, 25, 20, 10, 10, 5, 3, 2)
TECH_CAPS = {"not_applicable":0, "pilot_precommercial":11}


def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source-ledger", type=Path, required=True)
    p.add_argument("--full", type=Path, required=True)
    p.add_argument("--receipt-path", type=Path)
    a = p.parse_args()
    assert hashlib.sha256(a.source_ledger.read_bytes()).hexdigest() == SOURCE_SHA
    assert git_blob(a.full.read_bytes()) == FULL_BLOB
    with a.source_ledger.open(encoding="utf-8-sig",newline="") as stream:
        rows=list(csv.DictReader(stream))
    assert len(rows)==1330
    by_id={r["candidate_id"]:r for r in rows}
    assert len(by_id)==1330
    full=json.loads(a.full.read_text(encoding="utf-8"))
    assert full["total"]==len(full["cards"])==1676
    full_ids={x["id"] for x in full["cards"]}
    data_path=HERE/"STAGE_A_HIGH64_MULTI_SOURCE_EVENT_IDENTITY_ADDENDUM_20261030.json"
    d=json.loads(data_path.read_text(encoding="utf-8"))
    assert d["source_baseline_sha256"]==SOURCE_SHA and d["full_blob"]==FULL_BLOB
    assert d["original_universe"]==1330 and d["scoring_order"]==PARTS
    groups=d["evidence_groups"]
    assert len(groups)==d["subjects"]==6
    group_ids=[]
    for g in groups:
        assert g["source_owner_evidence"] and g["source_ids"] and g["case_ids"]
        assert len(g["source_ids"])==len(set(g["source_ids"]))
        assert all(ev["owner"] and ev["url"].startswith("https://") and ev["stage"] for ev in g["source_owner_evidence"])
        group_ids.extend(g["source_ids"])
    assert len(group_ids)==len(set(group_ids))==d["unique_original_ids_touched"]==18
    assert all(by_id[s]["economic_event_cluster_id"]=="" for s in group_ids)
    assert all(by_id[s]["stage_a_pool"] in ("candidate_review_pool", "watchlist_context_pool") for s in group_ids)
    high_ids={s for s in group_ids if int(by_id[s]["decision_news_value_score"])==64}
    other_ids=set(group_ids)-high_ids
    assert len(high_ids)==d["unique_metadata_64_ids_new"]==15
    assert len(other_ids)==d["other_metadata_ids_same_subject_distinct_stage"]==3
    assert {by_id[s]["decision_news_value_score"] for s in other_ids}=={"56"}
    cases=d["provisional_case_judgments"]
    assert len(cases)==d["event_or_reporting_acts"]==9
    assert len(set(c["case_id"] for c in cases))==9
    mapped=[]
    for c in cases:
        assert c["original_id_set_group"] in range(6)
        assert c["case_id"] in groups[c["original_id_set_group"]]["case_ids"]
        mapped.append(c["case_id"])
        assert c["execution"] in ("PASS","REVIEW","FAIL")
        assert c["independent_cardability"] in ("PASS","REVIEW","FAIL")
        assert c["date_role"] and c["before_after"] and c["missing"] and c["related"].startswith("HOLD")
        assert len(c["scores"])==8
        assert all(isinstance(v,int) and 0<=v<=cap for v,cap in zip(c["scores"],CAPS))
        assert c["scores"][2]<=TECH_CAPS[c["technology_evidence_level"]]
        assert c["scores"][5]<=2
        assert sum(c["scores"])==c["news_value"]
    assert set(mapped)=={v for g in groups for v in g["case_ids"]}
    assert next(c for c in cases if c["case_id"]=="ENERVENUE_11MWH_CHINA_ORDER_SEP23")["event_date"]=="2026-09-23"
    assert next(c for c in cases if c["case_id"]=="ENERVENUE_CHANGZHOU_AMC_LINE_START_SEP24")["event_date"]=="2026-09-24"
    assert next(c for c in cases if c["case_id"]=="DELTA_AKKU_ONE_CONSTRUCTION_PRIOR_FULL_REINFORCEMENT_SEP16")["independent_cardability"]=="FAIL"
    assert {"2026-09-16_EU_01","2026-09-10_EU_01"}.issubset(full_ids)
    assert d["formal_new_promotions"]==0 and d["formal_unadjudicated_remains"]==1285
    assert d["native_stage_a_contract"].startswith("NOT_RUN") and d["native_stage_a_lineage"].startswith("NOT_RUN")
    old1=json.loads((HERE/"STAGE_A_NIO_NYSERDA_BOUNDED_0_1P_REVIEW_20261030.json").read_text(encoding="utf-8"))
    old2=json.loads((HERE/"STAGE_A_THREE_MORE_64_POINT_CANDIDATES_BOUNDED_REVIEW_20261030.json").read_text(encoding="utf-8"))
    prior8={r["candidate_id"] for c in old1["cases"] for r in c["original_source_rows"]}|{s for c in old2["cases"] for s in c["source_ids"]}
    earlier5=json.loads((HERE/"STAGE_A_FIVE_MIXED_POOL_SOURCE_GROUPS_CASE_ADJUDICATION_20261030.json").read_text(encoding="utf-8"))
    earlier9=json.loads((HERE/"STAGE_A_NINE_REMAINING_MIXED_POOL_GROUPS_EVIDENCE_TRIAGE_20261030.json").read_text(encoding="utf-8"))
    conflicts={s for g in earlier5["source_observation_groups"] for s in g["source_ids"]}|{s for g in earlier9["triage_records"] for s in g["original_source_ids"]}
    prev11=json.loads((HERE/"STAGE_A_NEXT_HIGH64_PRIMARY_CASE_REVIEW_20261030.json").read_text(encoding="utf-8"))
    prev11_ids={s for c in prev11["source_case_records"] for s in c["original_source_ids"]}
    assert len(prior8)==8 and len(conflicts)==28 and len(prev11_ids)==11
    assert len(prior8|conflicts|prev11_ids)==47
    assert not(set(group_ids)&(prior8|conflicts|prev11_ids))
    assert len(prior8|conflicts|prev11_ids|set(group_ids))==65
    assert len(high_ids|({s for s in prior8|conflicts|prev11_ids if int(by_id[s]["decision_news_value_score"])>=60}))==33
    qc={"qc_status":"PASS_SCOPED_MULTISOURCE_EVENT_IDENTITY_NOT_NATIVE_STAGE_A_PASS", "original_unique_source_ids":1330,
        "locked_full_card_count":1676, "subjects":6,"distinct_acts":9,"new_source_ids_touched":18,
        "new_metadata64_ids":15,"new_non64_related_id_observations":3,"cumulative_original_source_ids_touched":65,
        "cumulative_high_metadata60plus_source_ids_deeper_or_bounded":33,"remaining_high_metadata60plus_ids":70,
        "formal_unadjudicated_original_ids_still":1285,"new_formal_strict_promotions":0,
        "original_source_sha256":SOURCE_SHA,"full_git_blob":FULL_BLOB,
        "case_artifact_sha256":hashlib.sha256(data_path.read_bytes()).hexdigest(),
        "native_stage_a_artifact_contract":"NOT_EXECUTED_INCOMPLETE_FULL_UNIVERSE",
        "native_stage_a_lineage":"NOT_EXECUTED_INCOMPLETE_FULL_UNIVERSE"}
    if a.receipt_path:
        with a.receipt_path.open("x",encoding="utf-8",newline="\n") as stream:
            json.dump(qc,stream,indent=2,ensure_ascii=False)
            stream.write("\n")
    print(json.dumps(qc,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
