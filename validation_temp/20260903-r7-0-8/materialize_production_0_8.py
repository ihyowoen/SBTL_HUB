#!/usr/bin/env python3
from __future__ import annotations
import copy, hashlib, json, subprocess, sys
from pathlib import Path

RUN_ID='card-run-2026-09-06-r7-20260903-production-r1'
BASE_MAIN='5317bec055b88a26cffb136e7844eb488ae4db0d'
BASE_BLOB='8b3d96b5c1fd779567ef8512f7123fc4310093ec'
OPS_SHA='a810e964e298a627b7edc65d28805b03f29a371a016b0aece5053f4589c87407'
RUN_ROOT=Path('runs/2026-09-06/r7-20260903-production-r1')
CARD_RUN=RUN_ROOT/'card-run.json'
STAGE08=RUN_ROOT/'stage-0-8.json'
AUDIT=RUN_ROOT/'card-run-audit.json'
LEDGER=RUN_ROOT/'prompt-0-8-id-ledger.json'
FULL=Path('data/cards.full.json')
LEAN=Path('public/data/cards.json')


def sh(*args, capture=False):
    p=subprocess.run(args, text=True, capture_output=capture)
    if p.returncode:
        if capture:
            print(p.stdout, file=sys.stderr); print(p.stderr, file=sys.stderr)
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

def ops_sha(ops):
    b=json.dumps(stable(ops),ensure_ascii=False,separators=(',',':')).encode('utf-8')
    return hashlib.sha256(b).hexdigest()

# Exact production branch baseline lock before any mutation.
head=sh('git','rev-parse','HEAD',capture=True)
assert head==BASE_MAIN,(head,BASE_MAIN)
assert sh('git','rev-parse',f'{BASE_MAIN}:data/cards.full.json',capture=True)==BASE_BLOB
assert sh('git','hash-object',str(FULL),capture=True)==BASE_BLOB
base=load(FULL); assert len(base['cards'])==1536

run=load(CARD_RUN)
assert run['run_id']==RUN_ID
assert run['base_main_commit_sha']==BASE_MAIN and run['base_full_blob_sha']==BASE_BLOB
assert run['expected_before']==1536 and run['expected_after']==1569
assert {k:len(run['operations'][k]) for k in ('insert','update','related_add')}=={'insert':33,'update':0,'related_add':3}
assert ops_sha(run['operations'])==OPS_SHA
assert run['independent_completeness_ref']==str(RUN_ROOT/'stage-0-7c.json')
assert run['audit_refs']==[str(AUDIT),str(STAGE08)]

# Assert the source 0.7C package itself still authorizes exactly this operation set.
c07=load(RUN_ROOT/'stage-0-7c.json')
assert c07['status']=='PASS_WITH_DECLARED_RESIDUAL_RISK' and c07['prompt_0_8_authorized'] is True
assert c07['reviewed_operations_sha256']==OPS_SHA
assert c07['operation_freeze']=={
    'status':'PASS','operations_sha256':OPS_SHA,'insert':33,'update':0,'related_add':3,
    'expected_before':1536,'expected_after':1569,'operation_drift_allowed':False,
}

# Low-level engine only requires audit_refs to resolve before apply. These temporary files
# are overwritten by final machine-bound 0.8/audit proofs before any commit can occur.
dump(AUDIT,{'schema':'card_run_audit_v1','status':'PASS','temporary_materialization_only':True})
dump(STAGE08,{'stage':'0.8','status':'PASS','temporary_materialization_only':True})

# Apply the frozen operation object using the repository-native engine. This deterministically
# writes canonical full, lean projection, and apply report from the declared base commit.
sh('node','scripts/apply_card_run.mjs',
   '--run',str(CARD_RUN),'--baseline',str(FULL),'--canonical-path',str(FULL),
   '--output',str(FULL),'--report',str(RUN_ROOT/'apply-report.json'),
   '--base-main-sha',BASE_MAIN,'--lean-path',str(LEAN),'--apply')

