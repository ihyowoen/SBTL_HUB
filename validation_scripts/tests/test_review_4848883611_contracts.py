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


class TestReview4848883611Contracts(unittest.TestCase):
    def base_v3_spec(self):
        return copy.deepcopy(TestReview4840844831Contracts().base_spec())

    def run_stage_a(self, spec):
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = lineage.check_stage_a({"strict_passed_spec": [spec]})
        return result, stream.getvalue()

    def test_stage_a_exit_runs_v3_lineage_validator(self):
        prompt = Path("docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md").read_text(encoding="utf-8")
        artifact = "python validation_scripts/stage_artifact_contract_check.py A"
        lineage_cmd = "python validation_scripts/stage_lineage_contract_check.py stage_a"
        self.assertIn(artifact, prompt)
        self.assertIn(lineage_cmd, prompt)
        self.assertLess(prompt.index(artifact), prompt.index(lineage_cmd))

    def test_concise_free_text_exact_metrics_are_accepted(self):
        for target in ("official revenue", "filing margin"):
            with self.subTest(target=target):
                spec = self.base_v3_spec()
                spec["evidence_needed_for_stage_b"] = [target]
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 0, output)

    def test_interpretation_effect_inflections_are_accepted(self):
        variants = (
            "would be confirmed",
            "confirmed thesis",
            "would be weakened",
            "invalidated thesis",
        )
        for effect in variants:
            with self.subTest(effect=effect):
                spec = self.base_v3_spec()
                spec["next_confirmation_points"] = [{
                    "measurable_event_or_metric": "2027 revenue",
                    "interpretation_effect": effect,
                }]
                result, output = self.run_stage_a(spec)
                self.assertEqual(result, 0, output)

    def test_complete_term_boundaries_remain_fail_closed(self):
        spec = self.base_v3_spec()
        spec["next_confirmation_points"] = [{
            "measurable_event_or_metric": "2027 revenue",
            "interpretation_effect": "unchanged thesis",
        }]
        result, output = self.run_stage_a(spec)
        self.assertEqual(result, 1, output)
        self.assertIn("next_confirmation_points entries", output)


if __name__ == "__main__":
    unittest.main()
