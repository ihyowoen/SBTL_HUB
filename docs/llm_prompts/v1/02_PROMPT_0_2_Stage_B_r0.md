<!-- REPLACE_ALL_CLEAN_VERSION: LLM_PROMPT_GITHUB_CANONICAL_V1_SOURCE_DIVERSITY_IB_CODEX -->
<!-- Generated KST: 2026-07-08T21:33:49.790191+09:00 -->
<!-- This file is a full clean replacement file. It is not a patch stub. -->

Prompt 0.2v — Reusable Default / Replace All / Strict Stage B Mode

Proceed to Stage B only.

Use the current run’s Stage A output as the only input universe for Stage B.

Do not continue from, trust, import, integrated rule, or reuse any previous Stage B/C/post-QC outputs unless the user explicitly declares them as current-run authoritative inputs.

Use GitHub main as the workflow source of truth.

Before starting, read the latest versions of all required workflow docs from GitHub main:

1. docs/FACT_DISCIPLINE.md
2. docs/PROMPT_ABC_DEFAULT_MODE.md
3. docs/PROMPT_ABC_SUPPORTING_RULES.md
4. docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md
5. docs/CARD_ID_STANDARD.md
6. docs/WORKFLOW.md
7. docs/OPERATIONS.md
8. docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md

Required-doc rule:

All 8 documents above are mandatory.

If any required document is missing, inaccessible, unreadable, stale, ambiguous, or cannot be confirmed from GitHub main, stop immediately and report:

- status: BLOCKED_REQUIRED_DOC_MISSING
- missing_or_unreadable_docs: [...]
- no Stage B work performed

Do not infer replacement rules from memory.
Do not use archived docs.
Do not use branch-only docs.
Do not use local snippets unless the user explicitly provides them as current-run authoritative docs.

Important scope note:

docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md must be read before Stage B because it defines downstream state discipline, evidence hard-fail rules, and naming restrictions.

However, Stage B must not perform post-acceptance QC.
Stage B produces draft_card or draft_blocked only.
Post-acceptance QC applies only after Prompt C has produced accepted_fact_safe cards.

Input files:

- Stage A JSON: {{STAGE_A_RESULTS_JSON}}
- Stage A report: {{STAGE_A_REPORT_MD}}
- Source input: {{SOURCE_INPUT_FILE}}
- Baseline cards: {{BASELINE_CARDS_SOURCE}}
- Baseline source declaration: {{BASELINE_SOURCE_DECLARATION}}
- Run tag: {{RUN_TAG}}
- Run label: {{RUN_LABEL_KST}}

Required input rule:

Stage B requires a valid Stage A JSON from the same run.

The Stage A JSON must include:

- required_docs_check
- run_tag
- run_label
- input_file
- baseline_file
- baseline_source_declaration
- baseline_count
- story_count
- original_status_counts
- strict_passed_spec[]
- review_pool[]
- rejected[]
- existing_reinforcement[]
- support_source_only[]
- decision_ledger[]
- summary.total_ledger_count
- summary.ledger_matches_story_count
- stage_a_validity_status
- artifact_consistency_status
- csv_schema_status
- review_pool_partition_status
- strict_pass_gate_metadata_status
- baseline_duplicate_screen_status
- review_pool_partition_summary
- candidate_review_pool[]
- watchlist_context_pool[]
- reject_or_support_only_pool[]

If Stage A JSON is missing, invalid, incomplete, not from the same run, or has ledger mismatch, stop and report:

- status: BLOCKED_STAGE_A_INVALID
- reason: [...]
- no Stage B work performed

## Structural default — Stage B preflight for Stage A artifact completeness

Before any fetch, search, evidence package, or draft work, Stage B must verify the current Stage A artifacts are structurally valid.

Required PASS statuses:

- `stage_a_validity_status = PASS`
- `artifact_consistency_status = PASS`
- `csv_schema_status = PASS`
- `review_pool_partition_status = PASS`
- `review_pool_carry_forward_ledger_status = PASS`
- `strict_pass_gate_metadata_status = PASS`
- `baseline_duplicate_screen_status = PASS`
- `summary.ledger_matches_story_count = true`

Required count agreement across Stage A JSON/report/CSV:

- story_count
- strict_passed_spec_count
- review_pool_count
- candidate_review_pool_count
- watchlist_context_pool_count
- reject_or_support_only_pool_count
- rejected_count
- existing_reinforcement_count
- support_source_only_count
- decision_ledger_count

If any required status is missing/not PASS or any count disagrees, stop and report:

- `status = BLOCKED_STAGE_A_ARTIFACT_OR_PARTITION_INVALID`
- `reason = [...]`
- `no Stage B work performed`

Stage B must not repair Stage A outputs.
Stage B must not infer missing partitions from CSV text.
Stage B must not use legacy unpartitioned `review_pool[]` for any purpose.


Stage B may use only:

- Stage A strict_passed_spec[]

Stage B must not use:

- Stage A review_pool
- Stage A candidate_review_pool
- Stage A watchlist_context_pool
- Stage A reject_or_support_only_pool
- Stage A needs_review
- Stage A rejected
- Stage A existing_reinforcement
- Stage A support_source_only
- non-sampled DROPPED items
- previous dry-run outputs
- previous accepted payloads
- previous addable payloads
- previous post-QC outputs
- prior manually integrated files
- any card or candidate not present in current Stage A strict_passed_spec[]

If the user wants review_pool items promoted, that requires an explicit separate review/promotion run before Stage B.

Governance hierarchy:

When rules conflict, apply this hierarchy:

1. docs/FACT_DISCIPLINE.md
2. docs/PROMPT_ABC_DEFAULT_MODE.md
3. docs/PROMPT_ABC_SUPPORTING_RULES.md
4. docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md
5. docs/CARD_ID_STANDARD.md
6. docs/WORKFLOW.md
7. docs/OPERATIONS.md
8. docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md

FACT_DISCIPLINE.md always wins for facts, numbers, quotes, and evidence discipline.

Stage B role:

Stage B is the evidence-fetching and draft-writing stage.

Stage B must:

1. Take only Stage A strict_passed_spec[].
2. Attempt the provided source-candidate URL (`primary_url`) for every strict_passed_spec, verify whether it is body-level evidence, and replace or supplement it through source discovery when it is not sufficient.
3. For every strict_passed_spec, perform bounded same-event source discovery before drafting: check fallback URLs from spec.urls[], cited-primary/source-owner candidates, official/primary sources, and open-access Tier 1/Tier 2 alternates.
4. Record the source-discovery result even when the provided source-candidate is already usable. "Primary URL worked" is not a waiver of official/source-diversity search; it is one row in the source-discovery ledger.
5. Prepare an evidence_package for every strict_passed_spec before drafting any card.
6. Extract body-level or official-material evidence.
7. Confirm or correct event_date from fetched evidence.
8. Re-check staleness based on fetched evidence.
9. Draft full-schema draft_card only when core event evidence is sufficient.
10. Mark draft_blocked when evidence is insufficient, stale, source-direction mismatched, or unsupported.
11. Produce draft cards, blocked specs, evidence packages, and fetch/source availability reports.


Stage B strict-pass gate validation:

Stage B must inspect Stage A format-risk and execution-anchor metadata when present.

- If a strict_passed_spec has format_risk_tags other than none, Stage B must verify that fetched evidence supports the claimed execution anchor.
- In v13 replace-all mode, missing `strict_pass_gate` is a Stage A structural failure. Stage B must stop with `BLOCKED_STAGE_A_STRICT_GATE_METADATA_MISSING` rather than infer the anchor. A legacy exception is allowed only if the user explicitly declares a non-v13 legacy Stage A artifact as authoritative for a one-off recovery run.
- If fetched evidence shows the item is only product news, demo, PoC, pilot, prototype, component launch, interview, commentary, roundup, speech, personnel, or partnership/integration with no concrete execution anchor, mark draft_blocked.
- If fetched evidence supports only a weaker stage than Stage A implied, mark draft_blocked with source_direction_mismatch or execution_anchor_missing.
- If the item remains strategically useful but not independently cardable, recommend support_source_only or review_pool triage in recommended_next_action; do not force a draft.

Allowed concrete execution anchors are the same as Stage A: signed contract, binding customer order, offtake, price floor/risk-sharing facility, commercial deployment, field installation, commissioning, production start, facility opening, certification/regulatory approval, regulatory decision/enforcement, public funding approval, binding procurement, measurable capacity addition, safety recall/regulatory safety action, named customer adoption, named deployment site with measurable pilot scale/duration/objective, factory/project groundbreaking, or final investment decision.

Stage B must not:

- decide accepted_fact_safe
- decide revise_required
- decide rejected as a final Stage C decision
- decide addable_merge_safe
- decide evidence_complete
- decide source_claim_covered
- decide content_enriched
- decide language_terminology_polished
- decide publish_ready
- promote review_pool items
- silently drop specs
- use headline-only evidence
- use RSS/listing/snippet text as source_quote
- write claims that are not supported by body-level or official-source evidence
- invent missing numbers, dates, comparisons, company roadmaps, market-share data, or causal claims
- rely on memory or general knowledge
- add new card candidates from web search
- use web search as silent content enrichment

Web search / fetch boundary:

Stage B may perform web_fetch and web search only for Stage A strict_passed_spec[].

For each strict_passed_spec, Stage B must perform bounded same-event web/source discovery unless the user explicitly disables external search for that run. If external search is disabled, Stage B must set `external_source_discovery_disabled_by_user: true` and route any item that cannot satisfy the single-source exception to `draft_blocked` or `needs_source_augmentation`; it must not pretend source diversity was checked.

Allowed purposes:

- primary_url source-candidate verification
- fallback URL fetch
- open-access alternate source search for the same event
- official/primary source search for the same event
- source accessibility check
- evidence package construction
- body-level quote extraction
- event_date / staleness confirmation

Prohibited purposes:

- discovering new card candidates
- promoting Stage A review_pool
- rescuing rejected or dropped stories
- adding unrelated background facts
- expanding the card beyond the Stage A event anchor
- inserting new claims that are not tied to the spec’s core event
- creating publish-ready evidence conclusions

Critical evidence-first rule:

Before drafting any card, Stage B must create an evidence_package for the corresponding strict_passed_spec.

If body-level or official-material evidence cannot be secured for the core event claim, do not draft the card.

Mark the spec as draft_blocked.

Terminology discipline:

Use these Stage B terms:

- source_availability
- fetch_coverage
- evidence_package
- evidence_candidate
- fact_source_candidate
- draft_card
- draft_blocked
- writer_notes
- needs_stage_c_attention

Do not use these terms as Stage B outcomes:

- accepted_fact_safe
- revise_required
- rejected, except as a quoted future Stage C category
- addable_merge_safe
- evidence_complete
- source_claim_covered
- content_enriched
- language_terminology_polished
- publish_ready
- final
- PR_CANDIDATE
- GitHub-ready
- merge-ready

Important state rule:

Stage B evidence_package / source_availability / fetch_coverage is not evidence_complete.

A Stage B draft_card is not accepted_fact_safe, not addable, not evidence_complete, and not publish_ready.

Stage B output must set:

- publish_ready: false
- stage_b_only: true

for every draft_card.

Evidence package requirements:

Each strict_passed_spec must receive an evidence_package.

Each evidence_package must include:

- spec_id
- source_story_ids
- primary_url
- attempted_urls[]
- event_fingerprint_search_profile
- official_source_search_ledger[]
- cited_primary_search_ledger[]
- alternate_source_search_ledger[]
- source_discovery_ledger[]
- source_discovery_status
- source_diversity_precheck
- fetch_status
- source_availability
- fetch_coverage
- event_date_from_stage_a
- event_date_from_fetched_source
- event_date_confidence
- staleness_recheck
- source_direction_check
- extracted_evidence[]
- missing_evidence[]
- evidence_package_status
- draft_decision

Allowed evidence_package_status values:

- evidence_package_ready_for_draft
- evidence_package_partial_needs_stage_c_attention
- evidence_package_blocked

Allowed draft_decision values:

- draft_card
- draft_blocked

Evidence extraction rules:

Extract only information that appears in fetched body-level text or official material:

- numbers and quantities
- dates
- named entities
- project names
- locations
- capacity / money / percentage / volume
- explicit comparisons
- direct quotes
- regulatory or official decisions
- announced company actions
- stated timeline from the source

Do not extract:

- reporter speculation
- implied causal claims
- unsupported market impact
- memory-based company roadmaps
- general background from model knowledge
- headline-only assertions
- search result snippets
- RSS-only text
- listing-card text
- paywall title text

Source quote rules:

Every fact_source_candidate must include a source_quote.

source_quote must be direct body-level or official-material text.

source_quote must not be:

- headline-only
- RSS-only
- snippet-only
- listing-title text
- metadata-only
- article-title-only
- near-title paraphrase
- generated summary
- translated paraphrase without original-source support

source_quote_status must be one of:

- body_quote_verified
- official_material_quote_verified
- document_quote_verified
- fetch_failed
- paywall_blocked
- js_blocked
- quote_not_found
- headline_only
- snippet_only
- rss_only
- listing_only

If source_quote_status is not one of:

- body_quote_verified
- official_material_quote_verified
- document_quote_verified

then the related claim must not be used in visible fields.

If the core event claim has no body_quote_verified, official_material_quote_verified, or document_quote_verified support, the spec must be draft_blocked.

Fact source candidate schema:

Each fact_source_candidate must include:

- source_name
- source_url
- claim
- source_quote
- source_quote_status
- evidence_role
- supports
- fetched_at
- fetch_method

Allowed evidence_role values:

- primary_event_evidence
- secondary_event_evidence
- background_context
- not_used

Rules for evidence_role:

- At least one primary_event_evidence or strong secondary_event_evidence must support the core event.
- background_context may support framing only.
- background_context cannot rescue a weak or unsupported core event.
- not_used evidence must not support visible fields.

supports must be an array containing one or more of:

- title
- sub
- gate
- fact
- implication
- not_used

Single-source rule:

Single-source drafting is an exception, not the default. Stage B must try to avoid single-source drafting through bounded same-event source discovery.

If single-source drafting is used, add:

- single_source_exception
- single_source_reason
- source_discovery_status
- source_discovery_ledger_reference
- needs_stage_c_attention: true

`single_source_exception.allowed` may be true only when the single source is official, primary, regulatory, filing, primary dataset/report, or body-level evidence sufficient for every core visible claim and the source-discovery ledger shows no better corroborating source was found.

Single-source cards must be draft_blocked if the single source is:

- headline-only
- RSS-only
- search-snippet-only
- listing-page-only
- paywall-title-only
- repost without body details
- inaccessible without quote extraction

Staleness recheck:

For every strict_passed_spec, Stage B must confirm or update event_date using fetched evidence.

If Stage A event_date differs from fetched event_date, record:

- event_date_discrepancy: true
- stage_a_event_date
- fetched_event_date
- discrepancy_notes
- needs_stage_c_attention: true

If fetched evidence shows:

- gap ≤ 7 days: staleness_recheck.decision = fresh
- gap 8–30 days: staleness_recheck.decision = stale_warm and needs_stage_c_attention = true
- gap > 30 days with no fresh follow-up: draft_blocked with blocked_reason = stale_republication
- gap > 30 days with documented fresh follow-up: draft may proceed only if framed around the fresh follow-up event

Do not invent event dates.

If event_date cannot be confirmed, set:

- event_date_confidence: low
- needs_stage_c_attention: true

and draft only if the core event is still body-supported and not obviously stale.

Source-direction check:

For every spec, compare Stage A event_anchor with fetched evidence.

If source direction differs, do not force a draft.

Mark draft_blocked when:

- product/demo/PoC/pilot/prototype/component/interview/commentary/roundup/speech/personnel/partnership format has no concrete execution anchor
- source reports MOU/pilot but spec implies commercial deployment
- source reports semi-solid but spec implies solid-state
- source reports consideration/plan but spec implies confirmed execution
- source reports one company statement but spec implies industry consensus
- source reports old event with no fresh follow-up
- source body does not support the event_anchor

Use blocked_reason = source_direction_mismatch.

Drafting rules:

Draft full-schema card only after evidence_package_status is:

- evidence_package_ready_for_draft

or, in limited cases:

- evidence_package_partial_needs_stage_c_attention

When partial evidence is used, set:

- needs_stage_c_attention: true
- writer_notes explaining the limitation

Do not draft if core event evidence is missing.

Draft card fields:

Each draft_card must include:

- draft_id
- source_spec_id
- source_story_ids
- region
- date
- cat
- sub_cat
- signal
- title
- sub
- gate
- fact
- implication
- urls
- related
- fact_sources
- source_availability
- fetch_coverage
- evidence_package_status
- single_source_reason, if applicable
- needs_stage_c_attention
- writer_notes
- stage_b_only: true
- publish_ready: false

Draft content rules:

Reader-facing writing persona:

Write visible card fields as a top-tier investment-banking sector veteran with
30 years of battery, ESS, EV, energy-infrastructure, and industrial supply-chain
deal experience. The card should read like a concise Korean strategy note from
an experienced IB industry banker: commercially literate, information-dense,
skeptical, and useful for decision-makers.

This persona affects only reader-facing framing and compression. It must not
weaken evidence discipline, add unsupported deal logic, imply investment advice,
or turn a weak source into a stronger claim.

The visible card should not read like a verification memo, LLM audit artifact,
RSS summary, PR rewrite, or generic news digest.

title:

- Must reflect source-supported event only.
- Must not add unsupported numbers, causality, or strategic conclusion.
- Must not use sensational phrasing.
- Must not copy the article headline unless it is rewritten and body-supported.

sub:

- One sentence.
- Must summarize source-supported event, scale, and why it matters.
- Must not introduce unsupported claims.

gate:

- 2–3 sentences.
- May interpret only within source-supported direction.
- Must not force SBTL relevance if weak.
- Must not claim direct benefit unless source-supported.

fact:

- Minimum 2 sentences.
- Prefer baseline-level information density: actor + asset/project/policy +
  geography + date/period + scale/value/capacity + status/stage + counterparty
  or authority when source-supported.
- Must contain only source-supported facts.
- Every number/date/entity/project/action must map to fact_sources.
- Do not use memory-based background.

implication:

- Minimum 2 items.
- Prefer 3 items:
  1. market / demand structure
  2. supply chain / materials / technology / grid impact
  3. next checkpoint or risk

- Must be observational, not definitive.
- Must not introduce new unsupported facts.
- Must read like an IB sector note: identify market structure, supply-chain,
  financing, localization, pricing, policy, or execution-risk relevance when
  evidence supports it.
- Avoid generic "watch/monitor" implications when a sharper source-supported
  checkpoint is available.

Allowed implication wording:

- 관찰된다
- 확인할 필요가 있다
- 변수가 될 수 있다
- 점검 대상이다
- 가능성이 열린다
- 리스크로 남는다
- 후속 확인이 필요하다

Banned implication wording:

- 수혜가 확정된다
- 직접 수혜다
- 반드시 증가한다
- 구조적으로 전환된다
- 확실한 신호다
- 시장 확대 기대
- 수혜 예상
- 주목 필요
- 모니터링 필요

Visible-field ban list:

Do not include workflow/meta language in reader-facing visible fields:

- 입력 원문 기준
- Stage A
- Stage B
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
- fetch
- upstream
- fallback
- prompt
- LLM
- expected to benefit
- game changer

Language and terminology rules:

- No raw Chinese/Japanese article titles in visible fields.
- Use Korean company/institution names where standard.
- English names may be added once in parentheses only when useful.
- Do not repeat bilingual names unnecessarily.
- Normalize units and terms:
  - MW-hours → MWh
  - megawatt-hours → MWh
  - gigawatt-hours → GWh
  - anode → 음극재
  - cathode → 양극재
  - separator → 분리막
  - lithium hydroxide → 수산화리튬
  - lithium carbonate → 탄산리튬
  - rare earth → 희토류
  - critical minerals → 핵심광물

Draft blocked rules:

Mark draft_blocked when:

- provided source-candidate and fallback URLs cannot be verified or replaced
- all accessible sources are headline-only
- evidence is RSS-only, snippet-only, or listing-only
- no body-level or official-material quote supports the core event
- source direction conflicts with Stage A event_anchor
- event is stale republication with no fresh follow-up
- event_date or key source facts contradict Stage A spec
- source is too weak to support a full-schema card
- source is generic landing page / listing page / static product page
- source requires speculation to write a meaningful fact field
- format-risk item has no fetched evidence for a concrete execution anchor
- only background_context evidence is available

Each draft_blocked item must include:

- spec_id
- source_story_ids
- primary_url
- attempted_urls
- blocked_reason
- blocked_reason_detail
- fetch_status
- source_availability
- fetch_coverage
- missing_evidence
- event_date_from_stage_a
- event_date_from_fetched_source
- staleness_recheck
- source_direction_check
- execution_anchor_check
- stage_a_strict_pass_gate_missing, must be false in v13 replace-all mode
- recommended_next_action

Allowed blocked_reason values:

- fact_fetch_failed
- evidence_not_body_level
- quote_not_found
- headline_only_evidence
- snippet_only_evidence
- rss_only_evidence
- listing_only_evidence
- paywall_blocked
- js_blocked
- source_direction_mismatch
- stale_republication
- event_date_conflict
- source_too_weak
- generic_landing_page
- insufficient_for_full_schema
- execution_anchor_missing
- duplicate_or_reinforcement_discovered
- other

Spec failure terminology:

If Stage B discovers the Stage A spec is wrong, unsupported, stale, source-direction mismatched, or lacks body-level evidence:

- mark draft_blocked
- do not use revise_required
- do not force a draft

revise_required is reserved for Stage C card/draft-level issues that are fixable without reopening candidate selection.

Accounting rule:

Every Stage A strict_passed_spec must appear exactly once in Stage B as either:

- draft_card
- draft_blocked

No silent skip is allowed.

Stage B must report:

- strict_passed_spec_count
- drafted_count
- draft_blocked_count
- drafted_count + draft_blocked_count
- stage_b_accounting_matches_strict_passed_spec_count: true/false

If accounting does not match, mark Stage B output invalid and report:

- status: BLOCKED_STAGE_B_ACCOUNTING_MISMATCH

Output files:

1. stage_b_prompt_b_drafts_{{RUN_TAG}}.json
2. stage_b_prompt_b_report_{{RUN_TAG}}.md
3. stage_b_prompt_b_fetch_coverage_{{RUN_TAG}}.csv
4. stage_b_prompt_b_evidence_packages_{{RUN_TAG}}.json

