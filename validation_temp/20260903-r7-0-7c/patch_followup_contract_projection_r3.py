#!/usr/bin/env python3
import hashlib, json
from pathlib import Path

ROOT=Path('runs/2026-09-06/r7-20260903-production-r1')
RUN=ROOT/'card-run.json'
C=ROOT/'stage-0-7c.json'
S07=ROOT/'stages/stage-0-7.json'
EXPECTED_OLD='80b214b597b36dc3c6821a61328d219efc694350b2c0a8e68f2df4ce5e955415'
EXPECTED_NEW='6310d929353a63429969a30985e00ffb01f43859d3f57d9e73405f060a02ccb6'
FOLLOW={'STD26_R7_003','STD26_R7_015'}
FIELDS=(
 'fresh_follow_up_anchor_class',
 'fresh_follow_up_anchor',
 'incremental_fact_vs_predecessor',
 'changed_judgment_vs_predecessor',
)

def stable(v):
    if isinstance(v,list): return [stable(x) for x in v]
    if isinstance(v,dict): return {k:stable(v[k]) for k in sorted(v)}
    return v

def digest(ops):
    raw=json.dumps(stable(ops),ensure_ascii=False,separators=(',',':')).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()

run=json.loads(RUN.read_text(encoding='utf-8'))
c=json.loads(C.read_text(encoding='utf-8'))
s07=json.loads(S07.read_text(encoding='utf-8'))
assert digest(run['operations'])==EXPECTED_OLD
assert c['reviewed_operations_sha256']==EXPECTED_OLD
rows={x['source_spec_id']:x for x in s07['publish_ready']}
assert FOLLOW <= set(rows)

projected=[]
for ins in run['operations']['insert']:
    card=ins['card']; sid=card.get('source_spec_id')
    if sid not in FOLLOW: continue
    source_lineage=rows[sid]['related_lineage']
    lineage=card['related_lineage']
    assert lineage['relation_type']=='new_unrelated_event' and lineage['related_ids']==[]
    for field in FIELDS:
        value=source_lineage.get(field)
        assert isinstance(value,str) and value.strip(),(sid,field,value)
        assert field not in lineage,(sid,field)
        lineage[field]=value
        projected.append((sid,field))

assert len(projected)==8,projected
assert digest(run['operations'])==EXPECTED_NEW
# No relation target is prelinked in the insert; only already-validated follow-up proof
# metadata is preserved so the post-apply distinct_follow_up contract can be evaluated.
for ins in run['operations']['insert']:
    card=ins['card']; sid=card.get('source_spec_id')
    if sid in FOLLOW:
        assert card['related']==[]
        assert card['related_lineage']['related_ids']==[]
        for field in FIELDS: assert card['related_lineage'][field]==rows[sid]['related_lineage'][field]

c['reviewed_operations_sha256']=EXPECTED_NEW
c['operation_freeze']['operations_sha256']=EXPECTED_NEW
RUN.write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
C.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('RESULT: PATCHED_FOLLOWUP_CONTRACT_PROJECTION_R3',{'projected':projected,'operations_sha256':EXPECTED_NEW})
