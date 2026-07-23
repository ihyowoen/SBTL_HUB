#!/usr/bin/env python3
"""Idempotently append the 2026-07-23 workflow contracts to named prompts.

Run from the repository root:
  python validation_scripts/apply_prompt_contract_overlays.py --check
  python validation_scripts/apply_prompt_contract_overlays.py --apply
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

BEGIN = "<!-- WORKFLOW_CONTRACT_OVERLAY_20260723:BEGIN -->"
END = "<!-- WORKFLOW_CONTRACT_OVERLAY_20260723:END -->"

COMMON = """
Mandatory shared contracts for this stage:

- `docs/RELATED_LIFECYCLE_CONTRACT.md`
- `docs/SCHEMA_CONTRACT_STAGE_LINEAGE.md`
- `docs/SOURCE_AUDIT_CONTRACT.md`
- `validation_data/source_owner_registry.json` when source-owner counting is performed

The shared contracts supersede conflicting wording only for Related lifecycle, date-role/freshness,
source-audit metadata derivation, stage-exit artifact conformance, and production-verification proof.
""".strip()

BLOCKS = {
    "docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md": """
Stage A Related/date overlay:

- Perform the metadata-only Related pre-pass required by `RELATED_LIFECYCLE_CONTRACT.md`.
- Every strict or bounded-review item must emit `related_prepass`.
- Clear same-event duplicates may not enter the normal Stage B full-draft queue.
- Candidate-to-candidate relation edges must be preserved.
- Emit preliminary `date_role` with publication/event/representative date candidates; do not invent dates.
- Stage exit must satisfy:
  `python validation_scripts/stage_artifact_contract_check.py A <STAGE_A_JSON>`.
""",
    "docs/llm_prompts/v1/02_PROMPT_0_2_Stage_B_r0.md": """
Stage B Related/date/source overlay:

- Resolve every `related_prepass` using body-level or official evidence and emit `related_evidence_review`.
- Emit `date_role` with event-date URL/quote and `earliest_same_event_date_checked=true`.
- A newer article date is not a fresh follow-up anchor.
- After any source add/remove/URL repair, run `recompute_source_audit_metadata.py` and then
  `evidence_qc_v8_check.py`; do not hand-maintain derived counters.
- Stage exit must satisfy:
  `python validation_scripts/stage_artifact_contract_check.py B <STAGE_B_JSON>`.
""",
    "docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md": """
Stage C Related/source overlay:

- Lock `related_lineage` for every accepted card.
- `same_event_duplicate`, `existing_card_reinforcement`, and `uncertain_needs_review` may not enter
  `accepted_fact_safe` as new cards.
- `distinct_follow_up` requires a direct fresh execution anchor.
- Recompute source independence from current `fact_sources`; do not trust stale counters.
- Stage exit must satisfy:
  `python validation_scripts/stage_artifact_contract_check.py C <STAGE_C_JSON>`.
""",
    "docs/llm_prompts/v1/04_PROMPT_0_2R_Stage_B_Revise.md": """
Stage B revise defect routing overlay:

Classify every defect as one of:
`same_url_quote_repair`, `date_only_repair`, `metadata_only_materialization`,
`new_source_augmentation`, `visible_claim_change`, `selection_or_staleness_defect`.

- Same-URL quote repair and verified metadata materialization do not consume a full revise-loop count.
- Date-only repair is allowed only when all other visible/evidence fields remain byte-stable.
- Selection/staleness defects return upstream; they are not repaired as draft wording issues.
- Any source change must trigger source-audit recomputation and Related/date recheck.
""",
    "docs/llm_prompts/v1/05_PROMPT_0_3R_Stage_C_Revise.md": """
Stage C revise bounded-repair overlay:

- Same-URL body/official quote repair is allowed when URL, event scope and visible claim are unchanged.
- Record before/after quote and status; numbers, dates or event stage changes require the normal B revise path.
- A deterministic date-only repair requires direct date evidence plus Related/story-ID impact revalidation.
- Preserve or re-lock `related_lineage`; do not accept a same-event duplicate as a new card.
""",
    "docs/llm_prompts/v1/06_PROMPT_0_4_Baseline_Revalidation.md": """
Prompt 0.4 Related baseline overlay:

- Re-run Related and duplicate screening against current main and the current candidate batch.
- Classify candidates as new unrelated, distinct follow-up, program lineage, same-event duplicate,
  existing reinforcement, or Related-uncertain hold.
