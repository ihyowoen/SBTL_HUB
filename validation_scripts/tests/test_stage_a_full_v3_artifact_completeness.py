from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_stage_a_v3_route_alignment import (
    TestStageAV3RouteAlignment,
)


class TestStageAFullV3ArtifactCompleteness(unittest.TestCase):
    def full_spec(self):
        spec = copy.deepcopy(TestStageAV3RouteAlignment().execution_spec())
        spec.update(
            {
                "execution_credibility_gate": {
                    "status": "PASS",
                    "anchor_type": "production_start",
                    "anchor_strength": "strong",
                    "stage_precision_note": "The upstream Stage A material identifies a current production-start state.",
                },
                "independent_cardability_gate": {
                    "status": "PASS",
                    "distinct_event_or_stage_progression": True,
                    "full_schema_viability": "PASS",
                    "duplicate_or_reinforcement_note": "The production-start event is distinct from the prior roadmap state.",
                },
                "decision_news_value_score": 58,
                "decision_value_breakdown": {
                    "market_structure_competition": 15,
                    "supply_demand_price_utilisation": 15,
                    "technology_performance_safety": 12,
                    "cashflow_asset_value": 5,
                    "law_policy_market_access": 5,
                    "systemic_scale": 2,
                    "persistence_irreversibility": 2,
                    "decision_urgency_actionability": 2,
                },
                "decision_value_classification": "material_industry_signal",
                "structural_value_lenses": ["technology_transition_commercialization"],
                "denominator_used": "Named production program; no broader market-share denominator is claimed.",
                "denominator_gap": False,
                "publication_urgency": {
                    "level": "near_term",
                    "action_required": "Reassess commercialization timing and customer-availability assumptions for the named product.",
                    "decision_deadline": None,
                },
                "baseline_follow_up_relation": "new_unrelated",
                "portfolio_coverage_contribution": ["technology_transition_commercialization"],
                "earnings_deep_dive_required": False,
                "earnings_release_available": "not_applicable",
                "ir_deck_available": "not_applicable",
                "call_or_transcript_expected": "not_applicable",
                "qna_status": "not_applicable",
                "prior_period_comparison_required": False,
                "earnings_rescue_questions": [],
                "anti_bias_check": {
                    "binding_status_used_as_importance_proxy": False,
                    "legal_formality_used_as_importance_proxy": False,
                    "headline_amount_used_without_denominator": False,
                    "announced_capacity_treated_as_actual_output": False,
                    "routine_execution_event_overranked": False,
                    "conventional_execution_event_required_without_reason": False,
                },
                "structural_rescue_required": False,
                "structural_rescue_question": None,
                "search_before_delete_status": "applied",
                "technology_validation_stage": "production_start",
                "technology_score_cap_applied": False,
                "technology_validation_gap": "Named customer shipment volume remains unverified at Stage A.",
            }
        )
        return spec

    def ledger_row(self, spec):
        return {
            "story_id": spec["source_story_ids"][0],
            "upstream_status": "kept",
            "upstream_drop_reason": None,
            "headline": "Synthetic production-start event",
            "site": "example.com",
            "url": "https://example.com/story",
            "integrity_group_id": "SYNTHETIC_GROUP_001",
            "integrity_is_best": True,
            "ledger_decision": "strict_passed_spec",
            "editorial_bucket": "strict_passed_spec",
            "reason": "The production-start event satisfies the strict current-change contract.",
            "spec_id": spec["spec_id"],
            "merged_into_spec_id": None,
            "baseline_match": None,
            "baseline_relation": spec["baseline_relation"],
            "duplicate_risk": spec["duplicate_risk"],
            "staleness_decision": spec["staleness_decision"],
            "treasure_hunt_sampled": False,
            "notes": "Synthetic full-artifact regression fixture.",
            "anchor_classes": copy.deepcopy(spec["anchor_classes"]),
            "news_value_basis": "Production start materially advances the named product beyond roadmap status.",
            "structural_value_lenses": copy.deepcopy(spec["structural_value_lenses"]),
            "structural_value_override_applied": spec["structural_value_override_applied"],
            "structural_value_override_reason": spec["structural_value_override_reason"],
            "evidence_needed_for_stage_b": copy.deepcopy(spec["evidence_needed_for_stage_b"]),
            "why_execution_event_not_required": spec["why_execution_event_not_required"],
            "incremental_information": spec["incremental_information"],
            "decision_relevance": spec["decision_relevance"],
            "baseline_expectation_changed": spec["baseline_expectation_changed"],
            "follow_up_relation": spec["baseline_follow_up_relation"],
            "next_confirmation_points": copy.deepcopy(spec["next_confirmation_points"]),
            "portfolio_coverage_contribution": copy.deepcopy(spec["portfolio_coverage_contribution"]),
            "earnings_deep_dive_required": spec["earnings_deep_dive_required"],
            "qna_status": spec["qna_status"],
            "review_pool_subtype": None,
            "review_pool_repromotion_precondition": None,
            "decision_news_value_score": spec["decision_news_value_score"],
            "decision_value_breakdown": copy.deepcopy(spec["decision_value_breakdown"]),
            "decision_value_classification": spec["decision_value_classification"],
            "prior_state": spec["prior_state"],
            "new_verified_fact": spec["new_verified_fact"],
            "changed_judgment": spec["changed_judgment"],
            "uncertainty_resolved": spec["uncertainty_resolved"],
            "remaining_uncertainty": spec["remaining_uncertainty"],
            "denominator_used": spec["denominator_used"],
            "denominator_gap": spec["denominator_gap"],
            "publication_urgency": copy.deepcopy(spec["publication_urgency"]),
            "anti_bias_check": copy.deepcopy(spec["anti_bias_check"]),
            "structural_rescue_required": spec["structural_rescue_required"],
            "structural_rescue_question": spec["structural_rescue_question"],
            "technology_validation_stage": spec["technology_validation_stage"],
            "technology_score_cap_applied": spec["technology_score_cap_applied"],
            "technology_validation_gap": spec["technology_validation_gap"],
            "legal_policy_stage": "not_applicable",
        }

    def full_artifact(self):
        spec = self.full_spec()
        return {
            "stage": "stage_a",
            "run_tag": "SYNTHETIC_V3_FULL_ARTIFACT",
            "source_universe": "synthetic one-story Stage A universe",
            "story_count": 1,
            "summary": {
                "structural_selector_policy_version": "STRUCTURAL_NEWS_VALUE_SELECTION_V3",
                "structural_selector_policy_file": "docs/STRUCTURAL_NEWS_VALUE_SELECTION.md",
                "structural_selector_policy_sha": "synthetic-policy-sha",
                "credibility_cardability_value_urgency_separated": True,
                "industry_first_weighting_applied": True,
                "core_industrial_weight_total": 70,
                "multi_anchor_class_model_applied": True,
                "mandatory_structural_lenses_applied": True,
                "anchor_class_counts": {
                    "execution_event_anchor": 1,
                    "technology_commercialization_anchor": 1,
                },
                "structural_lens_coverage_counts": {"technology_transition_commercialization": 1},
                "decision_value_classification_counts": {"material_industry_signal": 1},
                "critical_structural_candidate_ids": [],
                "high_decision_value_candidate_ids": [],
                "high_value_review_pool_ids": [],
                "structural_signal_review_pool_ids": [],
                "earnings_deep_dive_pool_ids": [],
                "follow_up_candidate_ids": [],
                "zero_coverage_domains": [],
                "execution_or_formality_bias_findings": [],
                "technology_validation_gap_ids": ["SPEC_EXEC_ROUTE_001"],
                "legal_policy_stage_gap_ids": [],
                "search_before_delete_applied": True,
                "structural_value_selector_status": "PASS",
                "portfolio_coverage_audit_status": "PASS",
                "earnings_call_qna_audit_status": "NOT_APPLICABLE",
                "follow_up_repromotion_audit_status": "PASS",
                "execution_event_bias_audit_status": "PASS",
                "content_depth_audit_status": "PASS",
                "decision_ledger_count": 1,
            },
            "strict_passed_spec": [spec],
            "candidate_review_pool": [],
            "watchlist_context_pool": [],
            "reject_or_support_only_pool": [],
            "rejected": [],
            "existing_reinforcement": [],
            "support_source_only": [],
            "decision_ledger": [self.ledger_row(spec)],
        }

    def run_stage_a(self, artifact):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a(artifact)
        return result, stream.getvalue()

    def test_complete_full_artifact_passes(self):
        result, output = self.run_stage_a(self.full_artifact())
        self.assertEqual(result, 0, output)
        self.assertIn("PASS_STAGE_A_SCHEMA_CONTRACT", output)

    def test_full_artifact_markers_cannot_disable_completeness(self):
        for field in ("stage", "run_tag", "summary"):
            with self.subTest(field=field):
                artifact = self.full_artifact()
                artifact.pop(field)
                result, output = self.run_stage_a(artifact)
                self.assertEqual(result, 1, output)
                self.assertNotIn("PASS_STAGE_A_SCHEMA_CONTRACT", output)

    def test_nested_score_object_is_rejected_for_full_artifact(self):
        artifact = self.full_artifact()
        spec = artifact["strict_passed_spec"][0]
        spec["decision_news_value_score"] = {
            "total": 58,
            "breakdown": spec.pop("decision_value_breakdown"),
            "classification": spec.pop("decision_value_classification"),
        }
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 1)
        self.assertIn("decision_news_value_score must be integer 0..100", output)

    def test_missing_summary_contract_field_is_rejected(self):
        artifact = self.full_artifact()
        artifact["summary"].pop("mandatory_structural_lenses_applied")
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 1)
        self.assertIn("mandatory_structural_lenses_applied must be true", output)

    def test_missing_required_item_field_is_rejected(self):
        artifact = self.full_artifact()
        artifact["strict_passed_spec"][0].pop("anti_bias_check")
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 1)
        self.assertIn("missing Prompt 0.1S field anti_bias_check", output)

    def test_strict_failed_gates_are_rejected(self):
        mutations = (
            ("execution_credibility_gate", "status"),
            ("independent_cardability_gate", "status"),
            ("independent_cardability_gate", "full_schema_viability"),
        )
        for outer, inner in mutations:
            with self.subTest(field=f"{outer}.{inner}"):
                artifact = self.full_artifact()
                artifact["strict_passed_spec"][0][outer][inner] = "FAIL"
                result, output = self.run_stage_a(artifact)
                self.assertEqual(result, 1, output)

    def test_technology_stage_cap_is_enforced(self):
        artifact = self.full_artifact()
        spec = artifact["strict_passed_spec"][0]
        spec["technology_validation_stage"] = "concept_or_target"
        spec["decision_value_breakdown"]["technology_performance_safety"] = 20
        spec["decision_value_breakdown"]["market_structure_competition"] = 7
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 1)
        self.assertIn("exceeds concept_or_target cap 4/20", output)

    def test_anti_bias_metadata_must_be_object(self):
        artifact = self.full_artifact()
        artifact["strict_passed_spec"][0]["anti_bias_check"] = None
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 1)
        self.assertIn("anti_bias_check must be an object", output)

    def test_summary_counts_are_reconciled(self):
        artifact = self.full_artifact()
        artifact["summary"]["anchor_class_counts"] = {}
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 1)
        self.assertIn("anchor_class_counts does not match emitted candidates", output)

    def test_candidate_pool_container_must_be_array(self):
        for pool in (
            "strict_passed_spec",
            "candidate_review_pool",
            "watchlist_context_pool",
            "reject_or_support_only_pool",
        ):
            with self.subTest(pool=pool):
                artifact = self.full_artifact()
                artifact[pool] = "corrupt"
                result, output = self.run_stage_a(artifact)
                self.assertEqual(result, 1, output)
                self.assertIn(f"{pool} must be an array", output)

    def test_decision_ledger_is_required_and_complete(self):
        artifact = self.full_artifact()
        artifact.pop("decision_ledger")
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 1)
        self.assertIn("decision_ledger must be an array", output)

        artifact = self.full_artifact()
        artifact["decision_ledger"][0].pop("news_value_basis")
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 1)
        self.assertIn("missing required V3 ledger field news_value_basis", output)


if __name__ == "__main__":
    unittest.main()
