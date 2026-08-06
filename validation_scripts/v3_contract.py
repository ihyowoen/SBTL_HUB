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
    "empty_only_fields_by_route",
)
_EXECUTION_ROUTE_REQUIRED_FIELDS = {
    "execution_anchor_type",
    "execution_anchor_strength",
    "structural_value_override_applied",
}
_EMPTY_ROUTE_VALUE_DEFINITION = {
    "oneOf": [
        {"type": "null"},
        {"type": "string", "maxLength": 0},
        {"type": "array", "maxItems": 0},
        {"type": "object", "maxProperties": 0},
    ]
}
_NONEMPTY_EXECUTION_ANCHOR_TYPE_SCHEMA = {
    "type": "string",
    "minLength": 1,
    "pattern": r"\S",
}
_CANONICAL_EVIDENCE_TARGET_KEY_PAIRS = (
    ("source_or_document_class", "exact_claim_or_metric"),
    ("source_class", "verification_target"),
)
_CANONICAL_CONFIRMATION_POINT_KEY_PAIRS = (
    ("measurable_event_or_metric", "interpretation_effect"),
    ("confirmation_event", "confirm_weaken_invalidate"),
)
_NONEMPTY_NARRATIVE_SCHEMA = {
    "type": "string",
    "minLength": 8,
}


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


def _required_fields_match(value: Any, expected: set[str]) -> bool:
    """Return true only for an exact, duplicate-free required-field array."""
    return (
        isinstance(value, list)
        and len(value) == len(expected)
        and set(value) == expected
    )


def _expected_structured_text_definition(
    key_pairs: tuple[tuple[str, str], ...],
) -> dict[str, Any]:
    """Build the exact structured/free-text schema from canonical key pairs."""
    options: list[dict[str, Any]] = []
    for first_key, second_key in key_pairs:
        options.append(
            {
                "type": "object",
                "required": [first_key, second_key],
                "properties": {
                    first_key: {"type": "string", "minLength": 2},
                    second_key: {"type": "string", "minLength": 2},
                },
                "additionalProperties": True,
            }
        )
    options.append({"type": "string", "minLength": 4})
    return {"oneOf": options}


