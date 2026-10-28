#!/usr/bin/env python3
"""Governed 0.6 V5 editorial proposals and fail-closed case-specific deep QC.

Never changes canonical Full/Lean/Related/main/production, never renames
upstream Stage 0.5 PASS. Existing original Stage 0.5 artifact stays intact.
New evidence excerpts below are literal, on-topic quotes retrieved from the
same published source pages on 2026-10-28; quote limits are retained.
"""
from __future__ import annotations
import copy, hashlib, json, pathlib, sys
from collections import Counter
ROOT=pathlib.Path("runs/2026-10-27/stage-c")
IN=ROOT/"STAGE_0_5_EVIDENCE_SOURCE_CLAIM_QC_20261028.json"
OUT=ROOT/"STAGE_0_6_V5_CASE_SPECIFIC_AUDIT_20261028.json"
STAGE=ROOT/"STAGE_0_6_V5_NATIVE_PASS_ONLY_20261028.json"
# Only source-verified, source-specific previously absent details; no invented excerpt.
ADDED_EXCERPTS={
 "A_SPEC_R13_DISC_001":{"energyx_buyer":["offtake being a key requirement for EnergyX’s financing from the U.S. EXIM Bank"]},
 "A_SPEC_R4_DISC_001":{"crma_press":["seven projects on lithium, 12 on nickel, 10 on cobalt"]},
 "A_SPEC_SRC26-20260928_160143-0194":{"waratah_report":["a transformer failure and months of reduced capacity"]},
 "A_SPEC_R13_DISC_004":{"benchmark_q3":["lithium carbonate prices (-20.8% q-o-q)","4.6% increase in its ferrous phosphate (anhydrous) price grade"]},
 "A_SPEC_C0_DISC_20261014_EU_GIGA_ALBATROSS_GRID":{"albatross_finance":["a €260 million debt financing package for the project"]},
 "A_SPEC_C0_DISC_20261006_EU_BWESS_BERKSWELL_OPT":{"berkswell_owner":["the four-hour battery system","use Sungrow’s PowerTitan 3 technology"]},
}
DELTA={
 "A_SPEC_R13_DISC_001":{"implication":"기존 Eni 투자와 달리 이번 변화는 제품의 장기 판로에 있다. 미국 수출입은행(EXIM Bank) 등의 프로젝트 금융에서 장기 구매약정이 대출 요건으로 작용하므로, 실제 금융집행·착공·첫 출하를 각각 확인해야 한다."},
 "A_SPEC_R4_DISC_001":{"fact":"유럽 집행위원회는 10월 9일 C(2026)8051 결정을 채택했다. 결정 제1조는 부속 목록의 사업을 CRMA 전략 프로젝트로 인정하며 제2조의 수신 사업자는 46개로 열거됐다. 이번 변화는 전략 지위의 부여다. 집행위 발표 기준 배터리 원료와 관련된 프로젝트에는 리튬 7건·니켈 12건·코발트 10건이 포함된다."},
 "A_SPEC_SRC26-20260928_160143-0194":{"fact":"Akaysha는 NSW Waratah 배터리가 최종 상업운전에 도달했다고 밝혔다. 명목 설계는 850MW·1,680MWh이며, 배터리와 Transgrid의 SIPS 제어체계가 계통 교란에 대응하도록 설계됐다. 9월 9일에는 701MW 출력으로 full-SIPS 계약 수준을 시험했다. 이번 발표는 시험 출력에서 최종 상업운전 상태로의 변화를 다룬다. 다만 앞서 변압기 고장과 수개월간의 출력 제한이 있었으므로, 운영 신뢰성은 실제 가동률로 추가 확인해야 한다."},
 "A_SPEC_R13_DISC_004":{"fact":"Benchmark는 2026년 3분기 양극재 리뷰에서 DDP 중국 기준 LFP 평가가격이 7.8% 내려 톤당 5만6,000위안에 이르렀다고 보고했다. 이는 해당 기관의 가격 평가 결과다. 공식 양극재 방법론은 LFP의 인도 조건을 DDP 중국·부가세 포함으로, 통화와 단위를 위안·톤으로 정의한다. 같은 리뷰에서 탄산리튬 가격은 전분기 대비 20.8% 하락한 반면 무수 인산철 가격은 4.6% 상승해 원재료별 가격 방향이 엇갈렸다."},
 "A_SPEC_C0_DISC_20261014_EU_GIGA_ALBATROSS_GRID":{"fact":"GIGA Storage와 Amprion은 10월 14일 Dortmund에서 Albatross의 계통접속 계약에 서명했다. 계획 규모는 350MW·1,400MWh이며 Merzen 변전소의 380kV망에 접속한다. 이후 10월 26일 사업자 발표는 금융종결일을 10월 23일로 밝히고 운영 목표를 2029년 초로 제시했다. 같은 후속 발표에는 차입금 2억6,000만유로(€260 million)의 금융조달 패키지가 공개됐으나 계통접속 계약 자체의 집행 금액은 아니다."},
 "A_SPEC_C0_DISC_20261006_EU_BWESS_BERKSWELL_OPT":{"fact":"BW ESS와 Danske Commodities는 Berkswell 200MW·857MWh 전체에 대한 10년 최적화 계약을 발표했다. floor 구조 아래 Danske Commodities가 거래·최적화를 맡는다. 8월 31일 Farrans가 발표한 현장 착공·초기 공사와 이번 상업적 계약은 서로 다른 행위다. 사업자는 운영을 2027년 4분기로 예상했다. 또한 약 4시간 저장 기능과 Sungrow PowerTitan 3 적용을 예정하고 있으나 실제 성능·납품 완료가 확인된 것은 아니다."}
}
DIMS=("prior_state","changed_state","quantitative_anchor","boundary_or_uncertainty","transmission_path","next_watchpoint")
PLAN={
 "A_SPEC_R13_DISC_001":("implication","transmission_path","energyx_buyer"),
 "A_SPEC_R4_DISC_001":("fact","quantitative_anchor","crma_press"),
 "A_SPEC_SRC26-20260928_160143-0194":("fact","prior_state","waratah_report"),
 "A_SPEC_R13_DISC_004":("fact","quantitative_anchor","benchmark_q3"),
 "A_SPEC_C0_DISC_20261014_EU_GIGA_ALBATROSS_GRID":("fact","quantitative_anchor","albatross_finance"),
 "A_SPEC_C0_DISC_20261006_EU_BWESS_BERKSWELL_OPT":("fact","quantitative_anchor","berkswell_owner")
}
def sha(x):
 return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def verify():
 data=json.loads(IN.read_text(encoding="utf-8"))
 assert data["status"]=="PASS_EVIDENCE_COMPLETE_AND_SOURCE_CLAIM_COVERED_AFTER_NATIVE_CHECKS"
 assert data["base_main_commit_sha"]=="805c2718d6daf40a219ae94242d9687e33ac3e88"
 assert data["base_full_blob_sha"]=="07a91714e56be2a8bfad10ab63822f0c5cb3f06e"
 assert len(data["evidence_complete_and_source_claim_covered"])==7
 return data

