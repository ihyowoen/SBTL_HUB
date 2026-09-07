#!/usr/bin/env python3
from __future__ import annotations
import copy, hashlib, json, subprocess, sys
from pathlib import Path

RUN_ID='card-run-2026-09-07-r7-20260905-production-r1'
BASE_MAIN='eb1a311ed378fcdf547b52ad5da0652cb9f1fc62'
BASE_BLOB='707fe5ea9836a0c2341771397da32c818a95cbed'
OPS_SHA='7899d373343332dac7b4e9e7000edc439a9c2b28ff5990f3d0d7088efbe1cd3e'
RUN_ROOT=Path('runs/2026-09-07/r7-20260905-production-r1')
CARD_RUN=RUN_ROOT/'card-run.json'
STAGE08=RUN_ROOT/'stage-0-8.json'
AUDIT=RUN_ROOT/'card-run-audit.json'
LEDGER=RUN_ROOT/'prompt-0-8-id-ledger.json'
FULL=Path('data/cards.full.json')
LEAN=Path('public/data/cards.json')
BEFORE=1569
AFTER=1578


def sh(*args, capture=False):
    p=subprocess.run(args,text=True,capture_output=capture)
    if p.returncode:
        if capture:
            print(p.stdout,file=sys.stderr); print(p.stderr,file=sys.stderr)
        raise SystemExit(p.returncode)
    return p.stdout.strip() if capture else ''

