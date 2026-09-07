#!/usr/bin/env python3
import hashlib, json
from pathlib import Path

R5_SHA='a1957c8cac140083029bbcff41e96980c740a03ab8d47bfefae55a8e91fc240c'
R6_SHA='82b5055b8410525fc2246b898bedf43cf0a6169c00828036e289576c020f54ab'
WRAPPER=Path('../builder/validation_temp/20260903-r7-0-8/materialize_production_0_8_r5.py')
if not WRAPPER.exists():
    WRAPPER=Path('validation_temp/20260903-r7-0-8/materialize_production_0_8_r5.py')
s=WRAPPER.read_text(encoding='utf-8')
assert s.count(R5_SHA)==1,s.count(R5_SHA)
s=s.replace(R5_SHA,R6_SHA)
exec(compile(s,str(WRAPPER)+'[R6_CODEX_REVIEW_OPERATION_BINDING]','exec'),{'__name__':'__main__','__file__':str(WRAPPER)})

ROOT=Path('runs/2026-09-06/r7-20260903-production-r1')

def load(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def allowed_single_source(v): return v is True or (isinstance(v,dict) and v.get('allowed') is True)

run=load(ROOT/'card-run.json')
c07=load(ROOT/'stage-0-7c.json')
s4=load(ROOT/'stages/stage-0-4.json')
s5=load(ROOT/'stages/stage-0-5.json')
s6=load(ROOT/'stages/stage-0-6.json')
s7=load(ROOT/'stages/stage-0-7.json')
stage08=load(ROOT/'stage-0-8.json')
audit=load(ROOT/'card-run-audit.json')

expected={
  'stage_c':'cf908afe889ed5a93566017d1000654e53c977261e1f3296a50c0101fe5452c6',
  'stage_0_4':'d7a6d79e624f6cbfe63b456b7139e1022e90ba52f817f194435bb3e39e6011d2',
  'stage_0_5':'c30c50934f29ff7a8dd960fc7c64fb0e66263e49a5a066485f6e6329e431f55c',
  'stage_0_6':'8a52693ecf8da9cf6ef1c8d4ca320e82781f2cd393fd34c5285a59d05c677cf9',
  'stage_0_7':'462b4720786f1ead62b7a6ea4f9ed3bf5a35f9697c9f7edbea2c97b9a12a2ec9',
}
assert c07['reviewed_operations_sha256']==R6_SHA
assert c07['operation_freeze']['operations_sha256']==R6_SHA
assert c07['review_corrections_r6']['status']=='PASS'
assert c07['hash_chain_rebinding_r6']['status']=='PASS'
assert sha(ROOT/'stages/stage-c.json')==expected['stage_c']
assert sha(ROOT/'stages/stage-0-4.json')==expected['stage_0_4']
assert sha(ROOT/'stages/stage-0-5.json')==expected['stage_0_5']
assert sha(ROOT/'stages/stage-0-6.json')==expected['stage_0_6']
assert sha(ROOT/'stages/stage-0-7.json')==expected['stage_0_7']
assert s4['stage_c_artifact_sha256']==expected['stage_c']
assert s5['stage_0_4_artifact_sha256']==expected['stage_0_4']
assert s6['input_0_5_sha256']==expected['stage_0_5']
assert s7['input_0_6_sha256']==expected['stage_0_6']
assert stage08['status']=='GITHUB_MERGE_READY'
assert stage08['reviewed_operations_sha256']==R6_SHA
assert stage08['operation_counts']=={'insert':33,'update':0,'related_add':4}
assert audit['status']=='PASS' and audit['audit_complete'] is True
assert audit['reviewed_operations_sha256']==R6_SHA
assert len(audit['inserted_ids'])==33 and audit['updated_ids']==[] and len(audit['related_additions'])==4

ins={op['card']['source_spec_id']:op['card'] for op in run['operations']['insert']}
v=ins['STD26_R7_001']
assert v['date']=='2026-09-02'
assert v['source_published_date']=='2026-09-02'
assert v['fact_sources'][0]['published']=='2026-09-02'
assert v['date_role']['source_publication_dates']==['2026-09-02']
assert 'Sep 02, 2026' in v['date_role']['event_date_source_quote']
s=ins['STD26_R7_P01P_010']
assert s['source_diversity_status']=='PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION'
assert s['source_diversity_measure']['independent_owner_count']==1
assert s['source_synthesis_audit']['independent_confirmation_used'] is False
assert allowed_single_source(s['single_source_exception'])
kr=ins['STD26_R7_011']
assert kr['date']=='2026-09-04' and '9월 4일자로' in kr['date_role']['event_date_source_quote']
wag=[x for x in run['operations']['related_add'] if x.get('source_spec_id')=='STD26_R7_043']
assert len(wag)==1 and wag[0]['target_id']=='2026-07-14_GL_02'

print('RESULT: PASS_PROMPT_0_8_R6_REVIEW_BINDING')
print('OPS_SHA',R6_SHA)
print('HASH_CHAIN',expected)
print('FULL_SHA256',audit['full_output_sha256'])
print('LEAN_SHA256',audit['lean_output_sha256'])
