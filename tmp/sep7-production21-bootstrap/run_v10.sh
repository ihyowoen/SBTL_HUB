#!/usr/bin/env bash
set -euo pipefail
NEW_MAIN=43e40935441c68412cdff7b92f6f082a27ad371d
BLOB=920646b6b335f211bcd224962f8ac0cc42cd3a4f
OLD_MAIN=aa7400ae67b221d1ddd5e198293762caec389303
NEW_PROJ_SHA=2fdaa3e892351d04a814d7853d49a629e65074b0e193095a88999dbf4b7f1079

echo '== sync branch workspace to current main =='
git config user.name ihyowoen
git config user.email hyowoen@hotmail.com
git fetch origin main
test "$(git rev-parse origin/main)" = "$NEW_MAIN"
test "$(git rev-parse "$NEW_MAIN:data/cards.full.json")" = "$BLOB"
git merge --no-edit "$NEW_MAIN"

echo '== relock bootstrap sources and normalize apply contract =='
python - <<'PY'
from pathlib import Path
NEW_MAIN='43e40935441c68412cdff7b92f6f082a27ad371d'
OLD_MAIN='aa7400ae67b221d1ddd5e198293762caec389303'
NEW_PROJ_SHA='2fdaa3e892351d04a814d7853d49a629e65074b0e193095a88999dbf4b7f1079'
OLD_PROJ_SHA='8925b0a5736bb40de036f2e668cbfa66a2cd934b285ea34d7499d889a0523f6e'

p=Path('tmp/sep7-production21-bootstrap/run_v4.sh')
s=p.read_text()
if OLD_MAIN not in s:
    raise SystemExit('run_v4 old-main binding missing')
s=s.replace(OLD_MAIN,NEW_MAIN)
marker="echo '== validate pre-apply governed chain =='"
normalize=r'''echo '== normalize Related apply paths and operation freeze =='
python - <<'PYNORM'
import hashlib,json,pathlib
runp=pathlib.Path('runs/2026-09-08/sep7-r7-current-main-production-r1/card-run.json')
run=json.loads(runp.read_text())
allowed={
 '/related/-',
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
    return hashlib.sha256(json.dumps(canon(ops),ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
oldhash=opshash(run['operations'])
removed=[]
for i,op in enumerate(run['operations'].get('related_add',[])):
    patches=op.get('patches',[])
    keep=[]
    for patch in patches:
        path=patch.get('path') if isinstance(patch,dict) else None
        if path in allowed:
            keep.append(patch)
        else:
            removed.append((i,path))
    op['patches']=keep
newhash=opshash(run['operations'])
if not removed:
    raise SystemExit('expected at least one non-lifecycle Related patch to normalize')
if oldhash==newhash:
    raise SystemExit('operation hash did not change after Related normalization')
def replace_hash(x):
    if isinstance(x,dict): return {k:replace_hash(v) for k,v in x.items()}
    if isinstance(x,list): return [replace_hash(v) for v in x]
    if x==oldhash: return newhash
    return x
run=replace_hash(run)
runp.write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n')
for p in runp.parent.rglob('*.json'):
    if p==runp: continue
    try: obj=json.loads(p.read_text())
    except Exception: continue
    newobj=replace_hash(obj)
    if newobj!=obj:
        p.write_text(json.dumps(newobj,ensure_ascii=False,indent=2)+'\n')
print('removed_related_paths=',removed)
print('old_operations_sha256=',oldhash)
print('new_operations_sha256=',newhash)
for i,op in enumerate(run['operations'].get('related_add',[])):
    bad=[p.get('path') for p in op.get('patches',[]) if p.get('path') not in allowed]
    if bad: raise SystemExit(f'related_add[{i}] unsupported paths remain: {bad}')
PYNORM
'''
if marker not in s:
    raise SystemExit('run_v4 validation marker missing')
s=s.replace(marker,normalize+marker,1)
p.write_text(s)

p=Path('tmp/sep7-production21-bootstrap/materialize_original18.py')
s=p.read_text()
if "MAIN='aa7400ae67b221d1ddd5e198293762caec389303'" not in s:
    raise SystemExit('materializer old-main binding missing')
s=s.replace("MAIN='aa7400ae67b221d1ddd5e198293762caec389303'",f"MAIN='{NEW_MAIN}'")
p.write_text(s)

p=Path('tmp/sep7-production21-bootstrap/run_v8.sh')
s=p.read_text()
if OLD_PROJ_SHA not in s:
    raise SystemExit('run_v8 old projection SHA target missing')
s=s.replace(OLD_PROJ_SHA,NEW_PROJ_SHA)
s=s.replace(OLD_MAIN,NEW_MAIN)
p.write_text(s)
PY

echo '== execute v9 governed chain with v10 relock/apply fix =='
bash tmp/sep7-production21-bootstrap/run_v9.sh
