<!-- REPLACE_ALL_CLEAN_VERSION: LLM_PROMPT_GITHUB_CANONICAL_V1_SOURCE_DIVERSITY_IB_CODEX -->
<!-- Generated KST: 2026-07-08T21:33:49.790191+09:00 -->
<!-- This file is a full clean replacement file. It is not a patch stub. -->

Prompt 0.6v — Reusable Default / Replace All / Content Enrichment & Language-Terminology Polish

Proceed to content enrichment and language/terminology polish only.

Use the current run’s evidence QC output as the only candidate input universe for this step.

This step starts after evidence completeness QC and source-claim coverage QC.

Do not continue from, trust, import, integrated rule, or reuse any previous content-enriched, final, PR candidate, GitHub-ready, publish-ready, or post-QC outputs unless the user explicitly declares them as current-run authoritative inputs.

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
- no content enrichment or language polish work performed

Do not infer replacement rules from memory.
Do not use archived docs.
Do not use branch-only docs.
Do not use local snippets unless the user explicitly provides them as current-run authoritative docs.

Input files:

- Evidence QC JSON: {{EVIDENCE_QC_RESULTS_JSON}}
- Source-claim coverage map: {{SOURCE_CLAIM_COVERAGE_MAP_JSON}}
- Evidence-complete payload: {{EVIDENCE_COMPLETE_SOURCE_CLAIM_COVERED_PENDING_CONTENT_QC_JSON}}
- Evidence QC hold manifest: {{EVIDENCE_QC_HOLD_MANIFEST_JSON}}
- Active baseline cards: {{BASELINE_CARDS_SOURCE}}
- Baseline source declaration: {{BASELINE_SOURCE_DECLARATION}}
- Run tag: {{RUN_TAG}}
- Run label: {{RUN_LABEL_KST}}

Required input rule:

This step requires a valid evidence QC output from the same run.

The evidence QC JSON must include:

- required_docs_check
- run_tag
- run_label
- addable_merge_safe_input_count
- evidence_complete_and_source_claim_covered[]
- addable_hold_source_gap[]
- addable_hold_claim_gap[]
- needs_source_augmentation[]
- evidence_qc_rejected[]
- review_pool_deferred[]
- source_claim_coverage_map[]
- evidence_qc_accounting_matches_input_count

If evidence QC JSON is missing, invalid, incomplete, not from the same run, or has accounting mismatch, stop and report:

- status: BLOCKED_EVIDENCE_QC_INVALID
- reason: [...]
- no content enrichment or language polish work performed


## Upstream lineage integrity gate

This prompt is downstream of selector, evidence, content, and/or production gates. It must not repair or launder an invalid upstream lineage.

Before doing any work, validate that the current-run evidence QC output carries a lineage integrity statement from the immediately previous step.

Required lineage fields, unless the previous step explicitly marks a field `not_applicable` with reason:

- `run_tag` matches this run
- `lineage_integrity_status: PASS`
- `stage_a_validity_status: PASS` or `not_applicable_after_validated_baseline_revalidation`
- `artifact_consistency_status: PASS` or `not_applicable_after_validated_baseline_revalidation`
- `accepted_pool_lineage_status: PASS` or `not_applicable_before_stage_c_pool`
- `strict_gate_metadata_preserved: true` or `not_applicable_after_non_card_stage`
- `execution_anchor_metadata_preserved: true` or `not_applicable_after_non_card_stage`
- `superseded_lineage_mixed: false`
- `manual_integrated_rule_mixed: false`
- `previous_run_output_mixed: false`


For Prompt 0.6 specifically, evidence QC is the last upstream evidence-safety checkpoint. It must prove that:
- every candidate has evidence_complete_and_source_claim_covered state
- publish_ready is still false
- format-risk / execution-anchor metadata was preserved or explicitly marked not_applicable
- no evidence hold, source gap, claim gap, duplicate hold, review pool, or rejected item was mixed in

If any required lineage field is missing, false, contradictory, stale, not from the same run, or inconsistent with the candidate payload, stop immediately and report:

- status: BLOCKED_UPSTREAM_LINEAGE_INVALID
- reason: [...]
- invalid_or_missing_lineage_fields: [...]
- no content enrichment or language polish work performed

Do not infer lineage validity from memory.
Do not continue just because candidate counts look correct.
Do not use this prompt to fix Stage A/B/C selection defects or post-QC evidence defects.

Candidate input rule:

Only evidence_complete_and_source_claim_covered[] may enter this step.

Do not include:

- addable_hold_source_gap
- addable_hold_claim_gap
- needs_source_augmentation
- evidence_qc_rejected
- review_pool_deferred
- duplicate_hold
- existing_reinforcement
- withheld_reinforcement
- baseline_conflict
- revise_required
- rejected
- support_source_only
- deferred_review_pool
- Stage B draft_blocked
- Stage A review_pool
- previous final files
- previous PR candidates
- previous publish-ready payloads

If any non-evidence_complete_and_source_claim_covered item is mixed into the candidate input, exclude it and report it as mixed_input_excluded.


Upstream lineage integrity rule — Stage A V2 selector safety:

This step must verify that every upstream workflow output belongs to the same current run lineage and that the Stage A V2 selector gates were valid.

Required lineage fields to confirm, directly or through carried-forward metadata:

- stage_a_validity_status: PASS
- artifact_consistency_gate.status: PASS
- Stage A selector marker is present and accepted. Accepted markers include `enhanced_selector_precision_version: 20260505_safe_execution_anchor` or later/equivalent, or legacy `selector_policy_version: stage_a_high_precision_execution_anchor_v2` or later.
- strict_pass_gate or strict_gate_check exists for every candidate that originated from strict_passed_spec[]
- execution_anchor_type / execution_anchor_strength is present for every format-risk candidate
- watchlist_audit, if a user watchlist was provided, accounts for every watchlist item without auto-promotion

If these fields are missing, inconsistent, stale, or indicate failure, do not silently continue. Stop this step and report:

- status: BLOCKED_INVALID_UPSTREAM_LINEAGE
- invalid_or_missing_lineage_fields: [...]
- no downstream state advancement performed

Do not repair Stage A/B/C selection defects in this step. Return the run to the earliest defective stage instead.


Content polish execution-anchor guard:

Content enrichment may improve reader-facing language only inside the existing source-locked claim coverage.

For format-risk cards, content polish must preserve the source-supported execution anchor and must not inflate it:

