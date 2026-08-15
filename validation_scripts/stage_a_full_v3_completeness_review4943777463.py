#!/usr/bin/env python3
"""Fail-closed Stage A surface for Codex reviews 4943777463 and 4943839828.

Adds cross-object reconciliation that is not safely expressible as simple
presence checks: usable strict source lineage, review workload accounting,
review-resolution partition/story lineage, decision-ledger disposition lineage,
treasure-hunt/original-status accounting, and safe preflight of LLM-controlled
legacy membership operands before set/dict membership.
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
_CANDIDATE_POOLS = (
    "strict_passed_spec",
    *_CANONICAL_REVIEW_POOLS,
    "review_pool",
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


def _candidate_label(item: Mapping[str, Any], fallback: str) -> str:
    for key in ("spec_id", "review_pool_item_id", "story_id"):
        value = item.get(key)
        if _nonempty_text(value):
            return value.strip()
    return fallback


def _append_nonstring_enum(
    messages: list[str], label: str, field: str, value: Any
) -> None:
    if value is not None and not isinstance(value, str):
        messages.append(
            f"{label}: {field} must be string metadata before legacy enum validation"
        )


def prevalidate_full_stage_a_artifact(data: Any) -> list[str]:
    """Run prior container preflight plus guards before legacy membership checks."""
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
            label = _candidate_label(item, f"{pool}[{index}]")
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
            label = _candidate_label(item, f"rejected[{index}]")
            _append_nonstring_enum(
                messages, label, "hard_reject_basis", item.get("hard_reject_basis")
            )

    summary = data.get("summary")
    if isinstance(summary, Mapping) and "earnings_call_qna_audit_status" in summary:
        _append_nonstring_enum(
            messages,
            "full Stage A summary",
            "earnings_call_qna_audit_status",
            summary.get("earnings_call_qna_audit_status"),
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


def _story_id_set(item: Mapping[str, Any]) -> set[str]:
    return set(_story_ids(item))


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


def _review_identity_by_item_id(data: Mapping[str, Any]) -> dict[str, set[str]]:
    expected: dict[str, set[str]] = {}
    for pool in (*_CANONICAL_REVIEW_POOLS, "review_pool"):
        values = data.get(pool)
        if not isinstance(values, list):
            continue
        for item in values:
            if not isinstance(item, Mapping):
                continue
            item_id = item.get("review_pool_item_id")
            if _nonempty_text(item_id):
                expected.setdefault(item_id.strip(), _story_id_set(item))
    return expected


def _validate_review_resolution_partition_lineage(
    data: Mapping[str, Any], messages: list[str]
) -> None:
    expected_partitions = _review_partition_by_item_id(data)
    expected_identities = _review_identity_by_item_id(data)
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
        expected_partition = expected_partitions.get(item_id)
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
        expected_story_ids = expected_identities.get(item_id, set())
        actual_story_ids = _story_id_set(row)
        if actual_story_ids != expected_story_ids:
            messages.append(
                f"review_pool_resolution_ledger[{index}]: story identity must match emitted review item {item_id}; "
                f"expected={sorted(expected_story_ids)!r} actual={sorted(actual_story_ids)!r}"
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
        row_ids = _story_id_set(row)
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
    if isinstance(sample_size, int) and not isinstance(sample_size, bool) and sample_size != len(sampled):
        messages.append(
            "full Stage A artifact dropped_treasure_hunt.sample_size must equal sampled_story_ids length"
        )
    if isinstance(rescued_count, int) and not isinstance(rescued_count, bool) and rescued_count != len(rescued):
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
    _validate_strict_source_story_ids(data, messages)
    _validate_needs_review_count(data, messages)
    _validate_review_resolution_partition_lineage(data, messages)
    _validate_decision_ledger_dispositions(data, messages)
    _validate_dropped_treasure_hunt(data, messages)
    _validate_original_status_counts(data, messages)
    return messages
