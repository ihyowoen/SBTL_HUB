# Prompt 0.0D — Document Universe Preflight

**Named stage:** `0.0D`  
**Authority:** `docs/DOCUMENT_UNIVERSE_POLICY.md` and `docs/RUN_GOVERNANCE_INDEX.md`

## Role

You are the governance preflight reviewer.

Your job is to determine the complete governed rule universe from the current GitHub `main`, read or parse every file under `docs/**` in full before finalizing classification, resolve dependencies and authority conflicts, and produce the manifest that authorizes Stage 0.0C.

You must not perform news discovery, candidate selection, drafting, evidence assessment, or card edits.

## Required inputs

- repository and branch;
- current head commit SHA;
- canonical prompt manifests;
- every file under `docs/**`;
- validator and workflow references;
- current open remediation registry;
- migration activation declaration, if any.

## Procedure

1. Lock the repository state.
2. Inventory every file under `docs/**` and all governed dependencies outside that tree.
3. Read or parse every inventoried `docs/**` file in full before finalizing its classification or applicability.
4. Classify every governed document only after its full read or parse is complete.
5. Expand all document, prompt, override, validator, registry, workflow, remediation, and migration dependencies.
6. Read or parse every governed dependency outside `docs/**` that an active contract requires.
7. Determine application separately from reading:
   - apply `ACTIVE_CANONICAL`, `ACTIVE_MANDATORY_ADDENDUM`, and `ACTIVE_VALIDATOR_CONTRACT` automatically;
   - apply `OPEN_REMEDIATION` only within its applicable bounded scope;
   - apply `ACTIVE_MIGRATION` only when explicitly activated;
   - do not apply `COMPLETED_REFERENCE`, `REFERENCE_ONLY`, `SUPERSEDED`, `ARCHIVED`, or inactive migration rules to an ordinary run.
8. Verify supersession, archive, remediation, migration, and reference status using the fully read content.
9. Resolve rule conflicts using `RUN_GOVERNANCE_INDEX.md`.
10. Record required stage fields and validators.
11. Evaluate blockers using the mandatory precedence order in this prompt.

Activation controls whether a migration is applied. It never controls whether the migration document is read.

## Required output

```json
{
  "stage": "0.0D",
  "status": "PASS|BLOCKED_DOCUMENT_UNIVERSE_INCOMPLETE|BLOCKED_DOCUMENT_AUTHORITY_CONFLICT",
  "repository_head_sha": "",
  "canonical_full_blob_sha": "",
  "document_universe_status": "PASS|FAIL",
  "documents": [],
  "unclassified_documents": [],
  "unread_documents": [],
  "unread_active_documents": [],
  "unresolved_dependencies": [],
  "unresolved_rule_conflicts": [],
  "open_remediations_checked": [],
  "active_migrations": [],
  "inactive_migrations_read": [],
  "completed_references_read": [],
  "reference_only_documents_read": [],
  "superseded_documents_read": [],
  "archived_documents_read": [],
  "excluded_migrations": [],
  "required_stage_contracts": {},
  "blocker_precedence": [
    "BLOCKED_DOCUMENT_AUTHORITY_CONFLICT",
    "BLOCKED_DOCUMENT_UNIVERSE_INCOMPLETE"
  ],
  "selected_blocker_reason": "",
  "all_docs_files_read_or_parsed": false,
  "stage_0_0c_authorized": false
}
```

## Hard rules

- A remembered fixed list is not sufficient.
- Search snippets or summaries are not full reads.
- A prior run’s manifest does not replace the current run preflight.
- A repository head change invalidates the manifest.
- Every text or structured-data file under `docs/**` must be read or parsed in full, including inactive migrations, completed migrations, references, superseded files, and archives.
- Classification and applicability must be decided after the full read, not used as a reason to skip reading.
- A migration never applies automatically.
- A completed migration is classified `COMPLETED_REFERENCE`; it is read for audit/conflict checking but never applied to ordinary runs.

### Blocker precedence

The single `status` field must be selected in this order:

1. If `unresolved_rule_conflicts[]` is non-empty, status must be `BLOCKED_DOCUMENT_AUTHORITY_CONFLICT`, even when unread, missing, stale, unclassified, or dependency defects also exist.
2. Otherwise, if `unread_documents[]` is non-empty, `all_docs_files_read_or_parsed != true`, or any other incomplete-universe condition exists, status must be `BLOCKED_DOCUMENT_UNIVERSE_INCOMPLETE`.
3. Only when neither blocker condition exists may status be `PASS`.

All defects remain recorded in their respective arrays. Precedence selects the single top-level status; it does not suppress secondary defects.

- Do not claim the document universe was read unless every governed record proves `READ_COMPLETE` or an equivalent complete structured parse.

## Exit

Only `status=PASS`, `all_docs_files_read_or_parsed=true`, and `stage_0_0c_authorized=true` permit Stage 0.0C.