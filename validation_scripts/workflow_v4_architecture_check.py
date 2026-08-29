#!/usr/bin/env python3
"""Static architecture contract for clean SBTL_HUB Workflow V4."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "docs" / "llm_prompts" / "v1"
REGISTRY = P / "GOVERNANCE_LIFECYCLE_REGISTRY.json"
PROMPT_MANIFEST = P / "PROMPT_MANIFEST.md"
MACHINE_MANIFEST = P / "LLM_PROMPT_GITHUB_CANONICAL_V1_MANIFEST.json"
UPLOAD_MANIFEST = P / "UPLOAD_MANIFEST.json"
STAGE_A = P / "01_PROMPT_0_1_Stage_A.md"
ADDABILITY = P / "06_PROMPT_0_4_Baseline_Revalidation.md"
MASTER = P / "00_NEW_RUN_MASTER_PROMPT.md"
DIRECT_DOC = ROOT / "docs" / "MANUAL_DIRECT_ADD_V2.md"
DIRECT_SCHEMA = ROOT / "schemas" / "manual-direct-add.v2.schema.json"
DIRECT_VALIDATOR = ROOT / "scripts" / "validate_manual_direct_add.mjs"

SUPERSEDED = [
    ROOT / "docs" / "STRUCTURAL_NEWS_VALUE_SELECTION.md",
    ROOT / "docs" / "PROMPT_ABC_SUPPORTING_RULES.md",
    P / "00_DATE_STORYID_RELATED_INTEGRITY_OVERRIDE_V1.md",
    P / "00_DYNAMIC_GOVERNANCE_COMPLETENESS_OVERRIDE_V1.md",
    P / "00_MANDATORY_SEARCH_BEFORE_DELETE_OVERRIDE.md",
    P / "01A_PROMPT_0_1S_Structural_Value_Override.md",
    P / "01_PROMPT_0_1_DYNAMIC_SOURCE_UNIVERSE_ADDENDUM_V1.md",
    P / "01_PROMPT_0_1_Stage_A_HARDENING_ADDENDUM_V1.md",
    P / "07_PROMPT_0_5_Evidence_QC_HARDENING_ADDENDUM_V1.md",
    P / "08_PROMPT_0_6_Content_Polish_HARDENING_ADDENDUM_V1.md",
    P / "09_PROMPT_0_7_Final_QC_HARDENING_ADDENDUM_V1.md",
    P / "10_PROMPT_0_8_GitHub_Merge_Prep_HARDENING_ADDENDUM_V1.md",
    P / "10_PROMPT_0_8_INCREMENTAL_OPERATION_ADDENDUM_V1.md",
    P / "11_PROMPT_0_9_Production_Verification_HARDENING_ADDENDUM_V1.md",
    P / "13_PROMPT_1_1_CANONICAL_PROMOTION_ADDENDUM_V1.md",
]


def need(path: Path, token: str, errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"missing {path.relative_to(ROOT)}")
        return
    if token not in path.read_text(encoding="utf-8"):
        errors.append(f"{path.relative_to(ROOT)} missing token {token!r}")


def main() -> int:
    errors: list[str] = []
    for path in (REGISTRY, MACHINE_MANIFEST, UPLOAD_MANIFEST, DIRECT_SCHEMA):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"invalid JSON {path.relative_to(ROOT)}: {exc}")

    if REGISTRY.exists():
        reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
        if reg.get("active_override_or_addendum_count") != 0:
            errors.append("registry active_override_or_addendum_count must be 0")
        prompts = reg.get("active_named_prompts")
        if not isinstance(prompts, list) or len(prompts) != 17:
            errors.append("registry must contain exactly 17 active named prompts")
        if any("01A_PROMPT_0_1S" in str(x) for x in prompts or []):
            errors.append("retired 0.1S is still registered active")
        for rel in prompts or []:
            if not (ROOT / rel).exists(): errors.append(f"registered active prompt missing: {rel}")

    need(STAGE_A, "EMBEDDED_NEWS_VALUE_SELECTION_V4", errors)
    need(STAGE_A, "related_prepass", errors)
    for token in ["execution_credibility_gate", "independent_cardability_gate", "decision_news_value_score", "publication_urgency", "structural_non_execution_route"]:
        need(STAGE_A, token, errors)
    need(ADDABILITY, "Addability Revalidation", errors)
    need(ADDABILITY, "not the first Related audit", errors)
    need(MASTER, "EMBEDDED_NEWS_VALUE_SELECTION_V4", errors)
    need(PROMPT_MANIFEST, "There is **no active 0.1S", errors)

    for path in SUPERSEDED:
        if not path.exists():
            errors.append(f"retired governance path missing audit stub: {path.relative_to(ROOT)}")
            continue
        head = path.read_text(encoding="utf-8")[:1200]
        if "SUPERSEDED" not in head and "REFERENCE_ONLY" not in head:
            errors.append(f"retired governance path not lifecycle-marked: {path.relative_to(ROOT)}")

    need(DIRECT_DOC, "MANUAL_DIRECT_ADD_V2_20260829", errors)
    need(DIRECT_VALIDATOR, "manual_direct_add_v2", errors)
    if DIRECT_SCHEMA.exists():
        schema = json.loads(DIRECT_SCHEMA.read_text(encoding="utf-8"))
        if schema.get("properties", {}).get("schema", {}).get("const") != "manual_direct_add_v2":
            errors.append("manual-direct-add.v2 schema const missing")

    active_text = "\n".join((ROOT / rel).read_text(encoding="utf-8") for rel in json.loads(REGISTRY.read_text(encoding="utf-8")).get("active_named_prompts", []) if (ROOT / rel).exists())
    for token in ["WORKFLOW_CONTRACT_OVERLAY_", "01A_PROMPT_0_1S_Structural_Value_Override.md", "00_DATE_STORYID_RELATED_INTEGRITY_OVERRIDE_V1.md", "00_DYNAMIC_GOVERNANCE_COMPLETENESS_OVERRIDE_V1.md"]:
        if token in active_text:
            errors.append(f"active named prompt dependency graph contains retired token: {token}")

    if errors:
        print("RESULT: BLOCKED_WORKFLOW_V4_ARCHITECTURE")
        for e in errors: print(f"- {e}")
        return 1
    print("RESULT: PASS_WORKFLOW_V4_ARCHITECTURE")
    print("- active named prompts: 17")
    print("- active override/addendum runtime dependencies: 0")
    print("- Stage A news value + Related pre-pass embedded: PASS")
    print("- Prompt 0.4 addability distinction: PASS")
    print("- Manual Direct Add V2 registered: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
