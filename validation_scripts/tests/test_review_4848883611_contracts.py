from __future__ import annotations

import copy
import unittest
from pathlib import Path

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests import test_review_4840844831_contracts as prior_contracts


class TestReview4848883611Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(prior_contracts.TestReview4840844831Contracts().base_spec())

    def test_stage_a_exit_commands_are_valid_markdown(self):
        expected = "  `python validation_scripts/stage_lineage_contract_check.py stage_a <STAGE_A_JSON>`."
        for path in (
            "validation_scripts/apply_prompt_contract_overlays.py",
            "docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md",
        ):
            text = Path(path).read_text(encoding="utf-8")
            self.assertIn(expected, text)
            self.assertNotIn("  ``python validation_scripts/stage_lineage_contract_check.py", text)

    def test_specific_confirmation_with_additional_data_substring_passes(self):
        value = "Publication of additional data center capacity for Project Alpha would confirm adoption"
        self.assertTrue(lineage._valid_confirmation_point(value))

    def test_existing_metric_confirmation_remains_valid(self):
        value = "Publication of implementing guidance with the final effective date would confirm the eligibility change"
        self.assertTrue(lineage._valid_confirmation_point(value))

    def test_generic_confirmation_scaffolds_still_fail(self):
        for value in (
            "additional data needed to confirm adoption",
            "more evidence required for approval",
            "confirmation needed for production",
        ):
            with self.subTest(value=value):
                self.assertFalse(lineage._valid_confirmation_point(value))

    def test_confirmation_requires_measurable_event_or_metric(self):
        self.assertFalse(lineage._valid_confirmation_point("Project Alpha would confirm the thesis"))
        self.assertFalse(lineage._valid_confirmation_point("General commentary may become available later"))

    def test_complete_v3_spec_accepts_specific_confirmation_text(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [
            "Publication of additional data center capacity for Project Alpha would confirm adoption"
        ]
        messages = []
        self.assertTrue(lineage.validate_stage_a_v3_override(spec, spec["spec_id"], messages), messages)
        self.assertEqual(messages, [])


if __name__ == "__main__":
    unittest.main()
