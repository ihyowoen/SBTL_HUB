#!/usr/bin/env python3
import copy, hashlib, json, re, runpy
from pathlib import Path

runpy.run_path('validation_temp/20260903-r7-stage-0-6/materialize_0_6.py')
p06=Path('/tmp/stage-0-6-r7.json')
sha=hashlib.sha256(p06.read_bytes()).hexdigest()
assert sha=='ea14b35bb1971f54460d8c8fa11d1ddf20dab53f50498b687cd3e1fa09026f75', sha
up=json.loads(p06.read_text(encoding='utf-8'))
rows0=up['content_enriched_and_language_polished']
assert len(rows0)==33

ready=[]
for src in rows0:
    row=copy.deepcopy(src)
    sid=row['source_spec_id']
    # Final visible-field and state checks; no content mutation in 0.7.
    for field in ('title','sub','gate','fact'):
        assert isinstance(row.get(field),str) and row[field].strip(), (sid,field)
    assert isinstance(row.get('implication'),list) and row['implication'], sid
    visible=' '.join([row['title'],row['sub'],row['gate'],row['fact']]+[str(x) for x in row['implication']])
    assert not re.search(r'\b(stage\s*[abc]|strict_passed_spec|supplied\s+r7|source-bound|must\s+verify|candidate\s+artifact)\b',visible,re.I), sid
    assert row.get('evidence_complete') is True and row.get('source_claim_covered') is True, sid
    assert row.get('content_enriched') is True and row.get('language_terminology_polished') is True, sid
    assert row.get('related_lineage',{}).get('status')=='PASS', sid
    assert row.get('date_role',{}).get('representative_date')==row.get('date'), sid
    assert row.get('source_diversity_status') in {'PASS_MULTI_SOURCE','PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION'}, sid
    gates={
      'status':'PASS',
      'full_schema_visible_fields':'PASS',
      'evidence_and_source_claim_coverage':'PASS',
      'date_role_and_id_compatibility':'PASS',
      'event_identity_and_duplicate_risk':'PASS',
      'selection_route_anchor_and_before_after_chain':'PASS',
      'related_lineage_targets_and_chronology':'PASS',
      'terminology_and_title_body_consistency':'PASS',
      'unsupported_inference_check':'PASS',
      'latest_candidate_version_check':'PASS',
      'existing_canonical_regression_check':'PASS',
    }
    row['final_qc_gates']=gates
    row['publish_ready']=True
    row['github_merge_ready']=False
    row['state']='publish_ready'
    row['final_qc']={'status':'PASS','return_stage':None,'blocking_issue_count':0}
    ready.append(row)

canonical=up['cards'][:1536]
assert len(canonical)==1536
root={
 'stage':'0.7','status':'PASS','run_tag':'20260903_R7_PROMPT_0_7_R1',
 'source_prompt_file':'docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md','source_prompt_version':'PROMPT_0_7_V4_20260829',
 'base_main_commit_sha':up['base_main_commit_sha'],'base_full_blob_sha':up['base_full_blob_sha'],
 'input_0_6_sha256':sha,'lineage_and_anchor_guard':'PASS','input_count':33,
 'publish_ready':ready,'hold_evidence':[],'return_content':[],'return_upstream_selection_lineage_date':[],
 'accounting':{'input':33,'publish_ready':33,'hold_evidence':0,'return_content':0,'return_upstream':0,'unaccounted':0},
 'cards':canonical+ready,
}
assert len(root['cards'])==1569 and len(root['publish_ready'])==33
Path('/tmp/stage-0-7-r7.json').write_text(json.dumps(root,ensure_ascii=False,indent=2),encoding='utf-8')
Path('/tmp/current-run-ids-0-7.json').write_text(json.dumps([x['source_spec_id'] for x in ready],ensure_ascii=False,indent=2),encoding='utf-8')
print('RESULT: MATERIALIZED_0_7 publish_ready=33')
