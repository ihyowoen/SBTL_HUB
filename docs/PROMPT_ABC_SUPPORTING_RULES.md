# PROMPT ABC — Supporting Rules

## 0. Purpose

This document defines **judgment criteria** used by the pipeline described in `docs/PROMPT_ABC_DEFAULT_MODE.md`.

Role separation between the two documents:

- `PROMPT_ABC_DEFAULT_MODE.md` defines **how** the pipeline flows — stage ownership, authority boundary, input / output contracts, ledger formats, decision taxonomy.
- This document defines **what criteria** each stage applies when judging events, sources, categories, and framing.

Both documents are self-contained for their own scope. If a rule in this document conflicts with `docs/FACT_DISCIPLINE.md`, fact discipline prevails.

This document contains:

1. Signal Rubric — three-axis scoring and threshold mapping for `signal` assignment
2. Source Tier Map — three-tier classification of media credibility
3. Card Selection Criteria — pipeline scope, explicit discard categories, impact weighting
4. Evidence Package Preparation — procedure for fetching and extracting before drafting
5. Daily Run Cycle — frequency requirement
6. Framing Rule — source-direction lock
7. Date Rule — event day vs publication day
8. Framing Self-Verification — three-question checklist used by Prompt B
9. Framing Verification Checklist — review items used by Prompt C

---

## 1. Signal Rubric

Signal is one of `top`, `high`, `mid`. It is determined by scoring three axes (A, B, C) from 0 to 2, then summing.

### 1.1 Axis Definitions

**Axis A — Market size / impact**
- 2 points: annual revenue impact ≥ US$1B, or GWh-scale capacity, or material same-day stock price impact
- 1 point: revenue impact US$100M ~ 1B, or MWh-scale single project
- 0 points: below

**Axis B — Policy / regulation**
- 2 points: government, federal, or EU mandate signed or enacted; or material tariff / subsidy change
- 1 point: draft policy, consultation, guideline release, or subnational decision
- 0 points: no policy dimension

**Axis C — Technology / supply chain**
- 2 points: new mass production start, factory groundbreaking, M&A, or first public technical standard
- 1 point: pilot, prototype, MOU, or joint R&D
- 0 points: no technology / supply dimension

### 1.2 Threshold Mapping

| Total score | signal |
|---|---|
| ≥ 5 | `top` |
| 3 – 4 | `high` |
| 1 – 2 | `mid` |
| 0 | not cardable — discard at Prompt A |

### 1.3 Exception Rule

When a single axis scores 2 and the other two score 0, but the event is objectively important (e.g., a global top-tier supplier starting mass production), `high` may still be assigned. The reason must be recorded in the spec and the card under a dedicated exception note.

### 1.4 Downgrade Constraint

Source Tier 3 with single-source reporting cannot receive `top`. Maximum is `high`, and `needs_review` must be set to `true`.

### 1.5 Recording Format

Each passed spec and each drafted card should carry the rubric scores in a structured form:

```json
"signal_rubric": {
  "A": 1,
  "B": 2,
  "C": 0,
  "total": 3,
  "exception": null
}
```

If the exception rule was invoked, the `exception` field carries the reason string.

---

## 2. Source Tier Map

Source credibility is classified into three tiers. When the same event appears in multiple sources, the highest available tier applies.

### 2.1 Tier 1 — Primary official / verified media

- Government and regulator official announcements (e.g., US state governor offices, European Commission, China MIIT, Korea MOTIE, Natural Resources Canada)
- Listed-company IR, filings, official newsrooms
- Global first-tier wires and financial press (Reuters, Bloomberg, Financial Times, Wall Street Journal, Nikkei)
- Verified industry specialty press (Energy-Storage.news, PV Magazine, Reuters Events, BloombergNEF primary reports)

### 2.2 Tier 2 — National legacy and industry specialty press

- National economic / industry dailies (e.g., 한국경제, 조선비즈, 서울경제, 매일경제, 中国电池联盟(CBEA), OFweek, Gasgoo, CnEVPost, 日刊工業新聞)
- Mid-tier industry specialty press (electrive, pv-tech, Renew Economy, Utility Magazine)
- Major consultancy / research public reports (IEA, IRENA, Aurora Energy Research, Wood Mackenzie, Rystad Energy, BloombergNEF monthly / quarterly summaries)

### 2.3 Tier 3 — Aggregators / blogs / small outlets

