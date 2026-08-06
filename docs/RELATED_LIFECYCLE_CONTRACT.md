# Related Event Lifecycle Contract

Version: `RELATED_LIFECYCLE_V2_20260802`

This contract governs duplicate, follow-up, reinforcement, program-lineage, and unrelated-event decisions from Stage A through Prompt 0.9.

It is aligned with:

- `docs/STRUCTURAL_NEWS_VALUE_SELECTION.md`
- `docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md`

## 1. Core principle

`related[]` is not a topical-similarity field. It represents a direct, auditable event lineage.

A relation is allowed only when at least one of the following is true:

- the new event is a distinct, evidence-backed execution, policy, data, strategic-behavior, technology-commercialisation, or follow-up-probability progression from an existing event;
- the new event is part of the same named project, facility, program, contract, policy instrument, investigation, proceeding, or product-service rollout;
- the existing card is the representative event and the current item contributes unique facts or quotes as reinforcement;
- the cards are explicit predecessor/successor events in a documented sequence.

Shared company, sector, chemistry, geography, theme, or keyword is not enough.

A non-execution follow-up is allowed only when it changes a material judgment about the same represented event and satisfies the direct-lineage, incremental-evidence, independent-cardability, and source requirements in this contract.

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
| `distinct_follow_up` | Yes | fresh V3 anchor class, incremental fact, and predecessor IDs required |
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
- anchor class and factual anchor;
- canonical source URL cluster;
- source story IDs;
- predecessor/successor stage or changed judgment.

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
        "incremental_anchor_class_candidate": "execution_event_anchor|policy_regulatory_anchor|data_financial_anchor|strategic_behavior_anchor|technology_commercialization_anchor|follow_up_probability_anchor|unknown",
        "incremental_anchor_to_verify": ""
      }
    ],
    "duplicate_disposition": "continue|early_duplicate_test|remove_new_card|review",
    "earliest_same_event_date_check": "PRELIMINARY_METADATA_ONLY",
    "fresh_follow_up_anchor_class_candidate": "",
    "fresh_follow_up_anchor_candidate": "",
    "structural_selector_policy_version": "STRUCTURAL_NEWS_VALUE_SELECTION_V3"
  }
}
```

Hard rules:

- Stage A must not lock final `related[]`.
- Clear same-event duplicates must not enter the normal Stage B full-draft queue.
- Probable follow-ups must carry the exact anchor class and incremental anchor question into Stage B.
- Candidate-to-candidate edges must be preserved, not dropped when production IDs do not yet exist.
- A new article date, repeated announcement, or generic management statement is not a fresh anchor.

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
    "fresh_follow_up_anchor_class": "execution_event_anchor|policy_regulatory_anchor|data_financial_anchor|strategic_behavior_anchor|technology_commercialization_anchor|follow_up_probability_anchor|null",
    "fresh_follow_up_anchor": "",
    "incremental_fact_vs_predecessor": "",
    "changed_judgment_vs_predecessor": "",
    "relation_reason": "",
    "rejected_relation_candidates": [],
    "reinforcement_transfer_ledger": [],
    "structural_selector_policy_version": "STRUCTURAL_NEWS_VALUE_SELECTION_V3"
  }
}
```

A `distinct_follow_up` must prove a fresh anchor from one of the V3 classes.

### 5.1 `execution_event_anchor`

Examples:

- MOU → binding contract or investment;
- plan/prequalification → final award or funding decision;
- definitive agreement → closing;
- announced project → financing close, construction, commissioning, or commercial operation;
- pilot → named commercial deployment;
- product/service concept → public launch or measurable customer deployment.

### 5.2 `policy_regulatory_anchor`

Examples:

- proposed rule or bill → enactment or final rule;
- adoption → implementing guidance, registry, eligibility criteria, customs practice, or enforcement;
- general rule → exemption, threshold, transition, grandfathering, denial, penalty, or judgment that changes operative treatment.

### 5.3 `data_financial_anchor`

Examples:

- official operating, shipment, price, inventory, utilisation, safety, or market data materially changes the predecessor assumption;
- filing, earnings call, or analyst Q&A verifies a material delay, scale change, economics change, impairment, customer loss, utilisation shift, or revenue-recognition change for the represented event.

A routine quarter, generic outlook, or repeated estimate is insufficient.

### 5.4 `strategic_behavior_anchor`

Examples:

- documented capex reduction, cancellation, relocation, or reallocation affecting the represented event;
- verified customer, supplier, insourcing, offtake, chemistry, form-factor, or market-priority change;
- management language changes only when tied to concrete comparative facts or actions.

