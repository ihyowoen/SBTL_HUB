from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_review_4840844831_contracts import (
    TestReview4840844831Contracts,
)


class TestLatestStageARouteReview(unittest.TestCase):
    def base_v3_spec(self):
        return TestReview4840844831Contracts().base_spec()

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def clean_execution_spec(self):
        spec = self.base_v3_spec()
        spec["execution_anchor_type"] = "commercial_award"
        spec["execution_anchor_strength"] = "strong"
        spec["structural_value_override_applied"] = False
        spec["structural_value_override_reason"] = None
        spec["why_execution_event_not_required"] = None
        spec["anchor_classes"] = ["execution_event_anchor"]
        # Shared V3 decision metadata from the base fixture remains populated on
        # the execution route; only true override rationale is empty.
        return spec

    def test_clean_execution_route_passes(self):
        result, output = self.run_stage_a(self.clean_execution_spec())
        self.assertEqual(result, 0, output)
        self.assertIn("PASS_STAGE_A_SCHEMA_CONTRACT", output)

    def test_execution_route_requires_explicit_false_marker(self):
        spec = self.clean_execution_spec()
        spec.pop("structural_value_override_applied")
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn("requires structural_value_override_applied=false", output)

    def test_execution_route_rejects_residual_override_package(self):
        spec = self.clean_execution_spec()
        spec["structural_value_override_reason"] = "Residual strategic rationale must not remain on the execution path."
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn(
            "execution route must leave override-only field structural_value_override_reason empty",
            output,
        )

    def test_exact_unlisted_and_korean_targets_pass(self):
        for target in ("SEC filing 2027 revenue", "금감원 공시 2027년 매출"):
            with self.subTest(target=target):
                spec = copy.deepcopy(self.base_v3_spec())
                spec["evidence_needed_for_stage_b"] = [target]
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 0, output)

    def test_generic_target_still_fails(self):
        spec = self.base_v3_spec()
        spec["evidence_needed_for_stage_b"] = ["official sources for confirmation"]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn("source/document class and an exact claim", output)


if __name__ == "__main__":
    unittest.main()
