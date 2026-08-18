#!/usr/bin/env python3
import base64,hashlib,json,lzma,subprocess,sys,tempfile,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
EXPECTED_SHA="8c31861ab94d5595487115a07b6d05c0c1bf0dc6b26b74e22e773a91bad2f3c5"
PAYLOAD=r"""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"""
EXPECTED=['REC26_A2_024', 'REC26_A2_028', 'REC26_A2_049', 'REC26_A2_050']

class Rescue4RepoNativeClosure(unittest.TestCase):
    def run_cmd(self,*args):
        cp=subprocess.run(args,cwd=ROOT,text=True,capture_output=True)
        if cp.returncode != 0:
            self.fail(f"command failed: {' '.join(map(str,args))}\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}")
        return cp.stdout

    def test_rescue4_contract_projection(self):
        raw=lzma.decompress(base64.b64decode(PAYLOAD))
        self.assertEqual(hashlib.sha256(raw).hexdigest(),EXPECTED_SHA)
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"rescue4_stage_c_closure.json"
            p.write_bytes(raw)
            out1=self.run_cmd(sys.executable,str(ROOT/"validation_scripts/stage_artifact_contract_check.py"),"C",str(p))
            out2=self.run_cmd(sys.executable,str(ROOT/"validation_scripts/stage_lineage_contract_check.py"),"stage_c",str(p))
            self.assertIn('"status": "PASS"',out1)
            self.assertIn("PASS_STAGE_C_SCHEMA_CONTRACT",out2)
            d=json.loads(raw)
            self.assertEqual(d["accepted_fact_safe_count"],4)
            self.assertEqual([x["source_spec_id"] for x in d["accepted_fact_safe"]],EXPECTED)
            self.assertEqual(d["revise_required_count"],0)
            self.assertEqual(d["rejected_count"],0)
            self.assertEqual(d["support_source_only_count"],0)
            self.assertEqual(d["deferred_review_pool_count"],0)
            self.assertFalse(d["boundary"]["prompt_0_4_started"])
            for item in d["accepted_fact_safe"]:
                self.assertEqual(item["state"],"accepted_fact_safe")
                self.assertTrue(item["stage_c_only"])
                self.assertTrue(item["strict_gate_acceptance_guard_applied"])
                self.assertEqual(item["accepted_pool_lineage_status"],"PASS")
                for flag in ("addable_merge_safe","evidence_complete","source_claim_covered","content_enriched","language_terminology_polished","publish_ready","github_merge_ready"):
                    self.assertFalse(item[flag])
            a028=next(x for x in d["accepted_fact_safe"] if x["source_spec_id"]=="REC26_A2_028")
            self.assertTrue(a028["single_source_exception"]["applied_at_stage_c"])
            self.assertEqual(a028["single_source_exception"]["status"],"CANDIDATE_REQUIRES_PROMPT_0_5_REAPPROVAL")

if __name__=="__main__":
    unittest.main()
