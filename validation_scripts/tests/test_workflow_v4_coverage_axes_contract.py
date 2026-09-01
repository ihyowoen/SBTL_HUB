#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AXES = ROOT / "schemas/workflow-v4-coverage-axes.json"
SHARED = ROOT / "scripts/workflow_v4_coverage_axes.mjs"
HARDENER = ROOT / "scripts/validate_card_run_v4_hardening.mjs"
STATUS = ROOT / "scripts/validate_card_run_status_consistency.mjs"
PY_BINDING = ROOT / "validation_scripts/card_run_v4_binding_hardening.py"


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

    def test_python_binding_loads_contract_lazily(self):
        text = PY_BINDING.read_text(encoding="utf-8")
        self.assertIn('schemas/workflow-v4-coverage-axes.json', text)
        self.assertIn("def coverage_axes():", text)
        self.assertNotIn("_AXES = json.loads", text)
        self.assertIn("FAIL [BLOCKED_V4_BINDING]", text)


if __name__ == "__main__":
    unittest.main()
