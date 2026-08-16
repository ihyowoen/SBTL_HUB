#!/usr/bin/env python3
"""Stage A hardening for Codex review 4945713246.

Closes four remaining fail-open/false-negative gaps without weakening the
historical validator chain: extended review-resolution audit rows, legacy_keep
ledger/disposition reconciliation, fail-closed review gate enum preflight, and
strict upstream-anchor support.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping

from validation_scripts import stage_a_full_v3_completeness_review4945668766 as _previous

CANONICAL_POLICY_VERSION = _previous.CANONICAL_POLICY_VERSION
CANONICAL_POLICY_FILE = _previous.CANONICAL_POLICY_FILE
looks_like_full_stage_a_artifact = _previous.looks_like_full_stage_a_artifact

_FIRST_CLASS_REVIEW_POOLS = (
    "candidate_review_pool",
    "watchlist_context_pool",
    "reject_or_support_only_pool",
)
_OTHER_CANONICAL_DISPOSITION_POOLS = (
    "strict_passed_spec",
    *_FIRST_CLASS_REVIEW_POOLS,
    "rejected",
    "existing_reinforcement",
    "support_source_only",
)
_REVIEW_RESOLUTION_EXTENDED_FIELDS = (
    "upstream_status",
    "final_review_pool_disposition",
    "reviewed_by_stage_or_pass",
    "review_artifact_id",
)
_REVIEW_RESOLUTION_CARRY_FORWARD_POLICIES = {
    "closed_not_cardable",
    "carry_forward_to_watchlist",
    "support_source_only",
    "candidate_for_authorized_promotion",
    "needs_user_decision",
}
_REVIEW_GATE_ENUM_FIELDS = (
    ("execution_credibility_gate", "status"),
    ("independent_cardability_gate", "status"),
    ("independent_cardability_gate", "full_schema_viability"),
)


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_hashable(value: Any) -> bool:
    try:
        hash(value)
    except TypeError:
        return False
    return True


def _candidate_label(item: Mapping[str, Any], fallback: str) -> str:
    for field in ("spec_id", "review_pool_item_id", "story_id"):
        value = item.get(field)
        if _nonempty_text(value):
            return value.strip()
    return fallback


def prevalidate_full_stage_a_artifact(data: Any) -> list[str]:
    """Guard review gate enum operands before legacy set membership is evaluated."""
    messages = list(_previous.prevalidate_full_stage_a_artifact(data))
    if not isinstance(data, Mapping):
        return messages

    for pool in (*_FIRST_CLASS_REVIEW_POOLS, "review_pool"):
        values = data.get(pool)
        if not isinstance(values, list):
            continue
        for index, item in enumerate(values):
            if not isinstance(item, Mapping):
                continue
            label = _candidate_label(item, f"{pool}[{index}]")
            for gate_name, field in _REVIEW_GATE_ENUM_FIELDS:
                gate = item.get(gate_name)
                if not isinstance(gate, Mapping) or field not in gate:
                    continue
                value = gate.get(field)
                if value is not None and not _is_hashable(value):
                    messages.append(
                        f"{label}: {gate_name}.{field} must be hashable scalar metadata before enum validation"
                    )
    return messages


def _review_items_by_id(data: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for pool in _FIRST_CLASS_REVIEW_POOLS:
        values = data.get(pool)
        if not isinstance(values, list):
            continue
        for item in values:
            if not isinstance(item, Mapping):
                continue
            item_id = item.get("review_pool_item_id")
            if _nonempty_text(item_id):
                result.setdefault(item_id.strip(), item)
    return result


def _resolution_rows_by_id(data: Mapping[str, Any]) -> dict[str, list[tuple[int, Mapping[str, Any]]]]:
    result: dict[str, list[tuple[int, Mapping[str, Any]]]] = defaultdict(list)
    ledger = data.get("review_pool_resolution_ledger")
    if not isinstance(ledger, list):
        return result
    for index, row in enumerate(ledger):
        if not isinstance(row, Mapping):
            continue
        item_id = row.get("review_pool_item_id")
        if _nonempty_text(item_id):
            result[item_id.strip()].append((index, row))
    return result


def _validate_extended_review_resolution_contract(
    data: Mapping[str, Any], messages: list[str]
) -> None:
    items = _review_items_by_id(data)
    rows = _resolution_rows_by_id(data)
    for item_id, item in items.items():
        final_disposition = item.get("final_review_pool_disposition")
        if not _nonempty_text(final_disposition):
            continue
        matching = rows.get(item_id, [])
        if len(matching) != 1:
            # The historical one-to-one validator reports the cardinality error.
            continue
        index, row = matching[0]
        label = f"review_pool_resolution_ledger[{index}]"
        for field in _REVIEW_RESOLUTION_EXTENDED_FIELDS:
            if field not in row:
                messages.append(f"{label}: missing required review-resolution field {field}")
            elif not _nonempty_text(row.get(field)):
                messages.append(f"{label}: review-resolution field {field} must be non-empty text")

        if row.get("final_review_pool_disposition") != final_disposition:
            messages.append(
                f"{label}: final_review_pool_disposition must match emitted review item {item_id}"
            )
        upstream_status = item.get("upstream_status")
        if _nonempty_text(upstream_status) and row.get("upstream_status") != upstream_status:
            messages.append(
                f"{label}: upstream_status must match emitted review item {item_id}"
            )
        carry_forward_policy = row.get("carry_forward_policy")
        if carry_forward_policy not in _REVIEW_RESOLUTION_CARRY_FORWARD_POLICIES:
            messages.append(
                f"{label}: carry_forward_policy must be one of the documented review-resolution policies"
            )


def _item_story_ids(item: Mapping[str, Any], *, strict: bool = False) -> set[str]:
    result: set[str] = set()
    if strict:
        source_ids = item.get("source_story_ids")
        if isinstance(source_ids, list):
            result.update(value.strip() for value in source_ids if _nonempty_text(value))
        return result
    story_id = item.get("story_id")
    if _nonempty_text(story_id):
        result.add(story_id.strip())
    grouped = item.get("grouped_story_ids")
    if isinstance(grouped, list):
        result.update(value.strip() for value in grouped if _nonempty_text(value))
    source_ids = item.get("source_story_ids")
    if isinstance(source_ids, list):
        result.update(value.strip() for value in source_ids if _nonempty_text(value))
    return result


def _legacy_keep_story_ids(data: Mapping[str, Any], messages: list[str]) -> set[str]:
    result: set[str] = set()
    values = data.get("legacy_keep")
    if not isinstance(values, list):
        return result
    for index, item in enumerate(values):
        if not isinstance(item, Mapping):
            continue
        ids = _item_story_ids(item)
        if not ids:
            messages.append(
                f"legacy_keep[{index}] must identify a story via story_id, grouped_story_ids, or source_story_ids"
            )
            continue
        overlap = result.intersection(ids)
        if overlap:
            messages.append(f"legacy_keep contains duplicate story IDs {sorted(overlap)!r}")
        result.update(ids)
    return result


def _filter_legacy_keep_reverse_false_positives(
    messages: list[str], legacy_story_ids: set[str]
) -> None:
    if not legacy_story_ids:
        return
    kept: list[str] = []
    for message in messages:
        if "no emitted canonical Stage A disposition" in message and any(
            f" story {story_id}:" in message for story_id in legacy_story_ids
        ):
            continue
        kept.append(message)
    messages[:] = kept


def _validate_legacy_keep_dispositions(
    data: Mapping[str, Any], messages: list[str], legacy_story_ids: set[str]
) -> None:
    if not legacy_story_ids:
        return

    other_assignments: dict[str, list[str]] = defaultdict(list)
    for pool in _OTHER_CANONICAL_DISPOSITION_POOLS:
        values = data.get(pool)
        if not isinstance(values, list):
            continue
        for index, item in enumerate(values):
            if not isinstance(item, Mapping):
                continue
            for story_id in _item_story_ids(item, strict=pool == "strict_passed_spec"):
                other_assignments[story_id].append(f"{pool}[{index}]")

    ledger_rows: dict[str, list[tuple[int, Mapping[str, Any]]]] = defaultdict(list)
    ledger = data.get("decision_ledger")
    if isinstance(ledger, list):
        for index, row in enumerate(ledger):
            if not isinstance(row, Mapping):
                continue
            story_id = row.get("story_id")
            if _nonempty_text(story_id):
                ledger_rows[story_id.strip()].append((index, row))

    for story_id in sorted(legacy_story_ids):
        if other_assignments.get(story_id):
            messages.append(
                f"story {story_id} must appear in exactly one Stage A disposition; legacy_keep overlaps "
                + ", ".join(other_assignments[story_id])
            )
        rows = ledger_rows.get(story_id, [])
        if len(rows) != 1:
            messages.append(
                f"legacy_keep story {story_id} must have exactly one decision_ledger row; found {len(rows)}"
            )
            continue
        index, row = rows[0]
        if row.get("ledger_decision") != "legacy_keep":
            messages.append(
                f"decision_ledger[{index}] story {story_id}: ledger_decision must be legacy_keep for emitted legacy_keep"
            )
        if row.get("editorial_bucket") != "legacy_keep":
            messages.append(
                f"decision_ledger[{index}] story {story_id}: editorial_bucket must be legacy_keep for emitted legacy_keep"
            )


def _validate_strict_upstream_anchor_support(
    data: Mapping[str, Any], messages: list[str]
) -> None:
    strict = data.get("strict_passed_spec")
    if not isinstance(strict, list):
        return
    for index, item in enumerate(strict):
        if not isinstance(item, Mapping):
            continue
        gate = item.get("strict_pass_gate")
        if not isinstance(gate, Mapping):
            continue
        status = gate.get("status")
        if not (isinstance(status, str) and status.strip().lower() == "pass"):
            continue
        if gate.get("anchor_supported_by_upstream_text") is not True:
            label = _candidate_label(item, f"strict_passed_spec[{index}]")
            messages.append(
                f"{label}: strict_pass_gate.anchor_supported_by_upstream_text must be true for strict_passed_spec"
            )


def validate_full_stage_a_artifact(
    data: Mapping[str, Any], compat_module: Any
) -> list[str]:
    messages = list(_previous.validate_full_stage_a_artifact(data, compat_module))
    legacy_story_ids = _legacy_keep_story_ids(data, messages)
    _filter_legacy_keep_reverse_false_positives(messages, legacy_story_ids)
    _validate_extended_review_resolution_contract(data, messages)
    _validate_legacy_keep_dispositions(data, messages, legacy_story_ids)
    _validate_strict_upstream_anchor_support(data, messages)
    return messages