- demo / prototype / PoC must not become commercial deployment
- partnership / MOU must not become binding contract unless the evidence says so
- product launch must not become market adoption unless named customer adoption exists
- interview / commentary must not become fact unless the source includes a concrete fresh event

If a visible field requires a stronger execution claim than the evidence supports, narrow the language or move the card to content_hold_claim_narrowing_needed. Do not invent execution evidence.

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

Role of this step:

This step decides only:

- content_enriched
- language_terminology_polished
- content_hold_claim_narrowing_needed
- content_hold_language_issue
- content_hold_schema_issue
- needs_return_to_evidence_qc
- review_pool_deferred

This step must not decide:

- publish_ready
- PR readiness
- GitHub readiness

State ladder reminder:

accepted_fact_safe
→ addable_merge_safe
→ evidence_complete
→ source_claim_covered
→ content_enriched
→ language_terminology_polished
→ publish_ready

This step may move evidence_complete_and_source_claim_covered only to:

- content_enriched_and_language_polished
- content_hold_claim_narrowing_needed
- content_hold_language_issue
- content_hold_schema_issue
- needs_return_to_evidence_qc
- review_pool_deferred

It cannot move any card to publish_ready.

Hard rule:

content_enriched and language_terminology_polished are not publish_ready.

Every surviving card after this step must still have:

- publish_ready: false
- needs_publish_readiness_qc: true

Do not preserve publish_ready=true from any upstream file.

If any candidate enters this step with publish_ready=true, reset it to false and record:

- publish_ready_reset: true
- reset_reason: content_enrichment_does_not_decide_publish_ready

Web search / fetch boundary:

This step must not use web search as content enrichment.

Allowed source universe for rewriting:

- existing fact_sources
- existing source_quote
- existing claim coverage map
- existing evidence QC findings
- existing Stage C accepted card fields
- existing source fields already in the card

External web search is prohibited by default.

Limited web checking is allowed only if needed to verify a language/terminology ambiguity or source-claim conflict already identified in evidence QC.

Do not use web search to:

- add new facts
- add new numbers
- add new sources
- expand market claims
- strengthen weak claims
- discover new card candidates
- rescue held/rejected items
- create publish_ready output

If new evidence is needed, do not add it here.

Mark:

- needs_return_to_evidence_qc: true
- recommended_next_action: source_augmentation_or_evidence_qc_rerun

Source-lock rule:

Visible-field rewriting may use only claims already supported by fact_sources and source_claim_coverage_map.

Do not add a claim unless it is already covered.

Do not make a claim stronger than the source coverage permits.

Do not convert:

- MOU → contract
- pilot → commercial deployment
- plan → confirmed execution
- consideration → policy decision
- semi-solid → solid-state
- company statement → industry consensus
- source-supported possibility → certainty

Content handling:

This step may rewrite only reader-facing visible fields:

- title
- sub
- gate
- fact
- implication

Do not modify by default:

- fact_sources
- source_quote
- source_quote_status
- source_url
- source_name
- evidence_role
- supports
- fetched_at
- fetch_method
- URLs
- baseline metadata
- event_fingerprint

If a non-visible field has a schema issue, record it as:

- content_hold_schema_issue
- required_schema_fix

Do not silently integrated rule evidence fields.

Content enrichment objectives:

For every candidate, improve visible fields so that they read as SBTL_HUB strategic intelligence, not raw article summaries.

However, enrichment must remain source-locked.

Reader-facing writing persona:

Visible fields must read as if written by a top-tier investment-banking sector
veteran with 30 years of battery, ESS, EV, energy-infrastructure, and industrial
supply-chain deal experience. The tone is Korean executive briefing prose:
commercially literate, compressed, skeptical, and decision-useful.

The persona is for framing and information density only. It must not create
unsupported valuation, deal, financing, market-share, causal, or investment
claims. Evidence discipline remains controlled by `FACT_DISCIPLINE.md` and the
current fact_sources/source_claim_coverage_map.

Reader-facing cards should not sound like:

- a verification memo
- an LLM audit artifact
- a raw RSS/news summary
- a PR rewrite
- a generic newsletter digest
- promotional equity-research language

They should sound like:

- a concise Korean strategy card
- a sector banker explaining why the event matters
- a source-locked industrial intelligence note
- a red-team factchecker operating behind the prose

Improve:

- clarity
- specificity
- strategic usefulness
- Korean executive briefing tone with 30-year top-tier IB sector-veteran
  judgment
- industry lane relevance
- fact/interpretation separation
- next-checkpoint usefulness
- terminology consistency
- readability

Do not improve by adding unsupported facts.

Field rules:

title:

- Must include at least two of:
  - actor
  - action
  - number/scale
  - region/location
  - strategic meaning
- Must be source-supported.
- Must not copy article headline.
- Must not exaggerate source direction.
- Must not use raw foreign-language headline.
- Must not force a number if unsupported.
- Must not contain workflow/meta language.

sub:

- Exactly one sentence.
- Must include event + source-supported scale/number if available + strategic angle.
- Must not introduce claims absent from source coverage.
- Must not be a generic summary.
- Must not exceed reasonable newsletter-card length.

gate:

- 2–3 sentences.
- Must explain why the event matters for the relevant lane:
  - materials
  - ESS
  - grid
  - supply chain
  - policy
  - EV/battery demand
  - raw materials/pricing
  - safety/certification/regulation
  - manufacturing capacity
  - charging infrastructure
- Must distinguish verified fact from strategic interpretation.
- Must not force SBTL relevance if weak.
- Must not assert direct benefit unless source-supported.
- Must not use hype or investor-promo language.

fact:

- Minimum 2 sentences.
- Prefer 3 sentences when evidence supports enough detail.
- Must include actor, region, period/date, business/policy scope, and scale when available.
- Must target baseline-level information density: actor + asset/project/policy +
  geography + date/period + scale/value/capacity + status/stage + counterparty
  or authority, when source-supported.
- Must contain only source-backed information.
- Every number/date/entity/project/action must remain covered by fact_sources.
- Must not include interpretation that belongs in gate/implication.
- Must not include memory-based context.

implication:

- Minimum 2 items.
- Prefer 3 items with distinct roles:
  1. market / demand structure
  2. supply chain / materials / technology / grid / policy impact
  3. next checkpoint or risk
- Must be observational.
- Must not introduce unsupported facts.
- Must not make certain benefit claims.
- Must not use generic filler.
- Must surface a source-supported strategic read a senior sector banker would
  care about: market structure, supply-chain control, localization, financing,
  pricing, policy, execution risk, customer demand, grid constraint, technology
  adoption, or competitive positioning.
