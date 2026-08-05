"""Regression coverage for review 4864682739 Final QC commands."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
TARGETS = (
    ROOT / "validation_scripts/apply_prompt_contract_overlays.py",
    ROOT / "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md",
)
COMMANDS = (
    "python validation_scripts/evidence_qc_v8_check.py <MERGED_BASELINE_CANDIDATE_ARTIFACT>",
    "python validation_scripts/related_lifecycle_check.py <MERGED_BASELINE_CANDIDATE_ARTIFACT> --require-contract --allow-provisional-related --new-id-file <CURRENT_RUN_ID_FILE>",
    "python validation_scripts/date_role_freshness_check.py <MERGED_BASELINE_CANDIDATE_ARTIFACT> --require-date-role",
    "python validation_scripts/stage_artifact_contract_check.py 0.7 <MERGED_BASELINE_CANDIDATE_ARTIFACT>",
)


class TestReview4864682739Contracts(unittest.TestCase):
    def test_every_final_qc_validator_has_python_and_required_input(self):
        for path in TARGETS:
            text = path.read_text(encoding="utf-8")
            for command in COMMANDS:
                self.assertIn(f"`{command}`", text, path)

    def test_bare_non_executable_final_qc_commands_are_absent(self):
        forbidden = (
            "`evidence_qc_v8_check.py`,",
            "`date_role_freshness_check.py --require-date-role`",
            "`stage_artifact_contract_check.py 0.7`",
        )
        for path in TARGETS:
            text = path.read_text(encoding="utf-8")
            for value in forbidden:
                self.assertNotIn(value, text, path)

    def test_generator_and_generated_prompt_keep_one_command_each(self):
        for path in TARGETS:
            text = path.read_text(encoding="utf-8")
            for command in COMMANDS:
                self.assertEqual(text.count(f"`{command}`"), 1, path)


if __name__ == "__main__":
    unittest.main()
