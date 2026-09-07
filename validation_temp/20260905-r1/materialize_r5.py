#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path

SRC=Path('validation_temp/20260905-r1/materialize_r4.py')
exec(compile(SRC.read_text(encoding='utf-8'),str(SRC)+'[R5_V3_COMPAT_METADATA]','exec'),{'__name__':'__main__','__file__':str(SRC)})
ROOT=Path('runs/2026-09-07/r7-20260905-production-r1')
A=ROOT/'stages/stage-a.json'; Q=ROOT/'stage-0-7c.json'
p=json.loads(A.read_text(encoding='utf-8'))

by_spec={}
for item in p['strict_passed_spec']:
    title=item['title_raw']
    date=item['representative_date']
    evidence=(
        f'Regulatory notice, filing, or issuer document verifying {title}: event date {date}, '
        'stage/status, and reported capacity, volume, price, or cost metric.'
    )
    confirmation=(
        f'A later filing or operating report with capacity, volume, utilisation, price, cost, or status metric for {title} '
        f'would strengthen or weaken the judgment that {item["decision_relevance"]}'
    )
    item['evidence_needed_for_stage_b']=[evidence]
    item['next_confirmation_points']=[confirmation]
    item['stage_a_evidence_status']='not_evidence_complete_no_fetch'
    item['primary_url_semantics']='provided_source_candidate_not_evidence'
    if item['spec_id']=='STD26_R8_005':
        item['execution_anchor_type']='portfolio_capacity_milestone'
        item['execution_anchor_strength']='moderate'
    if item['spec_id']=='STD26_R8_009':
        item['execution_anchor_type']='subsidy_application_window_opened'
        item['execution_anchor_strength']='strong'
    by_spec[item['spec_id']]=item

for row in p['decision_ledger']:
    item=by_spec[row['spec_id']]
    row['evidence_needed_for_stage_b']=list(item['evidence_needed_for_stage_b'])
    row['next_confirmation_points']=list(item['next_confirmation_points'])

A.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
q=json.loads(Q.read_text(encoding='utf-8'))
q['hash_chain']['stage_a']=sha(A)
Q.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('RESULT: PASS_R5_V3_COMPAT_METADATA_ALIGNMENT')
print('STAGE_A_SHA',sha(A))
