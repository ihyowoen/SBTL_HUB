from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class StructuralV3LatestReviewTests(unittest.TestCase):
    def read(self, path):
        return (ROOT / path).read_text(encoding="utf-8")

    def test_canonical_review_pools_are_subtypes(self):
        text = self.read("docs/STRUCTURAL_NEWS_VALUE_SELECTION.md")
        self.assertIn("review_pool_subtype: structural_signal_review", text)
        self.assertIn("review_pool_subtype: earnings_deep_dive", text)
        self.assertIn("prohibited as standalone top-level arrays", text)

    def test_stage_c_anchor_path_is_format_risk_only(self):
        text = self.read("docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md")
        self.assertIn("anchor_path_validation` only when the accepted item has non-empty `format_risk_tags", text)
        self.assertIn("ordinary accepted items without `format_risk_tags` must not invent", text)

    def test_stage_c_followup_accepts_v3_anchor_classes(self):
        text = self.read("docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md")
        generator = self.read("validation_scripts/apply_prompt_contract_overlays.py")
        self.assertIn("fresh_follow_up_anchor_class", text)
        self.assertIn("fresh_follow_up_anchor_class", generator)
        self.assertNotIn("`distinct_follow_up` requires a direct fresh execution anchor.", text)
        self.assertNotIn("`distinct_follow_up` requires a direct fresh execution anchor.", generator)

    def test_independent_review_uses_two_path_gate(self):
        text = self.read("docs/llm_prompts/v1/09A_PROMPT_0_7C_INDEPENDENT_COMPLETENESS_REVIEW.md")
        self.assertIn("exactly-one two-path check", text)
        self.assertIn("format_risk_anchor_path_review_complete", text)
        self.assertIn("valid fresh V3 anchor-class comparison", text)


if __name__ == "__main__":
    unittest.main()
