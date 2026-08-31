#!/usr/bin/env python3
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
REVISE = ROOT / "docs/llm_prompts/v1/04_PROMPT_0_2R_Stage_B_Revise.md"
SCHEMA = ROOT / "docs/SCHEMA_CONTRACT_STAGE_LINEAGE.md"
WORKFLOW = ROOT / "docs/WORKFLOW.md"


class StageBReviseCanonicalLineageContractTest(unittest.TestCase):
    def test_revise_prompt_preserves_integrated_selection_and_related_questions(self):
        prompt = REVISE.read_text(encoding="utf-8")
        self.assertIn("Preserve integrated selection package", prompt)
        self.assertIn("Related questions", prompt)
        self.assertIn("selection/staleness/event-identity defects return", prompt)
        self.assertNotIn("revise-only prerequisite", prompt)

    def test_stage_lineage_schema_owns_v4_stage_a_lineage(self):
        schema = SCHEMA.read_text(encoding="utf-8")
        stage_a = schema.split("## 3. Stage A strict lineage", 1)[1].split("## 4. Stage B lineage", 1)[0]
        for token in (
            "selection_policy_version = EMBEDDED_NEWS_VALUE_SELECTION_V4",
            "selection_route",
            "decision-news-value score",
            "related_prepass",
            "Stage B evidence targets",
            "next confirmation points",
        ):
            self.assertIn(token, stage_a)

    def test_workflow_keeps_02r_conditional_not_mandatory(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("0.2R and 0.3R are **conditional repair loops**", workflow)
        self.assertIn("B-owned evidence/date/source/draft defect → 0.2R", workflow)


if __name__ == "__main__":
    unittest.main()
