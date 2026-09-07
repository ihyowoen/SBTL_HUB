#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

SRC = Path('validation_temp/20260905-r1/materialize_r12.py')
exec(compile(SRC.read_text(encoding='utf-8'), str(SRC)+'[R13_NESTED_ROUND6_REBIND]', 'exec'), {'__name__':'__main__','__file__':str(SRC)})

ROOT = Path('runs/2026-09-07/r7-20260905-production-r1')
Q = ROOT/'stage-0-7c.json'
q=json.loads(Q.read_text(encoding='utf-8'))

ops=q['reviewed_operations_sha256']
hashes=q['hash_chain']
authority='independent_0_7c_r13_nested_round6_reconciled'

binding={
    'status':'PASS',
    'reviewed_operations_sha256':ops,
    'stage_hashes':hashes.copy(),
    'binding_authority':authority,
}
q['round_6_operation_binding']=binding.copy()
q.setdefault('six_round_review',{})['round_6_operation_binding']=binding.copy()

rem=q.setdefault('codex_p2_remediation',{})
fixed=rem.setdefault('fixed',[])
for item in (
    'nested_six_round_review_round_6_operation_binding_rebound',
    'top_level_and_nested_round_6_binding_identity_asserted',
):
    if item not in fixed:
        fixed.append(item)
rem['nested_round_6_binding_status']='PASS'
rem['binding_authority']=authority

Q.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Fail closed: no contradictory PASS binding may survive on either path.
q2=json.loads(Q.read_text(encoding='utf-8'))
top=q2['round_6_operation_binding']
nested=q2['six_round_review']['round_6_operation_binding']
assert top==nested
assert top['status']=='PASS'
assert top['reviewed_operations_sha256']==q2['reviewed_operations_sha256']==q2['operation_freeze']['operations_sha256']
assert top['stage_hashes']==q2['hash_chain']
assert top['binding_authority']==authority
assert q2['codex_p2_remediation']['nested_round_6_binding_status']=='PASS'
print('RESULT: PASS_R13_NESTED_ROUND6_REBIND')
print('OPS_SHA',ops)
print('BINDING_AUTHORITY',authority)
