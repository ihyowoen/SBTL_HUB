#!/usr/bin/env python3
"""0.7 V4 scoped, fail-closed preflight. Never mutates canonical Full."""
from __future__ import annotations
import json,subprocess,sys,hashlib
from pathlib import Path
BASE=Path("runs/2026-10-28/stage06-bounded")
OUT=Path("runs/2026-10-28/stage07-preflight")
MAIN="805c2718d6daf40a219ae94242d9687e33ac3e88"
FULL="07a91714e56be2a8bfad10ab63822f0c5cb3f06e"
FILES={
"B":("STAGE_B_0_2R_BOUNDED_20261028_V2.json","draft_cards"),
"C":("STAGE_C_0_3R_BOUNDED_20261028_V2.json","accepted_fact_safe"),
"0.4":("STAGE_0_4_BOUNDED_20261028_V2.json","addable_merge_safe"),
"0.5":("STAGE_0_5_BOUNDED_NATIVE_CANDIDATE_20261028_V2.json","evidence_complete_and_source_claim_covered"),
"0.6":("STAGE_0_6_BOUNDED_NATIVE_CANDIDATE_20261028_V2.json","content_enriched_and_language_polished"),
}
def load(p):return json.loads(Path(p).read_text(encoding="utf-8"))
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 env={}
 for st,(filename,bucket) in FILES.items():
  obj=load(BASE/filename)
  assert obj["base_main_commit_sha"]==MAIN and obj["base_full_blob_sha"]==FULL
  rows=obj[bucket]
  assert len(rows)==7
  env[st]={r["source_spec_id"]:r for r in rows}
 specs=list(env["0.6"])
 assert len(set(specs))==7 and all(set(by)==set(specs) for by in env.values())
 ids_path=OUT/"CURRENT_RUN_IDS_20261028.json"
 write(ids_path,specs)
 base=load("data/cards.full.json")
 assert isinstance(base,dict) and len(base.get("cards",[]))==1676
 baseline=base["cards"]
 existing={r.get("id") for r in baseline}
 assert None not in existing and len(existing)==1676
 staged=list(env["0.6"].values())
 assert not set(r.get("id") for r in staged)&existing
 merged=OUT/"MERGED_BASELINE_1683_READONLY_PREFLIGHT.json"
 write(merged,{"cards":baseline+staged})
 checks=[
  ("evidence_qc",["python","validation_scripts/evidence_qc_v8_check.py",str(merged),"--new-id-file",str(ids_path)]),
  ("related_lifecycle",["python","validation_scripts/related_lifecycle_check.py",str(merged),"--require-contract","--allow-provisional-related","--new-id-file",str(ids_path)]),
  ("date_role",["python","validation_scripts/date_role_freshness_check.py",str(merged),"--require-date-role","--new-id-file",str(ids_path)]),
 ]
 results={}
 for name,cmd in checks:
  p=subprocess.run(cmd,text=True,capture_output=True)
  try:
   details=json.loads(p.stdout)
  except ValueError:
   details=None
  results[name]={"status":"PASS" if p.returncode==0 else "BLOCKED",
   "exit_code":p.returncode,"structured_result":details,
   "error_excerpt":(p.stderr or p.stdout)[-3500:] if p.returncode else ""}
  print("STAGE07_RAW",name,results[name]["status"])
 needs=[
  {"source_spec_id":sid,"related_relation":env["0.6"][sid]["related_lineage"].get("relation_type"),
   "date_role_keys_missing":sorted({"publication_dates","earliest_same_event_date_checked","event_date_source_url","event_date_source_quote"}-set(env["0.6"][sid]["date_role"])),
   "related_contract_keys_missing":sorted({"earliest_same_event_date_checked"}-set(env["0.6"][sid]["related_lineage"]))}
  for sid in specs
 ]
 report={"stage":"0.7","status":"HOLD_UPSTREAM_METADATA_REMEDIATION",
  "created_from":"GitHub Actions pinned Full and Stage 0.6 seven-card PASS",
  "base_main_commit_sha":MAIN,"base_full_blob_sha":FULL,
  "full_existing_cards":1676,"staged_current_run_cards":7,
  "current_run_ids":specs,"current_run_exact_scope_count":7,
  "source_universe_1330_preserved":True,
  "blocked_LGES_Q3_preserved":True,
  "original_stage06_unchanged":True,
  "phase07_authorized":False,"phase07C_authorized":False,
  "scope_test_results":results,"upstream_defect_queue":needs,
  "next_required_action":"Controlled evidence-backed stage B date and C Related repair; rerun all scoped 0.7 native checks on exact 1683 merged full."
 }
 write(OUT/"STAGE_0_7_STRICT_PREFLIGHT_REPORT_20261028.json",report)
 print("STAGE07_PREFLIGHT_HOLD",sum(r["status"]!="PASS" for r in results.values()),"blocked validator families")
 # Failure is captured and classified. Never claim publish_ready from this audit.
if __name__=="__main__":main()
