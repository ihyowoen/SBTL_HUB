# Post-Acceptance Content Enrichment & Final QC

## 0. Role of this document

This document defines the reusable **post-acceptance enrichment and final QC** layer for SBTL_HUB news-card runs.

Use this document **only after `docs/PROMPT_ABC_DEFAULT_MODE.md` or the current approved A/B/C framework has already produced Prompt C accepted cards**.

This document is not a replacement for Prompt A/B/C.
It is a downstream finalization layer that turns accepted cards into production-safe, source-locked, publish-ready data.

Key distinction:

```text
Prompt C accepted != publish-ready
Prompt C accepted = fact-safe candidate only
```

A card is not publish-ready until it has passed merge safety, source coverage, content depth, language/terminology, and final QC gates under this document.

---

## 1. Governance hierarchy

When rules conflict, apply the current project hierarchy from `docs/PROMPT_ABC_DEFAULT_MODE.md`.

Priority:

1. `docs/FACT_DISCIPLINE.md`
2. `docs/PROMPT_ABC_DEFAULT_MODE.md`
3. `docs/PROMPT_ABC_SUPPORTING_RULES.md`
4. `docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md`
5. `docs/CARD_ID_STANDARD.md`
6. `docs/WORKFLOW.md`
7. `docs/OPERATIONS.md`
8. This document

Important inheritance:

- `FACT_DISCIPLINE.md` remains the top source-of-truth for facts, numbers, quotes, and evidence discipline.
- Prompt A/B/C remains the authority for selection, drafting, source verification, revise/reject decisions, and C-stage fact-safe acceptance.
- This document governs only the **post-acceptance visible-field enrichment, source-lock preservation, merge packaging, final QC, and publish-ready decision**.

If this document conflicts with Prompt A/B/C or Fact Discipline, do **not** follow this document. Report the conflict in the QC report.

---

## 2. Position in the latest workflow

The current Prompt A/B/C default mode is the **Final-input era** workflow.

Input universe for A/B/C:

```text
final_news_llm_input.stories[]
```

Prompt A/B/C handles:

```text
Prompt A = Editorial Selector / spec builder
Prompt B = Card Writer with mandatory source verification
Prompt C = Enhanced Red Team + Cross-Functional Validator + Formatter
```

This document starts **after Prompt C**.

```text
Prompt A/B/C
= selection, drafting, source verification, red-team validation, accepted/revise/reject decision

Post-Acceptance Content Enrichment & Final QC
= accepted payload merge-safety check, source-lock/source-coverage review, visible-field depth pass, language polish, final web QC, baseline merge, QC report, publish-ready decision
```

This means:

- A/B/C decides **what survives**.
- Prompt C produces `accepted_fact_safe` cards.
- This document separates `accepted_fact_safe` from `addable_merge_safe`, `source_enriched`, `content_enriched`, and `publish_ready`.
- This document must not silently reopen Prompt A or Prompt C decisions unless the user explicitly asks for a new A/B/C pass.

---

## 3. Required state ladder

Do not collapse the following states.

```text
accepted_fact_safe
  ↓
addable_merge_safe
  ↓
source_enriched or source_coverage_reviewed
  ↓
content_enriched
  ↓
language_terminology_polished
  ↓
publish_ready
```

Definitions:

| State | Meaning | Not enough for |
|---|---|---|
| `accepted_fact_safe` | Prompt C accepted the card as fact-safe | GitHub merge / publication |
| `addable_merge_safe` | baseline duplicate ID/URL/event checks passed, or exclusions documented | publication without content/source QC |
| `source_enriched` | source layer was strengthened with approved same-event evidence | publication without content QC |
| `source_coverage_reviewed` | no safe new source was added, but source coverage was reviewed and single-source reasons were documented | publication without content QC |
| `content_enriched` | visible fields were rewritten to SBTL_HUB publish-quality depth | publication without final QC |
| `language_terminology_polished` | foreign visible text, unit/name drift, and banned phrases were removed | publication without final QC |
| `publish_ready` | all final gates passed and QC report supports the decision | final GitHub candidate |

Hard rule:

