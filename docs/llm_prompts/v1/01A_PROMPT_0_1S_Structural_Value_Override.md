<!-- STAGE_A_OVERRIDE: STRUCTURAL_NEWS_VALUE_SELECTION_V3 -->
<!-- Effective KST: 2026-08-02 -->
<!-- Supersedes: STRUCTURAL_NEWS_VALUE_SELECTION_V2 override -->
<!-- REPLACE_ALL_CLEAN_VERSION: true -->

# Prompt 0.1S — Stage A Structural News Value Override V3

Use this prompt together with:

- `docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md`
- `docs/STRUCTURAL_NEWS_VALUE_SELECTION.md`
- the current source universe;
- the active baseline.

This override does not replace Fact Discipline, duplicate screening, lineage, review-pool partitioning, state-ladder, or source-diversity rules.

It overrides any Stage A rule that:

- treats a conventional execution event as the sole strict-pass anchor;
- ranks contracts, capital raises, financing, construction, production, corporate prominence, or legal form as a proxy for importance;
- blocks high-value data, policy, strategic, technology, earnings, or follow-up signals solely for lacking a transaction;
- treats an existing actor, asset, project, or policy as automatically duplicate;
- closes Stage A without structural-domain coverage accounting.

---

## 1. Four independent judgments — HARD RULE

For every candidate, produce separate:

1. `execution_credibility_gate`
2. `independent_cardability_gate`
3. `decision_news_value_score`
4. `publication_urgency`

Never collapse them.

### Required 100-point weighting

- market structure and competitive position: 0–25
- supply, demand, price, and utilisation: 0–25
- technology, performance, safety, and operational validity: 0–20
- future cash flow and asset value: 0–10
- law, policy, rights, obligations, and market access: 0–10
- systemic scale and coverage: 0–5
- persistence and irreversibility: 0–3
- decision urgency and actionability: 0–2

The first three dimensions total 70 points.

---

## 2. Multi-anchor strict eligibility

For every candidate, classify one or more:

- `execution_event_anchor`
- `policy_regulatory_anchor`
- `data_financial_anchor`
- `strategic_behavior_anchor`
- `technology_commercialization_anchor`
- `follow_up_probability_anchor`

A candidate may enter `strict_passed_spec[]` only when all are true:

1. SBTL_HUB lane fit;
2. at least one valid anchor class;
3. incremental information;
4. structural or decision value;
5. plausible source-direction compatibility;
6. acceptable freshness and staleness treatment;
7. acceptable duplicate, follow-up, or reinforcement treatment;
8. independent full-schema viability;
9. plausible Stage B source path.

**Do not require `execution_event_anchor` when another valid anchor class establishes the current decision-useful change.**

Do not lower evidence standards.

### Routing matrix

| Credibility | Cardability | Decision value | Route |
|---|---|---:|---|
| PASS | PASS | 70–100 | strict pass if all other Stage A gates pass |
| PASS | PASS | 55–69 | strict or candidate review based on evidence and duplicate risk |
| PASS | PASS/REVIEW | 40–54 | lower-priority strict, review, or reinforcement |
| REVIEW | PASS/REVIEW | 55–100 | candidate or structural review with mandatory rescue question |
| PASS/REVIEW | REVIEW | any | candidate review, earnings deep dive, reinforcement, or watchlist |
| FAIL | any | any | item-specific reject/support-only with reason and ledger |

Do not force cards to improve topic balance.

### Novelty classification caps — HARD RULE

Cap total score and classification as follows:

- repeated announcement or republication with no new fact: maximum 39 and `context_or_reinforcement`;
- routine stage progression resolving no material uncertainty: maximum 54 and `standard_monitoring`;
- company target without independent execution, validation, or current observable market effect: maximum 54 and `standard_monitoring`;
- unsupported political rhetoric without immediate operative authority or verified current market effect: maximum 39 and `context_or_reinforcement`.

Do not allow other score components or corporate prominence to bypass these caps.

---

## 3. Structural Value Override

