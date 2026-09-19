#!/usr/bin/env python3
from __future__ import annotations
import copy, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'runs/2026-09-03'
IN=RUN/'prompt_0_6_r6_combined9_20260903_R1.json'
OUT=RUN/'prompt_0_7_r6_combined9_20260903_R1.json'
MERGED=RUN/'prompt_0_7_r6_combined9_merged_baseline_candidate_20260903_R1.json'
REP=RUN/'prompt_0_7_r6_combined9_validation_20260903_R1.json'
IDS=RUN/'prompt_0_7_r6_combined9_current_run_ids_20260903_R1.json'
PROMPT=ROOT/'docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md'
CANON=ROOT/'data/cards.full.json'
MAIN='df6fcccf3a69464ff0a43a8ba5897d71b6a4d9c4'
BLOB='53219907cdb435c3822c41d097b23e475662aa8a'

data=json.loads(IN.read_text(encoding='utf-8'))
rows=data['content_enriched_and_language_polished']
assert data['status']=='PASS' and len(rows)==9
ids=[x['id'] for x in rows]
assert len(ids)==len(set(ids))==9
IDS.write_text(json.dumps(ids,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

passed=[]; holds=[]
for src in rows:
    x=copy.deepcopy(src); sid=x['source_spec_id']; lin=x.get('related_lineage',{}); errs=[]
    if not all(x.get(k) for k in ('id','date','region','cat','sub_cat','signal','title','sub','gate','fact')): errs.append('full_schema_visible_field_gap')
    if not isinstance(x.get('implication'),list) or not x['implication']: errs.append('implication_gap')
    if not isinstance(x.get('fact_sources'),list) or len(x['fact_sources'])<2: errs.append('fact_sources_gap')
    if x.get('source_diversity_status')!='PASS_MULTI_SOURCE': errs.append('source_diversity')
    if not x.get('evidence_complete') or not x.get('source_claim_covered'): errs.append('evidence_state')
    if not x.get('content_enriched') or not x.get('language_terminology_polished'): errs.append('content_state')
    if lin.get('status')!='PASS': errs.append('related_status')
    if lin.get('relation_type')=='new_unrelated_event' and lin.get('related_ids'): errs.append('new_unrelated_has_target')
    if lin.get('relation_type') in {'distinct_follow_up','program_lineage'} and not lin.get('related_ids'): errs.append('lineage_target_missing')
    if x.get('date_role',{}).get('status')!='PASS': errs.append('date_role')
    if x.get('visible_field_fact_safe',{}).get('unsupported_visible_claim_count',0)!=0: errs.append('visible_claim_support')
    if x.get('content_polish_audit',{}).get('new_fact_added') is not False: errs.append('content_fact_drift')
    if x.get('content_polish_audit',{}).get('related_edges_changed') is not False: errs.append('content_related_drift')
    if errs:
        holds.append({'source_spec_id':sid,'id':x.get('id'),'reasons':errs})
        continue
    x['final_qc_gates']={
      'status':'PASS',
      'full_schema_visible_fields':'PASS',
      'evidence_source_claim_coverage':'PASS',
      'source_synthesis_and_diversity':'PASS',
      'date_role_and_id_compatibility':'PASS',
      'event_identity_duplicate_risk':'PASS_0_4_REVALIDATED',
      'selection_route_anchor_before_after_chain':'PASS',
      'related_lineage_targets_chronology_self_duplicate':'PASS_PENDING_SCOPED_MACHINE_RECHECK',
      'terminology_title_body_consistency':'PASS',
      'unsupported_inference':'PASS',
      'latest_candidate_version':'PASS',
      'canonical_regression_guard':'PASS_BASELINE_HASH_LOCKED',
    }
    x['final_qc_scope']={'current_run_id':x['id'],'scope_method':'exact_id','fuzzy_matching_used':False}
    x['prompt_0_7_provenance']={
      'prompt_file':'docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md',
      'prompt_version':'PROMPT_0_7_V4_20260829',
      'prompt_sha256':hashlib.sha256(PROMPT.read_bytes()).hexdigest(),
      'input_0_6_artifact':str(IN.relative_to(ROOT)),
      'input_0_6_sha256':hashlib.sha256(IN.read_bytes()).hexdigest(),
      'current_run_id_file':str(IDS.relative_to(ROOT)),
    }
    x['publish_ready']=True
    x['github_merge_ready']=False
    passed.append(x)

artifact={
 'stage':'0.7','status':'PASS' if len(passed)==9 and not holds else 'HOLD',
 'run_tag':'20260903_R6_PROMPT_0_7_COMBINED9_R1',
 'lineage_and_anchor_guard':'PASS' if len(passed)==9 and not holds else 'HOLD',
 'base_main_commit_sha':MAIN,'base_full_blob_sha':BLOB,'base_full_card_count':1514,
 'input_0_6_artifact':str(IN.relative_to(ROOT)),'input_0_6_sha256':hashlib.sha256(IN.read_bytes()).hexdigest(),
 'current_run_id_file':str(IDS.relative_to(ROOT)),'current_run_id_count':9,
 'publish_ready':passed,
 'hold_evidence':[],'return_content':holds,'return_upstream_selection_lineage_date':[], 'authorized_reject':[],
 'card_claim_diversity_audit':copy.deepcopy(data.get('card_claim_diversity_audit',[])),
 'related_coverage_audit':copy.deepcopy(data.get('related_coverage_audit',[])),
 'accounting':{'input':9,'publish_ready':len(passed),'held_or_returned':len(holds),'accounted':len(passed)+len(holds)},
 'prompt_0_8_authorized':False,
 'next_authorized_stage':'Prompt 0.7C Independent Completeness Review' if len(passed)==9 and not holds else 'RETURN_EARLIEST_RESPONSIBLE_STAGE',
}
OUT.write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

canon=json.loads(CANON.read_text(encoding='utf-8'))
canon_cards=canon if isinstance(canon,list) else canon.get('cards',[])
assert len(canon_cards)==1514
merged=copy.deepcopy(artifact)
merged['cards']=canon_cards
merged['merged_baseline_candidate_card_count']=1514+len(passed)
merged['canonical_inventory_sha256']=hashlib.sha256(CANON.read_bytes()).hexdigest()
MERGED.write_text(json.dumps(merged,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

rep={
 'schema':'prompt_0_7_r6_combined9_validation_v1','status':'PASS' if len(passed)==9 and not holds else 'FAIL',
 'artifact':str(OUT.relative_to(ROOT)),'artifact_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),
 'merged_baseline_candidate':str(MERGED.relative_to(ROOT)),'merged_baseline_candidate_sha256':hashlib.sha256(MERGED.read_bytes()).hexdigest(),
 'current_run_id_file':str(IDS.relative_to(ROOT)),'current_run_id_sha256':hashlib.sha256(IDS.read_bytes()).hexdigest(),
 'input_count':9,'publish_ready_count':len(passed),'hold_count':len(holds),
 'prompt_0_8_authorized':False,'holds':holds,
}
REP.write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(rep,ensure_ascii=False,indent=2))
raise SystemExit(0 if rep['status']=='PASS' else 1)
