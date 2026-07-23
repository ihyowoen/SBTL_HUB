#!/usr/bin/env python3
"""Run workflow-contract regression checks with current-run and legacy scopes separated."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(name: str, command: list[str], expect_json: bool = True):
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    parsed = None
    if expect_json and completed.stdout.strip():
        try:
            parsed = json.loads(completed.stdout)
        except json.JSONDecodeError:
            parsed = None
    return {
        "name": name,
        "command": command,
        "return_code": completed.returncode,
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "json": parsed,
        "stdout": completed.stdout if parsed is None else None,
        "stderr": completed.stderr or None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cards", required=True)
    parser.add_argument("--new-id-file", required=True)
    parser.add_argument(
        "--owner-registry",
        default="validation_data/source_owner_registry.json",
    )
    parser.add_argument("--require-new-contract", action="store_true")
    parser.add_argument("--report")
    args = parser.parse_args()

    python = sys.executable
    checks = [
        run(
            "unit_tests",
            [python, "-m", "unittest", "discover", "-s", "validation_scripts/tests", "-v"],
            expect_json=False,
        ),
        run(
            "evidence_qc_current_run_scope",
            [
                python,
                "validation_scripts/evidence_qc_v8_check.py",
                args.cards,
                "--owner-registry",
                args.owner_registry,
                "--new-id-file",
                args.new_id_file,
            ],
        ),
        run(
            "related_current_run_scope",
            [
                python,
                "validation_scripts/related_lifecycle_check.py",
                args.cards,
                "--new-id-file",
                args.new_id_file,
            ] + (["--require-contract"] if args.require_new_contract else []),
        ),
        run(
            "date_role_current_run_scope",
            [
                python,
                "validation_scripts/date_role_freshness_check.py",
                args.cards,
                "--new-id-file",
                args.new_id_file,
            ] + (["--require-date-role"] if args.require_new_contract else []),
        ),
        run(
            "related_legacy_inventory",
            [python, "validation_scripts/related_lifecycle_check.py", args.cards],
        ),
    ]

    hard_checks = checks[:4]
    result = {
        "status": "PASS" if all(item["return_code"] == 0 for item in hard_checks) else "FAIL",
        "current_run_hard_check_count": len(hard_checks),
        "current_run_hard_fail_count": sum(item["return_code"] != 0 for item in hard_checks),
        "legacy_inventory_status": checks[4]["status"],
        "legacy_inventory_is_separate_remediation_scope": True,
        "checks": checks,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.report:
        Path(args.report).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
