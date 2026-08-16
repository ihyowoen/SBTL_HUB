#!/usr/bin/env python3
"""Stage A hardening for Codex reviews 4945668766 and 4945805914.

Adds fail-closed validation for strict Stage B evidence packaging, source-prompt
provenance, decision-ledger V3 mirror consistency, preserved source-cluster
coverage, strict review state, original-status accounting, and explicit hard
block statuses without changing route-only compatibility semantics.
"""
from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from validation_scripts import stage_a_full_v3_completeness_review4945466862 as _previous

CANONICAL_POLICY_VERSION = _previous.CANONICAL_POLICY_VERSION
CANONICAL_POLICY_FILE = _previous.CANONICAL_POLICY_FILE
looks_like_full_stage_a_artifact = _previous.looks_like_full_stage_a_artifact
prevalidate_full_stage_a_artifact = _previous.prevalidate_full_stage_a_artifact

_SOURCE_PROMPT_VERSION = "structural_default_review_pool_partition_20260506"
_SOURCE_PROMPT_AUTHORITY = "uploaded_or_repo_source_file_prompt"
_SOURCE_PROMPT_FIELDS = (
    "source_prompt_file",
    "source_prompt_sha256",
    "source_prompt_version",
    "source_prompt_authority",
    "source_prompt_provenance_status",
)
_REPO_ROOT = Path(__file__).resolve().parents[1]

_LEDGER_STRICT_MIRROR_FIELDS = {
    "anchor_classes": "anchor_classes",
    "structural_value_lenses": "structural_value_lenses",
    "structural_value_override_applied": "structural_value_override_applied",
    "structural_value_override_reason": "structural_value_override_reason",
    "evidence_needed_for_stage_b": "evidence_needed_for_stage_b",
    "why_execution_event_not_required": "why_execution_event_not_required",
    "incremental_information": "incremental_information",
    "decision_relevance": "decision_relevance",
    "baseline_expectation_changed": "baseline_expectation_changed",
    "follow_up_relation": "baseline_follow_up_relation",
    "next_confirmation_points": "next_confirmation_points",
    "portfolio_coverage_contribution": "portfolio_coverage_contribution",
    "earnings_deep_dive_required": "earnings_deep_dive_required",
    "qna_status": "qna_status",
    "decision_news_value_score": "decision_news_value_score",
    "decision_value_breakdown": "decision_value_breakdown",
    "decision_value_classification": "decision_value_classification",
    "prior_state": "prior_state",
    "new_verified_fact": "new_verified_fact",
    "changed_judgment": "changed_judgment",
    "uncertainty_resolved": "uncertainty_resolved",
    "remaining_uncertainty": "remaining_uncertainty",
    "denominator_used": "denominator_used",
    "denominator_gap": "denominator_gap",
    "publication_urgency": "publication_urgency",
    "anti_bias_check": "anti_bias_check",
    "structural_rescue_required": "structural_rescue_required",
    "structural_rescue_question": "structural_rescue_question",
    "technology_validation_stage": "technology_validation_stage",
    "technology_score_cap_applied": "technology_score_cap_applied",
    "technology_validation_gap": "technology_validation_gap",
}


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdefABCDEF" for char in value)
    )


def _repository_prompt_path(value: Any) -> Path | None:
    """Return an in-repository prompt path when the declared file is available."""
    if not _nonempty_text(value):
        return None
    raw = Path(value.strip())
    candidate = raw.resolve() if raw.is_absolute() else (_REPO_ROOT / raw).resolve()
    try:
        candidate.relative_to(_REPO_ROOT)
    except ValueError:
        return None
    return candidate if candidate.is_file() else None


def _validate_source_prompt_provenance(
    data: Mapping[str, Any], messages: list[str]
) -> None:
    for field in _SOURCE_PROMPT_FIELDS:
        if field not in data:
            messages.append(f"full Stage A artifact missing required source-prompt provenance field {field}")
    if "source_prompt_file" in data and not _nonempty_text(data.get("source_prompt_file")):
        messages.append("full Stage A artifact source_prompt_file must be a non-empty string")
    if "source_prompt_sha256" in data and not _valid_sha256(data.get("source_prompt_sha256")):
        messages.append("full Stage A artifact source_prompt_sha256 must be a 64-character hexadecimal SHA-256")
    if "source_prompt_version" in data and data.get("source_prompt_version") != _SOURCE_PROMPT_VERSION:
        messages.append(
            f"full Stage A artifact source_prompt_version must be {_SOURCE_PROMPT_VERSION}"
        )
    if "source_prompt_authority" in data and data.get("source_prompt_authority") != _SOURCE_PROMPT_AUTHORITY:
        messages.append(
            f"full Stage A artifact source_prompt_authority must be {_SOURCE_PROMPT_AUTHORITY}"
        )
    if "source_prompt_provenance_status" in data and data.get("source_prompt_provenance_status") != "PASS":
        messages.append("full Stage A artifact source_prompt_provenance_status must be PASS")

    prompt_path = _repository_prompt_path(data.get("source_prompt_file"))
    recorded_digest = data.get("source_prompt_sha256")
    if prompt_path is not None and _valid_sha256(recorded_digest):
        try:
            actual_digest = hashlib.sha256(prompt_path.read_bytes()).hexdigest()
        except OSError as exc:
            messages.append(
                f"full Stage A artifact repository source_prompt_file could not be hashed: {exc}"
            )
        else:
            if recorded_digest.lower() != actual_digest:
                messages.append(
                    "full Stage A artifact source_prompt_sha256 must match the SHA-256 of the referenced repository source_prompt_file"
                )


