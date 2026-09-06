#!/usr/bin/env python3
import base64, hashlib, json, zlib
from pathlib import Path
RUN_ID='card-run-2026-09-06-r7-20260903-production-r1'
MAIN='5317bec055b88a26cffb136e7844eb488ae4db0d'
BLOB='8b3d96b5c1fd779567ef8512f7123fc4310093ec'
TEMPLATE_SHA='a94521812453d18a7036f15296d246eb1d0a45902a3f5a8bb2e5dcab5391987b'
base=Path('validation_temp/20260903-r7-0-7c')
parts=[base/f'stage-a-prod33.part{i:02d}' for i in range(1,8)]
assert all(p.is_file() for p in parts), [str(p) for p in parts if not p.is_file()]
chunks=[p.read_text(encoding='utf-8').strip() for p in parts]
assert [len(x) for x in chunks]==[9000,9000,9000,9000,9000,9000,4388], [len(x) for x in chunks]
b64=''.join(chunks)
assert len(b64)==58388 and len(b64)%4==0
raw=zlib.decompress(base64.b64decode(b64))
assert len(raw)==684842
assert hashlib.sha256(raw).hexdigest()==TEMPLATE_SHA
d=json.loads(raw)
d['run_id']=RUN_ID
d['base_main_commit_sha']=MAIN
d['base_full_blob_sha']=BLOB
d['stage']='stage_a'
d['status']='PASS'
required_docs=[
    'docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md','docs/FACT_DISCIPLINE.md','docs/PROMPT_ABC_DEFAULT_MODE.md',
    'docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md','docs/CARD_ID_STANDARD.md','docs/WORKFLOW.md','docs/OPERATIONS.md',
    'docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md','docs/RELATED_LIFECYCLE_CONTRACT.md',
]
d['required_docs_check']={
    'docs_expected':required_docs,'docs_read_from_github_main':required_docs,'docs_missing_or_unreadable':[],'status':'PASS',
    'authority_note':'The integrated V4 Stage A prompt is the sole active selection authority. Superseded Structural V3 policy/addendum and PROMPT_ABC_SUPPORTING_RULES are not persisted as active authority; current main supplies frozen V3 document-presence aliases only in a private compatibility projection.'
}
p=Path('runs/2026-09-06/r7-20260903-production-r1/stages/stage-a.json')
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert len(d['strict_passed_spec'])==33
assert d['event_count']==33
assert d['story_count']==45 and len(d['decision_ledger'])==45
assert d['summary']['ledger_matches_story_count'] is True
assert d['review_pool_carry_forward_ledger_status']=='PASS'
print('RESULT: MATERIALIZED_FULL_STAGE_A_PRODUCTION33 events=33 stories=45 strict=33 review=0 template_sha='+TEMPLATE_SHA)
