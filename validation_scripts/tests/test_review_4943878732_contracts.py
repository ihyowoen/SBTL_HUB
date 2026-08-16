from __future__ import annotations

import copy
import unittest

from validation_scripts import stage_a_full_v3_completeness_review4943878732 as latest
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts import v3_stage_contract_flow_check as flow
from validation_scripts.tests.test_review_4943695732_contracts import Review4943695732Contracts
from validation_scripts.tests.test_stage_a_full_v3_artifact_completeness import (
    TestStageAFullV3ArtifactCompleteness,
)


class Review4943878732Contracts(unittest.TestCase):
    def full_artifact(self):
        return TestStageAFullV3ArtifactCompleteness().full_artifact()

    def validate_full(self, artifact):
        return latest.validate_full_stage_a_artifact(artifact, lineage._compat_module)

    def run_stage_a(self, artifact):
        return TestStageAFullV3ArtifactCompleteness().run_stage_a(artifact)

    def review_artifact(self):
        helper = Review4943695732Contracts()
        artifact = helper.full_artifact()
        item = helper.review_item()
        artifact["candidate_review_pool"] = [item]
        artifact["summary"]["needs_review_count"] = 1
        row = {
            "review_pool_item_id": item["review_pool_item_id"],
            "story_id": item["story_id"],
            "original_review_pool_partition": "candidate_review_pool",
            "current_disposition": "candidate_review_pool",
            "disposition_basis": "Synthetic review-resolution regression fixture.",
            "carry_forward_policy": item["carry_forward_policy"],
            "next_action_condition": item["next_action_condition"],
            "whether_user_authorization_required": False,
        }
        artifact["review_pool_resolution_ledger"] = [row]
        artifact["review_pool_partition_summary"] = {
            "candidate_review_pool": 1,
            "watchlist_context_pool": 0,
            "reject_or_support_only_pool": 0,
        }
        artifact["review_pool_carry_forward_ledger_status"] = "PASS"
        return artifact, item, row

    def test_duplicate_review_resolution_rows_are_rejected(self):
        artifact, item, row = self.review_artifact()
        duplicate = copy.deepcopy(row)
        duplicate["current_disposition"] = "watchlist_context_pool"
        duplicate["carry_forward_policy"] = "Conflicting synthetic policy."
        artifact["review_pool_resolution_ledger"].append(duplicate)
        messages = self.validate_full(artifact)
        self.assertTrue(
            any(
                "duplicate rows for review_pool_item_id" in message
                and item["review_pool_item_id"] in message
                for message in messages
            ),
            messages,
        )
        self.assertTrue(
            any("must contain exactly one row" in message for message in messages),
            messages,
        )

    def test_empty_review_workload_requires_explicit_audit_metadata(self):
        for field in (
            "review_pool_resolution_ledger",
            "review_pool_partition_summary",
            "review_pool_carry_forward_ledger_status",
        ):
            with self.subTest(field=field):
                artifact = self.full_artifact()
                artifact.pop(field)
                result, output = self.run_stage_a(artifact)
                self.assertEqual(result, 1, output)
                self.assertIn(field, output)

    def test_legacy_review_pool_cannot_create_standalone_items(self):
        artifact, item, _ = self.review_artifact()
        artifact["candidate_review_pool"] = []
        artifact["summary"]["needs_review_count"] = 0
        artifact["review_pool_resolution_ledger"] = []
        legacy_item = copy.deepcopy(item)
        legacy_item["review_pool_partition"] = "candidate_review_pool"
        artifact["review_pool"] = [legacy_item]
        messages = self.validate_full(artifact)
        self.assertTrue(
            any("has no matching first-class review partition entry" in message for message in messages),
            messages,
        )

    def test_legacy_review_pool_must_mirror_partition_and_story_identity(self):
        artifact, item, _ = self.review_artifact()
        legacy_item = copy.deepcopy(item)
        legacy_item["review_pool_partition"] = "watchlist_context_pool"
        legacy_item["story_id"] = "WRONG_STORY"
        artifact["review_pool"] = [legacy_item]
        messages = self.validate_full(artifact)
        self.assertTrue(
            any("must mirror first-class partition candidate_review_pool" in message for message in messages),
            messages,
        )
        self.assertTrue(
            any("story identity must mirror first-class review item" in message for message in messages),
            messages,
        )

    def test_stage_flow_rejects_dual_structured_alias_pairs(self):
        package = flow.execution_route_sample()
        evidence = package["evidence_needed_for_stage_b"][0]
        evidence.update(
            {
                "source_class": "company filing",
                "verification_target": "production start date and named product model",
            }
        )
        errors = flow.route_package_errors(package)
        self.assertIn("execution route requires concrete Stage B evidence targets", errors)

        package = flow.non_execution_route_sample()
        confirmation = package["next_confirmation_points"][0]
        confirmation.update(
            {
                "confirmation_event": "first covered procurement after the effective date",
                "confirm_weaken_invalidate": "confirm or weaken the expected supplier-switching requirement",
            }
        )
        errors = flow.route_package_errors(package)
        self.assertIn("v3_non_execution route requires measurable confirmation points", errors)


if __name__ == "__main__":
    unittest.main()
