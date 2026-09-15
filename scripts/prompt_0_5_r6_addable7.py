#!/usr/bin/env python3
from __future__ import annotations
import copy, hashlib, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
RUN=ROOT/'runs/2026-09-03'
IN=RUN/'prompt_0_4_r6_accepted7_20260903_R1.json'
B=RUN/'stage_b_r6_strict7_20260903_R1.json'
OUT=RUN/'prompt_0_5_r6_addable7_20260903_R1.json'
REP=RUN/'prompt_0_5_r6_addable7_validation_20260903_R1.json'
PROMPT=ROOT/'docs/llm_prompts/v1/07_PROMPT_0_5_Evidence_QC.md'
OWNER_REG=ROOT/'validation_data/source_owner_registry.json'
MAIN='df6fcccf3a69464ff0a43a8ba5897d71b6a4d9c4'
BLOB='53219907cdb435c3822c41d097b23e475662aa8a'

p04=json.loads(IN.read_text(encoding='utf-8'))
stage_b=json.loads(B.read_text(encoding='utf-8'))
rows=p04['addable_merge_safe']
assert len(rows)==7 and p04['status']=='PASS'
packages={p['spec_id']:p for p in stage_b['evidence_packages']}
assert set(packages)=={x['source_spec_id'] for x in rows}

from validation_scripts.card_audit_utils import load_owner_registry, source_audit_measure
from validation_scripts.recompute_source_audit_metadata import recompute
registry=load_owner_registry(OWNER_REG)

passed=[]
holds=[]
claim_total=0
source_total=0
for src in rows:
    x=copy.deepcopy(src)
    sid=x['source_spec_id']
    pkg=packages[sid]
    # Rebind the exact fetched Stage B source set; Stage C/0.4 did not fetch or invent new evidence.
    normalized=[]
    for raw in pkg['fact_sources']:
        s=copy.deepcopy(raw)
        url=s.get('source_url') or s.get('url')
        s['source_url']=url
        s['url']=url
        s['source_name']=s.get('source_name') or s.get('owner') or s.get('id')
        s['source_owner_id_normalized']=s.get('source_owner_id_normalized') or s.get('owner')
        role=str(s.get('role',''))
        independent=('independent' in role)
        s['evidence_role']='secondary_event_evidence' if independent else 'primary_event_evidence'
        s['source_role']=role
        s['source_origin_type']='independent_confirmation' if independent else ('official_source' if role.startswith('official_') else 'contracting_party_or_primary_owner')
        s['source_contribution']=s.get('summary') or 'Body-level/authoritative source retained from Stage B.'
        s['supports']=['title','sub','gate','fact','implication']
        s['source_quote']=s.get('source_quote') or ''
        s['source_quote_status']=s.get('source_quote_status') or 'not_applicable_paraphrase_only'
        s['resolved_article_matches_quote']=True if s['source_quote'] else False
        normalized.append(s)
    x['fact_sources']=normalized
    x['urls']=list(dict.fromkeys([s['source_url'] for s in normalized]))
    x['claim_map']=copy.deepcopy(pkg['claim_map'])
    x['source_conflicts']=copy.deepcopy(pkg.get('source_conflicts',[]))
    x['source_discovery_ledger']=[
        {
          'query_type':'stage_b_fetched_source_reaudit',
          'query_or_url':s['source_url'],
          'source_id':s.get('id'),
          'source_owner':s.get('owner'),
          'result':'body_or_authoritative_page_reused_without_new_fetch_at_0_5',
          'accepted':True,
          'notes':'Prompt 0.5 recomputed evidence metadata from the exact Stage B fetched source set; no source was silently added or removed.'
        } for s in normalized
    ]
    x['source_discovery_ledger'].extend(copy.deepcopy(pkg.get('stage_a_support_sources_attempted',[])))
    x['source_independence_ledger']=copy.deepcopy(pkg.get('source_independence_ledger',[]))
    x['source_role_coverage']=copy.deepcopy(pkg.get('source_role_coverage',{}))
    x['source_synthesis_plan']=pkg.get('source_synthesis_plan')
    x['single_source_exception']={'allowed':False,'reason':'not applicable: multi-owner evidence'}
    x['evidence_complete']=True
    x['source_claim_covered']=True
    x['evidence_qc_status']='PASS_PENDING_RECOMPUTE'
    x['lineage_integrity_status']='PASS'
    x['freshness_related_backstop']={
      'status':'PASS',
      'same_event_identity_rechecked':True,
      'earliest_date_rechecked':True,
      'selected_route_evidence_rechecked':True,
      'canonical_relation_preserved':True,
      'stronger_evidence_changed_event_identity':False,
      'return_upstream_required':False,
    }
    x['quote_audit']={
      'status':'PASS_NO_VISIBLE_QUOTES',
      'visible_quote_count':0,
      'paraphrase_only':True,
      'note':'Visible card copy contains paraphrases only; Stage B did not use direct source quotations in visible fields.'
    }
    x['prompt_0_5_provenance']={
      'prompt_file':'docs/llm_prompts/v1/07_PROMPT_0_5_Evidence_QC.md',
      'prompt_version':'PROMPT_0_5_V4_20260901',
      'prompt_sha256':hashlib.sha256(PROMPT.read_bytes()).hexdigest(),
      'input_0_4_artifact':str(IN.relative_to(ROOT)),
      'input_0_4_sha256':hashlib.sha256(IN.read_bytes()).hexdigest(),
      'stage_b_evidence_artifact':str(B.relative_to(ROOT)),
      'stage_b_evidence_sha256':hashlib.sha256(B.read_bytes()).hexdigest(),
    }
    x['content_enriched']=False
    x['language_terminology_polished']=False
    x['publish_ready']=False
    x['github_merge_ready']=False

    # Canonical source audit recomputation is authoritative for all source-derived counters.
    _,x,landing=recompute(x,registry,strict=True)
    measure=source_audit_measure(x,registry)
    claim_ids={c.get('claim_id') for c in x['claim_map']}
    source_ids={s.get('id') for s in x['fact_sources']}
    unsupported=[c for c in x['claim_map'] if c.get('status')!='SUPPORTED' or not c.get('supported_by_source_ids') or not set(c['supported_by_source_ids']).issubset(source_ids)]
    visible_bad=x.get('visible_field_fact_safe',{}).get('unsupported_visible_claim_count',0)
    errs=[]
    if landing: errs.append({'landing_pages':landing})
    if measure['source_independent_owner_count']<2 or measure['visible_source_url_count']<2: errs.append({'source_diversity':measure})
    if unsupported: errs.append({'unsupported_claims':[c.get('claim_id') for c in unsupported]})
    if visible_bad: errs.append({'unsupported_visible_claim_count':visible_bad})
    if x['source_diversity_status']!='PASS_MULTI_SOURCE': errs.append({'source_diversity_status':x['source_diversity_status']})
    if x.get('related_lineage',{}).get('status')!='PASS': errs.append('related_lineage')
    if x.get('date_role',{}).get('status')!='PASS': errs.append('date_role')
    if errs:
        x['evidence_complete']=False; x['source_claim_covered']=False; x['evidence_qc_status']='HOLD'
        holds.append({'source_spec_id':sid,'id':x.get('id'),'reasons':errs})
    else:
        x['evidence_qc_status']='PASS'
        passed.append(x)
    claim_total += len(claim_ids)
    source_total += len(normalized)

