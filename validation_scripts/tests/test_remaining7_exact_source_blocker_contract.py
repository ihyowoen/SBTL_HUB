import hashlib
import json
import unittest
from pathlib import Path

FIX = Path(__file__).resolve().parent / "fixtures" / "remaining7_exact_source_blocker_contract_fixture.json"
EXPECTED_SHA256 = "6c2885299ac6e54d79da010fd3c781868b8c0a6d7b10a4de76daef962b4bf4db"
EXPECTED_IDS = [
    "STD26_A_057",
    "STD26_A_014",
    "STD26_A_033",
    "STD26_A_017",
    "STD26_A_016",
    "STD26_A_021",
    "STD26_A_004",
]

class TestRemaining7ExactSourceBlockerContract(unittest.TestCase):
    def test_01_fixture_hash_locked(self):
        self.assertEqual(hashlib.sha256(FIX.read_bytes()).hexdigest(), EXPECTED_SHA256)

    def test_02_accounting_and_no_false_promotion(self):
        d = json.loads(FIX.read_text(encoding="utf-8"))
        self.assertEqual(d["input_count"], 7)
        self.assertEqual(set(d["blocked_ids"]), set(EXPECTED_IDS))
        self.assertEqual(d["stage_c_eligible_ids"], [])
        self.assertEqual(d["accepted_fact_safe_ids"], [])

    def test_03_downstream_boundary_remains_locked(self):
        d = json.loads(FIX.read_text(encoding="utf-8"))
        self.assertFalse(d["prompt_0_4_performed"])
        self.assertFalse(d["prompt_0_8_authorized"])
        self.assertFalse(d["production_ids_assigned"])
        self.assertFalse(d["main_write_performed"])
        self.assertEqual(d["main_sha"], "75e98148ae4c7af6234799cdd0852a181b11081b")
        self.assertEqual(d["main_tree"], "b7cc7cd0e7c1d06191017aa3882586e0dbe8e976")

if __name__ == "__main__":
    unittest.main()
