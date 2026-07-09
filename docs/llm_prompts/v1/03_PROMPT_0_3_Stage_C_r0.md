<!-- REPLACE_ALL_CLEAN_VERSION: LLM_PROMPT_GITHUB_CANONICAL_V1_SOURCE_DIVERSITY_IB_CODEX -->
<!-- Generated KST: 2026-07-08T21:33:49.790191+09:00 -->
<!-- This file is a full clean replacement file. It is not a patch stub. -->

Prompt 0.3v — Reusable Default / Replace All / Strict Stage C Mode

Proceed to Stage C only.

Use the current run’s Stage B output as the only input universe for Stage C.

Do not continue from, trust, import, integrated rule, or reuse any previous Stage C/post-QC outputs unless the user explicitly declares them as current-run authoritative inputs.

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
- no Stage C work performed

Do not infer replacement rules from memory.
Do not use archived docs.
Do not use branch-only docs.
Do not use local snippets unless the user explicitly provides them as current-run authoritative docs.

Important scope note:

docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md must be read before Stage C because it defines downstream state discipline, evidence hard-fail rules, and naming restrictions.

However, Stage C must not perform post-acceptance QC.

Stage C decides only whether Stage B draft_cards are:

- accepted_fact_safe
- revise_required
- rejected
- support_source_only
- deferred_review_pool

Stage C must not decide:

- addable_merge_safe
- evidence_complete
- source_claim_covered
- content_enriched
- language_terminology_polished
- publish_ready
- PR readiness
- GitHub readiness

Input files:

- Stage A JSON: {{STAGE_A_RESULTS_JSON}}
- Stage B JSON: {{STAGE_B_DRAFTS_JSON}}
- Stage B evidence packages: {{STAGE_B_EVIDENCE_PACKAGES_JSON}}
- Stage B report: {{STAGE_B_REPORT_MD}}
- Source input: {{SOURCE_INPUT_FILE}}
- Baseline cards: {{BASELINE_CARDS_SOURCE}}
- Baseline source declaration: {{BASELINE_SOURCE_DECLARATION}}
- Run tag: {{RUN_TAG}}
- Run label: {{RUN_LABEL_KST}}

Required input rule:

Stage C requires valid Stage A and Stage B outputs from the same run.

The Stage B JSON must include:

- required_docs_check
- run_tag
- run_label
- input_stage_a_file
- strict_passed_spec_count
- drafted_count
- draft_blocked_count
- stage_b_accounting_matches_strict_passed_spec_count
- draft_cards[]
- draft_blocked[]
- evidence_packages[]
- fetch_ledger[]

If Stage B JSON is missing, invalid, incomplete, not from the same run, or has accounting mismatch, stop and report:

- status: BLOCKED_STAGE_B_INVALID
- reason: [...]
- no Stage C work performed

Stage C may use only:

- Stage B draft_cards[]
- Stage B evidence_packages[]
- Stage B fetch_ledger[]
- Stage B writer_notes
- Stage A strict_passed_spec metadata for those drafted cards
- the active baseline only for duplicate-risk awareness, not final addable decision

Stage C must not use:

- Stage A review_pool
- Stage A rejected
- Stage A existing_reinforcement
- Stage A support_source_only
- Stage B draft_blocked as draft candidates
- previous accepted payloads
- previous addable payloads
- previous post-QC outputs
- previous PR candidates
- non-current-run files
- memory-based claims

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

Stage C role:

Stage C is the enhanced red-team validator and fact-safe acceptance gate.

Stage C must:

1. Review every Stage B draft_card.
2. Validate source direction.
3. Validate fact/source alignment.
4. Validate quote quality.
5. Validate visible-field claim support.
6. Validate fact vs implication separation.
7. Validate staleness and event_date logic.
8. Validate category, region, signal, and full-schema fit.
9. Validate language, terminology, and reader-facing tone.
10. Decide one Stage C outcome for each draft_card:
    - accepted_fact_safe
    - revise_required
    - rejected
    - support_source_only
    - deferred_review_pool
11. Produce machine-readable Stage C JSON and Markdown report.

Stage C must not:

