# Editorial Value and Completeness Standard V2

**Status:** `ACTIVE_CANONICAL`  
**Version:** `EDITORIAL_VALUE_COMPLETENESS_V2_20260829`  
**Stages:** `0.0C`, `0.1`, `0.6`, `0.7`, `0.7C`, direct-add attestation

## 0. Purpose

Accuracy, cardability, news value, and portfolio completeness are separate obligations. A factually correct subset can still be editorially weak or incomplete.

This document is the canonical portfolio-level standard. Stage A contains the complete item-level operating implementation; there is no separate active Structural News Value or Structural Value Override document.

## 1. Four independent item judgments

Never collapse:

1. `execution_credibility_gate` — is the claimed event/stage plausible and sufficiently current for further work?
2. `independent_cardability_gate` — can this become a distinct full-schema event rather than duplicate/reinforcement/context?
3. `decision_news_value_score` — how much can the verified change alter a professional judgment?
4. `publication_urgency` — how quickly does a decision-maker need the signal?

A high score cannot cure weak evidence or same-event duplication.

## 2. Anchor classes

Use one or more:

- `execution_event_anchor`;
- `policy_regulatory_anchor`;
- `data_financial_anchor`;
- `strategic_behavior_anchor`;
- `technology_commercialization_anchor`;
- `follow_up_probability_anchor`.

A conventional execution event is not required when another anchor independently changes a material decision-relevant judgment. This route must still prove incremental information, cardability, source path, and a before/after judgment chain.

For active V4 outputs, the authoritative route field is:

- `selection_route = execution_anchor_route`; or
- `selection_route = structural_non_execution_route`.

Legacy V3 validator aliases may be materialized for machine compatibility, but they do not create a separate governance layer.

## 3. Mandatory before/after chain

Strict and high-potential review items state:

- `prior_state`;
- `new_verified_fact` (Stage A: fact to verify, not a body-level proof claim);
- `changed_judgment`;
- `uncertainty_resolved`;
- `remaining_uncertainty`;
- `incremental_information`;
- `baseline_expectation_changed`;
- `next_confirmation_points[]`.

The controlling question is: **What previously reasonable judgment changes because this new fact is now known or is sufficiently plausible to justify verification?**

## 4. Decision news-value score — 100 points

Do not double-count the same transmission effect.

### A. Market structure and competitive position — 0–25
Concentration, bargaining power, entry barriers, switching cost, vertical integration, standards/data/channels/infrastructure/permits/input control, grid/site/customer/capital/procurement/subsidy access, recurring service models, dependence, market design, dispatch/revenue-stack access.

### B. Supply, demand, price, and utilisation — 0–25
Actual/expected supply and demand, inventory, trade flows, utilisation, shortage/surplus, price formation, cost curve, application/region/customer/chemistry mix. Planned/permitted/nameplate capacity is not production or utilisation.

### C. Technology, performance, safety, operational validity — 0–20
Cost, energy/power density, life, charging, temperature, degradation, yield, manufacturability, material intensity, field operation, safety/fire/defect/recall, maintenance/warranty/insurance/replacement, certification/qualification.

Technology evidence caps:
- company target/unsupported claim: max 4/20;
- laboratory result without independent validation: max 7/20;
- pilot without commercial-scale evidence: max 11/20;
- independent test/customer qualification: max 15/20;
- commercial-scale or long-duration field evidence: up to 20/20;
- material recall/defect/fire/warranty/operating-failure evidence: up to 20/20.

### D. Future cash flow and asset value — 0–10
Revenue, volume, realised price, operating cost/margin, utilisation, warranty/remediation/recall, capex, tax/subsidy/grant/guarantee, financing cost, project economics, impairment/stranding/replacement risk.

### E. Law, policy, rights, obligations, market access — 0–10
Operative rights/duties, eligibility, tariff/quota/export control/import ban/FEOC/local content/customs, licensing/certification/registration/permitting, passport/traceability/recycling/due diligence, enforcement/liability, court interpretation, market-entry/continuation rights.

### F. Systemic scale and coverage — 0–5
Use a defensible denominator: share of supply/demand/storage, affected customers/products/assets, geography, pipeline, operators, revenue/capacity/capital exposure. No defensible denominator: max 2/5 and record `denominator_gap`.

### G. Persistence and irreversibility — 0–3
Multi-quarter/multi-year persistence, switching/compliance cost, geographic relocation, hard-to-reverse capex, standard/contract/network lock-in, stranded investment, durable assumption change.

### H. Decision urgency and actionability — 0–2
Immediate implication for valuation/forecast, contracts/covenants, sourcing/customer strategy, compliance, schedule, alternate supply, hedging/inventory, permit/warranty/litigation/enforcement risk.

### Score bands

