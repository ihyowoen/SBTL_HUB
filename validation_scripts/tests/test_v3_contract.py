from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

VALIDATION_DIR = Path(__file__).resolve().parents[1]
if str(VALIDATION_DIR) not in sys.path:
    sys.path.insert(0, str(VALIDATION_DIR))

from v3_contract import (
    contract_projection,
    load_contract,
    validate_contract_document,
)
from v3_contract_drift_check import alignment_errors


class CanonicalV3ContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = load_contract()
        self.projection = contract_projection(self.contract)

    def test_canonical_contract_is_self_consistent(self):
        self.assertEqual([], validate_contract_document(self.contract))

    def test_exactly_one_route_and_expected_route_names(self):
        self.assertEqual(
            "exactly_one", self.projection["route_cardinality"]
        )
        self.assertEqual(
            {"execution", "v3_non_execution"},
            set(self.projection["route_names"]),
        )

    def test_route_residual_fields_are_empty_only(self):
        empty_only = self.projection["empty_only_fields_by_route"]
        self.assertEqual(
            set(self.projection["v3_override_required_fields"]),
            set(empty_only["execution"]),
        )
        self.assertEqual(
            {"execution_anchor_type", "execution_anchor_strength"},
            set(empty_only["v3_non_execution"]),
        )
        empty_ref = {"$ref": "#/$defs/empty_route_value"}
        definitions = self.contract["$defs"]
        for field in empty_only["execution"]:
            self.assertEqual(
                empty_ref,
                definitions["execution_route"]["properties"][field],
            )
        for field in empty_only["v3_non_execution"]:
            self.assertEqual(
                empty_ref,
                definitions["v3_non_execution_route"]["properties"][field],
            )

    def test_route_definitions_remain_object_only(self):
        route_names = ("execution_route", "v3_non_execution_route")
        for route_name in route_names:
            for loosened_type in ("array", ["object", "array"]):
                with self.subTest(
                    route=route_name, loosened_type=loosened_type
                ):
                    broken = copy.deepcopy(self.contract)
                    broken["$defs"][route_name]["type"] = loosened_type
                    errors = validate_contract_document(broken)
                    expected = (
                        "execution_route type must be exactly object"
                        if route_name == "execution_route"
                        else "v3_non_execution_route type must be exactly object"
                    )
                    self.assertIn(expected, errors)

    def test_execution_route_required_fields_cannot_drift(self):
        required_fields = (
            "execution_anchor_type",
            "execution_anchor_strength",
            "structural_value_override_applied",
        )
        for field in required_fields:
            with self.subTest(field=field):
                broken = copy.deepcopy(self.contract)
                broken["$defs"]["execution_route"]["required"].remove(field)
                errors = validate_contract_document(broken)
                self.assertTrue(
                    any(
                        "execution_route required fields differ" in error
                        for error in errors
                    ),
                    errors,
                )

        duplicate = copy.deepcopy(self.contract)
        duplicate["$defs"]["execution_route"]["required"].append(
            "execution_anchor_type"
        )
        errors = validate_contract_document(duplicate)
        self.assertTrue(
            any(
                "execution_route required fields differ" in error
                for error in errors
            ),
            errors,
        )

    def test_empty_route_value_cannot_be_loosened(self):
        broken_definitions = (
            {},
            {"type": ["null", "string", "array", "object"]},
            {
                "oneOf": [
                    {"type": "null"},
                    {"type": "string"},
                    {"type": "array", "maxItems": 0},
                    {"type": "object", "maxProperties": 0},
                ]
            },
        )
        for definition in broken_definitions:
            with self.subTest(definition=definition):
                broken = copy.deepcopy(self.contract)
                broken["$defs"]["empty_route_value"] = definition
                errors = validate_contract_document(broken)
                self.assertIn(
                    "empty_route_value must remain empty-only", errors
                )

    def test_positive_route_property_schemas_cannot_be_loosened(self):
        cases = (
            (
                "execution_route",
                "execution_anchor_type",
                {},
                "execution_anchor_type schema must require a non-whitespace string",
            ),
            (
                "execution_route",
                "execution_anchor_strength",
                {"type": "string"},
                "execution_route strength schema differs from canonical metadata",
            ),
            (
                "v3_non_execution_route",
                "remaining_uncertainty",
                {},
                "remaining_uncertainty must require a non-empty narrative",
            ),
            (
                "v3_non_execution_route",
                "anchor_classes",
                {"type": "array"},
                "anchor_classes schema differs from canonical metadata",
            ),
            (
                "v3_non_execution_route",
                "evidence_needed_for_stage_b",
                {"type": "array", "minItems": 1},
                "evidence_needed_for_stage_b schema differs from canonical contract",
            ),
            (
                "v3_non_execution_route",
                "next_confirmation_points",
                {"type": "array", "minItems": 1},
                "next_confirmation_points schema differs from canonical contract",
            ),
        )
        for route_name, field, schema, expected_fragment in cases:
            with self.subTest(route=route_name, field=field):
                broken = copy.deepcopy(self.contract)
                broken["$defs"][route_name]["properties"][field] = schema
                errors = validate_contract_document(broken)
                self.assertTrue(
                    any(expected_fragment in error for error in errors),
                    errors,
                )

    def test_structured_target_definitions_cannot_be_loosened(self):
        cases = (
            (
                "evidence_target",
                "evidence_target definition differs from canonical structured contract",
            ),
            (
                "confirmation_point",
                "confirmation_point definition differs from canonical structured contract",
            ),
        )
        for definition_name, expected_error in cases:
            with self.subTest(definition=definition_name):
                broken = copy.deepcopy(self.contract)
                broken["$defs"][definition_name] = {}
                errors = validate_contract_document(broken)
                self.assertIn(expected_error, errors)

                weakened = copy.deepcopy(self.contract)
                weakened_definition = weakened["$defs"][definition_name]
                first_option = weakened_definition["oneOf"][0]
                first_key = first_option["required"][0]
                del first_option["properties"][first_key]["minLength"]
                errors = validate_contract_document(weakened)
                self.assertIn(expected_error, errors)

    def test_route_reference_drift_is_rejected(self):
        broken = copy.deepcopy(self.contract)
        broken["oneOf"].reverse()
        errors = validate_contract_document(broken)
        self.assertTrue(
            any("must reference execution" in error for error in errors),
            errors,
        )

    def test_duplicate_enum_is_rejected(self):
        broken = copy.deepcopy(self.contract)
        strengths = broken["x-sbtl-contract"][
            "allowed_execution_anchor_strengths"
        ]
        strengths.append(strengths[0])
        errors = validate_contract_document(broken)
        self.assertTrue(
            any("duplicates" in error for error in errors), errors
        )

    def test_missing_override_field_is_rejected(self):
        broken = copy.deepcopy(self.contract)
        broken["$defs"]["v3_non_execution_route"]["required"].remove(
            "remaining_uncertainty"
        )
        errors = validate_contract_document(broken)
        self.assertTrue(
            any("required fields differ" in error for error in errors),
            errors,
        )

    def test_aligned_projection_has_no_drift(self):
        validator = SimpleNamespace(
            STAGE_A_ALLOWED_EXECUTION_ANCHOR_STRENGTH=set(
                self.projection["allowed_execution_anchor_strengths"]
            ),
            STAGE_A_NON_EXECUTION_ANCHOR_CLASSES=set(
                self.projection["allowed_non_execution_anchor_classes"]
            ),
            STAGE_A_V3_OVERRIDE_REQUIRED=list(
                self.projection["v3_override_required_fields"]
            ),
            STAGE_A_V3_NARRATIVE_FIELDS=tuple(
                self.projection["v3_narrative_fields"]
            ),
            STAGE_A_ALLOWED_STAGE_EVIDENCE_STATUS=set(
                self.projection["allowed_stage_a_evidence_statuses"]
            ),
            STAGE_A_ALLOWED_PRIMARY_URL_SEMANTICS=set(
                self.projection["allowed_primary_url_semantics"]
            ),
            STAGE_A_EVIDENCE_TARGET_KEY_PAIRS=tuple(
                self.projection["structured_evidence_target_key_pairs"]
            ),
            STAGE_A_CONFIRMATION_POINT_KEY_PAIRS=tuple(
                self.projection["structured_confirmation_point_key_pairs"]
            ),
        )
        self.assertEqual(
            [], alignment_errors(self.contract, validator)
        )

    def test_public_validator_has_no_drift(self):
        self.assertEqual([], alignment_errors(self.contract))

    def test_drift_is_reported(self):
        validator = SimpleNamespace(
            STAGE_A_ALLOWED_EXECUTION_ANCHOR_STRENGTH={"strong"},
            STAGE_A_NON_EXECUTION_ANCHOR_CLASSES=set(
                self.projection["allowed_non_execution_anchor_classes"]
            ),
            STAGE_A_V3_OVERRIDE_REQUIRED=list(
                self.projection["v3_override_required_fields"]
            ),
            STAGE_A_V3_NARRATIVE_FIELDS=tuple(
                self.projection["v3_narrative_fields"]
            ),
            STAGE_A_ALLOWED_STAGE_EVIDENCE_STATUS=set(
                self.projection["allowed_stage_a_evidence_statuses"]
            ),
            STAGE_A_ALLOWED_PRIMARY_URL_SEMANTICS=set(
                self.projection["allowed_primary_url_semantics"]
            ),
            STAGE_A_EVIDENCE_TARGET_KEY_PAIRS=tuple(
                self.projection["structured_evidence_target_key_pairs"]
            ),
            STAGE_A_CONFIRMATION_POINT_KEY_PAIRS=tuple(
                self.projection["structured_confirmation_point_key_pairs"]
            ),
        )
        errors = alignment_errors(self.contract, validator)
        self.assertTrue(
            any(
                "EXECUTION_ANCHOR_STRENGTH" in error
                for error in errors
            )
        )


if __name__ == "__main__":
    unittest.main()
