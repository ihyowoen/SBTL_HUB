# Historical Candidate Reconciliation R1

This is a **reconciliation-only cumulative working PR** for SBTL candidate governance.

## Baseline

- branch creation base: `8f3b6c3277d7cd13ccfc48f3c72a5d1ecb5d7c58`
- current relocked main: `3bb929004ff8b547b86e5f1beab0efb3dac19d62`
- canonical `data/cards.full.json` blob: `beb2aa7615b583b4c9c0c269974601a0b26c2684`
- current canonical card count: **1,617**
- canonical card data is **not modified in this PR**
- historical batches 1–50 still require their final collision relock against this 1,617-card baseline before PR closure/readiness

## Purpose

Accumulate candidate-review corrections and historical backlog reconciliation without losing provenance between chat sessions or moving-main events.

Allowed current dispositions: `PROMOTE`, `KEEP_CANDIDATE`, `DOWNGRADE_WATCH`, `CLOSE`.

`PROMOTE` means **authorized for formal re-entry/rematerialization**, not permission to edit canonical data directly. Any promoted item must still run through the normal Stage A/B/C → 0.4 → 0.5 → 0.6 → 0.7 → 0.7C → 0.8 production chain before a separate production/apply PR.

## Membership authority

For the Aug25 historical backlog, the **final 0.1P review-pool promotion artifact** is the membership authority. Where it explicitly re-tiered an item after the merged Stage A rescue audit, the later 0.1P disposition supersedes the earlier Stage A disposition.

The source-augmentation correction cohorts therefore restore lineages that had been omitted when pre-0.1P watchlist states were mistakenly treated as terminal. No candidates were invented to force the denominator.

## Current checkpoints

### Sep3 + Sep7 current candidate master

- 80 unique events
- PROMOTE 3 / KEEP 4 / WATCH 34 / CLOSE 39
- the 3 promotions are already canonicalized Sep7 items
- pending new Stage-B admission from Sep3 retained cohort: 0

### Historical Aug25-derived backlog

Derivation locked as:

`264 needs_user_decision - 18 later-promoted unique story IDs = 246 - 3 exact canonicalized = 243`

Historical membership reconciliation is now **243/243 complete**:

- PROMOTE **95**
- KEEP **49**
- WATCH **37**
- CLOSE **62**
- remaining membership **0**
- unassigned **0**
- duplicate membership **0**

Latest batch `226–243` is fully assigned at **PROMOTE 2 / KEEP 5 / WATCH 5 / CLOSE 6**. Its exact membership and reasons are recorded in `historical-candidate-243-progress-243.md`.

## Remaining closure gate

Membership accounting is complete, but this PR intentionally remains **draft**. Batches 1–50 were adjudicated before the current 1,617-card canonical baseline and therefore require a focused final collision relock. Batches 51–243 were already screened/relocked on the current baseline.

The next action is:

`identify the canonical baseline used by batches 1–50 → compare only canonical additions since that baseline → test the 50 historical memberships for exact/same-event collisions → supersede any affected decisions → record final 1,617-card relock`.

Only after that gate is PASS may PR #369 be made ready for review. Production card changes remain a separate PR.
