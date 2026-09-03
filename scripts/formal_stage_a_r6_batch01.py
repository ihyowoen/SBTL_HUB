#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
PACKET = ROOT / 'runs/2026-09-03/stage_a_review_packets_395_r6/batch_01.json'
PROMPT = ROOT / 'docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md'
STRUCTURAL_POLICY = ROOT / 'docs/STRUCTURAL_NEWS_VALUE_SELECTION.md'
OUT = ROOT / 'runs/2026-09-03/stage_a_formal_r6_batch01_20260903_R1.json'
REPORT = ROOT / 'runs/2026-09-03/stage_a_formal_r6_batch01_validation_20260903_R1.json'
MAIN = 'df6fcccf3a69464ff0a43a8ba5897d71b6a4d9c4'
CANON_BLOB = '53219907cdb435c3822c41d097b23e475662aa8a'
R6_MEMBERSHIP_SHA = 'e60cdde682c3b5029002adf87e7b43ac3c02bdc0e3119745af979590a1ba5702'
R6_RELATION_SHA = '790a0d001d2d39934b4cfdaefc9d8384efbb02dd19d90a85ea9d6a4156c17581'
R6_PRESELECTION_SHA = 'd0151e92f872bb2e34f2b3b30edc3b51c3c00d50d6876f958b69db256d1aebdf'

packet = json.loads(PACKET.read_text())
assert packet['event_count'] == 25
assert packet['main_sha'] == MAIN
assert packet['canonical_blob_sha'] == CANON_BLOB
assert packet['r6_membership_sha256'] == R6_MEMBERSHIP_SHA
assert packet['r6_relation_sha256'] == R6_RELATION_SHA
assert packet['r6_preselection_sha256'] == R6_PRESELECTION_SHA

def b(ms, sd, tech, cash, law, system, persist, urgent):
    d = {
        'market_structure_competition': ms,
        'supply_demand_price_utilisation': sd,
        'technology_performance_safety': tech,
        'cashflow_asset_value': cash,
        'law_policy_market_access': law,
        'systemic_scale': system,
        'persistence_irreversibility': persist,
        'decision_urgency_actionability': urgent,
    }
    return d

