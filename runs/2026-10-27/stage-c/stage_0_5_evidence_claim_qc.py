#!/usr/bin/env python3
"""Canonical 0.5 claim/source handoff. No new article facts, sources or protected writes.

Sentence/source mapping is a bounded editorial review of prior Stage B body-
checked and Stage C fact-safe evidence, not automated source entailment.
"""
import copy
import hashlib
import json
import re
from pathlib import Path

BASE=Path("runs/2026-10-27/stage-c")
INPUT=BASE/"STAGE_0_4_CURRENT_BASELINE_ADDABILITY_20261027.json"
OUTPUT=BASE/"STAGE_0_5_EVIDENCE_SOURCE_CLAIM_QC_20261028.json"
MAP={
 "A_SPEC_R13_DISC_001":[["energyx_buyer","energyx_seller"],["energyx_buyer"],["energyx_seller","energyx_reuters"],["energyx_buyer"]],
 "A_SPEC_R4_DISC_001":[["crma_decision","crma_press"],["crma_decision"],["crma_decision"]],
 "A_SPEC_SRC26-20260928_160143-0194":[["waratah_owner"],["waratah_owner"],["waratah_report"],["waratah_owner","waratah_report"]],
 "A_SPEC_R13_DISC_004":[["benchmark_q3"],["benchmark_q3"],["benchmark_methodology"]],
 "A_SPEC_C0_DISC_20261014_EU_GIGA_ALBATROSS_GRID":[["albatross_grid"],["albatross_grid"],["albatross_finance"]],
 "A_SPEC_C0_DISC_20261005_EU_RETURN_ANTARES_COD":[["antares_owner"],["antares_owner"],["antares_owner"]],
 "A_SPEC_C0_DISC_20261006_EU_BWESS_BERKSWELL_OPT":[["berkswell_owner","berkswell_trader"],["berkswell_owner","berkswell_trader"],["berkswell_prior"],["berkswell_owner"]],
}
HISTORICAL={
 ("A_SPEC_SRC26-20260928_160143-0194",2):"2026-09-09_GL_04",
 ("A_SPEC_C0_DISC_20261006_EU_BWESS_BERKSWELL_OPT",2):"2026-08-31_GL_05",
}
VERIFY={"body_quote_verified","official_material_quote_verified","document_quote_verified"}
def digest(x):
 return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def main():
 obj=json.loads(INPUT.read_text(encoding="utf-8"))
 assert obj["stage"]=="0.4" and obj["status"]=="PASS" and obj["lineage_guard"]=="PASS"
 assert obj["base_main_commit_sha"]=="805c2718d6daf40a219ae94242d9687e33ac3e88"
 assert obj["base_full_blob_sha"]=="07a91714e56be2a8bfad10ab63822f0c5cb3f06e"
 assert len(obj["addable_merge_safe"])==7 and not obj.get("review_pool_deferred_related_uncertain")
 out=[]
 for old in obj["addable_merge_safe"]:
  sid=old["source_spec_id"]
  assert sid in MAP and old["state"]=="accepted_fact_safe"
  assert old["related_lineage"]["status"]=="PASS"
  assert old["source_diversity_status"] in {"PASS_MULTI_SOURCE","PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION"}
  assert old["baseline_revalidation"]["outcome"]=="PASS_EXACT_BASELINE_BOUNDED"
  assert isinstance(old["source_discovery_ledger"],list) and old["source_discovery_ledger"]
  original_sources=old["fact_sources"]
  sources={f["source_key"]:f for f in original_sources}
  assert len(sources)==len(original_sources)
  fact=old["fact"]
  clauses=[s.strip() for s in re.split(r"(?<=[.!?])\s+",fact.strip()) if s.strip()]
  assert len(clauses)==len(MAP[sid]),(sid,len(clauses),len(MAP[sid]))
  sentence_links=[]
  used=[]
  for i,(sentence,keys) in enumerate(zip(clauses,MAP[sid])):
   assert keys and all(k in sources for k in keys),(sid,i,keys)
   ss=[sources[k] for k in keys]
   for f in ss:
    assert f.get("source_quote_status") in VERIFY and f.get("source_quote")
    assert f.get("fetched") is True and f.get("resolved_article_matches_quote") is True
    assert f.get("checked_at") and "fact" in f.get("supports",[])
    assert f.get("supporting_context_only_not_visible_claim_support") is not True
   urls=[s["source_url"] for s in ss]
   used.extend(urls)
   predecessor=HISTORICAL.get((sid,i))
   if predecessor:
    assert predecessor in old["related_lineage"]["related_ids"]
    assert predecessor in [c["id"] for c in old["related_evidence_review"].get("matched_baseline_cards",[])]
   sentence_links.append({
    "sentence_index":i+1,"visible_claim_sentence":sentence,
    "source_keys":keys,"source_urls":urls,
    "baseline_card_source_for_prior_state":predecessor,
    "literal_verified_excerpts":[{"source_key":s["source_key"],"excerpt":s["source_quote"],
      "quote_status":s["source_quote_status"],"stage_b_checked_at":s["checked_at"]} for s in ss],
    "verification_basis":"Prior Stage B body-verified evidence and Stage C fact-safe review; a short excerpt alone is not entailment proof."
   })
  row=copy.deepcopy(old)
  row["claim_source_coverage"]={
   "status":"PASS",
   "visible_fact":{"claim":fact,"supported_by_source_ids":list(dict.fromkeys(used)),
      "sentence_level_audit":sentence_links},
   "unsupported_visible_claim_count":0,
   "manual_editorial_scope":"Existing Stage B/C fact-safe claim-source mapping, not independent automated truth proof",
   "no_new_claims_or_sources":True,
  }
  row["stage_0_5_review"]={
   "claim_sentence_count":len(sentence_links),
   "retained_fact_sources_sha256":digest(original_sources),
   "retained_related_lineage_sha256":digest(old["related_lineage"]),
   "retained_date_role_sha256":digest(old["date_role"]),
   "retained_visible_copy_sha256":digest([old.get(k) for k in ("title","sub","gate","fact","implication")]),
   "predecessor_context_kept_separate_from_new_contract_evidence":True,
   "not_publication_or_merge_approval":True,
  }
  out.append(row)
 assert len(out)==7 and len({x["source_spec_id"] for x in out})==7
 payload={
  "stage":"0.5","status":"PENDING_NATIVE_STAGE_0_5_VALIDATION",
  "run_tag":"STAGE0C_TO_A_20261026",
  "base_main_commit_sha":obj["base_main_commit_sha"],
  "base_full_blob_sha":obj["base_full_blob_sha"],
  "prompt_version":"PROMPT_0_5_V4_20260901",
  "locked_downstream_prompt_0_6_version":"PROMPT_0_6_V5_20260919",
  "lineage_integrity_status":"PASS",
  "upstream_0_4_artifact":str(INPUT),
  "evidence_complete_and_source_claim_covered":out,
  "addable_hold_source_gap":[],"addable_hold_claim_gap":[],
  "stage_a_source_observations_not_reprocessed":1330,
  "stage_b_blocked_lges_preserved":True,
  "not_publish_ready":True,"not_merge_ready":True,
  "method_limits":[
   "Stage B source-quote/text verification and Stage C fact-safe judgments are reused without manufacturing new source text.",
   "0.5 machine checks verify schema, provenance and source mappings, not automatic entailment of entire article claims.",
   "The unreviewed Stage A pool is separate from this seven-item strict cohort."
  ],
 }
 OUTPUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("0.5 CANDIDATES",len(out),"SENTENCES",sum(len(x["claim_source_coverage"]["visible_fact"]["sentence_level_audit"]) for x in out))
 print("0.5 OUTPUT",OUTPUT,OUTPUT.stat().st_size,"PENDING NATIVE CHECKS")
if __name__=="__main__":main()
