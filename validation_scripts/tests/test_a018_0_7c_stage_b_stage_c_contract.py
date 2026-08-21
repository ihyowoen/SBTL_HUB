import hashlib, json, subprocess, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "validation_scripts" / "stage_lineage_contract_check.py"
FIX = Path(__file__).resolve().parent / "fixtures"
B = FIX / "a018_stage_b_contract_fixture.json"
C = FIX / "a018_stage_c_contract_fixture.json"

EXPECTED_B_SHA256 = "c4a77a9b49b5978c97fdad52bc613b4ac2f93f8f18e4e785d1a629ae028ddea4"
EXPECTED_C_SHA256 = "7f66f52f9ef985433d18ee4d88a15b602a19160971ad23ddafc5cd25f5c6e2a1"

class TestA018TargetedContract(unittest.TestCase):
    def _run(self, stage, path):
        cp = subprocess.run([sys.executable, str(VALIDATOR), stage, str(path)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertIn("RESULT: PASS_", cp.stdout)

    def test_01_fixture_hashes_are_locked(self):
        self.assertEqual(hashlib.sha256(B.read_bytes()).hexdigest(), EXPECTED_B_SHA256)
        self.assertEqual(hashlib.sha256(C.read_bytes()).hexdigest(), EXPECTED_C_SHA256)

    def test_02_stage_b_contract(self):
        self._run("stage_b", B)
        data = json.loads(B.read_text(encoding="utf-8"))
        self.assertEqual(data["spec_id"], "STD26_A_018")
        self.assertEqual(data["exact_stage_a_target_resolution"]["status"], "PASS_COMPOSITE_EXACT_TARGET_RECOVERED")
        self.assertFalse(data["prompt_0_4_performed"])
        package = data["evidence_packages"][0]
        self.assertGreaterEqual(package["source_independent_owner_count"], 2)
        self.assertIn("official_operating_stage", package["source_role_coverage"])
        self.assertIn("official_project_scope", package["source_role_coverage"])

    def test_03_stage_c_contract_and_boundary(self):
        self._run("stage_c", C)
        item = json.loads(C.read_text(encoding="utf-8"))["accepted_fact_safe"][0]
        self.assertEqual(item["spec_id"], "STD26_A_018")
        self.assertEqual(item["state"], "accepted_fact_safe")
        self.assertTrue(item["stage_c_only"])
        self.assertFalse(item["publish_ready"])
        self.assertFalse(item["addable_merge_safe"])
        self.assertTrue(item["prompt_0_4_required_later"])
        self.assertEqual(item["stage_b_lineage"]["selected_anchor_path"], "execution")
        self.assertEqual(item["stage_b_lineage"]["anchor_classes"], ["execution_event_anchor"])

if __name__ == "__main__":
    unittest.main()