Do not use FINAL, PR_CANDIDATE, GitHub-ready, merge-ready, publish-ready, evidence_complete, or source_claim_covered in Stage B filenames.

Stage B JSON requirements:

The JSON must include:

- stage
- run_tag
- run_label
- input_stage_a_file
- input_source_file
- baseline_file
- baseline_source_declaration
- baseline_count
- required_docs_check
  - docs_expected
  - docs_read_from_github_main
  - docs_missing_or_unreadable
  - status
- strict_passed_spec_count
- drafted_count
- draft_blocked_count
- fetch_success_count
- fetch_partial_count
- fetch_failed_count
- source_availability_summary
- fetch_coverage_summary
- staleness_recheck_summary
- source_direction_check_summary
- single_source_count
- needs_stage_c_attention_count
- stage_b_accounting_matches_strict_passed_spec_count
- draft_cards[]
- draft_blocked[]
- evidence_packages[]
- fetch_ledger[]

Each draft_card must include:

- draft_id
- source_spec_id
- source_story_ids
- region
- date
- cat
- sub_cat
- signal
- title
- sub
- gate
- fact
- implication
- urls
- related
- fact_sources
- source_availability
- fetch_coverage
- evidence_package_status
- single_source_reason
- needs_stage_c_attention
- writer_notes
- stage_b_only: true
- publish_ready: false

Each fact_sources item must include:

- source_name
- source_url
- claim
- source_quote
- source_quote_status
- evidence_role
- supports
- fetched_at
- fetch_method

Each evidence_package must include:

- spec_id
- source_story_ids
- primary_url
- attempted_urls
- event_fingerprint_search_profile
- official_source_search_ledger
- cited_primary_search_ledger
- alternate_source_search_ledger
- source_discovery_ledger
- source_discovery_status
- source_diversity_precheck
- fetch_status
- source_availability
- fetch_coverage
- event_date_from_stage_a
- event_date_from_fetched_source
- event_date_confidence
- staleness_recheck
- source_direction_check
- extracted_evidence
- fact_source_candidates
- missing_evidence
- evidence_package_status
- draft_decision
- notes

Each draft_blocked item must include:

- spec_id
- source_story_ids
- primary_url
- attempted_urls
- blocked_reason
- blocked_reason_detail
- fetch_status
- source_availability
- fetch_coverage
- missing_evidence
- event_date_from_stage_a
- event_date_from_fetched_source
- staleness_recheck
- source_direction_check
- execution_anchor_check
- stage_a_strict_pass_gate_missing, must be false in v13 replace-all mode
- recommended_next_action

Each fetch_ledger item must include:

- spec_id
- url
- fetch_attempt_order
- fetch_status
- fetch_method
- source_name
- evidence_found
- quote_quality
- body_level_quote_found
- official_material_quote_found
- failure_reason
- notes

Stage B report requirements:

The Markdown report must include:

1. Run metadata

   - Stage A input file
   - source input file
   - baseline file/source
   - baseline source declaration
   - baseline count
   - run tag
   - run label
   - strict_passed_spec count

2. Required docs check

   - list all 8 required docs
   - confirm each was read from GitHub main
   - if any doc was not read, Stage B must not proceed

3. Method

   - strict_passed_spec-only confirmation
   - review_pool exclusion confirmation
   - primary_url source-candidate verification requirement
   - fallback URL policy
   - alternate open-access source policy
   - evidence package before draft confirmation
   - source_availability / fetch_coverage terminology confirmation
   - no evidence_complete / no publish_ready confirmation

4. Fetch/source availability summary

   - fetch success count
   - fetch partial count
   - fetch failed count
   - source-candidate verification success rate
   - fallback used count
   - alternate source used count
   - paywall/js blocked count
   - headline-only/snippet-only/RSS-only/listing-only count

5. Evidence package summary

   - evidence_package_ready_for_draft count
   - evidence_package_partial_needs_stage_c_attention count
   - evidence_package_blocked count
   - quote_not_found count
   - body_quote_verified count
   - official_material_quote_verified count
   - document_quote_verified count

6. Drafted card manifest

   For each draft_card:
   - draft_id
   - source_spec_id
   - event anchor
   - region / cat / signal
   - primary URL used
   - evidence package status
   - source availability
   - fetch coverage
   - single-source reason, if any
   - needs_stage_c_attention
   - writer notes summary

7. Draft-blocked manifest

   For each draft_blocked:
   - spec_id
   - primary URL
   - attempted URLs
   - blocked reason
   - missing evidence
   - recommended next action

8. Staleness recheck summary

   - fresh count
   - stale_warm count
   - stale blocked count
   - event_date conflict count
   - unknown event_date count

9. Source-direction check summary

   - matched count
   - mismatch blocked count
   - needs_stage_c_attention count

10. Single-source caution list

   - draft_id
   - source_name
   - single_source_reason
   - why Stage C attention is required

11. Accounting check

   - strict_passed_spec_count
   - drafted_count
   - draft_blocked_count
   - drafted + blocked
   - accounting match: yes/no

12. Explicit Stage B boundary statement

   Include this exact statement:

   “Stage B produced draft cards and draft-blocked records only. Stage B did not decide accepted_fact_safe, revise_required, addable_merge_safe, evidence_complete, source_claim_covered, content_enriched, language_terminology_polished, publish_ready, PR readiness, or GitHub readiness.”

13. Next-step statement

   Include this exact statement:

   “Stage C may begin only after the user explicitly says ‘Stage C’. Stage C must evaluate draft_cards as accepted_fact_safe, revise_required, rejected, support_source_only, or deferred review, and must not treat Stage B fetch_coverage as evidence_complete.”



## Next-call recommendation rule

At the end of this step, recommend exactly one next call.

The recommendation must be based only on the current step’s output counts and blockers.

Do not proceed automatically.

The user must explicitly authorize the next call.

The recommendation must include:

- recommended_next_call
- recommended_prompt_id
- recommended_input_universe
- reason
- blocked_items_summary
- alternative_next_call, if applicable
- do_not_proceed_to, if applicable

When this step writes JSON and/or a report, emit the recommendation as a structured `next_call_recommendation` object in both outputs.

## Operational integrated rule — Stage B next-call recommendation

At the end of this step, produce a structured `next_call_recommendation` object in the JSON/report.

The recommendation must be based only on the current step’s output counts and blockers.

Do not proceed automatically.

The user must explicitly authorize the next call.

The recommendation must include:

- recommended_next_call
- recommended_prompt_id
- recommended_input_universe
- reason
- blocked_items_summary
- alternative_next_call, if applicable
- do_not_proceed_to, if applicable


Use this specific recommendation logic:

1. If drafted_count > 0:
   - recommended_next_call = "Stage C r0"
   - recommended_prompt_id = "Prompt 0.3"
   - recommended_input_universe = "Stage B draft_cards[] only"

2. If drafted_count = 0 and draft_blocked_count > 0:
   - recommended_next_call = "source augmentation review or retrospective"
   - recommended_prompt_id = "Prompt 1.1 or source augmentation prompt if explicitly authorized"

3. If draft_blocked_count is high, include blocked_reason summary and recommend whether source collector or Stage A selector should be reviewed.

Do not proceed automatically to Stage C.
Stop after Stage B.

Do not proceed to Stage C until I explicitly say “Stage C”.

## Operational integrated rule — NO_UNVERIFIED_HOLD_OR_DELETE_RULE_20260507_V2

This rule is mandatory for every stage that can move an item to hold, block, reject, delete, support-only, deferred, revise-blocked, draft_blocked, or production-hold because evidence looks weak, incomplete, suspicious, inaccessible, RSS-only, snippet-only, listing-only, claim-thin, format-risky, or uncertain.

Uncertainty is not an outcome. Uncertainty is a verification trigger.

Before any item is finalized as hold/block/reject/delete/support-only/deferred/draft_blocked for evidence, source, claim, access, quote, format, or uncertainty reasons, the output must prove a bounded rescue/verification pass was attempted or explicitly mark the field as not applicable under the stage-specific boundary below.

Required rescue metadata for every such item:

- `rescue_attempted: true`
- `rescue_attempt_log[]`
- `searched_source_types[]`
- `official_source_checked: true|false|NOT_APPLICABLE_STAGE_A_NO_FETCH`
- `official_source_check_reason`
- `alternate_tier1_tier2_checked: true|false|NOT_APPLICABLE_STAGE_A_NO_FETCH`
- `alternate_tier1_tier2_check_reason`
- `same_event_source_direction_check: PASS|FAIL|NOT_APPLICABLE`
- `same_actor_event_date_check: PASS|FAIL|NOT_APPLICABLE`
- `blocked_source_reason`, one of:
  - `not_found_after_search`
  - `found_but_does_not_support_claim`
  - `source_access_blocked`
  - `source_is_rss_or_snippet_only`
  - `claim_overreached_available_evidence`
  - `duplicate_or_baseline_conflict`
  - `out_of_scope_or_selection_defect`
  - `manual_review_required_after_rescue`
  - `not_applicable_stage_a_selector_only`
- `final_hold_or_reject_reason`, one of:
  - `not_found_after_search`
  - `found_but_does_not_support_claim`
  - `source_access_blocked`
  - `source_is_rss_or_snippet_only`
  - `claim_overreached_available_evidence`
  - `duplicate_or_baseline_conflict`
  - `out_of_scope_or_selection_defect`
  - `manual_review_required_after_rescue`
  - `not_applicable_stage_a_partitioned_review`

`blocked_source_reason` explains the source/evidence/access failure mode. `final_hold_or_reject_reason` explains the final editorial/workflow conclusion. They must not be collapsed into one field.

If any required rescue metadata is missing for a hold/block/reject/delete/support-only/deferred/draft_blocked item, the stage must stop and report:

- `status: BLOCKED_RESCUE_METADATA_MISSING`
- `missing_rescue_metadata_fields: [...]`
- `affected_items: [...]`
- `no next-stage recommendation`

No stage may finalize hold/block/reject/delete solely because the assistant is uncertain.

Allowed final outcomes after rescue:

1. If a same-event official/body-level source supports the claim, keep or rescue the item within the stage's authorized state boundaries.
2. If evidence supports only a narrower claim, narrow the claim or send to the appropriate revise/content-polish path.
3. If evidence is not found after the bounded rescue pass, hold/block/reject with the rescue log attached.
4. If the item fails lane-fit, duplicate, stale, or source-direction checks after verification, reject/hold with explicit reason.

Stage A selector-only override:

Stage A must not perform external web search, article-body fetch, source_quote generation, or fact_sources generation. For Stage A, rescue means partitioning and bounded-question capture, not searching.

For Stage A non-strict outcomes, use:

- `official_source_checked: NOT_APPLICABLE_STAGE_A_NO_FETCH`
- `alternate_tier1_tier2_checked: NOT_APPLICABLE_STAGE_A_NO_FETCH`
- `blocked_source_reason: not_applicable_stage_a_selector_only`
- `final_hold_or_reject_reason: not_applicable_stage_a_partitioned_review` unless the item is rejected/support-only for a non-evidence reason.

Stage A must instead record:

- `review_pool_partition`
- `review_pool_partition_reason`
- `promotion_precondition`
- `bounded_review_question`
- `recommended_next_action`

This rule must not be used to launder weak evidence into publish readiness. It prevents unverified early abandonment; it does not relax FACT_DISCIPLINE.

