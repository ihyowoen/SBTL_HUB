#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


package_block_evidence = """Each evidence_complete_and_source_claim_covered item must include:

- state: evidence_complete_and_source_claim_covered
- previous_state: addable_merge_safe
- draft_id
- source_spec_id
- source_story_ids
- region
- date
- cat
- sub_cat
- signal
- title
- sub
- gate
- fact
- implication
- urls
- related
- fact_sources

For every format-risk `evidence_complete_and_source_claim_covered[]` item, preserve the same-run `anchor_path_validation` and route-status fields without alteration.

For every such item with `selected_anchor_path = v3_non_execution`, preserve the complete canonical, source-backed Structural Value Override package byte-for-byte from Baseline Revalidation:

- `structural_value_override_applied: true`
- `structural_value_override_reason`
- non-empty valid `anchor_classes[]`
- `incremental_information`
- `decision_relevance`
- `baseline_expectation_changed`
- non-empty item-specific `evidence_needed_for_stage_b[]`
- non-empty measurable `next_confirmation_points[]`
- specific `why_execution_event_not_required`
- `prior_state`
- `new_verified_fact`
- `changed_judgment`
- applicable uncertainty / probability-change fields
- applicable baseline-expectation / before-after fields
- current-run source lineage that supports every package field

Do not summarize away, reconstruct from memory, rename, or drop any package field. Missing, altered, generic, unsupported, or internally inconsistent V3 package metadata requires `addable_hold_claim_gap` or return to the earliest defective stage; it must not enter `evidence_complete_and_source_claim_covered[]`.

- evidence_complete: true"""

old_evidence = """Each evidence_complete_and_source_claim_covered item must include:

- state: evidence_complete_and_source_claim_covered
- previous_state: addable_merge_safe
- draft_id
- source_spec_id
- source_story_ids
- region
- date
- cat
- sub_cat
- signal
- title
- sub
- gate
- fact
- implication
- urls
- related
- fact_sources
- evidence_complete: true"""

package_block_polish = """Each content_enriched_and_language_polished item must include:

- state: content_enriched_and_language_polished
- previous_state: evidence_complete_and_source_claim_covered
- draft_id
- source_spec_id
- source_story_ids
- region
- date
- cat
- sub_cat
- signal
- title
- sub
- gate
- fact
- implication
- urls
- related
- fact_sources

For every format-risk `content_enriched_and_language_polished[]` item, preserve the same-run `anchor_path_validation` and route-status fields without alteration.

For every such item with `selected_anchor_path = v3_non_execution`, preserve the complete canonical, source-backed Structural Value Override package byte-for-byte from Evidence QC:

- `structural_value_override_applied: true`
- `structural_value_override_reason`
- non-empty valid `anchor_classes[]`
- `incremental_information`
- `decision_relevance`
- `baseline_expectation_changed`
- non-empty item-specific `evidence_needed_for_stage_b[]`
- non-empty measurable `next_confirmation_points[]`
- specific `why_execution_event_not_required`
- `prior_state`
- `new_verified_fact`
- `changed_judgment`
- applicable uncertainty / probability-change fields
- applicable baseline-expectation / before-after fields
- current-run source lineage that supports every package field

Content Polish may change visible prose only within its existing source lock. It must not summarize away, reconstruct, rename, or drop any V3 package field. Missing, altered, generic, unsupported, or internally inconsistent package metadata requires `needs_return_to_evidence_qc[]`; it must not enter `content_enriched_and_language_polished[]`.

- evidence_complete: true"""

old_polish = """Each content_enriched_and_language_polished item must include:

- state: content_enriched_and_language_polished
- previous_state: evidence_complete_and_source_claim_covered
- draft_id
- source_spec_id
- source_story_ids
- region
- date
- cat
- sub_cat
- signal
- title
- sub
- gate
- fact
- implication
- urls
- related
- fact_sources
- evidence_complete: true"""

replace_once(
    ROOT / "docs/llm_prompts/v1/07_PROMPT_0_5_Evidence_QC.md",
    old_evidence,
    package_block_evidence,
    "Prompt 0.5 canonical V3 package producer contract",
)
replace_once(
    ROOT / "docs/llm_prompts/v1/08_PROMPT_0_6_Content_Polish.md",
    old_polish,
    package_block_polish,
    "Prompt 0.6 canonical V3 package producer contract",
)

old_overlay = """- Run `evidence_qc_v8_check.py`, `related_lifecycle_check.py`,
  `date_role_freshness_check.py --require-date-role`, and"""
new_overlay = """- Run `evidence_qc_v8_check.py`, `related_lifecycle_check.py --require-contract`,
  `date_role_freshness_check.py --require-date-role`, and"""
replace_once(
    ROOT / "docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md",
    old_overlay,
    new_overlay,
    "Prompt 0.7 strict related lifecycle invocation",
)
replace_once(
    ROOT / "validation_scripts/apply_prompt_contract_overlays.py",
    old_overlay,
    new_overlay,
    "overlay generator strict related lifecycle invocation",
)

log = ROOT / "docs/validation/STRUCTURAL_NEWS_VALUE_V3_VALIDATION_20260802.md"
with log.open("a", encoding="utf-8") as f:
    f.write("""

## Review 4839991362

- Prompt 0.5 promoted-item producer contract now preserves the complete canonical V3 non-execution package byte-for-byte.
- Prompt 0.6 polished-item producer contract preserves the same package and may not reconstruct or summarize it away.
- Prompt 0.7 and the overlay generator invoke `related_lifecycle_check.py --require-contract` for current V3 Final QC while legacy inventory mode remains permissive.
- Regression coverage blocks package-field loss and non-strict Final QC invocation.
""")

# Self-delete temporary patch machinery before commit.
(ROOT / "scripts/patch_structural_v3_review_4839991362.py").unlink()
(ROOT / ".github/workflows/patch-review-4839991362.yml").unlink()
