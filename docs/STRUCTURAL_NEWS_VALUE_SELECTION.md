<!-- CANONICAL_POLICY: STRUCTURAL_NEWS_VALUE_SELECTION_V2 -->
<!-- Effective KST: 2026-07-17 -->
<!-- Supersedes: STRUCTURAL_NEWS_VALUE_SELECTION_V1 -->

# Structural News Value Selection V2

## 0. Purpose

This document defines what makes a news event valuable for SBTL_HUB.

The selector must not confuse:

- ease of verification with importance;
- binding execution with structural impact;
- a large headline amount with a large market effect;
- a law being adopted with that law being implemented;
- announced capacity with actual output;
- a tender pipeline with awarded, financed, or commissioned capacity;
- an interesting event with a decision-useful event.

A signed contract, capital increase, financing close, construction start, first shipment, factory opening, policy announcement, bill, court decision, regulatory notice, or production start may be credible and cardable. None is automatically important merely because of its form.

### Canonical definition

> **News value is the magnitude by which a newly verified fact changes a market participant's expected future cash flows, asset value, market access, legal rights and obligations, cost structure, supply-demand balance, competitive position, technology pathway, or probability of loss.**

The core question is:

> **What previously reasonable judgment must change because this fact is now known?**

This document supplements:

- `docs/FACT_DISCIPLINE.md`
- `docs/PROMPT_ABC_DEFAULT_MODE.md`
- `docs/PROMPT_ABC_SUPPORTING_RULES.md`
- `docs/WORKFLOW.md`
- `docs/OPERATIONS.md`
- `docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md`

Conflict hierarchy:

1. `FACT_DISCIPLINE.md` always wins for facts, figures, dates, quotations, source direction, and evidence support.
2. This document wins over any selector rule that treats execution-anchor strength, transaction size, or corporate prominence as a proxy for editorial importance.
3. Existing state-ladder, lineage, duplicate, no-silent-enrichment, and source-diversity rules remain unchanged.
4. A high news-value score never waives an evidence or workflow requirement.

---

## 1. Four independent judgments — HARD RULE

Every candidate must be assessed through four separate objects.

### 1.1 `execution_credibility_gate`

Question:

> Is the event real, current, correctly scoped, and supportable?

This is a credibility gate, not an importance score.

Accepted credibility anchors include, but are not limited to:

- signed contract, binding order, offtake, procurement, financing close;
- construction start, commissioning, production start, delivery, or field deployment;
- statute, enacted rule, final regulation, delegated act, official standard, or administrative notice;
- regulator decision, enforcement action, recall, penalty, permit, suspension, or licence withdrawal;
- government programme award, budget allocation, tender decision, or implementation notice;
- official market, grid, price, demand, trade, inventory, utilisation, safety, accident, failure, or operating-data release;
- court judgment, tribunal ruling, injunction, administrative appeal, or legally operative filing;
- independently verified production, supply, shutdown, restart, cancellation, bankruptcy, eligibility, or market-access change.

The event stage must be labelled precisely.

- A plan is not execution.
- A bill is not enacted law.
- Adoption is not necessarily effectiveness.
- Effectiveness is not necessarily enforcement.
- A permit is not production.
- An award is not installation.
- A quota is not actual output.
- A tender is not awarded capacity.
- Awarded capacity is not financed capacity.
- Financed capacity is not commissioned capacity.

### 1.2 `independent_cardability_gate`

Question:

> Can this event support an independent, full-schema, decision-useful card rather than only a supporting fact?

Cardability requires:

- a distinct current event or material stage progression;
- a specific factual anchor;
- a clear affected market, company, asset, policy, legal rule, or technology;
- enough verified content to explain what changed, why it matters, and what remains conditional;
- acceptable duplicate and reinforcement treatment against the active baseline.

A source can be useful without supporting an independent card. Background, repeated plans, static explainers, and non-material stage updates may be reinforcement rather than new cards.

### 1.3 `decision_news_value_score`

Question:

> How much does the new fact change industrial, economic, legal, strategic, technical, or risk judgments?

This is the 100-point editorial-priority score defined in Section 4.

### 1.4 `publication_urgency`

Question:

> Must a decision-maker know this now to change an action, valuation, contract, compliance plan, procurement choice, hedge, or risk assessment?

Urgency is separate from long-run importance.

