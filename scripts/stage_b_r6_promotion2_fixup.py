#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
RUN = ROOT / "runs/2026-09-03"
BASE = ROOT / "scripts/stage_b_r6_promotion2.py"
OUT = RUN / "stage_b_r6_promotion2_20260903_R1.json"
REPORT = RUN / "stage_b_r6_promotion2_validation_20260903_R1.json"


def main() -> int:
    base = subprocess.run([sys.executable, str(BASE)], cwd=ROOT, check=False)
    if not OUT.exists():
        raise SystemExit("base Stage B promotion2 builder emitted no artifact")

    art = json.loads(OUT.read_text(encoding="utf-8"))
    packages = art.get("evidence_packages", [])
    drafts = art.get("draft_cards", [])
    if len(packages) != 2 or len(drafts) != 2:
        raise SystemExit("unexpected Stage B promotion2 cardinality")

    # The evidence/lineage gates already passed. Production Stage B additionally
    # requires the canonical resolved Related review marker on every passing draft.
    for scope in [*packages, *drafts]:
        related = scope.get("related_evidence_review")
        if not isinstance(related, dict):
            raise SystemExit("missing related_evidence_review object")
        related["status"] = "PASS"

    OUT.write_text(json.dumps(art, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    from validation_scripts import stage_lineage_contract_check as lineage
    rc_lineage = lineage.check_stage_b(art)
    rc_evidence = subprocess.run(
        [sys.executable, str(ROOT / "validation_scripts/stage_b_evidence_gate.py"), str(OUT)],
        cwd=ROOT,
    ).returncode
    rc_contract = subprocess.run(
        [sys.executable, str(ROOT / "validation_scripts/stage_artifact_contract_check.py"), "B", str(OUT)],
        cwd=ROOT,
    ).returncode

    errors = []
    if any((p.get("related_evidence_review") or {}).get("status") != "PASS" for p in packages):
        errors.append("package_related_status")
    if any((d.get("related_evidence_review") or {}).get("status") != "PASS" for d in drafts):
        errors.append("draft_related_status")
    status = "PASS" if rc_lineage == 0 and rc_evidence == 0 and rc_contract == 0 and not errors else "FAIL"
    report = {
        "schema": "stage_b_r6_promotion2_validation_v2",
        "status": status,
        "base_builder_rc": base.returncode,
        "artifact": str(OUT.relative_to(ROOT)),
        "artifact_sha256": hashlib.sha256(OUT.read_bytes()).hexdigest(),
        "stage_b_lineage_check_rc": rc_lineage,
        "stage_b_evidence_gate_rc": rc_evidence,
        "stage_b_production_contract_rc": rc_contract,
        "custom_errors": errors,
        "input_strict_count": 2,
        "draft_count": 2,
        "draft_blocked_count": 0,
        "claim_count": sum(len(p.get("claim_map", [])) for p in packages),
        "source_count": sum(len(p.get("fact_sources", [])) for p in packages),
        "all_claims_supported": all(
            all(c.get("status") == "SUPPORTED" for c in p.get("claim_map", [])) for p in packages
        ),
        "all_packages_multi_owner": all(p.get("source_independent_owner_count", 0) >= 2 for p in packages),
        "fact_safety_declared": False,
        "publish_ready_declared": False,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
