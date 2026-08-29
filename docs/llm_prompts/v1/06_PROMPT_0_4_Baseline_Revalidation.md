# Prompt 0.4 — Current-Baseline Addability Revalidation V4

**Status:** `ACTIVE_CANONICAL`  
**Version:** `PROMPT_0_4_ADDABILITY_V4_20260829`

## Purpose
Determine whether each latest `accepted_fact_safe` card is still addable against the exact current canonical full and current accepted batch.

**This is not the first Related audit.** Stage A pre-passed lineage, Stage B resolved evidence, and Stage C locked it. 0.4 revalidates identity/lineage after baseline movement and current-batch interaction.

Use only latest accepted versions. Re-lock current main/full SHA. If baseline moved, use new baseline and record it.

Checks: exact/canonical URL, normalized title and source-story collision, event fingerprint/broader representative coverage, Stage C locked relation and predecessor/successor judgment, fresh anchor, candidate-to-candidate edges, stale republication, target existence, update/reinforcement opportunity, and card-ID/date implications.

Outcomes: `addable_merge_safe_new_unrelated`, `addable_merge_safe_distinct_follow_up`, `addable_merge_safe_program_lineage`, `duplicate_hold_same_event`, `existing_reinforcement`, `existing_card_update`, `baseline_conflict`, `review_pool_deferred_related_uncertain`.

Reset downstream publish-readiness flags. Addable means safe to continue through post-acceptance QC, not ready to merge. Carry Stage C selection/anchor/lineage package unless explicitly routed upstream. Emit complete accounting and baseline provenance.