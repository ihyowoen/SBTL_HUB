#!/usr/bin/env python3
import base64, hashlib, lzma, subprocess, sys, tempfile
from pathlib import Path

EXPECTED_SHA = "60d7163ec24a1978f8b57a626c8f9bc71ca737670c48d4f43c8410e1c47e6863"


def test_exact10_stage_a_current_main_contract():
    root = Path(__file__).resolve().parents[2]
    here = Path(__file__).resolve().parent
    encoded = "".join((here / f"exact10_payload_chunk_{i}.txt").read_text().strip() for i in range(4))
    raw = lzma.decompress(base64.b64decode(encoded))
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA
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
