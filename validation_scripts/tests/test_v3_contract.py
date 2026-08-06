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

    def test_current_validator_projection_has_no_drift(self):
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
        )
        self.assertEqual(
            [], alignment_errors(self.contract, validator)
        )

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
