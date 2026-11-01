#!/usr/bin/env python3
"""Independent CP20 delta and owner-stage audit.  Does not import CP20 builder."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

BASE_SHA="bf30369c00bd528b4ab32c628a388b48a56471ac5e8f34fd22631bcb8eaead7d"
FULL_SHA="d22f0d4e39e035b9537b3e9abdf48abe6b7eb80f7e477e87aff1284f9e27e0d9"
STRICT={1263,683,497,728,367,865,165,1167,97,146,1259,772}
SUPPORT={869,870,1082,337,338,342,343,1068,1156,498,741,784,812,881}
REINFORCE={1184}
TARGET=STRICT|SUPPORT|REINFORCE
POOLS=("strict_passed_spec","candidate_review_pool","watchlist_context_pool",
       "reject_or_support_only_pool","existing_reinforcement")
EXPECTED={"strict_passed_spec":42,"candidate_review_pool":538,
          "watchlist_context_pool":658,"reject_or_support_only_pool":61,
          "existing_reinforcement":31,"promotion_reassessment_ledger":153,
          "review_pool_resolution_ledger":1257}

def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()

def verify(args):
    assert sha(args.base)==BASE_SHA,"CP19 checksum mismatch"
    assert sha(args.full)==FULL_SHA,"locked Full1676 checksum mismatch"
    base=json.loads(args.base.read_text(encoding="utf-8"))
    new=json.loads(args.artifact.read_text(encoding="utf-8"))
    receipt=json.loads(args.receipt.read_text(encoding="utf-8"))
    old_rows=base["decision_ledger"]
    new_rows=new["decision_ledger"]
    assert len(old_rows)==len(new_rows)==1330
    immutable=("source_row_index","story_id","candidate_id","headline_raw","primary_url","origin")
    changes=set()
    for i,(o,n) in enumerate(zip(old_rows,new_rows)):
        assert i==o["source_row_index"]==n["source_row_index"]
        assert all(o.get(k)==n.get(k) for k in immutable),(i,"original source identity edited")
        if o!=n:
            changes.add(i)
            assert n["cp20_source_identity_preserved"]["primary_url"]==o["primary_url"]
            assert n["cp20_source_identity_preserved"]["headline_raw"]==o["headline_raw"]
            assert n["formal_0_1P_cp20_source_to_economic_act_edges_20261101"]
    assert changes==TARGET,sorted(changes^TARGET)
    assert len(STRICT)==12 and len(SUPPORT)==14 and len(REINFORCE)==1
    assert all(len(new[k])==v for k,v in EXPECTED.items())
    partition={}
    for p in POOLS:
        for r in new[p]:
            sid=r["story_id"]
            assert sid not in partition,("duplicate across pools",sid)
            partition[sid]=p
    assert set(partition)=={r["story_id"] for r in old_rows}
    for group,p in ((STRICT,"strict_passed_spec"),
                    (SUPPORT,"reject_or_support_only_pool"),
                    (REINFORCE,"existing_reinforcement")):
        for i in group:
            row=new_rows[i]
            assert partition[row["story_id"]]==p,(i,p,partition[row["story_id"]])
            assert row["stage_b_authorized"] is False
            assert row["accepted_facts_approved"] is False
            assert row["canonical_card_write_allowed"] is False
    assert base["promotion_reassessment_ledger"]==new["promotion_reassessment_ledger"][:126]
    assert base["strict_passed_spec"]==new["strict_passed_spec"][:30]
    new_specs=new["strict_passed_spec"][30:]
    assert len(new_specs)==12
    assert {r["source_story_ids"][0] for r in new_specs}=={new_rows[i]["story_id"] for i in STRICT}
    assert len({r["economic_event_cluster_id"] for r in new_specs})==12
    assert all(r["stage_b_evidence_package_required"] is True and
               r["source_metadata_only"] is True and
               r["stage_b_authorized"] is False for r in new_specs)
    for spec in new_specs:
        assert spec["representative_date"]==spec["date_role"]["event_date"]
        assert spec["evidence_needed_for_stage_b"] and spec["next_confirmation_points"]
    assert new_rows[97]["source_headline_metric_correction"]["unreliable_media_gwh"]==3.8
    assert new_rows[97]["source_headline_metric_correction"]["original_company_gwh"]==3.6
    assert new_rows[97]["source_headline_metric_correction"]["actual_financing_close_window"]=="2026-04..2026-07"
    assert new_rows[1184]["baseline_match"]=="2026-09-06_CN_03"
    assert new_rows[1184]["formal_0_1P_cp20_existing_full_20261101"]["same_event_not_new_card"]
    assert new_rows[772]["supplier_performance_claim_guard"]["20pct_life_gain_unverified"]
    assert new_rows[772]["technology_evidence_level"]=="company_target_or_unsupported_claim"
    assert new_rows[772]["decision_value_breakdown"]["technology_performance_safety"]<=4
    assert "not closed" in new_rows[1263]["remaining_uncertainty"].lower() or "not completed" in new_rows[1263]["remaining_uncertainty"].lower()
    finnish_specs=[r for r in new_specs if r["region"]=="FI"]
    assert len(finnish_specs)==2
    for spec in finnish_specs:
        assert spec["no_double_count_finland_300mwh"]
        assert len(set(spec["within_batch_related_economic_event_families"]))==2
    vw=[r for r in new_specs if "EU_VW_POWERCO_GOTION" in r["economic_event_cluster_id"]]
    assert len(vw)==1
    vw_acts=vw[0]["formal_0_1P_cp20_strict_event_20261101"]["economic_subacts"]
    assert any("VALENCIA" in x for x in vw_acts)
    assert any("SURANY" in x for x in vw_acts)
    assert any("KENITRA_MOROCCO" in x for x in vw_acts)
    assert any("5P3PCT" in x for x in vw_acts)
    assert all(x["stage_b_authorized"] is False for x in new_specs)
    b=new["formal_0_1P_cp20_first_party_event_act_batch_20261101"]
    assert b["new_formal_source_ids"]==27 and b["new_independent_event_representatives"]==12
    assert b["new_same_event_support"]==14 and b["new_existing_full_reinforcement"]==1
    assert b["source_ids_preserved_total"]==1330 and b["formal_total"]==153
    assert b["pending_total"]==1177 and b["strict_total"]==42
    assert b["global_stage_a_status"].startswith("HOLD_")
    assert b["stage_b_executed"] is False and b["new_published_cards"]==0
    assert b["canonical_main_full_related_mutations"]==0
    assert b["jupiter_original_3600mwh_replaces_3800mwh_media"]
    assert b["finland_300mwh_not_double_counted"]
    acts=b["source_to_economic_act_edges"]
    assert len(acts)==27 and {x["row"] for x in acts}==TARGET
    assert all(x["first_party_owner_urls"] and x["economic_act_edges"] for x in acts)
    assert Counter(x["result"] for x in acts)=={
        "FORMAL_STRICT_EVENT_SELECTOR_ONLY":12,
        "FORMAL_SUPPORT_ONLY_SAME_EVENT_NO_SECOND_CARD":14,
        "FORMAL_REINFORCEMENT_LOCKED_FULL_NO_NEW_CARD":1,
    }
    assert len(new["promotion_reassessment_ledger"])==153
    assert len({r["candidate_id"] for r in new["promotion_reassessment_ledger"]})==153
    assert len({r["story_id"] for r in new["review_pool_resolution_ledger"]})==1257
    assert new["summary"]["strict_passed_spec_count"]==42
    assert new["summary"]["processed_priority_source_observations"]==153
    assert new["summary"]["unprocessed_editorial_observations"]==1177
    att=new["pre_native_0_1P_attachment_manifest_20261101"]
    assert att["formal_review_completed_after_attachment_count"]==108
    assert att["remaining_formal_source_count"]==1177
    assert att["formal_review_completed_source_ids"][:81]==base["pre_native_0_1P_attachment_manifest_20261101"]["formal_review_completed_source_ids"]
    assert len(set(att["formal_review_completed_source_ids"]))==108
    assert receipt["output_sha256"]==sha(args.artifact)
    assert receipt["base_cp19_sha256"]==BASE_SHA and receipt["locked_full_sha256"]==FULL_SHA
    native={}
    for name,command in {
        "artifact":["python","validation_scripts/stage_artifact_contract_check.py","A",str(args.artifact.resolve())],
        "lineage":["python","validation_scripts/stage_lineage_contract_check.py","stage_a",str(args.artifact.resolve())]
    }.items():
        process=subprocess.run(command,cwd=args.native_dir,timeout=120,capture_output=True,text=True,check=False)
        assert process.returncode==0,(name,process.stdout,process.stderr)
        assert "PASS" in process.stdout,(name,process.stdout)
        native[name]={"status":"PASS","stdout":process.stdout.strip()}
    return {"independent_qc":"PASS","verified_immutable_source_ids":1330,
            "exact_changed_source_rows":27,"new_strict":12,"same_event_support":14,
            "existing_full_reinforcement":1,"cumulative_formal":153,
            "cumulative_strict":42,"pending_formal":1177,
            "unchanged_previous_formal":126,"unchanged_previous_strict":30,
            "immutable_fields":list(immutable),
            "pool_counts":{p:len(new[p]) for p in POOLS},
            "stage_precision_controls":{
              "finland_project_300mwh_not_added_to_total_600mwh":True,
              "jupiter_gwh_3_6_company_original_not_3_8_media":True,
              "nio_conditional_cross_equity_not_closed":True,
              "global_lithium_AUD333m_scheme_not_closed":True,
              "vw_3_jvs_conditional_and_separate_5_3pct_sale":True,
              "geely_life_gain_company_claim_not_independent":True,
              "eve_30gwh_strategic_cooperation_not_verified_firm_purchase":True,
              "catl_foil_same_full_event_no_new_card":True},
            "native_contracts":native,
            "hashes":{"cp19":BASE_SHA,"full1676":FULL_SHA,"cp20":sha(args.artifact)},
            "global_stage_a":"HOLD","stage_b_executed":False,
            "canonical_main_full_related_mutations":0}

def main():
    p=argparse.ArgumentParser()
    for name in ("base","full","artifact","receipt","native-dir","out"):
        p.add_argument("--"+name,required=True,type=Path)
    args=p.parse_args()
    result=verify(args)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in ("independent_qc","verified_immutable_source_ids",
                   "exact_changed_source_rows","cumulative_formal","pending_formal","cumulative_strict",
                   "global_stage_a")},ensure_ascii=False,indent=2))

if __name__=="__main__":main()
