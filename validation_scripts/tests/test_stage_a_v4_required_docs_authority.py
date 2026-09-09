from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_stage_a_full_v3_artifact_completeness import (
    TestStageAFullV3ArtifactCompleteness,
)


RETIRED_V3_AUTHORITY = {
    "docs/STRUCTURAL_NEWS_VALUE_SELECTION.md",
    "docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md",
    "docs/PROMPT_ABC_SUPPORTING_RULES.md",
}


class StageAV4RequiredDocsAuthorityTest(unittest.TestCase):
    def active_full_artifact(self):
        artifact = TestStageAFullV3ArtifactCompleteness().full_artifact()
        spec = artifact["strict_passed_spec"][0]
        spec.update(
            {
                "selection_policy_version": "EMBEDDED_NEWS_VALUE_SELECTION_V4",
                "selection_route": "execution_anchor_route",
                "systemic_scale_denominator": (
                    "Synthetic named-program denominator used only for Stage A contract regression."
                ),
                "denominator_gap": None,
                "technology_evidence_level": "independent_test_or_customer_qualification",
                "policy_stage": None,
                "novelty_cap_basis": "none",
                "related_prepass": {
                    "status": "PASS",
                    "same_event_checked": True,
                    "matched_baseline_candidate_ids": [],
                    "matched_current_batch_candidate_ids": [],
                    "relation_candidates": [],
                    "duplicate_disposition": "no_duplicate_found",
                    "earliest_same_event_check_status": "PASS",
                    "fresh_anchor_questions": [
                        "Confirm whether any baseline card represents the same event before Stage B."
                    ],
                },
                "structural_non_execution_reason": None,
                "why_execution_event_not_required": None,
            }
        )
        artifact["source_prompt_version"] = "STAGE_A_INTEGRATED_SELECTOR_V4_20260901"
        artifact["run_tag"] = "SYNTHETIC_V4_ACTIVE_AUTHORITY"
        artifact["run_label"] = "Synthetic Stage A V4 active-authority artifact"

        active, nonoperative, mandatory, messages = lineage._load_registry_authority()
        self.assertEqual(messages, [])
        self.assertTrue(set(mandatory).issubset(active))
        self.assertTrue(RETIRED_V3_AUTHORITY.issubset(nonoperative))
        self.assertTrue(RETIRED_V3_AUTHORITY.isdisjoint(mandatory))
        artifact["required_docs_check"] = {
            "docs_expected": list(mandatory),
            "docs_read_from_github_main": list(mandatory),
            "docs_missing_or_unreadable": [],
            "status": "PASS",
        }
        # Keep the compatibility ledger aligned with the strict item for fields
        # the historical completeness chain may reconcile.
        artifact["decision_ledger"][0]["denominator_gap"] = None
        return artifact

    def run_active(self, artifact, *, full=False):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = (
                lineage.check_stage_a_full(artifact)
                if full
                else lineage.check_stage_a(artifact)
            )
        return result, stream.getvalue()

    def test_v4_full_artifact_passes_without_retired_v3_authority(self):
        artifact = self.active_full_artifact()
        original = copy.deepcopy(artifact)
        result, output = self.run_active(artifact, full=True)
        self.assertEqual(result, 0, output)
        self.assertIn("PASS_STAGE_A_SCHEMA_CONTRACT", output)
        self.assertEqual(artifact, original, "active validator must not mutate emitted artifact")
        for field in ("docs_expected", "docs_read_from_github_main"):
            self.assertTrue(
                RETIRED_V3_AUTHORITY.isdisjoint(artifact["required_docs_check"][field])
            )

    def test_public_active_entrypoint_also_passes_clean_full_artifact(self):
        artifact = self.active_full_artifact()
        result, output = self.run_active(artifact)
        self.assertEqual(result, 0, output)
        self.assertIn("PASS_STAGE_A_SCHEMA_CONTRACT", output)

    def test_retired_v3_policy_cannot_be_claimed_as_active_authority(self):
        for retired in sorted(RETIRED_V3_AUTHORITY):
            with self.subTest(retired=retired):
                artifact = self.active_full_artifact()
                artifact["required_docs_check"]["docs_expected"].append(retired)
                artifact["required_docs_check"]["docs_read_from_github_main"].append(retired)
                result, output = self.run_active(artifact, full=True)
                self.assertEqual(result, 1)
                self.assertIn("cannot claim superseded/reference authority", output)
                self.assertIn(retired, output)

    def test_missing_current_active_mandatory_doc_fails_closed(self):
        artifact = self.active_full_artifact()
        missing = artifact["required_docs_check"]["docs_expected"].pop()
        artifact["required_docs_check"]["docs_read_from_github_main"].remove(missing)
        result, output = self.run_active(artifact, full=True)
        self.assertEqual(result, 1)
        self.assertIn("missing active mandatory documents", output)
        self.assertIn(missing, output)

    def test_private_v3_projection_is_non_mutating_and_not_authority(self):
        artifact = self.active_full_artifact()
        original = copy.deepcopy(artifact)
        projected = lineage._project_full_stage_a_for_v3_compat(artifact)
        self.assertEqual(artifact, original)
        self.assertIsNot(projected, artifact)
        for field in ("docs_expected", "docs_read_from_github_main"):
            self.assertTrue(
                RETIRED_V3_AUTHORITY.issubset(projected["required_docs_check"][field])
            )
            self.assertTrue(
                RETIRED_V3_AUTHORITY.isdisjoint(artifact["required_docs_check"][field])
            )

    def test_explicit_historical_v3_lane_preserves_original_fixture(self):
        artifact = TestStageAFullV3ArtifactCompleteness().full_artifact()
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a_full_v3_compat(copy.deepcopy(artifact))
        self.assertEqual(result, 0, stream.getvalue())
        self.assertIn("PASS_STAGE_A_SCHEMA_CONTRACT", stream.getvalue())


if __name__ == "__main__":
    unittest.main()
