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
    ("stage_a_20260907_r1.xz.b64.part01_01", "9ecb45dce55cb3fc6058d55c0da69d8c519c5e99104d859b2b7c08c150da48f9"),
    ("stage_a_20260907_r1.xz.b64.part01_02", "d4c5c54daba97e4bb14033c17c9a126696c421ed7e7df3e7249e7fb7cc3dd6fb"),
    ("stage_a_20260907_r1.xz.b64.part01_03", "0d46f5848a08cc2d6215a0a4f64a9ff4bf583c5ae5960f70baf5af7ad15d8082"),
    ("stage_a_20260907_r1.xz.b64.part01_04", "4f33d47ce310c825eabdfb711043672a207f1d3a456bff25171f9b9a25b22012"),
    ("stage_a_20260907_r1.xz.b64.part01_05", "2e392a9812a0266576b95a1b1bcee6a1b481c00cb470762718188b9f10511d3f"),
    ("stage_a_20260907_r1.xz.b64.part01_06", "d95a2b813c14d2714bb7c9f7fcdea5a9ad1e4141b9ba0fc6591102b5b7e4ad48"),
    ("stage_a_20260907_r1.xz.b64.part01_07", "ce9b2bb8719919483ce4eb7cbe98c46ff287e128240505aa0a25617105354772"),
    ("stage_a_20260907_r1.xz.b64.part01_08", "51a4cc7c4bf0aa91fb5b25871b58731b24c5db5b369358488f8b497a914472c6"),
    ("stage_a_20260907_r1.xz.b64.part01_09_01", "12bc25985afd648fd278ef5f055b9d14e3cb4fda439aed8591534053b4d13e89"),
    ("stage_a_20260907_r1.xz.b64.part01_09_02", "192dbd1aa6d0ec404e0d4acb9270039f87bc7a22d8f1660d0d013502219066c4"),
    ("stage_a_20260907_r1.xz.b64.part01_09_03", "b9fefa0557fc47add3450b649ebe976045ea1f0617c25d6b19ce3d1a4ec7d907"),
    ("stage_a_20260907_r1.xz.b64.part01_09_04", "da3ed9fd7a9bc01f04032851a5618f06edb652bae25ef217f1255e669e4b09eb"),
    ("stage_a_20260907_r1.xz.b64.part01_09_05", "8ca2e094c20a13b8a9c2245ba327ba9f865b46331c8c563bb6247ce43e6cc4ab"),
    ("stage_a_20260907_r1.xz.b64.part01_09_06", "360fea0b6c9e87cc23278c8a6902f97d8201fe61145415d6b3d08bd3bd550a28"),
    ("stage_a_20260907_r1.xz.b64.part01_09_07", "0833b4431ee16f6d979e681f796cd8b8f96cfb3078759e6da3cad1145dbe56d6"),
    ("stage_a_20260907_r1.xz.b64.part01_09_08", "db40d44ed3c464f4882d808724917bd097c0f34b9162361d1499c823898ce021"),
    ("stage_a_20260907_r1.xz.b64.part01_09_09", "a6f7a4bad042b4fbfc4c327278d705e8d06bcafc48669ca7dc78540da3ae5bc7"),
    ("stage_a_20260907_r1.xz.b64.part01_09_10", "24379c89fe7817dfcea4a874d08d2c82bf3d1864030b3ddd0ff5097883d2384f"),
    ("stage_a_20260907_r1.xz.b64.part01_10", "c914961040e1dcdb58a2c4ebf3f520f66ccfa43af56d0d1ad530e8fdcf0e4e1e"),
    ("stage_a_20260907_r1.xz.b64.part02", "5b15b3ae4ff97beb14aa317e4c24bf9666e97f5a44a584fa3ccc7636a15e612b"),
    ("stage_a_20260907_r1.xz.b64.part03_04", "2c1c1c3902082ef2fd5d66041815ece0d758105cde9c2f16da76677189a05167"),
    ("stage_a_20260907_r1.xz.b64.part05_06", "2417616cc01fb7025956552a4c6fef9af7a6ede04b05f4d5cb7364fd8fc45897"),
    ("stage_a_20260907_r1.xz.b64.part07_08", "bb12a26e68e8a581eeefe90087c65cf16d602285432e4cb229edb7944c7544b7"),
)
EXPECTED_SHA256 = "fb96bda5f896cb2d73e63cc76dbdb78d7d631fb547b1f919a8bc2a5a8973bd37"


class StageA20260907R1RepoReplayTest(unittest.TestCase):
    def test_exact_stage_a_r1_passes_current_full_gate(self) -> None:
        chunks: list[str] = []
        mismatches: list[str] = []
        for name, expected_part_sha in PARTS:
            chunk = (FIXTURE_DIR / name).read_text(encoding="utf-8").strip()
            actual = hashlib.sha256(chunk.encode("utf-8")).hexdigest()
            if actual != expected_part_sha:
                mismatches.append(f"{name}: expected={expected_part_sha} actual={actual}")
            chunks.append(chunk)
        self.assertEqual(mismatches, [], msg="fixture byte mismatches: " + " | ".join(mismatches))

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
