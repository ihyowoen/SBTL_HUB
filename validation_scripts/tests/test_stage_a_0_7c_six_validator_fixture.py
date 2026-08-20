from __future__ import annotations

import base64
import hashlib
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHUNK_DIR = Path(__file__).resolve().parent / "fixtures"
EXPECTED_SHA256 = "d301af14b9c03abc013fba446e3b8e6278834340e75411badeb9a63ac504efa7"
CHUNK_NAMES = [f"stage_a_0_7c_six_payload_{index:02d}.txt" for index in range(7)]


class TestStageA07CSixValidatorFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        encoded = "".join((CHUNK_DIR / name).read_text(encoding="utf-8").strip() for name in CHUNK_NAMES)
        decoded = zlib.decompress(base64.b64decode(encoded))
        actual_sha256 = hashlib.sha256(decoded).hexdigest()
        if actual_sha256 != EXPECTED_SHA256:
            raise AssertionError(
                f"fixture SHA256 mismatch: expected {EXPECTED_SHA256}, got {actual_sha256}"
            )
        cls.tmp = tempfile.TemporaryDirectory()
        cls.fixture = Path(cls.tmp.name) / "stage_a_0_7c_six_validator_ready_r2.json"
        cls.fixture.write_bytes(decoded)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "tmp"):
            cls.tmp.cleanup()

    def _run(self, *args: str):
        proc = subprocess.run(
            [sys.executable, *args], cwd=ROOT, text=True, capture_output=True
        )
        self.assertEqual(
            proc.returncode,
            0,
            msg=f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}",
        )
        return proc

    def test_stage_artifact_contract_check(self):
        proc = self._run(
            "validation_scripts/stage_artifact_contract_check.py",
            "A",
            str(self.fixture),
        )
        self.assertIn('"status": "PASS"', proc.stdout)
        self.assertIn('"missing_count": 0', proc.stdout)

    def test_stage_lineage_contract_check(self):
        proc = self._run(
            "validation_scripts/stage_lineage_contract_check.py",
            "stage_a",
            str(self.fixture),
        )
        self.assertIn("RESULT: PASS_STAGE_A_SCHEMA_CONTRACT", proc.stdout)


if __name__ == "__main__":
    unittest.main()
