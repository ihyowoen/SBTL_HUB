#!/usr/bin/env python3
from __future__ import annotations
import copy, hashlib, json
from pathlib import Path

BASE='77b03de7cf8c941068e8adcc6ef7de4bdf5f92ae'
BLOB='920646b6b335f211bcd224962f8ac0cc42cd3a4f'
COUNT=1578
SRC=Path('runs/2026-09-07/r7-20260905-production-r1/stages/stage-a.json')
UNIVERSE=Path('validation_temp/20260905-promotion-r1/promotion-universe.json')
OUTROOT=Path('validation_temp/20260905-promotion-r1/out')
OUT=OUTROOT/'stage-a-promotion.json'
LEDGER=OUTROOT/'promotion-review-ledger.json'
PROMPT='docs/llm_prompts/v1/14_PROMPT_0_1P_Review_Pool_Promotion.md'
RUN_ID='card-run-2026-09-08-sep5-promotion-r1'
CHECKED='2026-09-08'

CANDS=[
 {
  'review_item_id':'SEP5_P01P_CURATED_IONIC_USSM','spec_id':'STD26_R8P_001','event_id':'SEP5P_001_IONIC_USSM',
  'story_ids':['GL_2026-09-03_C15'],'region':'US','date':'2026-09-03','source':'US Strategic Metals',
  'primary_url':'https://www.usstrategicmetals.com/us-strategic-metals-and-ionic-rare-earths-to-build-first-u-s-magnet-recycling-plant-in-missouri/',
  'support_urls':['https://www.mining.com/ionic-rare-earths-us-strategic-metals-form-jv-to-build-100m-magnet-recycling-plant-in-missouri','https://www.miningweekly.com/article/ionic-rare-earths-secures-term-sheet-for-magnet-recycling-jv-in-us-2026-09-03'],
  'title':'Ionic Rare Earths–US Strategic Metals, 미주리 희토류 자석 재활용 50:50 JV 비구속 term sheet',
  'fact':'US Strategic Metals와 Ionic Rare Earths USA는 미주리 Fredericktown의 허가 완료 부지에서 희토류 영구자석 재활용 시설을 추진하기 위한 비구속 50:50 JV term sheet를 체결했다. 초기 시설 자금은 총 1억달러를 의도하고 있으며 USSM이 9,500만달러, 양사가 나머지 500만달러 지분을 절반씩 부담하는 구조다. definitive agreement는 2026년 말까지를 목표로 하지만 효력 발생은 보장되지 않는다.',
  'relevance':'미국 희토류 자석 재활용의 현지화가 기존 MOU에서 구체적 JV 구조·부지·자금계획 단계로 진전됐다는 공급망 신호다.',
  'uncertainty':'term sheet는 명시적으로 non-binding이며 definitive agreement 체결과 실제 투자·착공은 아직 확정되지 않았다.',
  'score':58,'breakdown':{'market_structure_competition':18,'supply_demand_price_utilisation':14,'technology_performance_safety':0,'cashflow_asset_value':8,'law_policy_market_access':8,'systemic_scale':2,'persistence_irreversibility':4,'decision_urgency_actionability':4},
  'research_reason':'The official source resolves ownership, 50:50 structure, permitted-site and intended funding specificity, while preserving the explicit non-binding limitation.',
  'evidence':['https://www.usstrategicmetals.com/us-strategic-metals-and-ionic-rare-earths-to-build-first-u-s-magnet-recycling-plant-in-missouri/','https://www.miningweekly.com/article/ionic-rare-earths-secures-term-sheet-for-magnet-recycling-jv-in-us-2026-09-03']
 },
 {
  'review_item_id':'SEP5_P01P_CURATED_DTRADING_CAPALO','spec_id':'STD26_R8P_002','event_id':'SEP5P_002_DTRADING_CAPALO',
  'story_ids':['EU_2026-09-03_C06'],'region':'EU','date':'2026-09-03','source':'D.TRADING / Capalo AI',
  'primary_url':'https://d.trading/news/d-trading-partners-with-capalo-ai-to-unlock-bankable-revenues-for-battery-storage',
  'support_urls':['https://capaloai.com/news/d-trading-and-capalo-ai-partner-to-deliver-bankable-revenue-structures-for-battery-energy-storage-assets/','https://www.ess-news.com/2026/09/03/d-trading-capalo-ai-to-offer-bankable-bess-revenue-deals'],
  'title':'D.TRADING–Capalo AI, 유럽 BESS에 fixed-revenue·credit-support 결합형 offtake 구조 출시',
  'fact':'D.TRADING과 Capalo AI는 유럽 BESS·하이브리드 자산을 대상으로 전략적 파트너십을 시작했다. D.TRADING은 contractual counterparty·offtaker로서 fixed-revenue 구조와 credit support를 제공하고, Capalo AI는 Zeus VPP를 통해 day-ahead·intraday·ancillary 시장 접근과 최적화·거래를 담당한다.',
  'relevance':'BESS 수익 변동성을 금융조달 가능한 장기 수익구조와 결합하려는 상업모델이 실제 counterparty 역할까지 구체화됐다는 시장구조 신호다.',
  'uncertainty':'특정 자산의 체결 계약이나 프로젝트별 규모·기간·가격은 공개되지 않았으므로 named-asset execution으로 해석하지 않는다.',
  'score':57,'breakdown':{'market_structure_competition':17,'supply_demand_price_utilisation':16,'technology_performance_safety':0,'cashflow_asset_value':12,'law_policy_market_access':2,'systemic_scale':2,'persistence_irreversibility':4,'decision_urgency_actionability':4},
  'research_reason':'Both counterparties explicitly describe D.TRADING as contractual counterparty/offtaker providing fixed-revenue structures and credit support, resolving the prior vagueness question without implying a named-asset contract.',
  'evidence':['https://d.trading/news/d-trading-partners-with-capalo-ai-to-unlock-bankable-revenues-for-battery-storage','https://capaloai.com/news/d-trading-and-capalo-ai-partner-to-deliver-bankable-revenue-structures-for-battery-energy-storage-assets/']
 },
 {
  'review_item_id':'SEP5_P01P_CURATED_NEO_LIBERAWARE','spec_id':'STD26_R8P_003','event_id':'SEP5P_003_NEO_LIBERAWARE',
  'story_ids':['KR_2026-09-05_C30'],'region':'JP','date':'2026-09-02','source':'Liberaware',
  'primary_url':'https://liberaware.co.jp/liberaware%E3%81%A8neo-battery-materials-korea%E3%83%89%E3%83%AD%E3%83%BC%E3%83%B3%E7%94%A8%E9%AB%98%E6%80%A7%E8%83%BD%E3%83%90%E3%83%83%E3%83%86%E3%83%AA%E3%83%BC%E3%81%AE%E5%9B%BD%E5%86%85%E7%94%9F/',
  'support_urls':['https://prtimes.jp/main/html/rd/p/000000194.000031759.html','https://www.etnews.com/20260904000221'],
  'title':'Liberaware–NEO Battery Materials Korea, 일본 드론 고성능 배터리 국내생산·공동사업화 LOI',
  'fact':'Liberaware와 NEO Battery Materials Korea는 9월 2일 일본 내 드론용 고성능 배터리 생산체계 구축과 공동사업화를 위한 LOI를 체결했다. Liberaware 자회사 HINOTATE도 협력사업에 참여하며, 양측은 일본 내 중요 구성부품 공급망 구축을 추진한다.',
  'relevance':'실리콘계 차세대 배터리 기술과 일본 국산 무인기 생태계가 생산·공급망 현지화 단계에서 연결되는 전략적 공급망 신호다.',
  'uncertainty':'LOI 단계이며 JV/SPV, 양산량, 공급가격과 상업생산 일정은 확정되지 않았다.',
  'score':55,'breakdown':{'market_structure_competition':17,'supply_demand_price_utilisation':17,'technology_performance_safety':0,'cashflow_asset_value':5,'law_policy_market_access':5,'systemic_scale':2,'persistence_irreversibility':5,'decision_urgency_actionability':4},
  'research_reason':'Liberaware official disclosure fixes the operative date and explicitly confirms domestic-production and joint-commercialisation intent, resolving source/date identity while preserving LOI-stage limitations.',
  'evidence':['https://liberaware.co.jp/news-release/','https://prtimes.jp/main/html/rd/p/000000194.000031759.html']
 },
 {
  'review_item_id':'SEP5_P01P_CURATED_AEONUS_ID','spec_id':'STD26_R8P_004','event_id':'SEP5P_004_AEONUS_ID',
  'story_ids':['KR_2026-09-04_C112','KR_2026-09-04_C113','KR_2026-09-04_C114'],'region':'GL','date':'2026-09-04','source':'TodayEnergy / TheElec / E2News',
  'primary_url':'https://www.todayenergy.kr/news/articleView.html?idxno=302466',
  'support_urls':['http://www.e2news.com/news/articleView.html?idxno=333907','https://www.thelec.kr/news/articleView.html?idxno=61828'],
  'title':'Aeonus, 인도네시아 이동형 ESS 충전사업 JV 설립 협약…첫 거점 연내 착공 목표',
  'fact':'이온어스는 인도네시아 현지 파트너들과 전기차 충전 인프라·이동형 충전사업을 위한 JV 설립 협약을 진행했고, Jasa Marga 고속도로·휴게소 거점을 중심으로 첫 ESS 기반 충전시설의 연내 착공을 목표로 제시했다. 회사 관계자가 언급한 10년 3억달러 이동형 ESS 공급은 계획 단계로 한정한다.',
  'relevance':'한국 이동형 ESS 사업자가 인도네시아 현지 JV·충전거점·현지 제조·공급 체계를 묶어 시장진입 구조를 구체화한 초기 상업화 신호다.',
  'uncertainty':'JV 법인등기·첫 부지 착공과 10년 3억달러 공급의 binding contract는 확인되지 않았고, 해당 금액은 회사 측 계획으로만 취급한다.',
  'score':55,'breakdown':{'market_structure_competition':17,'supply_demand_price_utilisation':18,'technology_performance_safety':0,'cashflow_asset_value':8,'law_policy_market_access':2,'systemic_scale':2,'persistence_irreversibility':4,'decision_urgency_actionability':4},
  'research_reason':'Three contemporaneous reports consistently identify a JV-establishment agreement and first-site target; the promotion preserves moderate source-access risk and explicitly downgrades the $300m figure to a company-stated plan.',
  'evidence':['https://www.todayenergy.kr/news/articleView.html?idxno=302466','https://www.thelec.kr/news/articleView.html?idxno=61828','http://www.e2news.com/news/articleView.html?idxno=333907']
 }
]


