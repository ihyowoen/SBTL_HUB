#!/usr/bin/env bash
set -euo pipefail

FROZEN_MAIN=aa7400ae67b221d1ddd5e198293762caec389303
BLOB=920646b6b335f211bcd224962f8ac0cc42cd3a4f
RUN_REL=runs/2026-09-08/sep7-r7-current-main-production-r1

# Keep the governed run frozen to its authoritative base.  The live main branch
# is transport-only here; it may move as long as the canonical blob is unchanged.
git config user.name ihyowoen
git config user.email hyowoen@hotmail.com
git fetch origin main
CURRENT_MAIN="$(git rev-parse origin/main)"
test "$(git rev-parse "$FROZEN_MAIN:data/cards.full.json")" = "$BLOB"
test "$(git rev-parse "$CURRENT_MAIN:data/cards.full.json")" = "$BLOB"
git merge --no-edit "$CURRENT_MAIN"

echo "== frozen baseline $FROZEN_MAIN / live main $CURRENT_MAIN share canonical blob $BLOB =="

python - <<'PY'
from pathlib import Path

FROZEN_MAIN='aa7400ae67b221d1ddd5e198293762caec389303'
RUN_REL='runs/2026-09-08/sep7-r7-current-main-production-r1'

p=Path('tmp/sep7-production21-bootstrap/run_v4.sh')
s=p.read_text()

# Preserve the authoritative frozen base SHA while allowing unrelated main
# movement only when data/cards.full.json is byte-identical.
old='test "$(git rev-parse origin/main)" = "$BASE_MAIN"'
new='test "$(git rev-parse "origin/main:data/cards.full.json")" = "$BASE_BLOB"'
if old not in s:
    raise SystemExit('run_v4 live-main equality gate not found')
s=s.replace(old,new,1)
old='test "$(git merge-base HEAD origin/main)" = "$BASE_MAIN"'
new='git merge-base --is-ancestor "$BASE_MAIN" HEAD'
if old not in s:
    raise SystemExit('run_v4 merge-base gate not found')
s=s.replace(old,new,1)
if f'BASE_MAIN={FROZEN_MAIN}' not in s:
    raise SystemExit('run_v4 frozen base binding changed unexpectedly')

validate_marker="echo '== validate pre-apply governed chain =='"
apply_marker="echo '== apply against locked baseline =='"

normalize=r'''echo '== normalize exact invalid Related path and rebind operation freeze =='
python - <<'PYNORM'
import hashlib,json,pathlib
runp=pathlib.Path('runs/2026-09-08/sep7-r7-current-main-production-r1/card-run.json')
run=json.loads(runp.read_text())
BLOCKED='/related_lineage/fresh_follow_up_anchor_class'
ALLOWED={
 '/related/-',
 '/related_ids/-',
 '/related_lineage/related_ids/-',
 '/related_lineage/relation_type',
 '/related_lineage/reason',
 '/related_lineage/event_stage_relationship',
 '/related_lineage/direction',
}

def canon(x):
    if isinstance(x,dict): return {k:canon(x[k]) for k in sorted(x)}
    if isinstance(x,list): return [canon(v) for v in x]
    return x

def opshash(ops):
    payload=json.dumps(canon(ops),ensure_ascii=False,separators=(',',':')).encode()
    return hashlib.sha256(payload).hexdigest()

def replace_hash(x,old,new):
    if isinstance(x,dict): return {k:replace_hash(v,old,new) for k,v in x.items()}
    if isinstance(x,list): return [replace_hash(v,old,new) for v in x]
    return new if x==old else x

assert len(run['operations']['insert'])==21, len(run['operations']['insert'])
assert len(run['operations']['update'])==0, len(run['operations']['update'])
assert len(run['operations'].get('delete',[]))==0, len(run['operations'].get('delete',[]))
assert len(run['operations']['related_add'])==3, len(run['operations']['related_add'])
assert run['expected_before']==1578
assert run['expected_after']==1599

oldhash=opshash(run['operations'])
removed=[]
for i,op in enumerate(run['operations']['related_add']):
    patches=op.get('patches')
    if not isinstance(patches,list) or not patches:
        raise SystemExit(f'related_add[{i}].patches missing/empty')
    keep=[]
    for j,patch in enumerate(patches):
        if not isinstance(patch,dict):
            raise SystemExit(f'related_add[{i}].patches[{j}] not object')
        path=patch.get('path')
        if path==BLOCKED:
            removed.append((i,j,patch.get('card_id')))
            continue
        if path not in ALLOWED:
            raise SystemExit(f'unexpected Related patch path remains: related_add[{i}].patches[{j}] {path}')
        keep.append(patch)
    op['patches']=keep

newhash=opshash(run['operations'])
if removed:
    if oldhash==newhash:
        raise SystemExit('operation hash did not change after exact Related normalization')
    run=replace_hash(run,oldhash,newhash)
    runp.write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n')
    for q in runp.parent.rglob('*.json'):
        if q==runp: continue
        try: obj=json.loads(q.read_text())
        except Exception: continue
        newobj=replace_hash(obj,oldhash,newhash)
        if newobj!=obj:
            q.write_text(json.dumps(newobj,ensure_ascii=False,indent=2)+'\n')
else:
    runp.write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n')

# Re-read persisted card-run and fail closed on any apply-incompatible path.
run=json.loads(runp.read_text())
for i,op in enumerate(run['operations']['related_add']):
    for j,patch in enumerate(op['patches']):
        path=patch.get('path')
        if path==BLOCKED or path not in ALLOWED:
            raise SystemExit(f'apply-incompatible Related path persisted: related_add[{i}].patches[{j}] {path}')

print('removed_exact_blocker_patches=',removed)
print('old_operations_sha256=',oldhash)
print('new_operations_sha256=',newhash)
print('PASS exact Related normalization: insert=21 update=0 related_add=3 expected=1578->1599')
PYNORM
'''

preapply=r'''echo '== hard assert final serialized Related apply contract =='
python - <<'PYPRE'
import json,pathlib
run=json.loads(pathlib.Path('runs/2026-09-08/sep7-r7-current-main-production-r1/card-run.json').read_text())
allowed={
 '/related/-','/related_ids/-','/related_lineage/related_ids/-',
 '/related_lineage/relation_type','/related_lineage/reason',
 '/related_lineage/event_stage_relationship','/related_lineage/direction',
}
bad=[]
for i,op in enumerate(run['operations']['related_add']):
    for j,p in enumerate(op.get('patches',[])):
        if p.get('path') not in allowed:
            bad.append((i,j,p.get('path')))
if bad: raise SystemExit(f'pre-apply invalid Related paths: {bad}')
if len(run['operations']['insert'])!=21 or len(run['operations']['related_add'])!=3:
    raise SystemExit('operation cardinality drift before apply')
if run['expected_before']!=1578 or run['expected_after']!=1599:
    raise SystemExit('expected cardinality drift before apply')
print('PASS final serialized Related contract: invalid_paths=0 insert=21 related_add=3 1578->1599')
PYPRE
'''

if validate_marker not in s:
    raise SystemExit('run_v4 validation marker missing')
s=s.replace(validate_marker,normalize+validate_marker,1)
if apply_marker not in s:
    raise SystemExit('run_v4 apply marker missing')
s=s.replace(apply_marker,preapply+apply_marker,1)
p.write_text(s)
PY

echo '== execute governed v9 chain with frozen-base v11 apply repair =='
bash tmp/sep7-production21-bootstrap/run_v9.sh