- create new candidate cards
- promote Stage A review_pool
- resurrect Stage B draft_blocked
- silently drop draft_cards
- perform post-acceptance merge-safety
- assign addable_merge_safe
- assign evidence_complete
- assign source_claim_covered
- assign publish_ready
- rename output as FINAL / PR_CANDIDATE / GitHub-ready / merge-ready
- use web search as silent content enrichment
- add unsupported claims from memory or outside context

Critical Stage C state rule:

Stage C accepted means accepted_fact_safe only.

accepted_fact_safe is not:

- addable
- addable_merge_safe
- evidence_complete
- source_claim_covered
- content_enriched
- language_terminology_polished
- publish_ready
- PR-ready
- GitHub-ready

Every accepted_fact_safe card must include:

- publish_ready: false
- stage_c_only: true
- state: accepted_fact_safe

Stage C outcome definitions:

1. accepted_fact_safe

Use only when:
- the draft is within SBTL_HUB lane
- core event is source-supported
- source direction matches the card direction
- fact field is supported by fact_sources
- implication stays observational
- no fatal evidence issue is found
- no fatal staleness issue is found
- no fatal duplicate/reinforcement issue is obvious at Stage C level
- issues, if any, are minor and can be handled in downstream post-acceptance QC without changing the card’s core claim

Important:
accepted_fact_safe is still not addable and not publish_ready.

2. revise_required

Use only when:
- the card is likely salvageable
- issues are draft/card-level and fixable without reopening candidate selection
- evidence exists, but visible fields need narrowing, rewriting, claim removal, tone correction, category/signal adjustment, or source mapping clarification

Examples:
- title overstates the source
- gate is too definitive
- implication introduces a weak unsupported inference but can be narrowed
- signal is inflated but event is still cardable
- category/sub_cat needs correction
- fact wording needs closer source-locking
- source quote supports the claim but supports field/evidence_role needs cleanup
- visible wording contains workflow/meta language
- foreign-language residue remains

Do not use revise_required for:
- Stage A spec uncertainty
- missing core evidence
- stale republication with no fresh follow-up
- source direction reversal
- headline-only evidence for core claim
- non-cardable lane fit

Those should be rejected or deferred_review_pool depending on severity.

3. rejected

Use when the card should not proceed in the current run.

Reject for:
- unsupported core fact
- source direction reversal
- stale republication with no documented fresh follow-up
- headline-only core evidence
- snippet-only/RSS-only/listing-only core evidence
- no body-level or official-material support
- fact_sources do not support visible-field core claim
- memory-based number/date/company roadmap
- MOU/pilot reframed as commercial deployment
- semi-solid reframed as solid-state
- consideration/plan reframed as confirmed execution
- single company statement reframed as industry consensus
- event is out of SBTL_HUB lane
- generic landing/listing/static product page
- event is already covered and not a meaningful follow-up
- card requires speculation to be meaningful
- product/demo/PoC/pilot/prototype/component/interview/commentary/roundup/speech/personnel/partnership item lacks a concrete execution anchor

4. support_source_only

Use when:
- source is useful as background or supporting evidence
- event is not strong enough as an independent card
- item supports another accepted or future card
- item is a duplicate background source rather than a standalone event

support_source_only is not accepted_fact_safe and not addable.

5. deferred_review_pool

Use when:
- the card cannot be accepted safely in this run
- issue may be resolvable with a separate source augmentation, manual review, or candidate review loop
- evidence is partial but not clearly false
- duplicate/follow-up relation is uncertain
- source access requires additional manual work
- event_date/staleness uncertainty remains unresolved

deferred_review_pool is not accepted_fact_safe and not addable.

Web search / fetch boundary:

Stage C may perform limited spot-check only when needed for QC.

Allowed Stage C web use:

- verify source_quote is body-level or official-material
- verify source direction
- verify event_date / staleness
- verify source accessibility
- verify whether a source is headline-only, snippet-only, RSS-only, or listing-only
- spot-check duplicate or event conflict
- check official source when Stage B evidence appears inconsistent

Prohibited Stage C web use:

- discovering new card candidates
- promoting Stage A review_pool
- resurrecting draft_blocked
- adding new unsupported claims
- broad content enrichment
- silently adding numbers, forecasts, company intentions, policy effects, or market impact claims
- using web search to make a weak card look stronger without source-change disclosure