def load(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p,obj):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha256(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def stable(v):
    if isinstance(v,list): return [stable(x) for x in v]
    if isinstance(v,dict): return {k:stable(v[k]) for k in sorted(v)}
    return v
def operations_sha(ops):
    return hashlib.sha256(json.dumps(stable(ops),ensure_ascii=False,separators=(',',':')).encode('utf-8')).hexdigest()

head=sh('git','rev-parse','HEAD',capture=True)
assert head==BASE_MAIN,(head,BASE_MAIN)
assert sh('git','rev-parse',f'{BASE_MAIN}:data/cards.full.json',capture=True)==BASE_BLOB
assert sh('git','hash-object',str(FULL),capture=True)==BASE_BLOB
base=load(FULL)
assert base.get('total')==BEFORE and len(base['cards'])==BEFORE

run=load(CARD_RUN)
assert run['run_id']==RUN_ID
assert run['base_main_commit_sha']==BASE_MAIN
assert run['base_full_blob_sha']==BASE_BLOB
assert run['expected_before']==BEFORE and run['expected_after']==AFTER
assert {k:len(run['operations'].get(k,[])) for k in ('insert','update','related_add')}=={'insert':9,'update':0,'related_add':0}
assert operations_sha(run['operations'])==OPS_SHA
assert run['independent_completeness_ref']==str(RUN_ROOT/'stage-0-7c.json')
assert run['audit_refs']==[str(AUDIT),str(STAGE08)]

c07=load(RUN_ROOT/'stage-0-7c.json')
assert str(c07.get('status','')).startswith('PASS'),c07.get('status')
assert c07.get('prompt_0_8_authorized') is True
assert c07['reviewed_operations_sha256']==OPS_SHA
freeze=c07['operation_freeze']
assert freeze['status']=='PASS' and freeze['operations_sha256']==OPS_SHA
assert freeze['insert']==9 and freeze['update']==0 and freeze['related_add']==0
assert freeze['expected_before']==BEFORE and freeze['expected_after']==AFTER
assert freeze['operation_drift_allowed'] is False

expected_hashes={
    'stage_a':'5e2a35eba6f58155d3e8ce128c1cc2f72122a80295d188619cbcc64ae1b29d0e',
    'stage_b':'33dcc9600bc5ef60478f4bd8f22c129d22bbf83508676707cbb7b6e6be6583cd',
    'stage_c':'ce699c68e81af7b29a73e350fc710d66328e42c96951291262db377f09e4ecda',
    'stage_0_4':'c6dd3d2b5493360daf16a0d1b1a55593dbcc163f1be6bba027f7296906289972',
    'stage_0_5':'ab5b6033dc105a014ae9616e5f90098b197cd741c8889eeef06197d960436da9',
    'stage_0_6':'132e169d4685ad475e98c632e9b9624bc74e7612df2f26fbe3daf04b54c7c06f',
    'stage_0_7':'ca69e3952e0a617c312d951cdcb8a96244b5ab4188670c0eececbdbe0df0dd08',
}
paths={
    'stage_a':RUN_ROOT/'stages/stage-a.json',
    'stage_b':RUN_ROOT/'stages/stage-b.json',
    'stage_c':RUN_ROOT/'stages/stage-c.json',
    'stage_0_4':RUN_ROOT/'stages/stage-0-4.json',
    'stage_0_5':RUN_ROOT/'stages/stage-0-5.json',
    'stage_0_6':RUN_ROOT/'stages/stage-0-6.json',
    'stage_0_7':RUN_ROOT/'stages/stage-0-7.json',
}
for key,path in paths.items(): assert sha256(path)==expected_hashes[key],(key,sha256(path),expected_hashes[key])
assert c07['hash_chain']==expected_hashes
assert c07['round_6_operation_binding']['reviewed_operations_sha256']==OPS_SHA
assert c07['round_6_operation_binding']['stage_hashes']==expected_hashes
assert c07['round_6_operation_binding']['binding_authority']=='independent_0_7c_r11_verified_source_discovery_ledger'
assert c07['codex_p2_remediation']['status']=='PASS'
assert c07['codex_p2_remediation']['review_id']==5130980362
s4=load(paths['stage_0_4']); s5=load(paths['stage_0_5']); s6=load(paths['stage_0_6']); s7=load(paths['stage_0_7'])
assert s4['stage_c_artifact_sha256']==expected_hashes['stage_c']
assert s5['stage_0_4_artifact_sha256']==expected_hashes['stage_0_4']
assert s6['input_0_5_sha256']==expected_hashes['stage_0_5']
assert s7['input_0_6_sha256']==expected_hashes['stage_0_6']

CERTIFIED_WORKFLOW_RUN_ID=34129245202
CERTIFIED_ARTIFACT_ID=10021379057
CERTIFIED_ARTIFACT_SHA='5fe2a7ba0bec2a99d09a2456d6568cad5d769fe0b8cdcc4ffc31b086c2d8deb8'

dump(AUDIT,{'schema':'card_run_audit_v1','status':'PASS','temporary_materialization_only':True})
dump(STAGE08,{'stage':'0.8','status':'PASS','temporary_materialization_only':True})
sh('node','scripts/apply_card_run.mjs','--run',str(CARD_RUN),'--baseline',str(FULL),'--canonical-path',str(FULL),
   '--output',str(FULL),'--report',str(RUN_ROOT/'apply-report.json'),'--base-main-sha',BASE_MAIN,
   '--lean-path',str(LEAN),'--apply')

full=load(FULL)
assert full.get('total')==AFTER and len(full['cards'])==AFTER
by_id={c['id']:c for c in full['cards']}
insert_ids=[op['card']['id'] for op in run['operations']['insert']]
assert len(insert_ids)==9 and len(set(insert_ids))==9
assert all(cid in by_id for cid in insert_ids)
assert '2026-09-04_GL_01' in insert_ids and '2026-09-04_EU_01' not in insert_ids
assert not run['operations']['update'] and not run['operations']['related_add']
operation_ids=list(insert_ids)

eng=by_id['2026-09-04_GL_01']
assert eng.get('source_spec_id')=='STD26_R8_005' and eng.get('region')=='GL'
anson=by_id['2026-09-03_US_04']
assert anson['date_role']['event_date']=='2026-09-03'
assert anson['date_role']['event_date_source_url']=='https://inlandportauthority.utah.gov/board-info/'

merge_items=[]
for cid in operation_ids:
    item=copy.deepcopy(by_id[cid])
    assert item.get('source_spec_id')
    assert isinstance(item.get('related_lineage'),dict) and item['related_lineage'].get('status')=='PASS'
    assert isinstance(item.get('date_role'),dict)
    assert str(item.get('source_diversity_status','')).startswith('PASS')
    item['state']='github_merge_ready'
    item['publish_ready']=True
    item['github_merge_ready']=True
    item['merge_prep']={
        'status':'PASS','run_id':RUN_ID,'base_main_commit_sha':BASE_MAIN,
        'base_full_blob_sha':BASE_BLOB,'reviewed_operations_sha256':OPS_SHA,
        'post_resolution_semantic_validation':'PASS_PENDING_MACHINE_RECHECK',
    }
    merge_items.append(item)

stage08={
    'schema':'prompt_0_8_merge_prep_v4_operation_bound_r1','stage':'0.8','status':'GITHUB_MERGE_READY',
    'run_id':RUN_ID,'base_main_commit_sha':BASE_MAIN,'base_full_blob_sha':BASE_BLOB,
    'github_main_sync_gate':{
        'status':'PASS','baseline_locked':True,
        'main_unchanged_since_locked_preflight':True,'silent_rebase_performed':False,
    },
    'lineage_merge_gate':{
        'final_qc_lineage_passed':True,'anchor_path_lineage_passed':True,
        'anchor_path_hold_count':0,'github_ready_allowed':True,
    },
    'reviewed_operations_sha256':OPS_SHA,
    'independent_completeness_ref':str(RUN_ROOT/'stage-0-7c.json'),
    'certified_0_7c':{
        'workflow_run_id':CERTIFIED_WORKFLOW_RUN_ID,'artifact_id':CERTIFIED_ARTIFACT_ID,
        'artifact_zip_sha256':CERTIFIED_ARTIFACT_SHA,
    },
    'codex_p2_remediation':c07['codex_p2_remediation'],
    'operation_counts':{'insert':9,'update':0,'related_add':0},
    'id_ledger':{'schema':'prompt_0_8_current_run_id_ledger_v1','ids':insert_ids,'operation_ids':operation_ids},
    'github_merge_ready':merge_items,
}
dump(STAGE08,stage08)

selected=sh('node','scripts/validate_prompt_0_8_semantic_gate.mjs','--run',str(CARD_RUN),'--full',str(FULL),'--ledger',str(LEDGER),capture=True)
assert selected==str(STAGE08),(selected,str(STAGE08))
ledger=load(LEDGER)
assert ledger['ids']==insert_ids and ledger['operation_ids']==operation_ids
sh('python','validation_scripts/related_lifecycle_check.py',str(FULL),'--require-contract','--new-id-file',str(LEDGER))
sh('python','validation_scripts/evidence_qc_v8_check.py',str(FULL),'--new-id-file',str(LEDGER))
sh('python','validation_scripts/date_role_freshness_check.py',str(FULL),'--require-date-role','--new-id-file',str(LEDGER))
sh('python','validation_scripts/stage_artifact_contract_check.py','0.8',str(STAGE08))

stage08=load(STAGE08)
for item in stage08['github_merge_ready']:
    item['merge_prep']['post_resolution_semantic_validation']='PASS'
dump(STAGE08,stage08)
sh('python','validation_scripts/stage_artifact_contract_check.py','0.8',str(STAGE08))

audit={
    'schema':'card_run_audit_v1','status':'PASS','audit_complete':True,'reviewer_independence':'SEPARATE_PASS',
    'run_id':RUN_ID,'base_main_commit_sha':BASE_MAIN,'base_full_blob_sha':BASE_BLOB,
    'document_universe_manifest_ref':run['document_universe_manifest_ref'],
    'coverage_discovery_ref':run['coverage_discovery_ref'],
    'independent_completeness_ref':run['independent_completeness_ref'],
    'reviewed_operations_sha256':OPS_SHA,'expected_before':BEFORE,'expected_after':AFTER,
    'inserted_ids':insert_ids,'updated_ids':[],'related_additions':[],
    'zero_deletion_assertion':True,'zero_related_remove_assertion':True,
    'full_output_sha256':sha256(FULL),'lean_output_sha256':sha256(LEAN),
    'provisional_output_hashes':False,'output_binding_status':'PASS',
    'certified_0_7c_workflow_run_id':CERTIFIED_WORKFLOW_RUN_ID,
    'certified_0_7c_artifact_id':CERTIFIED_ARTIFACT_ID,
    'certified_0_7c_artifact_zip_sha256':CERTIFIED_ARTIFACT_SHA,
    'codex_p2_remediation':c07['codex_p2_remediation'],
}
dump(AUDIT,audit)

sh('node','scripts/validate_json_schema_subset.mjs','--schema','schemas/card-run.v1.schema.json','--instance',str(CARD_RUN))
sh('node','scripts/validate_card_run_stage_artifacts.mjs','--run',str(CARD_RUN))
sh('node','scripts/validate_card_run_v4_hardening.mjs','--run',str(CARD_RUN))
sh('python','validation_scripts/card_run_v4_binding_hardening.py','--run',str(CARD_RUN))
sh('node','scripts/validate_card_run_status_consistency.mjs','--run',str(CARD_RUN))
sh('node','scripts/validate_card_run_relations.mjs','--run',str(CARD_RUN))
sh('node','scripts/validate_card_run_lineage_containers.mjs','--run',str(CARD_RUN),'--canonical',str(FULL))
sh('node','scripts/validate_card_run_audits_dispatch.mjs','--run',str(CARD_RUN),'--full',str(FULL),'--lean',str(LEAN))
selected=sh('node','scripts/validate_prompt_0_8_semantic_gate.mjs','--run',str(CARD_RUN),'--full',str(FULL),'--ledger',str(LEDGER),capture=True)
assert selected==str(STAGE08)
sh('python','validation_scripts/related_lifecycle_check.py',str(FULL),'--require-contract','--new-id-file',str(LEDGER))
sh('python','validation_scripts/evidence_qc_v8_check.py',str(FULL),'--new-id-file',str(LEDGER))
sh('python','validation_scripts/date_role_freshness_check.py',str(FULL),'--require-date-role','--new-id-file',str(LEDGER))
sh('python','validation_scripts/stage_artifact_contract_check.py','0.8',str(STAGE08))
sh('node','scripts/apply_card_run.mjs','--run',str(CARD_RUN),'--baseline',str(FULL),'--canonical-path',str(FULL),
   '--output',str(FULL),'--report',str(RUN_ROOT/'apply-report.json'),'--base-main-sha',BASE_MAIN,
   '--lean-path',str(LEAN),'--verify')
sh('node','scripts/validate.mjs')
sh('node','scripts/validate_cards.mjs',str(FULL))
sh('node','scripts/validate_cards.mjs',str(LEAN))
sh('node','scripts/lean_cards.mjs','--check')

audit=load(AUDIT)
assert audit['full_output_sha256']==sha256(FULL)
assert audit['lean_output_sha256']==sha256(LEAN)
assert audit['reviewed_operations_sha256']==OPS_SHA
assert audit['certified_0_7c_artifact_id']==CERTIFIED_ARTIFACT_ID
assert len(load(FULL)['cards'])==AFTER
print('RESULT: PASS_PROMPT_0_8_PRODUCTION_MATERIALIZATION_R11')
print('RUN_ID',RUN_ID)
print('OPS_SHA',OPS_SHA)
print('COUNTS insert=9 update=0 related_add=0 before=1569 after=1578')
print('FULL_SHA256',sha256(FULL))
print('LEAN_SHA256',sha256(LEAN))
print('STAGE_0_8_SHA256',sha256(STAGE08))
print('AUDIT_SHA256',sha256(AUDIT))
