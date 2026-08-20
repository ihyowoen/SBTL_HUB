from __future__ import annotations

import base64
import csv
import hashlib
import io
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
EXPECTED_ARTIFACT_SHA256 = "1186ecbb1982b8497c56b3e0a9ceb6dde9fc3a700daf89f9cf7e3f5004c415e3"
EXPECTED_PROMPT_SHA256 = "0795fb16b89dc320a26e5ecb05965ffc67b73e06137e10a5c2a8132c01a846bc"
EXPECTED_MAIN = "75e98148ae4c7af6234799cdd0852a181b11081b"
CHUNKS = ["stage_a_a034_r2_payload_00.txt", "stage_a_a034_r2_payload_01.txt"]
CSV_FIX = FIX / "stage_a_a034_r2_decisions.csv"
REPORT_FIX = FIX / "stage_a_a034_r2_report.md"


def build_bytes() -> bytes:
    encoded = "".join((FIX / name).read_text(encoding="utf-8").strip() for name in CHUNKS)
    raw = zlib.decompress(base64.b64decode(encoded))
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_ARTIFACT_SHA256
    return raw


class TestStageAA034TargetedRereviewR2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = build_bytes()
        cls.data = json.loads(raw.decode("utf-8"))
        cls.tmp = tempfile.TemporaryDirectory()
        cls.artifact = Path(cls.tmp.name) / "stage_a_a034_r2.json"
        cls.artifact.write_bytes(raw)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_repo(self, *args: str):
        p = subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(p.returncode, 0, msg=f"STDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}")
        return p

    def test_00_exact_artifact_prompt_and_main_lock(self):
        self.assertEqual(hashlib.sha256(self.artifact.read_bytes()).hexdigest(), EXPECTED_ARTIFACT_SHA256)
        self.assertEqual(hashlib.sha256(PROMPT.read_bytes()).hexdigest(), EXPECTED_PROMPT_SHA256)
        self.assertEqual(self.data["stage_prompt_sha256"], EXPECTED_PROMPT_SHA256)
        self.assertEqual(self.data["current_main_sha"], EXPECTED_MAIN)

    def test_01_targeted_accounting_and_watchlist_routing(self):
        d = self.data
        self.assertEqual(d["story_count"], 1)
        self.assertEqual(d["summary"]["total_ledger_count"], 1)
        self.assertTrue(d["summary"]["ledger_matches_story_count"])
        self.assertEqual(d["summary"]["strict_passed_spec_count"], 0)
        self.assertEqual(d["summary"]["candidate_review_pool_count"], 0)
        self.assertEqual(d["summary"]["watchlist_context_pool_count"], 1)
        self.assertEqual(d["summary"]["rejected_count"], 0)
        self.assertEqual(d["strict_passed_spec"], [])
        self.assertEqual(d["candidate_review_pool"], [])
        self.assertEqual(d["rejected"], [])
        item = d["watchlist_context_pool"][0]
        self.assertEqual(item["spec_id"], "STD26_A_034")
        self.assertEqual(item["review_pool_partition"], "watchlist_context_pool")
        self.assertEqual(item["staleness"]["preserved_upstream_staleness_gap_days"], 16)
        self.assertFalse(item["staleness"]["fresh_followup"])
        self.assertFalse(item["staleness"]["staleness_override"])
        self.assertEqual(item["staleness"]["decision"], "stale_warm_no_fresh_followup")
        self.assertFalse(d["next_call_recommendation"]["a034_stage_b_eligible"])
        self.assertFalse(d["next_call_recommendation"]["a034_stage_c_eligible"])

    def test_02_stage_a_boundary_no_fetch_no_card_copy(self):
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

    def test_03_review_pool_resolution_ledger_complete(self):
        d = self.data
        self.assertEqual(d["review_pool_carry_forward_ledger_status"], "PASS")
        self.assertEqual(d["review_pool_partition_status"], "PASS")
        self.assertEqual(len(d["review_pool_resolution_ledger"]), 1)
        item = d["watchlist_context_pool"][0]
        row = d["review_pool_resolution_ledger"][0]
        self.assertEqual(row["review_pool_item_id"], item["review_pool_item_id"])
        self.assertEqual(row["current_disposition"], "watchlist_context_pool")
        self.assertEqual(row["carry_forward_policy"], "future_fresh_stage_a_only")
        self.assertTrue(row["whether_user_authorization_required"])

    def test_04_csv_contract_and_report_boundary(self):
        rows = list(csv.DictReader(io.StringIO(CSV_FIX.read_text(encoding="utf-8-sig"))))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        required = {"story_id","region","original_triage_status","status_detail","stage_a_bucket","ledger_decision","headline","reason","baseline_relation","duplicate_risk","staleness_decision","event_date","source_tier_estimate","source_access_risk","format_risk_tags","execution_anchor_type","execution_anchor_strength","structural_value_override_applied","anchor_classes","evidence_needed_for_stage_b","why_execution_event_not_required","strict_pass_gate_status","strict_pass_gate_reason","review_pool_partition","review_pool_subtype","review_pool_partition_reason","promotion_precondition","bounded_review_question","recommended_next_action"}
        self.assertFalse(required - set(row))
        self.assertEqual(row["story_id"], "20260809_221256::TF_0012")
        self.assertEqual(row["stage_a_bucket"], "review_pool")
        self.assertEqual(row["review_pool_partition"], "watchlist_context_pool")
        self.assertEqual(row["strict_pass_gate_status"], "blocked_to_review_pool")
        report = REPORT_FIX.read_text(encoding="utf-8")
        self.assertIn("strict_passed_spec: **0**", report)
        self.assertIn("watchlist_context_pool: **1**", report)
        self.assertIn("No external web search, no article body fetch, no card copy", report)

    def test_05_generic_stage_artifact_contract(self):
        p = self.run_repo("validation_scripts/stage_artifact_contract_check.py", "A", str(self.artifact))
        self.assertIn('"status": "PASS"', p.stdout)
        self.assertIn('"missing_count": 0', p.stdout)

    def test_06_generic_stage_lineage_contract(self):
        p = self.run_repo("validation_scripts/stage_lineage_contract_check.py", "stage_a", str(self.artifact))
        self.assertIn("RESULT: PASS_STAGE_A_SCHEMA_CONTRACT", p.stdout)


if __name__ == "__main__":
    unittest.main()