If Stage C finds useful new source evidence, do not silently insert it.

Instead mark:
- needs_source_augmentation: true
- recommended_next_action: source_augmentation_pass

Source augmentation is a separate user-authorized process.

Validation passes:

Stage C must run the following checks for every draft_card.

Pass 1 — Schema check

Validate required full-schema fields:

- id or draft_id
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

If ID is not final production ID, keep it as draft_id and do not assign final ID unless the workflow explicitly requires temporary ID normalization.

Stage C must not assign final production ID if doing so would imply publish readiness.

Pass 2 — Source direction check

Confirm the card direction matches source direction.

Reject or revise when:

- source says MOU but card says signed commercial deal
- source says pilot/prototype but card says commercial deployment
- source says semi-solid-state but card says solid-state
- source says consideration/plan but card says confirmed execution
- source says one company statement but card says industry consensus
- source reports old event but card frames it as fresh without follow-up
- product/demo/PoC/pilot/prototype/component/interview/commentary/roundup/speech/personnel/partnership wrapper is framed as independent strategic proof without a concrete execution anchor
- interview or roundup source is used as a generic theme instead of isolating a specific fresh event anchor
- card adds causality not present in source

Pass 2A — Execution-anchor check for format-risk cards

If a draft card originates from product news, demo, PoC, pilot, prototype, component launch, interview, commentary, event roundup, speech, personnel coverage, or partnership/integration coverage, Stage C must confirm that the visible fields are built around a concrete execution anchor.

Valid anchors include signed contract, binding customer order, offtake, price floor/risk-sharing facility, commercial deployment, field installation, commissioning, production start, facility opening, certification/regulatory approval, regulatory decision/enforcement, public funding approval, binding procurement, measurable capacity addition, safety recall/regulatory safety action, named customer adoption, named deployment site with measurable pilot scale/duration/objective, factory/project groundbreaking, or final investment decision.

Decision rule:

- If the anchor exists but wording overclaims its maturity, use revise_required to narrow the card.
- If no concrete execution anchor exists and the draft depends on strategic speculation, reject or classify as support_source_only.
- Do not reject solely because the source format is product/demo/PoC/interview/roundup; reject only because the execution anchor is absent, unsupported, stale, or non-cardable.

Pass 3 — Fact discipline check

Check every fact field claim.

For every number, date, company, project, policy, capacity, money amount, percentage, location, technology stage, and comparison in fact:

- confirm it is supported by fact_sources
- confirm source_quote supports the attached claim
- confirm source_quote is not headline-only/snippet-only/RSS-only/listing-only
- confirm claim is concrete and not just a label
- confirm no memory-based background has been inserted

If a core fact is unsupported, reject unless it can be removed without damaging the card; if removable, revise_required.

Pass 4 — Quote quality check

Hard-fail if any core evidence uses:

- missing source_quote
- headline-only source_quote
- RSS-only source_quote
- snippet-only source_quote
- listing-title source_quote
- exact article title as source_quote
- near-title paraphrase without body-level support
- generated summary as quote
- translated paraphrase without original-source support

Core claim evidence must have one of:

- body_quote_verified
- official_material_quote_verified
- document_quote_verified

If not, reject or deferred_review_pool depending on whether the card can be reworked with available evidence.

Pass 5 — fact_sources schema check

Each fact_sources item should include:

- source_name
- source_url
- claim
- source_quote
- source_quote_status
- evidence_role
- supports
- fetched_at
- fetch_method

If missing evidence_role/supports/source_name but source evidence is otherwise valid:
- revise_required

If fact_sources is URL-only:
- rejected

If source_quote_status is hard-fail:
- rejected unless the source is not used for visible fields and can be removed

Pass 6 — Claim coverage check

Map visible-field core claims to fact_sources.

At minimum check:

- title core claim
- sub core claim
- fact core claims
- every numeric claim
- any causal claim
- any stage claim
- implication claims that introduce factual dependency

Coverage strength values:

- strong
- adequate
- weak
- missing

If missing core coverage:
- revise_required if fixable by narrowing
- rejected if the card’s core event collapses

Pass 7 — Fact vs implication separation

fact must contain only source-backed facts.