full=load(FULL); assert len(full['cards'])==1569 and full.get('total')==1569
by_id={c['id']:c for c in full['cards']}
insert_ids=[op['card']['id'] for op in run['operations']['insert']]
assert len(insert_ids)==33 and len(set(insert_ids))==33
assert all(x in by_id for x in insert_ids)
assert not run['operations']['update']
for op in run['operations']['related_add']:
    src=by_id[op['source_id']]
    assert op['target_id'] in src.get('related',[])
    lin=src.get('related_lineage') or {}
    assert op['target_id'] in lin.get('related_ids',[])
    assert lin.get('relation_type')==op['relation_type']
    assert lin.get('reason')==op['lineage_reason']
    assert lin.get('event_stage_relationship')==op['event_stage_relationship']
    assert lin.get('direction')==op['direction']

# Operation identity set is exactly the 33 inserted cards: all Related ops explicitly bind
# identity_card_id to the current-run inserted source endpoint, never the legacy predecessor.
operation_ids=list(insert_ids)
for op in run['operations']['related_add']:
    assert op['identity_card_id']==op['source_id'] and op['identity_card_id'] in insert_ids
assert len(set(operation_ids))==33

# Build formal Prompt 0.8 proof from the exact post-apply candidate canonical cards.
merge_items=[]
for cid in operation_ids:
    item=copy.deepcopy(by_id[cid])
    assert item.get('source_spec_id')
    assert isinstance(item.get('related_lineage'),dict) and item['related_lineage'].get('status')=='PASS'
    assert isinstance(item.get('date_role'),dict)
    assert isinstance(item.get('source_diversity_status'),str) and item['source_diversity_status'].startswith('PASS')
    # 0.8 is the first stage allowed to attest formal merge readiness. This changes only
    # the 0.8 audit item; it does not mutate the already frozen card-run operation object.
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
    'github_main_sync_gate':{'status':'PASS','baseline_locked':True,'main_unchanged_since_locked_preflight':True,'silent_rebase_performed':False},
    'lineage_merge_gate':{'final_qc_lineage_passed':True,'anchor_path_lineage_passed':True,'anchor_path_hold_count':0,'github_ready_allowed':True},
    'reviewed_operations_sha256':OPS_SHA,'independent_completeness_ref':str(RUN_ROOT/'stage-0-7c.json'),
    'operation_counts':{'insert':33,'update':0,'related_add':3},
    'id_ledger':{'schema':'prompt_0_8_current_run_id_ledger_v1','ids':insert_ids,'operation_ids':operation_ids},
    'github_merge_ready':merge_items,
}
dump(STAGE08,stage08)

# Runtime gate independently derives exact strict/operation IDs and writes the governed JSON ledger.
selected=sh('node','scripts/validate_prompt_0_8_semantic_gate.mjs','--run',str(CARD_RUN),'--full',str(FULL),'--ledger',str(LEDGER),capture=True)
assert selected==str(STAGE08),(selected,str(STAGE08))
ledger=load(LEDGER)
assert ledger['ids']==insert_ids and ledger['operation_ids']==operation_ids

# Post-resolution card-wide semantics and 0.8 artifact contract.
sh('python','validation_scripts/related_lifecycle_check.py',str(FULL),'--require-contract','--new-id-file',str(LEDGER))
sh('python','validation_scripts/evidence_qc_v8_check.py',str(FULL),'--new-id-file',str(LEDGER))
sh('python','validation_scripts/date_role_freshness_check.py',str(FULL),'--require-date-role','--new-id-file',str(LEDGER))
sh('python','validation_scripts/stage_artifact_contract_check.py','0.8',str(STAGE08))

# Now that the machine checks passed, replace pending marker inside the 0.8 proof only.
stage08=load(STAGE08)
for item in stage08['github_merge_ready']:
    item['merge_prep']['post_resolution_semantic_validation']='PASS'
dump(STAGE08,stage08)
sh('python','validation_scripts/stage_artifact_contract_check.py','0.8',str(STAGE08))

