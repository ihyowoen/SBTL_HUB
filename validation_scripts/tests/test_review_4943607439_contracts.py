from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_a_full_v3_completeness_review4943607439 as hardening
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts import v3_contract
from validation_scripts import v3_stage_contract_flow_check as flow
from validation_scripts import v3_stage_contracts
from validation_scripts.tests.test_stage_a_full_v3_artifact_completeness import (
    TestStageAFullV3ArtifactCompleteness,
)


class Review4943607439Contracts(unittest.TestCase):
    def setUp(self):
        self.fixture = TestStageAFullV3ArtifactCompleteness()

    def test_finite_since_event_clause_does_not_supply_interpretation_effect(self):
        self.assertFalse(
            lineage._has_bound_interpretation_effect(
                "Project Alpha production weakened since publication was delayed and would strengthen the current demand outlook"
            )
        )
        self.assertTrue(
            lineage._has_bound_interpretation_effect(
                "Project Alpha production since 2025 would strengthen the current demand outlook"
            )
        )

    def test_generated_contract_projects_route_neutral_split_and_selector(self):
        document = v3_stage_contracts.build_stage_contract_document()
        canonical = document["canonical"]
        self.assertEqual(
            "STRUCTURAL_NEWS_VALUE_SELECTION_V3",
            canonical["structural_selector_policy_version"],
        )
        self.assertEqual(
            list(v3_contract.contract_projection(v3_contract.load_contract())["shared_strict_required_fields"]),
            canonical["shared_strict_required_fields"],
        )
        self.assertEqual(
            list(v3_contract.contract_projection(v3_contract.load_contract())["override_only_required_fields"]),
            canonical["override_only_required_fields"],
        )

    def test_flow_consumes_projected_override_split(self):
        document = v3_stage_contracts.build_stage_contract_document()
        mutated = copy.deepcopy(document)
        canonical = mutated["canonical"]
        canonical["shared_strict_required_fields"].remove("decision_relevance")
        canonical["override_only_required_fields"].append("decision_relevance")
        canonical["route_empty_only_fields"]["execution"].append("decision_relevance")
        errors = flow.route_package_errors(flow.execution_route_sample(), mutated)
        self.assertTrue(
            any("requires empty field decision_relevance" in error for error in errors),
            errors,
        )
        self.assertFalse(
            any("substantive decision_relevance" in error for error in errors),
            errors,
        )

    def test_canonical_schema_requires_non_execution_selector_version(self):
        contract = v3_contract.load_contract()
        non_execution = contract["$defs"]["v3_non_execution_route"]
        self.assertIn("structural_selector_policy_version", non_execution["required"])
        self.assertEqual(
            {"const": "STRUCTURAL_NEWS_VALUE_SELECTION_V3"},
            non_execution["properties"]["structural_selector_policy_version"],
        )

        broken = copy.deepcopy(contract)
        broken_non_execution = broken["$defs"]["v3_non_execution_route"]
        broken_non_execution["required"].remove("structural_selector_policy_version")
        broken_non_execution["properties"].pop("structural_selector_policy_version")
        errors = v3_contract.validate_contract_document(broken)
        self.assertTrue(
            any("structural_selector_policy_version" in error or "selector-lineage" in error for error in errors),
            errors,
        )

    def test_full_artifact_requires_non_review_outcome_arrays(self):
        for field in ("rejected", "existing_reinforcement", "support_source_only"):
            with self.subTest(field=field):
                artifact = self.fixture.full_artifact()
                artifact.pop(field)
                messages = hardening.validate_full_stage_a_artifact(
                    artifact, lineage._compat_module
                )
                self.assertIn(
                    f"full Stage A artifact {field} must be an array",
                    messages,
                )

    def test_decision_ledger_keeps_base_stage_a_columns(self):
        artifact = self.fixture.full_artifact()
        artifact["decision_ledger"][0].pop("upstream_status")
        messages = hardening.validate_full_stage_a_artifact(
            artifact, lineage._compat_module
        )
        self.assertIn(
            "decision_ledger[0]: missing required base ledger field upstream_status",
            messages,
        )

    def test_earnings_not_applicable_is_rejected_when_earnings_candidate_exists(self):
        artifact = self.fixture.full_artifact()
        spec = artifact["strict_passed_spec"][0]
        spec.update(
            {
                "earnings_deep_dive_required": True,
                "earnings_release_available": "yes",
                "ir_deck_available": "yes",
                "call_or_transcript_expected": "unknown",
                "qna_status": "not_checked_stage_a",
                "prior_period_comparison_required": True,
                "earnings_rescue_questions": [
                    "Confirm the named company's call transcript and analyst Q&A before promotion."
                ],
            }
        )
        ledger = artifact["decision_ledger"][0]
        ledger["earnings_deep_dive_required"] = True
        ledger["qna_status"] = "not_checked_stage_a"
        artifact["summary"]["earnings_call_qna_audit_status"] = "NOT_APPLICABLE"
        messages = hardening.validate_full_stage_a_artifact(
            artifact, lineage._compat_module
        )
        self.assertIn(
            "full Stage A summary earnings_call_qna_audit_status must be PASS when earnings candidates exist",
            messages,
        )

    def test_credibility_gate_requires_populated_and_matching_anchor_evidence(self):
        artifact = self.fixture.full_artifact()
        gate = artifact["strict_passed_spec"][0]["execution_credibility_gate"]
        gate["anchor_type"] = None
        messages = hardening.validate_full_stage_a_artifact(
            artifact, lineage._compat_module
        )
        self.assertTrue(
            any("execution_credibility_gate.anchor_type must be a non-empty string" in message for message in messages),
            messages,
        )

        artifact = self.fixture.full_artifact()
        gate = artifact["strict_passed_spec"][0]["execution_credibility_gate"]
        gate["stage_precision_note"] = None
        messages = hardening.validate_full_stage_a_artifact(
            artifact, lineage._compat_module
        )
        self.assertTrue(
            any("execution_credibility_gate.stage_precision_note must be item-specific" in message for message in messages),
            messages,
        )

        artifact = self.fixture.full_artifact()
        gate = artifact["strict_passed_spec"][0]["execution_credibility_gate"]
        gate["anchor_type"] = "signed_supply_agreement"
        messages = hardening.validate_full_stage_a_artifact(
            artifact, lineage._compat_module
        )
        self.assertTrue(
            any("must match execution_anchor_type" in message for message in messages),
            messages,
        )

    def test_review_items_must_match_partition_and_cannot_bypass_to_stage_b(self):
        artifact = self.fixture.full_artifact()
        item = copy.deepcopy(artifact["strict_passed_spec"].pop())
        item.update(
            {
                "review_pool_item_id": "REVIEW_WATCH_001",
                "story_id": item["source_story_ids"][0],
                "review_pool_partition": "candidate_review_pool",
                "review_pool_partition_reason": "Context-only signal awaiting a material change.",
                "recommended_next_action": "Send directly to Stage B",
                "review_pool_subtype": "general_candidate",
                "promotion_precondition": "A material execution or data change must occur.",
            }
        )
        artifact["watchlist_context_pool"].append(item)
        messages = hardening.validate_full_stage_a_artifact(
            artifact, lineage._compat_module
        )
        self.assertTrue(
            any("review_pool_partition must be 'watchlist_context_pool'" in message for message in messages),
            messages,
        )
        self.assertTrue(
            any("watchlist_context_pool recommended_next_action must not recommend Stage B" in message for message in messages),
            messages,
        )

        artifact = self.fixture.full_artifact()
        item = copy.deepcopy(artifact["strict_passed_spec"].pop())
        item.update(
            {
                "review_pool_item_id": "REVIEW_CANDIDATE_001",
                "story_id": item["source_story_ids"][0],
                "review_pool_partition": "candidate_review_pool",
                "review_pool_partition_reason": "Potential candidate awaiting bounded promotion evidence.",
                "recommended_next_action": "Retain in candidate review until promotion conditions are met.",
                "review_pool_subtype": "general_candidate",
                "promotion_precondition": "",
            }
        )
        artifact["candidate_review_pool"].append(item)
        messages = hardening.validate_full_stage_a_artifact(
            artifact, lineage._compat_module
        )
        self.assertTrue(
            any("candidate_review_pool promotion_precondition must be populated" in message for message in messages),
            messages,
        )


if __name__ == "__main__":
    unittest.main()
