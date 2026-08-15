#!/usr/bin/env python3
"""Fail-closed Stage A surface for Codex review 4943777463.

Adds cross-object reconciliation that is not safely expressible as simple
presence checks: usable strict source lineage, review workload accounting,
review-resolution partition lineage, decision-ledger disposition lineage, and
safe preflight of execution-strength types before legacy membership checks.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping

from validation_scripts import stage_a_full_v3_completeness_review4943656188_final as _previous

CANONICAL_POLICY_VERSION = _previous.CANONICAL_POLICY_VERSION
CANONICAL_POLICY_FILE = _previous.CANONICAL_POLICY_FILE
looks_like_full_stage_a_artifact = _previous.looks_like_full_stage_a_artifact

_CANONICAL_REVIEW_POOLS = (
    "candidate_review_pool",
    "watchlist_context_pool",
    "reject_or_support_only_pool",
)
_CANONICAL_DISPOSITION_POOLS = (
    "strict_passed_spec",
    *_CANONICAL_REVIEW_POOLS,
    "rejected",
    "existing_reinforcement",
    "support_source_only",
)
_LEDGER_DECISION_VALUES = {
    "strict_passed_spec": {"strict_passed_spec"},
    "candidate_review_pool": {"review_pool", "candidate_review_pool"},
    "watchlist_context_pool": {"review_pool", "watchlist_context_pool"},
    "reject_or_support_only_pool": {"review_pool", "reject_or_support_only_pool"},
    "rejected": {"rejected"},
    "existing_reinforcement": {"existing_reinforcement", "reinforcement"},
    "support_source_only": {"support_source_only"},
}
_EDITORIAL_BUCKET_VALUES = {
    "strict_passed_spec": {"strict_passed_spec"},
    "candidate_review_pool": {"review_pool", "candidate_review_pool"},
    "watchlist_context_pool": {"review_pool", "watchlist_context_pool"},
    "reject_or_support_only_pool": {"review_pool", "reject_or_support_only_pool"},
    "rejected": {"rejected"},
    "existing_reinforcement": {"existing_reinforcement", "reinforcement"},
    "support_source_only": {"support_source_only"},
}


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _candidate_label(item: Mapping[str, Any], fallback: str) -> str:
    for key in ("spec_id", "review_pool_item_id", "story_id"):
        value = item.get(key)
        if _nonempty_text(value):
            return value.strip()
    return fallback


def prevalidate_full_stage_a_artifact(data: Any) -> list[str]:
    """Run prior container preflight plus type guards needed before legacy code."""
    messages = list(_previous.prevalidate_full_stage_a_artifact(data))
    if not isinstance(data, Mapping):
        return messages
    strict = data.get("strict_passed_spec")
    if not isinstance(strict, list):
        return messages
    for index, item in enumerate(strict):
        if not isinstance(item, Mapping):
            continue
        anchor_type = item.get("execution_anchor_type")
        strength = item.get("execution_anchor_strength")
        execution_shaped = not (
            anchor_type is None or anchor_type == "" or anchor_type == [] or anchor_type == {}
        ) or not (
            strength is None or strength == "" or strength == [] or strength == {}
        )
        if execution_shaped and not isinstance(strength, str):
            label = _candidate_label(item, f"strict_passed_spec[{index}]")
            messages.append(
                f"{label}: execution_anchor_strength must be a string before execution-route validation"
            )
    return messages


def _story_ids(item: Mapping[str, Any], *, strict: bool = False) -> list[str]:
    if strict:
        values = item.get("source_story_ids")
        if not isinstance(values, list):
            return []
        return [value.strip() for value in values if _nonempty_text(value)]
    result: list[str] = []
    story_id = item.get("story_id")
    if _nonempty_text(story_id):
        result.append(story_id.strip())
    grouped = item.get("grouped_story_ids")
    if isinstance(grouped, list):
        result.extend(value.strip() for value in grouped if _nonempty_text(value))
    return result


def _validate_strict_source_story_ids(data: Mapping[str, Any], messages: list[str]) -> None:
    values = data.get("strict_passed_spec")
    if not isinstance(values, list):
        return
    for index, item in enumerate(values):
        if not isinstance(item, Mapping):
            continue
        label = _candidate_label(item, f"strict_passed_spec[{index}]")
        source_ids = item.get("source_story_ids")
        if not isinstance(source_ids, list) or not source_ids:
            messages.append(f"{label}: source_story_ids must be a non-empty array of unique non-blank strings")
            continue
        if any(not _nonempty_text(value) for value in source_ids):
            messages.append(f"{label}: source_story_ids must contain only non-blank strings")
            continue
        normalized = [value.strip() for value in source_ids]
        if any(value != normalized[index] for index, value in enumerate(source_ids)):
            messages.append(f"{label}: source_story_ids must use canonical trimmed IDs")
        if len(set(normalized)) != len(normalized):
            messages.append(f"{label}: source_story_ids must contain unique IDs")


def _validate_needs_review_count(data: Mapping[str, Any], messages: list[str]) -> None:
    summary = data.get("summary")
    if not isinstance(summary, Mapping):
        return
    expected = 0
    for pool in _CANONICAL_REVIEW_POOLS:
        values = data.get(pool)
        if isinstance(values, list):
            expected += len(values)
    actual = summary.get("needs_review_count")
    if isinstance(actual, int) and not isinstance(actual, bool) and actual != expected:
        messages.append(
            f"full Stage A summary needs_review_count must equal emitted review partitions ({expected})"
        )


def _review_partition_by_item_id(data: Mapping[str, Any]) -> dict[str, str]:
    expected: dict[str, str] = {}
    for pool in _CANONICAL_REVIEW_POOLS:
        values = data.get(pool)
        if not isinstance(values, list):
            continue
        for item in values:
            if not isinstance(item, Mapping):
                continue
            item_id = item.get("review_pool_item_id")
            if _nonempty_text(item_id):
                expected[item_id.strip()] = pool
    legacy = data.get("review_pool")
    if isinstance(legacy, list):
        for item in legacy:
            if not isinstance(item, Mapping):
                continue
            item_id = item.get("review_pool_item_id")
            if _nonempty_text(item_id):
                expected.setdefault(item_id.strip(), "review_pool")
    return expected


def _validate_review_resolution_partition_lineage(
    data: Mapping[str, Any], messages: list[str]
) -> None:
    expected = _review_partition_by_item_id(data)
    ledger = data.get("review_pool_resolution_ledger")
    if not isinstance(ledger, list):
        return
    for index, row in enumerate(ledger):
        if not isinstance(row, Mapping):
            continue
        item_id = row.get("review_pool_item_id")
        if not _nonempty_text(item_id):
            continue
        item_id = item_id.strip()
        expected_partition = expected.get(item_id)
        if expected_partition is None:
            messages.append(
                f"review_pool_resolution_ledger[{index}]: review_pool_item_id {item_id} does not match an emitted review item"
            )
            continue
        actual_partition = row.get("original_review_pool_partition")
        if actual_partition != expected_partition:
            messages.append(
                f"review_pool_resolution_ledger[{index}]: original_review_pool_partition must match emitted partition {expected_partition} for {item_id}"
            )


def _emitted_dispositions(data: Mapping[str, Any]) -> dict[str, tuple[str, str | None]]:
    result: dict[str, tuple[str, str | None]] = {}
    for pool in _CANONICAL_DISPOSITION_POOLS:
        values = data.get(pool)
        if not isinstance(values, list):
            continue
        for item in values:
            if not isinstance(item, Mapping):
                continue
            strict = pool == "strict_passed_spec"
            spec_id = item.get("spec_id") if _nonempty_text(item.get("spec_id")) else None
            for story_id in _story_ids(item, strict=strict):
                result.setdefault(story_id, (pool, spec_id))
    return result


def _validate_decision_ledger_dispositions(data: Mapping[str, Any], messages: list[str]) -> None:
    expected = _emitted_dispositions(data)
    ledger = data.get("decision_ledger")
    if not isinstance(ledger, list):
        return
    rows_by_story: dict[str, list[tuple[int, Mapping[str, Any]]]] = defaultdict(list)
    for index, row in enumerate(ledger):
        if not isinstance(row, Mapping) or not _nonempty_text(row.get("story_id")):
            continue
        rows_by_story[row.get("story_id").strip()].append((index, row))
    for story_id, (pool, spec_id) in expected.items():
        rows = rows_by_story.get(story_id, [])
        if len(rows) != 1:
            continue
        index, row = rows[0]
        ledger_decision = row.get("ledger_decision")
        if ledger_decision not in _LEDGER_DECISION_VALUES[pool]:
            messages.append(
                f"decision_ledger[{index}] story {story_id}: ledger_decision={ledger_decision!r} contradicts emitted disposition {pool}"
            )
        editorial_bucket = row.get("editorial_bucket")
        if editorial_bucket not in _EDITORIAL_BUCKET_VALUES[pool]:
            messages.append(
                f"decision_ledger[{index}] story {story_id}: editorial_bucket={editorial_bucket!r} contradicts emitted disposition {pool}"
            )
        if spec_id is not None and row.get("spec_id") != spec_id:
            messages.append(
                f"decision_ledger[{index}] story {story_id}: spec_id must match emitted spec {spec_id}"
            )


def validate_full_stage_a_artifact(
    data: Mapping[str, Any], compat_module: Any
) -> list[str]:
    messages = list(_previous.validate_full_stage_a_artifact(data, compat_module))
    _validate_strict_source_story_ids(data, messages)
    _validate_needs_review_count(data, messages)
    _validate_review_resolution_partition_lineage(data, messages)
    _validate_decision_ledger_dispositions(data, messages)
    return messages
