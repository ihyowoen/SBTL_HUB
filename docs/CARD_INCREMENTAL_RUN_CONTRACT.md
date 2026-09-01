# Card Incremental Run Contract V2

**Status:** `ACTIVE_CANONICAL`  
**Version:** `CARD_INCREMENTAL_RUN_V2_20260901`

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

### 6.1 Per-operation stage-chain binding
Every formal `insert`, `update`, and `related_add` operation must prove the complete ordinary editorial chain for the same governed candidate identity:

`A → B → C → 0.4 → 0.5 → 0.6 → 0.7`

`0.2R` and `0.3R` are conditional repair artifacts and never substitute for the re-established B/C outputs. A formal stage artifact must declare its ordinary `stage`; an unknown or repair/revise stage marker may not be reclassified from a bucket name. Run-level 0.0D, 0.0C, and 0.7C remain separately bound governance artifacts.

For each operation:

- every mandatory stage must be represented in that operation's own `stage_artifacts[]`;
- every A/B/C/0.4/0.5/0.6/0.7 artifact must carry exact `run_id`, `base_main_commit_sha`, and `base_full_blob_sha` equal to the card run; stale artifacts from another run/baseline are invalid even if their candidate ID matches;
- Stage A must pass both the V4 Stage A contract and the authoritative lineage/compatibility gate;
- B/C/0.4/0.5/0.6/0.7 artifacts must pass their stage-output machine contract;
- all seven stage outputs must contain the operation's same `source_spec_id` (`spec_id` at Stage A, `source_spec_id` downstream);
- an insert binds to required `card.source_spec_id`;
- an update normally binds to the existing canonical card's `source_spec_id`. If a legacy canonical card predates that field, the operation must declare `source_spec_id`; if both canonical and operation values exist they must match exactly;
- a Related addition normally binds to a governed endpoint `source_spec_id`. If neither legacy endpoint carries one, the operation must declare both `source_spec_id` and `identity_card_id`, where `identity_card_id` equals `source_id` or `target_id`; the declared candidate identity must then be present in every A→0.7 artifact. If an endpoint identity exists, any declared `source_spec_id` must match one of the governed endpoints.

A passing artifact for another candidate cannot authorize an operation. A global Stage A count cannot satisfy another operation. Missing stage, stale run/baseline binding, missing candidate identity, or cross-candidate artifact reuse is merge-blocking.

### 6.2 0.0D/0.0C production reconciliation
The formal gate must validate—not merely trust—the detailed preflight/discovery conclusions:

- 0.0D exact main/full SHA bindings; `active_canonical_paths` must exactly equal the current lifecycle registry's `active_canonical + active_named_prompts`; `active_validator_contract_paths` must exactly equal `active_validator_contracts`; applicable remediation/migration must exactly equal `open_remediations + activation_required_migrations`; `active_full_read_count` must equal that exact unique active/dependency closure; classified count equals inventory count; all defect/conflict/unread/unclassified ledgers are empty on PASS; active override/addendum count is zero; embedded Stage A news-value verification is true; compatibility booleans agree with the detailed ledgers.
- 0.0C exact 0.0D/full bindings; regional matrix must include `korea`, `north_america`, `china`, `japan`, `europe`, `material_global_markets`; topic matrix must include all canonical topic axes defined by Prompt 0.0C; each required axis must terminate as `searched` or `blocked` (with reason when blocked); every original/discovered candidate is present in the expanded-universe ledger; every expanded candidate has exactly one terminal disposition; terminal rows for unknown candidates are forbidden; only then may `original_input_accounted=true` and `stage_a_authorized=true` authorize Stage A.

## 7. Baseline moved

If current main/full differs from the declared baseline, stop with `BLOCKED_BASELINE_MOVED_REBASE_REQUIRED`. Revalidate duplicate/update/follow-up/Related/addability against the new baseline before applying.

## 8. Declared diff

Prove all inserts are new, updates target existing IDs and only declared fields change, no existing card/Related edge disappears, all new relations resolve, no new dangling/self/duplicate relation appears, counts reconcile, canonical remains latest-first, and lean regenerates exactly.

Any undeclared change blocks merge.

## 9. One PR boundary

Default formal run: one governed card-run manifest plus the committed canonical full/lean outputs and required audit artifacts under the current workflow contract. Do not mix formal card-run with manual direct-add or a dedicated migration in one data PR.

## 10. Apply order

`re-lock baseline → validate registry-bound 0.0D → validate mandatory-axis 0.0C → validate current-run/baseline-bound candidate A→0.7 chains → validate 0.7C → validate operations → apply inserts → apply updates → resolve/apply Related additions → validate declared diff → write full → generate lean → run validators → PR review → merge → 0.9`.

## 11. Manual direct-add boundary

Already-reviewed bounded changes may instead use `MANUAL_DIRECT_ADD_V2`. That mode declares its own editorial attestation and mutation scope and explicitly states `formal_full_run_claimed=false`. It does not require fake Stage A/B/C/0.7C/0.8 artifacts.

## 12. Completion

`github_merge_ready` is not `production_verified`. A formal run ends only after Prompt 0.9 verifies intended main and required production surfaces.