- Preserve candidate-to-candidate edges for production-ID resolution.
- Strong evidence does not override a stale or duplicate selection defect.
- Run `related_lifecycle_check.py` structurally before emitting addable candidates.
""",
    "docs/llm_prompts/v1/07_PROMPT_0_5_Evidence_QC.md": """
Prompt 0.5 source/date/Related overlay:

- Recompute all source counters, domains, owners, diversity status, discovery ledger and URL-resolution
  from current `fact_sources` before deciding evidence completeness.
- Run landing-page detection and reject non-durable article endpoints from evidence counts.
- When an earlier source is found, re-run earliest-same-event and fresh-anchor checks; return stale
  republications upstream instead of allowing evidence strength to launder selection.
- Run `evidence_qc_v8_check.py` before advancing a card.
""",
    "docs/llm_prompts/v1/08_PROMPT_0_6_Content_Polish.md": """
Prompt 0.6 lineage overlay:

- Preserve `related_lineage`, `date_role`, source-audit fields and all evidence verbatim.
- Emit the exact top-level lineage fields and `lineage_and_anchor_guard` required by Prompt 0.7;
  do not rely only on nested aliases.
- Content polish may not create or remove Related edges.
""",
    "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md": """
Prompt 0.7 final-gate overlay:

- Run `evidence_qc_v8_check.py`, `related_lifecycle_check.py`,
  `date_role_freshness_check.py --require-date-role`, and
  `stage_artifact_contract_check.py 0.7` before `publish_ready=true`.
- Reapprove bounded single-source exceptions without weakening Related proof.
- Output filename must be `publish_ready_PENDING_MERGE_PREP_<RUN_TAG>.json`;
  reserve `pr_candidate_payload` for Prompt 0.8.
""",
    "docs/llm_prompts/v1/10_PROMPT_0_8_GitHub_Merge_Prep.md": """
Prompt 0.8 merge overlay:

- Resolve all `related_candidate_spec_ids` to final production IDs and record
  `related_id_resolution_ledger`.
- Fail on dangling, self, duplicate, unexplained, or unresolved Related links.
- Recompute source-audit metadata after every source URL change and run the repository Evidence QC.
- Run `related_lifecycle_check.py --require-contract --new-id-file <ID_LEDGER>` and
  `evidence_qc_v8_check.py --new-id-file <ID_LEDGER>` against the merged candidate/current merge-ID scope.
- Only Prompt 0.8 may emit `pr_candidate_payload` and the authoritative replace-all file.
""",
    "docs/llm_prompts/v1/11_PROMPT_0_9_Production_Verification.md": """
Prompt 0.9 verification overlay:

Allowed overall states:

- `PASS`
- `PASS_WITH_LIMITATIONS`
- `FAIL`

Record separately:
`production_data_verified`, `production_deployment_verified`,
`production_html_shell_verified`, `production_interactive_ui_verified`, and
`production_mobile_verified`.

Never set `production_verified=true` while any mandatory surface is untested. Verify live Related IDs
and, when browser access exists, Related-card navigation/rendering.
""",
}


def overlay(block: str) -> str:
    return f"\n\n{BEGIN}\n{COMMON}\n\n{block.strip()}\n{END}\n"


def apply_one(path: Path, block: str) -> bool:
    text = path.read_text(encoding="utf-8")
    replacement = overlay(block)
    pattern = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END), re.S)
    if pattern.search(text):
        updated = pattern.sub(replacement.strip(), text)
    else:
        updated = text.rstrip() + replacement
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    missing = []
    changed = []
    for name, block in BLOCKS.items():
        path = Path(name)
        if not path.exists():
            missing.append(name)
            continue
        text = path.read_text(encoding="utf-8")
        expected = overlay(block).strip()
        if BEGIN not in text or expected not in text:
            changed.append(name)
            if args.apply:
                apply_one(path, block)

    print(f"prompt files checked: {len(BLOCKS)}")
    print(f"missing files: {len(missing)}")
    for name in missing:
        print(f"  MISSING {name}")
    print(f"overlay updates required: {len(changed)}")
    for name in changed:
        print(f"  {'UPDATED' if args.apply else 'NEEDS_UPDATE'} {name}")
    if missing:
        return 2
    if args.check and changed:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