| Score | Classification |
|---:|---|
| 85–100 | `critical_structural` |
| 70–84 | `high_decision_value` |
| 55–69 | `material_industry_signal` |
| 40–54 | `standard_monitoring` |
| 25–39 | `context_or_reinforcement` |
| 0–24 | `low_independent_value` |

## 5. Novelty caps — hard rule

- repeated announcement/republication with no new fact: max 39;
- routine stage progression resolving no material uncertainty: max 54;
- company target without independent execution/validation/current observable market effect: max 54;
- unsupported political rhetoric without operative authority/current verified market effect: max 39.

Corporate prominence, headline amount, or formal legal shape cannot bypass a cap.

## 6. Required structural lenses

Coverage and selection must inspect, where applicable:

1. AI/data-centre power and ESS demand;
2. U.S. policy/supply-chain rules;
3. EU policy/supply-chain rules;
4. China policy/supply-chain rules;
5. critical materials/rare earths/graphite economic security;
6. price/earnings/profitability;
7. competitor strategy;
8. customer strategy;
9. technology transition/commercialisation;
10. existing-card follow-up;
11. safety/quality/operating risk;
12. regional core signals.

These are discovery obligations, not card quotas.

## 7. Earnings hard rule

For listed-company results, inspect where available: release, regulator/exchange filing, IR deck, detailed statements/segments, prepared remarks, full call/transcript, analyst Q&A, corrections/supplements, and prior-period official language.

Extract price/volume/mix/cost, utilisation, raw material, inventory, one-offs, subsidy/tax-credit contribution, cash flow, capex, backlog, customer/application/region demand, guidance change, analyst themes, answer avoidance, and next-quarter confirmation points.

Without Q&A, do not make definitive claims about customer demand, inventory normalisation, utilisation recovery, profitability durability, capex strategy, or new-application revenue contribution. Record actual Q&A availability.

## 8. Law/policy hard rule

Classify legal-policy stage precisely:

0 rhetoric/advocacy; 1 roadmap/consultation/draft standard; 2 bill/proposed rule/draft act; 3 enacted law/final rule/adopted standard/signed instrument; 4 implementation rule/budget/guidance/registry; 5 enforcement/payment/award/denial/penalty/recall/licence action; 6 judicial/tribunal interpretation.

Default value caps: Stage 0 max 39, Stage 1 max 54, Stage 2 max 69; Stages 3–6 have no automatic floor/ceiling.

Separate adoption, publication, effective date, mandatory application, transition/grandfathering, implementation, enforcement, appeal/reversal risk, covered entities/products/geographies, and economic transmission.

## 9. Technology commercialisation ladder

Classify concept/target → research → prototype → pilot → field demonstration → customer evaluation → qualification → certification → order/offtake → mass-production equipment → production start → commercial shipment → repeat order → profitability/field validation.

Never upgrade pilot to commercialisation, MOU to supply contract, target yield to achieved yield, planned capacity to output, or customer evaluation to adoption.

## 10. Existing-event and follow-up value

A later article is not a follow-up by itself. A standalone follow-up may exist when a direct predecessor relationship is proven and stage, legal effect, financing, scale, timing, customer/supplier, price/economics, technical maturity, risk probability, earnings contribution, delay/suspension/reduction/cancellation, or other material judgment changes.

Related lineage is governed separately by `RELATED_LIFECYCLE_CONTRACT.md`.

## 11. Portfolio completeness

Every ordinary full run challenges:

- current canonical full;
- supplied raw;
- trackers/watchlists/review pools/holds;
- related lineages;
- official and high-quality independent sources;
- material corrections/reversals/delays/cancellations/operating results.

Required regions: Korea, North America, China, Japan, Europe, material global markets.

Required topics include cells/chemistries, materials/components, pouch/pouch-film demand, ESS/BESS, EV/charging, manufacturing/capacity/utilisation, grids/AI load, critical minerals, recycling, policy/trade/localisation, competitors/customers, substitute technology, price/cost/margin, financing, safety and operating validation.

## 12. IB-grade dimensions

A publishable item must survive materiality, execution/stage precision, incremental information, decision usefulness, evidence quality, claim completeness, and strategic read-through. Evidence quality, stage precision, and claim completeness are hard gates.

SBTL relevance is classified `direct`, `indirect`, `conditional`, `background_signal`, or `no_direct_link`. Never manufacture a direct pouch-film link.

## 13. Independent 0.7C completeness rounds

1. source-universe accounting;
2. existing-full duplicate/update/follow-up/reinforcement challenge;
3. event-stage and lineage challenge;
4. fact/claim completeness challenge;
5. news-value challenge;
6. exclusion/rescue red-team.

Valid formal completion is bounded, e.g. `PASS_WITH_DECLARED_RESIDUAL_RISK`, with known unknowns and residual risks recorded. Absolute global completeness is not claimed.