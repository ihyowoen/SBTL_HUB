#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROMPT_DIR = ROOT / "docs" / "llm_prompts" / "v1"


class PromptOverlayRetirementTest(unittest.TestCase):
    def test_overlay_guard_passes_for_clean_v4_prompts(self):
        completed = subprocess.run(
            [sys.executable, "validation_scripts/apply_prompt_contract_overlays.py", "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("PASS_V4_NO_ACTIVE_PROMPT_OVERLAYS", completed.stdout)

    def test_overlay_application_is_retired(self):
        completed = subprocess.run(
            [sys.executable, "validation_scripts/apply_prompt_contract_overlays.py", "--apply"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("BLOCKED_V4_OVERLAY_APPLICATION_RETIRED", completed.stdout)

    def test_stage_a_has_no_retired_runtime_dependency(self):
        text = (PROMPT_DIR / "01_PROMPT_0_1_Stage_A.md").read_text(encoding="utf-8")
        self.assertNotIn("WORKFLOW_CONTRACT_OVERLAY_", text)
        self.assertNotIn("01A_PROMPT_0_1S_Structural_Value_Override.md", text)
        self.assertIn("EMBEDDED_NEWS_VALUE_SELECTION_V4", text)


if __name__ == "__main__":
    unittest.main()
