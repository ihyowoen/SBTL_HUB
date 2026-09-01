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
                "systemic_scale_denominator": "Share of the named market/capacity denominator described in Stage A metadata.",
                "denominator_gap": None,
                "related_prepass": {
                    "status": "PASS",
                    "same_event_checked": True,
                    "matched_baseline_candidate_ids": [],
                    "matched_current_batch_candidate_ids": [],
                    "relation_candidates": [],
                    "duplicate_disposition": "no_duplicate_found",
                    "earliest_same_event_check_status": "PASS",
                    "fresh_anchor_questions": [
                        "Confirm whether a prior roadmap card becomes direct lineage if execution evidence changes."
                    ],
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

    def test_non_string_anchor_is_blocked_without_type_error(self):
        spec = self.valid_execution_spec()
        spec["anchor_classes"] = ["execution_event_anchor", {"malformed": True}]
        result, output = self.run_active(spec)
        self.assertEqual(result, 1)
        self.assertIn("anchor_classes must contain non-empty strings", output)

    def test_score_breakdown_must_sum_to_total(self):
        spec = self.valid_execution_spec()
        spec["decision_value_breakdown"]["systemic_scale"] = 2
        result, output = self.run_active(spec)
        self.assertEqual(result, 1)
        self.assertIn("decision_value_breakdown sum", output)

    def test_systemic_scale_above_two_requires_denominator(self):
        spec = self.valid_execution_spec()
        spec["systemic_scale_denominator"] = None
        spec["denominator_gap"] = "No defensible denominator is available yet."
        result, output = self.run_active(spec)
        self.assertEqual(result, 1)
        self.assertIn("systemic_scale must be <=2", output)

    def test_no_denominator_with_two_points_and_gap_is_allowed_by_v4_gate(self):
        spec = self.valid_execution_spec()
        spec["systemic_scale_denominator"] = None
        spec["denominator_gap"] = "No defensible denominator is available yet."
        spec["decision_value_breakdown"]["systemic_scale"] = 2
        spec["decision_value_breakdown"]["market_structure_competition"] = 16
        result, output = self.run_active(spec)
        self.assertEqual(result, 0, output)

    def test_structural_route_cannot_claim_execution_event_anchor(self):
        spec = self.valid_execution_spec()
        spec["selection_route"] = "structural_non_execution_route"
        spec["structural_non_execution_reason"] = "The verified policy change independently changes market access."
        spec["why_execution_event_not_required"] = "The policy effect is decision-relevant without a company execution event."
        result, output = self.run_active(spec)
        self.assertEqual(result, 1)
        self.assertIn("structural_non_execution_route cannot carry execution_event_anchor", output)

    def test_arbitrary_related_prepass_object_is_blocked(self):
        spec = self.valid_execution_spec()
        spec["related_prepass"] = {"junk": True}
        result, output = self.run_active(spec)
        self.assertEqual(result, 1)
        self.assertIn("related_prepass missing status", output)
        self.assertIn("related_prepass missing same_event_checked", output)

    def test_strict_related_prepass_hold_is_blocked(self):
        spec = self.valid_execution_spec()
        spec["related_prepass"]["status"] = "HOLD"
        spec["related_prepass"]["same_event_checked"] = False
        spec["related_prepass"]["earliest_same_event_check_status"] = "HOLD"
        spec["related_prepass"]["duplicate_disposition"] = "uncertain_needs_review"
        result, output = self.run_active(spec)
        self.assertEqual(result, 1)
        self.assertIn("strict related_prepass.status must be PASS", output)

    def test_strict_duplicate_disposition_is_blocked(self):
        spec = self.valid_execution_spec()
        spec["related_prepass"]["duplicate_disposition"] = "same_event_duplicate"
        result, output = self.run_active(spec)
        self.assertEqual(result, 1)
        self.assertIn("duplicate_disposition=no_duplicate_found", output)

    def test_follow_up_relation_requires_fresh_anchor_evidence_question(self):
        spec = self.valid_execution_spec()
        spec["related_prepass"]["relation_candidates"] = [
            {
                "target_candidate_id": "2026-01-01_KR_01",
                "proposed_relation_type": "distinct_follow_up",
                "confidence": "high",
                "reason": "Same named program with a later material stage.",
                "anchor_class_to_verify": None,
                "incremental_anchor_question": None,
            }
        ]
        result, output = self.run_active(spec)
        self.assertEqual(result, 1)
        self.assertIn("anchor_class_to_verify must be a valid anchor", output)
        self.assertIn("incremental_anchor_question must be non-empty", output)

    def test_non_finite_total_score_is_blocked(self):
        spec = self.valid_execution_spec()
        spec["decision_news_value_score"] = float("nan")
        result, output = self.run_active(spec)
        self.assertEqual(result, 1)
        self.assertIn("finite numeric 0..100", output)

    def test_non_finite_breakdown_score_is_blocked(self):
        spec = self.valid_execution_spec()
        spec["decision_value_breakdown"]["systemic_scale"] = float("nan")
        result, output = self.run_active(spec)
        self.assertEqual(result, 1)
        self.assertIn("systemic_scale must be finite numeric", output)

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