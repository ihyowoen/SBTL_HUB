# Card Run Engine V1 Validation — 2026-08-02

## Scope

This record validates the executable ordinary-run path required by `CARD_INCREMENTAL_RUN_CONTRACT.md` and the Prompt 0.8 incremental addendum.

Implemented files:

- `scripts/apply_card_run.mjs`
- `scripts/apply_card_run_test.mjs`
- `scripts/validate_card_run_stage_artifacts.mjs`
- `scripts/validate_card_run_status_consistency.mjs`
- `scripts/validate_card_run_relations.mjs`
- `schemas/card-run.v1.schema.json`
- `.github/workflows/apply-card-run.yml`

This code PR does not modify `data/cards.full.json` or `public/data/cards.json`.

## Enforced invariants

- `data/cards.full.json` is the only canonical full inventory.
- The declared main commit, its canonical full blob, and `expected_before` must all match.
- Ordinary operations are limited to `insert`, `update`, and `related_add`; deletion and `related_remove` are rejected.
- Inserted cards may not carry relationship edges. All new relations pass through `related_add`.
- Canonical cards use the app-visible `related` array and `related_lineage`; the current 1,343-card baseline does not use a top-level `related_ids` mirror.
- Every `related_add` must include `/related/-`, `/related_lineage/related_ids/-`, and matching lineage relation type, reason, event-stage relationship, and direction.
- A top-level `/related_ids/-` patch is blocked because it cannot be safely appended to the current canonical shape.
- Directional relations require the complete source-side patch set. Reciprocal relations require the same complete patch set on both sides.
- Every present status marker among `status`, `artifact_status`, `validation_status`, `state`, and `result` must be allowlisted.
- Status consistency applies to Stage 0.0D, Stage 0.0C, Stage 0.7C, and every operation-level stage artifact.
- A leading `status: PASS` cannot hide `validation_status: FAIL`, `result: HOLD`, or another nonpassing marker.
- Stage 0.7C is bound to the current run ID, baseline, universe refs, and exact operations digest.
- `output_updated` must be a complete RFC 3339 date-time with timezone.
- Existing canonical serialization, latest-first order, counts, relation preservation, and byte-exact lean projection remain enforced.

## Pull-request security model

The pull-request workflow is verification-only.

- Workflow permissions are `contents: read` only.
- Both checkouts use `persist-credentials: false`.
- PR-supplied engine, validator, test, and workflow code never runs with write-capable repository credentials.
- Same-repository PRs, fork PRs, and `workflow_dispatch` all require submitted full and lean outputs to already be byte-exact.
- The workflow does not apply operations, commit generated files, push branches, or dispatch another workflow.
- Governed outputs must be generated before submission using a trusted local or separately controlled execution path.

## Related lifecycle contract

Each required side of a declared relation carries exactly one patch for:

```text
/related/-
/related_lineage/related_ids/-
/related_lineage/relation_type
/related_lineage/reason
/related_lineage/event_stage_relationship
/related_lineage/direction
```

The following path is currently unsupported and blocked:

```text
/related_ids/-
```

## Regression result

Actions `apply-card-run` run #35 on head `155c511c3d13ca81a26b71285ab66b42d35c4b19`:

```text
PASS: validate-engine
PASS: verify-submitted-run
PASS: relation lifecycle self-test
PASS: unsupported top-level related_ids blocker
PASS: missing published edge blocker
PASS: missing lineage blocker
PASS: operation-level conflicting status blocker
PASS: run-level governance conflicting status blocker
PASS: RFC3339 output_updated blocker
PASS: Stage 0.7C run and operations binding blockers
PASS: read-only checkout and workflow execution
```

Existing engine blocker coverage continues to include moved main, stale full binding, forged blob, forbidden delete, relation smuggling, missing target, count mismatch, prelinked insert, missing governance references, invalid evidence references, and undeclared working-full modification.

## Workflow behavior

A canonical-data PR must contain exactly one `runs/**/card-run.json`. A code-only PR may contain no run.

```text
trigger on run, engine, schema, workflow, canonical full, or lean projection changes
→ execute PR-controlled code with contents:read only and no persisted credentials
→ fetch and lock the base branch and canonical full blob
→ validate all run-level and operation-level status markers
→ validate complete canonical related + related_lineage patches
→ require RFC3339 output_updated and run-bound Stage 0.7C
→ require submitted full/lean outputs to already equal the declared expected result
→ run full/public validators and byte-exact lean check
→ permit only the ephemeral apply-report working-tree change
→ never commit or push from the PR workflow
```

The first governed data PR remains a separate follow-up after this engine PR is independently reviewed and merged.
