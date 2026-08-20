from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHUNK_DIR = Path(__file__).resolve().parent / "fixtures"
R2_EXPECTED_SHA256 = "d301af14b9c03abc013fba446e3b8e6278834340e75411badeb9a63ac504efa7"
R4_EXPECTED_SHA256 = "4fdc2b4a87006b91a469dcb212374cfe11c9c6a8c319d3f92091fb9ab4431e60"
CHUNK_NAMES = [
    "stage_a_0_7c_six_payload_00a.txt",
    "stage_a_0_7c_six_payload_00b.txt",
    "stage_a_0_7c_six_payload_01.txt",
    "stage_a_0_7c_six_payload_02.txt",
    "stage_a_0_7c_six_payload_03.txt",
    "stage_a_0_7c_six_payload_04.txt",
    "stage_a_0_7c_six_payload_05.txt",
    "stage_a_0_7c_six_payload_06.txt",
]
CONFIRMATION_POINT_REPAIR = {
    "STD26_A_004": {
        "measurable_event_or_metric": "Noblevale EPBC approval decision date and permit status",
        "interpretation_effect": "This result would strengthen or weaken the Noblevale project-execution interpretation",
    },
    "STD26_A_007": {
        "measurable_event_or_metric": "Amanecer Puerto Rico BESS construction start date",
        "interpretation_effect": "This result would strengthen or weaken the Puerto Rico BESS execution interpretation",
    },
    "STD26_A_011": {
        "measurable_event_or_metric": "AEMC government adoption decision date and binding implementation status",
        "interpretation_effect": "This result would strengthen or weaken the data-centre policy-implementation interpretation",
    },
    "STD26_A_033": {
        "measurable_event_or_metric": "DLA replacement solicitation publication date lithium purchase volume and award status",
        "interpretation_effect": "This result would strengthen or weaken the strategic-stockpile demand interpretation",
    },
    "STD26_A_035": {
        "measurable_event_or_metric": "Cauchari-Olaroz debt draw volume and Stage 2 construction status",
        "interpretation_effect": "This result would strengthen or weaken the expansion-financing interpretation",
    },
    "STD26_A_036": {
        "measurable_event_or_metric": "PHMSA final-rule effective date and compliance implementation status",
        "interpretation_effect": "This result would strengthen or weaken the transport-compliance interpretation",
    },
}


class TestStageA07CSixValidatorFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        encoded = "".join(
            (CHUNK_DIR / name).read_text(encoding="utf-8").strip()
            for name in CHUNK_NAMES
        )
        r2_bytes = zlib.decompress(base64.b64decode(encoded))
        actual_r2_sha256 = hashlib.sha256(r2_bytes).hexdigest()
        if actual_r2_sha256 != R2_EXPECTED_SHA256:
            raise AssertionError(
                f"R2 fixture SHA256 mismatch: expected {R2_EXPECTED_SHA256}, got {actual_r2_sha256}"
            )

        data = json.loads(r2_bytes.decode("utf-8"))
        for item in data["strict_passed_spec"]:
            item["next_confirmation_points"] = [CONFIRMATION_POINT_REPAIR[item["spec_id"]]]
        for row in data["decision_ledger"]:
            row["next_confirmation_points"] = [CONFIRMATION_POINT_REPAIR[row["spec_id"]]]

        data["schema"] = "sbtl_stage_a_0_7c_six_lineage_rematerialization_v3"
        data["generated_kst"] = "2026-08-20T11:58:04+09:00"
        data["status"] = "PASS_LOCAL_CURRENT_MAIN_VALIDATOR_MIRROR_LINEAGE_REPAIR_R3_REPO_EXECUTION_PENDING"
        data["lineage_validator_repair_r3"] = {
            "source_failure_log": "GitHub validation branch run at head 4ff863f6cb1d267d4d851529d0e9a59d0472dcb5",
            "repair_scope": "next_confirmation_points only; same values mirrored into decision_ledger",
            "repair_reason": "Current-main lineage parser requires a structured exact measurable event/metric plus an interpretation effect explicitly bound to a thesis/interpretation.",
            "historical_editorial_outcome_changed": False,
            "stage_b_c_evidence_imported": False,
            "A011_expected_effect": "Once the confirmation point passes semantic validation, the preserved V3 non-execution package should satisfy exactly-one-path cardinality; no route reselection was performed.",
        }

        data["schema"] = "sbtl_stage_a_0_7c_six_lineage_rematerialization_v4"
        data["generated_kst"] = "2026-08-20T11:59:14+09:00"
        data["status"] = "PASS_LOCAL_CURRENT_MAIN_VALIDATOR_MIRROR_LINEAGE_REPAIR_R4_REPO_EXECUTION_PENDING"
        data["lineage_validator_repair_r4"] = {
            "source_failure_log": "GitHub validation branch run at head 882d5a7bcb2a7b1f0f270fa247d3ce686bd06cf5",
            "repair_scope": "STD26_A_007 next_confirmation_points only; same value mirrored into decision_ledger",
            "repair_reason": "Five other R3 confirmation points passed; A007 measurable target is narrowed to one named project milestone plus explicit date.",
            "historical_editorial_outcome_changed": False,
            "stage_b_c_evidence_imported": False,
        }

        r4_bytes = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        actual_r4_sha256 = hashlib.sha256(r4_bytes).hexdigest()
        if actual_r4_sha256 != R4_EXPECTED_SHA256:
            raise AssertionError(
                f"R4 fixture SHA256 mismatch: expected {R4_EXPECTED_SHA256}, got {actual_r4_sha256}"
            )

        cls.tmp = tempfile.TemporaryDirectory()
        cls.fixture = Path(cls.tmp.name) / "stage_a_0_7c_six_validator_ready_r4.json"
        cls.fixture.write_bytes(r4_bytes)

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
            "A",
            str(self.fixture),
        )
        self.assertIn('"status": "PASS"', proc.stdout)
        self.assertIn('"missing_count": 0', proc.stdout)

    def test_stage_lineage_contract_check(self):
        proc = self._run(
            "validation_scripts/stage_lineage_contract_check.py",
            "stage_a",
            str(self.fixture),
        )
        self.assertIn("RESULT: PASS_STAGE_A_SCHEMA_CONTRACT", proc.stdout)


if __name__ == "__main__":
    unittest.main()
