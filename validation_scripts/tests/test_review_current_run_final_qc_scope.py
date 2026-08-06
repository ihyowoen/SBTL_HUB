from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
FILES = [
    ROOT / "validation_scripts/apply_prompt_contract_overlays.py",
    ROOT / "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md",
]
EVIDENCE = "python validation_scripts/evidence_qc_v8_check.py <MERGED_BASELINE_CANDIDATE_ARTIFACT> --new-id-file <CURRENT_RUN_ID_FILE>"
DATE = "python validation_scripts/date_role_freshness_check.py <MERGED_BASELINE_CANDIDATE_ARTIFACT> --require-date-role --new-id-file <CURRENT_RUN_ID_FILE>"

class TestCurrentRunFinalQCScope(unittest.TestCase):
    def test_evidence_and_date_checks_are_current_run_scoped(self):
        for path in FILES:
            text = path.read_text(encoding="utf-8")
            self.assertEqual(text.count(EVIDENCE), 1, path)
            self.assertEqual(text.count(DATE), 1, path)

    def test_all_final_qc_validator_commands_remain_executable(self):
        for path in FILES:
            text = path.read_text(encoding="utf-8")
            self.assertIn("python validation_scripts/related_lifecycle_check.py <MERGED_BASELINE_CANDIDATE_ARTIFACT> --require-contract --allow-provisional-related --new-id-file <CURRENT_RUN_ID_FILE>", text)
            self.assertIn("python validation_scripts/stage_artifact_contract_check.py 0.7 <MERGED_BASELINE_CANDIDATE_ARTIFACT>", text)

if __name__ == "__main__":
    unittest.main()
