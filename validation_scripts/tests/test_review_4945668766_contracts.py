from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout

from validation_scripts import stage_a_full_v3_completeness_review4945668766 as latest
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_stage_a_full_v3_artifact_completeness import (
    TestStageAFullV3ArtifactCompleteness,
)
from validation_scripts.tests.test_stage_a_v3_route_alignment import (
    TestStageAV3RouteAlignment,
)


class Review4945668766Contracts(unittest.TestCase):
    def full_artifact(self):
        return TestStageAFullV3ArtifactCompleteness().full_artifact()

    def validate_full(self, artifact):
        return latest.validate_full_stage_a_artifact(artifact, lineage._compat_module)

    def test_cli_preserves_route_only_stage_a_compatibility(self):
        spec = TestStageAV3RouteAlignment().execution_spec()
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage._check_stage_a_cli({"strict_passed_spec": [spec]})
        self.assertEqual(result, 0, stream.getvalue())
        self.assertIn("PASS_STAGE_A_SCHEMA_CONTRACT", stream.getvalue())

    def test_cli_routes_recognizable_full_artifact_to_full_validation(self):
        artifact = self.full_artifact()
        artifact.pop("source_prompt_sha256")
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage._check_stage_a_cli(artifact)
        self.assertEqual(result, 1, stream.getvalue())
        self.assertIn("source_prompt_sha256", stream.getvalue())
        self.assertNotIn("RESULT: PASS_STAGE_A_SCHEMA_CONTRACT", stream.getvalue())

    def test_strict_spec_requires_stage_b_evidence_package(self):
        artifact = self.full_artifact()
        artifact["strict_passed_spec"][0]["stage_b_evidence_package_required"] = False
        messages = self.validate_full(artifact)
        self.assertTrue(
            any("stage_b_evidence_package_required must be true" in message for message in messages),
            messages,
        )

    def test_decision_ledger_v3_metadata_matches_emitted_strict_spec(self):
        mutations = {
            "decision_news_value_score": 999,
            "decision_value_breakdown": {},
            "anchor_classes": ["data_financial_anchor"],
            "structural_value_override_applied": True,
        }
        for field, value in mutations.items():
            with self.subTest(field=field):
                artifact = self.full_artifact()
                artifact["decision_ledger"][0][field] = copy.deepcopy(value)
                messages = self.validate_full(artifact)
                self.assertTrue(
                    any(
                        f"{field} must match emitted strict spec" in message
                        for message in messages
                    ),
                    messages,
                )

    def test_source_prompt_provenance_fields_are_required(self):
        fields = (
            "source_prompt_file",
            "source_prompt_sha256",
            "source_prompt_version",
            "source_prompt_authority",
            "source_prompt_provenance_status",
        )
        for field in fields:
            with self.subTest(field=field):
                artifact = self.full_artifact()
                artifact.pop(field)
                messages = self.validate_full(artifact)
                self.assertTrue(
                    any(
                        f"missing required source-prompt provenance field {field}" in message
                        for message in messages
                    ),
                    messages,
                )

    def test_source_prompt_provenance_values_fail_closed(self):
        mutations = (
            ("source_prompt_sha256", "abc", "source_prompt_sha256 must be a 64-character hexadecimal SHA-256"),
            ("source_prompt_version", "wrong-version", "source_prompt_version must be structural_default_review_pool_partition_20260506"),
            ("source_prompt_authority", "wrong-authority", "source_prompt_authority must be uploaded_or_repo_source_file_prompt"),
            ("source_prompt_provenance_status", "FAIL", "source_prompt_provenance_status must be PASS"),
        )
        for field, value, expected in mutations:
            with self.subTest(field=field):
                artifact = self.full_artifact()
                artifact[field] = value
                messages = self.validate_full(artifact)
                self.assertTrue(any(expected in message for message in messages), messages)

    def test_complete_fixture_has_no_review_4945668766_findings(self):
        messages = self.validate_full(self.full_artifact())
        review_markers = (
            "source-prompt provenance",
            "source_prompt_",
            "stage_b_evidence_package_required",
            "must match emitted strict spec",
        )
        self.assertFalse(
            any(any(marker in message for marker in review_markers) for message in messages),
            messages,
        )


if __name__ == "__main__":
    unittest.main()
