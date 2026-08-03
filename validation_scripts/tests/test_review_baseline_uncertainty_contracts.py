"""Regression coverage for the latest PR 233 baseline/uncertainty review."""

from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_review_4840844831_contracts import (
    TestReview4840844831Contracts,
)

ROOT = Path(__file__).resolve().parents[2]
FINAL_QC = ROOT / "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md"
MERGE_PREP = ROOT / "docs/llm_prompts/v1/10_PROMPT_0_8_GitHub_Merge_Prep.md"


class TestLatestBaselineUncertaintyContracts(unittest.TestCase):
    def base_spec(self):
        return TestReview4840844831Contracts().base_spec()

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def test_item_specific_baseline_change_narrative_passes(self):
        spec = self.base_spec()
        spec["baseline_expectation_changed"] = (
            "The baseline changed from optional screening to mandatory eligibility review."
        )
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 0, output)

    def test_boolean_baseline_change_is_rejected(self):
        spec = copy.deepcopy(self.base_spec())
        spec["baseline_expectation_changed"] = True
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn(
            "baseline_expectation_changed must be item-specific narrative text",
            output,
        )

    def test_placeholder_baseline_change_is_rejected(self):
        spec = copy.deepcopy(self.base_spec())
        spec["baseline_expectation_changed"] = "currently unknown"
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1)
        self.assertIn(
            "baseline_expectation_changed must be item-specific narrative text",
            output,
        )

    def test_final_qc_and_merge_prep_preserve_uncertainty_fields_by_name(self):
        final_text = FINAL_QC.read_text(encoding="utf-8")
        final_start = final_text.index(
            "For every format-risk `publish_ready[]` item with `selected_anchor_path = v3_non_execution`"
        )
        final_end = final_text.index("- evidence_complete: true", final_start)
        final_block = final_text[final_start:final_end]

        merge_text = MERGE_PREP.read_text(encoding="utf-8")
        merge_start = merge_text.index("For `selected_anchor_path: v3_non_execution`")
        merge_end = merge_text.index("If metadata is missing", merge_start)
        merge_block = merge_text[merge_start:merge_end]

        for block in (final_block, merge_block):
            self.assertIn("`uncertainty_resolved`", block)
            self.assertIn("`remaining_uncertainty`", block)
            self.assertNotIn("applicable uncertainty / probability-change fields", block)


if __name__ == "__main__":
    unittest.main()