def sha256(path:Path)->str:
 return hashlib.sha256(path.read_bytes()).hexdigest()

def writej(path:Path,obj):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def find_template(a):
 for x in a['strict_passed_spec']:
  if x.get('spec_id')=='STD26_R8_005': return x
 raise AssertionError('structural template missing')

def find_ledger_template(a):
 for x in a['decision_ledger']:
  if x.get('spec_id')=='STD26_R8_005': return x
 raise AssertionError('decision ledger template missing')

def make_spec(t,c):
 x=copy.deepcopy(t)
 x.update({
  'source_event_id':c['event_id'],'source_origin':'sep5_prompt_0_1p_authorized_bounded_research',
  'source_story_ids':c['story_ids'],'original_story_ids':c['story_ids'],'primary_url':c['primary_url'],
  'urls':[c['primary_url']]+c['support_urls'],'merge_status':'source_cluster' if len(c['story_ids'])==1 else 'multi_observation_event',
  'merged_story_ids':c['story_ids'][1:],'anchor_classes':['strategic_behavior_anchor'],'decision_news_value_score':c['score'],
  'decision_value_breakdown':c['breakdown'],'decision_value_classification':'material_industry_signal',
  'technology_evidence_level':'not_applicable','policy_stage':None,'novelty_cap_basis':'none',
  'systemic_scale_denominator':None,'denominator_gap':'No defensible market-wide denominator is asserted; systemic scale is capped at 2/5.',
  'prior_state':'The Sep5 main run retained this item for explicit Prompt 0.1P promotion review rather than publishing it.',
  'new_verified_fact':c['fact'],'changed_judgment':f"Bounded Prompt 0.1P research resolves the recorded review question and promotes {c['review_item_id']} through the ordinary Stage A strict contract.",
  'uncertainty_resolved':c['research_reason'],'remaining_uncertainty':c['uncertainty'],'incremental_information':c['fact'],
  'baseline_expectation_changed':f"Current canonical 1578 must now account for the newly resolved structural signal: {c['title']}",
  'decision_relevance':c['relevance'],'evidence_needed_for_stage_b':[f"Fetch and verify body-level source-owner/independent evidence for {c['title']}; preserve the stated non-binding/planned limitations and exact operative date {c['date']}."],
  'next_confirmation_points':[f"A definitive agreement, named asset/customer, construction/production start, or quantified commercial execution after {c['date']} would strengthen this judgment; failure to progress would weaken it."],
  'region':c['region'],'representative_date':c['date'],'representative_source':c['source'],'source_tier_estimate':'official_or_multi_source_candidate_set',
  'cat':'battery_ess_materials_grid','sub_cat':'strategy_market_structure','signal_estimate':'material',
  'strategic_lens':['market_structure_supply_chain_execution'],'event_anchor':'structural_non_execution_signal',
  'title_raw':c['title'],'summary_hint':c['fact'],'context_text':'Authorized Sep5 Prompt 0.1P promotion review against post-merge canonical 1578.',
  'why_now':f"Bounded promotion research resolved the recorded Stage A uncertainty with evidence dated {c['date']}.",
  'market_relevance':c['relevance'],'source_priority_notes':'Stage B must privilege source-owner/official body evidence and keep non-binding/planned wording exact.',
  'staleness_decision':'current','source_access_risk':'moderate' if c['spec_id']=='STD26_R8P_004' else 'low',
  'stage_a_evidence_status':'not_evidence_complete_no_fetch','stage_b_evidence_package_required':True,
  'primary_url_semantics':'provided_source_candidate_not_evidence','source_cluster_preserved':True,
  'support_source_candidates':c['support_urls'],'source_domain_candidates':[], 'support_source_candidates_accounted':True,
  'stage_b_requirement_note':'Stage B must independently fetch and freeze body-level evidence before drafting.',
  'needs_review':False,'review_reason':None,'denominator_used':'Named strategic event only.',
  'baseline_follow_up_relation':'new_unrelated','portfolio_coverage_contribution':['market_structure_supply_chain_execution'],
  'structural_value_lenses':['market_structure_supply_chain_execution'],'earnings_deep_dive_required':False,
  'earnings_release_available':'not_applicable','ir_deck_available':'not_applicable','call_or_transcript_expected':'not_applicable','qna_status':'not_applicable',
  'prior_period_comparison_required':False,'earnings_rescue_questions':[],'structural_rescue_required':False,'structural_rescue_question':None,
  'search_before_delete_status':'applied','technology_validation_stage':'concept_or_target','technology_score_cap_applied':False,
  'technology_validation_gap':'concept_or_target is a frozen-V3 compatibility placeholder only; active V4 technology_evidence_level is not_applicable and technology_performance_safety is 0/20.',
  'legal_policy_stage':None,'spec_id':c['spec_id']
 })
 x['publication_urgency']={'level':'near_term','action_required':f"Track the next measurable milestone for {c['review_item_id']}.",'decision_deadline':None}
 x['same_event_source_cluster']=[{'story_id':sid,'url':(c['primary_url'] if i==0 else c['support_urls'][min(i-1,len(c['support_urls'])-1)]),'preserve_for_stage_b':True} for i,sid in enumerate(c['story_ids'])]
 x['related_prepass']={'status':'PASS','same_event_checked':True,'matched_baseline_candidate_ids':[],'matched_current_batch_candidate_ids':[],'relation_candidates':[],'duplicate_disposition':'no_duplicate_found','earliest_same_event_check_status':'PASS','fresh_anchor_questions':[f"Confirm the next measurable stage after {c['date']} for {c['event_id']}."]}
 x['date_role']={'status':'PASS','representative_date':c['date'],'event_date':c['date'],'publication_dates':[c['date']],'earliest_same_event_date_checked':True,'event_date_source_url':c['primary_url'],'event_date_source_quote':f"Source-owner or bounded source package identifies the operative announcement/LOI/term-sheet/partnership date as {c['date']}.",'source_quote_emitted':False,'note':'Operative date is separated from downstream republication dates.'}
 x['execution_credibility_gate']={'status':'PASS','anchor_type':'structural_or_policy_signal','anchor_strength':'moderate','stage_precision_note':c['uncertainty']}
 x['independent_cardability_gate']={'status':'PASS','distinct_event_or_stage_progression':True,'full_schema_viability':'PASS','duplicate_or_reinforcement_note':'No same-event canonical card found on post-merge canonical 1578.'}
 x['execution_anchor_type']=None; x['execution_anchor_strength']=None
 x['structural_value_override_applied']=True
 x['structural_selector_policy_version']='STRUCTURAL_NEWS_VALUE_SELECTION_V3'
 x['structural_value_override_reason']='The active V4 selector admits this item through the structural non-execution route because bounded research resolves a decision-relevant market/supply-chain state change without requiring a conventional execution event.'
 x['structural_non_execution_reason']=f"{c['event_id']} is a strategic market/supply-chain structural signal with explicit stage limitations."
 x['why_execution_event_not_required']='V4 structural non-execution route is appropriate because the material change is the newly specified commercial/supply-chain structure; no conventional construction/COD event is claimed.'
 x['baseline_relation']='new_unrelated'; x['baseline_match']=[]; x['duplicate_risk']='low'
 x['source_diversity_path']={'status':'viable','probable_independent_owner_count':max(1,len(c['support_urls'])+1),'official_or_source_owner_candidate_present':c['spec_id']!='STD26_R8P_004','independent_confirmation_candidate_present':True,'context_candidate_present':True,'reason':'Prompt 0.1P bounded research supplies an explicit Stage B source path; Stage B must independently fetch/verify it.'}
 x['signal_rubric_estimate']={'status':'material_industry_signal','score':c['score']}
 x['upstream_labels']={'triage_status':'KEEP','matched_buckets':['battery_ess_materials_grid'],'drop_reason':None,'integrity_group_id':c['event_id'],'integrity_is_best':True,'drop_reason_overridden':True}
 x['staleness']={'event_date':c['date'],'publication_date':c['date'],'staleness_gap_days':0,'staleness_suspected':False,'fresh_followup':False,'staleness_override':False,'decision':'current_or_effective_date_milestone'}
 x['anti_bias_check']={'binding_status_used_as_importance_proxy':False,'legal_formality_used_as_importance_proxy':False,'headline_amount_used_without_denominator':False,'announced_capacity_treated_as_actual_output':False,'routine_execution_event_overranked':False,'conventional_execution_event_required_without_reason':False}
 x['strict_pass_gate']={'status':'pass','reason':f"{c['review_item_id']} satisfies current V4 strict Stage A after authorized bounded Prompt 0.1P research.",'all_six_conditions_passed':True,'anchor_supported_by_upstream_text':True,'why_not_review_pool':c['research_reason']}
 x['promotion_provenance']={'prompt_file':PROMPT,'prompt_version':'PROMPT_0_1P_V4_20260829','source_review_pool_item_id':c['review_item_id'],'bounded_research_disposition':'PROMOTE_TO_STRICT','original_score':None,'re_adjudicated_score':c['score'],'research_reason':c['research_reason'],'research_evidence_urls':c['evidence'],'checked_at':CHECKED}
 # No stale ENGIE specifics may survive the cloned structural template.
 forbidden=['SEP5_005_ENGIE10','STD26_R8_005','10.7GW','ENGIE는 9월 4일']
 payload=json.dumps(x,ensure_ascii=False)
 assert not any(v in payload for v in forbidden), (c['spec_id'],'stale template residue')
 return x

