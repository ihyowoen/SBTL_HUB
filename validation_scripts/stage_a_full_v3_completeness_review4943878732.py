#!/usr/bin/env python3
"""Final Stage A governance hardening through Codex review 4943904060.

This layer keeps the three first-class review partitions authoritative, treats
legacy ``review_pool[]`` as a mirror only, requires review audit metadata even
for an empty workload, enforces exactly one resolution-ledger row per logical
review item, validates the next-call safety gates, requires partition-specific
review metadata, applies canonical V3 route validation to candidate review
items, and restores legal-policy default caps unless an explicit documented
exception is proven.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Mapping

from validation_scripts import stage_a_full_v3_completeness as _base_contract
from validation_scripts import stage_a_full_v3_completeness_review4943777463 as _previous
from validation_scripts.v3_stage_contract_flow_check import route_package_errors

CANONICAL_POLICY_VERSION = _previous.CANONICAL_POLICY_VERSION
CANONICAL_POLICY_FILE = _previous.CANONICAL_POLICY_FILE
looks_like_full_stage_a_artifact = _previous.looks_like_full_stage_a_artifact
prevalidate_full_stage_a_artifact = _previous.prevalidate_full_stage_a_artifact

_CANONICAL_REVIEW_POOLS = (
    "candidate_review_pool",
    "watchlist_context_pool",
    "reject_or_support_only_pool",
)

_NEXT_CALL_PASS_FIELDS = (
    "stage_a_validity_status",
    "artifact_consistency_status",
    "csv_schema_status",
    "review_pool_partition_status",
    "review_pool_carry_forward_ledger_status",
    "strict_pass_gate_metadata_status",
    "baseline_duplicate_screen_status",
)
_NEXT_CALL_REQUIRED_FIELDS = (
    "recommended_next_call",
    "recommended_prompt_id",
    "recommended_input_universe",
    "reason",
    "blocked_items_summary",
)
_CANDIDATE_REVIEW_TEXT_FIELDS = (
    "bounded_review_question",
    "promotion_precondition",
    "recommended_review_method",
    "evidence_or_duplicate_question",
    "final_review_pool_disposition",
)
_CANDIDATE_REVIEW_DISPOSITIONS = {
    "not_cardable_after_review",
    "support_source_only_after_review",
    "watchlist_only_after_review",
    "duplicate_or_reinforcement_after_review",
    "promote_to_strict_spec_after_review",
    "needs_user_decision_after_review",
}
_WATCHLIST_TEXT_FIELDS = (
    "why_context_only",
    "future_trigger_to_reopen",
    "recommended_monitoring_action",
)
_REJECT_SUPPORT_TEXT_FIELDS = (
    "reject_or_support_only_basis",
    "final_reason",
)
_LEGAL_EXCEPTION_BASES_BY_STAGE = {
    "stage_0_rhetoric_or_advocacy": {
        "immediate_authority",
        "independently_verified_market_effect",
    },
    "stage_1_roadmap_consultation_or_draft_standard": {
        "current_administrative_procurement_funding_or_market_practice_change",
    },
    "stage_2_bill_or_proposed_rule": {
        "near_high_probability_adoption_with_material_observable_effect",
    },
}


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _story_id_set(item: Mapping[str, Any]) -> set[str]:
    ids: set[str] = set()
    story_id = item.get("story_id")
    if _nonempty_text(story_id):
        ids.add(story_id.strip())
    grouped = item.get("grouped_story_ids")
    if isinstance(grouped, list):
        ids.update(value.strip() for value in grouped if _nonempty_text(value))
    return ids


def _candidate_label(item: Mapping[str, Any], fallback: str) -> str:
    for field in ("review_pool_item_id", "spec_id", "story_id"):
        value = item.get(field)
        if _nonempty_text(value):
            return value.strip()
    return fallback


def _canonical_review_items(
    data: Mapping[str, Any], messages: list[str]
) -> dict[str, tuple[str, set[str]]]:
    items: dict[str, tuple[str, set[str]]] = {}
    for pool in _CANONICAL_REVIEW_POOLS:
        values = data.get(pool)
        if not isinstance(values, list):
            continue
        for index, item in enumerate(values):
            if not isinstance(item, Mapping):
                continue
            item_id = item.get("review_pool_item_id")
            if not _nonempty_text(item_id):
                continue
            item_id = item_id.strip()
            if item_id in items:
                prior_pool = items[item_id][0]
                messages.append(
                    f"{pool}[{index}]: review_pool_item_id {item_id} duplicates first-class review item from {prior_pool}"
                )
                continue
            items[item_id] = (pool, _story_id_set(item))
    return items


def _validate_review_audit_metadata(
    data: Mapping[str, Any], messages: list[str]
) -> dict[str, tuple[str, set[str]]]:
    expected = _canonical_review_items(data, messages)

    partition_summary = data.get("review_pool_partition_summary")
    if not isinstance(partition_summary, Mapping):
        messages.append(
            "full Stage A artifact review_pool_partition_summary must be a top-level object even when review pools are empty"
        )

    if data.get("review_pool_carry_forward_ledger_status") != "PASS":
        messages.append(
            "full Stage A artifact review_pool_carry_forward_ledger_status must be PASS even when review pools are empty"
        )

    ledger = data.get("review_pool_resolution_ledger")
    if not isinstance(ledger, list):
        messages.append(
            "full Stage A artifact review_pool_resolution_ledger must be a top-level array even when review pools are empty"
        )
        return expected

    ledger_ids: list[str] = []
    for row in ledger:
        if not isinstance(row, Mapping):
            continue
        item_id = row.get("review_pool_item_id")
        if _nonempty_text(item_id):
            ledger_ids.append(item_id.strip())

    counts = Counter(ledger_ids)
    for item_id in sorted(expected):
        count = counts.get(item_id, 0)
        if count != 1:
            messages.append(
                f"review_pool_resolution_ledger must contain exactly one row for emitted review item {item_id}; found {count}"
            )
    for item_id, count in sorted(counts.items()):
        if count > 1:
            messages.append(
                f"review_pool_resolution_ledger contains duplicate rows for review_pool_item_id {item_id}; found {count}"
            )
    return expected


def _validate_legacy_review_aggregate(
    data: Mapping[str, Any],
    expected: Mapping[str, tuple[str, set[str]]],
    messages: list[str],
) -> None:
    legacy = data.get("review_pool")
    if not isinstance(legacy, list):
        return

    seen: set[str] = set()
    for index, item in enumerate(legacy):
        if not isinstance(item, Mapping):
            continue
        item_id = item.get("review_pool_item_id")
        if not _nonempty_text(item_id):
            messages.append(
                f"review_pool[{index}]: legacy aggregate item must identify review_pool_item_id matching a first-class review item"
            )
            continue
        item_id = item_id.strip()
        if item_id in seen:
            messages.append(
                f"review_pool[{index}]: duplicate legacy aggregate item {item_id}"
            )
        seen.add(item_id)

        expected_item = expected.get(item_id)
        if expected_item is None:
            messages.append(
                f"review_pool[{index}]: legacy aggregate item {item_id} has no matching first-class review partition entry"
            )
            continue

        expected_partition, expected_story_ids = expected_item
        actual_partition = item.get("review_pool_partition")
        if actual_partition != expected_partition:
            messages.append(
                f"review_pool[{index}]: review_pool_partition must mirror first-class partition {expected_partition} for {item_id}"
            )
        actual_story_ids = _story_id_set(item)
        if actual_story_ids != expected_story_ids:
            messages.append(
                f"review_pool[{index}]: story identity must mirror first-class review item {item_id}; "
                f"expected={sorted(expected_story_ids)!r} actual={sorted(actual_story_ids)!r}"
            )


def _validate_next_call_safety(data: Mapping[str, Any], messages: list[str]) -> None:
    for field in _NEXT_CALL_PASS_FIELDS:
        if data.get(field) != "PASS":
            messages.append(f"full Stage A artifact {field} must be PASS before certification")

    summary = data.get("summary")
    ledger_matches = summary.get("ledger_matches_story_count") if isinstance(summary, Mapping) else None
    if ledger_matches is not True:
        messages.append("full Stage A summary ledger_matches_story_count must be true before certification")

    recommendation = data.get("next_call_recommendation")
    if not isinstance(recommendation, Mapping):
        messages.append("full Stage A artifact next_call_recommendation must be a structured object")
        return
    for field in _NEXT_CALL_REQUIRED_FIELDS:
        if field not in recommendation:
            messages.append(f"next_call_recommendation missing required field {field}")
            continue
        value = recommendation.get(field)
        if field == "blocked_items_summary":
            if not isinstance(value, (str, list, Mapping)):
                messages.append(
                    "next_call_recommendation.blocked_items_summary must be text, array, or object"
                )
        elif not _nonempty_text(value):
            messages.append(f"next_call_recommendation.{field} must be non-empty text")

    strict_count = summary.get("strict_passed_spec_count") if isinstance(summary, Mapping) else None
    all_gates_pass = all(data.get(field) == "PASS" for field in _NEXT_CALL_PASS_FIELDS) and ledger_matches is True
    recommendation_name = recommendation.get("recommended_next_call")
    if recommendation_name == "Stage B r0":
        if not all_gates_pass or not isinstance(strict_count, int) or isinstance(strict_count, bool) or strict_count <= 0:
            messages.append(
                "next_call_recommendation may recommend Stage B r0 only when every Stage A safety gate passes and strict_passed_spec_count > 0"
            )
        if recommendation.get("recommended_prompt_id") != "Prompt 0.2":
            messages.append("Stage B r0 recommendation must use recommended_prompt_id=Prompt 0.2")
        if recommendation.get("recommended_input_universe") != "Stage A strict_passed_spec[] only":
            messages.append(
                "Stage B r0 recommendation must use recommended_input_universe=Stage A strict_passed_spec[] only"
            )
    elif all_gates_pass and isinstance(strict_count, int) and not isinstance(strict_count, bool) and strict_count > 0:
        messages.append(
            "all Stage A safety gates PASS with strict candidates, so next_call_recommendation must be Stage B r0"
        )


def _validate_partition_specific_review_fields(
    data: Mapping[str, Any], messages: list[str]
) -> None:
    candidate = data.get("candidate_review_pool")
    if isinstance(candidate, list):
        for index, item in enumerate(candidate):
            if not isinstance(item, Mapping):
                continue
            label = _candidate_label(item, f"candidate_review_pool[{index}]")
            for field in _CANDIDATE_REVIEW_TEXT_FIELDS:
                if not _nonempty_text(item.get(field)):
                    messages.append(f"{label}: candidate_review_pool requires non-empty {field}")
            disposition = item.get("final_review_pool_disposition")
            if _nonempty_text(disposition) and disposition not in _CANDIDATE_REVIEW_DISPOSITIONS:
                messages.append(f"{label}: invalid final_review_pool_disposition {disposition}")

    watchlist = data.get("watchlist_context_pool")
    if isinstance(watchlist, list):
        for index, item in enumerate(watchlist):
            if not isinstance(item, Mapping):
                continue
            label = _candidate_label(item, f"watchlist_context_pool[{index}]")
            for field in _WATCHLIST_TEXT_FIELDS:
                if not _nonempty_text(item.get(field)):
                    messages.append(f"{label}: watchlist_context_pool requires non-empty {field}")

    reject_support = data.get("reject_or_support_only_pool")
    if isinstance(reject_support, list):
        for index, item in enumerate(reject_support):
            if not isinstance(item, Mapping):
                continue
            label = _candidate_label(item, f"reject_or_support_only_pool[{index}]")
            for field in _REJECT_SUPPORT_TEXT_FIELDS:
                if not _nonempty_text(item.get(field)):
                    messages.append(f"{label}: reject_or_support_only_pool requires non-empty {field}")
            if not isinstance(item.get("whether_support_source_only"), bool):
                messages.append(
                    f"{label}: reject_or_support_only_pool whether_support_source_only must be boolean"
                )


def _validate_candidate_review_routes(data: Mapping[str, Any], messages: list[str]) -> None:
    values = data.get("candidate_review_pool")
    if not isinstance(values, list):
        return
    for index, item in enumerate(values):
        if not isinstance(item, Mapping):
            continue
        label = _candidate_label(item, f"candidate_review_pool[{index}]")
        for error in route_package_errors(item):
            messages.append(f"{label}: candidate review V3 route invalid: {error}")


def _legal_exception_proven(item: Mapping[str, Any], stage: str) -> bool:
    exception = item.get("legal_policy_score_cap_exception")
    if not isinstance(exception, Mapping) or exception.get("applied") is not True:
        return False
    basis = exception.get("basis")
    allowed = _LEGAL_EXCEPTION_BASES_BY_STAGE.get(stage, set())
    if basis not in allowed:
        return False
    evidence = exception.get("evidence")
    return isinstance(evidence, str) and len(evidence.strip()) >= 20


def _validate_legal_default_caps(data: Mapping[str, Any], messages: list[str]) -> None:
    pools = (
        "strict_passed_spec",
        "candidate_review_pool",
        "watchlist_context_pool",
        "reject_or_support_only_pool",
    )
    for pool in pools:
        values = data.get(pool)
        if not isinstance(values, list):
            continue
        for index, item in enumerate(values):
            if not isinstance(item, Mapping):
                continue
            stage = item.get("legal_policy_stage")
            cap = _base_contract.LEGAL_TOTAL_SCORE_CAPS.get(stage)
            score = item.get("decision_news_value_score")
            if cap is None or not isinstance(score, int) or isinstance(score, bool) or score <= cap:
                continue
            if _legal_exception_proven(item, stage):
                continue
            label = _candidate_label(item, f"{pool}[{index}]")
            messages.append(
                f"{label}: decision_news_value_score {score} exceeds {stage} default cap {cap} without a proven legal_policy_score_cap_exception"
            )


def validate_full_stage_a_artifact(
    data: Mapping[str, Any], compat_module: Any
) -> list[str]:
    messages = list(_previous.validate_full_stage_a_artifact(data, compat_module))
    expected = _validate_review_audit_metadata(data, messages)
    _validate_legacy_review_aggregate(data, expected, messages)
    _validate_next_call_safety(data, messages)
    _validate_partition_specific_review_fields(data, messages)
    _validate_candidate_review_routes(data, messages)
    _validate_legal_default_caps(data, messages)
    return messages
