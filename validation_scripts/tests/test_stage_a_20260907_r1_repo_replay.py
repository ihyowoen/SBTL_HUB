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
    ("stage_a_20260907_r1.xz.b64.part01", "6792ad42f53272f7054114a99c70db60bc300d1a09f9771326bb5cc3a34ea769"),
    ("stage_a_20260907_r1.xz.b64.part02", "5b15b3ae4ff97beb14aa317e4c24bf9666e97f5a44a584fa3ccc7636a15e612b"),
    ("stage_a_20260907_r1.xz.b64.part03_04", "2c1c1c3902082ef2fd5d66041815ece0d758105cde9c2f16da76677189a05167"),
    ("stage_a_20260907_r1.xz.b64.part05_06", "2417616cc01fb7025956552a4c6fef9af7a6ede04b05f4d5cb7364fd8fc45897"),
    ("stage_a_20260907_r1.xz.b64.part07_08", "bb12a26e68e8a581eeefe90087c65cf16d602285432e4cb229edb7944c7544b7"),
)
EXPECTED_SHA256 = "fb96bda5f896cb2d73e63cc76dbdb78d7d631fb547b1f919a8bc2a5a8973bd37"


class StageA20260907R1RepoReplayTest(unittest.TestCase):
    def test_exact_stage_a_r1_passes_current_full_gate(self) -> None:
        chunks: list[str] = []
        for name, expected_part_sha in PARTS:
            chunk = (FIXTURE_DIR / name).read_text(encoding="utf-8").strip()
            self.assertEqual(
                hashlib.sha256(chunk.encode("utf-8")).hexdigest(),
                expected_part_sha,
                msg=f"fixture byte mismatch: {name}",
            )
            chunks.append(chunk)

        raw = lzma.decompress(base64.b64decode("".join(chunks)))
        self.assertEqual(hashlib.sha256(raw).hexdigest(), EXPECTED_SHA256)

        data = json.loads(raw.decode("utf-8"))
        self.assertEqual(data.get("baseline_count"), 1569)
        self.assertEqual(data.get("story_count"), 263)
        self.assertEqual(data.get("event_count"), 209)
        self.assertEqual(len(data.get("strict_passed_spec", [])), 27)

        self.assertEqual(check_stage_a_full(data), 0)


if __name__ == "__main__":
    unittest.main()
