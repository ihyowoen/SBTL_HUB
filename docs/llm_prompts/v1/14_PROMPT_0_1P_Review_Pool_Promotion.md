# Prompt 0.1P — Authorized Review-Pool Promotion V4

**Status:** `ACTIVE_CANONICAL`  
**Version:** `PROMPT_0_1P_V4_20260829`

Use only after explicit authorization to revisit Stage A `candidate_review_pool` items. Perform bounded research needed to resolve the recorded promotion question. Reapply integrated Stage A four judgments, anchor classes, decision-value score/caps, before/after chain, baseline/Related pre-pass, and Stage B source-path viability against current baseline.

## Machine-bound promotion contract

A promoted review-pool item is not a separate Stage A bypass artifact. A successful promotion must be re-emitted through the ordinary validator-bound Stage A passing bucket:

`strict_passed_spec[]`

Each promoted item must contain the complete current Stage A V4 schema and must satisfy the same policy version, selection route, score/cap metadata, Related pre-pass, date-role, evidence-path, and V3-compatibility requirements as an item that passed Stage A on its first review.

The surrounding artifact must be Stage-A-compatible and include the ordinary Stage A top-level PASS gates required before Stage B. Promotion provenance may be recorded separately, but `promoted_strict_passed_spec` must not be used as the only passing bucket and must never be treated as authorization to skip the Stage A machine gate.

Non-promoted items remain in review/watch/support/reject with an evidence-backed reason. Only items present in validated `strict_passed_spec[]` may enter Stage B. Do not bypass duplicate, cardability, freshness, Related, or news-value gates.

Before Stage B, run both active Stage A checks:

`python validation_scripts/stage_artifact_contract_check.py A <PROMOTED_STAGE_A_JSON>`

`python validation_scripts/stage_lineage_contract_check.py stage_a <PROMOTED_STAGE_A_JSON>`
