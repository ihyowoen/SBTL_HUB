from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]

class TestPR233LatestReviewContracts(unittest.TestCase):
    def test_review_pool_subtypes_are_canonical(self):
        for rel in [
            'docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md',
            'docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md',
        ]:
            text = (ROOT / rel).read_text(encoding='utf-8')
            self.assertNotIn('structural_signal_review_pool', text)
            self.assertNotIn('earnings_deep_dive_pool', text)
            self.assertIn('structural_signal_review', text)
            self.assertIn('earnings_deep_dive', text)

    def test_baseline_anchor_schema_is_format_risk_only(self):
        text = (ROOT / 'docs/llm_prompts/v1/06_PROMPT_0_4_Baseline_Revalidation.md').read_text(encoding='utf-8')
        self.assertIn('required only when the item has non-empty format_risk_tags', text)
        self.assertIn('ordinary items with no format risk must not invent this object', text)

    def test_content_polish_route_schema_is_format_risk_only(self):
        text = (ROOT / 'docs/llm_prompts/v1/08_PROMPT_0_6_Content_Polish.md').read_text(encoding='utf-8')
        self.assertIn('item with non-empty `format_risk_tags` must emit its selected path', text)
        self.assertIn('ordinary items must omit them rather than invent a route', text)

if __name__ == '__main__':
    unittest.main()
