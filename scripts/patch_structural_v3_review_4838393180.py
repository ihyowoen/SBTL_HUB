from pathlib import Path


def replace_once(path: str, old: str, new: str, label: str) -> None:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one target, found {count}")
    file_path.write_text(text.replace(old, new, 1), encoding="utf-8")


evidence_path = "docs/llm_prompts/v1/07_PROMPT_0_5_Evidence_QC.md"
old_evidence = """then evidence QC must confirm body-level or official evidence for at least one concrete execution anchor, such as:\n\n- signed contract\n- customer order\n- offtake\n- commercial deployment\n- field installation\n- commissioning\n- production start\n- facility opening\n- certification\n- regulatory decision\n- public funding approval\n- binding procurement\n- measurable capacity addition\n- safety recall or regulatory action\n- named customer adoption\n\nIf the anchor is missing or only implied by commentary, do not mark evidence_complete. Route the card to addable_hold_claim_gap or needs_return_to_prompt_c with reason execution_anchor_not_evidenced.\n"""
new_evidence = """then evidence QC must confirm body-level or official evidence for exactly one supported anchor path:\n\n1. `execution` — a concrete execution anchor such as:\n\n- signed contract\n- customer order\n- offtake\n- commercial deployment\n- field installation\n- commissioning\n- production start\n- facility opening\n- certification\n- regulatory decision\n- public funding approval\n- binding procurement\n- measurable capacity addition\n- safety recall or regulatory action\n- named customer adoption\n\n2. `v3_non_execution` — a complete, source-backed V3 Structural Value Override that preserves the governing `anchor_classes[]`, item-specific `evidence_needed_for_stage_b[]`, specific `why_execution_event_not_required`, before-after change, changed judgment, and route metadata from the current-run lineage.\n\nFor every format-risk item, validate the selected route and require exactly one route status to be `pass`; the other route must be `not_applicable` with a specific `non_applicable_anchor_path_reason`. If neither route is source-backed, both routes are claimed, the selected route conflicts with the current-run lineage, or the route is only implied by commentary, do not mark `evidence_complete`. Route the card to `addable_hold_claim_gap` or `needs_return_to_prompt_c` with reason `anchor_path_not_evidenced` or the more specific route conflict reason.\n\nA complete V3 non-execution route must not be held solely because a conventional execution anchor is absent.\n"""
replace_once(evidence_path, old_evidence, new_evidence, "Evidence QC early format-risk gate")

retro_path = "docs/llm_prompts/v1/13_PROMPT_1_1_Retrospective.md"
replace_once(
    retro_path,
    "- Were all 8 docs read from GitHub main?",
    "- Were all 10 docs read from GitHub main?",
    "Retrospective red-team required-doc count",
)
replace_once(
    retro_path,
    "   - list all 8 required docs",
    "   - list all 10 required docs",
    "Retrospective report required-doc count",
)

validation_path = Path("docs/validation/STRUCTURAL_NEWS_VALUE_V3_VALIDATION_20260802.md")
validation_text = validation_path.read_text(encoding="utf-8")
entry = """

## Review 4838393180 follow-up

- Evidence QC의 초기 format-risk guard를 execution-only에서 exactly-one two-path gate로 정렬했다.
- 유효한 V3 non-execution route는 conventional execution anchor 부재만으로 hold되지 않는다.
- Prompt 1.1 retrospective의 red-team question과 Markdown report contract를 모두 10 required docs 기준으로 통일했다.
"""
if "## Review 4838393180 follow-up" not in validation_text:
    validation_path.write_text(validation_text.rstrip() + entry + "\n", encoding="utf-8")