### 5.5 `technology_commercialization_anchor`

Examples:

- prototype → pilot → field demonstration → customer evaluation → qualification → production;
- verified safety, yield, cost, performance, degradation, or manufacturability result changes commercial probability;
- material delay, failed validation, recall, defect, or withdrawal changes the represented pathway.

### 5.6 `follow_up_probability_anchor`

Use when a new verified fact materially changes the probability, scale, timing, economics, legal effect, or risk of the same represented event but is not better classified by another anchor class.

### 5.7 Universal distinct-follow-up requirements

Every `distinct_follow_up`, including a non-execution follow-up, must prove all of the following:

1. direct lineage to named predecessor card(s);
2. a current, specific, source-supported anchor;
3. `incremental_fact_vs_predecessor`;
4. `changed_judgment_vs_predecessor`;
5. independent full-schema cardability;
6. a representative event date distinct from mere republication date;
7. no broader existing card already represents the new fact;
8. a specific reason why reinforcement alone is insufficient.

A newer article date alone is not a fresh anchor. Shared actor, topic, market, or project name alone is not direct lineage.

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
    "fresh_follow_up_anchor_class": "execution_event_anchor|policy_regulatory_anchor|data_financial_anchor|strategic_behavior_anchor|technology_commercialization_anchor|follow_up_probability_anchor|null",
    "fresh_follow_up_anchor": "",
    "incremental_fact_vs_predecessor": "",
    "changed_judgment_vs_predecessor": "",
    "same_event_checked": true,
    "earliest_same_event_date_checked": true,
    "follow_up_date_precedes_predecessor_justification": null,
    "rejected_relation_candidates": [],
    "structural_selector_policy_version": "STRUCTURAL_NEWS_VALUE_SELECTION_V3"
  }
}
```

`follow_up_date_precedes_predecessor_justification` must normally be `null` or absent. It may be populated only when a `distinct_follow_up` uses a representative date earlier than a predecessor date. The object must contain:

```json
{
  "applied": true,
  "predecessor_identifiers": ["final_or_provisional_predecessor_id"],
  "representative_date_basis": "specific explanation of what event the earlier date represents",
  "reason": "specific explanation of why the earlier representative date remains a later distinct follow-up judgment",
  "evidence_source_urls": ["https://..."]
}
```

The exception is target-specific and evidence-backed. A generic explanation, missing source URL, or identifier that does not resolve to the earlier predecessor does not waive the chronology invariant.

Stage C must not accept a new card with:

- `same_event_duplicate`;
- `existing_card_reinforcement`;
- `uncertain_needs_review`;
- a non-empty `related[]` with no relation reason;
- `distinct_follow_up` with no valid fresh anchor class;
- `distinct_follow_up` with no fresh anchor;
- `distinct_follow_up` with no incremental fact or changed judgment versus the predecessor;
- `new_unrelated_event` with a non-empty `related[]`.

## 7. Prompt 0.4 baseline revalidation

Prompt 0.4 must re-run Related screening against the latest baseline and current candidate batch.

Required checks:

- exact and canonical URL;
- normalized title;
- event fingerprint;
- broader representative card coverage;
- predecessor/successor stage or changed judgment;
- fresh V3 anchor class;
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
- whether the candidate has a valid fresh V3 anchor class and supporting fact;
- whether a prior baseline card already represents the event or changed judgment;
- whether the item should return to Stage A/0.4 as reinforcement or duplicate.

## 9. Prompt 0.7 final gate

Final QC must verify:

- `related_lineage.status = PASS`;
- every `related[]` ID exists in the active baseline or current merge batch;
- no self-reference;
- no duplicate related IDs;
- relation type and `related[]` are consistent;
- every `distinct_follow_up` has a valid anchor class, anchor, incremental fact, and changed judgment;
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

## 13. Version and lineage

Every run using V3 structural selection must preserve:

- `related_lifecycle_contract_version: RELATED_LIFECYCLE_V2_20260802`;
- `structural_selector_policy_version: STRUCTURAL_NEWS_VALUE_SELECTION_V3`;
- `fresh_follow_up_anchor_class` for every proposed or accepted `distinct_follow_up`;
- `incremental_fact_vs_predecessor`;
- `changed_judgment_vs_predecessor`.

## 14. Stage-exit hard block

A stage that is required to emit Related lineage but omits it must stop with:

```text
BLOCKED_RELATED_LIFECYCLE_SCHEMA_NONCOMPLIANT
```

A stage must not silently reconstruct substantive relation decisions from downstream memory. Metadata-only materialization is allowed only when the same decision and evidence already exist in a verified upstream object, with a before/after audit log.
