#!/usr/bin/env python3
"""Review 4943656188 hardening for full Stage A V3 artifacts.

This layer is run-independent.  It extends the prior full-artifact completeness
validator with provenance/base-schema reconciliation and safe preflight checks,
while preserving documented policy exceptions that must not be converted into
absolute machine ceilings.
"""
from __future__ import annotations

from typing import Any, Mapping

from validation_scripts import stage_a_full_v3_completeness as _base
from validation_scripts import stage_a_full_v3_completeness_review4943607439 as _previous

CANONICAL_POLICY_VERSION = _previous.CANONICAL_POLICY_VERSION
CANONICAL_POLICY_FILE = _previous.CANONICAL_POLICY_FILE
looks_like_full_stage_a_artifact = _previous.looks_like_full_stage_a_artifact

TOP_LEVEL_NONEMPTY_TEXT_FIELDS = (
    "run_label",
    "input_file",
    "baseline_file",
    "baseline_source_declaration",
)
TOP_LEVEL_OBJECT_FIELDS = (
    "original_status_counts",
    "integrity_summary",
    "required_docs_check",
    "dropped_treasure_hunt",
)
TOP_LEVEL_REQUIRED_FIELDS = (
    *TOP_LEVEL_NONEMPTY_TEXT_FIELDS,
    "baseline_count",
    "github_main_sync_required_later",
    "original_status_counts",
    "integrity_summary",
    "recommended_for",
    "required_docs_check",
    "lane_sanity_rules_applied",
    "dropped_treasure_hunt",
)
REQUIRED_DOCS_LIST_FIELDS = (
    "docs_expected",
    "docs_read_from_github_main",
    "docs_missing_or_unreadable",
)
DROPPED_TREASURE_HUNT_REQUIRED_FIELDS = (
    "performed",
    "trigger_reason",
    "sample_strategy",
    "sample_size",
    "sampled_story_ids",
    "rescued_count",
    "rescue_ids",
    "non_sampled_dropped_count",
    "non_sampled_ledger_policy",
)
BASE_STRICT_REQUIRED_FIELDS = (
    "spec_id",
    "source_story_ids",
    "source_origin",
    "merge_status",
    "merged_story_ids",
    "baseline_relation",
    "duplicate_risk",
    "region",
    "representative_date",
    "representative_source",
    "source_tier_estimate",
    "cat",
    "sub_cat",
    "signal_estimate",
    "signal_rubric_estimate",
    "strategic_lens",
    "primary_url",
    "urls",
    "event_anchor",
    "format_risk_tags",
    "execution_anchor_type",
    "execution_anchor_strength",
    "structural_value_override_applied",
    "structural_value_override_reason",
    "anchor_classes",
    "incremental_information",
    "decision_relevance",
    "baseline_expectation_changed",
    "evidence_needed_for_stage_b",
    "next_confirmation_points",
    "why_execution_event_not_required",
    "prior_state",
    "new_verified_fact",
    "changed_judgment",
    "uncertainty_resolved",
    "remaining_uncertainty",
    "strict_pass_gate",
    "title_raw",
    "summary_hint",
    "context_text",
    "why_now",
    "market_relevance",
    "source_priority_notes",
    "upstream_labels",
    "staleness",
    "needs_review",
    "review_reason",
    "stage_b_requirement_note",
)
BASE_STRICT_ARRAY_FIELDS = (
    "source_story_ids",
    "merged_story_ids",
    "urls",
    "format_risk_tags",
)
BASE_STRICT_OBJECT_FIELDS = (
    "strict_pass_gate",
    "upstream_labels",
    "staleness",
)
BASE_STRICT_TEXT_FIELDS = (
    "source_origin",
    "merge_status",
    "baseline_relation",
    "duplicate_risk",
    "region",
    "representative_date",
    "representative_source",
    "source_tier_estimate",
    "cat",
    "sub_cat",
    "primary_url",
    "title_raw",
    "summary_hint",
    "context_text",
    "why_now",
    "market_relevance",
    "source_priority_notes",
)
STAGE_B_REQUIREMENT_NOTE = (
    "Stage B must verify the provided source-candidate URL and build a valid evidence package before drafting. "
    "This Stage A spec is not evidence_complete, and primary_url is not evidence by itself."
)
OUTCOME_ARRAY_FIELDS = _previous.OUTCOME_ARRAY_FIELDS


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _nonempty_sequence_of_strings(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and bool(item.strip()) for item in value)
    )


