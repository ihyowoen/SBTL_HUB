import base64, gzip, hashlib, json, subprocess, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / "validation_scripts" / "tests" / "fixtures"
EXPECTED_MAIN = "75e98148ae4c7af6234799cdd0852a181b11081b"
EXPECTED_TREE = "b7cc7cd0e7c1d06191017aa3882586e0dbe8e976"
EXPECTED_SHA256 = "0a45b3869c55413340b14f43cc65c806a67844eaf6a4cc80239607c7eab56ecd"
CHUNKS = ['a022_supplemental_earnings_r2_payload_01.b64']
REQUIRED = ['earnings_release_checked', 'filing_checked', 'ir_deck_checked', 'prepared_remarks_checked', 'earnings_call_checked', 'qna_checked', 'qna_status', 'prior_quarter_language_compared', 'management_guidance_change', 'analyst_question_themes', 'answer_avoidance_or_uncertainty', 'price_volume_mix_cost_bridge', 'next_quarter_confirmation_points']
BLOCKERS = ['STD26_A_004', 'STD26_A_010', 'STD26_A_014', 'STD26_A_016', 'STD26_A_017', 'STD26_A_018', 'STD26_A_021', 'STD26_A_033', 'STD26_A_057']

def load_payload():
    encoded = "".join((FIX / n).read_text(encoding="utf-8").strip() for n in CHUNKS)
    raw = gzip.decompress(base64.b64decode(encoded))
    return raw, json.loads(raw.decode("utf-8"))

class A022SupplementalEarningsClosure(unittest.TestCase):
    def test_01_exact_materialization_and_sha(self):
        raw, data = load_payload()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), EXPECTED_SHA256)
        self.assertEqual(data["source_spec_id"], "STD26_A_022")
        self.assertEqual(data["draft_id"], "STD26_B_REVISE_R2_022")

    def test_02_current_main_ancestry_and_tree_lock(self):
        subprocess.run(["git","merge-base","--is-ancestor",EXPECTED_MAIN,"HEAD"], cwd=ROOT, check=True)
        tree = subprocess.check_output(["git","rev-parse",EXPECTED_MAIN+"^{tree}"], cwd=ROOT, text=True).strip()
        self.assertEqual(tree, EXPECTED_TREE)

    def test_03_historical_route_and_scope_lock(self):
        _, d=load_payload()
        h=d["historical_route_authority"]
        self.assertEqual(h["declared_status"],"STAGE_B_SUPPLEMENTAL_PACKAGE_PREPARED_STAGE_C_REVIEW_REQUIRED")
        self.assertFalse(h["normal_stage_b_replay"])
        s=d["scope_lock"]
        for k in ("visible_fields_changed","fact_sources_changed","source_quotes_changed",
                  "visible_source_urls_changed","related_changed","date_role_changed","event_fingerprint_changed"):
            self.assertFalse(s[k], k)
        self.assertEqual(s["new_visible_claims_introduced"],0)
        self.assertTrue(s["publish_ready_r5_preserved"])

    def test_04_earnings_contract_complete_and_explicit(self):
        _, d=load_payload()
        e=d["earnings_contract"]
        for k in REQUIRED:
            self.assertIn(k,e)
        self.assertEqual(e["qna_status"],"qna_available")
        self.assertTrue(e["earnings_call_checked"])
        self.assertTrue(e["qna_checked"])
        self.assertTrue(e["prior_quarter_language_compared"])
        self.assertFalse(e["ir_deck_checked"])
        self.assertTrue(bool(e.get("ir_deck_status")))
        self.assertFalse(e["prepared_remarks_checked"])
        self.assertTrue(bool(e.get("prepared_remarks_status")))
        self.assertTrue(d["policy_contract"]["all_required_fields_materialized"])

    def test_05_qna_and_bridge_are_bounded(self):
        _, d=load_payload()
        e=d["earnings_contract"]
        self.assertGreaterEqual(len(e["analyst_question_themes"]),4)
        self.assertGreaterEqual(len(e["next_quarter_confirmation_points"]),3)
        bridge=e["price_volume_mix_cost_bridge"]
        for k in ("revenue","price","volume","mix","cost","bottom_line"):
            self.assertTrue(bool(bridge.get(k)))
        self.assertGreaterEqual(len(d["earnings_call_qna_ledger"]),5)

    def test_06_r5_visible_snapshot_preserved(self):
        _, d=load_payload()
        r=d["incoming_publish_ready_r5"]
        self.assertTrue(r["publish_ready"])
        self.assertEqual(r["visible_snapshot"]["title"],"고려아연, 2026년 상반기 사상 최대 매출·영업이익")
        self.assertTrue(r["visible_snapshot"]["sub"].endswith("달성했다."))
        self.assertEqual(len(r["visible_snapshot"]["urls"]),2)
        self.assertTrue(all(v=="PASS" for v in r["final_qc_gates"].values()))

    def test_07_boundary_and_remaining_blockers(self):
        _, d=load_payload()
        self.assertEqual(d["closure"]["remaining_exact_source_stage_b_blockers"],BLOCKERS)
        self.assertEqual(len(BLOCKERS),9)
        self.assertFalse(d["closure"]["prompt_0_8_authorized"])
        b=d["boundary"]
        for k in ("prompt_0_4_or_later_rerun_performed","production_ids_assigned",
                  "card_run_created","main_write_performed","pr_created","merge_performed"):
            self.assertFalse(b[k], k)
        self.assertTrue(b["validation_branch_must_never_merge"])

if __name__ == "__main__":
    unittest.main()
