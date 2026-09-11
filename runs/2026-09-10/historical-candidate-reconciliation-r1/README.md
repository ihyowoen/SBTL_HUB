# Historical Candidate Reconciliation R1

This is a **reconciliation-only cumulative working PR** for SBTL candidate governance.

## Baseline

- branch creation base: `8f3b6c3277d7cd13ccfc48f3c72a5d1ecb5d7c58`
- current relocked main: `3bb929004ff8b547b86e5f1beab0efb3dac19d62`
- canonical `data/cards.full.json` blob: `beb2aa7615b583b4c9c0c269974601a0b26c2684`
- current canonical card count: **1,617**
- canonical data changed across the latest main move: **no**
- canonical card data is **not modified in this PR**
- historical batches 1–50 still require their separate final 1,617-card collision relock before full closure

## Purpose

Accumulate candidate-review corrections and historical backlog reconciliation without losing provenance between chat sessions or moving-main events.

The governing flow is:

`first_seen → prior_runs → last_review → later promotion/canonicalization/watch/closure → current disposition`

Allowed current dispositions: `PROMOTE`, `KEEP_CANDIDATE`, `DOWNGRADE_WATCH`, `CLOSE`.

`PROMOTE` here means **authorized for formal re-entry/rematerialization**, not permission to edit canonical data directly. Any promoted item must still run through the normal Stage A/B/C → 0.4 → 0.5 → 0.6 → 0.7 → 0.7C → 0.8 production chain before a separate production/apply PR.

## Membership authority

For the Aug25 historical backlog, the **final 0.1P review-pool promotion artifact** is the membership authority. Where it explicitly re-tiered an item after the merged Stage A rescue audit, the later 0.1P disposition supersedes the earlier Stage A disposition.

This matters for the source-augmentation correction cohort: items such as `U0335`, `U1219`, `U1660` and others were initially placed in watchlist but later restored by 0.1P to `needs_user_decision_after_review / source_augmentation_queue=true`. The 201–225 checkpoint records this supersession explicitly rather than silently dropping those lineages.

## Current checkpoints

### Sep3 + Sep7 current candidate master

- 80 unique events
- PROMOTE 3 / KEEP 4 / WATCH 34 / CLOSE 39
- the 3 promotions are already canonicalized Sep7 items
- pending new Stage-B admission from Sep3 retained cohort: 0

### Historical Aug25-derived backlog

Derivation locked as:

`264 needs_user_decision - 18 later-promoted unique story IDs = 246 - 3 exact canonicalized = 243`

Reconciliation progress is now committed through **225/243**:

- PROMOTE **93**
- KEEP **44**
- WATCH **32**
- CLOSE **56**
- remaining **18**

Latest batch `201–225` is fully assigned at **PROMOTE 6 / KEEP 7 / WATCH 4 / CLOSE 8**, with unassigned=0 and duplicate_membership=0.

Remaining exact membership is locked as four source-queue corrections — `U0891, U0335, U1219, U1660` — plus fourteen earnings-deep-dive lineages — `U0920, U1518, U0617, U0675, U1139, U0626, U1350, U0503, U0897, U1047, U1655, U0794, U1036, U1746`.

These counts remain partial until 243/243 is terminally accounted and the 1–50 cohort receives its final 1,617-card collision relock.

## PR operating rule

This PR stays **draft** while reconciliation is incomplete. The final historical-membership checkpoint is `243/243`; after that, the pending 1–50 collision relock must be closed before the reconciliation PR can be made ready for review. Production card changes remain a separate PR.
