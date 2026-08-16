from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts import v3_contract
from validation_scripts import v3_stage_contract_flow_check as flow
from validation_scripts import v3_stage_contracts
from validation_scripts.stage_a_full_v3_completeness import (
    validate_full_stage_a_artifact,
)
from validation_scripts.tests.test_stage_a_full_v3_artifact_completeness import (
    TestStageAFullV3ArtifactCompleteness,
)


class Review4937164285Contracts(unittest.TestCase):
    def full_artifact(self):
        return TestStageAFullV3ArtifactCompleteness().full_artifact()

    def run_stage_a(self, artifact):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a(artifact)
        return result, stream.getvalue()

    def test_malformed_empty_only_metadata_returns_errors_not_typeerror(self):
        canonical = v3_contract.load_contract()
        for malformed in (None, [["structural_value_override_reason"]]):
            with self.subTest(malformed=malformed):
                broken = copy.deepcopy(canonical)
                broken["x-sbtl-contract"]["empty_only_fields_by_route"]["execution"] = malformed
                errors = v3_contract.validate_contract_document(broken)
                self.assertTrue(errors)
                self.assertTrue(
                    any("execution empty-only fields" in error for error in errors),
                    errors,
                )

    def test_flow_rejects_malformed_execution_shared_values(self):
        document = v3_stage_contracts.load_generated_stage_contract()
        mutations = (
            ("prior_state", None),
            ("changed_judgment", ""),
            ("evidence_needed_for_stage_b", [None]),
            ("anchor_classes", ["technology_commercialization_anchor"]),
        )
        for field, value in mutations:
            with self.subTest(field=field):
                package = flow.execution_route_sample()
                package[field] = value
                self.assertTrue(flow.route_package_errors(package, document))

    def test_selector_lineage_is_required_and_preserved_downstream(self):
        document = v3_stage_contracts.load_generated_stage_contract()
        package = flow.non_execution_route_sample()
        for value in (None, "BROKEN"):
            with self.subTest(value=value):
                malformed = copy.deepcopy(package)
                if value is None:
                    malformed.pop("structural_selector_policy_version")
                else:
                    malformed["structural_selector_policy_version"] = value
                self.assertTrue(flow.route_package_errors(malformed, document))

        after = copy.deepcopy(package)
        after["structural_selector_policy_version"] = "BROKEN"
        with self.assertRaisesRegex(ValueError, "STRUCTURAL_NEWS_VALUE_SELECTION_V3|mutated"):
            flow.validate_stage_handoff("stage_b", package, after, document)

        self.assertIn(
            "structural_selector_policy_version",
            document["canonical"]["route_package_preserve_fields"],
        )

    def test_legal_policy_candidates_require_complete_legal_surface(self):
        artifact = self.full_artifact()
        spec = artifact["strict_passed_spec"][0]
        spec["anchor_classes"].append("policy_regulatory_anchor")
        messages = validate_full_stage_a_artifact(artifact, lineage._compat_module)
        self.assertTrue(
            any("legal-policy candidate missing legal_policy_stage" in msg for msg in messages),
            messages,
        )
        self.assertTrue(
            any("legal-policy candidate missing competent_authority" in msg for msg in messages),
            messages,
        )

    def test_earnings_candidates_require_bounded_rescue_questions(self):
        artifact = self.full_artifact()
        spec = artifact["strict_passed_spec"][0]
        spec.update(
            {
                "earnings_deep_dive_required": True,
                "earnings_release_available": "unknown",
                "ir_deck_available": "no",
                "call_or_transcript_expected": "unknown",
                "qna_status": "not_checked_stage_a",
                "prior_period_comparison_required": True,
                "earnings_rescue_questions": [],
            }
        )
        messages = validate_full_stage_a_artifact(artifact, lineage._compat_module)
        self.assertTrue(
            any("requires non-empty item-specific earnings_rescue_questions" in msg for msg in messages),
            messages,
        )

    def test_structural_signal_review_derives_rescue_requirement_from_subtype(self):
        artifact = self.full_artifact()
        review = copy.deepcopy(artifact["strict_passed_spec"][0])
        review.pop("spec_id", None)
        review["review_pool_item_id"] = "REVIEW_STRUCTURAL_001"
        review["story_id"] = "STORY_REVIEW_001"
        review["review_pool_subtype"] = "structural_signal_review"
        review["structural_rescue_required"] = False
        review["structural_rescue_question"] = None
        artifact["candidate_review_pool"] = [review]
        messages = validate_full_stage_a_artifact(artifact, lineage._compat_module)
        self.assertTrue(
            any("structural_signal_review requires structural_rescue_required=true" in msg for msg in messages),
            messages,
        )
        self.assertTrue(
            any("structural_signal_review requires an item-specific structural_rescue_question" in msg for msg in messages),
            messages,
        )

    def test_canonical_review_pool_summary_key_names_are_required(self):
        artifact = self.full_artifact()
        summary = artifact["summary"]
        summary["structural_signal_review_ids"] = summary.pop("structural_signal_review_pool_ids")
        summary["earnings_deep_dive_ids"] = summary.pop("earnings_deep_dive_pool_ids")
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 1, output)
        self.assertIn("structural_signal_review_pool_ids must be an array", output)
        self.assertIn("earnings_deep_dive_pool_ids must be an array", output)

    def test_non_earnings_summary_may_use_not_applicable_audit_status(self):
        artifact = self.full_artifact()
        artifact["summary"]["earnings_call_qna_audit_status"] = "NOT_APPLICABLE"
        result, output = self.run_stage_a(artifact)
        self.assertEqual(result, 0, output)


if __name__ == "__main__":
    unittest.main()
