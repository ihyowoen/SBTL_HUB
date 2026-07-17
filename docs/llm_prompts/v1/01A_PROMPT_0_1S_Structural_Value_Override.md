<!-- STAGE_A_OVERRIDE: STRUCTURAL_NEWS_VALUE_SELECTION_V2 -->
<!-- Effective KST: 2026-07-17 -->
<!-- Supersedes: STRUCTURAL_NEWS_VALUE_SELECTION_V1 override -->

# Prompt 0.1S — Stage A Structural News Value Override V2

Use this prompt together with:

- `docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md`
- `docs/STRUCTURAL_NEWS_VALUE_SELECTION.md`

This is not a replacement for Fact Discipline, lineage rules, duplicate screening, review-pool partitioning, or the state ladder.

It overrides candidate ranking and rescue priority wherever the existing Stage A prompt overweights contracts, capital raises, financing, construction, production, corporate prominence, or formal legal status.

## 1. Four independent judgments — HARD RULE

For every candidate, evaluate four separate objects.

### A. `execution_credibility_gate`

Determine whether the event is real, current, correctly scoped, and supportable.

This is a `PASS | REVIEW | FAIL` gate. It is not the news-value score.

### B. `independent_cardability_gate`

Determine whether the event is a distinct, current, full-schema card rather than background, repetition, watchlist, or reinforcement.

This is also a `PASS | REVIEW | FAIL` gate.

### C. `decision_news_value_score`

Score the change in industrial and decision value from 0 to 100.

Required weighting:

- market structure and competitive position: 0–25
- supply, demand, price, and utilisation: 0–25
- technology, performance, safety, and operational validity: 0–20
- future cash flow and asset value: 0–10
- law, policy, rights, obligations, and market access: 0–10
- systemic scale and coverage: 0–5
- persistence and irreversibility: 0–3
- decision urgency and actionability: 0–2

The first three core industrial dimensions must total a maximum of 70 points.

### D. `publication_urgency`

Record whether action is required immediately, in the near term, or only through monitoring.

Do not combine A, B, C, and D.

## 2. Selector correction

A candidate must not be ranked top solely because it is:

- a signed contract;
- an offtake;
- a capital increase;
- a financing close;
- a factory groundbreaking;
- a production start;
- a first shipment;
- a partnership between large companies;
- an enacted law;
- a court decision;
- an official policy announcement.

A market-operation, supply-demand, price, utilisation, technology, safety, policy, legal, compliance, or operating-data event may be more important even without a conventional corporate transaction.

Accepted non-transaction credibility anchors include:

- official grid or market operating data;
- enacted or formally adopted regulation or standard;
- implementation rule, budget allocation, programme opening, or eligibility guidance;
- regulator enforcement or recall;
- court or tribunal decision;
- official price, production, demand, utilisation, quota, inventory, or trade data;
- verified restart, shutdown, cancellation, bankruptcy, or eligibility change;
- independently validated technology, safety, cost, yield, or performance data.

## 3. Mandatory before–after chain

Each `strict_passed_spec[]` and each high-potential `candidate_review_pool[]` item must state:

- `prior_state`
- `new_verified_fact`
- `changed_judgment`
- `uncertainty_resolved`
- `remaining_uncertainty`

The item must answer:

> What previously reasonable judgment changes because this fact is now known?

If the answer is only "the event progressed" or "the company announced it," the item must not receive high value without a material economic, competitive, supply-demand, technology, legal, or risk consequence.

## 4. Stage A no-fetch boundary

Stage A must still not perform web search or fetch article bodies.

If the available preview indicates high decision value but the exact fact, denominator, date, exception, legal stage, technology-validation stage, or source direction is unresolved:

- do not reject the item merely because there is no signed contract, construction anchor, or final legal instrument;
- place it in `candidate_review_pool[]`;
- set `structural_rescue_required: true`;
- write a specific `structural_rescue_question` for Stage B or an authorised promotion run;
- preserve it under the search-before-delete rule.

Examples of valid rescue questions:

- What period, market and denominator does the reported BESS skip rate use?
- Is the rule proposed, adopted, effective, implemented, or already enforced?
- What exemptions, thresholds, transition rules, or grandfathering provisions apply?
- Is the mine merely permitted to restart, physically restarted, or already producing?
- Is the reported ESS share based on cell demand, energy capacity, shipments, or installations?
- Is the technology result a company target, laboratory test, independent test, customer qualification, or commercial field result?
- Does the court decision bind only the parties or create a wider precedent?
- Which auction tranche makes storage or demand response eligible?

## 5. Required routing logic