## Operational integrated rule — MANDATORY_FETCH_LADDER_BEFORE_DRAFT_BLOCKED_20260507_V2

Stage B must not convert a strict_passed_spec into `draft_blocked` merely because `primary_url` failed, was paywalled, JS-blocked, RSS-only, snippet-only, listing-only, or otherwise inaccessible.

Before any fetch/search attempt, Stage B must build an `event_fingerprint_search_profile` for every strict_passed_spec.

Required `event_fingerprint_search_profile` fields:

- `actor`
- `secondary_actors[]`
- `event_type`
- `project_or_asset_name`
- `amount_or_capacity`
- `location`
- `event_date_or_window`
- `source_owner_candidates[]`
- `official_source_domains_to_check[]`
- `cited_source_domains[]`
- `same_event_search_terms[]`
- `must_match_terms[]`
- `must_not_substitute_terms[]`

Stage B must also record:

- `source_discovery_strategy`
- `official_source_search_ledger[]`
- `cited_primary_search_ledger[]`
- `alternate_source_search_ledger[]`
- `source_discovery_ledger[]`
- `source_discovery_status: completed_verified_source_found|completed_no_verified_source|incomplete`

Before `draft_blocked` is allowed for source/access/evidence reasons, Stage B must attempt this bounded fetch ladder and record it in `fetch_ledger[]`, `source_discovery_ledger[]`, and the blocked item:

1. `primary_url`
2. listed fallback URLs / `source_urls[]` / `source_packets[]`
3. cited publication article body or accessible same article variant
4. issuer, company, agency, regulator, exchange, court, utility, or project owner official release
5. official filing / IR / report / consultation / tender page, if applicable
6. open-access same-event Tier 1 / Tier 2 secondary body source
7. reputable specialty press with body-level article, only if source direction and same-event checks pass

For each discovery/search/fetch attempt, record:

- `attempt_order`
- `ledger_type: official_source_search|cited_primary_search|alternate_source_search|fetch_attempt`
- `source_type_attempted`
- `query_or_url`
- `search_terms_used[]`
- `access_result`
- `supports_core_event: true|false`
- `supports_missing_claims[]`
- `source_direction_check: PASS|FAIL|UNKNOWN`
- `same_actor_event_date_check: PASS|FAIL|UNKNOWN`
- `reason_not_used`

A same-event alternate source must match the same actor, event, date/timeframe, location/project, and quantitative claim direction. If it changes the core event anchor, it is not an alternate source; it is a different candidate and must not be substituted.

Stage B may still draft-block after this ladder if no source supports the core event or if all usable sources fail FACT_DISCIPLINE. The block must include:

- `rescue_attempted: true`
- complete `rescue_attempt_log[]`
- complete source discovery ledgers listed above
- `source_discovery_status: completed_no_verified_source` or `incomplete` with reason
- `blocked_source_reason`
- `final_hold_or_reject_reason`

If event fingerprint/source discovery fields are missing, Stage B must stop and report:

- `status: BLOCKED_SOURCE_DISCOVERY_LEDGER_INCOMPLETE`
- `missing_source_discovery_fields: [...]`
- `no Stage C recommendation`

## Operational integrated rule — LINEAGE_METADATA_REQUIRED_SCHEMA_20260507

Lineage metadata is not optional.

Every Stage A `strict_passed_spec[]` item must include:

- `enhanced_selector_precision_version`
- `selector_policy_version`
- `strict_pass_gate.status`
- `strict_pass_gate.all_six_conditions_passed`
- `strict_gate_check`
- `format_risk_tags`
- `execution_anchor_type`
- `execution_anchor_strength`
- `baseline_relation`
- `duplicate_risk`
- `staleness_decision`
- `source_access_risk`

Every downstream stage must preserve these fields or explicitly mark them `not_applicable` with a reason.

Stage B output must include:

- `lineage_integrity_status: PASS|FAIL`
- `stage_a_validity_guard_applied: true`
- `strict_gate_metadata_preserved: true|false`
- `execution_anchor_metadata_preserved: true|false`
- `superseded_lineage_mixed: false`
- `manual_integrated_rule_mixed: false`
- `previous_run_output_mixed: false`

Stage C and Stage C revise outputs must include:

- `strict_gate_acceptance_guard_applied: true`
- `accepted_fact_safe_with_missing_strict_gate_count: 0`
- `accepted_pool_lineage_status: PASS|FAIL`
- `lineage_integrity_status: PASS|FAIL`
- `strict_gate_metadata_preserved: true|false`
- `execution_anchor_metadata_preserved: true|false`
- `superseded_lineage_mixed: false`
- `manual_integrated_rule_mixed: false`
- `previous_run_output_mixed: false`

If any accepted_fact_safe item lacks Stage A strict gate metadata, Stage C must not mark it accepted_fact_safe. It must move the item to `deferred_review_pool`, `revise_required`, `support_source_only`, or `rejected` depending on severity and stage rules.

## Operational integrated rule — EXECUTION_TRANSPARENCY_AND_FILE_VERIFICATION_20260507

For local validation runs, every stage report must identify:

- input files actually opened,
- input counts read from those files,
- output files written,
- post-write verification result,
- count reconciliation after reopening outputs,
- any step not performed.

If a file was not opened or a count was not verified, the assistant must not claim completion for that artifact.

## Operational integrated rule — STAGE_B_EVENT_FINGERPRINT_SOURCE_DISCOVERY_SCHEMA_20260507_V2

Stage B JSON output must include the source discovery artifacts needed to audit false draft_blocking.

Top-level required fields:

- `event_fingerprint_search_profile_count`
- `source_discovery_status_summary`
- `source_discovery_ledger[]`
- `official_source_search_ledger[]`
- `cited_primary_search_ledger[]`
- `alternate_source_search_ledger[]`

Each `evidence_packages[]`, `draft_cards[]`, and `draft_blocked[]` item must carry or reference:

- `event_fingerprint_search_profile`
- `source_discovery_strategy`
- `source_discovery_status`
- source discovery ledger references

If these fields are missing, Stage B must report:

- `status: BLOCKED_SOURCE_DISCOVERY_LEDGER_INCOMPLETE`
- `no Stage C recommendation`

## Operational integrated rule — NO_SILENT_DOWNSTREAM_ENRICHMENT_RULE_20260507_V3

This rule limits and complements `NO_UNVERIFIED_HOLD_OR_DELETE_RULE_20260507`.

The duty to attempt rescue does **not** authorize silent downstream enrichment.

A later-stage source, source_quote, number, named entity, claim, or source-derived framing may not be directly inserted into the current card state unless the current prompt explicitly permits that modification or the item is routed to the appropriate controlled validation path.

### Core distinction

- `NO_UNVERIFIED_HOLD_OR_DELETE_RULE`: do not give up before bounded verification/rescue.
- `NO_SILENT_DOWNSTREAM_ENRICHMENT_RULE`: do not quietly absorb later-discovered evidence or claims into a higher state.

Both rules must be satisfied.

### Later-discovered evidence rule

Any evidence, source, quote, numeric claim, named-entity claim, date, capacity, contract term, price, funding amount, or source-derived framing discovered after the original stage must not be silently accepted into the current card state.

It must enter the appropriate controlled pass:

- Stage B revise r1/r2/r3, if it repairs a Stage C `revise_required` item and source augmentation is explicitly authorized when needed.
- Stage C revise validation r1/r2/r3, before a revised item can become `accepted_fact_safe`.
- Evidence QC rescue / 0.5R, if it repairs `source_gap`, `claim_gap`, RSS-only, snippet-only, or quote-status failures after 0.5.
- Content polish supplemental, if visible fields change after evidence rescue.
- Final QC, before `publish_ready`.

Later-discovered evidence may be accepted only after all are true:

1. source direction compatibility is confirmed,
2. fact/source quote coverage is mapped,
3. unsupported prior claims are narrowed or removed,
4. lineage metadata is preserved,
5. supplemental or revise-pass accounting is explicit,
6. the item passes the next required validation gate.

No later-discovered source or claim may be directly inserted into:

- `accepted_fact_safe`
- `addable_merge_safe`
- `evidence_complete`
- `source_claim_covered`
- `content_enriched`
- `language_terminology_polished`
- `publish_ready`
- final payload
- PR candidate
- GitHub-ready output

without passing the required revalidation gate.

### When the current stage is not authorized to modify evidence or visible claims

If useful later evidence is discovered in a stage that is not authorized to modify `fact_sources`, `source_quote`, or visible claims, record it as metadata only:

- `rescue_candidate_evidence[]`
- `source_augmentation_needed: true`
- `recommended_return_stage`
- `reason_current_stage_cannot_absorb_evidence`

Then stop state advancement for that item until the required validation pass is completed.

### Required blocker

If a stage attempts to use later-discovered evidence without the appropriate controlled validation path, stop and report:

- `status: BLOCKED_SILENT_DOWNSTREAM_ENRICHMENT_ATTEMPT`
- `invalid_evidence_or_claims: [...]`
- `recommended_return_stage`
- `no next-stage recommendation`

### Mandatory output ledger for supplemental/revise paths

Any revise, rescue, or supplemental pass that uses later-discovered evidence must include:

- `later_discovered_evidence_used: true`
- `later_discovered_evidence_ledger[]`
- `source_discovery_or_rescue_pass_id`
- `authorized_modification_scope`
- `validation_gate_passed`
- `lineage_metadata_preserved: true`

### Final rule

Do not confuse rescue with laundering.

A valid rescue path proves the claim.  
Silent downstream enrichment hides the claim.  
The first is required when evidence may exist.  
The second is prohibited.



# V4 Addendum — Find, Verify, Integrate; Caveat Auto-0.5R; Review Pool/Treasure Review


## Operational integrated rule — FIND_AND_INTEGRATE_WITH_VALIDATION_RULE_20260507_V4

This rule clarifies the relationship between rescue, caveat handling, later-discovered evidence, and downstream state discipline.

The workflow must not abandon a potentially valid card, claim, source, quote, number, source-owner confirmation, original-data source, review-pool item, or treasure candidate merely because the first source is weak, blocked, incomplete, RSS-only, snippet-only, paywalled, caveated, or initially hard to verify.

The assistant must make a good-faith verification effort before hold/block/reject/delete/claim deletion.

If valid evidence is found at any point in the run, the evidence must not be ignored.

However, later-discovered evidence must not be silently inserted into a downstream state. It must be routed through the appropriate controlled validation path and integrated if it passes:

- Stage B evidence package, if found during Stage B and within the original Stage A strict spec.
- Stage B revise r1/r2/r3, if repairing a Stage C revise_required item.
- Stage C revise validation, before accepted_fact_safe.
- Prompt 0.5R evidence rescue or source-strength review, if found during or after Evidence QC.
- Prompt 0.6 supplemental, if visible fields, fact_sources, urls, or source_quote fields change after rescue.
- Prompt 0.7 Final QC, before publish_ready.
- Prompt 0.8 merge prep only after publish_ready.

If the evidence passes the appropriate validation gate, it should be incorporated into the card, evidence package, source-claim coverage map, or supplemental payload as applicable.

If it fails, the failure must be recorded with:

- rescue_attempted: true
- rescue_attempt_log[]
- searched_source_types[]
- official_source_checked
- alternate_tier1_tier2_checked
- blocked_source_reason, if applicable
- final_hold_or_reject_reason