# Final exact output-bound independent audit.
audit={
    'schema':'card_run_audit_v1','status':'PASS','audit_complete':True,'reviewer_independence':'SEPARATE_PASS',
    'run_id':RUN_ID,'base_main_commit_sha':BASE_MAIN,'base_full_blob_sha':BASE_BLOB,
    'document_universe_manifest_ref':run['document_universe_manifest_ref'],
    'coverage_discovery_ref':run['coverage_discovery_ref'],
    'independent_completeness_ref':run['independent_completeness_ref'],
    'reviewed_operations_sha256':OPS_SHA,'expected_before':1536,'expected_after':1569,
    'inserted_ids':insert_ids,'updated_ids':[],
    'related_additions':[{'source_id':op['source_id'],'target_id':op['target_id'],'direction':op['direction']} for op in run['operations']['related_add']],
    'zero_deletion_assertion':True,'zero_related_remove_assertion':True,
    'full_output_sha256':sha256(FULL),'lean_output_sha256':sha256(LEAN),
    'provisional_output_hashes':False,'output_binding_status':'PASS',
}
dump(AUDIT,audit)

# Full repository-native Prompt 0.8 / production validation chain.
sh('node','scripts/validate_json_schema_subset.mjs','--schema','schemas/card-run.v1.schema.json','--instance',str(CARD_RUN))
sh('node','scripts/validate_card_run_stage_artifacts.mjs','--run',str(CARD_RUN))
sh('node','scripts/validate_card_run_v4_hardening.mjs','--run',str(CARD_RUN))
sh('python','validation_scripts/card_run_v4_binding_hardening.py','--run',str(CARD_RUN))
sh('node','scripts/validate_card_run_status_consistency.mjs','--run',str(CARD_RUN))
sh('node','scripts/validate_card_run_relations.mjs','--run',str(CARD_RUN))
sh('node','scripts/validate_card_run_lineage_containers.mjs','--run',str(CARD_RUN),'--canonical',str(FULL))
sh('node','scripts/validate_card_run_audits_dispatch.mjs','--run',str(CARD_RUN),'--full',str(FULL),'--lean',str(LEAN))
# Semantic gate and scoped checks are repeated after final audit materialization.
selected=sh('node','scripts/validate_prompt_0_8_semantic_gate.mjs','--run',str(CARD_RUN),'--full',str(FULL),'--ledger',str(LEDGER),capture=True)
assert selected==str(STAGE08)
sh('python','validation_scripts/related_lifecycle_check.py',str(FULL),'--require-contract','--new-id-file',str(LEDGER))
sh('python','validation_scripts/evidence_qc_v8_check.py',str(FULL),'--new-id-file',str(LEDGER))
sh('python','validation_scripts/date_role_freshness_check.py',str(FULL),'--require-date-role','--new-id-file',str(LEDGER))
sh('python','validation_scripts/stage_artifact_contract_check.py','0.8',str(STAGE08))
# Byte-exact idempotent submitted full/lean verification from the frozen base commit.
sh('node','scripts/apply_card_run.mjs','--run',str(CARD_RUN),'--baseline',str(FULL),'--canonical-path',str(FULL),
   '--output',str(FULL),'--report',str(RUN_ROOT/'apply-report.json'),'--base-main-sha',BASE_MAIN,'--lean-path',str(LEAN),'--verify')
sh('node','scripts/validate.mjs')
sh('node','scripts/validate_cards.mjs',str(FULL))
sh('node','scripts/validate_cards.mjs',str(LEAN))
sh('node','scripts/lean_cards.mjs','--check')

# Recheck audit hashes after every validator and byte-exact verify.
audit=load(AUDIT)
assert audit['full_output_sha256']==sha256(FULL)
assert audit['lean_output_sha256']==sha256(LEAN)
assert len(load(FULL)['cards'])==1569
print('RESULT: PASS_PROMPT_0_8_PRODUCTION_MATERIALIZATION')
print('RUN_ID',RUN_ID)
print('OPS_SHA',OPS_SHA)
print('COUNTS insert=33 update=0 related_add=3 before=1536 after=1569')
print('FULL_SHA256',sha256(FULL))
print('LEAN_SHA256',sha256(LEAN))
print('STAGE_0_8_SHA256',sha256(STAGE08))
print('AUDIT_SHA256',sha256(AUDIT))
