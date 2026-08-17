import base64
import hashlib
import json
import lzma
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIX = Path(__file__).resolve().parent / "fixtures"
EXPECTED_SHA = "114420bfaccb31d48ef1ff1fa103d81f2b8ae2f60b23afbf158b26a3c19da501"


def load_exact_target():
    encoded = "".join(
        (FIX / f"early16_stage_b_target.xz.b64.{i:03d}").read_text(encoding="utf-8").strip()
        for i in range(1, 5)
    )
    raw = lzma.decompress(base64.b64decode(encoded))
    actual = hashlib.sha256(raw).hexdigest()
    if actual != EXPECTED_SHA:
        raise AssertionError(f"exact Stage B target SHA mismatch: {actual}")
    return raw


def run_validator(args, target):
    proc = subprocess.run(
        [sys.executable, *args, str(target)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if proc.returncode:
        message = (proc.stdout + "\n" + proc.stderr).replace("\n", "%0A")
        print(f"::error title=Early16 Stage B validator::{message}")
    return proc


class TestEarly16StageBArtifact(unittest.TestCase):
    def test_current_main_stage_b_contracts(self):
        raw = load_exact_target()
        payload = json.loads(raw.decode("utf-8"))
        self.assertEqual(len(payload["evidence_packages"]), 16)
        self.assertEqual(len(payload["draft_cards"]), 5)
        self.assertEqual(len(payload["draft_blocked"]), 11)
        self.assertTrue(payload["stage_b_accounting_matches_strict_passed_spec_count"])

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as fh:
            fh.write(raw)
            target = Path(fh.name)
        try:
            artifact = run_validator(
                ["validation_scripts/stage_artifact_contract_check.py", "B"], target
            )
            self.assertEqual(artifact.returncode, 0, artifact.stdout + "\n" + artifact.stderr)
            self.assertIn('"status": "PASS"', artifact.stdout)

            lineage = run_validator(
                ["validation_scripts/stage_lineage_contract_check.py", "stage_b"], target
            )
            self.assertEqual(lineage.returncode, 0, lineage.stdout + "\n" + lineage.stderr)
            self.assertIn("RESULT: PASS_STAGE_B_SCHEMA_CONTRACT", lineage.stdout)
        finally:
            target.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
