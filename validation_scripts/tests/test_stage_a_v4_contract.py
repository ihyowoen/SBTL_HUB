from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_stage_a_v3_route_alignment import TestStageAV3RouteAlignment


class StageAV4MachineContractTest(unittest.TestCase):
    def valid_execution_spec(self):
        spec = copy.deepcopy(TestStageAV3RouteAlignment().execution_spec())
        spec.update(
            {
                "selection_policy_version": "EMBEDDED_NEWS_VALUE_SELECTION_V4",
                "selection_route": "execution_anchor_route",
                "execution_credibility_gate": {"status": "PASS"},
                "independent_cardability_gate": {"status": "PASS"},
                "decision_news_value_score": 60,
                "decision_value_breakdown": {
                    "market_structure_competition": 15,
                    "supply_demand_price_utilisation": 15,
                    "technology_performance_safety": 12,
                    "cashflow_asset_value": 6,
                    "law_policy_market_access": 5,
                    "systemic_scale": 3,
                    "persistence_irreversibility": 2,
                    "decision_urgency_actionability": 2,
                },
                "decision_value_classification": "material_industry_signal",
                "publication_urgency": "near_term",
                "related_prepass": {
                    "status": "reviewed",
                    "candidate_relations": [],
                    "questions_for_stage_b": ["Confirm whether a prior roadmap card is direct lineage."],
                },
                "structural_non_execution_reason": None,
                "why_execution_event_not_required": None,
            }
        )
        return spec

    def run_active(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def test_active_entrypoint_rejects_missing_v4_policy(self):
        spec = self.valid_execution_spec()
        spec.pop("selection_policy_version")
        result, output = self.run_active(spec)
        self.assertEqual(result, 1)
        self.assertIn("selection_policy_version", output)

    def test_active_entrypoint_rejects_missing_v4_route(self):
        spec = self.valid_execution_spec()
        spec.pop("selection_route")
        result, output = self.run_active(spec)
        self.assertEqual(result, 1)
        self.assertIn("selection_route", output)

    def test_execution_route_requires_execution_anchor(self):
        spec = self.valid_execution_spec()
        spec["anchor_classes"] = ["technology_commercialization_anchor"]
        result, output = self.run_active(spec)
        self.assertEqual(result, 1)
        self.assertIn("execution_anchor_route requires execution_event_anchor", output)

    def test_score_breakdown_must_sum_to_total(self):
        spec = self.valid_execution_spec()
        spec["decision_value_breakdown"]["systemic_scale"] = 2
        result, output = self.run_active(spec)
        self.assertEqual(result, 1)
        self.assertIn("decision_value_breakdown sum", output)

    def test_structural_route_cannot_claim_execution_event_anchor(self):
        spec = self.valid_execution_spec()
        spec["selection_route"] = "structural_non_execution_route"
        spec["structural_non_execution_reason"] = "The verified policy change independently changes market access."
        spec["why_execution_event_not_required"] = "The policy effect is decision-relevant without a company execution event."
        result, output = self.run_active(spec)
        self.assertEqual(result, 1)
        self.assertIn("structural_non_execution_route cannot carry execution_event_anchor", output)

    def test_valid_v4_execution_spec_reaches_v3_compatibility_and_passes(self):
        result, output = self.run_active(self.valid_execution_spec())
        self.assertEqual(result, 0, output)
        self.assertIn("PASS_STAGE_A_SCHEMA_CONTRACT", output)

    def test_explicit_v3_compatibility_lane_does_not_require_v4(self):
        spec = TestStageAV3RouteAlignment().execution_spec()
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a_v3_compat({"strict_passed_spec": [spec]})
        self.assertEqual(result, 0, stream.getvalue())


if __name__ == "__main__":
    unittest.main()
