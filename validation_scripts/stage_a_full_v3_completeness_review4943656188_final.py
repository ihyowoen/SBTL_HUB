#!/usr/bin/env python3
"""Final fail-closed surface for review 4943656188.

Completes the active Prompt 0.1 top-level/base strict contract without changing
Stage A editorial decisions or introducing run-specific exceptions.
"""
from __future__ import annotations

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


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


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


def validate_full_stage_a_artifact(
    data: Mapping[str, Any],
    compat_module: Any,
) -> list[str]:
    messages = list(_previous.validate_full_stage_a_artifact(data, compat_module))
    _validate_remaining_top_level_surface(data, messages)
    _validate_strict_nested_base_surface(data, messages)
    return messages
