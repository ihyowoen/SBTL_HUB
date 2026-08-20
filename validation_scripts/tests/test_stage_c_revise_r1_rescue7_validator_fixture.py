from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_B64 = Path(__file__).resolve().parent / "fixtures/stage_c_revise_r1_rescue7_R2_payload.b64"
EXPECTED_ARTIFACT_SHA256 = "1ab37bcdf5e18b5fd099d8df463400e7bb747706dbd59c643d160f4d033a58e7"
EXPECTED_PROMPT_SHA256 = "5079bd1f6c5c5160de965e69aa8a53167da4d33cda9e172768c8d8e55a992b94"
PROMPT = ROOT / "docs/llm_prompts/v1/05_PROMPT_0_3R_Stage_C_Revise.md"
V3_FIELDS = [
    "structural_value_override_applied", "structural_value_override_reason", "anchor_classes",
    "evidence_needed_for_stage_b", "why_execution_event_not_required", "prior_state",
    "new_verified_fact", "changed_judgment", "uncertainty_resolved", "remaining_uncertainty",
    "incremental_information", "baseline_expectation_changed", "decision_relevance",
    "next_confirmation_points",
]


def build_fixture_bytes() -> bytes:
    encoded = FIXTURE_B64.read_text(encoding="utf-8").strip()
    raw = zlib.decompress(base64.b64decode(encoded))
    actual = hashlib.sha256(raw).hexdigest()
    if actual != EXPECTED_ARTIFACT_SHA256:
        raise AssertionError(f"artifact SHA mismatch: expected {EXPECTED_ARTIFACT_SHA256}, got {actual}")
    return raw


class TestStageCReviseR1Rescue7ValidatorFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = build_fixture_bytes()
        cls.data = json.loads(raw.decode("utf-8"))
        cls.tmp = tempfile.TemporaryDirectory()
        cls.fixture = Path(cls.tmp.name) / "stage_c_revise_r1_rescue7_R2.json"
        cls.fixture.write_bytes(raw)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def _run(self, *args: str):
        proc = subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(proc.returncode, 0, msg=f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
        return proc

    def test_prompt_hash_and_prompt_read_gate(self):
        actual_prompt_sha = hashlib.sha256(PROMPT.read_bytes()).hexdigest()
        self.assertEqual(actual_prompt_sha, EXPECTED_PROMPT_SHA256)
        self.assertEqual(self.data["stage_prompt_file"], "docs/llm_prompts/v1/05_PROMPT_0_3R_Stage_C_Revise.md")
        self.assertEqual(self.data["stage_prompt_sha256"], actual_prompt_sha)
        self.assertEqual(self.data["stage_prompt_sha256_status"], "PASS_REPO_CHECKOUT_HASH_LOCKED")

    def test_repo_native_stage_artifact_contract(self):
        proc = self._run("validation_scripts/stage_artifact_contract_check.py", "C", str(self.fixture))
        result = json.loads(proc.stdout)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["item_count"], 7)
        self.assertEqual(result["missing_count"], 0)

    def test_repo_native_stage_lineage_contract(self):
        proc = self._run("validation_scripts/stage_lineage_contract_check.py", "stage_c", str(self.fixture))
        self.assertIn("RESULT: PASS_STAGE_C_SCHEMA_CONTRACT", proc.stdout)

    def test_prompt_0_3r_accounting_state_and_boundaries(self):
        d = self.data
        self.assertEqual(d["stage"], "stage_c_revise")
        self.assertEqual(d["revision_pass"], "r1")
        self.assertEqual(d["revised_draft_card_input_count"], 7)
        self.assertEqual(d["accepted_fact_safe_count"], 7)
        self.assertEqual(d["revise_required_again_count"], 0)
        self.assertEqual(d["rejected_count"], 0)
        self.assertEqual(d["support_source_only_count"], 0)
        self.assertEqual(d["deferred_review_pool_count"], 0)
        self.assertEqual(d["outcome_total_count"], 7)
        self.assertTrue(d["accounting_matches_revised_draft_card_input_count"])
        self.assertTrue(d["revise_strict_gate_guard_applied"])
        self.assertEqual(d["accepted_fact_safe_with_missing_strict_gate_count"], 0)
        self.assertFalse(d["source_augmentation_performed"])
        self.assertEqual(d["new_source_url_count"], 0)
        self.assertEqual(d["next_call_recommendation"]["recommended_prompt_id"], "Prompt 0.4")
        self.assertEqual(d["boundary"]["repo_hosted_stage_exit_validation"], "PENDING_EXACT_R2_FIXTURE")

        accepted = d["accepted_fact_safe"]
        self.assertEqual(len(accepted), 7)
        routes = {"execution": 0, "v3_non_execution": 0}
        for card in accepted:
            self.assertEqual(card["state"], "accepted_fact_safe")
            self.assertTrue(card["stage_c_revise_only"])
            self.assertTrue(card["prior_issue_resolved"])
            self.assertTrue(card["strict_gate_acceptance_guard_applied"])
            self.assertEqual(card["accepted_pool_lineage_status"], "PASS")
            self.assertFalse(card["publish_ready"])
            self.assertFalse(card["addable_merge_safe"])
            self.assertFalse(card["evidence_complete"])
            self.assertFalse(card["source_claim_covered"])
            self.assertFalse(card["content_enriched"])
            self.assertFalse(card["language_terminology_polished"])
            self.assertFalse(card["github_merge_ready"])
            self.assertTrue(card["needs_post_acceptance_duplicate_review"])
            self.assertTrue(card["needs_post_acceptance_evidence_qc"])
            self.assertTrue(card["fact_sources"])
            for fs in card["fact_sources"]:
                self.assertTrue(fs.get("source_url"))
                self.assertTrue(fs.get("claim"))
                self.assertTrue(fs.get("source_quote"))
                self.assertIn(fs.get("source_quote_status"), {
                    "body_quote_verified", "official_material_quote_verified", "document_quote_verified"
                })

            anchor = card["anchor_path_validation"]
            route = anchor["selected_anchor_path"]
            self.assertIn(route, routes)
            routes[route] += 1
            self.assertTrue(anchor["anchor_path_qc_passed"])
            self.assertTrue(anchor["non_applicable_anchor_path_reason"])
            if route == "execution":
                self.assertEqual(anchor["execution_anchor_qc_status"], "pass")
                self.assertEqual(anchor["structural_value_override_qc_status"], "not_applicable")
            else:
                self.assertEqual(anchor["execution_anchor_qc_status"], "not_applicable")
                self.assertEqual(anchor["structural_value_override_qc_status"], "pass")
                for field in V3_FIELDS:
                    self.assertIn(field, card)
                    self.assertNotIn(card[field], (None, "", [], {}))

        self.assertEqual(routes, {"execution": 5, "v3_non_execution": 2})
        summary = d["anchor_path_revision_validation_summary"]
        self.assertEqual(summary["accepted_with_execution_path_count"], 5)
        self.assertEqual(summary["accepted_with_v3_non_execution_path_count"], 2)
        self.assertEqual(summary["unresolved_or_failed_path_count"], 0)


if __name__ == "__main__":
    unittest.main()