gate and implication may interpret, but only one step beyond verified facts.

Reject or revise when:
- implication introduces new unsupported facts
- implication states certainty not supported by source
- gate asserts direct benefit or structural shift without evidence
- speculative outlook is written as fact
- “industry expects” or “market says” appears without source support

Allowed implication style:

- 관찰된다
- 확인할 필요가 있다
- 변수가 될 수 있다
- 점검 대상이다
- 가능성이 열린다
- 리스크로 남는다
- 후속 확인이 필요하다

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

Pass 8 — Staleness check

Use Stage B staleness_recheck and evidence.

Rules:

- gap ≤ 7 days: fresh
- gap 8–30 days: stale_warm; accepted only if the fresh signal is clearly articulated and source-supported
- gap > 30 days: reject unless a distinct fresh follow-up event is documented
- unknown event_date: revise_required or deferred_review_pool unless the event is clearly fresh from source context

Reject stale republication with no fresh follow-up.

Do not invent event dates.

Pass 9 — Duplicate / reinforcement awareness

Stage C is not final merge-safety, but it must flag obvious duplicate/reinforcement risk.

If the draft is obviously the same event already in baseline:
- support_source_only or rejected

If it appears to be a meaningful follow-up:
- accepted_fact_safe may proceed with duplicate_risk flag

If uncertain:
- deferred_review_pool or accepted_fact_safe with needs_post_acceptance_duplicate_review=true, depending on evidence strength

Stage C must not decide addable_merge_safe.

Pass 10 — Region / category / signal check

Validate:

- region = event location / jurisdiction, not media country
- cat = one of the 12 locked categories
- sub_cat = concise Korean display category
- signal = top/high/mid and not inflated
- source tier constraints are respected
- Tier 3 single-source does not receive top
- signal_rubric aligns with event scale

If fixable:
- revise_required

If card value fails:
- rejected or support_source_only

Pass 11 — Language / terminology check

Reject or revise if visible fields contain:

- raw Chinese/Japanese article title
- workflow/meta language
- unsupported bilingual clutter
- inconsistent units
- sensational language
- forced SBTL benefit
- banned phrases

Banned visible-field workflow/meta phrases include:

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

Normalize terminology:

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

Pass 12 — Reader value check

Even with evidence, the card must be useful as an SBTL_HUB intelligence card.

Evaluate:

- strategic relevance
- SBTL_HUB lane fit
- decision usefulness
- market/supply-chain/policy/materials/grid relevance
- whether the item is merely background

If source is good but card value is weak:
- support_source_only

If event is useful but needs sharper framing:
- revise_required

If event is strong and fact-safe:
- accepted_fact_safe

Stage C outputs:

Every Stage B draft_card must appear exactly once in Stage C output as one of:

- accepted_fact_safe
- revise_required
- rejected
- support_source_only
- deferred_review_pool

No silent skip is allowed.

Accounting rule:

Stage C must report:

- draft_cards_input_count
- accepted_fact_safe_count
- revise_required_count
- rejected_count
- support_source_only_count
- deferred_review_pool_count
- outcome_total_count
- stage_c_accounting_matches_draft_cards_input_count: true/false

If accounting does not match, mark Stage C output invalid and report:

- status: BLOCKED_STAGE_C_ACCOUNTING_MISMATCH

Output files:

1. stage_c_prompt_c_results_{{RUN_TAG}}.json
2. stage_c_prompt_c_report_{{RUN_TAG}}.md
3. stage_c_prompt_c_decisions_{{RUN_TAG}}.csv
4. stage_c_prompt_c_claim_coverage_review_{{RUN_TAG}}.json

Do not use FINAL, PR_CANDIDATE, GitHub-ready, merge-ready, publish-ready, evidence_complete, source_claim_covered, or addable_merge_safe in Stage C filenames.

Stage C JSON requirements:

The JSON must include:

- stage
- run_tag
- run_label
- input_stage_a_file
- input_stage_b_file
- input_evidence_packages_file
- baseline_file
- baseline_source_declaration
- baseline_count
- required_docs_check
  - docs_expected
  - docs_read_from_github_main
  - docs_missing_or_unreadable
  - status
