#!/usr/bin/env python3
"""Generate stage-level V3 route contracts from the canonical JSON Schema."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from validation_scripts.v3_contract import (  # noqa: E402
    contract_projection,
    load_contract,
)

DEFAULT_OUTPUT_PATH = ROOT_DIR / "contracts" / "generated" / "v3_stage_contracts.json"
GENERATOR_VERSION = "1.0.0"

_STAGE_PROFILES = (
    (
        "stage_a",
        "A",
        "docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md",
        "select_and_emit_exactly_one",
        "emit",
    ),
    (
        "stage_b",
        "B",
        "docs/llm_prompts/v1/02_PROMPT_0_2_Stage_B_r0.md",
        "preserve_selected_route_and_enrich_evidence",
        "preserve",
    ),
    (
        "stage_c",
        "C",
        "docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md",
        "validate_lock_and_preserve_selected_route",
        "preserve",
    ),
    (
        "stage_b_revise",
        "B_REVISE",
        "docs/llm_prompts/v1/04_PROMPT_0_2R_Stage_B_Revise.md",
        "repair_without_route_reselection",
        "preserve",
    ),
    (
        "stage_c_revise",
        "C_REVISE",
        "docs/llm_prompts/v1/05_PROMPT_0_3R_Stage_C_Revise.md",
        "repair_and_relock_without_route_reselection",
        "preserve",
    ),
    (
        "baseline_revalidation",
        "0.4",
        "docs/llm_prompts/v1/06_PROMPT_0_4_Baseline_Revalidation.md",
        "revalidate_and_preserve_selected_route",
        "preserve",
    ),
    (
        "evidence_qc",
        "0.5",
        "docs/llm_prompts/v1/07_PROMPT_0_5_Evidence_QC.md",
        "validate_evidence_and_preserve_selected_route",
        "preserve",
    ),
    (
        "content_polish",
        "0.6",
        "docs/llm_prompts/v1/08_PROMPT_0_6_Content_Polish.md",
        "byte_preserve_route_package",
        "byte_preserve",
    ),
    (
        "final_qc",
        "0.7",
        "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md",
        "validate_publish_ready_and_preserve_selected_route",
        "preserve",
    ),
    (
        "merge_prep",
        "0.8",
        "docs/llm_prompts/v1/10_PROMPT_0_8_GitHub_Merge_Prep.md",
        "resolve_ids_and_preserve_selected_route",
        "preserve",
    ),
    (
        "production_verification",
        "0.9",
        "docs/llm_prompts/v1/11_PROMPT_0_9_Production_Verification.md",
        "verify_deployed_route_package",
        "verify",
    ),
)


def _copy_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _unique_in_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def build_stage_contract_document(
    contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the deterministic stage projection derived from the canonical schema."""
    source = dict(load_contract() if contract is None else contract)
    projection = contract_projection(source)
    metadata = source["x-sbtl-contract"]
    definitions = source["$defs"]

    route_required_fields = {
        "execution": _copy_list(definitions["execution_route"]["required"]),
        "v3_non_execution": _copy_list(
            definitions["v3_non_execution_route"]["required"]
        ),
    }
    route_identity_fields = [
        "structural_value_override_applied",
        "structural_selector_policy_version",
        "execution_anchor_type",
        "execution_anchor_strength",
    ]
    preserve_fields = _unique_in_order(
        route_identity_fields + _copy_list(metadata["v3_override_required_fields"])
    )

    canonical = {
        "source_schema": "contracts/v3_anchor_contract.schema.json",
        "schema_id": source.get("$id"),
        "contract_version": source["contract_version"],
        "route_cardinality": projection["route_cardinality"],
        "route_names": _copy_list(metadata["route_names"]),
        "route_required_fields": route_required_fields,
        "route_empty_only_fields": {
            route: _copy_list(fields)
            for route, fields in metadata["empty_only_fields_by_route"].items()
        },
        "route_package_preserve_fields": preserve_fields,
        "allowed_execution_anchor_strengths": _copy_list(
            metadata["allowed_execution_anchor_strengths"]
        ),
        "allowed_non_execution_anchor_classes": _copy_list(
            metadata["allowed_non_execution_anchor_classes"]
        ),
        "v3_override_required_fields": _copy_list(
            metadata["v3_override_required_fields"]
        ),
        "v3_narrative_fields": _copy_list(metadata["v3_narrative_fields"]),
        "allowed_stage_a_evidence_statuses": _copy_list(
            metadata["allowed_stage_a_evidence_statuses"]
        ),
        "allowed_primary_url_semantics": _copy_list(
            metadata["allowed_primary_url_semantics"]
        ),
        "structured_evidence_target_key_pairs": [
            _copy_list(pair)
            for pair in metadata["structured_evidence_target_key_pairs"]
        ],
        "structured_confirmation_point_key_pairs": [
            _copy_list(pair)
            for pair in metadata["structured_confirmation_point_key_pairs"]
        ],
    }

    stages: dict[str, Any] = {}
    for key, stage_id, prompt_path, transition, preservation_mode in _STAGE_PROFILES:
        stages[key] = {
            "stage_id": stage_id,
            "prompt_path": prompt_path,
            "route_transition": transition,
            "canonical_contract_ref": "#/canonical",
            "preservation_mode": preservation_mode,
        }

    return {
        "generator_version": GENERATOR_VERSION,
        "generated_from": "contracts/v3_anchor_contract.schema.json",
        "canonical": canonical,
        "stages": stages,
    }


