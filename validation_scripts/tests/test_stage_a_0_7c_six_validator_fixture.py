from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import zlib
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHUNK_DIR = Path(__file__).resolve().parent / "fixtures"
R2_EXPECTED_SHA256 = "d301af14b9c03abc013fba446e3b8e6278834340e75411badeb9a63ac504efa7"
R5_EXPECTED_SHA256 = "d8bf4392486e245187be52d3293cbfc265b3eb97fa0259e1cc477a0a7390c2a4"
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
UPSTREAM = {
    "STD26_A_004": "KEEP",
    "STD26_A_007": "KEEP",
    "STD26_A_011": "TRIAGE_FILTERED",
    "STD26_A_033": "KEEP",
    "STD26_A_035": "TRIAGE_FILTERED",
    "STD26_A_036": "TRIAGE_FILTERED",
}
CANONICAL_NOTE = (
    "Stage B must verify the provided source-candidate URL and build a valid evidence package before drafting. "
    "This Stage A spec is not evidence_complete, and primary_url is not evidence by itself."
)
SOURCE_PRIORITY = (
    "Preserve all observations and independently verify official/source-owner plus independent same-event evidence "
    "where available; apply an explicit downstream source-diversity exception only under policy."
)


def build_r5_bytes() -> bytes:
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

    # R3/R4 lineage semantic repairs: confirmation points only.
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

    # R5 base transport closure: fields required by Prompt 0.1/current full-artifact validator.
    for item in data["strict_passed_spec"]:
        sid = item["spec_id"]
        cluster = item["same_event_source_cluster"][0]
        pub = cluster["published_date"]
        ev = item["representative_date"]
        gap = abs((date.fromisoformat(pub) - date.fromisoformat(ev)).days)
        item["title_raw"] = item["headline"]
        item["summary_hint"] = item["event_anchor"]
        item["context_text"] = item["incremental_information"]
        item["why_now"] = (
            f"The preserved current-run event date {ev} provides the bounded Stage A timing anchor for {item['headline']}."
        )
        item["market_relevance"] = item["decision_relevance"]
        item["source_priority_notes"] = SOURCE_PRIORITY
        item["upstream_labels"] = {
            "triage_status": UPSTREAM[sid],
            "matched_buckets": [],
            "drop_reason": None,
            "integrity_group_id": None,
            "integrity_is_best": None,
            "drop_reason_overridden": UPSTREAM[sid] == "TRIAGE_FILTERED",
        }
        item["staleness"] = {
            "event_date": ev,
            "publication_date": pub,
            "staleness_gap_days": gap,
            "staleness_suspected": False,
            "fresh_followup": item.get("baseline_follow_up_relation") not in ("new_unrelated", "new", "unrelated", None, ""),
            "staleness_override": False,
            "decision": item["staleness_decision"],
        }
        item["needs_review"] = False
        item["review_reason"] = None
        item["stage_b_requirement_note"] = CANONICAL_NOTE

    data["lane_sanity_rules_applied"] = {
        "status": "PASS_REMATERIALIZED_FROM_PRESERVED_STRICT_DECISIONS",
        "editorial_reselection_performed": False,
        "stage_b_evidence_used": False,
    }
    data["dropped_treasure_hunt"]["non_sampled_ledger_policy"] = "not_applicable_targeted_lineage_rematerialization_subset"
    data["required_docs_check"]["status"] = "PASS"
    data["summary"]["duplicate_or_reinforcement_count"] = 0
    data["summary"]["stale_discarded_count"] = 0
    data["summary"]["stale_warm_review_count"] = 0

    by_spec = {item["spec_id"]: item for item in data["strict_passed_spec"]}
    for row in data["decision_ledger"]:
        item = by_spec[row["spec_id"]]
        cluster = item["same_event_source_cluster"][0]
        row["original_triage_status"] = UPSTREAM[row["spec_id"]]
        row["stage_a_bucket"] = "strict_passed_spec"
        row["upstream_drop_reason"] = None
        row["headline"] = item["title_raw"]
        row["site"] = cluster["site"]
        row["url"] = cluster["url"]
        row["integrity_group_id"] = item["upstream_labels"]["integrity_group_id"]
        row["integrity_is_best"] = item["upstream_labels"]["integrity_is_best"]
        row["merged_into_spec_id"] = None
        row["baseline_match"] = None
        row["treasure_hunt_sampled"] = False
        row["notes"] = "0.7C targeted Stage A lineage rematerialization; historical strict outcome preserved; no Stage B/C evidence imported."

    data["schema"] = "sbtl_stage_a_0_7c_six_lineage_rematerialization_v5"
    data["generated_kst"] = "2026-08-20T12:08:00+09:00"
    data["status"] = "PASS_BASE_TRANSPORT_CLOSURE_R5_REPO_EXECUTION_PENDING"
    data["lineage_validator_repair_r5"] = {
        "source_failure_log": "GitHub validation branch run at head 022b9d94862f1706cfef41594eb2b708b18900eb",
        "repair_scope": [
            "required Stage A base strict fields",
            "required base decision-ledger fields",
            "lane_sanity_rules_applied",
            "dropped_treasure_hunt.non_sampled_ledger_policy",
            "base summary integer counts",
            "required_docs_check.status exact PASS",
        ],
        "repair_basis": "Current-main Prompt 0.1 and repository-validated Early16 authoritative transport pattern.",
        "historical_editorial_outcome_changed": False,
        "strict_ids_changed": False,
        "source_story_ids_changed": False,
        "stage_b_c_evidence_imported": False,
    }
    data["authoritative_stage_a"] = False
    data["stage_b_eligible"] = False
    data["repo_validator"]["repository_native_validator_executed"] = False
    data["repo_validator"]["remaining_blocker"] = "REAL_REPOSITORY_STAGE_A_VALIDATOR_EXECUTION"

    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


class TestStageA07CSixValidatorFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r5_bytes = build_r5_bytes()
        actual_r5_sha256 = hashlib.sha256(r5_bytes).hexdigest()
        if actual_r5_sha256 != R5_EXPECTED_SHA256:
            raise AssertionError(
                f"R5 fixture SHA256 mismatch: expected {R5_EXPECTED_SHA256}, got {actual_r5_sha256}"
            )
        cls.tmp = tempfile.TemporaryDirectory()
        cls.fixture = Path(cls.tmp.name) / "stage_a_0_7c_six_validator_ready_r5.json"
        cls.fixture.write_bytes(r5_bytes)

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
