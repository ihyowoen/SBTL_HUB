#!/usr/bin/env bash
set -euo pipefail
python - <<'PY'
from pathlib import Path
src=Path('tmp/sep7-production21-bootstrap/run_v4.sh').read_text()
old="assert len(run['operations']['delete'])==0"
new="assert len(run['operations'].get('delete',[]))==0"
if old not in src: raise SystemExit('delete assertion patch target missing')
Path('/tmp/run_sep7_v5.sh').write_text(src.replace(old,new))
PY
bash /tmp/run_sep7_v5.sh