A later-discovered valid source must not be dropped merely because it was found after the initial stage.
A downstream stage must not advance the card while material valid evidence remains unvalidated.

If a stage is not authorized to absorb the later-discovered evidence, it must record:

- rescue_candidate_evidence[]
- source_augmentation_needed: true
- recommended_return_stage
- reason_current_stage_cannot_absorb_evidence
- status: BLOCKED_SILENT_DOWNSTREAM_ENRICHMENT_ATTEMPT, if the item would otherwise advance with unvalidated evidence

This rule supersedes any weaker interpretation of NO_SILENT_DOWNSTREAM_ENRICHMENT. The point is not to suppress later evidence. The point is to find valid evidence, validate it, and then integrate it through the correct state ladder.


## Operational integrated rule — SOURCE_STRENGTH_CAVEAT_AUTO_0_5R_RULE_20260507_V4

Prompt 0.5 must distinguish a clean evidence pass from a caveated evidence pass.

A card may enter Prompt 0.6 directly only if it is:

- evidence_complete_and_source_claim_covered,
- source_claim_coverage_complete,
- free of material source_strength_caveat,
- free of official/source-owner/original-data caveat,
- free of single-source or source-tier caveat that materially affects external-publication confidence.

If Prompt 0.5 leaves any statement such as:

- "official source would strengthen this"
- "original data would be stronger"
- "issuer/source-owner confirmation would improve confidence"
- "single-source exception requested"
- "Tier 2 source sufficient but not ideal"
- "source-strength caveat remains"
- "primary/original dataset would improve confidence"
- "regulator/company/agency source should be checked if available"

then the card is not a clean pass. It must be routed to:

- recommended_0_5R_source_strength_review[]

For external-publication, newsletter, or SBTL-facing outputs, recommended_0_5R_source_strength_review[] is treated as required unless the user explicitly waives it.

Prompt 0.5 output must include:

- source_strength_clean_pass[]
- recommended_0_5R_source_strength_review[]
- mandatory_0_5R_evidence_rescue[]
- source_strength_caveat[]
- source_strength_caveat_count
- caveat_triggered_0_5R_count
- caveat_waived_by_user: true/false
- caveat_waiver_reason, if applicable

If new evidence is found in 0.5R source-strength review, do not silently merge it into the existing pass state. It must pass:

0.5R re-QC → 0.6 supplemental if visible fields, fact_sources, urls, or source_quote fields change → 0.7 Final QC.

If no stronger evidence is found, record:

- source_strength_review_attempted: true
- source_strength_review_log[]
- final_source_strength_decision: clean_after_review | caveat_retained_but_acceptable | hold_after_review | reject_after_review
- final_hold_or_reject_reason, if held or rejected


## Operational integrated rule — REVIEW_POOL_AND_TREASURE_MUST_BE_REVIEWED_RULE_20260507_V4

Review pools and treasure candidates are not discard buckets.

The workflow must not silently discard, forget, or bury:

- review_pool[]
- candidate_review_pool[]
- watchlist_context_pool[]
- reject_or_support_only_pool[]
- support_source_only[]
- DROPPED stories
- TRIAGE_FILTERED stories
- missed_treasure candidates
- newsletter_expanded_added_treasure items
- any user-specified watchlist or treasure universe

These items are not automatically eligible for Stage B. They must not be auto-promoted.

For `final_news_llm_input_newsletter_expanded_*.json`, the expanded portion means:

```text
newsletter_clean kept stories
+ selected TRIAGE_FILTERED treasure card leads
```

The added treasure leads are review-only recall candidates. `treasure_score`,
`treasure_tier`, `newsletter_clean_reason: TRIAGE_FILTERED_TREASURE_CARD_LEAD`,
`newsletter_clean_selection_role: TREASURE_CARD_LEAD`, `newsletter_clean_score`,
`newsletter_anchor_matches`, `positive_signals`, and
`newsletter_positive_signals` are not acceptance, evidence, strict-pass, or
Stage-B-readiness signals.

If an expanded treasure item is valid, it must first pass an explicit
user-authorized review/promotion run and the same Stage A strict-pass gate as
any other candidate. Otherwise it remains in candidate review, watchlist, reject,
or support-only accounting.

However, when a review_pool/treasure review is triggered by the source input, prompt, user instruction, or retrospective integrated rule, the workflow must explicitly account for them and review them through a bounded review path.

For candidate_review_pool[] items, record:

- bounded_review_question
- promotion_precondition
- recommended_review_method
- evidence_or_duplicate_question
- source_or_date_question, if applicable
- final_review_pool_disposition

Allowed final_review_pool_disposition values:

- not_cardable_after_review
- support_source_only_after_review
- watchlist_only_after_review
- duplicate_or_reinforcement_after_review
- promote_to_strict_spec_after_review
- needs_user_decision_after_review

Disposition is not deletion. Every item that receives a `final_review_pool_disposition` must also appear in `review_pool_resolution_ledger[]` with:

- `story_id` or `grouped_story_ids`
- `upstream_status`
- `original_review_pool_partition`
- `final_review_pool_disposition`
- `disposition_basis`
- `reviewed_by_stage_or_pass`
- `review_artifact_id`
- `carry_forward_policy` = `closed_not_cardable` | `carry_forward_to_watchlist` | `support_source_only` | `candidate_for_authorized_promotion` | `needs_user_decision`
- `next_action_condition`

`not_cardable_after_review` is allowed only after a bounded item-specific review is recorded. It must not be used as a generic delete label.

A genuinely hard-reject item may be closed, but closure requires at least one specific hard-reject basis such as `out_of_scope`, `consumer_noise`, `local_noise`, `duplicate_without_incremental_value`, `stale_without_fresh_angle`, `source_broken_unrecoverable`, `generic_keyword_only`, or `not_sbtl_lane`. Closure must preserve the item in the ledger with `carry_forward_policy: closed_not_cardable` and a non-empty `disposition_basis`.

Hard-reject basis decision tests:

- `out_of_scope`: close only when the article has no battery, EV, charging, energy-storage, grid-flexibility, critical-minerals, battery-materials, recycling, supply-chain, tariff, subsidy, industrial-policy, or SBTL-adjacent strategic content. If any concrete SBTL-adjacent actor, asset, policy, material, capacity, customer, facility, or transaction appears, do not use this basis.
- `not_sbtl_lane`: close only when the subject is in an adjacent industry but the article gives no usable SBTL lane question. If a plausible question can be written about supply chain, localization, demand, cost, regulation, technology adoption, or competitive position, route to review/watchlist.
- `consumer_noise`: close only when the story is primarily consumer lifestyle, retail price, infotainment, personal-use gadget, app UX, travel, entertainment, or ordinary car review content, with no industrial, infrastructure, sourcing, policy, fleet, manufacturing, battery, charging, or grid implication.
- `local_noise`: close only when the story is a local incident, traffic notice, routine municipal update, crime/accident note, or local event with no named industrial actor, scalable deployment, policy signal, facility, procurement, recall, safety rule, or market implication.
- `duplicate_without_incremental_value`: close only when the item is the same event as an existing strict/baseline/lead item and adds no new source owner, number, date, geography, customer, capacity, official confirmation, contradiction, or materially better source. If it adds any of those, route to support-only or existing reinforcement.
- `stale_without_fresh_angle`: close only when the event is outside the run window and the article provides no fresh execution, regulatory, financial, customer, facility, data, or market-development angle. If freshness is uncertain, route to review with `source_or_date_question`.
- `source_broken_unrecoverable`: close only when the source is inaccessible, non-article, paywalled-with-no-usable-snippet, malformed, or content-mismatched and no headline/snippet/RSS/source_packet evidence supports a bounded review question. If a source gap might be repaired downstream, route to review; Stage A must not fabricate missing evidence.
- `generic_keyword_only`: close only when the item merely contains generic terms such as battery, energy, EV, lithium, charging, storage, AI, power, or supply chain without a concrete actor, event, asset, policy, metric, source-owner claim, or strategic question.

Anti-overclosure rule: if two or more weak signals exist across actor, event, asset, policy, metric, geography, source quality, or SBTL lane relevance, do not hard-reject. Route to `candidate_review_pool[]` or `watchlist_context_pool[]` with the unresolved question.

Hard-reject confidence must be `high`. If confidence is `low` or `medium`, the item is not closed; it is reviewed, watched, or support-only.


`needs_user_decision_after_review` is open, not closed. It must carry forward until the user decides or a later authorized review resolves it.

No stage may reduce, omit, or summarize away review_pool items unless the missing items are represented in `review_pool_resolution_ledger[]` or `review_pool_deferred[]`. If a prior review_pool universe exists but the current stage is not authorized to process it, the stage must report `review_pool_deferred_count` and preserve item IDs or an artifact reference. Missing ledger coverage is `BLOCKED_REVIEW_POOL_LEDGER_GAP`.

For watchlist_context_pool[] items, record:

- why_context_only
- future_trigger_to_reopen
- recommended_monitoring_action

For reject_or_support_only_pool[] items, record:

- reject_or_support_only_basis
- whether_support_source_only
- final_reason

For DROPPED / TRIAGE_FILTERED / treasure candidates, if dropped_review_treasure_hunt or equivalent is triggered, Stage A or the authorized treasure review pass must record:

- treasure_hunt_trigger_reason
- treasure_sample_strategy
- sampled_story_ids[]
- non_sampled_story_ids[] with reason
- treasure_review_result
- treasure_candidate_review_pool[]
- treasure_watchlist_context_pool[]
- treasure_reject_or_support_only_pool[]
- treasure_promotion_precondition
- treasure_bounded_review_question
- final_treasure_disposition

No item from review_pool or treasure may be promoted directly to Stage B.

Promotion requires an explicit user-authorized review_pool/treasure promotion run. If promoted, the item must become a new strict_passed_spec candidate, pass the same Stage A strict-pass gate, and then proceed through Stage B, Stage C, 0.4, 0.5, 0.6, and 0.7 like any other candidate.

Authorized review_pool/treasure promotion protocol:

- Input universe must be explicit: `candidate_review_pool[]`, `treasure_candidate_review_pool[]`, or named item IDs only.
- The pass must start from the prior ledger rows; it must not reload the full final input and silently change the universe.
- For each reviewed item, output exactly one disposition: `promote_to_strict_spec_after_review`, `watchlist_only_after_review`, `support_source_only_after_review`, `duplicate_or_reinforcement_after_review`, `not_cardable_after_review`, or `needs_user_decision_after_review`.
- Promotion requires a fresh strict-pass gate object with all six Stage A conditions, not a reference to score, treasure tier, user interest, or prior review_pool membership.
- Promoted items must be emitted as `rescue_candidate_strict_spec[]` or `promoted_strict_passed_spec[]` with `promotion_source_pool`, `promotion_review_artifact_id`, and `promotion_user_authorized: true`.
- Non-promoted items must remain visible in `review_pool_resolution_ledger[]` with carry-forward or closure policy.
- The promotion pass may recommend Stage B only for promoted strict specs. It must not recommend Stage B for the unresolved remainder.


The guiding principle is:

- Do not ignore review_pool or treasure.
- Do not auto-promote review_pool or treasure.
- Review them, account for them, and if valid, route them through the formal state ladder.


## Prompt 0.2 v4 source discovery output schema additions

For each strict_passed_spec, Stage B must output:

- event_fingerprint_search_profile
- source_discovery_strategy
- official_source_search_ledger[]
- cited_primary_search_ledger[]
- alternate_source_search_ledger[]
- source_discovery_status
- source_discovery_ledger[]

