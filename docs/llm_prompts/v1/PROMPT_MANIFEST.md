# SBTL LLM Editorial Prompt Package — Dynamic Governance Manifest

**Canonical source:** GitHub `main`  
**Governance mode:** `DYNAMIC_RUN_GOVERNANCE_V1`

## 0. Core rule

This package is not complete merely because a fixed list of files was uploaded.

Every run must begin with Stage 0.0D, read or parse every file under `docs/**`, classify applicability, reconcile the current active rule universe, and prove that all active canonical documents, mandatory overrides, validator contracts, and applicable open remediations came from the same repository state.

Static counts below are package inventory aids. Stage 0.0D is the authority for run-time completeness.

## 1. Pipeline

```text
0.0D Document Universe Preflight
→ 0.0C Coverage Discovery & Completeness
→ 0.0 Run intake / expanded source universe lock
→ 0.1 Stage A
→ 0.2 Stage B
→ 0.3 Stage C
→ authorized 0.2R / 0.3R
→ 0.4 Baseline Revalidation
→ 0.5 Evidence QC
→ 0.6 Content Polish
→ 0.7 Final QC
→ 0.7C Independent Completeness Review
→ 0.8 Incremental Merge Preparation
→ 0.9 Production Verification
→ 1.0 Remediation when needed
→ 1.1 Retrospective / Canonical Promotion
```

## 2. Named stage prompts (17)

| Stage | File | Role |
|---|---|---|
| 0.0D | `00D_PROMPT_0_0D_DOCUMENT_UNIVERSE_PREFLIGHT.md` | complete docs-universe read, classification, and authority proof |
| 0.0C | `00C_PROMPT_0_0C_COVERAGE_DISCOVERY.md` | missing-news, follow-up, correction, and reinforcement discovery |
| 0.1 | `01_PROMPT_0_1_Stage_A.md` | selector-only review of the expanded source universe |
| 0.2 | `02_PROMPT_0_2_Stage_B_r0.md` | evidence package and card draft |
| 0.3 | `03_PROMPT_0_3_Stage_C_r0.md` | fact-safe red-team validation |
| 0.2R | `04_PROMPT_0_2R_Stage_B_Revise.md` | controlled rewrite |
| 0.3R | `05_PROMPT_0_3R_Stage_C_Revise.md` | controlled revalidation |
| 0.4 | `06_PROMPT_0_4_Baseline_Revalidation.md` | current canonical full revalidation |
| 0.5 | `07_PROMPT_0_5_Evidence_QC.md` | evidence and source-claim completeness |
| 0.6 | `08_PROMPT_0_6_Content_Polish.md` | density, terminology, and strategic read-through |
| 0.7 | `09_PROMPT_0_7_Final_QC.md` | publish-readiness QC |
| 0.7C | `09A_PROMPT_0_7C_INDEPENDENT_COMPLETENESS_REVIEW.md` | independent completeness and news-value challenge |
| 0.8 | `10_PROMPT_0_8_GitHub_Merge_Prep.md` | governed incremental operation and merge prep |
| 0.9 | `11_PROMPT_0_9_Production_Verification.md` | main and production verification |
| 1.0 | `12_PROMPT_1_0_Remediation.md` | bounded remediation |
| 1.1 | `13_PROMPT_1_1_Retrospective.md` | retrospective and recurring-rule canonical promotion |
| 0.1P | `14_PROMPT_0_1P_Review_Pool_Promotion.md` | explicitly authorized review-pool promotion |

## 3. Permanent governance documents (15)

- `docs/FACT_DISCIPLINE.md`
- `docs/RUN_GOVERNANCE_INDEX.md`
- `docs/DOCUMENT_UNIVERSE_POLICY.md`
- `docs/EDITORIAL_VALUE_AND_COMPLETENESS_STANDARD.md`
- `docs/CARD_INCREMENTAL_RUN_CONTRACT.md`
- `docs/PROMPT_ABC_DEFAULT_MODE.md`
- `docs/PROMPT_ABC_SUPPORTING_RULES.md`
- `docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md`
- `docs/CARD_ID_STANDARD.md`
- `docs/SCHEMA_CONTRACT_STAGE_LINEAGE.md`
- `docs/RELATED_LIFECYCLE_CONTRACT.md`
- `docs/SOURCE_AUDIT_CONTRACT.md`
- `docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md`
- `docs/WORKFLOW.md`
- `docs/OPERATIONS.md`

