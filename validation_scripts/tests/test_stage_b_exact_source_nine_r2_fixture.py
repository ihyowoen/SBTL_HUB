import base64, gzip, hashlib, json, os, subprocess, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / "validation_scripts" / "tests" / "fixtures"
EXPECTED_MAIN = "75e98148ae4c7af6234799cdd0852a181b11081b"
EXPECTED_TREE = "b7cc7cd0e7c1d06191017aa3882586e0dbe8e976"
EXPECTED_SHA256 = "20fa23ca3e17ba3f970ff7d58e435e944a4a3cc7dfda1618418759e1a17c8270"
CHUNKS = ['stage_b_exact_source_nine_r2_payload_01.b64', 'stage_b_exact_source_nine_r2_payload_02.b64']
INPUTS = ['STD26_A_004', 'STD26_A_010', 'STD26_A_014', 'STD26_A_016', 'STD26_A_017', 'STD26_A_018', 'STD26_A_021', 'STD26_A_033', 'STD26_A_057']
BLOCKED = ['STD26_A_004', 'STD26_A_014', 'STD26_A_016', 'STD26_A_017', 'STD26_A_018', 'STD26_A_021', 'STD26_A_033', 'STD26_A_057']

def load_payload():
    encoded = "".join((FIX / n).read_text(encoding="utf-8").strip() for n in CHUNKS)
    raw = gzip.decompress(base64.b64decode(encoded))
    return raw, json.loads(raw.decode("utf-8"))

class StageBExactSourceNineR2(unittest.TestCase):
    def test_01_exact_materialization_and_sha(self):
        raw, d = load_payload()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), EXPECTED_SHA256)
        self.assertEqual(d["input_ids"], INPUTS)
        self.assertEqual(d["input_count"], 9)

    def test_02_main_and_tree_lock_shallow_safe(self):
        event_path = os.environ.get("GITHUB_EVENT_PATH")
        if event_path and Path(event_path).exists():
            event=json.loads(Path(event_path).read_text(encoding="utf-8"))
            pr=event.get("pull_request")
            if pr:
                self.assertEqual(pr["base"]["sha"], EXPECTED_MAIN)
                raw_head=subprocess.check_output(["git","cat-file","-p","HEAD"],cwd=ROOT,text=True)
                self.assertIn("parent "+EXPECTED_MAIN, raw_head)
        subprocess.run(["git","fetch","--no-tags","--depth=1","origin",EXPECTED_MAIN],cwd=ROOT,check=True)
        self.assertEqual(subprocess.check_output(["git","rev-parse","FETCH_HEAD"],cwd=ROOT,text=True).strip(),EXPECTED_MAIN)
        self.assertEqual(subprocess.check_output(["git","rev-parse","FETCH_HEAD^{tree}"],cwd=ROOT,text=True).strip(),EXPECTED_TREE)

    def test_03_accounting_and_routes(self):
        _, d=load_payload()
        self.assertEqual(len(d["draft_cards"]),1)
        self.assertEqual(d["draft_cards"][0]["source_spec_id"],"STD26_A_010")
        self.assertEqual([x["source_spec_id"] for x in d["draft_blocked"]],BLOCKED)
        self.assertEqual(d["summary"]["accounting_total"],9)
        self.assertTrue(d["summary"]["accounting_matches_input"])

    def test_04_a010_exact_target_recovered(self):
        _, d=load_payload()
        a=d["draft_cards"][0]
        self.assertEqual(a["bounded_recovery"]["result"],"EXACT_TARGET_SATISFIED")
        self.assertEqual(a["source_direction_check"],"PASS")
        self.assertEqual(a["evidence_package_status"],"evidence_package_ready_for_draft")
        owners={x["owner"] for x in a["source_independence_ledger"] if x["usable"]}
        self.assertEqual(owners,{"EIA","Reuters"})
        urls=[x.get("source_url") for x in a["source_discovery_ledger"]]
        self.assertIn("https://www.eia.gov/outlooks/steo/outlook.php",urls)
        self.assertIn("https://www.eia.gov/outlooks/steo/report/",urls)
        data=[x for x in a["source_discovery_ledger"] if x.get("data_resource_url")]
        self.assertEqual(data[0]["data_resource_url"],"https://www.eia.gov/outlooks/steo/xls/Fig31.xlsx")
        self.assertEqual(a["date_role"]["event_date"],"2026-08-11")

    def test_05_no_false_promotions(self):
        _, d=load_payload()
        blocked={x["source_spec_id"]:x for x in d["draft_blocked"]}
        a004=blocked["STD26_A_004"]["exact_missing_target"]
        self.assertIn("EPBC referral/project record",a004)
        self.assertIn("180MW/360MWh",a004)
        self.assertIn("referral-not-approval",a004)
        self.assertIn("Oberbergamt",blocked["STD26_A_014"]["exact_missing_target"])
        self.assertIn("Chinese antitrust",blocked["STD26_A_016"]["exact_missing_target"])
        self.assertIn("KIRIA",blocked["STD26_A_017"]["exact_missing_target"])
        self.assertIn("Contemporaneous official Serentica",blocked["STD26_A_018"]["exact_missing_target"])
        self.assertIn("Official DRC",blocked["STD26_A_021"]["exact_missing_target"])
        self.assertIn("Amendment 0003",blocked["STD26_A_033"]["exact_missing_target"])
        self.assertIn("General Administration of Customs",blocked["STD26_A_057"]["exact_missing_target"])

    def test_06_narrowed_blockers_are_still_blocked(self):
        _, d=load_payload()
        self.assertEqual(set(d["summary"]["narrowed_but_still_blocked_ids"]),{"STD26_A_016","STD26_A_018","STD26_A_033"})
        for x in d["draft_blocked"]:
            self.assertEqual(x["draft_decision"],"draft_blocked")

    def test_07_boundary(self):
        _, d=load_payload()
        b=d["boundary"]
        self.assertTrue(b["stage_b_only"])
        for k in ("stage_c_performed","accepted_fact_safe_assigned","prompt_0_4_performed","prompt_0_5_performed",
                  "prompt_0_6_performed","prompt_0_7_performed","prompt_0_8_performed","production_ids_assigned",
                  "main_branch_write_performed","data_pr_or_merge_performed"):
            self.assertFalse(b[k],k)
        self.assertEqual(d["next_call_recommendation"]["targeted_stage_c_ids"],["STD26_A_010"])

if __name__ == "__main__":
    unittest.main()
