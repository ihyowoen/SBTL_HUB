from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_a_full_v3_completeness_review4943878732 as latest
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts import v3_contract
from validation_scripts.tests.test_review_4943695732_contracts import Review4943695732Contracts
from validation_scripts.tests.test_review_4943878732_contracts import Review4943878732Contracts
from validation_scripts.tests.test_stage_a_full_v3_artifact_completeness import (
    TestStageAFullV3ArtifactCompleteness,
)


class Review4943904060Contracts(unittest.TestCase):
    def full_artifact(self):
        return TestStageAFullV3ArtifactCompleteness().full_artifact()

    def run_stage_a(self, artifact):
        return TestStageAFullV3ArtifactCompleteness().run_stage_a(artifact)

    def validate_full(self, artifact):
        return latest.validate_full_stage_a_artifact(artifact, lineage._compat_module)

    def review_artifact(self):
        return Review4943878732Contracts().review_artifact()

    def test_next_call_safety_gates_are_required(self):
        fields = (
            "stage_a_validity_status",
            "artifact_consistency_status",
            "csv_schema_status",
            "review_pool_partition_status",
            "strict_pass_gate_metadata_status",
            "baseline_duplicate_screen_status",
        )
        for field in fields:
            with self.subTest(field=field):
                artifact = self.full_artifact()
                artifact.pop(field)
                result, output = self.run_stage_a(artifact)
                self.assertEqual(result, 1, output)
                self.assertIn(f"{field} must be PASS", output)

        artifact = self.full_artifact()
        artifact.pop("review_pool_carry_forward_ledger_status")
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 1, output)
        self.assertIn("review_pool_carry_forward_ledger_status must be PASS", output)

    def test_structured_next_call_recommendation_is_required_and_safe(self):
        artifact = self.full_artifact()
        artifact.pop("next_call_recommendation")
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 1, output)
        self.assertIn("next_call_recommendation must be a structured object", output)

        artifact = self.full_artifact()
        artifact["next_call_recommendation"]["recommended_next_call"] = "Stage C"
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 1, output)
        self.assertIn("next_call_recommendation must be Stage B r0", output)

    def test_candidate_review_requires_partition_specific_fields(self):
        artifact, item, _ = self.review_artifact()
        item.pop("recommended_review_method")
        messages = self.validate_full(artifact)
        self.assertTrue(
            any("candidate_review_pool requires non-empty recommended_review_method" in message for message in messages),
            messages,
        )

        artifact, item, _ = self.review_artifact()
        item["final_review_pool_disposition"] = "invalid_disposition"
        messages = self.validate_full(artifact)
        self.assertTrue(any("invalid final_review_pool_disposition" in message for message in messages), messages)

    def test_watchlist_and_reject_support_require_partition_specific_fields(self):
        helper = Review4943695732Contracts()
        base_item = helper.review_item()

        watch = copy.deepcopy(base_item)
        watch["review_pool_partition"] = "watchlist_context_pool"
        messages: list[str] = []
        latest._validate_partition_specific_review_fields(
            {"candidate_review_pool": [], "watchlist_context_pool": [watch], "reject_or_support_only_pool": []},
            messages,
        )
        self.assertTrue(any("watchlist_context_pool requires non-empty why_context_only" in message for message in messages), messages)

        reject_support = copy.deepcopy(base_item)
        reject_support["review_pool_partition"] = "reject_or_support_only_pool"
        messages = []
        latest._validate_partition_specific_review_fields(
            {"candidate_review_pool": [], "watchlist_context_pool": [], "reject_or_support_only_pool": [reject_support]},
            messages,
        )
        self.assertTrue(any("reject_or_support_only_pool requires non-empty reject_or_support_only_basis" in message for message in messages), messages)
        self.assertTrue(any("whether_support_source_only must be boolean" in message for message in messages), messages)

    def test_unhashable_execution_strength_enum_fails_closed(self):
        contract = copy.deepcopy(v3_contract.load_contract())
        contract["$defs"]["execution_route"]["properties"]["execution_anchor_strength"]["enum"] = [{}]
        errors = v3_contract.validate_contract_document(contract)
        self.assertTrue(
            any("execution_route execution_anchor_strength must match the fixed V3 execution-strength set" in error for error in errors),
            errors,
        )

    def test_legal_default_cap_requires_proven_exception(self):
        item = {
            "spec_id": "LEGAL_STAGE0",
            "legal_policy_stage": "stage_0_rhetoric_or_advocacy",
            "decision_news_value_score": 85,
        }
        messages: list[str] = []
        latest._validate_legal_default_caps({"strict_passed_spec": [item]}, messages)
        self.assertTrue(any("default cap 39 without a proven legal_policy_score_cap_exception" in message for message in messages), messages)

        item["legal_policy_score_cap_exception"] = {
            "applied": True,
            "basis": "immediate_authority",
            "evidence": "A currently operative authority independently changes present procurement eligibility.",
        }
        messages = []
        latest._validate_legal_default_caps({"strict_passed_spec": [item]}, messages)
        self.assertEqual(messages, [])

    def test_candidate_review_uses_canonical_v3_route_validation(self):
        artifact, item, _ = self.review_artifact()
        item["structural_value_override_applied"] = True
        item["structural_selector_policy_version"] = "STRUCTURAL_NEWS_VALUE_SELECTION_V3"
        item["execution_anchor_type"] = None
        item["execution_anchor_strength"] = None
        item["anchor_classes"] = ["not_a_canonical_anchor"]
        item["structural_value_override_reason"] = "The unresolved structural signal changes the baseline decision context."
        item["why_execution_event_not_required"] = "The structural change can matter before a conventional execution event occurs."
        item["evidence_needed_for_stage_b"] = []
        messages = self.validate_full(artifact)
        self.assertTrue(any("candidate review V3 route invalid" in message and "anchor classes" in message for message in messages), messages)
        self.assertTrue(any("candidate review V3 route invalid" in message and "evidence targets" in message for message in messages), messages)


if __name__ == "__main__":
    unittest.main()