A major rule with a two-year transition period may be structurally important but not operationally urgent today. A smaller recall, permit suspension, customs block, or auction deadline may be immediately urgent.

### Prohibited collapse

The following objects must never be represented by one combined score:

- credibility;
- cardability;
- decision news value;
- publication urgency.

---

## 2. Mandatory before–after test

A valuable news item must establish the following chain.

### 2.1 Prior state

What was reasonably believed before the event?

Examples:

- a factory was planned but not financed;
- a policy was proposed but not legally binding;
- a subsidy was available but eligibility details were unresolved;
- a mine was suspended and supply was expected to remain offline;
- a technology had laboratory results but no commercial-scale yield data;
- storage capacity was growing but dispatch access was assumed to function normally.

### 2.2 New verified fact

What new fact has now been confirmed?

Examples:

- final regulation adopted;
- effective date and covered entities published;
- first enforcement action issued;
- budget allocated and programme application opened;
- financing closed;
- production restarted;
- market data contradicted the previous demand assumption;
- court invalidated or narrowed an agency interpretation;
- field performance, defect, or recall data became available.

### 2.3 Changed judgment

What decision or expectation should change?

Examples:

- market access is now conditional on traceability data;
- project revenue can include capacity payments;
- lithium supply expectations rise and price support weakens;
- a subsidy-dependent project becomes less bankable;
- liability or warranty risk increases;
- a chemistry gains or loses relative demand;
- a previously announced project is more or less likely to reach commercial operation.

### Mandatory output fields

Each high-value candidate must include:

- `prior_state`
- `new_verified_fact`
- `changed_judgment`
- `uncertainty_resolved`
- `remaining_uncertainty`

If these cannot be stated without speculation, the item is not yet ready for a high-priority card. It must be researched, narrowed, or routed to review.

---

## 3. Novelty and information-value gate

News value requires new information, not merely a new article.

### 3.1 Qualifying novelty

Qualifying novelty includes:

- a plan becoming a legally binding duty;
- a bill becoming enacted law;
- a law receiving implementation rules, budget, eligibility criteria, or enforcement;
- a target becoming a signed obligation or funded project;
- a permit becoming physical restart or output;
- a previously expected investment being cancelled, delayed, or reduced;
- a new exception, exemption, transition rule, or grandfathering provision;
- a first court interpretation or enforcement action;
- actual price, inventory, demand, utilisation, failure, safety, or operating data changing the prior assumption;
- a materially different follow-up event for the same actor, project, policy, or asset.

### 3.2 Low-novelty patterns

Default to reinforcement, watchlist, or lower priority when the item is:

- a repeated announcement with no new legal, financial, technical, or operational fact;
- the same contract distributed by another outlet;
- an inauguration or ceremony for an already-carded event with no new execution fact;
- a policy speech restating an existing programme;
- an unchanged capacity target;
- an article using a new headline for an old event;
- a stage update that resolves no material uncertainty.

### 3.3 Novelty caps

Unless a stronger fresh fact is established:

- repeated announcement: maximum `context_or_reinforcement`;
- routine stage progression with no changed decision: maximum `standard_monitoring`;
- corporate target without independent execution or validation: maximum `standard_monitoring`;
- political rhetoric without legal or administrative pathway: maximum `context_or_reinforcement`.

---

## 4. Decision news-value score — 100 points

The score is deliberately **industry-first**.

The three core industrial dimensions — market structure, supply-demand-price, and technology-performance-safety — account for **70 of 100 points**.

Law and policy are not allowed to dominate merely because an instrument is formal. A legal or policy event earns most of its value by changing market structure, supply, demand, technology pathways, costs, or risk. Its legal force is assessed separately in Section 5 and contributes a maximum of 10 points here.

Do not double-count the same effect across dimensions.

### A. Market structure and competitive position — 0 to 25

Assess whether the event changes:

- industry concentration;
- supplier or customer bargaining power;
- entry barriers;
- switching costs;
- vertical integration;
- control of standards, data, channels, infrastructure, permits, or key inputs;
- ownership and operating models;
- access to grids, sites, customers, capital, procurement, or subsidies;
- recurring revenue or service models;
- competitive dependence on a country, company, chemistry, or technology;
- market design, dispatch access, capacity remuneration, or revenue-stack availability.

High scores require a market-level consequence, not only a company-level transaction.

