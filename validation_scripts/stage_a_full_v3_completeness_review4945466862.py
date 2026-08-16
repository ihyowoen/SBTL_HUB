#!/usr/bin/env python3
"""Stage A hardening for Codex reviews 4945466862, 4945615067, and 4945643511.

This layer preserves the supported public route-only ``check_stage_a`` shape
while keeping real Stage A artifacts fail-closed. It closes reverse ledger-
disposition coverage, strict source-URL usability, explicitly selected legal
and technology stage applicability, pending follow-up routing, strict spec ID
uniqueness, strict source-diversity gate gaps, unknown explicit stage values,
treasure-hunt result identity, and review-partition summary reconciliation.
"""
from __future__ import annotations

from typing import Any, Mapping

from validation_scripts import stage_a_full_v3_completeness as _base_contract
from validation_scripts import stage_a_full_v3_completeness_review4943777463 as _historical
from validation_scripts import stage_a_full_v3_completeness_review4943878732 as _previous

CANONICAL_POLICY_VERSION = _previous.CANONICAL_POLICY_VERSION
CANONICAL_POLICY_FILE = _previous.CANONICAL_POLICY_FILE
prevalidate_full_stage_a_artifact = _previous.prevalidate_full_stage_a_artifact

_STAGE_A_OUTPUT_POOL_KEYS = _previous._STAGE_A_OUTPUT_POOL_KEYS
_CANONICAL_DISPOSITION_POOLS = (
    "strict_passed_spec",
    "candidate_review_pool",
    "watchlist_context_pool",
    "reject_or_support_only_pool",
    "rejected",
    "existing_reinforcement",
    "support_source_only",
)
_REVIEW_POOLS = (
    "candidate_review_pool",
    "watchlist_context_pool",
    "reject_or_support_only_pool",
)
_CANDIDATE_POOLS = (
    "strict_passed_spec",
    *_REVIEW_POOLS,
)
_PENDING_FOLLOWUP_EXPECTED = {
    "pending_parallel_or_followup_call": "review_pool/treasure triage",
    "pending_prompt_id": "authorized review_pool/treasure promotion protocol, not Prompt 0.2",
    "pending_input_universe": "candidate_review_pool[] + eligible treasure/review-only universe",
    "pending_reason": (
        "Stage B may process strict_passed_spec[] only; review_pool/treasure remains open "
        "and must not be treated as exhausted."
    ),
}


def looks_like_full_stage_a_artifact(data: Any) -> bool:
    if _historical.looks_like_full_stage_a_artifact(data):
        return True
    if not isinstance(data, Mapping):
        return False
    pool_key_count = sum(1 for field in _STAGE_A_OUTPUT_POOL_KEYS if field in data)
    return pool_key_count >= 2


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _story_ids(item: Mapping[str, Any], *, strict: bool = False) -> set[str]:
    result: set[str] = set()
    story_id = item.get("story_id")
    if _nonempty_text(story_id):
        result.add(story_id.strip())
    grouped = item.get("grouped_story_ids")
    if isinstance(grouped, list):
        result.update(value.strip() for value in grouped if _nonempty_text(value))
    if strict:
        source_ids = item.get("source_story_ids")
        if isinstance(source_ids, list):
            result.update(value.strip() for value in source_ids if _nonempty_text(value))
    return result


def _emitted_story_ids(data: Mapping[str, Any]) -> set[str]:
    result: set[str] = set()
    for pool in _CANONICAL_DISPOSITION_POOLS:
        values = data.get(pool)
        if not isinstance(values, list):
            continue
        for item in values:
            if isinstance(item, Mapping):
                result.update(_story_ids(item, strict=pool == "strict_passed_spec"))
    return result


def _validate_reverse_ledger_disposition_coverage(
    data: Mapping[str, Any], messages: list[str]
) -> None:
    ledger = data.get("decision_ledger")
    if not isinstance(ledger, list):
        return
    emitted = _emitted_story_ids(data)
    for index, row in enumerate(ledger):
        if not isinstance(row, Mapping):
            continue
        story_id = row.get("story_id")
        if not _nonempty_text(story_id):
            continue
        normalized = story_id.strip()
        if normalized not in emitted:
            messages.append(
                f"decision_ledger[{index}] story {normalized}: no emitted canonical Stage A disposition"
            )


