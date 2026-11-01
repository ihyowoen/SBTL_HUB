#!/usr/bin/env python3
"""CP21 human source-level decisions; retrieval/similarity does not decide pools."""
import sys,json,copy,hashlib,collections,re
from pathlib import Path
from cases import EVENTS,WATCHES,SUPPORT_EXISTING,ROOT
from build_stage_a_formal_kr_two_events_20261101 import coverage_maps,read,write,sha256,support_row
from build_stage_a_formal_usjp_four_events_20261101 import execution_strict
from build_stage_a_checkpoint_16_remaining_cases_20261101 import formal_watch
sys.path.insert(0,str(ROOT))
BASE=Path('work/cp20/STAGE_A_CP20_FORMAL_20261101.json')
OUT=Path('work/cp21/STAGE_A_CP21_FORMAL_20261102.json')
BASE_SHA='b0b06dae8fd3ac19950772479ba087e0c8b661f3388899b9bbd370f789cd21c1'
FULL_SHA='d22f0d4e39e035b9537b3e9abdf48abe6b7eb80f7e477e87aff1284f9e27e0d9'
assert sha256(BASE)==BASE_SHA and sha256(ROOT/'data/cards.full.json')==FULL_SHA
d=read(BASE);old=copy.deepcopy(d);rows=d['decision_ledger'];done={r['candidate_id'] for r in d['promotion_reassessment_ledger']}
review={r['story_id']:r for r in d['review_pool_resolution_ledger']}; changes={};results=[]
manifest=read(Path('work/source_fetch_manifest.json'));byurl={m['url']:m for m in manifest}
def evidence(url):
 m=byurl.get(url)
 if m is None:
  p=Path('work/evidence')/(hashlib.sha256(url.encode()).hexdigest()[:16]+'.json');m=read(p)
 assert m['status']==200,(url,m)
 p=Path('work/evidence')/(hashlib.sha256(url.encode()).hexdigest()[:16]+'.raw'); assert sha256(p)==m['sha256']
 return {k:m[k] for k in ('url','final_url','status','sha256','retrieved_utc','text_chars')}
def apply(i,e,row,result):
 o=old['decision_ledger'][i];sid=o['story_id'];assert sid not in done and i not in changes
 assert all(row.get(k)==o.get(k) for k in ('source_row_index','story_id','candidate_id','headline_raw','primary_url','origin'))
 urls=e['owner_urls'];ev=[evidence(u) for u in urls]
 tag={'source_id':sid,'row':i,'result':result,'event_family':e['case_id'],'economic_act_edges':[{'event':a,'role':'distinct_act_or_stage_preserved'} for a in e['event_units']], 'first_party_owner_urls':urls,'primary_retrieval':ev,'source_url':o['primary_url'],'source_body_retrieval':byurl.get(o['primary_url']),'stage_b_authorized':False,'human_adjudicated':True}
 row['formal_0_1P_cp21_source_to_economic_act_edges_20261102']=tag
 row['cp21_source_identity_preserved']={k:o[k] for k in ('source_row_index','story_id','candidate_id','headline_raw','primary_url','origin')}
 row['assessment_method']='PROMPT_0_1P_V4_20260829 manual original-body / Full1676 / stage audit CP21'
 row['economic_event_cluster_id']=e['case_id']
 # All new history references are local Stage A only.
 row['stage_b_authorized']=False;row['accepted_facts_approved']=False;row['canonical_card_write_allowed']=False
 row['stage_a_evidence_status']='not_evidence_complete_no_fetch'
 row['cp21_selector_body_inspection']={'performed':True,'compatibility_enum_note':'Legacy enum no_fetch refers to no Stage B evidence fetch/package; original bodies were retrieved and inspected in Stage A, hashes attached.'}
 row['date_role']={**row.get('date_role',{}),'event_date':e['date'],'status':'PASS_STAGE_A_PRELIMINARY','representative_date_basis':'Owner dated economic act or announcement, with retrospective/forward stage explicitly preserved.'}
 if i in (1165,730,1070):
  row['date_role'].update(event_date=None,announcement_date=e['date'],event_date_window='2026-09' if i==1165 else 'on_or_before_2026-09-25',representative_date_basis='Disclosure date known; exact underlying operation/market-entry date is not supplied. Preserve bounded event window.')
 changes[i]=row;rows[i]=row;results.append(tag)
 pool=row['stage_a_pool']
 status={'STRICT':'PROMOTED_VALIDATED_STRICT','SUPPORT':'FORMAL_SAME_EVENT_SUPPORT_ONLY','WATCH':'FORMAL_WATCH_NO_CARD'}[result]
 d['promotion_reassessment_ledger'].append({'candidate_id':sid,'economic_event_cluster_id':e['case_id'],'before_pool':o['stage_a_pool'],'after_pool':pool,'promotion_reassessment_status':status,'resolved':row.get('final_reason',row.get('new_verified_fact')),'remaining':row.get('remaining_uncertainty'),'source_candidates':urls,'source_observation_preserved':True})
 if pool!='strict_passed_spec':
  review[sid].update({'original_review_pool_partition':pool,'cp21_previous_partition':o['stage_a_pool'],'current_disposition':pool,'disposition_basis':row['final_reason'],'carry_forward_policy':'support_source_only' if result=='SUPPORT' else 'carry_forward_to_watchlist','next_action_condition':row.get('future_trigger_to_reopen','New dated independent act or stage only'),'final_review_pool_disposition':row['final_review_pool_disposition'],'reviewed_by_stage_or_pass':'PROMPT_0_1P_V4_20260829 manual owner-body CP21','review_artifact_id':'STAGE_A_CHECKPOINT_21_FORMAL_20261102'})
