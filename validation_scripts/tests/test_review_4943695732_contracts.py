from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_a_full_v3_completeness_review4943656188_final as final
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts import v3_contract
from validation_scripts.tests.test_stage_a_full_v3_artifact_completeness import (
    TestStageAFullV3ArtifactCompleteness,
)


class Review4943695732Contracts(unittest.TestCase):
    def full_artifact(self):
        return TestStageAFullV3ArtifactCompleteness().full_artifact()

    def validate_full(self, artifact):
        return final.validate_full_stage_a_artifact(artifact, lineage._compat_module)

    def valid_rejected(self, story_id="REJECTED_STORY"):
        return {
            "story_id": story_id,
            "upstream_status": "dropped",
            "rejected_reason_code": "outside_sbtl_lane",
            "rejected_reason_detail": "The story has no battery, storage, grid, materials, trade, policy, or industrial-supply-chain relevance.",
            "hard_reject_basis": "out_of_scope",
            "hard_reject_confidence": "high",
            "hard_reject_positive_test_passed": True,
            "hard_reject_anti_overclosure_check": "PASS",
            "why_not_review_pool": "No bounded SBTL-relevant review question remains after the lane check.",
            "baseline_match": None,
            "staleness_decision": "not_applicable",
            "notes": "Synthetic rejected-item regression fixture.",
        }

    def review_item(self):
        item = copy.deepcopy(self.full_artifact()["strict_passed_spec"][0])
        item.update(
            {
                "story_id": "REVIEW_STORY",
                "review_pool_item_id": "REVIEW_ITEM_001",
                "upstream_status": "review",
                "reason_for_review": "A bounded source-direction check is required before promotion.",
                "review_type": "general_candidate",
                "what_must_be_checked_before_promotion": "Verify the named stage and its current date from the provided source packet.",
                "why_not_strict_passed_spec": "The current preview does not yet support strict admission.",
                "baseline_relation_if_known": "new_unrelated",
                "staleness_decision": "current",
                "recommended_next_action": "Retain in candidate review until the bounded check is complete.",
                "carry_forward_policy": "carry_until_resolved",
                "next_action_condition": "Promote only after the source-direction and stage check passes.",
                "review_pool_resolution_status": "open",
                "review_pool_partition": "candidate_review_pool",
                "review_pool_partition_reason": "The item remains potentially cardable but unresolved.",
                "review_pool_subtype": "general_candidate",
                "promotion_precondition": "Verify the exact current event stage from the provided source packet.",
                "bounded_review_question": "Does the provided source packet support the claimed current event stage?",
            }
        )
        return item

    def test_story_cannot_appear_in_multiple_disposition_pools(self):
        artifact = self.full_artifact()
        story_id = artifact["strict_passed_spec"][0]["source_story_ids"][0]
        artifact["rejected"] = [self.valid_rejected(story_id)]
        artifact["summary"]["rejected_count"] = 1
        messages = self.validate_full(artifact)
        self.assertTrue(
            any("must appear in exactly one Stage A disposition" in message for message in messages),
            messages,
        )

    def test_rejected_entries_require_complete_audit_fields(self):
        artifact = self.full_artifact()
        rejected = self.valid_rejected()
        rejected.pop("upstream_status")
        artifact["rejected"] = [rejected]
        messages = self.validate_full(artifact)
        self.assertTrue(
            any("missing required rejected field upstream_status" in message for message in messages),
            messages,
        )

    def test_review_entries_require_complete_base_contract(self):
        artifact = self.full_artifact()
        item = self.review_item()
        item.pop("reason_for_review")
        artifact["candidate_review_pool"] = [item]
        messages = self.validate_full(artifact)
        self.assertTrue(
            any("missing required base review field reason_for_review" in message for message in messages),
            messages,
        )

    def test_summary_id_arrays_are_order_insensitive_but_unique(self):
        artifact = {
            "strict_passed_spec": [
                {
                    "spec_id": "A",
                    "decision_value_classification": "critical_structural",
                    "anchor_classes": [],
                    "structural_value_lenses": [],
                    "baseline_follow_up_relation": "new_unrelated",
                },
                {
                    "spec_id": "B",
                    "decision_value_classification": "critical_structural",
                    "anchor_classes": [],
                    "structural_value_lenses": [],
                    "baseline_follow_up_relation": "new_unrelated",
                },
            ],
            "candidate_review_pool": [],
            "watchlist_context_pool": [],
            "reject_or_support_only_pool": [],
            "summary": {"critical_structural_candidate_ids": ["B", "A"]},
        }
        messages: list[str] = []
        final._validate_summary_id_arrays_unordered(artifact, messages)
        self.assertEqual(messages, [])

        artifact["summary"]["critical_structural_candidate_ids"] = ["A", "A"]
        messages = []
        final._validate_summary_id_arrays_unordered(artifact, messages)
        self.assertTrue(any("must not contain duplicate IDs" in message for message in messages), messages)

    def test_required_docs_check_must_pass_and_cover_all_ten_docs(self):
        artifact = self.full_artifact()
        artifact["required_docs_check"]["status"] = "FAIL"
        artifact["required_docs_check"]["docs_missing_or_unreadable"] = [
            "docs/FACT_DISCIPLINE.md"
        ]
        artifact["required_docs_check"]["docs_expected"].remove("docs/FACT_DISCIPLINE.md")
        messages = self.validate_full(artifact)
        self.assertIn("full Stage A artifact required_docs_check.status must be PASS", messages)
        self.assertIn(
            "full Stage A artifact required_docs_check.docs_missing_or_unreadable must be empty",
            messages,
        )
        self.assertTrue(
            any("docs_expected missing mandatory documents" in message for message in messages),
            messages,
        )

    def test_canonical_route_enum_memberships_are_version_pinned(self):
        contract = copy.deepcopy(v3_contract.load_contract())
        metadata = contract["x-sbtl-contract"]
        metadata["allowed_execution_anchor_strengths"].append("weak")
        contract["$defs"]["execution_route"]["properties"]["execution_anchor_strength"]["enum"].append("weak")
        errors = v3_contract.validate_contract_document(contract)
        self.assertTrue(
            any("fixed V3 execution-strength set" in error for error in errors),
            errors,
        )

        contract = copy.deepcopy(v3_contract.load_contract())
        metadata = contract["x-sbtl-contract"]
        metadata["allowed_non_execution_anchor_classes"].remove("data_financial_anchor")
        for name in ("execution_anchor_classes", "non_execution_anchor_classes"):
            contract["$defs"][name]["items"]["enum"].remove("data_financial_anchor")
        errors = v3_contract.validate_contract_document(contract)
        self.assertTrue(
            any("fixed V3 non-execution anchor set" in error for error in errors),
            errors,
        )

    def test_all_v3_application_markers_are_required(self):
        for field in final.V3_APPLICATION_MARKERS:
            with self.subTest(field=field):
                artifact = self.full_artifact()
                artifact["summary"].pop(field)
                messages = self.validate_full(artifact)
                self.assertIn(f"full Stage A summary {field} must be true", messages)

    def test_denominator_gap_caps_systemic_scale_at_two(self):
        artifact = self.full_artifact()
        spec = artifact["strict_passed_spec"][0]
        spec["denominator_gap"] = True
        spec["decision_value_breakdown"]["systemic_scale"] = 5
        messages = self.validate_full(artifact)
        self.assertTrue(
            any("denominator_gap=true caps decision_value_breakdown.systemic_scale at 2/5" in message for message in messages),
            messages,
        )


if __name__ == "__main__":
    unittest.main()
