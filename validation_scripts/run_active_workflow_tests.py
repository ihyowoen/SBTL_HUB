#!/usr/bin/env python3
"""Run workflow machine/semantic regressions fail-closed.

Every ``validation_scripts/tests/test_*.py`` module is imported independently.
Import errors are fatal. Retired prompt snapshots are excluded only by exact
``path::Class::method`` identity from ``retired_prompt_snapshot_tests.json``;
filename patterns are never retirement criteria.

Historical V3 machine-contract modules remain active regressions. Only modules
listed exactly in ``v3_compat_machine_test_modules.json`` have their imported
Stage A checker rebound, inside this test runner only, to the explicit V3
compatibility API. Production ``stage_lineage_contract_check.check_stage_a``
remains V4 fail-closed and is never monkey-patched.
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
V3_COMPAT_REGISTRY = ROOT / "validation_scripts" / "v3_compat_machine_test_modules.json"
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
        if not isinstance(test_id, str) or test_id.count("::") != 2:
            raise ValueError(f"invalid retired test identity: {test_id!r}")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError(f"retired test requires audit reason: {test_id}")
        out[test_id] = reason.strip()
    return out


def load_v3_compat_modules() -> set[str]:
    raw = json.loads(V3_COMPAT_REGISTRY.read_text(encoding="utf-8"))
    if raw.get("schema") != "v3_compat_machine_test_modules_v1":
        raise ValueError("V3 compatibility registry schema mismatch")
    modules = raw.get("modules")
    if not isinstance(modules, list) or not modules:
        raise ValueError("V3 compatibility registry modules must be a non-empty array")
    if len(modules) != len(set(modules)):
        raise ValueError("V3 compatibility registry contains duplicate module paths")
    reason = raw.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("V3 compatibility registry requires an audit reason")

    out: set[str] = set()
    for relative in modules:
        if not isinstance(relative, str) or not relative.strip():
            raise ValueError(f"invalid V3 compatibility module path: {relative!r}")
        if not relative.startswith("validation_scripts/tests/test_") or not relative.endswith(".py"):
            raise ValueError(f"V3 compatibility path must name an exact test module: {relative}")
        path = ROOT / relative
        if not path.is_file():
            raise ValueError(f"V3 compatibility module does not exist: {relative}")
        out.add(relative)
    return out


def stable_test_id(path: Path, case: unittest.TestCase) -> str:
    relative = path.relative_to(ROOT).as_posix()
    method = getattr(case, "_testMethodName", None) or "<unknown>"
    return f"{relative}::{case.__class__.__name__}::{method}"


def _module_relative_path(module) -> str | None:
    filename = getattr(module, "__file__", None)
    if not filename:
        return None
    try:
        return Path(filename).resolve().relative_to(ROOT).as_posix()
    except (ValueError, OSError):
        return None


def bind_v3_compat_module(module, compat_modules: set[str]) -> bool:
    """Rebind imported Stage A entrypoints for one exact historical test module.

    This mutates only that test module's globals. The production validator
    module itself is never modified.
    """
    relative = _module_relative_path(module)
    if relative not in compat_modules:
        return False

    from validation_scripts import stage_lineage_contract_check as active_lineage
    from validation_scripts import stage_lineage_contract_check_v3_compat as compat_lineage

    replacements = (
        (active_lineage.check_stage_a, compat_lineage.check_stage_a),
        (active_lineage.check_stage_a_full, compat_lineage.check_stage_a_full),
        (active_lineage.validate_stage_a_spec, compat_lineage.validate_stage_a_spec),
    )
    for name, value in list(vars(module).items()):
        if value is active_lineage:
            setattr(module, name, compat_lineage)
            continue
        for active_value, compat_value in replacements:
            if value is active_value:
                setattr(module, name, compat_value)
                break
    return True


def bind_loaded_v3_compat_modules(compat_modules: set[str]) -> set[str]:
    bound: set[str] = set()
    for module in list(sys.modules.values()):
        if module is None:
            continue
        relative = _module_relative_path(module)
        if relative in compat_modules and bind_v3_compat_module(module, compat_modules):
            bound.add(relative)
    return bound


def load_test_file(
    path: Path,
    ordinal: int,
    retirements: dict[str, str],
    compat_modules: set[str],
) -> tuple[unittest.TestSuite, int, list[tuple[str, str]], bool]:
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

    compat_bound = bind_v3_compat_module(module, compat_modules)
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
    return owned, imported_cases, retired, compat_bound


def build_active_suite():
    files = sorted(TEST_DIR.glob("test_*.py"))
    retirements = load_retirements()
    compat_modules = load_v3_compat_modules()
    suite = unittest.TestSuite()
    imported_cases = 0
    retired_cases: list[tuple[str, str]] = []
    discovered_ids: set[str] = set()
    compat_bound_paths: set[str] = set()
    discovered_paths = {path.relative_to(ROOT).as_posix() for path in files}

    stale_compat = sorted(compat_modules - discovered_paths)
    if stale_compat:
        raise ValueError(
            "V3 compatibility registry contains undiscovered modules: "
            + ", ".join(stale_compat[:20])
        )

    for ordinal, path in enumerate(files):
        loaded, imported, retired, compat_bound = load_test_file(
            path, ordinal, retirements, compat_modules
        )
        suite.addTests(loaded)
        imported_cases += imported
        retired_cases.extend(retired)
        if compat_bound:
            compat_bound_paths.add(path.relative_to(ROOT).as_posix())
        for case in flatten(loaded):
            test_id = getattr(case, "_sbtl_stable_test_id", None)
            if test_id:
                discovered_ids.add(test_id)
        discovered_ids.update(test_id for test_id, _ in retired)

    # Some test modules are also imported canonically as helpers by other test
    # modules. Rebind those exact registered helper-module globals as well.
    compat_bound_paths.update(bind_loaded_v3_compat_modules(compat_modules))
    missing_compat_binding = sorted(compat_modules - compat_bound_paths)
    if missing_compat_binding:
        raise ValueError(
            "V3 compatibility modules were discovered but not explicitly rebound: "
            + ", ".join(missing_compat_binding[:20])
        )

    stale_registry = sorted(set(retirements) - discovered_ids)
    if stale_registry:
        raise ValueError(
            "retirement registry contains identities not discovered in current tree: "
            + ", ".join(stale_registry[:20])
        )
    return suite, files, imported_cases, retired_cases, compat_bound_paths


def failing_id(case) -> str:
    return getattr(case, "_sbtl_stable_test_id", case.id())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true", help="list active/retired exact test identities")
    args = parser.parse_args()

    try:
        suite, files, imported, retired, compat_bound = build_active_suite()
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
    print(f"- exact_v3_compat_test_modules: {len(compat_bound)}")
    print(f"- imported_test_cases_deduplicated: {imported}")
    print("- production_v4_entrypoint_monkeypatches: 0")

    if not files or count == 0:
        print("FAIL: active workflow test suite is empty")
        return 1

    if args.list:
        for case in flatten(suite):
            print(f"ACTIVE {failing_id(case)}")
        for test_id, reason in sorted(retired):
            print(f"RETIRED {test_id} :: {reason}")
        for path in sorted(compat_bound):
            print(f"V3_COMPAT_MODULE {path}")
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
