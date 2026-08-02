#!/usr/bin/env python3
from pathlib import Path


def replace_once(path: str, old: str, new: str, label: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one target, found {count}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


def append_once(path: str, marker: str, block: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if marker in text:
        return
    p.write_text(text.rstrip() + "\n\n" + block.strip() + "\n", encoding="utf-8")


stage_b_revise = "docs/llm_prompts/v1/04_PROMPT_0_2R_Stage_B_Revise.md"
retro = "docs/llm_prompts/v1/13_PROMPT_1_1_Retrospective.md"
validation = "docs/validation/STRUCTURAL_NEWS_VALUE_V3_VALIDATION_20260802.md"

replace_once(
    stage_b_revise,
    "Use the current run’s Stage C revise_required[] as the only input universe for this revise pass.\n\nThis is not a new Stage B run.\nThis is not candidate selection.\nThis is not source augmentation unless explicitly authorized.\nThis is a limited revision pass for cards that Stage C classified as revise_required.",
    "Use exactly one current-run revise input universe for this pass:\n\n- revision pass `r1`: the immediately previous Stage C `revise_required[]`; or\n- revision pass `r2` or later: the immediately previous Stage C revise `revise_required_again[]`.\n\nThis is not a new Stage B run.\nThis is not candidate selection.\nThis is not source augmentation unless explicitly authorized.\nThis is a limited revision pass for cards that the immediately preceding Stage C-family step classified into the selected revise state.",
    "Stage B revise opening input universe",
)

old_candidate = """Candidate input rule:

Only previous Stage C revise_required[] may enter this Stage B revise pass.

Do not include:
- previous Stage C accepted_fact_safe
- previous Stage C rejected
- previous Stage C support_source_only
- previous Stage C deferred_review_pool
- Stage B draft_blocked
- Stage A review_pool
- Stage A rejected
- Stage A existing_reinforcement
- Stage A support_source_only
- any new web-discovered candidate
- any prior-run candidate

If any non-revise_required item is mixed in, exclude it and report mixed_input_excluded.

Anchor-path revise input rule:

For every format-risk `revise_required[]` item, consume the complete Stage C `anchor_path_validation` object."""

new_candidate = """Candidate input rule:

Select exactly one input state from the immediately preceding Stage C-family output:

- If `REVISION_PASS = r1`, only previous Stage C `revise_required[]` may enter.
- If `REVISION_PASS = r2` or later, only the immediately previous Stage C revise `revise_required_again[]` may enter.

Do not mix `revise_required[]` and `revise_required_again[]` in one pass. Do not skip across revision generations or import an older loop's unresolved items.

Do not include:
- previous Stage C accepted_fact_safe
- previous Stage C rejected
- previous Stage C support_source_only
- previous Stage C deferred_review_pool
- previous Stage C `revise_required[]` when `REVISION_PASS` is r2 or later
- previous Stage C revise `revise_required_again[]` when `REVISION_PASS` is r1
- Stage B draft_blocked
- Stage A review_pool
- Stage A rejected
- Stage A existing_reinforcement
- Stage A support_source_only
- any new web-discovered candidate
- any prior-run candidate

If any item outside the selected revise input state is mixed in, exclude it and report `mixed_input_excluded`.

Anchor-path revise input rule:

For every format-risk item in the selected `revise_required[]` or `revise_required_again[]` input, consume the complete immediately preceding `anchor_path_validation` object."""
replace_once(stage_b_revise, old_candidate, new_candidate, "Stage B revise candidate input rule")

replace_once(
    stage_b_revise,
    "Stage B revise pass must fix only the specific issues identified by Stage C revise_required.",
    "Stage B revise pass must fix only the specific issues identified by the selected immediately preceding `revise_required[]` or `revise_required_again[]` input state.",
    "Stage B revise role",
)
replace_once(
    stage_b_revise,
    "If Stage C revise_required says source augmentation is needed, do not perform it automatically.",
    "If the selected Stage C-family revise input says source augmentation is needed, do not perform it automatically.",
    "Stage B revise source augmentation reference",
)
replace_once(
    stage_b_revise,
    "Every revise_required item must appear exactly once as:",
    "Every item in the selected `revise_required[]` or `revise_required_again[]` input must appear exactly once as:",
    "Stage B revise decision accounting universe",
)
replace_once(
    stage_b_revise,
    "Every previous Stage C revise_required item must appear exactly once in this Stage B revise output.",
    "Every item in the selected immediately preceding revise input must appear exactly once in this Stage B revise output.",
    "Stage B revise accounting rule",
)

replace_once(
    stage_b_revise,
    "- revise_required_input_count\n- revised_draft_card_count",
    "- revise_input_state: revise_required|revise_required_again\n- revise_input_count\n- revise_required_input_count\n- revise_required_again_input_count\n- revised_draft_card_count",
    "Stage B revise input accounting fields",
)
replace_once(
    stage_b_revise,
    "- accounting_matches_revise_required_input_count\n- revised_draft_cards[]",
    "- accounting_matches_revise_input_count\n- accounting_matches_revise_required_input_count, required for r1 and `not_applicable` with reason for r2+\n- accounting_matches_revise_required_again_input_count, required for r2+ and `not_applicable` with reason for r1\n- revised_draft_cards[]",
    "Stage B revise accounting status fields",
)
replace_once(
    stage_b_revise,
    "2. Stage C revise_required input count\n3. Scope confirmation",
    "2. Selected revise input state and count (`revise_required[]` for r1 or `revise_required_again[]` for r2+)\n3. Scope confirmation",
    "Stage B revise report accounting",
)
replace_once(
    stage_b_revise,
    "“Stage B revise pass fixed only Stage C revise_required items. It did not add new candidates, promote review_pool, rescue rejected cards, decide accepted_fact_safe, decide evidence_complete, or decide publish_ready.”",
    "“Stage B revise pass fixed only the selected immediately preceding Stage C-family revise items (`revise_required[]` for r1 or `revise_required_again[]` for r2+). It did not add new candidates, promote review_pool, rescue rejected cards, decide accepted_fact_safe, decide evidence_complete, or decide publish_ready.”",
    "Stage B revise boundary statement",
)

old_docs = """Before starting, read the latest versions of all required workflow docs from GitHub main:

1. docs/FACT_DISCIPLINE.md
2. docs/PROMPT_ABC_DEFAULT_MODE.md
3. docs/PROMPT_ABC_SUPPORTING_RULES.md
4. docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md
5. docs/CARD_ID_STANDARD.md
6. docs/WORKFLOW.md
7. docs/OPERATIONS.md
8. docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md

Required-doc rule:

All 8 documents above are mandatory."""

new_docs = """Before starting, read the latest versions of all required workflow docs from GitHub main:

1. docs/FACT_DISCIPLINE.md
2. docs/STRUCTURAL_NEWS_VALUE_SELECTION.md
3. docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md
4. docs/PROMPT_ABC_DEFAULT_MODE.md
5. docs/PROMPT_ABC_SUPPORTING_RULES.md
6. docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md
7. docs/CARD_ID_STANDARD.md
8. docs/WORKFLOW.md
9. docs/OPERATIONS.md
10. docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md

Required-doc rule:

All 10 documents above are mandatory."""
replace_once(retro, old_docs, new_docs, "Prompt 1.1 V3 required docs")

append_once(
    validation,
    "## REVIEW_4838372817_ADDRESSING",
    """## REVIEW_4838372817_ADDRESSING

The review's two findings are addressed as linked contract fixes:

- Prompt 0.2R now accepts `revise_required[]` only for r1 and the immediately previous Prompt 0.3R `revise_required_again[]` for r2+, with explicit generation, mixing, accounting, and anchor-path preservation rules.
- Prompt 1.1 now reads the two governing V3 contracts and uses the same 10-document preflight as other V3-aware stages before auditing Structural Value Override completeness.

Focused regression coverage is provided in `validation_scripts/tests/test_review_4838372817_contracts.py`.""",
)

# Focused local assertions before the workflow runs the full suite.
stage_b_text = Path(stage_b_revise).read_text(encoding="utf-8")
retro_text = Path(retro).read_text(encoding="utf-8")
assert "immediately previous Stage C revise `revise_required_again[]`" in stage_b_text
assert "If `REVISION_PASS = r2` or later" in stage_b_text
assert "accounting_matches_revise_required_again_input_count" in stage_b_text
assert "All 10 documents above are mandatory." in retro_text
assert "docs/STRUCTURAL_NEWS_VALUE_SELECTION.md" in retro_text
assert "docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md" in retro_text
assert "All 8 documents above are mandatory." not in retro_text
