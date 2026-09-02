#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AXES = ROOT / "schemas/workflow-v4-coverage-axes.json"
SHARED = ROOT / "scripts/workflow_v4_coverage_axes.mjs"
HARDENER = ROOT / "scripts/validate_card_run_v4_hardening.mjs"
STATUS = ROOT / "scripts/validate_card_run_status_consistency.mjs"
SCHEMA_VALIDATOR = ROOT / "scripts/validate_json_schema_subset.mjs"
CARD_RUN_SCHEMA = ROOT / "schemas/card-run.v1.schema.json"
HISTORICAL_RUN = ROOT / "runs/2026-08-26/card-run.json"
PY_BINDING = ROOT / "validation_scripts/card_run_v4_binding_hardening.py"
NODE = shutil.which("node") or "node"


class WorkflowV4CoverageAxesContractTest(unittest.TestCase):
    def test_shared_axes_contract_is_well_formed(self):
        payload = json.loads(AXES.read_text(encoding="utf-8"))
        self.assertEqual(payload.get("schema"), "workflow_v4_coverage_axes_v1")
        for field in ("regions", "topics"):
            values = payload.get(field)
            self.assertIsInstance(values, list)
            self.assertTrue(values)
            self.assertEqual(len(values), len(set(values)))
            self.assertTrue(all(isinstance(value, str) and value.strip() for value in values))

    def test_active_js_validators_consume_shared_contract_without_literals(self):
        for path in (HARDENER, STATUS):
            text = path.read_text(encoding="utf-8")
            self.assertIn('from "./workflow_v4_coverage_axes.mjs"', text, path.name)
            self.assertIn("loadWorkflowV4CoverageAxes", text, path.name)
            self.assertNotIn("const REQUIRED_REGION_AXES = [", text, path.name)
            self.assertNotIn("const REQUIRED_TOPIC_AXES = [", text, path.name)

    def test_shared_js_loader_is_lazy_and_fail_closed_at_call_site(self):
        text = SHARED.read_text(encoding="utf-8")
        self.assertIn("export function loadWorkflowV4CoverageAxes", text)
        self.assertNotIn("export const REQUIRED_REGION_AXES", text)
        self.assertNotIn("export const REQUIRED_TOPIC_AXES", text)
        self.assertIn("CoverageAxesContractError", text)
        self.assertIn("WORKFLOW_V4_COVERAGE_AXES_PATH", text)

    def test_python_binding_loads_contract_lazily(self):
        text = PY_BINDING.read_text(encoding="utf-8")
        self.assertIn('schemas/workflow-v4-coverage-axes.json', text)
        self.assertIn("def coverage_axes():", text)
        self.assertNotIn("_AXES = json.loads", text)
        self.assertIn("FAIL [BLOCKED_V4_BINDING]", text)
        self.assertIn("WORKFLOW_V4_COVERAGE_AXES_PATH", text)

    def test_corrupt_shared_axes_contract_is_normalized_without_touching_tracked_file(self):
        with tempfile.TemporaryDirectory(prefix="workflow-v4-axes-") as tmp:
            corrupt = Path(tmp) / "workflow-v4-coverage-axes.json"
            corrupt.write_text('{"schema":"broken","regions":[],"topics":[]}', encoding="utf-8")
            env = os.environ.copy()
            env["WORKFLOW_V4_COVERAGE_AXES_PATH"] = str(corrupt)
            cases = [
                ([NODE, str(STATUS), "--self-test"], "FAIL [BLOCKED_COVERAGE_AXIS_CONTRACT]"),
                ([NODE, str(HARDENER), "--self-test"], "FAIL [BLOCKED_COVERAGE_AXIS_CONTRACT]"),
                ([sys.executable, str(PY_BINDING), "--self-test"], "FAIL [BLOCKED_V4_BINDING]"),
            ]
            for command, marker in cases:
                result = subprocess.run(
                    command,
                    cwd=ROOT,
                    env=env,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                combined = f"{result.stdout}\n{result.stderr}"
                self.assertNotEqual(result.returncode, 0, command)
                self.assertIn(marker, combined, command)
                self.assertNotIn("Traceback", combined, command)
        self.assertEqual(
            json.loads(AXES.read_text(encoding="utf-8")).get("schema"),
            "workflow_v4_coverage_axes_v1",
        )

    def test_2026_08_26_historical_run_remains_card_run_v1_schema_compatible(self):
        result = subprocess.run(
            [
                NODE,
                str(SCHEMA_VALIDATOR),
                "--schema",
                str(CARD_RUN_SCHEMA),
                "--instance",
                str(HISTORICAL_RUN),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, f"stdout={result.stdout}\nstderr={result.stderr}")

    def test_v4_production_binding_still_requires_insert_source_spec_id(self):
        js_text = HARDENER.read_text(encoding="utf-8")
        py_text = PY_BINDING.read_text(encoding="utf-8")
        self.assertIn("card.source_spec_id is required to bind the formal stage chain", js_text)
        self.assertIn("card.source_spec_id required", py_text)


if __name__ == "__main__":
    unittest.main()
