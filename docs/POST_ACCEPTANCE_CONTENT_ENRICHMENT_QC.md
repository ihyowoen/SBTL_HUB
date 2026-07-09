# Post-Acceptance Content Enrichment & Evidence QC

## 0. Role of this document

This document defines the reusable **post-acceptance finalization process** for SBTL_HUB news-card runs.

Use this document only after `docs/PROMPT_ABC_DEFAULT_MODE.md` or the current approved A/B/C framework has already produced Prompt C accepted cards.

This document is not a replacement for Prompt A/B/C. It is the downstream process that turns Prompt C accepted cards into production-safe, source-locked, evidence-complete, publish-ready data.

Hard distinction:

```text
Prompt C accepted != publish-ready
Prompt C accepted = accepted_fact_safe candidate only
```

Even after duplicate/event checks, a card is still not publish-ready until evidence completeness, content depth, language/terminology, final QC, and baseline sync gates pass.

Harder distinction proven by the 2026-05-04 dry run:

```text
accepted_fact_safe != addable_merge_safe != evidence_complete != publish_ready
```

---

## 1. Governance hierarchy

When rules conflict, apply this hierarchy:

1. `docs/FACT_DISCIPLINE.md`
2. `docs/PROMPT_ABC_DEFAULT_MODE.md`
3. `docs/PROMPT_ABC_SUPPORTING_RULES.md`
4. `docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md`
5. `docs/CARD_ID_STANDARD.md`
6. `docs/WORKFLOW.md`
7. `docs/OPERATIONS.md`
8. This document

`FACT_DISCIPLINE.md` remains the top source of truth for facts, numbers, quotes, and evidence discipline.

This document governs only the post-acceptance layer:

- merge-safety validation
- evidence completeness validation
- source/claim coverage validation
- visible-field content depth enrichment
- language and terminology polish
- final file naming and QC report decision

If this document conflicts with Fact Discipline, follow Fact Discipline and report the conflict in QC.

---

## 2. Position in the workflow

Prompt A/B/C handles:

```text
Prompt A = Editorial selector / spec builder
Prompt B = Card writer with mandatory source verification
Prompt C = Enhanced red-team validator / formatter
```

This document starts only after Prompt C.

```text
Prompt A/B/C
→ accepted_fact_safe / revise_required / rejected

Post-acceptance process
→ addable_merge_safe
→ evidence_complete
→ content_enriched
→ language_terminology_polished
→ publish_ready
```

This document must not silently reopen Prompt A/B/C decisions unless the user explicitly asks for a new A/B/C pass.

---

## 3. Required state ladder

Do not collapse these states.

```text
accepted_fact_safe
  ↓
addable_merge_safe
  ↓
evidence_complete
  ↓
source_claim_covered
  ↓
content_enriched
  ↓
language_terminology_polished
  ↓
publish_ready
```

| State | Meaning | Not enough for |
|---|---|---|
| `accepted_fact_safe` | Prompt C accepted the card as fact-safe | GitHub merge / publication |
| `addable_merge_safe` | baseline duplicate ID/URL/event checks passed | publication |
| `evidence_complete` | source_quote and fact_sources pass evidence hard gates | publication without content/language QC |
| `source_claim_covered` | visible claims are mapped to source claims | publication without final polish |
| `content_enriched` | visible fields are rewritten to SBTL_HUB depth | publication without language/final QC |
| `language_terminology_polished` | terminology, units, foreign text, and banned phrases pass | publication without final report |
| `publish_ready` | all gates pass and QC report supports final PASS | final GitHub candidate |

Hard rule:

```text
Do not call a file final, PR candidate, GitHub-ready, or publish-ready unless publish_ready=true is supported by QC.
```

---

## 4. Inputs

This stage expects:

1. `ACCEPTED_CARDS_PAYLOAD`
   - Prompt C accepted cards only
   - these are `accepted_fact_safe`, not publish-ready

2. `BASELINE_CARDS_JSON`
   - current GitHub `main` `public/data/cards.json`, unless the user explicitly authorizes another baseline

3. `BASELINE_SOURCE_DECLARATION`
   - `github_main`
   - `local_final_candidate`
   - `user_uploaded_baseline`

