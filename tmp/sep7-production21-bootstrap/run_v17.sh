#!/usr/bin/env bash
set -euo pipefail

python - <<'PY'
from pathlib import Path
src=Path('tmp/sep7-production21-bootstrap/run_v10.sh').read_text()
old=r'''# Successful governed runs retain both the independent card-run audit and the
# Prompt 0.8 merge-prep artifact. Never replace the latter after apply.
old="run['audit_refs']=[str(ap)]"
new="run['audit_refs']=list(dict.fromkeys([str(ap), *run.get('audit_refs',[])]))"
if old not in s:
    raise SystemExit('run_v4 post-apply audit_refs overwrite target missing')
s=s.replace(old,new,1)
'''
new=r'''# Current validators intentionally use two phases: validate_card_run_audits
# consumes card_run_audit_v1 refs only; Prompt 0.8 then requires the stage-0-8
# merge-prep artifact to be present in final audit_refs. Preserve that sequence.
audit_validate_marker='node scripts/validate_card_run_audits.mjs --run "$RUN_REL/card-run.json"'
audit_restore=r'''echo '== restore Prompt 0.8 ref after independent audit validation =='
python - <<'PYAUDITREF'
import json,pathlib
runp=pathlib.Path('runs/2026-09-08/sep7-r7-current-main-production-r1/card-run.json')
run=json.loads(runp.read_text())
stage08='runs/2026-09-08/sep7-r7-current-main-production-r1/stage-0-8.json'
if not pathlib.Path(stage08).is_file():
    raise SystemExit(f'missing Prompt 0.8 artifact: {stage08}')
refs=run.get('audit_refs',[])
if len(refs)!=1 or not refs[0].endswith('/card-run-audit.json'):
    raise SystemExit(f'unexpected audit-only refs before 0.8 restore: {refs}')
run['audit_refs']=[refs[0],stage08]
runp.write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n')
print('PASS audit_refs phase transition:',run['audit_refs'])
PYAUDITREF
'''
if audit_validate_marker not in s:
    raise SystemExit('run_v4 audit validator marker missing')
s=s.replace(audit_validate_marker,audit_validate_marker+'\n'+audit_restore,1)
'''
if old not in src:
    raise SystemExit('run_v10 audit preservation patch block not found')
src=src.replace(old,new,1)
Path('/tmp/run_sep7_v17.sh').write_text(src)
PY
bash /tmp/run_sep7_v17.sh
