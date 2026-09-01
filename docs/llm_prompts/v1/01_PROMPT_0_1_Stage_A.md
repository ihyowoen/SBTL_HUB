# Prompt 0.1 — Stage A Integrated Editorial Selector V4

**Status:** `ACTIVE_CANONICAL`  
**Version:** `STAGE_A_INTEGRATED_SELECTOR_V4_20260901`  
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

For systemic scale/coverage, state `systemic_scale_denominator` when a defensible denominator exists. If no defensible denominator exists, set `systemic_scale_denominator = null`, record a non-empty `denominator_gap`, and cap `decision_value_breakdown.systemic_scale` at **2/5**. A 3–5 point systemic score without a defensible denominator is invalid.

Bands: 85–100 critical structural; 70–84 high decision value; 55–69 material industry signal; 40–54 standard monitoring; 25–39 context/reinforcement; 0–24 low independent value. Do not double-count transmission effects.

### 4.1 Machine-required cap metadata
Every strict item must emit all three fields below so the hard caps are machine-verifiable rather than prose-only:

- `technology_evidence_level`: `not_applicable|company_target_or_unsupported_claim|laboratory_unvalidated|pilot_precommercial|independent_test_or_customer_qualification|commercial_scale_or_long_duration_field|material_failure_evidence`;
- `policy_stage`: `null` or integer `0..6`; a `policy_regulatory_anchor` requires `0..6`;
- `novelty_cap_basis`: `none|repeated_announcement_no_new_fact|routine_progression_no_material_uncertainty|company_target_without_validation_or_effect|unsupported_political_rhetoric`.

Technology component ceilings are hard: `not_applicable` 0/20, company target/unsupported 4/20, laboratory-unvalidated 7/20, pilot/precommercial 11/20, independent test/customer qualification 15/20, commercial-scale/long-duration field or material failure evidence up to 20/20.

Policy-stage total ceilings are hard: stage 0 max 39, stage 1 max 54, stage 2 max 69; stages 3–6 have no automatic total ceiling.

Novelty total ceilings are hard: repeated announcement/no new fact max 39; routine progression/no material uncertainty max 54; company target without independent validation/current observable effect max 54; unsupported political rhetoric max 39. Use `none` only when none of those cap conditions applies.

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

The active Stage A machine shape is:

```json
{
  "status": "PASS|HOLD",
  "same_event_checked": true,
  "matched_baseline_candidate_ids": [],
  "matched_current_batch_candidate_ids": [],
  "relation_candidates": [
    {
      "target_candidate_id": "",
      "proposed_relation_type": "same_event_duplicate|existing_card_reinforcement|distinct_follow_up|program_lineage|new_unrelated_event|uncertain_needs_review",
      "confidence": "low|medium|high or numeric 0..1",
      "reason": "",
      "anchor_class_to_verify": null,
      "incremental_anchor_question": null
    }
  ],
  "duplicate_disposition": "no_duplicate_found|same_event_duplicate|existing_card_reinforcement|uncertain_needs_review",
  "earliest_same_event_check_status": "PASS|HOLD",
  "fresh_anchor_questions": []
}
```

**Strict queue rule:** every object placed in `strict_passed_spec[]` must have `related_prepass.status = PASS`, `same_event_checked = true`, `earliest_same_event_check_status = PASS`, and `duplicate_disposition = no_duplicate_found`. `HOLD`, `same_event_duplicate`, `existing_card_reinforcement`, and `uncertain_needs_review` belong outside the strict Stage B queue.

When `duplicate_disposition = no_duplicate_found`, `relation_candidates[]` must not contain `same_event_duplicate`, `existing_card_reinforcement`, or `uncertain_needs_review`; those are semantic contradictions and block strict passage.

For `distinct_follow_up` or `program_lineage`, `anchor_class_to_verify` must be one active anchor class and `incremental_anchor_question` must be non-empty. `fresh_anchor_questions[]` is non-empty for strict/high-potential items.

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
Strict requires lane fit, at least one valid anchor class, incremental information, decision value, plausible source direction/path, freshness, acceptable duplicate/follow-up treatment, independent cardability/full-schema viability, a **PASS** Related pre-pass, item-specific Stage B evidence targets, and machine-valid score-cap metadata.

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
  "technology_evidence_level": "not_applicable",
  "policy_stage": null,
  "novelty_cap_basis": "none",
  "systemic_scale_denominator": null,
  "denominator_gap": "required when systemic_scale_denominator is null",
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
The eight score components sum exactly to total. `systemic_scale_denominator` and `denominator_gap` must obey the 2/5 cap rule above. The three cap-metadata fields must obey §4.1 and the resulting component/total ceiling is machine-enforced.

## 15. Stage exit
Account for every input event. Emit strict specs, partitioned review/watch/support/reject pools, duplicate/reinforcement/update dispositions, summary counts, selection-route counts, score-band counts, anchor/lens coverage, high-value review IDs, follow-up IDs, and zero-coverage domains. Record current prompt path/SHA provenance. A missing or malformed Related pre-pass, denominator attestation, score-cap metadata, or integrated news-value core blocks Stage B recommendation.