import base64, gzip, hashlib, json, os, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
FIX=ROOT/"validation_scripts"/"tests"/"fixtures"
PARTS=['primary_doc_remaining8_r4.part01.b64']
EXPECTED_SHA="13441f8a6b035c53fe3c68efa4ca5a6e373340b2dd409a3a0e337f1283009ba8"
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

class PrimaryDocumentRemainingEightR4(unittest.TestCase):
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

    def test_03_accounting_and_zero_recovery(self):
        _,d=load()
        s=d["summary"]
        self.assertEqual(s["input_count"],8)
        self.assertEqual(s["exact_targets_recovered"],0)
        self.assertEqual(s["still_blocked_count"],8)
        self.assertEqual(s["accounting_total"],8)
        self.assertTrue(s["accounting_matches_input"])
        self.assertEqual(d["recovered_exact_targets"],[])
        self.assertEqual([x["source_spec_id"] for x in d["still_blocked"]],EXPECTED_IDS)

    def test_04_every_item_keeps_exact_gap_and_no_promotion(self):
        _,d=load()
        for item in d["still_blocked"]:
            self.assertTrue(item["exact_missing_target"].strip())
            self.assertTrue(item["current_exact_gap"].strip())
            self.assertTrue(item["latest_locator_result"].startswith("BLOCKED_"))
            self.assertGreaterEqual(len(item["new_locator_evidence"]),2)
            self.assertFalse(item["promotion_authorized"])
            self.assertFalse(item["stage_c_authorized"])

    def test_05_no_laundering_contract(self):
        _,d=load()
        m=d["method"]
        self.assertTrue(m["exact_target_must_be_directly_recovered_before_stage_b_promotion"])
        self.assertTrue(m["official_locator_or_notice_id_without_required_body_is_not_enough_when_upstream_requires_body_or_attachment"])
        self.assertTrue(m["source_owner_partial_field_coverage_is_not_enough_when_upstream_requires_one_exact_combined_body"])
        self.assertTrue(d["authorization"]["no_secondary_source_substitution_for_explicit_primary_target"])
        self.assertTrue(d["summary"]["no_laundering_promotions"])

    def test_06_priority_narrowing_is_explicit(self):
        _,d=load()
        by_id={x["source_spec_id"]:x for x in d["still_blocked"]}
        self.assertIn("248814a4ef384978897659abaa99146d"," ".join(by_id["STD26_A_033"]["new_locator_evidence"]))
        self.assertIn("009/VPM/CAB.MIN/ECO.NAT/2026"," ".join(by_id["STD26_A_021"]["new_locator_evidence"]))
        self.assertIn("200MWh"," ".join(by_id["STD26_A_018"]["new_locator_evidence"]))
        self.assertIn("2026年7月全国出口重点商品量值表"," ".join(by_id["STD26_A_057"]["new_locator_evidence"]))

    def test_07_stage_boundary(self):
        _,d=load()
        b=d["boundary"]
        for key in ("normal_stage_b_draft_created","stage_c_performed_for_remaining8",
                    "accepted_fact_safe_assigned","prompt_0_4_or_later_performed",
                    "prompt_0_8_performed","production_ids_assigned",
                    "main_write_performed","data_pr_or_merge_performed"):
            self.assertFalse(b[key],key)

if __name__=="__main__":
    unittest.main()
