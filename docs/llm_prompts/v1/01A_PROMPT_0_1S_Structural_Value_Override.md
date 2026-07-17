<!-- STAGE_A_OVERRIDE: STRUCTURAL_NEWS_VALUE_SELECTION_V1 -->
<!-- Effective KST: 2026-07-17 -->

# Prompt 0.1S — Stage A Structural News Value Override

Use this prompt together with:

- `docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md`
- `docs/STRUCTURAL_NEWS_VALUE_SELECTION.md`

This is not a replacement for Fact Discipline, lineage rules, duplicate screening, review-pool partitioning, or the state ladder.

It overrides only candidate ranking and rescue priority where the existing Stage A prompt overweights contracts, financing, construction, production, or other easy-to-verify execution events.

## 1. Mandatory distinction

For every candidate, evaluate two independent objects.

### A. `execution_credibility_gate`

Determine whether the event is real, current, correctly scoped, and supportable.

This is a pass/review/fail gate. It is not the news-value score.

### B. `structural_news_value_score`

Score the industry impact from 0 to 100 using:

- market structure and revenue formation: 0–25
- price, cost, margin, and project economics: 0–20
- demand, application, and chemistry mix: 0–15
- regulation, compliance, safety, and market access: 0–15
- systemic scale: 0–15
- persistence and irreversibility: 0–10

Do not combine A and B.

## 2. Selector correction

A candidate must not be ranked top solely because it is:

- a signed contract
- an offtake
- a capital increase
- a financing close
- a factory groundbreaking
- a production start
- a first shipment
- a partnership between large companies

A policy, data, market-operation, price, demand, technology, safety, legal, or compliance event may be more important even without a conventional corporate execution format.

Accepted non-transaction credibility anchors include:

- official grid or market operating data
- enacted or formally adopted regulation or standard
- regulator enforcement or recall
- court decision
- official price, production, demand, utilisation, quota, inventory, or trade data
- verified restart, shutdown, cancellation, bankruptcy, or eligibility change
- independently validated technology cost/performance data

## 3. Stage A no-fetch boundary

Stage A must still not perform web search or fetch article bodies.

If the available preview indicates high structural value but the exact fact, denominator, date, exception, policy stage, or source direction is unresolved:

- do not reject the item merely because there is no signed contract or construction anchor;
- place it in `candidate_review_pool[]`;
- set `structural_rescue_required: true`;
- write a specific `structural_rescue_question` for Stage B or an authorised promotion run;
- preserve it under the search-before-delete rule.

Examples of valid rescue questions:

- What period and denominator does the reported BESS skip rate use?
- Does the adopted EU standard create an immediate legal obligation or only a presumption of conformity?
- Is the mine restart permitted, physically commenced, or already producing?
- Is the 15% ESS share based on cell demand, energy capacity, shipments, or installations?
- Which auction tranche makes storage or demand response eligible?

## 4. Required routing logic

| Credibility | Structural score | Route |
|---|---:|---|
| PASS | 65–100 | strict pass if all other Stage A gates pass |
| REVIEW | 65–100 | candidate review pool with mandatory rescue question |
| PASS | 50–64 | strict or candidate review depending on evidence/full-schema risk |
| REVIEW | 35–64 | candidate review or watchlist |
| PASS/REVIEW | below 35 | lower priority, watchlist, reinforcement, support-only, or reject as appropriate |
| FAIL | any | item-specific reject/support-only only with valid reason and ledger |

Do not force a minimum number of structural cards. Do not lower evidence standards.

## 5. Required item fields

Each `strict_passed_spec[]` and `candidate_review_pool[]` item must include:

```json
{
  "execution_credibility_gate": {
    "status": "PASS|REVIEW|FAIL",
    "anchor_type": "...",
    "anchor_strength": "strong|moderate|weak|unknown",
    "stage_precision_note": "..."
  },
  "structural_news_value_score": 0,
  "structural_value_breakdown": {
    "market_structure": 0,
    "price_cost_margin": 0,
    "demand_chemistry_shift": 0,
    "regulation_compliance_safety": 0,
    "systemic_scale": 0,
    "persistence_irreversibility": 0
  },
  "structural_priority": "top_structural_priority|high_structural_priority|standard_structural_priority|watchlist_or_context|low_independent_value",
  "structural_change_types": [],
  "structural_value_reason": "...",
  "anti_execution_bias_check": {
    "binding_status_used_as_importance_proxy": false,
    "headline_amount_used_without_denominator": false,
    "routine_execution_event_overranked": false
  },
  "structural_rescue_required": false,
  "structural_rescue_question": null,
  "search_before_delete_status": "applied"
}
```

The six breakdown values must sum to `structural_news_value_score`.

## 6. Required Stage A summary fields

Stage A JSON must add:

- `structural_selector_policy_version`
- `structural_selector_policy_file`
- `structural_selector_policy_sha`
- `execution_credibility_separated_from_news_value`
- `structural_priority_counts`
- `top_structural_candidate_ids[]`
- `high_structural_candidate_ids[]`
- `high_structural_review_pool_ids[]`
- `execution_bias_findings[]`
- `search_before_delete_applied`

Stage A report must include two separate ranked lists:

1. structural-value priority list
2. execution-event list

Do not merge them into one ranking.

## 7. Required CSV columns

Add:

- `execution_credibility_gate_status`
- `execution_credibility_anchor_type`
- `structural_news_value_score`
- `structural_priority`
- `structural_change_types`
- `structural_value_reason`
- `structural_rescue_required`
- `structural_rescue_question`
- `anti_execution_bias_status`
- `search_before_delete_status`

## 8. Hard blockers

Block Stage A and do not recommend Stage B when any of the following occurs:

- execution credibility and news value are represented by one score;
- a top candidate lacks a structural-value breakdown;
- a contract, financing, capital increase, construction, or production event is ranked top with no structural explanation;
- a high-potential policy, price, demand, market-operation, technology, safety, or compliance event is rejected solely because it lacks a corporate execution anchor;
- a high-structural-value review item lacks a concrete rescue question;
- a headline market share, price effect, or systemic-scale claim lacks a denominator note;
- deletion/support-only is finalised before the applicable search-first process.

Use:

```text
status: BLOCKED_STRUCTURAL_NEWS_VALUE_SELECTION_INVALID
no Stage B recommendation
```

## 9. Required version metadata

Record:

```text
structural_selector_policy_version = STRUCTURAL_NEWS_VALUE_SELECTION_V1
structural_selector_policy_file = docs/STRUCTURAL_NEWS_VALUE_SELECTION.md
execution_credibility_separated_from_news_value = true
search_before_delete_applied = true
```

## 10. End condition

Stage A is valid only when:

- existing Stage A validity gates pass;
- execution credibility is separated from structural value;
- high-value non-transaction events have not been prematurely discarded;
- review-pool rescue questions are specific;
- the decision ledger accounts for every story;
- no weak item is laundered into strict pass merely to improve topic balance.