If a valid source is found by this search, it must be incorporated into the evidence_package before drafting.
If no valid source is found, draft_blocked may be used only after the ledgers prove the fetch ladder and source discovery attempt were completed.


## Operational integrated rule — STAGE_B_SOURCE_DISCOVERY_STATUS_AND_CAVEAT_ROUTING_20260508_V6

This v6 integrated rule tightens Stage B event-fingerprint source discovery output so fallback/rss-rich cases are auditable and routed correctly to 0.5R when source strength remains caveated.

Every Stage B strict spec must include a `source_discovery_status` and `source_strength_caveat_routing_decision`.

Required per-spec fields:

```json
"event_fingerprint_search_profile": {
  "actor": "...",
  "event_type": "...",
  "amount_or_capacity": "...|not_applicable",
  "date_window": "...",
  "source_owner_candidates": ["..."],
  "same_event_disambiguators": ["..."]
},
"source_discovery_status": "completed_verified_source_found|completed_verified_with_source_strength_caveat|completed_no_verified_source|incomplete",
"primary_source_status": "body_verified|official_verified|rss_rich_only|snippet_only|blocked|unreadable|not_applicable",
"fallback_body_source_status": "body_verified|official_verified|not_found|not_attempted_with_reason",
"official_source_attempt_status": "official_found|official_not_found|official_blocked|not_applicable_with_reason",
"source_strength_caveat_routing_decision": "clean_no_0_5R_needed|route_to_0_5R_source_strength_review|draft_blocked|not_applicable",
"source_discovery_ledger": []
```

Routing rule:

- If body/official evidence is strong and no material caveat remains: `clean_no_0_5R_needed`.
- If evidence supports drafting but relies on rss-rich fallback, single-source Tier 2, unofficial body corroboration, or missing official/original source: `route_to_0_5R_source_strength_review`.
- If no verified same-event source supports the core event: `draft_blocked` with `final_hold_or_reject_reason`.

Stage B must not resolve a source-strength caveat by silently inflating the claim. It must preserve the caveat into the draft/evidence package so 0.5 can route it to 0.5R.


## Source Diversity & Corroboration QC Rule — 2026-05-07 v8

Source diversity is not claim diversity.

Claim diversity checks whether visible cards repeat the same editorial angle, wording pattern, implication structure, or strategic question.

Source diversity checks whether each visible claim is supported by an adequate evidence structure:

- source count
- source independence
- official / primary source presence
- body-level quote quality
- evidence_role distribution
- source_url coverage in urls[]
- single-source exception validity
- whether background/context sources are being misused as core-event evidence

Do not treat a claim-diverse card as source-diverse.
Do not treat multi-source background context as core-event corroboration unless the source independently supports the visible core claim.

A single-source card may pass only when the single source is official, primary, regulatory, filing, primary dataset/report, or body-level evidence sufficient for every core visible claim.

If a card involves safety, environmental incidents, regulation, policy impact, subsidy/tariff claims, market share, rankings, first/largest claims, sensitive company risk, litigation/IP risk, high-signal strategic interpretation, or major market-structure claims, require either:

1. official/primary source support, or
2. at least two independent body-level sources that support the same core event/claim.

If source diversity is insufficient:

- do not mark publish_ready
- route to needs_return_to_evidence_qc or needs_source_augmentation
- or narrow visible fields so the claim strength matches the available evidence.

Single-source exceptions must be explicit:

```json
"single_source_exception": {
  "allowed": true,
  "reason": "official primary release directly supports all core claims",
  "limits": [
    "No broad market-impact claim beyond source.",
    "No unsupported causal claim.",
    "No unsupported forecast."
  ]
}
```

Visible-source URL sync is a hard gate: every `fact_sources[].source_url` that supports a visible field must be present in the card `urls[]` unless explicitly marked as `supporting_context_only_not_visible_claim_support` with a reason.

## Source Diversity Source-Discovery Alignment — 2026-05-19 v9

For Stage B and any later stage that performs source augmentation, source diversity requires a recorded same-event source-discovery effort, not just a count of URLs already attached to the card.

Required distinction:

- `fact_package` / `evidence_package` proves what was fetched and quoted.
- `source_discovery_ledger[]` proves what was searched, checked, rejected, or accepted.
- `source_claim_coverage_map[]` proves which fetched source supports each visible claim.

A card must not be treated as source-diverse merely because it has multiple URLs if those URLs are syndications, reposts, snippets, landing pages, same-owner duplicates, or background-only sources.

For every candidate that reaches Evidence QC, require one of these states:

1. `source_diversity_status: PASS_MULTI_SOURCE` with at least two independent body-level sources supporting the same core event or claim.
2. `source_diversity_status: PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION` with an explicit `single_source_exception` object and a completed `source_discovery_ledger[]`.
3. `source_diversity_status: HOLD_NEEDS_SOURCE_AUGMENTATION` when the card is promising but corroboration/source-discovery is incomplete.
4. `source_diversity_status: FAIL_SOURCE_DIVERSITY` when the visible claim cannot be supported without overclaiming.

`PASS_SINGLE_SOURCE` without official/primary basis is not allowed. informal single-source-acceptable phrasing is not enough; the exception must name why the source is official/primary/body-level sufficient, what claims are covered, what claims are excluded, and what source-discovery attempts failed to find corroboration.

For sensitive or high-interpretation claims, including safety, environmental incidents, regulation, policy impact, subsidy/tariff, market share, ranking, first/largest, litigation/IP risk, sensitive company risk, high-signal strategic interpretation, or major market-structure claims, Evidence QC must require either official/primary support or two independent body-level sources. If neither exists, narrow the visible claim or hold for source augmentation.

Web search must never create a new candidate silently. It may only verify or augment the same Stage A event anchor, and any newly discovered same-event source must be recorded in `source_discovery_ledger[]` and then mapped in `fact_sources[]` and `source_claim_coverage_map[]` before it supports visible text.

Visible-source URL sync remains a hard gate: every `fact_sources[].source_url` supporting visible text must appear in `urls[]`. Background-only sources may be absent from `urls[]` only when marked `supporting_context_only_not_visible_claim_support` with a reason.


## Stage B source diversity precheck

For every `draft_cards[]` and every `draft_blocked[]` item, Stage B must include a source diversity precheck object. This is not the final source-diversity decision; it is an early risk flag for 0.5.

Required object:

```json
"source_diversity_precheck": {
  "distinct_source_url_count": 0,
  "distinct_source_domain_count": 0,
  "official_or_primary_source_present": false,
  "independent_secondary_source_present": false,
  "single_source_candidate": false,
  "source_diversity_required": false,
  "source_diversity_reason_codes": [],
  "single_source_exception_candidate": false,
  "single_source_exception_candidate_reason": null,
  "background_context_source_count": 0,
  "core_event_source_count": 0,
  "source_diversity_precheck_status": "PASS_PRECHECK | CAVEAT_ROUTE_TO_0_5 | NEEDS_0_5_SOURCE_DIVERSITY_REVIEW"
}
```

Stage B must not use this precheck to mark evidence_complete, source_claim_covered, or publish_ready.

If `source_diversity_required=true` or `single_source_candidate=true`, Stage B must carry a `source_strength_caveat_routing_decision` forward to 0.5.


## Operational integrated rule — Stage B field-schema HARD RULES — 20260513

이 패치는 Stage B 출력 draft_card 의 4개 필드 (`signal`, `cat`, `sub_cat`, `region`) 와 `id` 형식에 대해 HARD RULE 을 박는다. run 20260512_134524 retrospective 결과 도입: 해당 run 의 Stage B 출력 15/15 카드가 모두 schema deviation 을 가져 0.7 Final QC 에서 mass-fail 했음.

### HARD RULE — signal field

- 값: Stage A spec 의 `signal_estimate` 를 **verbatim 복사** 한다.
- 허용 값: `top` | `high` | `mid` — 이 셋 외 어떤 값도 허용되지 않는다.
- **금지**: descriptive narrative (예: `"first_municipal_concession_agreement_for_curbside_charging"`), 대문자 변형 (`"HIGH"`, `"TOP"`), 다른 카테고리 라벨 (`"info"` 등)
- 이유: `docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md` §1 의 `"signal": "top|high|mid"` lock. descriptive narrative 는 `sub` / `gate` 필드에서 다룬다.
- Stage A signal_estimate 가 위 셋이 아닌 경우: `draft_blocked_schema` 로 분기하고 `block_reason: "stage_a_signal_estimate_non_canonical"` 기록.

### HARD RULE — cat field

- 값: `docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md` §3 의 locked 12개 중 **정확히 하나**:
  `Battery | ESS | Materials | EV | Charging | Policy | Manufacturing | AI | Robotics | PowerGrid | SupplyChain | Other`
- **금지**: production legacy 의 non-locked 값 (`Solar`, `Hydrogen`, `Equity`, `Energy`, `Strategy`, 한국어 compound 등). 이들은 historical 보존 only — 신규 카드 매핑 금지.
- **금지**: 영어 compound 신조어 (`"EV_charging_infrastructure"`, `"BESS_manufacturing"` 등)
- 12 cat 중 어디에도 명확히 속하지 않으면 `Other` 사용 (신중히)
- 카드가 두 축에 걸치면 더 지배적인 축을 cat 으로, 나머지는 `sub_cat` 에서 반영

### HARD RULE — sub_cat field

- 형식: **한국어 복합어** (Korean compound noun phrase)
- 길이: 8-15자 권장
- **금지**: 쉼표, 세미콜론, `|`, 영어 descriptive (`"residential_BESS_manufacturing"` 등)
- 예시: `도시EV충전인프라`, `BESS자회사출범`, `핵심광물IPO`, `재생동공급망`, `중국수소연료전지`

### HARD RULE — region field

- 값: `KR` | `US` | `CN` | `JP` | `EU` | `GL` — 이 6개 외 허용 안 됨
- 결정 기준: **event 의 primary geography anchor** (기사 출처 국적이 아니다)
- 단일 국가가 명확한 무대면 그 국가 (KR/US/CN/JP); 유럽 국가 또는 EU 제도면 EU; 그 외 국가 또는 다국적이면 GL
- **중요 케이스 — US-specific 판정 기준**:
  - US 시설 (공장/광산/플랜트) 신설·증설·M&A·인수 → **US** (예: Qcells 미시간 Jabil 공장, FH Capital/JinkoSolar 미국 제조법인 인수)
  - 미국 거래소 (NYSE / Nasdaq) IPO·상장 → **US** (예: 선샤인실버 NYSE Form S-1)
  - 미국 시 / 주 / 연방 정부 정책 발표지 기준 적용 → **US**
  - "미국 회사가 글로벌 사업" 자체로는 US 가 아님 — event 의 무대가 미국이어야 US
- **다른 국가 케이스**: 호주·인도·이집트·나우루 등 allowed-set 외 국가 → **GL** (allowed-set 에 없으므로)
- 매체 국적 (Korean media reporting US-specific event 등) 은 region 판정에 무관
- App.jsx 의 strict filter `(c.r || c.region) === filter` 가 newsdesk 노출을 결정하므로 misclassification 시 사용자에게 카드가 안 보임

### HARD RULE — id format

