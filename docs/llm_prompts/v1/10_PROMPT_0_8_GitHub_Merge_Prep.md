# Prompt 0.8 — Incremental Operation & GitHub Merge Preparation V4

**Status:** `ACTIVE_CANONICAL`  
**Version:** `PROMPT_0_8_V4_20260829`

Require formal 0.7 publish-ready and 0.7C authorization. Re-lock exact current main/canonical blob before operations. If baseline moved, rerun required 0.4+ checks.

Allowed ordinary operations: `insert`, `update`, `related_add`. No ordinary `delete` or `related_remove`.

Resolve all provisional current-batch relation identifiers to final production IDs and preserve a resolution ledger. Fail dangling, self, duplicate, ambiguous, unexplained, or unresolved relations.

Create governed card-run against locked baseline. Validate operation counts/targets/audit binding, apply canonical full mutation, generate lean deterministically from full, and prove no undeclared existing-card change or lost existing Related edge.

Run current card-run/schema/engine, full/lean/card/date/story-ID/Related/source/stage-lineage/selection-route validators, projection check, diff sanity, and workflows. Only this stage may emit formal full-run `github_merge_ready`; it is distinct from manual direct-add.