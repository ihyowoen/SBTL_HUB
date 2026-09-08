#!/usr/bin/env bash
set -euo pipefail
python - <<'PY'
from pathlib import Path
# Upgrade deterministic original18 projection to carry all card-run baseline bindings.
p=Path('tmp/sep7-production21-bootstrap/materialize_original18.py')
s=p.read_text()
s=s.replace("OUT_SHA='c22411c32b70b52f4cb4f978186cff66ecf7e630eafee018dc32499c833c1d8f'", "OUT_SHA='8925b0a5736bb40de036f2e668cbfa66a2cd934b285ea34d7499d889a0523f6e'")
needle="proj['run_tag']='20260908_SEP7_R7_CURRENT_MAIN_STRICT18_PROJECTION'"
replacement=("proj['run_id']='card-run-2026-09-08-sep7-r7-current-main-production-r1'\n"
             "proj['base_main_commit_sha']=MAIN\n"
             "proj['base_full_blob_sha']=BLOB\n"+needle)
if needle not in s: raise SystemExit('original18 baseline insertion target missing')
p.write_text(s.replace(needle,replacement,1))

# Upgrade the bootstrap reconstruction of Prompt 0.1P so its ordinary Stage-A
# artifact is bound to the same current run/main/blob before validation.
r=Path('tmp/sep7-production21-bootstrap/run_v4.sh')
t=r.read_text()
needle="o['run_id']='card-run-2026-09-08-sep7-r7-current-main-production-r1'"
replacement=(needle+"\n"
             "o['base_main_commit_sha']='aa7400ae67b221d1ddd5e198293762caec389303'\n"
             "o['base_full_blob_sha']='920646b6b335f211bcd224962f8ac0cc42cd3a4f'")
if needle not in t: raise SystemExit('promotion3 baseline insertion target missing')
r.write_text(t.replace(needle,replacement,1))
PY
bash tmp/sep7-production21-bootstrap/run_v5.sh
