from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_stage_a_full_v3_artifact_completeness import (
    TestStageAFullV3ArtifactCompleteness,
)


class Review4945805914Contracts(unittest.TestCase):
    def full_artifact(self):
        return TestStageAFullV3ArtifactCompleteness().full_artifact()

    def run_stage_a(self, artifact):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a(artifact)
        return result, stream.getvalue()

    def test_preserved_cluster_must_cover_strict_source_story_ids(self):
        artifact = self.full_artifact()
        artifact["strict_passed_spec"][0]["same_event_source_cluster"][0][
            "story_id"
        ] = "UNRELATED"
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 1, output)
        self.assertIn(
            "same_event_source_cluster must cover every strict source_story_id",
            output,
        )

    def test_repository_source_prompt_digest_must_match_file(self):
        artifact = self.full_artifact()
        artifact["source_prompt_sha256"] = "a" * 64
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 1, output)
        self.assertIn(
            "source_prompt_sha256 must match the SHA-256 of the referenced repository source_prompt_file",
            output,
        )

    def test_strict_spec_cannot_still_need_review(self):
        artifact = self.full_artifact()
        artifact["strict_passed_spec"][0]["needs_review"] = True
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 1, output)
        self.assertIn("needs_review must be false for strict_passed_spec", output)

    def test_original_status_counts_must_match_ledger_upstream_statuses(self):
        artifact = self.full_artifact()
        artifact["original_status_counts"] = {"dropped": 1}
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 1, output)
        self.assertIn(
            "original_status_counts must exactly match decision_ledger upstream_status counts",
            output,
        )

    def test_explicit_blocked_status_prevents_stage_b_certification(self):
        artifact = self.full_artifact()
        artifact["status"] = "BLOCKED_STAGE_A_SOURCE_CLUSTER_OR_DIVERSITY_PATH_INVALID"
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 1, output)
        self.assertIn("explicit blocked status", output)
        self.assertIn("cannot be certified or routed to Stage B", output)


if __name__ == "__main__":
    unittest.main()