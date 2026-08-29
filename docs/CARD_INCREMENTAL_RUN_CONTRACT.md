# Card Incremental Run Contract V2

**Status:** `ACTIVE_CANONICAL`  
**Version:** `CARD_INCREMENTAL_RUN_V2_20260829`

## 1. Scope

This contract owns **formal Prompt 0.8 card-run mutation** after a completed formal editorial workflow. Manual direct-add is a separate governed mutation mode and is not a card-run impersonation.

## 2. Canonical ownership

- `data/cards.full.json` = sole canonical inventory;
- `public/data/cards.json` = deterministic lean projection;
- every mutation locks exact base main commit SHA, full blob SHA, and before count;
- stale local/downloaded copies are never mutation baselines.

## 3. Formal ordinary operations

Allowed:

- `insert` — independently cardable new event/follow-up/program-lineage card;
- `update` — bounded declared field changes to an existing represented event;
- `related_add` — verified direct lineage edge.

Not ordinary:

- card deletion;
- `related_remove`;
- silent replacement;
- undeclared existing-card modification;
- legacy dangling-edge cleanup.

Those require separately scoped remediation/migration and explicit approval.

## 4. Insert/update distinction

Use update when the represented event remains the same and new evidence corrects/completes it without independent follow-up cardability.

Use insert for a distinct material event or direct follow-up that passed lineage/cardability/addability. A newer article alone is reinforcement, not insert.

## 5. Related

`related_add` requires source/target production IDs or a pre-0.8 provisional mapping that is resolved before canonical write, relation type, direct-lineage reason, and evidence. Shared actor/topic/chemistry/geography is insufficient. Existing edges are preserved by default.

## 6. Run artifact

The formal card-run records run ID, exact base SHAs/count, declared operations, expected after count, stage/audit references including 0.0D/0.0C/0.7C, Related ID-resolution ledger, and apply/validator results required by current machine schema.

## 7. Baseline moved

If current main/full differs from the declared baseline, stop with `BLOCKED_BASELINE_MOVED_REBASE_REQUIRED`. Revalidate duplicate/update/follow-up/Related/addability against the new baseline before applying.

## 8. Declared diff

Prove all inserts are new, updates target existing IDs and only declared fields change, no existing card/Related edge disappears, all new relations resolve, no new dangling/self/duplicate relation appears, counts reconcile, canonical remains latest-first, and lean regenerates exactly.

Any undeclared change blocks merge.

## 9. One PR boundary

Default formal run: one governed card-run manifest plus the committed canonical full/lean outputs and required audit artifacts under the current workflow contract. Do not mix formal card-run with manual direct-add or a dedicated migration in one data PR.

## 10. Apply order

`re-lock baseline → validate run/artifacts → validate operations → apply inserts → apply updates → resolve/apply Related additions → validate declared diff → write full → generate lean → run validators → PR review → merge → 0.9`.

## 11. Manual direct-add boundary

Already-reviewed bounded changes may instead use `MANUAL_DIRECT_ADD_V2`. That mode declares its own editorial attestation and mutation scope and explicitly states `formal_full_run_claimed=false`. It does not require fake Stage A/B/C/0.7C/0.8 artifacts.

## 12. Completion

`github_merge_ready` is not `production_verified`. A formal run ends only after Prompt 0.9 verifies intended main and required production surfaces.