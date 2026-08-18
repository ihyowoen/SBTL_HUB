#!/usr/bin/env python3
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_FIXTURE = ROOT / "validation_scripts/tests/fixtures/stage_a_a082_current_main_recertification_20260818.json"
EXPECTED_SPEC = "STD26_A_082"
EXPECTED_STORY = "20260807_160552::KR_2026-08-06_C23"

CONFIRMATION_REPAIR = [
    {
        "measurable_event_or_metric": "Shinheung SEC Malaysia CID production capacity reaches 100 million cell-equivalent units per month",
        "interpretation_effect": "Confirmed 100 million monthly capacity would strengthen the A082 capacity-expansion assessment; failure to reach it would weaken the A082 capacity-expansion assessment",
    },
    {
        "measurable_event_or_metric": "Samsung SDI BBU-related cylindrical-cell shipment volume after 2026-08-06",
        "interpretation_effect": "A verified shipment-volume increase would strengthen the BBU-demand assessment; flat or lower shipments would weaken the BBU-demand assessment",
    },
    {
        "measurable_event_or_metric": "Shinheung SEC Malaysia CID capacity utilization after the expansion",
        "interpretation_effect": "A verified utilization increase would strengthen the persistence assessment; low utilization would weaken the persistence assessment",
    },
]


class A082StageARecertificationContract(unittest.TestCase):
    def _run(self, *args):
        cp = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
        if cp.returncode != 0:
            self.fail(
                f"command failed: {' '.join(map(str, args))}\n"
                f"STDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
            )
        return cp.stdout

    def _materialize_repaired_artifact(self, target):
        data = json.loads(BASE_FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(len(data["strict_passed_spec"]), 1)
        spec = data["strict_passed_spec"][0]
        self.assertEqual(spec["spec_id"], EXPECTED_SPEC)
        spec["next_confirmation_points"] = CONFIRMATION_REPAIR
        data["repo_native_repair"] = {
            "reason": "Workflow #906 showed only next_confirmation_points semantic binding was insufficiently item-specific.",
            "fields_changed": ["strict_passed_spec[0].next_confirmation_points"],
            "selection_changed": False,
            "score_changed": False,
            "execution_route_changed": False,
            "source_story_mapping_changed": False,
            "source_urls_changed": False,
            "external_web_search_performed": False,
            "article_body_fetch_performed": False,
            "stage_b_started": False,
        }
        raw = (json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        target.write_bytes(raw)
        print("A082_REPAIRED_STAGE_A_SHA256=" + hashlib.sha256(raw).hexdigest())
        return data

    def test_repo_native_contract_and_scope(self):
        with tempfile.TemporaryDirectory() as td:
            repaired = Path(td) / "stage_a_a082_current_main_recertification_REPAIRED.json"
            data = self._materialize_repaired_artifact(repaired)

            artifact_out = self._run(
                sys.executable,
                str(ROOT / "validation_scripts/stage_artifact_contract_check.py"),
                "A",
                str(repaired),
            )
            lineage_out = self._run(
                sys.executable,
                str(ROOT / "validation_scripts/stage_lineage_contract_check.py"),
                "stage_a",
                str(repaired),
            )
            self.assertIn('"status": "PASS"', artifact_out)
            self.assertIn("PASS_STAGE_A_SCHEMA_CONTRACT", lineage_out)

            self.assertEqual(data["story_count"], 1)
            self.assertEqual(data["summary"]["strict_passed_spec_count"], 1)
            self.assertEqual(data["summary"]["decision_ledger_count"], 1)
            self.assertEqual(len(data["strict_passed_spec"]), 1)
            self.assertEqual(len(data["decision_ledger"]), 1)

            spec = data["strict_passed_spec"][0]
            self.assertEqual(spec["spec_id"], EXPECTED_SPEC)
            self.assertEqual(spec["source_story_ids"], [EXPECTED_STORY])
            self.assertEqual(spec["representative_story_id"], EXPECTED_STORY)
            self.assertEqual(spec["execution_anchor_type"], "component_capacity_expansion")
            self.assertEqual(spec["execution_anchor_strength"], "strong")
            self.assertFalse(spec["structural_value_override_applied"])
            self.assertEqual(spec["strict_gate_check"], "pass")
            self.assertEqual(spec["strict_pass_gate"]["status"], "pass")
            self.assertTrue(spec["strict_pass_gate"]["all_six_conditions_passed"])
            self.assertEqual(spec["stage_a_evidence_status"], "not_evidence_complete_no_fetch")
            self.assertEqual(spec["primary_url_semantics"], "provided_source_candidate_not_evidence")
            self.assertEqual(spec["next_confirmation_points"], CONFIRMATION_REPAIR)

            self.assertFalse(data["external_web_search_performed_in_stage_a"])
            self.assertFalse(data["article_body_fetch_performed_in_stage_a"])
            self.assertFalse(data["source_quote_generated_in_stage_a"])
            self.assertFalse(data["fact_sources_generated_in_stage_a"])
            self.assertFalse(data["card_copy_generated_in_stage_a"])
            self.assertFalse(data["production_ids_assigned"])
            self.assertFalse(data["boundary"]["stage_b_started"])
            self.assertFalse(data["boundary"]["stage_b_authorized"])
            self.assertFalse(data["boundary"]["prompt_0_4_started"])

            self.assertTrue(data["integrity_summary"]["exact_mapping_recovered_from_execution_log"])
            self.assertFalse(data["integrity_summary"]["superseded_reconstruction_used_as_original_mapping"])
            self.assertFalse(data["repo_native_repair"]["selection_changed"])
            self.assertFalse(data["repo_native_repair"]["execution_route_changed"])


if __name__ == "__main__":
    unittest.main()