A merger, partnership, or contract does not automatically score highly. Explain how it changes concentration, market access, operating control, revenue formation, or competitive behaviour.

### B. Supply, demand, price, and utilisation structure — 0 to 25

Assess whether the event changes:

- actual or expected commodity, material, cell, pack, system, or electricity supply;
- demand by application, region, customer, or chemistry;
- inventory;
- imports, exports, quotas, or trade flows;
- utilisation or operating rates;
- shortage or surplus expectations;
- benchmark prices or price formation;
- marginal cost or the industry cost curve;
- EV versus ESS demand composition;
- duration, power, safety, or duty-cycle requirements affecting product mix;
- relationships among lithium, nickel, cobalt, graphite, LFP, high-nickel, sodium-ion, flow-battery, and recycling demand.

Capacity announcements must be distinguished from actual output.

- Planned capacity is not supply.
- Permitted capacity is not production.
- Nameplate capacity is not utilisation.
- A quota is not actual extraction.
- A tender pipeline is not commissioned demand.

High scores generally require one or more of:

- a meaningful market denominator;
- actual operating, inventory, trade, demand, or price data;
- a credible change to supply or demand expectations;
- a demonstrated effect on price formation, cost curves, or utilisation.

### C. Technology, performance, safety, and operational validity — 0 to 20

Assess whether the event changes the credible position of a technology on:

- cost;
- energy density;
- power density;
- cycle life;
- calendar life;
- fast charging;
- temperature range;
- degradation;
- recovery rate;
- production yield;
- manufacturability;
- material intensity;
- commercial-scale operability;
- safety, defect, fire, recall, or failure rates;
- maintenance, warranty, insurance, or replacement requirements;
- standardisation, certification, customer qualification, or field validation.

Technology claims must be classified by evidence stage:

1. concept or company target;
2. laboratory result;
3. prototype or pilot;
4. third-party or standardised test;
5. customer qualification;
6. commercial-scale production data;
7. multi-site or long-duration field performance;
8. recall, defect, warranty, or operating-failure evidence.

Scoring caps:

- company target or unsupported claim: maximum 4/20;
- laboratory result without independent validation: maximum 7/20;
- pilot result without commercial-scale evidence: maximum 11/20;
- independent test or customer qualification: maximum 15/20;
- commercial-scale or long-duration field evidence may receive 16–20/20;
- material safety failure, recall, or operating evidence may receive 16–20/20 even when the technology outcome is negative.

### D. Future cash flow and asset-value impact — 0 to 10

Assess whether the event can materially change:

- revenue;
- sales volume;
- realised price;
- operating cost;
- gross margin or EBITDA;
- utilisation;
- warranty, insurance, remediation, or recall cost;
- capex;
- tax, subsidy, grant, guarantee, or financing cost;
- project NPV, IRR, DSCR, or bankability;
- impairment, stranded-asset, or replacement risk;
- asset or enterprise value.

This dimension measures the economic transmission, not the size of the announced transaction.

Generic claims such as "positive for growth" receive no meaningful score.

### E. Law, policy, rights, obligations, and market access — 0 to 10

Assess whether the event changes:

- legal rights or duties;
- product eligibility;
- subsidy, tax-credit, procurement, or financing eligibility;
- tariff, quota, export-control, import-ban, FEOC, local-content, or customs treatment;
- licensing, certification, registration, or permitting;
- battery-passport, traceability, recycling, repair, durability, disclosure, or due-diligence obligations;
- enforcement exposure, penalties, recall, refund, remediation, or civil liability;
- court interpretation of a statute, regulation, contract, patent, permit, or valuation method;
- the ability to enter, remain in, or compete in a material market.

The formal status of a legal instrument does not itself earn 10 points.

A policy or legal event should earn additional points under A, B, C, or D when it changes market structure, supply-demand, technology pathways, or economics.

Political statements and draft proposals score lower than effective, implemented, or enforced rules unless the actor possesses immediate legal authority and the transmission pathway is credible.

#### Policy/legal scoring transmission guard

The 10-point legal-policy dimension measures only the event's operative legal effect: enforceability, rights, duties, eligibility, liability, market-access status, and procedural certainty.

Do not place the full industrial consequence inside the legal-policy dimension.

Allocate consequences as follows:

- change in entry barriers, procurement access, competitive concentration, grid access, or revenue design → **A. Market structure**;
- change in quotas, tariffs, imports, exports, actual supply, demand, utilisation, or price formation → **B. Supply-demand-price**;
- change in mandatory technical standards, product qualification, safety performance, repairability, durability, or technology pathway → **C. Technology-performance-safety**;
- change in subsidy value, tax burden, compliance cost, financing, liability, margin, or asset value → **D. Cash flow and asset value**;
- legal force, covered rights and duties, effective status, enforcement exposure, and market-access entitlement itself → **E. Law-policy-market access**.

A policy event may therefore receive a high total score, but only when its verified industrial transmission is material. It must not receive a high score by placing the same policy effect in multiple dimensions without separate reasoning.

### F. Systemic scale and coverage — 0 to 5

Assess scale against the relevant denominator, not the headline amount alone.

Possible denominators include:

- share of global or national supply;
- share of annual demand;
- share of installed storage or new additions;
- affected customers, products, operators, or assets;
- covered geography;
- share of a regional project pipeline;
- number and significance of economic operators subject to a rule;
- proportion of company capacity, revenue, or capital committed.

If no defensible denominator is available, score no more than 2/5 and record `denominator_gap`.

### G. Persistence and irreversibility — 0 to 3

Assess whether the effect:

- persists beyond a quarter or single project;
- creates multi-year compliance or switching costs;
- changes supply-chain geography;
- requires hard-to-reverse capex;
- locks in a standard, contract, network, or operating model;
- strands prior investment;
- invalidates a durable market assumption.

### H. Decision urgency and actionability — 0 to 2

Assess whether a decision-maker should promptly:

- change valuation or forecasts;
- revise a contract or covenant;
- alter sourcing or customer strategy;
- prepare compliance systems;
- change a project schedule;
- secure alternative supply;
- adjust a hedge or inventory position;
- reassess a permit, warranty, litigation, or enforcement risk.

### Score bands

| Score | Classification | Meaning |
|---:|---|---|
| 85–100 | `critical_structural` | Resets an industry, market, technology, regulatory, price, or risk assumption |
| 70–84 | `high_decision_value` | Directly relevant to investment, procurement, policy, legal, technology, or operating decisions |
| 55–69 | `material_industry_signal` | Material execution or structural signal with bounded reach |
| 40–54 | `standard_monitoring` | Useful and cardable, but limited change to core assumptions |
| 25–39 | `context_or_reinforcement` | Better used as supporting context, watchlist, or baseline reinforcement |
| 0–24 | `low_independent_value` | Low independent card value unless additional facts are found |

---

## 5. Law and policy effect framework — HARD RULE

Law and policy news must be analysed by legal effect and implementation stage, not by headline language.

Legal-policy stage is an **effect and confidence framework**, not a substitute for the 100-point industrial-value score.

A formal legal event can be low-value if it affects only one narrow dispute. A guidance document can be high-value if it immediately controls subsidy eligibility, customs clearance, licensing, procurement, or market access.

### 5.1 Legal-policy stage classification

Record one primary stage and any relevant secondary stage.

#### Stage 0 — rhetoric, political statement, campaign pledge, or advocacy

Examples:

- ministerial statement;
- party manifesto;
- industry request;
- political speech;
- non-operative bilateral declaration.

Default treatment: watchlist or context unless the actor possesses immediate executive authority or the statement changes market expectations through a credible implementation pathway.

Default decision-value cap: 39/100 unless an immediate operative effect or independently verified market consequence exists.

#### Stage 1 — roadmap, white paper, study, consultation, or draft standard

Examples:

- government roadmap;
- consultation paper;
- regulator study;
- technical-standard draft;
- preliminary guidance.

Value rises when covered entities, obligations, dates, metrics, budget, or implementing authority are specific.

Default decision-value cap: 54/100 unless the document directly changes current administrative practice, procurement, funding, or market expectations.

#### Stage 2 — bill, proposed rule, draft delegated act, draft budget, or formal legislative proposal

Assess:

- sponsor and competent authority;
- legislative or rulemaking stage;
- political support;
- expected amendments;
- adoption probability;
- expected timing;
- legal authority and possible challenge.

Do not write as if adopted.

Default decision-value cap: 69/100 unless passage is highly probable, timing is near, and the market effect is already material and independently observable.

#### Stage 3 — enacted law, final rule, formally adopted standard, or signed legal instrument

Separate:

- adoption date;
- publication or gazette date;
- effective date;
- mandatory application date;
- transition period;
- grandfathering;
- delegated implementation still required.

Adoption does not prove administrative readiness or enforcement.

No automatic score floor or ceiling. Score the actual industrial effect.

#### Stage 4 — implementation rule, budget allocation, administrative guidance, registration system, eligibility criteria, or programme opening

This stage often has more practical value than enactment because it converts legal authority into an executable process.

Assess:

- responsible agency;
- budget and funding source;
- application and selection criteria;
- forms, registry, certification, or data system;
- administrative capacity;
- timetable;
- transitional recognition of existing operators.

No automatic score floor. High scores require a material effect on market structure, supply, demand, technology, economics, or access.

#### Stage 5 — enforcement, payment, award, denial, penalty, recall, customs action, licence suspension, or procurement exclusion

This is the point where legal or policy rules create realised economic effects.

Assess:

- affected party and conduct;
- legal basis;
- monetary or operating effect;
- precedent value;
- appeal or review rights;
- probability of wider enforcement.

First enforcement, first denial, first customs block, or first market exclusion may be highly valuable even when the monetary amount is small.

#### Stage 6 — judicial or tribunal interpretation

Court decisions are not automatically the highest-value stage. Their importance depends on:

- court level;
- finality;
- appealability;
- jurisdiction;
- binding versus persuasive effect;
- party-specific versus industry-wide application;
- whether the decision invalidates, narrows, or confirms agency action;
- remedy: damages, injunction, vacatur, remand, permit cancellation, or valuation order;
- likely regulatory or legislative response.

A project-specific valuation ruling may be a standard or support card. A ruling that changes subsidy eligibility, market access, permitting, FEOC treatment, patent freedom to operate, or agency authority may be critical.

### 5.2 Legal instrument type

Record the instrument precisely:

- constitution or treaty;
- statute or act;
- regulation or rule;
- delegated or implementing act;
- executive order or decree;
- ministerial notice, guidance, circular, or administrative interpretation;
- public-procurement requirement;
- mandatory or voluntary standard;
- court or tribunal decision;
- consent order, settlement, or enforcement undertaking;
- programme term, grant condition, loan condition, or guarantee condition.

Do not use generic labels such as "new law" when the instrument is guidance, a proposal, a programme notice, or a court order limited to the parties.

### 5.3 Legal-policy transmission analysis

Every policy or legal card must map the transmission chain.

Examples:

```text
rule change
→ subsidy eligibility changes
→ effective product price changes
→ demand and utilisation change
→ margin, cash flow, or asset value changes
```

```text
capacity-market implementation
→ storage availability receives remuneration
→ revenue stack and DSCR improve
→ financing probability rises
→ storage investment increases
```

```text
traceability obligation
→ data and supplier-verification systems become mandatory
→ compliance cost and supplier switching rise
→ market access depends on verified data
→ competitive advantage shifts to prepared operators
```

If the transmission pathway cannot be explained, policy implication must remain narrow.

### 5.4 Mandatory legal-policy questions

For every legal, policy, regulatory, judicial, enforcement, subsidy, tax, tariff, quota, procurement, or standardisation event, answer:

1. What is the exact legal instrument?
2. Which authority issued, adopted, implemented, or enforced it?
3. What procedural stage has actually been reached?
4. What dates govern adoption, publication, effectiveness, and mandatory application?
5. Who and what products are covered?
6. What exemptions, thresholds, transition periods, grandfathering, or emergency exceptions apply?
7. What budget, registry, guidance, certification, staffing, or administrative system is required?
8. What happens on non-compliance?
9. Can the action be appealed, stayed, invalidated, amended, or reversed?
10. Is the effect party-specific, national, regional, extraterritorial, or industry-wide?
11. What is the economic and industrial transmission pathway?
12. What next event determines real implementation?

### 5.5 Required legal-policy fields

Each applicable item must include:

- `legal_policy_stage`
- `legal_instrument_type`
- `competent_authority`
- `procedural_status`
- `adoption_date`
- `publication_date`
- `effective_date`
- `mandatory_application_date`
- `affected_entities[]`
- `affected_products_or_activities[]`
- `geographic_scope`
- `extraterritorial_effect`
- `budget_or_funding_source`
- `implementation_mechanism`
- `administrative_readiness`
- `exemptions_and_thresholds[]`
- `transition_and_grandfathering[]`
- `noncompliance_consequences[]`
- `appeal_or_litigation_risk`
- `reversibility_risk`
- `precedent_scope`
- `legal_policy_transmission_chain[]`
- `next_implementation_trigger`

