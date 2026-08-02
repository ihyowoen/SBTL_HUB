<!-- CANONICAL_POLICY: STRUCTURAL_NEWS_VALUE_SELECTION_V3 -->
<!-- Effective KST: 2026-08-02 -->
<!-- Supersedes: STRUCTURAL_NEWS_VALUE_SELECTION_V2 -->
<!-- REPLACE_ALL_CLEAN_VERSION: true -->

# Structural News Value Selection V3

## 0. Purpose

This document is the canonical SBTL_HUB policy for determining:

- whether an event is credible;
- whether it is independently cardable;
- how much industrial and decision value it carries;
- how urgently it must be published;
- which structural domains every run must actively search;
- how earnings, conference calls, analyst Q&A, follow-up events, and portfolio coverage must be handled;
- what downstream evidence, validation, and editorial fields must survive through the card lifecycle.

SBTL_HUB is an industrial-intelligence product, not a corporate-announcement ledger, transaction diary, or legal gazette.

The selector must not confuse:

- ease of verification with importance;
- binding execution with structural impact;
- transaction size with market effect;
- formal legal status with implemented industrial consequence;
- announced capacity with actual output;
- tender pipeline with awarded, financed, commissioned, or operating capacity;
- a new article with new information;
- a company statement with a durable strategy change;
- a quarterly result headline with the full earnings signal;
- the same actor or asset with the same event;
- individual card safety with portfolio completeness.

### Canonical definition

> **News value is the magnitude by which a newly verified fact changes a market participant's expected future cash flows, asset value, market access, legal rights and obligations, cost structure, supply-demand balance, competitive position, technology pathway, commercialisation probability, or probability of loss.**

The core question is:

> **What previously reasonable judgment must change because this fact is now known?**

### Core rule

Execution is one credibility-anchor class. It is not the sole source of news value and is not a mandatory form for every strict candidate.

A signed contract, financing close, construction start, first shipment, factory opening, enacted law, court decision, policy notice, earnings release, management statement, official market dataset, or production start may be credible and cardable. None is automatically important merely because of its form.

---

## 1. Governance hierarchy

For facts, numbers, dates, quotations, source direction, and evidence support:

1. `docs/FACT_DISCIPLINE.md`

For editorial value, structural selection, anchor classification, earnings-call review, follow-up value, and portfolio coverage:

2. `docs/STRUCTURAL_NEWS_VALUE_SELECTION.md` — this document
3. `docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md`
4. `docs/PROMPT_ABC_DEFAULT_MODE.md`
5. `docs/PROMPT_ABC_SUPPORTING_RULES.md`
6. `docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md`
7. `docs/CARD_ID_STANDARD.md`
8. `docs/WORKFLOW.md`
9. `docs/OPERATIONS.md`
10. `docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md`

This document overrides any selector rule that:

- treats execution-anchor strength as a proxy for editorial importance;
- blocks strict eligibility solely because a conventional corporate execution event is absent;
- over-ranks contracts, financing, construction, production, transaction size, corporate prominence, or legal form;
- allows earnings analysis to stop at the press release;
- treats a material follow-up as a duplicate merely because the actor, asset, policy, or project is already represented;
- closes a run without explaining zero coverage in a mandatory structural domain.

This document does not waive evidence, state-ladder, source-diversity, duplicate, lineage, no-silent-enrichment, or baseline-safety requirements.

Every run applying this policy must read both this file and Prompt 0.1S before Stage A selection.

---

## 2. Four independent judgments — HARD RULE

Every candidate must be represented by four separate objects.

### 2.1 `execution_credibility_gate`

Question:

> Is the event real, current, correctly scoped, stage-precise, and supportable?

This is a credibility gate, not an importance score.

Status:

- `PASS`
- `REVIEW`
- `FAIL`

### 2.2 `independent_cardability_gate`

Question:

> Can the event support an independent, full-schema, decision-useful card rather than only background, reinforcement, watchlist context, or support evidence?

Cardability requires:

- a distinct current event, verified structural change, or material stage progression;
- a specific anchor;
- a clear affected market, company, asset, policy, rule, customer, supply chain, or technology;
- sufficient factual specificity to explain what changed and what remains conditional;
- acceptable duplicate, follow-up, reinforcement, and baseline treatment;
- plausible Stage B source paths.

### 2.3 `decision_news_value_score`

Question:

> How much does the new fact change industrial, economic, legal, strategic, technical, operating, or risk judgments?

This is the 100-point score in Section 7.

### 2.4 `publication_urgency`

Question:

> Must a decision-maker know this now to alter valuation, sourcing, contract, compliance, investment, operating, customer, technology, inventory, or risk decisions?

Levels:

- `immediate`
- `near_term`
- `monitor`

### Prohibited collapse

Credibility, cardability, decision value, and urgency must never be collapsed into a single score or status.

A high decision-value score never waives a credibility, evidence, or workflow gate.

---

## 3. Anchor classes

Stage A must classify one or more anchor classes. A strict candidate does not require `execution_event_anchor` when another valid anchor class establishes a current, specific, decision-useful change.

### 3.1 `execution_event_anchor`

Use when rights, obligations, capital, facilities, procurement, production, or realised operating state changes.

Examples:

- signed contract, binding order, offtake, procurement;
- financing close, FID, investment approval;
- construction, expansion, commissioning, opening;
- production start, commercial shipment, field deployment;
- certification, regulatory approval;
- recall, enforcement, penalty, customs action, licence action.

### 3.2 `policy_regulatory_anchor`

Use when legal or administrative treatment changes.

Examples:

- bill, enacted law, final rule, delegated act;
- implementation guidance, FAQ, registry, application process;
- subsidy, tax-credit, procurement, tariff, quota, FEOC, local-content, customs, export-control rule;
- exemption, threshold, grandfathering, transition rule;
- enforcement, denial, payment, penalty, court or tribunal interpretation.

### 3.3 `data_financial_anchor`

Use when official or sufficiently reliable data changes a prior market or company judgment.

Examples:

- quarterly or annual results;
- exchange filing or audited financial statement;
- earnings call or analyst Q&A;
- shipment, order backlog, inventory, utilisation, margin, price, trade, production, demand, grid, interconnection, accident, safety, or market-operation data;
- official forecast revision.

### 3.4 `strategic_behavior_anchor`

Use when concrete behavior or comparative management language identifies a strategy change.

Examples:

- capital-allocation priority change;
- capex delay, reduction, cancellation, relocation, or reallocation;
- EV-to-ESS, AI-power, defence, or other application shift;
- supplier replacement, localisation, dual sourcing, or insourcing;
- chemistry, form-factor, packaging, service-model, or customer-selection change;
- material guidance or strategic-language change versus a prior quarter or prior official statement.

A generic interview, aspiration, or promotional statement is insufficient. The change must be specific and comparable to prior behavior, commitments, or language.

### 3.5 `technology_commercialization_anchor`

Use when technology maturity, qualification, manufacturability, cost, performance, safety, yield, or commercial timing changes.

Examples:

- research → prototype;
- prototype → pilot;
- pilot → field demonstration;
- field demonstration → customer evaluation;
- customer evaluation → qualification or certification;
- qualification → binding order;
- order → mass-production line;
- line → commercial shipment;
- verified yield, cost, energy-density, cycle-life, safety, degradation, or recovery-rate result;
- commercialisation delay, retreat, failure, or cancellation.

### 3.6 `follow_up_probability_anchor`

Use when a later event changes the probability, scale, economics, timing, or legal effect of an existing card.

Examples:

- proposal → selection;
- selection → approval;
- MOU → binding contract;
- plan → FID;
- FID → construction;
- construction → commissioning;
- commissioning → commercial operation;
- order → shipment or revenue recognition;
- policy adoption → implementation or enforcement;
- investigation → recall, penalty, litigation, or closure;
- expected capacity → awarded, financed, operating, reduced, delayed, or cancelled capacity.

---

## 4. Mandatory before–after and novelty tests

### 4.1 Prior state

Record what was reasonably believed before the event.

### 4.2 New verified fact

Record the new fact now established.

### 4.3 Changed judgment

Record what expectation, decision, probability, valuation, market-access view, technology view, or risk view must change.

### 4.4 Uncertainty

Record:

- `uncertainty_resolved`
- `remaining_uncertainty`

### Mandatory fields

- `prior_state`
- `new_verified_fact`
- `changed_judgment`
- `uncertainty_resolved`
- `remaining_uncertainty`
- `incremental_information`
- `baseline_expectation_changed`

### Qualifying novelty

Qualifying novelty includes:

- a plan becoming a binding duty, funded project, or executable process;
- a proposal becoming enacted, implemented, or enforced;
- a new exemption, threshold, transition, or grandfathering rule;
- a first enforcement, denial, customs block, recall, payment, or precedent;
- price, inventory, demand, utilisation, shipment, margin, safety, or operating data contradicting the prior assumption;
- management guidance, capital allocation, customer strategy, or commercial timing changing from a prior official position;
- a material follow-up event for the same actor, asset, policy, project, or technology;
- an analyst Q&A answer revealing new facts or uncertainty not visible in the prepared materials.

### Low-novelty patterns

Default to reinforcement, support, watchlist, or lower priority when the item is:

- a repeated press release with no new fact;
- a translation, syndication, or headline rewrite;
- a ceremony for an already-carded stage with no changed judgment;
- a restated policy speech;
- an unchanged capacity target;
- an unchanged corporate aspiration;
- a routine stage update resolving no material uncertainty;
- a quarterly headline whose drivers were already known and whose call adds no new signal.

### Novelty classification caps — HARD RULE

The following caps apply to the total `decision_news_value_score` and resulting classification, not only to one component:

- repeated announcement, translation, syndication, or headline rewrite with no new fact: maximum `context_or_reinforcement` and 39/100;
- routine stage progression resolving no material uncertainty: maximum `standard_monitoring` and 54/100;
- company target or aspiration without independent execution, validation, or a current observable market effect: maximum `standard_monitoring` and 54/100;
- unsupported political rhetoric or advocacy without immediate operative authority or an independently verified current market effect: maximum `context_or_reinforcement` and 39/100.

A component score or corporate prominence must not be used to bypass these overall caps.

---

## 5. Structural Value Override

### 5.1 Purpose

`Structural Value Override` prevents high-value non-transaction signals from being demoted solely because they lack a conventional execution event.

It never lowers the evidence standard.

### 5.2 Apply when one or more are material

- future cash flow or asset value changes;
- legal rights, duties, eligibility, liability, or market access changes;
- supply, demand, price, cost, inventory, utilisation, or product-mix structure changes;
- customer or competitor behavior changes;
- technology pathway, qualification, safety, yield, or commercialisation timing changes;
- the probability, scale, economics, or timing of an existing event changes;
- economic-security, localisation, traceability, strategic-mineral, or allied-supply-chain importance changes;
- management, investor, lender, customer, supplier, or policy decisions should change.

### 5.3 Do not apply to