- Avoid generic "watch/monitor" wording when a sharper next checkpoint exists:
  FID, COD, procurement award, offtake, customer qualification, policy
  implementation, subsidy decision, plant ramp, capacity utilization, shipment,
  pricing formula, or counterparty confirmation.

Allowed implication style:

- 관찰된다
- 확인할 필요가 있다
- 변수가 될 수 있다
- 점검 대상이다
- 가능성이 열린다
- 리스크로 남는다
- 후속 확인이 필요하다
- 비교 기준이 될 수 있다
- 압력으로 작용할 수 있다
- 판단 근거가 된다

Banned implication style:

- 수혜가 확정된다
- 직접 수혜다
- 반드시 증가한다
- 구조적으로 전환된다
- 확실한 신호다
- 시장 확대 기대
- 수혜 예상
- 주목 필요
- 모니터링 필요
- 게임체인저다
- 판이 바뀐다
- 무조건 유리하다

Language and terminology polish rules:

No raw Chinese/Japanese article titles in visible fields.

Use standard Korean names for companies, institutions, and policies when available.

English names may be added once in parentheses only when necessary for identification.

Do not repeat bilingual names unnecessarily.

Normalize units:

- MW-hours → MWh
- megawatt-hours → MWh
- gigawatt-hours → GWh
- kilowatt-hours → kWh
- USD → 달러
- EUR → 유로
- CNY → 위안
- JPY → 엔

Normalize battery/materials terms:

- anode → 음극재
- cathode → 양극재
- separator → 분리막
- electrolyte → 전해질
- lithium hydroxide → 수산화리튬
- lithium carbonate → 탄산리튬
- rare earth → 희토류
- critical minerals → 핵심광물
- recycling → 재활용
- black mass / black powder → 블랙매스 / 블랙파우더, source context에 맞게 사용
- solid-state battery → 전고체 배터리
- semi-solid-state battery → 반고체 배터리 또는 준고체 배터리, source wording에 맞게 사용
- ESS / BESS → ESS / BESS, 첫 등장 시 필요하면 에너지저장장치 병기

Avoid raw machine-translated terms.

Use polished Korean executive briefing tone.

Use the 30-year top-tier IB sector-veteran persona for visible-field compression
and strategic framing.

Avoid overly casual expressions.

Avoid promotional language.

Banned visible-field workflow/meta phrases:

Do not include any of the following or close variants in title/sub/gate/fact/implication:

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
- market expansion expected
- direct beneficiary
- likely winner

SBTL framing rule:

Do not force SBTL into a card.

Mention SBTL only when:
- the source-supported event directly relates to pouch film, battery materials, ESS safety, cell packaging, supply chain localization, customer procurement, or policy lanes relevant to SBTL’s business context; and
- the connection can be stated as an observation, not a direct benefit claim.

Prefer broad industry framing unless SBTL connection is concrete.

Unsupported direct-benefit claims are prohibited.

Claim preservation rule:

When rewriting, preserve the underlying source-supported meaning.

Do not:
- widen the claim
- add causality
- add certainty
- add unsupported comparison
- add unsupported forecast
- add unsupported company intention
- add unsupported market size
- add unsupported production timeline
- add unsupported customer linkage

If a current visible-field claim is too broad but can be safely narrowed using existing evidence, narrow it.

If narrowing is necessary but would materially change the card’s core event, mark:

- content_hold_claim_narrowing_needed

If unsupported visible claims remain and cannot be fixed without new evidence, mark:

- needs_return_to_evidence_qc

Output state definitions:

1. content_enriched_and_language_polished

Use only when:

- card entered as evidence_complete_and_source_claim_covered
- visible fields were enriched or confirmed as already strong
- title/sub/gate/fact/implication remain source-locked
- language/terminology polish passes
- no banned visible-field phrase remains
- no foreign-language headline residue remains
- no unsupported claim is introduced
- evidence fields are preserved
- publish_ready remains false

Every item in this state must include:

- state: content_enriched_and_language_polished
- previous_state: evidence_complete_and_source_claim_covered
- evidence_complete: true
- source_claim_covered: true
- content_enriched: true
- language_terminology_polished: true
- publish_ready: false
- needs_publish_readiness_qc: true

2. content_hold_claim_narrowing_needed

Use when:

- visible fields contain overbroad claims
- claims can likely be narrowed using existing evidence
- but the required narrowing is material enough to require separate review
- card should not proceed until revised and rechecked

3. content_hold_language_issue

Use when:

- raw foreign-language text remains
- terminology normalization is unresolved
- tone is too promotional or too casual
- banned workflow/meta phrase remains
- company/institution naming is ambiguous
- translation quality is insufficient

4. content_hold_schema_issue

Use when:

- non-visible schema issue blocks safe forward movement
- fact_sources schema issue remains
- source field preservation is uncertain
- required state flags are missing
- malformed arrays/types exist

5. needs_return_to_evidence_qc

Use when:

- enrichment reveals a claim coverage problem
- visible fields cannot be fixed without new source support
- evidence completeness appears invalid
- source_quote/fact_sources conflict with visible fields
- new source augmentation is needed

6. review_pool_deferred

Use when:

- content issue cannot be resolved in current step
- manual editorial decision is needed
- terminology or source interpretation is uncertain
- user review is required

Accounting rule:

Every evidence_complete_and_source_claim_covered item must appear exactly once in one of:

- content_enriched_and_language_polished
- content_hold_claim_narrowing_needed
- content_hold_language_issue
- content_hold_schema_issue
- needs_return_to_evidence_qc
- review_pool_deferred

No silent skip is allowed.

Report:

- evidence_complete_and_source_claim_covered_input_count
- content_enriched_and_language_polished_count
- content_hold_claim_narrowing_needed_count
- content_hold_language_issue_count
- content_hold_schema_issue_count
- needs_return_to_evidence_qc_count
- review_pool_deferred_count
- outcome_total_count
- content_polish_accounting_matches_input_count

If accounting does not match, mark output invalid and report:

- status: BLOCKED_CONTENT_POLISH_ACCOUNTING_MISMATCH

Output files:

1. content_polish_results_{{RUN_TAG}}.json
2. content_polish_report_{{RUN_TAG}}.md
3. content_polish_decisions_{{RUN_TAG}}.csv
4. content_enriched_language_polished_PENDING_FINAL_QC_{{RUN_TAG}}.json
5. content_polish_hold_manifest_{{RUN_TAG}}.json
6. visible_field_change_log_{{RUN_TAG}}.json