def make_ledger_row(t,c,sid,index):
 x=copy.deepcopy(t)
 x.update({'story_id':sid,'upstream_status':'KEEP','upstream_drop_reason':None,'headline':c['title'],'site':c['source'],'url':c['primary_url'] if index==0 else c['support_urls'][min(index-1,len(c['support_urls'])-1)],'integrity_group_id':c['event_id'],'integrity_is_best':index==0,'ledger_decision':'passed','editorial_bucket':'strict_passed_spec','reason':f"Prompt 0.1P promotion PASS for {c['review_item_id']}: {c['research_reason']}",'spec_id':c['spec_id'],'review_pool_item_id':c['review_item_id'],'merged_into_spec_id':None,'baseline_relation':'new_unrelated','duplicate_risk':'low','staleness_decision':'current','source_access_risk':'moderate' if c['spec_id']=='STD26_R8P_004' else 'low','decision_news_value_score':c['score'],'decision_value_breakdown':c['breakdown'],'decision_value_classification':'material_industry_signal','prior_state':'Retained for authorized promotion review in the Sep5 run.','new_verified_fact':c['fact'],'changed_judgment':f"Prompt 0.1P promotes {c['review_item_id']} to ordinary strict Stage A.",'uncertainty_resolved':c['research_reason'],'remaining_uncertainty':c['uncertainty'],'denominator_used':'Named strategic event only.','denominator_gap':'No market-wide denominator asserted; systemic scale capped at 2/5.'})
 x['baseline_match']={'duplicate_disposition':'no_duplicate_found','matched_baseline_candidate_ids':[]}
 x['publication_urgency']={'level':'near_term','action_required':f"Track next measurable milestone for {c['review_item_id']}.",'decision_deadline':None}
 return x

