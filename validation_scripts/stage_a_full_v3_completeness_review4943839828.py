#!/usr/bin/env python3
"""Fail-closed Stage A hardening for Codex review 4943839828.

This run-independent layer closes four remaining audit gaps:
- preflight enum/dict-key operands before legacy membership operations;
- reconcile review-resolution story identity as well as item/partition lineage;
- reconcile dropped-story treasure-hunt counts, IDs, and result coverage;
- reconcile original upstream-status counts with the declared story universe.
"""
from __future__ import annotations

from typing import Any, Mapping

from validation_scripts import stage_a_full_v3_completeness_review4943777463 as _previous

CANONICAL_POLICY_VERSION = _previous.CANONICAL_POLICY_VERSION
CANONICAL_POLICY_FILE = _previous.CANONICAL_POLICY_FILE
looks_like_full_stage_a_artifact = _previous.looks_like_full_stage_a_artifact

_CANDIDATE_POOLS = (
    "strict_passed_spec",
    "candidate_review_pool",
    "watchlist_context_pool",
    "reject_or_support_only_pool",
    "review_pool",
)
_DIRECT_ENUM_TEXT_FIELDS = (
    "stage_a_evidence_status",
    "primary_url_semantics",
    "execution_anchor_strength",
    "technology_validation_stage",
    "legal_policy_stage",
    "review_pool_subtype",
)
_EARNINGS_ENUM_TEXT_FIELDS = (
    "earnings_release_available",
    "ir_deck_available",
    "call_or_transcript_expected",
    "qna_status",
)


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _normalized_story_ids(item: Mapping[str, Any]) -> set[str]:
    result: set[str] = set()
    story_id = item.get("story_id")
    if _nonempty_text(story_id):
        result.add(story_id.strip())
    grouped = item.get("grouped_story_ids")
    if isinstance(grouped, list):
        result.update(value.strip() for value in grouped if _nonempty_text(value))
    return result


def _append_nonstring_enum(
    messages: list[str], label: str, field: str, value: Any
) -> None:
    if value is not None and not isinstance(value, str):
        messages.append(
            f"{label}: {field} must be string metadata before legacy enum validation"
        )


def prevalidate_full_stage_a_artifact(data: Any) -> list[str]:
    """Block malformed LLM-controlled membership operands before legacy code runs."""
    messages = list(_previous.prevalidate_full_stage_a_artifact(data))
    if not isinstance(data, Mapping):
        return messages

    for pool in _CANDIDATE_POOLS:
        values = data.get(pool)
        if not isinstance(values, list):
            continue
        for index, item in enumerate(values):
            if not isinstance(item, Mapping):
                continue
            label = _previous._candidate_label(item, f"{pool}[{index}]")
            for field in _DIRECT_ENUM_TEXT_FIELDS:
                if field in item:
                    _append_nonstring_enum(messages, label, field, item.get(field))
            for field in _EARNINGS_ENUM_TEXT_FIELDS:
                if field in item:
                    _append_nonstring_enum(messages, label, field, item.get(field))

            credibility = item.get("execution_credibility_gate")
            if isinstance(credibility, Mapping) and "anchor_strength" in credibility:
                _append_nonstring_enum(
                    messages,
                    label,
                    "execution_credibility_gate.anchor_strength",
                    credibility.get("anchor_strength"),
                )

            urgency = item.get("publication_urgency")
            if isinstance(urgency, Mapping) and "level" in urgency:
                _append_nonstring_enum(
                    messages,
                    label,
                    "publication_urgency.level",
                    urgency.get("level"),
                )

    rejected = data.get("rejected")
    if isinstance(rejected, list):
        for index, item in enumerate(rejected):
            if not isinstance(item, Mapping) or "hard_reject_basis" not in item:
                continue
            label = _previous._candidate_label(item, f"rejected[{index}]")
            _append_nonstring_enum(
                messages, label, "hard_reject_basis", item.get("hard_reject_basis")
            )

    summary = data.get("summary")
    if isinstance(summary, Mapping):
        if "earnings_call_qna_audit_status" in summary:
            _append_nonstring_enum(
                messages,
                "full Stage A summary",
                "earnings_call_qna_audit_status",
                summary.get("earnings_call_qna_audit_status"),
            )
    return messages


def _review_item_identity_by_id(
    data: Mapping[str, Any],
) -> dict[str, set[str]]:
    expected: dict[str, set[str]] = {}
    for pool in _previous._CANONICAL_REVIEW_POOLS:
        values = data.get(pool)
        if not isinstance(values, list):
            continue
        for item in values:
            if not isinstance(item, Mapping):
                continue
            item_id = item.get("review_pool_item_id")
            if _nonempty_text(item_id):
                expected[item_id.strip()] = _normalized_story_ids(item)
    legacy = data.get("review_pool")
    if isinstance(legacy, list):
        for item in legacy:
            if not isinstance(item, Mapping):
                continue
            item_id = item.get("review_pool_item_id")
            if _nonempty_text(item_id):
                expected.setdefault(item_id.strip(), _normalized_story_ids(item))
    return expected


