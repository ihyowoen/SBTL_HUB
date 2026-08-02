#!/usr/bin/env python3
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class Review4838372817ContractTest(unittest.TestCase):
    @staticmethod
    def read(relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_stage_b_revise_accepts_second_and_later_loop_state(self):
        text = self.read("docs/llm_prompts/v1/04_PROMPT_0_2R_Stage_B_Revise.md")
        self.assertIn("revision pass `r1`: the immediately previous Stage C `revise_required[]`", text)
        self.assertIn("revision pass `r2` or later: the immediately previous Stage C revise `revise_required_again[]`", text)
        self.assertIn("If `REVISION_PASS = r2` or later", text)
        self.assertIn("Do not mix `revise_required[]` and `revise_required_again[]`", text)
        self.assertIn("revise_input_state: revise_required|revise_required_again", text)
        self.assertIn("accounting_matches_revise_required_again_input_count", text)
        self.assertNotIn("Only previous Stage C revise_required[] may enter this Stage B revise pass.", text)

    def test_retrospective_reads_v3_governing_contracts(self):
        text = self.read("docs/llm_prompts/v1/13_PROMPT_1_1_Retrospective.md")
        self.assertIn("docs/STRUCTURAL_NEWS_VALUE_SELECTION.md", text)
        self.assertIn("docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md", text)
        self.assertIn("All 10 documents above are mandatory.", text)
        self.assertNotIn("All 8 documents above are mandatory.", text)


if __name__ == "__main__":
    unittest.main()
