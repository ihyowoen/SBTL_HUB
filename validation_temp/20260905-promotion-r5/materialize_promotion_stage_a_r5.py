#!/usr/bin/env python3
from __future__ import annotations
import copy, json
from pathlib import Path
from urllib.parse import urlparse

BASE='aa7400ae67b221d1ddd5e198293762caec389303'
BLOB='920646b6b335f211bcd224962f8ac0cc42cd3a4f'
COUNT=1578
R4_OUT=Path('validation_temp/20260905-promotion-r1/out/stage-a-promotion.json')
R4_LEDGER=Path('validation_temp/20260905-promotion-r1/out/promotion-review-ledger.json')
EXT=Path('validation_temp/20260905-promotion-r5/promotion-universe-r5-extension.json')
OUTROOT=Path('validation_temp/20260905-promotion-r5/out')
OUT=OUTROOT/'stage-a-promotion-r5.json'
LEDGER=OUTROOT/'promotion-review-ledger-r5.json'
RUN_ID='card-run-2026-09-08-sep5-promotion-r5'
PROMPT='docs/llm_prompts/v1/14_PROMPT_0_1P_Review_Pool_Promotion.md'
CHECKED='2026-09-08'

CFG={
 'STD26_R8P_005':{
  'event_id':'SEP5P_005_FOSU_JINLI','story_id':'CN_2026-09-05_C10','region':'CN','date':'2026-09-03','source':'Foshan Fosu Technology / disclosure mirrors',
  'primary':'https://paper.cnstock.com/html/2026-09/04/content_2265079.htm','supports':['https://epaper.cs.com.cn/zgzqb/html/2026-09/04/nw.D110000zgzqb_20260904_1-B033.htm'],
  'title':'佛塑科技·金力新能源, 80억㎡ 분리막 증설안 이사회 승인…주주총회 승인 대기',
  'fact':'佛塑科技 이사회는 9월 3일 韶关 40억㎡/년 습식 분리막 프로젝트(약 33.47억위안)와 武安 40억㎡/년 코팅 분리막 프로젝트(약 38.11억위안)를 승인했다. 두 투자안은 주주총회 승인이 아직 필요하다.',
  'relevance':'리튬이온 분리막 업체가 총 80억㎡/년 규모의 대형 증설안을 이사회 단계까지 구체화한 공급망 증설 신호다.',
  'uncertainty':'두 프로젝트는 이사회 승인 상태지만 주주총회 승인이 아직 필요하며 실제 착공·양산 시점은 확정되지 않았다.',
  'breakdown':{'market_structure_competition':18,'supply_demand_price_utilisation':17,'technology_performance_safety':0,'cashflow_asset_value':8,'law_policy_market_access':2,'systemic_scale':2,'persistence_irreversibility':4,'decision_urgency_actionability':4},
  'anchor_classes':['strategic_behavior_anchor'],'baseline_relation':'new_unrelated','predecessor':None,
  'research_reason':'Company disclosure mirrors identify the 9/3 board approval, exact 4bn+4bn m2 annual capacity and RMB3.347bn/RMB3.811bn project investments while explicitly preserving pending shareholder approval.'
 },
 'STD26_R8P_006':{
  'event_id':'SEP5P_006_LI_AUTO_SUNWODA','story_id':'CN_2026-09-04_C26','region':'CN','date':'2026-09-04','source':'Sunwoda disclosure / Li Auto',
  'primary':'https://money.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?id=12585331&stockid=300207','supports':['https://www.nbd.com.cn/articles/2026-09-04/4573133.html','https://www.cls.cn/detail/2474636'],
  'title':'理想汽车, 欣旺达动力에 26.5억위안 전략증자…완료 후 직접 8.79%',
  'fact':'欣旺达 이사회는 9월 4일 北京理想汽车가 欣旺达动力에 26.5억위안을 증자하는 C++ 라운드를 승인했다. 증자 완료 후 理想汽车의 직접 지분은 8.79%가 되며 欣旺达动力는 계속 欣旺达의 연결대상 자회사로 남는다. 공시 시점에는 관련 당사자가 증자계약을 체결할 예정이라고 기재됐다.',
  'relevance':'완성차 업체가 핵심 배터리 공급사의 지분을 직접 확대해 기술·제조·품질 협력의 이해관계를 강화하는 공급망 수직연계 신호다.',
  'uncertainty':'이사회 승인과 투자조건은 구체적이지만 공시 시점 증자계약 체결·거래 종결은 아직 완료되지 않았다.',
  'breakdown':{'market_structure_competition':19,'supply_demand_price_utilisation':14,'technology_performance_safety':0,'cashflow_asset_value':10,'law_policy_market_access':0,'systemic_scale':2,'persistence_irreversibility':6,'decision_urgency_actionability':4},
  'anchor_classes':['strategic_behavior_anchor','data_financial_anchor'],'baseline_relation':'new_unrelated','predecessor':None,
  'research_reason':'The issuer announcement fixes the 9/4 board approval, RMB2.65bn investment and 8.79% post-financing direct stake while distinguishing approval from later agreement execution/closing.'
 },
 'STD26_R8P_007':{
  'event_id':'SEP5P_007_CN_RE_SHIPMENTS','story_id':'GL_2026-09-04_C12','region':'GL','date':'2026-09-04','source':'Reuters',
  'primary':'https://www.reuters.com/business/aerospace-defense/china-rare-earth-firms-halt-some-us-shipments-over-geopolitical-worries-sources-2026-09-04/','supports':[],
  'title':'중국 일부 희토류 공급업체, 지정학·컴플라이언스 우려로 미국향 일부 출하 중단',
  'fact':'Reuters는 9월 4일 복수 소식통을 인용해 중국의 일부 희토류 공급업체들이 지정학·컴플라이언스 우려 속에 미국향 일부 출하를 중단했다고 보도했다. 이는 중국 전체 또는 정부의 포괄적 수출금지로 해석하지 않는다.',
  'relevance':'정식 수출금지와 별개로 공급업체 수준의 자율적 리스크 회피가 미국의 희토류 조달 가용성을 제약할 수 있다는 시장접근 신호다.',
  'uncertainty':'행동 범위는 일부 공급업체·일부 출하에 한정되며 정부의 전면 금지 또는 전체 중국 공급망의 동일 행동은 확인되지 않았다.',
  'breakdown':{'market_structure_competition':18,'supply_demand_price_utilisation':20,'technology_performance_safety':0,'cashflow_asset_value':4,'law_policy_market_access':4,'systemic_scale':2,'persistence_irreversibility':3,'decision_urgency_actionability':4},
  'anchor_classes':['strategic_behavior_anchor'],'baseline_relation':'new_unrelated','predecessor':None,
  'research_reason':'Reuters source-based reporting resolves the behavior signal but requires strict bounded wording: several/some suppliers and some U.S. shipments, not a nationwide Chinese export ban.'
 },
 'STD26_R8P_008':{
  'event_id':'SEP5P_008_HUNGARY_WATCHDOG','story_id':'GL_2026-09-03_C13','region':'EU','date':'2026-09-03','source':'Reuters',
  'primary':'https://www.reuters.com/sustainability/climate-energy/hungary-create-watchdog-oversee-ev-battery-plants-boost-fines-polluters-2026-09-03/','supports':[],
  'title':'헝가리, 배터리 환경감독 강화…최대 50억포린트·three-strikes 벌금 체계 구체화',
  'fact':'9월 3일 발표된 헝가리 환경감독 강화안은 배터리 제조·재활용·폐기 감독, 최대 50억포린트 벌금, 5년 내 3회 위반 시 최소 연간 순매출의 0.5% 벌금이라는 구체적 체계를 제시했다.',
  'relevance':'7월의 전담 감시기구 출범 추진에서 실제 감독범위와 벌금 상한·반복위반 산식이 구체화돼 헝가리 배터리 생산의 환경규제 비용과 운영 리스크가 한 단계 명확해졌다.',
  'uncertainty':'세부 법령·시행일과 개별 업체에 대한 실제 집행 사례는 후속 확인이 필요하다.',
  'breakdown':{'market_structure_competition':12,'supply_demand_price_utilisation':8,'technology_performance_safety':0,'cashflow_asset_value':8,'law_policy_market_access':17,'systemic_scale':2,'persistence_irreversibility':4,'decision_urgency_actionability':4},
  'anchor_classes':['policy_regulatory_anchor','strategic_behavior_anchor'],'baseline_relation':'distinct_follow_up','predecessor':'2026-07-06_KR_05',
  'research_reason':'Reuters resolves the follow-up question by adding the watchdog scope, HUF5bn maximum fine and three-strikes minimum 0.5%-of-revenue formula beyond the July canonical planning card.'
 }
}

