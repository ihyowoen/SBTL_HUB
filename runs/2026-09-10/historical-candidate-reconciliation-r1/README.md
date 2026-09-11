# Historical Candidate Reconciliation R1

This is a **reconciliation-only cumulative PR** for SBTL candidate governance.

## Final baseline

- original 1–50 review baseline: main `e19f6c113ccb62906e7fdefaf3bae657c58b5637` / canonical **1,599**
- current relocked main: `3bb929004ff8b547b86e5f1beab0efb3dac19d62`
- current canonical `data/cards.full.json` blob: `beb2aa7615b583b4c9c0c269974601a0b26c2684`
- current canonical card count: **1,617**
- canonical card data modified by this PR: **no**

## Historical membership reconciliation — COMPLETE

Derivation:

`264 needs_user_decision - 18 later-promoted unique story IDs = 246 - 3 exact canonicalized = 243`

Membership authority is the **final 0.1P review-pool promotion artifact**. When final 0.1P explicitly re-tiered an item after the merged Stage A rescue audit, the later 0.1P disposition superseded the earlier Stage A disposition.

All **243 / 243** historical memberships now have exactly one terminal reconciliation disposition:

- PROMOTE **95**
- KEEP **49**
- WATCH **37**
- CLOSE **62**
- remaining **0**
- unassigned **0**
- duplicate membership **0**

`PROMOTE` means **authorized for formal re-entry/rematerialization only**. It does not authorize direct canonical admission. Promoted items must still pass the ordinary Stage A/B/C → 0.4 → 0.5 → 0.6 → 0.7 → 0.7C → 0.8 production chain in a separate production workflow.

## Final 1–50 collision relock — PASS

Batches 1–50 had originally been adjudicated against the 1,599-card `e19f6c113…` baseline. The Sep8 production audit proves the canonical transition from that exact base to the current 1,617-card state was **18 inserts / 0 updates**.

The 18 inserted cards were read from the authoritative `id-allocation`, `card-run-audit` and Stage 0.8 lineage artifacts and checked against all 50 historical memberships.

Result:

- 50 / 50 checked
- delta cards checked: 18 / 18
- new exact/same-event collisions: **0**
- decision supersessions required: **0**
- relock status: **PASS**

Detailed audit: `historical-candidate-1-50-final-1617-collision-relock.md`.

## Current closure state

- membership gate: **PASS**
- 1–50 current-canonical collision gate: **PASS**
- reconciliation artifact consistency: **PASS**
- canonical mutation in this PR: **0**
- reconciliation PR state target: **READY FOR REVIEW**

The next workflow is not another reconciliation batch. It is the separate rematerialization/production handling of the 95 `PROMOTE` decisions under normal governed Stage A/B/C and 0.4–0.8 rules.
