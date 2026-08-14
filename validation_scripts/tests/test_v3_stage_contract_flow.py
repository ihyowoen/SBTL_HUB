from __future__ import annotations

import copy
import unittest

from validation_scripts import v3_stage_contract_flow_check as flow
from validation_scripts import v3_stage_contracts


class V3StageContractFlowTests(unittest.TestCase):
    def setUp(self):
        self.document = v3_stage_contracts.load_generated_stage_contract()

    def test_execution_route_reaches_production_verification(self):
        snapshots = flow.simulate_stage_flow(
            flow.execution_route_sample(), self.document
        )
        self.assertEqual(flow.EXPECTED_STAGE_ORDER, tuple(snapshots))
        self.assertEqual(
            "execution",
            flow.route_name(snapshots["production_verification"], self.document),
        )

    def test_non_execution_route_reaches_production_verification(self):
        snapshots = flow.simulate_stage_flow(
            flow.non_execution_route_sample(), self.document
        )
        self.assertEqual(flow.EXPECTED_STAGE_ORDER, tuple(snapshots))
        self.assertEqual(
            "v3_non_execution",
            flow.route_name(snapshots["production_verification"], self.document),
        )

    def test_preserved_field_mutation_is_rejected(self):
        before = flow.non_execution_route_sample()
        after = copy.deepcopy(before)
        after["changed_judgment"] = (
            "This unauthorized mutation changes the preserved route package."
        )
        with self.assertRaisesRegex(ValueError, "mutated"):
            flow.validate_stage_handoff(
                "content_polish", before, after, self.document
            )

    def test_route_switch_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "changed route"):
            flow.validate_stage_handoff(
                "stage_b",
                flow.execution_route_sample(),
                flow.non_execution_route_sample(),
                self.document,
            )

    def test_optional_preserved_field_presence_change_is_rejected(self):
        before = flow.execution_route_sample()
        after = copy.deepcopy(before)
        del after["structural_value_override_reason"]
        with self.assertRaisesRegex(ValueError, "mutated"):
            flow.validate_stage_handoff(
                "final_qc", before, after, self.document
            )

    def test_required_execution_field_removal_fails_closed(self):
        malformed = flow.execution_route_sample()
        del malformed["remaining_uncertainty"]
        errors = flow.route_package_errors(malformed, self.document)
        self.assertTrue(
            any("missing required field remaining_uncertainty" in error for error in errors),
            errors,
        )

    def test_malformed_route_package_fails_closed(self):
        malformed = flow.non_execution_route_sample()
        malformed["execution_anchor_type"] = "should remain empty"
        self.assertTrue(flow.route_package_errors(malformed, self.document))
        with self.assertRaises(ValueError):
            flow.simulate_stage_flow(malformed, self.document)

    def test_generated_operational_flow_is_current(self):
        self.assertEqual([], flow.end_to_end_flow_errors(self.document))


if __name__ == "__main__":
    unittest.main()
