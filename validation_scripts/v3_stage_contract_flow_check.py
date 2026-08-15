#!/usr/bin/env python3
"""Exercise canonical V3 route packages across every generated workflow stage."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Mapping

try:
    from validation_scripts.v3_stage_contracts import load_generated_stage_contract
except ModuleNotFoundError:
    from v3_stage_contracts import load_generated_stage_contract

ROOT_DIR = Path(__file__).resolve().parents[1]
EXPECTED_STAGE_ORDER = (
    "stage_a",
    "stage_b",
    "stage_c",
    "stage_b_revise",
    "stage_c_revise",
    "baseline_revalidation",
    "evidence_qc",
    "content_polish",
    "final_qc",
    "merge_prep",
    "production_verification",
)
_PRESERVING_MODES = {"preserve", "byte_preserve", "verify"}
_CANONICAL_SELECTOR_VERSION = "STRUCTURAL_NEWS_VALUE_SELECTION_V3"


def _shared_sample_fields() -> dict[str, Any]:
    return {
        "anchor_classes": [
            "execution_event_anchor",
            "technology_commercialization_anchor",
        ],
        "incremental_information": (
            "The named product moved from roadmap status to current production."
        ),
        "decision_relevance": (
            "The production start changes commercialization and customer-availability judgment."
        ),
        "baseline_expectation_changed": (
            "The baseline moves from a future roadmap to current manufacturing execution."
        ),
        "evidence_needed_for_stage_b": [
            {
                "source_or_document_class": "company filing",
                "exact_claim_or_metric": "production start date and named product model",
            }
        ],
        "next_confirmation_points": [
            {
                "measurable_event_or_metric": "named customer shipment volume",
                "interpretation_effect": "strengthen or weaken the commercialization judgment",
            }
        ],
        "prior_state": "The product had been presented as a future commercial offering.",
        "new_verified_fact": "The company now reports production start for the named product.",
        "changed_judgment": "Commercial availability is more advanced than previously assumed.",
        "uncertainty_resolved": "The manufacturing stage is no longer only a roadmap claim.",
        "remaining_uncertainty": "Customer shipments and production volume remain unverified.",
    }


def execution_route_sample() -> dict[str, Any]:
    sample = {
        "structural_value_override_applied": False,
        "execution_anchor_type": "signed supply agreement",
        "execution_anchor_strength": "strong",
        "structural_value_override_reason": None,
        "why_execution_event_not_required": None,
    }
    sample.update(_shared_sample_fields())
    return sample


def non_execution_route_sample() -> dict[str, Any]:
    return {
        "structural_value_override_applied": True,
        "structural_selector_policy_version": _CANONICAL_SELECTOR_VERSION,
        "execution_anchor_type": None,
        "execution_anchor_strength": None,
        "structural_value_override_reason": (
            "The policy change materially alters sourcing constraints."
        ),
        "anchor_classes": ["policy_regulatory_anchor"],
        "incremental_information": (
            "The final rule fixes the covered-entity threshold and effective date."
        ),
        "decision_relevance": (
            "The threshold changes supplier qualification and contracting priorities."
        ),
        "baseline_expectation_changed": (
            "The prior expectation of a broader transition period is no longer valid."
        ),
        "evidence_needed_for_stage_b": [
            {
                "source_or_document_class": "official final rule",
                "exact_claim_or_metric": "effective date and covered-entity threshold",
            }
        ],
        "next_confirmation_points": [
            {
                "measurable_event_or_metric": "first covered procurement after the effective date",
                "interpretation_effect": "confirm or weaken the expected supplier-switching requirement",
            }
        ],
        "why_execution_event_not_required": (
            "The binding rule itself changes the decision baseline before execution."
        ),
        "prior_state": (
            "The market expected a longer transition window and wider exemptions."
        ),
        "new_verified_fact": (
            "The published final rule sets a shorter transition and narrower exemption."
        ),
        "changed_judgment": (
            "Near-term supplier qualification risk is higher than previously assessed."
        ),
        "uncertainty_resolved": (
            "The effective date and covered-entity threshold are now confirmed."
        ),
        "remaining_uncertainty": (
            "Agency enforcement practice and case-specific waivers remain uncertain."
        ),
    }


def _is_empty_route_value(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def _valid_structured_item(
    value: Any, key_pairs: list[list[str]], minimum_text: int = 4
) -> bool:
    if isinstance(value, str):
        return len(value.strip()) >= minimum_text
    if not isinstance(value, Mapping):
        return False

    complete_pairs = 0
    for pair in key_pairs:
        if len(pair) != 2:
            continue
        first, second = pair
        if (
            isinstance(value.get(first), str)
            and len(value[first].strip()) >= 2
            and isinstance(value.get(second), str)
            and len(value[second].strip()) >= 2
        ):
            complete_pairs += 1
    return complete_pairs == 1


def _projected_string_list(
    canonical: Mapping[str, Any],
    field: str,
    errors: list[str],
) -> list[str]:
    value = canonical.get(field)
    if (
        not isinstance(value, list)
        or any(not isinstance(item, str) or not item for item in value)
        or len(set(value)) != len(value)
    ):
        errors.append(f"generated canonical {field} projection is malformed")
        return []
    return list(value)


def _validate_shared_route_values(
    package: Mapping[str, Any],
    canonical: Mapping[str, Any],
    route: str,
    errors: list[str],
) -> None:
    shared_fields = _projected_string_list(
        canonical, "shared_strict_required_fields", errors
    )
    narrative_fields = set(
        _projected_string_list(canonical, "v3_narrative_fields", errors)
    )

    anchor_classes = package.get("anchor_classes")
    allowed_non_execution = set(canonical.get("allowed_non_execution_anchor_classes", []))
    allowed_classes = set(allowed_non_execution)
    if route == "execution":
        allowed_classes.add("execution_event_anchor")
    if (
        not isinstance(anchor_classes, list)
        or not anchor_classes
        or any(not isinstance(item, str) or item not in allowed_classes for item in anchor_classes)
        or len(set(anchor_classes)) != len(anchor_classes)
    ):
        errors.append(f"{route} route requires unique allowed anchor classes")
    elif route == "execution" and "execution_event_anchor" not in anchor_classes:
        errors.append("execution route anchor_classes must include execution_event_anchor")

    for field in shared_fields:
        if field in {"anchor_classes", "evidence_needed_for_stage_b", "next_confirmation_points"}:
            continue
        if field in narrative_fields:
            value = package.get(field)
            if not isinstance(value, str) or len(value.strip()) < 8:
                errors.append(f"{route} route requires a substantive {field}")

    evidence = package.get("evidence_needed_for_stage_b")
    evidence_pairs = canonical.get("structured_evidence_target_key_pairs", [])
    if (
        not isinstance(evidence, list)
        or not evidence
        or any(not _valid_structured_item(item, evidence_pairs) for item in evidence)
    ):
        errors.append(f"{route} route requires concrete Stage B evidence targets")

    confirmations = package.get("next_confirmation_points")
    confirmation_pairs = canonical.get("structured_confirmation_point_key_pairs", [])
    if (
        not isinstance(confirmations, list)
        or not confirmations
        or any(not _valid_structured_item(item, confirmation_pairs) for item in confirmations)
    ):
        errors.append(f"{route} route requires measurable confirmation points")


def route_package_errors(
    package: Mapping[str, Any],
    document: Mapping[str, Any] | None = None,
) -> list[str]:
    stage_document = load_generated_stage_contract() if document is None else dict(document)
    canonical = stage_document.get("canonical")
    if not isinstance(canonical, Mapping):
        return ["generated stage contract canonical projection is missing"]

    errors: list[str] = []
    marker = package.get("structural_value_override_applied")
    if marker is False:
        route = "execution"
    elif marker is True:
        route = "v3_non_execution"
    else:
        return ["structural_value_override_applied must select exactly one boolean route"]

    required_by_route = canonical.get("route_required_fields", {})
    required = required_by_route.get(route, []) if isinstance(required_by_route, Mapping) else None
    if not isinstance(required, list):
        return [f"{route} required-field projection is malformed"]
    for field in required:
        if field not in package:
            errors.append(f"{route} route missing required field {field}")

    empty_by_route = canonical.get("route_empty_only_fields", {})
    empty_only = empty_by_route.get(route, []) if isinstance(empty_by_route, Mapping) else None
    if not isinstance(empty_only, list):
        errors.append(f"{route} empty-only projection is malformed")
    else:
        for field in empty_only:
            if field in package and not _is_empty_route_value(package[field]):
                errors.append(f"{route} route requires empty field {field}")

    if route == "execution":
        anchor_type = package.get("execution_anchor_type")
        if not isinstance(anchor_type, str) or not anchor_type.strip():
            errors.append("execution route requires a non-whitespace anchor type")
        allowed_strengths = canonical.get("allowed_execution_anchor_strengths", [])
        if package.get("execution_anchor_strength") not in allowed_strengths:
            errors.append("execution route has an unsupported anchor strength")
        _validate_shared_route_values(package, canonical, route, errors)
    else:
        selector_version = canonical.get("structural_selector_policy_version")
        if not isinstance(selector_version, str) or not selector_version:
            errors.append(
                "generated canonical structural_selector_policy_version projection is missing"
            )
        elif package.get("structural_selector_policy_version") != selector_version:
            errors.append(
                f"v3_non_execution route requires structural_selector_policy_version={selector_version}"
            )
        _validate_shared_route_values(package, canonical, route, errors)
        override_only = _projected_string_list(
            canonical, "override_only_required_fields", errors
        )
        narrative_fields = set(
            _projected_string_list(canonical, "v3_narrative_fields", errors)
        )
        for field in override_only:
            value = package.get(field)
            if field in narrative_fields:
                if not isinstance(value, str) or len(value.strip()) < 8:
                    errors.append(
                        f"v3_non_execution route requires a substantive {field}"
                    )
            elif _is_empty_route_value(value):
                errors.append(f"v3_non_execution route requires non-empty {field}")
    return errors


def route_name(
    package: Mapping[str, Any],
    document: Mapping[str, Any] | None = None,
) -> str:
    errors = route_package_errors(package, document)
    if errors:
        raise ValueError("; ".join(errors))
    return "v3_non_execution" if package["structural_value_override_applied"] is True else "execution"


def _preservation_snapshot(
    package: Mapping[str, Any], canonical: Mapping[str, Any]
) -> str:
    fields = canonical.get("route_package_preserve_fields")
    if not isinstance(fields, list) or not fields:
        raise ValueError("route_package_preserve_fields must be a non-empty array")
    snapshot = [
        {"field": field, "present": field in package, "value": package.get(field)}
        for field in fields
    ]
    return json.dumps(snapshot, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def validate_stage_handoff(
    stage_name: str,
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    document: Mapping[str, Any] | None = None,
) -> None:
    stage_document = load_generated_stage_contract() if document is None else dict(document)
    stages = stage_document.get("stages")
    canonical = stage_document.get("canonical")
    if not isinstance(stages, Mapping) or stage_name not in stages:
        raise ValueError(f"unknown generated stage {stage_name}")
    if not isinstance(canonical, Mapping):
        raise ValueError("generated stage contract canonical projection is missing")

    before_route = route_name(before, stage_document)
    after_route = route_name(after, stage_document)
    if before_route != after_route:
        raise ValueError(f"{stage_name} changed route from {before_route} to {after_route}")

    mode = stages[stage_name].get("preservation_mode")
    if mode in _PRESERVING_MODES:
        before_snapshot = _preservation_snapshot(before, canonical)
        after_snapshot = _preservation_snapshot(after, canonical)
        if before_snapshot != after_snapshot:
            raise ValueError(f"{stage_name} mutated the canonical route package")


def simulate_stage_flow(
    package: Mapping[str, Any],
    document: Mapping[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    stage_document = load_generated_stage_contract() if document is None else dict(document)
    stages = stage_document.get("stages")
    if not isinstance(stages, Mapping):
        raise ValueError("generated stage contract stages projection is missing")
    if tuple(stages) != EXPECTED_STAGE_ORDER:
        raise ValueError("generated stage order differs from the operational flow")

    route_name(package, stage_document)
    current = copy.deepcopy(dict(package))
    snapshots = {"stage_a": copy.deepcopy(current)}
    for stage_name in EXPECTED_STAGE_ORDER[1:]:
        next_package = copy.deepcopy(current)
        validate_stage_handoff(stage_name, current, next_package, stage_document)
        snapshots[stage_name] = copy.deepcopy(next_package)
        current = next_package
    return snapshots


def end_to_end_flow_errors(
    document: Mapping[str, Any] | None = None,
) -> list[str]:
    stage_document = load_generated_stage_contract() if document is None else dict(document)
    errors: list[str] = []
    for label, sample in (
        ("execution", execution_route_sample()),
        ("v3_non_execution", non_execution_route_sample()),
    ):
        try:
            snapshots = simulate_stage_flow(sample, stage_document)
        except (TypeError, ValueError) as exc:
            errors.append(f"{label} route flow failed: {exc}")
            continue
        if tuple(snapshots) != EXPECTED_STAGE_ORDER:
            errors.append(f"{label} route did not traverse all operational stages")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args()
    errors = end_to_end_flow_errors()
    if errors:
        print("RESULT: BLOCKED_V3_STAGE_CONTRACT_FLOW")
        for error in errors:
            print(f"- {error}")
        return 1
    print("RESULT: PASS_V3_STAGE_CONTRACT_FLOW")
    print(f"- stages checked: {len(EXPECTED_STAGE_ORDER)}")
    print("- routes checked: execution, v3_non_execution")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
