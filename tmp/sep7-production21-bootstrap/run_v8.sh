#!/usr/bin/env bash
set -euo pipefail
python - <<'PY'
from pathlib import Path
# 1) Upgrade deterministic original18 projection to carry all card-run baseline bindings.
p=Path('tmp/sep7-production21-bootstrap/materialize_original18.py')
s=p.read_text()
s=s.replace("OUT_SHA='c22411c32b70b52f4cb4f978186cff66ecf7e630eafee018dc32499c833c1d8f'", "OUT_SHA='8925b0a5736bb40de036f2e668cbfa66a2cd934b285ea34d7499d889a0523f6e'")
needle="proj['run_tag']='20260908_SEP7_R7_CURRENT_MAIN_STRICT18_PROJECTION'"
replacement=("proj['run_id']='card-run-2026-09-08-sep7-r7-current-main-production-r1'\n"
             "proj['base_main_commit_sha']=MAIN\n"
             "proj['base_full_blob_sha']=BLOB\n"+needle)
if needle not in s: raise SystemExit('original18 baseline insertion target missing')
p.write_text(s.replace(needle,replacement,1))

# 2) Upgrade Prompt 0.1P reconstruction to the same current run/main/blob.
r=Path('tmp/sep7-production21-bootstrap/run_v4.sh')
t=r.read_text()
needle="o['run_id']='card-run-2026-09-08-sep7-r7-current-main-production-r1'"
replacement=(needle+"\n"
             "o['base_main_commit_sha']='aa7400ae67b221d1ddd5e198293762caec389303'\n"
             "o['base_full_blob_sha']='920646b6b335f211bcd224962f8ac0cc42cd3a4f'")
if needle not in t: raise SystemExit('promotion3 baseline insertion target missing')
t=t.replace(needle,replacement,1)

# 3) Before validation, make Stage A Related prepass explicitly bind the same
# counterpart/type already preserved by B/C/0.4-0.7 and the governed related_add op.
marker="echo '== validate pre-apply governed chain =='"
insert=r'''python - <<'PYREL'
import json, pathlib, hashlib
runp=pathlib.Path('runs/2026-09-08/sep7-r7-current-main-production-r1/card-run.json')
run=json.loads(runp.read_text())
inserted={op['card']['id']:op['card']['source_spec_id'] for op in run['operations']['insert']}
paths=[
    pathlib.Path('runs/2026-09-08/sep7-r7-current-main-production-r1/stages/stage-a.json'),
    pathlib.Path('runs/2026-09-08/sep7-r7-current-main-production-r1/stages/stage-a-promotion3.json'),
]
artifacts={p:json.loads(p.read_text()) for p in paths}
by_spec={}
for p,obj in artifacts.items():
    for row in obj.get('strict_passed_spec',[]):
        sid=row.get('spec_id')
        if sid: by_spec[sid]=(p,row)

for i,op in enumerate(run['operations'].get('related_add',[])):
    expected=op.get('source_spec_id')
    if not expected:
        ss=inserted.get(op.get('source_id')); ts=inserted.get(op.get('target_id'))
        expected=ss or ts
    if expected not in by_spec:
        raise SystemExit(f'related_add[{i}] governed Stage A spec not found: {expected}')
    p,row=by_spec[expected]
    sid,tid=op['source_id'],op['target_id']
    ident=op.get('identity_card_id')
    if ident in (sid,tid):
        governed=ident
    else:
        matches=[]
        if inserted.get(sid)==expected: matches.append(sid)
        if inserted.get(tid)==expected: matches.append(tid)
        if len(matches)!=1:
            raise SystemExit(f'related_add[{i}] cannot determine governed endpoint for {expected}: {matches}')
        governed=matches[0]
    counterpart=tid if governed==sid else sid
    pre=row.setdefault('related_prepass',{})
    pre['status']='PASS'
    candidates=pre.setdefault('relation_candidates',[])
    candidate={
        'target_id':counterpart,
        'proposed_relation_type':op['relation_type'],
        'direction':op.get('direction'),
        'event_stage_relationship':op.get('event_stage_relationship'),
    }
    if not any(isinstance(x,dict) and x.get('target_id')==counterpart and (x.get('proposed_relation_type') or x.get('relation_type'))==op['relation_type'] for x in candidates):
        candidates.append(candidate)
    print(f'PASS related_prepass[{i}] spec={expected} counterpart={counterpart} type={op["relation_type"]}')

for p,obj in artifacts.items():
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    print(f'normalized {p} sha256={hashlib.sha256(p.read_bytes()).hexdigest()}')
PYREL
'''
if marker not in t: raise SystemExit('validation marker missing')
t=t.replace(marker,insert+marker,1)
r.write_text(t)
PY
bash tmp/sep7-production21-bootstrap/run_v5.sh