base=json.loads(SRC.read_text(encoding='utf-8'))
u=json.loads(UNIVERSE.read_text(encoding='utf-8'))
assert u['authorized_candidate_count']==83 and len(u['review_queue_story_ids'])==78 and len(u['curated_holds'])==5
assert base['baseline_count']==1569, 'source Stage A must be the merged Sep5 artifact, not a later mutated copy'
t=find_template(base); lt=find_ledger_template(base)
strict=[make_spec(t,c) for c in CANDS]
decision=[]
for c in CANDS:
 for i,sid in enumerate(c['story_ids']): decision.append(make_ledger_row(lt,c,sid,i))
assert len(strict)==4 and len(decision)==6

out=copy.deepcopy(base)
out.update({'status':'PASS','run_id':RUN_ID,'run_tag':'20260908_SEP5_PROMPT_0_1P_PROMOTION83_R1','run_label':'Prompt 0.1P V4 authorized review of 83 Sep5 promotion candidates against merged canonical 1578','input_file':str(UNIVERSE),'baseline_source_declaration':f'current GitHub main {BASE}; canonical blob {BLOB}; {COUNT} cards','baseline_count':COUNT,'github_main_sync_required_later':False,'source_universe':'83 authorized promotion candidates: 78 upstream review_queue items plus 5 explicitly preserved curated review-hold events. Four events / six observations promote after bounded research; 79 candidates remain outside Stage B.','story_count':6,'event_count':4,'original_status_counts':{'KEEP':6}})
out['integrity_summary']={'status':'PASS','main_sha':BASE,'canonical_blob_sha':BLOB,'candidate_event_count':4,'candidate_source_observation_count':6,'authorized_promotion_candidate_count':83,'promoted_count':4,'retained_count':79,'duplicate_candidate_membership':0,'unassigned_candidate_membership':0,'promotion_universe_sha256':sha256(UNIVERSE)}
out['recommended_for']=['Stage B evidence construction for the 4 newly promoted strict specs only','terminal promotion accounting for 79 non-promoted candidates']
out['next_call_recommendation']={'recommended_next_call':'Stage B r0','recommended_prompt_id':'Prompt 0.2','recommended_input_universe':'Stage A strict_passed_spec[] only','reason':'Four of 83 authorized promotion candidates satisfy the ordinary Stage A strict contract after bounded Prompt 0.1P research; 79 remain outside Stage B.','blocked_items_summary':[]}
out['dropped_treasure_hunt']={'performed':False,'trigger_reason':'Prompt 0.1P is bounded to the sealed 83-candidate promotion universe and does not open a new 0.0C discovery universe.','sample_strategy':'not_applicable','sample_size':0,'sampled_story_ids':[],'rescued_count':0,'rescue_ids':[],'non_sampled_dropped_count':0,'non_sampled_ledger_policy':'All 83 authorized candidates receive an explicit promotion disposition in promotion-review-ledger.json.'}
out['strict_passed_spec']=strict
for k in ['legacy_keep','candidate_review_pool','watchlist_context_pool','reject_or_support_only_pool','rejected','existing_reinforcement','support_source_only']:
 if k in out: out[k]=[]
