#!/usr/bin/env python3
import json, runpy
from pathlib import Path

# Materialize the canonical Prompt 0.5 combined bucket first.
runpy.run_path('validation_temp/20260903-r7-stage-0-5/materialize_0_5.py')
p=Path('/tmp/stage-0-5-r7.json')
data=json.loads(p.read_text(encoding='utf-8'))
rows=data['evidence_complete_and_source_claim_covered']
assert len(rows)==33
# Compatibility projection only: validators such as related_lifecycle_check/date_role_freshness_check
# consume an object with cards[]. The authoritative Prompt 0.5 passing bucket remains unchanged.
data['cards']=rows
p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('RESULT: MATERIALIZED_0_5_R2 cards_alias=33')
