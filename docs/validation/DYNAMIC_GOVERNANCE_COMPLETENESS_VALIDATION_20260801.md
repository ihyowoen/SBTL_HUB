# Dynamic Governance and Editorial Completeness — Validation Record

**Status:** `PASS_DOCS_AND_EXISTING_WORKFLOW_CI_WITH_NEW_ENGINE_PENDING`  
**Branch:** `agent/dynamic-governance-completeness`  
**Base main commit:** `27385027c94f83e060cbee2af964f6f45edd67f5`  
**Validated PR:** `#231`  
**Contract validation scope through:** `a39e0e8eb84889628e5ad241b03ec07418c659eb`

## 1. Scope validated

This record validates:

- governance-document restructuring;
- permanent-rule and one-time-migration separation;
- canonical prompt and manifest registration;
- existing repository workflow-contract tests and overlay checks;
- review findings addressed through the current PR head.

It does not validate:

- a card-data migration;
- the not-yet-implemented incremental apply engine;
- the first complete Stage 0.0D repository inventory;
- production behavior after a data migration.

## 2. Change isolation

GitHub comparison against `main` confirms:

- documentation, prompt, manifest, lifecycle-registry, migration, and validation-record files only;
- no `data/cards.full.json` change;
- no `public/data/cards.json` change;
- no application runtime-code change;
- no existing validator-code change.

The governance change and the one-time migration remain separated from card data.

## 3. Permanent versus migration separation

Validated permanent contracts:

- `docs/RUN_GOVERNANCE_INDEX.md`;
- `docs/DOCUMENT_UNIVERSE_POLICY.md`;
- `docs/EDITORIAL_VALUE_AND_COMPLETENESS_STANDARD.md`;
- `docs/CARD_INCREMENTAL_RUN_CONTRACT.md`;
- permanent named-stage prompts and addenda;
- canonical and upload manifests;
- package README and upload instructions.

The permanent contracts are date-independent and do not name the one-time source runs or transition counts.

Transition-specific source-run dates and consolidation instructions appear only in:

```text
docs/migrations/BOOTSTRAP_CONSOLIDATION_20260801.md
```

That document is classified as `ACTIVE_MIGRATION`, has `ordinary_run_applies=false`, requires explicit activation, and must become `COMPLETED_REFERENCE` after completion.

`COMPLETED_REFERENCE` is now an explicit lifecycle class in both the document-universe policy and the run-governance index. It is readable for audit and conflict detection but never applies automatically to ordinary runs.

## 4. Fixed-document governance closure

Validated:

- Stage 0.0D is the mandatory entry point;
- every file under `docs/**` must be read or parsed in full before applicability classification;
- archived, superseded, reference, completed-migration, and inactive-migration documents are read but not automatically applied;
- a fixed core-document list is not accepted as proof of completeness;
- repository head and file SHAs are mandatory;
- unresolved authority conflicts block the run with `BLOCKED_DOCUMENT_AUTHORITY_CONFLICT`;
- all other incomplete-universe states use `BLOCKED_DOCUMENT_UNIVERSE_INCOMPLETE`.

The Stage 0.0D output schema, Markdown override, and machine-readable override manifest now use the same conflict blocker.

## 5. Editorial completeness closure

Validated:

- Stage 0.0C may search for missing must-report news, material follow-ups, corrections, reversals, and existing-card reinforcement;
- Stage A remains selector-only;
- Stage 0.0C findings are candidate leads, not evidence or accepted facts;
- all discovered candidates must enter the explicit ledger and pass Stage A/B/C;
- regional and topic coverage matrices are mandatory;
- event-stage progression is explicit;
- IB-grade is defined by materiality, execution maturity, incremental information, decision usefulness, evidence quality, claim completeness, and strategic read-through;
- evidence quality, execution maturity, and claim completeness are hard gates;
- Stage 0.7C independently challenges completeness, news value, exclusions, and residual risk before Prompt 0.8.

## 6. FACT_DISCIPLINE compatibility

The dynamic-governance override explicitly preserves the prohibition on silently creating claims or cards through web search.

Stage 0.0C may discover a candidate lead only. The lead must still pass:

```text
Stage A selection
→ Stage B evidence collection
→ Stage C fact-safe validation
→ all post-acceptance gates
```

No source discovered at Stage 0.0C is treated as evidence without direct inspection and claim mapping.

## 7. Prompt 0.8 canonical-full closure

The canonical Prompt 0.8 entry path now directly declares:

```text
merge baseline and source of truth = data/cards.full.json
canonical output                  = data/cards.full.json
application projection            = public/data/cards.json
```

The previous accumulated Prompt 0.8 body is preserved at:

```text
docs/llm_prompts/v1/legacy/10_PROMPT_0_8_GitHub_Merge_Prep_LEGACY_BODY.md
```

It is subordinate and contributes compatible evidence, lineage, duplicate, schema, source-diversity, accounting, PR, and production-boundary safeguards only.

The following former clauses are explicitly non-operative:

- `public/data/cards.json` as current baseline;
- the public projection as merge source of truth or canonical count source;
- the public projection or a local copy as fallback for an unreadable full;
- Prompt 0.8 writing only the public file;
- replace-all as the only merge model;
- a fixed eight-document read as complete governance proof.

The canonical wrapper, mandatory incremental-operation addendum, Markdown override, override manifest, canonical manifest, upload manifest, and lifecycle registry are aligned on this interpretation.

