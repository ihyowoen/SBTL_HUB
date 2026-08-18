#!/usr/bin/env python3
import base64
import copy
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
R1_ORIGINAL_SHA = "dc734fc714c297017130a3821cbe11190e5123153eac488b00ec7c1894240fe5"
R2_ORIGINAL_SHA = "453a722a7f9b415a1e024f3f477ad0a0c1e3f9c93ecfe7b3818943931850e85f"
R1_REPAIRED_SHA = "441eaac2cbced0783e711af11cbe2db31a73acaddf06d55f28bc7f07bb7bd8d8"
R2_REPAIRED_SHA = "5f98001f954b77a3ea3a0da08890e88223ae759f83ac0aa28186dc7965be7228"
STAGE_B_SHA = "0e28bab204751c7a31196c58b578e9f580ce259e0e0c109c6db18b8da23880d9"
EXPECTED = ["STD26_A_052", "STD26_A_054", "STD26_A_058", "STD26_A_083", "STD26_A_084"]


def payload(paths):
    return "".join((FIX / name).read_text(encoding="utf-8") for name in paths)


def repair_map():
    return json.loads((FIX / "stage_b_lineage_repair_map.json").read_text(encoding="utf-8"))


def materialize_current_stage_c_contract(doc):
    mapping = repair_map()
    for bucket in ("accepted_fact_safe", "revise_required_again"):
        for item in doc.get(bucket, []):
            sid = item.get("source_spec_id")
            if sid not in mapping:
                continue
            upstream = mapping[sid]
            item["related_evidence_review"] = copy.deepcopy(upstream["related_evidence_review"])
            item["date_role"] = copy.deepcopy(upstream["date_role"])
            item["related_lineage"] = {
                "status": upstream["related_evidence_review"]["status"],
                "stage_b_related_evidence_review": copy.deepcopy(upstream["related_evidence_review"]),
                "production_related_modified": upstream["related_evidence_review"]["production_related_modified"],
            }
            item["single_source_exception"] = copy.deepcopy(upstream["single_source_exception"])

    doc["repo_native_artifact_contract_repair"] = {
        "repair_type": "CURRENT_MAIN_STAGE_C_ARTIFACT_CONTRACT_LINEAGE_MATERIALIZATION",
        "reason": "repo-native Stage C artifact validator requires related_lineage and date_role",
        "source": "stage_b_exact10_r0_results_20260818_STANDARD_NEW_RUN_CURRENT_MAIN.json",
        "source_sha256": STAGE_B_SHA,
        "fields_materialized": [
            "related_evidence_review",
            "related_lineage",
            "date_role",
            "single_source_exception",
        ],
        "editorial_content_changed": False,
        "fact_sources_changed": False,
        "v3_route_package_changed": False,
        "production_related_modified": False,
        "prompt_0_4_started": False,
        "diversity_lineage_source": "stage_b_exact10_r0_results_20260818_STANDARD_NEW_RUN_CURRENT_MAIN.json",
        "single_source_exception_materialized_from_stage_b": True,
    }
    return doc


class Exact10Accepted5Closure(unittest.TestCase):
    def _original(self, names, expected_sha):
        raw = lzma.decompress(base64.b64decode(payload(names)))
        self.assertEqual(hashlib.sha256(raw).hexdigest(), expected_sha)
        return json.loads(raw.decode("utf-8"))

    def _write_repaired(self, td, name, doc, expected_sha):
        raw = (json.dumps(doc, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
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
        r1_doc = self._original(
            ["r1_00.b64", "r1_01_03.b64", "r1_04_05.b64"],
            R1_ORIGINAL_SHA,
        )
        r2_doc = self._original(
            ["r2_00.b64", "r2_01.b64", "r2_02.b64"],
            R2_ORIGINAL_SHA,
        )
        r1_doc = materialize_current_stage_c_contract(r1_doc)
        r2_doc = materialize_current_stage_c_contract(r2_doc)

        with tempfile.TemporaryDirectory() as td:
            r1 = self._write_repaired(td, "stage_c_revise_r1_exact10_repaired.json", r1_doc, R1_REPAIRED_SHA)
            r2 = self._write_repaired(td, "stage_c_revise_r2_exact10_repaired.json", r2_doc, R2_REPAIRED_SHA)

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
            self.assertEqual((d1["accepted_fact_safe_count"], d1["revise_required_again_count"]), (4, 1))
            self.assertEqual((d2["accepted_fact_safe_count"], d2["revise_required_again_count"]), (1, 0))

            latest = {item["source_spec_id"]: item for item in d1["accepted_fact_safe"]}
            latest.update({item["source_spec_id"]: item for item in d2["accepted_fact_safe"]})
            self.assertEqual(sorted(latest), EXPECTED)
            self.assertEqual(len(latest), 5)
            self.assertEqual(latest["STD26_A_058"]["revision_pass"], "r2")
            self.assertTrue(latest["STD26_A_084"]["single_source_exception"]["allowed"])
            for sid, item in latest.items():
                self.assertEqual(item["state"], "accepted_fact_safe")
                self.assertFalse(item["publish_ready"])
                self.assertTrue(item["needs_post_acceptance_duplicate_review"])
                self.assertTrue(item["needs_post_acceptance_evidence_qc"])
                self.assertIn("related_lineage", item)
                self.assertIn("date_role", item)
                self.assertIn("single_source_exception", item)
                if sid != "STD26_A_084":
                    self.assertFalse(item["single_source_exception"]["allowed"])


if __name__ == "__main__":
    unittest.main()
