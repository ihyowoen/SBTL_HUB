#!/usr/bin/env python3
from pathlib import Path
import copy, json
src=Path('validation_temp/20260905-promotion-r1/materialize_promotion_stage_a_r3.py')
exec(compile(src.read_text(encoding='utf-8'),str(src)+'[R4_STRICT_LEDGER_SYNC]','exec'),{'__name__':'__main__','__file__':str(src)})
out=Path('validation_temp/20260905-promotion-r1/out/stage-a-promotion.json')
a=json.loads(out.read_text(encoding='utf-8'))
CANONICAL_WARNING='Stage B must verify the provided source-candidate URL and build a valid evidence package before drafting. This Stage A spec is not evidence_complete, and primary_url is not evidence by itself.'
MIRROR={
 'anchor_classes':'anchor_classes','structural_value_lenses':'structural_value_lenses','structural_value_override_applied':'structural_value_override_applied','structural_value_override_reason':'structural_value_override_reason','evidence_needed_for_stage_b':'evidence_needed_for_stage_b','why_execution_event_not_required':'why_execution_event_not_required','incremental_information':'incremental_information','decision_relevance':'decision_relevance','baseline_expectation_changed':'baseline_expectation_changed','follow_up_relation':'baseline_follow_up_relation','next_confirmation_points':'next_confirmation_points','portfolio_coverage_contribution':'portfolio_coverage_contribution','earnings_deep_dive_required':'earnings_deep_dive_required','qna_status':'qna_status','decision_news_value_score':'decision_news_value_score','decision_value_breakdown':'decision_value_breakdown','decision_value_classification':'decision_value_classification','prior_state':'prior_state','new_verified_fact':'new_verified_fact','changed_judgment':'changed_judgment','uncertainty_resolved':'uncertainty_resolved','remaining_uncertainty':'remaining_uncertainty','denominator_used':'denominator_used','denominator_gap':'denominator_gap','publication_urgency':'publication_urgency','anti_bias_check':'anti_bias_check','structural_rescue_required':'structural_rescue_required','structural_rescue_question':'structural_rescue_question','technology_validation_stage':'technology_validation_stage','technology_score_cap_applied':'technology_score_cap_applied','technology_validation_gap':'technology_validation_gap'
}
by_story={}
for spec in a['strict_passed_spec']:
    spec['stage_b_requirement_note']=CANONICAL_WARNING
    for story_id in spec['source_story_ids']:
        by_story[story_id]=spec
for row in a['decision_ledger']:
    spec=by_story[row['story_id']]
    for ledger_field,spec_field in MIRROR.items():
        if spec_field in spec:
            row[ledger_field]=copy.deepcopy(spec[spec_field])
    # Keep current structural-route compatibility metadata aligned too.
    for field in ('selection_route','format_risk_tags','execution_anchor_type','execution_anchor_strength','structural_selector_policy_version'):
        if field in spec:
            row[field]=copy.deepcopy(spec[field])
out.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('RESULT: PASS_R4_PROMOTION_STRICT_LEDGER_SYNC')
