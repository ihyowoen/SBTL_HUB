# Prompt 0.4 — Current-Baseline Addability Revalidation V4

**Status:** `ACTIVE_CANONICAL`  
**Version:** `PROMPT_0_4_ADDABILITY_V4_20260829`

## Purpose
Determine whether each latest `accepted_fact_safe` card is still addable against the exact current canonical full and current accepted batch.

**This is not the first Related audit.** Stage A pre-passed lineage, Stage B resolved evidence, and Stage C locked it. 0.4 revalidates identity/lineage after baseline movement and current-batch interaction.

Use only latest accepted versions. Re-lock current main/full SHA. If baseline moved, use the new baseline and record it.

Checks: exact/canonical URL, normalized title and source-story collision, event fingerprint/broader representative coverage, Stage C locked relation and predecessor/successor judgment, fresh anchor, candidate-to-candidate edges, stale republication, target existence, update/reinforcement opportunity, and card-ID/date implications.

## Machine-bound output contract

The single passing production bucket is **`addable_merge_safe[]`**. Do not emit passing cards only under route-specific top-level bucket names.

Every item in `addable_merge_safe[]` must contain at least:

- `source_spec_id`
- `event_fingerprint`
- `related_lineage`
- `addability_outcome`

`addability_outcome` preserves the semantic route and must be exactly one of:

- `addable_merge_safe_new_unrelated`
- `addable_merge_safe_distinct_follow_up`
- `addable_merge_safe_program_lineage`

Non-passing items remain outside `addable_merge_safe[]` and may use these explicit dispositions: `duplicate_hold_same_event`, `existing_reinforcement`, `existing_card_update`, `baseline_conflict`, `review_pool_deferred_related_uncertain`.

The artifact must also emit `lineage_guard: "PASS"` only when every item in the passing bucket has survived the current-baseline identity, Related, and addability checks. An empty passing bucket is not a successful 0.4 result when accepted Stage C candidates were supplied; account for every supplied candidate in either the passing bucket or a non-passing disposition.

Reset downstream publish-readiness flags. Addable means safe to continue through post-acceptance QC, not ready to merge. Carry the Stage C selection/anchor/lineage package unless explicitly routed upstream. Emit complete accounting and baseline provenance.

Before 0.5, the artifact must pass:

`python validation_scripts/stage_artifact_contract_check.py 0.4 <PROMPT_0_4_JSON>`