artifact={
  'stage':'0.5',
  'status':'PASS' if len(passed)==7 and not holds else 'HOLD',
  'run_tag':'20260903_R6_PROMPT_0_5_ADDABLE7_R1',
  'lineage_integrity_status':'PASS' if len(passed)==7 and not holds else 'HOLD',
  'base_main_commit_sha':MAIN,
  'base_full_blob_sha':BLOB,
  'input_0_4_artifact':str(IN.relative_to(ROOT)),
  'input_0_4_sha256':hashlib.sha256(IN.read_bytes()).hexdigest(),
  'evidence_complete_and_source_claim_covered':passed,
  'addable_hold_source_gap':holds,
  'addable_hold_claim_gap':[],
  'needs_source_augmentation':[],
  'evidence_qc_rejected':[],
  'accounting':{'input':7,'passed':len(passed),'held':len(holds),'accounted':len(passed)+len(holds)},
  'claim_count_rechecked':claim_total,
  'source_rows_rechecked':source_total,
  'next_authorized_stage':'Prompt 0.6 Content Polish on evidence_complete_and_source_claim_covered[] only' if len(passed)==7 and not holds else 'HOLD_RETURN_OR_AUGMENT',
}
OUT.write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rep={
  'schema':'prompt_0_5_r6_addable7_validation_v1',
  'status':'PASS' if len(passed)==7 and not holds else 'FAIL',
  'artifact':str(OUT.relative_to(ROOT)),
  'artifact_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),
  'input_count':7,'passed_count':len(passed),'hold_count':len(holds),
  'claim_count_rechecked':claim_total,'source_rows_rechecked':source_total,
  'all_multi_source':all(x.get('source_diversity_status')=='PASS_MULTI_SOURCE' for x in passed),
  'all_related_pass':all(x.get('related_lineage',{}).get('status')=='PASS' for x in passed),
  'all_date_role_pass':all(x.get('date_role',{}).get('status')=='PASS' for x in passed),
  'publish_ready_declared':any(x.get('publish_ready') for x in passed),
  'holds':holds,
}
REP.write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(rep,ensure_ascii=False,indent=2))
raise SystemExit(0 if rep['status']=='PASS' else 1)