def render_stage_contract_document(
    contract: Mapping[str, Any] | None = None,
) -> str:
    return json.dumps(
        build_stage_contract_document(contract),
        ensure_ascii=False,
        separators=(",", ":"),
    ) + "\n"


def load_generated_stage_contract(
    path: str | Path = DEFAULT_OUTPUT_PATH,
) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        document = json.load(handle)
    if not isinstance(document, dict):
        raise ValueError("generated V3 stage contract must be a JSON object")
    return document


def generated_stage_contract_errors(
    document: Mapping[str, Any] | None = None,
    contract: Mapping[str, Any] | None = None,
) -> list[str]:
    actual = dict(
        load_generated_stage_contract() if document is None else document
    )
    expected = build_stage_contract_document(contract)
    if actual == expected:
        return []
    return [
        "contracts/generated/v3_stage_contracts.json differs from the canonical V3 schema projection"
    ]


def stage_a_validator_constants(
    document: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    stage_document = dict(
        load_generated_stage_contract() if document is None else document
    )
    errors = generated_stage_contract_errors(stage_document)
    if errors:
        raise ValueError("; ".join(errors))
    canonical = stage_document["canonical"]
    return {
        "STAGE_A_ALLOWED_EXECUTION_ANCHOR_STRENGTH": set(
            canonical["allowed_execution_anchor_strengths"]
        ),
        "STAGE_A_NON_EXECUTION_ANCHOR_CLASSES": set(
            canonical["allowed_non_execution_anchor_classes"]
        ),
        "STAGE_A_V3_OVERRIDE_REQUIRED": list(
            canonical["v3_override_required_fields"]
        ),
        "STAGE_A_V3_NARRATIVE_FIELDS": tuple(
            canonical["v3_narrative_fields"]
        ),
        "STAGE_A_ALLOWED_STAGE_EVIDENCE_STATUS": set(
            canonical["allowed_stage_a_evidence_statuses"]
        ),
        "STAGE_A_ALLOWED_PRIMARY_URL_SEMANTICS": set(
            canonical["allowed_primary_url_semantics"]
        ),
        "STAGE_A_EVIDENCE_TARGET_KEY_PAIRS": tuple(
            tuple(pair)
            for pair in canonical["structured_evidence_target_key_pairs"]
        ),
        "STAGE_A_CONFIRMATION_POINT_KEY_PAIRS": tuple(
            tuple(pair)
            for pair in canonical["structured_confirmation_point_key_pairs"]
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    output_path = Path(args.output)
    expected = render_stage_contract_document()
    actual = output_path.read_text(encoding="utf-8") if output_path.exists() else None

    if args.check:
        if actual != expected:
            print("RESULT: BLOCKED_GENERATED_V3_STAGE_CONTRACT_DRIFT")
            print(f"- regenerate with: python {Path(__file__).as_posix()} --write")
            return 1
        print("RESULT: PASS_GENERATED_V3_STAGE_CONTRACT_ALIGNED")
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if actual == expected:
        print("RESULT: UNCHANGED_GENERATED_V3_STAGE_CONTRACT")
        return 0
    output_path.write_text(expected, encoding="utf-8")
    print("RESULT: UPDATED_GENERATED_V3_STAGE_CONTRACT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