def _validate_strict_stage_b_evidence_packaging(
    data: Mapping[str, Any], messages: list[str]
) -> None:
    strict = data.get("strict_passed_spec")
    if not isinstance(strict, list):
        return
    for index, item in enumerate(strict):
        if not isinstance(item, Mapping):
            continue
        label = item.get("spec_id") if _nonempty_text(item.get("spec_id")) else f"strict_passed_spec[{index}]"
        if item.get("stage_b_evidence_package_required") is not True:
            messages.append(
                f"{label}: stage_b_evidence_package_required must be true for strict_passed_spec"
            )
        if item.get("needs_review") is not False:
            messages.append(
                f"{label}: needs_review must be false for strict_passed_spec"
            )


def _strict_story_map(data: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    strict = data.get("strict_passed_spec")
    if not isinstance(strict, list):
        return result
    for item in strict:
        if not isinstance(item, Mapping):
            continue
        story_ids = item.get("source_story_ids")
        if not isinstance(story_ids, list):
            continue
        for story_id in story_ids:
            if _nonempty_text(story_id):
                result[story_id.strip()] = item
    return result


def _validate_decision_ledger_v3_mirror(
    data: Mapping[str, Any], messages: list[str]
) -> None:
    strict_by_story = _strict_story_map(data)
    ledger = data.get("decision_ledger")
    if not isinstance(ledger, list):
        return
    for index, row in enumerate(ledger):
        if not isinstance(row, Mapping):
            continue
        story_id = row.get("story_id")
        if not _nonempty_text(story_id):
            continue
        spec = strict_by_story.get(story_id.strip())
        if spec is None:
            continue
        for ledger_field, spec_field in _LEDGER_STRICT_MIRROR_FIELDS.items():
            if spec_field not in spec:
                continue
            expected = spec.get(spec_field)
            actual = row.get(ledger_field)
            if actual != expected:
                messages.append(
                    f"decision_ledger[{index}] story {story_id.strip()}: {ledger_field} must match emitted strict spec {spec_field}"
                )


def _validate_preserved_cluster_story_coverage(
    data: Mapping[str, Any], messages: list[str]
) -> None:
    strict = data.get("strict_passed_spec")
    if not isinstance(strict, list):
        return
    for index, item in enumerate(strict):
        if not isinstance(item, Mapping):
            continue
        source_ids = item.get("source_story_ids")
        cluster = item.get("same_event_source_cluster")
        if not isinstance(source_ids, list) or not isinstance(cluster, list):
            continue
        expected = {value.strip() for value in source_ids if _nonempty_text(value)}
        observed = {
            row.get("story_id").strip()
            for row in cluster
            if isinstance(row, Mapping) and _nonempty_text(row.get("story_id"))
        }
        missing = sorted(expected - observed)
        if missing:
            label = item.get("spec_id") if _nonempty_text(item.get("spec_id")) else f"strict_passed_spec[{index}]"
            messages.append(
                f"{label}: same_event_source_cluster must cover every strict source_story_id; missing {missing!r}"
            )


def _validate_original_status_counts_against_ledger(
    data: Mapping[str, Any], messages: list[str]
) -> None:
    counts = data.get("original_status_counts")
    ledger = data.get("decision_ledger")
    if not isinstance(counts, Mapping) or not isinstance(ledger, list):
        return
    if not all(
        _nonempty_text(key)
        and isinstance(value, int)
        and not isinstance(value, bool)
        and value >= 0
        for key, value in counts.items()
    ):
        return
    expected: Counter[str] = Counter()
    for row in ledger:
        if not isinstance(row, Mapping):
            continue
        status = row.get("upstream_status")
        if _nonempty_text(status):
            expected[status.strip()] += 1
    actual = {str(key).strip(): value for key, value in counts.items()}
    if actual != dict(expected):
        messages.append(
            "full Stage A artifact original_status_counts must exactly match decision_ledger upstream_status counts"
        )


def _validate_explicit_blocked_status(
    data: Mapping[str, Any], messages: list[str]
) -> None:
    status = data.get("status")
    if isinstance(status, str) and status.strip().upper().startswith("BLOCKED"):
        messages.append(
            f"full Stage A artifact explicit blocked status {status.strip()} cannot be certified or routed to Stage B"
        )


def validate_full_stage_a_artifact(
    data: Mapping[str, Any], compat_module: Any
) -> list[str]:
    messages = list(_previous.validate_full_stage_a_artifact(data, compat_module))
    _validate_source_prompt_provenance(data, messages)
    _validate_strict_stage_b_evidence_packaging(data, messages)
    _validate_decision_ledger_v3_mirror(data, messages)
    _validate_preserved_cluster_story_coverage(data, messages)
    _validate_original_status_counts_against_ledger(data, messages)
    _validate_explicit_blocked_status(data, messages)
    return messages