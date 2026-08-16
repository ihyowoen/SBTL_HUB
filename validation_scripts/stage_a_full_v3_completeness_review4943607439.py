#!/usr/bin/env python3
"""Review 4943607439 hardening for full Stage A V3 artifacts.

This layer keeps the existing completeness validator intact and adds the
remaining Prompt 0.1 / 0.1S fail-closed checks identified during PR #258
review.  It is deliberately run-independent.
"""
from __future__ import annotations

import re
from typing import Any, Mapping

from validation_scripts import stage_a_full_v3_completeness as _base

CANONICAL_POLICY_VERSION = _base.CANONICAL_POLICY_VERSION
CANONICAL_POLICY_FILE = _base.CANONICAL_POLICY_FILE
looks_like_full_stage_a_artifact = _base.looks_like_full_stage_a_artifact

OUTCOME_ARRAY_FIELDS = (
    "rejected",
    "existing_reinforcement",
    "support_source_only",
)
BASE_DECISION_LEDGER_REQUIRED_FIELDS = (
    "story_id",
    "upstream_status",
    "upstream_drop_reason",
    "headline",
    "site",
    "url",
    "integrity_group_id",
    "integrity_is_best",
    "ledger_decision",
    "editorial_bucket",
    "reason",
    "spec_id",
    "merged_into_spec_id",
    "baseline_match",
    "baseline_relation",
    "duplicate_risk",
    "staleness_decision",
    "treasure_hunt_sampled",
    "notes",
)
CANDIDATE_REVIEW_SUBTYPES = {
    "general_candidate",
    "structural_signal_review",
    "earnings_deep_dive",
}
_STAGE_B_RE = re.compile(r"(?:\bstage\s*[_-]?b\b|\b0\.2\b)", re.I)


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _nonempty_value(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, Mapping)):
        return bool(value)
    return value is not None


def _validate_outcome_arrays(data: Mapping[str, Any], messages: list[str]) -> None:
    for field in OUTCOME_ARRAY_FIELDS:
        if not isinstance(data.get(field), list):
            messages.append(f"full Stage A artifact {field} must be an array")


def _validate_review_partition(
    data: Mapping[str, Any],
    messages: list[str],
) -> None:
    for pool in _base.REVIEW_POOLS:
        values = data.get(pool)
        if not isinstance(values, list):
            continue
        for index, item in enumerate(values):
            if not isinstance(item, Mapping):
                continue
            label = _base._candidate_id(item, f"{pool}[{index}]")
            if item.get("review_pool_partition") != pool:
                messages.append(
                    f"{label}: review_pool_partition must be {pool!r} for {pool}"
                )
            if not _nonempty_text(item.get("review_pool_partition_reason")):
                messages.append(
                    f"{label}: review_pool_partition_reason must be populated"
                )
            action = item.get("recommended_next_action")
            if not _nonempty_text(action):
                messages.append(f"{label}: recommended_next_action must be populated")
            elif pool in {"watchlist_context_pool", "reject_or_support_only_pool"} and _STAGE_B_RE.search(action):
                messages.append(
                    f"{label}: {pool} recommended_next_action must not recommend Stage B"
                )
            if pool == "candidate_review_pool":
                if item.get("review_pool_subtype") not in CANDIDATE_REVIEW_SUBTYPES:
                    messages.append(
                        f"{label}: candidate_review_pool review_pool_subtype must be one of "
                        "general_candidate, structural_signal_review, earnings_deep_dive"
                    )
                if not _nonempty_value(item.get("promotion_precondition")):
                    messages.append(
                        f"{label}: candidate_review_pool promotion_precondition must be populated"
                    )


def _validate_base_decision_ledger(
    data: Mapping[str, Any],
    messages: list[str],
) -> None:
    ledger = data.get("decision_ledger")
    if not isinstance(ledger, list):
        return
    for index, row in enumerate(ledger):
        if not isinstance(row, Mapping):
            continue
        label = f"decision_ledger[{index}]"
        for field in BASE_DECISION_LEDGER_REQUIRED_FIELDS:
            if field not in row:
                messages.append(f"{label}: missing required base ledger field {field}")


def _all_emitted_items(data: Mapping[str, Any]):
    for pool in _base.FULL_POOL_FIELDS:
        values = data.get(pool)
        if isinstance(values, list):
            for item in values:
                if isinstance(item, Mapping):
                    yield item


def _validate_earnings_summary(
    data: Mapping[str, Any],
    messages: list[str],
) -> None:
    has_earnings = any(
        item.get("earnings_deep_dive_required") is True
        for item in _all_emitted_items(data)
    )
    present, status = _base._summary_field(data, "earnings_call_qna_audit_status")
    if not present:
        return
    if has_earnings and status != "PASS":
        messages.append(
            "full Stage A summary earnings_call_qna_audit_status must be PASS when earnings candidates exist"
        )
    elif not has_earnings and status not in {"PASS", "NOT_APPLICABLE"}:
        messages.append(
            "full Stage A summary earnings_call_qna_audit_status must be PASS or NOT_APPLICABLE when no earnings candidates exist"
        )


def _validate_credibility_evidence(
    data: Mapping[str, Any],
    compat_module: Any,
    messages: list[str],
) -> None:
    strict = data.get("strict_passed_spec")
    if not isinstance(strict, list):
        return
    for index, item in enumerate(strict):
        if not isinstance(item, Mapping):
            continue
        label = _base._candidate_id(item, f"strict_passed_spec[{index}]")
        gate = item.get("execution_credibility_gate")
        if not isinstance(gate, Mapping):
            continue
        anchor_type = gate.get("anchor_type")
        if not _nonempty_text(anchor_type):
            messages.append(
                f"{label}: execution_credibility_gate.anchor_type must be a non-empty string"
            )
        if not _base._item_specific(compat_module, gate.get("stage_precision_note")):
            messages.append(
                f"{label}: execution_credibility_gate.stage_precision_note must be item-specific"
            )
        if item.get("structural_value_override_applied") is False:
            route_anchor = item.get("execution_anchor_type")
            if _nonempty_text(route_anchor) and _nonempty_text(anchor_type):
                if anchor_type.strip() != route_anchor.strip():
                    messages.append(
                        f"{label}: execution_credibility_gate.anchor_type must match execution_anchor_type for execution route"
                    )


def validate_full_stage_a_artifact(
    data: Mapping[str, Any],
    compat_module: Any,
) -> list[str]:
    messages = list(_base.validate_full_stage_a_artifact(data, compat_module))
    _validate_outcome_arrays(data, messages)
    _validate_review_partition(data, messages)
    _validate_base_decision_ledger(data, messages)
    _validate_earnings_summary(data, messages)
    _validate_credibility_evidence(data, compat_module, messages)
    return messages
