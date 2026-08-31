#!/usr/bin/env python3
"""Run the complete workflow machine/semantic regression suite fail-closed.

Every ``validation_scripts/tests/test_*.py`` module is imported independently.
Import errors are fatal. Review-numbered filenames are not treated as legacy by
name: many of them are durable machine-regression tests. Any genuinely retired
prompt snapshot must be excluded later by an explicit test-method identity with
an audit reason, never by a broad filename pattern.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
import traceback
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST_DIR = ROOT / "validation_scripts" / "tests"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def flatten(suite: unittest.TestSuite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def load_test_file(path: Path, ordinal: int) -> tuple[unittest.TestSuite, int]:
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
    for case in flatten(loaded):
        # Modules sometimes import TestCase classes from another regression file.
        # Run those classes only in the file that actually defines them so there
        # is no duplicate execution, but never suppress loader/import failures.
        if case.__class__.__module__ != module_name:
            imported_cases += 1
            continue
        owned.addTest(case)
    return owned, imported_cases


def build_active_suite() -> tuple[unittest.TestSuite, list[Path], int]:
    files = sorted(TEST_DIR.glob("test_*.py"))
    suite = unittest.TestSuite()
    imported_cases = 0
    for ordinal, path in enumerate(files):
        loaded, imported = load_test_file(path, ordinal)
        suite.addTests(loaded)
        imported_cases += imported
    return suite, files, imported_cases


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true", help="list every active test module")
    args = parser.parse_args()

    try:
        suite, files, imported = build_active_suite()
    except Exception as exc:
        print("WORKFLOW_TEST_IMPORT_FAILURE")
        print(f"- error: {type(exc).__name__}: {exc}")
        traceback.print_exc()
        return 1

    count = suite.countTestCases()
    print("WORKFLOW_TEST_CLASSIFICATION_V4")
    print(f"- active_test_files: {len(files)}")
    print("- broad_legacy_filename_exclusions: 0")
    print(f"- active_test_cases: {count}")
    print(f"- imported_test_cases_deduplicated: {imported}")

    if not files or count == 0:
        print("FAIL: active workflow test suite is empty")
        return 1

    if args.list:
        for path in files:
            print(f"ACTIVE {path.relative_to(ROOT)}")
        return 0

    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1
    print("RESULT: PASS_ACTIVE_WORKFLOW_TESTS_V4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
