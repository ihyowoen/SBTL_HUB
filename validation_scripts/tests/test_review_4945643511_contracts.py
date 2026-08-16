from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_a_full_v3_completeness_review4945466862 as latest
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_stage_a_full_v3_artifact_completeness import (
    TestStageAFullV3ArtifactCompleteness,
)


class Review4945643511Contracts(unittest.TestCase):
    def full_artifact(self):
        return TestStageAFullV3ArtifactCompleteness().full_artifact()

    def validate_full(self, artifact):
        return latest.validate_full_stage_a_artifact(artifact, lineage._compat_module)

    def test_unknown_explicit_legal_stage_is_rejected_without_policy_hints(self):
        artifact = self.full_artifact()
        spec = artifact["strict_passed_spec"][0]
        spec["anchor_classes"] = ["execution_event_anchor"]
        spec["structural_value_lenses"] = ["supply_demand_price_utilisation"]
        spec["legal_policy_stage"] = "stage_99"

        messages = self.validate_full(artifact)
        self.assertTrue(
            any("legal_policy_stage must be one of the canonical legal-policy stages" in message for message in messages),
            messages,
        )

    def test_unknown_explicit_technology_stage_is_rejected_without_technology_hints(self):
        artifact = self.full_artifact()
        spec = artifact["strict_passed_spec"][0]
        spec["anchor_classes"] = ["execution_event_anchor"]
        spec["structural_value_lenses"] = ["supply_demand_price_utilisation"]
        spec["technology_validation_stage"] = "warp_drive"

        messages = self.validate_full(artifact)
        self.assertTrue(
            any("technology_validation_stage must be one of the canonical technology stages" in message for message in messages),
            messages,
        )

    def test_every_treasure_result_row_requires_story_identity(self):
        artifact = self.full_artifact()
        artifact["dropped_treasure_hunt"] = {
            "performed": True,
            "trigger_reason": "Synthetic sampled dropped story.",
            "sample_strategy": "deterministic synthetic regression sample",
            "sample_size": 1,
            "sampled_story_ids": ["SYNTHETIC_DROPPED_001"],
            "rescued_count": 0,
            "rescue_ids": [],
            "non_sampled_dropped_count": 0,
            "non_sampled_ledger_policy": "No additional synthetic dropped stories.",
        }
        artifact["dropped_treasure_hunt_result"] = [{}]

        messages = self.validate_full(artifact)
        self.assertTrue(
            any("dropped_treasure_hunt_result[0] must identify its sampled story" in message for message in messages),
            messages,
        )

    def test_review_partition_summary_reconciles_authoritative_pool_counts(self):
        artifact = self.full_artifact()
        artifact["candidate_review_pool"] = [
            {"review_pool_item_id": "SYNTHETIC_REVIEW_001"}
        ]
        artifact["review_pool_partition_summary"] = {}

        messages = self.validate_full(artifact)
        for pool in (
            "candidate_review_pool",
            "watchlist_context_pool",
            "reject_or_support_only_pool",
        ):
            with self.subTest(pool=pool):
                self.assertTrue(
                    any(f"missing canonical partition count {pool}" in message for message in messages),
                    messages,
                )

        artifact = self.full_artifact()
        artifact["candidate_review_pool"] = [
            {"review_pool_item_id": "SYNTHETIC_REVIEW_001"}
        ]
        artifact["review_pool_partition_summary"] = {
            "candidate_review_pool": 999,
            "watchlist_context_pool": 0,
            "reject_or_support_only_pool": 0,
        }
        messages = self.validate_full(artifact)
        self.assertTrue(
            any("candidate_review_pool must equal emitted candidate_review_pool count 1" in message for message in messages),
            messages,
        )

    def test_empty_review_workload_preserves_empty_partition_summary_compatibility(self):
        artifact = self.full_artifact()
        artifact["review_pool_partition_summary"] = {}
        messages = self.validate_full(artifact)
        self.assertFalse(
            any("review_pool_partition_summary" in message for message in messages),
            messages,
        )


if __name__ == "__main__":
    unittest.main()
