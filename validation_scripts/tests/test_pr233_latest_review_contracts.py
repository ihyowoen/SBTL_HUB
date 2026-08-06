from pathlib import Path
import unittest

from validation_scripts import related_lifecycle_check as related
from validation_scripts import stage_lineage_contract_check as stage

ROOT = Path(__file__).resolve().parents[2]


class TestPR233LatestReviewContracts(unittest.TestCase):
    """Regression coverage for the latest verified PR #233 review fixes."""

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

    def test_numbered_entity_classes_are_exact_targets(self):
        for value in (
            'Project 1 revenue',
            'Program 2 capex',
            'Facility 2 output',
        ):
            with self.subTest(value=value):
                self.assertTrue(stage._structured_exact_target(value))

        for value in ('2026 revenue', 'Q2 revenue', 'revenue 100'):
            with self.subTest(value=value):
                self.assertFalse(stage._structured_exact_target(value))

    def test_temporal_noun_modifiers_preserve_main_effect(self):
        for value in (
            'The filing after review would strengthen the current demand outlook',
            'Project Alpha after-tax profit would strengthen the current demand outlook',
        ):
            with self.subTest(value=value):
                self.assertTrue(stage._has_bound_interpretation_effect(value))

    def test_once_and_whenever_suffixes_do_not_supply_effect(self):
        for value in (
            'Project Alpha production weakened once the current demand outlook improved',
            'Project Alpha production weakened whenever the current demand outlook improved',
        ):
            with self.subTest(value=value):
                self.assertFalse(stage._has_bound_interpretation_effect(value))

    def test_generic_forecast_and_sentiment_descriptors_are_not_lineage_subjects(self):
        for value in (
            'forecast worsened',
            'sentiment improved',
            'confidence reduced',
        ):
            with self.subTest(value=value):
                self.assertFalse(related.item_specific_lineage_assertion(value))

        self.assertTrue(
            related.item_specific_lineage_assertion(
                'Project Alpha commissioning schedule improved'
            )
        )


if __name__ == '__main__':
    unittest.main()
