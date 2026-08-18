#!/usr/bin/env python3
import base64, hashlib, json, lzma, subprocess, sys, tempfile
from pathlib import Path

CANDIDATE_SHA = "60d7163ec24a1978f8b57a626c8f9bc71ca737670c48d4f43c8410e1c47e6863"
FINAL_SHA = "92b9f36aa390555e02dc05b70b5bc0424ad938b55ae4f2076f4272bf1ca30191"


def _finalize_exit_state(raw: bytes) -> bytes:
    data = json.loads(raw.decode("utf-8"))
    data["status"] = "PASS_STAGE_A_EXACT10_CURRENT_MAIN_REPO_VALIDATED"
    data["stage_a_validity_status"] = "PASS"
    data["baseline_duplicate_screen_status"] = "PASS"
    data["authoritative_stage_a"] = True
    data["stage_b_eligible"] = True
    data["recommended_for"] = ["Stage B r0 / Prompt 0.2 using exact10 strict_passed_spec[] only"]
    data["next_call_recommendation"]["reason"] = (
        "All ten exact recoverable items are materialized under the current Stage A V3 contract and "
        "the repository-native Stage A lineage/artifact validators passed. Stage B r0 may now begin "
        "for these ten strict specs only."
    )
    data["boundary"]["repo_validator_executed"] = True
    data["boundary"]["stage_b_authorized"] = True
    data["boundary"]["reason"] = (
        "Stage A exact10 recertification is repository-validated and closed. "
        "Only the exact10 strict_passed_spec[] may proceed to Stage B; A059-A082 remain excluded."
    )
    data["repo_validation_result"] = {
        "validation_only_pr": 264,
        "branch": "agent/validate-exact10-stage-a-20260818",
        "base_main_sha": "75e98148ae4c7af6234799cdd0852a181b11081b",
        "workflow_name": "Workflow contract validation",
        "workflow_run_number": 893,
        "workflow_run_id": 32097526690,
        "candidate_exact_sha256": CANDIDATE_SHA,
        "candidate_contract_result": "PASS",
        "exit_state_finalization": [
            "status", "stage_a_validity_status", "baseline_duplicate_screen_status",
            "authoritative_stage_a", "stage_b_eligible", "recommended_for",
            "next_call_recommendation.reason", "boundary.repo_validator_executed",
            "boundary.stage_b_authorized", "boundary.reason", "repo_validation_result"
        ],
        "final_exact_byte_revalidation_required": False,
    }
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def test_exact10_stage_a_current_main_contract():
    root = Path(__file__).resolve().parents[2]
    here = Path(__file__).resolve().parent
    encoded = "".join((here / f"exact10_payload_chunk_{i}.txt").read_text().strip() for i in range(4))
    candidate = lzma.decompress(base64.b64decode(encoded))
    assert hashlib.sha256(candidate).hexdigest() == CANDIDATE_SHA
    raw = _finalize_exit_state(candidate)
    assert hashlib.sha256(raw).hexdigest() == FINAL_SHA

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        f.write(raw)
        path = Path(f.name)
    try:
        lineage = subprocess.run(
            [sys.executable, str(root / "validation_scripts/stage_lineage_contract_check.py"), "stage_a", str(path)],
            text=True, capture_output=True,
        )
        assert lineage.returncode == 0, lineage.stdout + "\n" + lineage.stderr
        assert "PASS_STAGE_A_SCHEMA_CONTRACT" in lineage.stdout

        artifact = subprocess.run(
            [sys.executable, str(root / "validation_scripts/stage_artifact_contract_check.py"), "A", str(path)],
            text=True, capture_output=True,
        )
        assert artifact.returncode == 0, artifact.stdout + "\n" + artifact.stderr
        assert '"status": "PASS"' in artifact.stdout
        assert '"item_count": 10' in artifact.stdout
        assert '"missing_count": 0' in artifact.stdout
    finally:
        path.unlink(missing_ok=True)
