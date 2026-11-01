#!/usr/bin/env python3
"""Independent read-only CP19 integrity and native-check verifier.

Does not import or execute the CP19 builder.  Original raw Source ID rows,
all previous formal decisions and all five partition sets are checked.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

BASE_SHA="4b9039f9f045e92ae5485ddab4ab0ab40bb19da8fdf59bb02c6c0b5adba44b66"
FULL_SHA="d22f0d4e39e035b9537b3e9abdf48abe6b7eb80f7e477e87aff1284f9e27e0d9"
EVENT_REPS={1277,1244,1255,1267,1280,1294,1324,700,1200,425}
SUPPORT={226,302,349,709,851,852}
WATCH={423,1299,1236}
REJECT={855,1133}
TARGET=EVENT_REPS|SUPPORT|WATCH|REJECT
POOLS=("strict_passed_spec","candidate_review_pool","watchlist_context_pool",
       "reject_or_support_only_pool","existing_reinforcement")
EXPECTED_COUNTS={"strict_passed_spec":30,"candidate_review_pool":563,
                 "watchlist_context_pool":660,"reject_or_support_only_pool":47,
                 "existing_reinforcement":30,"promotion_reassessment_ledger":126,
                 "review_pool_resolution_ledger":1270}

def digest(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda:f.read(1024*1024),b""):
            h.update(part)
    return h.hexdigest()

def verify(a):
    assert digest(a.base)==BASE_SHA,"CP18 immutable baseline sha mismatch"
    assert digest(a.full)==FULL_SHA,"locked Full baseline sha mismatch"
    base=json.loads(a.base.read_text(encoding="utf-8"))
    new=json.loads(a.artifact.read_text(encoding="utf-8"))
    receipt=json.loads(a.receipt.read_text(encoding="utf-8"))
    base_rows=base["decision_ledger"]
    new_rows=new["decision_ledger"]
    assert len(base_rows)==len(new_rows)==1330
    assert len({r["story_id"] for r in base_rows})==1330
    immutable=("source_row_index","story_id","candidate_id","headline_raw","primary_url","origin")
    changed=set()
    for i,(b,n) in enumerate(zip(base_rows,new_rows)):
        assert all(b.get(k)==n.get(k) for k in immutable),(i,"source changed")
        assert b["source_row_index"]==n["source_row_index"],(i,"source order")
        if b!=n:
            changed.add(i)
            assert n["cp19_source_identity_preserved"]["primary_url"]==b["primary_url"]
            assert n["cp19_source_identity_preserved"]["headline_raw"]==b["headline_raw"]
            assert n["cp19_source_identity_preserved"]["source_row_index"]==i
            assert n["formal_0_1P_cp19_source_to_economic_act_edges_20261101"]
    assert changed==TARGET,("unexpected changed source rows",sorted(changed^TARGET))
    assert all(len(new[k])==v for k,v in EXPECTED_COUNTS.items())
    partitions={}
    for pool in POOLS:
        for r in new[pool]:
            sid=r["story_id"]
            assert sid not in partitions,("duplicate Source ID across Stage A pools",sid,pool)
            partitions[sid]=pool
    assert set(partitions)=={r["story_id"] for r in base_rows}
    for idx in EVENT_REPS:
        r=new_rows[idx]
        assert partitions[r["story_id"]]=="strict_passed_spec"
        assert r["stage_b_authorized"] is False
        assert r["accepted_facts_approved"] is False
        assert r["canonical_card_write_allowed"] is False
    for group,pool in ((SUPPORT,"reject_or_support_only_pool"),
                       (WATCH,"watchlist_context_pool"),
                       (REJECT,"reject_or_support_only_pool")):
        for idx in group:
            assert partitions[new_rows[idx]["story_id"]]==pool,(idx,pool)
            assert new_rows[idx]["stage_b_authorized"] is False
            assert new_rows[idx]["accepted_facts_approved"] is False
    for idx in REJECT:
        assert new_rows[idx]["review_pool_resolution_status"]=="closed_not_cardable"
        assert new_rows[idx]["review_pool_subtype"]=="out_of_scope_verified_original"
        assert new_rows[idx]["canonical_card_write_allowed"] is False
    assert new_rows[1236]["protected_support_metric"]["usd_millions"]==720
    assert new_rows[1236]["protected_support_metric"]["yoy_pct"]==14.0
    assert new_rows[349]["headline_original_overstates_stage"]
    assert base["promotion_reassessment_ledger"]==new["promotion_reassessment_ledger"][:105]
    assert base["strict_passed_spec"]==new["strict_passed_spec"][:20]
    new_strict=new["strict_passed_spec"][20:]
    assert {r["source_story_ids"][0] for r in new_strict}=={new_rows[i]["story_id"] for i in EVENT_REPS}
    assert len({r["economic_event_cluster_id"] for r in new_strict})==10
    assert all(r["stage_b_authorized"] is False and r["canonical_card_write_allowed"] is False
               and r["accepted_facts_approved"] is False for r in new_strict)
    vault=[r for r in new_strict if "VAULTCO" in r["economic_event_cluster_id"]]
    assert len(vault)==1
    subacts=vault[0]["formal_0_1P_cp19_strict_event_20261101"]["subacts"]
    assert any("GLENCORE_USD500M" in v for v in subacts)
    assert any("MERCURIA_USD500M" in v for v in subacts)
    assert all(not ("STOCKPILE_DELIVERED" in v) for v in subacts)
    for r in new_strict:
        assert r["date_role"]["event_date"]==r["representative_date"]
        assert r["stage_b_evidence_package_required"] is True
        assert r["source_metadata_only"] is True
        assert r["bounded_research_source_candidates"]
        assert r["evidence_needed_for_stage_b"]
        assert r["next_confirmation_points"]
    assert len(new["review_pool_resolution_ledger"])==1270
    assert len({r["story_id"] for r in new["review_pool_resolution_ledger"]})==1270
    assert new["summary"]["strict_passed_spec_count"]==30
    assert new["summary"]["unprocessed_editorial_observations"]==1204
    assert new["summary"]["processed_priority_source_observations"]==126
    batch=new["formal_0_1P_cp19_owner_document_batch_20261101"]
    assert batch["new_formal_source_ids"]==21 and batch["new_strict_economic_event_families"]==10
    assert batch["same_event_support_source_ids"]==6 and batch["watch_or_protected_metric_source_ids"]==3
    assert batch["owner_verified_off_industry_reject_source_ids"]==2
    assert batch["source_ids_preserved_total"]==1330
    assert batch["global_stage_a_status"].startswith("HOLD_")
    assert batch["canonical_main_full_related_mutations"]==0
    assert batch["stage_b_executed"] is False and batch["new_published_cards"]==0
    source_edges=batch["source_to_economic_act_edges"]
    assert len(source_edges)==21
    assert {r["row"] for r in source_edges}==TARGET
    assert all(r["first_party_owner_urls"] for r in source_edges)
    att=new["pre_native_0_1P_attachment_manifest_20261101"]
    assert att["formal_review_completed_after_attachment_count"]==81
    assert att["remaining_formal_source_count"]==1204
    assert len(set(att["formal_review_completed_source_ids"]))==81
    assert receipt["output_sha256"]==digest(a.artifact)
    assert receipt["base_sha256"]==BASE_SHA
    assert receipt["locked_full_sha256"]==FULL_SHA
    native={}
    native_commands={
        "artifact_contract":["python","validation_scripts/stage_artifact_contract_check.py","A",str(a.artifact.resolve())],
        "lineage_contract":["python","validation_scripts/stage_lineage_contract_check.py","stage_a",str(a.artifact.resolve())]
    }
    for name,command in native_commands.items():
        completed=subprocess.run(command,cwd=a.native_dir,capture_output=True,text=True,timeout=120,check=False)
        assert completed.returncode==0,(name,completed.stdout,completed.stderr)
        assert ("PASS" in completed.stdout),(name,"PASS status missing",completed.stdout)
        native[name]={"pass":True,"return_code":0,"stdout":completed.stdout.strip()}
    return {
        "qc_status":"INDEPENDENT_QC_PASS","original_source_ids_preserved":1330,
        "source_identity_fields_unchanged":list(immutable),
        "new_formal_source_id_decisions":21,
        "new_strict_events":10,"same_event_support":6,"watch":3,"out_of_scope_reject":2,
        "formal_cumulative":126,"pending_formal":1204,"strict_cumulative":30,
        "all_previous_formal_decisions_unchanged":105,
        "all_previous_strict_selectors_unchanged":20,
        "partition_counts":{p:len(new[p]) for p in POOLS},
        "source_to_event_edges_preserved":21,
        "owner_original_available":True,
        "vaultco_two_partner_commitments_independently_labeled":True,
        "protected_metric_kept":True,"native_validators":native,
        "sha256":{"cp18":BASE_SHA,"full_locked_1676":FULL_SHA,"cp19":digest(a.artifact)},
        "main_full_related_production_mutation":False,
        "stage_b_executed":False,
        "global_stage_a":"HOLD",
    }

def main():
    p=argparse.ArgumentParser()
    for name in ("base","full","artifact","receipt","native-dir","out"):
        p.add_argument("--"+name,required=True,type=Path)
    a=p.parse_args()
    result=verify(a)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in ("qc_status","original_source_ids_preserved",
                    "new_formal_source_id_decisions","pending_formal","strict_cumulative",
                    "global_stage_a")},ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
