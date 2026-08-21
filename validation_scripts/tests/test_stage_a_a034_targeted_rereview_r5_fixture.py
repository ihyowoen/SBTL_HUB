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
FIX = Path(__file__).resolve().parent / "fixtures"
PROMPT = ROOT / "docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md"
EXPECTED_R4_SHA256 = "7c57e832a34bb1284893cd843445833ab16beb4bdf092c6006d5b7334e2e46e8"
EXPECTED_R4_BYTES = 41077
EXPECTED_R5_SHA256 = "dc61c625c3e6e1d736da0b5cf3b428b5593876a62edef3c81c844a31a5c88db8"
EXPECTED_R5_BYTES = 41655
EXPECTED_PROMPT_SHA256 = "0795fb16b89dc320a26e5ecb05965ffc67b73e06137e10a5c2a8132c01a846bc"
EXPECTED_MAIN = "75e98148ae4c7af6234799cdd0852a181b11081b"
EXPECTED_TREE = "b7cc7cd0e7c1d06191017aa3882586e0dbe8e976"
R4_CHUNKS = [
    "stage_a_a034_r4_exact2k_00.txt",
    "stage_a_a034_r4_exact2k_01.txt",
    "stage_a_a034_r4_exact2k_02.txt",
    "stage_a_a034_r4_exact1k_03a.txt",
    "stage_a_a034_r4_exact1k_03b.txt",
    "stage_a_a034_r4_exact1k_04a.txt",
    "stage_a_a034_r4_exact1k_04b.txt",
]


def build_r4_bytes() -> bytes:
    encoded = "".join((FIX / name).read_text(encoding="utf-8").strip() for name in R4_CHUNKS)
    raw = zlib.decompress(base64.b64decode(encoded))
    assert len(raw) == EXPECTED_R4_BYTES
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_R4_SHA256
    return raw