```text
Do not call a file “final GitHub candidate” unless publish_ready=true.
```

---

## 4. What this stage must not do

This stage must not:

- select new candidates from `final_news_llm_input.stories[]`
- rescue dropped/rejected items
- discard accepted cards silently
- merge accepted cards silently without QC evidence
- rewrite source fields except when the user explicitly authorizes a separate source-augmentation pass
- change schema shape
- create new cards from scratch
- treat web search as a silent enrichment source
- bypass Prompt A/B/C or Fact Discipline
- convert `accepted_fact_safe` into `publish_ready` without source, duplicate, content, language, and final QC gates

If a serious issue is discovered during this stage, the correct action is:

1. narrow the visible wording if the issue is a wording/source-lock problem;
2. mark the card as `needs_return_to_prompt_c` or `needs_source_augmentation` in the QC report if it cannot be fixed within this stage;
3. document whether the card was excluded from `addable_merge_safe` or kept with an exception.

---

## 5. Inputs

This stage expects:

1. `ACCEPTED_CARDS_PAYLOAD`
   - cards already accepted by Prompt C or the current approved final validator
   - these are `accepted_fact_safe`, not automatically publish-ready
   - not raw `KEEP`, `REVIEW`, `DROPPED`, `STEP2_PENDING`, `INPUT_ONLY`, collector, refined, or triage-only data

2. `BASELINE_CARDS_JSON`
   - current GitHub `main` `public/data/cards.json`
   - this is the only canonical baseline unless the user explicitly authorizes another baseline

3. `BASELINE_SOURCE_DECLARATION`
   - one of:
     - `github_main`
     - `local_final_candidate`
     - `user_uploaded_baseline`
   - if the baseline is not `github_main`, the final response and QC report must state that the output is based on a local/user-provided candidate and must still be synced against GitHub main before PR/merge

4. `RUN_METADATA`, if provided
   - `run_tag`
   - `run_date`
   - `expected_new_card_count`
   - `expected_baseline_count`
   - `expected_final_count`

If `BASELINE_CARDS_JSON` is not from GitHub `main`, do not pretend it is canonical. Continue only if the user explicitly authorizes the local/user baseline, and mark the final output as requiring GitHub main sync before PR/merge.

If only `final_news_llm_input.stories[]` is provided, this document is not the starting point. Run Prompt A/B/C first.

If only raw `triage_output`, `rescue`, or `dropped` files are provided, do not use this post-acceptance prompt as the first step. Resolve the active input mode under `docs/PROMPT_ABC_DEFAULT_MODE.md` and project governance first.

---

## 6. Upstream requirements this document expects from A/B/C

This document is downstream, but the final QC must verify that upstream outputs carried enough auditability.

### Prompt A should provide discard/merge taxonomy

For every non-passed unit from `KEEP`, `REVIEW`, and `STEP2_PENDING`, Prompt A should preserve a ledger outcome and reason code.

Recommended reason codes:

```text
baseline_duplicate
existing_reinforcement
stale_republication
low_signal
non_scope
source_weak
event_too_small
already_covered_by_broader_card
integrity_group_duplicate
manual_review_required
```

### Dropped treasure hunt marker

The source file may be recommended for `dropped_review_treasure_hunt`. Prompt A should state whether a dropped treasure hunt was performed.

Recommended QC object:

```json
"dropped_treasure_hunt": {
  "performed": true,
  "sample_size": 50,
  "rescued": 0,
  "notes": "..."
}
```

This post-acceptance document must not run dropped treasure hunt itself, but the QC report should flag if a run appears to have skipped it when the user expected it.

### Prompt B should provide source coverage

Prompt B should not use web/source checks only as hidden reasoning. If a source supported acceptance, it should either appear in `fact_sources` or be documented as not included.

Recommended source coverage object:

```json
"source_coverage": {
  "unique_source_count": 2,
  "primary_source_type": "official | filing | government | media | industry | other",
  "secondary_source_type": "official | filing | government | media | industry | none | other",
  "single_source_reason": null,
  "not_included_sources": [
    {
      "url": "...",
      "reason": "repost | snippet_only | paywall_headline | background_only | duplicate_source | user_not_authorized"
    }
  ]
}
```