- draft_cards_input_count
- accepted_fact_safe_count
- revise_required_count
- rejected_count
- support_source_only_count
- deferred_review_pool_count
- outcome_total_count
- stage_c_accounting_matches_draft_cards_input_count
- accepted_fact_safe[]
- revise_required[]
- rejected[]
- support_source_only[]
- deferred_review_pool[]
- decision_ledger[]
- claim_coverage_review[]
- stage_c_summary

Each accepted_fact_safe item must include:

- state: accepted_fact_safe
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
- stage_c_findings
  - source_direction
  - fact_safety
  - quote_quality
  - claim_coverage
  - staleness
  - duplicate_risk
  - language_tone
  - card_value
- needs_post_acceptance_duplicate_review
- needs_post_acceptance_evidence_qc: true
- stage_c_only: true
- publish_ready: false

Each revise_required item must include:

- state: revise_required
- draft_id
- source_spec_id
- issue_type
- issue_severity
- revise_reason
- specific_fields_to_revise
- required_changes
- evidence_status
- can_be_revised_without_new_source: true/false
- needs_source_augmentation: true/false
- recommended_next_action

Allowed issue_type values:

- title_overclaim
- sub_overclaim
- gate_overclaim
- fact_source_mismatch
- weak_claim_coverage
- implication_overreach
- category_or_signal_adjustment
- region_adjustment
- language_tone_issue
- terminology_issue
- foreign_language_residue
- source_schema_cleanup
- stale_warm_needs_fresh_signal
- duplicate_risk_uncertain
- other

Each rejected item must include:

- state: rejected
- draft_id
- source_spec_id
- rejection_reason_code
- rejection_reason_detail
- fatal_issue_field
- evidence_status
- source_direction_status
- staleness_status
- recommended_next_action

Allowed rejection_reason_code values:

- unsupported_core_fact
- source_direction_reversal
- headline_only_core_evidence
- snippet_only_core_evidence
- rss_only_core_evidence
- listing_only_core_evidence
- url_only_fact_sources
- source_quote_missing
- source_quote_status_hard_fail
- stale_republication
- no_fresh_followup
- event_out_of_scope
- duplicate_event
- insufficient_card_value
- memory_based_claim
- company_roadmap_unsupported
- numeric_claim_unsupported
- causal_claim_unsupported
- generic_landing_or_listing
- other

Each support_source_only item must include:

- state: support_source_only
- draft_id
- source_spec_id
- useful_for_topic
- reason_not_independent_card
- possible_target_card_or_spec
- evidence_summary
- recommended_next_action

Each deferred_review_pool item must include:

- state: deferred_review_pool
- draft_id
- source_spec_id
- defer_reason
- unresolved_questions
- required_manual_or_source_checks
- recommended_next_action
- not_addable_in_current_run: true

Each decision_ledger row must include:

- draft_id
- source_spec_id
- source_story_ids
- input_stage_b_status
- stage_c_outcome
- primary_reason
- source_direction_status
- fact_safety_status
- quote_quality_status
- claim_coverage_status
- staleness_status
- duplicate_risk_status
- language_tone_status
- card_value_status
- notes

Claim coverage review requirements:

For every accepted_fact_safe and revise_required card, include claim coverage review for:

- title core claim
- sub core claim
- fact core claims
- every numeric claim
- every causal claim
- every stage/timeline claim
- implication claims with factual dependency

Each claim_coverage_review item must include:

- draft_id
- field
- visible_claim
- covered_by_fact_sources
- coverage_strength
- issue
- action

Allowed coverage_strength values:

- strong
- adequate
- weak
- missing

Allowed action values:

- keep
- narrow
- revise
- remove
- reject
- defer

Stage C report requirements:

The Markdown report must include:

1. Run metadata

   - Stage A input file
   - Stage B input file
   - evidence packages file
   - baseline file/source
   - baseline source declaration
   - baseline count
   - run tag
   - run label
   - draft_cards input count

2. Required docs check

   - list all 8 required docs
   - confirm each was read from GitHub main
   - if any doc was not read, Stage C must not proceed

3. Method

   - Stage B draft_cards-only confirmation
   - draft_blocked exclusion confirmation
   - review_pool exclusion confirmation
   - Stage C outcome definitions
   - no publish_ready confirmation
   - no addable_merge_safe confirmation
   - limited spot-check policy
   - no silent content enrichment policy

