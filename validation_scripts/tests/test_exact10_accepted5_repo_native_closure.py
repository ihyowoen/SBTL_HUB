#!/usr/bin/env python3
import base64
import hashlib
import json
import lzma
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
R1_SHA = "dc734fc714c297017130a3821cbe11190e5123153eac488b00ec7c1894240fe5"
R2_SHA = "453a722a7f9b415a1e024f3f477ad0a0c1e3f9c93ecfe7b3818943931850e85f"
EXPECTED = ["STD26_A_052", "STD26_A_054", "STD26_A_058", "STD26_A_083", "STD26_A_084"]


def _payload_from_pr_body(key):
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        raise RuntimeError("GITHUB_EVENT_PATH is required for validation-only PR test")
    event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    body = ((event.get("pull_request") or {}).get("body") or "")
    match = re.search(rf"<!-- {key}:([A-Za-z0-9+/=]+) -->", body)
    if not match:
        raise RuntimeError(f"missing {key} payload in PR body")
    return match.group(1)


class Exact10Accepted5Closure(unittest.TestCase):
    def _write(self, td, name, key, expected_sha):
        raw = lzma.decompress(base64.b64decode(_payload_from_pr_body(key)))
        self.assertEqual(hashlib.sha256(raw).hexdigest(), expected_sha)
        path = Path(td) / name
        path.write_bytes(raw)
        return path

    def _run(self, *args):
        cp = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
        if cp.returncode != 0:
            self.fail(f"command failed: {' '.join(map(str, args))}\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}")

    def test_exact10_accepted5_repo_native_closure(self):
        with tempfile.TemporaryDirectory() as td:
            r1 = self._write(td, "stage_c_revise_r1_exact10.json", "EXACT10_R1_XZ_B64", R1_SHA)
            r2 = self._write(td, "stage_c_revise_r2_exact10.json", "EXACT10_R2_XZ_B64", R2_SHA)
            for artifact in (r1, r2):
                self._run(sys.executable, str(ROOT / "validation_scripts/stage_artifact_contract_check.py"), "C", str(artifact))
                self._run(sys.executable, str(ROOT / "validation_scripts/stage_lineage_contract_check.py"), "stage_c", str(artifact))

            d1 = json.loads(r1.read_text(encoding="utf-8"))
            d2 = json.loads(r2.read_text(encoding="utf-8"))
            self.assertEqual((d1["accepted_fact_safe_count"], d1["revise_required_again_count"]), (4, 1))
            self.assertEqual((d2["accepted_fact_safe_count"], d2["revise_required_again_count"]), (1, 0))

            latest = {item["source_spec_id"]: item for item in d1["accepted_fact_safe"]}
            latest.update({item["source_spec_id"]: item for item in d2["accepted_fact_safe"]})
            self.assertEqual(sorted(latest), EXPECTED)
            self.assertEqual(latest["STD26_A_058"]["revision_pass"], "r2")
            for item in latest.values():
                self.assertEqual(item["state"], "accepted_fact_safe")
                self.assertFalse(item["publish_ready"])
                self.assertTrue(item["needs_post_acceptance_duplicate_review"])
                self.assertTrue(item["needs_post_acceptance_evidence_qc"])


if __name__ == "__main__":
    unittest.main()
