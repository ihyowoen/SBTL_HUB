from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_a_full_v3_completeness_review4943878732 as latest
from validation_scripts import v3_contract
from validation_scripts.tests.test_stage_a_full_v3_artifact_completeness import (
    TestStageAFullV3ArtifactCompleteness,
)


class Review4943980352Contracts(unittest.TestCase):
    def full_artifact(self):
        return TestStageAFullV3ArtifactCompleteness().full_artifact()

    def run_stage_a(self, artifact):
        return TestStageAFullV3ArtifactCompleteness().run_stage_a(artifact)

    def next_call_base(self):
        return {
            "stage_a_validity_status": "PASS",
            "artifact_consistency_status": "PASS",
            "csv_schema_status": "PASS",
            "review_pool_partition_status": "PASS",
            "review_pool_carry_forward_ledger_status": "PASS",
            "strict_pass_gate_metadata_status": "PASS",
            "baseline_duplicate_screen_status": "PASS",
            "summary": {
                "ledger_matches_story_count": True,
                "strict_passed_spec_count": 0,
            },
            "strict_passed_spec": [],
            "candidate_review_pool": [],
            "watchlist_context_pool": [],
            "next_call_recommendation": {
                "recommended_next_call": "Stage C",
                "recommended_prompt_id": "Prompt 999",
                "recommended_input_universe": "arbitrary universe",
                "reason": "Synthetic malformed zero-strict recommendation.",
                "blocked_items_summary": [],
            },
        }

    def test_zero_strict_next_call_is_routed_by_emitted_review_pools(self):
        artifact = self.next_call_base()
        artifact["candidate_review_pool"] = [{"review_pool_item_id": "REVIEW_1"}]
        messages: list[str] = []
        latest._validate_next_call_safety(artifact, messages)
        self.assertTrue(
            any("must recommend candidate_review_pool triage" in message for message in messages),
            messages,
        )
        self.assertTrue(
            any("recommended_input_universe=Stage A candidate_review_pool[] only" in message for message in messages),
            messages,
        )

        artifact = self.next_call_base()
        artifact["watchlist_context_pool"] = [{"review_pool_item_id": "WATCH_1"}]
        messages = []
        latest._validate_next_call_safety(artifact, messages)
        self.assertTrue(
            any("must recommend retrospective or watchlist context review" in message for message in messages),
            messages,
        )
        self.assertTrue(
            any("recommended_input_universe=watchlist_context_pool[] only, not Stage B" in message for message in messages),
            messages,
        )

        artifact = self.next_call_base()
        messages = []
        latest._validate_next_call_safety(artifact, messages)
        self.assertTrue(
            any("must recommend retrospective" in message for message in messages),
            messages,
        )
        self.assertTrue(
            any("recommended_prompt_id=Prompt 1.1" in message for message in messages),
            messages,
        )

    def test_malformed_override_required_fields_fail_closed(self):
        contract = copy.deepcopy(v3_contract.load_contract())
        contract["x-sbtl-contract"]["v3_override_required_fields"] = [{}]
        errors = v3_contract.validate_contract_document(contract)
        self.assertTrue(errors)
        self.assertTrue(
            any(
                "v3_override_required_fields must be a unique non-empty canonical string array"
                in error
                for error in errors
            ),
            errors,
        )

    def test_emitted_stage_a_pool_prevents_completeness_bypass(self):
        artifact = self.full_artifact()
        for field in (
            "stage",
            "run_tag",
            "summary",
            "story_count",
            "decision_ledger",
            "source_universe",
        ):
            artifact.pop(field)

        self.assertTrue(latest.looks_like_full_stage_a_artifact(artifact))
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 1, output)
        self.assertNotIn("PASS_STAGE_A_SCHEMA_CONTRACT", output)


if __name__ == "__main__":
    unittest.main()
