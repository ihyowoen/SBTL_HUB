# Prompt 0.7C — Independent Completeness & News-Value Review V4

**Status:** `ACTIVE_CANONICAL`  
**Version:** `PROMPT_0_7C_V4_20260901`

Run separately from authoring/final QC.

Six rounds: (1) universe accounting; (2) existing-full duplicate/reinforcement/update/follow-up/new-event challenge; (3) event-stage/lineage challenge; (4) fact/claim completeness; (5) news-value/scoring/caps/urgency challenge; (6) exclusion/rescue red-team.

Recheck mandatory regions/topics and zero-coverage structural lenses. Do not force cards for balance.

## Formal card-run binding

Before authorizing Prompt 0.8, prepare the exact proposed current-run operation set (`insert`, `update`, `related_add`) **without mutating canonical data** and calculate its stable SHA-256 using the same canonical operation serialization as the card-run engine. The independent reviewer must review that exact operation set, not a later silently changed set.

The formal 0.7C artifact used as `independent_completeness_ref` must contain the machine-required envelope and exact run bindings. Because this workflow explicitly does **not** claim absolute global completeness, the canonical passing state is `PASS_WITH_DECLARED_RESIDUAL_RISK` and `residual_risks[]` must contain at least one concrete residual-risk statement. An empty `residual_risks[]` is inconsistent with that status and is merge-blocking.

```json
{
  "stage": "0.7C",
  "status": "PASS_WITH_DECLARED_RESIDUAL_RISK",
  "completeness_status": "PASS_WITH_DECLARED_RESIDUAL_RISK",
  "run_id": "<exact card-run run_id>",
  "base_main_commit_sha": "<exact locked main SHA>",
  "base_full_blob_sha": "<exact locked data/cards.full.json blob SHA>",
  "document_universe_manifest_ref": "<exact 0.0D artifact ref>",
  "coverage_discovery_ref": "<exact 0.0C artifact ref>",
  "reviewed_operations_sha256": "<stable SHA-256 of the exact proposed operations object>",
  "source_universe_accounted": true,
  "regional_search_complete": true,
  "topic_search_complete": true,
  "baseline_follow_up_review_complete": true,
  "review_pool_rescue_complete": true,
  "must_report_candidates_accounted": true,
  "material_exclusions": [],
  "known_unknowns": [],
  "residual_risks": [
    "Absolute global completeness beyond the registry-bound search universe is not claimed."
  ],
  "reviewer_independence": "SEPARATE_PASS",
  "prompt_0_8_authorized": true
}
```

`status` is the machine stage status. `completeness_status` is the editorial completeness conclusion and must exactly equal `status`. `PASS_WITH_DECLARED_RESIDUAL_RISK` is valid only when `residual_risks[]` is non-empty and each entry is a concrete non-empty residual-risk statement.

The following bindings must exactly equal the subsequent formal card-run fields:

- `run_id`;
- `base_main_commit_sha`;
- `base_full_blob_sha`;
- `document_universe_manifest_ref`;
- `coverage_discovery_ref`;
- `reviewed_operations_sha256`.

If Prompt 0.8 changes any proposed operation after this review, the operation SHA changes and the prior 0.7C authorization becomes stale. Re-run the affected completeness review and emit a newly bound 0.7C artifact before merge preparation may continue.

Absolute global completeness is not claimed. Any unaccounted must-report candidate, mandatory coverage gap, unresolved material exclusion, missing independent pass, empty/false residual-risk declaration, binding mismatch, or operation-set drift blocks 0.8.