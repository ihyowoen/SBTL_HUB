#!/usr/bin/env bash
set -euo pipefail
python - <<'PY'
from pathlib import Path
src=Path('tmp/sep7-production21-bootstrap/run_v8.sh').read_text()
old="""    candidate={
        'target_id':counterpart,
        'proposed_relation_type':op['relation_type'],
        'direction':op.get('direction'),
        'event_stage_relationship':op.get('event_stage_relationship'),
    }
    if not any(isinstance(x,dict) and x.get('target_id')==counterpart and (x.get('proposed_relation_type') or x.get('relation_type'))==op['relation_type'] for x in candidates):
        candidates.append(candidate)
"""
new="""    templates=[x for x in candidates if isinstance(x,dict) and (x.get('proposed_relation_type') or x.get('relation_type'))==op['relation_type'] and all(x.get(k) not in (None,'') for k in ('target_candidate_id','confidence','reason','anchor_class_to_verify','incremental_anchor_question'))]
    if not templates:
        raise SystemExit(f'related_add[{i}] has no complete validated R7 relation candidate template for {expected}')
    candidate=dict(templates[0])
    candidate['target_candidate_id']=counterpart
    if not any(isinstance(x,dict) and x.get('target_candidate_id')==counterpart and (x.get('proposed_relation_type') or x.get('relation_type'))==op['relation_type'] for x in candidates):
        candidates.append(candidate)
"""
if old not in src: raise SystemExit('v8 partial Related candidate block not found')
Path('/tmp/run_sep7_v9.sh').write_text(src.replace(old,new,1))
PY
bash /tmp/run_sep7_v9.sh
