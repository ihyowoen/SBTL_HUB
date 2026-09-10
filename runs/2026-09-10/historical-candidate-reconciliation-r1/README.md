# Historical Candidate Reconciliation R1

This is a **reconciliation-only cumulative working PR** for SBTL candidate governance.

## Baseline

- branch creation base: `8f3b6c3277d7cd13ccfc48f3c72a5d1ecb5d7c58`
- current relocked main: `3bb929004ff8b547b86e5f1beab0efb3dac19d62`
- canonical `data/cards.full.json` blob before/after main move: `beb2aa7615b583b4c9c0c269974601a0b26c2684` → `beb2aa7615b583b4c9c0c269974601a0b26c2684`
- canonical data changed across relock: **no**
- therefore the moving-main event requires provenance relock only; previously completed candidate adjudications do **not** reset
- canonical card data is **not modified in this PR**
- `data/cards.full.json` and card-run production operations are out of scope

## Purpose

Accumulate candidate-review corrections and historical backlog reconciliation without losing provenance between chat sessions or moving-main events.

The governing flow is:

`first_seen → prior_runs → last_review → later promotion/canonicalization/watch/closure → current disposition`

Allowed current dispositions:

- `PROMOTE`
- `KEEP_CANDIDATE`
- `DOWNGRADE_WATCH`
- `CLOSE`

`PROMOTE` here means **authorized for formal re-entry/rematerialization**, not permission to edit canonical data directly. Any promoted item must still run through the normal Stage A/B/C → 0.4 → 0.5 → 0.6 → 0.7 → 0.7C → 0.8 production chain before a separate production/apply PR.

## Current checkpoints

### Sep3 + Sep7 current candidate master

- 80 unique events
- PROMOTE 3 / KEEP 4 / WATCH 34 / CLOSE 39
- the 3 promotions are already canonicalized Sep7 items
- pending new Stage-B admission from Sep3 retained cohort: 0

### Historical Aug25-derived backlog

Derivation locked as:

`264 needs_user_decision - 18 later-promoted unique story IDs = 246 - 3 exact canonicalized = 243`

Reconciliation progress currently committed in batches. At 50/243:

- PROMOTE 15
- KEEP 10
- WATCH 9
- CLOSE 16
- remaining 193

These counts are partial and must not be treated as final until 243/243 is assigned with unassigned=0 and duplicate_membership=0.

## PR operating rule

This PR stays **draft** while reconciliation is incomplete. New 25-item checkpoints are appended as commits (`75/243`, `100/243`, ...). Existing decisions may be corrected only with an explicit supersession note and provenance. When 243/243 is terminally accounted, the reconciliation PR can be made ready for review. Production card changes remain a separate PR.
