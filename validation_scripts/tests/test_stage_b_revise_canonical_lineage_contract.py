#!/usr/bin/env python3
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class StageBReviseCanonicalLineageContractTest(unittest.TestCase):
    def test_revise_prompt_uses_shared_stage_a_lineage_contract(self):
        prompt = (ROOT / "docs/llm_prompts/v1/04_PROMPT_0_2R_Stage_B_Revise.md").read_text(encoding="utf-8")
        schema = (ROOT / "docs/SCHEMA_CONTRACT_STAGE_LINEAGE.md").read_text(encoding="utf-8")

        self.assertIn("Stage A `strict_gate_check`", prompt)
        self.assertIn("Stage A `spec_id`", prompt)
        self.assertIn("docs/SCHEMA_CONTRACT_STAGE_LINEAGE.md", prompt)
        self.assertIn("Do not add a revise-only prerequisite", prompt)
        self.assertNotIn("selection_risk_flags", prompt)

        stage_a_block = schema.split("## Stage A strict_passed_spec[] required lineage fields", 1)[1]
        stage_a_block = stage_a_block.split("## Stage A top-level review-pool contract fields", 1)[0]
        self.assertIn("spec_id", stage_a_block)
        self.assertIn("strict_gate_check", stage_a_block)
        self.assertNotIn("selection_risk_flags", stage_a_block)


if __name__ == "__main__":
    unittest.main()