---

## 7. Absolute scope control

Rewrite ONLY the following reader-facing visible fields:

- `title`
- `sub`
- `gate`
- `fact`
- `implication`

Preserve all other fields exactly as they are unless the user explicitly instructs otherwise.

Do not modify:

- `id`
- `region`
- `date`
- `cat`
- `sub_cat`
- `signal`
- `signal_rubric`
- `source_tier`
- `source_quote`
- `fact_sources`
- `url`
- `urls`
- `source_urls`
- `primary_url`
- `created_at`
- `updated_at`
- `run_tag`
- `related`
- `tags`
- any other metadata, source, ranking, or app-runtime fields

Exception:

- If the user explicitly authorizes a separate **source-augmentation pass**, source fields may be updated, but this must be a separately named operation and must include a source-change diff in the QC report.
- Without that authorization, do not clean, rewrite, delete, or silently supplement `fact_sources` or `source_quote`.

Do not normalize the schema.
Do not rename keys.
Do not change ID formats.
Do not change URL formats except for duplicate-check canonicalization performed only inside the QC report.
Do not change array fields into strings or string fields into arrays unless the existing schema for that field already requires it.

Preserve the original data type and schema shape of each visible field:

- If `implication` is an array, keep it as an array.
- If `implication` is a string, keep it as a string unless the user explicitly asks to convert it.
- If `fact` is a string, keep it as a string.
- If any visible field is missing, create it only if the surrounding schema clearly supports that field; otherwise flag it in QC before changing structure.

---

## 8. Source-lock and claim coverage rules

### 8.1 Allowed evidence universe for visible rewriting

The allowed evidence universe for rewriting visible fields is limited to:

- `source_quote`
- `fact_sources`
- source fields already present in the accepted card

Do not use memory or outside knowledge to expand claims.
Do not use web search to add new facts into visible fields unless the user explicitly authorizes a separate source-augmentation pass.

### 8.2 Fact Discipline inheritance

This stage does not weaken Fact Discipline.

In particular:

- no unsupported numbers
- no unsupported causal claims
- no unsupported projections
- no unsupported company intention
- no unsupported benefit or demand claims
- no paraphrased quote masquerading as source_quote
- no fact claim that cannot be traced to source_quote or fact_sources

If the accepted payload itself appears to violate Fact Discipline, do not silently fix by inventing evidence. Narrow visible wording where possible and flag the issue in QC.

### 8.3 No stage inflation

Do not convert a weaker stage into a stronger stage.

Examples:

- plan → confirmed execution is forbidden
- proposal → final rule is forbidden
- under review → approved is forbidden
- MOU → binding contract is forbidden
- announcement → commercial operation is forbidden
- construction start → confirmed battery/material demand is forbidden
- company guidance → verified market outcome is forbidden
- analyst interpretation → company intention is forbidden

### 8.4 Fact vs interpretation separation

- `fact` must contain only verifiable source-backed information.
- `gate` and `implication` may interpret, but only one step beyond verified facts.
- Every major visible-field claim must be traceable to at least one `source_quote` or `fact_sources` entry.
- If a claim cannot be traced, remove it or narrow it.

### 8.5 Claim coverage map

The QC report should include a claim coverage summary for each new card, especially where source support is thin.

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

### 8.6 Weak source handling

Do not rely on the following as the sole basis for a core claim:

- search snippet
- paywalled headline only
- copied press-release repost without independent detail
- vague secondary summary
- article title without body support
- social media text unless it is the primary source for the event

Headline-only evidence is not sufficient for:

- numbers
- causality
- forecasts
- commercial impact
- policy effect
- company intention
- market share
- demand impact

If source support is weak, write more narrowly and conservatively.
If sources conflict, use the more conservative version and flag the issue in the QC report.

---

## 9. Evidence role classification

When source evidence is reviewed or augmented, classify each source role.

Allowed evidence roles:

```text
primary_event_evidence
secondary_event_evidence
background_context
not_used
```

Rules:

- At least one `primary_event_evidence` or strong `secondary_event_evidence` should support the core event.
- `background_context` can support framing only. It cannot rescue a weak card by itself.
- Paywall-title, snippet-only, or repost-only items cannot be counted as independent evidence for a core claim.
- If a card remains single-source, the QC report must include `single_source_reason`.

Hard rule:

```text
Do not promote a revise_required card to accepted/publish-ready using background_context only.
```

---

## 10. Final web QC rules

If web search is available, perform a targeted final QC web check before producing the final files.

This final web QC does **not** replace Prompt B's mandatory `web_fetch` requirement under `docs/FACT_DISCIPLINE.md`.
Prompt B remains responsible for source verification before fact writing; this stage only performs post-acceptance verification, conflict detection, duplicate detection, and source-strength checks.

The purpose of web search at this stage is:

- verification
- conflict detection
- duplicate detection
- source accessibility/source-strength checking

The purpose of web search is **not** content enrichment.

Use web search only for:

- confirming that source URLs match the event described in the card
- checking whether actor, date, number, project name, location, and stage are consistent with public source evidence
- detecting duplicate events between `ACCEPTED_CARDS_PAYLOAD` and `BASELINE_CARDS_JSON`
- identifying whether a source is only a search snippet, paywalled headline, repost, or weak secondary summary
- detecting conflicts between `source_quote`, `fact_sources`, and publicly available source text
- checking whether a breaking-news item has a fuller follow-up article that changes the event stage
- checking whether the same event already appears in baseline under a different title, URL, or follow-up article

Do not use web search to:

- add new numbers to visible fields
- add new forecasts
- add new causal claims
- add company intentions
- add policy effects
- add market impact claims
- strengthen implications beyond the existing fact_sources
- silently replace or override fact_sources
- rewrite a card around a newly discovered external article without user approval
- bypass Prompt B's source verification or Prompt C's acceptance decision

If web search finds useful new evidence:

- do not insert that evidence into visible fields automatically
- flag it in the QC report
- state whether the source should be added to `fact_sources` in a future source-augmentation pass
- only use it in visible fields if the user explicitly authorizes source augmentation

If web search contradicts `source_quote` or `fact_sources`:

- narrow the visible field wording
- avoid the disputed claim
- flag the contradiction in QC
- do not decide the conflict silently
- do not strengthen the claim using whichever source seems more convenient

If web search is unavailable:

- proceed with `source_quote` and `fact_sources` only
- state in the QC report that external web QC was not performed

---

## 11. Visible field writing rules

Write visible fields in polished Korean unless the user explicitly requests another language.
Use an executive briefing tone suitable for C-level readers, strategy teams, and institutional investors.
Avoid casual, promotional, blog-style, machine-translated, or hype-driven phrasing.

### 11.1 title

Goal:
The reader should understand who did what, at what scale if available, and why the item matters strategically.

Rules:

- Include at least two of the following: actor, action, number/scale, strategic meaning.
- Avoid sensational language.
- Avoid direct translation tone from the original article title.
- Do not expose raw Chinese or Japanese titles.
- Do not use internal workflow terms.
- If writing in Korean, prefer roughly 45–75 Korean characters.
- If no number is source-backed, do not force one.
- Do not overfit the title to SBTL unless the source-backed connection is direct.

### 11.2 sub

Goal:
One sentence that explains what happened, the scale if available, and why the item deserves attention.

Rules:

- Exactly one sentence.
- Include event + scale/number if available + strategic angle.
- Do not write a generic summary.
- Do not use empty phrases such as “needs attention,” “important issue,” or “worth monitoring.”
- If the source has no number, describe the qualitative shift.
- Do not introduce a new claim that is absent from fact.

### 11.3 gate

Goal:
Explain why the item matters in 2–3 sentences.

Rules:

- 2–3 sentences.
- No generic industry commentary.
- Use only the angle directly connected to the card: materials, ESS, grid, supply chain, policy, EV/battery demand, raw materials/pricing, safety/certification/regulation, manufacturing capacity, trade/localization.
- Do not force an SBTL angle.
- Do not mention SBTL unless the connection is direct, relevant, and source-supported.
- If mentioning SBTL, avoid benefit claims. Use watch point / relevance / exposure / possible connection language instead.
- Explain the decision point created by the news, not merely that it is important.

