# Prompt 0.0D — Active Governance Preflight V4

**Status:** `ACTIVE_CANONICAL`  
**Version:** `PROMPT_0_0D_V4_20260829`

## Purpose
Establish the complete active rule universe before discovery or selection. Inventory every document, but do not treat historical/reference content as active authority.

## Required input
- current GitHub `main` HEAD;
- current repository tree under `docs/**`;
- `RUN_GOVERNANCE_INDEX.md`;
- `DOCUMENT_UNIVERSE_POLICY.md`;
- `PROMPT_MANIFEST.md`;
- lifecycle registry and active validator/workflow registration.

## Procedure
1. Lock `main` SHA.
2. Inventory every `docs/**` path.
3. Classify every path from registry + authoritative header.
4. Fully read/parse all active canonical documents, active validator contracts required by the intended run path, applicable open remediation/migration, and direct dependency closure.
5. Confirm `SUPERSEDED`, `REFERENCE_ONLY`, archived, and completed-migration files are non-operative.
6. Verify every active named prompt is a complete prompt and does not require a later override/addendum/overlay.
7. Verify Stage A declares `selection_policy_version = EMBEDDED_NEWS_VALUE_SELECTION_V4` and contains both news-value selection and Related pre-pass.
8. Verify the current manual-direct-add governance path is registered if available.
9. Detect missing dependencies, duplicate active authorities, unresolved conflicts, or unregistered active-looking files.

## Hard prohibitions
- Do not use remembered document lists as authority.
- Do not apply a historical override/addendum merely because it exists.
- Do not start 0.0C with unread active authority.
- Do not allow a later-read reference document to change an already-started run.

## Required output
```json
{
  "stage": "0.0D",
  "status": "PASS|BLOCKED",
  "baseline_main_sha": "",
  "docs_inventory_count": 0,
  "classified_count": 0,
  "active_full_read_count": 0,
  "active_canonical_paths": [],
  "active_validator_contract_paths": [],
  "applicable_remediation_or_migration": [],
  "superseded_or_reference_paths": [],
  "unclassified_paths": [],
  "unread_active_paths": [],
  "unresolved_dependencies": [],
  "unresolved_conflicts": [],
  "unregistered_active_looking_paths": [],
  "active_override_or_addendum_count": 0,
  "stage_a_embedded_news_value_verified": true,
  "stage_0_0c_authorized": true
}
```
PASS requires all defect arrays empty and `active_override_or_addendum_count = 0`.