def writej(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def domains(urls): return sorted({urlparse(u).netloc for u in urls if u})

def make_related(c):
 pred=c['predecessor']
 if not pred:
  return {'status':'PASS','same_event_checked':True,'matched_baseline_candidate_ids':[],'matched_current_batch_candidate_ids':[],'relation_candidates':[],'duplicate_disposition':'no_duplicate_found','earliest_same_event_check_status':'PASS','fresh_anchor_questions':[f"Confirm next measurable stage after {c['date']} for {c['event_id']}."]}
 return {'status':'PASS','same_event_checked':True,'matched_baseline_candidate_ids':[pred],'matched_current_batch_candidate_ids':[],'relation_candidates':[{'target_candidate_id':pred,'proposed_relation_type':'distinct_follow_up','confidence':'high','reason':'September watchdog scope and fine formula are a later policy-stage progression from the July canonical planning card.','anchor_class_to_verify':'follow_up_probability_anchor','incremental_anchor_question':f"What new verified policy detail after the prior {pred} planning card changes the judgment?"}], 'duplicate_disposition':'distinct_follow_up','earliest_same_event_check_status':'PASS','fresh_anchor_questions':['Verify implementation/effective-date and first enforcement actions.']}

def make_spec(template,c,spec_id):
 x=copy.deepcopy(template); urls=[c['primary']]+c['supports']; sid=c['story_id']
 x.update({
  'source_event_id':c['event_id'],'source_origin':'sep5_prompt_0_1p_r5_authorized_bounded_research','source_story_ids':[sid],'original_story_ids':[sid],
  'primary_url':c['primary'],'urls':urls,'same_event_source_cluster':[{'story_id':sid,'url':c['primary'],'preserve_for_stage_b':True}],
  'merge_status':'source_cluster','merged_story_ids':[],'enhanced_selector_precision_version':'v3','selector_policy_version':'STRUCTURAL_NEWS_VALUE_SELECTION_V3','selection_policy_version':'EMBEDDED_NEWS_VALUE_SELECTION_V4',
  'selection_route':'structural_non_execution_route','strict_gate_check':'pass','format_risk_tags':['v4_structural_non_execution_route_compatibility'],'anchor_classes':c['anchor_classes'],
  'decision_news_value_score':55,'decision_value_breakdown':c['breakdown'],'decision_value_classification':'material_industry_signal',
  'publication_urgency':{'level':'near_term','action_required':f"Track next measurable milestone for {c['event_id']}.",'decision_deadline':None},
  'technology_evidence_level':'not_applicable','policy_stage':2 if spec_id=='STD26_R8P_008' else None,'novelty_cap_basis':'none','systemic_scale_denominator':None,
  'denominator_gap':f"No market-wide denominator is asserted for {c['event_id']}; systemic scale is capped at 2/5.",
  'prior_state':'The Sep5 main run retained this event outside the initial strict production set and user explicitly authorized Prompt 0.1P re-adjudication.',
  'new_verified_fact':c['fact'],'changed_judgment':f"Authorized Prompt 0.1P R5 research promotes {c['event_id']} through the ordinary Stage A strict contract.",
  'uncertainty_resolved':c['research_reason'],'remaining_uncertainty':c['uncertainty'],'incremental_information':c['fact'],
  'baseline_expectation_changed':('The current 1578-card baseline contains the July predecessor, and the September item adds a distinct later policy-stage progression.' if c['predecessor'] else 'Current canonical 1578 contains no same-event card after URL/event-fingerprint reconciliation.'),
  'decision_relevance':c['relevance'],'evidence_needed_for_stage_b':[f"Fetch and verify body-level evidence for {c['title']}; preserve the exact stage limitation and operative date {c['date']}."],
  'next_confirmation_points':[f"{c['uncertainty']} A later binding/implementation/execution milestone would strengthen the judgment; non-progression would weaken it."],
  'related_prepass':make_related(c),'date_role':{'status':'PASS','representative_date':c['date'],'event_date':c['date'],'publication_dates':[c['date']],'earliest_same_event_date_checked':True,'event_date_source_url':c['primary'],'event_date_source_quote':f"Bounded source package anchors the operative event to {c['date']}.",'source_quote_emitted':False,'note':'Operative date separated from republication dates.'},
  'execution_credibility_gate':{'status':'PASS','anchor_type':'structural_or_policy_signal','anchor_strength':'moderate','stage_precision_note':c['uncertainty']},
  'independent_cardability_gate':{'status':'PASS','distinct_event_or_stage_progression':True,'full_schema_viability':'PASS','duplicate_or_reinforcement_note':('Distinct follow-up to '+c['predecessor'] if c['predecessor'] else 'No same-event canonical card found on current canonical 1578.')},
  'execution_anchor_type':None,'execution_anchor_strength':None,'structural_value_override_applied':True,'structural_selector_policy_version':'STRUCTURAL_NEWS_VALUE_SELECTION_V3',
  'structural_value_override_reason':'The active V4 selector admits this item through the structural non-execution route because bounded research resolves a decision-relevant market/supply-chain/policy state change without claiming conventional execution.',
  'structural_non_execution_reason':f"{c['event_id']} is a structural market/supply-chain/policy signal with explicit stage limitations.",
  'why_execution_event_not_required':'V4 structural non-execution route is appropriate because the material change is the newly specified strategic/policy state; no construction/COD or completed transaction is claimed.',
  'baseline_relation':c['baseline_relation'],'baseline_match':([c['predecessor']] if c['predecessor'] else []),'duplicate_risk':'low_after_current_main_event_reconciliation','staleness_decision':'current','source_access_risk':('moderate' if 'Reuters' in c['source'] else 'low'),
  'stage_a_evidence_status':'not_evidence_complete_no_fetch','stage_b_evidence_package_required':True,'primary_url_semantics':'provided_source_candidate_not_evidence','source_cluster_preserved':True,
  'support_source_candidates':c['supports'],'source_domain_candidates':domains(urls),'source_diversity_path':{'status':'viable','probable_independent_owner_count':max(1,len(domains(urls))),'official_or_source_owner_candidate_present':('Reuters' not in c['source']),'independent_confirmation_candidate_present':bool(c['supports']),'context_candidate_present':True,'reason':'Prompt 0.1P bounded research supplies an explicit Stage B source path; Stage B must independently fetch/verify before drafting.'},
  'support_source_candidates_accounted':True,'stage_b_requirement_note':'Stage B must independently fetch and verify the candidate source package; Stage A does not declare evidence_complete.',
  'region':c['region'],'representative_date':c['date'],'representative_source':c['source'],'source_tier_estimate':'bounded_authoritative_or_reuters_source_candidate','cat':'battery_ess_materials_grid','sub_cat':'strategy_market_structure','signal_estimate':'material','signal_rubric_estimate':{'status':'material_industry_signal','score':55},
  'strategic_lens':['market_structure_supply_chain_execution'],'event_anchor':'structural_non_execution_signal','title_raw':c['title'],'summary_hint':c['fact'],'context_text':'Authorized Sep5 Prompt 0.1P R5 review against current main aa7400ae / canonical 1578.','why_now':f"Bounded promotion research resolved the recorded uncertainty at the {c['date']} stage.",'market_relevance':c['relevance'],'source_priority_notes':'Stage B must verify the strongest source-owner/authoritative or Reuters body evidence and preserve limitations.',
  'upstream_labels':{'triage_status':'KEEP','matched_buckets':['battery_ess_materials_grid'],'drop_reason':None,'integrity_group_id':c['event_id'],'integrity_is_best':True,'drop_reason_overridden':True},
  'staleness':{'event_date':c['date'],'publication_date':c['date'],'staleness_gap_days':0,'staleness_suspected':False,'fresh_followup':bool(c['predecessor']),'staleness_override':False,'decision':'current_or_effective_date_milestone'},
  'needs_review':False,'review_reason':None,'denominator_used':'Named event/policy only.','baseline_follow_up_relation':c['baseline_relation'],'portfolio_coverage_contribution':['market_structure_supply_chain_execution'],'structural_value_lenses':['market_structure_supply_chain_execution'],
  'anti_bias_check':{'binding_status_used_as_importance_proxy':False,'legal_formality_used_as_importance_proxy':False,'headline_amount_used_without_denominator':False,'announced_capacity_treated_as_actual_output':False,'routine_execution_event_overranked':False,'conventional_execution_event_required_without_reason':False},
  'structural_rescue_required':False,'structural_rescue_question':None,'search_before_delete_status':'applied','spec_id':spec_id,
  'strict_pass_gate':{'status':'pass','reason':f"{c['event_id']} satisfies current V4 strict Stage A after authorized bounded Prompt 0.1P R5 research.",'all_six_conditions_passed':True,'anchor_supported_by_upstream_text':True,'why_not_review_pool':c['research_reason']},
  'promotion_provenance':{'prompt_file':PROMPT,'prompt_version':'PROMPT_0_1P_V4_20260829','source_review_pool_item_id':f"SEP5_P01P_CURATED_{c['event_id']}",'bounded_research_disposition':'PROMOTE_TO_STRICT','original_score':None,'re_adjudicated_score':55,'research_reason':c['research_reason'],'research_evidence_urls':urls,'checked_at':CHECKED},
  'legal_policy_stage':('stage_2_bill_or_proposed_rule' if spec_id=='STD26_R8P_008' else None),
  'follow_up_relation':c['baseline_relation']
 })
 # Frozen V3 compatibility fields intentionally remain bounded, never upgrading evidence.
 x['technology_validation_stage']='concept_or_target'; x['technology_score_cap_applied']=False; x['technology_validation_gap']='not_applicable'
 forbidden=['SEP5_001_CITRUS','SEP5_005_ENGIE10','STD26_R8_005','10.7GW']
 payload=json.dumps(x,ensure_ascii=False)
 assert not any(v in payload for v in forbidden), (spec_id,'stale template residue')
 return x

def main():
 out=json.loads(R4_OUT.read_text()); ledger=json.loads(R4_LEDGER.read_text()); ext=json.loads(EXT.read_text())
 assert len(ledger['items'])==83 and out['candidate_promotion_contract']['promoted_count']==4
 assert ext['final_authorized_candidate_count']==87 and ext['base_main_commit_sha']==BASE and ext['base_canonical_blob_sha']==BLOB
 template=out['strict_passed_spec'][0]; decision_template=out['decision_ledger'][0]
 strict=list(out['strict_passed_spec']); decision=list(out['decision_ledger'])
 for spec_id,c in CFG.items():
  s=make_spec(template,c,spec_id); strict.append(s)
  d=copy.deepcopy(decision_template)
  # synchronize every Stage-A semantic field from the strict spec, preserving ledger-only keys.
  for k,v in s.items(): d[k]=copy.deepcopy(v)
  d['story_id']=c['story_id']; d['ledger_decision']='strict_passed_spec'; d['decision']='strict_passed_spec'; d['spec_id']=spec_id; d['source_event_id']=c['event_id']
  decision.append(d)
  ledger['items'].append({'review_item_id':f"SEP5_P01P_CURATED_{c['event_id']}",'origin':'curated_hold_r5_extension','source_story_ids':[c['story_id']],'disposition':'PROMOTE_TO_STRICT','reason':c['research_reason'],'promoted_spec_id':spec_id,'evidence':[c['primary']]+c['supports']})
 out['strict_passed_spec']=strict; out['decision_ledger']=decision
 out['run_id']=RUN_ID; out['run_tag']='20260908_SEP5_PROMPT_0_1P_PROMOTION87_R5'; out['run_label']='Prompt 0.1P V4 authorized full Sep5 promotion universe: 87 candidates, current-main rebind R5.'
 out['base_main_commit_sha']=BASE; out['base_full_blob_sha']=BLOB; out['baseline_count']=COUNT; out['baseline_source_declaration']=f'current GitHub main {BASE}, canonical blob {BLOB}, {COUNT} cards'
 out['source_universe']='Exact 87 authorized promotion candidates: 78 upstream review_queue plus 9 curated review/hold events; all receive terminal promotion accounting.'
 out['story_count']=10; out['event_count']=8; out['original_status_counts']={'KEEP':10}
 out['integrity_summary'].update({'main_sha':BASE,'canonical_blob_sha':BLOB,'candidate_event_count':8,'candidate_source_observation_count':10,'duplicate_candidate_membership':0,'unassigned_candidate_membership':0})
 out['recommended_for']=['Stage B evidence construction for the 8 newly promoted strict specs only','terminal accounting for 79 retained review candidates']
 out['next_call_recommendation']={'recommended_next_call':'Stage B r0','recommended_prompt_id':'Prompt 0.2','recommended_input_universe':'Stage A strict_passed_spec[] only','reason':'Eight of 87 authorized promotion candidates satisfy the ordinary Stage A strict contract after bounded Prompt 0.1P R5 research; 79 remain outside Stage B.','blocked_items_summary':[]}
 out['dropped_treasure_hunt']={'performed':False,'trigger_reason':'Prompt 0.1P R5 is bounded to the exact authorized 87-item promotion universe and does not open new discovery.','sample_strategy':'not_applicable','sample_size':0,'sampled_story_ids':[],'rescued_count':0,'rescue_ids':[],'non_sampled_dropped_count':0,'non_sampled_ledger_policy':'All 87 promotion candidates receive explicit terminal disposition.'}
 s=out['summary']; s.update({'strict_passed_spec_count':8,'total_ledger_count':10,'ledger_matches_story_count':True,'decision_ledger_count':10,'formal_event_count':8,'source_bound_observation_count':10,'decision_value_classification_counts':{'material_industry_signal':8},'selection_route_counts':{'structural_non_execution_route':8}})
 ac={}
 for row in strict:
  for a in row.get('anchor_classes',[]): ac[a]=ac.get(a,0)+1
 s['anchor_class_counts']=ac; s['follow_up_candidate_ids']=['STD26_R8P_008']; s['legal_policy_stage_gap_ids']=[]
 out['candidate_promotion_contract']={'prompt_file':PROMPT,'prompt_version':'PROMPT_0_1P_V4_20260829','candidate_count':87,'promoted_count':8,'retained_count':79,'score_inflation_for_source_recovery':False,'current_main_sha':BASE,'current_canonical_blob_sha':BLOB,'promotion_ledger_ref':str(LEDGER),'universe_extension_ref':str(EXT),'promotion_ledger':[x for x in ledger['items'] if x['disposition']=='PROMOTE_TO_STRICT']}
 assert len(strict)==8 and len(decision)==10 and len(ledger['items'])==87
 assert len({x['review_item_id'] for x in ledger['items']})==87
 ledger.update({'schema':'sep5_prompt_0_1p_review_ledger_r5_v1','status':'PASS','run_id':RUN_ID,'base_main_commit_sha':BASE,'base_canonical_blob_sha':BLOB,'candidate_count':87,'promoted_count':8,'retained_count':79})
 writej(OUT,out); writej(LEDGER,ledger)
 print('RESULT: MATERIALIZED_SEP5_PROMOTION_R5',OUT); print('PROMOTED',len(strict),'RETAINED',79,'OBS',len(decision),'UNIVERSE',len(ledger['items']))

if __name__=='__main__': main()
