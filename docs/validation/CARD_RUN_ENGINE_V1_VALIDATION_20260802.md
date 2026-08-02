# Card Run Engine V1 Validation — 2026-08-02

## Scope

This record validates the first executable ordinary-run path required by `CARD_INCREMENTAL_RUN_CONTRACT.md` and the Prompt 0.8 incremental addendum.

Implemented files:

- `scripts/apply_card_run.mjs`
- `schemas/card-run.v1.schema.json`
- `.github/workflows/apply-card-run.yml`
- `scripts/apply_card_run_test.mjs`

## Enforced invariants

- `data/cards.full.json` is the only canonical baseline.
- `base_main_commit_sha`, canonical Git blob SHA, and `expected_before` must all match.
- The workflow reconstructs the declared baseline from `git show <base_main_commit_sha>:data/cards.full.json`; it never treats an already-generated PR working copy as the original baseline.
- Ordinary operations are limited to `insert`, `update`, and `related_add`.
- Card deletion and `related_remove` are rejected.
- Existing IDs cannot disappear or change.
- Existing `related`, `related_ids`, and `related_lineage` values must remain a deep subset of the result.
- Updates may change only declared JSON Pointer paths and may not edit relation roots.
- Relation changes are append-only and require source, target, type, evidence, lineage reason, event-stage relationship, and direction.
- New missing, duplicate, and self-related edges are rejected.
- Counts must reconcile exactly.
- Unpositioned inserts are applied as one latest-first block without reordering existing cards.
- The canonical full is written before the existing full-to-lean exporter runs.
- `github_merge_ready` remains false until all repository validators and the exact lean-projection check pass.

## Local regression result

```text
PASS: apply_card_run_test — positive + 5 blockers
PASS: schema JSON parse
PASS: workflow YAML parse
PASS: synthetic apply → lean → verify → idempotent rerun
PASS: moved-main baseline blocker
```

Covered blocker cases:

1. stale canonical blob SHA;
2. forbidden delete operation;
3. relation modification smuggled through update;
4. newly missing related target;
5. count reconciliation failure;
6. current main SHA differing from the declared run baseline.

## Rerun and generated-commit safety

The first workflow execution may commit generated `data/cards.full.json`, `public/data/cards.json`, and `apply-report.json` to the data PR branch. A later `pull_request synchronize` execution must not reinterpret that generated full as the declared original baseline. The workflow therefore reconstructs the immutable baseline from the declared base commit and verifies its Git blob SHA before every application. Re-execution deterministically regenerates the same outputs and produces no further commit when the branch already matches the declared result.

## Operational boundary

This PR installs the engine only. It does not apply the 2026-08-01 editorial input and does not modify either card inventory. After this PR is reviewed and merged, the first data PR may submit exactly one governed input at `runs/2026-08-01/card-run.json`; the workflow will generate and validate the canonical full, lean projection, and apply report.
