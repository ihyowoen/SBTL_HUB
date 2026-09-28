from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "docs" / "llm_prompts" / "v1"


class WorkflowV4ArchitectureTests(unittest.TestCase):
    def test_registry_has_clean_named_stage_model(self):
        registry = json.loads((P / "GOVERNANCE_LIFECYCLE_REGISTRY.json").read_text(encoding="utf-8"))
        self.assertEqual(registry["active_override_or_addendum_count"], 0)
        self.assertEqual(len(registry["active_named_prompts"]), 17)
        self.assertFalse(any("01A_PROMPT_0_1S" in x for x in registry["active_named_prompts"]))
        self.assertIn("docs/MANUAL_DIRECT_ADD_V2.md", registry["active_canonical"])
        self.assertIn("docs/MANUAL_DIRECT_ADD_V1.md", registry["superseded"])
        self.assertEqual(len(registry["bootstrap_read"]), 8)

    def test_stage_a_embeds_news_value_and_related(self):
        text = (P / "01_PROMPT_0_1_Stage_A.md").read_text(encoding="utf-8")
        for token in (
            "EMBEDDED_NEWS_VALUE_SELECTION_V4",
            "execution_credibility_gate",
            "independent_cardability_gate",
            "decision_news_value_score",
            "publication_urgency",
            "related_prepass",
            "structural_non_execution_route",
        ):
            self.assertIn(token, text)
        self.assertNotIn("01A_PROMPT_0_1S_Structural_Value_Override.md", text)

    def test_revise_loops_are_conditional_and_bounded(self):
        master = (P / "00_NEW_RUN_MASTER_PROMPT.md").read_text(encoding="utf-8")
        manifest = (P / "PROMPT_MANIFEST.md").read_text(encoding="utf-8")
        workflow = (ROOT / "docs" / "WORKFLOW.md").read_text(encoding="utf-8")
        self.assertIn("0.2R only for bounded Stage-B repair", master)
        self.assertIn("0.3R only for controlled Stage-C revalidation", master)
        self.assertIn("JIT 0.2 B ⇄ JIT 0.2R", manifest)
        self.assertIn("JIT 0.3 C ⇄ JIT 0.3R", manifest)
        self.assertIn("0.2R and 0.3R are conditional repair loops", manifest)
        self.assertIn("There are no separate ordinary `0.4R`, `0.5R`, `0.6R`, or `0.7R`", workflow)
        self.assertIn("earliest responsible", workflow)
        self.assertIn("stage", workflow.lower())

    def test_addability_is_not_lineage_origin(self):
        text = (P / "06_PROMPT_0_4_Baseline_Revalidation.md").read_text(encoding="utf-8")
        self.assertIn("Addability Revalidation", text)
        self.assertIn("not the first Related audit", text)

    def test_master_prompt_is_launcher(self):
        text = (P / "00_NEW_RUN_MASTER_PROMPT.md").read_text(encoding="utf-8")
        self.assertIn("NEW_RUN_MASTER_PROMPT_V4_1_20260902", text)
        self.assertIn("EMBEDDED_NEWS_VALUE_SELECTION_V4", text)
        self.assertIn("governance_lock_v4.mjs", text)
        self.assertIn("Do **not** pre-load all 17 named-stage prompts", text)

    def test_direct_add_v2_machine_schema(self):
        schema = json.loads((ROOT / "schemas" / "manual-direct-add.v2.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["schema"]["const"], "manual_direct_add_v2")
        self.assertIn("editorial_attestation", schema["required"])

    def test_v4_architecture_script(self):
        p = subprocess.run([sys.executable, "validation_scripts/workflow_v4_architecture_check.py"], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_legacy_overlay_guard(self):
        p = subprocess.run([sys.executable, "validation_scripts/apply_prompt_contract_overlays.py", "--check"], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)


if __name__ == "__main__":
    unittest.main()