def validate_contract_document(contract: Mapping[str, Any]) -> list[str]:
    """Return structural and consistency errors for the canonical document."""
    errors: list[str] = []
    if contract.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append("$schema must use JSON Schema draft 2020-12")
    if contract.get("contract_version") != "3.0.0":
        errors.append("contract_version must be 3.0.0")
    if contract.get("type") != "object":
        errors.append("canonical V3 contract root type must be object")

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

    projection_fields = (
        "allowed_execution_anchor_strengths",
        "allowed_non_execution_anchor_classes",
        "v3_override_required_fields",
        "v3_narrative_fields",
        "allowed_stage_a_evidence_statuses",
        "allowed_primary_url_semantics",
    )
    projected = {
        key: _as_unique_string_tuple(metadata.get(key), key, errors)
        for key in projection_fields
    }

    narrative = set(projected["v3_narrative_fields"])
    override_required = set(projected["v3_override_required_fields"])
    if narrative and not narrative.issubset(override_required):
        errors.append(
            "v3_narrative_fields must be a subset of v3_override_required_fields"
        )

    empty_only_fields = metadata.get("empty_only_fields_by_route")
    if not isinstance(empty_only_fields, dict):
        errors.append("empty_only_fields_by_route must be an object")
        empty_only_fields = {}
    execution_empty_fields = _as_unique_string_tuple(
        empty_only_fields.get("execution"),
        "empty_only_fields_by_route.execution",
        errors,
    )
    non_execution_empty_fields = _as_unique_string_tuple(
        empty_only_fields.get("v3_non_execution"),
        "empty_only_fields_by_route.v3_non_execution",
        errors,
    )
    if execution_empty_fields and set(execution_empty_fields) != override_required:
        errors.append(
            "execution empty-only fields must equal v3_override_required_fields"
        )
    if non_execution_empty_fields and set(non_execution_empty_fields) != {
        "execution_anchor_type",
        "execution_anchor_strength",
    }:
        errors.append(
            "v3_non_execution empty-only fields must be execution anchor fields"
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
        "empty_route_value",
        "execution_route",
        "evidence_target",
        "confirmation_point",
        "v3_non_execution_route",
    ):
        if definition not in definitions:
            errors.append(f"$defs missing {definition}")

    if definitions.get("empty_route_value") != _EMPTY_ROUTE_VALUE_DEFINITION:
        errors.append("empty_route_value must remain empty-only")

    expected_evidence_definition = _expected_structured_text_definition(
        evidence_pairs
    )
    if definitions.get("evidence_target") != expected_evidence_definition:
        errors.append(
            "evidence_target definition differs from canonical structured contract"
        )

    expected_confirmation_definition = _expected_structured_text_definition(
        confirmation_pairs
    )
    if definitions.get("confirmation_point") != expected_confirmation_definition:
        errors.append(
            "confirmation_point definition differs from canonical structured contract"
        )

    execution_definition = definitions.get("execution_route", {})
    non_execution_definition = definitions.get("v3_non_execution_route", {})
    if execution_definition.get("type") != "object":
        errors.append("execution_route type must be exactly object")
    if non_execution_definition.get("type") != "object":
        errors.append("v3_non_execution_route type must be exactly object")

    execution_properties = execution_definition.get("properties", {})
    non_execution_properties = non_execution_definition.get("properties", {})

    execution_required = execution_definition.get("required")
    if not _required_fields_match(
        execution_required, _EXECUTION_ROUTE_REQUIRED_FIELDS
    ):
        errors.append(
            "execution_route required fields differ from canonical contract"
        )

    if execution_properties.get(
        "execution_anchor_type"
    ) != _NONEMPTY_EXECUTION_ANCHOR_TYPE_SCHEMA:
        errors.append(
            "execution_anchor_type schema must require a non-whitespace string"
        )

    expected_execution_strength_schema = {
        "enum": list(projected["allowed_execution_anchor_strengths"])
    }
    if execution_properties.get(
        "execution_anchor_strength"
    ) != expected_execution_strength_schema:
        errors.append(
            "execution_route strength schema differs from canonical metadata"
        )

    expected_anchor_classes_schema = {
        "type": "array",
        "minItems": 1,
        "uniqueItems": True,
        "items": {
            "enum": list(projected["allowed_non_execution_anchor_classes"])
        },
    }
    if non_execution_properties.get(
        "anchor_classes"
    ) != expected_anchor_classes_schema:
        errors.append(
            "v3_non_execution_route anchor_classes schema differs from canonical metadata"
        )

    non_execution_required = non_execution_definition.get("required")
    expected_required = {"structural_value_override_applied", *override_required}
    if not _required_fields_match(non_execution_required, expected_required):
        errors.append(
            "v3_non_execution_route required fields differ from canonical metadata"
        )

    for field in projected["v3_narrative_fields"]:
        if non_execution_properties.get(field) != _NONEMPTY_NARRATIVE_SCHEMA:
            errors.append(
                f"v3_non_execution_route {field} must require a non-empty narrative"
            )

    expected_evidence_array_schema = {
        "type": "array",
        "minItems": 1,
        "items": {"$ref": "#/$defs/evidence_target"},
    }
    if non_execution_properties.get(
        "evidence_needed_for_stage_b"
    ) != expected_evidence_array_schema:
        errors.append(
            "evidence_needed_for_stage_b schema differs from canonical contract"
        )

    expected_confirmation_array_schema = {
        "type": "array",
        "minItems": 1,
        "items": {"$ref": "#/$defs/confirmation_point"},
    }
    if non_execution_properties.get(
        "next_confirmation_points"
    ) != expected_confirmation_array_schema:
        errors.append(
            "next_confirmation_points schema differs from canonical contract"
        )

    empty_ref = {"$ref": "#/$defs/empty_route_value"}
    if execution_properties.get("structural_value_override_applied") != {
        "const": False
    }:
        errors.append("execution_route override marker must be const false")
    if non_execution_properties.get("structural_value_override_applied") != {
        "const": True
    }:
        errors.append("v3_non_execution_route override marker must be const true")
    for field in execution_empty_fields:
        if execution_properties.get(field) != empty_ref:
            errors.append(
                f"execution_route {field} must reference empty_route_value"
            )
    for field in non_execution_empty_fields:
        if non_execution_properties.get(field) != empty_ref:
            errors.append(
                f"v3_non_execution_route {field} must reference empty_route_value"
            )

    if evidence_pairs != _CANONICAL_EVIDENCE_TARGET_KEY_PAIRS:
        errors.append(
            "structured_evidence_target_key_pairs must equal the canonical aliases"
        )
    if confirmation_pairs != _CANONICAL_CONFIRMATION_POINT_KEY_PAIRS:
        errors.append(
            "structured_confirmation_point_key_pairs must equal the canonical aliases"
        )

    expected_routes = [
        {"$ref": "#/$defs/execution_route"},
        {"$ref": "#/$defs/v3_non_execution_route"},
    ]
    if contract.get("oneOf") != expected_routes:
        errors.append(
            "top-level oneOf must reference execution and v3_non_execution routes"
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
        "empty_only_fields_by_route": {
            route: tuple(fields)
            for route, fields in metadata["empty_only_fields_by_route"].items()
        },
    }
