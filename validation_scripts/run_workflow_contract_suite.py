#!/usr/bin/env python3
"""Run workflow-contract regression checks with current-run and legacy scopes separated."""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

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


def load_card_ids(path: str) -> set[str]:
    payload: Any = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict) and isinstance(payload.get("cards"), list):
        rows = payload["cards"]
    else:
        raise ValueError("--cards must be a card list or an object with cards[]")
    return {
        str(row.get("id"))
        for row in rows
        if isinstance(row, dict) and row.get("id")
    }


def load_scope_ids(path: str) -> set[str]:
    source = Path(path)
    if source.suffix.lower() == ".csv":
        rows = csv.DictReader(source.open(encoding="utf-8-sig"))
        values = set()
        for row in rows:
            value = row.get("assigned_id") or row.get("id") or row.get("card_id")
            if value:
                values.add(str(value))
        return values

    payload: Any = json.loads(source.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return {str(value) for value in payload if value}
    if isinstance(payload, dict):
        for key in ("ids", "new_ids", "production_ids"):
            values = payload.get(key)
            if isinstance(values, list):
                return {str(value) for value in values if value}
    raise ValueError("--new-id-file must be a list, ids[] JSON, or CSV with assigned_id/id/card_id")


def validate_scope(cards_path: str, id_path: str) -> dict[str, Any]:
    available = load_card_ids(cards_path)
    requested = load_scope_ids(id_path)
    matched = requested & available
    missing = requested - available
    errors = []

    if not requested:
        errors.append("ID scope is empty")
    if requested and not matched:
        errors.append("ID scope matched zero cards")
    if missing:
        errors.append(f"ID scope contains {len(missing)} IDs absent from cards")

    status = "PASS" if not errors else "FAIL"
    return {
        "name": "current_run_scope_validation",
        "command": ["internal", "validate_scope", cards_path, id_path],
        "return_code": 0 if status == "PASS" else 1,
        "status": status,
        "json": {
            "status": status,
            "requested_id_count": len(requested),
            "matched_card_count": len(matched),
            "missing_id_count": len(missing),
            "missing_ids": sorted(missing),
            "errors": errors,
        },
        "stdout": None,
        "stderr": None,
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
    scope_validation = validate_scope(args.cards, args.new_id_file)
    checks = [
        run(
            "unit_tests",
            [python, "-m", "unittest", "discover", "-s", "validation_scripts/tests", "-v"],
            expect_json=False,
        ),
        scope_validation,
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

    hard_checks = checks[:5]
    result = {
        "status": "PASS" if all(item["return_code"] == 0 for item in hard_checks) else "FAIL",
        "current_run_hard_check_count": len(hard_checks),
        "current_run_hard_fail_count": sum(item["return_code"] != 0 for item in hard_checks),
        "scope_validation": scope_validation["json"],
        "legacy_inventory_status": checks[5]["status"],
        "legacy_inventory_is_separate_remediation_scope": True,
        "checks": checks,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.report:
        Path(args.report).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