4. Stage C summary table

   - draft_cards input count
   - accepted_fact_safe count
   - revise_required count
   - rejected count
   - support_source_only count
   - deferred_review_pool count
   - outcome total count
   - accounting match: yes/no

5. accepted_fact_safe manifest

   For each accepted card:
   - draft_id
   - source_spec_id
   - event anchor
   - region / cat / signal
   - key source
   - source direction result
   - fact safety result
   - staleness result
   - duplicate risk flag
   - post-acceptance checks still required

6. revise_required manifest

   For each revise_required card:
   - draft_id
   - issue type
   - exact problem
   - field(s) to revise
   - required change
   - whether new source augmentation is needed

7. rejected manifest

   For each rejected card:
   - draft_id
   - rejection reason code
   - fatal issue
   - evidence/source/staleness explanation

8. support_source_only manifest

   For each support_source_only item:
   - draft_id
   - why not independent card
   - what topic/card it can support

9. deferred_review_pool manifest

   For each deferred item:
   - draft_id
   - unresolved issue
   - what must be checked later

10. Claim coverage summary

   - strong count
   - adequate count
   - weak count
   - missing count
   - cards with missing core coverage
   - actions taken or required

11. Hard-fail summary

   Count:
   - source_quote missing
   - headline-only evidence
   - snippet-only evidence
   - RSS-only evidence
   - listing-only evidence
   - URL-only fact_sources
   - unsupported numeric claims
   - unsupported causal claims
   - source direction reversals
   - stale republications
   - memory-based claims
   - forced SBTL benefit claims

12. Explicit Stage C boundary statement

   Include this exact statement:

   “Stage C produced accepted_fact_safe, revise_required, rejected, support_source_only, and deferred_review_pool decisions only. Stage C did not decide addable_merge_safe, evidence_complete, source_claim_covered, content_enriched, language_terminology_polished, publish_ready, PR readiness, or GitHub readiness.”

13. Next-call recommendation statement

   Do not hard-code the next step as post-acceptance.

   Generate the structured `next_call_recommendation` object according to the Stage C r0 next-call recommendation rule below.

   If revise_required_count > 0, post-acceptance baseline revalidation must not be the recommended_next_call unless the user explicitly chooses an accepted-only path in a separate decision.



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

## Operational integrated rule — Stage C r0 next-call recommendation and revise-loop routing

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

After Stage C r0, recommend exactly one next call using this priority order:

1. If accepted_fact_safe_count > 0 and revise_required_count > 0:
   - recommended_next_call = "Stage B revise {{NEXT_REVISION_PASS}}"
   - recommended_prompt_id = "Prompt 0.2R"
   - recommended_input_universe = "Stage C revise_required[] only"
   - reason = "Some cards are already accepted_fact_safe, but fixable revise_required cards remain. Recommend B revise first so salvageable cards can join the same run before post-acceptance. Preserve the accepted_fact_safe pool unchanged."
   - blocked_items_summary = "revise_required cards must not enter post-acceptance until they pass Stage C revise validation. accepted_fact_safe cards are preserved but held from post-acceptance unless the user explicitly chooses an accepted-only path."
   - alternative_next_call = "post-acceptance baseline revalidation using accepted_fact_safe[] only, if the user explicitly chooses not to include revised cards in the same run"
   - do_not_proceed_to = "post-acceptance baseline revalidation, unless the user explicitly chooses the accepted-only path or the revise loop completes"

2. If accepted_fact_safe_count = 0 and revise_required_count > 0:
   - recommended_next_call = "Stage B revise {{NEXT_REVISION_PASS}}"
   - recommended_prompt_id = "Prompt 0.2R"
   - recommended_input_universe = "Stage C revise_required[] only"
   - reason = "No cards are accepted yet, but fixable card-level issues remain."
   - blocked_items_summary = "revise_required cards must not enter post-acceptance until they pass Stage C revise validation."
   - do_not_proceed_to = "post-acceptance baseline revalidation"

