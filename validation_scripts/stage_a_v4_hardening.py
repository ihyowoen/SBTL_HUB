#!/usr/bin/env python3
"""Fail-closed hardening for conditional Stage A V4 score and Related semantics."""
from __future__ import annotations

import math
from typing import Any

TECHNOLOGY_EVIDENCE_CAPS = {
    "not_applicable": 0,
    "company_target_or_unsupported_claim": 4,
    "laboratory_unvalidated": 7,
    "pilot_precommercial": 11,
    "independent_test_or_customer_qualification": 15,
    "commercial_scale_or_long_duration_field": 20,
    "material_failure_evidence": 20,
}
POLICY_STAGE_TOTAL_CAPS = {0: 39, 1: 54, 2: 69}
NOVELTY_TOTAL_CAPS = {
    "none": None,
    "repeated_announcement_no_new_fact": 39,
    "routine_progression_no_material_uncertainty": 54,
    "company_target_without_validation_or_effect": 54,
    "unsupported_political_rhetoric": 39,
}
DUPLICATE_RELATION_TYPES = {
    "same_event_duplicate",
    "existing_card_reinforcement",
    "uncertain_needs_review",
}

REQUIRED_HARDENING_FIELDS = (
    "technology_evidence_level",
    "policy_stage",
    "novelty_cap_basis",
)


def _identifier(spec: dict[str, Any], index: int) -> str:
    return str(spec.get("spec_id") or spec.get("source_spec_id") or f"idx_{index}")


def _finite_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    value = float(value)
    return value if math.isfinite(value) else None


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _empty(value: Any) -> bool:
    return value is None or value == ""


def validate_stage_a_v4_hardening(
    spec: Any,
    index: int,
    messages: list[str],
    *,
    require_contract: bool = True,
) -> None:
    if not isinstance(spec, dict):
        if require_contract:
            messages.append(f"idx_{index}: Stage A V4 hardening requires an object")
        return

    spec_id = _identifier(spec, index)
    if require_contract:
        for field in REQUIRED_HARDENING_FIELDS:
            if field not in spec:
                messages.append(f"{spec_id}: missing Stage A V4 hardening field {field}")

    tech_level = spec.get("technology_evidence_level")
    if tech_level not in TECHNOLOGY_EVIDENCE_CAPS:
        messages.append(
            f"{spec_id}: technology_evidence_level must be one of "
            f"{sorted(TECHNOLOGY_EVIDENCE_CAPS)}"
        )
    breakdown = spec.get("decision_value_breakdown")
    technology_score = None
    systemic_score = None
    if isinstance(breakdown, dict):
        technology_score = _finite_number(breakdown.get("technology_performance_safety"))
        systemic_score = _finite_number(breakdown.get("systemic_scale"))
    if tech_level in TECHNOLOGY_EVIDENCE_CAPS and technology_score is not None:
        tech_cap = TECHNOLOGY_EVIDENCE_CAPS[tech_level]
        if technology_score > tech_cap:
            messages.append(
                f"{spec_id}: technology_performance_safety {technology_score:g} exceeds "
                f"technology_evidence_level={tech_level} cap {tech_cap}/20"
            )
        if tech_level == "not_applicable" and technology_score != 0:
            messages.append(
                f"{spec_id}: technology_evidence_level=not_applicable requires technology score 0"
            )

    denominator_gap = spec.get("denominator_gap")
    denominator = spec.get("systemic_scale_denominator")
    if _nonempty_text(denominator):
        if not _empty(denominator_gap):
            messages.append(
                f"{spec_id}: denominator_gap must be empty when systemic_scale_denominator is supplied"
            )
    else:
        if not _nonempty_text(denominator_gap):
            messages.append(
                f"{spec_id}: missing defensible systemic_scale_denominator requires non-empty denominator_gap"
            )
        if systemic_score is not None and systemic_score > 2:
            messages.append(
                f"{spec_id}: systemic_scale must be <=2 when no defensible denominator is supplied"
            )

    raw_anchors = spec.get("anchor_classes")
    anchors: set[str] = set()
    if isinstance(raw_anchors, list):
        invalid_anchor_type = False
        for anchor in raw_anchors:
            if not isinstance(anchor, str):
                invalid_anchor_type = True
                continue
            anchors.add(anchor)
        if invalid_anchor_type:
            messages.append(f"{spec_id}: anchor_classes must contain only strings")

    policy_stage = spec.get("policy_stage")
    if policy_stage is not None:
        if isinstance(policy_stage, bool) or not isinstance(policy_stage, int) or not 0 <= policy_stage <= 6:
            messages.append(f"{spec_id}: policy_stage must be null or integer 0..6")
    elif "policy_regulatory_anchor" in anchors:
        messages.append(f"{spec_id}: policy_regulatory_anchor requires policy_stage 0..6")

    total = _finite_number(spec.get("decision_news_value_score"))
    if total is not None and policy_stage in POLICY_STAGE_TOTAL_CAPS:
        cap = POLICY_STAGE_TOTAL_CAPS[policy_stage]
        if total > cap:
            messages.append(
                f"{spec_id}: decision_news_value_score {total:g} exceeds policy_stage={policy_stage} cap {cap}"
            )

    novelty_basis = spec.get("novelty_cap_basis")
    if novelty_basis not in NOVELTY_TOTAL_CAPS:
        messages.append(
            f"{spec_id}: novelty_cap_basis must be one of {sorted(NOVELTY_TOTAL_CAPS)}"
        )
    elif total is not None:
        novelty_cap = NOVELTY_TOTAL_CAPS[novelty_basis]
        if novelty_cap is not None and total > novelty_cap:
            messages.append(
                f"{spec_id}: decision_news_value_score {total:g} exceeds "
                f"novelty_cap_basis={novelty_basis} cap {novelty_cap}"
            )

    related = spec.get("related_prepass")
    if isinstance(related, dict) and related.get("duplicate_disposition") == "no_duplicate_found":
        candidates = related.get("relation_candidates")
        if isinstance(candidates, list):
            contradictory = sorted({
                candidate.get("proposed_relation_type")
                for candidate in candidates
                if isinstance(candidate, dict)
                and candidate.get("proposed_relation_type") in DUPLICATE_RELATION_TYPES
            })
            if contradictory:
                messages.append(
                    f"{spec_id}: duplicate_disposition=no_duplicate_found contradicts "
                    f"relation_candidates types {contradictory}"
                )


def validate_stage_a_v4_hardening_payload(payload: Any, *, require_contract: bool = True) -> list[str]:
    messages: list[str] = []
    if not isinstance(payload, dict):
        return ["Stage A artifact must be an object"] if require_contract else []
    specs = payload.get("strict_passed_spec")
    if not isinstance(specs, list):
        return ["strict_passed_spec must be an array"] if require_contract else []
    for index, spec in enumerate(specs):
        validate_stage_a_v4_hardening(spec, index, messages, require_contract=require_contract)
    return messages
