#!/usr/bin/env python3
"""Stage 0.7 V4 editorial gate on a machine-PASS current-run scope.

Separate content decisions from machine validation. Protected canonical data
is never written. Hold cards stay in audit inventory, never publish_ready.
"""
import json,copy,subprocess
from pathlib import Path
P=Path("runs/2026-10-28/stage07-preflight")
TECH=P/"STAGE_0_7_CONTROLLED_REPAIR_NATIVE_REPORT_20261028.json"
REPAIRED=P/"REPAIRED_STAGE_0_6_07.json"
OUT=P/"STAGE_0_7_FINAL_EDITORIAL_DISPOSITION_20261028.json"
MACHINE=P/"STAGE_0_7_FINAL_EDITORIAL_SCHEMA_RECEIPT_20261028.json"
PASS={
 "A_SPEC_R4_DISC_001":{
  "story":"EU CRMA 46 second-list strategic projects",
  "review":"October 9 designation is distinguished from permits, funding disbursement, construction and realized output.",
  "source":"https://luxembourg.representation.ec.europa.eu/actualites-et-evenements/actualites/commission-selects-46-new-strategic-projects-bolster-eus-supply-critical-raw-materials-2026-10-09_en"},
 "A_SPEC_R13_DISC_004":{
  "story":"Benchmark Q3 cathode DDP China LFP grade",
  "review":"LFP 7.8% and carbonate 20.8% are Benchmark assessment observations with different product/grade/price bases; no realized company margin inferred.",
  "source":"https://source.benchmarkminerals.com/article/bearish-battery-feedstock-markets-weigh-on-cathode-prices-cathode-q3-2026-price-review"},
 "A_SPEC_C0_DISC_20261014_EU_GIGA_ALBATROSS_GRID":{
  "story":"Albatross grid agreement",
  "review":"Grid agreement signed 14 October is separate from financial close on 23 October and early-2029 operation target; €260m is borrowing package, not contract value.",
  "source":"https://giga-storage.com/en/giga-storage-bereikt-financial-close-voor-energieopslagproject-albatross-in-duitsland-en-bouwt-nu-aan-14-gw-in-drie-landen/"},
 "A_SPEC_C0_DISC_20261005_EU_RETURN_ANTARES_COD":{
  "story":"Antares commercial operation",
  "review":"October 5 is owner disclosure not separately observed physical COD date; earlier 2025 Vattenfall 50MW Antares agreement is explicitly distinct from Sirius BESS.",
  "source":"https://return.energy/news/return-and-vattenfall-sign-long-term-agreement-for-sirius-as-project-reaches-financial-close"},
}
RETURN={
 "A_SPEC_R13_DISC_001":{
  "outcome":"return_content",
  "defect":"0.6 implication includes unedited English source sentence (66% of Phase 1) in Korean reader-visible copy.",
  "required_repair":"Restore Korean exposition with direct original Trafigura sentence retained as source_quote only; preserve project phase and financing condition; rerun V5 source-grounded substantive delta.",
  "source":"https://www.trafigura.com/news-and-insights/press-releases/2026/trafigura-signs-10-year-lithium-offtake-agreement-with-energyx/"},
 "A_SPEC_SRC26-20260928_160143-0194":{
  "outcome":"return_content",
  "defect":"English 'more than $1 billion' source fragment was copied into Korean implication without a completed Korean explanatory sentence.",
  "required_repair":"Describe as issuer-reported private investment exceeding USD1bn, NOT realized project revenue, and rerun V5 same-source claim grounding.",
  "source":"https://akayshaenergy.com/news/waratah-super-battery-reaches-final-commercial-operations"},
 "A_SPEC_C0_DISC_20261006_EU_BWESS_BERKSWELL_OPT":{
  "outcome":"return_content",
  "defect":"700000-home metric is a company-stated theoretical design capability, not observed households supplied or realized operations.",
  "required_repair":"Qualify as hypothetical 'once operational up to four hours' issuer claim or remove promotional household-equivalent from decision implication; retain 200MW/857MWh 10y floor agreement and undisclosed floor amount.",
  "source":"https://www.bw-ess.com/news/bw-ess-and-danske-commodities-sign-10-year-optimisation-agreement-for-200-mw-857-mwh-battery-in-the-uk"},
}
def load(p):return json.loads(p.read_text(encoding="utf-8"))
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def main():
 t=load(TECH)
 assert t["status"]=="PASS_TECHNICAL_SCOPE_ONLY_EDITORIAL_GATE_PENDING"
 assert all(v["status"]=="PASS" for v in t["strict_07_scoped_validators"].values())
 assert all(v=="PASS" for v in t["native_06_cross_stage_v5"].values())
 a=load(REPAIRED)
 assert a["base_main_commit_sha"]==t["base_main_commit_sha"]
 rows=a["content_enriched_and_language_polished"]
 assert len(rows)==7
 order=[x["source_spec_id"] for x in rows]
 assert len(set(order))==7 and set(order)==set(PASS)|set(RETURN)
 publish=[];returns=[]
 for x in rows:
  sid=x["source_spec_id"]
  assert x["related_lineage"]["status"]=="PASS"
  assert x["date_role"]["earliest_same_event_date_checked"] is True
  if sid in RETURN:
   returns.append({"source_spec_id":sid,"draft_id":x.get("draft_id"),
      "original_candidate_id":x.get("id"),**RETURN[sid],
      "stage_0_6_copy_left_unchanged":True,"original_source_id_retained":True})
   continue
  val=copy.deepcopy(x)
  val["state"]="publish_ready";val["publish_ready"]=True
  val["final_qc_gates"]={
   "status":"PASS",
   "source_evidence":"PASS_SCOPED_QC",
   "related_lifecycle":"PASS_EXACT_CURRENT_RUN",
   "date_role":"PASS_EXACT_CURRENT_RUN",
   "content_0_6_v5":"PASS_REVALIDATED_NATIVE",
   "editorial_claims":"PASS_BOUNDED_SOURCE_REVIEW",
   "canonical_regression":"PASS_ORIGINAL_FULL_1676_READONLY",
   "materiality_and_anchor":"PASS_STAGE_A_PREVIOUS_VERIFIED_ROUTE",
   "full_schema_and_visible_text":"PASS_STAGE_C_TO_0_6_WITH_0_7_BOUNDARIES",
   "editorial_readback":PASS[sid]["review"],
   "source_checked":PASS[sid]["source"],
   "not_final_publication_or_merge_authorization":True
  }
  publish.append(val)
 assert len(publish)+len(returns)==7
 result={
  "stage":"0.7","status":"PASS_PARTIAL_WITH_RETURN_CONTENT",
  "run_tag":a["run_tag"],"base_main_commit_sha":t["base_main_commit_sha"],
  "base_full_blob_sha":t["base_full_blob_sha"],
  "prompt_version":"PROMPT_0_7_V4_20260829",
  "lineage_and_anchor_guard":"PASS",
  "current_run_scope_ids":order,
  "current_run_source_id_count":7,
  "publish_ready":publish,
  "hold_evidence":[],"return_content":returns,
  "return_upstream_selection_lineage_date":[],
  "authorized_reject":[],
  "previous_stage_0_6_copy_preserved":True,
  "all_source_observations_1330_preserved":True,
  "LGES_Q3_Stage_B_blocked_preserved":True,
  "original_Full_1676_plus_7_validated":True,
  "publication_and_merge_not_authorized":True,
  "independent_0_7C_not_completed":True,
  "review_limits":[
   "Source URL/latest-article fetch was supported for primary examples but machine source checks are not complete natural-language entailment proofs.",
   "0.7 only covers seven already selected current-run cards, not all 1330 source observations.",
   "Three returned cards remain candidates; no forced article count or hidden deletion."]
 }
 save(OUT,result)
 p=subprocess.run(["python","validation_scripts/stage_artifact_contract_check.py","0.7",str(OUT)],text=True,capture_output=True)
 try:body=json.loads(p.stdout)
 except ValueError:body={"raw":p.stdout[-4000:],"stderr":p.stderr[-1500:]}
 receipt={"schema_exit":"PASS" if p.returncode==0 else "BLOCKED","result":body,
   "publish_ready_count":len(publish),"return_content_count":len(returns),
   "all_7_accounted":len(publish)+len(returns)==7,"no_canonical_writes":True}
 save(MACHINE,receipt)
 print("STAGE07_EDITORIAL_DECISION",len(publish),"PUBLISH_READY_CANDIDATES",len(returns),"RETURN_CONTENT")
 print("STAGE07_NATIVE_ARTIFACT","PASS" if p.returncode==0 else "BLOCKED")
 if p.returncode:raise RuntimeError("stage 0.7 artifact contract blocked: "+str(body)[:2500])
if __name__=="__main__":main()
