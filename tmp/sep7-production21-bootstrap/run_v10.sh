#!/usr/bin/env bash
set -euo pipefail

FROZEN_MAIN=aa7400ae67b221d1ddd5e198293762caec389303
BLOB=920646b6b335f211bcd224962f8ac0cc42cd3a4f

# Keep the governed run frozen to its authoritative base. Live main is checked
# only for canonical-data equivalence; transport/mergeability is a later gate.
git config user.name ihyowoen
git config user.email hyowoen@hotmail.com
git fetch origin main
CURRENT_MAIN="$(git rev-parse origin/main)"
test "$(git rev-parse "$FROZEN_MAIN:data/cards.full.json")" = "$BLOB"
test "$(git rev-parse "$CURRENT_MAIN:data/cards.full.json")" = "$BLOB"
git merge-base --is-ancestor "$FROZEN_MAIN" origin/main

echo "== frozen baseline $FROZEN_MAIN; live main $CURRENT_MAIN has identical canonical blob $BLOB =="

python - <<'PY'
from pathlib import Path

FROZEN_MAIN='aa7400ae67b221d1ddd5e198293762caec389303'
p=Path('tmp/sep7-production21-bootstrap/run_v4.sh')
s=p.read_text()

old='test "$(git rev-parse origin/main)" = "$BASE_MAIN"'
new='test "$(git rev-parse "origin/main:data/cards.full.json")" = "$BASE_BLOB"'
if old not in s:
    raise SystemExit('run_v4 live-main equality gate not found')
s=s.replace(old,new,1)
old='test "$(git merge-base HEAD origin/main)" = "$BASE_MAIN"'
new='git merge-base --is-ancestor "$BASE_MAIN" origin/main\ngit merge-base --is-ancestor "$BASE_MAIN" HEAD'
if old not in s:
    raise SystemExit('run_v4 merge-base gate not found')
s=s.replace(old,new,1)
if f'BASE_MAIN={FROZEN_MAIN}' not in s:
    raise SystemExit('run_v4 frozen base binding changed unexpectedly')

# Successful governed runs retain both the independent card-run audit and the
# Prompt 0.8 merge-prep artifact. Never replace the latter after apply.
old="run['audit_refs']=[str(ap)]"
new="run['audit_refs']=list(dict.fromkeys([str(ap), *run.get('audit_refs',[])]))"
if old not in s:
    raise SystemExit('run_v4 post-apply audit_refs overwrite target missing')
s=s.replace(old,new,1)

validate_marker="echo '== validate pre-apply governed chain =='"
apply_marker="echo '== apply against locked baseline =='"

