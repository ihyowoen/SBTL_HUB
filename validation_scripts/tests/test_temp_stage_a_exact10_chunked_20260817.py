#!/usr/bin/env python3
import base64
import hashlib
import json
import lzma
from pathlib import Path
import unittest

from validation_scripts import stage_lineage_contract_check as validator

EXPECTED_ARTIFACT_SHA256 = "724c7931d95ef55f107cc36b0bc13d9913fb72b6ca0d33ec88b4e583a9f5f9cc"
EXPECTED_ENCODED_SHA256 = "058d13fe9c8ee35e59436a10738b3f59435cfa25629b9f58f9b024c49ba361b8"
EXPECTED_ENCODED_LENGTH = 28524
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
FIXTURES = [
    ("temp_exact10_good_00.txt", "91baf2236789209272ba53c2f595396d49d37e43650866578357781864bbeeb8"),
    ("temp_exact10_good_01.txt", "4c004e9a9b80dea8f18028406ef508d8f398727b9dbb4c356866f676b031bb2a"),
    ("temp_exact10_good_02.txt", "88e08db167de472738963abdf66c9533bbf1673c953d462ffd209809656430b2a"),
    ("temp_exact10_good_03.txt", "4a69c07092fbbd4476c2588fff39080cbb392269f40e1f5389e3dc44f32492e3"),
    ("temp_exact10_good_tail_a.txt", "a0dc8442dd09afd82f98d4dff3ccbdb0841317b72e7c286124406e1bfe61f0f7"),
    ("temp_exact10_good_tail_b.txt", "5a19112ca63decb76d19084ed2571926310068eb7460c94f5106b6eec64aace1"),
]


class Exact10StageAChunkedValidationTest(unittest.TestCase):
    def test_exact_stage_a_artifact_against_current_public_validator(self):
        chunks = []
        for filename, expected_sha in FIXTURES:
            text = (FIXTURE_DIR / filename).read_text(encoding="utf-8")
            self.assertEqual(hashlib.sha256(text.encode("utf-8")).hexdigest(), expected_sha, filename)
            chunks.append(text)

        encoded = "".join(chunks)
        self.assertEqual(len(encoded), EXPECTED_ENCODED_LENGTH)
        self.assertEqual(hashlib.sha256(encoded.encode("utf-8")).hexdigest(), EXPECTED_ENCODED_SHA256)

        raw = lzma.decompress(base64.b64decode(encoded, validate=True))
        self.assertEqual(hashlib.sha256(raw).hexdigest(), EXPECTED_ARTIFACT_SHA256)
        payload = json.loads(raw.decode("utf-8"))
        self.assertEqual(len(payload["strict_passed_spec"]), 10)
        self.assertEqual(len(payload["decision_ledger"]), 13)
        self.assertEqual(validator.check_stage_a_full(payload), 0)


if __name__ == "__main__":
    unittest.main()