4. `RUN_METADATA`, if provided
   - `run_tag`
   - `run_date`
   - expected counts

If the baseline is not GitHub main, the QC report and final response must state that GitHub main sync is still required before PR/merge.

---

## 5. What this stage must not do

This stage must not:

- select new candidates from `final_news_llm_input.stories[]`
- rescue dropped/rejected items without explicit user instruction
- merge accepted cards without QC evidence
- treat web search as silent content enrichment
- add unsupported claims from memory or outside context
- rewrite source fields unless a separate source-augmentation pass is explicitly authorized
- force expected final count when duplicate or evidence holds reduce additions
- preserve `publish_ready=true` through later QC gates without revalidation

If serious evidence issues are found, mark the card as `addable_hold_source_gap`, `needs_source_augmentation`, or `needs_return_to_prompt_c`.

---

## 6. Stage A/B/C audit expectations

These checks are downstream verification requirements. They do not replace Prompt A/B/C.

### 6.1 KEEP is not an editorial pass

`KEEP` is an upstream recommendation, not a final editorial pass.

Prompt A must re-run lane-sanity inside KEEP before producing strict `passed_spec`.

Downgrade to `needs_review` or `rejected` when an item is:

- consumer/lifestyle news
- real estate or model-house news
- weather or local life information
- generic education/culture/publicity
- generic finance/insurance/ETF without battery/materials/ESS/grid/supply-chain relevance
- general politics/diplomacy without direct industrial relevance
- weakly connected to SBTL_HUB lanes

Prompt A output should distinguish:

- `legacy_keep`
- `strict_passed_spec`
- `needs_review`
- `rejected`
- `existing_reinforcement`

### 6.2 Stage B fetch coverage is not final evidence coverage

Stage B may classify source availability/fetch quality, but this is not final evidence coverage.

Use separate concepts:

| Stage | Preferred field | Meaning |
|---|---|---|
| Stage B | `fetch_coverage` or `source_availability` | Whether the source/article appears available enough for Prompt C review |
| Final post-acceptance QC | `evidence_coverage` | Whether final claims are backed by non-headline `source_quote` and valid `fact_sources` |

A Stage B value such as `source_coverage=strong` cannot become final `evidence_coverage=strong` unless final card-level evidence independently passes this document.

### 6.3 needs_review is not rejection

Track review pools separately:

| Pool | Meaning |
|---|---|
| Stage A `needs_review` | lane-sanity review pool; do not auto-fetch unless user opens review run |
| Stage B `needs_review=true` | source/duplicate/lane issue review pool; eligible for later rescue/evidence run |
| Stage C `maybe` | manual review or roundup pool |
| Stage C `dropped` | rejected unless user explicitly reopens |

If a run defers review pools, the report must state:

- deferred intentionally
- not included in current accepted/addable count
- eligible or not eligible for later review

### 6.4 Stage C card-value gate

Strong source availability does not guarantee card value.

Prompt C must separately evaluate:

1. strategic relevance
2. SBTL_HUB lane fit
3. decision usefulness
4. duplicate cluster role
5. source strength

A candidate with strong source availability may still be `dropped` or `support_source_only` if it is not worth an independent SBTL_HUB card.

---

## 7. Merge safety and full baseline revalidation

### 7.1 Merge safety checks

Check accepted payload internally and against baseline for:

- duplicate IDs
- duplicate URLs
- duplicate canonical URLs
- duplicate event fingerprints
- same actor + same asset/policy + same event type + same date
- breaking-news / follow-up / full-report duplicates
- cards that should be `existing_reinforcement` or `withheld_reinforcement`

### 7.2 Event fingerprint

URL matching is not enough. Use event fingerprints.

Recommended fingerprint:

```json
"event_fingerprint": {
  "actor": "...",
  "asset_or_policy": "...",
  "location": "...",
  "event_type": "resource_assessment | financing | plant_construction | earnings | policy_change | contract | partnership | capacity_ramp | other",
  "event_date": "YYYY-MM-DD or null"
}
```

If actor + asset/policy + event_type + event_date are effectively the same, treat it as a duplicate event even when URLs and titles differ.