for e in EVENTS:
 obs=[old['decision_ledger'][i] for i in e['rows']];rep=e['representative'];spec=execution_strict(old['decision_ledger'][rep],{},e,obs)
 # Prevent an unrelated old strict event from leaking via template inheritance.
 spec.update(headline=e['title'],title_raw=e['title'],representative_date=e['date'],publication_date='2026-09-22' if rep==1287 else '2026-09-24' if rep==581 else e['date'])
 spec['date_role']['publication_date']=spec['publication_date']
 spec['date_role']['announcement_date']=spec['publication_date']
 spec['date_role']['earliest_check_scope']='Full1676 + complete Source ID universe + relevant dated owner document, inspected CP21.'
 spec['staleness']['publication_date']=spec['publication_date']
 spec['staleness']['staleness_gap_days']=2 if rep==581 else 1 if rep==1287 else 0
 spec['upstream_labels']={k:old['decision_ledger'][rep].get(k) for k in ('upstream_status','upstream_drop_reason','integrity_group_id','integrity_is_best')}
 spec['upstream_labels']['triage_status']=old['decision_ledger'][rep].get('upstream_status')
 spec['upstream_labels'].update(matched_buckets=old['decision_ledger'][rep].get('matched_buckets',[]),drop_reason=old['decision_ledger'][rep].get('upstream_drop_reason',''),drop_reason_overridden=bool(old['decision_ledger'][rep].get('upstream_drop_reason')))
 spec['evidence_needed_for_stage_b']=[f"{e['owner']} official document: verify event date {e['date']} and exact stage: {e['new_fact']} {e['must_not']}"]
 follow={1278:'CATL Debrecen series-production start date and measured cell shipment volume would strengthen European local supply readiness outlook; further trial delay would weaken that outlook.',1290:'Form Energy actual credit drawdown amount and eligible45X production volume would strengthen manufacturing liquidity outlook; cancelled facility availability would weaken that outlook.',1287:'Pylontech Hefei monthly601Ah cell shipment volume and production yield would strengthen large-cell commercialization outlook; failed independent cycle test results would weaken the lifetime outlook.',581:'LGES and B2U signed purchase contract volume and first project commissioning date would strengthen U.S. second-life supply outlook; cancellation of priority access would weaken that outlook.',91:'Invest Ontario signed loan contract amount and Marathon construction start date would strengthen project financing outlook; unmet conditions or suspended loan approval would weaken that outlook.'}
 spec['next_confirmation_points']=[follow[rep]]
 spec['decision_value_classification']='high_decision_value' if sum(e['score'])>=70 else 'material_industry_signal'
 spec['anchor_classes']=['execution_event_anchor','strategic_behavior_anchor']
 spec['source_priority_notes']=e['must_not'];spec['technology_validation_gap']=e['must_not']
 spec['execution_anchor_type']=e['event_units'][0].lower();spec['execution_credibility_gate']['anchor_type']=spec['execution_anchor_type']
 spec['formal_0_1P_cp21_strict_event_20261102']={'owner':e['owner'],'event_units':e['event_units'],'guard':e['must_not'],'related_full_ids':e['related_full'],'manual_body_comparison':True}
 if rep==1287:
  spec['technology_evidence_level']='company_target_or_unsupported_claim';spec['technology_validation_stage']='concept_or_target';spec['technology_score_cap_applied']=True;spec['technology_stage_provisional']=False
 apply(rep,e,spec,'STRICT');d['strict_passed_spec'].append(spec)
 for i in e['rows']:
  if i==rep:continue
  su=support_row(old['decision_ledger'][i],e,old['decision_ledger'][rep]['story_id']);su['related_prepass']['earliest_check_scope']='Full1676 + owner original + actual source body';apply(i,e,su,'SUPPORT')
