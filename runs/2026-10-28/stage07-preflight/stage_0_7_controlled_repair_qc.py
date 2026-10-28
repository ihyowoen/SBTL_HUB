#!/usr/bin/env python3
"""0.7 V4 controlled upstream date/Related backport and scoped technical QC.

All changes are derived copies stored only in the workflow workspace/artifacts.
No production Full/Lean, Related, main or prior B/C/0.4/0.5/0.6 file changes.
"""
import json,copy,hashlib,re,subprocess
from pathlib import Path
from validation_scripts.card_run_v4_binding_hardening import validate_content_enrichment_delta
ROOT=Path("runs/2026-10-28/stage06-bounded")
OUT=Path("runs/2026-10-28/stage07-preflight")
MAIN="805c2718d6daf40a219ae94242d9687e33ac3e88"
FULL="07a91714e56be2a8bfad10ab63822f0c5cb3f06e"
VERSION="PROMPT_0_6_V5_20260919"
FILES={
 "B":("STAGE_B_0_2R_BOUNDED_20261028_V2.json","draft_cards"),
 "C":("STAGE_C_0_3R_BOUNDED_20261028_V2.json","accepted_fact_safe"),
 "0.4":("STAGE_0_4_BOUNDED_20261028_V2.json","addable_merge_safe"),
 "0.5":("STAGE_0_5_BOUNDED_NATIVE_CANDIDATE_20261028_V2.json","evidence_complete_and_source_claim_covered"),
 "0.6":("STAGE_0_6_BOUNDED_NATIVE_CANDIDATE_20261028_V2.json","content_enriched_and_language_polished"),
}
FOLLOW={
"A_SPEC_R13_DISC_001":(
 "EnergyX Black Giant and Lonestar signed Trafigura 10-year 100000 tonne binding purchase contract after Eni equity investment.",
 "Black Giant lender bankability changed from Eni equity investment to potential EnergyX Trafigura 100000 tonne contracted offtake; actual revenue is not realized."),
"A_SPEC_SRC26-20260928_160143-0194":(
 "Waratah 850MW battery reached final commercial operations September 28 after September 9 701MW SIPS capacity test.",
 "Waratah operating readiness changed from a 701MW SIPS output test to final commercial operation announcement; contracted SIPS revenues remain unverified."),
"A_SPEC_C0_DISC_20261006_EU_BWESS_BERKSWELL_OPT":(
 "Berkswell 200MW 857MWh signed Danske 10-year optimisation floor agreement October 6 after August 31 construction milestone.",
 "Berkswell moved beyond initial construction to contracted revenue floor optimisation covering the asset; the floor value remains undisclosed."),
}
def load(p):return json.loads(Path(p).read_text(encoding="utf-8"))
def write(p,obj):Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def getdates(src,event):
 return sorted(set(x["source_published_date"] for x in src
     if re.fullmatch(r"20\d\d-\d\d-\d\d",str(x.get("source_published_date",""))) and x["source_published_date"]>=event))
def patched(row):
 new=copy.deepcopy(row);sid=row["source_spec_id"]
 assert new["related_evidence_review"]["status"]=="PASS"
 assert "PASS" in new["related_evidence_review"]["earliest_same_event_check_status"]
 dr=new["date_role"];date=dr["event_date"]
 owners=[x for x in new["fact_sources"] if x.get("source_published_date")==date and x.get("source_url") and x.get("source_quote")]
 assert owners,(sid,"missing same-date original evidence")
 owner=next((x for x in owners if x.get("is_primary_source") is True),owners[0])
 dr.update(publication_dates=getdates(new["fact_sources"],date),
           earliest_same_event_date_checked=True,
           event_date_source_url=owner["source_url"],
           event_date_source_quote=owner["source_quote"],
           event_date_evidence_scope="source publication-date metadata anchors earliest public announcement, not hidden private action")
 assert date in dr["publication_dates"]
 if "related_lineage" in new:
  rel=new["related_lineage"];rel["earliest_same_event_date_checked"]=True
  if rel.get("relation_type")=="distinct_follow_up":
   assert sid in FOLLOW
   cls=rel.get("fresh_follow_up_anchor_class")
   assert isinstance(cls,list) and cls==["execution_event_anchor"]
   rel["fresh_follow_up_anchor_class"]=cls[0]
   rel["incremental_fact_vs_predecessor"]=FOLLOW[sid][0]
   rel["changed_judgment_vs_predecessor"]=FOLLOW[sid][1]
   if sid in {"A_SPEC_R13_DISC_001","A_SPEC_C0_DISC_20261006_EU_BWESS_BERKSWELL_OPT"}:
    rel["fresh_follow_up_anchor"]=FOLLOW[sid][0]
 return new,{
  "source_spec_id":sid,"derived_scope":"date_role_and_related_lifecycle_only",
  "evidence_url":owner["source_url"],
  "event_date_source_quote":owner["source_quote"],
  "same_event_review_status":new["related_evidence_review"]["earliest_same_event_check_status"],
  "fact_sources_unchanged":row["fact_sources"]==new["fact_sources"],
  "visible_copy_unchanged":all(row[k]==new[k] for k in ("title","sub","gate","fact","implication")),
  "related_ids_unchanged":row.get("related")==new.get("related"),
  "event_date_unchanged":row["date_role"]["event_date"]==dr["event_date"],
 }