def _validate_strict_source_urls(data: Mapping[str, Any], messages: list[str]) -> None:
    values = data.get("strict_passed_spec")
    if not isinstance(values, list):
        return
    for index, item in enumerate(values):
        if not isinstance(item, Mapping):
            continue
        label = item.get("spec_id") if _nonempty_text(item.get("spec_id")) else f"strict_passed_spec[{index}]"
        primary_url = item.get("primary_url")
        if not _nonempty_text(primary_url):
            messages.append(f"{label}: primary_url must be a non-blank source URL candidate")
        urls = item.get("urls")
        if (
            not isinstance(urls, list)
            or not urls
            or not any(_nonempty_text(value) for value in urls)
        ):
            messages.append(f"{label}: urls must contain at least one non-blank source URL candidate")
        elif any(not _nonempty_text(value) for value in urls):
            messages.append(f"{label}: urls entries must be non-blank strings")


def _legal_policy_inferred_from_anchor_or_lens(item: Mapping[str, Any]) -> bool:
    classes = item.get("anchor_classes")
    lenses = item.get("structural_value_lenses")
    return (
        isinstance(classes, list) and "policy_regulatory_anchor" in classes
    ) or (
        isinstance(lenses, list)
        and any(
            isinstance(value, str) and ("policy" in value or "legal" in value)
            for value in lenses
        )
    )


def _technology_inferred_from_anchor_or_lens(item: Mapping[str, Any]) -> bool:
    classes = item.get("anchor_classes")
    lenses = item.get("structural_value_lenses")
    return (
        isinstance(classes, list) and "technology_commercialization_anchor" in classes
    ) or (
        isinstance(lenses, list)
        and "technology_transition_commercialization" in lenses
    )


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


def _validate_explicit_legal_stage_applicability(
    data: Mapping[str, Any], messages: list[str]
) -> None:
    for pool in _CANDIDATE_POOLS:
        values = data.get(pool)
        if not isinstance(values, list):
            continue
        for index, item in enumerate(values):
            if not isinstance(item, Mapping):
                continue
            stage = item.get("legal_policy_stage")
            if stage not in _base_contract.LEGAL_POLICY_STAGES:
                continue
            if _legal_policy_inferred_from_anchor_or_lens(item):
                continue
            label = _candidate_label(item, f"{pool}[{index}]")
            for field in _base_contract.LEGAL_POLICY_FIELDS:
                if field not in item:
                    messages.append(f"{label}: legal-policy candidate missing {field}")
                    continue
                value = item.get(field)
                if field in _base_contract.LEGAL_ARRAY_FIELDS:
                    if not isinstance(value, list):
                        messages.append(f"{label}: legal-policy {field} must be an array")
                elif value is None or (isinstance(value, str) and not value.strip()):
                    messages.append(f"{label}: legal-policy {field} must be populated")


def _validate_explicit_technology_stage_applicability(
    data: Mapping[str, Any], messages: list[str]
) -> None:
    for pool in _CANDIDATE_POOLS:
        values = data.get(pool)
        if not isinstance(values, list):
            continue
        for index, item in enumerate(values):
            if not isinstance(item, Mapping):
                continue
            stage = item.get("technology_validation_stage")
            if stage not in _base_contract.TECH_STAGE_CAPS:
                continue
            if _technology_inferred_from_anchor_or_lens(item):
                continue
            label = _candidate_label(item, f"{pool}[{index}]")
            if not isinstance(item.get("technology_score_cap_applied"), bool):
                messages.append(f"{label}: technology_score_cap_applied must be boolean")
            gap = item.get("technology_validation_gap")
            if not _nonempty_text(gap):
                messages.append(f"{label}: technology_validation_gap must be populated")
            breakdown = item.get("decision_value_breakdown")
            component = (
                breakdown.get("technology_performance_safety")
                if isinstance(breakdown, Mapping)
                else None
            )
            cap = _base_contract.TECH_STAGE_CAPS[stage]
            if isinstance(component, int) and not isinstance(component, bool) and component > cap:
                messages.append(
                    f"{label}: technology_performance_safety {component} exceeds {stage} cap {cap}/20"
                )