def _validate_review_resolution_story_lineage(
    data: Mapping[str, Any], messages: list[str]
) -> None:
    expected = _review_item_identity_by_id(data)
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
        expected_ids = expected.get(item_id)
        if expected_ids is None:
            continue
        actual_ids = _normalized_story_ids(row)
        if actual_ids != expected_ids:
            messages.append(
                f"review_pool_resolution_ledger[{index}]: story identity must match emitted review item {item_id}; "
                f"expected={sorted(expected_ids)!r} actual={sorted(actual_ids)!r}"
            )


def _validate_unique_id_array(
    value: Any, label: str, messages: list[str]
) -> list[str] | None:
    if not isinstance(value, list):
        return None
    if any(not _nonempty_text(item) for item in value):
        messages.append(f"{label} must contain only non-blank strings")
        return None
    normalized = [item.strip() for item in value]
    if len(set(normalized)) != len(normalized):
        messages.append(f"{label} must contain unique IDs")
        return None
    return normalized


def _treasure_result_story_ids(
    result: list[Any], messages: list[str]
) -> set[str] | None:
    ids: set[str] = set()
    saw_identity = False
    for index, row in enumerate(result):
        if not isinstance(row, Mapping):
            messages.append(f"dropped_treasure_hunt_result[{index}] must be an object")
            continue
        row_ids = _normalized_story_ids(row)
        if row_ids:
            saw_identity = True
            overlap = ids.intersection(row_ids)
            if overlap:
                messages.append(
                    f"dropped_treasure_hunt_result contains duplicate story IDs {sorted(overlap)!r}"
                )
            ids.update(row_ids)
    return ids if saw_identity else None


def _validate_dropped_treasure_hunt(
    data: Mapping[str, Any], messages: list[str]
) -> None:
    treasure = data.get("dropped_treasure_hunt")
    result = data.get("dropped_treasure_hunt_result")
    if not isinstance(treasure, Mapping) or not isinstance(result, list):
        return

    sampled = _validate_unique_id_array(
        treasure.get("sampled_story_ids"),
        "full Stage A artifact dropped_treasure_hunt.sampled_story_ids",
        messages,
    )
    rescued = _validate_unique_id_array(
        treasure.get("rescue_ids"),
        "full Stage A artifact dropped_treasure_hunt.rescue_ids",
        messages,
    )
    if sampled is None or rescued is None:
        return

    sample_size = treasure.get("sample_size")
    rescued_count = treasure.get("rescued_count")
    if isinstance(sample_size, int) and not isinstance(sample_size, bool):
        if sample_size != len(sampled):
            messages.append(
                "full Stage A artifact dropped_treasure_hunt.sample_size must equal sampled_story_ids length"
            )
    if isinstance(rescued_count, int) and not isinstance(rescued_count, bool):
        if rescued_count != len(rescued):
            messages.append(
                "full Stage A artifact dropped_treasure_hunt.rescued_count must equal rescue_ids length"
            )

    sampled_set = set(sampled)
    rescued_set = set(rescued)
    if not rescued_set.issubset(sampled_set):
        messages.append(
            "full Stage A artifact dropped_treasure_hunt.rescue_ids must be a subset of sampled_story_ids"
        )

    if len(result) != len(sampled):
        messages.append(
            "full Stage A artifact dropped_treasure_hunt_result length must equal sampled_story_ids length"
        )
    result_ids = _treasure_result_story_ids(result, messages)
    if result_ids is not None and result_ids != sampled_set:
        messages.append(
            "full Stage A artifact dropped_treasure_hunt_result story identities must match sampled_story_ids"
        )

    if treasure.get("performed") is False and (
        sampled or rescued or result or sample_size not in (0, None) or rescued_count not in (0, None)
    ):
        messages.append(
            "full Stage A artifact dropped_treasure_hunt performed=false requires zero/empty sample, rescue, and result accounting"
        )


def _validate_original_status_counts(
    data: Mapping[str, Any], messages: list[str]
) -> None:
    counts = data.get("original_status_counts")
    story_count = data.get("story_count")
    if not isinstance(counts, Mapping):
        return
    total = 0
    valid = True
    for key, value in counts.items():
        if not _nonempty_text(key):
            messages.append("full Stage A artifact original_status_counts keys must be non-blank strings")
            valid = False
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            messages.append(
                f"full Stage A artifact original_status_counts[{key!r}] must be a non-negative integer"
            )
            valid = False
        else:
            total += value
    if (
        valid
        and isinstance(story_count, int)
        and not isinstance(story_count, bool)
        and total != story_count
    ):
        messages.append(
            f"full Stage A artifact original_status_counts total {total} must equal story_count {story_count}"
        )


def validate_full_stage_a_artifact(
    data: Mapping[str, Any], compat_module: Any
) -> list[str]:
    messages = list(_previous.validate_full_stage_a_artifact(data, compat_module))
    _validate_review_resolution_story_lineage(data, messages)
    _validate_dropped_treasure_hunt(data, messages)
    _validate_original_status_counts(data, messages)
    return messages