- 형식: `YYYY-MM-DD_REGION_NN`
- `docs/CARD_ID_STANDARD.md` 의 sequence 규칙 (signal 우선순위 → 편집자 판단) 준수
- 같은 `(date, region)` 그룹의 기존 max sequence 보다 +1 부터 배정

### Stage B 출력 self-check (필수)

draft_cards 를 emit 하기 직전, 각 카드에 대해 다음 체크를 수행하고 결과를 `stage_b_self_check` 필드에 기록:

```json
"stage_b_self_check": {
  "signal_canonical": true|false,
  "cat_locked_12": true|false,
  "sub_cat_korean_compound": true|false,
  "region_allowed": true|false,
  "id_format_valid": true|false,
  "all_pass": true|false
}
```

하나라도 `false` 인 카드는 `draft_cards` 가 아니라 `draft_blocked_schema` 로 분기. accounting:

```
strict_passed_spec_count
= draft_cards_count
+ draft_blocked_evidence_count
+ draft_blocked_schema_count   // 새 카테고리
```

### 적용 효과

- 0.7 Final QC Gate 7 mass-fail 차단
- 0.7 ad-hoc micro-fix pass 제거
- codex_followup remediation rounds (cat / region) 제거
- Stage B 단계에서 schema 정합성을 즉시 보장 → 5개 downstream stage (0.3 / 0.4 / 0.5 / 0.5R / 0.6) 의 처리 효율 향상

<!-- INTEGRATED_RULE_BEGIN: STAGE_B_VISIBLE_FIELD_KOREAN_ONLY_POLICY_20260514_v2 -->
## Operational integrated rule P_012 — Stage B visible field Korean-only language policy — 20260514_v2

### 문제 정의

run 20260513_165421 의 user instruction (2026-05-14):
> "중간 중간 외국어(영어, 중국어) 특히 중국어일본어는 없어야해"
> "고유명사/회사명/ 등은 외국어(한국어 병기) 또는 반대로"

baseline 744 카드 분석 결과:
- 한국어(영문) 병기 패턴: **450건** dominant
- 영문(한국어) 병기 패턴: 75건 secondary
- 한자/일본어 잔존: 37 카드 (元 15회, 美 6회, 储 6회, 中 4회 등)
- 신규 24 카드도 Stage B drafting 단계에서 중국어 inherited

→ Stage B 드래프팅 단계에서 visible field 의 언어 정책을 HARD RULE 화 필요.

### HARD RULE — visible field language policy

Stage B 의 draft_cards 의 다음 visible fields **MUST** 한국어 + ASCII 만 포함:

- `title`
- `sub`
- `gate`
- `fact`
- `implication[]` (각 항목)
- `sub_cat` (Korean compound 기존 P_001 유지)

**허용**:
- 한글 (가-힣)
- ASCII (영문 letters, numbers, punctuation, whitespace)
- 한국어(English) 또는 한국어 (English) 병기 패턴
- 한자(汉字) — 한국어(English) 병기의 일부로만 허용. standalone 한자 금지.

**금지**:
- 중국어 단독 (汉字 단독 표기): `元`, `美`, `中`, `小鹏`, `天齐锂业` 등
- 일본어 hiragana/katakana: `ソフトバンク`, `真水` 등
- 한자 prefix: `美 2GW`, `中 시장` 등

**예외**:
- `fact_sources[].source_quote` 는 원문 인용 보존을 위해 본 정책 면제

### Bilingual notation rules (baseline 분석 기반)

| 카테고리 | 정책 | 예시 |
|---|---|---|
| Standard abbreviations | English-only | CATL, BYD, BNEF, LFP, ESS, BESS, GWh, MWh, IPO, MOU |
| Familiar transliterations | Korean-only | 비야디, 샤오펑, 니오, 지커, 지리, 샤오미, 칭타오에너지 |
| First-occurrence proper nouns | korean(english) bilingual | 톈치리튬(Tianqi), 후난위넝(Hunan Yuneng), 룽바이(Ronbay) |
| Standard org acronyms | korean(english) 또는 english(korean) | 한국전자기술연구원(KETI), AMPC(첨단제조생산세액공제) |
| Hanja prefix (한자 단독) | 한국어 변환 | 美→미국, 中→중국, 英→영국, 印→인도, 日→일본 |
| Hanja currency | 한국어 변환 | 元→위안 |
| Hanja place names | Korean transliteration | 北京→베이징, 上海→상하이, 重庆→충칭, 宁夏→닝샤, 사카이市→사카이시 |
| Japanese (Hiragana/Katakana) | Korean transliteration | ソフトバンク→소프트뱅크, トヨタ→토요타 |

### Stage B 출력 self-check 확장

`stage_b_self_check` 필드에 항목 추가:

```json
"stage_b_self_check": {
  "signal_canonical": true,
  "cat_locked_12": true,
  "sub_cat_korean_compound": true,
  "region_allowed": true,
  "id_format_valid": true,
  "visible_fields_foreign_char_free": true,   // 신규
  "all_pass": true
}
```

`visible_fields_foreign_char_free` = false 인 카드는 `draft_cards` 가 아니라 `draft_blocked_schema` 로 분기.

### Regex 검증 패턴

```python
import re
CHINESE_PATTERN = re.compile(r'[\u4E00-\u9FFF]')
JAPANESE_PATTERN = re.compile(r'[\u3040-\u309F\u30A0-\u30FF]')

def check_korean_only(text):
    """Returns (passes, foreign_chars_found)."""
    if not text: return True, []
    cn = set(CHINESE_PATTERN.findall(text))
    jp = set(JAPANESE_PATTERN.findall(text))
    if cn or jp:
        return False, list(cn) + list(jp)
    return True, []

# Stage B draft card check
def stage_b_card_korean_check(card):
    fields_to_check = ['title','sub','gate','fact','sub_cat']
    for field in fields_to_check:
        ok, foreign = check_korean_only(card.get(field,''))
        if not ok:
            return False, f"{field}: {foreign}"
    for i, imp in enumerate(card.get('implication',[])):
        ok, foreign = check_korean_only(imp)
        if not ok:
            return False, f"implication[{i}]: {foreign}"
    return True, ""
```

### 적용 효과

- 외국어 cleanup round (run 20260513_165421 의 v3/v4) 제거
- baseline 보존 원칙과 호환 (Stage B 단계 enforcement → baseline 은 점진적으로만 정리)
- Codex review surface 감소 (visible field foreign char 0)

## R3C_P01 — Stage B evidence-package gate (mechanically enforced)

> run 20260516_012728 retrospective integrated rule. P0.

Stage B 는 `strict_passed_spec[]` 의 모든 spec 에 대해, **draft card 를 하나라도
생성하기 전에** evidence package 가 존재하고 그 안에 **최소 1개의 fetch 된
body-level source** 가 있음을 확인해야 한다.

이 규칙은 prose 권고가 아니라 **기계적 게이트**다:

- 동반 스크립트: `validation_scripts/stage_b_evidence_gate.py`
- 실행: `python3 validation_scripts/stage_b_evidence_gate.py <stage_b_output.json>`
- 게이트 동작:
  - strict spec 에 evidence_package / fetch_ledger 가 없으면 → 해당 draft 차단,
    상태 `BLOCKED_STAGE_B_EVIDENCE_PACKAGE_MISSING`.
  - source_url 이 landing-page 패턴(host 루트, article 경로 없음)이면 flag.
  - 하나라도 fail 이면 Stage B 출력은 무효이며 draft 를 진행할 수 없다.

근거: 1차 시도는 fetch_ledger 0건으로 32 카드를 작성 (PV_001). 규칙은
이미 있었으나 구조적으로 draft 를 막는 장치가 없었다. 이 게이트가 그것을 강제한다.

## FIX-001 — PROVIDED_SOURCE_IS_NOT_EVIDENCE_RULE

A provided URL, `primary_url`, triage URL, uploaded link, source hint, Stage A `usable_text`, or Stage A `context_text` is **not evidence by itself**.

It is only an evidence candidate. It becomes evidence only after Stage B has fetched or directly inspected the source, recorded the resolved `source_url`, extracted body-level / official-material / document-level support, captured `source_quote`, mapped that quote to a specific claim, recorded fetch metadata, and included it in `evidence_package` and `fetch_ledger`.

A `fact_sources` entry built only from a provided URL without fetched/directly inspected evidence is invalid.

## FIX-003 — PRIMARY_URL_TERM_COLLISION_RULE

In Stage A outputs, `primary_url` is not a primary source and not verified evidence.

`primary_url` means only the provided/source-candidate URL selected as the representative starting point for Stage B source discovery. It must not be interpreted as Tier 1, official, primary evidence, or an evidence package.

Preferred schema annotation for every `strict_passed_spec[]` item:

```json
{
  "provided_source_candidate_url": "...",
  "primary_url_semantics": "provided_source_candidate_not_evidence",
  "stage_a_evidence_status": "not_evidence_complete_no_fetch",
  "stage_b_evidence_package_required": true
}
```

Replace any wording equivalent to “fetch primary_url and prepare an evidence package” with: Stage B must build a valid `evidence_package` before drafting; `primary_url` is only one provided source candidate and must be independently verified or replaced via the source-discovery ladder.

## FIX-004 — Evidence gate must distinguish `draft_card` and `draft_blocked`

For `draft_card`, a valid evidence package is mandatory: at least one fetched body-level, official-material, or document-level core event source with `source_quote` and claim mapping.

For `draft_blocked`, a valid evidence package is not required, because the correct outcome may be that no valid evidence exists. Instead, `draft_blocked` must include rescue/source-discovery accounting: `rescue_attempted=true`, source/fetch/discovery ledger entries, `blocked_source_reason`, and `final_hold_or_reject_reason`.

A legitimate `draft_blocked` with populated rescue ledger must pass the evidence gate. A `draft_blocked` with no rescue/fetch ledger must block.

## FIX-005 — Stage A/B must emit required lineage metadata

Prompt 0.4 lineage guard must remain hard. Do not soften it.

The corrected diagnosis from run `20260516_012728` is that Stage A and Stage B failed to emit lineage fields that their own prompts already required. This is execution non-compliance, not a schema-version gap.

Stage A exit must fail if any `strict_passed_spec[]` item lacks required lineage fields from `SCHEMA_CONTRACT_STAGE_LINEAGE.md`, including `enhanced_selector_precision_version`, `selector_policy_version`, `strict_gate_check`, `staleness_decision`, `source_access_risk`, and `strict_pass_gate.all_six_conditions_passed`.

Stage B preflight must run `stage_a_validity_guard` before drafting. Stage B output must include `lineage_integrity_status`, `stage_a_validity_guard_applied`, `strict_gate_metadata_preserved`, `execution_anchor_metadata_preserved`, `superseded_lineage_mixed`, `manual_integrated_rule_mixed`, and `previous_run_output_mixed`.

If required fields are missing, stop with `BLOCKED_STAGE_OUTPUT_SCHEMA_NONCOMPLIANT` or `BLOCKED_STAGE_A_LINEAGE_NONCOMPLIANT`.

## FIX-007 — Shared schema contract and stage-exit conformance check

All stages must reference `SCHEMA_CONTRACT_STAGE_LINEAGE.md`.

Each named stage must run or explicitly satisfy a stage-exit artifact conformance check before recommending the next stage. Missing required fields must stop the stage with:

```text
BLOCKED_STAGE_OUTPUT_SCHEMA_NONCOMPLIANT
```

Do not wait until Prompt 0.4 to discover Stage A/B lineage omissions.