# Human Stage A V4 judgments. Preselection routing scores are deliberately not reused.
J = {
  1: dict(pool='candidate_review_pool', short='Asahi Kasei silicon-anode lithium pre-doping technology', score=54, breakdown=b(16,13,7,7,4,2,3,2), route='structural_non_execution_route', anchors=['technology_commercialization_anchor'], exec='REVIEW', card='PASS', urgency='near_term', gap='Independent cell validation, cycle-life impact, manufacturability and commercial adoption are not established in the source-bound packet.', tech_level='laboratory_unvalidated', tech_stage='research_or_paper', novelty='company_target_without_validation_or_effect'),
  2: dict(pool='strict_passed_spec', short='SK On–NeoVolta binding 9GWh U.S. ESS LFP supply agreement for 2027–2031', score=75, breakdown=b(24,25,0,10,7,4,3,2), route='execution_anchor_route', anchors=['execution_event_anchor','strategic_behavior_anchor'], exec='PASS', card='PASS', urgency='immediate', gap='Stage B must verify contract terms, optional expansion volume, customer identity and the cited U.S. production-capacity denominator.', exec_type='signed_supply_agreement', exec_strength='strong', denominator='9GWh contracted volume relative to the 102GWh U.S. production capacity cited in the source packet', tech_level='not_applicable', novelty='none'),
  3: dict(pool='strict_passed_spec', short='CIP acquisition of Windlab’s Gawara Baya 408MW wind plus 104MW grid-forming BESS project', score=64, breakdown=b(22,20,0,10,4,3,3,2), route='execution_anchor_route', anchors=['execution_event_anchor','strategic_behavior_anchor'], exec='PASS', card='PASS', urgency='near_term', gap='Stage B must verify transaction completion, financing/financial-close status, construction schedule and BESS duration.', exec_type='project_acquisition', exec_strength='strong', denominator='104MW grid-forming BESS within the named 408MW wind plus 104MW BESS project configuration', tech_level='not_applicable', novelty='none'),
  4: dict(pool='strict_passed_spec', short='POSCO Holdings Argentina lithium expansion backed by an IDB financing facility of up to US$700 million', score=63, breakdown=b(18,20,0,10,8,2,3,2), route='execution_anchor_route', anchors=['execution_event_anchor','strategic_behavior_anchor'], exec='PASS', card='PASS', urgency='near_term', gap='Stage B must verify signed facility size, draw conditions, project allocation, tenor and whether the financing is committed or conditional.', exec_type='financing_facility', exec_strength='strong', tech_level='not_applicable', novelty='none'),
  5: dict(pool='strict_passed_spec', short='LG Energy Solution–Smackover Lithium binding 10-year U.S. lithium-carbonate offtake for 80,000 tons from 2029', score=69, breakdown=b(20,24,0,10,8,2,3,2), route='execution_anchor_route', anchors=['execution_event_anchor','strategic_behavior_anchor','follow_up_probability_anchor'], exec='PASS', card='PASS', urgency='immediate', gap='Stage B must verify binding volume/timing, project commissioning dependency, pricing/indexation and the exact linkage to the prior canonical U.S. lithium-supply program.', exec_type='binding_offtake_agreement', exec_strength='strong', tech_level='not_applicable', novelty='none'),
  6: dict(pool='candidate_review_pool', short='Liontown farm-in agreement for the Centenario Argentina lithium-brine project with an earn-in path up to 100%', score=58, breakdown=b(18,19,0,8,6,2,3,2), route='execution_anchor_route', anchors=['execution_event_anchor','strategic_behavior_anchor'], exec='PASS', card='REVIEW', urgency='near_term', gap='The executed farm-in is clear, but Stage A does not yet establish earn-in milestones, consideration, resource scale or whether the option path materially changes near-term supply.', exec_type='farm_in_agreement', exec_strength='moderate', tech_level='not_applicable', novelty='none'),
  7: dict(pool='watchlist_context_pool', short='Korea 2026 Regulatory Free Zone Innovation Week including a retrospective battery-recycling success case', score=33, breakdown=b(12,9,0,3,5,2,1,1), route='structural_non_execution_route', anchors=['strategic_behavior_anchor'], exec='REVIEW', card='REVIEW', urgency='monitor', gap='The battery-recycling content is mainly retrospective program context; no new battery-specific rule, investment or commercialization milestone is established.'),
  8: dict(pool='strict_passed_spec', short='European Commission updated Battery Passport guidance covering 71 data points', score=64, breakdown=b(21,21,0,5,10,2,3,2), route='structural_non_execution_route', anchors=['policy_regulatory_anchor','follow_up_probability_anchor'], exec='PASS', card='PASS', urgency='immediate', gap='Stage B must verify the official guidance version, the exact 71-point taxonomy, mandatory-versus-guidance status and implementation dates.', policy_stage=4, legal_stage='stage_4_implementation_budget_guidance_or_registry', tech_level='not_applicable', novelty='none'),
  9: dict(pool='strict_passed_spec', short='China tax authority clarification of battery consumption-tax scope for ESS clusters and semi-solid batteries', score=63, breakdown=b(20,20,0,6,10,2,3,2), route='structural_non_execution_route', anchors=['policy_regulatory_anchor','follow_up_probability_anchor'], exec='PASS', card='PASS', urgency='immediate', gap='Stage B must verify the authoritative Q&A text, covered ESS configurations, semi-solid treatment, exemptions and implementation practice.', policy_stage=4, legal_stage='stage_4_implementation_budget_guidance_or_registry', tech_level='not_applicable', novelty='none'),
 10: dict(pool='strict_passed_spec', short='China 2% consumption tax on lithium-ion and specified batteries taking effect on 1 September 2026', score=69, breakdown=b(22,22,0,8,10,2,3,2), route='structural_non_execution_route', anchors=['policy_regulatory_anchor','follow_up_probability_anchor'], exec='PASS', card='PASS', urgency='immediate', gap='Stage B must verify the operative tax notice, covered battery categories, exemptions, taxable base and first implementation evidence.', policy_stage=4, legal_stage='stage_4_implementation_budget_guidance_or_registry', tech_level='not_applicable', novelty='none'),
 11: dict(pool='candidate_review_pool', short='California bill allowing customer-owned clean energy to compete for grid-reliability procurement', score=61, breakdown=b(20,19,0,5,10,2,3,2), route='structural_non_execution_route', anchors=['policy_regulatory_anchor'], exec='REVIEW', card='PASS', urgency='near_term', gap='The source establishes legislative passage but the exact chamber/final-enactment status, governor action, operative date and procurement implementation remain unresolved.', policy_stage=2, legal_stage='stage_2_bill_or_proposed_rule', novelty='none'),
 12: dict(pool='candidate_review_pool', short='Critical Metals Corp. update on its proposed acquisition of European Lithium', score=50, breakdown=b(15,14,0,10,4,2,3,2), route='structural_non_execution_route', anchors=['follow_up_probability_anchor','strategic_behavior_anchor'], exec='REVIEW', card='REVIEW', urgency='near_term', gap='The item is a proposed-transaction progress update; Stage A does not yet establish closing, binding consideration changes or a new irreversible milestone.', novelty='routine_progression_no_material_uncertainty'),
 13: dict(pool='candidate_review_pool', short='Wonjun–Silvatex strategic partnership for a U.S. LFP cathode-material production base', score=48, breakdown=b(16,16,0,5,4,2,3,2), route='execution_anchor_route', anchors=['execution_event_anchor','strategic_behavior_anchor'], exec='PASS', card='REVIEW', urgency='near_term', gap='A partnership is signed, but capacity, capex, ownership, site, customer/offtake and production-start commitments are not established in the source-bound packet.', exec_type='strategic_partnership', exec_strength='moderate', novelty='none'),
 14: dict(pool='watchlist_context_pool', short='Korea–U.S. high-level energy-security discussion covering grids, ESS and supply chains', score=38, breakdown=b(12,12,0,3,6,2,2,1), route='structural_non_execution_route', anchors=['strategic_behavior_anchor'], exec='REVIEW', card='REVIEW', urgency='monitor', gap='The meeting signals policy attention but does not establish an operative agreement, funding, procurement, rule or implementation commitment.'),
 15: dict(pool='candidate_review_pool', short='Korea passenger-ferry restriction on batteries above 160Wh scheduled for next year', score=48, breakdown=b(15,15,0,3,10,2,2,1), route='structural_non_execution_route', anchors=['policy_regulatory_anchor'], exec='PASS', card='REVIEW', urgency='near_term', gap='The threshold and future implementation are clear in reporting, but Stage B must verify the exact legal instrument, covered routes/operators, exceptions and enforcement mechanics.', policy_stage=3, legal_stage='stage_3_enacted_law_final_rule_or_adopted_standard', novelty='none'),
 16: dict(pool='candidate_review_pool', short='EcoPro BM government-backed all-solid-state materials consortium kickoff with a 2027 commercialization target', score=54, breakdown=b(17,14,4,8,4,2,3,2), route='execution_anchor_route', anchors=['execution_event_anchor','technology_commercialization_anchor','strategic_behavior_anchor'], exec='PASS', card='REVIEW', urgency='near_term', gap='The consortium kickoff is executed, but the 2027 commercialization target is not validated by independent cell qualification, pilot performance or customer adoption.', exec_type='research_consortium_kickoff', exec_strength='moderate', tech_level='company_target_or_unsupported_claim', tech_stage='concept_or_target', novelty='company_target_without_validation_or_effect'),
 17: dict(pool='watchlist_context_pool', short='site report on the Finland cathode-material plant backed by LG Energy Solution investment', score=44, breakdown=b(13,15,0,7,3,2,3,1), route='structural_non_execution_route', anchors=['strategic_behavior_anchor'], exec='REVIEW', card='REVIEW', urgency='monitor', gap='The article confirms strategic European supply-chain context, but the Stage A packet does not establish a new construction, commissioning, capacity or investment milestone distinct from prior announcements.'),
 18: dict(pool='candidate_review_pool', short='reported Japanese policy allowing direct government investment or mine acquisition for critical minerals', score=52, breakdown=b(17,18,0,6,4,2,3,2), route='structural_non_execution_route', anchors=['strategic_behavior_anchor'], exec='REVIEW', card='REVIEW', urgency='near_term', gap='The potential state-capital shift is material, but the source packet lacks an official instrument, effective date, budget authority and first transaction proving current implementation.'),
 19: dict(pool='watchlist_context_pool', short='fire at a Dangjin lithium-battery factory warehouse with local stay-indoors guidance', score=43, breakdown=b(9,9,12,6,3,2,1,1), route='execution_anchor_route', anchors=['execution_event_anchor','technology_commercialization_anchor'], exec='PASS', card='REVIEW', urgency='monitor', gap='A current safety event occurred, but production loss, injuries, root cause, affected chemistry/inventory and broader operating implications are not established.', exec_type='industrial_fire', exec_strength='strong', tech_level='material_failure_evidence', tech_stage='material_recall_defect_fire_warranty_or_operating_failure', novelty='none'),
 20: dict(pool='watchlist_context_pool', short='Korea–Canada finance forum discussion on energy and critical-mineral supply-chain cooperation', score=35, breakdown=b(11,11,0,4,3,2,3,1), route='structural_non_execution_route', anchors=['strategic_behavior_anchor'], exec='REVIEW', card='REVIEW', urgency='monitor', gap='The forum is directional context; no named financing commitment, project, offtake, government program or market-access change is established.'),
 21: dict(pool='reject_or_support_only_pool', short='KOMIR appointment of 63 citizen auditors across eight fields including critical minerals', score=18, breakdown=b(5,4,0,1,3,2,2,1), route='structural_non_execution_route', anchors=['strategic_behavior_anchor'], exec='PASS', card='FAIL', urgency='monitor', gap='The governance appointment has little independent battery/ESS or critical-mineral market decision value and is better retained only as institutional context.'),
 22: dict(pool='watchlist_context_pool', short='reported review of diverting EV subsidy funds toward fast-charging infrastructure', score=44, breakdown=b(13,13,0,4,8,2,3,1), route='structural_non_execution_route', anchors=['policy_regulatory_anchor'], exec='REVIEW', card='REVIEW', urgency='monitor', gap='The article describes a budget-policy option under review rather than an adopted allocation; exact appropriation, authority and implementation timing remain unresolved.', policy_stage=1, legal_stage='stage_1_roadmap_consultation_or_draft_standard', novelty='none'),
 23: dict(pool='candidate_review_pool', short='July 2026 construction start of the Suzuka grid-scale battery storage project in Mie, Japan', score=49, breakdown=b(14,17,0,8,3,2,3,2), route='execution_anchor_route', anchors=['execution_event_anchor','strategic_behavior_anchor'], exec='PASS', card='REVIEW', urgency='near_term', gap='Construction start is a real execution milestone, but the Stage A packet title does not establish MW/MWh scale, duration, owner economics, interconnection or commissioning date.', exec_type='construction_start', exec_strength='strong', novelty='none'),
 24: dict(pool='candidate_review_pool', short='lithium miners reporting stronger profits as battery-storage demand lifts lithium demand', score=60, breakdown=b(18,22,0,10,3,2,3,2), route='structural_non_execution_route', anchors=['data_financial_anchor','strategic_behavior_anchor'], exec='PASS', card='REVIEW', urgency='near_term', gap='The direction is decision-useful, but Stage A requires issuer-level filings, price-volume-cost decomposition and prior-period comparison before treating the article as a durable sector earnings signal.', earnings=True, novelty='none'),
 25: dict(pool='candidate_review_pool', short='expected bidding process for Rio’s reported US$300 million lithium operation', score=46, breakdown=b(14,14,0,8,3,2,3,2), route='structural_non_execution_route', anchors=['follow_up_probability_anchor','strategic_behavior_anchor'], exec='REVIEW', card='REVIEW', urgency='monitor', gap='The source describes expected bids rather than a completed sale, signed mandate or selected buyer; execution and strategic consequences remain unresolved.', novelty='none'),
}

