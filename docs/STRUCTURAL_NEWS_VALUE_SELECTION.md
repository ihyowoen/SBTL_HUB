<!-- CANONICAL_POLICY: STRUCTURAL_NEWS_VALUE_SELECTION_V1 -->
<!-- Effective KST: 2026-07-17 -->

# Structural News Value Selection

## 0. Purpose

This document prevents the SBTL_HUB selector from confusing **easy-to-verify execution events** with **high-value industry news**.

A signed contract, capital increase, financing close, groundbreaking, shipment, or production start can be credible and cardable. It is not automatically important.

The selector must answer two separate questions:

1. **Credibility / execution question** — Is the event real, current, correctly scoped, and supportable?
2. **News-value question** — Does the event materially change market structure, prices, costs, demand, regulation, technology, safety, or supply-chain risk?

The first question is a gate. The second question determines priority.

This document supplements:

- `docs/FACT_DISCIPLINE.md`
- `docs/PROMPT_ABC_DEFAULT_MODE.md`
- `docs/PROMPT_ABC_SUPPORTING_RULES.md`
- `docs/WORKFLOW.md`
- `docs/OPERATIONS.md`
- `docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md`

If a rule conflicts:

1. `FACT_DISCIPLINE.md` always wins for factual claims, numbers, dates, quotes, and source support.
2. This document wins over any selector rule that treats execution-anchor strength as a proxy for editorial importance.
3. Existing state-ladder, lineage, evidence, duplicate, and no-silent-enrichment rules remain unchanged.

---

## 1. Core separation — HARD RULE

### 1.1 Execution credibility gate

Execution credibility determines whether an item may proceed to evidence building.

Accepted credibility anchors include, but are not limited to:

- signed contract, binding order, offtake, procurement, financing close
- construction start, commissioning, production start, delivery, field deployment
- regulatory decision, enforcement action, enacted rule, official standard
- government programme award or official implementation notice
- official market, grid, price, demand, safety, recall, accident, failure, or operating-data release
- official court decision or legally operative filing
- independently verified change in production, supply, utilisation, dispatch, shutdown, restart, cancellation, bankruptcy, or eligibility

The anchor must be correctly labelled. A plan is not execution. A permit is not production. An award is not installation. A quota is not actual output. A tender is not commissioned capacity.

### 1.2 Structural news-value score

Editorial priority must be scored independently from execution credibility.

A card cannot receive top priority solely because it is:

- binding
- large in headline amount
- financed
- under construction
- a factory opening
- a capital increase
- a partnership with well-known companies

A routine transaction may be credible but lower-priority than a market-design failure, mandatory compliance rule, price-moving supply change, chemistry-demand shift, systemic safety event, or technology-cost change.

---

## 2. Structural value score — 100 points

Score each candidate on the following six dimensions.

### A. Market structure and revenue formation — 0 to 25

Does the event alter:

- market design
- dispatch or curtailment
- capacity remuneration
- grid access or interconnection
- eligibility for subsidies or procurement
- competitive concentration
- customer access
- revenue-stack availability
- ownership or operating model across a material market

### B. Price, cost, margin, and project economics — 0 to 20

Can the event materially affect:

- commodity prices
- cell, pack, system, or project costs
- producer margins
- warranty or insurance costs
- financing conditions
- utilisation or revenue assumptions
- project bankability
- replacement economics

### C. Demand, application, and chemistry mix — 0 to 15

Does the event change:

- EV versus ESS demand composition
- LFP, high-nickel, sodium-ion, flow-battery, or other chemistry mix
- end-market adoption
- customer purchasing behaviour
- duration or performance requirements
- raw-material demand relationships

### D. Regulation, compliance, safety, and market access — 0 to 15

Does the event create or alter:

- mandatory traceability or battery-passport obligations
- local-content, FEOC, tariff, subsidy, or eligibility rules
- safety standards, recalls, enforcement, or liability
- data, repair, recycling, durability, or disclosure requirements
- customs or market-surveillance controls

### E. Systemic scale — 0 to 15

Assess scale relative to the relevant market, not the headline amount alone.

Examples:

- share of national or global supply
- share of installed storage or new demand
- affected customer or asset base
- grid, market, or policy coverage
- capacity relative to regional pipeline
- number of economic operators subject to a rule

### F. Persistence and irreversibility — 0 to 10

Does the event:

- reshape multi-year investment decisions
- create switching or compliance costs
- change infrastructure or supply-chain geography
- persist beyond a single quarter or project
- invalidate prior market assumptions

### Score bands

