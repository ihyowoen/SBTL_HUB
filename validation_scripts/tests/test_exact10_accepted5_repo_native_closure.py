#!/usr/bin/env python3
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
FIX = Path(__file__).resolve().parent / "fixtures" / "exact10_accepted5"
R1_SHA = "752c24b2309968318ea784e16ae79e97cc2f14c8c0dbab75557ab530f60629ff"
R2_SHA = "10b6dff5bb9607174f627acdb6f06495c3218e4dc6238e13366542a564a7c34e"
EXPECTED = ["STD26_A_052", "STD26_A_054", "STD26_A_058", "STD26_A_083", "STD26_A_084"]


def payload(prefix):
    paths = sorted(FIX.glob(f"{prefix}*.b64"))
    if not paths:
        raise RuntimeError(f"missing fixture parts for {prefix}")
    return "".join(p.read_text(encoding="utf-8") for p in paths)


class Exact10Accepted5Closure(unittest.TestCase):
    def _write(self, td, name, prefix, expected_sha):
        raw = lzma.decompress(base64.b64decode(payload(prefix)))
        self.assertEqual(hashlib.sha256(raw).hexdigest(), expected_sha)
        path = Path(td) / name
        path.write_bytes(raw)
        return path

    def _run(self, *args):
        cp = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
        if cp.returncode != 0:
            self.fail(
                f"command failed: {' '.join(map(str, args))}\n"
                f"STDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
            )

    def test_exact10_accepted5_repo_native_closure(self):
        with tempfile.TemporaryDirectory() as td:
            r1 = self._write(td, "stage_c_revise_r1_exact10_lineage_repaired.json", "r1_repaired_", R1_SHA)
            r2 = self._write(td, "stage_c_revise_r2_exact10_lineage_repaired.json", "r2_repaired_", R2_SHA)

            for artifact in (r1, r2):
                self._run(
                    sys.executable,
                    str(ROOT / "validation_scripts/stage_artifact_contract_check.py"),
                    "C",
                    str(artifact),
                )
                self._run(
                    sys.executable,
                    str(ROOT / "validation_scripts/stage_lineage_contract_check.py"),
                    "stage_c",
                    str(artifact),
                )

            d1 = json.loads(r1.read_text(encoding="utf-8"))
            d2 = json.loads(r2.read_text(encoding="utf-8"))
            self.assertEqual(
                (d1["accepted_fact_safe_count"], d1["revise_required_again_count"]),
                (4, 1),
            )
            self.assertEqual(
                (d2["accepted_fact_safe_count"], d2["revise_required_again_count"]),
                (1, 0),
            )

            latest = {item["source_spec_id"]: item for item in d1["accepted_fact_safe"]}
            latest.update({item["source_spec_id"]: item for item in d2["accepted_fact_safe"]})
            self.assertEqual(sorted(latest), EXPECTED)
            self.assertEqual(len(latest), 5)
            self.assertEqual(latest["STD26_A_058"]["revision_pass"], "r2")
            for item in latest.values():
                self.assertEqual(item["state"], "accepted_fact_safe")
                self.assertFalse(item["publish_ready"])
                self.assertTrue(item["needs_post_acceptance_duplicate_review"])
                self.assertTrue(item["needs_post_acceptance_evidence_qc"])
                self.assertIn("related_lineage", item)
                self.assertIn("date_role", item)


if __name__ == "__main__":
    unittest.main()
