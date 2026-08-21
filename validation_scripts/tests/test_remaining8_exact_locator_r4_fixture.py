import base64, gzip, hashlib, json, os, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
FIX=ROOT/"validation_scripts"/"tests"/"fixtures"
PARTS=['remaining8_r4.part01.b64']
EXPECTED_SHA="2a426cc82075bee0db5b8d15df2e1aff60af1046562b41dfa9236f3ceeafbd31"
EXPECTED_MAIN="75e98148ae4c7af6234799cdd0852a181b11081b"
EXPECTED_TREE="b7cc7cd0e7c1d06191017aa3882586e0dbe8e976"
EXPECTED_IDS=["STD26_A_004","STD26_A_014","STD26_A_016","STD26_A_017","STD26_A_018","STD26_A_021","STD26_A_033","STD26_A_057"]

def load():
    raw=gzip.decompress(base64.b64decode("".join((FIX/p).read_text().strip() for p in PARTS)))
    return raw,json.loads(raw.decode())

class RemainingEightExactLocatorR4(unittest.TestCase):
    def test_01_exact_sha_and_main_lock(self):
        raw,d=load()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),EXPECTED_SHA)
        self.assertEqual(d["current_main_sha"],EXPECTED_MAIN)
        self.assertEqual(d["current_main_tree_sha"],EXPECTED_TREE)

    def test_02_accounting_and_identity(self):
        _,d=load()
        self.assertEqual(d["input_ids"],EXPECTED_IDS)
        self.assertEqual(d["summary"]["input"],8)
        self.assertEqual(d["summary"]["exact_target_recovered"],0)
        self.assertEqual(d["summary"]["still_blocked"],8)
        self.assertTrue(d["summary"]["accounting_matches"])
        self.assertEqual(d["summary"]["unauthorized_promotions"],0)

    def test_03_each_item_keeps_exact_target_closed(self):
        _,d=load()
        self.assertEqual(len(d["results"]),8)
        for r in d["results"]:
            self.assertIn(r["source_spec_id"],EXPECTED_IDS)
            self.assertTrue(r["exact_missing_target"].strip())
            self.assertFalse(r["exact_target_recovered"])
            self.assertTrue(r["why_not_promoted"].strip())
            self.assertTrue(r["next_locator"].strip())
            self.assertGreaterEqual(len(r["official_primary_locator_attempts"]),2)
            self.assertGreaterEqual(len(r["new_r4_evidence"]),2)

    def test_04_no_corroboration_laundering(self):
        _,d=load()
        self.assertIn("not allowed",d["decision_rule"])
        for r in d["results"]:
            self.assertTrue(r["recovery_status"].startswith("BLOCKED_"))

    def test_05_narrowing_partitions_cover_all_ids(self):
        _,d=load()
        s=d["summary"]
        u=set(s["very_strongly_narrowed"]+s["strongly_narrowed"]+s["narrowed"])
        self.assertEqual(u,set(EXPECTED_IDS))

    def test_06_boundary(self):
        _,d=load()
        b=d["boundary"]
        for k in ("normal_stage_b_draft_created","stage_c_performed","accepted_fact_safe_assigned",
                  "prompt_0_4_or_later_performed","prompt_0_8_performed","production_ids_assigned",
                  "main_write_performed","data_pr_or_merge_performed"):
            self.assertFalse(b[k],k)

    def test_07_next_step_does_not_authorize_prompt_08(self):
        _,d=load()
        n=d["next_safe_project_action"]
        self.assertFalse(n["prompt_0_8_authorized"])
        self.assertIn("upstream-target necessity re-review",n["recommended"])

if __name__=="__main__":
    unittest.main()
