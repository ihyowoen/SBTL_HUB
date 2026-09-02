# Fact Discipline V2

**Status:** `ACTIVE_CANONICAL`  
**Version:** `FACT_DISCIPLINE_V2_20260829`  
**Authority:** highest authority for factual claims, numbers, dates, quotes, and fact/inference separation.

## 1. Core rule

If a factual claim was not directly verified from an inspected body-level or official/document source, do not present it as fact. Memory, model training, headline/snippet text, supplied URLs, Stage A metadata, and plausible inference are not evidence.

## 2. Prohibited

- unsupported numbers, dates, capacities, prices, customers, contracts, schedules, rankings, or comparisons;
- remembering prior guidance/roadmaps instead of verifying the current source;
- currency conversion without a source/date basis;
- turning a target, plan, MOU, pilot, evaluation, proposed rule, or forecast into a later execution state;
- reporter/management speculation written as verified fact;
- causal or beneficiary claims that the evidence does not establish;
- silently filling missing fields because a complete-looking card is preferred.

## 3. Evidence candidate versus evidence

A provided URL, `primary_url`, raw story, `usable_text`, search result, RSS/snippet, discovery hit, or source hint is an **evidence candidate** only.

It becomes usable evidence after Stage B or another authorized fetch-enabled stage directly inspects the durable source, records the resolved URL, extracts body/official/document support, maps the support to a claim, and records audit metadata.

Stage A performs no external body fetch and therefore cannot declare evidence completeness.

## 4. `fact_sources` and claim mapping

Every material visible factual claim must be supported by current `fact_sources`/claim coverage. At minimum preserve:

- claim;
- source URL;
- source quote or exact document support under an allowed verified status;
- source publication date where available;
- fetch/check audit timestamp;
- supports/role metadata required by the current Source Audit contract.

Numbers, dates, named counterparties, legal effects, and quotations without support are removed, narrowed, or held.

Source independence/diversity, canonical URL ownership, and derived counters are governed only by `SOURCE_AUDIT_CONTRACT.md`, not duplicated here.

## 5. Date discipline

Separate at least:

- source publication date;
- announcement date;
- representative event date;
- signing/approval/effective/mandatory-application dates;
- construction/production/shipment/operation dates;
- expected future dates.

The card `date` and Story ID use the representative event date under `CARD_ID_STANDARD.md`. The date shown beside source evidence is the source publication date. Fetch/check timestamps are audit-only.

## 6. Fact, gate, and implication

`fact` contains source-supported factual synthesis only.

`gate` may state verified limitations, conditions, stage boundaries, missing confirmation, or what must be checked next.

`implication` is evidence-bounded interpretation. It must be linguistically distinguishable from verified fact and may not introduce unsupported numbers, concrete customer/project claims, causal certainty, or invented beneficiary exposure.

## 7. Comparison discipline

A before/after comparison requires support for both the prior state and new state, or an explicit bounded statement that the prior state comes from a cited prior canonical event/source. Do not reconstruct a historical baseline from memory.

## 8. Earnings and policy

For earnings, do not infer durable demand/utilisation/profitability from one headline metric or a release when Q&A/segment evidence is material and unavailable. Record evidence limitations.

For law/policy, distinguish rhetoric, proposal, adoption, publication, effectiveness, mandatory application, implementation, enforcement, and judicial interpretation. Do not collapse stages.

## 9. Rescue and narrowing

Missing evidence is a verification trigger, not permission to invent. In fetch-enabled stages:

1. inspect/repair the original source;
2. seek official/original material;
3. seek independent same-event evidence;
4. narrow unsupported wording;
5. reinforce an existing card where appropriate;
6. hold/reject only after bounded rescue permitted by the stage.

Stage A rescue means preserving a concrete review/evidence question, not fetching.

## 10. Assistant assertion discipline

Claims such as `all passed`, `clean`, `no issue`, or `N cards are valid` require an executed item-level or repository-level check that supports that exact scope. If not checked, say it is unverified rather than generalizing.

## 11. Final rule

Accuracy outranks completeness of prose. It is correct to leave a claim out; it is incorrect to fill the gap with memory or inference.