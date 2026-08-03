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

### 2A. Stage 0.7C governance-preflight consumer gate

Before any card may enter `pr_candidate_payload`, Prompt 0.8 must validate the Stage 0.7C artifact itself rather than trusting its top-level PASS label.

The artifact must contain all of the following from the same repository revision used by Stage 0.7C:

- `status: PASS_WITH_DECLARED_RESIDUAL_RISK`;
- `prompt_0_8_authorized: true`;
- `governing_contracts_same_revision: true`;
- `v3_contract_preflight_passed: true`;
- `governing_contracts_read[]` containing exactly these required original documents:
  - `docs/EDITORIAL_VALUE_AND_COMPLETENESS_STANDARD.md`;
  - `docs/STRUCTURAL_NEWS_VALUE_SELECTION.md`;
  - `docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md`;
  - `docs/RELATED_LIFECYCLE_CONTRACT.md`.

A summary, downstream excerpt, renamed substitute, missing path, duplicate path, mixed repository revision, false/absent preflight field, or internally inconsistent authorization is a hard consumer-side failure even when the Stage 0.7C artifact claims PASS. Stop before operation materialization and report:

```text
status: BLOCKED_STAGE_0_7C_GOVERNANCE_PREFLIGHT_INVALID
invalid_or_missing_stage_0_7c_fields: [...]
no pr_candidate_payload emitted
```

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
- a fixed eight-document read is complete governance proof;
- a conventional execution event is the sole valid strict-pass route for a format-risk card;
- a merge-prep lineage gate may omit the selected V3 anchor path, route-specific statuses, or non-applicable-route reason.

All compatible evidence, lineage, duplicate, schema, source-diversity, accounting, PR, and production-boundary safeguards remain in force.

## 5A. V3 anchor-path merge-prep gate

The subordinate legacy execution-only overlay is non-operative. Before any format-risk `publish_ready[]` card may enter `pr_candidate_payload`, Prompt 0.8 must verify the Final QC output preserves exactly one source-backed route:

1. `selected_anchor_path: execution` with `execution_anchor_qc_status: pass` and `structural_value_override_qc_status: not_applicable`; or
2. `selected_anchor_path: v3_non_execution` with `structural_value_override_qc_status: pass` and `execution_anchor_qc_status: not_applicable`.

Both routes require:

- `anchor_path_qc_passed: true`;
- a specific `non_applicable_anchor_path_reason`;
- exact current-run lineage from Stage A through Final QC;
- no route switch, status rewrite, or evidence laundering during merge preparation.

The execution route must retain its source-backed execution evidence.

For `selected_anchor_path: v3_non_execution`, Prompt 0.8 must verify and preserve the complete canonical package byte-for-byte from Final QC:

- `structural_value_override_applied: true`;
- `structural_value_override_reason`;
- non-empty valid `anchor_classes[]`;
- `incremental_information`;
- `decision_relevance`;
- `baseline_expectation_changed`;
- non-empty item-specific `evidence_needed_for_stage_b[]`;
- non-empty measurable `next_confirmation_points[]`;
- specific `why_execution_event_not_required`;
- `prior_state`;
- `new_verified_fact`;
- `changed_judgment`;
- applicable uncertainty / probability-change fields;
- applicable baseline-expectation / before-after fields;
- current-run source lineage supporting every package field.

Missing, renamed, summarized, reconstructed, generic, altered, unsupported, or internally inconsistent package data requires `BLOCKED_FINAL_QC_ANCHOR_PATH_INVALID`; it must not enter `pr_candidate_payload`. Absence of a conventional execution event is not itself a defect when the complete V3 non-execution route passed.

If metadata is missing, contradictory, stale, or unsupported, return:

```text
status: BLOCKED_FINAL_QC_ANCHOR_PATH_INVALID
merge_prep_hold_count: [...]
no PR candidate emitted for affected items
```

Add to Prompt 0.8 JSON:

```json
"lineage_merge_gate": {
  "final_qc_lineage_passed": true,
  "anchor_path_lineage_passed": true,
  "publish_ready_lineage_checked_count": 0,
  "execution_path_checked_count": 0,
  "v3_non_execution_path_checked_count": 0,
  "anchor_path_hold_count": 0,
  "github_ready_allowed": true
}
```

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
