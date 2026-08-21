import base64
import gzip
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / "validation_scripts" / "tests" / "fixtures"
B64_B = FIX / "a010_stage_b_r3.json.gz.b64"
B64_C = FIX / "a010_stage_c_r1.json.gz.b64"

EXPECTED_MAIN = "75e98148ae4c7af6234799cdd0852a181b11081b"
EXPECTED_TREE = "b7cc7cd0e7c1d06191017aa3882586e0dbe8e976"
EXPECTED_B_SHA = "5e978eb4872b50fd9b21fc69b764d9e25a84aafe988cc4e06922149cd75be500"
EXPECTED_C_SHA = "24462f9a09301e41cc0beead044071464a5541b4f41ad99cbbc6e5b20020c6d8"

def raw(path):
    return gzip.decompress(base64.b64decode(path.read_text(encoding="utf-8").strip()))

def data(blob):
    return json.loads(blob.decode("utf-8"))

class A010StageBCClosure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.br = raw(B64_B)
        cls.cr = raw(B64_C)
        cls.b = data(cls.br)
        cls.c = data(cls.cr)

    def test_01_exact_materialization(self):
        self.assertEqual(hashlib.sha256(self.br).hexdigest(), EXPECTED_B_SHA)
        self.assertEqual(hashlib.sha256(self.cr).hexdigest(), EXPECTED_C_SHA)
        self.assertEqual(self.b["draft_cards"][0]["source_spec_id"], "STD26_A_010")
        self.assertEqual(self.c["accepted_fact_safe"][0]["spec_id"], "STD26_A_010")

    def test_02_main_lock(self):
        event_path = os.environ.get("GITHUB_EVENT_PATH")
        if event_path and Path(event_path).exists():
            event = json.loads(Path(event_path).read_text(encoding="utf-8"))
            pr = event.get("pull_request") or {}
            base = (pr.get("base") or {}).get("sha")
            if base:
                self.assertEqual(base, EXPECTED_MAIN)
        check = subprocess.run(
            ["git", "cat-file", "-e", f"{EXPECTED_MAIN}^{{commit}}"],
            cwd=ROOT, capture_output=True, text=True
        )
        if check.returncode != 0:
            subprocess.run(
                ["git", "fetch", "--no-tags", "--depth=1", "origin", EXPECTED_MAIN],
                cwd=ROOT, check=True
            )
        tree = subprocess.check_output(
            ["git", "rev-parse", f"{EXPECTED_MAIN}^{{tree}}"],
            cwd=ROOT, text=True
        ).strip()
        self.assertEqual(tree, EXPECTED_TREE)

    def test_03_stage_b_prompt_and_accounting(self):
        b = self.b
        self.assertEqual(b["stage"], "stage_b")
        self.assertEqual(b["stage_prompt_file"], "docs/llm_prompts/v1/02_PROMPT_0_2_Stage_B_r0.md")
        self.assertEqual(b["stage_prompt_read_gate"], "PASS")
        self.assertEqual(b["required_docs_check"]["status"], "PASS")
        self.assertEqual(len(b["required_docs_check"]["docs_read_from_github_main"]), 10)
        self.assertEqual(b["strict_passed_spec_count"], 1)
        self.assertEqual(b["drafted_count"], 1)
        self.assertEqual(b["draft_blocked_count"], 0)
        self.assertTrue(b["stage_b_accounting_matches_strict_passed_spec_count"])
        self.assertEqual(len(b["evidence_packages"]), 1)
        self.assertEqual(len(b["fetch_ledger"]), 5)

    def test_04_exact_eia_target_and_v3_route(self):
        p = self.b["evidence_packages"][0]
        t = p["exact_stage_a_target_resolution"]
        self.assertEqual(t["status"], "PASS_TARGET_RECOVERED")
        self.assertIn("Table 7a", t["official_locator"])
        self.assertIn("ELCOTWH", t["series_identity"])
        self.assertIn("4,268", t["independent_value_match"])
        d = self.b["draft_cards"][0]
        self.assertTrue(d["stage_a_lineage"]["structural_value_override_applied"])
        self.assertEqual(d["anchor_path_validation"]["selected_anchor_path"], "v3_non_execution")
        self.assertEqual(d["anchor_path_validation"]["structural_value_override_qc_status"], "pass")
        self.assertEqual(d["source_independent_owner_count"], 2)
        self.assertFalse(d["publish_ready"])

    def test_05_stage_b_generic_lineage_validator(self):
        with tempfile.NamedTemporaryFile("wb", suffix=".json", delete=False) as f:
            f.write(self.br)
            path = f.name
        try:
            subprocess.run(
                [sys.executable, str(ROOT / "validation_scripts/stage_lineage_contract_check.py"), "stage_b", path],
                cwd=ROOT, check=True
            )
        finally:
            os.unlink(path)

    def test_06_stage_c_outcome_and_boundary(self):
        c = self.c
        self.assertEqual(c["stage"], "stage_c")
        self.assertEqual(c["stage_prompt_file"], "docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md")
        self.assertEqual(c["stage_prompt_read_gate"], "PASS")
        self.assertEqual(c["accepted_fact_safe_count"], 1)
        self.assertEqual(c["revise_required_count"], 0)
        self.assertTrue(c["stage_c_accounting_matches_draft_card_count"])
        a = c["accepted_fact_safe"][0]
        self.assertEqual(a["state"], "accepted_fact_safe")
        self.assertTrue(a["stage_c_only"])
        self.assertTrue(a["strict_gate_acceptance_guard_applied"])
        self.assertEqual(a["accepted_pool_lineage_status"], "PASS")
        self.assertFalse(a["publish_ready"])
        self.assertFalse(a["addable_merge_safe"])
        self.assertFalse(a["evidence_complete"])
        self.assertFalse(c["boundary"]["prompt_0_4_or_later_performed"])
        self.assertFalse(c["boundary"]["prompt_0_8_performed"])

    def test_07_stage_c_generic_lineage_validator(self):
        with tempfile.NamedTemporaryFile("wb", suffix=".json", delete=False) as f:
            f.write(self.cr)
            path = f.name
        try:
            subprocess.run(
                [sys.executable, str(ROOT / "validation_scripts/stage_lineage_contract_check.py"), "stage_c", path],
                cwd=ROOT, check=True
            )
        finally:
            os.unlink(path)

if __name__ == "__main__":
    unittest.main()