def _positive_count(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _validate_pending_followup_routing(
    data: Mapping[str, Any], messages: list[str]
) -> None:
    strict_values = data.get("strict_passed_spec")
    if not isinstance(strict_values, list) or len(strict_values) == 0:
        return
    candidate_values = data.get("candidate_review_pool")
    candidate_review_count = len(candidate_values) if isinstance(candidate_values, list) else 0
    summary = data.get("summary")
    triage_filtered_count = summary.get("TRIAGE_FILTERED_count") if isinstance(summary, Mapping) else None
    treasure_count = (
        summary.get("newsletter_expanded_added_treasure_count")
        if isinstance(summary, Mapping)
        else None
    )
    if not (
        candidate_review_count > 0
        or _positive_count(triage_filtered_count)
        or _positive_count(treasure_count)
    ):
        return
    recommendation = data.get("next_call_recommendation")
    if not isinstance(recommendation, Mapping):
        return
    for field, expected in _PENDING_FOLLOWUP_EXPECTED.items():
        if recommendation.get(field) != expected:
            messages.append(
                f"next_call_recommendation.{field} must be {expected!r} when strict Stage B work coexists with open review/treasure work"
            )


def _validate_strict_spec_identity_and_source_diversity(
    data: Mapping[str, Any], messages: list[str]
) -> None:
    values = data.get("strict_passed_spec")
    if not isinstance(values, list):
        return
    seen_spec_ids: set[str] = set()
    for index, item in enumerate(values):
        if not isinstance(item, Mapping):
            continue
        label = _candidate_label(item, f"strict_passed_spec[{index}]")
        spec_id = item.get("spec_id")
        if _nonempty_text(spec_id):
            normalized = spec_id.strip()
            if normalized in seen_spec_ids:
                messages.append(f"strict_passed_spec spec_id must be unique; duplicate {normalized}")
            seen_spec_ids.add(normalized)
        if item.get("source_cluster_preserved") is not True:
            messages.append(f"{label}: source_cluster_preserved must be true for strict_passed_spec")
        diversity_path = item.get("source_diversity_path")
        if not isinstance(diversity_path, Mapping):
            messages.append(f"{label}: source_diversity_path must be an object")
        elif diversity_path.get("status") not in {"viable", "uncertain"}:
            messages.append(
                f"{label}: source_diversity_path.status must be viable or uncertain for strict_passed_spec"
            )
        if item.get("support_source_candidates_accounted") is not True:
            messages.append(
                f"{label}: support_source_candidates_accounted must be true for strict_passed_spec"
            )


def _treasure_result_row_story_ids(row: Mapping[str, Any]) -> set[str]:
    result: set[str] = set()
    story_id = row.get("story_id")
    if _nonempty_text(story_id):
        result.add(story_id.strip())
    grouped = row.get("grouped_story_ids")
    if isinstance(grouped, list):
        result.update(value.strip() for value in grouped if _nonempty_text(value))
    return result


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
    sampled_ids = {value.strip() for value in sampled if _nonempty_text(value)}
    result_ids: set[str] = set()
    complete = True
    for index, row in enumerate(result):
        if not isinstance(row, Mapping):
            complete = False
            continue
        row_ids = _treasure_result_row_story_ids(row)
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
    _validate_reverse_ledger_disposition_coverage(data, messages)
    _validate_strict_source_urls(data, messages)
    _validate_explicit_stage_enums(data, messages)
    _validate_explicit_legal_stage_applicability(data, messages)
    _validate_explicit_technology_stage_applicability(data, messages)
    _validate_pending_followup_routing(data, messages)
    _validate_strict_spec_identity_and_source_diversity(data, messages)
    _validate_treasure_result_row_identities(data, messages)
    _validate_review_partition_summary(data, messages)
    return messages