Do not use FINAL, PR_CANDIDATE, GitHub-ready, merge-ready, or publish-ready in filenames.

The phrase content_enriched or language_polished may be used only for cards that also clearly include publish_ready=false and pending final QC flags.

JSON output requirements:

The main JSON must include:

- stage
- run_tag
- run_label
- input_evidence_qc_file
- input_source_claim_coverage_map_file
- baseline_file
- baseline_source_declaration
- baseline_count
- required_docs_check
  - docs_expected
  - docs_read_from_github_main
  - docs_missing_or_unreadable
  - status
- evidence_complete_and_source_claim_covered_input_count
- mixed_input_excluded_count
- content_enriched_and_language_polished_count
- content_hold_claim_narrowing_needed_count
- content_hold_language_issue_count
- content_hold_schema_issue_count
- needs_return_to_evidence_qc_count
- review_pool_deferred_count
- outcome_total_count
- content_polish_accounting_matches_input_count
- language_terminology_summary
- banned_phrase_summary
- foreign_language_residue_summary
- visible_field_change_summary
- content_enriched_and_language_polished[]
- content_hold_claim_narrowing_needed[]
- content_hold_language_issue[]
- content_hold_schema_issue[]
- needs_return_to_evidence_qc[]
- review_pool_deferred[]
- mixed_input_excluded[]
- visible_field_change_log[]
- decision_ledger[]

Each content_enriched_and_language_polished item must include:

- state: content_enriched_and_language_polished
- previous_state: evidence_complete_and_source_claim_covered
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
- evidence_complete: true
- source_claim_covered: true
- content_enriched: true
- language_terminology_polished: true
- publish_ready: false
- needs_publish_readiness_qc: true
- content_polish_findings
  - title_quality
  - sub_quality
  - gate_depth
  - fact_source_lock
  - implication_quality
  - terminology_consistency
  - foreign_language_residue
  - banned_phrase_check
  - tone_check
  - sbtl_forcing_check
- visible_field_change_summary
- publish_ready_reset
- reset_reason
- notes

Each content_hold_claim_narrowing_needed item must include:

- state: content_hold_claim_narrowing_needed
- previous_state: evidence_complete_and_source_claim_covered
- draft_id
- source_spec_id
- hold_reason
- overbroad_claims
- affected_visible_fields
- suggested_narrowing
- source_coverage_reference
- recommended_next_action

Each content_hold_language_issue item must include:

- state: content_hold_language_issue
- previous_state: evidence_complete_and_source_claim_covered
- draft_id
- source_spec_id
- hold_reason
- affected_visible_fields
- language_or_terminology_issue
- required_fix
- recommended_next_action

Each content_hold_schema_issue item must include:

- state: content_hold_schema_issue
- previous_state: evidence_complete_and_source_claim_covered
- draft_id
- source_spec_id
- schema_issue
- affected_fields
- required_fix
- recommended_next_action

Each needs_return_to_evidence_qc item must include:

- state: needs_return_to_evidence_qc
- previous_state: evidence_complete_and_source_claim_covered
- draft_id
- source_spec_id
- reason
- evidence_or_claim_gap_discovered
- affected_visible_fields
- recommended_next_action

Each review_pool_deferred item must include:

- state: review_pool_deferred
- previous_state: evidence_complete_and_source_claim_covered
- draft_id
- source_spec_id
- defer_reason
- unresolved_editorial_questions
- required_manual_checks
- recommended_next_action
- not_publish_ready: true

Each visible_field_change_log item must include:

- draft_id
- field
- before
- after
- change_type
- reason
- source_lock_check
- introduced_new_claim: true/false
- introduced_new_claim_explanation

Allowed change_type values:

- clarity
- compression
- source_lock_narrowing
- strategic_depth
- terminology_normalization
- tone_polish
- banned_phrase_removal
- foreign_language_cleanup
- implication_role_split
- fact_interpretation_separation
- no_change_needed

Each decision_ledger row must include:

- draft_id
- source_spec_id
- prior_state
- content_polish_outcome
- content_enriched
- language_terminology_polished
- publish_ready
- banned_phrase_status
- foreign_language_residue_status
- terminology_status
- source_lock_status
- reason
- notes

Language/terminology summary must count:

- raw_chinese_visible_count
- raw_japanese_visible_count
- raw_foreign_headline_count
- unit_normalization_count
- company_name_normalization_count
- terminology_normalization_count
- banned_phrase_removed_count
- banned_phrase_remaining_count
- forced_sbtl_claim_count
- unsupported_new_claim_introduced_count

Report requirements:

The Markdown report must include:

1. Run metadata

   - evidence QC input file
   - evidence-complete payload file
   - baseline file/source
   - baseline source declaration
   - baseline count
   - run tag
   - run label
   - evidence_complete_and_source_claim_covered input count

2. Required docs check

   - list all 8 required docs
   - confirm each was read from GitHub main
   - if any doc was not read, this step must not proceed

3. Method

   - evidence_complete_and_source_claim_covered-only confirmation
   - mixed input exclusion confirmation
   - source-lock rewriting method
   - visible-fields-only edit confirmation
   - no fact_sources/source_quote modification confirmation
   - no web-search content enrichment confirmation
   - no publish_ready confirmation

4. Summary table

   - input count
   - content_enriched_and_language_polished count
   - content_hold_claim_narrowing_needed count
   - content_hold_language_issue count
   - content_hold_schema_issue count
   - needs_return_to_evidence_qc count
   - review_pool_deferred count
   - mixed_input_excluded count
   - outcome total count
   - accounting match: yes/no

5. content_enriched_and_language_polished manifest

   For each passed item:
   - draft_id
   - source_spec_id
   - short event anchor
   - title/sub/gate/fact/implication quality result
   - terminology result
   - banned phrase result
   - foreign-language residue result
   - next required gate: final publish-readiness QC

6. Hold manifest

   Include:
   - content_hold_claim_narrowing_needed
   - content_hold_language_issue
   - content_hold_schema_issue
   - needs_return_to_evidence_qc
   - review_pool_deferred

   For each item:
   - draft_id
   - hold/defer reason
   - affected fields
   - required fix
   - recommended next action

7. Visible field change summary

   Include:
   - number of changed titles
   - number of changed subs
   - number of changed gates
   - number of changed facts
   - number of changed implications
   - source-lock narrowing count
   - strategic-depth improvement count
   - terminology normalization count
   - banned phrase removal count

