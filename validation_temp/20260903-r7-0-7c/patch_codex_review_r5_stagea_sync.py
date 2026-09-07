#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path('runs/2026-09-06/r7-20260903-production-r1')
PATH=ROOT/'stages/stage-a.json'
SID='STD26_R7_043'
TARGET='2026-07-14_GL_02'
EXPECTED='Current baseline treatment for NR_20260903_E0410 now follows R5 review correction relation=distinct_follow_up to 2026-07-14_GL_02.'

obj=json.loads(PATH.read_text(encoding='utf-8-sig'))
strict=[x for x in obj.get('strict_passed_spec',[]) if x.get('spec_id')==SID]
assert len(strict)==1,len(strict)
row=strict[0]
assert row.get('baseline_match')==[TARGET]
assert row.get('baseline_relation')=='distinct_follow_up'
assert row.get('baseline_follow_up_relation')=='distinct_follow_up'
assert row.get('baseline_expectation_changed')==EXPECTED

summary=obj.get('summary',{})
ids=summary.get('follow_up_candidate_ids')
assert isinstance(ids,list),ids
if SID not in ids: ids.append(SID)
assert set(ids)=={'STD26_R7_003','STD26_R7_015',SID},ids

ledger=[x for x in obj.get('decision_ledger',[]) if x.get('spec_id')==SID]
assert ledger, 'missing Stage A ledger row for Wagerup'
for entry in ledger:
    entry['baseline_match']=[TARGET]
    entry['baseline_relation']='distinct_follow_up'
    entry['baseline_expectation_changed']=EXPECTED
    entry['follow_up_relation']='distinct_follow_up'

PATH.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('RESULT: PATCHED_CODEX_REVIEW_R5_STAGE_A_SYNC',{'spec_id':SID,'ledger_rows':len(ledger),'follow_up_candidate_ids':ids})