def materialize_r5_bytes() -> bytes:
    d = json.loads(build_r4_bytes().decode("utf-8"))
    old = d["summary"]["follow_up_candidate_ids"]
    assert old == ["REVIEW_0_7C_A034_STALE_REREVIEW_R3"]
    d["summary"]["follow_up_candidate_ids"] = ["STD26_A_034"]
    d["schema"] = "sbtl_stage_a_0_7c_targeted_rereview_a034_r5_current_v3_candidate_id_normalized"
    d["status"] = "PASS_STAGE_A_A034_TARGETED_REREVIEW_CURRENT_RUN_WATCHLIST__REPO_VALIDATION_PENDING"
    d["r5_schema_materialization"] = {
        "change_scope": "summary.follow_up_candidate_ids canonical candidate-ID normalization only",
        "previous_value": old,
        "new_value": ["STD26_A_034"],
        "validator_basis": "current Stage A V3 completeness resolves candidate identity as spec_id before review_pool_item_id",
        "substantive_disposition_changed": False,
        "decision_news_value_score_changed": False,
        "visible_content_changed": False,
        "source_or_evidence_changed": False,
        "external_web_or_body_fetch_performed": False,
    }
    raw = (json.dumps(d, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    assert len(raw) == EXPECTED_R5_BYTES
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_R5_SHA256
    return raw


class TestStageAA034TargetedRereviewR5(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = materialize_r5_bytes()
        cls.data = json.loads(raw.decode("utf-8"))
        cls.tmp = tempfile.TemporaryDirectory()
        cls.artifact = Path(cls.tmp.name) / "stage_a_a034_r5.json"
        cls.artifact.write_bytes(raw)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_repo(self, *args: str):
        p = subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(p.returncode, 0, msg=f"STDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}")
        return p

    def test_00_exact_r4_to_r5_materialization_prompt_and_main_lock(self):
        raw = self.artifact.read_bytes()
        self.assertEqual(len(raw), EXPECTED_R5_BYTES)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), EXPECTED_R5_SHA256)
        self.assertEqual(hashlib.sha256(PROMPT.read_bytes()).hexdigest(), EXPECTED_PROMPT_SHA256)
        self.assertEqual(self.data["stage_prompt_sha256"], EXPECTED_PROMPT_SHA256)
        self.assertEqual(self.data["source_prompt_sha256"], EXPECTED_PROMPT_SHA256)
        self.assertEqual(self.data["current_main_sha"], EXPECTED_MAIN)
        self.assertEqual(self.data["current_main_tree_sha"], EXPECTED_TREE)

    def test_01_accounting_watchlist_and_canonical_follow_up_id(self):
        d = self.data
        s = d["summary"]
        self.assertEqual(d["story_count"], 1)
        self.assertEqual(s["total_ledger_count"], 1)
        self.assertTrue(s["ledger_matches_story_count"])
        self.assertEqual(s["strict_passed_spec_count"], 0)
        self.assertEqual(s["candidate_review_pool_count"], 0)
        self.assertEqual(s["watchlist_context_pool_count"], 1)
        self.assertEqual(s["rejected_count"], 0)
        self.assertEqual(s["follow_up_candidate_ids"], ["STD26_A_034"])
        item = d["watchlist_context_pool"][0]
        self.assertEqual(item["spec_id"], "STD26_A_034")
        self.assertEqual(item["review_pool_partition"], "watchlist_context_pool")
        self.assertEqual(d["decision_ledger"][0]["ledger_decision"], "watchlist_context_pool")

    def test_02_structural_v3_score_staleness_and_review_gate(self):
        item = self.data["watchlist_context_pool"][0]
        self.assertEqual(item["decision_news_value_score"], 39)
        self.assertEqual(item["decision_value_classification"], "context_or_reinforcement")
        self.assertEqual(sum(item["decision_value_breakdown"].values()), 39)
        self.assertEqual(item["execution_credibility_gate"]["status"], "REVIEW")
        self.assertEqual(item["independent_cardability_gate"]["status"], "REVIEW")
        self.assertEqual(item["independent_cardability_gate"]["full_schema_viability"], "PASS")
        self.assertFalse(item["independent_cardability_gate"]["distinct_event_or_stage_progression"])
        self.assertEqual(item["staleness"]["event_date"], "2026-07-21")
        self.assertEqual(item["staleness"]["publication_date"], "2026-08-08")
        self.assertEqual(item["staleness"]["staleness_gap_days"], 16)
        self.assertFalse(item["staleness"]["fresh_followup"])
        self.assertFalse(item["staleness"]["staleness_override"])
        self.assertEqual(item["staleness"]["decision"], "stale_warm_no_fresh_followup")
        self.assertEqual(item["baseline_follow_up_relation"], "same_historical_event_no_fresh_follow_up")

    def test_03_review_ledger_and_future_reopen_contract(self):
        d = self.data
        self.assertEqual(d["review_pool_carry_forward_ledger_status"], "PASS")
        self.assertEqual(d["review_pool_partition_status"], "PASS")
        self.assertEqual(len(d["review_pool_resolution_ledger"]), 1)
        item = d["watchlist_context_pool"][0]
        row = d["review_pool_resolution_ledger"][0]
        self.assertEqual(row["review_pool_item_id"], item["review_pool_item_id"])
        self.assertEqual(row["original_review_pool_partition"], "watchlist_context_pool")
        self.assertEqual(row["current_disposition"], "watchlist_context_pool")
        self.assertEqual(row["carry_forward_policy"], "carry_forward_to_watchlist")
        self.assertTrue(row["whether_user_authorization_required"])
        checkpoints = " ".join(item["next_confirmation_points"]).lower()
        for term in ("registration", "shareholder", "financing", "closing", "listing"):
            self.assertIn(term, checkpoints)
        self.assertIn("distinct fresh transaction milestone", item["promotion_precondition"])
        self.assertTrue(item["recommended_monitoring_action"].strip())
        self.assertIn("do not create a new current-run card", item["recommended_monitoring_action"].lower())

    def test_04_stage_a_boundary_and_next_call_discipline(self):
        d = self.data
        self.assertEqual(d["stage_a_external_web_search_count"], 0)
        self.assertEqual(d["stage_a_article_body_fetch_count"], 0)
        self.assertEqual(d["source_quote_created_count"], 0)
        self.assertEqual(d["fact_sources_created_count"], 0)
        self.assertEqual(d["card_copy_created_count"], 0)
        b = d["boundary"]
        self.assertEqual(b["stage_b_authorized_ids"], [])
        self.assertFalse(b["stage_c_performed"])
        self.assertFalse(b["prompt_0_4_or_later_performed"])
        self.assertFalse(b["prompt_0_8_performed"])
        self.assertFalse(b["main_write_performed"])
        self.assertFalse(b["pr_or_merge_performed"])
        nxt = d["next_call_recommendation"]
        self.assertEqual(nxt["recommended_next_call"], "retrospective or watchlist context review")
        self.assertEqual(nxt["recommended_prompt_id"], "Prompt 1.1 or separate context review prompt")
        self.assertEqual(nxt["recommended_input_universe"], "watchlist_context_pool[] only, not Stage B")

    def test_05_generic_stage_artifact_contract(self):
        p = self.run_repo("validation_scripts/stage_artifact_contract_check.py", "A", str(self.artifact))
        self.assertIn('"status": "PASS"', p.stdout)
        self.assertIn('"missing_count": 0', p.stdout)

    def test_06_generic_stage_lineage_and_v3_contract(self):
        p = self.run_repo("validation_scripts/stage_lineage_contract_check.py", "stage_a", str(self.artifact))
        self.assertIn("RESULT: PASS_STAGE_A_SCHEMA_CONTRACT", p.stdout)


if __name__ == "__main__":
    unittest.main()
