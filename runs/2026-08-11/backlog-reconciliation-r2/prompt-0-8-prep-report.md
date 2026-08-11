# Prompt 0.8 — Canonical Incremental Merge Preparation

Run: `20260809_BACKLOG_RECONCILIATION_R2`
Baseline main: `d3137945860664116b1bf90bbb7bee54d2a6c1d9`
Canonical blob: `a52745170c70aa649323e346413615c5995b890b`
Baseline count: **1,343**

## Final result after PR review remediation

**GITHUB_MERGE_READY**

The current Prompt 0.8 package was rematerialized from the exact locked baseline after addressing Codex review `#issuecomment-5252539754`. No card selection was discarded: two candidates that duplicated already represented events were reclassified from new-card inserts to existing-card updates.

### Final operations

- insert: **30**
- update: **3** (`2026-06-26_EU_01`, `R14_05`, `2026-07-07_KR_01`)
- related_add: **9**
- related_remove: **0**
- delete: **0**
- expected canonical count: **1,373**

### Review corrections

- Source-derived audit metadata is persisted for every current insert and every updated target; strict recomputation is clean on the final merge scope.
- All current inserts carry accepted/addable/publish/GitHub/PR readiness state and no runtime-pending flag.
- `REC26_A2_072` is reinforcement/update of baseline `R14_05`, not a duplicate Volta card.
- `REC26_A2_042` updates baseline `2026-07-07_KR_01` with the July 30 final Q2 ESS shipment/order detail; the former distinct-follow-up edge is removed.
- The Korea–Argentina correction artifact is included in the bundle manifest.
- Markdown hard-break trailing spaces were removed; PR-range `git diff --check` is part of the final gate.

### Runtime verification

- governed materialization: **PASS**
- source-audit recomputation strict check: **PASS**
- date-role freshness on current inserts: **PASS**
- Evidence QC on current merge scope: **PASS**
- Related lifecycle contract on current inserts: **PASS**
- Stage 0.8 artifact contract: **PASS**
- canonical/lean validators and exact lean projection: **PASS**
- run-level audit/operation binding: **PASS**
- byte-exact governed output verify: **PASS**
- PR-range `git diff --check`: **PASS**
