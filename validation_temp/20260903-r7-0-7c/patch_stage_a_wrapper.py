#!/usr/bin/env python3
import copy, json
from collections import Counter
from pathlib import Path

RUN_ID='card-run-2026-09-06-r7-20260903-production-r1'
MAIN='5317bec055b88a26cffb136e7844eb488ae4db0d'
BLOB='8b3d96b5c1fd779567ef8512f7123fc4310093ec'
ROOT=Path('runs/2026-09-06/r7-20260903-production-r1')
A_SRC=Path('/tmp/r7-stage-a-src/r7-stage-a-full/stage-a-b01.json')
P_SRC=Path('/tmp/r7-p01p-src/r7-p01p/stage-a-promotion13.json')
OUT=ROOT/'stages/stage-a.json'

base=json.loads(A_SRC.read_text(encoding='utf-8'))
promo=json.loads(P_SRC.read_text(encoding='utf-8'))
s07=json.loads((ROOT/'stages/stage-0-7.json').read_text(encoding='utf-8'))
ready=[x['source_spec_id'] for x in s07['publish_ready']]
ready_set=set(ready)
assert len(ready)==33 and len(ready_set)==33

specs={x['spec_id']:x for src in (base,promo) for x in src['strict_passed_spec']}
missing=[x for x in ready if x not in specs]
assert not missing, missing
strict=[copy.deepcopy(specs[x]) for x in ready]
ledger=[copy.deepcopy(x) for src in (base,promo) for x in src['decision_ledger'] if x.get('spec_id') in ready_set]
assert len(ledger)==45
assert {x['spec_id'] for x in ledger}==ready_set
assert {sid for s in strict for sid in s['source_story_ids']}=={x['story_id'] for x in ledger}
assert sum(1 for x in ready if x.startswith('STD26_R7_P01P_'))==12

def cid(x): return x.get('spec_id') or x.get('candidate_id') or x.get('source_event_id')
def count_list(field):
    c=Counter()
    for x in strict:
        for v in x.get(field,[]): c[v]+=1
    return dict(c)
def is_follow(x):
    if 'follow_up_probability_anchor' in (x.get('anchor_classes') or []): return True
    rel=(x.get('baseline_follow_up_relation') or '').strip().lower()
    return rel not in {'','new','new_unrelated','unrelated','not_applicable','none'}
def tech_app(x):
    return 'technology_commercialization_anchor' in (x.get('anchor_classes') or []) or 'technology_transition_commercialization' in (x.get('structural_value_lenses') or [])
def policy_app(x):
    return 'policy_regulatory_anchor' in (x.get('anchor_classes') or []) or any(('policy' in v or 'legal' in v) for v in (x.get('structural_value_lenses') or []) if isinstance(v,str))
LEGAL={
 'stage_0_rhetoric_or_advocacy','stage_1_roadmap_consultation_or_draft_standard','stage_2_bill_or_proposed_rule',
 'stage_3_enacted_law_final_rule_or_adopted_standard','stage_4_implementation_budget_guidance_or_registry',
 'stage_5_enforcement_payment_denial_penalty_or_recall','stage_6_judicial_or_tribunal_interpretation'
}