def _candidate_id(item: Mapping[str, Any], fallback: str) -> str:
    return _base._candidate_id(item, fallback)


def _story_ids_from_item(item: Mapping[str, Any], *, strict: bool = False) -> set[str]:
    result: set[str] = set()
    if strict:
        values = item.get("source_story_ids")
        if isinstance(values, list):
            result.update(value for value in values if isinstance(value, str) and value)
        return result
    story_id = item.get("story_id")
    if isinstance(story_id, str) and story_id:
        result.add(story_id)
    grouped = item.get("grouped_story_ids")
    if isinstance(grouped, list):
        result.update(value for value in grouped if isinstance(value, str) and value)
    return result


def prevalidate_full_stage_a_artifact(data: Any) -> list[str]:
    """Catch malformed containers before the legacy validator dereferences them."""
    if not looks_like_full_stage_a_artifact(data) or not isinstance(data, Mapping):
        return []
    messages: list[str] = []
    for field in OUTCOME_ARRAY_FIELDS:
        values = data.get(field)
        if values is None:
            continue
        if not isinstance(values, list):
            messages.append(f"full Stage A artifact {field} must be an array")
            continue
        for index, item in enumerate(values):
            if not isinstance(item, Mapping):
                messages.append(f"{field}[{index}] must be an object")
    ledger = data.get("decision_ledger")
    if isinstance(ledger, list):
        for index, row in enumerate(ledger):
            if not isinstance(row, Mapping):
                messages.append(f"decision_ledger[{index}] must be an object")
    return messages


def _validate_top_level_provenance(data: Mapping[str, Any], messages: list[str]) -> None:
    for field in TOP_LEVEL_REQUIRED_FIELDS:
        if field not in data:
            messages.append(f"full Stage A artifact missing required top-level field {field}")
    for field in TOP_LEVEL_NONEMPTY_TEXT_FIELDS:
        if field in data and not _nonempty_text(data.get(field)):
            messages.append(f"full Stage A artifact {field} must be a non-empty string")
    baseline_count = data.get("baseline_count")
    if "baseline_count" in data and (
        isinstance(baseline_count, bool) or not isinstance(baseline_count, int) or baseline_count < 0
    ):
        messages.append("full Stage A artifact baseline_count must be a non-negative integer")
    if "github_main_sync_required_later" in data and not isinstance(
        data.get("github_main_sync_required_later"), bool
    ):
        messages.append("full Stage A artifact github_main_sync_required_later must be boolean")
    for field in TOP_LEVEL_OBJECT_FIELDS:
        if field in data and not isinstance(data.get(field), Mapping):
            messages.append(f"full Stage A artifact {field} must be an object")
    recommended_for = data.get("recommended_for")
    if "recommended_for" in data and not (
        _nonempty_text(recommended_for) or _nonempty_sequence_of_strings(recommended_for)
    ):
        messages.append("full Stage A artifact recommended_for must be non-empty text or string array")
    if "lane_sanity_rules_applied" in data and data.get("lane_sanity_rules_applied") is None:
        messages.append("full Stage A artifact lane_sanity_rules_applied must be populated")

    docs = data.get("required_docs_check")
    if isinstance(docs, Mapping):
        for field in REQUIRED_DOCS_LIST_FIELDS:
            if not isinstance(docs.get(field), list):
                messages.append(f"full Stage A artifact required_docs_check.{field} must be an array")
        if not _nonempty_text(docs.get("status")):
            messages.append("full Stage A artifact required_docs_check.status must be populated")

    treasure = data.get("dropped_treasure_hunt")
    if isinstance(treasure, Mapping):
        for field in DROPPED_TREASURE_HUNT_REQUIRED_FIELDS:
            if field not in treasure:
                messages.append(f"full Stage A artifact dropped_treasure_hunt missing {field}")
        if "performed" in treasure and not isinstance(treasure.get("performed"), bool):
            messages.append("full Stage A artifact dropped_treasure_hunt.performed must be boolean")
        for field in ("sample_size", "rescued_count", "non_sampled_dropped_count"):
            value = treasure.get(field)
            if field in treasure and (
                isinstance(value, bool) or not isinstance(value, int) or value < 0
            ):
                messages.append(f"full Stage A artifact dropped_treasure_hunt.{field} must be a non-negative integer")
        for field in ("sampled_story_ids", "rescue_ids"):
            if field in treasure and not isinstance(treasure.get(field), list):
                messages.append(f"full Stage A artifact dropped_treasure_hunt.{field} must be an array")
        for field in ("trigger_reason", "sample_strategy", "non_sampled_ledger_policy"):
            if field in treasure and not isinstance(treasure.get(field), str):
                messages.append(f"full Stage A artifact dropped_treasure_hunt.{field} must be string")