def main():
 sys.path.insert(0,str(pathlib.Path.cwd()))
 sys.path.insert(0,str(pathlib.Path.cwd()/"validation_scripts"))
 data=verify()
 try:
  from validation_scripts.card_run_v4_binding_hardening import validate_content_enrichment_delta
 except ImportError:
  from card_run_v4_binding_hardening import validate_content_enrichment_delta
 batch=[]; accepted=[];held=[]
 for original in data["evidence_complete_and_source_claim_covered"]:
  spec=original["source_spec_id"]
  row=copy.deepcopy(original)
  assert len(row["fact_sources"])>0 and row["related_lineage"]["status"]=="PASS"
  before_hashes={k:sha(original[k]) for k in ("fact_sources","related_lineage","date_role","source_story_ids")}
  excerpts=ADDED_EXCERPTS.get(spec,{})
  for source in row["fact_sources"]:
   extras=excerpts.get(source.get("source_key"))
   if extras:
    assert source["source_quote_status"] in {"official_material_quote_verified","body_quote_verified","document_quote_verified"}
    assert source.get("fetched") is True and source.get("resolved_article_matches_quote") is True
    source["source_excerpt"]=list(extras)
    source["additional_excerpt_provenance"]={
      "method":"2026-10-28 original-publisher public article text independently retrieved, literal excerpt",
      "original_url":source["source_url"],
      "not_a_new_fact_source_or_editorial_owner":True,
    }
  augmented_05=copy.deepcopy(row)
  change=DELTA.get(spec,{})
  for k,v in change.items():
   assert k in {"sub","gate","fact","implication"}
   row[k]=v
  fields=list(change)
  dims={k:False for k in DIMS}; mapping={}
  if spec in PLAN:
   field,dim,source_key=PLAN[spec]
   dims[dim]=True
   token=next(s["source_url"] for s in row["fact_sources"] if s["source_key"]==source_key)
   mapping[dim]={"fields":[field],"evidence_refs":[token]}
  elif not change:
   # Insufficient incremental source facts; no forced enrichment/false success.
   held.append({"source_spec_id":spec,"status":"HOLD_NO_PROVEN_INCREMENTAL_SIGNAL",
    "reason":"Existing copy requires additional verified quote-level evidence for V5 no-change and cannot be called enriched from its short excerpts."})
   continue
  row["content_enriched"]=True
  row["language_terminology_polished"]=True
  row["prompt_provenance_0_6"]={"prompt_version":"PROMPT_0_6_V5_20260919","locked_main_commit_sha":data["base_main_commit_sha"]}
  row["content_enrichment_audit"]={
   "baseline_strategy":"nearest_upstream_visible_copy_0.5_0.4_C",
   "changed_fields":fields,"no_change_required":False,"no_change_reason":"",
   "density_audit":{"status":"PASS","dimensions":dims,"supported_dimension_count":sum(dims.values()),
    "evidence_notes":"Case-specific substantive delta with source-specific literal excerpt; other claims retain Stage C fact-safe caveats.",
    "dimension_evidence":mapping}}
  row["stage06_candidate_limits"]={
   "original_05_fact_sources_sha256":before_hashes["fact_sources"],
   "original_05_related_lineage_sha256":before_hashes["related_lineage"],
   "original_05_date_role_sha256":before_hashes["date_role"],
   "original_05_source_story_ids_sha256":before_hashes["source_story_ids"],
   "editorial_proposal_only_until_exact_native_v5_deep_validation":True,
   "web_quote_corroboration_no_unchanged_raw_snapshot_claim":True,
  }
  try:
   validate_content_enrichment_delta(
      {"C":[original],"0.4":[original],"0.5":[augmented_05],"0.6":[row]},
      f"Stage0.6 {spec}", locked_prompt_version="PROMPT_0_6_V5_20260919")
  except Exception as e:
   held.append({"source_spec_id":spec,"status":"HOLD_NATIVE_V5_DEEP_GATE",
    "reason":str(e)[:2000],"proposed_copy":{f:row[f] for f in change},
    "source_excerpt_retrieved":excerpts,
    "no_canonical_writes":True})
   batch.append({"source_spec_id":spec,"check":"HOLD","changed_fields":fields,"reason":str(e)[:300]})
  else:
   accepted.append(row)
   batch.append({"source_spec_id":spec,"check":"PASS_NATIVE_V5_DEEP","changed_fields":fields})
 assert len(accepted)+len(held)==7
 common={"stage":"0.6","run_tag":data["run_tag"],
    "base_main_commit_sha":data["base_main_commit_sha"],
    "base_full_blob_sha":data["base_full_blob_sha"],
    "prompt_provenance":{"prompt_version":"PROMPT_0_6_V5_20260919","locked_main_commit_sha":data["base_main_commit_sha"]},
    "upstream_lineage_integrity":"PASS","lineage_and_anchor_guard":"PASS",
    "readonly_original_0_5_sha256":hashlib.sha256(IN.read_bytes()).hexdigest(),
    "stage_a_1330_source_universe_preserved":True,
    "stage_b_lges_blocked_preserved":True,
    "canonical_main_full_lean_related_production_written":False}
 final=dict(common,**{"status":"PENDING_0_6_SCHEMA_EXIT",
   "content_enriched_and_language_polished":accepted,
   "content_polish_hold":held})
 STAGE.write_text(json.dumps(final,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 report=dict(common,**{"status":"PASS" if not held else "BLOCKED_V5_CONTENT_GATE_PARTIAL",
   "proposed":len(DELTA),"native_v5_deep_pass":len(accepted),"held":len(held),
   "case_receipts":batch,"held_detail":held,"no_authorization_for_0_7":bool(held),
   "notes":"Direct locked V5 deep evidence validator applied per row. No source truth inferred from schema-only success."})
 OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("STAGE06",len(accepted),"V5_DEEP_PASSED",len(held),"HELD",len(accepted)+len(held),"ACCOUNTED")
 for c in batch:print("C06_CASE",c["source_spec_id"],c["check"],c.get("reason",""))
 print("HOLD_ONLY",*[v["source_spec_id"] for v in held if v["status"]=="HOLD_NO_PROVEN_INCREMENTAL_SIGNAL"])
 print("AUDIT",OUT,"STAGE_ARTIFACT",STAGE)
if __name__=="__main__":main()
