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

    def test_apply_workflow_dispatches_08_and_binds_exact_touched_id_set(self):
        text = APPLY_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('AUDIT_ONLY_RUN="$RUNNER_TEMP/card-run-audits-only.json"', text)
        self.assertIn("if (payload?.stage === '0.8')", text)
        self.assertIn("no card_run_audit_v1 reference remains after 0.8 dispatch", text)
        self.assertIn("BLOCKED_PROMPT_0_8_ITEM_SET", text)
        self.assertIn("const expectedIds = [...ids].sort();", text)
        self.assertIn("const reviewedIds = [...artifactIds].sort();", text)
        self.assertIn("JSON.stringify(reviewedIds) !== JSON.stringify(expectedIds)", text)

    def test_apply_workflow_historical_v1_exception_is_base_bound_and_deletion_aware(self):
        text = APPLY_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("--diff-filter=ACMRD", text)
        self.assertIn('D*) base_manifest="$path1"; manifest=""', text)
        self.assertIn('git show "${base_sha}:${base_manifest}"', text)
        self.assertIn('[[ "$base_schema_name" == "manual_direct_add_v1" ]] || return 1', text)
        self.assertIn('if [[ "$status" == D* ]]; then', text)

    def test_schema_workflow_cannot_downgrade_v2_to_v1_and_allows_historical_v1_delete(self):
        text = DIRECT_ADD_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("--diff-filter=ACMRD", text)
        self.assertIn("base_schema()", text)
        self.assertIn("only historical manual_direct_add_v1 audit manifests may use the audit-only deletion path", text)
        self.assertIn("cannot downgrade non-V1 base manifest to retired manual_direct_add_v1", text)
        self.assertIn('[[ "$base_schema_name" == "manual_direct_add_v1" ]]', text)


if __name__ == "__main__":
    unittest.main()
