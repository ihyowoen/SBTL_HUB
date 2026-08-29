#!/usr/bin/env python3
"""V4 guard: active prompt overlays are retired and must not reappear."""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPT_DIR = ROOT / "docs" / "llm_prompts" / "v1"
ACTIVE_PROMPTS = [
    "00D_PROMPT_0_0D_DOCUMENT_UNIVERSE_PREFLIGHT.md",
    "00C_PROMPT_0_0C_COVERAGE_DISCOVERY.md",
    "01_PROMPT_0_1_Stage_A.md",
    "02_PROMPT_0_2_Stage_B_r0.md",
    "03_PROMPT_0_3_Stage_C_r0.md",
    "04_PROMPT_0_2R_Stage_B_Revise.md",
    "05_PROMPT_0_3R_Stage_C_Revise.md",
    "06_PROMPT_0_4_Baseline_Revalidation.md",
    "07_PROMPT_0_5_Evidence_QC.md",
    "08_PROMPT_0_6_Content_Polish.md",
    "09_PROMPT_0_7_Final_QC.md",
    "09A_PROMPT_0_7C_INDEPENDENT_COMPLETENESS_REVIEW.md",
    "10_PROMPT_0_8_GitHub_Merge_Prep.md",
    "11_PROMPT_0_9_Production_Verification.md",
    "12_PROMPT_1_0_Remediation.md",
    "13_PROMPT_1_1_Retrospective.md",
    "14_PROMPT_0_1P_Review_Pool_Promotion.md",
]
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


def check() -> list[str]:
    errors: list[str] = []
    for name in ACTIVE_PROMPTS:
        path = PROMPT_DIR / name
        if not path.exists():
            errors.append(f"missing active prompt: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_ACTIVE_TOKENS:
            if token in text:
                errors.append(f"{path.relative_to(ROOT)} contains retired runtime dependency token: {token}")
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
    print("RESULT: PASS_V4_NO_ACTIVE_PROMPT_OVERLAYS")
    print(f"- active named prompts checked: {len(ACTIVE_PROMPTS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
