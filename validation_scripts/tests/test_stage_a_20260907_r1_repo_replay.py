from __future__ import annotations

import base64
import hashlib
import json
import lzma
import unittest
from pathlib import Path

from validation_scripts.stage_lineage_contract_check import check_stage_a_full

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
PARTS = (
    "stage_a_20260907_r1.xz.b64.part01",
    "stage_a_20260907_r1.xz.b64.part02",
    "stage_a_20260907_r1.xz.b64.part03_04",
    "stage_a_20260907_r1.xz.b64.part05_06",
    "stage_a_20260907_r1.xz.b64.part07_08",
)
EXPECTED_SHA256 = "fb96bda5f896cb2d73e63cc76dbdb78d7d631fb547b1f919a8bc2a5a8973bd37"


class StageA20260907R1RepoReplayTest(unittest.TestCase):
    def test_exact_stage_a_r1_passes_current_full_gate(self) -> None:
        encoded = "".join(
            (FIXTURE_DIR / name).read_text(encoding="utf-8").strip()
            for name in PARTS
        )
        raw = lzma.decompress(base64.b64decode(encoded))
        self.assertEqual(hashlib.sha256(raw).hexdigest(), EXPECTED_SHA256)

        data = json.loads(raw.decode("utf-8"))
        self.assertEqual(data.get("baseline_count"), 1569)
        self.assertEqual(data.get("story_count"), 263)
        self.assertEqual(data.get("event_count"), 209)
        self.assertEqual(len(data.get("strict_passed_spec", [])), 27)

        self.assertEqual(check_stage_a_full(data), 0)


if __name__ == "__main__":
    unittest.main()
