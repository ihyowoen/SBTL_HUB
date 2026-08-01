# Editorial Value and Completeness Standard

**Status:** `ACTIVE_CANONICAL`  
**Stages:** `0.0C`, `0.6`, `0.7C`  
**Version:** `EDITORIAL_VALUE_COMPLETENESS_V1`

## 0. Purpose

This contract prevents SBTL_HUB from becoming a pipeline that merely verifies facts already present in an input file.

Every run must independently challenge:

- whether important news is missing from the input;
- whether an existing card has a material follow-up;
- whether an existing card should be reinforced or corrected;
- whether a candidate represents a new execution stage;
- whether the card contains the facts needed for a decision-useful understanding;
- whether excluded or held candidates contain must-report events that can be rescued through further research.

Accuracy and completeness are separate obligations. A factually correct subset can still be editorially incomplete.

## 1. Stage separation

### Stage 0.0C — discovery and completeness

External search and source-universe expansion are allowed.

Stage 0.0C does not draft cards or decide fact safety. It identifies and structures the authoritative expanded source universe for Stage A.

### Stage A — selector-only

Stage A evaluates the expanded universe. It does not perform external search or fetch article bodies.

### Stage 0.7C — independent final challenge

A separate prompt and artifact challenge the final publish-ready set, exclusions, baseline updates, and coverage completeness.

The authoring pass must not mark its own output complete without this independent review.

## 2. Required coverage universe

Every run must review:

- the current canonical full;
- the new input stories;
- trackers, watchlists, review pools, holds, and unresolved rescue candidates;
- related lineages;
- official sources, company releases, regulators, exchanges, courts, project owners, and reputable independent reporting;
- material corrections, reversals, delays, suspensions, cancellations, and operating results.

The input file is a source candidate universe, not proof of editorial completeness.

## 3. Mandatory regional axes

At minimum:

- Korea;
- United States and North America;
- China;
- Japan;
- Europe;
- material global markets outside those regions.

The global axis must explicitly examine material markets rather than treating them as an undifferentiated remainder.

## 4. Mandatory topic axes

At minimum:

- battery cells and chemistries;
- materials and components;
- pouch-cell and pouch-film demand signals;
- ESS and BESS;
- EVs and charging;
- manufacturing, investment, capacity, and utilization;
- grids, data centers, and AI-related electricity demand;
- critical minerals and refining;
- recycling and circularity;
- policy, regulation, subsidies, trade, sanctions, and enforcement;
- supply-chain localization and diversification;
- competitors, customers, and channel partners;
- substitute technologies;
- prices, costs, margins, and profitability;
- financing and project finance;
- safety, recalls, commissioning, and operating validation.

A run may add more axes but must not silently omit a mandatory axis.

## 5. Event-stage progression

Every material event must be classified by its current execution stage.

```text
statement or plan
→ preliminary discussion or MOU
→ binding contract, order, or offtake
→ financing or public-funding approval
→ FID or final authorization
→ construction start
→ equipment installation
→ commissioning
→ commercial operation
→ expansion or scaled production
→ delay, reduction, suspension, or cancellation
→ operating result or measured outcome
```

A later publication date does not create a follow-up.

A follow-up requires a new material execution anchor, changed obligation, changed economics, changed schedule, changed scale, changed operating result, or material reversal.

## 6. Existing-full challenge

For every candidate that resembles an existing card, classify the relationship as one of:

- `exact_duplicate`;
- `non_material_repetition`;
- `existing_card_reinforcement`;
- `material_follow_up`;
- `stage_transition`;
- `correction_or_reversal`;
- `distinct_new_event`.

The review must ask whether the existing card lacks:

- a new official source;
- a confirmed amount or capacity;
- a changed schedule;
- a counterparty;
- a binding status;
- a funding or regulatory condition;
- an implementation date;
- an operating result;
- a delay, cancellation, or reduction;
- a source needed to support a visible claim.

“Already in the full” is never a terminal reason without this comparison.

## 7. IB-grade standard

`IB-grade` means the item passes all seven dimensions below. It is not a stylistic label.

### 7.1 Materiality

The event changes or materially informs one or more of:

- market size;
- demand;
- supply or capacity;
- price, cost, margin, or profitability;
- competitive position;
- financing or bankability;
- policy obligation or enforcement;
- supply-chain risk;
- technology adoption;
- customer behavior;
- execution probability.

### 7.2 Execution maturity

The card accurately distinguishes statement, MOU, contract, funding, FID, construction, commissioning, operation, and measured outcome.