Use `not_disclosed`, `not_applicable`, or `not_yet_determined` where appropriate. Do not invent missing legal detail.

---

## 6. Anti-execution and anti-formality bias — HARD RULE

### 6.1 Binding status is not an importance score

The following is invalid reasoning:

> This is a binding contract, therefore it is a top news item.

Valid reasoning explains the structural effect:

> The contract covers a material share of regional demand, changes supplier concentration, establishes a price benchmark, or materially de-risks a technology or project.

### 6.2 Legal formality is not an importance score

The following is invalid reasoning:

> Parliament passed a law, therefore the event is top priority.

Valid reasoning explains:

- the covered market;
- enforceable duties;
- effective and application dates;
- exceptions and transition;
- implementation readiness;
- market, supply, demand, technology, cost, or access effects.

### 6.3 Transaction-size discipline

A large amount supports importance only after clarifying:

- currency;
- committed versus potential amount;
- total project cost versus current financing;
- capacity actually awarded versus pipeline or target;
- annual capacity versus cumulative volume;
- relevant market denominator;
- conditions precedent;
- share of company or market exposure.

### 6.4 Construction and production discipline

Construction start, factory opening, production start, or first delivery must not automatically outrank:

- market-rule changes;
- grid dispatch failures;
- price-moving supply restarts or shutdowns;
- recalls, fires, warranty failures, or safety enforcement;
- demand and chemistry shifts;
- independently validated technology change;
- mandatory compliance and market-access rules.

### 6.5 MOU and partnership discipline

An MOU or partnership may be cardable only when the card states:

- binding or non-binding status;
- concrete role of each party;
- committed capital, volume, site, or deliverable, if any;
- previous LOI or earlier agreement;
- conditions for execution;
- structural consequence beyond the announcement itself.

---

## 7. Structural-event patterns requiring active rescue

The selector must not discard the following merely because they lack a conventional corporate execution anchor.

### 7.1 Market structure and market-operation signals

- storage skip rates or dispatch failures;
- curtailment, congestion, negative-price, interconnection, or queue changes;
- capacity-market design;
- ancillary-service or balancing-rule changes;
- network-tariff or charging-rule changes;
- concentration, market-access, or platform-control changes.

### 7.2 Supply, demand, price, and utilisation signals

- material mine, refinery, plant, or factory restart or shutdown;
- quota, export-control, tariff, inventory, or utilisation change;
- cost-curve or benchmark-price change;
- supply deficit or surplus revision supported by data;
- EV versus ESS demand-mix change;
- chemistry-share change;
- regional sales, installation, or operating-data reversal.

### 7.3 Technology, safety, and operating evidence

- independently verified cost, cycle-life, safety, energy-density, recovery-rate, or yield change;
- standardised or third-party-tested performance;
- customer qualification;
- commercial-scale production result;
- long-duration field performance;
- recall, fire, defect, warranty, degradation, or insurer response;
- project cancellation or revenue-model failure caused by technical or operating weakness.

### 7.4 Regulation, policy, and law

- enacted or implemented battery-passport, traceability, recycling, safety, repair, durability, local-content, FEOC, tariff, subsidy, procurement, or market-access rule;
- implementation standard or administrative guidance that changes eligibility or compliance;
- first enforcement, denial, customs block, recall, penalty, or licence action;
- court decision changing agency authority, eligibility, permitting, valuation, liability, or freedom to operate.

These items may use official data, policy, legal, safety, standards, or market-operation material as the credibility anchor.

---

## 8. Stage A operating rule

Stage A remains selector-only and must not perform external web search or article-body fetch.

Stage A must:

1. estimate news value from current-run metadata, previews, usable text, and source-packet metadata;
2. separate credibility, cardability, decision value, and urgency;
3. avoid rejecting a high-potential structural item solely because a corporate execution anchor is absent;
4. route unresolved but high-potential structural items to `candidate_review_pool[]` with a concrete rescue question;
5. mark easy-to-verify but low-value transactions as lower editorial priority even when they enter `strict_passed_spec[]`;
6. preserve unresolved legal, policy, market, supply, technology, and denominator questions for Stage B or an authorised rescue loop;
7. apply search-before-delete at all stages where search is authorised.

