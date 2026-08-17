import base64
import gzip
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / "validation_scripts" / "tests" / "fixtures"
EXPECTED_SHA = "fe6154824fa99a09755e4c2b3efe342abaa4043438adf2a91d3853e0d55a1cca"


class TestEarly16StageAArtifact(unittest.TestCase):
    def test_current_main_stage_lineage_validator(self):
        encoded = "".join(
            (FIX / f"early16_stage_a_target.b64.{i:03d}").read_text(encoding="utf-8").strip()
            for i in range(1, 5)
        )
        raw = gzip.decompress(base64.b64decode(encoded))
        self.assertEqual(hashlib.sha256(raw).hexdigest(), EXPECTED_SHA)
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as fh:
            fh.write(raw)
            target = Path(fh.name)
        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    "validation_scripts/stage_lineage_contract_check.py",
                    "stage_a",
                    str(target),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + "\n" + proc.stderr)
            self.assertIn("RESULT: PASS_STAGE_A_SCHEMA_CONTRACT", proc.stdout)
        finally:
            target.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
