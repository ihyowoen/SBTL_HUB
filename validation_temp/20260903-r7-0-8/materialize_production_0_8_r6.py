#!/usr/bin/env python3
import hashlib, json
from pathlib import Path

R5_SHA='a1957c8cac140083029bbcff41e96980c740a03ab8d47bfefae55a8e91fc240c'
R6_SHA='29f02d480ebc8a4c47555d15e5bd23f012c64598574d57e74d18821931e56278'
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
def allowed_single_source(v): return isinstance(v,dict) and v.get('allowed') is True and bool(v.get('reason')) and bool(v.get('mitigation') or v.get('scope_limits'))

run=load(ROOT/'card-run.json')
c07=load(ROOT/'stage-0-7c.json')
s4=load(ROOT/'stages/stage-0-4.json')
s5=load(ROOT/'stages/stage-0-5.json')
s6=load(ROOT/'stages/stage-0-6.json')
s7=load(ROOT/'stages/stage-0-7.json')
stage08=load(ROOT/'stage-0-8.json')
audit=load(ROOT/'card-run-audit.json')

expected={
  'stage_c':'e3eec5c66d3d3b4fa54ccac9aa4ae036f86780a3b97e7ebb1f4faee17b1e4277',
  'stage_0_4':'2944a0c50df99a5c2cf1cb4d3e246011d6d062e19528f07781e37f6dc1fc7152',
  'stage_0_5':'71c24b95e2c5967debc93c14035b41d60bf6530d317148cd2ab4616333a37399',
  'stage_0_6':'216217ff6d439281832637e1edf0bfff1eb6de97ef26c739d19d4a8ada1a84f6',
  'stage_0_7':'d5d4b64bb9696f772c9eb21f589765b09d2362cf7450b708803310c4b93c1aa6',
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
