#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NODE = shutil.which("node") or "node"
PROMPT_GATE = ROOT / "scripts/validate_prompt_0_8_semantic_gate.mjs"
AUDIT_DISPATCH = ROOT / "scripts/validate_card_run_audits_dispatch.mjs"
V1_HISTORY = ROOT / "scripts/manual_direct_add_v1_history.mjs"

sys.path.insert(0, str(ROOT / "validation_scripts"))
import evidence_qc_v8_check as evidence_qc  # noqa: E402
import date_role_freshness_check as date_role  # noqa: E402
import related_lifecycle_core as related_core  # noqa: E402


class Prompt08RuntimeGateTest(unittest.TestCase):
    def _run(self, command, *, cwd=ROOT):
        result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
        self.assertEqual(
            result.returncode,
            0,
            f"command={command}\nstdout={result.stdout}\nstderr={result.stderr}",
        )
        return result

    def test_runtime_helpers_self_test(self):
        for script in (PROMPT_GATE, AUDIT_DISPATCH, V1_HISTORY):
            self._run([NODE, str(script), "--self-test"])

    def test_prompt_gate_produces_json_scope_all_three_python_consumers_parse(self):
        with tempfile.TemporaryDirectory(prefix="prompt-0-8-fixture-", dir=ROOT) as tmp:
            fixture = Path(tmp)
            relative = fixture.relative_to(ROOT).as_posix()
            full = {
                "cards": [
                    {"id": "NEW", "source_spec_id": "SPEC_NEW"},
                    {"id": "OLD"},
                ]
            }
            run = {
                "run_id": "runtime-regression",
                "base_main_commit_sha": "a" * 40,
                "base_full_blob_sha": "b" * 40,
                "operations": {
                    "insert": [{"card": {"id": "NEW", "source_spec_id": "SPEC_NEW"}}],
                    "update": [],
                    "related_add": [
                        {
                            "source_id": "NEW",
                            "target_id": "OLD",
                            "source_spec_id": "SPEC_NEW",
                            "identity_card_id": "NEW",
                            "relation_type": "distinct_follow_up",
                            "lineage_reason": "new evidence",
                            "event_stage_relationship": "successor",
                            "direction": "reciprocal",
                            "patches": [
                                {"card_id": "NEW"},
                                {"card_id": "OLD"},
                            ],
                        }
                    ],
                },
                "audit_refs": [f"{relative}/merge-prep.json"],
            }
            merge_prep = {
                "stage": "0.8",
                "status": "GITHUB_MERGE_READY",
                "run_id": run["run_id"],
                "base_main_commit_sha": run["base_main_commit_sha"],
                "base_full_blob_sha": run["base_full_blob_sha"],
                "github_merge_ready": [{"id": "NEW"}],
            }
            (fixture / "full.json").write_text(json.dumps(full), encoding="utf-8")
            (fixture / "run.json").write_text(json.dumps(run), encoding="utf-8")
            (fixture / "merge-prep.json").write_text(json.dumps(merge_prep), encoding="utf-8")
            ledger = fixture / "ledger.json"

            result = self._run(
                [
                    NODE,
                    str(PROMPT_GATE),
                    "--run",
                    f"{relative}/run.json",
                    "--full",
                    f"{relative}/full.json",
                    "--ledger",
                    str(ledger),
                ]
            )
            self.assertEqual(result.stdout, f"{relative}/merge-prep.json")
            payload = json.loads(ledger.read_text(encoding="utf-8"))
            self.assertEqual(payload["ids"], ["NEW"])
            self.assertEqual(payload["operation_ids"], ["NEW"])
            self.assertNotIn("OLD", payload["ids"])

            for loader in (related_core.load_ids, evidence_qc.load_ids, date_role.load_ids):
                self.assertEqual(loader(str(ledger)), {"NEW"})

    def test_reciprocal_patch_only_endpoint_is_not_strict_current_run_scope(self):
        self.test_prompt_gate_produces_json_scope_all_three_python_consumers_parse()


if __name__ == "__main__":
    unittest.main()
