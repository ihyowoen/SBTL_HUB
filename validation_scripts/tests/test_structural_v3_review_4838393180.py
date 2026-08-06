import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class StructuralV3Review4838393180Tests(unittest.TestCase):
    def test_evidence_qc_early_guard_uses_exactly_one_two_path_contract(self) -> None:
        text = (ROOT / "docs/llm_prompts/v1/07_PROMPT_0_5_Evidence_QC.md").read_text(encoding="utf-8")
        self.assertIn("exactly one supported anchor path", text)
        self.assertIn("`v3_non_execution`", text)
        self.assertIn("A complete V3 non-execution route must not be held solely", text)
        self.assertNotIn(
            "then evidence QC must confirm body-level or official evidence for at least one concrete execution anchor",
            text,
        )
        self.assertNotIn("reason execution_anchor_not_evidenced", text)

    def test_retrospective_uses_ten_required_docs_everywhere_reviewed(self) -> None:
        text = (ROOT / "docs/llm_prompts/v1/13_PROMPT_1_1_Retrospective.md").read_text(encoding="utf-8")
        self.assertIn("- Were all 10 docs read from GitHub main?", text)
        self.assertIn("   - list all 10 required docs", text)
        self.assertNotIn("Were all 8 docs read", text)
        self.assertNotIn("list all 8 required docs", text)

    def test_temporary_patch_machinery_is_removed(self) -> None:
        self.assertFalse((ROOT / "scripts/patch_structural_v3_review_4838393180.py").exists())
        self.assertFalse((ROOT / ".github/workflows/patch-review-4838393180.yml").exists())


if __name__ == "__main__":
    unittest.main()