### 7.3 Full baseline revalidation is merge-safety only

Full baseline revalidation may decide only:

- `addable_merge_safe`
- `duplicate_hold`
- `existing_reinforcement`
- `withheld_reinforcement`
- `baseline_conflict`

It must not assign or preserve `publish_ready=true`.

After full baseline revalidation, every surviving addable card must be reset to:

```json
"publish_ready": false
```

Surviving addable cards may become `publish_ready=true` only after evidence completeness QC passes.

Hard rule:

```text
Full baseline revalidation decides addable/hold only.
It does not decide publish-ready.
```

---

## 8. Evidence completeness QC

Every surviving addable card must pass evidence completeness QC before it can become publish-ready.

### 8.1 Hard-fail conditions

A card fails evidence completeness if any of the following is true:

- `source_quote` is missing
- `source_quote` is headline-only
- `source_quote` is RSS-only
- `source_quote` is snippet-only
- `source_quote` is listing-card text only
- `source_quote` is exact title text
- `source_quote` is a near-title paraphrase without body-level support
- `source_quote_status` is missing, unknown, `headline_only`, `snippet_only`, `not_generated`, or `not_generated_no_direct_quote_extraction`
- `fact_sources` is URL-only
- `claim` is copied from the headline
- `claim` is a label rather than a concrete factual claim
- visible-field numeric claims lack source support
- single-source justification relies on headline-only evidence

No override is allowed for headline-only evidence.

### 8.2 Publish-ready fact_sources schema

For any card marked `publish_ready=true`, each core `fact_sources` entry must include:

```json
{
  "source_name": "...",
  "source_url": "...",
  "claim": "concrete factual claim supported by this source",
  "source_quote": "body-level or official/primary quote, not a headline",
  "evidence_role": "primary_event_evidence | secondary_event_evidence | background_context",
  "supports": ["title", "sub", "fact", "implication"],
  "checked_at": "...",
  "fetch_method": "..."
}
```

`fetched_at` may be used instead of `checked_at` if that is the existing schema.

Invalid for publish-ready:

- URL-only source
- title-only `source_quote`
- headline copied into `claim`
- missing `evidence_role`
- missing `supports`
- `source_quote_status = not_generated_no_direct_quote_extraction`

### 8.3 Evidence roles

Allowed roles:

```text
primary_event_evidence
secondary_event_evidence
background_context
not_used
```

Rules:

- At least one `primary_event_evidence` or strong `secondary_event_evidence` must support the core event.
- `background_context` can support framing only.
- `background_context` cannot rescue a weak event claim by itself.
- Paywall-title, snippet-only, headline-only, repost-only items cannot be counted as independent core evidence.

### 8.4 Single-source exception

Single-source cards can be publish-ready only if the single source is:

- official filing
- government release
- company official release
- regulatory document
- primary dataset/statistics page
- article body with direct source text sufficient for all core visible claims

Single-source cards cannot be publish-ready if the only evidence is:

- RSS headline
- search snippet
- paywall headline only
- listing page title
- repost without body details
- `source_quote` not extracted
- headline-only article card

`single_source_reason` is not a waiver. It must explain why the single source itself is body-level or official primary evidence sufficient for the visible claims.

---

## 9. Source-lock and claim coverage

### 9.1 Allowed evidence universe

Visible-field rewriting may use only:

- `source_quote`
- `fact_sources`
- source fields already present in the accepted card
- newly added sources only if the user explicitly authorized a source-augmentation pass

Do not use memory or outside knowledge to expand claims.

### 9.2 Claim coverage map

All publish-ready cards require claim coverage.

For small addable batches, produce a card-level claim coverage map for every publish-ready candidate.

For large batches, at minimum map:

- title core claim
- sub core claim
- fact core claims
- every numeric claim
- any causal or stage claim

Recommended shape:

```json
"claim_coverage": [
  {
    "card_id": "...",
    "claim": "The concrete visible-field claim being checked",
    "covered_by": ["source_1", "source_2"],
    "coverage_strength": "strong | adequate | weak | missing",
    "action": "kept | narrowed | flagged | excluded"
  }
]
```

### 9.3 Fact vs interpretation separation