- unsupported general commentary;
- promotional forecasts;
- generic “market growth expected” claims;
- interpretations without an identifiable event, document, dataset, or statement;
- repeated reporting with no incremental information;
- direct-benefit or inevitability claims unsupported by evidence.

### 5.4 Required override fields

- `structural_value_override_applied`
- `structural_value_override_reason`
- `anchor_classes[]`
- `incremental_information`
- `decision_relevance`
- `baseline_expectation_changed`
- `evidence_needed_for_stage_b[]`
- `next_confirmation_points[]`
- `why_execution_event_not_required`

---

## 6. Mandatory structural lenses — PORTFOLIO OBLIGATION

Every run must actively inspect all lenses below. They are discovery obligations, not card quotas.

### 6.1 AI data-centre power demand and ESS demand structure

Do not stop at data-centre investment headlines.

Check:

- AI/HPC load size and load characteristics;
- interconnection, transmission, substation, and generation constraints;
- power-procurement structure and timing;
- utility BESS, UPS, BBU, backup generation, and microgrid roles;
- required duration, power, safety, and response profile;
- co-development of data centres, generation, grid assets, and BESS;
- reuse of existing power infrastructure;
- PPA, interconnection, approval, construction, and operating stage;
- planned versus contracted versus operating capacity;
- conversion of AI-power demand into actual orders, shipments, revenue, or utilisation.

### 6.2 United States, European Union, and China policy and supply-chain rules

Independently inspect:

- proposal;
- adoption;
- implementing rule;
- effective date;
- mandatory application;
- customs or enforcement practice;
- exemption, threshold, transition, and grandfathering;
- judicial or administrative interpretation;
- corporate response.

Check covered products, entities, ownership, origin, content, mineral, component, subsidy, tax-credit, procurement, tariff, export-control, investment-screening, and market-access conditions.

### 6.3 Economic security of battery materials, rare earths, and graphite

Inspect:

- critical-mineral or strategic-item designation;
- government stockpiling;
- price floors, purchase guarantees, and offtake;
- localisation or allied-sourcing requirements;
- policy finance, grants, loan guarantees, and insurance;
- export controls, tariffs, investment screening, and procurement exclusion;
- defence, aerospace, grid, and other strategic demand;
- domestic separation, refining, conversion, and processing capacity;
- supply-chain lead-company designation;
- country-dependence reduction.

Focus on bargaining power, market access, risk allocation, and the mechanism by which government changes private economics.

### 6.4 Price, earnings, and profitability direction

Decompose:

- price;
- volume;
- mix;
- utilisation;
- raw-material cost;
- inventory;
- fixed cost;
- subsidy or tax-credit contribution;
- one-off gains or losses;
- cash flow;
- capex;
- backlog;
- customer and regional demand.

Determine whether the signal is structural demand, inventory normalisation, price pressure, utilisation recovery, policy support, or a one-off accounting effect.

### 6.5 Competitor and customer strategy

Inspect:

- application priorities across EV, ESS, AI power, defence, and small batteries;
- production-footprint relocation;
- JV expansion, reduction, withdrawal, or restructuring;
- customer insourcing versus external procurement;
- supplier replacement, qualification, and dual sourcing;
- chemistry, cell format, pack, packaging, and material selection;
- capex delay, reduction, suspension, or reallocation;
- pricing, warranty, service, and commercial-model changes;
- customer concentration and regional dependence.

Competitor news is not automatically external-news material, but it must be analysed when it changes industry structure, customer demand, or SBTL-relevant positioning.

### 6.6 Technology transition and commercialisation speed

Classify exactly:

1. concept or target;
2. research or paper;
3. prototype;
4. pilot;
5. field demonstration;
6. customer evaluation;
7. qualification;
8. certification;
9. order or offtake;
10. mass-production equipment;
11. production start;
12. commercial shipment;
13. repeat order;
14. profitability or field-performance validation.

Do not convert:

- semi-solid into all-solid-state;
- pilot into commercialisation;
- MOU into supply contract;
- target yield into achieved yield;
- planned capacity into operating output;
- customer evaluation into customer adoption.

### 6.7 Existing-card follow-ups and next confirmation points

Do not classify a story as duplicate merely because actor, asset, project, policy, or topic is already represented.

A standalone follow-up may exist when any of the following changes:

- stage;
- legal rights or duties;
- approval;
- financing;
- scale;
- timing;
- customer or supplier;
- price or economics;
- technical maturity;
- risk probability;
- earnings contribution;
- delay, suspension, reduction, or cancellation probability.

Every applicable card must state the next event or metric that would confirm, weaken, or invalidate the current interpretation.

---

## 7. Decision news-value score — 100 points

The V2 100-point industry-first model is preserved without reducing any weight or scoring discipline.

The three core industrial dimensions carry 70 of 100 points.

Do not double-count the same effect across dimensions.

### A. Market structure and competitive position — 0 to 25

Assess:

- concentration;
- supplier and customer bargaining power;
- entry barriers and switching costs;
- vertical integration;
- control of standards, data, channels, infrastructure, permits, or key inputs;
- ownership and operating models;
- access to grids, sites, customers, capital, procurement, or subsidies;
- recurring-revenue or service models;
- dependence on a country, company, chemistry, or technology;
- market design, dispatch access, capacity remuneration, and revenue-stack availability.

A company transaction receives a high score only when it changes market-level structure or competitive behavior.

### B. Supply, demand, price, and utilisation — 0 to 25

Assess:

- actual and expected supply;
- demand by application, region, customer, and chemistry;
- inventory;
- trade flows, quotas, tariffs, and export controls;
- operating and utilisation rates;
- shortage or surplus expectations;
- price formation and cost curves;
- EV versus ESS demand mix;
- duration, power, safety, and duty-cycle requirements;
- lithium, nickel, cobalt, graphite, LFP, high-nickel, sodium-ion, flow-battery, and recycling relationships.

Capacity discipline:

- planned capacity is not supply;
- permitted capacity is not production;
- nameplate capacity is not utilisation;
- quota is not output;
- tender pipeline is not commissioned demand.

### C. Technology, performance, safety, and operational validity — 0 to 20

Assess:

- cost;
- energy and power density;
- cycle and calendar life;
- charging;
- temperature range;
- degradation;
- recovery rate;
- production yield;
- manufacturability;
- material intensity;
- commercial-scale operability;
- safety, fire, defect, recall, and failure rates;
- maintenance, warranty, insurance, and replacement requirements;
- standardisation, certification, qualification, and field validation.

Technology score caps:

- company target or unsupported claim: maximum 4/20;
- laboratory result without independent validation: maximum 7/20;
- pilot result without commercial-scale evidence: maximum 11/20;
- independent test or customer qualification: maximum 15/20;
- commercial-scale or long-duration field evidence: up to 20/20;
- material recall, defect, fire, warranty, or operating-failure evidence: up to 20/20.

### D. Future cash flow and asset value — 0 to 10

Assess:

- revenue, volume, realised price;
- operating cost and margin;
- utilisation;
- warranty, insurance, remediation, and recall cost;
- capex;
- tax, subsidy, grant, guarantee, and financing cost;
- project NPV, IRR, DSCR, and bankability;
- impairment, stranded-asset, and replacement risk;
- asset and enterprise value.

Transaction size is not the score. Economic transmission is the score.

### E. Law, policy, rights, obligations, and market access — 0 to 10

Assess operative effect on:

- rights and duties;
- product eligibility;
- subsidy, tax-credit, procurement, and financing eligibility;
- tariff, quota, export-control, import-ban, FEOC, local-content, and customs treatment;
- licensing, certification, registration, and permitting;
- battery-passport, traceability, recycling, repair, durability, disclosure, and due diligence;
- enforcement, penalty, recall, refund, remediation, and liability;
- court interpretation;
- ability to enter, remain in, or compete in a market.

Formal status alone does not earn a high score.

Transmission guard:

- entry barriers, procurement access, concentration, grid access, revenue design → A;
- quotas, tariffs, trade, supply, demand, utilisation, price formation → B;
- standards, qualification, safety, durability, repairability, technology pathway → C;
- subsidy value, tax burden, compliance cost, financing, liability, margin, asset value → D;
- legal force, enforceability, rights, duties, eligibility, liability, market-access entitlement → E.

### F. Systemic scale and coverage — 0 to 5

Use a defensible denominator:

- share of global or national supply;
- share of annual demand;
- installed or new storage;
- affected customers, products, operators, or assets;
- geography;
- regional project pipeline;
- economic operators covered;
- company capacity, revenue, or capital exposed.

If no defensible denominator exists, score no more than 2/5 and record `denominator_gap`.

### G. Persistence and irreversibility — 0 to 3

Assess whether the event:

- persists beyond one quarter or one project;
- creates multi-year compliance or switching cost;
- changes supply-chain geography;
- requires hard-to-reverse capex;
- locks in a standard, contract, network, or operating model;
- strands investment;
- invalidates a durable assumption.

### H. Decision urgency and actionability — 0 to 2

Assess whether a decision-maker should promptly change:

- valuation or forecast;
- contract or covenant;
- sourcing or customer strategy;
- compliance systems;
- project schedule;
- alternative supply;
- hedge or inventory;
- permit, warranty, litigation, or enforcement risk.

### Score bands

| Score | Classification |
|---:|---|
| 85–100 | `critical_structural` |
| 70–84 | `high_decision_value` |
| 55–69 | `material_industry_signal` |
| 40–54 | `standard_monitoring` |
| 25–39 | `context_or_reinforcement` |
| 0–24 | `low_independent_value` |

---

## 8. Law and policy effect framework — HARD RULE

Law and policy must be analysed by legal effect and implementation stage, not headline language.

### Stage 0 — rhetoric or advocacy

Political statement, campaign pledge, manifesto, industry request, or non-operative declaration.

Default score cap: 39 unless immediate authority or an independently verified market effect exists.

### Stage 1 — roadmap, study, consultation, or draft standard

Check covered entities, obligations, dates, metrics, budget, and implementing authority.

Default score cap: 54 unless current administrative, procurement, funding, or market practice changes.

### Stage 2 — bill, proposed rule, draft act, or draft budget

Check sponsor, authority, procedural stage, political support, amendment risk, adoption probability, timing, and legal challenge.

Default score cap: 69 unless adoption is highly probable, near, and already causing a material observable effect.

### Stage 3 — enacted law, final rule, adopted standard, or signed legal instrument

Separate:

- adoption date;
- publication date;
- effective date;
- mandatory-application date;
- transition;
- grandfathering;
- delegated implementation still required.

No automatic score floor or ceiling.

### Stage 4 — implementation rule, budget, guidance, registry, eligibility criteria, or programme opening

Assess agency, budget, application process, certification or data system, administrative capacity, timetable, and transitional recognition.

### Stage 5 — enforcement, payment, award, denial, penalty, recall, customs action, or licence action

Assess legal basis, affected party, economic effect, precedent, appeal, and probability of wider enforcement.

### Stage 6 — judicial or tribunal interpretation