| Credibility | Cardability | Decision value | Route |
|---|---|---:|---|
| PASS | PASS | 70–100 | strict pass if all other Stage A gates pass |
| PASS | PASS | 55–69 | strict or candidate review based on evidence and duplicate risk |
| PASS | PASS/REVIEW | 40–54 | lower-priority strict, review, or reinforcement |
| REVIEW | PASS/REVIEW | 55–100 | candidate review pool with mandatory rescue question |
| PASS/REVIEW | REVIEW | any | candidate review, reinforcement, or watchlist |
| FAIL | any | any | item-specific reject/support-only only with valid reason and ledger |

Do not force a minimum number of structural cards. Do not lower evidence standards.

## 6. Required item fields

Each `strict_passed_spec[]` and `candidate_review_pool[]` item must include:

```json
{
  "execution_credibility_gate": {
    "status": "PASS|REVIEW|FAIL",
    "anchor_type": "...",
    "anchor_strength": "strong|moderate|weak|unknown",
    "stage_precision_note": "..."
  },
  "independent_cardability_gate": {
    "status": "PASS|REVIEW|FAIL",
    "distinct_event_or_stage_progression": true,
    "full_schema_viability": "PASS|REVIEW|FAIL",
    "duplicate_or_reinforcement_note": "..."
  },
  "decision_news_value_score": 0,
  "decision_value_breakdown": {
    "market_structure_competition": 0,
    "supply_demand_price_utilisation": 0,
    "technology_performance_safety": 0,
    "cashflow_asset_value": 0,
    "law_policy_market_access": 0,
    "systemic_scale": 0,
    "persistence_irreversibility": 0,
    "decision_urgency_actionability": 0
  },
  "decision_value_classification": "critical_structural|high_decision_value|material_industry_signal|standard_monitoring|context_or_reinforcement|low_independent_value",
  "structural_change_types": [],
  "prior_state": "...",
  "new_verified_fact": "...",
  "changed_judgment": "...",
  "uncertainty_resolved": "...",
  "remaining_uncertainty": "...",
  "denominator_used": "...",
  "denominator_gap": false,
  "publication_urgency": {
    "level": "immediate|near_term|monitor",
    "action_required": "...",
    "decision_deadline": null
  },
  "anti_bias_check": {
    "binding_status_used_as_importance_proxy": false,
    "legal_formality_used_as_importance_proxy": false,
    "headline_amount_used_without_denominator": false,
    "announced_capacity_treated_as_actual_output": false,
    "routine_execution_event_overranked": false
  },
  "structural_rescue_required": false,
  "structural_rescue_question": null,
  "search_before_delete_status": "applied"
}
```

The eight breakdown values must sum to `decision_news_value_score`.

The maximum values must be exactly:

```text
25 + 25 + 20 + 10 + 10 + 5 + 3 + 2 = 100
```

## 7. Technology-evidence caps

Stage A must preserve the evidence-stage risk for later verification.

Default maximum technology scores:

- company target or unsupported claim: 4/20
- laboratory result without independent validation: 7/20
- pilot result without commercial-scale evidence: 11/20
- independent test or customer qualification: 15/20
- commercial-scale or long-duration field evidence: 20/20
- material recall, defect, fire, warranty, or operating-failure evidence: up to 20/20

Required fields:

- `technology_validation_stage`
- `technology_score_cap_applied`
- `technology_validation_gap`

## 8. Legal and policy handling

Policy and legal form is not a substitute for industrial impact.

Classify the stage precisely:

- `stage_0_rhetoric_or_advocacy`
- `stage_1_roadmap_consultation_or_draft_standard`
- `stage_2_bill_or_proposed_rule`
- `stage_3_enacted_law_final_rule_or_adopted_standard`
- `stage_4_implementation_budget_guidance_or_registry`
- `stage_5_enforcement_payment_denial_penalty_or_recall`
- `stage_6_judicial_or_tribunal_interpretation`

Default value caps:

- stage 0: 39/100 unless immediate operative effect or independently verified market consequence exists;
- stage 1: 54/100 unless current administrative, funding, procurement, or market practice changes;
- stage 2: 69/100 unless adoption is highly probable, near, and already causing a material observable effect;
- stages 3–6: no automatic floor or ceiling; score the actual industrial consequence.

### Policy/legal scoring transmission guard

The legal-policy score measures only operative legal force, rights, duties, eligibility, liability, market-access status, and procedural certainty.

Allocate the industrial consequences separately:

