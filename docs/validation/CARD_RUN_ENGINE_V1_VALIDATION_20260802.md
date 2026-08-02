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
- `base_main_commit_sha`, the Git blob at `<base commit>:data/cards.full.json`, and `expected_before` must all match.
- The expected result is rebuilt from bytes read with `git show <declared main>:data/cards.full.json`; a branch-modified full can never become the baseline.
- The working full must be either the declared baseline, the exact expected result, or a semantically equal result needing format normalization. Any other branch edit blocks with `BLOCKED_UNDECLARED_CARD_DIFF`.
- Ordinary operations are limited to `insert`, `update`, and `related_add`; card deletion and `related_remove` are rejected.
- Inserted cards may not carry relationship edges. All new relations must pass through `related_add`.
- Every `related_add` must include the app-visible `/related/-` edge, the `/related_ids/-` mirror, the `/related_lineage/related_ids/-` edge, and matching lineage metadata for relation type, reason, event-stage relationship, and direction.
- Directional relations require the complete source-side patch set. Reciprocal relations require the same complete patch set on both sides.
- A lone `related_ids` patch, a lone `related` patch, missing lineage metadata, duplicate card/path patches, and undeclared-side patches are blocked before apply.
- Every relation patch must point to the operation’s declared opposite endpoint. A single operation cannot smuggle a third relation target.
- Existing `related` and `related_ids` edges are preserved; legacy dangling edges remain frozen and no new dangling edge may appear.
- Updates may change only declared JSON Pointer paths and may not edit relation roots.
- Counts reconcile exactly and the result remains stable latest-first.
- Stage 0.0D, Stage 0.0C, and Stage 0.7C references must resolve to passing JSON artifacts bound to the declared run and baseline.
- Stage 0.7C must match the current `run_id`, base main SHA, full blob SHA, document-universe reference, coverage-discovery reference, and a stable SHA-256 digest of the exact declared operations.
- Audit and per-operation stage artifact paths must exist and be nonempty.
- Every present stage-status marker among `status`, `artifact_status`, `validation_status`, `state`, and `result` must be in the explicit passing allowlist.
- A leading `status: PASS` cannot hide `validation_status: FAIL`, `result: HOLD`, or any other nonpassing marker.
- `HOLD`, `SKIPPED`, missing status, and every unrecognized status are rejected before the apply engine can emit merge-readiness output.
- `output_updated` must be a complete RFC 3339 date-time with timezone; bare years, date-only values, locale dates, impossible calendar dates, and invalid offsets are rejected.
- Evidence references must resolve to an absolute HTTP(S) URL or a real repository file.
- The canonical full preserves the baseline BOM, indentation, CRLF/LF convention, and trailing-newline convention. A semantically equal minified working copy is normalized before merge.
- `github_merge_ready=true` is written only by verify mode after repository card validators and exact full-to-lean projection validation pass.
- Pull requests that edit `data/cards.full.json` or `public/data/cards.json` must contain exactly one governed `runs/**/card-run.json`.
- Same-repository PRs may receive generated full, lean, and report commits from the workflow.
- Fork PRs never receive a generated push. They must already contain the byte-exact generated full and lean outputs; the workflow performs verify-only validation and rejects runner-side full/lean changes.
- `workflow_dispatch` is explicitly read-only. It verifies the selected ref and run but never applies or pushes generated outputs; submitted full/lean outputs must already be byte-exact.

## Stage 0.7C run binding

The independent completeness artifact must contain the following exact bindings:

```json
{
  "stage": "0.7C",
  "status": "PASS_WITH_DECLARED_RESIDUAL_RISK",
  "run_id": "<card-run run_id>",
  "base_main_commit_sha": "<card-run base_main_commit_sha>",
  "base_full_blob_sha": "<card-run base_full_blob_sha>",
  "document_universe_manifest_ref": "<card-run document_universe_manifest_ref>",
  "coverage_discovery_ref": "<card-run coverage_discovery_ref>",
  "reviewed_operations_sha256": "<stable canonical SHA-256 of card-run operations>"
}
```

The operations digest recursively sorts object keys while preserving array order. Reusing a passing 0.7C artifact from another run, baseline, universe, or operation set is blocked.

## Explicit passing-status allowlist

Every present status field is validated. Current accepted states are:

```text
PASS
PASSED
PASS_WITH_DECLARED_RESIDUAL_RISK
PASS_WITH_NOTES
PASS_WITH_WARNINGS
VERIFIED
ACCEPTED_FACT_SAFE
ACCEPTED_FACT_SAFE_AFTER_CONTROLLED_RESCUE
ADDABLE_MERGE_SAFE
EVIDENCE_COMPLETE
SOURCE_CLAIM_COVERED
EVIDENCE_COMPLETE_AND_SOURCE_CLAIM_COVERED
CONTENT_ENRICHED
LANGUAGE_TERMINOLOGY_POLISHED
CONTENT_ENRICHED_AND_LANGUAGE_TERMINOLOGY_POLISHED
PUBLISH_READY
GITHUB_MERGE_READY
```

Unknown or contradictory nonpassing values do not pass by omission. Adding a new valid stage state requires an intentional code and regression-test change.

## Related lifecycle contract

Each required side of a declared relation must carry exactly one patch for every path below:

```text
/related/-
/related_ids/-
/related_lineage/related_ids/-
/related_lineage/relation_type
/related_lineage/reason
/related_lineage/event_stage_relationship
/related_lineage/direction
```

The values must match the declared source, target, relation type, lineage reason, event-stage relationship, and direction. This closes the gap where the app-visible edge, legacy mirror, or lineage metadata could diverge.

## Regression result

Actions `apply-card-run` run #31 on head `041ff0af3b77db6dced0f5875cf3dd5af72fb9d5`:

```text
PASS: validate-engine
PASS: apply
PASS: engine syntax
PASS: engine regression suite
PASS: schema JSON parse
PASS: stage-status exact-allowlist self-test
PASS: conflicting status marker blocker
PASS: related lifecycle validator self-test
PASS: related_ids-only blocker
PASS: missing lineage blocker
PASS: missing related_ids mirror blocker
PASS: non-RFC3339 output_updated blocker
PASS: stale Stage 0.7C run binding blocker
PASS: stale Stage 0.7C operation digest blocker
```

Existing engine blocker coverage continues to include moved main, stale full binding, forged blob, forbidden delete, relation smuggling, missing target, count mismatch, prelinked insert, missing governance references, invalid evidence references, and undeclared working-full modification.

## Workflow behavior

A canonical-data PR must contain exactly one `runs/**/card-run.json`. A code-only PR may contain no run.

```text
trigger on run, engine, schema, workflow, canonical full, or lean projection changes
→ fetch the base branch
→ detect canonical-data changes and require exactly one governed run
→ checkout the PR head, including fork PR heads
→ validate all present status markers
→ validate complete related lifecycle patches
→ require RFC3339 output_updated and run-bound Stage 0.7C
→ lock declared main and full blob to the base commit
→ same-repository PR: apply declared operations and generate full/lean/report
→ fork PR: skip apply and require submitted full/lean to already be byte-exact
→ workflow_dispatch: skip apply and perform the same read-only verification
→ run full/public validators and byte-exact lean check
→ verify expected full and set github_merge_ready=true
→ same-repository PR: allow only full, lean, and apply-report working-tree changes
→ fork/dispatch: allow only the ephemeral apply-report change; any full/lean change fails
→ commit generated outputs only for same-repository PR branches
```

The first governed data PR remains a separate follow-up after this engine PR is independently reviewed and merged.
