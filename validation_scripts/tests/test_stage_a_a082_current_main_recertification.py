#!/usr/bin/env python3
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from validation_scripts import stage_lineage_contract_check as lineage

ROOT = Path(__file__).resolve().parents[2]
BASE_FIXTURE = ROOT / "validation_scripts/tests/fixtures/stage_a_a082_current_main_recertification_20260818.json"
EXPECTED_SPEC = "STD26_A_082"
EXPECTED_STORY = "20260807_160552::KR_2026-08-06_C23"

# Current public validator accepts direct-transitive interpretation binding such as
# "The milestone confirmed the adoption thesis". Keep measurable targets separate
# and bind only the interpretation effect here.
CONFIRMATION_REPAIR = [
    {
        "measurable_event_or_metric": "Shinheung SEC Malaysia CID 2026 production capacity",
        "interpretation_effect": "The capacity milestone confirmed the A082 capacity-expansion thesis",
    },
    {
        "measurable_event_or_metric": "Samsung SDI BBU 2026 shipment volume",
        "interpretation_effect": "The shipment result strengthened the A082 BBU-demand thesis",
    },
    {
        "measurable_event_or_metric": "Shinheung SEC Malaysia CID 2026 capacity utilization",
        "interpretation_effect": "The utilization result strengthened the A082 persistence thesis",
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
            "reason": "Workflows #906-#909 isolated the only remaining block to interpretation_effect binding. The measurable targets already pass. Effects now use the current-repo direct-transitive pattern proven by test_review_4850532920_contracts.py.",
            "fields_changed": ["strict_passed_spec[0].next_confirmation_points[*].interpretation_effect"],
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
        for index, point in enumerate(CONFIRMATION_REPAIR):
            measurable_ok = lineage._structured_exact_target(point["measurable_event_or_metric"])
            effect_ok = lineage._structured_interpretation_effect(point["interpretation_effect"])
            self.assertTrue(measurable_ok, f"confirmation[{index}] measurable target invalid: {point!r}")
            self.assertTrue(effect_ok, f"confirmation[{index}] interpretation effect invalid: {point!r}")
            self.assertTrue(lineage._valid_confirmation_point(point), f"confirmation[{index}] pair invalid: {point!r}")

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
