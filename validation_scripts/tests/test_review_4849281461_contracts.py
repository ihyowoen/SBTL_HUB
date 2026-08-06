from __future__ import annotations

import copy
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from validation_scripts import stage_lineage_contract_check as lineage
from validation_scripts.tests.test_review_4840844831_contracts import (
    TestReview4840844831Contracts,
)


class TestReview4849281461Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(TestReview4840844831Contracts().base_spec())

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def test_stage_a_exit_commands_are_valid_markdown(self):
        expected = (
            "  `python validation_scripts/stage_lineage_contract_check.py "
            "stage_a <STAGE_A_JSON>`."
        )
        malformed = (
            "\npython validation_scripts/stage_lineage_contract_check.py "
            "stage_a <STAGE_A_JSON>`."
        )
        for path in (
            Path("validation_scripts/apply_prompt_contract_overlays.py"),
            Path("docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md"),
        ):
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertIn(expected, text)
                self.assertNotIn(malformed, text)

    def test_specific_confirmation_with_generic_substring_passes(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [
            "Publication of additional data center capacity for Project Alpha would confirm adoption"
        ]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 0, output)

    def test_placeholder_only_confirmation_still_fails(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = ["more evidence on adoption"]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1, output)
        self.assertIn("measurable events or metrics", output)


if __name__ == "__main__":
    unittest.main()