8. Language/terminology summary

   Include:
   - raw Chinese/Japanese residue count
   - unit normalization count
   - company/institution name normalization count
   - banned phrase remaining count
   - forced SBTL claim count
   - unsupported new claim introduced count

9. Source-lock summary

   Include:
   - cards with no new claims introduced
   - cards with narrowed claims
   - cards requiring return to evidence QC
   - cards with source-lock concerns

10. Explicit boundary statement

   Include this exact statement:

   “Content enrichment and language/terminology polish edited only reader-facing visible fields within the existing source-locked evidence universe. It did not decide publish_ready, PR readiness, or GitHub readiness.”

11. Next-step statement

   Include this exact statement:

   “The next step is final publish-readiness QC. Only content_enriched_and_language_polished cards may enter that step. content_enriched and language_terminology_polished are not publish_ready.”

## Operational integrated rule — source-locked content polish lineage guard

Content enrichment and language polish must not repair Stage A selection defects or evidence-lineage gaps.

Before editing any visible field, verify that the Evidence QC output includes:

- `upstream_lineage_guard_status = PASS`, or equivalent;
- `evidence_qc_accounting_matches_input_count = true`;
- `evidence_complete_and_source_claim_covered[]` contains only candidates that passed upstream Stage A/B/C/0.4 lineage guards;
- `evidence_complete_with_selection_lineage_gap_count = 0`;
- `evidence_complete_with_execution_anchor_gap_count = 0`;
- `evidence_complete_with_missing_strict_gate_count = 0`.

For each candidate with `format_risk_tags`, content polish may improve wording only within the verified source-locked scope. It must not convert a demo, PoC, component launch, interview, commentary, speech, or partnership into a stronger commercial deployment claim unless the already-accepted evidence universe contains a concrete execution anchor.

If the Evidence QC output is missing lineage fields or contains unresolved selector/execution-anchor gaps, stop and report:

```json
{
  "status": "BLOCKED_EVIDENCE_QC_LINEAGE_INVALID",
  "no_content_polish_performed": true,
  "reason": "Content polish cannot repair or hide upstream selection/evidence-lineage defects.",
  "recommended_next_call": "return to Evidence QC or rerun Stage A lineage"
}
```

If an individual candidate shows an unresolved execution-anchor gap during polish, move it to `content_hold_selection_or_execution_anchor_gap` and do not include it in `content_enriched_and_language_polished[]`.

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

## Operational integrated rule — content polish next-call recommendation

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

1. If content_enriched_and_language_polished_count > 0:
   - recommended_next_call = "final publish-readiness QC"
   - recommended_prompt_id = "Prompt 0.7"
   - recommended_input_universe = "content_enriched_and_language_polished[] only"

2. If holds exist:
   - recommend return to evidence QC, content polish, manual review, or retrospective based on hold state

Do not proceed automatically to final QC.
Stop after content enrichment and language/terminology polish.

Do not proceed to final publish-readiness QC until I explicitly say “final QC” or “publish-readiness QC”.

---

## Execution-anchor and selector-lineage safety overlay — 2026-05-05

This overlay is downstream of the Stage A safe-selector integrated rule. It prevents post-acceptance steps from laundering a weak or superseded Stage A/B/C lineage into publish-ready or production status.

Terminology lock:

- Do not use or enforce a format-based hard-exclude rule.
- Product, demo, PoC, component, interview, commentary, roundup, speech, or personnel formats are not automatically rejected by format alone.
- They are subject to a strict-pass presumption block: without a concrete fresh execution anchor, they must not have entered `strict_passed_spec[]`; if they did, the downstream step must hold, reject, or return the item to the appropriate prior stage rather than polishing it forward.
- Concrete execution anchors include signed contract, binding customer order, offtake, commercial deployment, field installation, commissioning, production start, facility opening, certification, regulatory decision, public funding approval, binding procurement, measurable capacity addition, safety recall/regulatory action, or named customer adoption.

### Required upstream lineage gate for Content Polish

Before content enrichment begins, verify that `EVIDENCE_QC_RESULTS_JSON` includes:

- `upstream_lineage_validation.decision: pass`
- `execution_anchor_qc_summary`
- `evidence_qc_accounting_matches_input_count: true`

If these are missing or failed, stop and report:

```text
status: BLOCKED_EVIDENCE_QC_LINEAGE_OR_ANCHOR_INVALID
reason: [...]
no content enrichment or language polish work performed
```

### Content polish boundary for format-risk cards

Content polish must not use language to upgrade an unsupported format-risk item. In particular, do not turn:

- demo into commercial deployment
- PoC into rollout
- partnership/MOU into signed contract or implementation
- interview/commentary into fresh event
- component/product launch into market adoption
- regulatory discussion/speech into enacted measure

unless the existing `fact_sources`, `source_claim_coverage_map`, and Evidence QC output already support that execution anchor.

If an execution-anchor gap is found during content polish, do not polish the card forward. Route it to:

- `needs_return_to_evidence_qc`, or
- `content_hold_claim_narrowing_needed` if a safe narrower version can be produced without changing the event status.

### Output requirement

Add to the Content Polish JSON:

```json
"lineage_and_anchor_guard": {
  "evidence_qc_lineage_passed": true,
  "execution_anchor_qc_passed": true,
  "format_risk_claims_narrowed_count": 0,
  "returned_to_evidence_qc_count": 0
}
```

Final override: if lineage or execution-anchor guard fails, the next recommended call must not be Prompt 0.7.

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

## Operational integrated rule — REPAIR_BEFORE_DELETION_FOR_NUMERIC_AND_NAMED_CLAIMS_20260507_V2

When Stage B revise, Stage C, Evidence QC, Content polish, or Final QC finds a numeric, named-entity, date, capacity, price, market-share, contract-duration, or project-scope claim that is weak or unmapped, it must first decide whether the claim can be repaired by:

1. remapping the claim to an already-cited source quote,
2. narrowing the visible-field wording to match the source,
3. using an already-fetched official/body-level source from the same evidence package,
4. performing explicitly authorized source augmentation when the current prompt/stage allows it.

Deletion or over-narrowing is allowed only when:

- source repair is impossible,
- source augmentation is not authorized,
- same-event/source-direction checks fail,
- or the claim remains unsupported after rescue.

Outputs must record `claim_repair_before_deletion_check` for every deleted or narrowed core claim, and if deletion/narrowing results in hold/reject/block, the item must also include `final_hold_or_reject_reason`.

## Operational integrated rule — SUPPLEMENTAL_PASS_ACCOUNTING_20260507

