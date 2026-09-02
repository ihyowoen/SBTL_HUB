# Prompt 0.0D — Active Governance Preflight V4

**Status:** `ACTIVE_CANONICAL`  
**Version:** `PROMPT_0_0D_V4_20260901`

## Purpose
Establish the complete active rule universe before discovery or selection. Inventory every document, but do not treat historical/reference content as active authority.

## Required input
- current GitHub `main` HEAD;
- current `data/cards.full.json` blob identity;
- current repository tree under `docs/**`;
- `RUN_GOVERNANCE_INDEX.md`;
- `DOCUMENT_UNIVERSE_POLICY.md`;
- `PROMPT_MANIFEST.md`;
- `docs/llm_prompts/v1/GOVERNANCE_LIFECYCLE_REGISTRY.json`;
- active validator/workflow registration.

## Procedure
1. Lock `main` SHA and the canonical `data/cards.full.json` blob SHA used by this run.
2. Inventory every `docs/**` path.
3. Classify every path from registry + authoritative header.
4. Derive the required active/dependency closure directly from the **current lifecycle registry**: `active_canonical + active_named_prompts`, `active_validator_contracts`, and `open_remediations + activation_required_migrations`.
5. Fully read/parse every path in that exact required closure. Do not allow the artifact to self-select a smaller active set.
6. Confirm `SUPERSEDED`, `REFERENCE_ONLY`, archived, and completed-migration files are non-operative.
7. Verify every active named prompt is a complete prompt and does not require a later override/addendum/overlay.
8. Verify Stage A declares `selection_policy_version = EMBEDDED_NEWS_VALUE_SELECTION_V4` and contains both news-value selection and Related pre-pass.
9. Verify the current manual-direct-add governance path is registered if available.
10. Detect missing dependencies, duplicate active authorities, unresolved conflicts, or unregistered active-looking files.

## Hard prohibitions
- Do not use remembered document lists as authority.
- Do not apply a historical override/addendum merely because it exists.
- Do not start 0.0C with unread active authority.
- Do not allow a later-read reference document to change an already-started run.
- Do not set compatibility fields to PASS by pretending every historical/reference body was deep-read. Their V4 meaning is defined below.
- Do not emit empty/self-selected `active_canonical_paths` or `active_validator_contract_paths`; they are registry-derived machine bindings.

## Production artifact compatibility semantics
The production card-run engine consumes several legacy-named fields. They remain mandatory compatibility fields, but their V4 semantics are applicability-driven:

- `repository_head_sha`: exact locked `main` commit SHA for the run.
- `canonical_full_blob_sha`: exact blob SHA of the locked `data/cards.full.json` baseline.
- `all_docs_files_read_or_parsed`: `true` only when every document that V4 requires to be fully read/parsed has been fully read/parsed and every other `docs/**` path has been lifecycle-classified. It does not mean that superseded/reference-only bodies were unnecessarily deep-read.
- `unresolved_rule_conflicts`: compatibility mirror of unresolved active-authority conflicts; it must be empty on PASS.
- `incomplete_universe_defects`: aggregate blocker ledger for any unclassified path, unread required active/dependency path, unresolved dependency, unregistered active-looking file, registry mismatch, or other incomplete-universe defect; it must be empty on PASS.
- `stage_0_0c_authorized`: `true` only when all V4 preflight exit conditions are satisfied.

These compatibility fields must agree with the detailed V4 ledgers below. Any contradiction is BLOCKED, never normalized to PASS.

## Machine reconciliation rules
The production gate validates the detailed conclusions rather than trusting the summary booleans:

- `docs_inventory_count`, `classified_count`, `active_full_read_count`, and `active_override_or_addendum_count` are non-negative integers.
- PASS requires `classified_count == docs_inventory_count`.
- `active_canonical_paths` must exactly equal the current registry's unique `active_canonical + active_named_prompts` set.
- `active_validator_contract_paths` must exactly equal the current registry's `active_validator_contracts` set.
- `applicable_remediation_or_migration` must exactly equal the current registry's unique `open_remediations + activation_required_migrations` set.
- `superseded_or_reference_paths` is a unique non-empty-path array used for classification/audit; it does not reduce the required active set.
- `active_full_read_count` must equal the size of the exact unique union of the three required sets above; a self-reported smaller closure is invalid.
- `unclassified_paths`, `unread_active_paths`, `unresolved_dependencies`, `unresolved_conflicts`, `unregistered_active_looking_paths`, `unresolved_rule_conflicts`, and `incomplete_universe_defects` are arrays and all are empty on PASS.
- `active_override_or_addendum_count == 0` and `stage_a_embedded_news_value_verified == true` on PASS.
- `repository_head_sha` and `canonical_full_blob_sha` must match the exact card-run baseline bindings.
- `all_docs_files_read_or_parsed == true` and `stage_0_0c_authorized == true` are accepted only when all detailed and registry-binding rules above also pass.

## Required output
```json
{
  "stage": "0.0D",
  "status": "PASS|BLOCKED",
  "repository_head_sha": "",
  "canonical_full_blob_sha": "",
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
  "all_docs_files_read_or_parsed": true,
  "unresolved_rule_conflicts": [],
  "incomplete_universe_defects": [],
  "stage_0_0c_authorized": true
}
```

PASS requires exact registry-set reconciliation, all detailed defect arrays and compatibility blocker arrays empty, `active_override_or_addendum_count = 0`, `classified_count = docs_inventory_count`, exact required active/dependency full-read count, `stage_a_embedded_news_value_verified = true`, `all_docs_files_read_or_parsed = true`, exact SHA bindings, and `stage_0_0c_authorized = true`.
