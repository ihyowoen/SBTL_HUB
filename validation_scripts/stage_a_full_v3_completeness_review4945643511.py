#!/usr/bin/env python3
"""Stage A hardening for Codex review 4945643511.

Closes four remaining fail-closed audit gaps without changing the supported
route-only API: unknown explicit legal/technology stages, treasure-hunt result
identity, and review-partition summary reconciliation.
"""
from __future__ import annotations

from typing import Any, Mapping

from validation_scripts import stage_a_full_v3_completeness as _base_contract
from validation_scripts import stage_a_full_v3_completeness_review4945466862 as _previous

CANONICAL_POLICY_VERSION = _previous.CANONICAL_POLICY_VERSION
CANONICAL_POLICY_FILE = _previous.CANONICAL_POLICY_FILE
looks_like_full_stage_a_artifact = _previous.looks_like_full_stage_a_artifact
prevalidate_full_stage_a_artifact = _previous.prevalidate_full_stage_a_artifact

_REVIEW_POOLS = (
    "candidate_review_pool",
    "watchlist_context_pool",
    "reject_or_support_only_pool",
)
_CANDIDATE_POOLS = (
    "strict_passed_spec",
    *_REVIEW_POOLS,
)


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _candidate_label(item: Mapping[str, Any], fallback: str) -> str:
    spec_id = item.get("spec_id")
    if _nonempty_text(spec_id):
        return spec_id.strip()
    review_id = item.get("review_pool_item_id")
    if _nonempty_text(review_id):
        return review_id.strip()
    return fallback


def _explicit_stage_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def _validate_explicit_stage_enums(
    data: Mapping[str, Any], messages: list[str]
) -> None:
    """Any populated explicit stage must be a canonical enum member."""
    for pool in _CANDIDATE_POOLS:
        values = data.get(pool)
        if not isinstance(values, list):
            continue
        for index, item in enumerate(values):
            if not isinstance(item, Mapping):
                continue
            label = _candidate_label(item, f"{pool}[{index}]")

            legal_stage = item.get("legal_policy_stage")
            if (
                _explicit_stage_present(legal_stage)
                and legal_stage not in _base_contract.LEGAL_POLICY_STAGES
            ):
                messages.append(
                    f"{label}: legal_policy_stage must be one of the canonical legal-policy stages; got {legal_stage!r}"
                )

            technology_stage = item.get("technology_validation_stage")
            if (
                _explicit_stage_present(technology_stage)
                and technology_stage not in _base_contract.TECH_STAGE_CAPS
            ):
                messages.append(
                    f"{label}: technology_validation_stage must be one of the canonical technology stages; got {technology_stage!r}"
                )


def _row_story_ids(row: Mapping[str, Any]) -> set[str]:
    ids: set[str] = set()
    story_id = row.get("story_id")
    if _nonempty_text(story_id):
        ids.add(story_id.strip())
    grouped = row.get("grouped_story_ids")
    if isinstance(grouped, list):
        ids.update(value.strip() for value in grouped if _nonempty_text(value))
    return ids


def _validate_treasure_result_row_identities(
    data: Mapping[str, Any], messages: list[str]
) -> None:
    treasure = data.get("dropped_treasure_hunt")
    result = data.get("dropped_treasure_hunt_result")
    if not isinstance(treasure, Mapping) or not isinstance(result, list):
        return

    sampled = treasure.get("sampled_story_ids")
    if not isinstance(sampled, list):
        return
    sampled_ids = {
        value.strip() for value in sampled if _nonempty_text(value)
    }

    result_ids: set[str] = set()
    complete = True
    for index, row in enumerate(result):
        if not isinstance(row, Mapping):
            # Historical validation already reports the row-shape error.
            complete = False
            continue
        row_ids = _row_story_ids(row)
        if not row_ids:
            messages.append(
                f"dropped_treasure_hunt_result[{index}] must identify its sampled story via story_id or grouped_story_ids"
            )
            complete = False
            continue
        result_ids.update(row_ids)

    if complete and result_ids != sampled_ids:
        messages.append(
            "full Stage A artifact dropped_treasure_hunt_result story identities must match sampled_story_ids"
        )


def _validate_review_partition_summary(
    data: Mapping[str, Any], messages: list[str]
) -> None:
    summary = data.get("review_pool_partition_summary")
    if not isinstance(summary, Mapping):
        return

    expected: dict[str, int] = {}
    for pool in _REVIEW_POOLS:
        values = data.get(pool)
        if not isinstance(values, list):
            return
        expected[pool] = len(values)

    any_review_work = any(expected.values())
    for pool, expected_count in expected.items():
        if pool not in summary:
            if any_review_work:
                messages.append(
                    f"review_pool_partition_summary missing canonical partition count {pool}"
                )
            continue
        actual = summary.get(pool)
        if isinstance(actual, bool) or not isinstance(actual, int) or actual < 0:
            messages.append(
                f"review_pool_partition_summary.{pool} must be a non-negative integer"
            )
        elif actual != expected_count:
            messages.append(
                f"review_pool_partition_summary.{pool} must equal emitted {pool} count {expected_count}; got {actual}"
            )


def validate_full_stage_a_artifact(
    data: Mapping[str, Any], compat_module: Any
) -> list[str]:
    messages = list(_previous.validate_full_stage_a_artifact(data, compat_module))
    _validate_explicit_stage_enums(data, messages)
    _validate_treasure_result_row_identities(data, messages)
    _validate_review_partition_summary(data, messages)
    return messages