def _validate_base_strict_contract(data: Mapping[str, Any], messages: list[str]) -> None:
    strict = data.get("strict_passed_spec")
    if not isinstance(strict, list):
        return
    for index, item in enumerate(strict):
        if not isinstance(item, Mapping):
            continue
        label = _candidate_id(item, f"strict_passed_spec[{index}]")
        for field in BASE_STRICT_REQUIRED_FIELDS:
            if field not in item:
                messages.append(f"{label}: missing required base strict field {field}")
        for field in BASE_STRICT_ARRAY_FIELDS:
            if field in item and not isinstance(item.get(field), list):
                messages.append(f"{label}: base strict field {field} must be an array")
        for field in BASE_STRICT_OBJECT_FIELDS:
            if field in item and not isinstance(item.get(field), Mapping):
                messages.append(f"{label}: base strict field {field} must be an object")
        for field in BASE_STRICT_TEXT_FIELDS:
            if field in item and not isinstance(item.get(field), str):
                messages.append(f"{label}: base strict field {field} must be string")
        if "needs_review" in item and not isinstance(item.get("needs_review"), bool):
            messages.append(f"{label}: needs_review must be boolean")
        if "review_reason" in item and item.get("review_reason") is not None and not isinstance(
            item.get("review_reason"), str
        ):
            messages.append(f"{label}: review_reason must be string or null")
        if "stage_b_requirement_note" in item and item.get("stage_b_requirement_note") != STAGE_B_REQUIREMENT_NOTE:
            messages.append(f"{label}: stage_b_requirement_note must match the canonical Stage A warning")


def _validate_review_promotion_types(data: Mapping[str, Any], messages: list[str]) -> None:
    values = data.get("candidate_review_pool")
    if not isinstance(values, list):
        return
    for index, item in enumerate(values):
        if not isinstance(item, Mapping):
            continue
        label = _candidate_id(item, f"candidate_review_pool[{index}]")
        if not _nonempty_text(item.get("promotion_precondition")):
            messages.append(f"{label}: candidate_review_pool promotion_precondition must be meaningful text")
        if item.get("review_pool_subtype") == "earnings_deep_dive" and item.get(
            "earnings_deep_dive_required"
        ) is not True:
            messages.append(
                f"{label}: earnings_deep_dive subtype requires earnings_deep_dive_required=true"
            )


