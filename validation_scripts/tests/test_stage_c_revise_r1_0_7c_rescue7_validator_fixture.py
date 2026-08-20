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
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
EXPECTED_ARTIFACT_SHA256 = "1ab37bcdf5e18b5fd099d8df463400e7bb747706dbd59c643d160f4d033a58e7"
EXPECTED_PROMPT_SHA256 = "5079bd1f6c5c5160de965e69aa8a53167da4d33cda9e172768c8d8e55a992b94"
PROMPT_PATH = ROOT / "docs/llm_prompts/v1/05_PROMPT_0_3R_Stage_C_Revise.md"
CHUNK_NAMES = [
    "stage_c_revise_r1_R2_payload_00.txt",
    "stage_c_revise_r1_R2_payload_01.txt",
    "stage_c_revise_r1_R2_payload_02.txt",
    "stage_c_revise_r1_R2_payload_03.txt",
    "stage_c_revise_r1_R2_payload_04.txt",
]
EXPECTED_IDS = {
    "STD26_A_007", "STD26_A_011", "STD26_A_023", "STD26_A_035",
    "STD26_A_036", "STD26_A_049", "STD26_A_056",
}
ALLOWED_QUOTE_STATUS = {
    "body_quote_verified", "official_material_quote_verified", "document_quote_verified",
}
V3_FIELDS = [
    "structural_value_override_applied", "structural_value_override_reason", "anchor_classes",
    "evidence_needed_for_stage_b", "why_execution_event_not_required", "prior_state",
    "new_verified_fact", "changed_judgment", "uncertainty_resolved", "remaining_uncertainty",
    "incremental_information", "baseline_expectation_changed", "decision_relevance",
    "next_confirmation_points",
]
ANCHOR_HASHES = {
    "STD26_A_007": "6a08a4f9db23fbaa8a11d20d0368b6e6e96b2a688631c7844ae5ba0b1269f56f",
    "STD26_A_011": "e132ba970e4dfd2cb0814b6bfe6247a8160d9aafb655cf605f35208a4c51bb60",
    "STD26_A_023": "e132ba970e4dfd2cb0814b6bfe6247a8160d9aafb655cf605f35208a4c51bb60",
    "STD26_A_035": "6a08a4f9db23fbaa8a11d20d0368b6e6e96b2a688631c7844ae5ba0b1269f56f",
    "STD26_A_036": "6a08a4f9db23fbaa8a11d20d0368b6e6e96b2a688631c7844ae5ba0b1269f56f",
    "STD26_A_049": "6a08a4f9db23fbaa8a11d20d0368b6e6e96b2a688631c7844ae5ba0b1269f56f",
    "STD26_A_056": "6a08a4f9db23fbaa8a11d20d0368b6e6e96b2a688631c7844ae5ba0b1269f56f",
}
V3_PACKAGE_HASHES = {
    "STD26_A_011": "6016f93074b5cc5da031e772e81ea8099887eae65ff6facb36aa3e5e552c801f",
    "STD26_A_023": "6dac15a5ca5e8f48fd2dca14b4a3d1934128a0aaf5177559c6c833c12742ca9e",
}


def canonical_hash(value) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def build_fixture_bytes() -> bytes:
    encoded = "".join((FIXTURE_DIR / name).read_text(encoding="utf-8").strip() for name in CHUNK_NAMES)
    raw = zlib.decompress(base64.b64decode(encoded))
    actual = hashlib.sha256(raw).hexdigest()
    if actual != EXPECTED_ARTIFACT_SHA256:
        raise AssertionError(f"fixture SHA mismatch: expected {EXPECTED_ARTIFACT_SHA256}, got {actual}")
    return raw


