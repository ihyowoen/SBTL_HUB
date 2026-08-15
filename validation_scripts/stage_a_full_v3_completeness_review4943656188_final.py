#!/usr/bin/env python3
"""Final fail-closed surface for reviews through 4943729715.

Completes the active Prompt 0.1 / Structural V3 Stage A contract without
changing editorial decisions or introducing run-specific exceptions.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping

from validation_scripts import stage_a_full_v3_completeness as _base
from validation_scripts import stage_a_full_v3_completeness_review4943656188 as _previous

CANONICAL_POLICY_VERSION = _previous.CANONICAL_POLICY_VERSION
CANONICAL_POLICY_FILE = _previous.CANONICAL_POLICY_FILE
looks_like_full_stage_a_artifact = _previous.looks_like_full_stage_a_artifact
prevalidate_full_stage_a_artifact = _previous.prevalidate_full_stage_a_artifact

TOP_LEVEL_ARRAY_FIELDS = (
    "legacy_keep",
    "review_pool",
    "dropped_treasure_hunt_result",
)
BASE_SUMMARY_INTEGER_FIELDS = (
    "legacy_keep_count",
    "strict_passed_spec_count",
    "needs_review_count",
    "rejected_count",
    "existing_reinforcement_count",
    "support_source_only_count",
    "duplicate_or_reinforcement_count",
    "stale_discarded_count",
    "stale_warm_review_count",
    "total_ledger_count",
)
STRICT_GATE_REQUIRED_FIELDS = (
    "status",
    "reason",
    "anchor_supported_by_upstream_text",
)
UPSTREAM_LABEL_REQUIRED_FIELDS = (
    "triage_status",
    "matched_buckets",
    "drop_reason",
    "integrity_group_id",
    "integrity_is_best",
    "drop_reason_overridden",
)
STALENESS_REQUIRED_FIELDS = (
    "event_date",
    "publication_date",
    "staleness_gap_days",
    "staleness_suspected",
    "fresh_followup",
    "staleness_override",
    "decision",
)
MANDATORY_STAGE_A_DOCS = (
    "docs/FACT_DISCIPLINE.md",
    "docs/STRUCTURAL_NEWS_VALUE_SELECTION.md",
    "docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md",
    "docs/PROMPT_ABC_DEFAULT_MODE.md",
    "docs/PROMPT_ABC_SUPPORTING_RULES.md",
    "docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md",
    "docs/CARD_ID_STANDARD.md",
    "docs/WORKFLOW.md",
    "docs/OPERATIONS.md",
    "docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md",
)
V3_APPLICATION_MARKERS = (
    "earnings_call_qna_rule_applied",
    "follow_up_probability_review_applied",
    "portfolio_coverage_audit_applied",
)
CANONICAL_DISPOSITION_POOLS = (
    "strict_passed_spec",
    "candidate_review_pool",
    "watchlist_context_pool",
    "reject_or_support_only_pool",
    "rejected",
    "existing_reinforcement",
    "support_source_only",
)
BASE_REVIEW_REQUIRED_FIELDS = (
    "review_pool_item_id",
    "upstream_status",
    "reason_for_review",
    "review_type",
    "what_must_be_checked_before_promotion",
    "why_not_strict_passed_spec",
    "baseline_relation_if_known",
    "staleness_decision",
    "recommended_next_action",
    "carry_forward_policy",
    "next_action_condition",
    "review_pool_resolution_status",
)
BASE_REVIEW_NONEMPTY_TEXT_FIELDS = (
    "review_pool_item_id",
    "upstream_status",
    "reason_for_review",
    "review_type",
    "what_must_be_checked_before_promotion",
    "why_not_strict_passed_spec",
    "staleness_decision",
    "recommended_next_action",
    "carry_forward_policy",
    "next_action_condition",
    "review_pool_resolution_status",
)
BASE_REJECTED_REQUIRED_FIELDS = (
    "upstream_status",
    "rejected_reason_code",
    "rejected_reason_detail",
    "hard_reject_basis",
    "hard_reject_confidence",
    "hard_reject_positive_test_passed",
    "hard_reject_anti_overclosure_check",
    "why_not_review_pool",
    "staleness_decision",
    "notes",
)
BASE_REJECTED_NONEMPTY_TEXT_FIELDS = (
    "upstream_status",
    "rejected_reason_code",
    "rejected_reason_detail",
    "hard_reject_basis",
    "hard_reject_confidence",
    "hard_reject_anti_overclosure_check",
    "why_not_review_pool",
    "staleness_decision",
)
REINFORCEMENT_REQUIRED_FIELDS = (
    "reinforcement_type",
    "reason_not_new_card",
    "notes",
)
REINFORCEMENT_NONEMPTY_TEXT_FIELDS = (
    "reinforcement_type",
    "reason_not_new_card",
)
SUPPORT_SOURCE_REQUIRED_FIELDS = (
    "potential_supported_topic",
    "reason_not_independent_card",
    "notes",
)
SUPPORT_SOURCE_NONEMPTY_TEXT_FIELDS = (
    "potential_supported_topic",
    "reason_not_independent_card",
)
REVIEW_RESOLUTION_REQUIRED_FIELDS = (
    "review_pool_item_id",
    "original_review_pool_partition",
    "current_disposition",
    "disposition_basis",
    "carry_forward_policy",
    "next_action_condition",
    "whether_user_authorization_required",
)
REVIEW_RESOLUTION_NONEMPTY_TEXT_FIELDS = (
    "review_pool_item_id",
    "original_review_pool_partition",
    "current_disposition",
    "disposition_basis",
    "carry_forward_policy",
    "next_action_condition",
)
ALLOWED_REVIEW_RESOLUTION_PARTITIONS = {
    "candidate_review_pool",
    "watchlist_context_pool",
    "reject_or_support_only_pool",
    "review_pool",
}


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _story_ids(item: Mapping[str, Any], *, strict: bool = False) -> set[str]:
    result: set[str] = set()
    if strict:
        values = item.get("source_story_ids")
        if isinstance(values, list):
            result.update(value for value in values if _nonempty_text(value))
        return result
    story_id = item.get("story_id")
    if _nonempty_text(story_id):
        result.add(story_id)
    grouped = item.get("grouped_story_ids")
    if isinstance(grouped, list):
        result.update(value for value in grouped if _nonempty_text(value))
    return result


def _validate_remaining_top_level_surface(data: Mapping[str, Any], messages: list[str]) -> None:
    for field in TOP_LEVEL_ARRAY_FIELDS:
        if not isinstance(data.get(field), list):
            messages.append(f"full Stage A artifact {field} must be an array")
    summary = data.get("summary")
    if not isinstance(summary, Mapping):
        return
    for field in BASE_SUMMARY_INTEGER_FIELDS:
        value = summary.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            messages.append(f"full Stage A summary {field} must be a non-negative integer")
    if summary.get("ledger_matches_story_count") is not True:
        messages.append("full Stage A summary ledger_matches_story_count must be true")
    ledger = data.get("decision_ledger")
    if isinstance(ledger, list) and summary.get("total_ledger_count") != len(ledger):
        messages.append("full Stage A summary total_ledger_count must equal decision_ledger length")
    strict = data.get("strict_passed_spec")
    if isinstance(strict, list) and summary.get("strict_passed_spec_count") != len(strict):
        messages.append("full Stage A summary strict_passed_spec_count must equal strict_passed_spec length")
    for field, pool in (
        ("rejected_count", "rejected"),
        ("existing_reinforcement_count", "existing_reinforcement"),
        ("support_source_only_count", "support_source_only"),
        ("legacy_keep_count", "legacy_keep"),
    ):
        values = data.get(pool)
        if isinstance(values, list) and summary.get(field) != len(values):
            messages.append(f"full Stage A summary {field} must equal {pool} length")


def _validate_strict_nested_base_surface(data: Mapping[str, Any], messages: list[str]) -> None:
    strict = data.get("strict_passed_spec")
    if not isinstance(strict, list):
        return
    for index, item in enumerate(strict):
        if not isinstance(item, Mapping):
            continue
        label = _base._candidate_id(item, f"strict_passed_spec[{index}]")
        gate = item.get("strict_pass_gate")
        if isinstance(gate, Mapping):
            for field in STRICT_GATE_REQUIRED_FIELDS:
                if field not in gate:
                    messages.append(f"{label}: strict_pass_gate missing {field}")
            if gate.get("status") == "pass" and not _nonempty_text(gate.get("why_not_review_pool")):
                messages.append(f"{label}: strict_pass_gate pass requires why_not_review_pool")
            if "reason" in gate and not _nonempty_text(gate.get("reason")):
                messages.append(f"{label}: strict_pass_gate.reason must be populated")
            if "anchor_supported_by_upstream_text" in gate and gate.get(
                "anchor_supported_by_upstream_text"
            ) not in {True, False, "unknown"}:
                messages.append(
                    f"{label}: strict_pass_gate.anchor_supported_by_upstream_text invalid"
                )
        upstream = item.get("upstream_labels")
        if isinstance(upstream, Mapping):
            for field in UPSTREAM_LABEL_REQUIRED_FIELDS:
                if field not in upstream:
                    messages.append(f"{label}: upstream_labels missing {field}")
        staleness = item.get("staleness")
        if isinstance(staleness, Mapping):
            for field in STALENESS_REQUIRED_FIELDS:
                if field not in staleness:
                    messages.append(f"{label}: staleness missing {field}")


def _validate_strict_bucket_exclusions(data: Mapping[str, Any], messages: list[str]) -> None:
    strict = data.get("strict_passed_spec")
    if not isinstance(strict, list):
        return
    disqualifying = (
        ("baseline_relation", "duplicate_of_main"),
        ("duplicate_risk", "fatal"),
        ("staleness_decision", "stale"),
    )
    for index, item in enumerate(strict):
        if not isinstance(item, Mapping):
            continue
        label = _base._candidate_id(item, f"strict_passed_spec[{index}]")
        for field, blocked_value in disqualifying:
            value = item.get(field)
            if isinstance(value, str) and value.strip().lower() == blocked_value:
                messages.append(
                    f"{label}: strict_passed_spec cannot use {field}={blocked_value}; route to a non-strict disposition"
                )


def _validate_required_docs_check(data: Mapping[str, Any], messages: list[str]) -> None:
    docs = data.get("required_docs_check")
    if not isinstance(docs, Mapping):
        return
    if docs.get("status") != "PASS":
        messages.append("full Stage A artifact required_docs_check.status must be PASS")
    expected = docs.get("docs_expected")
    read = docs.get("docs_read_from_github_main")
    missing = docs.get("docs_missing_or_unreadable")
    mandatory = set(MANDATORY_STAGE_A_DOCS)
    for field, values in (
        ("docs_expected", expected),
        ("docs_read_from_github_main", read),
    ):
        if not isinstance(values, list):
            continue
        if any(not _nonempty_text(value) for value in values) or len(set(values)) != len(values):
            messages.append(f"full Stage A artifact required_docs_check.{field} must contain unique non-empty paths")
            continue
        absent = sorted(mandatory - set(values))
        if absent:
            messages.append(
                f"full Stage A artifact required_docs_check.{field} missing mandatory documents: "
                + ", ".join(absent)
            )
    if isinstance(missing, list) and missing:
        messages.append("full Stage A artifact required_docs_check.docs_missing_or_unreadable must be empty")


def _validate_application_markers(data: Mapping[str, Any], messages: list[str]) -> None:
    for field in V3_APPLICATION_MARKERS:
        present, value = _base._summary_field(data, field)
        if not present or value is not True:
            messages.append(f"full Stage A summary {field} must be true")


def _validate_story_identity(item: Mapping[str, Any], label: str, messages: list[str]) -> None:
    story_id = item.get("story_id")
    grouped = item.get("grouped_story_ids")
    has_story = _nonempty_text(story_id)
    has_group = (
        isinstance(grouped, list)
        and bool(grouped)
        and all(_nonempty_text(value) for value in grouped)
    )
    if not has_story and not has_group:
        messages.append(f"{label}: requires story_id or non-empty grouped_story_ids")


def _validate_review_base_contract(data: Mapping[str, Any], messages: list[str]) -> None:
    for pool in _base.REVIEW_POOLS:
        values = data.get(pool)
        if not isinstance(values, list):
            continue
        for index, item in enumerate(values):
            if not isinstance(item, Mapping):
                continue
            label = _base._candidate_id(item, f"{pool}[{index}]")
            _validate_story_identity(item, label, messages)
            for field in BASE_REVIEW_REQUIRED_FIELDS:
                if field not in item:
                    messages.append(f"{label}: missing required base review field {field}")
            for field in BASE_REVIEW_NONEMPTY_TEXT_FIELDS:
                if field in item and not _nonempty_text(item.get(field)):
                    messages.append(f"{label}: base review field {field} must be non-empty text")


def _validate_review_resolution_ledger(data: Mapping[str, Any], messages: list[str]) -> None:
    review_items_present = any(
        isinstance(data.get(pool), list) and bool(data.get(pool))
        for pool in (*_base.REVIEW_POOLS, "review_pool")
    )
    ledger = data.get("review_pool_resolution_ledger")
    if review_items_present and not isinstance(ledger, list):
        messages.append("full Stage A artifact review_pool_resolution_ledger must be an array when review items exist")
        return
    if not isinstance(ledger, list):
        return
    for index, row in enumerate(ledger):
        label = f"review_pool_resolution_ledger[{index}]"
        if not isinstance(row, Mapping):
            messages.append(f"{label} must be an object")
            continue
        _validate_story_identity(row, label, messages)
        for field in REVIEW_RESOLUTION_REQUIRED_FIELDS:
            if field not in row:
                messages.append(f"{label}: missing required review-resolution field {field}")
        for field in REVIEW_RESOLUTION_NONEMPTY_TEXT_FIELDS:
            if field in row and not _nonempty_text(row.get(field)):
                messages.append(f"{label}: review-resolution field {field} must be non-empty text")
        partition = row.get("original_review_pool_partition")
        if _nonempty_text(partition) and partition not in ALLOWED_REVIEW_RESOLUTION_PARTITIONS:
            messages.append(
                f"{label}: original_review_pool_partition must be a supported review partition"
            )
        if "whether_user_authorization_required" in row and not isinstance(
            row.get("whether_user_authorization_required"), bool
        ):
            messages.append(
                f"{label}: whether_user_authorization_required must be boolean"
            )


def _validate_rejected_base_contract(data: Mapping[str, Any], messages: list[str]) -> None:
    values = data.get("rejected")
    if not isinstance(values, list):
        return
    for index, item in enumerate(values):
        if not isinstance(item, Mapping):
            continue
        label = item.get("story_id") if _nonempty_text(item.get("story_id")) else f"rejected[{index}]"
        _validate_story_identity(item, label, messages)
        for field in BASE_REJECTED_REQUIRED_FIELDS:
            if field not in item:
                messages.append(f"{label}: missing required rejected field {field}")
        for field in BASE_REJECTED_NONEMPTY_TEXT_FIELDS:
            if field in item and not _nonempty_text(item.get(field)):
                messages.append(f"{label}: rejected field {field} must be non-empty text")
        if "hard_reject_positive_test_passed" in item and item.get("hard_reject_positive_test_passed") is not True:
            messages.append(f"{label}: hard_reject_positive_test_passed must be true")


def _validate_nonreview_outcome_contracts(data: Mapping[str, Any], messages: list[str]) -> None:
    configs = (
        (
            "existing_reinforcement",
            REINFORCEMENT_REQUIRED_FIELDS,
            REINFORCEMENT_NONEMPTY_TEXT_FIELDS,
        ),
        (
            "support_source_only",
            SUPPORT_SOURCE_REQUIRED_FIELDS,
            SUPPORT_SOURCE_NONEMPTY_TEXT_FIELDS,
        ),
    )
    for pool, required_fields, text_fields in configs:
        values = data.get(pool)
        if not isinstance(values, list):
            continue
        for index, item in enumerate(values):
            label = f"{pool}[{index}]"
            if not isinstance(item, Mapping):
                messages.append(f"{label} must be an object")
                continue
            _validate_story_identity(item, label, messages)
            for field in required_fields:
                if field not in item:
                    messages.append(f"{label}: missing required {pool} field {field}")
            for field in text_fields:
                if field in item and not _nonempty_text(item.get(field)):
                    messages.append(f"{label}: {pool} field {field} must be non-empty text")


def _validate_unique_dispositions(data: Mapping[str, Any], messages: list[str]) -> None:
    assignments: dict[str, list[str]] = defaultdict(list)
    for pool in CANONICAL_DISPOSITION_POOLS:
        values = data.get(pool)
        if not isinstance(values, list):
            continue
        for index, item in enumerate(values):
            if not isinstance(item, Mapping):
                continue
            ids = _story_ids(item, strict=(pool == "strict_passed_spec"))
            for story_id in ids:
                assignments[story_id].append(f"{pool}[{index}]")
    for story_id, locations in sorted(assignments.items()):
        if len(locations) > 1:
            messages.append(
                f"story {story_id} must appear in exactly one Stage A disposition; found "
                + ", ".join(locations)
            )


def _validate_summary_id_arrays_unordered(data: Mapping[str, Any], messages: list[str]) -> None:
    expected_map = _previous._expected_summary_id_arrays(data)
    for field, expected in expected_map.items():
        present, actual = _base._summary_field(data, field)
        if not present or not isinstance(actual, list):
            continue
        legacy_message = f"full Stage A summary {field} does not match emitted candidates"
        valid_strings = all(_nonempty_text(value) for value in actual)
        if not valid_strings:
            messages.append(f"full Stage A summary {field} must contain only non-empty story/spec IDs")
            continue
        unique = len(set(actual)) == len(actual)
        if not unique:
            messages.append(f"full Stage A summary {field} must not contain duplicate IDs")
        if unique and set(actual) == set(expected):
            while legacy_message in messages:
                messages.remove(legacy_message)
        elif set(actual) != set(expected) and legacy_message not in messages:
            messages.append(legacy_message)


def _validate_denominator_gap_cap(data: Mapping[str, Any], messages: list[str]) -> None:
    for pool, index, item in _previous._all_candidate_items(data):
        if item.get("denominator_gap") is not True:
            continue
        breakdown = item.get("decision_value_breakdown")
        if not isinstance(breakdown, Mapping):
            continue
        systemic_scale = breakdown.get("systemic_scale")
        if isinstance(systemic_scale, (int, float)) and not isinstance(systemic_scale, bool) and systemic_scale > 2:
            label = _base._candidate_id(item, f"{pool}[{index}]")
            messages.append(
                f"{label}: denominator_gap=true caps decision_value_breakdown.systemic_scale at 2/5"
            )


def validate_full_stage_a_artifact(
    data: Mapping[str, Any],
    compat_module: Any,
) -> list[str]:
    messages = list(_previous.validate_full_stage_a_artifact(data, compat_module))
    _validate_remaining_top_level_surface(data, messages)
    _validate_strict_nested_base_surface(data, messages)
    _validate_strict_bucket_exclusions(data, messages)
    _validate_required_docs_check(data, messages)
    _validate_application_markers(data, messages)
    _validate_review_base_contract(data, messages)
    _validate_review_resolution_ledger(data, messages)
    _validate_rejected_base_contract(data, messages)
    _validate_nonreview_outcome_contracts(data, messages)
    _validate_unique_dispositions(data, messages)
    _validate_summary_id_arrays_unordered(data, messages)
    _validate_denominator_gap_cap(data, messages)
    return messages