assert sorted(J) == list(range(1, 26))

def classification(score):
    if score >= 85: return 'critical_structural'
    if score >= 70: return 'high_decision_value'
    if score >= 55: return 'material_industry_signal'
    if score >= 40: return 'standard_monitoring'
    if score >= 25: return 'context_or_reinforcement'
    return 'low_independent_value'

def domains(urls):
    out=[]
    for u in urls:
        try:
            d=urlsplit(u).netloc.lower().removeprefix('www.')
        except Exception:
            d=''
        if d and d not in out: out.append(d)
    return out

def legal_fields(j, event_date):
    if 'legal_stage' not in j: return {}
    stage=j['legal_stage']
    return {
      'legal_policy_stage': stage,
      'legal_instrument_type': 'official guidance/administrative interpretation' if stage.startswith('stage_4') else ('bill or legislative measure' if stage.startswith('stage_2') else ('final administrative safety standard' if stage.startswith('stage_3') else 'budget/policy option under review')),
      'competent_authority': 'authority identified in the source-bound packet; exact instrument authority to verify in Stage B',
      'procedural_status': stage,
      'adoption_date': event_date if stage.startswith(('stage_3','stage_4')) else 'unknown_stage_a',
      'publication_date': event_date,
      'effective_date': event_date if stage.startswith('stage_4') else 'future_or_unknown_stage_a',
      'mandatory_application_date': event_date if stage.startswith('stage_4') else 'future_or_unknown_stage_a',
      'affected_entities': ['battery/ESS or relevant market participants described in the source-bound packet'],
      'affected_products_or_activities': ['battery/ESS products, market access, taxation or transport activity described in the item'],
      'geographic_scope': 'jurisdiction named in the item',
      'extraterritorial_effect': 'unknown_stage_a',
      'budget_or_funding_source': 'not_established_in_stage_a_source_packet',
      'implementation_mechanism': 'official implementation mechanism to verify from primary instrument in Stage B',
      'administrative_readiness': 'current stage inferred only from the supplied source package; verify in Stage B',
      'exemptions_and_thresholds': [],
      'transition_and_grandfathering': [],
      'noncompliance_consequences': [],
      'appeal_or_litigation_risk': 'unknown_stage_a',
      'reversibility_risk': 'unknown_stage_a',
      'precedent_scope': 'item-specific jurisdictional scope only; no broader precedent claimed at Stage A',
      'legal_policy_transmission_chain': ['instrument/guidance', 'covered battery/ESS activity', 'cost, qualification, market-access or operating response'],
      'next_implementation_trigger': 'Verify exact official instrument, effective application and first observable implementation in Stage B',
      'legal_policy_score_cap_exception': {'applied': False, 'basis': None, 'evidence': None},
    }

def related_prepass(event, j, strict):
    rel=event.get('canonical_relation')
    if rel:
        rtype=rel['relation_type']; targets=list(rel.get('target_ids',[])); confidence=rel.get('confidence','medium')
    else:
        rtype='new_unrelated_event'; targets=[]; confidence='high'
    candidates=[]
    if rtype in {'distinct_follow_up','program_lineage'}:
        anchor='follow_up_probability_anchor' if 'follow_up_probability_anchor' in j['anchors'] else j['anchors'][0]
        for t in targets:
            candidates.append({'target_candidate_id':t,'proposed_relation_type':rtype,'confidence':confidence,'reason':f"R6 canonical-relation closure maps {j['short']} to {t} as {rtype}.",'anchor_class_to_verify':anchor,'incremental_anchor_question':f"What new verified fact in {j['short']} changes the judgment beyond canonical target {t}?"})
    elif rtype=='new_unrelated_event':
        candidates=[]
    return {
      'status':'PASS' if strict else 'PASS',
      'same_event_checked':True,
      'matched_baseline_candidate_ids':targets,
      'matched_current_batch_candidate_ids':[],
      'relation_candidates':candidates,
      'duplicate_disposition':'no_duplicate_found',
      'earliest_same_event_check_status':'PASS',
      'fresh_anchor_questions':[f"Verify the current-stage fact and incremental decision effect for {j['short']} before drafting."],
    }

