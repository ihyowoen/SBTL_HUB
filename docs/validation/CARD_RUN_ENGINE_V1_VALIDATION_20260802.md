# Card Run Engine V1 Validation — 2026-08-02

## Scope

This record validates the executable ordinary-run path required by `CARD_INCREMENTAL_RUN_CONTRACT.md` and the Prompt 0.8 incremental addendum.

Implemented files:

- `scripts/apply_card_run.mjs`
- `scripts/apply_card_run_test.mjs`
- `scripts/validate_card_run_stage_artifacts.mjs`
- `scripts/validate_card_run_status_consistency.mjs`
- `scripts/validate_card_run_relations.mjs`
- `scripts/validate_card_run_lineage_containers.mjs`
- `scripts/validate_card_run_audits.mjs`
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
- A top-level `/related_ids/-` patch is blocked and is no longer permitted by the JSON schema.
- Directional relations require the complete source-side patch set. Reciprocal relations require the same complete patch set on both sides.
- A required relation side must already contain `related: []` and `related_lineage.related_ids: []` array containers.
- Missing or malformed relation containers fail closed before the apply engine runs. The engine never creates `related_ids: {"-": target}` objects from absent parents.
- Existing cards without an initialized lineage container are not eligible for ordinary `related_add` until a separately reviewed canonical-data migration initializes those containers.
- Every present status marker among `status`, `artifact_status`, `validation_status`, `state`, and `result` must be allowlisted.
- Status consistency applies to Stage 0.0D, Stage 0.0C, Stage 0.7C, every operation-level stage artifact, and every independent run audit.
- A leading `status: PASS` cannot hide `validation_status: FAIL`, `result: HOLD`, or another nonpassing marker.
- Stage 0.7C is bound to the current run ID, baseline, universe refs, and exact operations digest.
- Every `audit_refs` entry must be a JSON `card_run_audit_v1` artifact bound to the same run, baseline, governance refs, expected counts, exact operations digest, declared insert/update/related sets, and submitted full/lean output hashes.
- Every run audit must declare `audit_complete=true`, `reviewer_independence=SEPARATE_PASS`, zero deletion, and zero `related_remove`.
- `output_updated` must be a complete RFC 3339 date-time with timezone.
- Existing canonical serialization, latest-first order, counts, relation preservation, and byte-exact lean projection remain enforced.

## Pull-request security model

The pull-request workflow is verification-only.

- Workflow permissions are `contents: read` only.
- Both checkouts use `persist-credentials: false`.
- PR-supplied engine, validator, test, and workflow code never runs with write-capable repository credentials.
- Same-repository PRs, fork PRs, and `workflow_dispatch` all require submitted full and lean outputs to already be byte-exact.
- The workflow does not apply operations, commit generated files, push branches, or dispatch another workflow.
- Governed outputs and their independent run audit must be generated before submission using a trusted local or separately controlled execution path.

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

The following path is unsupported by both schema and runtime:

```text
/related_ids/-
```

Before relation patches can be submitted, the source side—and both sides for reciprocal relations—must already have:

```json
{
  "related": [],
  "related_lineage": {
    "related_ids": []
  }
}
```

If the canonical card lacks that shape, the run blocks with `BLOCKED_RELATED_PUBLISHED_CONTAINER_MISSING` or `BLOCKED_RELATED_LINEAGE_CONTAINER_MISSING`. Initialization is intentionally deferred to a separate canonical-data migration rather than silently performed by this code-only PR.

## Independent run audit contract

Every path in `audit_refs` must end in `.json` and contain a passing independent audit with at least the following binding fields:

```json
{
  "schema": "card_run_audit_v1",
  "status": "PASS",
  "audit_complete": true,
  "reviewer_independence": "SEPARATE_PASS",
  "run_id": "<card-run run_id>",
  "base_main_commit_sha": "<card-run base_main_commit_sha>",
  "base_full_blob_sha": "<card-run base_full_blob_sha>",
  "document_universe_manifest_ref": "<card-run document_universe_manifest_ref>",
  "coverage_discovery_ref": "<card-run coverage_discovery_ref>",
  "independent_completeness_ref": "<card-run independent_completeness_ref>",
  "reviewed_operations_sha256": "<stable SHA-256 of card-run operations>",
  "expected_before": 0,
  "expected_after": 0,
  "inserted_ids": [],
  "updated_ids": [],
  "related_additions": [],
  "zero_deletion_assertion": true,
  "zero_related_remove_assertion": true,
  "full_output_sha256": "<submitted canonical full SHA-256>",
  "lean_output_sha256": "<submitted lean projection SHA-256>"
}
```

The validator compares inserted IDs, updated IDs, and relation declarations to the actual run operations, and compares both output hashes to the committed files in the PR head. An unrelated JSON document, stale audit, audit from another baseline, or audit that reviewed different operations cannot satisfy `audit_refs`.

## Regression result

Actions `apply-card-run` run #42 on head `6eae40b71042dfed1374484eea5f4d4993515be8`:

```text
PASS: validate-engine
PASS: verify-submitted-run
PASS: independent audit happy path
PASS: stale audit run binding blocker
PASS: stale audit operations digest blocker
PASS: stale full-output hash blocker
PASS: conflicting audit status blocker
PASS: schema parse after removing /related_ids/-
PASS: relation lifecycle self-test
PASS: unsupported top-level related_ids blocker
PASS: missing published edge blocker
PASS: missing lineage patch blocker
PASS: missing lineage container blocker
PASS: malformed lineage related_ids object blocker
PASS: initialized inserted-card relation container
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
→ validate all run-level, operation-level, and audit status markers
→ validate each independent audit against run, baseline, operations, counts, IDs, relations, and committed output hashes
→ validate complete canonical related + related_lineage patches
→ fail closed when required relation containers are missing or malformed
→ require RFC3339 output_updated and run-bound Stage 0.7C
→ require submitted full/lean outputs to already equal the declared expected result
→ run full/public validators and byte-exact lean check
→ permit only the ephemeral apply-report working-tree change
→ never commit or push from the PR workflow
```

The first governed data PR remains a separate follow-up after this engine PR is independently reviewed and merged. A separate lineage-container migration must precede ordinary `related_add` for legacy cards that do not yet carry `related_lineage.related_ids` arrays.
