#!/usr/bin/env python3
"""Independent no-loss ledger and two native schema QC tests for checkpoint #15."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys

BASE_SHA = "32cde5ebdfe5dbb751c8fba2f1cc62c2ef6a3d0647efa00f8c10ff2498cbb69e"
ROW_GROUPS = {
    "US_GEORGIA_ROBINS":[86],
    "CN_EVE_FLUENCE":[16,116,133,158,1265],
    "US_JP_FACTORIAL_MITSUI":[126],
    "JP_PANASONIC_KADOMA":[78,119],
    "US_FLEXGEN_EXISTING_FULL":[115],
}
REP_ROWS={86,1265,126,78}
SUPPORT_ROWS={16,116,133,158,119}
REINFORCE_ROWS={115}
HOLD_ROWS={8}
ALL_ROWS=REP_ROWS|SUPPORT_ROWS|REINFORCE_ROWS
IDENTITY_FIELDS=("story_id","candidate_id","source_row_index","primary_url","headline_raw")
OUTPUT_POOLS=("strict_passed_spec","candidate_review_pool","watchlist_context_pool",
              "reject_or_support_only_pool","existing_reinforcement")
EXACT_TOP_CHANGES={
    "strict_passed_spec","candidate_review_pool","watchlist_context_pool",
    "reject_or_support_only_pool","existing_reinforcement", "decision_ledger",
    "promotion_reassessment_ledger", "review_pool_resolution_ledger", "summary",
    "review_pool_partition_summary", "pre_native_0_1P_attachment_manifest_20261101",
    "formal_0_1P_four_usjp_economic_events_20261101","next_call_recommendation","recommended_for",
}


def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):
            h.update(chunk)
    return h.hexdigest()


def read(path:Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def check(label:str,predicate:bool):
    if not predicate:
        raise AssertionError(label)


def main():
    p=argparse.ArgumentParser()
    for field in ("base","artifact","full","receipt","native_root","output"):
        p.add_argument("--"+field.replace("_","-"),required=True,type=Path)
    a=p.parse_args()
    check("previous canonical checkpoint hash",sha(a.base)==BASE_SHA)
    old,new,full,receipt=read(a.base),read(a.artifact),read(a.full),read(a.receipt)
    check("result hash equals receipt",sha(a.artifact)==receipt["output_sha256"])
    check("prior 1330 source universe",len(old["decision_ledger"])==len(new["decision_ledger"])==1330)
    check("original source IDs in exact original order",[r["story_id"] for r in old["decision_ledger"]]
          ==[r["story_id"] for r in new["decision_ledger"]])
    pre={r["source_row_index"]:r for r in old["decision_ledger"]}
    post={r["source_row_index"]:r for r in new["decision_ledger"]}
    check("1330 unique source rows",len(pre)==len(post)==1330 and pre.keys()==post.keys())
    changed={idx for idx in pre if pre[idx]!=post[idx]}
    check("exact ten changed decisions",changed==ALL_ROWS)
    check("mixed Factorial interview held unchanged",all(pre[idx]==post[idx] for idx in HOLD_ROWS))
    for idx in pre:
        for field in IDENTITY_FIELDS:
            check(f"preserve original {idx}:{field}",pre[idx].get(field)==post[idx].get(field))
    ids={idx:post[idx]["story_id"] for idx in ALL_ROWS}
    new_strict_ids={ids[idx] for idx in REP_ROWS}
    new_support_ids={ids[idx] for idx in SUPPORT_ROWS}
    reinforce_id=ids[115]
    check("all preexisting ten strict specs identical",new["strict_passed_spec"][:10]==old["strict_passed_spec"])
    check("strict 10+4",len(new["strict_passed_spec"])==14 and
          {r["story_id"] for r in new["strict_passed_spec"][10:]}==new_strict_ids)
    for strict in new["strict_passed_spec"][10:]:
        rid=strict["story_id"]
        check(f"strict source single original ID {rid}",strict["source_story_ids"]==[rid])
        check(f"strict not Stage B {rid}",strict["stage_b_authorized"] is False and
              strict["accepted_facts_approved"] is False and strict["canonical_card_write_allowed"] is False)
        check(f"strict score components {rid}",sum(strict["decision_value_breakdown"].values())==
              strict["decision_news_value_score"])
        check(f"strict execution route {rid}",strict["selection_route"]=="execution_anchor_route" and
              strict["execution_credibility_gate"]["anchor_type"]==strict["execution_anchor_type"])
        check(f"strict case id {rid}",strict["economic_event_cluster_id"] in
              {"US_GEORGIA_POWER_ROBINS_128MW_COD_BY_20260915",
               "CN_EVE_POWER_FLUENCE_206GWH_FRAMEWORK_20260918",
               "US_JP_FACTORIAL_MITSUI_SULFIDE_JDA_20260917",
               "JP_PANASONIC_ENERGY_KADOMA_RND_HUB_OPEN_20260916"})
    check("Georgia same article sibling events still separate",
          {x["full_id"] for x in next(x for x in new["strict_passed_spec"]
                                     if x["story_id"]==ids[86])["mixed_source_sibling_lineage"]}
          =={None,"2026-09-10_US_01","2026-09-16_US_02"})

    check("5 new support-only entries",len(new["reject_or_support_only_pool"])==33 and
          new["reject_or_support_only_pool"][:28]==old["reject_or_support_only_pool"])
    check("new support IDs only",{r["story_id"] for r in new["reject_or_support_only_pool"][28:]}==new_support_ids)
    for item in new["reject_or_support_only_pool"][28:]:
        index=item["source_row_index"]
        check(f"support disposition source {index}",item["whether_support_source_only"] is True and
              item["canonical_card_write_allowed"] is False)
        check(f"support original identity {index}",item["primary_url"]==pre[index]["primary_url"])
        check(f"support same event rep {index}",item["formal_0_1P_support_only_20261101"]["representative_source_id"]
              in new_strict_ids)
    for index in (133,158):
        check(f"special overstated/mixed title caveat {index}",bool(post[index]["source_specific_editorial_correction"]))

    check("existing Full reinforcement append",len(new["existing_reinforcement"])==30 and
          new["existing_reinforcement"][:29]==old["existing_reinforcement"] and
          new["existing_reinforcement"][-1]["story_id"]==reinforce_id)
    reinforced=new["existing_reinforcement"][-1]
    check("reinforcement not extra FlexGen card",reinforced["baseline_match"]=="2026-09-16_US_02"
          and reinforced["canonical_card_write_allowed"] is False)
    check("Eos and FlexGen actually in Full",len(full["cards"])==1676 and
          {"2026-09-10_US_01","2026-09-16_US_02"}.issubset({r["id"] for r in full["cards"]}))

    check("all previous reviews/promotion entries preserved",new["promotion_reassessment_ledger"][:76]
          ==old["promotion_reassessment_ledger"] and len(new["promotion_reassessment_ledger"])==86)
    check("promotion new set exact 10",{v["candidate_id"] for v in new["promotion_reassessment_ledger"][76:]}
          =={ids[idx] for idx in ALL_ROWS})
    before_reviews={r["story_id"]:r for r in old["review_pool_resolution_ledger"]}
    after_reviews={r["story_id"]:r for r in new["review_pool_resolution_ledger"]}
    check("four reps + existing reinforcement leave review ledger",set(before_reviews)-set(after_reviews)
          ==new_strict_ids|{reinforce_id})
    check("review ledger now1286",len(after_reviews)==1286)
    for sid,entry in after_reviews.items():
        if sid not in new_support_ids:
            check(f"old review unchanged {sid}",entry==before_reviews[sid])
        else:
            check(f"support 0.1P review marked {sid}",entry["current_disposition"]=="reject_or_support_only_pool")

    expect={"strict_passed_spec":14,"candidate_review_pool":598,"watchlist_context_pool":655,
            "reject_or_support_only_pool":33,"existing_reinforcement":30}
    check("all pool counts exactly sum1330",all(len(new[k])==v for k,v in expect.items()) and
          sum(expect.values())==1330)
    emitted=[r["story_id"] for pool in OUTPUT_POOLS for r in new[pool]]
    check("1330 unique emitted Source IDs",len(set(emitted))==len(emitted)==1330 and
          set(emitted)=={x["story_id"] for x in new["decision_ledger"]})
    check("all previous attachments preserved",all(old[k]==new[k] for k in old
          if k.startswith("pre_native_") and k!="pre_native_0_1P_attachment_manifest_20261101"))
    previous_manifest=old["pre_native_0_1P_attachment_manifest_20261101"]
    manifest=new["pre_native_0_1P_attachment_manifest_20261101"]
    check("70 prenative original hash immutable",manifest["source_input_sha256"]==previous_manifest["source_input_sha256"])
    check("41 formal new since original 45",manifest["new_formal_decisions"]==41 and
          manifest["new_strict_promotions"]==6 and manifest["remaining_formal_source_count"]==1244 and
          len(manifest["formal_review_completed_source_ids"])==41)
    check("original 31 formal IDs preserved",manifest["formal_review_completed_source_ids"][:31]
          ==previous_manifest["formal_review_completed_source_ids"])
    check("prior KR2 checkpoint unchanged",new["formal_0_1P_two_korean_events_20261101"]
          ==old["formal_0_1P_two_korean_events_20261101"])
    check("only expected top-level keys changed",{k for k in set(old)|set(new) if old.get(k)!=new.get(k)}
          <=EXACT_TOP_CHANGES)
    summary=new["summary"]
    check("summary counts complete",summary["processed_priority_source_observations"]==86
          and summary["unprocessed_editorial_observations"]==1244 and
          summary["needs_review_count"]==1286 and
          summary["existing_reinforcement_count"]==30 and
          all(summary["pool_counts"][k]==v for k,v in expect.items()))
    audit=new["formal_0_1P_four_usjp_economic_events_20261101"]
    check("event-level no-force-card",audit["independent_new_event_families"]==4 and
          audit["new_strict_passes"]==4 and audit["new_same_event_support_sources"]==5 and
          audit["new_existing_full_reinforcements"]==1 and audit["new_cards_created"]==0)
    check("Factorial interview split hold explicitly retained",{v["source_row_index"] for v in audit["mixed_source_split_holds"]}==HOLD_ROWS)
    check("hold and safety boundary",audit["global_editorial_stage_a_status"].startswith("HOLD") and
          audit["stage_b_executed"] is False and audit["canonical_main_full_related_mutations"]==0)
    check("no receipt loss",len(audit["source_decisions"])==10 and
          receipt["new_formalized"]==10 and receipt["formal_pending"]==1244)

    native_checks={}
    for name,argv in (
        ("artifact_contract",["validation_scripts/stage_artifact_contract_check.py","A",a.artifact.name]),
        ("lineage_contract",["validation_scripts/stage_lineage_contract_check.py","stage_a",a.artifact.name]),
    ):
        r=subprocess.run([sys.executable,*argv],cwd=a.native_root,text=True,capture_output=True,check=False)
        native_checks[name]={"return_code":r.returncode,"stdout":r.stdout.strip(),"stderr":r.stderr.strip()}
        check("native "+name,r.returncode==0 and "PASS" in r.stdout)

    output={
        "result":"PASS_1330_NOLOSS_10_SOURCE_DECISIONS_BOTH_NATIVE_CONTRACTS",
        "scope":"Independent delta arithmetic and native schema checks; not Stage B accepted-fact-safe",
        "base_sha256":sha(a.base), "output_sha256":sha(a.artifact),
        "original_source_universe":1330,"exactly_changed_rows":sorted(changed),
        "strict_source_rows":sorted(REP_ROWS),"support_source_rows":sorted(SUPPORT_ROWS),
        "full_reinforcement_rows":sorted(REINFORCE_ROWS),
        "unmodified_mixed_article_hold_rows":sorted(HOLD_ROWS),
        "case_source_rows":ROW_GROUPS,
        "counts":{**expect,"formal_completed":86,"formal_pending":1244,
                  "review_resolution_count":1286},
        "native_checks":native_checks,
        "stage_a_global_status":"HOLD","stage_b_executed":False,
        "main_full_related_production_mutated":False,
    }
    with a.output.open("w",encoding="utf-8",newline="\n") as f:
        json.dump(output,f,ensure_ascii=False,indent=2)
        f.write("\n")
    print(json.dumps({"result":output["result"],"output_sha256":output["output_sha256"],
                      "counts":output["counts"]},ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