| Score | Structural priority | Default treatment |
|---:|---|---|
| 80–100 | `top_structural_priority` | Must be actively rescued and evidence-built if lane-relevant |
| 65–79 | `high_structural_priority` | Strong card candidate; compare against baseline and same-event follow-ups |
| 50–64 | `standard_structural_priority` | Cardable if evidence and full-schema value are sufficient |
| 35–49 | `watchlist_or_context` | Keep for monitoring or support unless a stronger fresh fact emerges |
| 0–34 | `low_independent_value` | Usually support-only or reject after applicable verification |

A high score does not waive evidence requirements.

---

## 3. Anti-execution-bias rules — HARD RULE

### 3.1 Binding status is not an importance score

`execution_anchor_strength` and `structural_news_value_score` must be stored separately.

The following is invalid reasoning:

> This is a binding contract, therefore it is a top news item.

Valid reasoning must explain the structural effect, for example:

> The contract represents a material share of the regional storage pipeline and changes supplier concentration, revenue visibility, or cost benchmarks.

### 3.2 Transaction-size discipline

A large amount may support systemic scale, but only after clarifying:

- currency
- committed versus potential amount
- total project cost versus current financing
- capacity actually awarded versus pipeline or target
- annual capacity versus cumulative volume
- market denominator
- conditions precedent

### 3.3 Construction and production discipline

Construction start, factory opening, production start, or first delivery must not automatically outrank:

- market-rule changes
- grid dispatch failures
- price-moving supply restarts or shutdowns
- recalls, fires, warranty failures, or safety enforcement
- demand and chemistry shifts
- mandatory compliance standards

### 3.4 MOU and partnership discipline

An MOU or partnership may be cardable only when the card precisely states:

- binding or non-binding status
- concrete role of each party
- committed capital, volume, site, or deliverable, if any
- previous LOI or earlier agreement
- conditions for execution
- structural consequence beyond the announcement itself

---

## 4. Structural-event patterns that require active rescue

The selector must not discard the following merely because they lack a conventional corporate execution anchor.

### 4.1 Market-operation and grid signals

- storage skip rates or dispatch failures
- curtailment, congestion, negative-price, interconnection, or queue changes
- capacity-market design
- ancillary-service or balancing-rule changes
- network-tariff or charging-rule changes

### 4.2 Price and supply signals

- material mine, refinery, or plant restart/shutdown
- quota, export-control, tariff, inventory, or utilisation changes
- cost-curve or benchmark-price change
- supply deficit/surplus revisions supported by data

### 4.3 Demand and chemistry shifts

- EV versus ESS demand-mix changes
- LFP/high-nickel/sodium-ion/flow-battery share changes
- duration, safety, fast-charge, or warranty requirements changing product mix
- regional sales or installation reversals that alter material demand assumptions

### 4.4 Regulation and compliance

- enacted or formally adopted battery-passport, traceability, recycling, safety, repair, durability, local-content, FEOC, tariff, subsidy, or market-access rules
- official implementation standard, delegated act, enforcement action, or court decision

### 4.5 Safety and failure

- recalls
- fires or systemic defect findings
- warranty revisions
- insurer or regulator responses
- project cancellation, bankruptcy, subsidy withdrawal, or revenue-model failure

### 4.6 Technology and cost validation

- independently verified cost, cycle-life, safety, energy-density, recovery-rate, or production-yield changes
- standardised or third-party-tested performance
- commercial data that changes a technology's economic position

These items may use an official data, policy, legal, safety, or market-operation release as the credibility anchor.

---

## 5. Stage A operating rule

Stage A remains selector-only and must not perform external web search or article-body fetch.

Therefore Stage A must:

1. estimate structural value from the available current-run metadata, previews, usable text, and source-packet metadata;
2. separate credibility from structural value;
3. avoid rejecting a high-potential structural item solely because a contract, funding, construction, or production anchor is absent;
4. route unresolved but high-potential structural items to `candidate_review_pool[]` with a concrete search question;
5. mark easy-to-verify but low-structural-value transactions as lower editorial priority even when they enter `strict_passed_spec[]`;
6. preserve all uncertainty for Stage B or an authorised promotion/rescue loop.

### Required Stage A fields

Each `strict_passed_spec[]` and `candidate_review_pool[]` item must include:

- `execution_credibility_gate`
  - `status: PASS | REVIEW | FAIL`
  - `anchor_type`
  - `anchor_strength`
  - `stage_precision_note`
- `structural_news_value_score`
- `structural_value_breakdown`
  - `market_structure`
  - `price_cost_margin`
  - `demand_chemistry_shift`
  - `regulation_compliance_safety`
  - `systemic_scale`
  - `persistence_irreversibility`
- `structural_priority`
- `structural_change_types[]`
- `structural_value_reason`
- `anti_execution_bias_check`
  - `binding_status_used_as_importance_proxy: false`
  - `headline_amount_used_without_denominator: false`
  - `routine_execution_event_overranked: false`