- `fact` must contain only verifiable source-backed information.
- `gate` and `implication` may interpret only one step beyond verified facts.
- Every major visible-field claim must trace to at least one source claim.
- If a claim cannot be traced, remove it or narrow it.

---

## 10. Source augmentation and web QC

Final web QC is for:

- verification
- conflict detection
- duplicate detection
- source-strength checking
- source accessibility checking

Final web QC is not silent content enrichment.

Do not use web search to add new facts, numbers, forecasts, causal claims, company intentions, policy effects, or market impact claims unless the user explicitly authorizes a separate source-augmentation pass.

If useful new evidence is found:

- flag it in QC
- state whether it should be added in a source-augmentation pass
- do not silently insert it into visible fields

If source augmentation is explicitly authorized:

- update `fact_sources` with required evidence schema
- include a source-change diff in the QC report
- rerun evidence completeness QC after augmentation

---

## 11. Visible field writing rules

Rewrite only reader-facing visible fields unless explicitly instructed otherwise:

- `title`
- `sub`
- `gate`
- `fact`
- `implication`

Preserve all other fields unless a separate source-augmentation or schema-fix pass is explicitly authorized.

### title

- Include at least two of: actor, action, number/scale, strategic meaning.
- Avoid sensational or translated-title tone.
- Do not expose raw Chinese/Japanese titles.
- Do not force a number if unsupported.

### sub

- Exactly one sentence.
- Include event + scale/number if available + strategic angle.
- Do not introduce claims absent from fact/source coverage.

### gate

- 2–3 sentences.
- Explain why the item matters for the specific lane: materials, ESS, grid, supply chain, policy, EV/battery demand, raw materials/pricing, safety/certification/regulation, manufacturing capacity, trade/localization.
- Do not force SBTL if relevance is weak.

### fact

- Minimum 2 sentences.
- Prefer 3 sentences when source supports enough detail.
- Include actor, region, period/date, business or policy scope, and scale when available.
- Do not include interpretation that belongs in gate/implication.

### implication

- Minimum 2 items.
- Prefer 3 distinct roles:
  1. market / demand structure
  2. supply chain / materials / technology / grid impact
  3. next checkpoint or risk
- Generic phrases such as “주목 필요”, “확인 필요”, “모니터링 필요”, “수혜 예상”, “시장 확대 기대” are banned.

---

## 12. Language, terminology, and banned phrases

Do not treat foreign-language cleanup as only a Han/Kana scan. It is also terminology consistency.

Rules:

- No raw Chinese/Japanese article titles in visible fields.
- Use commonly accepted Korean names for companies/institutions.
- English names may be added once in parentheses only when necessary.
- Do not repeat bilingual names.

Preferred units:

- GWh
- MWh
- MW
- kWh
- 억원
- 조원
- 만톤
- %
- 달러
- 유로
- 위안
- 엔

Normalize:

```text
MW-hours → MWh
megawatt-hours → MWh
gigawatt-hours → GWh
anode → 음극재
cathode → 양극재
separator → 분리막
lithium hydroxide → 수산화리튬
lithium carbonate → 탄산리튬
rare earth → 희토류
critical minerals → 핵심광물
```

Banned visible-field phrases include close variants of:

```text
입력 원문 기준
Stage C
재검증 필요
보강 필요
제작자
검수자
카드화
본 카드
출처 확인 필요
통과 카드
검토 카드
작업자
프롬프트
원문 스니펫
기사 스니펫 기준
확인 필요
모니터링 필요
주목 필요
수혜 예상
시장 확대 기대
fetch
upstream
fallback
prompt
LLM
expected to benefit
market expansion expected
game changer
```

The QC report may mention these phrases when explaining tests. Reader-facing visible fields may not contain them.

---

## 13. Final publish gates

A card/file is publish-ready only if all gates pass.

### Gate 1 — Fact Safety

- every core claim is supported by source_quote or fact_sources
- no unsupported number, causal claim, forecast, benefit claim, company intention, or policy effect

### Gate 2 — Merge Safety

- accepted vs addable separated
- duplicate ID/URL/canonical URL/event checks pass
- baseline duplicate events excluded or documented
- expected final count is not forced

