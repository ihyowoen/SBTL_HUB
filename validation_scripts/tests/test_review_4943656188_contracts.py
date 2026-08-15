from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout

from validation_scripts import stage_a_full_v3_completeness as full_base
from validation_scripts import stage_a_full_v3_completeness_review4943656188 as hardening
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts import v3_contract
from validation_scripts.tests.test_stage_a_full_v3_artifact_completeness import (
    TestStageAFullV3ArtifactCompleteness,
)


class Review4943656188Contracts(unittest.TestCase):
    def full_artifact(self):
        return TestStageAFullV3ArtifactCompleteness().full_artifact()

    def validate_full(self, artifact):
        return hardening.validate_full_stage_a_artifact(artifact, lineage._compat_module)

    def test_modal_since_event_clause_does_not_supply_interpretation_effect(self):
        self.assertFalse(
            lineage._has_bound_interpretation_effect(
                "Project Alpha production weakened since publication would strengthen the current demand outlook"
            )
        )
        self.assertTrue(
            lineage._has_bound_interpretation_effect(
                "Project Alpha results since 2025 would strengthen the current demand outlook"
            )
        )

    def test_outcome_story_ids_are_reconciled_to_decision_ledger(self):
        artifact = self.full_artifact()
        artifact["rejected"] = [{"story_id": "REJECTED_STORY"}]
        artifact["story_count"] = 2
        unrelated = copy.deepcopy(artifact["decision_ledger"][0])
        unrelated["story_id"] = "UNRELATED_STORY"
        artifact["decision_ledger"].append(unrelated)
        artifact["summary"]["decision_ledger_count"] = 2
        artifact["summary"]["total_ledger_count"] = 2
        messages = self.validate_full(artifact)
        self.assertTrue(
            any("REJECTED_STORY" in message and "decision_ledger is missing emitted" in message for message in messages),
            messages,
        )

    def test_strict_credibility_strength_matches_execution_route(self):
        artifact = self.full_artifact()
        artifact["strict_passed_spec"][0]["execution_credibility_gate"]["anchor_strength"] = "weak"
        messages = self.validate_full(artifact)
        self.assertTrue(
            any("anchor_strength must match execution_anchor_strength" in message for message in messages),
            messages,
        )

    def test_full_artifact_requires_top_level_provenance(self):
        artifact = self.full_artifact()
        artifact.pop("run_label")
        messages = self.validate_full(artifact)
        self.assertIn(
            "full Stage A artifact missing required top-level field run_label",
            messages,
        )

    def test_summary_candidate_id_arrays_are_reconciled(self):
        artifact = self.full_artifact()
        spec = artifact["strict_passed_spec"][0]
        spec["decision_value_breakdown"] = {
            "market_structure_competition": 25,
            "supply_demand_price_utilisation": 25,
            "technology_performance_safety": 12,
            "cashflow_asset_value": 10,
            "law_policy_market_access": 10,
            "systemic_scale": 3,
            "persistence_irreversibility": 3,
            "decision_urgency_actionability": 2,
        }
        spec["decision_news_value_score"] = 90
        spec["decision_value_classification"] = "critical_structural"
        artifact["summary"]["decision_value_classification_counts"] = {"critical_structural": 1}
        messages = self.validate_full(artifact)
        self.assertIn(
            "full Stage A summary critical_structural_candidate_ids does not match emitted candidates",
            messages,
        )

    def test_earnings_review_subtype_cannot_self_disable_requirements(self):
        artifact = self.full_artifact()
        item = copy.deepcopy(artifact["strict_passed_spec"][0])
        item.update(
            {
                "review_pool_item_id": "REVIEW_EARNINGS_001",
                "review_pool_partition": "candidate_review_pool",
                "review_pool_partition_reason": "Listed-company result requires call and Q&A review.",
                "review_pool_subtype": "earnings_deep_dive",
                "promotion_precondition": "Verify the full call, analyst Q&A, and prior-period comparison.",
                "recommended_next_action": "Retain in candidate review until the earnings evidence package is complete.",
                "earnings_deep_dive_required": False,
                "earnings_release_available": "not_applicable",
                "ir_deck_available": "not_applicable",
                "call_or_transcript_expected": "not_applicable",
                "qna_status": "not_applicable",
                "prior_period_comparison_required": False,
                "earnings_rescue_questions": [],
            }
        )
        artifact["candidate_review_pool"] = [item]
        artifact["summary"]["earnings_call_qna_audit_status"] = "NOT_APPLICABLE"
        messages = self.validate_full(artifact)
        self.assertTrue(
            any("earnings_deep_dive subtype requires earnings_deep_dive_required=true" in message for message in messages),
            messages,
        )
        self.assertTrue(
            any("must be PASS when earnings_deep_dive subtype exists" in message for message in messages),
            messages,
        )

    def test_malformed_outcome_entries_fail_closed_before_legacy_validator(self):
        for value in (None, "corrupt", []):
            with self.subTest(value=value):
                artifact = self.full_artifact()
                artifact["rejected"] = [value]
                stream = io.StringIO()
                with redirect_stdout(stream):
                    result = lineage.check_stage_a(artifact)
                self.assertEqual(result, 1, stream.getvalue())
                self.assertIn("rejected[0] must be an object", stream.getvalue())

    def test_legal_default_caps_are_not_absolute_ceilings(self):
        item = {
            "anchor_classes": ["policy_regulatory_anchor"],
            "structural_value_lenses": ["law_policy"],
            "decision_news_value_score": 40,
            "legal_policy_stage": "stage_0_rhetoric_or_advocacy",
            "legal_instrument_type": "official executive statement",
            "competent_authority": "competent authority with immediate authority",
            "procedural_status": "current statement with immediate authority",
            "adoption_date": "not_applicable",
            "publication_date": "2026-08-15",
            "effective_date": "not_applicable",
            "mandatory_application_date": "not_applicable",
            "affected_entities": ["named regulated entities"],
            "affected_products_or_activities": ["named procurement activity"],
            "geographic_scope": "named jurisdiction",
            "extraterritorial_effect": "not_applicable",
            "budget_or_funding_source": "not_applicable",
            "implementation_mechanism": "immediate authority",
            "administrative_readiness": "authority already exists",
            "exemptions_and_thresholds": [],
            "transition_and_grandfathering": [],
            "noncompliance_consequences": [],
            "appeal_or_litigation_risk": "not_applicable",
            "reversibility_risk": "possible but not automatic",
            "precedent_scope": "named procurement context",
            "legal_policy_transmission_chain": ["authority -> procurement practice"],
            "next_implementation_trigger": "first observable procurement action",
        }
        messages: list[str] = []
        full_base._validate_legal_policy(item, "POLICY_001", messages)
        self.assertFalse(any("exceeds stage_0" in message for message in messages), messages)

    def test_split_metadata_rejects_padded_names(self):
        contract = copy.deepcopy(v3_contract.load_contract())
        contract["x-sbtl-contract"]["shared_strict_required_fields"][0] = "  anchor_classes  "
        errors = v3_contract.validate_contract_document(contract)
        self.assertTrue(
            any("shared_strict_required_fields" in error for error in errors),
            errors,
        )

    def test_fixed_v3_field_set_cannot_be_coherently_shrunk(self):
        contract = copy.deepcopy(v3_contract.load_contract())
        metadata = contract["x-sbtl-contract"]
        for field in (
            "shared_strict_required_fields",
            "v3_override_required_fields",
            "v3_narrative_fields",
        ):
            metadata[field] = [value for value in metadata[field] if value != "remaining_uncertainty"]
        for route in ("execution_route", "v3_non_execution_route"):
            definition = contract["$defs"][route]
            definition["required"] = [
                value for value in definition["required"] if value != "remaining_uncertainty"
            ]
            definition["properties"].pop("remaining_uncertainty", None)
        errors = v3_contract.validate_contract_document(contract)
        self.assertTrue(
            any("fixed V3 shared field set" in error or "fixed V3 route field set" in error for error in errors),
            errors,
        )

    def test_strict_base_fields_are_part_of_full_artifact_contract(self):
        artifact = self.full_artifact()
        artifact["strict_passed_spec"][0].pop("source_origin")
        messages = self.validate_full(artifact)
        self.assertIn(
            "SPEC_EXEC_ROUTE_001: missing required base strict field source_origin",
            messages,
        )

    def test_promotion_precondition_rejects_non_text_scalars(self):
        artifact = self.full_artifact()
        item = copy.deepcopy(artifact["strict_passed_spec"][0])
        item.update(
            {
                "review_pool_item_id": "REVIEW_GENERAL_001",
                "review_pool_partition": "candidate_review_pool",
                "review_pool_partition_reason": "Bounded review is required before promotion.",
                "review_pool_subtype": "general_candidate",
                "promotion_precondition": False,
                "recommended_next_action": "Keep in candidate review pending the bounded check.",
            }
        )
        artifact["candidate_review_pool"] = [item]
        messages = self.validate_full(artifact)
        self.assertTrue(
            any("promotion_precondition must be meaningful text" in message for message in messages),
            messages,
        )


if __name__ == "__main__":
    unittest.main()
