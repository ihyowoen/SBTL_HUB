#!/usr/bin/env python3
"""Machine-enforced Stage A V4 selection contract.

This module owns the V4 editorial-selection metadata introduced by the
embedded Stage A news-value policy. Historical V3 lineage/source/format checks
remain separate compatibility layers and may impose additional constraints.
"""
from __future__ import annotations

from typing import Any

POLICY_VERSION = "EMBEDDED_NEWS_VALUE_SELECTION_V4"
ROUTES = {"execution_anchor_route", "structural_non_execution_route"}
ANCHOR_CLASSES = {
    "execution_event_anchor",
    "policy_regulatory_anchor",
    "data_financial_anchor",
    "strategic_behavior_anchor",
    "technology_commercialization_anchor",
    "follow_up_probability_anchor",
}
NON_EXECUTION_ANCHORS = ANCHOR_CLASSES - {"execution_event_anchor"}
URGENCY_LEVELS = {"immediate", "near_term", "monitor"}
CLASS_THRESHOLDS = (
    (85, "critical_structural"),
    (70, "high_decision_value"),
    (55, "material_industry_signal"),
    (40, "standard_monitoring"),
    (25, "context_or_reinforcement"),
    (0, "low_independent_value"),
)
BREAKDOWN_MAX = {
    "market_structure_competition": 25,
    "supply_demand_price_utilisation": 25,
    "technology_performance_safety": 20,
    "cashflow_asset_value": 10,
    "law_policy_market_access": 10,
    "systemic_scale": 5,
    "persistence_irreversibility": 3,
    "decision_urgency_actionability": 2,
}
REQUIRED_FIELDS = (
    "selection_policy_version",
    "selection_route",
    "execution_credibility_gate",
    "independent_cardability_gate",
    "anchor_classes",
    "decision_news_value_score",
    "decision_value_breakdown",
    "decision_value_classification",
    "publication_urgency",
    "prior_state",
    "new_verified_fact",
    "changed_judgment",
    "uncertainty_resolved",
    "remaining_uncertainty",
    "incremental_information",
    "baseline_expectation_changed",
    "decision_relevance",
    "evidence_needed_for_stage_b",
    "next_confirmation_points",
    "related_prepass",
    "structural_non_execution_reason",
    "why_execution_event_not_required",
)
NARRATIVE_FIELDS = (
    "prior_state",
    "new_verified_fact",
    "changed_judgment",
    "uncertainty_resolved",
    "remaining_uncertainty",
    "incremental_information",
    "baseline_expectation_changed",
    "decision_relevance",
)
RELATED_PREPASS_REQUIRED = (
    "status",
    "same_event_checked",
    "matched_baseline_candidate_ids",
    "matched_current_batch_candidate_ids",
    "relation_candidates",
    "duplicate_disposition",
    "earliest_same_event_check_status",
    "fresh_anchor_questions",
)
RELATED_RELATION_TYPES = {
    "same_event_duplicate",
    "existing_card_reinforcement",
    "distinct_follow_up",
    "program_lineage",
    "new_unrelated_event",
    "uncertain_needs_review",
}
RELATED_DUPLICATE_DISPOSITIONS = {
    "no_duplicate_found",
    "same_event_duplicate",
    "existing_card_reinforcement",
    "uncertain_needs_review",
}
RELATED_CONFIDENCE = {"low", "medium", "high"}
RELATED_CANDIDATE_REQUIRED = (
    "target_candidate_id",
    "proposed_relation_type",
    "confidence",
    "reason",
    "anchor_class_to_verify",
    "incremental_anchor_question",
)


