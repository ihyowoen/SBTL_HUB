# Document Universe Policy

**Status:** `ACTIVE_CANONICAL`  
**Stage:** `0.0D`  
**Version:** `DOCUMENT_UNIVERSE_PREFLIGHT_V2`

## 0. Purpose

Stage 0.0D prevents a run from applying only a remembered or fixed subset of SBTL_HUB rules.

Its purpose is to discover the complete governed document universe from the current GitHub `main`, read every document under `docs/**` in full, classify applicability after reading, resolve authority conflicts, and produce a reproducible manifest before editorial work begins.

## 1. Scope

The inventory scope includes:

- `docs/**`;
- `docs/llm_prompts/v1/**`;
- validator scripts and registries explicitly referenced by active documents or manifests;
- GitHub workflows that enforce card, prompt, document, or production contracts;
- open remediation manifests;
- migration documents, including inactive and completed migrations, to determine status, conflicts, and applicability.

The inventory must not be limited to files named in a remembered list.

## 2. Classification

Each discovered governed file must receive one class:

| Class | Meaning | Full text required? | Applies automatically? |
|---|---|---:|---:|
| `ACTIVE_CANONICAL` | permanent authoritative rule | Yes | Yes |
| `ACTIVE_MANDATORY_ADDENDUM` | temporary but mandatory active overlay | Yes | Yes |
| `ACTIVE_VALIDATOR_CONTRACT` | active machine-enforced contract or registry | Yes | Yes |
| `OPEN_REMEDIATION` | unresolved bounded legacy defect | Yes | Yes, within applicable scope only |
| `ACTIVE_MIGRATION` | explicitly activated one-time transition | Yes | Only when activated |
| `COMPLETED_REFERENCE` | completed migration retained only as historical/audit reference | Yes | No |
| `REFERENCE_ONLY` | explanatory or historical context | Yes | No |
| `SUPERSEDED` | replaced by a named active document | Yes | No |
| `ARCHIVED` | historical, non-operative | Yes | No |

A file without a classification is not silently ignored. It enters `UNCLASSIFIED_REVIEW_REQUIRED` and blocks progression until dispositioned.

## 3. Full-read rule

A valid full read requires more than opening a filename.

Every text or structured-data file under `docs/**` must be read or parsed in full before classification is finalized. Archived, superseded, reference, completed migration, and inactive migration documents are read to detect hidden patches, stale authority, contradictory language, and missing supersession links, but their rules are not applied unless their classification authorizes application.

Reading and applying are separate decisions:

- full read or parse is mandatory for every file under `docs/**`;
- classification is finalized only after the full read or parse;
- activation controls whether a migration is applied, never whether it is read;
- non-operative documents remain available for conflict detection and audit but do not govern ordinary runs.

For each document, the Stage 0.0D artifact must record:

- path;
- Git blob SHA or content SHA-256;
- classification;
- authority;
- applicable stages;
- extracted mandatory rule IDs;
- required output fields or validators;
- superseded documents;
- read status `READ_COMPLETE` or equivalent complete structured parse;
- application status;
- reader notes on conflicts or dependencies.

Reading only headers, snippets, search matches, summaries, old chat memory, or a prior run’s manifest is insufficient.

## 4. Discovery procedure

### 4.1 Repository-state lock

Record:

- repository;
- branch;
- head commit SHA;
- prompt-package manifest SHA;
- canonical full blob SHA when relevant.

All later document reads must come from that same repository state. A head change invalidates the manifest unless the changed files are proved irrelevant and the manifest is regenerated.

### 4.2 Inventory

Enumerate the full scope and collect:

- path;
- file type;
- directory;
- last-known registration source;
- apparent lifecycle markers;
- manifest references;
- validator references;
- replacement or archive references.

### 4.3 Full read and classification

Read or parse every inventoried `docs/**` file in full. Only after that full read may Stage 0.0D classify the document using explicit evidence from:

- `RUN_GOVERNANCE_INDEX.md`;
- canonical prompt manifests;
- override manifests;
- the document’s own status header;
- explicit supersession language;
- remediation status;
- migration activation in the current run intake.

File age alone is not authority evidence. An apparent lifecycle label is not permission to skip the full read.

### 4.4 Dependency expansion

When an active document references another rule, registry, schema, prompt, validator, or remediation, add that target to the inventory and repeat until no unresolved dependency remains.

### 4.5 Conflict resolution

For each conflicting pair, record:

- rule IDs;
- paths;
- scopes;
- authority basis;
- winning rule;
- losing rule disposition;
- whether canonical cleanup is required.

Any unresolved conflict produces `BLOCKED_DOCUMENT_AUTHORITY_CONFLICT`.

### 4.6 Defect preservation

Every non-conflict hard blocker must be represented both in its dedicated category field and exactly once in the normalized `incomplete_universe_defects[]` ledger.

The normalized ledger uses these defect types:

- `REPOSITORY_HEAD_CHANGED`;
- `MISSING_COMPONENT`;
- `STALE_COMPONENT`;
- `MISSING_CONTENT_IDENTITY`;
- `UNREAD_DOCUMENT`;
- `UNCLASSIFIED_DOCUMENT`;
- `MISSING_DEPENDENCY`;
- `MISAPPLIED_NON_AUTHORITATIVE_DOCUMENT`;
- `UNCHECKED_OPEN_REMEDIATION`;
- `UNAUTHORIZED_MIGRATION_APPLICATION`;
- `INACTIVE_DOCUMENT_CONTAMINATION`.

Authority conflicts remain exclusively in `unresolved_rule_conflicts[]`. Selecting one top-level blocker must never erase secondary defects.

## 5. Required output

```json
{
  "stage": "0.0D",
  "status": "PASS|BLOCKED_DOCUMENT_UNIVERSE_INCOMPLETE|BLOCKED_DOCUMENT_AUTHORITY_CONFLICT",
  "document_universe_status": "PASS|FAIL",
  "repository_head_sha": "",
  "canonical_full_blob_sha": "",
  "documents": [
    {
      "path": "",
      "sha256": "",
      "git_blob_sha": "",
      "classification": "ACTIVE_CANONICAL",
      "authority_level": 0,
      "applicable_stages": [],
      "read_status": "READ_COMPLETE",
      "application_status": "APPLIED|NOT_APPLIED|APPLIED_WITHIN_SCOPE",
      "rule_ids": [],
      "dependencies": [],
      "supersedes": [],
      "superseded_by": null
    }
  ],
  "repository_state_defects": [],
  "missing_or_stale_components": [],
  "missing_content_identity_documents": [],
  "unclassified_documents": [],
  "unread_documents": [],
  "unread_active_documents": [],
  "unresolved_dependencies": [],
  "unresolved_rule_conflicts": [],
  "misapplied_non_authoritative_documents": [],
  "unchecked_open_remediations": [],
  "unauthorized_migration_applications": [],
  "inactive_document_contamination": [],
  "incomplete_universe_defects": [
    {
      "type": "REPOSITORY_HEAD_CHANGED|MISSING_COMPONENT|STALE_COMPONENT|MISSING_CONTENT_IDENTITY|UNREAD_DOCUMENT|UNCLASSIFIED_DOCUMENT|MISSING_DEPENDENCY|MISAPPLIED_NON_AUTHORITATIVE_DOCUMENT|UNCHECKED_OPEN_REMEDIATION|UNAUTHORIZED_MIGRATION_APPLICATION|INACTIVE_DOCUMENT_CONTAMINATION",
      "path": "",
      "detail": ""
    }
  ],
  "open_remediations_checked": [],
  "active_migrations": [],
  "inactive_migrations_read": [],
  "completed_references_read": [],
  "reference_only_documents_read": [],
  "superseded_documents_read": [],
  "archived_documents_read": [],
  "excluded_migrations": [],
  "blocker_precedence": [
    "BLOCKED_DOCUMENT_AUTHORITY_CONFLICT",
    "BLOCKED_DOCUMENT_UNIVERSE_INCOMPLETE"
  ],
  "selected_blocker_reason": "",
  "all_docs_files_read_or_parsed": true,
  "stage_0_0c_authorized": true
}
```