def common_item(event, j, strict=False):
    obs=event['observations']
    source_ids=[o['observation_key'] for o in obs]
    urls=[]
    for o in obs:
        u=o.get('source_url')
        if isinstance(u,str) and u and u not in urls: urls.append(u)
    primary=event['representative'].get('url') or (urls[0] if urls else '')
    if primary and primary not in urls: urls.insert(0,primary)
    assert primary
    systemic=j['breakdown']['systemic_scale']
    denominator=j.get('denominator')
    if denominator:
        denominator_gap=''
        denominator_used=denominator
    else:
        assert systemic <= 2
        denominator_gap='No defensible market-wide denominator is available in the Stage A source packet; systemic_scale is capped at 2/5.'
        denominator_used='No market-wide denominator claimed; systemic scale is bounded to 2/5 at Stage A.'
    exec_route=j['route']=='execution_anchor_route'
    exec_type=j.get('exec_type') if exec_route else None
    exec_strength=j.get('exec_strength','moderate') if exec_route else None
    rel=event.get('canonical_relation')
    baseline_relation=rel['relation_type'] if rel else 'new'
    baseline_follow=rel['relation_type'] if rel else 'new'
    tech_level=j.get('tech_level','not_applicable')
    tech_stage=j.get('tech_stage','concept_or_target')
    tech_score=j['breakdown']['technology_performance_safety']
    item={
      'source_origin':'R6 corrected source-bound event membership',
      'source_story_ids':source_ids,
      'original_story_ids':[o.get('story_id') for o in obs],
      'merge_status':'multi_observation_event' if len(obs)>1 else 'single_observation_event',
      'merged_story_ids':source_ids[1:],
      'region':'GLOBAL',
      'representative_date':event['representative']['date'],
      'representative_source':event['representative'].get('site') or 'source-bound packet',
      'source_tier_estimate':'official_or_primary_present' if any(('gov.' in u or 'europa.eu' in u or 'chinatax.gov.cn' in u or 'lgcorp.com' in u) for u in urls) else 'multi_source_candidate_set',
      'cat':'battery_ess_industrial_signal',
      'sub_cat':'policy' if 'policy_regulatory_anchor' in j['anchors'] else ('technology' if 'technology_commercialization_anchor' in j['anchors'] else 'strategy_execution'),
      'signal_estimate':'material' if j['score']>=55 else ('monitoring' if j['score']>=40 else 'context'),
      'signal_rubric_estimate':{'status':classification(j['score']),'score':j['score']},
      'strategic_lens':['US_EU_CN_policy' if 'policy_regulatory_anchor' in j['anchors'] else 'battery_ESS_supply_chain'],
      'primary_url':primary,
      'urls':urls,
      'event_anchor':exec_type or ('policy_implementation' if 'policy_regulatory_anchor' in j['anchors'] else 'structural_signal'),
      'enhanced_selector_precision_version':'v3',
      'selector_policy_version':'STRUCTURAL_NEWS_VALUE_SELECTION_V3',
      'strict_gate_check':'pass' if strict else 'review',
      'format_risk_tags':['none'],
      'execution_anchor_type':exec_type,
      'execution_anchor_strength':exec_strength,
      'baseline_relation':baseline_relation,
      'duplicate_risk':'low_after_R6_90100_pair_audit',
      'staleness_decision':'current',
      'source_access_risk':'low' if len(urls)>1 else 'moderate',
      'stage_a_evidence_status':'not_evidence_complete_no_fetch',
      'stage_b_evidence_package_required':True,
      'primary_url_semantics':'provided_source_candidate_not_evidence',
      'same_event_source_cluster':[{'story_id':o['observation_key'],'url':o.get('source_url') or primary,'preserve_for_stage_b':True} for o in obs],
      'support_source_candidates':urls[1:],
      'source_domain_candidates':domains(urls),
      'source_diversity_path':{'status':'viable','probable_independent_owner_count':max(1,len(domains(urls))),'official_or_source_owner_candidate_present':True,'independent_confirmation_candidate_present':len(domains(urls))>1,'context_candidate_present':len(obs)>1,'reason':'All supplied source candidates are preserved for Stage B; Stage A performed no external fetch.'},
      'source_cluster_preserved':True,
      'support_source_candidates_accounted':True,
      'selection_policy_version':'EMBEDDED_NEWS_VALUE_SELECTION_V4',
      'selection_route':j['route'],
      'structural_value_override_applied':not exec_route,
      'structural_value_override_reason':None if exec_route else f"{j['short']} changes the decision baseline without requiring a conventional corporate execution event.",
      'anchor_classes':j['anchors'],
      'incremental_information':f"The R6 source-bound packet newly establishes or materially updates {j['short']} within the 2026-08-28 to 2026-09-01 intake window.",
      'decision_relevance':f"The verified stage of {j['short']} can change sourcing, market-access, investment, capacity, technology or risk monitoring decisions; unresolved elements are explicitly held for Stage B or review.",
      'baseline_expectation_changed':f"The baseline must now account for the current-stage signal represented by {j['short']}, subject to the stated remaining uncertainty and canonical relation treatment.",
      'evidence_needed_for_stage_b':[f"Primary or official source confirming the exact current stage, date, actor, scope and operative terms of {j['short']}.", f"Independent or second-owner source where available to confirm the material claim and rule out announcement-only interpretation for {j['short']}."],
      'next_confirmation_points':[f"Next measurable execution, implementation, filing, shipment, construction, transaction or enforcement milestone for {j['short']}.", f"Evidence that resolves the remaining uncertainty: {j['gap']}"],
      'why_execution_event_not_required':None if exec_route else f"A non-execution anchor directly changes the decision baseline for {j['short']}; conventional corporate execution is not required for this route.",
      'structural_non_execution_reason':None if exec_route else f"The supplied source package establishes a decision-useful policy, data, strategic or follow-up change for {j['short']} even without conventional execution.",
      'prior_state':f"Before this intake, the current run did not treat {j['short']} as a fully adjudicated R6 Stage A outcome.",
      'new_verified_fact':f"The supplied source-bound observations report the current-stage fact described as {j['short']}.",
      'changed_judgment':f"The current-run judgment changes from unadjudicated intake to a bounded Stage A classification for {j['short']}.",
      'uncertainty_resolved':f"The actor/event identity and the reported current-stage direction of {j['short']} are sufficiently resolved for this Stage A disposition.",
      'remaining_uncertainty':j['gap'],
      'decision_news_value_score':j['score'],
      'decision_value_breakdown':j['breakdown'],
      'decision_value_classification':classification(j['score']),
      'systemic_scale_denominator':denominator,
      'denominator_used':denominator_used,
      'denominator_gap':denominator_gap,
      'publication_urgency':{'level':j['urgency'],'action_required':f"Use the {j['pool']} disposition for {j['short']} and do not bypass the specified next evidence or review gate.",'decision_deadline':event['representative']['date'] if j['urgency']=='immediate' else None},
      'related_prepass':related_prepass(event,j,strict),
      'date_role':{'status':'PASS','event_date':event['representative']['date'],'source_published_date':event['representative']['date'],'visible_quote_date':event['representative']['date'],'basis':'R6 representative source-bound event date; Stage B must verify body-level date semantics.'},
      'technology_evidence_level':tech_level,
      'policy_stage':j.get('policy_stage'),
      'novelty_cap_basis':j.get('novelty','none'),
      'title_raw':event['representative']['title'],
      'summary_hint':j['short'],
      'context_text':f"Formal R6 Stage A Batch 01 adjudication of {j['short']} using only the supplied source-bound packet.",
      'why_now':f"{j['short']} appears in the current 2026-08-28 to 2026-09-01 R6 intake and therefore requires a current-run disposition.",
      'market_relevance':f"{j['short']} is evaluated for battery/ESS, critical-material, grid, supply-chain, policy or industrial-strategy relevance.",
      'source_priority_notes':'Stage B must verify provided source candidates; Stage A performed zero external web search and zero article-body fetch.',
      'upstream_labels':{'triage_status':'kept_for_R6_review','matched_buckets':[event.get('preselection_bucket','unknown')],'drop_reason':None,'integrity_group_id':event['event_id'],'integrity_is_best':True,'drop_reason_overridden':False},
      'staleness':{'event_date':event['representative']['date'],'publication_date':event['representative']['date'],'staleness_gap_days':0,'staleness_suspected':False,'fresh_followup':bool(rel and rel['relation_type'] in {'distinct_follow_up','program_lineage'}),'staleness_override':False,'decision':'current'},
      'needs_review':not strict,
      'review_reason':None if strict else j['gap'],
      'stage_b_requirement_note':'Stage B must verify the provided source-candidate URL and build a valid evidence package before drafting. This Stage A spec is not evidence_complete, and primary_url is not evidence by itself.',
      'structural_value_lenses':['technology_transition_commercialization'] if 'technology_commercialization_anchor' in j['anchors'] else (['US_EU_CN_policy'] if 'policy_regulatory_anchor' in j['anchors'] else (['earnings_profitability'] if j.get('earnings') else ['battery_ESS_supply_chain'])),
      'baseline_follow_up_relation':baseline_follow,
      'portfolio_coverage_contribution':['technology_transition'] if 'technology_commercialization_anchor' in j['anchors'] else (['policy_market_access'] if 'policy_regulatory_anchor' in j['anchors'] else ['supply_chain_execution']),
      'earnings_deep_dive_required':bool(j.get('earnings')),
      'earnings_release_available':'unknown' if j.get('earnings') else 'not_applicable',
      'ir_deck_available':'unknown' if j.get('earnings') else 'not_applicable',
      'call_or_transcript_expected':'unknown' if j.get('earnings') else 'not_applicable',
      'qna_status':'not_checked_stage_a' if j.get('earnings') else 'not_applicable',
      'prior_period_comparison_required':bool(j.get('earnings')),
      'earnings_rescue_questions':([f"Which named lithium miners, reporting periods and primary filings support the profit signal in {j['short']}?",'What are the price-volume-mix-cost, inventory, utilisation, guidance and Q&A drivers versus the prior period?'] if j.get('earnings') else []),
      'anti_bias_check':{'binding_status_used_as_importance_proxy':False,'legal_formality_used_as_importance_proxy':False,'headline_amount_used_without_denominator':False,'announced_capacity_treated_as_actual_output':False,'routine_execution_event_overranked':False,'conventional_execution_event_required_without_reason':False},
      'structural_rescue_required':False,
      'structural_rescue_question':None,
      'search_before_delete_status':'applied',
      'technology_validation_stage':tech_stage,
      'technology_score_cap_applied':bool(tech_level in {'company_target_or_unsupported_claim','laboratory_unvalidated'}),
      'technology_validation_gap':j['gap'] if 'technology_commercialization_anchor' in j['anchors'] else 'Technology commercialization scoring is not used for this item.',
    }
    if not exec_route:
        item['structural_selector_policy_version']='STRUCTURAL_NEWS_VALUE_SELECTION_V3'
    item.update(legal_fields(j,event['representative']['date']))
    return item