- entry barriers, procurement access, concentration, grid access, or revenue design → `market_structure_competition`;
- quotas, tariffs, imports, exports, actual supply, demand, utilisation, or price formation → `supply_demand_price_utilisation`;
- technical standards, qualification, safety, durability, repairability, or technology pathways → `technology_performance_safety`;
- subsidy value, tax burden, compliance cost, financing, liability, margin, or asset value → `cashflow_asset_value`;
- legal force and enforceability itself → `law_policy_market_access`.

Do not double-count the same policy effect.

Every applicable item must preserve or request:

- exact instrument type;
- competent authority;
- procedural stage;
- adoption, publication, effective, and mandatory-application dates;
- covered entities and products;
- exemptions, thresholds, transition, and grandfathering;
- implementation mechanism and administrative readiness;
- non-compliance consequences;
- appeal, litigation, reversal, and precedent risk;
- economic and industrial transmission chain;
- next implementation trigger.

At Stage A, unavailable details must become bounded rescue questions, not invented facts.

## 9. Required Stage A summary fields

Stage A JSON must add:

- `structural_selector_policy_version`
- `structural_selector_policy_file`
- `structural_selector_policy_sha`
- `credibility_cardability_value_urgency_separated`
- `industry_first_weighting_applied`
- `core_industrial_weight_total`
- `decision_value_classification_counts`
- `critical_structural_candidate_ids[]`
- `high_decision_value_candidate_ids[]`
- `high_value_review_pool_ids[]`
- `execution_or_formality_bias_findings[]`
- `technology_validation_gap_ids[]`
- `legal_policy_stage_gap_ids[]`
- `search_before_delete_applied`

Stage A report must include separate ranked lists:

1. industrial-structure priority list;
2. supply-demand-price priority list;
3. technology-safety priority list;
4. legal-policy priority list;
5. execution-event list.

Do not merge them into one undifferentiated ranking.

## 10. Required CSV columns

Add:

- `execution_credibility_gate_status`
- `execution_credibility_anchor_type`
- `independent_cardability_gate_status`
- `decision_news_value_score`
- `decision_value_classification`
- `market_structure_competition_score`
- `supply_demand_price_utilisation_score`
- `technology_performance_safety_score`
- `cashflow_asset_value_score`
- `law_policy_market_access_score`
- `systemic_scale_score`
- `persistence_irreversibility_score`
- `decision_urgency_actionability_score`
- `prior_state`
- `new_verified_fact`
- `changed_judgment`
- `remaining_uncertainty`
- `denominator_used`
- `denominator_gap`
- `technology_validation_stage`
- `legal_policy_stage`
- `structural_rescue_required`
- `structural_rescue_question`
- `anti_bias_status`
- `search_before_delete_status`

## 11. Hard blockers

Block Stage A and do not recommend Stage B when any of the following occurs:

- credibility, cardability, value, and urgency are represented by one score;
- the eight breakdown values do not sum to the decision-value score;
- the three core industrial dimensions do not use 25/25/20 maximum weights;
- a top candidate lacks a before–after chain;
- a contract, financing, capital increase, construction, production, legal, judicial, or policy event is ranked top with no industrial-effect explanation;
- a high-potential market, supply, demand, price, utilisation, technology, safety, policy, or legal event is rejected solely because it lacks a corporate execution anchor;
- a high-value review item lacks a concrete rescue question;
- a technology claim exceeds its evidence-stage score cap;
- a legal or policy item lacks instrument and procedural-stage precision;
- adoption, effectiveness, implementation, and enforcement are conflated;
- a headline market-share, price-effect, or systemic-scale claim lacks a denominator note;
- announced capacity is treated as actual output;
- deletion/support-only is finalised before the applicable search-first process.

Use:

```text
status: BLOCKED_STRUCTURAL_NEWS_VALUE_SELECTION_INVALID
no Stage B recommendation
```

## 12. Required version metadata

Record:

```text
structural_selector_policy_version = STRUCTURAL_NEWS_VALUE_SELECTION_V2
structural_selector_policy_file = docs/STRUCTURAL_NEWS_VALUE_SELECTION.md
credibility_cardability_value_urgency_separated = true
industry_first_weighting_applied = true
core_industrial_weight_total = 70
search_before_delete_applied = true
```

## 13. End condition

Stage A is valid only when:

- existing Stage A validity gates pass;
- credibility, cardability, decision value, and urgency are separated;
- market structure, supply-demand-price, and technology-safety receive the required 70-point core weighting;
- high-value non-transaction events have not been prematurely discarded;
- legal and policy stages are not overstated;
- technology claims are bounded by validation stage;
- review-pool rescue questions are specific;
- the decision ledger accounts for every story;
- no weak item is laundered into strict pass merely to improve topic balance.