- `structural_rescue_required`
- `structural_rescue_question`
- `search_before_delete_status`

### Stage A routing matrix

| Credibility | Structural score | Default route |
|---|---:|---|
| PASS | ≥65 | `strict_passed_spec[]`, subject to all other strict gates |
| PASS | 50–64 | strict or candidate review based on evidence/full-schema risk |
| PASS | <50 | lower priority, watchlist, reinforcement, or support-only |
| REVIEW | ≥65 | `candidate_review_pool[]` with mandatory rescue question |
| REVIEW | <65 | review/watchlist depending on lane fit and future trigger |
| FAIL | any | reject/support-only only when failure is item-specific and properly logged |

A candidate does not need a corporate transaction format to score highly.

---

## 6. Stage B and rescue search order

For each structurally important candidate, search in this order:

1. re-read the full existing source packet;
2. official government, regulator, court, exchange, standards body, grid operator, company filing, or source-owner material;
3. independent Tier 1/Tier 2 same-event reporting;
4. preceding and follow-up events for the same actor, policy, asset, or market;
5. market denominator and comparison data;
6. repair and enrich the claim;
7. narrow the visible scope only if evidence remains insufficient;
8. consider support-only or deletion only after the failed search and repair steps are logged.

Deletion is the last resort.

A missing fact that can be found must be added through the authorised revise/rescue path. It must not be deleted merely because the initial source packet was thin.

---

## 7. Required decision-useful content

An IB-grade structural card should answer, where applicable:

- What changed?
- What was the prior state?
- What is legally, financially, technically, or operationally different now?
- What percentage or share of the relevant market is affected?
- What is committed, conditional, planned, or already operating?
- What are the exceptions and conditions?
- What changes for price, margin, demand, compliance, project finance, or market access?
- What next measurable event determines whether the change is real?

Do not fill these fields with generic implications. Use verified facts and clearly bounded inference.

---

## 8. Signal assignment

`signal = top | high | mid` remains a publication field, but it must be assigned after structural-value review.

Default guidance:

- `top`: structural score ≥80 with strong evidence and material lane impact
- `high`: structural score 65–79, or score ≥80 with bounded unresolved limitations
- `mid`: structural score 50–64, or a credible execution event with narrower independent value

A deal does not become `top` solely due to GWh, dollar, euro, won, or yuan size.

Tier 3 single-source items remain ineligible for `top`.

---

## 9. Mandatory validation blockers

Stage A or any promotion/reselection run must block if:

- execution credibility and structural value are collapsed into one score;
- a top candidate lacks `structural_news_value_score` and breakdown;
- a binding/funded/construction event is ranked top without a structural-value explanation;
- a high-potential policy, market, price, demand, technology, or safety event is rejected solely for lacking a corporate execution anchor;
- a high-structural-value review item lacks a specific rescue question;
- deletion/support-only is finalised before the applicable search-first process;
- a market-share, price-impact, or systemic-scale statement lacks a denominator or is framed as fact without support.

Required blocker status:

```text
BLOCKED_STRUCTURAL_NEWS_VALUE_SELECTION_INVALID
```

Required output:

- `affected_items[]`
- `missing_or_invalid_fields[]`
- `execution_bias_findings[]`
- `recommended_return_stage`
- `no_next_stage_recommendation: true`

---

## 10. Examples

### Example A — credible but not automatically top

A 2GWh BESS supply contract is signed.

- credibility: strong
- structural value: depends on regional market share, supplier concentration, price benchmark, financing, and system role
- default: high or mid until structural significance is demonstrated

### Example B — no corporate contract but top structural value

A grid operator reports that 35% of available BESS dispatch opportunities are skipped because of market or control-system design.

- credibility: official operating-data release
- structural value: high because it affects revenue formation and the value of installed assets
- default: top structural priority if definitions and period are verified

### Example C — regulation changes market access

The EU formally adopts technical standards required for battery-passport implementation.

- credibility: enacted or officially adopted legal/standards material
- structural value: high because compliance data becomes a condition of market access
- default: top structural priority

### Example D — price-moving supply change

A mine representing a material share of global supply receives restart permission.

- credibility: permit is not output; restart timing must be verified
- structural value: potentially top because supply expectations and commodity prices may change
- default: candidate rescue or strict pass depending on evidence

---

## 11. Version and lineage

Every run applying this policy must record:

- `structural_selector_policy_version: STRUCTURAL_NEWS_VALUE_SELECTION_V1`
- `structural_selector_policy_file: docs/STRUCTURAL_NEWS_VALUE_SELECTION.md`
- `structural_selector_policy_sha`
- `execution_credibility_separated_from_news_value: true`
- `search_before_delete_applied: true`

Downstream stages must preserve these fields or explicitly record why they are not applicable.
