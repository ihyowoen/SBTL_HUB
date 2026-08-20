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
EXPECTED_SHA256 = "11124ad00699d0c5c996693b7bf82059ff53f0e51f110c69af5d751b190f1dbc"
CHUNK_NAMES = [
    "stage_b_0_7c_six_payload_00.txt",
    "stage_b_0_7c_six_payload_01.txt",
    "stage_b_0_7c_six_payload_02.txt",
    "stage_b_0_7c_six_payload_03.txt",
    "stage_b_0_7c_six_payload_04.txt",
    "stage_b_0_7c_six_payload_05a.txt",
    "stage_b_0_7c_six_payload_05b.txt",
    "stage_b_0_7c_six_payload_06.txt",
    "stage_b_0_7c_six_payload_07.txt",
]


class TestStageB07CSixValidatorFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        encoded = "".join(
            (CHUNK_DIR / name).read_text(encoding="utf-8").strip()
            for name in CHUNK_NAMES
        )
        payload = zlib.decompress(base64.b64decode(encoded))
        actual_sha = hashlib.sha256(payload).hexdigest()
        if actual_sha != EXPECTED_SHA256:
            raise AssertionError(
                f"Stage B fixture SHA256 mismatch: expected {EXPECTED_SHA256}, got {actual_sha}"
            )
        cls.tmp = tempfile.TemporaryDirectory()
        cls.fixture = Path(cls.tmp.name) / "stage_b_0_7c_six_r1.json"
        cls.fixture.write_bytes(payload)

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
            "B",
            str(self.fixture),
        )
        self.assertIn('"status": "PASS"', proc.stdout)
        self.assertIn('"missing_count": 0', proc.stdout)

    def test_stage_lineage_contract_check(self):
        proc = self._run(
            "validation_scripts/stage_lineage_contract_check.py",
            "stage_b",
            str(self.fixture),
        )
        self.assertIn("RESULT: PASS_STAGE_B_SCHEMA_CONTRACT", proc.stdout)


if __name__ == "__main__":
    unittest.main()
