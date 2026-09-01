# Related Event Lifecycle Contract V3

**Status:** `ACTIVE_CANONICAL`  
**Version:** `RELATED_LIFECYCLE_V3_20260901`

## 0. Purpose

This contract governs duplicate, reinforcement, follow-up, program-lineage, and unrelated-event decisions from Stage A through production.

`related[]` is direct auditable event lineage. It is not a same-company, same-sector, same-chemistry, same-country, same-theme, or keyword-similarity field.

## 1. Canonical relation types

- `same_event_duplicate`
- `distinct_follow_up`
- `existing_card_reinforcement`
- `program_lineage`
- `new_unrelated_event`
- `uncertain_needs_review`

Publishing treatment:

| relation type | new card? | treatment |
|---|---:|---|
| same_event_duplicate | no | retain unique facts/sources in reinforcement ledger |
| existing_card_reinforcement | no | update/reinforce representative card |
| distinct_follow_up | yes, if independently cardable | direct predecessor + fresh material anchor required |
| program_lineage | yes, if independently cardable | named project/program evidence required |
| new_unrelated_event | yes | `related[]` empty |
| uncertain_needs_review | no | bounded review/hold |

## 2. Event fingerprint

Compare actor/authority, asset/project/policy/program/contract/product, location/jurisdiction, event type, event/representative date, anchor class, factual anchor, canonical source cluster, source story identities, and predecessor/successor stage or changed judgment.

Similarity can rank candidates but never decide lineage alone.

## 3. Stage A related pre-pass

Stage A is metadata-only. Every strict and bounded-review candidate emits `related_prepass` containing:

- `status: PASS|HOLD`;
- `same_event_checked`;
- baseline candidate IDs and current-batch candidate IDs;
- relation candidates with target, proposed type, confidence, reason, anchor class to verify, and incremental anchor question;
- duplicate disposition;
- preliminary earliest-same-event check status;
- proposed fresh follow-up anchor class/question.

**Queue rule:** `strict_passed_spec[]` accepts only `related_prepass.status = PASS`. A `HOLD` pre-pass belongs in the bounded review/hold pool and must not enter the normal Stage B strict queue.

For a strict PASS pre-pass:

- `same_event_checked = true`;
- `earliest_same_event_check_status = PASS`;
- `duplicate_disposition = no_duplicate_found`;
- clear same-event duplicate, reinforcement-only, or unresolved relation dispositions are forbidden.

Hard rules:

- Stage A does not lock final `related[]`.
- clear same-event duplicates do not enter the normal Stage B new-card queue;
- probable follow-ups carry the exact relation/evidence question into Stage B;
- candidate-to-candidate edges are preserved even before production IDs exist;
- a newer article date is not a fresh anchor.

## 4. Stage B evidence resolution

Stage B resolves the pre-pass using body-level or official evidence and emits `related_evidence_review` with:

- same-event and earliest-same-event checks;
- earliest same-event date/source when known;
- final evidence-level relation type;
- matched baseline/current candidate identifiers;
- fresh follow-up anchor class and anchor;
- incremental fact vs predecessor;
- changed judgment vs predecessor;
- relation reason;
- rejected relation candidates;
- reinforcement transfer ledger.

A `distinct_follow_up` must prove a current anchor from the integrated Stage A anchor classes: execution, policy/regulatory, data/financial, strategic behavior, technology commercialisation, or follow-up probability.

## 5. Universal distinct-follow-up requirements

Every distinct follow-up proves:

1. direct lineage to named predecessor card(s);
2. current specific evidence-backed anchor;
3. incremental fact vs predecessor;
4. changed judgment vs predecessor;
5. independent full-schema cardability;
6. representative event date distinct from mere republication date;
7. no broader existing card already represents the new fact;
8. why reinforcement alone is insufficient.

## 6. Stage C lineage lock

Every `accepted_fact_safe` new card emits `related_lineage` with:

- `status: PASS`;
- `relation_type`;
- final baseline `related_ids[]` and provisional current-batch candidate IDs when needed;
- reason;
- fresh follow-up anchor class/anchor when applicable;
- incremental fact and changed judgment when applicable;
- same-event and earliest-date checks;
- rejected relation candidates;
- chronology exception object only when evidence specifically justifies an earlier representative date.

Stage C may not accept a new card whose relation is same-event duplicate, reinforcement-only, or unresolved. `new_unrelated_event` must have empty related targets.

## 7. Prompt 0.4 is addability revalidation

Prompt 0.4 re-runs relation and duplicate screening against the **latest** canonical full and current accepted batch. It does not originate lineage.

It checks exact/canonical URL, normalized title, event fingerprint, broader representative-card coverage, predecessor/successor judgment, fresh anchor, candidate-to-candidate edges, stale republication, and target existence.

Conceptual outcomes:

- `addable_merge_safe_new_unrelated`;
- `addable_merge_safe_distinct_follow_up`;
- `addable_merge_safe_program_lineage`;
- `duplicate_hold_same_event`;
- `existing_reinforcement`;
- `review_pool_deferred_related_uncertain`;
- baseline conflict/update routing where applicable.

This is the distinction: **lineage answers what the event is related to; addability answers whether that already-audited event may be added to the current baseline now.**

## 8. 0.5 freshness backstop

When stronger/earlier evidence changes event identity, 0.5 rechecks earliest same-event date, fresh anchor, existing representative coverage, and whether the item must return upstream as duplicate/reinforcement/update.

Evidence strength cannot launder a selection or lineage defect.

## 9. 0.7 final gate

Final QC verifies relation status, target existence or uniquely resolvable provisional target, self/duplicate links, relation-type consistency, distinct-follow-up anchor/incremental fact/changed judgment, chronology, and current-run scope.

## 10. 0.7C independent challenge

The independent completeness reviewer reopens likely follow-ups incorrectly classified as duplicates, repeated reporting incorrectly promoted to follow-up, omitted reinforcements/corrections, and thematic links incorrectly encoded as lineage.

## 11. 0.8 production-ID resolution

Before merge:

- resolve provisional current-batch relation identifiers to final production IDs;
- preserve baseline IDs;
- write only production IDs into canonical `related[]`;
- keep a resolution ledger;
- fail dangling, self, duplicate, ambiguous, unexplained, or unresolved targets.

Ordinary operations can `related_add`; they do not silently remove existing edges.

## 12. 0.9 production verification

Confirm merged related IDs exist in live data, no provisional identifiers remain, relation metadata survived deployment, and interactive related-card navigation resolves when that surface is available.

## 13. Reinforcement preservation

A duplicate/reinforcement source is not automatically discarded. Preserve unique useful source contributions with representative card ID, source URL, unique fact/quote, and action (`add_source`, `correct_fact`, `expand_context`, `no_unique_value`).

## 14. Stage-exit blocker

A stage required to emit relation metadata but omitting it stops with `BLOCKED_RELATED_LIFECYCLE_SCHEMA_NONCOMPLIANT`. Downstream stages must not reconstruct a missing substantive relation decision from memory.