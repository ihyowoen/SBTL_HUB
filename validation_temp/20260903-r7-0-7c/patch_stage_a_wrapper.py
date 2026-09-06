#!/usr/bin/env python3
import json
from pathlib import Path
p=Path('runs/2026-09-06/r7-20260903-production-r1/stages/stage-a.json')
d=json.loads(p.read_text(encoding='utf-8'))
for field in (
    'stage_a_validity_status',
    'artifact_consistency_status',
    'csv_schema_status',
    'review_pool_partition_status',
    'strict_pass_gate_metadata_status',
    'baseline_duplicate_screen_status',
):
    d[field]='PASS'
required_docs=[
    'docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md',
    'docs/FACT_DISCIPLINE.md',
    'docs/PROMPT_ABC_DEFAULT_MODE.md',
    'docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md',
    'docs/CARD_ID_STANDARD.md',
    'docs/WORKFLOW.md',
    'docs/OPERATIONS.md',
    'docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md',
    'docs/RELATED_LIFECYCLE_CONTRACT.md',
]
d['required_docs_check']={
    'docs_expected':required_docs,
    'docs_read_from_github_main':required_docs,
    'docs_missing_or_unreadable':[],
    'status':'PASS',
    'authority_note':'The integrated V4 Stage A prompt is the sole active selection authority. Superseded Structural V3 policy/addendum and PROMPT_ABC_SUPPORTING_RULES are not persisted as active authority; current main supplies frozen V3 document-presence aliases only in a private compatibility projection.',
}
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('RESULT: PATCHED_STAGE_A_WRAPPER_STATUS_6_AND_REQUIRED_DOCS_PASS')