### 11.4 fact

Goal:
Reconstruct only verifiable facts in 2–3 sentences.

Rules:

- Minimum 2 sentences.
- Prefer 3 sentences when the source supports enough detail.
- Include actor, region, date/period, business or policy scope, and scale when available.
- Do not copy long article wording.
- Do not add unsupported numbers.
- Clearly distinguish current stage: announced, proposed, under review, MOU signed, approved, contract signed, construction started, operation started, earnings reported, final rule issued.
- Do not include interpretation that belongs in gate or implication.

### 11.5 implication

Goal:
Provide at least 2 implications, preferably 3.

Rules:

- Preserve the existing field type and schema shape.
- Minimum 2 implication items.
- Prefer 3 items with distinct roles:
  1. market / demand structure
  2. supply chain / materials / technology / grid impact
  3. next checkpoint or risk
- Concrete checkpoint language is allowed.
- Generic checkpoint language is banned.

Bad implication examples:

```text
주목 필요
확인 필요
모니터링 필요
수혜가 예상된다
시장 확대가 기대된다
```

Good implication shape:

```text
- Market/demand: what changed in demand structure or buyer behavior
- Supply/technology/grid: what specific part of the value chain is affected
- Checkpoint/risk: what next milestone, filing, contract, operation start, capacity ramp, or policy text would confirm the signal
```

---

## 12. Banned phrases in visible fields

The following phrases, including close equivalents and case-insensitive variants, must not appear in `title`, `sub`, `gate`, `fact`, or `implication`.

English:

- input text basis
- based on input text
- Stage C
- needs re-verification
- needs reinforcement
- producer
- reviewer
- cardization
- this card
- source verification needed
- fetch
- upstream
- fallback
- draft
- pending
- rescue
- hard block
- soft block
- passed card
- review card
- operator
- prompt
- LLM
- original snippet
- article snippet basis
- needs confirmation
- needs monitoring
- needs attention
- expected to benefit
- market expansion expected
- game changer

Korean:

- 입력 원문 기준
- Stage C
- 재검증 필요
- 보강 필요
- 제작자
- 검수자
- 카드화
- 본 카드
- 출처 확인 필요
- 통과 카드
- 검토 카드
- 작업자
- 프롬프트
- 원문 스니펫
- 기사 스니펫 기준
- 확인 필요
- 모니터링 필요
- 주목 필요
- 수혜 예상
- 시장 확대 기대
- 게임체인저

The QC report may mention these phrases when explaining test results.
Reader-facing visible fields may not contain them.

---

## 13. Language, names, and units

Do not treat foreign-language cleanup as only a Han/Kana character scan. It is also a terminology consistency pass.

Rules:

- Do not expose raw Chinese or Japanese article titles in visible fields.
- Do not leave Chinese Han characters or Japanese Kana in visible fields unless unavoidable as part of an official legal name; if used, explain in QC.
- Use commonly accepted Korean names for companies and institutions.
- English names may be added once in parentheses only when necessary.
- Do not repeat bilingual names multiple times in the same card.

Preferred unit style:

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

Banned/normalize:

- `MW-hours` → `MWh`
- `megawatt-hours` → `MWh`
- `gigawatt-hours` → `GWh`
- `RMB` without explanation → `위안` if source meaning is clear
- awkward untranslated source units

Recommended terminology dictionary:

```text
anode → 음극재
cathode → 양극재
separator → 분리막
lithium hydroxide → 수산화리튬
lithium carbonate → 탄산리튬
rare earth → 희토류
critical minerals → 핵심광물
battery energy storage system → BESS or 배터리 에너지저장장치
MW-hours → MWh
```

Do not convert currencies unless the source itself provides the converted value or the user explicitly instructs you to convert using a stated FX rate.

---

## 14. Merge safety and duplicate event rules

### 14.1 Accepted payload internal check

Check for:

- duplicate IDs
- duplicate URLs
- duplicate canonical URLs
- duplicate events
- same actor + same date + same project
- breaking-news / follow-up / full-report duplicates

### 14.2 Baseline vs accepted payload check

Check for:

- same URL
- same canonical URL
- same event
- same actor + same date + same project
- duplicate breaking-news/full-report coverage
- accepted cards that are merely rewritten versions of existing baseline cards

### 14.3 Event fingerprint

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

Hard rule:

```text
If actor + asset_or_policy + event_type + event_date are effectively the same, treat it as a duplicate event even when URLs and titles differ.
```

If a Prompt C accepted card duplicates a baseline event, do not add it as a new card. Mark it as `withheld_reinforcement` or `existing_reinforcement` and document the reason.

### 14.4 Canonical URL check

For duplicate-check purposes only, canonicalize URLs by:

- lowercasing scheme/host
- removing clear tracking parameters
- removing trailing slash
- treating http/https versions of the same host/path as potential duplicates

Preserve original URLs in actual data.

### 14.5 Merge behavior

- Use `BASELINE_CARDS_JSON` as the base.
- Merge enriched accepted cards into the baseline only after `addable_merge_safe=true`.
- Do not modify existing baseline cards unless explicitly instructed.
- Maintain latest-first sorting.
- Do not force expected_final_count if duplicates or exclusions are found.

Sorting rule:

1. date descending
2. if available, published_date / created_at / updated_at descending within the same date
3. preserve existing baseline relative order where dates are identical and no better timestamp exists
4. place accepted cards naturally within their date group

If a card has missing or invalid date, do not invent a date. Keep the original value and flag it in QC.

---

## 15. Final publish gates

A file is `publish_ready` only if all six gates pass.

### Gate 1 — Fact Safety

- every core claim is supported by `fact_sources` or `source_quote`
- source_quote does not contradict visible fields
- no unsupported number, causal claim, forecast, benefit claim, company intention, or policy effect

### Gate 2 — Merge Safety

- accepted vs addable cards are separated
- duplicate ID/URL/canonical URL/event checks pass
- baseline duplicate events are excluded or documented
- expected final count is treated as a check, not forced

### Gate 3 — Source Layer

- source coverage was reviewed
- single-source cards have `single_source_reason`
- background-only support is not used as event proof
- claim coverage summary exists for weak or important cards

### Gate 4 — Content Depth

- title/sub/gate/fact/implication are reader-facing strategic briefing fields, not raw summaries
- fact has 2+ sentences
- gate has 2–3 sentences
- implication has 2+ items and role separation

### Gate 5 — Language & Tone

- raw Chinese/Japanese visible residue is 0
- units and company names are consistent
- SBTL is not forced where direct relevance is weak
- promotional, hype, and workflow language is 0

### Gate 6 — Publish Readiness

- latest-first sort passes
- schema/type drift is 0
- rejected/revise_required/non-accepted cards are not mixed in
- QC report supports final PASS
- GitHub main sync gate is still required before PR/merge if baseline was local or user-uploaded

---

## 16. QC requirements

Before finalizing, produce a QC report with PASS/FAIL for each item.

### A. Count checks

- accepted input count
- baseline input count
- expected final count, if provided
- actual final merged count
- addable card count
- withheld reinforcement count
- rejected/revise_required/non-accepted mixed into output: must be 0
- whether every accepted card was included or explicitly excluded with reason

### B. Preservation checks

- fact_sources deleted: must be 0
- source_quote deleted: must be 0
- source URLs deleted: must be 0
- non-visible fields changed: must be 0 unless explicitly authorized
- ID changed without instruction: must be 0
- URL changed without instruction: must be 0
- schema/type drift: must be 0

### C. Visible field checks

- cards with fewer than 2 implications: must be 0
- cards with fact shorter than 2 sentences: must be 0
- cards with gate shorter than 2 sentences: must be 0
- cards with sub longer than 1 sentence: must be 0
- raw Chinese/Japanese remaining in visible fields: must be 0
- banned workflow phrases remaining: must be 0
- unsupported numbers added: must be 0
- unsupported causal claims added: must be 0
- unsupported forecast or benefit claims added: must be 0
- promotional or hype language remaining: must be 0

