#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AXES = ROOT / "schemas/workflow-v4-coverage-axes.json"
HARDENER = ROOT / "scripts/validate_card_run_v4_hardening.mjs"
STATUS = ROOT / "scripts/validate_card_run_status_consistency.mjs"
PY_BINDING = ROOT / "validation_scripts/card_run_v4_binding_hardening.py"


def _literal_array(text: str, name: str) -> list[str]:
    match = re.search(rf"const\s+{re.escape(name)}\s*=\s*\[(.*?)\];", text, re.S)
    if not match:
        raise AssertionError(f"{name} literal not found in remaining compatibility validator")
    return re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', match.group(1))


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

    def test_remaining_js_literal_must_exactly_match_shared_contract(self):
        payload = json.loads(AXES.read_text(encoding="utf-8"))
        text = HARDENER.read_text(encoding="utf-8")
        self.assertEqual(_literal_array(text, "REQUIRED_REGION_AXES"), payload["regions"])
        self.assertEqual(_literal_array(text, "REQUIRED_TOPIC_AXES"), payload["topics"])

    def test_other_active_validators_consume_shared_contract(self):
        status = STATUS.read_text(encoding="utf-8")
        binding = PY_BINDING.read_text(encoding="utf-8")
        self.assertIn('from "./workflow_v4_coverage_axes.mjs"', status)
        self.assertNotRegex(status, r"const\s+REQUIRED_REGION_AXES\s*=\s*\[")
        self.assertNotRegex(status, r"const\s+REQUIRED_TOPIC_AXES\s*=\s*\[")
        self.assertIn('schemas/workflow-v4-coverage-axes.json', binding)


if __name__ == "__main__":
    unittest.main()
