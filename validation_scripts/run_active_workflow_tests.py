#!/usr/bin/env python3
"""Run active semantic/machine workflow tests without reactivating historical prompt snapshots.

Historical PR/review-specific test modules are retained in Git for audit but are not
ordinary active governance. New active tests must use domain/contract names rather than
`test_review_*` or `test_structural_v3_review_*` snapshot naming.
"""
from __future__ import annotations

import argparse
import fnmatch
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST_DIR = ROOT / "validation_scripts" / "tests"

LEGACY_PROMPT_SNAPSHOT_PATTERNS = (
    "test_review_*.py",
    "test_structural_v3_review_*.py",
    "test_pr233_latest_review_contracts.py",
)


def is_legacy_snapshot(path: Path) -> bool:
    return any(fnmatch.fnmatch(path.name, pattern) for pattern in LEGACY_PROMPT_SNAPSHOT_PATTERNS)


def flatten(suite: unittest.TestSuite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def build_active_suite() -> tuple[unittest.TestSuite, list[Path], list[Path], int]:
    loader = unittest.TestLoader()
    active_files: list[Path] = []
    legacy_files: list[Path] = []
    active_suite = unittest.TestSuite()
    filtered_imported_cases = 0

    for path in sorted(TEST_DIR.glob("test_*.py")):
        if is_legacy_snapshot(path):
            legacy_files.append(path)
            continue
        active_files.append(path)
        # Match the repository's historical working discovery semantics:
        # validation_scripts/tests is not a Python package, so do not force a
        # top_level_dir that would require __init__.py.
        discovered = loader.discover(
            str(TEST_DIR),
            pattern=path.name,
        )
        for case in flatten(discovered):
            owner_module = case.__class__.__module__.split(".")[-1]
            if owner_module != path.stem:
                # Some historical tests import TestCase classes from another
                # module. Keep those modules in Git, but do not execute an
                # imported case under the wrong active file.
                filtered_imported_cases += 1
                continue
            active_suite.addTest(case)

    return active_suite, active_files, legacy_files, filtered_imported_cases


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true", help="classify files without running tests")
    args = parser.parse_args()

    suite, active_files, legacy_files, filtered = build_active_suite()
    count = suite.countTestCases()

    print("WORKFLOW_TEST_CLASSIFICATION_V4")
    print(f"- active_test_files: {len(active_files)}")
    print(f"- legacy_prompt_snapshot_files: {len(legacy_files)}")
    print(f"- active_test_cases: {count}")
    print(f"- imported_test_cases_filtered: {filtered}")
    print("- legacy_patterns:")
    for pattern in LEGACY_PROMPT_SNAPSHOT_PATTERNS:
        print(f"  - {pattern}")

    if not active_files or count == 0:
        print("FAIL: active workflow test suite is empty")
        return 1

    if args.list:
        for path in active_files:
            print(f"ACTIVE {path.relative_to(ROOT)}")
        for path in legacy_files:
            print(f"LEGACY_PROMPT_SNAPSHOT {path.relative_to(ROOT)}")
        return 0

    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1
    print("RESULT: PASS_ACTIVE_WORKFLOW_TESTS_V4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