- News aggregators, blogs, social media quotes
- Small-outlet sole reporting without cross-verification
- Press release distribution platforms (PR Newswire, CNW, etc.) — identify the original issuer and reclassify to the correct tier

### 2.4 Judgment Rules

- If both Tier 1 and Tier 2 cover the same event, apply Tier 1.
- Tier 3 sole-source → `source_tier: 3` and `needs_review: true`.
- The Tier 1 media registry is maintained in `scope_policy.json`. Additions and downgrades go through that file.

### 2.5 Recording Format

Each passed spec and each drafted card should carry:

```json
"source_tier": 1
```

---

## 3. Card Selection Criteria

### 3.1 Pipeline Scope

This pipeline covers events relevant to:

- battery (cell, pack, materials)
- ESS (grid-scale, behind-the-meter, residential)
- EV (BEV, PHEV, EREV, hybrid large-capacity cells)
- charging (hardware, network, payment, standards)
- battery materials (cathode, anode, separator, electrolyte, pouch film, critical minerals)
- recycling (EOL, second-life, urban mining)
- power grid (when it connects to storage, EV, or data center load)
- industrial policy affecting the above sectors
- adjacent supply chain structures

Events outside these domains are out of scope.

### 3.2 Adjacent Topic Handling

- General renewable energy (solar, wind): included only when co-located with storage or when it materially changes storage economics.
- Nuclear, hydrogen: included only when they directly affect battery / ESS market structure.
- AI and data centers: included when they affect power demand, grid structure, or battery / ESS procurement.
- General climate policy: included only when it carries a concrete mandate on battery / ESS / EV sectors.

### 3.3 Explicit Discard Categories

The following always trigger a `discarded` decision in Prompt A, with a specific `discard_reason`:

- generic homepage or landing page
- static product page with no new event signal
- reference, wiki, or evergreen explainer
- event participation, exhibition, or seminar notice without operational or strategic signal
- general politics, social, or culture news outside §3.1 scope
- pure opinion piece with no factual anchor
- duplicate repost with no incremental signal
- routine personnel appointment without strategic restructuring context
- unverified rumor with no named primary source
- evidence too weak to support a downstream full-schema card

### 3.4 Impact Weighting

Within the pipeline scope, three weighting layers inform signal assignment:

1. **Direct impact on the Korean battery industry** — K-3 cell makers, cathode and anode producers, separator, electrolyte, pouch film, equipment vendors. Maximum weight.
2. **Impact on global competitors or upstream supply chain** that changes the K-battery competitive position. Medium weight.
3. **Macro or background context** — policy trends, demand forecasts, regional market shifts. Lowest weight; included only when the Signal Rubric qualifies the event.

This weighting informs signal placement but does not override the rubric. A macro event cannot receive `top` unless its rubric score independently qualifies.

---

## 4. Evidence Package Preparation

Before Prompt B drafts a card, the primary URL of each passed spec must be fetched and structured into an evidence package. Prompt B drafts cards exclusively from this evidence package plus the spec metadata. Drafting without evidence is prohibited.

### 4.1 Input

- `passed_specs[]` from Prompt A output

### 4.2 Procedure

For every passed spec:

1. **Fetch** the `primary_url` via `web_fetch`.

2. **Handle failure**:
   - If the failure is paywall or login-required: search for an open-access source covering the same event and substitute the URL.
   - If the failure is 404, timeout, or JavaScript-only: attempt a fallback URL from `urls[]` or a newly searched alternate source.
   - If all fallbacks fail: the spec is removed from the Prompt B input set and recorded with a blocked status and failure reason.

3. **Multi-source specs**: if the spec was merged from multiple clusters, fetch the representative URL plus at least one cross-check URL.

4. **Extract** exactly four kinds of information from each successful fetch:
   - **Numbers and quantities** — money, capacity (MW / MWh / GWh), dates, percentages, headcount, volume
   - **Named entities** — companies, people, products, bill or act names, project names, place names
   - **Direct quotes** — on-record statements by named CEOs, chairs, ministers, governors
   - **Explicit comparisons or context stated in the source** — year-on-year comparisons, first-of-kind claims, explicit causal statements

5. **Do not extract** reporter commentary, speculative outlook, or implied context. Those are not usable as fact anchors in the card.

6. **Record** each extracted item with source URL, a 30-character-or-less direct quote from the original text, and fetch timestamp.

### 4.3 Output

An evidence package keyed by `spec_id`, with each entry shaped as:

```json
{
  "spec_id": "...",
  "fetch_status": "success|substituted|blocked",
  "primary_url_used": "...",
  "extracted": [
    {
      "item_type": "number|entity|quote|comparison",
      "item": "...",
      "source_url": "...",
      "source_quote": "...",
      "fetched_at": "ISO8601"
    }
  ]
}
```

Specs with `fetch_status: blocked` do not proceed to Prompt B.

### 4.4 Mapping to `fact_sources`

When Prompt B drafts a card, every number, entity, date, or quoted phrase in `fact` and `implication` must trace back to an extracted item in the evidence package. The `fact_sources[]` array on the card is the mapping layer: one entry per claim, with `claim`, `source_url`, `source_quote`, `fetched_at` fields aligned to extracted items.

---

## 5. Daily Run Cycle

The pipeline runs **at least once per day**. Battery, ESS, and EV industry events occur at daily frequency, and intelligence latency beyond one day degrades analytical value.

- Weekly or multi-day batching is prohibited.
- On weekends or public holidays with no triage output, a run may be skipped. The next active run processes accumulated data normally.
- Within a single calendar day, multiple runs are allowed (e.g., morning and evening passes) and should be tagged with distinct run identifiers.

---

## 6. Framing Rule — Direction Lock

The direction of a card's framing must match the direction of the underlying source material.

### 6.1 Principle

Editorial interpretation is permitted only within the direction of the source. Strong reinterpretation that reverses the source's own framing requires a clearly cited contrary source; otherwise the card is rejected.

### 6.2 Representative Violations

- Source reports "semi-solid-state mass production" → card reframes it as "solid-state commercialization begins". Direction-reversed. Reject.
- Source reports "corporate investment decision" → card reframes it as "policy-driven outcome" without a cited policy source. Invented causation. Reject.
- Source reports "pilot / prototype / MOU" → card reframes it as "commercial deployment". Overclaim. Reject or require revision.
- Source reports "press release from one company" → card reframes it as "industry consensus". Unsupported generalization. Reject.

### 6.3 Prohibited Stylistic Templates

The following patterns are prohibited in `title` and `gate`:

- "X가 아니라 Y다" / "it is not X but Y" — flagged as AI-template framing
- "이 카드의 진짜 의미는 ~이다" / "the real meaning of this card is ~" — flagged as deductive overclaim

### 6.4 Memory-Based Claims

Roadmap years, production timelines, and specific numerical predictions attributed to a named company must appear in the evidence package. Statements such as "Company X plans year Y for technology Z" cannot be written from recall. If the claim is not in the evidence package, it is not in the card.

---

## 7. Date Rule — Event Day vs Publication Day

The `date` field of a card is the **event day**, not the publication day of the source.

### 7.1 Examples

- Law signed on April 13, reported on April 16 → `date: 2026-04-13`
- Plant begins production on April 16, reported the same day → `date: 2026-04-16`
- Company announces Q1 earnings on April 30, media summaries appear May 1 → `date: 2026-04-30`

### 7.2 Uncertain Cases

If the source does not specify the event day clearly, use the earliest date explicitly stated as the event trigger. If still unclear, use the publication day and set `needs_review: true`.

---

## 8. Framing Self-Verification (Prompt B)

Immediately after drafting each card, Prompt B answers three self-check questions:

1. Does the direction of `fact` match the direction of the source material?
2. Does `title` compress `fact` faithfully, or does it add interpretation that changes direction?
3. Does `implication` extend `fact` observationally, or does it invent a new fact?

If any answer is uncertain, set `needs_review: true`.
If any answer is clearly "direction-reversed" or "invented fact", rewrite the offending field before emitting the draft.

---

## 9. Framing Verification Checklist (Prompt C)

During review, Prompt C applies a dedicated framing pass alongside schema, traceability, and separation checks. The framing pass confirms:

- `title` and `gate` travel in the same direction as the source material (§6)
- the card does not reframe a semi-solid-state event as solid-state, a pilot as commercial, an MOU as a signed deal, a press release as industry consensus, or similar direction reversals
- the card avoids the prohibited stylistic templates from §6.3
- no company roadmap year or specific timeline claim appears in the card without direct support in the evidence package

### 9.1 Decision Outcomes

- Minor framing drift that can be rewritten without changing facts → `revise_required`
- Framing-direction reversal relative to source → `rejected`
- Memory-based claim that cannot be anchored in the evidence package → `rejected`

Framing reversal, even without a single-number error, is grounds for rejection. Prose quality does not substitute for framing integrity.
