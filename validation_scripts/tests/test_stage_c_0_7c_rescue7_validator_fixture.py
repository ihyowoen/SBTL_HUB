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
EXPECTED_SHA256 = "becfe73d5b5ebaf687cbda1c7732f8b0c3454b879f990ce0fcbfc46db105dd34"
CHUNK_NAMES = [
    "stage_c_0_7c_rescue7_payload_00.txt",
    "stage_c_0_7c_rescue7_payload_01.txt",
    "stage_c_0_7c_rescue7_payload_02_03.txt",
    "stage_c_0_7c_rescue7_payload_04_05.txt",
    "stage_c_0_7c_rescue7_payload_06_07.txt",
    "stage_c_0_7c_rescue7_payload_08.txt",
]


def build_fixture_bytes() -> bytes:
    encoded = "".join((CHUNK_DIR / name).read_text(encoding="utf-8").strip() for name in CHUNK_NAMES)
    raw = zlib.decompress(base64.b64decode(encoded))
    actual = hashlib.sha256(raw).hexdigest()
    if actual != EXPECTED_SHA256:
        raise AssertionError(f"Stage C fixture SHA256 mismatch: expected {EXPECTED_SHA256}, got {actual}")
    return raw


class TestStageC07CRescue7ValidatorFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = build_fixture_bytes()
        cls.tmp = tempfile.TemporaryDirectory()
        cls.fixture = Path(cls.tmp.name) / "stage_c_0_7c_rescue7_r1.json"
        cls.fixture.write_bytes(raw)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "tmp"):
            cls.tmp.cleanup()

    def _run(self, *args: str):
        proc = subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(proc.returncode, 0, msg=f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
        return proc

    def test_stage_artifact_contract_check(self):
        proc = self._run("validation_scripts/stage_artifact_contract_check.py", "C", str(self.fixture))
        self.assertIn('"status": "PASS"', proc.stdout)
        self.assertIn('"missing_count": 0', proc.stdout)

    def test_stage_lineage_contract_check(self):
        proc = self._run("validation_scripts/stage_lineage_contract_check.py", "stage_c", str(self.fixture))
        self.assertIn("RESULT: PASS_STAGE_C_SCHEMA_CONTRACT", proc.stdout)


if __name__ == "__main__":
    unittest.main()
