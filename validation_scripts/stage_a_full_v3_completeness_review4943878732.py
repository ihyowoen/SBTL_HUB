#!/usr/bin/env python3
"""Final Stage A review-accounting hardening for Codex review 4943878732.

This layer keeps the three first-class review partitions authoritative, treats
legacy ``review_pool[]`` as a mirror only, requires review audit metadata even
for an empty workload, and enforces exactly one resolution-ledger row per
logical review item.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Mapping

from validation_scripts import stage_a_full_v3_completeness_review4943777463 as _previous

CANONICAL_POLICY_VERSION = _previous.CANONICAL_POLICY_VERSION
CANONICAL_POLICY_FILE = _previous.CANONICAL_POLICY_FILE
looks_like_full_stage_a_artifact = _previous.looks_like_full_stage_a_artifact
prevalidate_full_stage_a_artifact = _previous.prevalidate_full_stage_a_artifact

_CANONICAL_REVIEW_POOLS = (
    "candidate_review_pool",
    "watchlist_context_pool",
    "reject_or_support_only_pool",
)


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


def validate_full_stage_a_artifact(
    data: Mapping[str, Any], compat_module: Any
) -> list[str]:
    messages = list(_previous.validate_full_stage_a_artifact(data, compat_module))
    expected = _validate_review_audit_metadata(data, messages)
    _validate_legacy_review_aggregate(data, expected, messages)
    return messages