Set `structural_value_override_applied: true` when a candidate lacks a conventional execution event but materially changes one or more of:

- cash flow or asset value;
- legal rights, duties, eligibility, liability, or market access;
- supply, demand, price, cost, inventory, utilisation, or mix;
- customer or competitor behavior;
- technology pathway, safety, yield, qualification, or commercial timing;
- existing-event probability, scale, economics, or schedule;
- economic-security, localisation, or strategic-supply-chain position.

Required fields:

- `structural_value_override_reason`
- `anchor_classes[]`
- `incremental_information`
- `decision_relevance`
- `baseline_expectation_changed`
- `evidence_needed_for_stage_b[]`
- `next_confirmation_points[]`
- `why_execution_event_not_required`

When `structural_value_override_applied: true`:

- `structural_value_override_reason` must be non-empty and item-specific;
- `anchor_classes[]` must contain at least one valid non-execution anchor class;
- `evidence_needed_for_stage_b[]` must be a non-empty array of item-specific verification targets;
- every evidence entry must identify both (a) the source, document, dataset, transcript, filing, technical test, or independent-reporting class and (b) the exact claim, metric, stage, date, or uncertainty to verify;
- generic placeholders such as `official sources`, `company materials`, `media reports`, `additional confirmation`, `more evidence`, or equivalent wording are invalid;
- `why_execution_event_not_required` must be non-empty and explain why the verified change is independently decision-useful without a conventional execution event;
- `next_confirmation_points[]` must identify measurable events or metrics that would confirm, weaken, or invalidate the interpretation.

A false override may use empty or null values for override-only fields.

Do not use override for generic forecasts, unsupported commentary, repeated reporting, or direct-benefit claims without evidence.

---

## 4. Mandatory before–after chain

Every strict and high-potential review item must state:

- `prior_state`
- `new_verified_fact`
- `changed_judgment`
- `uncertainty_resolved`
- `remaining_uncertainty`
- `incremental_information`
- `baseline_expectation_changed`

Answer:

> What previously reasonable judgment changes because this fact is now known?

“An event progressed” is not sufficient without a material economic, competitive, demand, supply, price, technology, legal, strategic, or risk consequence.

---

## 5. Mandatory structural lenses

Inspect and tag every applicable item against:

1. `ai_data_center_power_and_ess_demand`
2. `us_policy_and_supply_chain_rules`
3. `eu_policy_and_supply_chain_rules`
4. `china_policy_and_supply_chain_rules`
5. `critical_materials_rare_earths_graphite_economic_security`
6. `price_earnings_profitability`
7. `competitor_strategy`
8. `customer_strategy`
9. `technology_transition_commercialization`
10. `existing_card_follow_up`
11. `safety_quality_operating_risk`
12. `regional_core_signal`

These are discovery obligations, not quotas.

If a domain is zero, Stage A must recheck review, watchlist, support, dropped, and full-input stories before closing it.

---

## 6. Earnings candidate handling

When preview or metadata indicates a listed-company result:

- classify `data_financial_anchor`;
- set `earnings_deep_dive_required: true`;
- place the candidate in strict or `earnings_deep_dive[]` according to current Stage A evidence and cardability;
- do not imply that release-only information proves customer demand, utilisation recovery, profitability durability, or capex strategy.

Stage B rescue questions must cover, where applicable:

- filing and IR deck;
- prepared remarks;
- complete call or transcript;
- analyst Q&A;
- prior-quarter language;
- price/volume/mix/cost bridge;
- customer inventory and actual orders;
- utilisation and breakeven;
- guidance change;
- capex change;
- repeated analyst concerns;
- answer avoidance;
- next-quarter confirmation points.

Required Stage A fields:

- `earnings_deep_dive_required`
- `earnings_release_available`
- `ir_deck_available`
- `call_or_transcript_expected`
- `qna_status: not_checked_stage_a | not_applicable`
- `prior_period_comparison_required`
- `earnings_rescue_questions[]`

