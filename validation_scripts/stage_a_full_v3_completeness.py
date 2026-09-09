#!/usr/bin/env python3
"""Fail-closed completeness checks for real Stage A V3 artifacts.

This module is deliberately run-independent.  Small unit fixtures that exercise
only route semantics are not treated as full artifacts, while any payload that
carries full-artifact identity/accounting markers is required to materialise the
complete Prompt 0.1S / Structural News Value V3 surface.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Mapping

CANONICAL_POLICY_VERSION = "STRUCTURAL_NEWS_VALUE_SELECTION_V3"
CANONICAL_POLICY_FILE = "docs/STRUCTURAL_NEWS_VALUE_SELECTION.md"
V4_POLICY_VERSION = "EMBEDDED_NEWS_VALUE_SELECTION_V4"

SCORE_COMPONENT_LIMITS = {
    "market_structure_competition": 25,
    "supply_demand_price_utilisation": 25,
    "technology_performance_safety": 20,
    "cashflow_asset_value": 10,
    "law_policy_market_access": 10,
    "systemic_scale": 5,
    "persistence_irreversibility": 3,
    "decision_urgency_actionability": 2,
}
SCORE_BANDS = (
    (85, "critical_structural"),
    (70, "high_decision_value"),
    (55, "material_industry_signal"),
    (40, "standard_monitoring"),
    (25, "context_or_reinforcement"),
    (0, "low_independent_value"),
)
ANTI_BIAS_FIELDS = (
    "binding_status_used_as_importance_proxy",
    "legal_formality_used_as_importance_proxy",
    "headline_amount_used_without_denominator",
    "announced_capacity_treated_as_actual_output",
    "routine_execution_event_overranked",
    "conventional_execution_event_required_without_reason",
)
FULL_ITEM_PRESENCE_FIELDS = (
    "structural_value_override_reason",
    "why_execution_event_not_required",
    "denominator_used",
    "denominator_gap",
    "baseline_follow_up_relation",
    "portfolio_coverage_contribution",
    "earnings_deep_dive_required",
    "earnings_release_available",
    "ir_deck_available",
    "call_or_transcript_expected",
    "qna_status",
    "prior_period_comparison_required",
    "earnings_rescue_questions",
    "anti_bias_check",
    "structural_rescue_required",
    "structural_rescue_question",
    "search_before_delete_status",
)
FULL_SUMMARY_DICT_FIELDS = (
    "anchor_class_counts",
    "structural_lens_coverage_counts",
    "decision_value_classification_counts",
)
FULL_SUMMARY_ARRAY_FIELDS = (
    "critical_structural_candidate_ids",
    "high_decision_value_candidate_ids",
    "high_value_review_pool_ids",
    "structural_signal_review_pool_ids",
    "earnings_deep_dive_pool_ids",
    "follow_up_candidate_ids",
    "zero_coverage_domains",
    "execution_or_formality_bias_findings",
    "technology_validation_gap_ids",
    "legal_policy_stage_gap_ids",
)
FULL_SUMMARY_PASS_FIELDS = (
    "structural_value_selector_status",
    "portfolio_coverage_audit_status",
    "follow_up_repromotion_audit_status",
    "execution_event_bias_audit_status",
    "content_depth_audit_status",
)
FULL_POOL_FIELDS = (
    "strict_passed_spec",
    "candidate_review_pool",
    "watchlist_context_pool",
    "reject_or_support_only_pool",
)
REVIEW_POOLS = FULL_POOL_FIELDS[1:]

TECH_STAGE_CAPS = {
    "concept_or_target": 4,
    "research_or_paper": 7,
    "prototype": 7,
    "pilot": 11,
    "field_demonstration": 15,
    "customer_evaluation": 15,
    "qualification": 15,
    "certification": 15,
    "order_or_offtake": 15,
    "mass_production_equipment": 15,
    "production_start": 20,
    "commercial_shipment": 20,
    "repeat_order": 20,
    "profitability_or_field_performance_validation": 20,
    "material_recall_defect_fire_warranty_or_operating_failure": 20,
}

LEGAL_POLICY_STAGES = {
    "stage_0_rhetoric_or_advocacy",
    "stage_1_roadmap_consultation_or_draft_standard",
    "stage_2_bill_or_proposed_rule",
    "stage_3_enacted_law_final_rule_or_adopted_standard",
    "stage_4_implementation_budget_guidance_or_registry",
    "stage_5_enforcement_payment_denial_penalty_or_recall",
    "stage_6_judicial_or_tribunal_interpretation",
}
LEGAL_TOTAL_SCORE_CAPS = {
    "stage_0_rhetoric_or_advocacy": 39,
    "stage_1_roadmap_consultation_or_draft_standard": 54,
    "stage_2_bill_or_proposed_rule": 69,
}
LEGAL_POLICY_FIELDS = (
    "legal_policy_stage",
    "legal_instrument_type",
    "competent_authority",
    "procedural_status",
    "adoption_date",
    "publication_date",
    "effective_date",
    "mandatory_application_date",
    "affected_entities",
    "affected_products_or_activities",
    "geographic_scope",
    "extraterritorial_effect",
    "budget_or_funding_source",
    "implementation_mechanism",
    "administrative_readiness",
    "exemptions_and_thresholds",
    "transition_and_grandfathering",
    "noncompliance_consequences",
    "appeal_or_litigation_risk",
    "reversibility_risk",
    "precedent_scope",
    "legal_policy_transmission_chain",
    "next_implementation_trigger",
)
LEGAL_ARRAY_FIELDS = {
    "affected_entities",
    "affected_products_or_activities",
    "exemptions_and_thresholds",
    "transition_and_grandfathering",
    "noncompliance_consequences",
    "legal_policy_transmission_chain",
}

DECISION_LEDGER_REQUIRED_FIELDS = (
    "story_id",
    "anchor_classes",
    "news_value_basis",
    "structural_value_lenses",
    "structural_value_override_applied",
    "structural_value_override_reason",
    "evidence_needed_for_stage_b",
    "why_execution_event_not_required",
    "incremental_information",
    "decision_relevance",
    "baseline_expectation_changed",
    "follow_up_relation",
    "next_confirmation_points",
    "portfolio_coverage_contribution",
    "earnings_deep_dive_required",
    "qna_status",
    "review_pool_subtype",
    "review_pool_repromotion_precondition",
    "decision_news_value_score",
    "decision_value_breakdown",
    "decision_value_classification",
    "prior_state",
    "new_verified_fact",
    "changed_judgment",
    "uncertainty_resolved",
    "remaining_uncertainty",
    "denominator_used",
    "denominator_gap",
    "publication_urgency",
    "anti_bias_check",
    "structural_rescue_required",
    "structural_rescue_question",
    "technology_validation_stage",
    "technology_score_cap_applied",
    "technology_validation_gap",
    "legal_policy_stage",
)


def looks_like_full_stage_a_artifact(data: Any) -> bool:
    if not isinstance(data, Mapping):
        return False
    # Any one of these markers means the payload is attempting to be a real
    # Stage A artifact.  Missing sibling markers therefore cannot disable the
    # completeness gate.
    markers = (
        "stage",
        "run_tag",
        "summary",
        "story_count",
        "decision_ledger",
        "source_universe",
    )
    return any(field in data for field in markers)


def _item_specific(compat_module: Any, value: Any) -> bool:
    fn = getattr(compat_module, "_item_specific_narrative", None)
    if callable(fn):
        return bool(fn(value))
    return isinstance(value, str) and len(value.strip()) >= 8


def _candidate_id(item: Mapping[str, Any], fallback: str) -> str:
    return str(
        item.get("spec_id")
        or item.get("review_pool_item_id")
        or item.get("story_id")
        or fallback
    )


def _validate_denominator_gap_compat(
    item: Mapping[str, Any],
    label: str,
    messages: list[str],
) -> None:
    """Preserve frozen V3 booleans while honoring the active V4 text contract."""
    if "denominator_gap" not in item:
        return
    denominator_gap = item.get("denominator_gap")
    if item.get("selection_policy_version") == V4_POLICY_VERSION:
        denominator = item.get("systemic_scale_denominator")
        denominator_present = isinstance(denominator, str) and bool(denominator.strip())
        if denominator_present:
            if denominator_gap not in (None, "", [], {}):
                messages.append(
                    f"{label}: V4 denominator_gap must be empty when systemic_scale_denominator is supplied"
                )
        elif not isinstance(denominator_gap, str) or not denominator_gap.strip():
            messages.append(
                f"{label}: V4 denominator_gap must be a non-empty explanation when systemic_scale_denominator is absent"
            )
        return
    if not isinstance(denominator_gap, bool):
        messages.append(f"{label}: V3 denominator_gap must be boolean")


def _score_classification(score: int) -> str:
    for floor, classification in SCORE_BANDS:
        if score >= floor:
            return classification
    return "low_independent_value"


def _validate_identity_and_pool_types(data: Mapping[str, Any], messages: list[str]) -> None:
    if data.get("stage") != "stage_a":
        messages.append("full Stage A artifact stage must be 'stage_a'")
    run_tag = data.get("run_tag")
    if not isinstance(run_tag, str) or not run_tag.strip():
        messages.append("full Stage A artifact run_tag must be a non-empty string")
    if not isinstance(data.get("summary"), Mapping):
        messages.append("full Stage A artifact summary must be an object")
    source_universe = data.get("source_universe")
    if not isinstance(source_universe, str) or not source_universe.strip():
        messages.append("full Stage A artifact source_universe must be a non-empty string")
    story_count = data.get("story_count")
    if isinstance(story_count, bool) or not isinstance(story_count, int) or story_count < 0:
        messages.append("full Stage A artifact story_count must be a non-negative integer")
    for pool in FULL_POOL_FIELDS:
        if not isinstance(data.get(pool), list):
            messages.append(f"full Stage A artifact {pool} must be an array")
    if not isinstance(data.get("decision_ledger"), list):
        messages.append("full Stage A artifact decision_ledger must be an array")


def _validate_gate_objects(
    compat_module: Any,
    item: Mapping[str, Any],
    label: str,
    messages: list[str],
    *,
    strict: bool,
) -> None:
    credibility = item.get("execution_credibility_gate")
    if not isinstance(credibility, Mapping):
        messages.append(f"{label}: execution_credibility_gate must be an object")
    else:
        status = credibility.get("status")
        if strict:
            if status != "PASS":
                messages.append(f"{label}: strict execution_credibility_gate.status must be PASS")
        elif status not in {"PASS", "REVIEW", "FAIL"}:
            messages.append(f"{label}: execution_credibility_gate.status invalid")
        for field in ("anchor_type", "anchor_strength", "stage_precision_note"):
            if field not in credibility:
                messages.append(f"{label}: execution_credibility_gate missing {field}")
        if credibility.get("anchor_strength") not in {"strong", "moderate", "weak", "unknown"}:
            messages.append(f"{label}: execution_credibility_gate.anchor_strength invalid")

    cardability = item.get("independent_cardability_gate")
    if not isinstance(cardability, Mapping):
        messages.append(f"{label}: independent_cardability_gate must be an object")
    else:
        status = cardability.get("status")
        viability = cardability.get("full_schema_viability")
        progression = cardability.get("distinct_event_or_stage_progression")
        if strict:
            if status != "PASS":
                messages.append(f"{label}: strict independent_cardability_gate.status must be PASS")
            if viability != "PASS":
                messages.append(
                    f"{label}: strict independent_cardability_gate.full_schema_viability must be PASS"
                )
            if progression is not True:
                messages.append(
                    f"{label}: strict independent_cardability_gate.distinct_event_or_stage_progression must be true"
                )
        else:
            if status not in {"PASS", "REVIEW", "FAIL"}:
                messages.append(f"{label}: independent_cardability_gate.status invalid")
            if viability not in {"PASS", "REVIEW", "FAIL"}:
                messages.append(f"{label}: independent_cardability_gate.full_schema_viability invalid")
            if not isinstance(progression, bool):
                messages.append(
                    f"{label}: independent_cardability_gate.distinct_event_or_stage_progression must be boolean"
                )
        if not _item_specific(compat_module, cardability.get("duplicate_or_reinforcement_note")):
            messages.append(
                f"{label}: independent_cardability_gate.duplicate_or_reinforcement_note must be item-specific"
            )


def _validate_decision_score(item: Mapping[str, Any], label: str, messages: list[str]) -> None:
    score = item.get("decision_news_value_score")
    if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 100:
        messages.append(f"{label}: decision_news_value_score must be integer 0..100")
        return
    breakdown = item.get("decision_value_breakdown")
    if not isinstance(breakdown, Mapping):
        messages.append(f"{label}: decision_value_breakdown must be an object")
    elif set(breakdown) != set(SCORE_COMPONENT_LIMITS):
        messages.append(f"{label}: decision_value_breakdown keys must match canonical eight components")
    else:
        total = 0
        valid = True
        for field, upper in SCORE_COMPONENT_LIMITS.items():
            value = breakdown.get(field)
            if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= upper:
                valid = False
                messages.append(
                    f"{label}: decision_value_breakdown.{field} must be integer 0..{upper}"
                )
            else:
                total += value
        if valid and total != score:
            messages.append(
                f"{label}: decision_value_breakdown sum {total} != decision_news_value_score {score}"
            )
    expected = _score_classification(score)
    if item.get("decision_value_classification") != expected:
        messages.append(
            f"{label}: decision_value_classification must be {expected!r} for score {score}"
        )


def _validate_publication_urgency(
    compat_module: Any,
    item: Mapping[str, Any],
    label: str,
    messages: list[str],
) -> None:
    urgency = item.get("publication_urgency")
    if not isinstance(urgency, Mapping):
        messages.append(f"{label}: publication_urgency must be an object")
        return
    if urgency.get("level") not in {"immediate", "near_term", "monitor"}:
        messages.append(f"{label}: publication_urgency.level invalid")
    if not _item_specific(compat_module, urgency.get("action_required")):
        messages.append(f"{label}: publication_urgency.action_required must be item-specific")
    if "decision_deadline" not in urgency:
        messages.append(f"{label}: publication_urgency missing decision_deadline")


def _validate_earnings_fields(
    compat_module: Any,
    item: Mapping[str, Any],
    label: str,
    messages: list[str],
) -> None:
    earnings = item.get("earnings_deep_dive_required")
    if not isinstance(earnings, bool):
        messages.append(f"{label}: earnings_deep_dive_required must be boolean")
        return
    availability_fields = (
        "earnings_release_available",
        "ir_deck_available",
        "call_or_transcript_expected",
    )
    questions = item.get("earnings_rescue_questions")
    if not isinstance(questions, list):
        messages.append(f"{label}: earnings_rescue_questions must be an array")
        questions = []
    if earnings:
        for field in availability_fields:
            if item.get(field) not in {"yes", "no", "unknown"}:
                messages.append(f"{label}: {field} invalid for earnings candidate")
        if item.get("qna_status") != "not_checked_stage_a":
            messages.append(f"{label}: earnings candidate qna_status must be not_checked_stage_a")
        if item.get("prior_period_comparison_required") is not True:
            messages.append(f"{label}: earnings candidate prior_period_comparison_required must be true")
        # At Stage A the call/Q&A and prior-period work remain unresolved by
        # definition, so every earnings candidate needs concrete bounded rescue.
        if not questions or any(not _item_specific(compat_module, q) for q in questions):
            messages.append(
                f"{label}: earnings candidate requires non-empty item-specific earnings_rescue_questions"
            )
    else:
        for field in availability_fields:
            if item.get(field) != "not_applicable":
                messages.append(f"{label}: non-earnings {field} must be not_applicable")
        if item.get("qna_status") != "not_applicable":
            messages.append(f"{label}: non-earnings qna_status must be not_applicable")
        if item.get("prior_period_comparison_required") is not False:
            messages.append(f"{label}: non-earnings prior_period_comparison_required must be false")


def _validate_technology(item: Mapping[str, Any], label: str, messages: list[str]) -> None:
    classes = item.get("anchor_classes")
    lenses = item.get("structural_value_lenses")
    applicable = (
        isinstance(classes, list) and "technology_commercialization_anchor" in classes
    ) or (
        isinstance(lenses, list) and "technology_transition_commercialization" in lenses
    )
    if not applicable:
        return
    stage = item.get("technology_validation_stage")
    if stage not in TECH_STAGE_CAPS:
        messages.append(f"{label}: technology_validation_stage invalid")
        return
    cap_flag = item.get("technology_score_cap_applied")
    if not isinstance(cap_flag, bool):
        messages.append(f"{label}: technology_score_cap_applied must be boolean")
    gap = item.get("technology_validation_gap")
    if not isinstance(gap, str) or not gap.strip():
        messages.append(f"{label}: technology_validation_gap must be populated")
    breakdown = item.get("decision_value_breakdown")
    component = breakdown.get("technology_performance_safety") if isinstance(breakdown, Mapping) else None
    cap = TECH_STAGE_CAPS[stage]
    if isinstance(component, int) and not isinstance(component, bool) and component > cap:
        messages.append(
            f"{label}: technology_performance_safety {component} exceeds {stage} cap {cap}/20"
        )


def _validate_legal_policy(item: Mapping[str, Any], label: str, messages: list[str]) -> None:
    classes = item.get("anchor_classes")
    lenses = item.get("structural_value_lenses")
    applicable = (
        isinstance(classes, list) and "policy_regulatory_anchor" in classes
    ) or (
        isinstance(lenses, list)
        and any(isinstance(v, str) and ("policy" in v or "legal" in v) for v in lenses)
    )
    if not applicable:
        return
    for field in LEGAL_POLICY_FIELDS:
        if field not in item:
            messages.append(f"{label}: legal-policy candidate missing {field}")
            continue
        value = item.get(field)
        if field in LEGAL_ARRAY_FIELDS:
            if not isinstance(value, list):
                messages.append(f"{label}: legal-policy {field} must be an array")
        elif value is None or (isinstance(value, str) and not value.strip()):
            messages.append(f"{label}: legal-policy {field} must be populated")
    stage = item.get("legal_policy_stage")
    if stage not in LEGAL_POLICY_STAGES:
        messages.append(f"{label}: legal_policy_stage invalid")
    score = item.get("decision_news_value_score")
    cap = LEGAL_TOTAL_SCORE_CAPS.get(stage)
    if cap is not None and isinstance(score, int) and not isinstance(score, bool) and score > cap:
        messages.append(f"{label}: decision_news_value_score {score} exceeds {stage} cap {cap}")


def _validate_full_candidate(
    compat_module: Any,
    item: Mapping[str, Any],
    label: str,
    messages: list[str],
    *,
    strict: bool,
) -> None:
    _validate_gate_objects(compat_module, item, label, messages, strict=strict)
    _validate_decision_score(item, label, messages)
    _validate_publication_urgency(compat_module, item, label, messages)

    lenses = item.get("structural_value_lenses")
    if not isinstance(lenses, list) or (strict and not lenses):
        messages.append(
            f"{label}: structural_value_lenses must be {'non-empty ' if strict else ''}array"
        )
    for field in FULL_ITEM_PRESENCE_FIELDS:
        if field not in item:
            messages.append(f"{label}: missing Prompt 0.1S field {field}")

    _validate_denominator_gap_compat(item, label, messages)
    if "denominator_used" in item and not isinstance(item.get("denominator_used"), str):
        messages.append(f"{label}: denominator_used must be string")
    if "baseline_follow_up_relation" in item and not isinstance(item.get("baseline_follow_up_relation"), str):
        messages.append(f"{label}: baseline_follow_up_relation must be string")
    if "portfolio_coverage_contribution" in item and not isinstance(item.get("portfolio_coverage_contribution"), list):
        messages.append(f"{label}: portfolio_coverage_contribution must be an array")

    anti_bias = item.get("anti_bias_check")
    if not isinstance(anti_bias, Mapping):
        messages.append(f"{label}: anti_bias_check must be an object")
    else:
        for field in ANTI_BIAS_FIELDS:
            if anti_bias.get(field) is not False:
                messages.append(f"{label}: anti_bias_check.{field} must be false")

    rescue_required = item.get("structural_rescue_required")
    if "structural_rescue_required" in item and not isinstance(rescue_required, bool):
        messages.append(f"{label}: structural_rescue_required must be boolean")
    subtype = item.get("review_pool_subtype")
    if subtype == "structural_signal_review":
        if rescue_required is not True:
            messages.append(f"{label}: structural_signal_review requires structural_rescue_required=true")
        if not _item_specific(compat_module, item.get("structural_rescue_question")):
            messages.append(f"{label}: structural_signal_review requires an item-specific structural_rescue_question")
    elif rescue_required is True and not _item_specific(compat_module, item.get("structural_rescue_question")):
        messages.append(f"{label}: structural_rescue_question required when rescue is true")

    if item.get("search_before_delete_status") != "applied":
        messages.append(f"{label}: search_before_delete_status must be applied")

    _validate_earnings_fields(compat_module, item, label, messages)
    _validate_technology(item, label, messages)
    _validate_legal_policy(item, label, messages)


def _summary_field(data: Mapping[str, Any], field: str) -> tuple[bool, Any]:
    if field in data:
        return True, data.get(field)
    summary = data.get("summary")
    if isinstance(summary, Mapping) and field in summary:
        return True, summary.get(field)
    return False, None


def _all_candidates(data: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    result: list[Mapping[str, Any]] = []
    for pool in FULL_POOL_FIELDS:
        values = data.get(pool)
        if isinstance(values, list):
            result.extend(item for item in values if isinstance(item, Mapping))
    return result


def _validate_summary_counts(data: Mapping[str, Any], messages: list[str]) -> None:
    candidates = _all_candidates(data)
    anchors = Counter()
    lenses = Counter()
    classifications = Counter()
    for item in candidates:
        for value in item.get("anchor_classes", []) if isinstance(item.get("anchor_classes"), list) else []:
            if isinstance(value, str):
                anchors[value] += 1
        for value in item.get("structural_value_lenses", []) if isinstance(item.get("structural_value_lenses"), list) else []:
            if isinstance(value, str):
                lenses[value] += 1
        value = item.get("decision_value_classification")
        if isinstance(value, str) and value:
            classifications[value] += 1
    expected = {
        "anchor_class_counts": dict(sorted(anchors.items())),
        "structural_lens_coverage_counts": dict(sorted(lenses.items())),
        "decision_value_classification_counts": dict(sorted(classifications.items())),
    }
    for field, computed in expected.items():
        present, value = _summary_field(data, field)
        if not present or not isinstance(value, Mapping):
            continue
        if dict(value) != computed:
            messages.append(f"full Stage A summary {field} does not match emitted candidates")


def _validate_summary(data: Mapping[str, Any], messages: list[str]) -> None:
    exact_fields = {
        "structural_selector_policy_version": CANONICAL_POLICY_VERSION,
        "structural_selector_policy_file": CANONICAL_POLICY_FILE,
        "core_industrial_weight_total": 70,
    }
    true_fields = (
        "credibility_cardability_value_urgency_separated",
        "industry_first_weighting_applied",
        "multi_anchor_class_model_applied",
        "mandatory_structural_lenses_applied",
        "search_before_delete_applied",
    )
    for field, expected in exact_fields.items():
        present, value = _summary_field(data, field)
        if not present or value != expected:
            messages.append(f"full Stage A summary {field} must be {expected!r}")
    present, policy_sha = _summary_field(data, "structural_selector_policy_sha")
    if not present or not isinstance(policy_sha, str) or not policy_sha.strip():
        messages.append("full Stage A summary structural_selector_policy_sha must be populated")
    for field in true_fields:
        present, value = _summary_field(data, field)
        if not present or value is not True:
            messages.append(f"full Stage A summary {field} must be true")
    for field in FULL_SUMMARY_DICT_FIELDS:
        present, value = _summary_field(data, field)
        if not present or not isinstance(value, Mapping):
            messages.append(f"full Stage A summary {field} must be an object")
    for field in FULL_SUMMARY_ARRAY_FIELDS:
        present, value = _summary_field(data, field)
        if not present or not isinstance(value, list):
            messages.append(f"full Stage A summary {field} must be an array")
    for field in FULL_SUMMARY_PASS_FIELDS:
        present, value = _summary_field(data, field)
        if not present or value != "PASS":
            messages.append(f"full Stage A summary {field} must be PASS")
    present, earnings_status = _summary_field(data, "earnings_call_qna_audit_status")
    if not present or earnings_status not in {"PASS", "NOT_APPLICABLE"}:
        messages.append(
            "full Stage A summary earnings_call_qna_audit_status must be PASS or NOT_APPLICABLE"
        )
    _validate_summary_counts(data, messages)


def _candidate_story_ids(data: Mapping[str, Any]) -> set[str]:
    story_ids: set[str] = set()
    strict = data.get("strict_passed_spec")
    if isinstance(strict, list):
        for item in strict:
            if not isinstance(item, Mapping):
                continue
            values = item.get("source_story_ids")
            if isinstance(values, list):
                story_ids.update(v for v in values if isinstance(v, str) and v)
    for pool in REVIEW_POOLS:
        values = data.get(pool)
        if not isinstance(values, list):
            continue
        for item in values:
            if not isinstance(item, Mapping):
                continue
            story_id = item.get("story_id")
            if isinstance(story_id, str) and story_id:
                story_ids.add(story_id)
            grouped = item.get("grouped_story_ids")
            if isinstance(grouped, list):
                story_ids.update(v for v in grouped if isinstance(v, str) and v)
    return story_ids


def _validate_decision_ledger(data: Mapping[str, Any], messages: list[str]) -> None:
    ledger = data.get("decision_ledger")
    if not isinstance(ledger, list):
        return
    story_count = data.get("story_count")
    if isinstance(story_count, int) and not isinstance(story_count, bool):
        if len(ledger) != story_count:
            messages.append(
                f"decision_ledger count {len(ledger)} must equal story_count {story_count}"
            )
    ids: list[str] = []
    for index, row in enumerate(ledger):
        label = f"decision_ledger[{index}]"
        if not isinstance(row, Mapping):
            messages.append(f"{label} must be an object")
            continue
        for field in DECISION_LEDGER_REQUIRED_FIELDS:
            if field not in row:
                messages.append(f"{label}: missing required V3 ledger field {field}")
        story_id = row.get("story_id")
        if not isinstance(story_id, str) or not story_id:
            messages.append(f"{label}: story_id must be populated")
        else:
            ids.append(story_id)
    if len(ids) != len(set(ids)):
        messages.append("decision_ledger story_id values must be unique")
    if isinstance(story_count, int) and not isinstance(story_count, bool) and len(set(ids)) != story_count:
        messages.append("decision_ledger unique story coverage must equal story_count")
    emitted_story_ids = _candidate_story_ids(data)
    missing = sorted(emitted_story_ids - set(ids))
    if missing:
        messages.append(
            "decision_ledger is missing emitted candidate story IDs: " + ", ".join(missing)
        )
    summary = data.get("summary")
    if isinstance(summary, Mapping) and "decision_ledger_count" in summary:
        if summary.get("decision_ledger_count") != len(ledger):
            messages.append("summary.decision_ledger_count must equal decision_ledger length")


def validate_full_stage_a_artifact(
    data: Mapping[str, Any],
    compat_module: Any,
) -> list[str]:
    messages: list[str] = []
    _validate_identity_and_pool_types(data, messages)

    strict = data.get("strict_passed_spec")
    if isinstance(strict, list):
        for index, item in enumerate(strict):
            if not isinstance(item, Mapping):
                messages.append(f"strict_passed_spec[{index}] must be an object")
                continue
            label = _candidate_id(item, f"strict_passed_spec[{index}]")
            _validate_full_candidate(
                compat_module, item, label, messages, strict=True
            )

    for pool in REVIEW_POOLS:
        values = data.get(pool)
        if not isinstance(values, list):
            continue
        for index, item in enumerate(values):
            if not isinstance(item, Mapping):
                messages.append(f"{pool}[{index}] must be an object")
                continue
            label = _candidate_id(item, f"{pool}[{index}]")
            _validate_full_candidate(
                compat_module, item, label, messages, strict=False
            )

    _validate_summary(data, messages)
    _validate_decision_ledger(data, messages)
    return messages
