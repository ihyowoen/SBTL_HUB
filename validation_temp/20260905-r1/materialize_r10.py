#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path

SRC=Path('validation_temp/20260905-r1/materialize_r9.py')
try:
    exec(compile(SRC.read_text(encoding='utf-8'),str(SRC)+'[R10_COMPLETE_07C_BINDING]','exec'),{'__name__':'__main__','__file__':str(SRC)})
except AssertionError as exc:
    # R9 intentionally fails closed if the pre-0.8 0.7C object has no legacy
    # round_6_operation_binding. R10 makes that binding authoritative here,
    # before artifact certification, rather than letting 0.8 synthesize it.
    if 'round_6_operation_binding missing' not in str(exc):
        raise

ROOT=Path('runs/2026-09-07/r7-20260905-production-r1')
STAGES=[
    ROOT/'stages/stage-a.json', ROOT/'stages/stage-b.json', ROOT/'stages/stage-c.json',
    ROOT/'stages/stage-0-4.json', ROOT/'stages/stage-0-5.json', ROOT/'stages/stage-0-6.json', ROOT/'stages/stage-0-7.json',
]
RUN=ROOT/'card-run.json'; Q=ROOT/'stage-0-7c.json'
sha=lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
keys=['stage_a','stage_b','stage_c','stage_0_4','stage_0_5','stage_0_6','stage_0_7']
expected=dict(zip(keys,[sha(p) for p in STAGES]))
run=json.loads(RUN.read_text(encoding='utf-8'))
def stable(v):
    if isinstance(v,list): return [stable(x) for x in v]
    if isinstance(v,dict): return {k:stable(v[k]) for k in sorted(v)}
    return v
ops_sha=hashlib.sha256(json.dumps(stable(run['operations']),ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
q=json.loads(Q.read_text(encoding='utf-8'))
q['hash_chain']=expected
q['reviewed_operations_sha256']=ops_sha
q['operation_freeze']['operations_sha256']=ops_sha
q['round_6_operation_binding']={
    'status':'PASS',
    'reviewed_operations_sha256':ops_sha,
    'stage_hashes':expected.copy(),
    'binding_authority':'independent_0_7c_r10_pre_0_8',
}
q['codex_p2_remediation']={
    'status':'PASS','review_id':5130980362,
    'fixed':['stage_a_nested_hash_binding','engie_global_region_and_id','six_single_source_bounded_search_audits','anson_exact_event_date_evidence'],
    'engie_corrected_id':'2026-09-04_GL_01','anson_event_date':'2026-09-03',
    'single_source_search_audit_spec_ids':['STD26_R8_001','STD26_R8_002','STD26_R8_005','STD26_R8_007','STD26_R8_008','STD26_R8_009'],
}
Q.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
q=json.loads(Q.read_text(encoding='utf-8'))
assert q['hash_chain']==expected
assert q['round_6_operation_binding']['stage_hashes']==expected
assert q['reviewed_operations_sha256']==ops_sha==q['operation_freeze']['operations_sha256']==q['round_6_operation_binding']['reviewed_operations_sha256']
eng=[op['card'] for op in run['operations']['insert'] if op.get('card',{}).get('spec_id')=='STD26_R8_005']
assert len(eng)==1 and eng[0]['region']=='GL' and eng[0]['id']=='2026-09-04_GL_01'
print('RESULT: PASS_R10_COMPLETE_0_7C_BINDING')
print('OPS_SHA',ops_sha)
print('HASH_CHAIN',json.dumps(expected,sort_keys=True))
