#!/usr/bin/env python3
"""Independent, source-preserving delta and native Stage A QC for checkpoint #16."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

PREVIOUS_SHA="8bd11020fea3c8874837fa2a30b5bab619e0174a7e92b43661d5c5b225a230c6"
STRICT_ROWS={19,79,122,173}
SUPPORT_ROWS={123,138,468}
WATCH_ROWS={120,172,176,177,178,179}
CHANGED_ROWS=STRICT_ROWS|SUPPORT_ROWS|WATCH_ROWS
ORIGINAL54_HOLD_ROWS={8,48,244,614,916}
IDENTITY_FIELDS=("story_id","candidate_id","source_row_index","headline_raw","primary_url","origin")
POOLS=("strict_passed_spec","candidate_review_pool","watchlist_context_pool",
       "reject_or_support_only_pool","existing_reinforcement")
ALLOWED_TOP_CHANGES={
    *POOLS,"decision_ledger","review_pool_resolution_ledger",
    "promotion_reassessment_ledger","summary","review_pool_partition_summary",
    "pre_native_0_1P_attachment_manifest_20261101",
    "formal_0_1P_remaining_pre_native_cases_20261101","recommended_for","next_call_recommendation",
}

def read(p:Path):
    with p.open(encoding="utf-8") as f:
        return json.load(f)

def digest(p:Path):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda:f.read(1048576),b""):
            h.update(block)
    return h.hexdigest()

def chk(label,condition):
    if not condition:
        raise AssertionError(label)

def main():
    p=argparse.ArgumentParser()
    for f in ("base","artifact","full","prenative","receipt","native_root","output"):
        p.add_argument("--"+f.replace("_","-"),required=True,type=Path)
    a=p.parse_args()
    chk("exact previous checkpoint hash",digest(a.base)==PREVIOUS_SHA)
    prev,now,full,pre54,receipt=(read(p) for p in (a.base,a.artifact,a.full,a.prenative,a.receipt))
    chk("actual native hash recorded",digest(a.artifact)==receipt["output_sha256"])
    chk("full source universe unchanged",len(prev["decision_ledger"])==len(now["decision_ledger"])==1330)
    chk("full locked 1676",len(full["cards"])==1676)
    chk("all original Source IDs same order",
        [r["story_id"] for r in prev["decision_ledger"]]==[r["story_id"] for r in now["decision_ledger"]])
    before={r["source_row_index"]:r for r in prev["decision_ledger"]}
    after={r["source_row_index"]:r for r in now["decision_ledger"]}
    chk("all row indices unique",len(before)==len(after)==1330 and set(before)==set(after))
    changed={i for i in before if before[i]!=after[i]}
    chk("only intended 13 Source ID rows edited",changed==CHANGED_ROWS)
    for i in before:
        for key in IDENTITY_FIELDS:
            chk(f"original source identity preserved {i}:{key}",before[i].get(key)==after[i].get(key))
    chk("all prior korean mixed Source IDs preserved in original pools and decisions",
        all(before[i]==after[i] for i in ORIGINAL54_HOLD_ROWS|{228}))
    changed_ids={i:before[i]["story_id"] for i in CHANGED_ROWS}
    strict_ids={changed_ids[i] for i in STRICT_ROWS}
    support_ids={changed_ids[i] for i in SUPPORT_ROWS}
    watch_ids={changed_ids[i] for i in WATCH_ROWS}
    chk("14 preexisting strict spec objects identical",now["strict_passed_spec"][:14]==prev["strict_passed_spec"])
    new_strict=now["strict_passed_spec"][14:]
    chk("four new independent strict representatives",len(new_strict)==4 and
        {v["story_id"] for v in new_strict}==strict_ids and len(now["strict_passed_spec"])==18)
    for x in new_strict:
        i=x["source_row_index"]
        chk(f"strict original source only {i}",x["source_story_ids"]==[x["story_id"]])
        chk(f"strict Stage B blocked {i}",x["stage_b_authorized"] is False and
            x["accepted_facts_approved"] is False and x["canonical_card_write_allowed"] is False)
        chk(f"strict scored exact arithmetic {i}",sum(x["decision_value_breakdown"].values())==x["decision_news_value_score"])
        chk(f"strict official original owner URLs retained {i}",len(x["formal_0_1P_remaining_cases_20261101"]["owner_urls"])>0)
    strict_by_row={x["source_row_index"]:x for x in new_strict}
    chk("esVolta field pilot not standardized market",strict_by_row[19]["technology_validation_stage"]=="field_demonstration"
        and "9.2GWh" in strict_by_row[19]["summary_hint"]
        and "not independently" in strict_by_row[19]["remaining_uncertainty"].lower())
    chk("Ofgem no final approval not implemented",strict_by_row[122]["policy_stage"]==1 and
        strict_by_row[122]["legal_policy_stage"]=="stage_1_roadmap_consultation_or_draft_standard" and
        strict_by_row[122]["adoption_date"].startswith("NOT_ADOPTED") and
        strict_by_row[122]["effective_date"].startswith("NOT_EFFECTIVE") and
        strict_by_row[122]["decision_news_value_score"]<=54)
    chk("Canada PV only final customs act",strict_by_row[173]["policy_stage"]==5 and
        "태양광" in strict_by_row[173]["summary_hint"] and
        "battery" in strict_by_row[173]["remaining_uncertainty"].lower())
    chk("Hirasol market prequal not 3.8MW physical expansion",strict_by_row[79]["execution_anchor_type"]=="verified_bess_balancing_market_bid_eligibility"
        and "1,900kW" in strict_by_row[79]["systemic_scale_denominator"] and
        "3,800kW" in strict_by_row[79]["systemic_scale_denominator"])
    chk("prior support records unchanged",now["reject_or_support_only_pool"][:33]==prev["reject_or_support_only_pool"])
    chk("support cluster exact three",len(now["reject_or_support_only_pool"])==36 and
        {x["story_id"] for x in now["reject_or_support_only_pool"][33:]}==support_ids)
    for x in now["reject_or_support_only_pool"][33:]:
        chk("support-only mapped to 1 strict source",x["baseline_match"] in strict_ids and
            x["whether_support_source_only"] is True)
    chk("watch context count exact 6 newly reclassified from candidate",len(now["watchlist_context_pool"])==660 and
        {x["story_id"] for x in now["watchlist_context_pool"] if x.get("formal_0_1P_watch_context_20261101")}==watch_ids)
    for x in now["watchlist_context_pool"]:
        if x["story_id"] in watch_ids:
            chk("formal watch remains no card",x["stage_b_authorized"] is False and
                x["canonical_card_write_allowed"] is False and
                x["final_review_pool_disposition"]=="watchlist_only_after_review")
    chk("all prior existing Full reinforcements identical",now["existing_reinforcement"]==prev["existing_reinforcement"])
    chk("all prior strict and pool totals match",len(now["candidate_review_pool"])==586 and
        len(now["existing_reinforcement"])==30 and
        sum(len(now[k]) for k in POOLS)==1330)
    emitted=[x["story_id"] for pool in POOLS for x in now[pool]]
    chk("one and only one native pool entry per original source",len(emitted)==len(set(emitted))==1330 and
        set(emitted)=={x["story_id"] for x in now["decision_ledger"]})
    chk("previous promotion ledger prefix immutable",now["promotion_reassessment_ledger"][:86]==prev["promotion_reassessment_ledger"])
    chk("exact 13 new promotion disposition audit entries",len(now["promotion_reassessment_ledger"])==99 and
        {x["candidate_id"] for x in now["promotion_reassessment_ledger"][86:]}==set(changed_ids.values()))
    old_res={x["story_id"]:x for x in prev["review_pool_resolution_ledger"]}
    new_res={x["story_id"]:x for x in now["review_pool_resolution_ledger"]}
    chk("four strict exit open review ledger",set(old_res)-set(new_res)==strict_ids and len(new_res)==1282)
    for sid,x in new_res.items():
        if sid not in support_ids|watch_ids:
            chk(f"older review carryforward intact {sid}",x==old_res[sid])
        elif sid in support_ids:
            chk("support disposition",x["current_disposition"]=="reject_or_support_only_pool")
        else:
            chk("watch disposition",x["current_disposition"]=="watchlist_context_pool" and
                x["carry_forward_policy"]=="carry_forward_to_watchlist")
    chk("all previous top-level manifests unchanged",all(prev[k]==now[k] for k in prev
        if k.startswith("pre_native_") and k!="pre_native_0_1P_attachment_manifest_20261101"))
    previous_manifest=prev["pre_native_0_1P_attachment_manifest_20261101"]
    manifest=now["pre_native_0_1P_attachment_manifest_20261101"]
    chk("source attachment SHA immutable",manifest["source_input_sha256"]==previous_manifest["source_input_sha256"])
    chk("old 41 formalized ID prefix exactly preserved",manifest["formal_review_completed_source_ids"][:41]
        ==previous_manifest["formal_review_completed_source_ids"])
    chk("54 new since base45, 99 total, 1231 pending",len(manifest["formal_review_completed_source_ids"])==54 and
        manifest["new_formal_decisions"]==54 and manifest["new_strict_promotions"]==10 and
        manifest["remaining_formal_source_count"]==1231)
    original54_ids={before[i]["story_id"] for e in pre54["case_definitions"] for i in e["source_row_indices"]}
    formal_original54=original54_ids & set(manifest["formal_review_completed_source_ids"])
    unresolved_rows={i for e in pre54["case_definitions"] for i in e["source_row_indices"]
                     if before[i]["story_id"] not in formal_original54}
    chk("49 of originally 54 resolved, 5 hold",len(formal_original54)==49 and
        unresolved_rows==ORIGINAL54_HOLD_ROWS)
    audit=now["formal_0_1P_remaining_pre_native_cases_20261101"]
    chk("exact case arithmetic",len(audit["source_decisions"])==13 and
        audit["source_disposition_counts"]=={"strict":4,"support_only":3,"watch_context":6} and
        audit["source_rows_original54_remaining_unresolved"]==sorted(ORIGINAL54_HOLD_ROWS))
    chk("Flow live site discrepancy explicitly held",audit["flow_power_announcement_vs_live_capacity_disagreement"]
        =={"dated_release_MWh":223,"live_site_MWh":233,"resolution":"HOLD_MWH_ENGINEERING_SPEC_CHECK","no_new_September_construction":True})
    chk("prior checkpoint metadata identical",all(now[k]==prev[k] for k in (
        "formal_0_1P_resolution_20261101","formal_0_1P_two_korean_events_20261101",
        "formal_0_1P_four_usjp_economic_events_20261101")))
    chk("only authorized top-level delta",{k for k in set(prev)|set(now) if prev.get(k)!=now.get(k)}<=ALLOWED_TOP_CHANGES)
    chk("complete summary counts",now["summary"]["strict_passed_spec_count"]==18 and
        now["summary"]["processed_priority_source_observations"]==99 and
        now["summary"]["unprocessed_editorial_observations"]==1231 and
        now["summary"]["needs_review_count"]==1282)
    chk("stage B and canonical mutations are prohibited",audit["new_cards_created"]==0 and
        audit["stage_b_executed"] is False and audit["canonical_main_full_related_mutations"]==0 and
        audit["global_editorial_stage_a_status"].startswith("HOLD"))
    chk("receipt matches 13 changed rows",receipt["new_formalized"]==13 and
        receipt["formal_pending"]==1231 and receipt["strict_count"]==18)
    native={}
    for name,argv in (
        ("artifact_contract",["validation_scripts/stage_artifact_contract_check.py","A",a.artifact.name]),
        ("lineage_contract",["validation_scripts/stage_lineage_contract_check.py","stage_a",a.artifact.name]),
    ):
        result=subprocess.run([sys.executable,*argv],cwd=a.native_root,text=True,capture_output=True,check=False)
        native[name]={"return_code":result.returncode,"stdout":result.stdout.strip(),"stderr":result.stderr.strip()}
        chk(f"native {name} PASS",result.returncode==0 and "PASS" in result.stdout)
    qc={
        "result":"PASS_1330_NOLOSS_13_FORMAL_SOURCE_DECISIONS_4_STRICT_BOTH_NATIVE_CHECKS",
        "scope":"Independent ledger/source order and immutable-old-artifact check; native schema checks do not authenticate Stage B content",
        "base_sha256":digest(a.base),"output_sha256":digest(a.artifact),"full_reference_sha256":digest(a.full),
        "original_sources_preserved":1330,"only_changed_source_row_indices":sorted(CHANGED_ROWS),
        "strict_representative_rows":sorted(STRICT_ROWS),"same_event_support_source_rows":sorted(SUPPORT_ROWS),
        "formal_watch_source_rows":sorted(WATCH_ROWS),"still_pending_original54_rows":sorted(unresolved_rows),
        "cases":7,"prior_formal":86,"new_formal":13,"cumulative_formal":99,"formal_pending":1231,
        "pool_counts":{k:len(now[k]) for k in POOLS},
        "native_checks":native,"global_stage_a_status":"HOLD","stage_b_executed":False,
        "main_full_related_production_mutated":False,
    }
    with a.output.open("w",encoding="utf-8",newline="\n") as f:
        json.dump(qc,f,ensure_ascii=False,indent=2)
        f.write("\n")
    print(json.dumps({"result":qc["result"],"output_sha256":qc["output_sha256"],
                      "pool_counts":qc["pool_counts"],"formal_pending":1231},ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