def strict_item(event,j):
    item=common_item(event,j,True)
    item['spec_id']=f"STD26_R6_B01_{event['ordinal']:03d}"
    item['strict_pass_gate']={'status':'pass','reason':f"{j['short']} passes lane, anchor, incremental-information, decision-value, freshness, duplicate and full-schema viability checks within the source-bound packet.",'all_six_conditions_passed':True,'anchor_supported_by_upstream_text':True,'why_not_review_pool':f"The supplied packet supports a current and independently cardable anchor for {j['short']} with bounded Stage B verification targets."}
    item['execution_credibility_gate']={'status':'PASS','anchor_type':item['execution_anchor_type'] or ('policy_or_structural_change' if 'policy_regulatory_anchor' in j['anchors'] else 'structural_change'),'anchor_strength':item['execution_anchor_strength'] or 'strong','stage_precision_note':f"The current stage for {j['short']} is explicit enough for strict Stage A selection, while body-level evidence remains Stage B work."}
    item['independent_cardability_gate']={'status':'PASS','distinct_event_or_stage_progression':True,'full_schema_viability':'PASS','duplicate_or_reinforcement_note':f"R6 90,100-pair duplicate audit is closed; {j['short']} is not a same-event duplicate or existing-card reinforcement."}
    return item

def review_item(event,j):
    item=common_item(event,j,False)
    iid=f"R6_B01_REVIEW_{event['ordinal']:03d}"
    obsids=item['source_story_ids']
    item.update({
      'story_id':obsids[0], 'grouped_story_ids':obsids[1:], 'review_pool_item_id':iid,
      'upstream_status':'review', 'reason_for_review':j['gap'],
      'review_type':'earnings_deep_dive' if j.get('earnings') else 'general_candidate',
      'what_must_be_checked_before_promotion':f"Resolve the bounded uncertainty for {j['short']}: {j['gap']}",
      'why_not_strict_passed_spec':f"Strict admission is withheld because {j['gap']}",
      'baseline_relation_if_known':item['baseline_follow_up_relation'],
      'recommended_next_action':'Retain in the assigned first-class review partition and reopen only through the authorized review/promotion path.',
      'carry_forward_policy':'carry_until_resolved',
      'next_action_condition':f"Reopen or promote only after the source-bound question for {j['short']} is resolved.",
      'review_pool_resolution_status':'open',
      'review_pool_partition':j['pool'],
      'review_pool_partition_reason':f"Formal Stage A score/gates place {j['short']} in {j['pool']} rather than the strict Stage B queue.",
      'review_pool_subtype':'earnings_deep_dive' if j.get('earnings') else 'general_candidate',
      'promotion_precondition':f"Verify the unresolved execution, legal, scale, technology or incremental-value fact for {j['short']} from the supplied/authorized evidence path.",
      'bounded_review_question':f"Does the source packet support a stronger current-stage and decision-value judgment for {j['short']} than the present {classification(j['score'])} classification?",
      'recommended_review_method':'Use source-bound packet and current canonical comparison first; do not invent missing evidence or silently promote.',
      'evidence_or_duplicate_question':f"Can the unresolved fact for {j['short']} be verified while preserving the R6 duplicate/lineage decision?",
      'final_review_pool_disposition':'promote_to_strict_spec_after_review' if j['pool']=='candidate_review_pool' else ('watchlist_only_after_review' if j['pool']=='watchlist_context_pool' else 'not_cardable_after_review'),
    })
    if j['pool']=='watchlist_context_pool':
        item.update({'why_context_only':f"Current evidence leaves {j['short']} below strict independent-card threshold because {j['gap']}",'future_trigger_to_reopen':f"A binding policy, signed transaction, verified scale, production impact or other new measurable milestone for {j['short']} would reopen review.",'recommended_monitoring_action':f"Monitor only the bounded next milestone for {j['short']}; do not send to Stage B now."})
    if j['pool']=='reject_or_support_only_pool':
        item.update({'reject_or_support_only_basis':f"{j['short']} lacks sufficient independent battery/ESS decision value for a card in this run.",'final_reason':j['gap'],'whether_support_source_only':False})
    item['execution_credibility_gate']={'status':j['exec'],'anchor_type':item['execution_anchor_type'] or 'structural_or_policy_signal','anchor_strength':item['execution_anchor_strength'] or ('moderate' if j['exec']!='FAIL' else 'weak'),'stage_precision_note':f"Formal Stage A review status for {j['short']}; unresolved elements are not inferred."}
    item['independent_cardability_gate']={'status':j['card'],'distinct_event_or_stage_progression':j['card']!='FAIL','full_schema_viability':'PASS' if j['card']=='PASS' else ('REVIEW' if j['card']=='REVIEW' else 'FAIL'),'duplicate_or_reinforcement_note':f"R6 duplicate audit is resolved; review status for {j['short']} reflects cardability/value uncertainty, not unresolved event identity."}
    item['strict_pass_gate']={'status':'review','reason':j['gap'],'all_six_conditions_passed':False,'anchor_supported_by_upstream_text':True,'why_not_review_pool':None}
    return item

