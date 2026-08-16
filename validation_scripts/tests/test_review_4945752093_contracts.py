from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_review_4945713246_contracts import (
    Review4945713246Contracts,
)
from validation_scripts.tests.test_stage_a_full_v3_artifact_completeness import (
    TestStageAFullV3ArtifactCompleteness,
)


class Review4945752093Contracts(unittest.TestCase):
    def full_artifact(self):
        artifact = TestStageAFullV3ArtifactCompleteness().full_artifact()
        artifact["decision_ledger"][0]["ledger_decision"] = "passed"
        return artifact

    def run_stage_a(self, artifact):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a(artifact)
        return result, stream.getvalue()

    def test_legacy_keep_rejects_non_object_rows(self):
        artifact = self.full_artifact()
        artifact["legacy_keep"] = ["not-an-object"]
        artifact["summary"]["legacy_keep_count"] = 1
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 1, output)
        self.assertIn("legacy_keep[0] must be an object", output)

    def test_remaining_unhashable_enum_operands_fail_closed(self):
        artifact = self.full_artifact()
        artifact["strict_passed_spec"][0]["strict_pass_gate"][
            "anchor_supported_by_upstream_text"
        ] = {}
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 1, output)
        self.assertIn(
            "strict_pass_gate.anchor_supported_by_upstream_text must be hashable scalar metadata before enum validation",
            output,
        )
        self.assertNotIn("TypeError", output)

        for field in ("ledger_decision", "editorial_bucket"):
            with self.subTest(field=field):
                artifact = self.full_artifact()
                artifact["decision_ledger"][0][field] = {}
                result, output = self.run_stage_a(artifact)
                self.assertEqual(result, 1, output)
                self.assertIn(
                    f"decision_ledger[0]: {field} must be hashable scalar metadata before enum validation",
                    output,
                )
                self.assertNotIn("TypeError", output)

        artifact, item, row = Review4945713246Contracts().review_artifact()
        Review4945713246Contracts.complete_resolution_row(item, row)
        row["carry_forward_policy"] = {}
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 1, output)
        self.assertIn(
            "review_pool_resolution_ledger[0]: carry_forward_policy must be hashable scalar metadata before enum validation",
            output,
        )
        self.assertNotIn("TypeError", output)

    def test_preserved_source_cluster_is_required_and_structured(self):
        artifact = self.full_artifact()
        artifact["strict_passed_spec"][0]["same_event_source_cluster"] = False
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 1, output)
        self.assertIn("same_event_source_cluster must be a non-empty array", output)

        for field in ("story_id", "url", "preserve_for_stage_b"):
            with self.subTest(field=field):
                artifact = self.full_artifact()
                row = artifact["strict_passed_spec"][0]["same_event_source_cluster"][0]
                row.pop(field)
                result, output = self.run_stage_a(artifact)
                self.assertEqual(result, 1, output)
                self.assertIn(f"same_event_source_cluster[0].{field}", output)

    def test_strict_ledger_uses_decision_vocabulary_not_editorial_bucket(self):
        artifact = self.full_artifact()
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 0, output)
        self.assertIn("PASS_STAGE_A_SCHEMA_CONTRACT", output)

        artifact = self.full_artifact()
        artifact["decision_ledger"][0]["ledger_decision"] = "strict_passed_spec"
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 1, output)
        self.assertIn(
            "ledger_decision must be passed or merged for emitted strict_passed_spec",
            output,
        )


if __name__ == "__main__":
    unittest.main()
