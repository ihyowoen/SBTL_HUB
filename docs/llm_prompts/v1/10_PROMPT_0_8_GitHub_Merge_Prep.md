# Prompt 0.8 — Incremental Operation & GitHub Merge Preparation V4

**Status:** `ACTIVE_CANONICAL`  
**Version:** `PROMPT_0_8_V4_20260902_R2`

Require formal 0.7 publish-ready and 0.7C authorization. Re-lock exact current main/canonical blob before operations. If baseline moved, rerun required 0.4+ checks.

Allowed ordinary operations: `insert`, `update`, `related_add`. No ordinary `delete` or `related_remove`.

Resolve all provisional current-batch relation identifiers to final production IDs and preserve a resolution ledger. Fail dangling, self, duplicate, ambiguous, unexplained, or unresolved relations.

## Post-resolution current-run scopes

Prompt 0.8 uses two related but distinct final-ID sets:

1. **Strict card-QC scope (`ID_LEDGER.ids[]`)** — the exact final production IDs for current-run inserted cards and materially updated cards. This is the scope passed to the three card-wide semantic validators below.
2. **Operation identity set (`ID_LEDGER.operation_ids[]`)** — the strict card-QC scope plus the single governed identity endpoint for each `related_add`. The governed endpoint is resolved from `identity_card_id`, canonical/declared `source_spec_id`, or another unambiguous current-run identity rule. `github_merge_ready[]` must equal this set exactly.

The ledger is a JSON document, not newline text. Minimum shape:

```json
{
  "schema": "prompt_0_8_current_run_id_ledger_v1",
  "ids": ["<inserted-or-materially-updated-final-ID>"],
  "operation_ids": ["<all-governed-operation-final-IDs>"]
}
```

A reciprocal `related_add` may patch the existing predecessor/program card to maintain the mirror representation. **Patch presence alone does not make that legacy counterpart a new current-run card-wide QC subject.** The pre-existing counterpart is therefore not added to `ids[]` merely because it receives a declared reciprocal Related patch. The Related operation itself remains fully bound to the same A→0.7 candidate identity, counterpart, relation type, reason, direction, and event-stage semantics, and its governed identity must appear in `operation_ids[]` and `github_merge_ready[]`.

Every ID in either set must resolve to exactly one card in the candidate canonical full. The ledger must not contain provisional candidate IDs, titles, partial IDs, fuzzy aliases, or unresolved mappings. Zero-match, multi-match, duplicate, or ambiguous identity resolution blocks merge preparation.

When `ids[]` is non-empty, re-run the semantic validators **after** provisional-to-production ID resolution and against the materialized candidate canonical full:

```text
python validation_scripts/related_lifecycle_check.py <CANDIDATE_CANONICAL_FULL> --require-contract --new-id-file <ID_LEDGER>
python validation_scripts/evidence_qc_v8_check.py <CANDIDATE_CANONICAL_FULL> --new-id-file <ID_LEDGER>
python validation_scripts/date_role_freshness_check.py <CANDIDATE_CANONICAL_FULL> --require-date-role --new-id-file <ID_LEDGER>
```

For a relation-only formal run with no inserted/materially updated card, `ids[]` may be empty while `operation_ids[]` remains non-empty. In that narrow case the card-wide current-run validators are not applied to an unchanged legacy reciprocal endpoint merely because its Related mirror is patched; the formal Related semantics remain enforced by the operation-bound A→0.7 chain and the exact Prompt 0.8 operation identity set.

Always validate the Prompt 0.8 artifact itself:

```text
python validation_scripts/stage_artifact_contract_check.py 0.8 <PROMPT_0_8_ARTIFACT>
```

Prompt 0.8 must **not** use `--allow-provisional-related`: provisional Related targets are a bounded 0.7 allowance only. At merge prep all current-run Related targets must be final production IDs. A JavaScript card-run shape validator, declared patch validator, or projection validator does not substitute for the scoped semantic checks.

## Machine-bound Prompt 0.8 artifact

The formal card-run `audit_refs[]` must contain **exactly one** JSON artifact with `stage: "0.8"`. That artifact is the machine-consumed proof that post-resolution semantic validation and merge preparation passed for this exact run/baseline. It must bind to the same `run_id`, `base_main_commit_sha`, and `base_full_blob_sha` as the card-run and must include the final passing `github_merge_ready[]` item set exactly equal to `ID_LEDGER.operation_ids[]`.

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

The repository workflow executes `scripts/validate_prompt_0_8_semantic_gate.mjs` to derive and validate the JSON ledger and exact merge-prep item set, and `scripts/validate_card_run_audits_dispatch.mjs` to separate the single Prompt 0.8 artifact from true `card_run_audit_v1` references without sending a repository-external temporary run to the audit validator. Both helpers have executable self-tests and durable runtime regressions. The workflow then runs the scoped Python semantic validators and the 0.8 stage checker before byte-exact apply verification.

Any failure routes the item back to the earliest responsible stage or blocks the run. `github_merge_ready` may not be emitted while a required scoped semantic validator is failing or while the operation identity set differs from the final reviewed item set.

Create governed card-run against locked baseline. Validate operation counts/targets/audit binding, apply canonical full mutation, generate lean deterministically from full, and prove no undeclared existing-card change or lost existing Related edge.

Run current card-run/schema/engine, full/lean/card/date/story-ID/Related/source/stage-lineage/selection-route validators, projection check, diff sanity, and workflows. Only this stage may emit formal full-run `github_merge_ready`; it is distinct from manual direct-add.
