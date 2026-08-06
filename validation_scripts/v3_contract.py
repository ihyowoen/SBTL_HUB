#!/usr/bin/env python3
"""Load and validate the canonical SBTL V3 anchor-route contract.

This module intentionally uses only the Python standard library. The JSON
Schema document is the contract source of truth; this loader validates the
SBTL-specific metadata needed by the existing validators and CI drift gate.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT_PATH = ROOT_DIR / "contracts" / "v3_anchor_contract.schema.json"

_REQUIRED_METADATA_KEYS = (
    "route_cardinality",
    "route_names",
    "allowed_execution_anchor_strengths",
    "allowed_non_execution_anchor_classes",
    "v3_override_required_fields",
    "v3_narrative_fields",
    "allowed_stage_a_evidence_statuses",
    "allowed_primary_url_semantics",
    "structured_evidence_target_key_pairs",
    "structured_confirmation_point_key_pairs",
)


def load_contract(path: str | Path | None = None) -> dict[str, Any]:
    """Return the decoded canonical contract document."""
    contract_path = Path(path) if path is not None else DEFAULT_CONTRACT_PATH
    with contract_path.open(encoding="utf-8") as handle:
        document = json.load(handle)
    if not isinstance(document, dict):
        raise ValueError("canonical V3 contract must be a JSON object")
    return document


def _as_unique_string_tuple(
    value: Any, label: str, errors: list[str]
) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        errors.append(f"{label} must be a non-empty array")
        return ()
    if any(not isinstance(item, str) or not item.strip() for item in value):
        errors.append(f"{label} must contain non-empty strings")
        return ()
    normalized = tuple(item.strip() for item in value)
    if len(set(normalized)) != len(normalized):
        errors.append(f"{label} must not contain duplicates")
    return normalized


def _as_key_pairs(
    value: Any, label: str, errors: list[str]
) -> tuple[tuple[str, str], ...]:
    if not isinstance(value, list) or not value:
        errors.append(f"{label} must be a non-empty array")
        return ()
    pairs: list[tuple[str, str]] = []
    for index, pair in enumerate(value):
        if (
            not isinstance(pair, list)
            or len(pair) != 2
            or any(not isinstance(item, str) or not item.strip() for item in pair)
        ):
            errors.append(
                f"{label}[{index}] must contain exactly two non-empty strings"
            )
            continue
        pairs.append((pair[0].strip(), pair[1].strip()))
    if len(set(pairs)) != len(pairs):
        errors.append(f"{label} must not contain duplicate key pairs")
    return tuple(pairs)


def validate_contract_document(contract: Mapping[str, Any]) -> list[str]:
    """Return structural and consistency errors for the canonical document."""
    errors: list[str] = []
    if contract.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append("$schema must use JSON Schema draft 2020-12")
    if contract.get("contract_version") != "3.0.0":
        errors.append("contract_version must be 3.0.0")

    metadata = contract.get("x-sbtl-contract")
    if not isinstance(metadata, dict):
        return errors + ["x-sbtl-contract must be an object"]
    for key in _REQUIRED_METADATA_KEYS:
        if key not in metadata:
            errors.append(f"x-sbtl-contract missing {key}")

    route_names = _as_unique_string_tuple(
        metadata.get("route_names"), "route_names", errors
    )
    if metadata.get("route_cardinality") != "exactly_one":
        errors.append("route_cardinality must be exactly_one")
    if route_names and set(route_names) != {"execution", "v3_non_execution"}:
        errors.append(
            "route_names must contain execution and v3_non_execution only"
        )

    projection_fields = {
        "allowed_execution_anchor_strengths": "allowed_execution_anchor_strengths",
        "allowed_non_execution_anchor_classes": "allowed_non_execution_anchor_classes",
        "v3_override_required_fields": "v3_override_required_fields",
        "v3_narrative_fields": "v3_narrative_fields",
        "allowed_stage_a_evidence_statuses": "allowed_stage_a_evidence_statuses",
        "allowed_primary_url_semantics": "allowed_primary_url_semantics",
    }
    projected: dict[str, tuple[str, ...]] = {}
    for output_key, metadata_key in projection_fields.items():
        projected[output_key] = _as_unique_string_tuple(
            metadata.get(metadata_key), metadata_key, errors
        )

    narrative = set(projected["v3_narrative_fields"])
    override_required = set(projected["v3_override_required_fields"])
    if narrative and not narrative.issubset(override_required):
        errors.append(
            "v3_narrative_fields must be a subset of v3_override_required_fields"
        )

    evidence_pairs = _as_key_pairs(
        metadata.get("structured_evidence_target_key_pairs"),
        "structured_evidence_target_key_pairs",
        errors,
    )
    confirmation_pairs = _as_key_pairs(
        metadata.get("structured_confirmation_point_key_pairs"),
        "structured_confirmation_point_key_pairs",
        errors,
    )

    definitions = contract.get("$defs")
    if not isinstance(definitions, dict):
        errors.append("$defs must be an object")
        return errors
    for definition in (
        "execution_route",
        "evidence_target",
        "confirmation_point",
        "v3_non_execution_route",
    ):
        if definition not in definitions:
            errors.append(f"$defs missing {definition}")

    execution_strengths = (
        definitions.get("execution_route", {})
        .get("properties", {})
        .get("execution_anchor_strength", {})
        .get("enum")
    )
    if (
        isinstance(execution_strengths, list)
        and tuple(execution_strengths)
        != projected["allowed_execution_anchor_strengths"]
    ):
        errors.append(
            "execution_route strength enum differs from canonical metadata"
        )

    anchor_classes = (
        definitions.get("v3_non_execution_route", {})
        .get("properties", {})
        .get("anchor_classes", {})
        .get("items", {})
        .get("enum")
    )
    if (
        isinstance(anchor_classes, list)
        and tuple(anchor_classes)
        != projected["allowed_non_execution_anchor_classes"]
    ):
        errors.append(
            "v3_non_execution_route anchor enum differs from canonical metadata"
        )

    non_execution_required = definitions.get(
        "v3_non_execution_route", {}
    ).get("required")
    expected_required = {"structural_value_override_applied", *override_required}
    if (
        not isinstance(non_execution_required, list)
        or set(non_execution_required) != expected_required
    ):
        errors.append(
            "v3_non_execution_route required fields differ from canonical metadata"
        )

    if evidence_pairs and evidence_pairs[0] != (
        "source_or_document_class",
        "exact_claim_or_metric",
    ):
        errors.append(
            "first evidence key pair must be the canonical structured representation"
        )
    if confirmation_pairs and confirmation_pairs[0] != (
        "measurable_event_or_metric",
        "interpretation_effect",
    ):
        errors.append(
            "first confirmation key pair must be the canonical structured representation"
        )

    routes = contract.get("oneOf")
    if not isinstance(routes, list) or len(routes) != 2:
        errors.append(
            "top-level oneOf must contain exactly two route definitions"
        )
    return errors


def contract_projection(contract: Mapping[str, Any]) -> dict[str, Any]:
    """Return immutable values consumed by validators and drift checks."""
    errors = validate_contract_document(contract)
    if errors:
        raise ValueError(
            "invalid canonical V3 contract: " + "; ".join(errors)
        )
    metadata = contract["x-sbtl-contract"]
    return {
        "route_cardinality": metadata["route_cardinality"],
        "route_names": tuple(metadata["route_names"]),
        "allowed_execution_anchor_strengths": frozenset(
            metadata["allowed_execution_anchor_strengths"]
        ),
        "allowed_non_execution_anchor_classes": frozenset(
            metadata["allowed_non_execution_anchor_classes"]
        ),
        "v3_override_required_fields": tuple(
            metadata["v3_override_required_fields"]
        ),
        "v3_narrative_fields": tuple(metadata["v3_narrative_fields"]),
        "allowed_stage_a_evidence_statuses": frozenset(
            metadata["allowed_stage_a_evidence_statuses"]
        ),
        "allowed_primary_url_semantics": frozenset(
            metadata["allowed_primary_url_semantics"]
        ),
        "structured_evidence_target_key_pairs": tuple(
            tuple(pair)
            for pair in metadata["structured_evidence_target_key_pairs"]
        ),
        "structured_confirmation_point_key_pairs": tuple(
            tuple(pair)
            for pair in metadata["structured_confirmation_point_key_pairs"]
        ),
    }