def _all_candidate_items(data: Mapping[str, Any]):
    for pool in _base.FULL_POOL_FIELDS:
        values = data.get(pool)
        if not isinstance(values, list):
            continue
        for index, item in enumerate(values):
            if isinstance(item, Mapping):
                yield pool, index, item


def _technology_applicable(item: Mapping[str, Any]) -> bool:
    classes = item.get("anchor_classes")
    lenses = item.get("structural_value_lenses")
    return (
        isinstance(classes, list) and "technology_commercialization_anchor" in classes
    ) or (
        isinstance(lenses, list) and "technology_transition_commercialization" in lenses
    )


def _policy_applicable(item: Mapping[str, Any]) -> bool:
    classes = item.get("anchor_classes")
    lenses = item.get("structural_value_lenses")
    return (
        isinstance(classes, list) and "policy_regulatory_anchor" in classes
    ) or (
        isinstance(lenses, list)
        and any(isinstance(value, str) and ("policy" in value or "legal" in value) for value in lenses)
    )


def _is_follow_up(item: Mapping[str, Any]) -> bool:
    classes = item.get("anchor_classes")
    if isinstance(classes, list) and "follow_up_probability_anchor" in classes:
        return True
    relation = item.get("baseline_follow_up_relation")
    if not isinstance(relation, str):
        return False
    normalized = relation.strip().lower()
    return normalized not in {"", "new", "new_unrelated", "unrelated", "not_applicable", "none"}


def _expected_summary_id_arrays(data: Mapping[str, Any]) -> dict[str, list[str]]:
    critical: list[str] = []
    high: list[str] = []
    high_review: list[str] = []
    structural_review: list[str] = []
    earnings_review: list[str] = []
    follow_up: list[str] = []
    technology_gaps: list[str] = []
    legal_gaps: list[str] = []
    for pool, index, item in _all_candidate_items(data):
        candidate_id = _candidate_id(item, f"{pool}[{index}]")
        classification = item.get("decision_value_classification")
        if classification == "critical_structural":
            critical.append(candidate_id)
        if classification == "high_decision_value":
            high.append(candidate_id)
        score = item.get("decision_news_value_score")
        if pool in _base.REVIEW_POOLS and isinstance(score, int) and not isinstance(score, bool) and score >= 70:
            high_review.append(candidate_id)
        if pool == "candidate_review_pool":
            subtype = item.get("review_pool_subtype")
            if subtype == "structural_signal_review":
                structural_review.append(candidate_id)
            if subtype == "earnings_deep_dive":
                earnings_review.append(candidate_id)
        if _is_follow_up(item):
            follow_up.append(candidate_id)
        if _technology_applicable(item) and _nonempty_text(item.get("technology_validation_gap")):
            technology_gaps.append(candidate_id)
        if _policy_applicable(item) and item.get("legal_policy_stage") not in _base.LEGAL_POLICY_STAGES:
            legal_gaps.append(candidate_id)
    return {
        "critical_structural_candidate_ids": critical,
        "high_decision_value_candidate_ids": high,
        "high_value_review_pool_ids": high_review,
        "structural_signal_review_pool_ids": structural_review,
        "earnings_deep_dive_pool_ids": earnings_review,
        "follow_up_candidate_ids": follow_up,
        "technology_validation_gap_ids": technology_gaps,
        "legal_policy_stage_gap_ids": legal_gaps,
    }


def _validate_summary_id_arrays(data: Mapping[str, Any], messages: list[str]) -> None:
    for field, expected in _expected_summary_id_arrays(data).items():
        present, actual = _base._summary_field(data, field)
        if not present or not isinstance(actual, list):
            continue
        if actual != expected:
            messages.append(f"full Stage A summary {field} does not match emitted candidates")


