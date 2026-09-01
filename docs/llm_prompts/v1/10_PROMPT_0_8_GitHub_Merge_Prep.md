# Prompt 0.8 — Incremental Operation & GitHub Merge Preparation V4

**Status:** `ACTIVE_CANONICAL`  
**Version:** `PROMPT_0_8_V4_20260901`

Require formal 0.7 publish-ready and 0.7C authorization. Re-lock exact current main/canonical blob before operations. If baseline moved, rerun required 0.4+ checks.

Allowed ordinary operations: `insert`, `update`, `related_add`. No ordinary `delete` or `related_remove`.

Resolve all provisional current-batch relation identifiers to final production IDs and preserve a resolution ledger. Fail dangling, self, duplicate, ambiguous, unexplained, or unresolved relations.

## Post-resolution current-run scope

After final production IDs are assigned, write `ID_LEDGER` as the exact set of final production IDs for every current-run inserted or materially updated card. For a `related_add`, any endpoint whose canonical Related representation is materially changed by the declared patches is also part of this final current-run scope. The ledger must not contain provisional candidate IDs, titles, partial IDs, fuzzy aliases, or unresolved mappings. Every ledger ID must resolve to exactly one card in the candidate canonical full, and every current-run materialized/mutated candidate must resolve to exactly one ledger ID. Zero-match, multi-match, duplicate, or ambiguous identity resolution blocks merge preparation.

Re-run the semantic validators **after** provisional-to-production ID resolution and against the materialized candidate canonical full:

```text
python validation_scripts/related_lifecycle_check.py <CANDIDATE_CANONICAL_FULL> --require-contract --new-id-file <ID_LEDGER>
python validation_scripts/evidence_qc_v8_check.py <CANDIDATE_CANONICAL_FULL> --new-id-file <ID_LEDGER>
python validation_scripts/date_role_freshness_check.py <CANDIDATE_CANONICAL_FULL> --require-date-role --new-id-file <ID_LEDGER>
python validation_scripts/stage_artifact_contract_check.py 0.8 <PROMPT_0_8_ARTIFACT>
```

Prompt 0.8 must **not** use `--allow-provisional-related`: provisional Related targets are a bounded 0.7 allowance only. At merge prep all current-run Related targets must be final production IDs and must pass the active Related lifecycle/fresh-anchor contract in final graph form. A JavaScript card-run shape validator, declared patch validator, or projection validator does not substitute for these scoped semantic checks.

## Machine-bound Prompt 0.8 artifact

The formal card-run `audit_refs[]` must contain **exactly one** JSON artifact with `stage: "0.8"`. That artifact is the machine-consumed proof that post-resolution semantic validation and merge preparation passed for this exact run/baseline. It must bind to the same `run_id`, `base_main_commit_sha`, and `base_full_blob_sha` as the card-run and must include the final passing `github_merge_ready[]` item set.

Minimum passing envelope:

```json
{
  "stage": "0.8",
  "status": "GITHUB_MERGE_READY",
  "run_id": "<exact card-run run_id>",
  "base_main_commit_sha": "<exact card-run base main SHA>",
  "base_full_blob_sha": "<exact card-run canonical full blob SHA>",
  "github_main_sync_gate": {
    "status": "PASS",
    "baseline_locked": true,
    "main_unchanged_since_locked_preflight": true,
    "silent_rebase_performed": false
  },
  "lineage_merge_gate": {
    "final_qc_lineage_passed": true,
    "anchor_path_lineage_passed": true,
    "anchor_path_hold_count": 0,
    "github_ready_allowed": true
  },
  "github_merge_ready": [
    {
      "id": "<final production ID>",
      "source_spec_id": "<current-run source spec ID>",
      "related_lineage": {
        "status": "PASS",
        "relation_type": "new_unrelated_event",
        "related_ids": []
      },
      "date_role": {"representative_date": "YYYY-MM-DD"},
      "source_diversity_status": "PASS_MULTI_SOURCE",
      "merge_prep": {"status": "PASS"}
    }
  ]
}
```

`relation_type` and `related_ids` may instead carry a verified `distinct_follow_up` or `program_lineage` decision with its resolved production target(s). `source_diversity_status` may use the governed official/primary single-source exception when that exception itself passed the active evidence contract. A blocked/HOLD source state, null/empty Related or date-role object, unresolved/provisional target, false content/evidence attestation, or failing merge-prep gate cannot appear in `github_merge_ready[]`.

The repository workflow reconstructs the final `ID_LEDGER` from the declared operations and submitted canonical full, discovers this single 0.8 artifact from `audit_refs[]`, checks its run/baseline binding, and executes the four semantic commands above before the byte-exact apply verification. Therefore a prose-only Prompt 0.8 claim or an unreferenced 0.8 file does not authorize merge.

Any failure routes the item back to the earliest responsible stage or blocks the run. `github_merge_ready` may not be emitted while any scoped semantic validator is failing or while `ID_LEDGER` differs from the final current-run identity set.

Create governed card-run against locked baseline. Validate operation counts/targets/audit binding, apply canonical full mutation, generate lean deterministically from full, and prove no undeclared existing-card change or lost existing Related edge.

Run current card-run/schema/engine, full/lean/card/date/story-ID/Related/source/stage-lineage/selection-route validators, projection check, diff sanity, and workflows. Only this stage may emit formal full-run `github_merge_ready`; it is distinct from manual direct-add.
