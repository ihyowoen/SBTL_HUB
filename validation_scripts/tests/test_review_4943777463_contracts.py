from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_a_full_v3_completeness_review4943777463 as latest
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts import v3_contract
from validation_scripts import v3_stage_contract_flow_check as flow
from validation_scripts.tests.test_review_4943695732_contracts import Review4943695732Contracts
from validation_scripts.tests.test_stage_a_full_v3_artifact_completeness import (
    TestStageAFullV3ArtifactCompleteness,
)


class Review4943777463Contracts(unittest.TestCase):
    def full_artifact(self):
        return TestStageAFullV3ArtifactCompleteness().full_artifact()

    def validate_full(self, artifact):
        return latest.validate_full_stage_a_artifact(artifact, lineage._compat_module)

    def run_stage_a(self, artifact):
        return TestStageAFullV3ArtifactCompleteness().run_stage_a(artifact)

    def test_strict_source_story_ids_require_unique_nonblank_strings(self):
        for bad in ([None], [""], ["STORY", "STORY"]):
            with self.subTest(bad=bad):
                artifact = self.full_artifact()
                artifact["strict_passed_spec"][0]["source_story_ids"] = bad
                result, output = self.run_stage_a(artifact)
                self.assertEqual(result, 1, output)
                self.assertIn("source_story_ids", output)

    def test_needs_review_count_matches_emitted_review_partitions(self):
        artifact = self.full_artifact()
        artifact["summary"]["needs_review_count"] = 999
        messages = self.validate_full(artifact)
        self.assertTrue(
            any("needs_review_count must equal emitted review partitions" in message for message in messages),
            messages,
        )

    def test_resolution_ledger_partition_matches_review_item_partition(self):
        helper = Review4943695732Contracts()
        artifact = helper.full_artifact()
        item = helper.review_item()
        artifact["candidate_review_pool"] = [item]
        artifact["summary"]["needs_review_count"] = 1
        artifact["review_pool_resolution_ledger"] = [
            {
                "review_pool_item_id": item["review_pool_item_id"],
                "story_id": item["story_id"],
                "original_review_pool_partition": "watchlist_context_pool",
                "current_disposition": "candidate_review_pool",
                "disposition_basis": "Synthetic partition-lineage regression fixture.",
                "carry_forward_policy": item["carry_forward_policy"],
                "next_action_condition": item["next_action_condition"],
                "whether_user_authorization_required": False,
            }
        ]
        messages = self.validate_full(artifact)
        self.assertTrue(
            any("original_review_pool_partition must match emitted partition candidate_review_pool" in message for message in messages),
            messages,
        )

    def test_decision_ledger_routing_must_match_emitted_strict_disposition(self):
        artifact = self.full_artifact()
        row = artifact["decision_ledger"][0]
        row["ledger_decision"] = "rejected"
        row["editorial_bucket"] = "rejected"
        row["spec_id"] = "WRONG_SPEC"
        messages = self.validate_full(artifact)
        self.assertTrue(any("ledger_decision" in message and "contradicts emitted disposition strict_passed_spec" in message for message in messages), messages)
        self.assertTrue(any("editorial_bucket" in message and "contradicts emitted disposition strict_passed_spec" in message for message in messages), messages)
        self.assertTrue(any("spec_id must match emitted spec" in message for message in messages), messages)

    def test_execution_route_requires_materialized_empty_override_fields(self):
        contract = v3_contract.load_contract()
        required = contract["$defs"]["execution_route"]["required"]
        for field in ("structural_value_override_reason", "why_execution_event_not_required"):
            self.assertIn(field, required)
            mutated = copy.deepcopy(contract)
            mutated["$defs"]["execution_route"]["required"].remove(field)
            errors = v3_contract.validate_contract_document(mutated)
            self.assertTrue(any("materialized empty override-only fields" in error for error in errors), errors)

            package = flow.execution_route_sample()
            package.pop(field)
            flow_errors = flow.route_package_errors(package)
            self.assertIn(f"execution route missing required field {field}", flow_errors)

    def test_unhashable_execution_strength_fails_closed(self):
        for bad in ([], {}, ["strong"]):
            with self.subTest(bad=bad):
                artifact = self.full_artifact()
                artifact["strict_passed_spec"][0]["execution_anchor_strength"] = bad
                result, output = self.run_stage_a(artifact)
                self.assertEqual(result, 1, output)
                self.assertNotIn("TypeError", output)


if __name__ == "__main__":
    unittest.main()