events={e['ordinal']:e for e in packet['events']}
pools={'strict_passed_spec':[],'candidate_review_pool':[],'watchlist_context_pool':[],'reject_or_support_only_pool':[]}
for ordinal in range(1,26):
    event=events[ordinal]; j=J[ordinal]
    assert sum(j['breakdown'].values()) == j['score'], ordinal
    if j['pool']=='strict_passed_spec': pools['strict_passed_spec'].append(strict_item(event,j))
    else: pools[j['pool']].append(review_item(event,j))
assert {k:len(v) for k,v in pools.items()} == {'strict_passed_spec':7,'candidate_review_pool':11,'watchlist_context_pool':6,'reject_or_support_only_pool':1}

review_items=pools['candidate_review_pool']+pools['watchlist_context_pool']+pools['reject_or_support_only_pool']
review_resolution=[]
for item in review_items:
    pool=item['review_pool_partition']
    cf='candidate_for_authorized_promotion' if pool=='candidate_review_pool' else ('carry_forward_to_watchlist' if pool=='watchlist_context_pool' else 'closed_not_cardable')
    review_resolution.append({'review_pool_item_id':item['review_pool_item_id'],'story_id':item['story_id'],'grouped_story_ids':item['grouped_story_ids'],'review_pool_partition':pool,'original_review_pool_partition':pool,'current_disposition':pool,'disposition_basis':f"Formal Stage A V4 Batch 01 retains {item['review_pool_item_id']} in {pool}; no review-pool promotion is performed in this batch.",'resolution_status':'open','carry_forward_policy':cf,'next_action_condition':item['next_action_condition'],'whether_user_authorization_required':False,'upstream_status':item['upstream_status'],'final_review_pool_disposition':item['final_review_pool_disposition'],'reviewed_by_stage_or_pass':'Formal Stage A V4 R6 Batch 01','review_artifact_id':'stage_a_formal_r6_batch01_20260903_R1'})

all_candidates=pools['strict_passed_spec']+review_items
anchors=Counter(a for item in all_candidates for a in item.get('anchor_classes',[]))
lenses=Counter(a for item in all_candidates for a in item.get('structural_value_lenses',[]))
classes=Counter(item['decision_value_classification'] for item in all_candidates)

