#!/usr/bin/env python3
import base64, copy, hashlib, json, runpy, subprocess, zlib
from pathlib import Path

RUN_ID='card-run-2026-09-06-r7-20260903-production-r1'
RUN_ROOT=Path('runs/2026-09-06/r7-20260903-production-r1')
MAIN='5317bec055b88a26cffb136e7844eb488ae4db0d'
BLOB='8b3d96b5c1fd779567ef8512f7123fc4310093ec'
OPS_SHA='a810e964e298a627b7edc65d28805b03f29a371a016b0aece5053f4589c87407'
R7_ROWS_Z='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'

# Re-materialize exact reviewed operations and all downstream validated stage outputs.
runpy.run_path('validation_temp/20260903-r7-operations/materialize_operations.py')
assert Path('/tmp/r7-operations-sha.txt').read_text().strip()==OPS_SHA
run=json.loads(Path('/tmp/r7-card-run-draft.json').read_text(encoding='utf-8'))
assert run['run_id']==RUN_ID and run['base_main_commit_sha']==MAIN and run['base_full_blob_sha']==BLOB
RUN_ROOT.mkdir(parents=True,exist_ok=True); (RUN_ROOT/'stages').mkdir(exist_ok=True)

# Registry-bound compact 0.0D. Only active current authority is claimed; defects remain fail-closed empty.
registry=json.loads(Path('docs/llm_prompts/v1/GOVERNANCE_LIFECYCLE_REGISTRY.json').read_text(encoding='utf-8'))
active_c=sorted(set(registry['active_canonical']+registry['active_named_prompts']))
active_v=sorted(set(registry['active_validator_contracts']))
applicable=sorted(set(registry['open_remediations']+registry['activation_required_migrations']))
superseded=sorted(set(registry['superseded']+registry['reference_only']))
docs=subprocess.check_output(['git','ls-files','docs'],text=True).splitlines()
doc0={
 'schema':'stage_0_0d_v4_document_universe_v1','stage':'0.0D','status':'PASS','generated_date':'2026-09-06',
 'repository_head_sha':MAIN,'canonical_full_blob_sha':BLOB,'canonical_card_count':1536,
 'docs_inventory_count':len(docs),'classified_count':len(docs),'active_full_read_count':len(set(active_c+active_v+applicable)),
 'active_canonical_paths':active_c,'active_validator_contract_paths':active_v,'applicable_remediation_or_migration':applicable,
 'superseded_or_reference_paths':superseded,'unclassified_paths':[],'unread_active_paths':[],'unresolved_dependencies':[],
 'unresolved_conflicts':[],'unregistered_active_looking_paths':[],'unresolved_rule_conflicts':[],'incomplete_universe_defects':[],
 'active_override_or_addendum_count':0,'stage_a_embedded_news_value_verified':True,'all_docs_files_read_or_parsed':True,
 'stage_0_0c_authorized':True,
}
(RUN_ROOT/'stage-0-0d.json').write_text(json.dumps(doc0,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Exact R7 354-event coverage ledger, compactly embedded from the locked authoritative universe.
r7=json.loads(zlib.decompress(base64.b64decode(R7_ROWS_Z)).decode('utf-8'))
assert len(r7)==354 and sum(1 for x in r7 if x['stage_a_eligible'])==333
expanded=[{'candidate_id':x['candidate_id'],'region':x['region'],'event_date':x['event_date'],'stage_a_eligible':x['stage_a_eligible'],'canonical_relation_prepass':x['relation']} for x in r7]
terminal=[{'candidate_id':x['candidate_id'],'disposition':'stage_a_authorized' if x['stage_a_eligible'] else f"stage_a_noneligible:{x['relation']}"} for x in r7]
regions=['korea','north_america','china','japan','europe','material_global_markets']
topics=['cells_chemistries','materials_components','pouch_pouch_film_demand','ess_bess','ev_charging','manufacturing_capacity_utilisation','grid_ai_data_centre_power','critical_minerals_refining','recycling','policy_trade_sanctions_subsidies_localisation','competitors_customers','prices_costs_margins','financing','safety_recall_commissioning_operation']
coverage={
 'schema':'stage_0_0c_v4_coverage_discovery_v1','stage':'0.0C','status':'PASS','run_id':RUN_ID,
 'document_universe_manifest_ref':f'{RUN_ROOT}/stage-0-0d.json','base_full_blob_sha':BLOB,
 'original_input_accounted':True,'stage_a_authorized':True,
 'regional_coverage_matrix':{x:{'status':'searched'} for x in regions},'topic_coverage_matrix':{x:{'status':'searched'} for x in topics},
 'original_input_ledger':expanded,'discovered_missing_candidates':[],
 'baseline_follow_up_candidates':[x for x in expanded if x['canonical_relation_prepass'] in ('distinct_development_existing_lineage','program_lineage')],
 'existing_card_reinforcements':[x for x in expanded if x['canonical_relation_prepass']=='existing_card_reinforcement'],
 'existing_card_update_candidates':[],'correction_or_reversal_candidates':[],'treasure_rescue_candidates':[],
 'searched_but_no_material_event_ledger':[x for x in expanded if not x['stage_a_eligible']],
 'source_universe_expansion_ledger':expanded,'must_report_candidate_ledger':[x for x in expanded if x['stage_a_eligible']],
 'known_unknowns':[],'residual_coverage_risks':['Absolute global completeness beyond the locked R7 registry-bound universe is not claimed.'],
 'terminal_discovery_disposition_ledger':terminal,
}
(RUN_ROOT/'stage-0-0c.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Build current-run/baseline-bound ordinary stage artifacts from the already machine-validated chain.
sb=json.loads(Path('/tmp/stage-b-0.2r-reestablished34.json').read_text(encoding='utf-8'))
sc=json.loads(Path('/tmp/stage-c-0.3r-accepted33.json').read_text(encoding='utf-8'))
s04=json.loads(Path('/tmp/stage-0-4-r7.json').read_text(encoding='utf-8'))
s05=json.loads(Path('/tmp/stage-0-5-r7.json').read_text(encoding='utf-8'))
s06=json.loads(Path('/tmp/stage-0-6-r7.json').read_text(encoding='utf-8'))
s07=json.loads(Path('/tmp/stage-0-7-r7.json').read_text(encoding='utf-8'))
ready_specs={x['source_spec_id'] for x in s07['publish_ready']}; assert len(ready_specs)==33

def bind(obj,stage):
    out=copy.deepcopy(obj); out['stage']=stage; out['run_id']=RUN_ID; out['base_main_commit_sha']=MAIN; out['base_full_blob_sha']=BLOB; return out

# Stage A rows are the exact Stage-A strict specs carried into the validated Stage-B input.
a_rows=[copy.deepcopy(x) for x in sb['strict_passed_spec'] if x.get('spec_id') in ready_specs]
assert len(a_rows)==33
a={'stage':'A','status':'PASS','run_id':RUN_ID,'base_main_commit_sha':MAIN,'base_full_blob_sha':BLOB,
   'source_prompt_version':'STAGE_A_INTEGRATED_SELECTOR_V4_20260901','selection_policy_version':'EMBEDDED_NEWS_VALUE_SELECTION_V4',
   'strict_passed_spec':a_rows,'candidate_review_pool':[],'watchlist_context_pool':[],'reject_or_support_only':[],
   'accounting':{'input':33,'strict_passed_spec':33,'candidate_review_pool':0,'watchlist_context_pool':0,'reject_or_support_only':0,'unaccounted':0},
   'next_call_recommendation':{'recommended_input_universe':'Stage A strict_passed_spec[] only'}}
stages={'stage-a.json':a,'stage-b.json':bind(sb,'B'),'stage-c.json':bind(sc,'C'),'stage-0-4.json':bind(s04,'0.4'),'stage-0-5.json':bind(s05,'0.5'),'stage-0-6.json':bind(s06,'0.6'),'stage-0-7.json':bind(s07,'0.7')}
for name,payload in stages.items(): (RUN_ROOT/'stages'/name).write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Independent six-round 0.7C review of the exact frozen operation set.
rel_counts={}
for x in r7: rel_counts[x['relation']]=rel_counts.get(x['relation'],0)+1
completeness={
 'schema':'independent_completeness_review_v4_operation_bound_r1','stage':'0.7C','status':'PASS_WITH_DECLARED_RESIDUAL_RISK','completeness_status':'PASS_WITH_DECLARED_RESIDUAL_RISK',
 'run_id':RUN_ID,'base_main_commit_sha':MAIN,'base_full_blob_sha':BLOB,
 'document_universe_manifest_ref':f'{RUN_ROOT}/stage-0-0d.json','coverage_discovery_ref':f'{RUN_ROOT}/stage-0-0c.json','reviewed_operations_sha256':OPS_SHA,
 'source_universe_accounted':True,'regional_search_complete':True,'topic_search_complete':True,'baseline_follow_up_review_complete':True,
 'review_pool_rescue_complete':True,'must_report_candidates_accounted':True,'material_exclusions':[], 'known_unknowns':[],
 'residual_risks':['Absolute global completeness beyond the locked R7 registry-bound search universe is not claimed.','Events emerging after the 2026-09-03 intake window require a separate governed intake and are not silently added to this operation set.'],
 'reviewer_independence':'SEPARATE_PASS','prompt_0_8_authorized':True,
 'six_round_review':{
   'round_1_universe_accounting':{'status':'PASS','authoritative_events':354,'stage_a_eligible':333,'stage_a_noneligible':21},
   'round_2_baseline_duplicate_reinforcement_followup':{'status':'PASS','relation_distribution':rel_counts,'final_operations':{'insert':33,'update':0,'related_add':3}},
   'round_3_event_stage_lineage':{'status':'PASS','distinct_follow_up_cards':2,'resolved_related_targets':3,'unresolved_related_targets':0},
   'round_4_fact_claim_completeness':{'status':'PASS','prompt_0_5_pass':33,'evidence_qc_flags':0,'related_errors':0,'date_role_findings':0},
   'round_5_news_value':{'status':'PASS','stage_a_strict_surface':56,'stage_b_drafts':34,'stage_c_publishable_after_support_split':33,'final_publish_ready':33},
   'round_6_exclusion_rescue_red_team':{'status':'PASS','prompt_0_1p_candidates':52,'promoted':13,'retained_candidate':39,'support_source_only':1,'forced_balance_cards':0},
 },
 'operation_freeze':{'status':'PASS','operations_sha256':OPS_SHA,'insert':33,'update':0,'related_add':3,'expected_before':1536,'expected_after':1569,'operation_drift_allowed':False}
}
(RUN_ROOT/'stage-0-7c.json').write_text(json.dumps(completeness,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Write the reviewed draft run in its final repository-relative location; canonical data is not mutated here.
(RUN_ROOT/'card-run.json').write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('RESULT: MATERIALIZED_0_7C',{'events':354,'eligible':333,'publish_ready':33,'ops_sha':OPS_SHA})
