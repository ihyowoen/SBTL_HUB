import base64, gzip, hashlib, json, os, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
FIX=ROOT/"validation_scripts"/"tests"/"fixtures"
PARTS=['remaining8_r4.part01.b64', 'remaining8_r4.part02.b64']
EXPECTED_SHA="068a6ce2caf83f21561708d70c0c38767faf53c609de4a742eaaf6bb90b1b62d"
EXPECTED_MAIN="75e98148ae4c7af6234799cdd0852a181b11081b"
EXPECTED_TREE="b7cc7cd0e7c1d06191017aa3882586e0dbe8e976"
EXPECTED_IDS=["STD26_A_004","STD26_A_014","STD26_A_016","STD26_A_017","STD26_A_018","STD26_A_021","STD26_A_033","STD26_A_057"]

def load():
    encoded="".join((FIX/p).read_text(encoding="utf-8").strip() for p in PARTS)
    raw=gzip.decompress(base64.b64decode(encoded))
    return raw,json.loads(raw.decode("utf-8"))

class RemainingEightExactSourceR4(unittest.TestCase):
    def test_01_exact_materialization(self):
        raw,d=load(); self.assertEqual(hashlib.sha256(raw).hexdigest(),EXPECTED_SHA)
        self.assertEqual(d["input_ids"],EXPECTED_IDS); self.assertEqual(d["input_count"],8)
    def test_02_main_lock(self):
        _,d=load(); self.assertEqual(d["current_main_sha"],EXPECTED_MAIN); self.assertEqual(d["current_main_tree_sha"],EXPECTED_TREE)
        event=os.environ.get("GITHUB_EVENT_PATH")
        if event and Path(event).exists():
            e=json.loads(Path(event).read_text()); base=((e.get("pull_request") or {}).get("base") or {}).get("sha")
            if base: self.assertEqual(base,EXPECTED_MAIN)
    def test_03_accounting_zero_promotion(self):
        _,d=load(); s=d["summary"]
        self.assertEqual((s["input_count"],s["recovered_count"],s["draft_blocked_count"],s["accounting_total"]),(8,0,8,8))
        self.assertTrue(s["accounting_matches_input"]); self.assertEqual(s["unauthorized_promotions"],0); self.assertEqual(d["recovered_for_stage_b_draft"],[])
    def test_04_exact_targets_and_primary_discipline(self):
        _,d=load(); self.assertTrue(d["method"]["no_promotion_without_exact_required_primary_target"]); self.assertTrue(d["method"]["independent_corroboration_does_not_substitute_for_explicit_official_target"])
        for x in d["draft_blocked"]:
            self.assertTrue(x["exact_missing_target"]); self.assertTrue(x["official_source_checked"]); self.assertTrue(x["alternate_tier1_tier2_checked"]); self.assertEqual(x["draft_decision"],"draft_blocked")
    def test_05_r4_material_narrowing(self):
        _,d=load(); narrowed=set(d["summary"]["r4_materially_narrowed_ids"]); self.assertEqual(narrowed,{"STD26_A_014","STD26_A_016","STD26_A_021","STD26_A_057"})
        by={x["source_spec_id"]:x for x in d["draft_blocked"]}
        self.assertIn("2026_07_24",by["STD26_A_014"]["blocked_source_reason"]); self.assertIn("chinese_review",by["STD26_A_016"]["blocked_source_reason"]); self.assertIn("ctcpm",by["STD26_A_021"]["blocked_source_reason"]); self.assertIn("gacc",by["STD26_A_057"]["blocked_source_reason"])
    def test_06_all_eight_have_rescue_and_direction_checks(self):
        _,d=load()
        for x in d["draft_blocked"]:
            self.assertTrue(x["rescue_attempted"]); self.assertEqual(x["same_event_source_direction_check"],"PASS"); self.assertEqual(x["same_actor_event_date_check"],"PASS"); self.assertTrue(x["blocked_source_reason"]); self.assertTrue(x["recommended_next_action"])
    def test_07_boundary(self):
        _,d=load(); b=d["boundary"]
        for k in ("normal_stage_b_draft_created","stage_c_performed","accepted_fact_safe_assigned","prompt_0_4_or_later_performed","prompt_0_8_performed","production_ids_assigned","main_write_performed","data_pr_or_merge_performed"): self.assertFalse(b[k],k)
        self.assertTrue(b["stage_b_recovery_only"])

if __name__=="__main__": unittest.main()