### Required item fields

Each `strict_passed_spec[]` and `candidate_review_pool[]` item must include:

- `execution_credibility_gate`
  - `status: PASS | REVIEW | FAIL`
  - `anchor_type`
  - `anchor_strength`
  - `stage_precision_note`
- `independent_cardability_gate`
  - `status: PASS | REVIEW | FAIL`
  - `distinct_event_or_stage_progression`
  - `full_schema_viability`
  - `duplicate_or_reinforcement_note`
- `decision_news_value_score`
- `decision_value_breakdown`
  - `market_structure_competition` — 0 to 25
  - `supply_demand_price_utilisation` — 0 to 25
  - `technology_performance_safety` — 0 to 20
  - `cashflow_asset_value` — 0 to 10
  - `law_policy_market_access` — 0 to 10
  - `systemic_scale` — 0 to 5
  - `persistence_irreversibility` — 0 to 3
  - `decision_urgency_actionability` — 0 to 2
- `decision_value_classification`
- `structural_change_types[]`
- `prior_state`
- `new_verified_fact`
- `changed_judgment`
- `uncertainty_resolved`
- `remaining_uncertainty`
- `denominator_used`
- `denominator_gap`
- `publication_urgency`
  - `level: immediate | near_term | monitor`
  - `action_required`
  - `decision_deadline`
- `anti_bias_check`
  - `binding_status_used_as_importance_proxy: false`
  - `legal_formality_used_as_importance_proxy: false`
  - `headline_amount_used_without_denominator: false`
  - `announced_capacity_treated_as_actual_output: false`
  - `routine_execution_event_overranked: false`
- `structural_rescue_required`
- `structural_rescue_question`
- `search_before_delete_status`

Policy and legal items must also include the Section 5 fields, subject to Stage A's no-fetch boundary and available metadata.

### Routing matrix

| Credibility | Cardability | Decision value | Default route |
|---|---|---:|---|
| PASS | PASS | 70–100 | `strict_passed_spec[]`, subject to all other strict gates |
| PASS | PASS | 55–69 | strict or candidate review based on evidence and duplicate risk |
| PASS | PASS/REVIEW | 40–54 | lower-priority strict, candidate review, or reinforcement |
| REVIEW | PASS/REVIEW | 55–100 | `candidate_review_pool[]` with mandatory rescue question |
| PASS/REVIEW | REVIEW | any | candidate review, reinforcement, or watchlist |
| FAIL | any | any | reject/support-only only with item-specific reason and ledger |

Do not force a minimum number of structural cards. Do not lower evidence standards to improve topic balance.

---

## 9. Stage B and rescue search order

For each important candidate, search in this order:

1. re-read the full existing source packet;
2. official government, regulator, legislature, court, exchange, standards body, grid operator, company filing, or source-owner material;
3. independent Tier 1/Tier 2 same-event reporting;
4. preceding and follow-up events for the same actor, policy, asset, technology, or market;
5. market denominator and comparison data;
6. legal instrument, procedural stage, effective date, exception, implementation, and appeal details where applicable;
7. technology validation stage and commercial or field evidence where applicable;
8. repair and enrich the claim;
9. narrow the visible scope only if evidence remains insufficient;
10. consider support-only or deletion only after failed search and repair steps are logged.

Deletion is the last resort.

A missing fact that can be found must be added through the authorised revise or rescue path. It must not be deleted merely because the initial source packet was thin.

---

## 10. IB-grade decision-useful content

A high-quality card should answer, where applicable:

1. What changed?
2. What was the prior state?
3. What new uncertainty was resolved?
4. What is legally, financially, technically, competitively, or operationally different now?
5. Who and what products, assets, or markets are affected?
6. What is the relevant denominator and market share?
7. What is committed, conditional, proposed, effective, enforced, operating, or still planned?
8. What exceptions, thresholds, conditions, transition periods, or appeal risks apply?
9. Through what chain does the event change market structure, supply-demand, technology, cash flow, access, or risk?
10. What measurable next event determines whether the effect is realised?
11. What remains unknown or undisclosed?
12. What action should an investor, operator, supplier, customer, lender, regulator, or legal team reconsider?

Do not fill these questions with generic implications. Use verified facts and clearly bounded inference.