for e in SUPPORT_EXISTING:
 for i in e['rows']:
  su=support_row(old['decision_ledger'][i],e,old['decision_ledger'][e['rep']]['story_id']);su['related_prepass']['earliest_check_scope']='Geely Sep23 original + CP20 row772 + actual commentary body';apply(i,e,su,'SUPPORT')
for e in WATCHES:
 if not e['owner_urls']:e['owner_urls']=[old['decision_ledger'][e['rows'][0]]['primary_url']]
 obs=[old['decision_ledger'][i] for i in e['rows']]
 for i in e['rows']:
  w=formal_watch(old['decision_ledger'][i],e,obs,obs[0]['story_id'])
  w['prior_state']='Full1676 and formal153 body/title comparisons; context/limited-scale/early-stage result is explicitly retained, not deleted.'
  w['new_verified_fact']=e['why'];w['uncertainty_resolved']='Original document identity, topic and announced action stage; industrial-scale realization not inferred.'
  w['date_role']['publication_date']=e['date'];w['protected_source_context']=e['why'];apply(i,e,w,'WATCH')
changed_sids={r['story_id'] for r in changes.values()}
for pool in ('candidate_review_pool','watchlist_context_pool','reject_or_support_only_pool','existing_reinforcement'):
 d[pool]=[r for r in old[pool] if r['story_id'] not in changed_sids]+[r for i,r in sorted(changes.items()) if r['stage_a_pool']==pool]
strict_sids={r['story_id'] for r in d['strict_passed_spec']};d['review_pool_resolution_ledger']=[r for r in d['review_pool_resolution_ledger'] if r['story_id'] not in strict_sids]
counts=collections.Counter(r['result'] for r in results);total=153+len(results);pending=1330-total
s=d['summary'];s.update(strict_passed_spec_count=len(d['strict_passed_spec']),processed_priority_source_observations=total,unprocessed_editorial_observations=pending,processed_priority_economic_clusters=s['processed_priority_economic_clusters']+len(EVENTS),needs_review_count=len(d['review_pool_resolution_ledger']))
s['pool_counts']={k:len(d[k]) for k in ('strict_passed_spec','candidate_review_pool','watchlist_context_pool','reject_or_support_only_pool','existing_reinforcement','rejected','support_source_only')}
d['review_pool_partition_summary']={k:len(d[k]) for k in ('candidate_review_pool','watchlist_context_pool','reject_or_support_only_pool')};coverage_maps(d)
from validation_scripts.stage_a_full_v3_completeness_review4943656188 import _expected_summary_id_arrays
for k,v in _expected_summary_id_arrays(d).items():
 if k in s:s[k]=v
att=d['pre_native_0_1P_attachment_manifest_20261101'];att['formal_review_completed_source_ids'] += [r['source_id'] for r in sorted(results,key=lambda z:z['row'])];att['formal_review_completed_after_attachment_count']=len(att['formal_review_completed_source_ids']);att['remaining_formal_source_count']=pending;att['new_formal_decisions']=len(att['formal_review_completed_source_ids']);att['new_strict_promotions']+=counts['STRICT'];att['native_validator_scope_warning']=f'Native validity is not global completion; {pending} unadjudicated Source IDs remain.'
d['formal_0_1P_cp21_owner_body_batch_20261102']={'base_cp20_sha256':BASE_SHA,'formal_total':total,'pending_total':pending,'strict_total':len(d['strict_passed_spec']),'new_formal_source_ids':len(results),'new_result_counts':dict(counts),'source_to_economic_act_edges':sorted(results,key=lambda z:z['row']),'case_index':EVENTS+WATCHES+SUPPORT_EXISTING,'global_stage_a_status':f'HOLD_OPEN_{pending}_UNADJUDICATED','stage_b_executed':False,'canonical_main_full_related_mutations':0,'new_published_cards':0}
d['recommended_for']=[f'Finish {pending} pending Source IDs with original body comparison. Stage A HOLD; Stage B prohibited.']
d['next_call_recommendation']['reason']=d['recommended_for'][0]
d['next_call_recommendation']['blocked_items_summary']=d['review_pool_partition_summary']
write(OUT,d)
write(OUT.with_name('STAGE_A_CP21_RECEIPT_20261102.json'),{'status':'PENDING_NATIVE_AND_INDEPENDENT_QC','base_sha256':BASE_SHA,'output_sha256':sha256(OUT),'locked_full_sha256':FULL_SHA,'new_formal':len(results),'results':dict(counts),'cumulative_formal':total,'remaining':pending,'cumulative_strict':len(d['strict_passed_spec']),'stage_b_executed':False,'canonical_main_full_related_mutations':0,'source_decisions':sorted(results,key=lambda z:z['row'])})
print(json.dumps({'new':len(results),'results':dict(counts),'formal':total,'pending':pending,'strict':len(d['strict_passed_spec'])}))
