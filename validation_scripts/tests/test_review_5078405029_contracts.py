#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGE_CHECKER = ROOT / "validation_scripts/stage_artifact_contract_check.py"
APPLY_WORKFLOW = ROOT / ".github/workflows/apply-card-run.yml"
CONTRACT_WORKFLOW = ROOT / ".github/workflows/workflow-contract-validation.yml"
DIRECT_SCHEMA = ROOT / "schemas/manual-direct-add.v2.schema.json"
DIRECT_HARDENER = ROOT / "scripts/validate_manual_direct_add_v4_hardening.mjs"
PROMPT_08 = ROOT / "docs/llm_prompts/v1/10_PROMPT_0_8_GitHub_Merge_Prep.md"


class Review5078405029ContractsTest(unittest.TestCase):
    def run_stage(self, stage: str, payload: dict):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "artifact.json"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            return subprocess.run(
                ["python3", str(STAGE_CHECKER), stage, str(path)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

    def test_06_false_component_and_hold_values_fail_closed(self):
        payload = {
            "stage": "0.6",
            "status": "CONTENT_ENRICHED_AND_LANGUAGE_TERMINOLOGY_POLISHED",
            "upstream_lineage_integrity": "PASS",
            "lineage_and_anchor_guard": "PASS",
            "content_enriched_and_language_polished": [
                {
                    "source_spec_id": "SPEC_1",
                    "content_enriched": False,
                    "language_terminology_polished": False,
                    "related_lineage": None,
                    "date_role": None,
                    "source_diversity_status": "HOLD_NEEDS_SOURCE_AUGMENTATION",
                }
            ],
        }
        result = self.run_stage("0.6", payload)
        combined = f"{result.stdout}\n{result.stderr}"
        self.assertNotEqual(result.returncode, 0, combined)
        self.assertIn("content_enriched", combined)
        self.assertIn("language_terminology_polished", combined)
        self.assertIn("source_diversity_status", combined)
        self.assertIn("related_lineage", combined)
        self.assertIn("date_role", combined)

    def test_06_positive_values_pass(self):
        payload = {
            "stage": "0.6",
            "status": "CONTENT_ENRICHED_AND_LANGUAGE_TERMINOLOGY_POLISHED",
            "upstream_lineage_integrity": "PASS",
            "lineage_and_anchor_guard": "PASS",
            "content_enriched_and_language_polished": [
                {
                    "source_spec_id": "SPEC_1",
                    "content_enriched": True,
                    "language_terminology_polished": True,
                    "related_lineage": {
                        "status": "PASS",
                        "relation_type": "new_unrelated_event",
                        "related_ids": [],
                    },
                    "date_role": {"representative_date": "2026-09-01"},
                    "source_diversity_status": "PASS_MULTI_SOURCE",
                }
            ],
        }
        result = self.run_stage("0.6", payload)
        self.assertEqual(result.returncode, 0, f"stdout={result.stdout}\nstderr={result.stderr}")

    def test_apply_workflow_enforces_post_resolution_08_gate(self):
        text = APPLY_WORKFLOW.read_text(encoding="utf-8")
        for required in (
            "Enforce post-resolution Prompt 0.8 semantic gate",
            "prompt-0-8-id-ledger.txt",
            "related_lifecycle_check.py",
            "--require-contract --new-id-file",
            "evidence_qc_v8_check.py",
            "date_role_freshness_check.py",
            "--require-date-role --new-id-file",
            "stage_artifact_contract_check.py",
            'artifact?.stage === \'0.8\'',
            "expected exactly one stage=0.8 audit artifact",
        ):
            self.assertIn(required, text)
        self.assertNotIn("--allow-provisional-related", text)

    def test_shared_coverage_contract_changes_trigger_both_workflows(self):
        apply_text = APPLY_WORKFLOW.read_text(encoding="utf-8")
        contract_text = CONTRACT_WORKFLOW.read_text(encoding="utf-8")
        for text in (apply_text, contract_text):
            self.assertIn('schemas/workflow-v4-coverage-axes.json', text)
            self.assertIn('scripts/workflow_v4_coverage_axes.mjs', text)

    def test_manual_direct_add_schema_and_runtime_reject_noop(self):
        schema = json.loads(DIRECT_SCHEMA.read_text(encoding="utf-8"))
        operations = schema["properties"]["operations"]
        self.assertIn("anyOf", operations)
        self.assertEqual(len(operations["anyOf"]), 3)
        self.assertTrue(all(
            next(iter(branch["properties"].values())).get("minItems") == 1
            for branch in operations["anyOf"]
        ))
        hardener = DIRECT_HARDENER.read_text(encoding="utf-8")
        self.assertIn("BLOCKED_MANUAL_DIRECT_ADD_EMPTY_OPERATION", hardener)
        self.assertIn("validateDeclaredOperationPresence(manifest)", hardener)

    def test_prompt_08_requires_bound_audit_artifact(self):
        text = PROMPT_08.read_text(encoding="utf-8")
        self.assertIn('audit_refs[] must contain **exactly one** JSON artifact with `stage: "0.8"`', text)
        self.assertIn('"run_id": "<exact card-run run_id>"', text)
        self.assertIn('"github_merge_ready": [', text)
        self.assertIn("repository workflow reconstructs the final `ID_LEDGER`", text)


if __name__ == "__main__":
    unittest.main()
