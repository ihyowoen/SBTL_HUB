# Dynamic Governance and Editorial Completeness — Validation Record

**Status:** `PASS_GOVERNANCE_AND_FULL_TO_LEAN_RUNTIME_WITH_INCREMENTAL_ENGINE_PENDING`  
**Branch:** `agent/dynamic-governance-completeness`  
**Base main commit:** `27385027c94f83e060cbee2af964f6f45edd67f5`  
**Validated PR:** `#231`  
**Validated head:** `8a7c7a41fe0335df8306e0616e30daae508e7e77`

## 1. Validated scope

This record validates:

- permanent governance and one-time migration separation;
- full `docs/**` document-universe preflight requirements;
- coverage discovery and independent completeness review contracts;
- canonical full ownership and Stage A baseline requirements;
- Prompt 0.8 canonical-full merge preparation contract;
- full-to-lean exporter implementation;
- lean-cards workflow direction and write boundaries;
- existing repository validators, workflow-contract tests, and prompt-overlay checks;
- all Codex findings addressed through the validated head.

This record does not claim completion of:

- the general incremental apply engine for `insert`, `update`, and `related_add`;
- executable Stage 0.0D manifest generation;
- executable coverage-completeness validation;
- the first governed migration execution;
- production verification after a future card-data merge.

## 2. Canonical data contract

The validated ownership model is:

```text
data/cards.full.json      sole canonical inventory and full metadata source
public/data/cards.json    generated lean application projection only
```

The following are enforced by the contract and runtime implementation:

- Stage A screens duplicates, reinforcement, follow-ups, corrections, and relations against the verified current GitHub `main` full content;
- an uploaded or local copy is usable only when byte-equivalent to the locked canonical full blob;
- Prompt 0.8 uses the canonical full as merge input, count source, metadata-preservation source, and canonical output;
- the public projection is not a baseline, batch inbox, fallback, or source for rebuilding the full;
- `scripts/lean_cards.mjs` reads the full and writes only the public projection;
- `.github/workflows/lean-cards.yml` commits only the generated public projection;
- public-only edits are overwritten by the canonical projection;
- the exporter fails if the canonical full is absent or invalid.

## 3. Runtime changes

This PR is no longer documentation-only. It intentionally changes:

```text
scripts/lean_cards.mjs
.github/workflows/lean-cards.yml
```

### Exporter behavior

Default execution:

```text
node scripts/lean_cards.mjs
```

performs:

```text
read data/cards.full.json
→ project KEEP fields in canonical order
→ preserve canonical top-level metadata
→ write public/data/cards.json only
→ verify the written projection
```

Check mode:

```text
node scripts/lean_cards.mjs --check
```

verifies:

- top-level metadata equality;
- card-count equality;
- card-order equality;
- ID equality by position;
- KEEP-field presence and value equality;
- absence of non-KEEP fields in the public projection.

The exporter contains no ordinary public-to-full ingestion path and does not write the canonical full.

### Workflow behavior

The lean-cards workflow now triggers on changes to:

- `data/cards.full.json`;
- `public/data/cards.json`;
- `scripts/lean_cards.mjs`;
- `.github/workflows/lean-cards.yml`.

It regenerates the public projection, validates tracker/public/full/projection consistency, and commits only `public/data/cards.json` when generation changes it.

## 4. Document-universe closure

Stage 0.0D now requires:

- full enumeration of `docs/**`;
- full reading or complete parsing before classification;
- reading inactive migrations, completed references, reference-only, superseded, and archived files;
- lifecycle classification using the complete nine-class model;
- lifecycle-registry self-classification as `ACTIVE_VALIDATOR_CONTRACT`;
- conflict-specific blocker precedence;
- preservation of every secondary incomplete-universe defect in typed ledgers;
- no Stage 0.0C authorization unless all required read, identity, dependency, classification, and conflict gates pass.

## 5. Editorial completeness closure

The permanent workflow now requires:

```text
0.0D Document Universe Preflight
→ 0.0C Coverage Discovery
→ Stage A/B/C
→ post-acceptance quality stages
→ 0.7C independent completeness and news-value review
→ 0.8 canonical incremental merge preparation
→ 0.9 production verification
```

The review surface includes:

- missing must-report news outside the supplied input;
- follow-ups to existing full cards;
- execution-stage transitions;
- corrections, reversals, delays, reductions, suspensions, and cancellations;
- existing-card reinforcement;
- regional and topic coverage;
- exclusion and hold rescue review;
- evidence quality, execution maturity, claim completeness, materiality, incremental information, and decision usefulness.

Stage 0.0C findings remain candidate leads and must pass Stage A/B/C. Discovery search does not become evidence automatically.

## 6. Incremental operation contract

Ordinary run operations remain:

```text
insert
update
related_add
```

Ordinary runs prohibit:

```text
delete
related_remove
public_to_full_ingest
undeclared existing-card changes
silent related-edge loss
```

The canonical full may be materialized only through a governed declared-operation path with:

- main commit and full blob lock;
- count reconciliation;
- declared field-level diffs;
- ID and duplicate validation;
- related preservation and target resolution;
- full validation before public projection generation.

The generic executable incremental apply engine remains a required follow-up implementation.

## 7. Review findings addressed

Codex findings accepted and addressed include:

- public projection incorrectly allowed as Prompt 0.8 baseline;
- missing `COMPLETED_REFERENCE` lifecycle class;
- missing authority-conflict blocker;
- inactive documents not guaranteed to be read;
- ambiguous blocker precedence;
- unregistered missing-related-target blocker;
- incomplete secondary-defect fields;
- out-of-contract unverifiable-universe status;
- lifecycle registry lacking an allowed self-classification;
- document record classification template limited to one lifecycle class;
- active reverse-direction public-to-full exporter conflict;
- Stage A allowing stale uploaded or local baselines.

Each review thread was answered with the implementing head and corresponding CI result, then resolved.

## 8. CI results

Against validated head `8a7c7a41fe0335df8306e0616e30daae508e7e77`:

### Workflow contract validation — run #70

- Python validator compilation: PASS
- workflow-contract unit/regression suite: **31 tests PASS**
- prompt-overlay presence and idempotence: PASS

### validate-tracker — run #222

- tracker validation: PASS
- public cards validation: PASS
- canonical full validation: PASS
- public projection equals canonical full projection: PASS

### lean-cards — run #17

- full-to-lean generation: PASS
- tracker validation: PASS
- public validation: PASS
- canonical full validation: PASS
- exact projection check: PASS
- generated-commit step: PASS
- canonical full remained unmodified by the exporter: PASS

Vercel preview also reported ready during the PR review cycle.

## 9. One-time migration isolation

The date-specific consolidation remains isolated in:

```text
docs/migrations/BOOTSTRAP_CONSOLIDATION_20260801.md
```

It does not define ordinary-run governance. It requires explicit activation and becomes `COMPLETED_REFERENCE` after completion.

## 10. Remaining implementation work

A subsequent code-focused PR should implement, at minimum:

```text
scripts/build_run_doc_manifest.py
scripts/validate_run_doc_manifest.py
scripts/validate_coverage_completeness.py
schemas/card-run.v1.schema.json
scripts/validate_incremental_card_run.py
scripts/apply_incremental_card_run.py
scripts/validate_declared_card_diff.py
```

It should also add CI gates requiring Stage 0.0D, Stage 0.0C, and Stage 0.7C artifacts for governed card runs.

## 11. Conclusion

The PR now aligns governance and repository automation on one direction:

```text
governed incremental operations
→ data/cards.full.json
→ scripts/lean_cards.mjs
→ public/data/cards.json
```

The canonical full remains the sole source of truth. The public file is a reproducible application artifact. The existing runtime and workflow tests pass, while the not-yet-implemented general incremental apply engine remains explicitly pending rather than being overstated as complete.