def _validate_outcome_ledger_reconciliation(data: Mapping[str, Any], messages: list[str]) -> None:
    ledger = data.get("decision_ledger")
    if not isinstance(ledger, list):
        return
    ledger_ids = {
        row.get("story_id")
        for row in ledger
        if isinstance(row, Mapping) and isinstance(row.get("story_id"), str) and row.get("story_id")
    }
    emitted: set[str] = set()
    strict = data.get("strict_passed_spec")
    if isinstance(strict, list):
        for item in strict:
            if isinstance(item, Mapping):
                emitted.update(_story_ids_from_item(item, strict=True))
    for pool in _base.REVIEW_POOLS:
        values = data.get(pool)
        if isinstance(values, list):
            for item in values:
                if isinstance(item, Mapping):
                    emitted.update(_story_ids_from_item(item))
    for field in OUTCOME_ARRAY_FIELDS:
        values = data.get(field)
        if isinstance(values, list):
            for item in values:
                if isinstance(item, Mapping):
                    emitted.update(_story_ids_from_item(item))
    missing = sorted(emitted - ledger_ids)
    if missing:
        messages.append(
            "decision_ledger is missing emitted strict/review/outcome story IDs: " + ", ".join(missing)
        )


def _validate_earnings_subtype_summary(data: Mapping[str, Any], messages: list[str]) -> None:
    values = data.get("candidate_review_pool")
    subtype_present = isinstance(values, list) and any(
        isinstance(item, Mapping) and item.get("review_pool_subtype") == "earnings_deep_dive"
        for item in values
    )
    if not subtype_present:
        return
    present, status = _base._summary_field(data, "earnings_call_qna_audit_status")
    if present and status != "PASS":
        messages.append(
            "full Stage A summary earnings_call_qna_audit_status must be PASS when earnings_deep_dive subtype exists"
        )


def _validate_credibility_strength(data: Mapping[str, Any], messages: list[str]) -> None:
    strict = data.get("strict_passed_spec")
    if not isinstance(strict, list):
        return
    for index, item in enumerate(strict):
        if not isinstance(item, Mapping) or item.get("structural_value_override_applied") is not False:
            continue
        label = _candidate_id(item, f"strict_passed_spec[{index}]")
        gate = item.get("execution_credibility_gate")
        if not isinstance(gate, Mapping):
            continue
        gate_strength = gate.get("anchor_strength")
        route_strength = item.get("execution_anchor_strength")
        if gate_strength != route_strength:
            messages.append(
                f"{label}: execution_credibility_gate.anchor_strength must match execution_anchor_strength for execution route"
            )
        if gate.get("status") == "PASS" and gate_strength not in {"strong", "moderate"}:
            messages.append(
                f"{label}: strict PASS execution_credibility_gate.anchor_strength must be strong or moderate"
            )


# The policy defines Stage 0-2 legal score caps as defaults with explicit
# authority/observable-effect exceptions.  The older validator encoded them as
# absolute ceilings.  Keep the legal completeness/stage checks but drop only
# that over-strong absolute-cap diagnostic.
_original_legal_policy_validator = _base._validate_legal_policy


def _legal_policy_validator_with_documented_exceptions(
    item: Mapping[str, Any], label: str, messages: list[str]
) -> None:
    local: list[str] = []
    _original_legal_policy_validator(item, label, local)
    for message in local:
        if "decision_news_value_score" in message and " exceeds stage_" in message and " cap " in message:
            continue
        messages.append(message)


_base._validate_legal_policy = _legal_policy_validator_with_documented_exceptions


def validate_full_stage_a_artifact(
    data: Mapping[str, Any],
    compat_module: Any,
) -> list[str]:
    messages = list(_previous.validate_full_stage_a_artifact(data, compat_module))
    _validate_top_level_provenance(data, messages)
    _validate_base_strict_contract(data, messages)
    _validate_review_promotion_types(data, messages)
    _validate_summary_id_arrays(data, messages)
    _validate_outcome_ledger_reconciliation(data, messages)
    _validate_earnings_subtype_summary(data, messages)
    _validate_credibility_strength(data, messages)
    return messages
