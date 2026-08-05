from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "validation_scripts/related_lifecycle_check.py"


def lifecycle(relation_type: str, related_candidate_spec_ids=None):
    return {
        "status": "PASS",
        "same_event_checked": True,
        "earliest_same_event_date_checked": True,
        "relation_type": relation_type,
        "related_ids": [],
        "related_candidate_spec_ids": related_candidate_spec_ids or [],
        "fresh_follow_up_anchor": "new verified timing change" if relation_type == "distinct_follow_up" else None,
        "fresh_follow_up_anchor_class": "follow_up_probability_anchor" if relation_type == "distinct_follow_up" else None,
        "incremental_fact_vs_predecessor": "schedule moved" if relation_type == "distinct_follow_up" else None,
        "changed_judgment_vs_predecessor": "Project Alpha probability reduced" if relation_type == "distinct_follow_up" else None,
        "reason": "current-run candidate relation",
    }


class TestReview4840431415Contracts(unittest.TestCase):
    def run_validator(self, allow_provisional: bool):
        parent = {
            "source_spec_id": "SPEC_PARENT",
            "date": "2026-08-01",
            "related": [],
            "related_lineage": lifecycle("new_unrelated_event"),
        }
        child = {
            "source_spec_id": "SPEC_CHILD",
            "date": "2026-08-02",
            "related": [],
            "related_candidate_spec_ids": ["SPEC_PARENT"],
            "related_lineage": lifecycle("distinct_follow_up", ["SPEC_PARENT"]),
        }
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cards = tmp_path / "cards.json"
            ids = tmp_path / "ids.json"
            cards.write_text(json.dumps({"cards": [parent, child]}), encoding="utf-8")
            ids.write_text(json.dumps(["SPEC_PARENT", "SPEC_CHILD"]), encoding="utf-8")
            cmd = [
                sys.executable, str(VALIDATOR), str(cards),
                "--require-contract", "--new-id-file", str(ids),
            ]
            if allow_provisional:
                cmd.append("--allow-provisional-related")
            return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)

    def test_final_qc_allows_uniquely_resolved_current_run_provisional_edge(self):
        result = self.run_validator(True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "PASS")

    def test_final_id_gate_still_rejects_unresolved_provisional_only_edge(self):
        result = self.run_validator(False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires at least one final or allowed provisional related ID", result.stdout)

    def test_final_qc_prompt_and_generator_use_provisional_flag(self):
        needle = "--require-contract --allow-provisional-related --new-id-file <CURRENT_RUN_ID_FILE>"
        for rel in [
            "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md",
            "validation_scripts/apply_prompt_contract_overlays.py",
        ]:
            self.assertIn(needle, (ROOT / rel).read_text(encoding="utf-8"))

    def test_revise_outputs_preserve_complete_v3_package(self):
        required = [
            "structural_value_override_reason", "anchor_classes[]",
            "evidence_needed_for_stage_b[]", "why_execution_event_not_required",
            "prior_state", "new_verified_fact", "changed_judgment",
            "uncertainty_resolved", "remaining_uncertainty",
            "incremental_information", "baseline_expectation_changed",
            "decision_relevance", "next_confirmation_points[]",
        ]
        for rel in [
            "docs/llm_prompts/v1/04_PROMPT_0_2R_Stage_B_Revise.md",
            "docs/llm_prompts/v1/05_PROMPT_0_3R_Stage_C_Revise.md",
        ]:
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("complete byte-for-byte canonical package", text)
            for field in required:
                self.assertIn(field, text)


if __name__ == "__main__":
    unittest.main()
