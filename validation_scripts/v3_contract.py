#!/usr/bin/env python3
"""Canonical V3 loader with route-neutral shared strict metadata.

The canonical schema distinguishes:

- shared strict decision metadata, required on execution and non-execution routes;
- override-only rationale, required only on V3 non-execution routes;
- execution-anchor identity, required only on execution routes.

The historical base validator is retained for all unchanged checks. A normalized
validation view lets it verify the legacy invariants while this module validates
the corrected route-neutral contract directly.
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
from typing import Any, Mapping

_BASE_PATH = Path(__file__).with_name("v3_contract_review4871719239_base.py")
_SPEC = importlib.util.spec_from_file_location(
    "validation_scripts.v3_contract_review4871719239_base",
    _BASE_PATH,
)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"cannot load canonical V3 contract base from {_BASE_PATH}")
_base = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_base)

for _name in dir(_base):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_base, _name)

_TRIMMED_NARRATIVE_PATTERN = r"^\s*\S[\s\S]{6,}\S\s*$"
_NONEMPTY_NARRATIVE_SCHEMA = {
    "type": "string",
    "minLength": 8,
    "pattern": _TRIMMED_NARRATIVE_PATTERN,
}
_EMPTY_REF = {"$ref": "#/$defs/empty_route_value"}
_EXECUTION_IDENTITY_FIELDS = {
    "execution_anchor_type",
    "execution_anchor_strength",
    "structural_value_override_applied",
}


def _expected_structured_text_definition(key_pairs):
    """Build exact schemas with minimum lengths applied after trimming."""
    structured_pattern = r"^\s*\S[\s\S]*\S\s*$"
    free_text_pattern = r"^\s*\S[\s\S]{2,}\S\s*$"
    options = []
    for first_key, second_key in key_pairs:
        options.append(
            {
                "type": "object",
                "required": [first_key, second_key],
                "properties": {
                    first_key: {
                        "type": "string",
                        "minLength": 2,
                        "pattern": structured_pattern,
                    },
                    second_key: {
                        "type": "string",
                        "minLength": 2,
                        "pattern": structured_pattern,
                    },
                },
                "additionalProperties": True,
            }
        )
    options.append(
        {"type": "string", "minLength": 4, "pattern": free_text_pattern}
    )
    return {"oneOf": options}


def _unique_string_list(value: Any) -> list[str] | None:
    if (
        not isinstance(value, list)
        or not value
        or any(not isinstance(item, str) or not item.strip() for item in value)
    ):
        return None
    normalized = [item.strip() for item in value]
    if len(set(normalized)) != len(normalized):
        return None
    return normalized


def _anchor_class_schema(values: list[str], require_execution: bool) -> dict[str, Any]:
    schema: dict[str, Any] = {
        "type": "array",
        "minItems": 1,
        "uniqueItems": True,
        "items": {"enum": values},
    }
    if require_execution:
        schema["contains"] = {"const": "execution_event_anchor"}
        schema["minContains"] = 1
    return schema


def _legacy_validation_view(contract: Mapping[str, Any]) -> dict[str, Any]:
    """Translate only the corrected route split into the historical checker shape."""
    view = copy.deepcopy(dict(contract))
    metadata = view.get("x-sbtl-contract")
    definitions = view.get("$defs")
    if not isinstance(metadata, dict) or not isinstance(definitions, dict):
        return view

    override_required = metadata.get("v3_override_required_fields")
    if isinstance(override_required, list):
        empty_by_route = metadata.get("empty_only_fields_by_route")
        if isinstance(empty_by_route, dict):
            empty_by_route["execution"] = list(override_required)

    execution = definitions.get("execution_route")
    if isinstance(execution, dict):
        execution["required"] = sorted(_EXECUTION_IDENTITY_FIELDS)
        properties = execution.get("properties")
        if isinstance(properties, dict) and isinstance(override_required, list):
            for field in override_required:
                properties[field] = copy.deepcopy(_EMPTY_REF)

    non_execution = definitions.get("v3_non_execution_route")
    if isinstance(non_execution, dict):
        properties = non_execution.get("properties")
        allowed = metadata.get("allowed_non_execution_anchor_classes")
        if isinstance(properties, dict) and isinstance(allowed, list):
            properties["anchor_classes"] = {
                "type": "array",
                "minItems": 1,
                "uniqueItems": True,
                "items": {"enum": list(allowed)},
            }
    return view


def _route_neutral_contract_errors(contract: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    metadata = contract.get("x-sbtl-contract")
    definitions = contract.get("$defs")
    if not isinstance(metadata, Mapping) or not isinstance(definitions, Mapping):
        return errors

    shared = _unique_string_list(metadata.get("shared_strict_required_fields"))
    override_only = _unique_string_list(metadata.get("override_only_required_fields"))
    override_required = _unique_string_list(metadata.get("v3_override_required_fields"))
    if shared is None:
        errors.append("shared_strict_required_fields must be a unique non-empty string array")
        shared = []
    if override_only is None:
        errors.append("override_only_required_fields must be a unique non-empty string array")
        override_only = []
    if override_required is None:
        return errors

    if set(shared) & set(override_only):
        errors.append("shared_strict_required_fields and override_only_required_fields must be disjoint")
    if set(shared) | set(override_only) != set(override_required):
        errors.append(
            "shared_strict_required_fields plus override_only_required_fields must equal v3_override_required_fields"
        )

    empty_by_route = metadata.get("empty_only_fields_by_route")
    if not isinstance(empty_by_route, Mapping):
        return errors
    if set(empty_by_route.get("execution", [])) != set(override_only):
        errors.append("execution empty-only fields must equal override_only_required_fields")

    execution = definitions.get("execution_route")
    non_execution = definitions.get("v3_non_execution_route")
    if not isinstance(execution, Mapping) or not isinstance(non_execution, Mapping):
        return errors

    execution_required = execution.get("required")
    expected_execution_required = _EXECUTION_IDENTITY_FIELDS | set(shared)
    if (
        not isinstance(execution_required, list)
        or len(execution_required) != len(expected_execution_required)
        or set(execution_required) != expected_execution_required
    ):
        errors.append(
            "execution_route required fields must contain execution identity plus shared strict fields exactly"
        )

    non_execution_required = non_execution.get("required")
    expected_non_execution_required = {"structural_value_override_applied", *override_required}
    if (
        not isinstance(non_execution_required, list)
        or len(non_execution_required) != len(expected_non_execution_required)
        or set(non_execution_required) != expected_non_execution_required
    ):
        errors.append(
            "v3_non_execution_route required fields differ from shared-plus-override contract"
        )

    allowed_non_execution = _unique_string_list(
        metadata.get("allowed_non_execution_anchor_classes")
    ) or []
    execution_anchor_values = ["execution_event_anchor", *allowed_non_execution]
    expected_execution_anchor_schema = _anchor_class_schema(
        execution_anchor_values, require_execution=True
    )
    expected_non_execution_anchor_schema = _anchor_class_schema(
        allowed_non_execution, require_execution=False
    )
    if definitions.get("execution_anchor_classes") != expected_execution_anchor_schema:
        errors.append("execution_anchor_classes definition is not canonical")
    if definitions.get("non_execution_anchor_classes") != expected_non_execution_anchor_schema:
        errors.append("non_execution_anchor_classes definition is not canonical")

    execution_properties = execution.get("properties")
    non_execution_properties = non_execution.get("properties")
    if not isinstance(execution_properties, Mapping) or not isinstance(non_execution_properties, Mapping):
        return errors

    if execution_properties.get("anchor_classes") != {
        "$ref": "#/$defs/execution_anchor_classes"
    }:
        errors.append("execution_route anchor_classes must reference execution_anchor_classes")
    if non_execution_properties.get("anchor_classes") != {
        "$ref": "#/$defs/non_execution_anchor_classes"
    }:
        errors.append("v3_non_execution_route anchor_classes must reference non_execution_anchor_classes")

    for field in override_only:
        if execution_properties.get(field) != _EMPTY_REF:
            errors.append(f"execution_route {field} must remain override-only and empty")

    for field in shared:
        if field == "anchor_classes":
            continue
        if execution_properties.get(field) != non_execution_properties.get(field):
            errors.append(
                f"shared strict field {field} must use the same schema on both routes"
            )
    return errors


def validate_contract_document(contract: Mapping[str, Any]) -> list[str]:
    errors = list(_base.validate_contract_document(_legacy_validation_view(contract)))
    errors.extend(_route_neutral_contract_errors(contract))
    return errors


def contract_projection(contract: Mapping[str, Any]) -> dict[str, Any]:
    errors = validate_contract_document(contract)
    if errors:
        raise ValueError("invalid canonical V3 contract: " + "; ".join(errors))
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
        "shared_strict_required_fields": tuple(
            metadata["shared_strict_required_fields"]
        ),
        "override_only_required_fields": tuple(
            metadata["override_only_required_fields"]
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


# The historical checker resolves these expectations through module globals.
_base._NONEMPTY_NARRATIVE_SCHEMA = _NONEMPTY_NARRATIVE_SCHEMA
_base._expected_structured_text_definition = _expected_structured_text_definition
globals()["_NONEMPTY_NARRATIVE_SCHEMA"] = _NONEMPTY_NARRATIVE_SCHEMA
globals()["_expected_structured_text_definition"] = _expected_structured_text_definition

load_contract = _base.load_contract
