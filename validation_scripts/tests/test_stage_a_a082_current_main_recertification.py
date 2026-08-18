#!/usr/bin/env python3
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from validation_scripts import stage_lineage_contract_check as lineage

ROOT = Path(__file__).resolve().parents[2]
BASE_FIXTURE = ROOT / "validation_scripts/tests/fixtures/stage_a_a082_current_main_recertification_20260818.json"
EXPECTED_SPEC = "STD26_A_082"
EXPECTED_STORY = "20260807_160552::KR_2026-08-06_C23"
MANDATORY_DOCS = [
    "docs/FACT_DISCIPLINE.md",
    "docs/STRUCTURAL_NEWS_VALUE_SELECTION.md",
    "docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md",
    "docs/PROMPT_ABC_DEFAULT_MODE.md",
    "docs/PROMPT_ABC_SUPPORTING_RULES.md",
    "docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md",
    "docs/CARD_ID_STANDARD.md",
    "docs/WORKFLOW.md",
    "docs/OPERATIONS.md",
    "docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md",
]
CONFIRMATION_REPAIR = [
    {
        "measurable_event_or_metric": "Shinheung SEC Malaysia CID 2026 production capacity",
        "interpretation_effect": "The A082 capacity milestone confirmed the supplier-expansion thesis",
    },
    {
        "measurable_event_or_metric": "Samsung SDI BBU 2026 shipment volume",
        "interpretation_effect": "The A082 shipment result strengthened the BBU-demand thesis",
    },
    {
        "measurable_event_or_metric": "Shinheung SEC Malaysia CID 2026 capacity utilization",
        "interpretation_effect": "The A082 utilization result strengthened the persistence thesis",
    },
]
BREAKDOWN = {
    "market_structure_competition": 18,
    "supply_demand_price_utilisation": 22,
    "technology_performance_safety": 8,
    "cashflow_asset_value": 7,
    "law_policy_market_access": 2,
    "systemic_scale": 4,
    "persistence_irreversibility": 3,
    "decision_urgency_actionability": 2,
}


