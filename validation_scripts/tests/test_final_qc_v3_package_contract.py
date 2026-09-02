#!/usr/bin/env python3
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
FINAL_QC = ROOT / "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md"
MERGE_PREP = ROOT / "docs/llm_prompts/v1/10_PROMPT_0_8_GitHub_Merge_Prep.md"


class FinalQcSelectionPackageContractTest(unittest.TestCase):
    def test_final_qc_preserves_integrated_selection_and_lineage_semantics(self):
        prompt = FINAL_QC.read_text(encoding="utf-8")
        for token in (
            "integrated selection route",
            "anchor classes",
            "before-after chain",
            "Related lineage",
            "current-run scope",
            "publish_ready",
            "0.7C",
        ):
            self.assertIn(token, prompt)
        self.assertNotIn("selected_anchor_path = v3_non_execution", prompt)
        self.assertNotIn("Structural Value Override", prompt)

    def test_merge_prep_requires_formal_final_and_completeness_authorization(self):
        prompt = MERGE_PREP.read_text(encoding="utf-8")
        for token in (
            "formal 0.7 publish-ready",
            "0.7C authorization",
            "insert",
            "update",
            "related_add",
            "final production IDs",
        ):
            self.assertIn(token, prompt)
        self.assertNotIn("selected_anchor_path: v3_non_execution", prompt)


if __name__ == "__main__":
    unittest.main()