### 7.3 Incremental information

The card identifies what is new relative to the canonical full and prior reporting.

### 7.4 Decision usefulness

The information could change or sharpen a professional reader’s view of market direction, execution risk, competitive dynamics, policy exposure, or commercial opportunity.

### 7.5 Evidence quality

Visible claims are supported by body-level or official-material evidence under `FACT_DISCIPLINE.md` and `SOURCE_AUDIT_CONTRACT.md`.

### 7.6 Claim completeness

The review checks for omitted facts that materially change interpretation, including:

- amount;
- capacity;
- timing;
- location;
- counterparty;
- ownership or share;
- binding status;
- policy condition;
- effective date;
- project stage;
- source attribution;
- distinction between a total project and one participant’s exposure.

### 7.7 Strategic read-through

The implication explains the decision-relevant meaning within the verified evidence boundary.

SBTL relevance must be classified as:

- `direct`;
- `indirect`;
- `conditional`;
- `background_signal`;
- `no_direct_link`.

A weak direct link must not be manufactured to justify inclusion.

### Hard gates

Evidence quality, execution maturity, and claim completeness are hard gates. A candidate cannot compensate for a hard failure with a high score elsewhere.

## 8. Stage 0.0C outputs

Stage 0.0C must produce:

- `discovered_missing_candidates[]`;
- `baseline_follow_up_candidates[]`;
- `existing_card_reinforcements[]`;
- `correction_or_reversal_candidates[]`;
- `regional_coverage_matrix`;
- `topic_coverage_matrix`;
- `must_report_candidate_ledger[]`;
- `searched_but_no_material_event[]`;
- `source_universe_expansion_ledger[]`.

Every discovered candidate receives a terminal discovery disposition, such as:

- `send_to_stage_a`;
- `existing_update_candidate`;
- `material_follow_up_candidate`;
- `related_add_candidate`;
- `support_source_only`;
- `hold_for_evidence`;
- `excluded_non_material`;
- `exact_duplicate`.

No discovered candidate may disappear between discovery and Stage A.

## 9. Independent Stage 0.7C review

The independent review must run six rounds.

### Round 1 — source-universe completeness

Confirm every input, discovered candidate, and terminal pool is accounted for.

### Round 2 — existing-full challenge

Reassess duplicates, reinforcement, updates, follow-ups, related links, and accidental loss of existing relations.

### Round 3 — event-stage challenge

Confirm the exact stage, new execution anchor, next milestone, and any contrary signal.

### Round 4 — fact completeness

Challenge missing amounts, capacities, timing, counterparties, effective dates, conditions, project stages, and original sources.

### Round 5 — news-value challenge

Ask:

> Would excluding this item cause the reader to miss a material industry development?

> Does including it add decision-useful information rather than promotional repetition?

### Round 6 — exclusion red team

Reopen material held or excluded candidates where:

- source weakness may be curable;
- a follow-up may have been misclassified as duplicate;
- regional or specialist importance may have been underestimated;
- an official implementation source may exist;
- a correction, reversal, delay, or cancellation may have been overlooked.

The default order is:

```text
search first
verify second
expand supported facts third
narrow only when necessary
delete or abandon last
```

## 10. Completeness status

Absolute global completeness cannot be proved from public information.

The valid final status is evidence-based and bounded:

```json
{
  "completeness_status": "PASS_WITH_DECLARED_RESIDUAL_RISK",
  "source_universe_accounted": true,
  "regional_search_complete": true,
  "topic_search_complete": true,
  "baseline_follow_up_review_complete": true,
  "review_pool_rescue_complete": true,
  "must_report_candidates_accounted": true,
  "material_exclusions": [],
  "known_unknowns": [],
  "residual_risks": [],
  "reviewer_independence": "SEPARATE_PASS"
}
```

A simple statement such as “no important news omitted,” “IB-grade,” or “complete” is invalid without the underlying ledgers and matrices.

## 11. Hard blockers

A run cannot enter Prompt 0.8 when:

- a mandatory regional or topic axis was not searched;
- a discovered candidate lacks a terminal disposition;
- a must-report candidate is unaccounted for;
- a likely follow-up lacks an event-stage comparison;
- a material exclusion was not red-teamed;
- a baseline reinforcement or correction was identified but not dispositioned;
- known unknowns or residual risks were suppressed;
- Stage 0.7C was not performed as a separate pass.

Blocked status:

```text
BLOCKED_EDITORIAL_COMPLETENESS_UNPROVEN
```