If a supplemental pass is authorized after a hold-rescue or schema repair step, the supplemental output must not silently mix with already-passed items.

Required fields:

- `supplemental_pass: true`
- `supplemental_pass_reason`
- `supplemental_input_universe`
- `supplemental_input_ids[]`
- `previous_pass_reference_file`
- `excluded_previous_pass_ids[]`
- `combined_reference_payload_created: true|false`
- `combined_reference_payload_status: reference_only|pending_next_gate|invalid`

A combined payload may be produced only as a clearly named reference or pending-next-gate payload. It must preserve lineage and must not assign a later state by combining files.

## Operational integrated rule — EXECUTION_TRANSPARENCY_AND_FILE_VERIFICATION_20260507

For local validation runs, every stage report must identify:

- input files actually opened,
- input counts read from those files,
- output files written,
- post-write verification result,
- count reconciliation after reopening outputs,
- any step not performed.

If a file was not opened or a count was not verified, the assistant must not claim completion for that artifact.

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


## Downstream boundary — v4 rescue/review rules do not authorize state laundering

This downstream stage must preserve and validate prior rescue/review metadata. It must not use merge safety, content polish, final QC, GitHub merge prep, production verification, or remediation to launder unresolved evidence defects, unvalidated later-discovered evidence, unreviewed caveats, or unreviewed review_pool/treasure items.

If this stage encounters material unvalidated evidence, unresolved source-strength caveat, missing rescue metadata, or an unreviewed review_pool/treasure promotion attempt, it must stop or route back to the appropriate earlier stage and report one of:

- BLOCKED_RESCUE_METADATA_MISSING
- BLOCKED_SILENT_DOWNSTREAM_ENRICHMENT_ATTEMPT
- BLOCKED_SOURCE_STRENGTH_CAVEAT_REVIEW_REQUIRED
- BLOCKED_REVIEW_POOL_OR_TREASURE_PROMOTION_UNAUTHORIZED

No next-stage recommendation may be made for the affected item until the required validation path is completed.


## Operational integrated rule — PROMPT_0_6_EXACT_LINEAGE_AND_ANCHOR_GUARD_20260508_V6

This v6 integrated rule closes the metadata contract defect found in the clean-v5 local validation run: Prompt 0.6 produced semantically valid content polish output, but Prompt 0.7 could not machine-verify the exact nested `lineage_and_anchor_guard` contract.

Prompt 0.6 must now emit an exact machine-readable guard at both root level and payload-item level.

Required root-level fields in the 0.6 JSON output:

```json
"lineage_and_anchor_guard": {
  "status": "PASS",
  "evidence_qc_lineage_passed": true,
  "execution_anchor_qc_passed": true,
  "source_strength_caveat_preserved": true,
  "publish_ready_remains_false": true,
  "content_polish_modified_visible_fields_only": true,
  "fact_sources_unchanged_unless_authorized_supplemental": true,
  "source_quote_unchanged_unless_authorized_supplemental": true,
  "no_silent_downstream_enrichment": true,
  "supplemental_pass_accounting_preserved": true
}
```

Required payload-item fields for every `content_enriched_and_language_polished[]` item:

```json
"lineage_and_anchor_guard": {
  "status": "PASS",
  "source_spec_id": "...",
  "evidence_qc_lineage_passed": true,
  "execution_anchor_qc_passed": true,
  "source_strength_caveat_preserved": true,
  "publish_ready_remains_false": true,
  "visible_field_change_log_ref": "...",
  "fact_sources_change_status": "unchanged|authorized_supplemental_metadata_only|authorized_supplemental_source_added",
  "source_quote_change_status": "unchanged|authorized_supplemental_quote_added",
  "reason_if_any_source_field_changed": "...|not_applicable"
}
```

If any required root or payload guard field is missing, false, contradictory, stale, or not from the same run, Prompt 0.6 must stop and report:

```text
status = BLOCKED_CONTENT_POLISH_LINEAGE_AND_ANCHOR_GUARD_MISSING
no Final QC recommendation
```

Prompt 0.6 must not rely on prose statements like “lineage preserved” as a substitute for the exact guard object.
Prompt 0.7 must treat absence of this exact guard as a hard preflight block.

## CARD_CLAIM_DIVERSITY_AUDIT_RULE_20260507_V7

This rule adds an editorial-quality gate after evidence safety has already been established. It must never override `FACT_DISCIPLINE.md`.

The workflow must audit not only whether each card is fact-safe, but also whether each publish-ready card answers a distinct, source-supported strategic question.

The goal is not artificial variety. The goal is to prevent a batch from collapsing into repetitive surface claims such as “Company A announced/supplied/launched/expanded Project B” when the underlying sources support a more useful, still source-locked strategic angle.

### Required fields for Prompt 0.6 and Prompt 0.7

For every card entering Prompt 0.6 Content Polish and Prompt 0.7 Final QC, produce `card_claim_diversity_audit[]` with one row per card. Each row must include:

- `card_id` or provisional draft/addable ID
- `source_spec_id`
- `primary_claim_type`
- `secondary_claim_type`
- `event_anchor_type`
- `strategic_question`
- `why_this_card_is_not_redundant`
- `similar_claim_cards_in_current_batch[]`
- `claim_overlap_risk`: `low | medium | high`
- `required_claim_repositioning`: `true | false`
- `claim_repositioning_applied`: `true | false`
- `claim_repositioning_source_safe`: `true | false | not_applicable`
- `claim_overlap_accepted_reason`, required when overlap remains medium/high
- `source_safe_repositioning_not_possible`: `true | false`

Allowed `primary_claim_type` / `secondary_claim_type` values:

- `capacity_execution`
- `policy_shift`
- `market_structure`
- `pricing_or_cost_signal`
- `demand_adoption`
- `supply_chain_security`
- `technology_validation`
- `financing_or_capital_market`
- `safety_or_reliability`
- `company_strategy`
- `trade_or_tariff`
- `grid_integration`
- `customer_qualification_or_reference`
- `production_or_factory_execution`
- `litigation_or_ip_risk`
- `regulatory_compliance_or_certification`
- `infrastructure_bottleneck`
- `earnings_or_margin_signal`
- `recycling_or_circularity`
- `source_strength_or_data_release`
- `other_source_locked_claim`

### Hard warning rule

If 3 or more cards in the same candidate batch share the same `primary_claim_type` and the same `event_anchor_type`, do not automatically reject them. Instead:

1. Check whether each card can answer a distinct `strategic_question` using only already validated source evidence.
2. If source evidence permits safe repositioning, Prompt 0.6 must reposition visible fields to clarify the distinct role of each card.
3. If source evidence does not permit safe repositioning, preserve the narrower source-locked claim and record:
   - `claim_overlap_accepted_reason`
   - `source_safe_repositioning_not_possible: true`

### Guardrail — no invented variety

This audit must not override `FACT_DISCIPLINE.md`.

Do not invent strategic variety. Do not add unsupported market-structure, causal, competitive, pricing, supply-chain, or SBTL-benefit claims. Do not use memory or outside context to diversify a card.

If the source evidence only supports a narrow surface claim, keep the narrow claim and mark the overlap risk honestly. A boring but true card is better than a distinctive but unsupported card.

### Output and blocker

Prompt 0.6 must include `card_claim_diversity_audit[]` and `claim_diversity_summary` in its JSON output. Prompt 0.7 must validate them before assigning `publish_ready`.

If `card_claim_diversity_audit[]` is missing, incomplete, or contradicts visible fields, report:

- `status: BLOCKED_CARD_CLAIM_DIVERSITY_AUDIT_MISSING`
- `no publish_ready assignment`
- `recommended_return_stage: Prompt 0.6 Content Polish`

If overlap risk is high and source-safe repositioning was possible but not applied, report:

- `status: BLOCKED_CLAIM_OVERLAP_REQUIRES_REPOSITIONING`
- `recommended_return_stage: Prompt 0.6 Content Polish`

Prompt 1.1 retrospective must report claim-type distribution, over-clustered claim types, and any accepted overlap reasons.

## Prompt 0.6 required output contract — claim diversity

Prompt 0.6 must treat `card_claim_diversity_audit[]` as part of the content-polish output, not as optional commentary.

JSON output must include:

- `card_claim_diversity_audit[]`
- `claim_diversity_summary`
- `claim_type_distribution`
- `over_clustered_claim_groups[]`
- `claim_repositioning_change_log[]`
- `claim_repositioning_source_safety_status`

Each `visible_field_change_log[]` entry that changes title/sub/gate/fact/implication for claim repositioning must link to the relevant `card_claim_diversity_audit[]` row.

Allowed action in 0.6:
- Reposition visible fields using only already validated source evidence.
- Narrow or clarify a strategic question.
- Explain why overlap remains acceptable when source-safe repositioning is not possible.

Not allowed in 0.6:
- Add new source evidence.
- Add unsupported strategic claims.
- Modify `fact_sources` or `source_quote` silently.
- Change evidence state to publish_ready.

If claim repositioning requires new evidence, return the item to evidence QC / 0.5R rather than inventing the angle.



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

## Source-URL resolution integrity — canonical completeness, article resolution, and 0.6 restore propagation (P06)

This integrated rule adds a THIRD source_url verification axis on top of the two that already exist in the workflow:
1. quote-presence at the URL is checked upstream (Prompt 0.5 Test 9), and
2. source_url membership in `urls[]` is checked by the v8/v9 "Visible-source URL sync is a hard gate" rules above.

Neither axis verifies that `source_url` is the FULL canonical article permalink that resolves to the exact article the quote was extracted from. That missing axis is the root cause of EFP-01 (truncated source_urls that still pass the membership gate) and EFP-02 (a wrong-article URL attached by post-0.7 augmentation). This file is the EFP-01 non-propagation site: 0.6 restored/normalized `urls[]` entries but left the matching `fact_sources[].source_url` as a truncated prefix.

This rule does NOT add new fact_sources and does NOT perform source augmentation. It only (a) blocks advancement when a source_url is not canonical/resolvable, and (b) — when an upstream restore/normalize already changed `urls[]` — overwrites the matching existing `source_url` with the full canonical URL already present in that same `urls[]` entry. Overwriting an existing field to match its own `urls[]` entry is an edit, not a new source.

### CHECK 1 — Canonical completeness
Every `fact_sources[].source_url` that supports a visible field (title/sub/gate/fact/implication) must be the full article permalink, byte-identical to the `urls[]` entry the quote was extracted from. HARD-FAIL the card if any supporting source_url is:
- (a) a truncated prefix of a longer `urls[]` entry (the longer entry being the real article permalink), or
- (b) a generic endpoint carrying no article identifier (no numeric id and no slug of 8+ chars): e.g. `read.do`, `article.html`, `view.php`, `list`, `index`, `board`, or a bare domain root.

### CHECK 2 — Article resolution
The resolved article behind `source_url` must be the SAME article that contains `source_quote` (same headline / actor / event) — not a section index, a listing page, a syndication hub, or a different article. Record per supporting source:
- `resolved_article_matches_quote: true|false`

0.6 must not perform new web search to satisfy this axis. Resolution may be confirmed only from the already-fetched evidence package (fetched body, source_quote, source_claim_coverage_map). If resolution cannot be confirmed from existing evidence, route the card to `needs_return_to_evidence_qc` / `needs_source_augmentation` rather than fetching new content.

### CHECK 3 — Prefix-laundering block + mandatory 0.6 restore propagation (EFP-01 fix)
If `urls[]` contains a longer URL that has the current `source_url` as a prefix, the longer URL is the canonical article URL: overwrite `source_url` with it and re-run CHECK 1 and CHECK 2.

Restore-propagation hard rule — this is the specific EFP-01 fix for this stage:
- Whenever this stage (0.6 content polish, including any 0.6 supplemental pass after 0.5R rescue) RESTORES or NORMALIZES a `urls[]` entry — i.e. any time `urls`, `fact_sources`, or `source_url` change under the supplemental paths defined above ("0.5R re-QC → 0.6 supplemental if … urls … fields change → 0.7 Final QC") — the corresponding `fact_sources[].source_url` MUST be overwritten with the full canonical URL in the SAME pass.
- Never leave `source_url` as a truncated prefix after a `urls[]` restore/normalize. The v8/v9 membership gate ("must appear in `urls[]`") is NOT sufficient: a truncated prefix can satisfy membership while failing canonical completeness.
- Every such overwrite is an existing-field edit, not a new source. Log it in `visible_field_change_log[]`-style accounting via a dedicated `source_url_propagation_log[]` entry: `{ source_spec_id, fact_source_index, before_source_url, after_source_url, urls_entry_used, trigger: "0.6_urls_restore" | "0.6_urls_normalize" | "prefix_laundering_block", resolved_article_matches_quote }`.

