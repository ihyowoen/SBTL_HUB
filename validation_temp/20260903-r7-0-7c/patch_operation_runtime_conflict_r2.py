#!/usr/bin/env python3
import copy, hashlib, json
from pathlib import Path

ROOT=Path('runs/2026-09-06/r7-20260903-production-r1')
RUN=ROOT/'card-run.json'
C=ROOT/'stage-0-7c.json'
EXPECTED_OLD='a810e964e298a627b7edc65d28805b03f29a371a016b0aece5053f4589c87407'
EXPECTED_NEW='80b214b597b36dc3c6821a61328d219efc694350b2c0a8e68f2df4ce5e955415'
SCALARS={
 '/related_lineage/relation_type',
 '/related_lineage/reason',
 '/related_lineage/event_stage_relationship',
 '/related_lineage/direction',
}

def stable(v):
    if isinstance(v,list): return [stable(x) for x in v]
    if isinstance(v,dict): return {k:stable(v[k]) for k in sorted(v)}
    return v

def digest(ops):
    raw=json.dumps(stable(ops),ensure_ascii=False,separators=(',',':')).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()

run=json.loads(RUN.read_text(encoding='utf-8'))
c=json.loads(C.read_text(encoding='utf-8'))
ops=run['operations']
assert digest(ops)==EXPECTED_OLD
assert c['reviewed_operations_sha256']==EXPECTED_OLD
assert c['operation_freeze']['operations_sha256']==EXPECTED_OLD

# A single inserted card may have multiple declared predecessor edges. The first
# edge creates scalar lineage fields; later edges on the same source must replace
# the same scalar values, not add the already-existing path again. Array edges
# remain append-only and each operation retains the full declared semantics.
seen_sources=set()
changed=[]
for idx,op in enumerate(ops['related_add']):
    sid=op['source_id']
    if sid in seen_sources:
        for p in op['patches']:
            if p['path'] in SCALARS:
                assert p['op'] in {'add','replace'}
                if p['op']=='add':
                    p['op']='replace'
                    changed.append((idx,sid,p['path']))
    seen_sources.add(sid)

assert changed==[
 (2,'2026-09-02_GL_02','/related_lineage/event_stage_relationship'),
 (2,'2026-09-02_GL_02','/related_lineage/direction'),
], changed
assert digest(ops)==EXPECTED_NEW

# Minimal sequential runtime-shape simulation for inserted Related containers.
inserted={x['card']['id']:copy.deepcopy(x['card']) for x in ops['insert']}
for op in ops['related_add']:
    card=inserted[op['source_id']]
    for p in op['patches']:
        path=p['path']; val=copy.deepcopy(p['value'])
        if path=='/related/-':
            assert p['op']=='add' and val not in card['related']; card['related'].append(val); continue
        if path=='/related_lineage/related_ids/-':
            assert p['op']=='add' and val not in card['related_lineage']['related_ids']; card['related_lineage']['related_ids'].append(val); continue
        assert path in SCALARS
        key=path.rsplit('/',1)[1]
        if p['op']=='add':
            assert key not in card['related_lineage']; card['related_lineage'][key]=val
        elif p['op']=='replace':
            assert key in card['related_lineage']; card['related_lineage'][key]=val
        else: raise AssertionError(p)

amazon=inserted['2026-09-02_GL_02']
assert amazon['related']==['2026-07-02_GL_08','2026-04-16_GL_02']
assert amazon['related_lineage']['related_ids']==amazon['related']
assert amazon['related_lineage']['relation_type']=='distinct_follow_up'
assert amazon['related_lineage']['event_stage_relationship']=='prior_storage_lineage_to_signed_tolling_agreement'
assert amazon['related_lineage']['direction']=='directional'

c['reviewed_operations_sha256']=EXPECTED_NEW
c['operation_freeze']['operations_sha256']=EXPECTED_NEW
RUN.write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
C.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('RESULT: PATCHED_OPERATION_RUNTIME_CONFLICT_R2',{'changed':changed,'operations_sha256':EXPECTED_NEW})
