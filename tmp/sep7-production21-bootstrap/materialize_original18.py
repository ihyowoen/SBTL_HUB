#!/usr/bin/env python3
import collections, copy, hashlib, json, pathlib, sys

R7_SHA='0d9679a136a92d395f1c99f432ce35342e28d5f231294afd5ad77f2a03299bd9'
OUT_SHA='c22411c32b70b52f4cb4f978186cff66ecf7e630eafee018dc32499c833c1d8f'
MAIN='aa7400ae67b221d1ddd5e198293762caec389303'
BLOB='920646b6b335f211bcd224962f8ac0cc42cd3a4f'
SURVIVORS=[
'STD26_0907_A_001','STD26_0907_A_002','STD26_0907_A_003','STD26_0907_A_005','STD26_0907_A_006',
'STD26_0907_A_007','STD26_0907_A_008','STD26_0907_A_009','STD26_0907_A_010','STD26_0907_A_015',
'STD26_0907_A_017','STD26_0907_A_018','STD26_0907_A_019','STD26_0907_A_023','STD26_0907_A_024',
'STD26_0907_A_025','STD26_0907_A_026','STD26_0907_A_027']

src=pathlib.Path(sys.argv[1]); out=pathlib.Path(sys.argv[2])
if hashlib.sha256(src.read_bytes()).hexdigest()!=R7_SHA: raise SystemExit('R7 SHA mismatch')
r7=json.loads(src.read_text())
proj=copy.deepcopy(r7)
sidset=set(SURVIVORS)
specs=[x for x in r7['strict_passed_spec'] if x.get('spec_id') in sidset]
if [x.get('spec_id') for x in specs] != SURVIVORS: raise SystemExit('survivor strict order/coverage mismatch')
story_ids=[]
for s in specs: story_ids.extend(s.get('source_story_ids',[]))
if len(story_ids)!=50 or len(set(story_ids))!=50: raise SystemExit('strict18 story accounting mismatch')
story_set=set(story_ids)
ledger=[x for x in r7['decision_ledger'] if x.get('story_id') in story_set]
if len(ledger)!=50 or {x.get('story_id') for x in ledger}!=story_set: raise SystemExit('strict18 ledger mismatch')

proj['run_tag']='20260908_SEP7_R7_CURRENT_MAIN_STRICT18_PROJECTION'
proj['run_label']='Sep 7 R7 strict18 survivor operation projection on current main'
proj['baseline_source_declaration']=f'current main {MAIN}; canonical blob {BLOB}; 1578 cards'
proj['baseline_count']=1578
proj['source_universe']='50 source observations belonging to 18 current-main-surviving strict events, projected from exact R7.'
proj['story_count']=50
proj['event_count']=18
proj['original_status_counts']={'kept':50}
proj['integrity_summary']={
    'status':'PASS','main_sha':MAIN,'canonical_blob_sha':BLOB,'source_observation_count':50,
    'authoritative_event_count':18,
    'projection':'strict18 survivor projection from exact R7; full 263-observation accounting retained in source R7 proof',
    'source_stage_a_r7_sha256':R7_SHA,
}
proj['strict_passed_spec']=specs
for key in ['legacy_keep','review_pool','candidate_review_pool','watchlist_context_pool','reject_or_support_only_pool','review_pool_resolution_ledger','rejected','existing_reinforcement','support_source_only','dropped_treasure_hunt_result']:
    proj[key]=[]
proj['review_pool_partition_summary']={'candidate_review_pool':0,'watchlist_context_pool':0,'reject_or_support_only_pool':0}
proj['decision_ledger']=ledger
proj['dropped_treasure_hunt']={
    'performed':False,
    'trigger_reason':'Full 263-observation accounting remains preserved in exact R7 run-level proof; this is a strict-survivor operation projection.',
    'sample_strategy':'not_applicable_projection','sample_size':0,'sampled_story_ids':[],
    'rescued_count':0,'rescue_ids':[],'non_sampled_dropped_count':0,
    'non_sampled_ledger_policy':'Every source story in this strict-survivor projection is represented exactly once in decision_ledger.'
}
proj['stage_b_authorized']=True
proj['next_call_recommendation']={
    'recommended_next_call':'Stage B r0','recommended_prompt_id':'Prompt 0.2',
    'recommended_input_universe':'Stage A strict_passed_spec[] only',
    'reason':'18 current-main-surviving strict items retain complete validated Stage A R7 lineage and are authorized for Stage B.',
    'blocked_items_summary':[],'pending_parallel_or_followup_call':'none','pending_prompt_id':'not_applicable',
    'pending_input_universe':'none','pending_reason':'Prompt 0.1P is materialized separately for its three promoted strict items.'
}
summary=copy.deepcopy(r7['summary'])
summary.update({
    'legacy_keep_count':0,'strict_passed_spec_count':18,'strict_source_observation_count':50,
    'candidate_review_pool_count':0,'candidate_review_source_observation_count':0,
    'watchlist_context_pool_count':0,'watchlist_source_observation_count':0,
    'reject_or_support_only_pool_count':0,'reject_or_support_source_observation_count':0,
    'existing_reinforcement_count':0,'existing_reinforcement_source_observation_count':0,
    'existing_update_candidate_count':0,'total_event_count':18,'total_ledger_count':50,'ledger_matches_story_count':True,
    'decision_ledger_count':50,'formal_event_count':18,'source_bound_observation_count':50,
    'needs_review_count':0,'rejected_count':0,'support_source_only_count':0,'duplicate_or_reinforcement_count':0,
    'stale_discarded_count':0,'stale_warm_review_count':0,'high_value_review_pool_ids':[],
    'structural_signal_review_pool_ids':[],'earnings_deep_dive_pool_ids':[],
    'zero_coverage_domains':[],'execution_or_formality_bias_findings':[],
})
anchors=collections.Counter(); lenses=collections.Counter(); classes=collections.Counter(); routes=collections.Counter()
for s in specs:
    anchors.update(s.get('anchor_classes',[])); lenses.update(s.get('structural_value_lenses',[]))
    classes.update([s.get('decision_value_classification')]); routes.update([s.get('selection_route')])
summary['anchor_class_counts']=dict(sorted(anchors.items()))
summary['structural_lens_coverage_counts']=dict(sorted(lenses.items()))
summary['decision_value_classification_counts']=dict(sorted(classes.items()))
summary['selection_route_counts']=dict(sorted(routes.items()))
summary['critical_structural_candidate_ids']=[s['spec_id'] for s in specs if s.get('decision_value_classification')=='critical_structural']
summary['high_decision_value_candidate_ids']=[s['spec_id'] for s in specs if s.get('decision_value_classification')=='high_decision_value']
summary['material_industry_signal_candidate_ids']=[s['spec_id'] for s in specs if s.get('decision_value_classification')=='material_industry_signal']
for key in ['follow_up_candidate_ids','technology_validation_gap_ids','legal_policy_stage_candidate_ids','legal_policy_stage_gap_ids']:
    summary[key]=[x for x in r7['summary'].get(key,[]) if x in sidset]
proj['summary']=summary
out.write_text(json.dumps(proj,ensure_ascii=False,indent=2)+'\n')
actual=hashlib.sha256(out.read_bytes()).hexdigest()
if actual!=OUT_SHA: raise SystemExit(f'projection SHA mismatch {actual}')
print(f'PASS strict18 projection sha256={actual} story_count=50 strict_count=18')