3. If accepted_fact_safe_count > 0 and revise_required_count = 0:
   - recommended_next_call = "post-acceptance baseline revalidation"
   - recommended_prompt_id = "Prompt 0.4"
   - recommended_input_universe = "Stage C accepted_fact_safe[] only"
   - reason = "No revise_required cards remain; accepted_fact_safe cards can move to addable/hold baseline revalidation."
   - blocked_items_summary = "No revise_required blockers. accepted_fact_safe is still not addable_merge_safe, evidence_complete, content_enriched, language_terminology_polished, or publish_ready."

4. If accepted_fact_safe_count = 0 and revise_required_count = 0:
   - recommended_next_call = "stop or retrospective"
   - recommended_prompt_id = "Prompt 1.1"
   - recommended_input_universe = "current run outputs"
   - reason = "No accepted or revise_required cards remain to advance."
   - blocked_items_summary = "Only rejected/support_source_only/deferred items remain, or no draft survived Stage C."

5. If rejected/support_source_only/deferred dominate, summarize whether the safer next action is stop, source augmentation review, manual review, or retrospective based on the actual hold/rejection reasons.

Do not proceed automatically.
Stop after Stage C.

Do not proceed to post-acceptance baseline revalidation until I explicitly say “post-acceptance” or “baseline revalidation”.

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


## Stage C source diversity awareness

Stage C does not perform final source diversity QC. However, if a draft relies on a single source, fallback source, rss-rich source, or source-strength caveat, Stage C must preserve that caveat and must not silently upgrade the card to clean accepted status.

Accepted cards with source-strength caveats must carry those caveats to 0.5 for source diversity / corroboration review.

## FIX-006 — Stage C must preserve provisional `id`

Stage C must preserve the provisional `id` from every Stage B `draft_card` into `accepted_fact_safe[]`, `revise_required[]`, `rejected[]`, and related lineage records.

Prompt 0.4 cannot perform ID-collision screening if Stage C drops `id`.

If Stage C intentionally changes or removes an ID, it must record `prior_id`, `new_id`, `id_change_reason`, and `id_collision_recheck_required=true`.

## FIX-007 — Shared schema contract and stage-exit conformance check

All stages must reference `SCHEMA_CONTRACT_STAGE_LINEAGE.md`.

Each named stage must run or explicitly satisfy a stage-exit artifact conformance check before recommending the next stage. Missing required fields must stop the stage with:

```text
BLOCKED_STAGE_OUTPUT_SCHEMA_NONCOMPLIANT
```

Do not wait until Prompt 0.4 to discover Stage A/B lineage omissions.

# 03_PROMPT_0_3_Stage_C_r0.md — Source Diversity source-diversity integrated rule

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

## Stage C source-diversity validation — HARD RULE

Stage C must independently recalculate canonical URL, domain and editorial-owner counts. It must
not trust a Stage B `PASS_MULTI_SOURCE` label.

For every draft, validate:

- all Stage A support-source candidates were attempted or explicitly dispositioned;
- repeated claim rows from one URL were counted as one source;
- mirrored or syndicated release copies were not counted as independent;
- every source has `source_role` and a concrete `source_contribution`;
- additional-source information is visible in `fact`, `gate` or `implication`;
- source publication dates, not fetch dates, are prepared for display.

Required per-card output:

```json
{
  "stage_c_source_diversity_review": {
    "recomputed_unique_url_count": 0,
    "recomputed_unique_domain_count": 0,
    "recomputed_independent_owner_count": 0,
    "false_multi_source_detected": false,
    "syndication_or_owner_overlap": [],
    "source_role_coverage": {},
    "source_synthesis_visible_field_check": "PASS|FAIL",
    "single_source_exception_check": "PASS|FAIL|NOT_APPLICABLE"
  }
}
```

A card may become `accepted_fact_safe` only when multi-domain synthesis passes or the narrow
single-source exception passes. Otherwise use `revise_required` or
`deferred_review_pool_needs_source_augmentation`, preferring repair over deletion.

Required blockers:

```text
BLOCKED_STAGE_C_FALSE_MULTI_SOURCE
BLOCKED_STAGE_C_SOURCE_CONTRIBUTION_MISSING
BLOCKED_STAGE_C_SYNTHESIS_NOT_VISIBLE
```

    Stop after Stage C. accepted_fact_safe is not publish_ready.

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