## 6. Hard blockers

Stage 0.0C and all later stages are blocked when any of the following is true:

- any text or structured-data file under `docs/**` was not read or parsed in full before classification was finalized;
- any governed document lacks a SHA or equivalent content identity;
- `all_docs_files_read_or_parsed != true`;
- `unread_documents[]` is non-empty;
- the repository head changed after manifest creation;
- an active addendum or validator is absent from the package;
- a referenced dependency is missing;
- an unclassified governed file remains;
- a superseded, archived, reference-only, completed-migration, or inactive-migration document was applied as authority;
- an active rule conflict is unresolved;
- an open remediation applicable to the current data was not checked;
- a migration was applied without explicit activation;
- a migration or other inactive document contaminated a permanent rule decision.

### Blocker precedence

The single `status` field must be selected in this order:

1. When `unresolved_rule_conflicts[]` is non-empty, use `BLOCKED_DOCUMENT_AUTHORITY_CONFLICT` even if other defects coexist.
2. Otherwise, when `incomplete_universe_defects[]` is non-empty or any other incomplete-universe condition exists, use `BLOCKED_DOCUMENT_UNIVERSE_INCOMPLETE`.
3. Only when both ledgers are empty and all completeness conditions pass may status be `PASS`.

All secondary defects remain in their dedicated fields and normalized ledger regardless of the selected top-level status.

## 7. First adoption and subsequent runs

### First adoption

The first governed run after adoption must:

- inventory the complete scope;
- create the initial classification registry;
- identify duplicate prompt roots and stale references;
- reconcile all active addenda and validators;
- identify open remediation;
- establish explicit supersession links.

### Subsequent runs

Every subsequent run must still enumerate the full scope, but may optimize review by:

- fully rereading or parsing every file under `docs/**`;
- highlighting documents changed since the previous manifest;
- comparing SHAs and dependencies;
- verifying archived and superseded status without treating them as authority;
- detecting new files automatically.

A previous manifest is evidence of history, not permission to skip the current preflight.

## 8. Relationship to Stage 0.0C

Stage 0.0D decides which rules apply.

Stage 0.0C applies those rules to discover the complete current news universe.

Stage 0.0D must not perform candidate selection or news discovery. Stage 0.0C must not redefine document authority.

## 9. Migration isolation

Migration documents are always inventoried and fully read or parsed. They are ordinarily not applied.

They affect a run only when the run intake explicitly records:

- migration path;
- activation authority;
- bounded scope;
- start condition;
- completion condition;
- required audit artifacts.

Once completed, the migration becomes `COMPLETED_REFERENCE`; it remains readable for audit and conflict detection but must not influence later ordinary runs.

## 10. Assertion discipline

The assistant may state that “all applicable documents were read” only when the Stage 0.0D manifest proves:

- full scope enumeration;
- full reads or complete parsing for every file under `docs/**`;
- `all_docs_files_read_or_parsed=true`;
- no unread governed files;
- no unclassified governed files;
- no unresolved dependency;
- no unresolved conflict;
- `incomplete_universe_defects=[]`.

If any assertion prerequisite is missing, set `document_universe_status=FAIL` and select the permitted top-level blocker using Section 6: `BLOCKED_DOCUMENT_AUTHORITY_CONFLICT` when `unresolved_rule_conflicts[]` is non-empty; otherwise `BLOCKED_DOCUMENT_UNIVERSE_INCOMPLETE`.
