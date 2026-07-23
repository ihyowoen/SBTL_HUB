# Related Event Lifecycle Contract

Version: `RELATED_LIFECYCLE_V1_20260723`

This contract governs duplicate, follow-up, reinforcement, program-lineage, and unrelated-event decisions from Stage A through Prompt 0.9.

## 1. Core principle

`related[]` is not a topical-similarity field. It represents a direct, auditable event lineage.

A relation is allowed only when at least one of the following is true:

- the new event is a distinct execution-stage progression from an existing event;
- the new event is part of the same named project, facility, program, contract, policy instrument, investigation, proceeding, or product-service rollout;
- the existing card is the representative event and the current item contributes unique facts or quotes as reinforcement;
- the cards are explicit predecessor/successor events in a documented sequence.

Shared company, sector, chemistry, geography, theme, or keyword is not enough.

## 2. Canonical relation types

Every relation decision must use one of these values:

- `same_event_duplicate`
- `distinct_follow_up`
- `existing_card_reinforcement`
- `program_lineage`
- `new_unrelated_event`
- `uncertain_needs_review`

Publish rules:

| relation_type | New card allowed? | Required treatment |
|---|---:|---|
| `same_event_duplicate` | No | retain unique sources/facts in reinforcement ledger |
| `distinct_follow_up` | Yes | fresh execution anchor and predecessor IDs required |
| `existing_card_reinforcement` | No | update/reinforce representative card only |
| `program_lineage` | Yes, if independently cardable | direct named-program/project evidence required |
| `new_unrelated_event` | Yes | `related[]` must be empty |
| `uncertain_needs_review` | No | route to bounded Related review |

## 3. Event fingerprint

Related and duplicate screening must compare:

- actor / company / agency;
- asset, project, policy, program, contract, proceeding, or product-service;
- location and jurisdiction;
- event type;
- event date and representative date;
- factual execution anchor;
- canonical source URL cluster;
- source story IDs;
- predecessor/successor stage.

A similarity score may rank candidates, but it may not decide a relation by itself.

## 4. Stage A pre-pass contract

Stage A remains selector-only and may not fetch article bodies. For every strict candidate and bounded review candidate, it must emit:

```json
{
  "related_prepass": {
    "status": "PASS|HOLD",
    "same_event_checked": true,
    "baseline_candidate_ids": [],
    "candidate_spec_ids": [],
    "relation_candidates": [
      {
        "target_type": "baseline_card|current_candidate",
        "target_id": "",
        "relation_type_candidate": "distinct_follow_up|same_event_duplicate|existing_card_reinforcement|program_lineage|new_unrelated_event|uncertain_needs_review",
        "confidence": "high|medium|low",
        "reason": "",
        "incremental_anchor_to_verify": ""
      }
    ],
    "duplicate_disposition": "continue|early_duplicate_test|remove_new_card|review",
    "earliest_same_event_date_check": "PRELIMINARY_METADATA_ONLY",
    "fresh_follow_up_anchor_candidate": ""
  }
}
```

Hard rules:

- Stage A must not lock final `related[]`.
- Clear same-event duplicates must not enter the normal Stage B full-draft queue.
- Probable follow-ups must carry the exact incremental anchor question into Stage B.
- Candidate-to-candidate edges must be preserved, not dropped when production IDs do not yet exist.

## 5. Stage B evidence contract

Stage B must resolve the Stage A pre-pass using body-level or official evidence. Each evidence package and draft must emit:

```json
{
  "related_evidence_review": {
    "same_event_checked": true,
    "earliest_same_event_date_checked": true,
    "earliest_same_event_date": "YYYY-MM-DD|null",
    "earliest_same_event_source_url": "",
    "relation_type": "...",
    "matched_baseline_card_ids": [],
    "matched_candidate_spec_ids": [],
    "fresh_follow_up_anchor": "",
    "incremental_fact_vs_predecessor": "",
    "relation_reason": "",
    "rejected_relation_candidates": [],
    "reinforcement_transfer_ledger": []
  }
}
```

A `distinct_follow_up` must prove a new execution anchor, such as:

- MOU → binding contract or investment;
- plan/prequalification → final award or funding decision;
- definitive agreement → closing;
- announced project → financing close, construction, commissioning, or commercial operation;
- pilot → named commercial deployment;
- proposed rule/bill → enactment, final rule, enforcement, or implementation;
- product/service concept → public launch or measurable customer deployment.

A newer article date alone is not a fresh anchor.

## 6. Stage C lock contract

Stage C must decide fact safety and lock the Related lineage for accepted cards:

```json
{
  "related_lineage": {
    "status": "PASS",
    "relation_type": "distinct_follow_up|program_lineage|new_unrelated_event",
    "related_ids": [],
    "related_candidate_spec_ids": [],
    "reason": "",
    "fresh_follow_up_anchor": "",
    "same_event_checked": true,
    "earliest_same_event_date_checked": true,
    "rejected_relation_candidates": []
  }
}
```

Stage C must not accept a new card with:

- `same_event_duplicate`;
- `existing_card_reinforcement`;
- `uncertain_needs_review`;
- a non-empty `related[]` with no relation reason;
- `distinct_follow_up` with no fresh anchor;
- `new_unrelated_event` with a non-empty `related[]`.

## 7. Prompt 0.4 baseline revalidation

Prompt 0.4 must re-run Related screening against the latest baseline and current candidate batch.

Required checks:

- exact and canonical URL;
- normalized title;
- event fingerprint;
- broader representative card coverage;
- predecessor/successor stage;
- candidate-to-candidate relation edges;
- stale republication without a fresh anchor;
- all baseline `related` IDs exist.

Allowed results:

- `addable_merge_safe_new_unrelated`
- `addable_merge_safe_distinct_follow_up`
- `addable_merge_safe_program_lineage`
- `duplicate_hold_same_event`
- `existing_reinforcement`
- `review_pool_deferred_related_uncertain`

## 8. Prompt 0.5 / 0.5R freshness backstop

Evidence strength must not launder a stale or duplicate selection defect.

When a stronger or earlier source is discovered, Prompt 0.5/0.5R must re-check:

- earliest same-event publication/event date;
- whether the candidate has a fresh execution anchor;
- whether a prior baseline card already represents the event;
- whether the item should return to Stage A/0.4 as reinforcement or duplicate.

## 9. Prompt 0.7 final gate

Final QC must verify:

- `related_lineage.status = PASS`;
- every `related[]` ID exists in the active baseline or current merge batch;
- no self-reference;
- no duplicate related IDs;
- relation type and `related[]` are consistent;
- follow-up dates are not earlier than predecessor dates unless explicitly justified;
- single-source exceptions do not weaken the Related proof requirement.

## 10. Prompt 0.8 production-ID resolution

Before merge:

- resolve all `related_candidate_spec_ids` to final production IDs;
- preserve baseline IDs unchanged;
- write only final production IDs into `related[]`;
- retain the mapping in `related_id_resolution_ledger[]`;
- fail on unresolved spec IDs, dangling IDs, self-links, duplicate links, or invalid relation types;
- run `validation_scripts/related_lifecycle_check.py` against the merged candidate.

## 11. Prompt 0.9 production verification

Production verification must confirm:

- merged `related[]` IDs exist in live data;
- relation metadata survived deployment;
- no unresolved candidate spec IDs remain;
- UI links or related-card rendering resolve to the intended production cards when interactive verification is available.

## 12. Reinforcement preservation

A same-event duplicate is not a throwaway source. Unique facts and quotes must be preserved in:

```json
{
  "reinforcement_transfer_ledger": [
    {
      "representative_card_id": "",
      "source_url": "",
      "unique_fact_or_quote": "",
      "action": "add_source|correct_fact|expand_context|no_unique_value"
    }
  ]
}
```

## 13. Stage-exit hard block

A stage that is required to emit Related lineage but omits it must stop with:

```text
BLOCKED_RELATED_LIFECYCLE_SCHEMA_NONCOMPLIANT
```

A stage must not silently reconstruct substantive relation decisions from downstream memory. Metadata-only materialization is allowed only when the same decision and evidence already exist in a verified upstream object, with a before/after audit log.
