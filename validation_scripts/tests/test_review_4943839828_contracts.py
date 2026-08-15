from __future__ import annotations

import unittest

from validation_scripts import stage_a_full_v3_completeness_review4943777463 as latest
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_review_4943695732_contracts import Review4943695732Contracts
from validation_scripts.tests.test_stage_a_full_v3_artifact_completeness import (
    TestStageAFullV3ArtifactCompleteness,
)


class Review4943839828Contracts(unittest.TestCase):
    def full_artifact(self):
        return TestStageAFullV3ArtifactCompleteness().full_artifact()

    def run_stage_a(self, artifact):
        return TestStageAFullV3ArtifactCompleteness().run_stage_a(artifact)

    def validate_full(self, artifact):
        return latest.validate_full_stage_a_artifact(artifact, lineage._compat_module)

    def test_legacy_membership_operands_fail_closed_before_typeerror(self):
        mutations = (
            ("stage_a_evidence_status", []),
            ("primary_url_semantics", {}),
            ("execution_anchor_strength", ["strong"]),
            ("technology_validation_stage", []),
            ("legal_policy_stage", {}),
        )
        for field, bad in mutations:
            with self.subTest(field=field):
                artifact = self.full_artifact()
                artifact["strict_passed_spec"][0][field] = bad
                result, output = self.run_stage_a(artifact)
                self.assertEqual(result, 1, output)
                self.assertNotIn("TypeError", output)
                self.assertIn(field, output)

        nested_mutations = (
            ("execution_credibility_gate", "anchor_strength", []),
            ("publication_urgency", "level", {}),
        )
        for outer, inner, bad in nested_mutations:
            with self.subTest(field=f"{outer}.{inner}"):
                artifact = self.full_artifact()
                artifact["strict_passed_spec"][0][outer][inner] = bad
                result, output = self.run_stage_a(artifact)
                self.assertEqual(result, 1, output)
                self.assertNotIn("TypeError", output)
                self.assertIn(f"{outer}.{inner}", output)

        artifact = self.full_artifact()
        artifact["summary"]["earnings_call_qna_audit_status"] = []
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 1, output)
        self.assertNotIn("TypeError", output)
        self.assertIn("earnings_call_qna_audit_status", output)

    def test_resolution_ledger_story_identity_matches_review_item(self):
        helper = Review4943695732Contracts()
        artifact = helper.full_artifact()
        item = helper.review_item()
        artifact["candidate_review_pool"] = [item]
        artifact["summary"]["needs_review_count"] = 1
        artifact["review_pool_resolution_ledger"] = [
            {
                "review_pool_item_id": item["review_pool_item_id"],
                "story_id": "WRONG_STORY",
                "original_review_pool_partition": "candidate_review_pool",
                "current_disposition": "candidate_review_pool",
                "disposition_basis": "Synthetic story-lineage regression fixture.",
                "carry_forward_policy": item["carry_forward_policy"],
                "next_action_condition": item["next_action_condition"],
                "whether_user_authorization_required": False,
            }
        ]
        messages = self.validate_full(artifact)
        self.assertTrue(
            any("story identity must match emitted review item" in message for message in messages),
            messages,
        )

    def test_treasure_hunt_counts_ids_subset_and_results_reconcile(self):
        artifact = self.full_artifact()
        treasure = artifact["dropped_treasure_hunt"]
        treasure.update(
            {
                "performed": True,
                "sample_size": 5,
                "sampled_story_ids": [],
                "rescued_count": 4,
                "rescue_ids": [],
            }
        )
        messages = self.validate_full(artifact)
        self.assertTrue(any("sample_size must equal sampled_story_ids length" in m for m in messages), messages)
        self.assertTrue(any("rescued_count must equal rescue_ids length" in m for m in messages), messages)

        artifact = self.full_artifact()
        treasure = artifact["dropped_treasure_hunt"]
        treasure.update(
            {
                "performed": True,
                "sample_size": 1,
                "sampled_story_ids": ["SAMPLE_1"],
                "rescued_count": 1,
                "rescue_ids": ["OTHER_STORY"],
            }
        )
        artifact["dropped_treasure_hunt_result"] = []
        messages = self.validate_full(artifact)
        self.assertTrue(any("rescue_ids must be a subset" in m for m in messages), messages)
        self.assertTrue(any("dropped_treasure_hunt_result length" in m for m in messages), messages)

        artifact["dropped_treasure_hunt"]["rescue_ids"] = ["SAMPLE_1"]
        artifact["dropped_treasure_hunt_result"] = [{"story_id": "WRONG_STORY"}]
        messages = self.validate_full(artifact)
        self.assertTrue(any("result story identities must match sampled_story_ids" in m for m in messages), messages)

    def test_original_status_counts_are_integer_counts_matching_story_count(self):
        artifact = self.full_artifact()
        artifact["original_status_counts"] = {"kept": 999}
        messages = self.validate_full(artifact)
        self.assertTrue(any("original_status_counts total 999 must equal story_count 1" in m for m in messages), messages)

        artifact["original_status_counts"] = {"kept": []}
        messages = self.validate_full(artifact)
        self.assertTrue(any("must be a non-negative integer" in m for m in messages), messages)


if __name__ == "__main__":
    unittest.main()
