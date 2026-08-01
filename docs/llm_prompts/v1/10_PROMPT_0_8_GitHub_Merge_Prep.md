# Prompt 0.8 — Canonical Incremental Merge Preparation

**Status:** `ACTIVE_CANONICAL`  
**Named stage:** `0.8`  
**Canonical baseline:** `data/cards.full.json`

## 0. Assembly contract

This file is the canonical entry point for Prompt 0.8.

Before execution, read together:

1. `docs/llm_prompts/v1/00_DYNAMIC_GOVERNANCE_COMPLETENESS_OVERRIDE_V1.md`;
2. `docs/llm_prompts/v1/10_PROMPT_0_8_INCREMENTAL_OPERATION_ADDENDUM_V1.md`;
3. `docs/llm_prompts/v1/legacy/10_PROMPT_0_8_GitHub_Merge_Prep_LEGACY_BODY.md` for compatible accumulated merge-prep, lineage, evidence, validation, and reporting rules.

The legacy body remains subordinate. Any conflicting public-baseline, public-inbox, reverse-export, replace-all-only, fixed-document, or fallback clause is superseded by this canonical entry point and the registered addendum.

## 1. Canonical baseline and outputs

Prompt 0.8 must use:

```text
GitHub main → data/cards.full.json
```

as the only merge input, source of truth, canonical count source, duplicate-screening baseline, and metadata-preservation baseline.

The outputs are:

```text
canonical output              = data/cards.full.json
application lean projection   = public/data/cards.json
```

`public/data/cards.json` is never a merge input, batch inbox, canonical count source, fallback source of truth, or metadata-preservation source. It is regenerated only from the validated updated canonical full.

If the canonical full cannot be read, parsed, counted, and verified against its Git blob SHA, stop with:

```text
BLOCKED_CANONICAL_FULL_UNREADABLE
```

If any assembled instruction, script, or workflow still treats `public/data/cards.json` as the merge baseline or as input to rebuild the canonical full, stop with:

```text
BLOCKED_PROMPT_0_8_PUBLIC_BASELINE_CONFLICT
```

## 2. Preconditions

Prompt 0.8 requires passing artifacts from:

```text
0.0D → 0.0C → Stage A/B/C → 0.4 → 0.5 → 0.6 → 0.7 → 0.7C
```

It also requires:

- current main commit SHA;
- current `data/cards.full.json` blob SHA and count;
- the verified canonical full content from that locked state;
- a declared incremental run artifact;
- exact current-run lineage and accounting;
- all registered validators and open-remediation checks required by Stage 0.0D.

## 3. Ordinary-run operations

Only the following operations are permitted:

```text
insert
update
related_add
```

Existing cards and existing related edges must be preserved unless a separately authorized remediation explicitly permits deletion or `related_remove`.

Manual, ad-hoc editing of the canonical full is prohibited. Prompt 0.8 may materialize a new canonical full only through the governed declared-operation apply path, with base-SHA locking and declared-diff validation.

## 4. Merge and export sequence

```text
lock current main and canonical full
→ validate declared operations
→ apply insert/update/related_add through the governed incremental apply path
→ validate declared diff, ID accounting, and related preservation
→ materialize the candidate data/cards.full.json
→ validate the candidate canonical full
→ run node scripts/lean_cards.mjs
→ verify public/data/cards.json is the exact KEEP projection of the full
→ prepare branch, commit, and PR only when authorized
```

Repository exporter contract:

- `scripts/lean_cards.mjs` reads `data/cards.full.json` and writes only `public/data/cards.json`;
- the exporter must never write or reconstruct `data/cards.full.json` from the public projection;
- `.github/workflows/lean-cards.yml` triggers on canonical-full, public-projection, exporter, or workflow changes and commits only the generated public projection;
- `node scripts/lean_cards.mjs --check` proves projection equality without writing;
- a direct public-only edit is overwritten by the canonical projection and cannot alter the full.

The earlier `docs/OPERATIONS.md` Section F public-inbox/reverse-merge procedure is non-operative for ordinary runs. Its prohibition on uncontrolled manual edits remains compatible; its direction of data ownership and exporter flow is superseded.

## 5. Legacy-body compatibility rule

The subordinate legacy body remains active only where compatible with this file, the dynamic-governance override, the incremental-operation addendum, `FACT_DISCIPLINE.md`, `RELATED_LIFECYCLE_CONTRACT.md`, `SOURCE_AUDIT_CONTRACT.md`, and the current canonical manifests.

The following legacy statements are expressly non-operative:

- `public/data/cards.json` is the current baseline;
- `public/data/cards.json` is the merge source of truth or batch inbox;
- the public projection may rebuild or replace the canonical full;
- the public projection may replace an unreadable canonical full;
- Prompt 0.8 writes only the public file;
- replace-all is the only permitted merge model;
- a fixed eight-document read is complete governance proof.

All compatible evidence, lineage, duplicate, schema, source-diversity, accounting, PR, and production-boundary safeguards remain in force.

## 6. Exit

Prompt 0.8 may emit `github_merge_ready=true` only after:

- canonical full baseline verification passes;
- all declared operations reconcile;
- no undeclared existing-card change exists;
- no existing related edge is lost;
- the canonical full passes validation;
- the public file is regenerated from that full and passes exact projection validation;
- the exporter and workflow preserve the full-to-lean direction;
- all blockers are empty.

Production verification remains a separate Prompt 0.9 stage.

<!-- WORKFLOW_CONTRACT_OVERLAY_20260723:BEGIN -->
Mandatory shared contracts for this stage:

- `docs/RELATED_LIFECYCLE_CONTRACT.md`
- `docs/SCHEMA_CONTRACT_STAGE_LINEAGE.md`
- `docs/SOURCE_AUDIT_CONTRACT.md`
- `validation_data/source_owner_registry.json` when source-owner counting is performed

The shared contracts supersede conflicting wording only for Related lifecycle, date-role/freshness,
source-audit metadata derivation, stage-exit artifact conformance, and production-verification proof.

Prompt 0.8 merge overlay:

- Resolve all `related_candidate_spec_ids` to final production IDs and record
  `related_id_resolution_ledger`.
- Fail on dangling, self, duplicate, unexplained, or unresolved Related links.
- Recompute source-audit metadata after every source URL change and run the repository Evidence QC.
- Run `related_lifecycle_check.py --require-contract --new-id-file <ID_LEDGER>` and
  `evidence_qc_v8_check.py --new-id-file <ID_LEDGER>` against the merged candidate/current merge-ID scope.
- Only Prompt 0.8 may emit `pr_candidate_payload` and the authoritative replace-all file.
<!-- WORKFLOW_CONTRACT_OVERLAY_20260723:END -->