For listed-company results:

- `earnings_deep_dive_required: true`;
- `qna_status: not_checked_stage_a`;
- `prior_period_comparison_required: true`;
- availability fields must not be `not_applicable`;
- unresolved items must be listed in `earnings_rescue_questions[]`.

Only non-earnings candidates may use `false` and `not_applicable`.

---

## 7. Follow-up and duplicate handling

Do not mark duplicate solely because actor, asset, project, technology, or policy already exists.

Check whether the new event changes:

- stage;
- legal rights or duties;
- approval or financing;
- scale or schedule;
- customer or supplier;
- price or economics;
- technical maturity;
- risk probability;
- earnings contribution;
- delay, suspension, reduction, or cancellation.

Required fields:

- `baseline_relation`
- `baseline_follow_up_relation`
- `incremental_information`
- `follow_up_probability_changed`
- `predecessor_card_ids[]`
- `next_confirmation_points[]`

A later article with the same facts is reinforcement. A changed stage or judgment may be a standalone follow-up.

---

## 8. Review-pool partition

Use only the supported top-level Stage A partitions:

- `candidate_review_pool[]`
- `watchlist_context_pool[]`
- `reject_or_support_only_pool[]`

`existing_reinforcement[]`, `support_source_only[]`, and `rejected[]` remain separate non-review outcomes.

`structural_signal_review` and `earnings_deep_dive` are not standalone top-level partition arrays. They are `review_pool_subtype` values inside `candidate_review_pool[]` so the existing promotion workflow remains authoritative.

For every non-strict review item include:

- `review_pool_partition`
- `review_pool_subtype`
- `review_pool_partition_reason`
- `promotion_precondition`
- `bounded_review_question`
- `recommended_next_action`

For `review_pool_partition: candidate_review_pool`, set exactly one subtype:

- `general_candidate`
- `structural_signal_review`
- `earnings_deep_dive`

High-value unresolved structural items use `structural_signal_review`; listed-company results awaiting full call/Q&A or prior-period comparison use `earnings_deep_dive`. Both remain promotable only through the existing candidate-review authorization path.

High-value unresolved structural items require:

- `structural_rescue_required: true`
- a concrete `structural_rescue_question`

Stage A remains no-fetch. Rescue means bounded-question capture and preservation, not external search.

---

## 9. Technology evidence caps

Preserve:

- company target or unsupported claim: max 4/20
- laboratory result without independent validation: max 7/20
- pilot without commercial-scale evidence: max 11/20
- independent test or customer qualification: max 15/20
- commercial-scale or long-duration field evidence: max 20/20
- material recall, defect, fire, warranty, or operating-failure evidence: max 20/20

Required:

- `technology_validation_stage`
- `technology_score_cap_applied`
- `technology_validation_gap`

---

## 10. Legal and policy handling

Classify:

- `stage_0_rhetoric_or_advocacy`
- `stage_1_roadmap_consultation_or_draft_standard`
- `stage_2_bill_or_proposed_rule`
- `stage_3_enacted_law_final_rule_or_adopted_standard`
- `stage_4_implementation_budget_guidance_or_registry`
- `stage_5_enforcement_payment_denial_penalty_or_recall`
- `stage_6_judicial_or_tribunal_interpretation`

Default caps:

- Stage 0: 39
- Stage 1: 54
- Stage 2: 69
- Stages 3–6: no automatic floor or ceiling

At Stage A, unavailable legal details become bounded rescue questions.

Do not conflate proposal, adoption, publication, effectiveness, mandatory application, implementation, enforcement, or judicial review.

---