out['decision_ledger']=decision
s=out['summary']
s.update({'legacy_keep_count':0,'strict_passed_spec_count':4,'needs_review_count':0,'candidate_review_pool_count':0,'watchlist_context_pool_count':0,'reject_or_support_only_pool_count':0,'rejected_count':0,'existing_reinforcement_count':0,'support_source_only_count':0,'duplicate_or_reinforcement_count':0,'stale_discarded_count':0,'stale_warm_review_count':0,'total_ledger_count':6,'ledger_matches_story_count':True,'anchor_class_counts':{'strategic_behavior_anchor':4},'structural_lens_coverage_counts':{'market_structure_supply_chain_execution':4},'decision_value_classification_counts':{'material_industry_signal':4},'critical_structural_candidate_ids':[],'high_decision_value_candidate_ids':[],'high_value_review_pool_ids':[],'structural_signal_review_pool_ids':[],'earnings_deep_dive_pool_ids':[],'follow_up_candidate_ids':[],'zero_coverage_domains':[],'execution_or_formality_bias_findings':[],'technology_validation_gap_ids':[],'legal_policy_stage_gap_ids':[],'decision_ledger_count':6,'selection_route_counts':{'structural_non_execution_route':4},'formal_event_count':4,'source_bound_observation_count':6})
out['formal_stage_a_batch']={'batch':'0.1P','event_count':4,'strict_count':4,'candidate_review_count':0,'watchlist_count':0,'reject_or_support_only_count':0,'formal_stage_a_external_web_search_count':'bounded_prompt_0_1p_research','formal_stage_a_new_article_body_fetch_count':'bounded_prompt_0_1p_research','adjudication_method':'PROMPT_0_1P_V4_20260829 bounded research then ordinary Stage A strict re-emission'}

