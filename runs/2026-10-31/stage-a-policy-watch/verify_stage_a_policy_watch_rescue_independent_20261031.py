#!/usr/bin/env python3
"""Independent QC: primary bounded cohort schema and original 1,330 identity, NOT native PASS."""
import hashlib,json,collections,copy,sys
from pathlib import Path
root=Path(__file__).resolve().parent
names={
 'baseline':'STAGE_A_1330_SOURCE_INTEGRATED_EVIDENCE_OVERLAY_V4_20261030.json',
 'prior':'STAGE_A_LAST16_FOUR_JUDGMENTS_PRE_NATIVE_20261031.json',
 'batch':'STAGE_A_0_1P_POLICY_MARKET_WATCH_RESCUE_CASES_20261031.json',
 'overlay':'STAGE_A_1330_SOURCE_INTEGRATED_EVIDENCE_OVERLAY_V5_POLICY_WATCH_20261031.json'}
expected={'baseline':'0646b280eac1963e6889410529d1b1f92a2b485077982677527612c176201104',
 'prior':'1faf426f340e8c8c2bd2570c6d84697cd062397e25bee478c2e139b2aba2cb1e'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
d={n:json.loads((root/f).read_text()) for n,f in names.items()}
for n,h in expected.items():assert sha(root/names[n])==h,(n,'input hash drift')
b=d['baseline'];p=d['prior'];w=d['batch'];v=d['overlay']
assert b['original_csv_sha256']==w['original_csv_sha256']=='5e78420916b0c1d70ff56bf928779cd969b94fbb15dd4119c841872997486116'
assert w['previous16_sha256']==sha(root/names['prior'])
assert w['parent_v4_sha256']==v['parent_v4_sha256']==sha(root/names['baseline'])
assert v['oct31_policy_watch_source_judgments_sha256']==sha(root/names['batch'])
a=b['source_rows'];c=v['source_rows'];assert len(a)==len(c)==1330
assert len(set(x['candidate_id'] for x in a))==1330
assert [x['candidate_id'] for x in a]==[x['candidate_id'] for x in c]
assert [x['source_row_index'] for x in c]==list(range(1330))
assert b['original_pool_counts']==v['original_pool_counts']=={'candidate_review_pool':636,'existing_reinforcement':28,'strict_passed_spec':8,'watchlist_context_pool':658}
assert v['original_formal_individually_reviewed_0_1P']==45
assert v['original_formal_pending_0_1P_unchanged']==1285
assert v['new_promotions']==0
assert v['original_csv_sha256']==b['original_csv_sha256']
assert v['review_evidence_scope_counts']==b['review_evidence_scope_counts']
assert len(w['source_level_judgments'])==54
assert len(w['case_definitions'])==13
assert w['combined_pre_native_individual_four_judgments_count']==70
assert len(p['judgments'])==16
seen=set();by_sid={r['source_id']:r for r in w['source_level_judgments']}
assert len(by_sid)==54
assert not (set(by_sid)&{x['source_id'] for x in p['judgments']})
assert sum(len(k['source_row_indices']) for k in w['case_definitions'])==54
assert sum(len(k['event_units']) for k in w['case_definitions'])==23
review_counts=collections.Counter()
for a0,b0 in zip(a,c):
    id=a0['candidate_id'];delta={k for k in b0 if b0.get(k)!=a0.get(k)}
    if id in by_sid:
        assert delta=={'oct31_policy_watch_pre_native_case_ref_NOT_FORMAL'},(id,delta)
        assert b0['oct31_policy_watch_pre_native_case_ref_NOT_FORMAL']['native_0_1P_approved'] is False
        assert a0['additional_evidence_scope']=='NO_ADDITIONAL_EVIDENCE_ON_THIS_ID'
    else:
        assert delta==set(),(id,delta)
    review_counts[a0['original_stage_a_pool']]+=int(id in by_sid)
assert {k:v for k,v in review_counts.items() if v}=={'candidate_review_pool':49,'watchlist_context_pool':5}
bycase=collections.defaultdict(list)
for s in w['source_level_judgments']:
    bycase[s['case_id']].append(s)
    source=a[s['source_row_index']]
    assert source['candidate_id']==s['source_id']
    assert source['headline_raw']==s['headline_raw_original']
    assert source['primary_url_original']==s['source_url_original']
    assert source['metadata_score_original_not_selection_decision']==s['original_metadata_score_not_selection']
    assert s['native_0_1P_approved'] is False
    assert s['execution_credibility_gate']['status'] in {'PASS','REVIEW','FAIL'}
    assert s['independent_cardability_gate']['status'] in {'PASS','REVIEW','FAIL'}
    assert s['publication_urgency'] in {'immediate','near_term','monitor'}
    assert s['related_prepass']['status']=='HOLD'
    assert s['related_prepass']['earliest_same_event_check_status']=='HOLD'
    assert s['no_automatic_rejection_by_metadata_score'] is True
    parts=s['decision_value_breakdown']
    limits={'market_structure_competition':25,'supply_demand_price_utilisation':25,'technology_performance_safety':20,'cashflow_asset_value':10,'law_policy_market_access':10,'systemic_scale':5,'persistence_irreversibility':3,'decision_urgency_actionability':2}
    assert set(parts)==set(limits)
    assert all(isinstance(parts[k],int) and 0<=parts[k]<=limits[k] for k in limits)
    assert s['decision_news_value_score']==sum(parts.values())
    tech_caps={'not_applicable':0,'company_target_or_unsupported_claim':4,'laboratory_unvalidated':7,'pilot_precommercial':11,'independent_test_or_customer_qualification':15,'commercial_scale_or_long_duration_field':20,'material_failure_evidence':20}
    assert parts['technology_performance_safety']<=tech_caps[s['technology_evidence_level']]
    novelty={'none':100,'repeated_announcement_no_new_fact':39,'routine_progression_no_material_uncertainty':54,'company_target_without_validation_or_effect':54,'unsupported_political_rhetoric':39}
    assert s['decision_news_value_score']<=novelty[s['novelty_cap_basis']]
    if s['policy_stage'] in [0,1,2]:assert s['decision_news_value_score']<=[39,54,69][s['policy_stage']]
    if not s['systemic_scale_denominator']:
        assert parts['systemic_scale']<=2
        assert s['denominator_gap']
    if s['source_is_case_representative']:
        assert s['independent_cardability_gate']['status']=='REVIEW'
    else:
        assert s['independent_cardability_gate']['status']=='FAIL'
        assert s['decision_news_value_score']<=39
        assert s['novelty_cap_basis']=='repeated_announcement_no_new_fact'
for k in w['case_definitions']:
    items=bycase[k['case_id']]
    assert len(items)==len(k['source_row_indices'])
    assert {r['source_row_index'] for r in items}==set(k['source_row_indices'])
    reps=[r for r in items if r['source_is_case_representative']]
    assert len(reps)==1 and reps[0]['source_row_index']==k['representative_source_row_index']
    assert k['original_first_party_or_owner_url'].startswith('https://')
    assert k['remaining_evidence']
# Reject attempts to collapse same source observations into already-published baseline event counts.
roundup=bycase['US_ESS_ROUNDUP_EOS_FLEXGEN_GEORGIA_202609']
assert set(roundup[0]['economic_event_units_preserved'])=={'EOS_DOE_87018K_THIRD_DRAW_ALREADY_FULL','FLEXGEN_LIGHTSHIFT_16_BESS_ALREADY_FULL','GEORGIA_ROBINS_128MW_COD_NEW_CANDIDATE'}
assert set(roundup[0]['related_prepass']['matched_baseline_candidate_ids'])=={'2026-09-10_US_01','2026-09-16_US_02'}
assert len(next(k for k in w['case_definitions'] if k['case_id']=='KR_RESOURCE_SECURITY_PLAN_20260923')['event_units'])==4
assert len(next(k for k in w['case_definitions'] if k['case_id']=='EVE_FLUENCE_206GWH_FRAMEWORK_20260918')['event_units'])==2
receipt={
 'scope':'PASS_54_CASE_ANCHORED_PRE_NATIVE_JUDGMENTS_AND_1330_LOSSLESS_RECONCILIATION_ONLY',
 'native_stage_artifact_contract_A_executed':False,
 'native_stage_lineage_contract_stage_a_executed':False,
 'baseline_sha256':sha(root/names['baseline']),'prior16_sha256':sha(root/names['prior']),
 'new_batch_sha256':sha(root/names['batch']),'overlay_v5_sha256':sha(root/names['overlay']),
 'original_1330_source_ids_preserved':True,'source_ids_with_new_individual_inputs':54,
 'previous_16_pre_native_inputs_preserved':True,
 'combined_pre_native_source_inputs':70,
 'case_groups':13,'economic_event_unit_definitions':23,
 'new_input_source_pool_counts':dict(review_counts),
 'new_source_dispositions':dict(collections.Counter(x['provisional_disposition_not_native'] for x in w['source_level_judgments'])),
 'previous_45_formally_individually_reviewed_preserved':45,
 'formal_individual_pending_unchanged':1285,
 'original_strict_8_unchanged':8,'new_formal_strict_pass':0,
 'full_card_data_mutations':0,
 'caveat':'Issuer or original agency event-level anchors inspected; not all 54 secondary source article bodies were independently read; no native Stage A output or Stage B approval.'}
path=root/'STAGE_A_0_1P_POLICY_WATCH_INDEPENDENT_QC_20261031.json'
if path.exists():raise FileExistsError(path)
path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
