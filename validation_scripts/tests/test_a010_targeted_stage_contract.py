import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "validation_scripts" / "stage_lineage_contract_check.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
B = FIXTURES / "a010_stage_b_contract_fixture.json"
C = FIXTURES / "a010_stage_c_contract_fixture.json"

EXPECTED_SHA256 = {
    "stage_b": "bbd3be8e4f285bdc141ff39fbac5e13adcb2c0404e060329b46c9b2111c6fb9b",
    "stage_c": "32a3ed560e78e4c641005381c2af102c400c20a138352c02e0d09d060a3a1113",
}

class TestA010TargetedContract(unittest.TestCase):
    def _run_validator(self, stage, path):
        cp = subprocess.run(
            [sys.executable, str(VALIDATOR), stage, str(path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertIn("RESULT: PASS_", cp.stdout)

    def test_fixture_hashes_are_locked(self):
        self.assertEqual(hashlib.sha256(B.read_bytes()).hexdigest(), EXPECTED_SHA256["stage_b"])
        self.assertEqual(hashlib.sha256(C.read_bytes()).hexdigest(), EXPECTED_SHA256["stage_c"])

    def test_stage_b_contract(self):
        self._run_validator("stage_b", B)
        data = json.loads(B.read_text(encoding="utf-8"))
        self.assertEqual(data["spec_id"], "STD26_A_010")
        self.assertEqual(data["exact_stage_a_target_resolution"]["status"], "PASS_TARGET_RECOVERED")
        self.assertFalse(data["prompt_0_4_performed"])
        package = data["evidence_packages"][0]
        self.assertGreaterEqual(package["source_independent_owner_count"], 2)

    def test_stage_c_contract_and_boundary(self):
        self._run_validator("stage_c", C)
        data = json.loads(C.read_text(encoding="utf-8"))
        item = data["accepted_fact_safe"][0]
        self.assertEqual(item["spec_id"], "STD26_A_010")
        self.assertEqual(item["state"], "accepted_fact_safe")
        self.assertTrue(item["stage_c_only"])
        self.assertFalse(item["publish_ready"])
        self.assertFalse(item["addable_merge_safe"])
        self.assertTrue(item["prompt_0_4_required_later"])
        self.assertEqual(item["stage_b_lineage"]["selected_anchor_path"], "v3_non_execution")
        self.assertEqual(item["stage_b_lineage"]["anchor_classes"], ["data_financial_anchor"])

if __name__ == "__main__":
    unittest.main()
