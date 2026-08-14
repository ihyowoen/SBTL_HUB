#!/usr/bin/env python3
"""Fail CI when the public Stage A validator drifts from the V3 contract."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

from v3_contract import contract_projection, load_contract

VALIDATION_DIR = Path(__file__).resolve().parent
PUBLIC_VALIDATOR_PATH = VALIDATION_DIR / "stage_lineage_contract_check.py"


def load_public_validator(path: Path = PUBLIC_VALIDATOR_PATH) -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "sbtl_stage_lineage_contract_check", path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load public validator from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _normalized(value: Any) -> Any:
    if isinstance(value, (set, frozenset)):
        return frozenset(value)
    if isinstance(value, (list, tuple)):
        return tuple(value)
    return value


def alignment_errors(
    contract: dict[str, Any] | None = None,
    validator: ModuleType | None = None,
) -> list[str]:
    projection = contract_projection(contract or load_contract())
    public_validator = validator or load_public_validator()

    comparisons = {
        "STAGE_A_ALLOWED_EXECUTION_ANCHOR_STRENGTH": projection[
            "allowed_execution_anchor_strengths"
        ],
        "STAGE_A_NON_EXECUTION_ANCHOR_CLASSES": projection[
            "allowed_non_execution_anchor_classes"
        ],
        "STAGE_A_SHARED_STRICT_REQUIRED": projection[
            "shared_strict_required_fields"
        ],
        "STAGE_A_OVERRIDE_ONLY_REQUIRED": projection[
            "override_only_required_fields"
        ],
        "STAGE_A_V3_OVERRIDE_REQUIRED": projection[
            "v3_override_required_fields"
        ],
        "STAGE_A_V3_NARRATIVE_FIELDS": projection[
            "v3_narrative_fields"
        ],
        "STAGE_A_ALLOWED_STAGE_EVIDENCE_STATUS": projection[
            "allowed_stage_a_evidence_statuses"
        ],
        "STAGE_A_ALLOWED_PRIMARY_URL_SEMANTICS": projection[
            "allowed_primary_url_semantics"
        ],
        "STAGE_A_EVIDENCE_TARGET_KEY_PAIRS": projection[
            "structured_evidence_target_key_pairs"
        ],
        "STAGE_A_CONFIRMATION_POINT_KEY_PAIRS": projection[
            "structured_confirmation_point_key_pairs"
        ],
    }

    errors: list[str] = []
    for constant_name, expected in comparisons.items():
        if not hasattr(public_validator, constant_name):
            errors.append(f"public validator missing {constant_name}")
            continue
        actual = _normalized(getattr(public_validator, constant_name))
        normalized_expected = _normalized(expected)
        if actual != normalized_expected:
            errors.append(
                f"{constant_name} drifted: expected "
                f"{normalized_expected!r}, got {actual!r}"
            )

    if projection["route_cardinality"] != "exactly_one":
        errors.append("canonical route cardinality is no longer exactly_one")
    if set(projection["route_names"]) != {
        "execution",
        "v3_non_execution",
    }:
        errors.append(
            "canonical routes are no longer execution and v3_non_execution"
        )
    return errors


def main() -> int:
    try:
        errors = alignment_errors()
    except (OSError, ValueError, ImportError) as exc:
        errors = [str(exc)]
    if errors:
        print("RESULT: BLOCKED_CANONICAL_V3_CONTRACT_DRIFT")
        for error in errors:
            print(f"- {error}")
        return 1
    print("RESULT: PASS_CANONICAL_V3_CONTRACT_ALIGNED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
