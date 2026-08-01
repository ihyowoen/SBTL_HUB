# Prompt 0.8 Incremental Operation Addendum

**Status:** `ACTIVE_MANDATORY_ADDENDUM`  
**Applies to:** `10_PROMPT_0_8_GitHub_Merge_Prep.md`

## 1. Preconditions

Prompt 0.8 must not begin unless all are present and passing:

- Stage 0.0D document-universe manifest;
- Stage 0.0C coverage-discovery artifact;
- Prompt 0.7 publish-ready artifact;
- Stage 0.7C independent completeness artifact;
- current GitHub main commit SHA;
- current `data/cards.full.json` blob SHA;
- current canonical full count;
- declared incremental run artifact.

Missing or stale input blocks with:

```text
BLOCKED_INCREMENTAL_MERGE_PRECONDITION_MISSING
```

## 2. Canonical baseline

Prompt 0.8 uses:

```text
GitHub main → data/cards.full.json
```

as the only canonical full baseline.

`public/data/cards.json` is a generated lean projection and must not substitute for the full when preserving evidence, lineage, audit, or workflow metadata.

## 3. Allowed ordinary operations

```text
insert
update
related_add
```

Prompt 0.8 must reject ordinary-run payloads containing:

```text
delete
related_remove
```

unless the current task is a separately authorized remediation with its own contract and approval.

## 4. Declared-diff rules

Before writing any output, verify:

- every insert ID is absent from the full;
- every update target exists;
- every update declares its changed fields;
- every related addition has a direct lineage reason;
- no existing card disappears;
- no undeclared existing-card field changes;
- no existing related edge disappears;
- no new dangling, duplicate, or self-related edge appears;
- expected counts reconcile.

Hard blockers:

```text
BLOCKED_UNDECLARED_CARD_DIFF
BLOCKED_EXISTING_RELATED_EDGE_LOSS
BLOCKED_NEW_MISSING_RELATED_TARGETS
```

## 5. Baseline movement

If current main, full blob SHA, or count differs from the declared base:

```text
BLOCKED_BASELINE_MOVED_REBASE_REQUIRED
```

Rebase the run and repeat duplicate, follow-up, update, and related decisions against the new full. Do not force-apply a stale run.

## 6. Output order

```text
validate operations
→ apply insert
→ apply update
→ apply related_add
→ validate declared diff
→ write canonical full
→ regenerate public lean projection
→ validate full and projection
→ prepare GitHub change
```

The full must be preserved and verified before the lean projection is written.

## 7. Required output additions

```json
{
  "operation_schema": "card_run_v1",
  "base_main_commit_sha": "",
  "base_full_blob_sha": "",
  "expected_before": 0,
  "insert_count": 0,
  "update_count": 0,
  "related_add_count": 0,
  "delete_count": 0,
  "related_remove_count": 0,
  "existing_related_preserved": true,
  "undeclared_existing_card_change_count": 0,
  "expected_after": 0,
  "full_output_sha256": "",
  "lean_output_sha256": "",
  "github_merge_ready": false
}
```

`github_merge_ready` remains false until every Prompt 0.8 validator passes.