Background-only sources that genuinely do not support visible text are exempt from CHECK 1–3 only when already marked `supporting_context_only_not_visible_claim_support` with a reason (same carve-out as the v8/v9 sync gate).

### HARD-FAIL routing (use this file's existing 0.6 output states)
If a supporting source_url fails CHECK 1, 2, or 3 and cannot be fixed by in-card prefix propagation from an existing `urls[]` entry, do NOT mark the card `content_enriched_and_language_polished`. Route it, using this file's existing output states, with a `hold_reason_code`:
- truncated prefix with no longer `urls[]` entry to restore from → `needs_source_augmentation`, `hold_reason_code: source_url_truncated`
- generic endpoint with no article identifier → `needs_source_augmentation`, `hold_reason_code: source_url_generic_endpoint`
- resolves to a different article → `needs_return_to_evidence_qc`, `hold_reason_code: source_url_resolves_to_wrong_article`
- resolves to a section index / listing / hub → `needs_return_to_evidence_qc`, `hold_reason_code: source_url_resolves_to_listing`

These routes reuse the states already defined in this prompt (`needs_return_to_evidence_qc`, `needs_source_augmentation`). They do not create a new hold state and do not relax `FACT_DISCIPLINE.md`.

### AUGMENTATION rule — including any post-0.7 augmentation (EFP-02 fix)
Any source attached by augmentation — including a later post-0.7 augmentation pass that re-enters 0.6 supplemental — must pass CHECK 1, 2, and 3 before it may support visible text. Specifically:
- A `web_search_snippet` URL must never be attached as `source_url` without a body fetch confirming `source_quote` appears in the resolved article (CHECK 2).
- Any pass that attaches or changes a `source_url` without re-running this resolution axis AND Evidence QC is prohibited: set `publish_ready=false` (it is already false at 0.6) and route the item to `needs_return_to_evidence_qc` / `needs_source_augmentation`. This is consistent with the existing NO_SILENT_DOWNSTREAM_ENRICHMENT rule and FIND_AND_INTEGRATE rule above (`BLOCKED_SILENT_DOWNSTREAM_ENRICHMENT_ATTEMPT`).

### Required output object
Emit `source_url_resolution_summary` at root level of the 0.6 JSON (use this EXACT field name so Prompt 0.7 can gate on it):

```json
"source_url_resolution_summary": {
  "checked": 0,
  "canonical_complete": 0,
  "truncated_prefix_fixed": 0,
  "generic_endpoint_failed": 0,
  "wrong_article_failed": 0,
  "resolves_to_listing_failed": 0
}
```

Also extend the per-item `source_diversity_carry_forward` object with:

```json
"source_url_resolution_status": "PASS | PREFIX_FIXED | FAIL_TRUNCATED | FAIL_GENERIC_ENDPOINT | FAIL_WRONG_ARTICLE | FAIL_LISTING"
```

`source_url_urls_sync_status` (membership) and `source_url_resolution_status` (canonical resolution) are two distinct gates; a `PASS` on sync does not imply a `PASS` on resolution.

If `source_url_resolution_summary` is missing, or any supporting source_url remains `FAIL_*` in a card placed in `content_enriched_and_language_polished[]`, this step's output is invalid:

```text
status: BLOCKED_SOURCE_URL_RESOLUTION_INTEGRITY_FAILED
no Final QC recommendation
```


## Prompt 0.6 source diversity carry-forward boundary

Prompt 0.6 performs content polish and claim diversity audit. It must not perform source diversity repair or silently add source evidence.

Every content-polished item must carry forward:

```json
"source_diversity_carry_forward": {
  "source_diversity_status": "...",
  "do_not_expand_claims": true,
  "source_augmentation_required": false,
  "source_diversity_caveat_preserved": true,
  "source_url_urls_sync_status": "PASS",
  "claim_strength_matches_source_diversity": true
}
```

If a 0.6 rewrite would require stronger source diversity than 0.5 established, do not rewrite silently. Route to `needs_return_to_evidence_qc[]` with reason `source_diversity_insufficient_for_repositioned_claim`.

0.6 may reposition visible fields for claim diversity only if `claim_repositioning_source_safe=true` and source diversity status still supports the repositioned claim.

## R3C_P06 — Content audit gate (0.6)

> run 20260516_012728 retrospective integrated rule. P1.

0.6 Content Polish 는 다음 두 audit 산출물을 **반드시 생성**한다:

1. `card_claim_diversity_audit[]` — CARD_CLAIM_DIVERSITY_AUDIT_RULE v7 schema 그대로.
2. `related_coverage_audit[]` — 각 카드에 대해, batch 내부 + 최근 baseline 과
   대조해 동일 이벤트/동일 클러스터 링크가 **검토되었는지** 기록 (카드별 1 entry).

- 동반 스크립트: `validation_scripts/content_audit_check.py`
- 실행: `python3 validation_scripts/content_audit_check.py <content_output.json>`
- audit 는 링크를 **강제로 만들라는 것이 아니다.** related[] 는 진짜 링크만 담는다.
  audit 는 "링크가 검토되었는가" 를 확인하는 것이다.

근거: 1차 시도는 card_claim_diversity_audit 미생성, related[] 30/32 공란인데
링크 존재 여부 audit 자체가 없었음 (PV_007).

# 08_PROMPT_0_6_Content_Polish.md — Source Diversity source-diversity integrated rule

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

## Content Polish — synthesis, not URL accumulation

This stage must produce `source_synthesis_audit[]` for every card.

For each independent source owner, identify:

- source role;
- unique fact, condition or context;
- which visible field uses that contribution;
- whether the contribution changes interpretation or merely repeats the event.

A card fails content enrichment when:

- all visible copy can be traced to only one source despite multiple URLs;
- `gate` omits a limitation or condition uniquely identified by an independent source;
- `implication` ignores material policy, market or operational context already in the evidence
  package;
- extra sources are decorative rather than integrated;
- content was thinned to pass quote checks instead of being safely supported and retained.

Required output:

```json
{
  "source_synthesis_audit": [],
  "source_synthesis_applied": true,
  "source_synthesis_fields": [],
  "unused_material_source_contributions": [],
  "density_preservation_check": "PASS|FAIL"
}
```

If a useful contribution cannot be safely integrated, preserve it in
`unused_material_source_contributions[]` and route to an authorized supplemental pass. Do not
delete it silently.

    Stop after Content Polish. Do not assign publish_ready.

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


## Content Polish extra

Content polish may improve IB-grade framing but must not add unsupported factual weight.
