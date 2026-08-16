from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout

from validation_scripts import stage_a_full_v3_completeness_review4945466862 as latest
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_stage_a_full_v3_artifact_completeness import (
    TestStageAFullV3ArtifactCompleteness,
)
from validation_scripts.tests.test_stage_a_v3_route_alignment import (
    TestStageAV3RouteAlignment,
)


class Review4945466862Contracts(unittest.TestCase):
    def full_artifact(self):
        return TestStageAFullV3ArtifactCompleteness().full_artifact()

    def validate_full(self, artifact):
        return latest.validate_full_stage_a_artifact(artifact, lineage._compat_module)

    def test_route_only_public_validation_survives_but_full_entrypoint_is_fail_closed(self):
        route_only = {
            "strict_passed_spec": [
                copy.deepcopy(TestStageAV3RouteAlignment().execution_spec())
            ]
        }
        self.assertFalse(latest.looks_like_full_stage_a_artifact(route_only))

        public_stream = io.StringIO()
        with redirect_stdout(public_stream):
            public_result = lineage.check_stage_a(copy.deepcopy(route_only))
        self.assertEqual(public_result, 0, public_stream.getvalue())
        self.assertIn("PASS_STAGE_A_SCHEMA_CONTRACT", public_stream.getvalue())

        full_stream = io.StringIO()
        with redirect_stdout(full_stream):
            full_result = lineage.check_stage_a_full(copy.deepcopy(route_only))
        self.assertEqual(full_result, 1, full_stream.getvalue())
        self.assertNotIn("PASS_STAGE_A_SCHEMA_CONTRACT", full_stream.getvalue())

    def test_marker_stripped_multi_pool_artifact_still_cannot_bypass_full_validation(self):
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

        # Multiple outcome/accounting pools still identify generated Stage A
        # output, even after every historical strong marker is stripped.
        self.assertTrue(latest.looks_like_full_stage_a_artifact(artifact))
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a(artifact)
        self.assertEqual(result, 1, stream.getvalue())
        self.assertNotIn("PASS_STAGE_A_SCHEMA_CONTRACT", stream.getvalue())

    def test_every_decision_ledger_story_requires_an_emitted_disposition(self):
        artifact = self.full_artifact()
        extra = copy.deepcopy(artifact["decision_ledger"][0])
        extra["story_id"] = "LEDGER_ONLY_STORY"
        extra["spec_id"] = None
        extra["ledger_decision"] = "rejected"
        extra["editorial_bucket"] = "rejected"
        artifact["decision_ledger"].append(extra)
        artifact["story_count"] = 2
        artifact["original_status_counts"] = {"kept": 2}
        artifact["summary"]["total_ledger_count"] = 2
        artifact["summary"]["decision_ledger_count"] = 2

        messages = self.validate_full(artifact)
        self.assertTrue(
            any(
                "LEDGER_ONLY_STORY: no emitted canonical Stage A disposition"
                in message
                for message in messages
            ),
            messages,
        )

    def test_strict_candidate_requires_usable_source_url_candidates(self):
        artifact = self.full_artifact()
        spec = artifact["strict_passed_spec"][0]
        spec["primary_url"] = ""
        spec["urls"] = [""]

        messages = self.validate_full(artifact)
        self.assertTrue(
            any("primary_url must be a non-blank source URL candidate" in message for message in messages),
            messages,
        )
        self.assertTrue(
            any("urls must contain at least one non-blank source URL candidate" in message for message in messages),
            messages,
        )

    def test_explicit_legal_policy_stage_makes_legal_contract_applicable(self):
        artifact = self.full_artifact()
        spec = artifact["strict_passed_spec"][0]
        self.assertNotIn("policy_regulatory_anchor", spec["anchor_classes"])
        spec["legal_policy_stage"] = "stage_3_enacted_law_final_rule_or_adopted_standard"
        for field in latest._base_contract.LEGAL_POLICY_FIELDS:
            if field != "legal_policy_stage":
                spec.pop(field, None)

        messages = self.validate_full(artifact)
        self.assertTrue(
            any("legal-policy candidate missing legal_instrument_type" in message for message in messages),
            messages,
        )
        self.assertTrue(
            any("legal-policy candidate missing competent_authority" in message for message in messages),
            messages,
        )


if __name__ == "__main__":
    unittest.main()