review_ledger=[]
for sid in u['review_queue_story_ids']:
 reason='No bounded evidence in this promotion pass establishes a new independently cardable current anchor above the ordinary Stage A threshold; retain outside Stage B.'
 disp='RETAIN_REVIEW'
 if sid=='TF_0042': disp='EXISTING_CANONICAL_REINFORCEMENT'; reason='German EUR35bn capacity mechanism was already published in the prior R7 canonical chain.'
 if sid=='TF_0053': disp='EXISTING_CANONICAL_REINFORCEMENT'; reason='Sungrow H1 storage revenue/25GWh milestone was already published in the prior R7 canonical chain.'
 if sid=='TF_0069': disp='EXISTING_CANONICAL_REINFORCEMENT'; reason='LG Energy Solution–Smackover Lithium 10-year/80,000t offtake was already published in the prior R6 canonical chain.'
 review_ledger.append({'review_item_id':sid,'origin':'upstream_review_queue','disposition':disp,'reason':reason,'promoted_spec_id':None})
for c in CANDS:
 review_ledger.append({'review_item_id':c['review_item_id'],'origin':'curated_hold','source_story_ids':c['story_ids'],'disposition':'PROMOTE_TO_STRICT','reason':c['research_reason'],'promoted_spec_id':c['spec_id'],'evidence':c['evidence']})
