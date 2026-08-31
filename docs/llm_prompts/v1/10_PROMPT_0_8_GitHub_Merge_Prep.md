# Prompt 0.8 — Incremental Operation & GitHub Merge Preparation V4

**Status:** `ACTIVE_CANONICAL`  
**Version:** `PROMPT_0_8_V4_20260831`

Require formal 0.7 publish-ready and 0.7C authorization. Re-lock exact current main/canonical blob before operations. If baseline moved, rerun required 0.4+ checks.

Allowed ordinary operations: `insert`, `update`, `related_add`. No ordinary `delete` or `related_remove`.

Resolve all provisional current-batch relation identifiers to final production IDs and preserve a resolution ledger. Fail dangling, self, duplicate, ambiguous, unexplained, or unresolved relations.

## Post-resolution current-run scope

After final production IDs are assigned, write `ID_LEDGER` as the exact set of final production IDs for every current-run inserted or materially updated card. The ledger must not contain provisional candidate IDs, titles, partial IDs, fuzzy aliases, or unresolved mappings. Every ledger ID must resolve to exactly one card in the candidate canonical full, and every current-run candidate must resolve to exactly one ledger ID. Zero-match, multi-match, duplicate, or ambiguous identity resolution blocks merge preparation.

Re-run the semantic validators **after** provisional-to-production ID resolution and against the materialized candidate canonical full:

```text
python validation_scripts/related_lifecycle_check.py <CANDIDATE_CANONICAL_FULL> --require-contract --new-id-file <ID_LEDGER>
python validation_scripts/evidence_qc_v8_check.py <CANDIDATE_CANONICAL_FULL> --new-id-file <ID_LEDGER>
python validation_scripts/date_role_freshness_check.py <CANDIDATE_CANONICAL_FULL> --require-date-role --new-id-file <ID_LEDGER>
python validation_scripts/stage_artifact_contract_check.py 0.8 <PROMPT_0_8_ARTIFACT>
```

Prompt 0.8 must **not** use `--allow-provisional-related`: provisional Related targets are a bounded 0.7 allowance only. At merge prep all current-run Related targets must be final production IDs and must pass the active Related lifecycle/fresh-anchor contract in final graph form. A JavaScript card-run shape validator, declared patch validator, or projection validator does not substitute for these scoped semantic checks.

Any failure routes the item back to the earliest responsible stage or blocks the run. `github_merge_ready` may not be emitted while any scoped semantic validator is failing or while `ID_LEDGER` differs from the final current-run identity set.

Create governed card-run against locked baseline. Validate operation counts/targets/audit binding, apply canonical full mutation, generate lean deterministically from full, and prove no undeclared existing-card change or lost existing Related edge.

Run current card-run/schema/engine, full/lean/card/date/story-ID/Related/source/stage-lineage/selection-route validators, projection check, diff sanity, and workflows. Only this stage may emit formal full-run `github_merge_ready`; it is distinct from manual direct-add.
