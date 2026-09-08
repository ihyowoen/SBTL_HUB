#!/usr/bin/env bash
set -euo pipefail
python - <<'PY'
from pathlib import Path
p=Path('tmp/sep7-production21-bootstrap/materialize_original18.py')
s=p.read_text()
s=s.replace("OUT_SHA='c22411c32b70b52f4cb4f978186cff66ecf7e630eafee018dc32499c833c1d8f'", "OUT_SHA='104ad42928890808069b9e24f486b913763c2fa3d64ecd905017181396b87407'")
needle="proj['run_tag']='20260908_SEP7_R7_CURRENT_MAIN_STRICT18_PROJECTION'"
replacement="proj['run_id']='card-run-2026-09-08-sep7-r7-current-main-production-r1'\n"+needle
if needle not in s: raise SystemExit('run_id insertion target missing')
p.write_text(s.replace(needle,replacement,1))
PY
bash tmp/sep7-production21-bootstrap/run_v5.sh
