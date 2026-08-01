# Card Incremental Run Contract

**Status:** `ACTIVE_CANONICAL`  
**Version:** `CARD_INCREMENTAL_RUN_V1`

## 0. Purpose

This contract governs how a completed editorial run changes the canonical SBTL_HUB card inventory.

An incremental run is not limited to adding new cards. It may add new events, reinforce or correct existing cards, and add verified event-lineage relations while preserving the canonical full as the sole source of truth.

## 1. Canonical files

```text
data/cards.full.json      canonical full inventory
public/data/cards.json    generated lean application projection
```

Rules:

- only `data/cards.full.json` is canonical;
- `public/data/cards.json` must be reproducibly generated from the full;
- a run must not use a downloaded replacement file or stale branch copy as the baseline;
- every run records the current main commit SHA and canonical full blob SHA.

## 2. Ordinary operation types

An ordinary governed run may declare:

- `insert`;
- `update`;
- `related_add`.

An ordinary run must not perform:

- card deletion;
- `related_remove`;
- silent replacement of an existing card;
- undeclared modification of an existing card;
- automatic cleanup of legacy dangling relations.

Deletion and relation removal require a separate remediation contract, item-specific evidence, explicit approval, a declared diff, and an independently reviewed PR.

## 3. Operation meanings

### 3.1 `insert`

Use for:

- a distinct new event;
- a material follow-up;
- a new execution-stage transition;
- a material correction or reversal that is independently newsworthy.

An insert requires a new production ID and full schema.

### 3.2 `update`

Use for the same represented event when new evidence:

- corrects a factual error;
- confirms or refines an amount, capacity, timing, counterparty, or condition;
- adds a durable official or independent source;
- improves claim coverage;
- strengthens strategic context without creating a separate event.

An update must declare every changed field and preserve all undeclared fields.

### 3.3 `related_add`

Use only for a verified direct event lineage under `RELATED_LIFECYCLE_CONTRACT.md`.

A related addition must declare:

- source card ID;
- target card ID;
- relation type;
- evidence;
- lineage reason;
- event-stage relationship;
- whether the link is reciprocal or directional.

Shared topic, actor, chemistry, geography, or keyword is insufficient.

## 4. Update versus follow-up

Use an update when the same event is being corrected or completed.

Use `insert + related_add` when a separate material stage occurs, including:

```text
plan → contract
contract → financing close
financing → FID
FID → construction
construction → commissioning
commissioning → commercial operation
operation → expansion or measured result
active project → delay, suspension, reduction, or cancellation
proposal → enactment, final rule, implementation, or enforcement
```

A newer article about the same facts is reinforcement, not a follow-up.

## 5. Required run artifact

```json
{
  "schema": "card_run_v1",
  "run_id": "",
  "base_main_commit_sha": "",
  "base_full_blob_sha": "",
  "expected_before": 0,
  "operations": {
    "insert": [],
    "update": [],
    "related_add": []
  },
  "expected_after": 0,
  "audit_refs": [],
  "document_universe_manifest_ref": "",
  "coverage_discovery_ref": "",
  "independent_completeness_ref": ""
}
```

Each operation must include its governing stage artifacts and source/evidence references.

## 6. Baseline lock

Before applying operations:

1. fetch current `main`;
2. verify `base_main_commit_sha`;
3. verify `base_full_blob_sha`;
4. verify `expected_before`;
5. stop if any value differs.

Blocked status:

```text
BLOCKED_BASELINE_MOVED_REBASE_REQUIRED
```

The run must be rebased and all duplicate, follow-up, update, and related decisions rerun against the new full.

## 7. Declared-diff contract

The apply process must prove:

- all inserted IDs are new;
- every update targets an existing ID;
- every changed existing field was declared;
- no existing card disappeared;
- no existing related edge disappeared;
- every related addition resolves;
- no new dangling relation exists;
- no self-link or duplicate link exists;
- counts reconcile;
- the resulting full regenerates the lean projection exactly.

Any undeclared change blocks merge.

## 8. Existing relation preservation

Ordinary runs obey:

```text
existing related edges   preserve
verified new relation    related_add
missing valid relation   related_add
relation removal         separate remediation only
card deletion            separate remediation only
```

Legacy dangling relations remain visible as open remediation until resolved through the separate audited process. They are not silently deleted or retargeted.

## 9. Run audit

Every run retains an independent audit containing:

- input universe;
- Stage 0.0D manifest;
- Stage 0.0C discovery ledger;
- Stage A/B/C and post-acceptance artifacts;
- inserted IDs;
- updated IDs and field-level diffs;
- related additions;
- zero deletion assertion for ordinary runs;
- count reconciliation;
- full and lean output hashes;
- production verification result.

The audit is not embedded as uncontrolled top-level fields in every card. Card-level durable provenance may reference the run audit.

## 10. One run, one governed operation

Default operation:

```text
one editorial run → one governed incremental run artifact
```

Multiple unmerged runs may be consolidated only as an exceptional recovery or transition procedure with explicit approval.

An exceptional consolidation must:

- preserve each original run’s inputs, decisions, and audit separately;
- re-evaluate cross-run duplicates;
- re-evaluate existing-card reinforcement;
- re-evaluate material follow-ups and event-stage transitions;
- re-evaluate related additions;
- use a bounded migration document;
- return to ordinary one-run operation after completion.

Consolidation is not the default workflow and must not be encoded as a permanent date-specific rule.

## 11. Apply order

```text
validate document universe
→ validate coverage and completeness artifacts
→ lock canonical baseline
→ validate operations
→ apply inserts
→ apply updates
→ apply related additions
→ validate declared diff
→ write canonical full
→ regenerate lean projection
→ run schema, lineage, evidence, and relation validators
→ verify main
→ verify production
```

The canonical full must be written and validated before the lean projection is published.

## 12. Production completion

A run is complete only when:

- the intended canonical full is on `main`;
- the lean projection matches the full;
- the application endpoint serves the expected count and IDs;
- inserted and updated cards render correctly;
- related links resolve;
- production verification is recorded.

`github_merge_ready` is not `production_verified`.
