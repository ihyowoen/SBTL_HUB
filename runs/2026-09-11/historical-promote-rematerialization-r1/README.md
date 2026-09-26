# Historical PROMOTE-95 Rematerialization R1

This is the governed production-lane re-entry for the **95 historical items authorized as PROMOTE by reconciliation PR #369**.

## Locked baseline

- main: `3bb929004ff8b547b86e5f1beab0efb3dac19d62`
- canonical full cards: **1,617**
- `data/cards.full.json` blob: `beb2aa7615b583b4c9c0c269974601a0b26c2684`
- source reconciliation: PR #369, final **PROMOTE 95 / KEEP 49 / WATCH 37 / CLOSE 62**
- PROMOTE membership: **95 / 95 unique, duplicate 0**

## Current state

- Stage 0.0D: **PASS**
- Prompt 0.0C: **IN PROGRESS**
- Stage A: **NOT YET AUTHORIZED** until 0.0C passes
- production IDs: **NOT AUTHORIZED**
- canonical mutation: **NOT AUTHORIZED**
- delete / related_remove: **NOT AUTHORIZED**

## Governance boundary

PR #369 remains the reconciliation ledger and is not modified by this run. `PROMOTE` there authorizes rematerialization only; every surviving item must still pass Stage A → Stage B → Stage C → 0.4 → 0.5 → 0.6 → 0.7 → 0.7C → 0.8 before any canonical apply.

The concurrent Sep9 current-run PR #371 is a separate workflow. It remains blocked before Stage A because its 393-row raw source bytes are not materialized. This historical run may perform bounded preflight/coverage/selection work independently, but any later merge/apply must re-lock current main and reconcile against whatever current-run work has landed by then.

## Immediate next gate

Prompt 0.0C must challenge the locked 95 against current canonical, related/lineage, later follow-ups/corrections and current public information across all required regional and topic axes. Only after exact terminal accounting may `stage_a_authorized=true`.