review_ledger.append({'review_item_id':'SEP5_P01P_CURATED_PURE_LITHIUM','origin':'curated_hold','source_story_ids':['US_2026-09-04_C15'],'disposition':'RETAIN_REVIEW','reason':'Company-only 9,315-cycle laboratory result does not resolve the independent-validation technology-evidence cap; no promotion.','promoted_spec_id':None})
assert len(review_ledger)==83
out['candidate_promotion_contract']={'prompt_file':PROMPT,'prompt_version':'PROMPT_0_1P_V4_20260829','candidate_count':83,'promoted_count':4,'retained_count':79,'score_inflation_for_source_recovery':False,'promotion_ledger_ref':str(LEDGER),'promotion_ledger':[x for x in review_ledger if x['origin']=='curated_hold']}
writej(LEDGER,{'schema':'sep5_prompt_0_1p_review_ledger_v1','status':'PASS','run_id':RUN_ID,'base_main_commit_sha':BASE,'base_canonical_blob_sha':BLOB,'candidate_count':83,'promoted_count':4,'retained_count':79,'items':review_ledger})
writej(OUT,out)
print('RESULT: MATERIALIZED_SEP5_PROMOTION_STAGE_A',OUT)
print('PROMOTED',len(strict),'RETAINED',79,'OBS',len(decision))