Assess court level, finality, appealability, jurisdiction, binding effect, remedy, industry scope, agency response, and legislative response.

### Mandatory legal-policy questions

For every applicable item, answer:

1. What is the exact legal instrument?
2. Which authority issued, adopted, implemented, or enforced it?
3. What procedural stage has actually been reached?
4. Which dates govern adoption, publication, effectiveness, and mandatory application?
5. Which entities, products, activities, and geographies are covered?
6. Which exemptions, thresholds, transitions, grandfathering, or emergency exceptions apply?
7. Which budget, registry, guidance, certification, staffing, or data system is required?
8. What happens on non-compliance?
9. Can the action be appealed, stayed, invalidated, amended, or reversed?
10. Is the effect party-specific, national, regional, extraterritorial, or industry-wide?
11. What is the economic and industrial transmission pathway?
12. What next event determines real implementation?

### Required legal-policy fields

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

Use `not_disclosed`, `not_applicable`, or `not_yet_determined`; do not invent missing legal detail.

---

## 9. Earnings, conference call, and analyst Q&A — HARD RULE

### 9.1 Required evidence universe

For a listed-company earnings candidate, inspect where available:

1. earnings release;
2. exchange or regulator filing;
3. quarterly or annual IR deck;
4. detailed statements and segment results;
5. prepared remarks;
6. complete conference-call or earnings-call recording/transcript;
7. analyst Q&A;
8. correction, FAQ, or supplemental material;
9. prior-quarter and prior-year official language.

Prepared remarks alone are not a completed call review.

### 9.2 Mandatory extraction

- revenue, operating profit, EBITDA, and cash-flow drivers;
- price, volume, mix, utilisation, and raw-material bridge;
- demand by EV, ESS, AI data centre, small battery, defence, and other applications;
- customer inventory correction versus actual orders and shipments;
- new customers, backlog, offtake, qualification, and mass-production timing;
- capex expansion, reduction, delay, cancellation, or reallocation;
- plant utilisation and breakeven;
- inventory write-down, impairment, provision, and one-off item;
- price-decline effect on revenue and margin;
- subsidy, tax-credit, and policy-support contribution;
- regional sales, profitability, and market access;
- management-language change versus the prior period;
- guidance maintained, raised, lowered, or withdrawn;
- future revenue, margin, shipment, utilisation, and capex outlook;
- evasive, conditional, vague, or repeatedly challenged answers.

### 9.3 Q&A is a structural signal

Separately capture:

- new facts first disclosed in Q&A;
- demand, price, utilisation, or capex change versus prior guidance;
- customer, region, product, or application concentration;
- order delay, renegotiation, destocking, or qualification delay;
- prerequisites for margin recovery;
- one-off versus structural profitability;
- commercialisation and mass-production schedule change;
- competitor pricing and customer insourcing;
- policy, tariff, FEOC, localisation, and market-access effects;
- analyst themes repeated across questions;
- management uncertainty or answer avoidance.

### 9.4 Required earnings conclusion

Do not stop at “revenue increased,” “profit declined,” or “turned profitable.”

Explain:

- what moved the numbers;
- price/volume/mix/cost bridge;
- genuine demand versus inventory or one-off effect;
- affected business, customer, region, and application;
- guidance change;
- analyst focus and risk;
- next-quarter confirmation points;
- discrepancy between press release, prepared remarks, Q&A, and prior-period language.

### 9.5 Missing call or Q&A

Record one:

- `earnings_materials_only`
- `prepared_remarks_only`
- `full_call_transcript_available`
- `qna_available`
- `qna_partial`
- `qna_unavailable`
- `call_not_held`
- `transcript_access_blocked`

Without Q&A, do not make definitive conclusions about customer demand, inventory normalisation, utilisation recovery, profitability durability, capex strategy, or new-application revenue contribution.

### 9.6 Required earnings fields

- `earnings_release_checked`
- `filing_checked`
- `ir_deck_checked`
- `prepared_remarks_checked`
- `earnings_call_checked`
- `qna_checked`
- `qna_status`
- `prior_quarter_language_compared`
- `management_guidance_change`
- `analyst_question_themes[]`
- `answer_avoidance_or_uncertainty[]`
- `price_volume_mix_cost_bridge`
- `next_quarter_confirmation_points[]`

---

## 10. Stage A operating rule

Stage A remains selector-only and must not perform external web search or article-body fetch.

Stage A must:

1. assess all current-run stories;
2. separate credibility, cardability, value, and urgency;
3. classify one or more anchor classes;
4. apply Structural Value Override where warranted;
5. inspect all mandatory structural lenses;
6. preserve high-potential unresolved items with a bounded rescue question;
7. screen all baseline relations for duplicate, reinforcement, and material follow-up;
8. identify earnings candidates requiring deep-dive review;
9. record portfolio coverage contribution;
10. apply search-before-delete within the Stage A no-fetch boundary.

### Strict eligibility

A candidate may enter `strict_passed_spec[]` only when:

1. SBTL_HUB lane fit passes;
2. at least one valid anchor class exists;
3. incremental information exists;
4. structural or decision value exists;
5. source direction is plausibly compatible;
6. freshness and staleness treatment is acceptable;
7. duplicate, follow-up, and reinforcement treatment is acceptable;
8. full-schema viability exists;
9. a plausible Stage B source path exists.

**The absence of a conventional corporate execution event is not, by itself, a strict-pass blocker.**

### Stage A routing matrix

