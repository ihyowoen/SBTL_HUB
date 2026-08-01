# SBTL_HUB Run Governance Index

**Status:** `ACTIVE_CANONICAL`  
**Version:** `DYNAMIC_RUN_GOVERNANCE_V1`

## 0. Purpose

This document is the mandatory entry point for every governed SBTL_HUB news-card run.

No fixed list of “core documents” is complete by itself. A run is governed by the complete active rule universe identified from the current GitHub `main`, including canonical documents, mandatory addenda and overrides, applicable validator contracts, and open remediation records.

A run must not start Stage 0.0C, Stage A, or any later stage until Stage 0.0D has produced a valid document-universe manifest.

## 1. Canonical data principle

- `data/cards.full.json` is the only canonical card inventory.
- `public/data/cards.json` is a generated lean projection for the application.
- A branch file, prior run payload, downloaded replacement file, chat attachment, or memory-based copy is not a canonical baseline.
- The current run must record the Git commit SHA and canonical full blob SHA used as its baseline.

## 2. Governance classes

Every relevant repository document must be classified as exactly one of:

- `ACTIVE_CANONICAL`
- `ACTIVE_MANDATORY_ADDENDUM`
- `ACTIVE_VALIDATOR_CONTRACT`
- `OPEN_REMEDIATION`
- `ACTIVE_MIGRATION`
- `REFERENCE_ONLY`
- `SUPERSEDED`
- `ARCHIVED`

Only the first four classes apply automatically to ordinary runs.

`ACTIVE_MIGRATION` applies only when the run intake explicitly activates that migration. Migration documents never become default operating rules merely because they exist in the repository.

## 3. Permanent canonical rule domains

The active document universe must cover, at minimum, the following domains:

### 3.1 Fact and evidence authority

- `docs/FACT_DISCIPLINE.md`
- `docs/SOURCE_AUDIT_CONTRACT.md`
- active source-diversity and source-resolution rules registered in the canonical prompt package

### 3.2 Editorial workflow and stage authority

- `docs/PROMPT_ABC_DEFAULT_MODE.md`
- `docs/PROMPT_ABC_SUPPORTING_RULES.md`
- `docs/WORKFLOW.md`
- `docs/OPERATIONS.md`
- all active named-stage prompts registered in `docs/llm_prompts/v1/`

### 3.3 Schema, identity, lineage, and relations

- `docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md`
- `docs/CARD_ID_STANDARD.md`
- `docs/SCHEMA_CONTRACT_STAGE_LINEAGE.md`
- `docs/RELATED_LIFECYCLE_CONTRACT.md`
- active date, story-ID, and related integrity overrides and validators

### 3.4 Editorial value and completeness

- `docs/EDITORIAL_VALUE_AND_COMPLETENESS_STANDARD.md`
- `docs/DOCUMENT_UNIVERSE_POLICY.md`
- Stage 0.0D, Stage 0.0C, and Stage 0.7C prompts registered in the canonical prompt package

### 3.5 Incremental canonical operation

- `docs/CARD_INCREMENTAL_RUN_CONTRACT.md`
- the current canonical full and lean-projection contract
- applicable declared-diff, schema, and production-verification validators

### 3.6 Post-acceptance quality

- `docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md`
- applicable Prompt 0.4–0.9 contracts, overlays, and validators

This section identifies required domains, not a closed file list. Stage 0.0D must discover later active documents that govern the same domains.

## 4. Dynamic authority resolution

When rules conflict, apply the following order:

1. `FACT_DISCIPLINE.md` for facts, figures, quotations, evidence, and claim boundaries.
2. This governance index for document applicability, authority, and lifecycle.
3. A more specific active canonical contract over a general active canonical contract.
4. A registered mandatory override over the rule it explicitly overrides.
5. A current named-stage prompt for that stage’s permitted inputs, outputs, and state transition.
6. An applicable validator contract for machine-enforced schema and integrity requirements.
7. An open remediation record only for its explicitly identified legacy defect or bounded scope.
8. A migration document only for the migration explicitly activated in the current run.

A newer file does not automatically outrank an older one. Authority comes from active registration, scope, and explicit supersession.

Unresolved conflicts block the run.

## 5. Mandatory run entry sequence

Every ordinary run follows this order:

```text
0.0D  Document Universe Preflight
0.0C  Coverage Discovery & Completeness Scan
0.0   Run intake and authoritative expanded source universe
0.1   Stage A selector
0.2   Stage B evidence package and draft
0.3   Stage C fact-safe red team
0.2R / 0.3R revise loops when authorized
0.4   Canonical full baseline revalidation
0.5   Evidence and source-claim completeness
0.6   Content, terminology, density, and strategic-read-through polish
0.7   Publish-readiness QC
0.7C  Independent completeness and news-value review
0.8   Governed incremental operation and GitHub merge preparation
0.9   Main and production verification
1.0   Remediation when needed
1.1   Retrospective and canonical rule promotion
```

A named stage cannot be replaced by an ad hoc “deep dive,” “red team,” or memory-based pass.

## 6. Required document-universe proof

The Stage 0.0D artifact must record:

- repository head SHA;
- canonical full blob SHA or explicit reason it is not yet required;
- every discovered governed document path;
- file SHA;
- governance class;
- authority level;
- applicable stages;
- read status;
- extracted rule IDs;
- supersession target;
- unresolved conflicts;
- open remediation applicability;
- migration activation status.

The run is blocked when any active governed document is unread, unregistered, stale, missing its SHA, or in unresolved conflict.

## 7. Prompt and validator registration

The canonical prompt package manifest must register:

- every named stage prompt;
- every active mandatory override or addendum;
- every active validator contract;
- every active permanent governance document;
- any open remediation that must be checked by ordinary runs.

A prompt assembler or upload package that omits a registered mandatory component is invalid.

Static counts in a manifest are informational only. Completeness is established by the current active registry and Stage 0.0D reconciliation.

## 8. Rule lifecycle

A recurring rule discovered during a retrospective must not remain indefinitely as an isolated patch.

Before the retrospective closes, the rule must be dispositioned as one of:

- incorporated into an existing canonical contract;
- established as a new canonical contract;
- registered as a temporary mandatory addendum with an owner and expiry condition;
- recorded as a bounded open remediation;
- rejected with a reason;
- superseded or archived.

For a recurring rule promoted to canonical status, the retrospective must also:

1. register it in this index or the canonical manifest;
2. identify its authority and applicable stages;
3. update the relevant named prompts;
4. add or update a validator where the rule is machine-testable;
5. mark the displaced patch as `SUPERSEDED`;
6. verify that the next Stage 0.0D run discovers it automatically.

## 9. Migration isolation

Migration documents belong under `docs/migrations/`.

A migration document:

- may contain dates, counts, branch names, run IDs, or one-time transition details;
- must declare `ACTIVE_MIGRATION` or `COMPLETED_REFERENCE`;
- is not part of the default ordinary-run contract;
- must name its activation condition and completion condition;
- must be excluded from subsequent ordinary runs after completion.

Permanent documents must not embed one-time migration facts.

## 10. Completion standard

A governed run may claim that the rule universe was reviewed only when:

- Stage 0.0D passed;
- all active documents were read;
- all conflicts were resolved;
- all required stage prompts and validators were registered;
- migrations were either explicitly activated or explicitly excluded;
- the exact repository state was recorded.

“Read the core documents” is not a valid substitute for this proof.