### D. Duplicate checks

- duplicate IDs among accepted cards
- duplicate URLs among accepted cards
- duplicate canonical URLs among accepted cards
- duplicate event fingerprints among accepted cards
- duplicate events between baseline and accepted cards
- withheld reinforcement list, if any

### E. Sorting checks

- latest-first sorting preserved
- cards with missing or invalid date flagged
- accepted cards do not break date order

### F. Source-lock and source-coverage checks

- every core visible-field claim is supported by source_quote or fact_sources
- no paywall headline/snippet-only core claim
- no contradiction with source_quote
- fact and implication are clearly separated
- no outside-source claim added without explicit permission
- source coverage reviewed
- single-source cards documented
- background_context-only cards not promoted to publish-ready
- claim coverage map included for weak or important cards

### G. Web QC checks

If web search was performed, report:

- number of cards checked
- source URL accessibility issues
- source/date/stage conflicts
- duplicate event risks
- stronger follow-up articles
- source-augmentation recommendations
- useful new evidence not inserted due to source-lock rules

If web search was not performed, report “External web QC was not performed” and why.

### H. Baseline source and GitHub sync checks

Report:

- baseline source: `github_main`, `local_final_candidate`, or `user_uploaded_baseline`
- whether GitHub main was confirmed after file generation
- if not confirmed, state that a GitHub main sync gate is required before PR/merge

### I. Change summary

Include:

- number of cards enriched
- fields rewritten
- fields preserved
- cards narrowed due to weak source support
- cards flagged for source conflict or duplicate risk
- cards requiring source augmentation or return to Prompt C

---

## 17. Output files

Produce:

1. `accepted_cards_content_enriched_{RUN_TAG}.json`
   - content-enriched accepted payload
   - visible fields only rewritten
   - fact_sources and source_quote preserved unless a separately authorized source-augmentation pass is active
   - original schema shape preserved
   - valid JSON

2. `cards_merged_content_enriched_{RUN_TAG}.json`
   - `BASELINE_CARDS_JSON` + enriched addable accepted cards
   - adjusted only for documented duplicate exclusions if needed
   - latest-first sorting
   - existing baseline cards unchanged unless explicitly instructed
   - app-runtime compatible structure
   - valid JSON

3. `qc_report_content_enriched_{RUN_TAG}.md`
   - task summary
   - input/output counts
   - accepted vs addable vs withheld reinforcement counts
   - baseline source declaration
   - changed-field scope
   - source preservation check
   - source coverage / claim coverage check
   - duplicate ID/URL/event fingerprint check
   - banned phrase check
   - foreign-language residue check
   - implication/fact/gate/sub minimum requirement check
   - latest-first sorting check
   - source-lock check
   - web QC check
   - GitHub sync gate status
   - schema/type drift check
   - exception/risk card list
   - final PASS/FAIL decision

---

## 18. Final response format

In the final response, report only:

1. links to the three generated files
2. accepted input count
3. addable card count
4. withheld reinforcement count, if any
5. baseline count
6. final merged count
7. baseline source declaration
8. QC final decision
9. whether the output is `publish_ready`
10. exceptions, if any

Do not include rewritten cards inline unless the user explicitly asks.
Do not include long explanations.
Do not claim completion unless the QC report supports it.
Do not call a file GitHub-ready if the GitHub main sync gate has not been performed.

---

## 19. Operating note

This document is reusable across runs.

Do not hard-code run-specific counts such as “18 cards” or “631 final cards” into this prompt. Use runtime variables:

- `ACCEPTED_CARDS_PAYLOAD`
- `BASELINE_CARDS_JSON`
- `BASELINE_SOURCE_DECLARATION`
- `RUN_METADATA`
- `expected_new_card_count`
- `expected_baseline_count`
- `expected_final_count`

---

## 20. Final rule

**Prompt A/B/C decides what is accepted. This document prevents accepted cards from being mistaken for publish-ready cards. Only cards that pass merge safety, source coverage, content depth, language polish, final QC, and baseline sync checks may be called publish-ready.**
