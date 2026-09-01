#!/usr/bin/env python3
"""V4 guard: active prompt overlays are retired and must not reappear."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs" / "llm_prompts" / "v1" / "GOVERNANCE_LIFECYCLE_REGISTRY.json"
FORBIDDEN_ACTIVE_TOKENS = [
    "WORKFLOW_CONTRACT_OVERLAY_",
    "01A_PROMPT_0_1S_Structural_Value_Override.md",
    "00_DATE_STORYID_RELATED_INTEGRITY_OVERRIDE_V1.md",
    "00_DYNAMIC_GOVERNANCE_COMPLETENESS_OVERRIDE_V1.md",
    "00_MANDATORY_SEARCH_BEFORE_DELETE_OVERRIDE.md",
    "_HARDENING_ADDENDUM_V1.md",
    "_INCREMENTAL_OPERATION_ADDENDUM_V1.md",
    "_CANONICAL_PROMOTION_ADDENDUM_V1.md",
    "_DYNAMIC_SOURCE_UNIVERSE_ADDENDUM_V1.md",
]
STATUS_RE = re.compile(r"^\*\*Status:\*\*\s*`?([A-Z_]+)`?\s*$", re.MULTILINE)


def active_prompt_paths() -> tuple[list[Path], list[str]]:
    errors: list[str] = []
    try:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except Exception as exc:
        return [], [f"cannot read lifecycle registry: {exc}"]

    raw = registry.get("active_named_prompts")
    if not isinstance(raw, list) or not raw:
        return [], ["lifecycle registry active_named_prompts must be a non-empty array"]
    expected_count = registry.get("active_named_prompt_count")
    if expected_count != len(raw):
        errors.append(
            f"registry active_named_prompt_count={expected_count} != actual {len(raw)}"
        )
    if len(raw) != len(set(raw)):
        errors.append("registry active_named_prompts contains duplicate paths")

    paths: list[Path] = []
    for entry in raw:
        if not isinstance(entry, str) or not entry.strip():
            errors.append(f"invalid active prompt registry entry: {entry!r}")
            continue
        paths.append(ROOT / entry)
    return paths, errors


def check() -> list[str]:
    paths, errors = active_prompt_paths()
    for path in paths:
        if not path.exists():
            errors.append(f"missing active prompt: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        match = STATUS_RE.search(text[:1600])
        if not match:
            errors.append(f"registered active prompt lacks parseable Status header: {path.relative_to(ROOT)}")
        elif match.group(1) != "ACTIVE_CANONICAL":
            errors.append(
                f"registered active prompt status is {match.group(1)}, not ACTIVE_CANONICAL: {path.relative_to(ROOT)}"
            )
        for token in FORBIDDEN_ACTIVE_TOKENS:
            if token in text:
                errors.append(
                    f"{path.relative_to(ROOT)} contains retired runtime dependency token: {token}"
                )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.apply:
        print("BLOCKED_V4_OVERLAY_APPLICATION_RETIRED: recurring rules must be integrated into clean named prompts")
        return 2
    errors = check()
    if errors:
        print("RESULT: BLOCKED_V4_LEGACY_PROMPT_OVERLAY_PRESENT")
        for error in errors:
            print(f"- {error}")
        return 1
    paths, _ = active_prompt_paths()
    print("RESULT: PASS_V4_NO_ACTIVE_PROMPT_OVERLAYS")
    print(f"- active named prompts checked from registry: {len(paths)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
