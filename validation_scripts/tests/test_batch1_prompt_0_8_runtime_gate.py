import hashlib
import json
import subprocess
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
FIX=ROOT/"validation_scripts"/"tests"/"fixtures"/"batch1_35_runtime"
MAIN="75e98148ae4c7af6234799cdd0852a181b11081b"
BLOB="0cc4e610f9c1ad105761d399be1cd0e316f95128"
DREF="validation_scripts/tests/fixtures/batch1_35_runtime/stage-0-0d-engine-bridge.json"
CREF="validation_scripts/tests/fixtures/batch1_35_runtime/stage-0-0c-engine-bridge.json"
IREF="validation_scripts/tests/fixtures/batch1_35_runtime/independent-completeness-batch1-35.json"

def stable(v):
    if isinstance(v, list): return [stable(x) for x in v]
    if isinstance(v, dict): return {k:stable(v[k]) for k in sorted(v)}
    return v

def op_sha(ops):
    raw=json.dumps(stable(ops),separators=(",",":"),ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()

def file_sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

class Batch1Prompt08RuntimeGate(unittest.TestCase):
    def test_01_zero_op_real_engine_verify(self):
        d=json.loads((FIX/"stage-0-0d-engine-bridge.json").read_text())
        c=json.loads((FIX/"stage-0-0c-engine-bridge.json").read_text())
        i=json.loads((FIX/"independent-completeness-batch1-35.json").read_text())
        self.assertEqual(d["repository_head_sha"],MAIN)
        self.assertEqual(d["canonical_full_blob_sha"],BLOB)
        self.assertEqual(c["base_full_blob_sha"],BLOB)
        self.assertEqual(c["document_universe_manifest_ref"],DREF)
        self.assertEqual(i["status"],"PASS_WITH_DECLARED_RESIDUAL_RISK")
        self.assertTrue(i["prompt_0_8_authorized"])

        actual_blob=subprocess.check_output(
            ["git","rev-parse",f"{MAIN}:data/cards.full.json"], cwd=ROOT, text=True
        ).strip()
        self.assertEqual(actual_blob,BLOB)

        ops={"insert":[],"update":[],"related_add":[]}
        run={
          "schema":"card_run_v1",
          "run_id":"PUBLISH_BATCH1_35_20260825_RUNTIME_GATE_ZERO_OP",
          "base_main_commit_sha":MAIN,
          "base_full_blob_sha":BLOB,
          "expected_before":1373,
          "output_updated":"2026-08-25T13:02:00+09:00",
          "operations":ops,
          "expected_after":1373,
          "audit_refs":["validation_scripts/tests/fixtures/batch1_35_runtime/runtime-audit.generated.json"],
          "document_universe_manifest_ref":DREF,
          "coverage_discovery_ref":CREF,
          "independent_completeness_ref":IREF,
          "notes":"validation-only zero-op runtime gate; no production IDs or data writes"
        }
        audit={
          "schema":"card_run_audit_v1",
          "status":"PASS",
          "audit_complete":True,
          "reviewer_independence":"SEPARATE_PASS",
          "run_id":run["run_id"],
          "base_main_commit_sha":MAIN,
          "base_full_blob_sha":BLOB,
          "document_universe_manifest_ref":DREF,
          "coverage_discovery_ref":CREF,
          "independent_completeness_ref":IREF,
          "reviewed_operations_sha256":op_sha(ops),
          "expected_before":1373,
          "expected_after":1373,
          "inserted_ids":[],
          "updated_ids":[],
          "related_additions":[],
          "zero_deletion_assertion":True,
          "zero_related_remove_assertion":True,
          "full_output_sha256":file_sha(ROOT/"data/cards.full.json"),
          "lean_output_sha256":file_sha(ROOT/"public/data/cards.json")
        }

        run_path=FIX/"runtime-card-run.generated.json"
        audit_path=FIX/"runtime-audit.generated.json"
        report_path=FIX/"runtime-apply-report.generated.json"
        try:
            run_path.write_text(json.dumps(run,ensure_ascii=False,indent=2)+"\n")
            audit_path.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n")
            proc=subprocess.run([
              "node","scripts/apply_card_run.mjs",
              "--run",str(run_path.relative_to(ROOT)),
              "--baseline","data/cards.full.json",
              "--canonical-path","data/cards.full.json",
              "--output","data/cards.full.json",
              "--report",str(report_path.relative_to(ROOT)),
              "--lean-path","public/data/cards.json",
              "--base-main-sha",MAIN,
              "--verify"
            ],cwd=ROOT,text=True,capture_output=True)
            self.assertEqual(proc.returncode,0,msg=proc.stdout+"\n"+proc.stderr)
            payload=json.loads(report_path.read_text())
            self.assertEqual(payload.get("status"),"PASS")
            self.assertEqual(payload.get("before"),1373)
            self.assertEqual(payload.get("after"),1373)
        finally:
            for p in (run_path,audit_path,report_path):
                if p.exists(): p.unlink()

    def test_02_bridge_is_alias_only(self):
        d=json.loads((FIX/"stage-0-0d-engine-bridge.json").read_text())
        c=json.loads((FIX/"stage-0-0c-engine-bridge.json").read_text())
        self.assertFalse(d["authority_guards"]["substantive_governance_redecision_performed"])
        self.assertFalse(c["authority_guards"]["coverage_rediscovery_performed"])
        self.assertFalse(c["authority_guards"]["editorial_reselection_performed"])

if __name__=="__main__":
    unittest.main()
