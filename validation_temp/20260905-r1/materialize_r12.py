#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

SRC = Path('validation_temp/20260905-r1/materialize_r11.py')
exec(compile(SRC.read_text(encoding='utf-8'), str(SRC)+'[R12_ID_ALLOCATION_REBIND]', 'exec'), {'__name__':'__main__','__file__':str(SRC)})

ROOT = Path('runs/2026-09-07/r7-20260905-production-r1')
RUN = ROOT/'card-run.json'
ALLOC = ROOT/'id-allocation.json'
Q = ROOT/'stage-0-7c.json'

run=json.loads(RUN.read_text(encoding='utf-8'))
insert=run['operations']['insert']
id_map={op['card']['spec_id']:op['card']['id'] for op in insert}
assert len(id_map)==9 and len(set(id_map.values()))==9
assert id_map['STD26_R8_005']=='2026-09-04_GL_01'
assert '2026-09-04_EU_01' not in id_map.values()
ALLOC.write_text(json.dumps({'run_id':run['run_id'],'count':len(id_map),'id_map':id_map},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

q=json.loads(Q.read_text(encoding='utf-8'))
rem=q.setdefault('codex_p2_remediation',{})
fixed=rem.setdefault('fixed',[])
if 'id_allocation_ledger_rebound_to_governed_insert_ids' not in fixed:
    fixed.append('id_allocation_ledger_rebound_to_governed_insert_ids')
rem['id_allocation_status']='PASS'
rem['id_allocation_ref']=str(ALLOC)
Q.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# fail closed on all ID surfaces
alloc=json.loads(ALLOC.read_text(encoding='utf-8'))
q2=json.loads(Q.read_text(encoding='utf-8'))
assert alloc['count']==9
assert alloc['id_map']==id_map
assert alloc['id_map']['STD26_R8_005']=='2026-09-04_GL_01'
assert q2['codex_p2_remediation']['id_allocation_status']=='PASS'
print('RESULT: PASS_R12_ID_ALLOCATION_REBIND')
print('ENGIE_ID',alloc['id_map']['STD26_R8_005'])