| Credibility | Cardability | Decision value | Default route |
|---|---|---:|---|
| PASS | PASS | 70–100 | `strict_passed_spec[]`, subject to all other strict gates |
| PASS | PASS | 55–69 | strict or candidate review based on evidence and duplicate risk |
| PASS | PASS/REVIEW | 40–54 | lower-priority strict, candidate review, or reinforcement |
| REVIEW | PASS/REVIEW | 55–100 | `candidate_review_pool[]` or `structural_signal_review_pool[]` with a mandatory rescue question |
| PASS/REVIEW | REVIEW | any | candidate review, earnings deep dive, reinforcement, or watchlist |
| FAIL | any | any | item-specific reject/support-only only with a valid reason and ledger |

Do not force a minimum number of structural cards. Do not lower evidence standards to improve topic balance.

### Review partitions

- `candidate_review_pool[]` — potentially cardable after bounded clarification;
- `structural_signal_review_pool[]` — high structural potential requiring source, denominator, stage, or comparison rescue;
- `earnings_deep_dive_pool[]` — earnings candidate lacking full call/Q&A or prior-period comparison;
- `watchlist_context_pool[]` — not yet cardable, but a defined future trigger exists;
- `existing_reinforcement[]` — strengthens an existing card without a distinct event;
- `support_source_only[]` — contextual evidence only;
- `rejected[]` — item-specific closure after the applicable review rule.

### Treasure hunting

Stage A must inspect KEEP, REVIEW, STEP2_PENDING, DROPPED, and INPUT_ONLY stories for:

- structural false negatives;
- earnings-call fragments separated from the earnings release;
- material follow-ups misclassified as duplicates;
- AI-power or grid demand hidden inside general energy coverage;
- strategic-mineral or graphite policy hidden inside mining coverage;
- strategy change hidden inside interview or commentary format;
- technology delay or failure hidden inside promotional coverage.

---

## 11. Stage B and authorised rescue

Stage B validates the Stage A anchor and structural thesis. It must not search for an execution event merely to retrofit the candidate into an obsolete selector rule.

Search order:

1. full current source packet;
2. official government, regulator, legislature, court, exchange, standards body, grid operator, company filing, or source-owner material;
3. independent Tier 1/Tier 2 same-event reporting;
4. preceding and follow-up events;
5. denominator and comparison data;
6. policy instrument, dates, exceptions, implementation, and appeal;
7. technology validation and commercial/field evidence;
8. earnings release, filing, IR deck, call, Q&A, and prior-period comparison;
9. repair and enrich;
10. narrow only if evidence remains insufficient;
11. support-only or deletion only after the search and repair ledger is complete.

### Required evidence package additions

- `anchor_classes[]`
- `structural_value_thesis`
- `incremental_information`
- `baseline_expectation`
- `source_discovery_ledger[]`
- `official_source_search_ledger[]`
- `independent_confirmation_ledger[]`
- `earnings_call_qna_ledger[]`
- `prior_statement_comparison`
- `event_or_data_date`
- `source_publication_date`
- `source_direction_check`
- `extracted_evidence[]`
- `missing_evidence[]`
- `next_confirmation_points[]`
- `evidence_package_status`

### No anchor laundering

Never transform:

- strategy into committed investment;
- discussion into contract;
- target into result;
- pilot into commercialisation;
- guidance into confirmed demand;
- vague Q&A into a firm plan;
- capacity ceiling into installed capacity;
- proposed policy into effective rule.

---

## 12. Stage C and downstream validation

Stage C validates both fact safety and value safety.

Check:

- source direction;
- quote quality;
- visible-claim coverage;
- numbers, dates, and event stage;
- fact versus implication;
- anchor-class suitability;
- structural-value thesis;
- incremental information;
- baseline follow-up relation;
- earnings-call and Q&A completeness;
- next confirmation points;
- portfolio contribution.

Do not reject solely because an item is not a contract, investment, construction event, production event, or other execution event.

Revise when:

- implication exceeds evidence;
- execution stage is overstated;
- customer demand is asserted without Q&A or other direct support;
- price, volume, mix, and cost are conflated;
- follow-up incremental information is unclear;
- next confirmation point is absent;
- the card is a mere event summary.

### Post-acceptance content requirement

Every card should answer:

- what happened;
- what changed;
- why it matters now;
- which demand, supply, price, profitability, policy, technology, competition, or risk variable changes;
- whether the prior view is strengthened, weakened, or replaced;
- what remains uncertain;
- what must be checked next.

Required durable value fields:

- `news_value_basis`
- `structural_value_lenses[]`
- `incremental_information`
- `industry_implication`
- `uncertainty_boundary`
- `next_confirmation_points[]`
- `baseline_follow_up_relation`
- `why_standalone_card`

### IB-grade decision-useful content test

A high-quality card should answer, where applicable:

1. What changed?
2. What was the prior state?
3. What uncertainty was resolved?
4. What is legally, financially, technically, competitively, or operationally different?
5. Who and what products, assets, customers, or markets are affected?
6. What is the relevant denominator?
7. What is committed, conditional, proposed, effective, enforced, operating, or still planned?
8. What exceptions, thresholds, conditions, transitions, or appeal risks apply?
9. Through what chain does the event change market structure, supply-demand, technology, cash flow, access, or risk?
10. What measurable next event determines whether the effect is realised?
11. What remains unknown or undisclosed?
12. What action should an investor, operator, supplier, customer, lender, regulator, or legal team reconsider?

Do not answer these questions with generic implications. Use verified facts and bounded inference.

### Signal assignment

`signal = top | high | mid` remains a publication field and must be assigned after the four independent judgments.

Default guidance:

- `top`: decision score 85–100, or 70–84 with exceptional urgency and strong evidence;
- `high`: decision score 70–84, or 55–69 with material lane impact and strong evidence;
- `mid`: decision score 40–69 depending on scope, or a credible execution event with narrower independent value.

No transaction, law, court ruling, policy announcement, funding round, factory event, or earnings headline becomes `top` solely because of its form.

---

## 13. Follow-up and related lifecycle

### Duplicate

- same release or syndicated copy;
- same facts and same stage;
- no new rights, obligations, scale, timing, economics, technology, or risk.

### Material follow-up

- stage change;
- approval, finance, contract, or legal-effect change;
- scale or timing change;
- customer or supplier change;
- profitability or earnings-contribution change;
- delay, cancellation, or risk realisation;
- implementation, enforcement, or judgment;
- qualification, mass production, or commercial shipment.

`related` must reflect event lineage, not mere thematic similarity.

Record:

- predecessor;
- follow-up;
- parallel policy;
- same asset;
- same customer;
- same supply-chain dependency;
- reinforcement only.

Ordinary processing must not remove existing related edges without a separately authorised remediation procedure.

---

## 14. Portfolio coverage audit

A run is not complete merely because every selected card is individually safe.

### Mandatory coverage domains

1. AI data-centre power and ESS demand structure;
2. U.S. policy and supply-chain rules;
3. European policy and supply-chain rules;
4. China policy and supply-chain rules;
5. battery materials, rare earths, and graphite economic security;
6. price, earnings, and profitability;
7. competitor strategy;
8. customer strategy;
9. technology transition and commercialisation;
10. existing-card follow-ups;
11. safety, recall, quality, and operating risk;
12. regional coverage;
13. balance across demand, supply, policy, technology, finance, and risk.

### Zero-coverage treatment

A zero count must not automatically mean “no news.”

Record one:

- `no_material_event_found_after_full_scan`
- `candidate_found_evidence_insufficient`
- `existing_card_reinforcement_only`
- `watchlist_trigger_pending`
- `selector_bias_detected_and_reopened`
- `source_universe_gap`
- `earnings_call_or_qna_gap`
- `regional_source_gap`

Before closing a zero domain, recheck review, watchlist, support, dropped, and full input stories.

### Required artifacts

- `portfolio_coverage_audit.json`
- `structural_lens_coverage.csv`
- `zero_coverage_explanation.json`
- `follow_up_tracker.json`
- `earnings_call_qna_ledger.json`
- `review_pool_repromotion_ledger.json`

---

## 15. Required Stage A fields

Every strict and high-potential review item must include:

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

The eight score components must total the decision score.

For a listed-company result, the template is conditional and must be materialised as follows:

- `earnings_deep_dive_required: true`;
- `qna_status: not_checked_stage_a`;
- `prior_period_comparison_required: true`;
- availability fields must not be `not_applicable`;
- `earnings_rescue_questions[]` must cover every unavailable or unresolved filing, IR, call, Q&A, bridge, guidance, and prior-period item.

Only a non-earnings candidate may use `earnings_deep_dive_required: false` and `qna_status: not_applicable`.

When `structural_value_override_applied: true`, materialise all override fields as follows:

- `structural_value_override_reason` must be non-empty and item-specific;
- `anchor_classes[]` must contain at least one valid non-execution anchor class;
- `evidence_needed_for_stage_b[]` must be a non-empty array of item-specific verification targets;
- every evidence entry must identify both (a) the source, document, dataset, transcript, filing, technical test, or independent-reporting class and (b) the exact claim, metric, stage, date, or uncertainty to verify;
- generic placeholders such as `official sources`, `company materials`, `media reports`, `additional confirmation`, `more evidence`, or equivalent wording are invalid;
- `why_execution_event_not_required` must be non-empty and explain why the verified change is independently decision-useful without a conventional execution event;
- `next_confirmation_points[]` must identify the measurable event or metric that would confirm, weaken, or invalidate the interpretation.

A false override may use empty or null values for the override-only fields.

---

## 16. Stage A summary and decision ledger

Required summary fields:

- `structural_selector_policy_version`
- `structural_selector_policy_file`
- `structural_selector_policy_sha`
- `credibility_cardability_value_urgency_separated`
- `industry_first_weighting_applied`
- `core_industrial_weight_total`
- `anchor_class_counts`
- `structural_lens_coverage_counts`
- `decision_value_classification_counts`
- `critical_structural_candidate_ids[]`
- `high_decision_value_candidate_ids[]`
- `high_value_review_pool_ids[]`
- `structural_signal_review_pool_ids[]`
- `earnings_deep_dive_pool_ids[]`
- `execution_or_formality_bias_findings[]`
- `technology_validation_gap_ids[]`
- `legal_policy_stage_gap_ids[]`
- `follow_up_candidate_ids[]`
- `zero_coverage_domains[]`
- `search_before_delete_applied`

Required decision-ledger columns include:

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
- `review_pool_repromotion_precondition`

Stage A reports must keep separate ranked views for:

1. market structure and competition;
2. supply, demand, price, and utilisation;
3. technology, safety, and operations;
4. law and policy;
5. price, earnings, and profitability;
6. AI power and ESS demand;
7. economic security and strategic materials;
8. execution events;
9. follow-ups.

Do not collapse them into one undifferentiated list.

---

## 17. Anti-regression guard and hard blockers

Block when:

- the four judgments are collapsed;
- score components do not total 100-point scoring logic;
- the 25/25/20 core weights are changed;
- a top candidate lacks the before–after chain;
- an execution, legal, or transaction form is used as the importance explanation;
- a high-potential structural item is rejected solely for lacking a conventional execution event;
- `structural_value_override_applied: true` is used while `evidence_needed_for_stage_b` is not an array, is empty, contains blank, generic, placeholder, duplicate-only, or non-item-specific entries, fails to identify both the evidence target and the exact claim or uncertainty to verify, or while `why_execution_event_not_required` is missing, null, generic, or non-specific;
- a high-value review item lacks a concrete rescue question;
- legal stage, effective date, or implementation is overstated;
- announced capacity is treated as output;
- a systemic claim lacks a denominator;
- a technology claim exceeds its evidence-stage cap;
- earnings analysis is completed without recording call/Q&A status;
- a listed-company earnings candidate uses `qna_status: not_applicable`, omits required earnings availability fields, or lacks prior-period comparison and rescue questions;
- a novelty-capped item exceeds its maximum total score or classification;
- a material follow-up is closed as duplicate without an incremental-information analysis;
- a mandatory structural domain is zero without a recheck and explanation;
- deletion or support-only is finalised before the applicable search-first process;
- a card merely states that an investment, contract, factory, law, or profit result occurred.

Required blocker:

```text
BLOCKED_STRUCTURAL_NEWS_VALUE_SELECTION_INVALID
```

Required blocker output:

- `affected_items[]`
- `missing_or_invalid_fields[]`
- `execution_or_formality_bias_findings[]`
- `recommended_return_stage`
- `no_next_stage_recommendation: true`

Required validator outcomes:

- `structural_value_selector_status = PASS`
- `portfolio_coverage_audit_status = PASS`
- `earnings_call_qna_audit_status = PASS | NOT_APPLICABLE`
- `follow_up_repromotion_audit_status = PASS`
- `execution_event_bias_audit_status = PASS`
- `content_depth_audit_status = PASS`

No Prompt 0.6 or final-QC recommendation is allowed when an applicable validator is missing or nonpassing.

---

## 18. Calibration examples

### Large contract, limited structural value

A 2 GWh BESS contract is credible and cardable. Its priority depends on regional market share, supplier concentration, price benchmark, technology de-risking, customer significance, and system role.

### Grid operating failure, high structural value

Official data showing that a material share of available BESS dispatch is skipped can be more important than a new project announcement because it changes expected revenue and asset value.

### Battery-passport implementation standard

Value depends on mandatory dates, covered batteries, registry readiness, required data, liability, exceptions, and market-access consequences—not merely official adoption.

### Price-moving mine restart

Permission is not output. Assess capacity, physical restart, utilisation, inventory, global denominator, and price transmission.

### Technology breakthrough claim

Apply the evidence-stage score caps. Corporate claims alone do not justify top priority.

### First enforcement

A first customs block, subsidy denial, recall, or exclusion may be highly valuable when it establishes an actionable precedent.

### Earnings headline versus Q&A

A reported profit improvement may be low-value if caused by a one-off credit. A Q&A disclosure that utilisation recovery depends on customer destocking and delayed qualification may be the more important structural signal.

### Material follow-up

A previously carded project entering financing close, losing a customer, delaying commercial operation, or cutting capacity is not a duplicate merely because the project name is unchanged.

---

## 19. Run completion criteria

A structural-selection run is complete only when:

1. the complete source universe is accounted for;
2. strict, review, structural-review, earnings-deep-dive, watchlist, reinforcement, support, and reject outcomes are item-specific;
3. all mandatory structural lenses were inspected;
4. zero-coverage domains have explanations;
5. earnings candidates record call and Q&A status;
6. existing-card follow-ups were separately reviewed;
7. execution-event bias audit passed;
8. every strict candidate has anchor class and news-value basis;
9. every card has incremental information and next confirmation points;
10. evidence and interpretation remain separated;
11. lineage is preserved;
12. portfolio coverage audit passed.

---

## 20. Version and lineage

Every run applying this policy must record:

- `structural_selector_policy_version: STRUCTURAL_NEWS_VALUE_SELECTION_V3`
- `structural_selector_policy_file: docs/STRUCTURAL_NEWS_VALUE_SELECTION.md`
- `structural_selector_policy_sha`
- `credibility_cardability_value_urgency_separated: true`
- `industry_first_weighting_applied: true`
- `core_industrial_weight_total: 70`
- `multi_anchor_class_model_applied: true`
- `mandatory_structural_lenses_applied: true`
- `earnings_call_qna_rule_applied: true`
- `follow_up_probability_review_applied: true`
- `portfolio_coverage_audit_applied: true`
- `search_before_delete_applied: true`

Downstream stages must preserve these fields or explicitly record why a field is not applicable.

---

## 21. Supersession statement

This V3 replace-all policy preserves and operationalises the governing V2 framework:

- four independent judgments;
- before–after and novelty tests;
- 100-point industry-first score;
- 25/25/20 core weighting;
- denominator discipline;
- technology-validation caps;
- legal-policy Stage 0–6;
- anti-execution and anti-formality bias;
- search-before-delete;
- IB-grade decision-useful content;
- Stage A no-fetch boundary;
- signal and blocker discipline.

V3 adds and makes mandatory:

- multiple anchor classes;
- Structural Value Override;
- seven structural discovery lenses;
- full earnings-call and analyst-Q&A review;
- material follow-up probability review;
- explicit portfolio coverage audit;
- anti-regression validators.

Any older rule stating or implying that strict eligibility requires a conventional corporate execution event is superseded.

**Structural value determines editorial priority.  
Anchor class fixes what changed.  
Evidence supports the visible claim.  
The next confirmation point preserves future decision value.**
