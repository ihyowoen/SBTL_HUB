from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout

from validation_scripts import stage_a_full_v3_completeness_review4945713246 as latest
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_review_4943878732_contracts import (
    Review4943878732Contracts,
)
from validation_scripts.tests.test_stage_a_full_v3_artifact_completeness import (
    TestStageAFullV3ArtifactCompleteness,
)


class Review4945713246Contracts(unittest.TestCase):
    def full_artifact(self):
        return TestStageAFullV3ArtifactCompleteness().full_artifact()

    def review_artifact(self):
        return Review4943878732Contracts().review_artifact()

    def validate_full(self, artifact):
        return latest.validate_full_stage_a_artifact(artifact, lineage._compat_module)

    def run_stage_a(self, artifact):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a(artifact)
        return result, stream.getvalue()

    @staticmethod
    def complete_resolution_row(item, row):
        row["upstream_status"] = item["upstream_status"]
        row["final_review_pool_disposition"] = item["final_review_pool_disposition"]
        row["reviewed_by_stage_or_pass"] = "Stage A bounded review regression pass"
        row["review_artifact_id"] = "SYNTHETIC_REVIEW_ARTIFACT_001"
        row["carry_forward_policy"] = "needs_user_decision"

    def test_review_resolution_requires_extended_audit_contract(self):
        artifact, item, row = self.review_artifact()
        messages = self.validate_full(artifact)
        for field in (
            "upstream_status",
            "final_review_pool_disposition",
            "reviewed_by_stage_or_pass",
            "review_artifact_id",
        ):
            with self.subTest(field=field):
                self.assertTrue(
                    any(f"missing required review-resolution field {field}" in message for message in messages),
                    messages,
                )
        self.assertTrue(
            any("carry_forward_policy must be one of the documented review-resolution policies" in message for message in messages),
            messages,
        )

        artifact, item, row = self.review_artifact()
        self.complete_resolution_row(item, row)
        messages = self.validate_full(artifact)
        markers = (
            "missing required review-resolution field upstream_status",
            "missing required review-resolution field final_review_pool_disposition",
            "missing required review-resolution field reviewed_by_stage_or_pass",
            "missing required review-resolution field review_artifact_id",
            "carry_forward_policy must be one of the documented review-resolution policies",
            "final_review_pool_disposition must match emitted review item",
            "upstream_status must match emitted review item",
        )
        self.assertFalse(
            any(any(marker in message for marker in markers) for message in messages),
            messages,
        )

    def test_review_resolution_disposition_must_match_emitted_item(self):
        artifact, item, row = self.review_artifact()
        self.complete_resolution_row(item, row)
        row["final_review_pool_disposition"] = "watchlist_only_after_review"
        messages = self.validate_full(artifact)
        self.assertTrue(
            any("final_review_pool_disposition must match emitted review item" in message for message in messages),
            messages,
        )

    def test_legacy_keep_is_a_canonical_ledger_disposition(self):
        artifact = self.full_artifact()
        legacy_story_id = "LEGACY_KEEP_STORY_001"
        artifact["legacy_keep"] = [
            {
                "story_id": legacy_story_id,
                "notes": "Synthetic legacy-keep regression fixture.",
            }
        ]
        legacy_row = copy.deepcopy(artifact["decision_ledger"][0])
        legacy_row.update(
            {
                "story_id": legacy_story_id,
                "ledger_decision": "passed",
                "editorial_bucket": "legacy_keep",
                "spec_id": None,
                "merged_into_spec_id": None,
                "reason": "Existing accepted legacy item remains in the legacy_keep editorial bucket.",
            }
        )
        artifact["decision_ledger"].append(legacy_row)
        artifact["story_count"] = 2
        artifact["original_status_counts"] = {"kept": 2}
        artifact["summary"]["legacy_keep_count"] = 1
        artifact["summary"]["total_ledger_count"] = 2
        artifact["summary"]["decision_ledger_count"] = 2

        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 0, output)
        self.assertIn("PASS_STAGE_A_SCHEMA_CONTRACT", output)

        artifact["decision_ledger"][1]["ledger_decision"] = "legacy_keep"
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 1, output)
        self.assertIn("ledger_decision must be passed or merged for emitted legacy_keep", output)

    def test_legacy_keep_cannot_overlap_another_disposition(self):
        artifact = self.full_artifact()
        strict_story_id = artifact["strict_passed_spec"][0]["source_story_ids"][0]
        artifact["legacy_keep"] = [{"story_id": strict_story_id}]
        artifact["summary"]["legacy_keep_count"] = 1
        messages = self.validate_full(artifact)
        self.assertTrue(
            any("legacy_keep overlaps strict_passed_spec" in message for message in messages),
            messages,
        )

    def test_unhashable_review_gate_enums_fail_closed_before_membership(self):
        mutations = (
            ("execution_credibility_gate", "status"),
            ("independent_cardability_gate", "status"),
            ("independent_cardability_gate", "full_schema_viability"),
        )
        for gate_name, field in mutations:
            with self.subTest(field=f"{gate_name}.{field}"):
                artifact, item, row = self.review_artifact()
                self.complete_resolution_row(item, row)
                item[gate_name][field] = {}
                result, output = self.run_stage_a(artifact)
                self.assertEqual(result, 1, output)
                self.assertIn(
                    f"{gate_name}.{field} must be hashable scalar metadata before enum validation",
                    output,
                )
                self.assertNotIn("TypeError", output)

    def test_strict_pass_requires_upstream_anchor_support(self):
        artifact = self.full_artifact()
        artifact["strict_passed_spec"][0]["strict_pass_gate"]["anchor_supported_by_upstream_text"] = False
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 1, output)
        self.assertIn(
            "strict_pass_gate.anchor_supported_by_upstream_text must be true for strict_passed_spec",
            output,
        )


if __name__ == "__main__":
    unittest.main()