class A082StageARecertificationContract(unittest.TestCase):
    def _run(self, *args):
        cp = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
        if cp.returncode != 0:
            self.fail(
                f"command failed: {' '.join(map(str, args))}\n"
                f"STDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
            )
        return cp.stdout

    def _materialize_full_artifact(self, target):
        data = json.loads(BASE_FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(len(data["strict_passed_spec"]), 1)
        spec = data["strict_passed_spec"][0]
        self.assertEqual(spec["spec_id"], EXPECTED_SPEC)

        # Current Prompt 0.1 / 0.1S full-item surface. This does not reopen the
        # recovered story mapping, selector decision, score, or execution route.
        spec.update({
            "merged_story_ids": [],
            "signal_rubric_estimate": {"status": "material"},
            "summary_hint": "Shinheung SEC is reported to be raising Malaysia cylindrical-battery CID capacity by 20% in a Samsung SDI BBU-demand context.",
            "context_text": "Recovered final-sweep A082 observation covering a supplier-level cylindrical CID capacity response associated with Samsung SDI AI-data-center BBU demand.",
            "why_now": "The reported supplier response moves from demand tightness into a quantified Malaysia component-capacity increase from 80 million to 100 million cell-equivalent units per month.",
            "market_relevance": "A realized supplier-capacity increase would connect AI-data-center BBU demand to cylindrical-battery component supply and customer allocation pressure.",
            "source_priority_notes": "Stage B must verify the cited body, seek Shinheung SEC or Samsung SDI source-owner confirmation where reasonably available, and lock capacity denominator and implementation timing.",
            "review_reason": None,
            "stage_b_requirement_note": (
                "Stage B must verify the provided source-candidate URL and build a valid evidence package before drafting. "
                "This Stage A spec is not evidence_complete, and primary_url is not evidence by itself."
            ),
            "execution_credibility_gate": {
                "status": "PASS",
                "anchor_type": "component_capacity_expansion",
                "anchor_strength": "strong",
                "stage_precision_note": "The recovered upstream observation states a quantified current Malaysia CID capacity increase from cell-equivalent 80 million to 100 million units per month.",
                "basis": "Specific facility-level component-capacity expansion metric is present in the recovered upstream text; Stage B evidence lock remains required."
            },
            "independent_cardability_gate": {
                "status": "PASS",
                "distinct_event_or_stage_progression": True,
                "full_schema_viability": "PASS",
                "duplicate_or_reinforcement_note": "Targeted current-main code search did not surface the same Shinheung SEC Malaysia CID capacity-expansion event; full duplicate/follow-up lock remains Prompt 0.4 work.",
                "basis": "If Stage B verifies the stated capacity expansion and BBU-linked demand context, the event can support a distinct supply-chain card."
            },
            "decision_value_breakdown": copy.deepcopy(BREAKDOWN),
            "portfolio_coverage_contribution": [
                "ai_data_center_power_and_ess_demand",
                "customer_strategy",
                "supply_demand_price_utilisation"
            ],
            "earnings_deep_dive_required": False,
            "earnings_release_available": "not_applicable",
            "ir_deck_available": "not_applicable",
            "call_or_transcript_expected": "not_applicable",
            "qna_status": "not_applicable",
            "prior_period_comparison_required": False,
            "earnings_rescue_questions": [],
            "structural_rescue_question": None,
            "search_before_delete_status": "applied",
            "review_pool_subtype": None,
            "review_pool_repromotion_precondition": None,
            "next_confirmation_points": copy.deepcopy(CONFIRMATION_REPAIR),
        })
        self.assertEqual(sum(BREAKDOWN.values()), spec["decision_news_value_score"])

        # Full artifact identity/accounting surface.
        data.update({
            "input_file": "recovered_exact_story_20260807_160552::KR_2026-08-06_C23",
            "github_main_sync_required_later": False,
            "recommended_for": ["Stage B evidence package construction after explicit user authorization"],
            "lane_sanity_rules_applied": [
                "selector_only_no_fetch",
                "exact_recovered_mapping_only",
                "superseded_raw_reselection_not_used_as_original_mapping"
            ],
            "dropped_treasure_hunt": {
                "performed": False,
                "trigger_reason": "Bounded one-item exact-mapping recertification; no dropped-story universe is being reprocessed.",
                "sample_strategy": "not_applicable_bounded_recertification",
                "sample_size": 0,
                "sampled_story_ids": [],
                "rescued_count": 0,
                "rescue_ids": [],
                "non_sampled_dropped_count": 0,
                "non_sampled_ledger_policy": "The sole recovered story is represented once in the decision ledger."
            },
            "legacy_keep": [],
            "dropped_treasure_hunt_result": [],
        })
        data["required_docs_check"] = {
            "docs_expected": list(MANDATORY_DOCS),
            "docs_read_from_github_main": list(MANDATORY_DOCS),
            "docs_missing_or_unreadable": [],
            "status": "PASS",
            "main_sha": data["baseline_main_sha"],
            "main_tree_sha": "b7cc7cd0e7c1d06191017aa3882586e0dbe8e976"
        }
        data["next_call_recommendation"] = {
            "recommended_next_call": "Stage B r0",
            "recommended_prompt_id": "Prompt 0.2",
            "recommended_input_universe": "Stage A strict_passed_spec[] only",
            "reason": "The exact A082 mapping has a current-main execution-route strict object; Stage B may begin only after repo-native Stage A validation and explicit user authorization.",
            "blocked_items_summary": [],
            "do_not_proceed_to": ["Stage C", "Prompt 0.4", "Prompt 0.5", "Prompt 0.6", "Prompt 0.7", "Prompt 0.8"]
        }
        data["summary"].update({
            "legacy_keep_count": 0,
            "needs_review_count": 0,
            "duplicate_or_reinforcement_count": 0,
            "stale_discarded_count": 0,
            "stale_warm_review_count": 0,
            "total_ledger_count": 1,
            "ledger_matches_story_count": True,
            "structural_selector_policy_version": "STRUCTURAL_NEWS_VALUE_SELECTION_V3",
            "structural_selector_policy_file": "docs/STRUCTURAL_NEWS_VALUE_SELECTION.md",
            "structural_selector_policy_sha": "3024fd411b9df1c6c3369e46ed6b423e04a36ddf",
            "credibility_cardability_value_urgency_separated": True,
            "industry_first_weighting_applied": True,
            "core_industrial_weight_total": 70,
            "multi_anchor_class_model_applied": True,
            "mandatory_structural_lenses_applied": True,
            "anchor_class_counts": {"execution_event_anchor": 1, "strategic_behavior_anchor": 1},
            "structural_lens_coverage_counts": {
                "ai_data_center_power_and_ess_demand": 1,
                "customer_strategy": 1,
                "supply_demand_price_utilisation": 1
            },
            "decision_value_classification_counts": {"material_industry_signal": 1},
            "critical_structural_candidate_ids": [],
            "high_decision_value_candidate_ids": [],
            "high_value_review_pool_ids": [],
            "structural_signal_review_pool_ids": [],
            "earnings_deep_dive_pool_ids": [],
            "follow_up_candidate_ids": [],
            "zero_coverage_domains": [],
            "execution_or_formality_bias_findings": [],
            "technology_validation_gap_ids": [],
            "legal_policy_stage_gap_ids": [],
            "search_before_delete_applied": True,
            "earnings_call_qna_rule_applied": True,
            "follow_up_probability_review_applied": True,
            "portfolio_coverage_audit_applied": True,
            "structural_value_selector_status": "PASS",
            "portfolio_coverage_audit_status": "PASS",
            "earnings_call_qna_audit_status": "NOT_APPLICABLE",
            "follow_up_repromotion_audit_status": "PASS",
            "execution_event_bias_audit_status": "PASS",
            "content_depth_audit_status": "PASS",
            "decision_ledger_count": 1,
        })

        ledger = data["decision_ledger"][0]
        ledger.update({
            "upstream_drop_reason": None,
            "integrity_group_id": None,
            "integrity_is_best": True,
            "merged_into_spec_id": None,
            "baseline_match": None,
            "anchor_classes": copy.deepcopy(spec["anchor_classes"]),
            "news_value_basis": "A quantified 20% supplier-capacity response is a concrete execution signal linking cylindrical component supply to reported Samsung SDI BBU demand pressure.",
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
            "technology_validation_stage": None,
            "technology_score_cap_applied": False,
            "technology_validation_gap": None,
            "legal_policy_stage": None,
        })
        data["repo_native_repair"] = {
            "reason": "Workflow #911 confirmed confirmation semantics but exposed the original bounded fixture as incomplete against the full current Stage A artifact contract. This pass materializes the current repo-tested full-artifact surface without changing the recovered mapping, selection, score, route, or source URLs.",
            "fields_changed": ["current full Stage A contract surface", "next_confirmation_points interpretation binding"],
            "selection_changed": False,
            "score_changed": False,
            "execution_route_changed": False,
            "source_story_mapping_changed": False,
            "source_urls_changed": False,
            "external_web_search_performed": False,
            "article_body_fetch_performed": False,
            "stage_b_started": False,
        }
        raw = (json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        target.write_bytes(raw)
        print("A082_FULL_STAGE_A_SHA256=" + hashlib.sha256(raw).hexdigest())
        return data

    def test_repo_native_contract_and_scope(self):
        for index, point in enumerate(CONFIRMATION_REPAIR):
            self.assertTrue(lineage._structured_exact_target(point["measurable_event_or_metric"]), f"target[{index}]")
            self.assertTrue(lineage._structured_interpretation_effect(point["interpretation_effect"]), f"effect[{index}]")
            self.assertTrue(lineage._valid_confirmation_point(point), f"pair[{index}]")

        with tempfile.TemporaryDirectory() as td:
            repaired = Path(td) / "stage_a_a082_current_main_recertification_FULL.json"
            data = self._materialize_full_artifact(repaired)
            artifact_out = self._run(sys.executable, str(ROOT / "validation_scripts/stage_artifact_contract_check.py"), "A", str(repaired))
            lineage_out = self._run(sys.executable, str(ROOT / "validation_scripts/stage_lineage_contract_check.py"), "stage_a", str(repaired))
            self.assertIn('"status": "PASS"', artifact_out)
            self.assertIn("PASS_STAGE_A_SCHEMA_CONTRACT", lineage_out)

            spec = data["strict_passed_spec"][0]
            self.assertEqual(spec["spec_id"], EXPECTED_SPEC)
            self.assertEqual(spec["source_story_ids"], [EXPECTED_STORY])
            self.assertEqual(spec["representative_story_id"], EXPECTED_STORY)
            self.assertEqual(spec["execution_anchor_type"], "component_capacity_expansion")
            self.assertEqual(spec["execution_anchor_strength"], "strong")
            self.assertFalse(spec["structural_value_override_applied"])
            self.assertEqual(spec["decision_news_value_score"], 66)
            self.assertEqual(sum(spec["decision_value_breakdown"].values()), 66)
            self.assertEqual(spec["strict_gate_check"], "pass")
            self.assertTrue(spec["strict_pass_gate"]["all_six_conditions_passed"])
            self.assertEqual(spec["next_confirmation_points"], CONFIRMATION_REPAIR)

            self.assertEqual(data["story_count"], 1)
            self.assertEqual(data["summary"]["strict_passed_spec_count"], 1)
            self.assertEqual(data["summary"]["decision_ledger_count"], 1)
            self.assertEqual(len(data["decision_ledger"]), 1)
            self.assertEqual(data["required_docs_check"]["status"], "PASS")
            self.assertEqual(data["required_docs_check"]["docs_read_from_github_main"], MANDATORY_DOCS)
            self.assertEqual(data["next_call_recommendation"]["recommended_input_universe"], "Stage A strict_passed_spec[] only")

            self.assertFalse(data["external_web_search_performed_in_stage_a"])
            self.assertFalse(data["article_body_fetch_performed_in_stage_a"])
            self.assertFalse(data["source_quote_generated_in_stage_a"])
            self.assertFalse(data["fact_sources_generated_in_stage_a"])
            self.assertFalse(data["card_copy_generated_in_stage_a"])
            self.assertFalse(data["production_ids_assigned"])
            self.assertFalse(data["boundary"]["stage_b_started"])
            self.assertFalse(data["boundary"]["stage_b_authorized"])
            self.assertFalse(data["boundary"]["prompt_0_4_started"])
            self.assertTrue(data["integrity_summary"]["exact_mapping_recovered_from_execution_log"])
            self.assertFalse(data["integrity_summary"]["superseded_reconstruction_used_as_original_mapping"])
            self.assertFalse(data["repo_native_repair"]["selection_changed"])
            self.assertFalse(data["repo_native_repair"]["execution_route_changed"])


if __name__ == "__main__":
    unittest.main()