def _identifier(spec: dict[str, Any], index: int) -> str:
    return str(spec.get("spec_id") or spec.get("source_spec_id") or f"idx_{index}")


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _empty(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def _gate_status(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip().upper()
    if isinstance(value, dict):
        status = value.get("status")
        if isinstance(status, str):
            return status.strip().upper()
    return None


def _urgency_level(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        level = value.get("level")
        if isinstance(level, str):
            return level.strip()
    return None


def _expected_class(score: float) -> str:
    for minimum, classification in CLASS_THRESHOLDS:
        if score >= minimum:
            return classification
    return "low_independent_value"


def _string_array(value: Any, *, nonempty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (not nonempty or bool(value))
        and all(_nonempty_text(item) for item in value)
        and len(value) == len(set(value))
    )


def _valid_confidence(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in RELATED_CONFIDENCE
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and 0 <= float(value) <= 1
    )


def _validate_related_prepass(
    related: Any,
    spec_id: str,
    messages: list[str],
) -> None:
    if not isinstance(related, dict):
        messages.append(f"{spec_id}: related_prepass must be an object")
        return

    for field in RELATED_PREPASS_REQUIRED:
        if field not in related:
            messages.append(f"{spec_id}: related_prepass missing {field}")

    status = related.get("status")
    if status not in {"PASS", "HOLD"}:
        messages.append(f"{spec_id}: related_prepass.status must be PASS|HOLD")

    if not isinstance(related.get("same_event_checked"), bool):
        messages.append(f"{spec_id}: related_prepass.same_event_checked must be boolean")
    elif status == "PASS" and related.get("same_event_checked") is not True:
        messages.append(f"{spec_id}: related_prepass PASS requires same_event_checked=true")

    for field in (
        "matched_baseline_candidate_ids",
        "matched_current_batch_candidate_ids",
    ):
        value = related.get(field)
        if not _string_array(value):
            messages.append(
                f"{spec_id}: related_prepass.{field} must be a unique array of non-empty IDs"
            )

    earliest_status = related.get("earliest_same_event_check_status")
    if earliest_status not in {"PASS", "HOLD"}:
        messages.append(
            f"{spec_id}: related_prepass.earliest_same_event_check_status must be PASS|HOLD"
        )
    elif status == "PASS" and earliest_status != "PASS":
        messages.append(
            f"{spec_id}: related_prepass PASS requires earliest_same_event_check_status=PASS"
        )

    disposition = related.get("duplicate_disposition")
    if disposition not in RELATED_DUPLICATE_DISPOSITIONS:
        messages.append(
            f"{spec_id}: related_prepass.duplicate_disposition must be one of "
            f"{sorted(RELATED_DUPLICATE_DISPOSITIONS)}"
        )
    elif status == "PASS" and disposition == "uncertain_needs_review":
        messages.append(
            f"{spec_id}: related_prepass PASS cannot retain uncertain_needs_review disposition"
        )

    fresh_questions = related.get("fresh_anchor_questions")
    if not _string_array(fresh_questions, nonempty=True):
        messages.append(
            f"{spec_id}: related_prepass.fresh_anchor_questions must be a non-empty unique text array"
        )

    candidates = related.get("relation_candidates")
    if not isinstance(candidates, list):
        messages.append(f"{spec_id}: related_prepass.relation_candidates must be an array")
        return

    seen_targets: set[tuple[str, str]] = set()
    for index, candidate in enumerate(candidates):
        label = f"{spec_id}: related_prepass.relation_candidates[{index}]"
        if not isinstance(candidate, dict):
            messages.append(f"{label} must be an object")
            continue
        for field in RELATED_CANDIDATE_REQUIRED:
            if field not in candidate:
                messages.append(f"{label} missing {field}")

        target = candidate.get("target_candidate_id")
        relation_type = candidate.get("proposed_relation_type")
        if not _nonempty_text(target):
            messages.append(f"{label}.target_candidate_id must be non-empty")
        if relation_type not in RELATED_RELATION_TYPES:
            messages.append(
                f"{label}.proposed_relation_type must be one of {sorted(RELATED_RELATION_TYPES)}"
            )
        if _nonempty_text(target) and relation_type in RELATED_RELATION_TYPES:
            marker = (target.strip(), relation_type)
            if marker in seen_targets:
                messages.append(f"{label} duplicates target/relation pair {marker}")
            seen_targets.add(marker)

        if not _valid_confidence(candidate.get("confidence")):
            messages.append(f"{label}.confidence must be low|medium|high or numeric 0..1")
        if not _nonempty_text(candidate.get("reason")):
            messages.append(f"{label}.reason must be non-empty")

        anchor = candidate.get("anchor_class_to_verify")
        question = candidate.get("incremental_anchor_question")
        if relation_type in {"distinct_follow_up", "program_lineage"}:
            if anchor not in ANCHOR_CLASSES:
                messages.append(
                    f"{label}.anchor_class_to_verify must be a valid anchor for {relation_type}"
                )
            if not _nonempty_text(question):
                messages.append(
                    f"{label}.incremental_anchor_question must be non-empty for {relation_type}"
                )
        else:
            if anchor is not None and anchor not in ANCHOR_CLASSES:
                messages.append(f"{label}.anchor_class_to_verify is invalid")
            if question is not None and not _nonempty_text(question):
                messages.append(
                    f"{label}.incremental_anchor_question must be null or non-empty text"
                )


def validate_stage_a_v4_spec(
    spec: Any,
    index: int,
    messages: list[str],
    *,
    require_contract: bool = True,
) -> None:
    """Append fail-closed V4 contract violations for one Stage A strict spec."""
    if not isinstance(spec, dict):
        if require_contract:
            messages.append(f"idx_{index}: Stage A strict item must be an object")
        return

    spec_id = _identifier(spec, index)
    has_v4_marker = "selection_policy_version" in spec or "selection_route" in spec
    if not require_contract and not has_v4_marker:
        return

    for field in REQUIRED_FIELDS:
        if field not in spec:
            messages.append(f"{spec_id}: missing Stage A V4 field {field}")

    if spec.get("selection_policy_version") != POLICY_VERSION:
        messages.append(
            f"{spec_id}: selection_policy_version must be {POLICY_VERSION}"
        )

    route = spec.get("selection_route")
    if route not in ROUTES:
        messages.append(f"{spec_id}: selection_route must be one of {sorted(ROUTES)}")

    for field in ("execution_credibility_gate", "independent_cardability_gate"):
        if _gate_status(spec.get(field)) != "PASS":
            messages.append(f"{spec_id}: {field} must resolve to PASS")

    anchors = spec.get("anchor_classes")
    if not isinstance(anchors, list) or not anchors:
        messages.append(f"{spec_id}: anchor_classes must be a non-empty array")
        anchor_set: set[str] = set()
    else:
        valid_string_anchors = [
            value.strip()
            for value in anchors
            if isinstance(value, str) and bool(value.strip())
        ]
        if len(valid_string_anchors) != len(anchors):
            messages.append(f"{spec_id}: anchor_classes must contain non-empty strings")
        if len(valid_string_anchors) != len(set(valid_string_anchors)):
            messages.append(f"{spec_id}: anchor_classes must be unique")
        invalid = [value for value in valid_string_anchors if value not in ANCHOR_CLASSES]
        if invalid:
            messages.append(f"{spec_id}: invalid Stage A V4 anchor_classes={invalid}")
        anchor_set = set(valid_string_anchors)

    if route == "execution_anchor_route":
        if "execution_event_anchor" not in anchor_set:
            messages.append(
                f"{spec_id}: execution_anchor_route requires execution_event_anchor"
            )
        for field in ("structural_non_execution_reason", "why_execution_event_not_required"):
            if not _empty(spec.get(field)):
                messages.append(
                    f"{spec_id}: execution_anchor_route must leave {field} empty"
                )
    elif route == "structural_non_execution_route":
        if "execution_event_anchor" in anchor_set:
            messages.append(
                f"{spec_id}: structural_non_execution_route cannot carry execution_event_anchor"
            )
        if not (anchor_set & NON_EXECUTION_ANCHORS):
            messages.append(
                f"{spec_id}: structural_non_execution_route requires a non-execution anchor class"
            )
        for field in ("structural_non_execution_reason", "why_execution_event_not_required"):
            if not _nonempty_text(spec.get(field)):
                messages.append(
                    f"{spec_id}: structural_non_execution_route requires non-empty {field}"
                )

    score = spec.get("decision_news_value_score")
    if not isinstance(score, (int, float)) or isinstance(score, bool) or score < 0 or score > 100:
        messages.append(f"{spec_id}: decision_news_value_score must be numeric 0..100")
        numeric_score = None
    else:
        numeric_score = float(score)

    breakdown = spec.get("decision_value_breakdown")
    if not isinstance(breakdown, dict):
        messages.append(f"{spec_id}: decision_value_breakdown must be an object")
    else:
        missing = [key for key in BREAKDOWN_MAX if key not in breakdown]
        extra = [key for key in breakdown if key not in BREAKDOWN_MAX]
        if missing:
            messages.append(f"{spec_id}: decision_value_breakdown missing {missing}")
        if extra:
            messages.append(f"{spec_id}: decision_value_breakdown has unknown fields {extra}")
        total = 0.0
        valid_total = not missing and not extra
        for key, maximum in BREAKDOWN_MAX.items():
            value = breakdown.get(key)
            if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0 or value > maximum:
                messages.append(
                    f"{spec_id}: decision_value_breakdown.{key} must be numeric 0..{maximum}"
                )
                valid_total = False
            else:
                total += float(value)
        if valid_total and numeric_score is not None and abs(total - numeric_score) > 1e-9:
            messages.append(
                f"{spec_id}: decision_value_breakdown sum {total:g} != decision_news_value_score {numeric_score:g}"
            )

    classification = spec.get("decision_value_classification")
    if numeric_score is not None:
        expected = _expected_class(numeric_score)
        if classification != expected:
            messages.append(
                f"{spec_id}: decision_value_classification {classification!r} != {expected!r} for score {numeric_score:g}"
            )
    elif not _nonempty_text(classification):
        messages.append(f"{spec_id}: decision_value_classification must be non-empty")

    urgency = _urgency_level(spec.get("publication_urgency"))
    if urgency not in URGENCY_LEVELS:
        messages.append(
            f"{spec_id}: publication_urgency must resolve to one of {sorted(URGENCY_LEVELS)}"
        )

    for field in NARRATIVE_FIELDS:
        if not _nonempty_text(spec.get(field)):
            messages.append(f"{spec_id}: {field} must be non-empty narrative text")

    for field in ("evidence_needed_for_stage_b", "next_confirmation_points"):
        value = spec.get(field)
        if not _string_array(value, nonempty=True):
            messages.append(f"{spec_id}: {field} must be a non-empty unique array of text")

    _validate_related_prepass(spec.get("related_prepass"), spec_id, messages)


def validate_stage_a_v4_payload(
    payload: Any,
    *,
    require_contract: bool = True,
) -> list[str]:
    """Validate every strict Stage A item in a payload and return violations."""
    messages: list[str] = []
    if not isinstance(payload, dict):
        return ["Stage A payload must be an object"] if require_contract else []
    specs = payload.get("strict_passed_spec")
    if not isinstance(specs, list):
        return ["Stage A payload strict_passed_spec must be an array"] if require_contract else []
    for index, spec in enumerate(specs):
        validate_stage_a_v4_spec(spec, index, messages, require_contract=require_contract)
    return messages
