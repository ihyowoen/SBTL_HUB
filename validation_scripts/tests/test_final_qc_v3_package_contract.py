#!/usr/bin/env python3
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class FinalQcV3PackageContractTest(unittest.TestCase):
    def test_publish_ready_non_execution_items_preserve_complete_package(self):
        prompt = (ROOT / "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md").read_text(encoding="utf-8")
        required = [
            "selected_anchor_path = v3_non_execution",
            "structural_value_override_applied: true",
            "anchor_classes[]",
            "evidence_needed_for_stage_b[]",
            "why_execution_event_not_required",
            "prior_state",
            "new_verified_fact",
            "changed_judgment",
            "must remain available to Prompt 0.8",
        ]
        for token in required:
            self.assertIn(token, prompt)


if __name__ == "__main__":
    unittest.main()