---

## 11. Signal assignment

`signal = top | high | mid` remains a publication field, but it must be assigned after the four independent judgments.

Default guidance:

- `top`: decision score 85–100, or 70–84 with exceptional urgency and strong evidence;
- `high`: decision score 70–84, or 55–69 with material lane impact and strong evidence;
- `mid`: decision score 40–69 depending on scope, or a credible execution event with narrower independent value.

A contract, law, court ruling, policy announcement, funding round, or factory event does not become `top` solely because of its form.

---

## 12. Mandatory validation blockers

Stage A or any promotion, reselection, or rescue run must block if:

- credibility, cardability, decision value, and urgency are collapsed into one score;
- the eight breakdown values do not sum to `decision_news_value_score`;
- the three core industrial dimensions do not use the required 25/25/20 maximum weights;
- a top candidate lacks the before–after chain;
- a contract, financing, capital increase, construction, production, legal, or policy event is ranked top without an industrial-effect explanation;
- a high-potential market, supply, demand, price, technology, safety, policy, or legal event is rejected solely for lacking a corporate execution anchor;
- a high-value review item lacks a specific rescue question;
- a legal or policy item lacks instrument and procedural-stage precision;
- adoption, effectiveness, implementation, and enforcement are conflated;
- announced capacity is treated as actual output;
- a market-share, price-impact, or scale claim lacks a denominator;
- a company technology claim receives a high technology score without validation-stage support;
- deletion or support-only is finalised before the applicable search-first process.

Required blocker status:

```text
BLOCKED_STRUCTURAL_NEWS_VALUE_SELECTION_INVALID
```

Required output:

- `affected_items[]`
- `missing_or_invalid_fields[]`
- `execution_or_formality_bias_findings[]`
- `recommended_return_stage`
- `no_next_stage_recommendation: true`

---

## 13. Calibration examples

### Example A — large contract, limited structural value

A 2GWh BESS supply contract is signed.

- credibility: strong;
- cardability: likely pass;
- value: depends on regional market share, supplier concentration, price benchmark, technology de-risking, and system role;
- default: material or high only when structural significance is demonstrated.

### Example B — grid operating failure, high structural value

A grid operator reports that 35% of available BESS dispatch opportunities are skipped because of market or control-system design.

- credibility: official operating data;
- market-structure value: high because installed assets cannot access expected revenue;
- supply-demand value: relevant if dispatch affects curtailment and balancing;
- default: critical or high when definitions, period, and denominator are verified.

### Example C — adopted battery-passport standard

A regulator formally adopts technical standards supporting battery-passport implementation.

- legal stage: formally adopted standard, not necessarily mandatory application;
- value: depends on effective date, covered batteries, registry readiness, required data, liability, and market-access consequences;
- default: high when it materially changes supplier systems and market access; not top merely because it is an official standard.

### Example D — price-moving mine restart

A mine representing a material share of global supply receives restart permission.

- permit is not output;
- supply score depends on capacity, restart timing, actual utilisation, inventory, and global denominator;
- price impact must be supported or framed as bounded inference;
- default: candidate rescue or high priority depending on evidence.

### Example E — technology breakthrough claim

A company announces a battery with exceptional cycle life and cost.

- company target only: technology score capped at 4/20;
- laboratory result: capped at 7/20;
- independent standardised test: up to 15/20;
- customer qualification or field data: potentially 16–20/20;
- default: do not rank top from corporate claims alone.

### Example F — first enforcement under an existing law

A customs authority blocks imports under a battery-supply-chain rule for the first time.

- legal stage: enforcement;
- policy score: material;
- market-structure and supply scores may also be high if the action affects a major supplier or establishes a replicable precedent;
- urgency: immediate for importers and customers;
- default: high or critical depending on scope and precedent.

---

## 14. Version and lineage

Every run applying this policy must record:

- `structural_selector_policy_version: STRUCTURAL_NEWS_VALUE_SELECTION_V2`
- `structural_selector_policy_file: docs/STRUCTURAL_NEWS_VALUE_SELECTION.md`
- `structural_selector_policy_sha`
- `credibility_cardability_value_urgency_separated: true`
- `industry_first_weighting_applied: true`
- `core_industrial_weight_total: 70`
- `search_before_delete_applied: true`

Downstream stages must preserve these fields or explicitly record why they are not applicable.