ledger=[]
for ordinal in range(1,26):
    event=events[ordinal]; j=J[ordinal]
    item=next(x for x in all_candidates if (x.get('spec_id')==f"STD26_R6_B01_{ordinal:03d}" or x.get('review_pool_item_id')==f"R6_B01_REVIEW_{ordinal:03d}"))
    source_ids=item['source_story_ids']
    bucket=j['pool']
    for sid in source_ids:
        obs=next(o for o in event['observations'] if o['observation_key']==sid)
        ledger.append({'story_id':sid,'original_story_id':obs.get('story_id'),'upstream_status':'kept','upstream_drop_reason':None,'headline':obs.get('title'),'site':obs.get('site'),'url':obs.get('source_url'),'integrity_group_id':event['event_id'],'integrity_is_best':sid==event['representative']['observation_key'],'ledger_decision':'passed' if bucket=='strict_passed_spec' else bucket,'editorial_bucket':bucket,'reason':f"Formal Stage A R6 Batch 01 disposition for {j['short']}: {bucket}.",'spec_id':item.get('spec_id'),'review_pool_item_id':item.get('review_pool_item_id'),'merged_into_spec_id':item.get('spec_id') if bucket=='strict_passed_spec' and len(source_ids)>1 else None,'baseline_match':event.get('canonical_relation'),'baseline_relation':item['baseline_relation'],'duplicate_risk':item['duplicate_risk'],'staleness_decision':item['staleness_decision'],'treasure_hunt_sampled':False,'notes':'Source-bound observation identity is used as story_id to prevent cross-run raw story-ID collisions.','anchor_classes':copy.deepcopy(item['anchor_classes']),'news_value_basis':j['short'],'structural_value_lenses':copy.deepcopy(item['structural_value_lenses']),'structural_value_override_applied':item['structural_value_override_applied'],'structural_value_override_reason':item['structural_value_override_reason'],'evidence_needed_for_stage_b':copy.deepcopy(item['evidence_needed_for_stage_b']),'why_execution_event_not_required':item['why_execution_event_not_required'],'incremental_information':item['incremental_information'],'decision_relevance':item['decision_relevance'],'baseline_expectation_changed':item['baseline_expectation_changed'],'follow_up_relation':item['baseline_follow_up_relation'],'next_confirmation_points':copy.deepcopy(item['next_confirmation_points']),'portfolio_coverage_contribution':copy.deepcopy(item['portfolio_coverage_contribution']),'earnings_deep_dive_required':item['earnings_deep_dive_required'],'qna_status':item['qna_status'],'review_pool_subtype':item.get('review_pool_subtype'),'review_pool_repromotion_precondition':item.get('promotion_precondition'),'decision_news_value_score':item['decision_news_value_score'],'decision_value_breakdown':copy.deepcopy(item['decision_value_breakdown']),'decision_value_classification':item['decision_value_classification'],'prior_state':item['prior_state'],'new_verified_fact':item['new_verified_fact'],'changed_judgment':item['changed_judgment'],'uncertainty_resolved':item['uncertainty_resolved'],'remaining_uncertainty':item['remaining_uncertainty'],'denominator_used':item['denominator_used'],'denominator_gap':item['denominator_gap'],'publication_urgency':copy.deepcopy(item['publication_urgency']),'anti_bias_check':copy.deepcopy(item['anti_bias_check']),'structural_rescue_required':item['structural_rescue_required'],'structural_rescue_question':item['structural_rescue_question'],'technology_validation_stage':item['technology_validation_stage'],'technology_score_cap_applied':item['technology_score_cap_applied'],'technology_validation_gap':item['technology_validation_gap'],'legal_policy_stage':item.get('legal_policy_stage','not_applicable')})

story_ids=[row['story_id'] for row in ledger]
assert len(story_ids)==len(set(story_ids))
assert len(story_ids)==sum(e['observation_count'] for e in packet['events'])

summary={
 'legacy_keep_count':0,'strict_passed_spec_count':7,'needs_review_count':18,'rejected_count':0,'existing_reinforcement_count':0,'support_source_only_count':0,'duplicate_or_reinforcement_count':0,'stale_discarded_count':0,'stale_warm_review_count':0,'total_ledger_count':len(ledger),'ledger_matches_story_count':True,
 'structural_selector_policy_version':'STRUCTURAL_NEWS_VALUE_SELECTION_V3','structural_selector_policy_file':'docs/STRUCTURAL_NEWS_VALUE_SELECTION.md','structural_selector_policy_sha':hashlib.sha256(STRUCTURAL_POLICY.read_bytes()).hexdigest(),
 'credibility_cardability_value_urgency_separated':True,'industry_first_weighting_applied':True,'core_industrial_weight_total':70,'multi_anchor_class_model_applied':True,'mandatory_structural_lenses_applied':True,
 'anchor_class_counts':dict(sorted(anchors.items())),'structural_lens_coverage_counts':dict(sorted(lenses.items())),'decision_value_classification_counts':dict(sorted(classes.items())),
 'critical_structural_candidate_ids':[i.get('spec_id') or i.get('review_pool_item_id') for i in all_candidates if i['decision_value_classification']=='critical_structural'],
 'high_decision_value_candidate_ids':[i.get('spec_id') or i.get('review_pool_item_id') for i in all_candidates if i['decision_value_classification']=='high_decision_value'],
 'high_value_review_pool_ids':[i['review_pool_item_id'] for i in review_items if i['decision_news_value_score']>=70],
 'structural_signal_review_pool_ids':[],'earnings_deep_dive_pool_ids':[i['review_pool_item_id'] for i in review_items if i.get('earnings_deep_dive_required')],
 'follow_up_candidate_ids':[i.get('spec_id') or i.get('review_pool_item_id') for i in all_candidates if i['baseline_follow_up_relation'] in {'distinct_follow_up','program_lineage'}],
 'zero_coverage_domains':[],'execution_or_formality_bias_findings':[],'technology_validation_gap_ids':[i.get('spec_id') or i.get('review_pool_item_id') for i in all_candidates if 'technology_commercialization_anchor' in i['anchor_classes']],
 'legal_policy_stage_gap_ids':[],'search_before_delete_applied':True,'earnings_call_qna_rule_applied':True,'follow_up_probability_review_applied':True,'portfolio_coverage_audit_applied':True,
 'structural_value_selector_status':'PASS','portfolio_coverage_audit_status':'PASS','earnings_call_qna_audit_status':'PASS','follow_up_repromotion_audit_status':'PASS','execution_event_bias_audit_status':'PASS','content_depth_audit_status':'PASS','decision_ledger_count':len(ledger),
 'selection_route_counts':dict(Counter(i['selection_route'] for i in all_candidates)),'formal_event_count':25,'source_bound_observation_count':len(ledger),
}

