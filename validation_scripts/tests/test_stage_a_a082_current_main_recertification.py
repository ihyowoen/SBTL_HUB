#!/usr/bin/env python3
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "validation_scripts/tests/fixtures/stage_a_a082_current_main_recertification_20260818.json"
EXPECTED_SPEC = "STD26_A_082"
EXPECTED_STORY = "20260807_160552::KR_2026-08-06_C23"


class A082StageARecertificationContract(unittest.TestCase):
    def _run(self, *args):
        cp = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
        if cp.returncode != 0:
            self.fail(
                f"command failed: {' '.join(map(str, args))}\n"
                f"STDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
            )
        return cp.stdout

    def test_repo_native_contract_and_scope(self):
        artifact_out = self._run(
            sys.executable,
            str(ROOT / "validation_scripts/stage_artifact_contract_check.py"),
            "A",
            str(FIXTURE),
        )
        lineage_out = self._run(
            sys.executable,
            str(ROOT / "validation_scripts/stage_lineage_contract_check.py"),
            "stage_a",
            str(FIXTURE),
        )
        self.assertIn('"status": "PASS"', artifact_out)
        self.assertIn("PASS_STAGE_A_SCHEMA_CONTRACT", lineage_out)

        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
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


if __name__ == "__main__":
    unittest.main()
