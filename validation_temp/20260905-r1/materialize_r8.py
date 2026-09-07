#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path

SRC=Path('validation_temp/20260905-r1/materialize_r7.py')
exec(compile(SRC.read_text(encoding='utf-8'),str(SRC)+'[R8_FINAL_STAGE_A_ENVELOPE]','exec'),{'__name__':'__main__','__file__':str(SRC)})
ROOT=Path('runs/2026-09-07/r7-20260905-production-r1')
A=ROOT/'stages/stage-a.json'; Q=ROOT/'stage-0-7c.json'
p=json.loads(A.read_text(encoding='utf-8'))

p['review_pool_partition_summary']={
    'candidate_review_pool':0,
    'watchlist_context_pool':0,
    'reject_or_support_only_pool':0,
}
p['source_prompt_authority']='uploaded_or_repo_source_file_prompt'
p['original_status_counts']={'kept':len(p['decision_ledger'])}

compat_gap=(
    'Technology commercialization scoring is not used for this item; '
    'concept_or_target is a frozen-V3 compatibility placeholder only, while active V4 '
    'technology_evidence_level remains not_applicable and technology_performance_safety remains 0/20.'
)
for item in p['strict_passed_spec']:
    assert item['decision_value_breakdown']['technology_performance_safety']==0
    assert item['technology_evidence_level']=='not_applicable'
    item['technology_validation_stage']='concept_or_target'
    item['technology_score_cap_applied']=False
    item['technology_validation_gap']=compat_gap

by_spec={x['spec_id']:x for x in p['strict_passed_spec']}
for row in p['decision_ledger']:
    item=by_spec[row['spec_id']]
    row['technology_validation_stage']=item['technology_validation_stage']
    row['technology_score_cap_applied']=item['technology_score_cap_applied']
    row['technology_validation_gap']=item['technology_validation_gap']

assert p['original_status_counts']=={'kept':11}
assert all(len(p[k])==0 for k in ('candidate_review_pool','watchlist_context_pool','reject_or_support_only_pool'))
A.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
q=json.loads(Q.read_text(encoding='utf-8'))
q['hash_chain']['stage_a']=sha(A)
Q.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('RESULT: PASS_R8_FINAL_STAGE_A_ENVELOPE')
print('STAGE_A_SHA',sha(A))