out=copy.deepcopy(base)
out.update({
 'stage':'stage_a','status':'PASS','run_id':RUN_ID,'base_main_commit_sha':MAIN,'base_full_blob_sha':BLOB,
 'run_tag':'20260906_R7_PRODUCTION33_STAGE_A_COMPOSITE',
 'run_label':'R7 production33 Stage A composite from machine-PASS Stage A + Prompt 0.1P artifacts',
 'input_file':'authoritative_event_universe_20260905_INPUT_20260903_MAIN_5317bec_R7.json',
 'baseline_source_declaration':f'current main {MAIN}; canonical blob {BLOB}; 1536 cards','baseline_count':1536,
 'github_main_sync_required_later':False,
 'source_universe':'45 source observations / 33 final strict Stage A specs filtered only from machine-PASS R7 Stage A and Prompt 0.1P artifacts.',
 'story_count':45,'event_count':33,'original_status_counts':dict(Counter(x.get('upstream_status') for x in ledger)),
 'recommended_for':['Stage B evidence package construction for strict_passed_spec[] only'],
 'legacy_keep':[],'strict_passed_spec':strict,'review_pool':[],'candidate_review_pool':[],'watchlist_context_pool':[],
 'reject_or_support_only_pool':[],'rejected':[],'existing_reinforcement':[],'support_source_only':[],'dropped_treasure_hunt_result':[],
 'review_pool_partition_summary':{'candidate_review_pool':0,'watchlist_context_pool':0,'reject_or_support_only_pool':0},
 'review_pool_carry_forward_ledger_status':'PASS','review_pool_resolution_ledger':[],'decision_ledger':ledger,
})
out['integrity_summary']=copy.deepcopy(base['integrity_summary'])
out['integrity_summary'].update({'status':'PASS','main_sha':MAIN,'canonical_blob_sha':BLOB,'source_stage_a_pass_run_id':33970279358,'source_p01p_pass_run_id':34013275047,'production_strict_event_count':33,'production_source_observation_count':45})
out['next_call_recommendation']={'recommended_next_call':'Stage B r0','recommended_prompt_id':'Prompt 0.2','recommended_input_universe':'Stage A strict_passed_spec[] only','reason':'33 production candidates are exact filtered rows from machine-PASS Stage A / Prompt 0.1P outputs.','blocked_items_summary':[]}
out['dropped_treasure_hunt']={'performed':False,'trigger_reason':'0.0C discovery was locked upstream; production composite performs no new selection or search.','sample_strategy':'not_applicable_at_production_composite','sample_size':0,'sampled_story_ids':[],'rescued_count':0,'rescue_ids':[],'non_sampled_dropped_count':0,'non_sampled_ledger_policy':'Every carried production observation is represented exactly once in the decision ledger.'}
s=copy.deepcopy(base['summary'])
s.update({
 'legacy_keep_count':0,'strict_passed_spec_count':33,'needs_review_count':0,'candidate_review_pool_count':0,'watchlist_context_pool_count':0,'reject_or_support_only_pool_count':0,
 'rejected_count':0,'existing_reinforcement_count':0,'support_source_only_count':0,'duplicate_or_reinforcement_count':0,'stale_discarded_count':0,'stale_warm_review_count':0,
 'total_ledger_count':45,'ledger_matches_story_count':True,'decision_ledger_count':45,
 'anchor_class_counts':count_list('anchor_classes'),'structural_lens_coverage_counts':count_list('structural_value_lenses'),
 'decision_value_classification_counts':dict(Counter(x.get('decision_value_classification') for x in strict)),
 'critical_structural_candidate_ids':[cid(x) for x in strict if x.get('decision_value_classification')=='critical_structural'],
 'high_decision_value_candidate_ids':[cid(x) for x in strict if x.get('decision_value_classification')=='high_decision_value'],
 'high_value_review_pool_ids':[],'structural_signal_review_pool_ids':[],'earnings_deep_dive_pool_ids':[],
 'follow_up_candidate_ids':[cid(x) for x in strict if is_follow(x)],'zero_coverage_domains':[],'execution_or_formality_bias_findings':[],
 'technology_validation_gap_ids':[cid(x) for x in strict if tech_app(x) and isinstance(x.get('technology_validation_gap'),str) and x['technology_validation_gap'].strip()],
 'legal_policy_stage_gap_ids':[cid(x) for x in strict if policy_app(x) and x.get('legal_policy_stage') not in LEGAL],
 'selection_route_counts':dict(Counter(x.get('selection_route') for x in strict)),'formal_event_count':33,'source_bound_observation_count':45,
})
out['summary']=s
OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('RESULT: MATERIALIZED_FULL_STAGE_A_PRODUCTION33 events=33 stories=45 strict=33 original=21 promoted=12')