# Prompt 0.7 — Final Publish-Readiness QC V4

**Status:** `ACTIVE_CANONICAL`  
**Version:** `PROMPT_0_7_V4_20260829`

Create `publish_ready` only after all earlier state contracts remain valid.

Verify full schema/visible fields; evidence/source-claim coverage and source synthesis; dates/date roles and ID compatibility; event identity/duplicate risk; integrated selection route/anchor classes/score logic/before-after chain; Related lineage/targets/chronology/self/duplicate checks; terminology/title-body consistency; unsupported inference; latest candidate version; and no hidden regression of existing canonical content.

## Current-run scoped machine gate

Before any item can become `publish_ready`, build `CURRENT_RUN_ID_FILE` containing only identifiers introduced or materially updated by the current run. Use the final `id`/`card_id` when already assigned; otherwise carry the exact `draft_id` or `source_spec_id` that the candidate has used through the stage lineage. Do not use fuzzy, partial, title, company, or topic matching to define current-run scope.

Run the current merged baseline candidate artifact through the active validators with the strict scoped flags below:

```text
python validation_scripts/evidence_qc_v8_check.py <MERGED_BASELINE_CANDIDATE_ARTIFACT> --new-id-file <CURRENT_RUN_ID_FILE>
python validation_scripts/related_lifecycle_check.py <MERGED_BASELINE_CANDIDATE_ARTIFACT> --require-contract --allow-provisional-related --new-id-file <CURRENT_RUN_ID_FILE>
python validation_scripts/date_role_freshness_check.py <MERGED_BASELINE_CANDIDATE_ARTIFACT> --require-date-role --new-id-file <CURRENT_RUN_ID_FILE>
python validation_scripts/stage_artifact_contract_check.py 0.7 <MERGED_BASELINE_CANDIDATE_ARTIFACT>
```

`CURRENT_RUN_ID_FILE` resolution is fail-closed: every scoped identifier must resolve to exactly one candidate by exact `id`, `card_id`, `draft_id`, or `source_spec_id`. Zero-match, multi-match, ambiguous, or partial matches block Final QC. Current-run candidate-to-candidate Related edges may remain provisional only when each target is uniquely resolvable in the current run; Prompt 0.8 must convert them to final production IDs before merge.

Do **not** apply `--require-contract` or `--require-date-role` unscoped to the whole inherited legacy inventory merely to obtain a Final-QC result. The strict flags above are deliberately bound to `CURRENT_RUN_ID_FILE`; inherited legacy metadata is not silently rewritten or treated as newly authored by this run.

The stage-artifact gate and integrated selection/lineage checks remain mandatory. A validator failure must route the item to the earliest responsible stage; it may not be waived inside 0.7 to manufacture a green result.

Outcomes: `publish_ready`, `hold_evidence`, `return_content`, `return_upstream_selection_lineage_date`, or authorized reject. Publish-ready does not authorize formal 0.8 without separate 0.7C.
