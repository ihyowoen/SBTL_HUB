import base64,gzip,hashlib,json,unittest
EXPECTED_SHA="125cba26970f174305fa146fdc02f76752e337bb0ed56d671afeaccd6d9daaad"
EXPECTED_MAIN="75e98148ae4c7af6234799cdd0852a181b11081b"
EXPECTED_TREE="b7cc7cd0e7c1d06191017aa3882586e0dbe8e976"
EXPECTED_IDS=["STD26_A_004","STD26_A_014","STD26_A_016","STD26_A_017","STD26_A_018","STD26_A_021","STD26_A_033","STD26_A_057"]
DATA="""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"""
def load():
    raw=gzip.decompress(base64.b64decode(DATA))
    return raw,json.loads(raw.decode("utf-8"))
class Remaining8R5(unittest.TestCase):
    def test_01_sha(self):
        raw,d=load()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),EXPECTED_SHA)
    def test_02_main_tree(self):
        _,d=load()
        self.assertEqual(d["current_main_sha"],EXPECTED_MAIN)
        self.assertEqual(d["current_main_tree_sha"],EXPECTED_TREE)
    def test_03_accounting(self):
        _,d=load(); s=d["summary"]
        self.assertEqual(d["input_ids"],EXPECTED_IDS)
        self.assertEqual(s["input_count"],8)
        self.assertEqual(s["exact_targets_recovered"],0)
        self.assertEqual(s["still_blocked_count"],8)
        self.assertEqual(s["accounting_total"],8)
        self.assertTrue(s["accounting_matches_input"])
    def test_04_no_promotion(self):
        _,d=load()
        self.assertEqual(d["recovered_exact_targets"],[])
        for x in d["still_blocked"]:
            self.assertFalse(x["promotion_authorized"])
            self.assertTrue(x["r5_result"].startswith("BLOCKED_"))
    def test_05_no_laundering(self):
        _,d=load()
        self.assertTrue(d["authorization"]["no_secondary_substitution_for_explicit_primary_target"])
        self.assertTrue(d["summary"]["no_laundering_promotions"])
        self.assertEqual(d["summary"]["unauthorized_promotions"],0)
    def test_06_key_locator_narrowing(self):
        _,d=load()
        e=d["source_evidence_updates"]
        self.assertEqual(e["A021"]["document_id"],2641)
        self.assertEqual(e["A033"]["solicitation"],"SP8000-26-R-0021")
        self.assertEqual(e["A057"]["july_values_attributed_to_gacc"]["july_export_tonnes"],4223.5)
        self.assertEqual(e["A018"]["source_owner_confirmed_capacity_mwh"],200)
    def test_07_boundary(self):
        _,d=load()
        for k,v in d["boundary"].items():
            self.assertFalse(v,k)
if __name__=="__main__":
    unittest.main()