## 11. Required item object

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
  "anchor_classes": [],
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
  "decision_value_classification": "",
  "structural_value_lenses": [],
  "structural_value_override_applied": false,
  "structural_value_override_reason": null,
  "evidence_needed_for_stage_b": [],
  "why_execution_event_not_required": null,
  "prior_state": "",
  "new_verified_fact": "",
  "changed_judgment": "",
  "uncertainty_resolved": "",
  "remaining_uncertainty": "",
  "incremental_information": "",
  "baseline_expectation_changed": "",
  "decision_relevance": "",
  "denominator_used": "",
  "denominator_gap": false,
  "publication_urgency": {
    "level": "immediate|near_term|monitor",
    "action_required": "",
    "decision_deadline": null
  },
  "baseline_follow_up_relation": "",
  "next_confirmation_points": [],
  "portfolio_coverage_contribution": [],
  "earnings_deep_dive_required": "true_for_listed_company_results|false_otherwise",
  "earnings_release_available": "yes|no|unknown|not_applicable",
  "ir_deck_available": "yes|no|unknown|not_applicable",
  "call_or_transcript_expected": "yes|no|unknown|not_applicable",
  "qna_status": "not_checked_stage_a_for_earnings|not_applicable_otherwise",
  "prior_period_comparison_required": "true_for_listed_company_results|false_otherwise",
  "earnings_rescue_questions": [],
  "anti_bias_check": {
    "binding_status_used_as_importance_proxy": false,
    "legal_formality_used_as_importance_proxy": false,
    "headline_amount_used_without_denominator": false,
    "announced_capacity_treated_as_actual_output": false,
    "routine_execution_event_overranked": false,
    "conventional_execution_event_required_without_reason": false
  },
  "structural_rescue_required": false,
  "structural_rescue_question": null,
  "search_before_delete_status": "applied"
}
```

The eight score values must sum to the total.

---

## 12. Stage A summary requirements

Add:

- `structural_selector_policy_version`
- `structural_selector_policy_file`
- `structural_selector_policy_sha`
- `credibility_cardability_value_urgency_separated`
- `industry_first_weighting_applied`
- `core_industrial_weight_total`
- `multi_anchor_class_model_applied`
- `mandatory_structural_lenses_applied`
- `anchor_class_counts`
- `structural_lens_coverage_counts`
- `decision_value_classification_counts`
- `critical_structural_candidate_ids[]`
- `high_decision_value_candidate_ids[]`
- `high_value_review_pool_ids[]`
- `structural_signal_review_ids[]`
- `earnings_deep_dive_ids[]`
- `follow_up_candidate_ids[]`
- `zero_coverage_domains[]`
- `execution_or_formality_bias_findings[]`
- `technology_validation_gap_ids[]`
- `legal_policy_stage_gap_ids[]`
- `search_before_delete_applied`

Produce separate ranked lists for:

1. market structure and competition;
2. supply-demand-price-utilisation;
3. technology-safety-operations;
4. legal-policy;
5. price-earnings-profitability;
6. AI power and ESS;
7. economic security and strategic materials;
8. execution events;
9. follow-ups.

---

## 13. Portfolio coverage audit

Stage A must produce or prepare:

- `portfolio_coverage_audit.json`
- `structural_lens_coverage.csv`
- `zero_coverage_explanation.json`
- `follow_up_tracker.json`
- `earnings_call_qna_ledger.json`
- `review_pool_repromotion_ledger.json`

A zero domain requires one reason:

- `no_material_event_found_after_full_scan`
- `candidate_found_evidence_insufficient`
- `existing_card_reinforcement_only`
- `watchlist_trigger_pending`
- `selector_bias_detected_and_reopened`
- `source_universe_gap`
- `earnings_call_or_qna_gap`
- `regional_source_gap`

Do not force cards to fill a domain.

---

## 14. Required decision-ledger columns

Add:

- `anchor_classes`
- `news_value_basis`
- `structural_value_lenses`
- `structural_value_override_applied`
- `structural_value_override_reason`
- `evidence_needed_for_stage_b`
- `why_execution_event_not_required`
- `incremental_information`
- `decision_relevance`
- `baseline_expectation_changed`
- `follow_up_relation`
- `next_confirmation_points`
- `portfolio_coverage_contribution`
- `earnings_deep_dive_required`
- `qna_status`
- `review_pool_subtype`
- `review_pool_repromotion_precondition`

Retain all V2 score, before–after, denominator, technology, legal-policy, urgency, rescue, and anti-bias columns.

---

## 15. Hard blockers

Use:

```text
status: BLOCKED_STRUCTURAL_NEWS_VALUE_SELECTION_INVALID
no Stage B recommendation
```

Block if:

- the four judgments are collapsed;
- score components do not sum correctly;
- 25/25/20 core weights are changed;
- a top item lacks the before–after chain;
- transaction, execution, legal form, or company prominence is the importance explanation;
- a high-potential structural item is rejected only for lacking a conventional execution event;
- `structural_value_override_applied: true` is used while `evidence_needed_for_stage_b` is not an array, is empty, contains blank, generic, placeholder, duplicate-only, or non-item-specific entries, fails to identify both the evidence target and the exact claim or uncertainty to verify, or while `why_execution_event_not_required` is missing, null, generic, or non-specific;
- a high-value review item lacks a rescue question;
- technology score exceeds evidence-stage cap;
- legal stage or date is overstated;
- a legal-policy candidate lacks the exact instrument, competent authority, or procedural status required by the legal-policy questions;
- proposal, adoption, publication, effectiveness, mandatory application, implementation, enforcement, or judicial review is conflated;
- announced capacity is treated as output;
- scale or price claim lacks a denominator note;
- an earnings candidate is completed without a call/Q&A status;
- a listed-company earnings candidate uses `qna_status: not_applicable` or omits availability, prior-period, or rescue fields;
- a novelty-capped item exceeds its total-score or classification cap;
- a material follow-up is treated as duplicate without incremental analysis;
- a mandatory structural domain is zero without recheck and explanation;
- `structural_signal_review` or `earnings_deep_dive` is emitted as a standalone top-level partition instead of a `candidate_review_pool` subtype;
- a candidate-review item lacks a valid `review_pool_subtype`;
- deletion/support-only is finalised before the applicable search-first process.

Required summary validators:

- `structural_value_selector_status`
- `portfolio_coverage_audit_status`
- `earnings_call_qna_audit_status`
- `follow_up_repromotion_audit_status`
- `execution_event_bias_audit_status`
- `content_depth_audit_status`

---

## 15A. Signal assignment

Assign `signal = top | high | mid` only after the four independent judgments.

- `top`: 85–100, or 70–84 with exceptional urgency and strong evidence;
- `high`: 70–84, or 55–69 with material lane impact and strong evidence;
- `mid`: 40–69 depending on scope, or a credible independently cardable execution event below 40 with narrow value when all novelty, evidence, and workflow gates pass.

No execution, legal, corporate, or earnings form creates a signal level by itself.

---

## 16. Required version metadata

```text
structural_selector_policy_version = STRUCTURAL_NEWS_VALUE_SELECTION_V3
structural_selector_policy_file = docs/STRUCTURAL_NEWS_VALUE_SELECTION.md
credibility_cardability_value_urgency_separated = true
industry_first_weighting_applied = true
core_industrial_weight_total = 70
multi_anchor_class_model_applied = true
mandatory_structural_lenses_applied = true
earnings_call_qna_rule_applied = true
follow_up_probability_review_applied = true
portfolio_coverage_audit_applied = true
search_before_delete_applied = true
```

---

## 17. End condition

Stage A is valid only when:

- all existing Stage A validity gates pass;
- all stories are ledger-accounted;
- credibility, cardability, value, and urgency are separate;
- the 70-point industrial weighting is preserved;
- multi-anchor eligibility is applied;
- high-value non-transaction signals are preserved;
- every applied Structural Value Override has a concrete Stage B evidence path and an item-specific explanation for why execution is not required;
- legal stages are not overstated;
- technology claims are evidence-bounded;
- earnings candidates are routed for full-call review;
- material follow-ups are not suppressed as duplicates;
- mandatory structural domains are audited;
- review rescue questions are specific;
- no weak item is laundered into strict pass to fill a topic quota.