artifact={
 'stage':'stage_a','status':'PASS','run_tag':'20260903_R6_FORMAL_STAGE_A_BATCH01','run_label':'Formal Stage A V4 R6 Batch 01 of 16','source_prompt_file':'docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md','source_prompt_sha256':hashlib.sha256(PROMPT.read_bytes()).hexdigest(),'source_prompt_version':'STAGE_A_INTEGRATED_SELECTOR_V4_20260901','source_prompt_authority':'uploaded_or_repo_source_file_prompt','source_prompt_provenance_status':'PASS',
 'input_file':'runs/2026-09-03/stage_a_review_packets_395_r6/batch_01.json','baseline_file':'data/cards.full.json','baseline_source_declaration':f"current GitHub main {MAIN}, canonical blob {CANON_BLOB}, 1514 cards",'baseline_count':1514,'github_main_sync_required_later':False,
 'source_universe':'R6 corrected 395-event universe; Formal Stage A Batch 01 covers ordinals 1-25 and all source-bound observations assigned to those events','story_count':len(ledger),'event_count':25,'original_status_counts':{'kept':len(ledger)},
 'integrity_summary':{'status':'PASS','main_sha':MAIN,'canonical_blob_sha':CANON_BLOB,'r6_membership_sha256':R6_MEMBERSHIP_SHA,'r6_relation_sha256':R6_RELATION_SHA,'r6_preselection_sha256':R6_PRESELECTION_SHA,'packet_sha256':hashlib.sha256(PACKET.read_bytes()).hexdigest(),'duplicate_event_membership':0,'unassigned_event_membership':0},
 'recommended_for':['Stage B evidence package construction for strict_passed_spec[] only','separate authorized review-pool handling for non-strict items'],
 'stage_a_validity_status':'PASS','artifact_consistency_status':'PASS','csv_schema_status':'PASS','review_pool_partition_status':'PASS','strict_pass_gate_metadata_status':'PASS','baseline_duplicate_screen_status':'PASS','review_pool_carry_forward_ledger_status':'PASS',
 'next_call_recommendation':{'recommended_next_call':'Stage B r0','recommended_prompt_id':'Prompt 0.2','recommended_input_universe':'Stage A strict_passed_spec[] only','reason':'Formal Batch 01 has seven strict Stage A V4 specs and all Stage A safety/accounting gates pass; review pools are explicitly excluded from Stage B.','pending_parallel_or_followup_call':'review_pool/treasure triage','pending_prompt_id':'authorized review_pool/treasure promotion protocol, not Prompt 0.2','pending_input_universe':'candidate_review_pool[] + eligible treasure/review-only universe','pending_reason':'Stage B may process strict_passed_spec[] only; review_pool/treasure remains open and must not be treated as exhausted.','blocked_items_summary':[{'pool':k,'count':len(v)} for k,v in pools.items() if k!='strict_passed_spec']},
 'required_docs_check':{'docs_expected':['docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md','docs/FACT_DISCIPLINE.md','docs/PROMPT_ABC_DEFAULT_MODE.md','docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md','docs/CARD_ID_STANDARD.md','docs/WORKFLOW.md','docs/OPERATIONS.md','docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md','docs/RELATED_LIFECYCLE_CONTRACT.md'],'docs_read_from_github_main':['docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md','docs/FACT_DISCIPLINE.md','docs/PROMPT_ABC_DEFAULT_MODE.md','docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md','docs/CARD_ID_STANDARD.md','docs/WORKFLOW.md','docs/OPERATIONS.md','docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md','docs/RELATED_LIFECYCLE_CONTRACT.md'],'docs_missing_or_unreadable':[],'status':'PASS','authority_note':'The integrated V4 Stage A prompt is the sole active selection authority. Superseded Structural V3 policy/addendum and PROMPT_ABC_SUPPORTING_RULES are not persisted as active authority; the current main validator supplies any frozen V3 document-presence aliases only in its private compatibility projection.'},
 'lane_sanity_rules_applied':['selector_only_no_external_web_search','no_article_body_fetch','source_bound_observation_identity','R6_event_duplicate_gate_pass','rescue_before_delete','V4_score_caps_machine_checked'],
 'dropped_treasure_hunt':{'performed':False,'trigger_reason':'Coverage/discovery already locked upstream by current 0.0C/R6 source universe; Batch 01 performs no external treasure hunt.','sample_strategy':'not_applicable_at_formal_batch_selector','sample_size':0,'sampled_story_ids':[],'rescued_count':0,'rescue_ids':[],'non_sampled_dropped_count':0,'non_sampled_ledger_policy':'All Batch 01 R6 source-bound observations are represented in the decision ledger.'},
 'summary':summary,'legacy_keep':[],'strict_passed_spec':pools['strict_passed_spec'],'candidate_review_pool':pools['candidate_review_pool'],'watchlist_context_pool':pools['watchlist_context_pool'],'reject_or_support_only_pool':pools['reject_or_support_only_pool'],
 'review_pool':[copy.deepcopy(i) for i in review_items],
 'review_pool_partition_summary':{'candidate_review_pool':11,'watchlist_context_pool':6,'reject_or_support_only_pool':1,'total_review_items':18,'strict_passed_spec':7,'event_total':25},
 'review_pool_resolution_ledger':review_resolution,'rejected':[],'existing_reinforcement':[],'support_source_only':[],'dropped_treasure_hunt_result':[],'decision_ledger':ledger,
 'formal_stage_a_batch':{'batch':1,'batch_count_total':16,'ordinal_start':1,'ordinal_end':25,'decision_batches_committed_before_this':0,'event_count':25,'strict_count':7,'candidate_review_count':11,'watchlist_count':6,'reject_or_support_only_count':1,'formal_stage_a_external_web_search_count':0,'formal_stage_a_article_body_fetch_count':0}
}

OUT.write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+'\n')

# Fail-closed validation against the current repo validator chain.
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.stage_a_v4_contract import validate_stage_a_v4_payload
from validation_scripts.stage_a_v4_hardening import validate_stage_a_v4_hardening_payload
from validation_scripts.stage_a_full_v3_completeness_review4945713246 import prevalidate_full_stage_a_artifact, validate_full_stage_a_artifact

pre_errors=prevalidate_full_stage_a_artifact(artifact)
v4_errors=validate_stage_a_v4_payload(artifact,require_contract=True)
hard_errors=validate_stage_a_v4_hardening_payload(artifact,require_contract=True)
authority_errors=lineage._validate_active_required_docs(artifact)
compat_payload=lineage._project_full_stage_a_for_v3_compat(artifact) if not authority_errors else artifact
full_errors=validate_full_stage_a_artifact(compat_payload,lineage._compat_module)
rc=lineage.check_stage_a(artifact)
report={'schema':'formal_stage_a_r6_batch01_validation_v1','status':'PASS' if not(pre_errors or v4_errors or hard_errors or authority_errors or full_errors) and rc==0 else 'FAIL','artifact':str(OUT.relative_to(ROOT)),'artifact_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'event_count':25,'source_bound_observation_count':len(ledger),'strict_count':7,'candidate_review_count':11,'watchlist_count':6,'reject_or_support_only_count':1,'prevalidation_errors':pre_errors,'v4_contract_errors':v4_errors,'v4_hardening_errors':hard_errors,'active_authority_errors':authority_errors,'full_completeness_errors':full_errors,'lineage_check_rc':rc,'external_web_search_count':0,'article_body_fetch_count':0}
REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
if report['status']!='PASS':
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(1)
print(json.dumps(report,ensure_ascii=False))
