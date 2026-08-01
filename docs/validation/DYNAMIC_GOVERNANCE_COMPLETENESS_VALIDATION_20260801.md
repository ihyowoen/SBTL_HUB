# Dynamic Governance and Editorial Completeness — Validation Record

**Status:** `PASS_GOVERNANCE_AND_FULL_TO_LEAN_RUNTIME_WITH_INCREMENTAL_ENGINE_PENDING`  
**Branch:** `agent/dynamic-governance-completeness`  
**Base main commit:** `27385027c94f83e060cbee2af964f6f45edd67f5`  
**Validated PR:** `#231`  
**Runtime, upload workflow, and regression-test implementation validated through:** `0293b1601aee3221ce238969a104dbeca59ca18a`

Later commits that only synchronize manifests or this validation record do not alter the validated exporter, workflow, upload instructions, or regression-test behavior; their own CI must still pass before merge.

## 1. Validated scope

This record validates:

- permanent governance and one-time migration separation;
- complete `docs/**` document-universe preflight requirements;
- coverage discovery and independent completeness review contracts;
- canonical full ownership and Stage A baseline requirements;
- Prompt 0.8 canonical-full merge preparation contract;
- full-to-lean exporter implementation and workflow write boundaries;
- malformed-public self-healing;
- byte-exact public projection serialization;
- direct-path, symlink-alias, and hard-link full/public collision protection;
- upload instructions that stage all registered runtime contracts and their tests;
- repository validators, prompt-overlay checks, and 35 unit/regression tests;
- Codex findings addressed through the implementation commit above.

This record does not claim completion of:

- the generic incremental apply engine for `insert`, `update`, and `related_add`;
- executable Stage 0.0D manifest generation;
- executable coverage-completeness validation;
- the first governed migration execution;
- production verification after a future card-data merge.

## 2. Canonical data contract

```text
data/cards.full.json      sole canonical inventory and full metadata source
public/data/cards.json    generated lean application projection only
```

Enforced rules:

- Stage A performs duplicate, reinforcement, follow-up, correction, stage-transition, and related-lineage screening against the verified current GitHub `main` full content;
- an uploaded or local copy is usable only when byte-equivalent to the locked canonical full blob;
- Prompt 0.8 uses the canonical full as merge input, count source, metadata-preservation source, and canonical output;
- the public projection is not a baseline, batch inbox, fallback, or source for rebuilding the full;
- `scripts/lean_cards.mjs` reads the full and writes only the public projection;
- `.github/workflows/lean-cards.yml` commits only the generated public projection;
- public-only edits are overwritten by the canonical projection;
- an absent or invalid canonical full blocks generation;
- an invalid existing public projection is treated as stale output in generation mode and rebuilt from the valid full;
- semantically equivalent but byte-different public JSON is regenerated into the canonical compact serialization;
- `--check` fails on unreadable, mismatched, or byte-different public output;
- full and public paths must resolve to distinct paths and distinct filesystem objects before any write;
- device/inode identity prevents distinct hard-link names from bypassing the collision guard.

## 3. Runtime, upload, and regression-test changes

This PR intentionally changes:

```text
scripts/lean_cards.mjs
.github/workflows/lean-cards.yml
validation_scripts/tests/test_lean_cards_exporter.py
docs/llm_prompts/v1/UPLOAD_INSTRUCTIONS.md
```

### Exporter modes

```text
node scripts/lean_cards.mjs          generate public from full
node scripts/lean_cards.mjs --check  verify exact projection and bytes without writing
node scripts/lean_cards.mjs --dry    preview generation without writing
```

Projection verification covers:

- top-level metadata equality;
- card-count equality;
- card-order and ID equality;
- KEEP-field presence and value equality;
- absence of non-KEEP fields in public output;
- exact generated-byte equality.

### Added regression tests

- `test_generation_repairs_malformed_public_without_mutating_full`
- `test_generation_normalizes_semantically_equal_pretty_public`
- `test_same_full_and_public_path_is_rejected_without_writing`
- `test_hard_linked_full_and_public_paths_are_rejected_without_writing`

Together they verify malformed-public recovery, pretty-print normalization, strict byte checks, direct-path rejection, hard-link rejection, and byte-for-byte full preservation.