# 02_PROMPT_0_2_Stage_B_r0.md — Source Diversity source-diversity integrated rule

    This integrated rule is authoritative for source-diversity, source-preservation, synthesis,
    visible-source-date and same-source grouping rules. Earlier language that conflicts with this
    integrated rule is superseded only to the extent of that conflict.

    ## Source Diversity source-diversity — common definitions

### 1. Diversity unit

Source diversity is measured by **canonical source identity and editorial independence**, not by
`fact_sources[]` row count.

The following count as one source:

- multiple claims or quotes from the same canonical article URL;
- print/mobile/AMP/RSS mirrors of the same article;
- the same press release copied by multiple syndication sites without independent reporting;
- multiple pages controlled by the same editorial owner that merely repeat the same source text;
- one article split into several `fact_sources[]` entries.

Required calculations:

```text
source_evidence_entry_count = count(fact_sources[])
source_unique_url_count = count(unique canonical article URLs)
source_unique_domain_count = count(unique canonical domains after ownership/syndication review)
source_independent_owner_count = count(editorially independent source owners)
```

`PASS_MULTI_SOURCE` or any equivalent status is prohibited when
`source_independent_owner_count < 2`.

### 2. Preferred evidence-role structure

For each independently cardable event, target three complementary roles:

1. `primary_event_evidence`
   - official notice, regulator, filing, contracting party, project owner, research institution,
     original dataset or source owner;
2. `independent_event_confirmation`
   - independent news agency, financial press, trade press or local reporting that confirms the
     event and identifies omissions, conditions or execution status;
3. `policy_market_context`
   - policy, market, operational, comparable-project or system-impact evidence that materially
     improves `gate` or `implication`.

Two independent source owners are the minimum default. Three complementary roles are preferred.
A source does not satisfy diversity merely by existing; it must make a distinct contribution.

### 3. Source contribution requirement

Every retained source must record:

```json
{
  "source_role": "",
  "source_contribution": "",
  "source_origin_type": "",
  "source_published_date": "YYYY-MM-DD",
  "visible_quote_date": "YYYY-MM-DD"
}
```

`source_contribution` must explain the unique information supplied by that source. Generic values
such as `corroboration`, `additional source`, `supports card`, or `same event` are insufficient.

### 4. Visible-field synthesis requirement

When an additional source supplies material information, at least one of the following visible
fields must be revised using source-locked wording:

- `fact`
- `gate`
- `implication`

The output must record:

```json
{
  "source_synthesis_applied": true,
  "source_synthesis_fields": ["fact", "gate", "implication"],
  "source_synthesis_audit": [
    {
      "source_domain": "",
      "source_role": "",
      "unique_contribution": "",
      "affected_visible_fields": []
    }
  ]
}
```

A card that merely integrates URLs while its visible content still reflects only one article has not
passed source-diversity synthesis.

### 5. Publication date and audit timestamps

The date shown beside a quote must be the article or official-material publication date:

```text
visible date = source_published_date
```

`fetched_at` and `checked_at` are audit timestamps only. They must be preserved but must never be
used as the visible news date.

### 6. Rescue-before-delete rule

A weak, blocked or duplicate source must not be silently discarded when it contains unique useful
information.

Use this order:

1. refetch or locate the source owner/original material;
2. find an independent same-event source;
3. narrow unsupported wording;
4. move unique information into an existing card as reinforcement;
5. place unresolved items in `needs_source_augmentation` or a controlled remediation queue;
6. use hard rejection only when the item is false, irrelevant, irreparable, promotional noise or
   lacks any defensible decision value.

Duplicate-event articles are not separate cards, but their unique facts and quotes must follow the
representative event as support-source candidates.

### 7. Single-source exception

A single-source exception is narrow and rare. It may pass only when all conditions are true:

- the source is official, regulatory, a filing, original dataset, court decision, contracting-party
  release, or original research institution;
- bounded discovery was performed and no independent body-level source was available;
- the card contains only claims supported by that source;
- no broad causal, comparative, first/largest, market-impact or strategic implication is asserted
  unless the source explicitly supports it;
- the exception reason, search ledger and scope limitation are recorded;
- downstream Evidence QC and Final QC separately approve the exception.

A media article alone does not qualify merely because it is detailed.

## Stage B multi-source discovery and synthesis — HARD RULE

Stage B must consume the complete Stage A `same_event_source_cluster[]` and
`support_source_candidates[]`. It may not begin with the representative URL and ignore the rest.

For every strict spec, perform and record:

1. fetch all viable current-run same-event candidates;
2. search for the official/source-owner material;
3. search for an independent same-event confirmation;
4. search for a policy, market or operational context source when it can safely improve the card;
5. identify syndication, ownership overlap and repeated press-release text;
6. calculate canonical URL, domain and independent-owner counts;
7. record each source's unique contribution;
8. draft only after the evidence package and synthesis plan are complete.

Required evidence-package fields:

```json
{
  "same_event_source_cluster_received": true,
  "stage_a_support_sources_attempted": [],
  "source_independence_ledger": [],
  "source_unique_url_count": 0,
  "source_unique_domain_count": 0,
  "source_independent_owner_count": 0,
  "source_role_coverage": {
    "primary_event_evidence": false,
    "independent_event_confirmation": false,
    "policy_market_context": false
  },
  "source_synthesis_plan": [],
  "single_source_exception_candidate": null
}
```

### Draft rule

A default Stage B draft requires at least two independent source owners.

If only one qualifying source remains after bounded discovery:

- do not call it multi-source;
- use `draft_blocked_needs_source_augmentation`, or
- use `draft_card_single_source_exception_candidate` only when the narrow exception conditions are
  fully met;
- set `publish_ready: false`.

### Synthesis rule

The draft must use complementary evidence. At least one non-primary source must contribute a
material condition, independent confirmation, schedule, financing structure, policy scope,
operational risk, market context or limitation to `fact`, `gate` or `implication`.

A second source that merely repeats the first source's release does not satisfy this rule.

### Stage B blockers

```text
BLOCKED_STAGE_A_SOURCE_CLUSTER_MISSING
BLOCKED_STAGE_B_SOURCE_DISCOVERY_INCOMPLETE
BLOCKED_FALSE_MULTI_SOURCE_COUNT
BLOCKED_STAGE_B_SOURCE_SYNTHESIS_NOT_APPLIED
```

    Stop after Stage B. Do not assign accepted_fact_safe or publish_ready.

# Source Diversity / IB-grade + Codex Hardening Integrated rule

Version: `GITHUB_CANONICAL_V1_SOURCE_DIVERSITY_IB_CODEX`  
Generated KST: `2026-07-08T21:18:40.089502+09:00`

This integrated section supersedes earlier conflicting language only to the extent of conflict.  
It does **not** weaken Source Diversity source-diversity. It adds downstream hardening learned from PR #148 and the 20260706_130022 run.

## 1. IB-grade editorial upgrade rule

Cards should not be treated as publishable merely because they are fact-safe.

Before `publish_ready=true`, the pipeline must classify each card into one of the following:

| Tier | Meaning | Publish rule |
|---|---|---|
| `A` / `A-` | IB-grade or near-IB anchor | May be used as lead/anchor signal |
| `B+` | publishable supporting signal | May publish, but must not be described as top-tier anchor |
| below `B+` | insufficient | Must remain deferred, remediation, or support-only |

A `B+` card may be upgraded only through supported visible-field refinement:

- stronger strategic framing;
- clearer `sub`;
- sharper `gate`;
- implication rewritten toward market / policy / supply-chain decision use;
- no unsupported new numbers, contracts, capacity, pricing, or customer claims.

Never upgrade a weak source into a strong source by language alone.

## 2. Visible-field upgrade boundary

When improving title, sub, fact, gate, or implication:

- preserve all source boundaries;
- do not add a new factual claim unless it is directly supported by an existing `fact_sources[]` quote or an added source;
- do not convert `prequalified` into `awarded`;
- do not convert `pilot` into commercial performance;
- do not convert product showcase into customer order, certification, delivery, or revenue;
- do not convert policy award/achievement material into implementing notice unless the notice text is present;
- do not convert “focus / plan / report says” into confirmed CAPEX, customer, chemistry, or production start.

## 3. Single-source publish-ready waiver rule

If a card has:

```text
publish_ready = true
source_independent_owner_count = 1
```

then it must satisfy one of the following:

1. official / regulator / company primary source;
2. reputable market data provider with bounded data claim;
3. reputable trade or mainstream media with body-level evidence and bounded claims;
4. explicit user-provided official body text.

A valid waiver must include:

```json
"single_source_exception": {
  "allowed": true,
  "type": "...",
  "reason": "...",
  "mitigation": "..."
}
```

Invalid patterns:

```json
"single_source_exception": {
  "allowed": false,
  "reason": "two or more source owners..."
}
```

on a publish-ready single-source card is a blocker.

Required blocker:

```text
status = BLOCKED_PUBLISH_READY_SINGLE_SOURCE_WITHOUT_VALID_WAIVER
```

## 4. Stale publish blocker removal rule

No card may be both publish-ready and actively blocked.

Invalid:

```json
{
  "publish_ready": true,
  "state": "publish_ready",
  "do_not_publish_until": "..."
}
```

If the blocker has been satisfied, remove the active field entirely.

Permitted audit trail:

```json
"prior_publish_blocker_removed": {
  "field": "do_not_publish_until",
  "old_value": "...",
  "reason": "...",
  "removed_at_kst": "..."
}
```

Required blocker:

```text
status = BLOCKED_PUBLISH_READY_CARD_HAS_ACTIVE_DO_NOT_PUBLISH_UNTIL
```

## 5. Deferred/watchlist discipline

Do not delete high-value deferred cards simply because official/independent evidence is not yet available.

Use:

- `deferred_watchlist_high_value`
- `conditional_watchlist`
- `support_only_pending`
- `deprioritized_not_deleted`

A deferred card can be promoted only when the missing source-claim coverage is actually satisfied.

## 6. PR / GitHub merge hardening

Before PR or merge:

- verify total count;
- verify latest baseline;
- verify `publish_ready` cards have no active blockers;
- verify single-source publish cards have valid waiver;
- verify no visible internal terms remain:
  - `fetch`
  - `stage`
  - `quote mapping`
  - `baseline` unless user-facing context explicitly requires it;
- verify `source_independent_owner_count` is editorial-owner based, not `fact_sources[]` row count;
- verify UI display groups same canonical URL once;
- verify quote date is article/publication date, not fetch/check date.

## 7. Codex response protocol

If Codex flags metadata inconsistency:

1. Determine whether the issue is a visible claim problem or metadata/QC state problem.
2. Do not expand visible claims unless evidence requires it.
3. Prefer minimal metadata fix if the card is already fact-safe.
4. Add an audit record only if it is non-blocking.
5. Re-run:
   - JSON parse
   - publish-ready blocker scan
   - single-source waiver scan
   - visible internal-term scan
   - total count check

## 8. Required final statuses

A card may be merged only when:

```text
accepted_fact_safe = true
addable_merge_safe = true
evidence_complete = true
source_claim_covered = true
content_enriched = true
language_terminology_polished = true
publish_ready = true
github_ready = true
```

Any waiver or exception must be explicit, bounded, and auditable.


## Stage B extra

Stage B must not draft from source-lite evidence. It must separate official, independent, contextual, and copied/syndicated evidence.
