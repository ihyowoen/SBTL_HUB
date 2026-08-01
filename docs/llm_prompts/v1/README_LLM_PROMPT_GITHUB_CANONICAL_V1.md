# SBTL_HUB LLM Prompt Package — Dynamic Governance

**Stable package path:** `docs/llm_prompts/v1/`  
**Current internal version:** `LLM_PROMPT_GITHUB_CANONICAL_V2_DYNAMIC_GOVERNANCE_COMPLETENESS`

The directory name remains `v1` for repository-path stability. The active manifest version, not the directory name alone, defines the current governance contract.

## 1. Mandatory entry point

Every governed run begins with:

```text
Stage 0.0D — Document Universe Preflight
```

Stage 0.0D reads or parses every file under `docs/**` in full, classifies applicability, resolves conflicts, and records the exact repository state.

A fixed list of core documents is not a complete run contract.

## 2. Pipeline

```text
0.0D Document Universe Preflight
→ 0.0C Coverage Discovery & Completeness
→ 0.0 Run intake / expanded source universe lock
→ 0.1 Stage A
→ 0.2 Stage B
→ 0.3 Stage C
→ authorized revise loops
→ 0.4 Baseline Revalidation
→ 0.5 Evidence QC
→ 0.6 Content Polish
→ 0.7 Final QC
→ 0.7C Independent Completeness Review
→ 0.8 Incremental Merge Preparation
→ 0.9 Production Verification
→ 1.0 Remediation when needed
→ 1.1 Retrospective and Canonical Promotion
```

## 3. Package layout

- `docs/` — permanent governance, active contracts, remediation, validation records, and migration records.
- `docs/llm_prompts/v1/` — named prompts, mandatory overrides, addenda, manifests, and package registries.
- `validation_scripts/` — executable integrity validators referenced by active contracts.
- `docs/migrations/` — one-time transitions that never apply automatically to ordinary runs.

## 4. Permanent governance additions

- `docs/RUN_GOVERNANCE_INDEX.md`
- `docs/DOCUMENT_UNIVERSE_POLICY.md`
- `docs/EDITORIAL_VALUE_AND_COMPLETENESS_STANDARD.md`
- `docs/CARD_INCREMENTAL_RUN_CONTRACT.md`

These documents do not replace compatible fact, source, schema, related, or stage contracts. They close the governance, completeness, and incremental-operation gaps.

## 5. New named stages

- `00D_PROMPT_0_0D_DOCUMENT_UNIVERSE_PREFLIGHT.md`
- `00C_PROMPT_0_0C_COVERAGE_DISCOVERY.md`
- `09A_PROMPT_0_7C_INDEPENDENT_COMPLETENESS_REVIEW.md`

Stage A remains selector-only. External search for missing news and follow-ups belongs to Stage 0.0C.

## 6. Mandatory override families

Prompt assemblers and upload tooling must include both:

1. `DATE_STORYID_RELATED_INTEGRITY_V1`
2. `DYNAMIC_GOVERNANCE_COMPLETENESS_V1`

Required manifests:

- `DATE_STORYID_RELATED_INTEGRITY_OVERRIDE_MANIFEST.json`
- `DYNAMIC_GOVERNANCE_COMPLETENESS_OVERRIDE_MANIFEST.json`
- `LLM_PROMPT_GITHUB_CANONICAL_V1_MANIFEST.json`
- `UPLOAD_MANIFEST.json`
- `GOVERNANCE_LIFECYCLE_REGISTRY.json`

Omitting a mandatory override, stage addendum, active validator, or permanent governance document produces an incomplete package.

## 7. Canonical card data

```text
data/cards.full.json      canonical full inventory
public/data/cards.json    generated lean application projection
```

Ordinary runs declare:

- `insert`;
- `update`;
- `related_add`.

Ordinary runs do not delete cards or remove existing related edges. Those changes require separate remediation.

## 8. Editorial completeness and IB grade

Fact safety is necessary but not sufficient.

Each run must also review:

- missing must-report news;
- material follow-ups;
- event-stage transitions;
- existing-card reinforcement and correction;
- regional and topic coverage;
- exclusions and held candidates;
- decision usefulness and evidence-bounded strategic read-through.

The final completeness claim must come from the independent Stage 0.7C artifact and disclose residual risk.

## 9. Historical package records

The following files remain for traceability but are not current rule-universe authority:

- `LLM_PROMPT_GITHUB_CANONICAL_V1_FULL_PRESERVED_MANIFEST.json`
- `QC_REPORT_LLM_PROMPT_GITHUB_CANONICAL_V1.md`

Their lifecycle classification is recorded in `GOVERNANCE_LIFECYCLE_REGISTRY.json`.

## 10. Migration isolation

A file under `docs/migrations/` is read during Stage 0.0D but affects a run only when explicitly activated.

After completion it becomes `COMPLETED_REFERENCE` and does not apply to later ordinary runs.

## 11. Current source of truth

Use:

- `PROMPT_MANIFEST.md` for the human-readable package map;
- `LLM_PROMPT_GITHUB_CANONICAL_V1_MANIFEST.json` for the canonical machine-readable package;
- `UPLOAD_MANIFEST.json` for upload completeness;
- `RUN_GOVERNANCE_INDEX.md` and the Stage 0.0D artifact for run-time authority.