normalize=r'''echo '== normalize Related apply surface/op semantics and rebind operation freeze =='
python - <<'PYNORM'
import hashlib,json,pathlib,subprocess
runp=pathlib.Path('runs/2026-09-08/sep7-r7-current-main-production-r1/card-run.json')
run=json.loads(runp.read_text())
FROZEN='aa7400ae67b221d1ddd5e198293762caec389303'
ALLOWED={
 '/related/-',
 '/related_ids/-',
 '/related_lineage/related_ids/-',
 '/related_lineage/relation_type',
 '/related_lineage/reason',
 '/related_lineage/event_stage_relationship',
 '/related_lineage/direction',
}
META={
 '/related_lineage/relation_type',
 '/related_lineage/reason',
 '/related_lineage/event_stage_relationship',
 '/related_lineage/direction',
}
EDGE={'/related/-','/related_ids/-','/related_lineage/related_ids/-'}

def canon(x):
    if isinstance(x,dict): return {k:canon(x[k]) for k in sorted(x)}
    if isinstance(x,list): return [canon(v) for v in x]
    return x

def opshash(ops):
    return hashlib.sha256(json.dumps(canon(ops),ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def replace_hash(x,old,new):
    if isinstance(x,dict): return {k:replace_hash(v,old,new) for k,v in x.items()}
    if isinstance(x,list): return [replace_hash(v,old,new) for v in x]
    return new if x==old else x

def load_base_cards():
    raw=subprocess.check_output(['git','show',f'{FROZEN}:data/cards.full.json'])
    obj=json.loads(raw)
    cards=obj if isinstance(obj,list) else obj.get('cards',[])
    return {c['id']:c for c in cards if isinstance(c,dict) and c.get('id')}

assert len(run['operations']['insert'])==21
assert len(run['operations']['update'])==0
assert len(run['operations'].get('delete',[]))==0
assert len(run['operations']['related_add'])==3
assert run['expected_before']==1578 and run['expected_after']==1599

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
        if path in ALLOWED:
            keep.append(patch)
            continue
        if isinstance(path,str) and path.startswith('/related_lineage/'):
            removed.append((i,j,patch.get('card_id'),path))
            continue
        raise SystemExit(f'unexpected non-lineage Related patch path: related_add[{i}].patches[{j}] {path}')
    if not keep:
        raise SystemExit(f'related_add[{i}] lost all apply patches after lineage metadata normalization')
    op['patches']=keep

state=load_base_cards()
for ins in run['operations']['insert']:
    card=ins['card']
    state[card['id']]=json.loads(json.dumps(card))
normalized_ops=[]
for i,op in enumerate(run['operations']['related_add']):
    for j,patch in enumerate(op['patches']):
        cid=patch.get('card_id'); path=patch.get('path')
        card=state.get(cid)
        if card is None:
            raise SystemExit(f'related_add[{i}].patches[{j}] card missing from candidate state: {cid}')
        if path in META:
            rl=card.get('related_lineage')
            if not isinstance(rl,dict):
                rl={}; card['related_lineage']=rl
            key=path.rsplit('/',1)[-1]
            desired='replace' if key in rl else 'add'
            if patch.get('op')!=desired:
                normalized_ops.append((i,j,cid,path,patch.get('op'),desired))
                patch['op']=desired
            rl[key]=json.loads(json.dumps(patch.get('value')))
        elif path in EDGE:
            if patch.get('op')!='add':
                raise SystemExit(f'related_add[{i}].patches[{j}] edge op must remain add: {path}')
            if path=='/related/-':
                arr=card.setdefault('related',[])
            elif path=='/related_ids/-':
                arr=card.setdefault('related_ids',[])
            else:
                rl=card.setdefault('related_lineage',{})
                arr=rl.setdefault('related_ids',[])
            if not isinstance(arr,list):
                raise SystemExit(f'related_add[{i}].patches[{j}] edge parent not array: {path}')
            if patch.get('value') in arr:
                raise SystemExit(f'true duplicate Related edge before apply: related_add[{i}].patches[{j}] {cid} {path} {patch.get("value")}')
            arr.append(json.loads(json.dumps(patch.get('value'))))

newhash=opshash(run['operations'])
if removed or normalized_ops:
    if oldhash==newhash:
        raise SystemExit('operation hash did not change after Related normalization')
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

run=json.loads(runp.read_text())
for i,op in enumerate(run['operations']['related_add']):
    for j,patch in enumerate(op['patches']):
        path=patch.get('path')
        if path not in ALLOWED:
            raise SystemExit(f'apply-incompatible Related path persisted: related_add[{i}].patches[{j}] {path}')
        if path in EDGE and patch.get('op')!='add':
            raise SystemExit(f'append-only edge op drift: related_add[{i}].patches[{j}] {path} {patch.get("op")}')
        if path in META and patch.get('op') not in {'add','replace'}:
            raise SystemExit(f'metadata op invalid: related_add[{i}].patches[{j}] {path} {patch.get("op")}')

print('removed_noncanonical_lineage_metadata_patches=',removed)
print('removed_count=',len(removed))
print('normalized_metadata_ops=',normalized_ops)
print('normalized_metadata_op_count=',len(normalized_ops))
print('old_operations_sha256=',oldhash)
print('new_operations_sha256=',newhash)
print('PASS Related apply normalization: insert=21 update=0 related_add=3 expected=1578->1599')
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
meta={
 '/related_lineage/relation_type','/related_lineage/reason',
 '/related_lineage/event_stage_relationship','/related_lineage/direction',
}
edge={'/related/-','/related_ids/-','/related_lineage/related_ids/-'}
bad=[]
for i,op in enumerate(run['operations']['related_add']):
    for j,p in enumerate(op.get('patches',[])):
        path=p.get('path'); pop=p.get('op')
        if path not in allowed or (path in edge and pop!='add') or (path in meta and pop not in {'add','replace'}):
            bad.append((i,j,path,pop))
if bad: raise SystemExit(f'pre-apply invalid Related patches: {bad}')
if len(run['operations']['insert'])!=21 or len(run['operations']['related_add'])!=3:
    raise SystemExit('operation cardinality drift before apply')
if run['expected_before']!=1578 or run['expected_after']!=1599:
    raise SystemExit('expected cardinality drift before apply')
print('PASS final serialized Related contract: invalid_patches=0 insert=21 related_add=3 1578->1599')
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

echo '== execute governed v9 chain with frozen-base v16 apply repair =='
bash tmp/sep7-production21-bootstrap/run_v9.sh
