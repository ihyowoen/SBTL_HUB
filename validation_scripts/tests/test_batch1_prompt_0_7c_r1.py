import base64, gzip, hashlib, json, os, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
FIX=ROOT/"validation_scripts"/"tests"/"fixtures"/"batch1_0_7c_r1.b64"
EXPECTED_SHA="7c37dac4b0ea574887ebb943029f1901fddd6cc828319a3d00ad1138af2104b6"
EXPECTED_MAIN="75e98148ae4c7af6234799cdd0852a181b11081b"
EXPECTED_TREE="b7cc7cd0e7c1d06191017aa3882586e0dbe8e976"
REQ_DOCS=[
 "docs/EDITORIAL_VALUE_AND_COMPLETENESS_STANDARD.md",
 "docs/STRUCTURAL_NEWS_VALUE_SELECTION.md",
 "docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md",
 "docs/RELATED_LIFECYCLE_CONTRACT.md"
]

def load():
    raw=gzip.decompress(base64.b64decode(FIX.read_text().strip()))
    return raw,json.loads(raw)

class Batch1Prompt07C(unittest.TestCase):
    def test_01_exact_artifact_sha_and_main_lock(self):
        raw,d=load()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),EXPECTED_SHA)
        self.assertEqual(d["current_main_sha"],EXPECTED_MAIN)
        self.assertEqual(d["current_main_tree_sha"],EXPECTED_TREE)

    def test_02_required_0_7c_consumer_fields(self):
        _,d=load()
        self.assertEqual(d["stage"],"0.7C")
        self.assertEqual(d["status"],"PASS_WITH_DECLARED_RESIDUAL_RISK")
        self.assertTrue(d["prompt_0_8_authorized"])
        self.assertTrue(d["governing_contracts_same_revision"])
        self.assertTrue(d["v3_contract_preflight_passed"])
        self.assertEqual(d["governing_contracts_read"],REQ_DOCS)
        self.assertEqual(set(d["governing_contract_git_blobs"]),set(REQ_DOCS))

    def test_03_batch1_exactly_35_unique_and_final_qc_pass(self):
        _,d=load()
        b=d["publish_batch"]
        self.assertEqual(b["publish_ready_count"],35)
        self.assertEqual(len(b["source_spec_ids"]),35)
        self.assertEqual(len(set(b["source_spec_ids"])),35)
        self.assertTrue(b["final_qc_all_nine_gates_passed"])
        self.assertEqual(b["format_risk_checked_count"],13)
        self.assertEqual(b["execution_path_pass_count"],8)
        self.assertEqual(b["v3_non_execution_path_pass_count"],5)
        self.assertEqual(b["format_risk_hold_count"],0)
        self.assertEqual(b["duplicate_event_fingerprint_count"],0)

    def test_04_all_non_batch_pools_are_explicit_and_disjoint(self):
        _,d=load()
        batch=set(d["publish_batch"]["source_spec_ids"])
        ex=set()
        for row in d["material_exclusions"]:
            ids=set(row["ids"])
            self.assertFalse(batch & ids)
            ex |= ids
        for row in d["known_unknowns"]:
            self.assertNotIn(row["id"],batch)
        self.assertEqual(len(d["material_exclusions"][0]["ids"]),8)
        self.assertEqual(len(d["material_exclusions"][1]["ids"]),23)
        self.assertEqual(len(d["material_exclusions"][2]["ids"]),8)
        self.assertTrue(d["material_exclusions"][0]["red_team_status"].startswith("PASS_"))
        self.assertTrue(d["material_exclusions"][1]["false_ordinal_inference_prohibited"])

    def test_05_six_round_review_and_completeness_flags(self):
        _,d=load()
        for k in ("source_universe_accounted","regional_search_complete","topic_search_complete",
                  "baseline_follow_up_review_complete","review_pool_rescue_complete",
                  "must_report_candidates_accounted","format_risk_anchor_path_review_complete"):
            self.assertTrue(d[k],k)
        self.assertEqual(len(d["six_round_review"]),6)
        for v in d["six_round_review"].values():
            self.assertTrue(v.startswith("PASS"),v)

    def test_06_authorization_scope_is_batch_only(self):
        _,d=load()
        a=d["authorization"]
        self.assertTrue(a["prompt_0_8_authorized"])
        self.assertEqual(a["authorized_scope"],"PUBLISH_BATCH1_35_20260825_ONLY")
        self.assertTrue(a["production_id_assignment_allowed_only_inside_prompt_0_8_for_batch1"])
        self.assertTrue(a["main_write_not_yet_authorized_by_this_artifact"])
        self.assertGreaterEqual(len(a["unauthorized_scopes"]),6)

    def test_07_boundary_no_0_8_or_write_yet(self):
        _,d=load()
        for k,v in d["boundary"].items():
            self.assertFalse(v,k)

if __name__=="__main__":
    unittest.main()
