#!/usr/bin/env python3
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class Review4838187744ContractTest(unittest.TestCase):
    @staticmethod
    def read(path: str) -> str:
        return (ROOT / path).read_text(encoding="utf-8")

    def test_final_qc_emits_merge_prep_route_fields(self):
        text = self.read("docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md")
        self.assertIn("For every format-risk `publish_ready[]` item", text)
        for field in (
            "selected_anchor_path: execution|v3_non_execution",
            "anchor_path_qc_passed: true",
            "execution_anchor_qc_status: pass|not_applicable",
            "structural_value_override_qc_status: pass|not_applicable",
            "non_applicable_anchor_path_reason",
        ):
            self.assertIn(field, text)

    def test_revise_loop_carries_anchor_path_validation(self):
        stage_b_revise = self.read("docs/llm_prompts/v1/04_PROMPT_0_2R_Stage_B_Revise.md")
        stage_c_revise = self.read("docs/llm_prompts/v1/05_PROMPT_0_3R_Stage_C_Revise.md")
        for text in (stage_b_revise, stage_c_revise):
            self.assertIn("All 10 documents above are mandatory.", text)
            self.assertIn("anchor_path_validation", text)
            self.assertNotIn("All 8 documents above are mandatory.", text)
        self.assertIn("resolved_from_unresolved", stage_b_revise)
        self.assertIn("accepted_with_v3_non_execution_path_count", stage_c_revise)

    def test_stage_c_uses_anchor_classes_array(self):
        text = self.read("docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md")
        self.assertIn("`anchor_classes[]` containing at least one valid non-execution anchor class", text)
        self.assertNotIn("one valid non-execution `anchor_class`", text)

    def test_retrospective_recognizes_v3_override(self):
        text = self.read("docs/llm_prompts/v1/13_PROMPT_1_1_Retrospective.md")
        self.assertIn("complete V3 non-execution Structural Value Override package", text)
        self.assertNotIn("without a hard commercial/policy event", text)
        self.assertNotIn("unless a concrete battery/grid/ESS/EV/materials execution anchor is present", text)


if __name__ == "__main__":
    unittest.main()