### Upload workflow

The active upload procedure stages:

```text
docs/
validation_scripts/
scripts/lean_cards.mjs
.github/workflows/lean-cards.yml
```

It also verifies that the registered exporter, workflow, and exporter regression-test path are present in the staged package. Card data remains excluded.

## 4. Document-universe closure

Stage 0.0D requires:

- full enumeration, reading, or parsing of every `docs/**` file before classification;
- reading inactive migrations, completed references, reference-only, superseded, and archived files;
- the complete nine-class lifecycle model;
- lifecycle-registry self-classification as `ACTIVE_VALIDATOR_CONTRACT`;
- conflict-specific blocker precedence;
- typed preservation of every secondary incomplete-universe defect;
- no Stage 0.0C authorization unless all identity, read, classification, dependency, and conflict gates pass.

## 5. Editorial completeness closure

```text
0.0D Document Universe Preflight
→ 0.0C Coverage Discovery
→ Stage A/B/C
→ post-acceptance quality stages
→ 0.7C independent completeness and news-value review
→ 0.8 canonical incremental merge preparation
→ 0.9 production verification
```

Required review surface includes missing must-report news, follow-ups, execution-stage transitions, corrections and reversals, existing-card reinforcement, regional/topic coverage, exclusion rescue, evidence quality, materiality, incremental information, and decision usefulness.

Stage 0.0C findings remain candidate leads and must pass Stage A/B/C. Discovery search does not become evidence automatically.

## 6. Incremental operation contract

Ordinary operations:

```text
insert
update
related_add
```

Ordinary prohibitions:

```text
delete
related_remove
public_to_full_ingest
undeclared existing-card changes
silent related-edge loss
```

The canonical full may be materialized only through a governed declared-operation path with base locking, count reconciliation, declared field-level diffs, ID and duplicate validation, related preservation, target resolution, and full validation before public projection generation.

The generic executable incremental apply engine remains pending follow-up implementation.

## 7. Review findings addressed

Accepted and addressed findings include:

- public projection incorrectly allowed as Prompt 0.8 baseline;
- missing lifecycle and blocker registrations;
- inactive documents not guaranteed to be read;
- ambiguous blocker precedence and incomplete secondary-defect recording;
- invalid universe status and registry self-classification;
- document-record classification limited to one lifecycle class;
- reverse-direction public-to-full exporter conflict;
- Stage A allowing stale uploaded or local baselines;
- generation unable to repair malformed public JSON;
- direct path collision capable of overwriting full metadata;
- different hard-link names capable of bypassing path-string collision checks;
- upload instructions omitting registered runtime files from staging;
- semantically equal but byte-different public JSON escaping deterministic regeneration.

Each thread was answered with implementation and CI evidence, then resolved.

## 8. CI evidence

Against implementation head `0293b1601aee3221ce238969a104dbeca59ca18a`:

### Workflow contract validation — run #82

- Python validator compilation: PASS
- unit/regression suite: **35 tests PASS**
- malformed-public, pretty-print normalization, direct-path, and hard-link exporter tests: PASS
- prompt files checked: 11
- missing prompt files: 0
- overlay updates required: 0

### validate-tracker — run #234

- tracker validation: PASS
- public cards validation: PASS
- canonical full validation: PASS
- public projection equals canonical full exact projection: PASS

### lean-cards — run #29

- full-to-lean generation: PASS
- tracker/public/full validation: PASS
- exact value and byte projection check: PASS
- generated-commit step: PASS
- canonical full write boundary: PASS

Vercel preview also reported ready during the PR review cycle.

## 9. One-time migration isolation

The date-specific consolidation remains isolated in:

```text
docs/migrations/BOOTSTRAP_CONSOLIDATION_20260801.md
```

It requires explicit activation, does not define ordinary-run governance, and becomes `COMPLETED_REFERENCE` after completion.

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

The validated direction is:

```text
governed incremental operations
→ data/cards.full.json
→ scripts/lean_cards.mjs
→ public/data/cards.json
```

The canonical full remains the sole source of truth. The public file is a reproducible, byte-deterministic application artifact. Runtime protection, upload-package completeness, and regression tests pass, while the not-yet-implemented generic incremental apply engine remains explicitly pending.
