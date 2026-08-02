# Card Run Engine V1 Validation — 2026-08-02

## Scope

This record validates the executable ordinary-run path required by `CARD_INCREMENTAL_RUN_CONTRACT.md` and the Prompt 0.8 incremental addendum.

Implemented files:

- `scripts/apply_card_run.mjs`
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
- Stage 0.0D, Stage 0.0C, and Stage 0.7C references must resolve to passing JSON artifacts bound to the declared main/full baseline.
- Audit and per-operation stage artifact paths must exist and be nonempty. Referenced JSON stage artifacts may not carry blocked/failing status.
- Evidence references must resolve to an absolute HTTP(S) URL or a real repository file.
- The canonical full preserves the baseline BOM, indentation, CRLF/LF convention, and trailing-newline convention. A semantically equal minified working copy is normalized before merge.
- `github_merge_ready=true` is written only by verify mode after repository card validators and exact full-to-lean projection validation pass.

## Regression result

```text
PASS: engine syntax
PASS: test syntax
PASS: schema JSON parse
PASS: positive apply
PASS: byte-identical idempotent reapply
PASS: CRLF and indentation preservation
PASS: formatting normalization
PASS: latest-first result
PASS: metadata update
PASS: legacy dangling-edge preservation
PASS: governed reference resolution
PASS: 14 blocker cases
```

Blocker coverage includes:

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

A data PR must contain exactly one `runs/**/card-run.json`. The workflow:

```text
fetch base branch
→ lock declared main and full blob to the base commit
→ validate governance and operation references
→ apply declared operations
→ generate lean projection from full
→ run full/public validators and byte-exact lean check
→ verify expected full and set github_merge_ready=true
→ allow only full, lean, and apply-report working-tree changes
→ commit generated outputs
```

The first governed data PR remains a separate follow-up after this engine PR is independently reviewed and merged.