class TestStageCReviseR107CRescue7ValidatorFixture(unittest.TestCase):
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

    def test_00_exact_artifact_and_prompt_hash(self):
        self.assertEqual(hashlib.sha256(self.fixture.read_bytes()).hexdigest(), EXPECTED_ARTIFACT_SHA256)
        self.assertEqual(hashlib.sha256(PROMPT_PATH.read_bytes()).hexdigest(), EXPECTED_PROMPT_SHA256)
        self.assertEqual(self.data["stage_prompt_sha256"], EXPECTED_PROMPT_SHA256)
        self.assertEqual(self.data["stage_prompt_sha256_status"], "PASS_REPO_CHECKOUT_HASH_LOCKED")

    def test_01_prompt_0_3r_accounting_and_boundaries(self):
        d = self.data
        required = {
            "stage", "revision_pass", "run_tag", "run_label", "revised_draft_card_input_count",
            "accepted_fact_safe_count", "revise_required_again_count", "rejected_count",
            "support_source_only_count", "deferred_review_pool_count", "outcome_total_count",
            "accounting_matches_revised_draft_card_input_count", "accepted_fact_safe",
            "revise_required_again", "rejected", "support_source_only", "deferred_review_pool",
            "decision_ledger", "claim_coverage_review", "anchor_path_revision_validation_summary",
            "revise_strict_gate_guard_applied", "revise_strict_gate_guard_findings",
            "next_call_recommendation",
        }
        self.assertFalse(required - set(d))
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
        self.assertFalse(d["source_augmentation_performed"])
        self.assertEqual(d["new_source_url_count"], 0)
        self.assertFalse(d["later_discovered_evidence_used"])
        self.assertEqual(d["next_call_recommendation"]["recommended_prompt_id"], "Prompt 0.4")
        self.assertTrue(d["boundary"]["prompt_0_4_not_run"])
        self.assertTrue(d["boundary"]["prompt_0_8_not_run"])
        self.assertFalse(d["boundary"]["main_write_performed"])
        self.assertFalse(d["boundary"]["pr_or_merge_performed"])

    def test_02_accepted_item_schema_strict_gate_and_downstream_flags(self):
        items = self.data["accepted_fact_safe"]
        self.assertEqual({item["source_spec_id"] for item in items}, EXPECTED_IDS)
        required = {
            "id", "spec_id", "source_spec_id", "source_story_ids", "stage_b_lineage",
            "strict_gate_acceptance_guard_applied", "accepted_pool_lineage_status",
            "region", "date", "cat", "sub_cat", "signal", "title", "sub", "gate", "fact",
            "implication", "urls", "related", "fact_sources", "related_lineage", "date_role",
            "anchor_path_validation", "state", "revision_pass", "previous_draft_id", "revised_draft_id",
            "stage_c_revise_only", "publish_ready", "prior_issue_resolved",
            "needs_post_acceptance_duplicate_review", "needs_post_acceptance_evidence_qc",
        }
        forbidden_true = {
            "addable_merge_safe", "evidence_complete", "source_claim_covered", "content_enriched",
            "language_terminology_polished", "publish_ready", "github_merge_ready",
        }
        for item in items:
            self.assertFalse(required - set(item), msg=item["source_spec_id"])
            self.assertEqual(item["state"], "accepted_fact_safe")
            self.assertTrue(item["accepted_fact_safe"])
            self.assertTrue(item["stage_c_revise_only"])
            self.assertTrue(item["prior_issue_resolved"])
            self.assertTrue(item["strict_gate_acceptance_guard_applied"])
            self.assertEqual(item["accepted_pool_lineage_status"], "PASS")
            self.assertTrue(item["stage_b_lineage"]["lineage_preserved"])
            self.assertTrue(item["stage_b_lineage"]["strict_gate_check_preserved"])
            self.assertTrue(item["stage_b_lineage"]["anchor_path_validation_preserved"])
            self.assertTrue(item["stage_b_lineage"]["no_new_source_augmentation"])
            self.assertFalse(any(item.get(flag) is True for flag in forbidden_true), msg=item["source_spec_id"])

    def test_03_anchor_paths_and_v3_packages_match_stage_b_revise_locked_hashes(self):
        exec_count = 0
        v3_count = 0
        for item in self.data["accepted_fact_safe"]:
            sid = item["source_spec_id"]
            anchor = item["anchor_path_validation"]
            self.assertEqual(canonical_hash(anchor), ANCHOR_HASHES[sid], msg=sid)
            route = anchor["selected_anchor_path"]
            self.assertTrue(anchor["anchor_path_qc_passed"])
            self.assertTrue(anchor.get("non_applicable_anchor_path_reason"))
            if route == "execution":
                exec_count += 1
                self.assertEqual(anchor["execution_anchor_qc_status"], "pass")
                self.assertEqual(anchor["structural_value_override_qc_status"], "not_applicable")
            elif route == "v3_non_execution":
                v3_count += 1
                self.assertEqual(anchor["execution_anchor_qc_status"], "not_applicable")
                self.assertEqual(anchor["structural_value_override_qc_status"], "pass")
                package = {field: item[field] for field in V3_FIELDS}
                self.assertEqual(canonical_hash(package), V3_PACKAGE_HASHES[sid], msg=sid)
            else:
                self.fail(f"{sid}: unresolved route {route}")
        self.assertEqual(exec_count, 5)
        self.assertEqual(v3_count, 2)

    def test_04_source_audit_quote_quality_and_single_source_exception(self):
        for item in self.data["accepted_fact_safe"]:
            sid = item["source_spec_id"]
            self.assertTrue(item["fact_sources"], msg=sid)
            for row in item["fact_sources"]:
                self.assertTrue(row.get("source_url"), msg=sid)
                self.assertTrue(row.get("claim"), msg=sid)
                self.assertTrue(row.get("source_quote"), msg=sid)
                self.assertIn(row.get("source_quote_status"), ALLOWED_QUOTE_STATUS, msg=sid)
            status = item["source_diversity_status"]
            if status == "PASS_MULTI_SOURCE":
                self.assertGreaterEqual(item["source_unique_url_count"], 2, msg=sid)
                self.assertGreaterEqual(item["source_independent_owner_count"], 2, msg=sid)
                self.assertFalse(item["single_source_exception"]["allowed"], msg=sid)
            elif status == "PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION":
                self.assertEqual(sid, "STD26_A_036")
                self.assertEqual(item["source_independent_owner_count"], 1)
                self.assertTrue(item["single_source_exception"]["allowed"])
            else:
                self.fail(f"{sid}: invalid accepted source_diversity_status={status}")

    def test_05_generic_stage_artifact_contract(self):
        proc = self._run("validation_scripts/stage_artifact_contract_check.py", "C", str(self.fixture))
        self.assertIn('"status": "PASS"', proc.stdout)
        self.assertIn('"missing_count": 0', proc.stdout)
        self.assertIn('"item_count": 7', proc.stdout)

    def test_06_generic_stage_lineage_contract(self):
        proc = self._run("validation_scripts/stage_lineage_contract_check.py", "stage_c", str(self.fixture))
        self.assertIn("RESULT: PASS_STAGE_C_SCHEMA_CONTRACT", proc.stdout)


if __name__ == "__main__":
    unittest.main()
