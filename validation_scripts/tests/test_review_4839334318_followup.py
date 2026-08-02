from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class Review4839334318FollowupTests(unittest.TestCase):
    def test_earnings_review_routes_through_candidate_pool(self):
        text = (ROOT / "docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md").read_text(encoding="utf-8")
        self.assertIn("`candidate_review_pool[]` with `review_pool_subtype: earnings_deep_dive`", text)
        self.assertNotIn("strict or `earnings_deep_dive[]`", text)

    def test_baseline_preserves_complete_v3_package(self):
        text = (ROOT / "docs/llm_prompts/v1/06_PROMPT_0_4_Baseline_Revalidation.md").read_text(encoding="utf-8")
        for field in (
            "structural_value_override_applied: true",
            "anchor_classes[]",
            "evidence_needed_for_stage_b[]",
            "why_execution_event_not_required",
            "prior_state",
            "new_verified_fact",
            "changed_judgment",
            "baseline_expectation_changed",
        ):
            self.assertIn(field, text)
        self.assertIn("selected_anchor_path = v3_non_execution", text)

    def test_execution_event_anchor_class_is_canonical(self):
        generator = (ROOT / "validation_scripts/apply_prompt_contract_overlays.py").read_text(encoding="utf-8")
        stage_c = (ROOT / "docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md").read_text(encoding="utf-8")
        self.assertIn("selected anchor class is `execution_event_anchor`", generator)
        self.assertIn("selected anchor class is `execution_event_anchor`", stage_c)
        self.assertNotIn("selected anchor class is `execution`;", generator)
        self.assertNotIn("selected anchor class is `execution`;", stage_c)


if __name__ == "__main__":
    unittest.main()
