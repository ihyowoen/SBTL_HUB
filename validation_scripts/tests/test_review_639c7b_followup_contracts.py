#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGE_CHECK = ROOT / "validation_scripts" / "stage_artifact_contract_check.py"
APPLY_WORKFLOW = ROOT / ".github" / "workflows" / "apply-card-run.yml"
DIRECT_ADD_WORKFLOW = ROOT / ".github" / "workflows" / "manual-direct-add-schema-validation.yml"


def run_stage(stage: str, payload: dict) -> tuple[subprocess.CompletedProcess[str], dict]:
    with tempfile.TemporaryDirectory() as tmp:
        artifact = Path(tmp) / "artifact.json"
        artifact.write_text(json.dumps(payload), encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(STAGE_CHECK), stage, str(artifact)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        return completed, json.loads(completed.stdout)


def related_unrelated() -> dict:
    return {
        "status": "PASS",
        "relation_type": "new_unrelated_event",
        "related_ids": [],
    }


def valid_06_item() -> dict:
    return {
        "source_spec_id": "SPEC-1",
        "content_enriched": True,
        "language_terminology_polished": True,
        "related_lineage": related_unrelated(),
        "date_role": {"status": "PASS"},
        "source_diversity_status": "PASS_MULTI_SOURCE",
    }


def valid_08_item() -> dict:
    return {
        "id": "2026-09-02_US_01",
        "source_spec_id": "SPEC-1",
        "related_lineage": related_unrelated(),
        "date_role": {"status": "PASS"},
        "source_diversity_status": "PASS_MULTI_SOURCE",
        "merge_prep": {"status": "PASS"},
    }


class LatestPrompt08AndHistoricalV1Review(unittest.TestCase):
    def test_duplicate_stage_identity_is_rejected_and_every_row_is_validated(self):
        failing_duplicate = valid_06_item()
        failing_duplicate["content_enriched"] = False
        failing_duplicate["source_diversity_status"] = "HOLD_NEEDS_SOURCE_AUGMENTATION"
        payload = {
            "stage": "0.6",
            "status": "CONTENT_ENRICHED_AND_LANGUAGE_TERMINOLOGY_POLISHED",
            "upstream_lineage_integrity": "PASS",
            "lineage_and_anchor_guard": "PASS",
            "content_enriched_and_language_polished": [
                valid_06_item(),
                failing_duplicate,
            ],
        }
        completed, report = run_stage("0.6", payload)
        self.assertNotEqual(completed.returncode, 0)
        fields = [finding.get("field") for finding in report["findings"]]
        self.assertIn("duplicate_stage_item_identity", fields)
        self.assertIn("content_enriched", fields)
        self.assertIn("source_diversity_status", fields)
        self.assertEqual(report["item_count"], 2)

    def test_scalar_only_prompt_08_gates_are_rejected(self):
        payload = {
            "stage": "0.8",
            "status": "GITHUB_MERGE_READY",
            "github_main_sync_gate": "PASS",
            "lineage_merge_gate": "PASS",
            "github_merge_ready": [valid_08_item()],
        }
        completed, report = run_stage("0.8", payload)
        self.assertNotEqual(completed.returncode, 0)
        fields = {finding.get("field") for finding in report["findings"]}
        self.assertIn("github_main_sync_gate", fields)
        self.assertIn("lineage_merge_gate", fields)

    def test_structured_prompt_08_gates_still_pass(self):
        payload = {
            "stage": "0.8",
            "status": "GITHUB_MERGE_READY",
            "github_main_sync_gate": {
                "status": "PASS",
                "baseline_locked": True,
                "main_unchanged_since_locked_preflight": True,
                "silent_rebase_performed": False,
            },
            "lineage_merge_gate": {
                "final_qc_lineage_passed": True,
                "anchor_path_lineage_passed": True,
                "github_ready_allowed": True,
                "anchor_path_hold_count": 0,
            },
            "github_merge_ready": [valid_08_item()],
        }
        completed, report = run_stage("0.8", payload)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(report["status"], "PASS")

    def test_apply_workflow_delegates_audit_dispatch_and_exact_operation_item_set(self):
        text = APPLY_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("scripts/validate_card_run_audits_dispatch.mjs", text)
        self.assertIn("scripts/validate_prompt_0_8_semantic_gate.mjs", text)
        self.assertIn("prompt-0-8-id-ledger.json", text)
        self.assertIn("OPERATION_ID_COUNT", text)
        self.assertNotIn('AUDIT_ONLY_RUN="$RUNNER_TEMP/card-run-audits-only.json"', text)
        self.assertNotIn("const expectedIds = [...ids].sort();", text)

    def test_apply_workflow_historical_v1_exception_uses_shared_classifier(self):
        text = APPLY_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("scripts/manual_direct_add_v1_history.mjs", text)
        self.assertIn("--audit-only", text)
        self.assertIn('historical_v1_audit_only()', text)
        self.assertNotIn('D*) base_manifest="$path1"; manifest=""', text)
        self.assertNotIn('git show "${BASE_SHA}:data/cards.full.base.json"', text)

    def test_schema_workflow_uses_same_shared_v1_classifier(self):
        text = DIRECT_ADD_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("scripts/manual_direct_add_v1_history.mjs", text)
        self.assertIn("--validate-changed", text)
        self.assertNotIn("base_schema()", text)
        self.assertNotIn("resolve_manifest_paths()", text)


if __name__ == "__main__":
    unittest.main()
