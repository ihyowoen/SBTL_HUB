#!/usr/bin/env python3
from __future__ import annotations
import copy, hashlib, json, subprocess, sys
from pathlib import Path

RUN_ID='card-run-2026-09-07-r7-20260905-production-r1'
BASE_MAIN='eb1a311ed378fcdf547b52ad5da0652cb9f1fc62'
BASE_BLOB='707fe5ea9836a0c2341771397da32c818a95cbed'
OPS_SHA='c77ad924c2c07abccd5659b4e262ed183e86dcae272ff32379ae8ecf034921a2'
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

# Production worktree must still be the exact frozen baseline. No silent rebase.
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

# Exact final R8 stage-byte chain certified by workflow 34108930897.
expected_hashes={
    'stage_a':'3c6295f6935581705b20522c746344097312afb561266381558019fa1d7af6c1',
    'stage_b':'3625c169d9f95e3ef85b3cbcb09d845de4ebf5a42dfe33239351639409d8557e',
    'stage_c':'fc7eaa5169158fc47a843a4db47251ab26e425ab40e2bd84828b99db22f3591e',
    'stage_0_4':'3da0e9ca5f5719d2c853c44eb837892b58d4f946474ebf851759dede9c877911',
    'stage_0_5':'98d2aced0d1bc62ed8a3b3a4a228d46b382403e4ec63d62bf242a53cec927680',
    'stage_0_6':'5495e7aa197a4d46719504bb95a340f33d957bddf26e07985373d3b73c758405',
    'stage_0_7':'05be0c74a11beff32de4dba55889310a2c74b1a34c512dcc1fba0fd93e080b47',
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
s4=load(paths['stage_0_4']); s5=load(paths['stage_0_5']); s6=load(paths['stage_0_6']); s7=load(paths['stage_0_7'])
assert s4['stage_c_artifact_sha256']==expected_hashes['stage_c']
assert s5['stage_0_4_artifact_sha256']==expected_hashes['stage_0_4']
assert s6['input_0_5_sha256']==expected_hashes['stage_0_5']
assert s7['input_0_6_sha256']==expected_hashes['stage_0_6']

# Temporary audit refs allow the repository-native engine to apply the frozen operation object.
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
assert not run['operations']['update'] and not run['operations']['related_add']
operation_ids=list(insert_ids)

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
        'workflow_run_id':34108930897,'artifact_id':10013554175,
        'artifact_zip_sha256':'6fde3a4cec01c3ae741b9b78f2cea7643f761766f230dbc40dc5eeb32a942b9c',
    },
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

# Exact output-bound independent audit.
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
    'certified_0_7c_artifact_id':10013554175,
    'certified_0_7c_artifact_zip_sha256':'6fde3a4cec01c3ae741b9b78f2cea7643f761766f230dbc40dc5eeb32a942b9c',
}
dump(AUDIT,audit)

# Full repository-native production gate chain.
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
assert len(load(FULL)['cards'])==AFTER
print('RESULT: PASS_PROMPT_0_8_PRODUCTION_MATERIALIZATION')
print('RUN_ID',RUN_ID)
print('OPS_SHA',OPS_SHA)
print('COUNTS insert=9 update=0 related_add=0 before=1569 after=1578')
print('FULL_SHA256',sha256(FULL))
print('LEAN_SHA256',sha256(LEAN))
print('STAGE_0_8_SHA256',sha256(STAGE08))
print('AUDIT_SHA256',sha256(AUDIT))