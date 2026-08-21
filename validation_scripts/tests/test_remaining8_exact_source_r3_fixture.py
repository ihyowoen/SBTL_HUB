import base64, gzip, hashlib, json, os, subprocess, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
FIX=ROOT/"validation_scripts"/"tests"/"fixtures"
PARTS=['remaining8_r3.part01.b64', 'remaining8_r3.part02.b64']
EXPECTED_SHA="e3f4021d927bee647e44a57e2546d90f8e7fb3adbeae749f67d0f09d290ec7c5"
EXPECTED_MAIN="75e98148ae4c7af6234799cdd0852a181b11081b"
EXPECTED_TREE="b7cc7cd0e7c1d06191017aa3882586e0dbe8e976"
EXPECTED_IDS=[
 "STD26_A_004","STD26_A_014","STD26_A_016","STD26_A_017",
 "STD26_A_018","STD26_A_021","STD26_A_033","STD26_A_057"
]

def load():
    encoded="".join((FIX/p).read_text(encoding="utf-8").strip() for p in PARTS)
    raw=gzip.decompress(base64.b64decode(encoded))
    return raw,json.loads(raw.decode("utf-8"))

class RemainingEightExactSourceR3(unittest.TestCase):
    def test_01_exact_materialization_and_sha(self):
        raw,d=load()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),EXPECTED_SHA)
        self.assertEqual(d["input_count"],8)
        self.assertEqual(d["input_ids"],EXPECTED_IDS)

    def test_02_main_tree_lock(self):
        _,d=load()
        self.assertEqual(d["current_main_sha"],EXPECTED_MAIN)
        self.assertEqual(d["current_main_tree_sha"],EXPECTED_TREE)
        event_path=os.environ.get("GITHUB_EVENT_PATH")
        if event_path and Path(event_path).exists():
            event=json.loads(Path(event_path).read_text(encoding="utf-8"))
            base=((event.get("pull_request") or {}).get("base") or {}).get("sha")
            if base:
                self.assertEqual(base,EXPECTED_MAIN)

    def test_03_accounting_and_zero_promotion(self):
        _,d=load()
        s=d["summary"]
        self.assertEqual(s["input_count"],8)
        self.assertEqual(s["recovered_count"],0)
        self.assertEqual(s["draft_blocked_count"],8)
        self.assertEqual(s["accounting_total"],8)
        self.assertTrue(s["accounting_matches_input"])
        self.assertEqual(d["recovered_for_stage_b_draft"],[])
        self.assertEqual([x["source_spec_id"] for x in d["draft_blocked"]],EXPECTED_IDS)

    def test_04_all_blockers_have_exact_target_and_rescue_metadata(self):
        _,d=load()
        for item in d["draft_blocked"]:
            self.assertTrue(item["exact_missing_target"].strip())
            self.assertTrue(item["rescue_attempted"])
            self.assertGreaterEqual(len(item["rescue_attempt_log"]),2)
            self.assertGreaterEqual(len(item["searched_source_types"]),2)
            self.assertTrue(item["official_source_checked"])
            self.assertTrue(item["alternate_tier1_tier2_checked"])
            self.assertEqual(item["same_event_source_direction_check"],"PASS")
            self.assertEqual(item["same_actor_event_date_check"],"PASS")
            self.assertTrue(item["blocked_source_reason"])
            self.assertEqual(item["draft_decision"],"draft_blocked")

    def test_05_no_independent_corroboration_launders_official_target(self):
        _,d=load()
        self.assertTrue(d["method"]["official_or_primary_target_required_when_stage_a_explicitly_requires_it"])
        self.assertTrue(d["method"]["independent_corroboration_does_not_substitute_for_explicit_official_target"])
        for item in d["draft_blocked"]:
            self.assertNotEqual(item["recovery_result"],"EXACT_TARGET_SATISFIED")
            self.assertNotEqual(item["draft_decision"],"draft_card")

    def test_06_narrowing_partitions_reconcile(self):
        _,d=load()
        s=d["summary"]
        union=set(s["strongly_narrowed_ids"]+s["narrowed_ids"]+s["unchanged_exact_record_gap_ids"])
        self.assertEqual(union,set(EXPECTED_IDS))
        self.assertEqual(len(union),8)

    def test_07_boundary_and_next_step(self):
        _,d=load()
        b=d["boundary"]
        for key in ("normal_stage_b_draft_created","stage_c_performed","accepted_fact_safe_assigned",
                    "prompt_0_4_or_later_performed","prompt_0_8_performed","production_ids_assigned",
                    "main_write_performed","data_pr_or_merge_performed"):
            self.assertFalse(b[key],key)
        self.assertTrue(b["stage_b_recovery_only"])
        self.assertIn("manual/primary-document locator",d["next_safe_project_action"]["recommended"])
        self.assertIn("Prompt 0.8",d["next_safe_project_action"]["do_not_proceed_to"])

if __name__=="__main__":
    unittest.main()
