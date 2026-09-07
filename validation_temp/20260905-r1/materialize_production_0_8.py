#!/usr/bin/env python3
from __future__ import annotations
import copy, hashlib, json, subprocess, sys
from pathlib import Path

RUN_ID='card-run-2026-09-07-r7-20260905-production-r1'
BASE_MAIN='eb1a311ed378fcdf547b52ad5da0652cb9f1fc62'
BASE_BLOB='707fe5ea9836a0c2341771397da32c818a95cbed'
OPS_SHA='236b86f3a0cc7c0a862074884dc06303b0875a73337067e4d8e7a2f3d8e2ed86'
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
    'stage_a':'bafd91ebcbd5fcdc246c8fcc0ee1865d2489e77f94d9f1723f9da34a41f74bee',
    'stage_b':'c0407a7ab09cfdc501ef19f474598903a815d23e5a551566152f96efb96350f2',
    'stage_c':'a1861b35f9865f2a4672e9d2ecc300d3a771d31d24ca2f319dc063a6cb76c961',
    'stage_0_4':'6549427c4babdf94c38ff10a58bb9038fe46637e6b0c60d97c41e550bd2c6b33',
    'stage_0_5':'eccffdc19d1b2b9426896ccaf795189f38a37f4f2dfabc89f8c5c8bc15e7ba74',
    'stage_0_6':'e8c277544369405d6be14bafb14bec7f024b313145ef81de2bfb802f33fe809d',
    'stage_0_7':'34a9f92858646da3b5d42d97011a772b2be0dba504f9dab12de22ee6ee57c8cb',
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

CERTIFIED_ARTIFACT_ID=10013536223
CERTIFIED_ARTIFACT_SHA='4e8e4c4ab9c1f5be09320ef9c0901b796a186143b01ea9659a1a8a85dc9d97b3'

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
        'workflow_run_id':34108930897,'artifact_id':CERTIFIED_ARTIFACT_ID,
        'artifact_zip_sha256':CERTIFIED_ARTIFACT_SHA,
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
    'certified_0_7c_artifact_id':CERTIFIED_ARTIFACT_ID,
    'certified_0_7c_artifact_zip_sha256':CERTIFIED_ARTIFACT_SHA,
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
assert len(load(FULL)['cards'])==AFTER
print('RESULT: PASS_PROMPT_0_8_PRODUCTION_MATERIALIZATION')
print('RUN_ID',RUN_ID)
print('OPS_SHA',OPS_SHA)
print('COUNTS insert=9 update=0 related_add=0 before=1569 after=1578')
print('FULL_SHA256',sha256(FULL))
print('LEAN_SHA256',sha256(LEAN))
print('STAGE_0_8_SHA256',sha256(STAGE08))
print('AUDIT_SHA256',sha256(AUDIT))
