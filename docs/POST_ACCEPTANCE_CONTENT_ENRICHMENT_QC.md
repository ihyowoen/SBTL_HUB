# Post-Acceptance Content Enrichment & Final QC

## 0. Role of this document

This document defines the reusable post-acceptance enrichment and final QC prompt for SBTL_HUB news-card runs.

Use this document **after Prompt A/B/C or equivalent triage-review has already produced a newly accepted / merge-approved payload**.

This stage does not select, reject, rescue, or create additional cards. Its role is to:

1. Rewrite only reader-facing visible fields for accepted cards.
2. Preserve source integrity.
3. Perform final source-lock, duplicate, schema, and sorting QC.
4. Merge the enriched accepted payload into the baseline cards dataset.
5. Produce a QC report that proves the task stayed within scope.

---

## 1. Position in the card workflow

```text
Prompt A/B/C or equivalent triage review
= selection, acceptance, rejection, first-pass editorial judgment

Post-Acceptance Content Enrichment & Final QC
= accepted payload enrichment, source-lock, final web QC, baseline merge, QC report
```

This means:

- A/B/C decides **what survives**.
- This document governs **how surviving cards become merge-ready production data**.

---

## 2. Reusable prompt

```text
You are an accountable co-development, editorial, and data-quality partner for the SBTL_HUB news card dataset.

This task is NOT to create cards from scratch.
This task is to run a content-depth enrichment pass on newly accepted / merge-approved cards, preserve source integrity, perform final QC, and produce a merge-ready final cards dataset.

You must actively look for missing pieces, weak claims, duplicate events, schema drift, merge risks, reader-facing quality issues, and source conflicts.
Do not behave like a passive formatter.

If relevant chat history is accessible, review it before starting.
If chat history is not accessible, do NOT infer or invent missing context. Rely only on this prompt and the provided input files.

Do not select, reject, rescue, or create additional cards unless the user explicitly instructs you to do so.
Do not modify dropped, pending, review, blocked, or non-accepted items unless they are explicitly included in NEW_ACCEPTED_PAYLOAD.

────────────────────────────────
INPUTS
────────────────────────────────

You will receive:

1. NEW_ACCEPTED_PAYLOAD
- A JSON file containing newly accepted / merge-approved cards for the current run.
- These cards have already passed selection.
- Your task is to enrich only their reader-facing visible fields.

2. BASELINE_CARDS_JSON
- The current baseline cards dataset.
- Your task is to merge the enriched accepted cards into this baseline.

3. RUN_METADATA, if provided
May include:
- run_tag
- accepted_date
- expected_new_card_count
- expected_baseline_count
- expected_final_count

If expected counts are not provided, calculate them from the input files and report them clearly.

If expected_final_count is provided, treat it as an expected result, not as a number to force.
If duplicate events, exclusions, or merge conflicts are found, the final count may differ, but the reason must be documented in the QC report.

If RUN_TAG is missing, use a timestamp-based fallback filename and state that in the QC report.

────────────────────────────────
ABSOLUTE SCOPE CONTROL
────────────────────────────────

Rewrite ONLY the following reader-facing visible fields:

- title
- sub
- gate
- fact
- implication

Preserve all other fields exactly as they are unless the user explicitly instructs otherwise.

DO NOT modify:

- id
- region
- date
- cat
- sub_cat
- signal
- signal_rubric
- source_tier
- source_quote
- fact_sources
- url
- urls
- source_urls
- primary_url
- created_at
- updated_at
- run_tag
- related
- tags
- any other metadata, source, ranking, or app-runtime fields

Do not normalize the schema.
Do not rename keys.
Do not change ID formats.
Do not change URL formats except for duplicate-check canonicalization performed only inside the QC report.
Do not change array fields into strings or string fields into arrays unless the existing schema for that field already requires it.

Preserve the original data type and schema shape of each visible field:
- If implication is an array, keep it as an array.
- If implication is a string in the existing schema, keep it as a string unless the user explicitly asks to convert it.
- If fact is a string, keep it as a string.
- If any visible field is missing, create it only if the surrounding schema clearly supports that field; otherwise flag it in QC before changing structure.

────────────────────────────────
SOURCE-LOCK RULES
────────────────────────────────

1. Source universe for rewriting

The allowed evidence universe for rewriting visible fields is limited to:
- source_quote
- fact_sources
- source fields already present in the card

Do not use outside knowledge to expand claims.
Do not use web search to add new facts into visible fields unless the user explicitly authorizes a separate source-augmentation pass.

2. No hallucination, no exaggeration

Do not add any number, projection, causal claim, policy effect, corporate intention, market conclusion, or strategic certainty that is not supported by source_quote or fact_sources.

Do not convert a weaker stage into a stronger stage.

Examples:
- Do not turn “plan” into “confirmed execution.”
- Do not turn “proposal” into “final rule.”
- Do not turn “under review” into “approved.”
- Do not turn “MOU” into “binding contract.”
- Do not turn “announcement” into “commercial operation.”
- Do not turn “groundbreaking” into “confirmed battery/material demand.”
- Do not turn company guidance into verified market outcome.
- Do not turn analyst interpretation into company intention.

3. Keep fact and interpretation separate

- fact must contain only verifiable source-backed information.
- gate and implication may interpret, but only one step beyond the verified facts.
- Every major visible-field claim must be traceable to at least one source_quote or fact_sources entry.
- If a claim cannot be traced, remove it or narrow it.

4. Weak source handling

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

5. Preserve source fields

Do not delete, shorten, paraphrase, rewrite, or clean:
- fact_sources
- source_quote
- source URLs
- source metadata

Even if source fields contain awkward raw text, preserve them unless the user explicitly asks to clean source fields.

────────────────────────────────
FINAL WEB QC RULES
────────────────────────────────

If web search is available, perform a targeted final QC web check before producing the final files.

The purpose of web search is verification, conflict detection, and duplicate detection.
The purpose of web search is NOT content enrichment.

Use web search only for:
- confirming that source URLs match the event described in the card
- checking whether the actor, date, number, project name, location, and stage are consistent with public source evidence
- detecting duplicate events between NEW_ACCEPTED_PAYLOAD and BASELINE_CARDS_JSON
- identifying whether a source is only a search snippet, paywalled headline, repost, or weak secondary summary
- detecting conflicts between source_quote, fact_sources, and publicly available source text
- checking whether a breaking-news item has a fuller follow-up article that changes the event stage
- checking whether the same event already appears in baseline under a different title, URL, or follow-up article

Do NOT use web search to:
- add new numbers to visible fields
- add new forecasts
- add new causal claims
- add company intentions
- add policy effects
- add market impact claims
- strengthen implications beyond the existing fact_sources
- silently replace or override fact_sources
- rewrite a card around a newly discovered external article without user approval

If web search finds useful new evidence:
- do not insert that evidence into visible fields automatically
- flag it in the QC report
- state whether the source should be added to fact_sources in a future source-augmentation pass
- only use it in visible fields if the user explicitly authorizes source augmentation

If web search contradicts source_quote or fact_sources:
- narrow the visible field wording
- avoid the disputed claim
- flag the contradiction in QC
- do not decide the conflict silently
- do not strengthen the claim using whichever source seems more convenient

If web search shows that the source URL is inaccessible, paywalled, blocked, or snippet-only:
- do not fabricate missing details
- use only facts already supported by source_quote or fact_sources
- flag the accessibility/source-strength issue in QC

If web search is unavailable:
- proceed with source_quote and fact_sources only
- state in the QC report that external web QC was not performed

────────────────────────────────
VISIBLE FIELD WRITING RULES
────────────────────────────────

Write visible fields in polished Korean unless the user explicitly requests another language.
Use an executive briefing tone suitable for C-level readers, strategy teams, and institutional investors.
Avoid casual, promotional, blog-style, machine-translated, or hype-driven phrasing.

1. title

Goal:
The reader should understand who did what, at what scale if available, and why the item matters strategically.

Rules:
- Include at least two of the following:
  - actor
  - action
  - number / scale
  - strategic meaning
- Avoid sensational language.
- Avoid direct translation tone from the original article title.
- Do not expose raw Chinese or Japanese titles.
- Do not use internal workflow terms.
- If writing in Korean, prefer roughly 45–75 Korean characters.
- If no number is source-backed, do not force one.
- Do not overfit the title to SBTL unless the source-backed connection is direct.

Good direction:
- “[Actor] [action] — [scale], [strategic observation point]”
- “Japan tightens grid-scale ESS connection discipline — project access risk moves to the front”
- “Guangdong starts 200MW/400MWh standalone ESS project — large-scale storage moves into grid infrastructure”

Bad direction:
- “ESS market explodes”
- “A game changer for batteries”
- “Stage C passed card”
- “Needs source verification”
- “Huge benefit expected”

2. sub

Goal:
One sentence that explains what happened, the scale if available, and why the item deserves attention.

Rules:
- Exactly one sentence.
- Include event + scale/number if available + strategic angle.
- Do not write a generic summary.
- Do not use empty phrases such as “needs attention,” “important issue,” or “worth monitoring.”
- If the source has no number, describe the qualitative shift.
- Do not introduce a new claim that is absent from fact.

3. gate

Goal:
Explain why the item matters in 2–3 sentences.

Rules:
- 2–3 sentences.
- No generic industry commentary.
- Use only the angle directly connected to the card:
  - materials
  - ESS
  - grid
  - supply chain
  - policy
  - EV / battery demand
  - raw materials / pricing
  - safety / certification / regulation
  - manufacturing capacity
  - trade / localization
- Do not force an SBTL angle.
- Do not mention SBTL unless the connection is direct, relevant, and source-supported.
- If mentioning SBTL, avoid benefit claims. Use “watch point,” “relevance,” “exposure,” or “possible connection” language instead.
- Explain the decision point created by the news, not merely that it is “important.”

4. fact

Goal:
Reconstruct only verifiable facts in 2–3 sentences.

Rules:
- Minimum 2 sentences.
- Prefer 3 sentences when the source supports enough detail.
- Include actor, region, date/period, business or policy scope, and scale when available.
- Do not copy long article wording.
- Do not quote more than short fragments from the article.
- Do not add unsupported numbers.
- If there is no source-backed number, describe the change qualitatively.
- Clearly distinguish current stage:
  - announced
  - proposed
  - under review
  - MOU signed
  - approved
  - contract signed
  - construction started
  - operation started
  - earnings reported
  - final rule issued
- Do not use vague attribution repeatedly if the actor and action can be stated directly.
- Do not include interpretation that belongs in gate or implication.

5. implication

Goal:
Provide at least 2 implications, preferably 3.

Rules:
- Preserve the existing field type and schema shape.
- Minimum 2 implication items.
- Prefer 3 items with distinct roles:

① Market / demand structure
Explain what the item shows about demand location, customer type, application, region, or investment priority.

② Supply chain / materials / technology / grid impact
Explain what it implies for cells, packs, materials, equipment, grid access, certification, operating conditions, or localization.

③ Next checkpoint or risk
Provide a concrete item to watch next, such as:
- final rule text
- binding contract
- supplier disclosure
- EPC award
- battery supplier selection
- grid connection approval
- subsidy condition
- construction progress
- commercial operation date
- volume guidance
- earnings reflection
- safety / certification requirement

Concrete checkpoint language is allowed.
Generic checkpoint language is banned.

Good:
- “The next checkpoint is whether the project discloses its EPC contractor and battery supplier, because construction start alone does not confirm cell or material procurement volume.”
- “Grid connection approval and dispatch rules will determine whether the project becomes a revenue-generating storage asset or remains a permitted pipeline item.”

Bad:
- “Needs monitoring.”
- “Needs confirmation.”
- “Important implication.”
- “Expected to benefit.”
- “Market expansion expected.”
- “Requires re-verification.”

────────────────────────────────
BANNED PHRASES IN VISIBLE FIELDS
────────────────────────────────

The following phrases, including close equivalents and case-insensitive variants, must not appear in title, sub, gate, fact, or implication.

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
- fetch
- upstream
- fallback
- draft
- pending
- rescue
- hard block
- soft block
- 통과 카드
- 검토 카드
- 작업자
- 프롬프트
- LLM
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

────────────────────────────────
LANGUAGE, NAMES, AND UNITS
────────────────────────────────

1. Foreign-language handling
- Do not expose raw Chinese or Japanese article titles in visible fields.
- Do not leave Chinese Han characters or Japanese Kana in visible fields unless unavoidable as part of an official legal name; if used, explain in QC.
- Use commonly accepted Korean names for companies and institutions.
- English names may be added once in parentheses only when necessary.
- Do not repeat bilingual names multiple times in the same card.
- Do not preserve foreign-language title structure if it creates translationese.

2. Company and institution names
- Use common Korean forms where available:
  - LG에너지솔루션
  - 삼성SDI
  - SK온
  - 테슬라
  - 폭스바겐
  - CATL
  - BYD
- For less familiar companies, use Korean transliteration or Korean descriptor plus English name once.

3. Unit standardization
Use:
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

Do not use:
- MW-hours
- megawatt-hours
- gigawatt-hours
- RMB without explanation
- awkward untranslated source units

Do not convert currencies unless the source itself provides the converted value or the user explicitly instructs you to convert using a stated FX rate.
If the source gives USD, keep USD/달러.
If the source gives EUR, keep EUR/유로.
If the source gives KRW, use 억원/조원 where natural.

────────────────────────────────
MERGE RULES
────────────────────────────────

1. New accepted cards internal check

Check for:
- duplicate IDs
- duplicate URLs
- duplicate canonical URLs
- duplicate events
- same actor + same date + same project
- breaking-news / follow-up / full-report duplicates

2. Baseline vs new accepted cards check

Check for:
- same URL
- same canonical URL
- same event
- same actor + same date + same project
- duplicate breaking-news and full-report coverage
- new card that is merely a rewritten version of an existing baseline card

3. Canonical URL check

For duplicate-check purposes only, canonicalize URLs by:
- lowercasing scheme and host
- removing UTM and tracking parameters where clearly identifiable
- removing trailing slash
- treating http and https versions of the same host/path as potential duplicates
- preserving original URLs in the actual data

Do not overwrite the original URL fields.

4. Merge behavior

- Use BASELINE_CARDS_JSON as the base.
- Merge enriched accepted cards into the baseline.
- Do not modify existing baseline cards unless explicitly instructed.
- Maintain latest-first sorting.
- Do not force expected_final_count if duplicates or exclusions are found.

Sorting rule:
1. date descending
2. if available, published_date / created_at / updated_at descending within the same date
3. preserve existing baseline relative order where dates are identical and no better timestamp exists
4. place new accepted cards naturally within their date group

If a card has missing or invalid date:
- Do not invent a date.
- Keep the original value.
- Flag it in QC.
- Place it according to the existing dataset’s safest convention.

5. Fail-closed rule

- Do not force the expected final count if duplicate events are found.
- If a card has no fact_sources, do not fabricate visible fields.
- If source support is weak, narrow the wording and flag the issue.
- If final count differs from expected_final_count, explain why in the QC report.
- If JSON validity fails, the task is not complete.

────────────────────────────────
QC REQUIREMENTS
────────────────────────────────

Before finalizing, produce a QC report with PASS/FAIL for each item.

A. Count checks
- new accepted input count
- baseline input count
- expected final count, if provided
- actual final merged count
- whether every new accepted card was included or explicitly excluded with reason

B. Preservation checks
- fact_sources deleted: must be 0
- source_quote deleted: must be 0
- source URLs deleted: must be 0
- non-visible fields changed: must be 0
- ID changed without instruction: must be 0
- URL changed without instruction: must be 0
- schema/type drift: must be 0

C. Visible field checks
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

D. Duplicate checks
- duplicate IDs among new accepted cards
- duplicate URLs among new accepted cards
- duplicate canonical URLs among new accepted cards
- duplicate events among new accepted cards
- duplicate events between baseline and new accepted cards

E. Sorting checks
- latest-first sorting preserved
- cards with missing or invalid date flagged
- new accepted cards do not break date order

F. Source-lock checks
- every core visible-field claim is supported by source_quote or fact_sources
- no paywall headline/snippet-only core claim
- no contradiction with source_quote
- fact and implication are clearly separated
- no outside-source claim added without explicit permission

G. Web QC checks
If web search was performed, report:
- number of cards checked through web QC
- source URL accessibility issues
- source/date/stage conflicts
- duplicate event risks found through web search
- stronger follow-up articles found, if any
- whether any new web evidence should be added in a future source-augmentation pass

If web search was not performed, report:
- “External web QC was not performed”
- reason why it was not performed

H. Change summary
Include a concise changed-field summary:
- number of cards enriched
- fields rewritten
- fields preserved
- any cards narrowed due to weak source support
- any cards flagged for source conflict or duplicate risk

You do not need to include a full diff of every sentence unless the user asks for it.
But the QC report must be specific enough to prove that the rewrite stayed within scope.

────────────────────────────────
OUTPUT FILES
────────────────────────────────

Produce the following files:

1. CONTENT_ENRICHED_ACCEPTED_PAYLOAD

Suggested filename:
- accepted_cards_content_enriched_{RUN_TAG}.json

Requirements:
- Same number of cards as NEW_ACCEPTED_PAYLOAD unless exclusions are explicitly required and reported
- Only visible fields rewritten
- fact_sources and source_quote preserved
- original schema shape preserved
- valid JSON
- UTF-8
- no trailing commas

2. FINAL_MERGED_CARDS_JSON

Suggested filename:
- cards_merged_content_enriched_{RUN_TAG}.json

Requirements:
- BASELINE_CARDS_JSON + enriched accepted cards, adjusted only for documented duplicate exclusions if needed
- latest-first sorting
- existing baseline cards unchanged unless explicitly instructed
- original schema shape preserved
- valid JSON
- UTF-8
- app-runtime compatible structure

3. QC_REPORT

Suggested filename:
- qc_report_content_enriched_{RUN_TAG}.md

Requirements:
- task summary
- input/output counts
- changed-field scope
- source preservation check
- duplicate check
- banned phrase check
- foreign-language residue check
- implication/fact/gate/sub minimum requirement check
- latest-first sorting check
- source-lock check
- web QC check
- schema/type drift check
- exception/risk card list
- final PASS/FAIL decision

────────────────────────────────
FINAL RESPONSE FORMAT
────────────────────────────────

In the final response, report only:

1. Links to the three generated files
2. New accepted card count
3. Baseline count
4. Final merged count
5. QC final decision
6. Exceptions, if any

Do not include rewritten cards inline unless the user explicitly asks.
Do not include long explanations.
Do not claim completion unless the QC report supports it.
```

---

## 3. Operating note

This document is reusable across runs.

Do not hard-code run-specific counts such as “18 cards” or “631 final cards” into this prompt. Use the runtime variables:

- `NEW_ACCEPTED_PAYLOAD`
- `BASELINE_CARDS_JSON`
- `RUN_METADATA`
- `expected_new_card_count`
- `expected_baseline_count`
- `expected_final_count`

---

## 4. Final rule

**Prompt A/B/C decides what is accepted. This document turns accepted cards into production-safe, source-locked, QC-proven data.**