def run(label,cmd):
 p=subprocess.run(cmd,text=True,capture_output=True)
 try:obj=json.loads(p.stdout)
 except ValueError:obj=None
 result={"exit_code":p.returncode,"status":"PASS" if p.returncode==0 else "BLOCKED",
  "structured_result":obj,"error_excerpt":(p.stderr or p.stdout)[-4000:] if p.returncode else ""}
 print("STAGE07_REPAIR",label,result["status"])
 return result
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 parsed={}
 for stage,(filename,bucket) in FILES.items():
  src=load(ROOT/filename)
  assert src["base_main_commit_sha"]==MAIN and src["base_full_blob_sha"]==FULL
  assert len(src[bucket])==7
  parsed[stage]=src
 ids=[r["source_spec_id"] for r in parsed["0.6"]["content_enriched_and_language_polished"]]
 assert len(set(ids))==7
 specs=set(ids)
 receipts=[]
 for stage,(filename,bucket) in FILES.items():
  orig=parsed[stage][bucket]
  assert set(x["source_spec_id"] for x in orig)==specs
  rows=[]
  for r in orig:
   a,w=patched(r);rows.append(a)
   if stage=="0.6":receipts.append(w)
  parsed[stage][bucket]=rows
  parsed[stage]["bounded_07_upstream_metadata_reconciliation"]={
   "source_stage":stage,"status":"REVALIDATION_PENDING",
   "original_file":str(ROOT/filename),
   "original_sha256":hashlib.sha256((ROOT/filename).read_bytes()).hexdigest(),
   "date_role_and_related_lifecycle_only":True}
  write(OUT/("REPAIRED_STAGE_"+stage.replace(".","_")+"_07.json"),parsed[stage])
 by={stage:{r["source_spec_id"]:r for r in parsed[stage][bucket]}
     for stage,(_,bucket) in FILES.items()}
 v5={}
 for sid in ids:
  try:
   validate_content_enrichment_delta({k:[v[sid]] for k,v in by.items()},sid,
    operation_card=by["0.6"][sid],locked_prompt_version=VERSION)
   v5[sid]="PASS"
  except Exception as e:v5[sid]="BLOCKED: "+str(e)[:1000]
 print("STAGE07_REPAIRED_06_V5",sum(v=="PASS" for v in v5.values()),"/7")
 full=load("data/cards.full.json")
 assert isinstance(full,dict) and len(full.get("cards",[]))==1676
 origids=[r["id"] for r in full["cards"]]
 assert len(set(origids))==1676
 add=[by["0.6"][sid] for sid in ids]
 assert len(set(r["id"] for r in add))==7 and not set(r["id"] for r in add)&set(origids)
 merged=OUT/"MERGED_BASELINE_1683_REPAIRED_EPHEMERAL.json"
 write(merged,{"cards":full["cards"]+add})
 idfile=OUT/"CURRENT_RUN_IDS_20261028.json";write(idfile,ids)
 results={
  "evidence":run("evidence",["python","validation_scripts/evidence_qc_v8_check.py",str(merged),"--new-id-file",str(idfile)]),
  "related":run("related",["python","validation_scripts/related_lifecycle_check.py",str(merged),"--require-contract","--allow-provisional-related","--new-id-file",str(idfile)]),
  "date":run("date",["python","validation_scripts/date_role_freshness_check.py",str(merged),"--require-date-role","--new-id-file",str(idfile)]),
 }
 good=all(v=="PASS" for v in v5.values()) and all(v["status"]=="PASS" for v in results.values())
 findings={
  "stage":"0.7","status":"PASS_TECHNICAL_SCOPE_ONLY_EDITORIAL_GATE_PENDING" if good else "HOLD_UPSTREAM_METADATA_REPAIR",
  "base_main_commit_sha":MAIN,"base_full_blob_sha":FULL,
  "input_full_cards":1676,"current_run_cards":7,"total_ephemeral_cards":1683,
  "source_id_order_unchanged":ids==[r["source_spec_id"] for r in add],
  "preserved_original_and_blocked_LGES":True,
  "original_main_Full_Lean_Related_untouched":True,"current_run_ids":ids,
  "repair_receipts":receipts,"native_06_cross_stage_v5":v5,
  "strict_07_scoped_validators":results,
  "editorial_disposition":"not reviewed by this mechanical receipt; no publication decision granted",
  "no_auto_publish_ready":True,"no_0_7C_or_0_8_authorization":True}
 write(OUT/"STAGE_0_7_CONTROLLED_REPAIR_NATIVE_REPORT_20261028.json",findings)
 print("STAGE07_CONTROLLED_TECHNICAL",findings["status"])
if __name__=="__main__":main()