The list is a registered permanent baseline, not a closed universe. Stage 0.0D must read every `docs/**` file and discover later active documents and dependencies.

## 4. Mandatory override families

### 4.1 Date, story-ID, and related integrity

- `00_DATE_STORYID_RELATED_INTEGRITY_OVERRIDE_V1.md`
- `DATE_STORYID_RELATED_INTEGRITY_OVERRIDE_MANIFEST.json`
- registered stage hardening addenda
- registered date, story-ID, and related validators

### 4.2 Dynamic governance and editorial completeness

- `00_DYNAMIC_GOVERNANCE_COMPLETENESS_OVERRIDE_V1.md`
- `DYNAMIC_GOVERNANCE_COMPLETENESS_OVERRIDE_MANIFEST.json`
- Stage 0.0D, 0.0C, and 0.7C prompts
- permanent governance documents added by that manifest

### 4.3 Dynamic stage addenda

- `01_PROMPT_0_1_DYNAMIC_SOURCE_UNIVERSE_ADDENDUM_V1.md`
- `10_PROMPT_0_8_INCREMENTAL_OPERATION_ADDENDUM_V1.md`
- `13_PROMPT_1_1_CANONICAL_PROMOTION_ADDENDUM_V1.md`

These addenda close the exact execution gaps in the legacy Stage A, Prompt 0.8, and Prompt 1.1 bodies without deleting compatible accumulated rules.

Omission of either mandatory override family or any registered stage addendum invalidates prompt assembly and upload.

## 5. Lifecycle registry

`GOVERNANCE_LIFECYCLE_REGISTRY.json` is the seed registry for package-artifact lifecycle.

It identifies active package guides and classifies historical assembly manifests and QC reports as reference-only. It is not a substitute for Stage 0.0D’s full repository read and classification.

## 6. Active contract families

- fact and assertion discipline;
- source identity, owner independence, discovery, and synthesis;
- full schema and stage lineage;
- date-role, story-ID, and related lifecycle integrity;
- review-pool and treasure rescue;
- document-universe completeness;
- editorial value, IB-grade, and independent completeness;
- canonical full and declared incremental operations;
- main and production verification.

## 7. Open remediation

Open remediation is not silently normalized or deleted.

Applicable remediation manifests must be discovered by Stage 0.0D and carried into the governed run. A remediation affects only its bounded legacy scope.

## 8. Migration isolation

Files under `docs/migrations/` are not ordinary-run rules.

They apply only when explicitly activated in the current run intake and must become `COMPLETED_REFERENCE` after their bounded transition is finished.

Exact dates, run names, counts, or one-time branch details belong only in migration records and their audits.

## 9. Canonical baseline

```text
GitHub main → data/cards.full.json
```

`public/data/cards.json` is the application lean projection and is not the canonical full baseline.

## 10. Ordinary run operations

```text
insert
update
related_add
```

Existing related edges are preserved.

Card deletion and `related_remove` require separate remediation and explicit approval.

## 11. Package validity

The package is invalid when:

- Stage 0.0D is missing;
- a `docs/**` file was not read or parsed in full;
- a mandatory active component is omitted;
- a superseded document is applied as authority;
- an active dependency or validator is missing;
- the supplied input is treated as the complete news universe without Stage 0.0C;
- Stage A ignores the expanded source universe;
- Prompt 0.8 is authorized without Stage 0.7C;
- Prompt 0.8 applies undeclared changes or loses existing related edges;
- Prompt 1.1 leaves a recurring rule as an unregistered patch;
- a migration is applied as a permanent rule;
- the baseline is not locked to the current canonical full.
