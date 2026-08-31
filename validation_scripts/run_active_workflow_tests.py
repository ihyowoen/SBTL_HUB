#!/usr/bin/env python3
"""Run workflow machine/semantic regressions fail-closed.

Every ``validation_scripts/tests/test_*.py`` module is imported independently.
Import errors are fatal. Retired prompt snapshots are excluded only by exact
``path::Class::method`` identity from ``retired_prompt_snapshot_tests.json``;
filename patterns are never retirement criteria.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import traceback
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST_DIR = ROOT / "validation_scripts" / "tests"
RETIREMENT_REGISTRY = ROOT / "validation_scripts" / "retired_prompt_snapshot_tests.json"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def flatten(suite: unittest.TestSuite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def load_retirements() -> dict[str, str]:
    raw = json.loads(RETIREMENT_REGISTRY.read_text(encoding="utf-8"))
    if raw.get("schema") != "retired_prompt_snapshot_tests_v1":
        raise ValueError("retirement registry schema mismatch")
    tests = raw.get("tests")
    if not isinstance(tests, dict):
        raise ValueError("retirement registry tests must be an object")
    out: dict[str, str] = {}
    for test_id, reason in tests.items():
        if not isinstance(test_id, str) or "::" not in test_id:
            raise ValueError(f"invalid retired test identity: {test_id!r}")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError(f"retired test requires audit reason: {test_id}")
        out[test_id] = reason.strip()
    return out


def stable_test_id(path: Path, case: unittest.TestCase) -> str:
    relative = path.relative_to(ROOT).as_posix()
    method = getattr(case, "_testMethodName", None) or "<unknown>"
    return f"{relative}::{case.__class__.__name__}::{method}"


def load_test_file(
    path: Path,
    ordinal: int,
    retirements: dict[str, str],
) -> tuple[unittest.TestSuite, int, list[tuple[str, str]]]:
    """Import one test file under a unique name; any import error propagates."""
    module_name = f"_sbtl_workflow_test_{ordinal}_{path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot create import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(module_name, None)
        raise

    loaded = unittest.TestLoader().loadTestsFromModule(module)
    owned = unittest.TestSuite()
    imported_cases = 0
    retired: list[tuple[str, str]] = []
    for case in flatten(loaded):
        # Modules sometimes import TestCase classes from another regression file.
        # Run those classes only in the file that actually defines them so there
        # is no duplicate execution, but never suppress loader/import failures.
        if case.__class__.__module__ != module_name:
            imported_cases += 1
            continue
        test_id = stable_test_id(path, case)
        setattr(case, "_sbtl_stable_test_id", test_id)
        if test_id in retirements:
            retired.append((test_id, retirements[test_id]))
            continue
        owned.addTest(case)
    return owned, imported_cases, retired


def build_active_suite():
    files = sorted(TEST_DIR.glob("test_*.py"))
    retirements = load_retirements()
    suite = unittest.TestSuite()
    imported_cases = 0
    retired_cases: list[tuple[str, str]] = []
    discovered_ids: set[str] = set()
    for ordinal, path in enumerate(files):
        loaded, imported, retired = load_test_file(path, ordinal, retirements)
        suite.addTests(loaded)
        imported_cases += imported
        retired_cases.extend(retired)
        for case in flatten(loaded):
            test_id = getattr(case, "_sbtl_stable_test_id", None)
            if test_id:
                discovered_ids.add(test_id)
        discovered_ids.update(test_id for test_id, _ in retired)

    stale_registry = sorted(set(retirements) - discovered_ids)
    if stale_registry:
        raise ValueError(
            "retirement registry contains identities not discovered in current tree: "
            + ", ".join(stale_registry[:20])
        )
    return suite, files, imported_cases, retired_cases


def failing_id(case) -> str:
    return getattr(case, "_sbtl_stable_test_id", case.id())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true", help="list active/retired exact test identities")
    args = parser.parse_args()

    try:
        suite, files, imported, retired = build_active_suite()
    except Exception as exc:
        print("WORKFLOW_TEST_IMPORT_OR_CLASSIFICATION_FAILURE")
        print(f"- error: {type(exc).__name__}: {exc}")
        traceback.print_exc()
        return 1

    count = suite.countTestCases()
    print("WORKFLOW_TEST_CLASSIFICATION_V4")
    print(f"- discovered_test_files: {len(files)}")
    print("- broad_legacy_filename_exclusions: 0")
    print(f"- active_test_cases: {count}")
    print(f"- exact_retired_snapshot_cases: {len(retired)}")
    print(f"- imported_test_cases_deduplicated: {imported}")

    if not files or count == 0:
        print("FAIL: active workflow test suite is empty")
        return 1

    if args.list:
        for case in flatten(suite):
            print(f"ACTIVE {failing_id(case)}")
        for test_id, reason in sorted(retired):
            print(f"RETIRED {test_id} :: {reason}")
        return 0

    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        print("WORKFLOW_TEST_FAILURE_IDENTITIES")
        for case, _trace in result.failures:
            print(f"FAIL_ID {failing_id(case)}")
        for case, _trace in result.errors:
            print(f"ERROR_ID {failing_id(case)}")
        return 1
    print("RESULT: PASS_ACTIVE_WORKFLOW_TESTS_V4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
