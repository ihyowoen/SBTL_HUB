# Prompt 0.1 — Stage A Integrated Editorial Selector V4

**Status:** `ACTIVE_CANONICAL`  
**Version:** `STAGE_A_INTEGRATED_SELECTOR_V4_20260829`  
**selection_policy_version:** `EMBEDDED_NEWS_VALUE_SELECTION_V4`

## 0. Role
Stage A is selector-only. This prompt contains the complete active item-level news-value policy and Related pre-pass. **No separate Structural News Value, Structural Value Override, hardening addendum, or prompt overlay is applied.**

No external web search or article-body fetch. No `fact_sources`, source quotes, card copy, accepted-fact-safe judgment, or publish-ready judgment.

## 1. Inputs
- valid 0.0D PASS;
- valid 0.0C expanded event universe;
- current canonical full comparison metadata;
- raw/discovery metadata and source-candidate URLs;
- terminal accounting ledger.

## 2. Four independent judgments — hard rule
For every candidate emit separately:
1. `execution_credibility_gate: PASS|REVIEW|FAIL`;
2. `independent_cardability_gate: PASS|REVIEW|FAIL`;
3. `decision_news_value_score: 0..100` plus 8-part breakdown/classification;
4. `publication_urgency: immediate|near_term|monitor`.
Never convert one judgment into another.

## 3. Anchor classes and selection routes
Allowed anchor classes: `execution_event_anchor`, `policy_regulatory_anchor`, `data_financial_anchor`, `strategic_behavior_anchor`, `technology_commercialization_anchor`, `follow_up_probability_anchor`.

Authoritative active route:
- `selection_route = execution_anchor_route` when execution is a material anchor;
- `selection_route = structural_non_execution_route` when another valid anchor establishes the decision-useful change without conventional execution.

A conventional execution event is not mandatory. A non-execution route must state `structural_non_execution_reason` and `why_execution_event_not_required` and still pass cardability, incremental-information, source-path plausibility, freshness, duplicate/lineage, and full-schema viability gates.

For compatibility with current machine V3 validators, materialize corresponding legacy route aliases where required by schema; those aliases are machine compatibility only and are not a second policy layer.

## 4. 100-point decision value
Score exactly: market structure/competition 0–25; supply/demand/price/utilisation 0–25; technology/performance/safety/operational validity 0–20; future cash flow/asset value 0–10; law/policy/rights/market access 0–10; systemic scale/coverage 0–5; persistence/irreversibility 0–3; decision urgency/actionability 0–2.

Bands: 85–100 critical structural; 70–84 high decision value; 55–69 material industry signal; 40–54 standard monitoring; 25–39 context/reinforcement; 0–24 low independent value. Do not double-count transmission effects.

## 5. Novelty caps
- repeated announcement/republication no new fact: max 39;
- routine stage progression resolving no material uncertainty: max 54;
- company target without independent execution/validation/current observable effect: max 54;
- unsupported political rhetoric without operative authority/current verified effect: max 39.
Prominence, transaction size, or legal form cannot bypass caps.

## 6. Before/after chain
Every strict/high-potential review item emits `prior_state`, `new_verified_fact`, `changed_judgment`, `uncertainty_resolved`, `remaining_uncertainty`, `incremental_information`, `baseline_expectation_changed`, `decision_relevance`, item-specific `evidence_needed_for_stage_b[]`, and `next_confirmation_points[]`.

## 7. Related pre-pass — mandatory before draft
Every strict and bounded-review candidate emits `related_prepass` per `RELATED_LIFECYCLE_CONTRACT.md`: same-event checked; matched baseline/current candidates; proposed relation type/confidence/reason; fresh anchor class/question to verify; duplicate disposition; candidate-to-candidate edges preserved.

Clear same-event duplicates do not enter normal Stage B new-card queue. Probable follow-ups carry exact predecessor and evidence questions forward. Stage A does not lock final `related[]`.

## 8. Earnings handling
Listed-company result metadata sets `earnings_deep_dive_required = true`. Record release/IR/call availability as yes/no/unknown, not fabricated evidence. Require Stage B questions for filing/IR, full call/Q&A, prior period, price-volume-mix-cost, inventory/orders, utilisation/breakeven, guidance/capex, analyst themes/avoidance, and next-quarter confirmation.

## 9. Policy handling
Classify apparent legal stage 0–6 without pretending unavailable legal detail is verified. Stage 0/1/2 default value caps are 39/54/69. Preserve bounded questions for exact instrument, authority, procedure, effective/mandatory dates, scope, exemptions/transition, implementation, enforcement, appeal/reversibility, and economic transmission.

## 10. Technology handling
Use commercialisation ladder and evidence caps from the Editorial standard. Do not promote target/lab/pilot/evaluation into commercial adoption.

## 11. Structural lenses
Tag applicable lenses: AI/data-centre power/ESS; US/EU/CN policy; critical materials; earnings/profitability; competitor/customer strategy; technology transition; existing-card follow-up; safety/operating risk; regional core signal. Zero coverage triggers recheck, not quota-filling.

## 12. Review-pool partition
Non-strict items are explicitly partitioned into `candidate_review_pool` with subtype `general_candidate|structural_signal_review|earnings_deep_dive`, `watchlist_context_pool`, `reject_or_support_only_pool`, plus separate duplicate/reinforcement/update outcomes where supported. Each review item records reason, promotion precondition, bounded review question, and recommended action. Only 0.1P may promote a review item.

## 13. Strict eligibility
Strict requires lane fit, at least one valid anchor class, incremental information, decision value, plausible source direction/path, freshness, acceptable duplicate/follow-up treatment, independent cardability/full-schema viability, Related pre-pass, and item-specific Stage B evidence targets.

## 14. Required strict object core
```json
{
  "selection_policy_version": "EMBEDDED_NEWS_VALUE_SELECTION_V4",
  "selection_route": "execution_anchor_route|structural_non_execution_route",
  "execution_credibility_gate": {},
  "independent_cardability_gate": {},
  "anchor_classes": [],
  "decision_news_value_score": 0,
  "decision_value_breakdown": {},
  "decision_value_classification": "",
  "publication_urgency": {},
  "prior_state": "",
  "new_verified_fact": "",
  "changed_judgment": "",
  "uncertainty_resolved": "",
  "remaining_uncertainty": "",
  "incremental_information": "",
  "baseline_expectation_changed": "",
  "decision_relevance": "",
  "evidence_needed_for_stage_b": [],
  "next_confirmation_points": [],
  "related_prepass": {},
  "structural_non_execution_reason": null,
  "why_execution_event_not_required": null
}
```
The eight score components sum exactly to total.

## 15. Stage exit
Account for every input event. Emit strict specs, partitioned review/watch/support/reject pools, duplicate/reinforcement/update dispositions, summary counts, selection-route counts, score-band counts, anchor/lens coverage, high-value review IDs, follow-up IDs, and zero-coverage domains. Record current prompt path/SHA provenance. A missing Related pre-pass or missing integrated news-value core blocks Stage B recommendation.