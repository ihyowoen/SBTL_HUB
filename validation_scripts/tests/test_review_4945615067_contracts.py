from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_a_full_v3_completeness_review4945466862 as latest
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_stage_a_full_v3_artifact_completeness import (
    TestStageAFullV3ArtifactCompleteness,
)


class Review4945615067Contracts(unittest.TestCase):
    def full_artifact(self):
        return TestStageAFullV3ArtifactCompleteness().full_artifact()

    def validate_full(self, artifact):
        return latest.validate_full_stage_a_artifact(artifact, lineage._compat_module)

    def test_explicit_technology_stage_applies_cap_without_anchor_or_lens_hint(self):
        artifact = self.full_artifact()
        spec = artifact["strict_passed_spec"][0]
        spec["anchor_classes"] = ["execution_event_anchor"]
        spec["structural_value_lenses"] = ["supply_demand_price_utilisation"]
        spec["technology_validation_stage"] = "prototype"
        spec["decision_value_breakdown"]["technology_performance_safety"] = 12

        messages = self.validate_full(artifact)
        self.assertTrue(
            any("exceeds prototype cap 7/20" in message for message in messages),
            messages,
        )

    def test_stage_b_recommendation_requires_pending_followup_when_review_work_remains(self):
        artifact = self.full_artifact()
        artifact["candidate_review_pool"] = [{"review_pool_item_id": "REVIEW_PENDING_001"}]

        messages = self.validate_full(artifact)
        for field in (
            "pending_parallel_or_followup_call",
            "pending_prompt_id",
            "pending_input_universe",
            "pending_reason",
        ):
            with self.subTest(field=field):
                self.assertTrue(
                    any(f"next_call_recommendation.{field} must be" in message for message in messages),
                    messages,
                )

    def test_strict_spec_ids_must_be_unique(self):
        artifact = self.full_artifact()
        duplicate = copy.deepcopy(artifact["strict_passed_spec"][0])
        duplicate["source_story_ids"] = ["SYNTHETIC_SECOND_STORY"]
        artifact["strict_passed_spec"].append(duplicate)

        messages = self.validate_full(artifact)
        self.assertTrue(
            any("strict_passed_spec spec_id must be unique" in message for message in messages),
            messages,
        )

    def test_strict_source_diversity_gate_is_fail_closed(self):
        artifact = self.full_artifact()
        spec = artifact["strict_passed_spec"][0]
        spec["source_cluster_preserved"] = False
        spec["source_diversity_path"] = {"status": "not_viable"}
        spec["support_source_candidates_accounted"] = False

        messages = self.validate_full(artifact)
        self.assertTrue(
            any("source_cluster_preserved must be true" in message for message in messages),
            messages,
        )
        self.assertTrue(
            any("source_diversity_path.status must be viable or uncertain" in message for message in messages),
            messages,
        )
        self.assertTrue(
            any("support_source_candidates_accounted must be true" in message for message in messages),
            messages,
        )


if __name__ == "__main__":
    unittest.main()
