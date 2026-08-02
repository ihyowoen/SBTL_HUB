# Card Run Engine V1 Validation — 2026-08-02

## Scope

This record validates the executable ordinary-run path required by `CARD_INCREMENTAL_RUN_CONTRACT.md` and the Prompt 0.8 incremental addendum.

Implemented files:

- `scripts/apply_card_run.mjs`
- `scripts/validate_card_run_stage_artifacts.mjs`
- `schemas/card-run.v1.schema.json`
- `.github/workflows/apply-card-run.yml`
- `scripts/apply_card_run_test.mjs`

This code PR does not modify `data/cards.full.json` or `public/data/cards.json`.

## Enforced invariants

- `data/cards.full.json` is the only canonical full inventory.
- `base_main_commit_sha`, the Git blob at `<base commit>:data/cards.full.json`, and `expected_before` must all match.
- The expected result is rebuilt from bytes read with `git show <declared main>:data/cards.full.json`; a branch-modified full can never become the baseline.
- The working full must be either the declared baseline, the exact expected result, or a semantically equal result needing format normalization. Any other branch edit blocks with `BLOCKED_UNDECLARED_CARD_DIFF`.
- Ordinary operations are limited to `insert`, `update`, and `related_add`; card deletion and `related_remove` are rejected.
- Inserted cards may not carry relationship edges. All new `related`, `related_ids`, and non-independent lineage links must pass through `related_add`.
- Every edge-valued relation patch must point to the operation’s declared opposite endpoint. A single operation cannot smuggle a third relation target.
- Directional and reciprocal edge patches are checked independently.
- Existing `related` and `related_ids` edges are preserved; legacy dangling edges remain frozen and no new dangling edge may appear.
- Updates may change only declared JSON Pointer paths and may not edit relation roots.
- Counts reconcile exactly and the result remains stable latest-first.
- Stage 0.0D, Stage 0.0C, and Stage 0.7C references must resolve to passing JSON artifacts bound to the declared run and baseline.
- Stage 0.7C must match the current `run_id`, base main SHA, full blob SHA, document-universe reference, coverage-discovery reference, and a stable SHA-256 digest of the exact declared operations.
- Audit and per-operation stage artifact paths must exist and be nonempty.
- Every per-operation stage artifact must be JSON and carry an explicit status in the allowlist enforced by `scripts/validate_card_run_stage_artifacts.mjs`.
- `HOLD`, `SKIPPED`, missing status, and every unrecognized status are rejected before the apply engine can emit merge-readiness output.
- `output_updated` must be a complete RFC 3339 date-time with timezone; bare years, date-only values, locale dates, impossible calendar dates, and invalid offsets are rejected.
- Evidence references must resolve to an absolute HTTP(S) URL or a real repository file.
- The canonical full preserves the baseline BOM, indentation, CRLF/LF convention, and trailing-newline convention. A semantically equal minified working copy is normalized before merge.
- `github_merge_ready=true` is written only by verify mode after repository card validators and exact full-to-lean projection validation pass.
- Pull requests that edit `data/cards.full.json` or `public/data/cards.json` must contain exactly one governed `runs/**/card-run.json`.
- Same-repository PRs may receive generated full, lean, and report commits from the workflow.
- Fork PRs never receive a generated push. They must already contain the byte-exact generated full and lean outputs; the workflow performs verify-only validation and rejects any runner-side full/lean change.

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

The per-operation stage-artifact preflight accepts only an explicitly enumerated passing state. Current accepted states are:

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

Unknown values do not pass by omission. Adding a new valid stage state requires an intentional code and regression-test change.

## Regression result

```text
PASS: engine syntax
PASS: test syntax
PASS: governance preflight syntax
PASS: stage-status exact-allowlist self-test
PASS: schema JSON parse
PASS: positive apply
PASS: byte-identical idempotent reapply
PASS: CRLF and indentation preservation
PASS: formatting normalization
PASS: latest-first result
PASS: metadata update
PASS: legacy dangling-edge preservation
PASS: governed reference resolution
PASS: HOLD rejected
PASS: SKIPPED rejected
PASS: missing stage status rejected
PASS: non-RFC3339 output_updated rejected
PASS: impossible calendar date rejected
PASS: stale Stage 0.7C run binding rejected
PASS: stale Stage 0.7C operation digest rejected
PASS: 14 engine blocker cases
```

Engine blocker coverage includes:

1. current main SHA moved;
2. Stage 0.0D/full binding stale;
3. forged full blob rejected by Git object lookup;
4. forbidden delete operation;
5. relation edit smuggled through update;
6. missing related target;
7. third endpoint smuggled through `related`;
8. count reconciliation failure;
9. prelinked inserted card;
10. third endpoint smuggled through `related_lineage`;
11. missing Stage 0.0D artifact;
12. blocked Stage 0.7C artifact;
13. missing per-operation stage artifact;
14. invalid evidence reference;
15. undeclared working-full modification.

## Workflow behavior

A canonical-data PR must contain exactly one `runs/**/card-run.json`. A code-only PR may contain no run. The workflow:

```text
trigger on run, engine, schema, workflow, canonical full, or lean projection changes
→ fetch the base branch
→ detect canonical-data changes and require exactly one governed run
→ checkout the PR head, including fork PR heads
→ require exact allowlisted PASS states, RFC3339 output_updated, and run-bound Stage 0.7C
→ lock declared main and full blob to the base commit
→ same-repository: apply declared operations and generate full/lean/report
→ fork: skip apply and require submitted full/lean to already be byte-exact expected outputs
→ run full/public validators and byte-exact lean check
→ verify expected full and set github_merge_ready=true
→ same-repository: allow only full, lean, and apply-report working-tree changes
→ fork: allow only the ephemeral apply-report change; any full/lean change fails
→ commit generated outputs only for same-repository PR branches
```

Fork PRs receive full read-only verification but never receive a token-backed generated push. They cannot pass by submitting only a run artifact.

The first governed data PR remains a separate follow-up after this engine PR is independently reviewed and merged.