If the canonical full is unreadable, Prompt 0.8 must use:

```text
BLOCKED_CANONICAL_FULL_UNREADABLE
```

If an assembled instruction still treats the public projection as the merge baseline, it must use:

```text
BLOCKED_PROMPT_0_8_PUBLIC_BASELINE_CONFLICT
```

## 8. Incremental operation closure

Validated ordinary operations:

- `insert`;
- `update`;
- `related_add`.

Validated prohibitions for ordinary runs:

- no card deletion;
- no `related_remove`;
- no undeclared existing-card changes;
- no silent loss of existing related edges;
- no stale-baseline force application.

Canonical baseline:

```text
data/cards.full.json
```

Application projection:

```text
public/data/cards.json
```

## 9. Stage-specific closure

Added and registered:

- Stage A expanded-source-universe addendum;
- Prompt 0.8 incremental-operation addendum;
- Prompt 1.1 canonical-promotion addendum.

The canonical Prompt 0.8 wrapper also contains the repository-required `WORKFLOW_CONTRACT_OVERLAY_20260723` block. The preserved legacy body remains separately registered as a subordinate support dependency.

## 10. Manifest reconciliation

Canonical package metadata declares:

- 17 named stage prompts;
- 15 permanent governance documents;
- 2 mandatory override families;
- 9 registered hardening/stage addenda;
- 8 registered existing validator scripts;
- canonical full and lean-projection roles;
- the Prompt 0.8 subordinate legacy body;
- open remediation references;
- migration isolation.

The static counts are informational. Stage 0.0D remains the run-time source of completeness proof.

## 11. Registered path checks

The following registered validator paths were confirmed on the branch with Git blob SHAs:

- `date_role_alignment_check.py`;
- `story_id_lineage_check.py`;
- `related_lineage_check.py`;
- `date_role_freshness_check.py`;
- `evidence_qc_v8_check.py`;
- `related_lifecycle_check.py`;
- `stage_artifact_contract_check.py`;
- `run_workflow_contract_suite.py`.

The registered workflow-gap and legacy-related remediation files were also confirmed.

The canonical manifest, upload manifest, dynamic override manifest, lifecycle registry, canonical Prompt 0.8 wrapper, and subordinate legacy body were fetched back from the branch after update.

## 12. Codex review disposition

Codex review `4834968293` raised three findings. All were accepted as valid and addressed.

### Finding 1 — public-projection merge baseline

Resolution:

- canonical Prompt 0.8 path replaced with a full-baseline wrapper;
- accumulated old body preserved under `legacy/`;
- all public-baseline and public-fallback clauses expressly superseded;
- manifests and lifecycle registry updated;
- workflow-contract overlay restored.

### Finding 2 — missing completed-migration class

Resolution:

- `COMPLETED_REFERENCE` added to the exhaustive policy classification table;
- same class added to the upper-level governance index;
- completed migrations defined as non-operative audit references.

### Finding 3 — authority-conflict blocker absent from Stage 0.0D schema

Resolution:

- Stage 0.0D status enum expanded;
- conflict-specific blocker required when unresolved conflicts exist;
- Markdown and machine-readable override registrations aligned.

All three review threads were replied to and resolved.

## 13. Existing workflow CI completed

GitHub Actions workflow `Workflow contract validation`, run `#51`, completed successfully against the review-addressed PR head.

Validated by that workflow:

- Python validator compilation: PASS;
- existing workflow-contract unit/regression suite: **31 tests PASS**;
- prompt-overlay idempotence and presence check: PASS.

Vercel preview deployment also reported success.

This proves compatibility with the repository’s existing validator and overlay suite. It does not prove the not-yet-implemented dynamic document-universe or incremental-apply engine.

## 14. Remaining execution work

The following remain pending and must not be described as complete:

1. implementation of document-manifest build and validation scripts;
2. implementation of coverage-completeness validation;
3. implementation of the incremental run JSON schema, declared-diff validator, and apply engine;
4. CI gates that require the new Stage 0.0D, Stage 0.0C, and Stage 0.7C artifacts;
5. first actual Stage 0.0D full repository inventory;
6. one-time migration execution;
7. canonical full and lean-projection production verification after data merge.

## 15. Required next implementation PR

The next code-focused PR should implement, at minimum:

```text
scripts/build_run_doc_manifest.py
scripts/validate_run_doc_manifest.py
scripts/validate_coverage_completeness.py
schemas/card-run.v1.schema.json
scripts/validate_incremental_card_run.py
scripts/apply_incremental_card_run.py
scripts/validate_declared_card_diff.py
```

It must add CI gates that block Stage A, Prompt 0.8, and merge when required governance artifacts are absent, stale, or inconsistent.

## 16. Final conclusion

The documentation layer now separates:

```text
permanent ordinary-run governance
from
one-time migration execution
```

and closes the structural gaps around full-document reading, missing-news discovery, existing-card strengthening, material follow-ups, independent completeness review, canonical-full ownership, related preservation, completed-migration classification, and authority-conflict reporting.

The branch passes the repository’s existing workflow-contract CI and has addressed all findings in Codex review `4834968293`.

It is ready for renewed review, but it is not yet entitled to claim machine-enforced end-to-end dynamic governance or incremental card application until the next implementation PR is completed.