### Gate 3 — Evidence Completeness

- source_quote is body-level or official/primary evidence
- no headline-only or snippet-only evidence
- source_quote_status hard-fail values are zero
- fact_sources are not URL-only
- publish-ready schema is complete
- single-source exceptions are valid

### Gate 4 — Claim Coverage

- title/sub/fact/numeric/stage claims are mapped to source claims
- missing/weak claims are narrowed, held, or excluded

### Gate 5 — Content Depth

- title/sub/gate/fact/implication are reader-facing strategic briefing fields
- fact has 2+ sentences
- gate has 2–3 sentences
- implication has 2+ role-separated items

### Gate 6 — Language & Tone

- raw Chinese/Japanese visible residue is zero
- units and company names are consistent
- SBTL is not forced where direct relevance is weak
- promotional, hype, and workflow language is zero

### Gate 7 — Publish Readiness

- latest-first sort passes
- schema/type drift is zero
- rejected/revise_required/non-accepted cards are not mixed in
- QC report supports final PASS
- GitHub main sync gate is confirmed or explicitly marked as still required

---

## 14. QC report requirements

The QC report must be data-driven, not only checklist-driven.

Report counts for:

- accepted input count
- baseline input count
- addable_merge_safe count
- duplicate_hold count
- addable_hold_source_gap count
- publish_ready count
- expected vs actual final count
- source_quote missing
- source_quote headline-only
- source_quote_status fail
- URL-only fact_sources
- claim copied from headline
- missing evidence_role
- missing supports
- single-source cards
- single-source headline-only cards
- publish_ready true despite evidence fail
- rejected/revise_required/non-accepted mixed into output
- schema/type drift
- latest-first sort result
- baseline source declaration
- GitHub main sync status

If any hard-fail count is non-zero, final QC cannot be PASS.

---

## 15. Required final decision states

After merge-safety and evidence QC, every surviving candidate must be assigned exactly one state:

| State | Meaning |
|---|---|
| `publish_ready` | merge-safety and evidence completeness both pass |
| `addable_hold_source_gap` | duplicate-safe but evidence incomplete |
| `duplicate_hold` | same URL/event/fingerprint already exists in baseline |
| `support_source_only` | useful only as supporting evidence for another card |
| `review_pool_deferred` | intentionally deferred for later review |
| `rejected` | not suitable for this run |

Do not mix states.
Do not treat `addable_hold_source_gap` as publish-ready.

---

## 16. Output naming rules

Do not use these labels in filenames, inventory, or final response unless merge safety and evidence completeness both pass:

- `FINAL`
- `PR_CANDIDATE`
- `publish_ready`
- `GitHub-ready`

If only duplicate/event QC passed, use one of:

- `DUPLICATE_SAFE_ONLY`
- `MERGE_SAFE_PENDING_EVIDENCE`
- `EVIDENCE_QC_HOLD`

Preferred output set after evidence revalidation:

```text
evidence_revalidated_addable_payload_{run_tag}_{N}.json
final_cards_{run_tag}_EVIDENCE_REVALIDATED_{final_count}.json
evidence_qc_report_{run_tag}.md
superseded_and_review_pool_manifest_{run_tag}.json
```

Every superseded or HOLD file must include a reason code:

```text
evidence_qc_failed
headline_only_source_quote
claim_coverage_missing
baseline_duplicate_revalidated
merge_safe_pending_evidence
replaced_by_evidence_revalidated_version
```

---

## 17. Final response format

In the final response, report only:

1. links to generated files
2. accepted input count
3. addable_merge_safe count
4. publish_ready count
5. addable_hold_source_gap count
6. duplicate_hold count
7. baseline count
8. final merged count
9. baseline source declaration
10. QC final decision
11. exceptions, if any

Do not claim completion unless the QC report supports it.
Do not call a file GitHub-ready if GitHub main sync has not been performed.

---

## 18. Final locked rule

```text
Full baseline revalidation decides addable/hold only.
It must reset publish_ready=false for all surviving addable cards.
Publish-ready may be assigned only after surviving addable cards pass evidence completeness QC.
```

If this rule blocks all addable cards, the correct final output is zero publish-ready additions, not a forced final-count match.
