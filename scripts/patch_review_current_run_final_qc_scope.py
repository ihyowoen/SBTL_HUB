#!/usr/bin/env python3
from pathlib import Path

GENERATOR = Path("validation_scripts/apply_prompt_contract_overlays.py")
PROMPT = Path("docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md")
LEGACY_TEST = Path("validation_scripts/tests/test_review_4864682739_contracts.py")
TEST = Path("validation_scripts/tests/test_review_current_run_final_qc_scope.py")

OLD_EVIDENCE = "python validation_scripts/evidence_qc_v8_check.py <MERGED_BASELINE_CANDIDATE_ARTIFACT>"
NEW_EVIDENCE = OLD_EVIDENCE + " --new-id-file <CURRENT_RUN_ID_FILE>"
OLD_DATE = "python validation_scripts/date_role_freshness_check.py <MERGED_BASELINE_CANDIDATE_ARTIFACT> --require-date-role"
NEW_DATE = OLD_DATE + " --new-id-file <CURRENT_RUN_ID_FILE>"

for path in (GENERATOR, PROMPT):
    text = path.read_text(encoding="utf-8")
    if NEW_EVIDENCE not in text:
        count = text.count(OLD_EVIDENCE)
        if count != 1:
            raise SystemExit(f"{path}: expected one unscoped evidence command, found {count}")
        text = text.replace(OLD_EVIDENCE, NEW_EVIDENCE, 1)
    if NEW_DATE not in text:
        count = text.count(OLD_DATE)
        if count != 1:
            raise SystemExit(f"{path}: expected one unscoped date command, found {count}")
        text = text.replace(OLD_DATE, NEW_DATE, 1)
    path.write_text(text, encoding="utf-8")

legacy = LEGACY_TEST.read_text(encoding="utf-8")
legacy = legacy.replace(f'    "{OLD_EVIDENCE}",', f'    "{NEW_EVIDENCE}",')
legacy = legacy.replace(f'    "{OLD_DATE}",', f'    "{NEW_DATE}",')
if NEW_EVIDENCE not in legacy or NEW_DATE not in legacy:
    raise SystemExit("legacy Final QC command regression was not updated")
LEGACY_TEST.write_text(legacy, encoding="utf-8")

TEST.write_text('''from pathlib import Path\nimport unittest\n\nROOT = Path(__file__).resolve().parents[2]\nFILES = [\n    ROOT / "validation_scripts/apply_prompt_contract_overlays.py",\n    ROOT / "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md",\n]\nEVIDENCE = "python validation_scripts/evidence_qc_v8_check.py <MERGED_BASELINE_CANDIDATE_ARTIFACT> --new-id-file <CURRENT_RUN_ID_FILE>"\nDATE = "python validation_scripts/date_role_freshness_check.py <MERGED_BASELINE_CANDIDATE_ARTIFACT> --require-date-role --new-id-file <CURRENT_RUN_ID_FILE>"\n\nclass TestCurrentRunFinalQCScope(unittest.TestCase):\n    def test_evidence_and_date_checks_are_current_run_scoped(self):\n        for path in FILES:\n            text = path.read_text(encoding="utf-8")\n            self.assertEqual(text.count(EVIDENCE), 1, path)\n            self.assertEqual(text.count(DATE), 1, path)\n\n    def test_all_final_qc_validator_commands_remain_executable(self):\n        for path in FILES:\n            text = path.read_text(encoding="utf-8")\n            self.assertIn("python validation_scripts/related_lifecycle_check.py <MERGED_BASELINE_CANDIDATE_ARTIFACT> --require-contract --allow-provisional-related --new-id-file <CURRENT_RUN_ID_FILE>", text)\n            self.assertIn("python validation_scripts/stage_artifact_contract_check.py 0.7 <MERGED_BASELINE_CANDIDATE_ARTIFACT>", text)\n\nif __name__ == "__main__":\n    unittest.main()\n''', encoding="utf-8")
