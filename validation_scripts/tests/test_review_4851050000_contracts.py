from __future__ import annotations

import copy
import unittest

from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4840844831_contracts as prior_contracts


class TestReview4851050000Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(prior_contracts.TestReview4840844831Contracts().base_spec())

    def test_bare_target_vocabulary_is_not_item_specific(self):
        for value in ("revenue", "margin", "capacity", "launch"):
            with self.subTest(value=value):
                self.assertFalse(lineage._structured_exact_target(value))

    def test_item_specific_or_qualified_targets_remain_valid(self):
        for value in (
            "Project Alpha revenue",
            "Project Alpha capacity",
            "Project Alpha 2027 revenue",
            "Project Alpha was approved",
            "Project Alpha launch date",
        ):
            with self.subTest(value=value):
                self.assertTrue(lineage._structured_exact_target(value))

    def test_complete_v3_rejects_bare_structured_evidence_and_confirmation(self):
        spec = self.base_v3_spec()
        spec["evidence_needed_for_stage_b"] = [{
            "source_or_document_class": "official filing",
            "exact_claim_or_metric": "revenue",
        }]
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "revenue",
            "interpretation_effect": "would weaken the demand outlook",
        }]
        messages = []
        self.assertFalse(lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages))

    def test_generic_follow_up_assertions_fail(self):
        for value in ("same project", "same topic", "new evidence", "follow-up"):
            with self.subTest(value=value):
                self.assertFalse(related.item_specific_lineage_assertion(value))

    def test_item_specific_follow_up_assertions_pass(self):
        for value in (
            "DOE final rule moved Project Alpha eligibility to the effective stage",
            "The August filing added a 6 GWh contracted volume versus the predecessor",
            "The judgment changed from announced target to financed execution",
        ):
            with self.subTest(value=value):
                self.assertTrue(related.item_specific_lineage_assertion(value))

    def test_final_qc_overlay_contains_executable_merged_artifact_command(self):
        expected = (
            "python validation_scripts/related_lifecycle_check.py "
            "<MERGED_BASELINE_CANDIDATE_ARTIFACT> --require-contract "
            "--allow-provisional-related --new-id-file <CURRENT_RUN_ID_FILE>"
        )
        for path in (
            "validation_scripts/apply_prompt_contract_overlays.py",
            "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md",
        ):
            with self.subTest(path=path):
                text = open(path, encoding="utf-8").read()
                self.assertIn(expected, text)


if __name__ == "__main__":
    unittest.main()
