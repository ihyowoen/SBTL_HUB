#!/usr/bin/env python3
import base64
import hashlib
import json
import lzma
from pathlib import Path
import unittest

from validation_scripts import stage_lineage_contract_check as validator

EXPECTED_SHA256 = "724c7931d95ef55f107cc36b0bc13d9913fb72b6ca0d33ec88b4e583a9f5f9cc"
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
CHUNKS = [FIXTURE_DIR / f"temp_exact10_chunk_{i:02d}.txt" for i in range(4)]


class Exact10StageAChunkedValidationTest(unittest.TestCase):
    def test_exact_stage_a_artifact_against_current_public_validator(self):
        encoded = "".join(path.read_text(encoding="utf-8").strip() for path in CHUNKS)
        raw = lzma.decompress(base64.b64decode(encoded, validate=True))
        self.assertEqual(hashlib.sha256(raw).hexdigest(), EXPECTED_SHA256)
        payload = json.loads(raw.decode("utf-8"))
        self.assertEqual(len(payload["strict_passed_spec"]), 10)
        self.assertEqual(len(payload["decision_ledger"]), 13)
        self.assertEqual(validator.check_stage_a_full(payload), 0)


if __name__ == "__main__":
    unittest.main()
