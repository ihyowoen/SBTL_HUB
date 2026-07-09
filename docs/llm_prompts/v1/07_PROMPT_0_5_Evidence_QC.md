<!-- REPLACE_ALL_CLEAN_VERSION: LLM_PROMPT_GITHUB_CANONICAL_V1_SOURCE_DIVERSITY_IB_CODEX -->
<!-- Generated KST: 2026-07-08T21:33:49.790191+09:00 -->
<!-- This file is a full clean replacement file. It is not a patch stub. -->

Prompt 0.5v — Reusable Default / Replace All / Evidence Completeness & Source-Claim Coverage QC

Proceed to evidence completeness QC and source-claim coverage QC only.

Use the current run’s post-acceptance baseline revalidation output as the only candidate input universe for this step.

This step starts after full baseline revalidation.

Do not continue from, trust, import, integrated rule, or reuse any previous evidence QC, final, PR candidate, GitHub-ready, publish-ready, or post-QC outputs unless the user explicitly declares them as current-run authoritative inputs.

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
- no evidence QC work performed

Do not infer replacement rules from memory.
Do not use archived docs.
Do not use branch-only docs.
Do not use local snippets unless the user explicitly provides them as current-run authoritative docs.

Input files:

- Stage C JSON: {{STAGE_C_RESULTS_JSON}}
- Baseline revalidation JSON: {{BASELINE_REVALIDATION_JSON}}
- Addable merge-safe payload: {{ADDABLE_MERGE_SAFE_PENDING_EVIDENCE_QC_JSON}}
- Baseline hold manifest: {{BASELINE_HOLD_MANIFEST_JSON}}
- Active baseline cards: {{BASELINE_CARDS_SOURCE}}
- Baseline source declaration: {{BASELINE_SOURCE_DECLARATION}}
- Run tag: {{RUN_TAG}}
- Run label: {{RUN_LABEL_KST}}

Required input rule:

This step requires a valid baseline revalidation output from the same run.

The baseline revalidation JSON must include:

- required_docs_check
- run_tag
- run_label
- accepted_fact_safe_input_count
- addable_merge_safe[]
- duplicate_hold[]
- existing_reinforcement[]
- withheld_reinforcement[]
- baseline_conflict[]
- review_pool_deferred[]
- baseline_revalidation_accounting_matches_input_count

If baseline revalidation JSON is missing, invalid, incomplete, not from the same run, or has accounting mismatch, stop and report:

- status: BLOCKED_BASELINE_REVALIDATION_INVALID
- reason: [...]
- no evidence QC work performed


## Upstream lineage integrity gate

This prompt is downstream of selector, evidence, content, and/or production gates. It must not repair or launder an invalid upstream lineage.

Before doing any work, validate that the current-run baseline revalidation output carries a lineage integrity statement from the immediately previous step.

Required lineage fields, unless the previous step explicitly marks a field `not_applicable` with reason:

- `run_tag` matches this run
- `lineage_integrity_status: PASS`
- `stage_a_validity_status: PASS` or `not_applicable_after_validated_baseline_revalidation`
- `artifact_consistency_status: PASS` or `not_applicable_after_validated_baseline_revalidation`
- `accepted_pool_lineage_status: PASS` or `not_applicable_before_stage_c_pool`
- `strict_gate_metadata_preserved: true` or `not_applicable_after_non_card_stage`
- `execution_anchor_metadata_preserved: true` or `not_applicable_after_non_card_stage`
- `superseded_lineage_mixed: false`
- `manual_integrated rule_mixed: false`
- `previous_run_output_mixed: false`


For Prompt 0.5 specifically, baseline revalidation is the last upstream selector-safety checkpoint. It must prove that:
- Stage A was valid for the current run
- Stage A artifact consistency passed
- Stage B/C accepted pool was assembled only from the valid current-run lineage
- format-risk / execution-anchor metadata was preserved into addable_merge_safe[]
- no superseded Stage A/B/C lineage, previous accepted payload, or manually repaired candidate was mixed in

If any required lineage field is missing, false, contradictory, stale, not from the same run, or inconsistent with the candidate payload, stop immediately and report:

- status: BLOCKED_UPSTREAM_LINEAGE_INVALID
- reason: [...]
- invalid_or_missing_lineage_fields: [...]
- no evidence QC work performed

Do not infer lineage validity from memory.
Do not continue just because candidate counts look correct.
Do not use this prompt to fix Stage A/B/C selection defects or post-QC evidence defects.

Candidate input rule:

Only addable_merge_safe[] may enter evidence completeness QC.

Do not include:

- duplicate_hold
- existing_reinforcement
- withheld_reinforcement
- baseline_conflict
- review_pool_deferred
- revise_required
- rejected
- support_source_only
- deferred_review_pool
- Stage B draft_blocked
- Stage A review_pool
- previous final files
- previous PR candidates
- previous publish-ready payloads

If any non-addable_merge_safe item is mixed into the candidate input, exclude it and report it as mixed_input_excluded.


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


Evidence QC execution-anchor guard:

For every addable_merge_safe[] candidate, evidence QC must re-check whether the visible core claim depends on a Stage A execution anchor.

If a candidate has any of these tags:

- product_launch
- demo
- prototype
- PoC
- component
- interview
- commentary
- roundup
- partnership
- speech_or_political_statement
- personnel

then evidence QC must confirm body-level or official evidence for at least one concrete execution anchor, such as:

- signed contract
- customer order
- offtake
- commercial deployment
- field installation
- commissioning
- production start
- facility opening
- certification
- regulatory decision
- public funding approval
- binding procurement
- measurable capacity addition
- safety recall or regulatory action
- named customer adoption

If the anchor is missing or only implied by commentary, do not mark evidence_complete. Route the card to addable_hold_claim_gap or needs_return_to_prompt_c with reason execution_anchor_not_evidenced.

Evidence QC must not convert review_pool, support_source_only, rejected, duplicate_hold, existing_reinforcement, or baseline_conflict items into addable candidates.

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

- evidence_complete
- source_claim_covered
- addable_hold_source_gap
- addable_hold_claim_gap
- needs_source_augmentation
- evidence_qc_rejected
- review_pool_deferred

This step must not decide:

- content_enriched
- language_terminology_polished
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

This step may move addable_merge_safe only to:

- evidence_complete_and_source_claim_covered
- addable_hold_source_gap
- addable_hold_claim_gap
- needs_source_augmentation
- evidence_qc_rejected
- review_pool_deferred

It cannot move any card beyond source_claim_covered.

Hard rule:

addable_merge_safe is not evidence_complete and not publish_ready.

source_claim_covered is not content_enriched and not publish_ready.

Every surviving card after this step must still have:

- publish_ready: false

Do not preserve publish_ready=true from any upstream file.

If any candidate enters this step with publish_ready=true, reset it to false and record:

- publish_ready_reset: true
- reset_reason: evidence_qc_does_not_decide_publish_ready

Web search / fetch boundary:

This step may perform web fetch or web search only for evidence QC purposes.

Allowed purposes:

- verify source_quote exists in body-level or official-material source
- verify source_quote is not headline-only, snippet-only, RSS-only, or listing-only
- verify source_quote supports the attached claim
- verify source URL accessibility
- verify official source or document source if already cited
- verify source conflict or quote mismatch
- confirm whether evidence is sufficient for visible claims

Prohibited purposes:

- discovering new card candidates
- expanding card scope
- silently adding new facts
- rewriting visible fields
- rescuing rejected/revise_required cards
- creating publish_ready output
- adding new sources without explicit source augmentation authorization

Source augmentation rule:

By default, this step is QC, not source augmentation.

If useful new evidence is found but was not already in fact_sources:

- do not silently add it to fact_sources
- mark needs_source_augmentation: true
- record recommended source augmentation
- keep publish_ready=false

Only add or modify fact_sources if the user explicitly authorized source augmentation for this step.

If source augmentation is explicitly authorized, then:
- update fact_sources with required schema
- record source_change_diff
- rerun evidence completeness QC
- rerun source-claim coverage QC
- keep publish_ready=false

Evidence completeness hard-fail conditions:

A card fails evidence completeness if any core visible claim relies on:

- missing source_quote
- headline-only source_quote
- RSS-only source_quote
- snippet-only source_quote
- listing-card text only
- exact article title as source_quote
- near-title paraphrase without body-level or official-material support
- generated summary as quote
- translated paraphrase without original-source support
- source_quote_status missing
- source_quote_status unknown
- source_quote_status headline_only
- source_quote_status snippet_only
- source_quote_status rss_only
- source_quote_status listing_only
- source_quote_status not_generated
- source_quote_status not_generated_no_direct_quote_extraction
- fact_sources URL-only
- claim copied from headline
- claim that is a label rather than concrete factual claim
- missing source_name
- missing evidence_role
- missing supports
- single-source card relying on headline-only evidence
- source_quote that does not support the specific claim it is attached to

No override is allowed for headline-only core evidence.

Required publish-forward fact_sources schema:

Each core fact_sources item must include:

- source_name
- source_url
- claim
- source_quote
- source_quote_status
- evidence_role
- supports
- fetched_at or checked_at
- fetch_method

Allowed source_quote_status values for usable core evidence:

- body_quote_verified
- official_material_quote_verified
- document_quote_verified

All other source_quote_status values are unusable for core visible claims.

Allowed evidence_role values:

- primary_event_evidence
- secondary_event_evidence
- background_context
- not_used

Evidence role rules:

- At least one primary_event_evidence or strong secondary_event_evidence must support the core event.
- background_context may support framing only.
- background_context cannot rescue an unsupported core event.
- not_used evidence must not support visible fields.

Allowed supports values:

- title
- sub
- gate
- fact
- implication
- not_used

supports must be an array.

A source marked not_used must not be used to cover visible-field claims.

Single-source rule:

Single-source cards can pass evidence completeness only if the single source is:

- official filing
- government release
- company official release
- regulatory document
- primary dataset/statistics page
- article body with sufficient direct source text for all core visible claims

Single-source cards cannot pass if the only evidence is:

- RSS headline
- search snippet
- paywall headline only
- listing page title
- repost without body details
- source_quote not extracted
- headline-only article card

single_source_reason is not a waiver.

It must explain why the single source itself is body-level or official primary evidence sufficient for the visible claims.

Evidence completeness tests:

For each addable_merge_safe card, run the following.

Test 1 — fact_sources presence

Check:
- fact_sources exists
- fact_sources is not empty
- fact_sources is not URL-only
- every fact_sources item has required fields

If missing:
- addable_hold_source_gap

Test 2 — source_quote quality

For every fact_sources item used for visible fields:

Check:
- source_quote exists
- source_quote is body-level or official-material
- source_quote is not title/headline/snippet/RSS/listing-only
- source_quote_status is usable
- source_quote directly supports claim

If a core claim fails:
- addable_hold_source_gap or evidence_qc_rejected depending on severity

Test 3 — source_quote / claim alignment

For each fact_sources item:

Check:
- claim is concrete factual claim
- claim is not copied from headline
- source_quote supports that exact claim
- source_quote does not merely support a weaker/different claim

If mismatch is fixable by narrowing visible fields:
- addable_hold_claim_gap or needs_source_augmentation

If core event collapses:
- evidence_qc_rejected

Test 4 — visible claim coverage

Map all visible claims to fact_sources.

At minimum map:

- title core claim
- sub core claim
- gate core claims
- fact core claims
- every numeric claim
- every date claim
- every company/project/entity claim
- every causal claim
- every technology-stage claim
- every timeline claim
- implication claims that depend on factual assertions

Coverage strength values:

- strong
- adequate
- weak
- missing

Actions:

- keep
- narrow
- remove
- source_augmentation_needed
- hold
- reject

If title/sub/fact core claim coverage is missing:
- addable_hold_claim_gap or evidence_qc_rejected

If implication coverage is weak but core event is safe:
- addable_hold_claim_gap or pass with needs_content_narrowing=true, depending on severity

Test 5 — numeric claim audit

For every number in visible fields:

Check:
- the exact number is in source_quote or clearly supported by source_quote
- units are supported
- currency conversion is sourced or removed
- percentage comparison is sourced
- capacity / money / volume / date / headcount / GWh/MWh/MW values are supported

Unsupported numeric claim:
- addable_hold_claim_gap
- evidence_qc_rejected if central to card

Test 6 — causal and stage claim audit

Check for unsupported causality or stage escalation.

Fail or hold if visible fields claim:

- will benefit
- directly benefits
- caused by
- leads to
- commercial deployment
- mass production
- binding contract
- final approval
- structural shift
- roadmap year
- market consensus

without direct source support.

Test 7 — fact vs implication support

Check:
- fact contains only verified facts
- gate and implication interpret only within source-supported direction
- implication does not introduce new unsupported fact
- SBTL/direct benefit language is not forced

This step may flag needs_content_narrowing but must not perform content enrichment.

Test 8 — source role sufficiency

Check:
- at least one primary_event_evidence or strong secondary_event_evidence supports the core event
- background_context is not being used as primary evidence
- not_used sources do not cover visible fields
- single-source rule is satisfied if applicable

Test 9 — accessibility / quote verification

When needed, fetch cited URLs to verify quote status.

Record:

- quote_verified
- quote_not_found
- page_inaccessible
- paywall_blocked
- js_blocked
- official_document_verified
- source_conflict_found

If quote cannot be verified and is core evidence:
- addable_hold_source_gap

Test 10 — source conflict check

If sources conflict on core number/date/event/action:

- do not choose silently
- mark review_pool_deferred or needs_source_augmentation
- record conflict details

Output state definitions:

1. evidence_complete_and_source_claim_covered

Use only when:

- fact_sources are complete
- source_quote quality passes
- core event evidence is body-level or official-material
- title/sub/fact/numeric claims are covered
- source_claim_covered is true
- no hard-fail evidence condition remains
- publish_ready remains false
- content/language/final QC still required

Every item in this state must include:

- state: evidence_complete_and_source_claim_covered
- previous_state: addable_merge_safe
- evidence_complete: true
- source_claim_covered: true
- content_enriched: false
- language_terminology_polished: false
- publish_ready: false
- needs_content_enrichment: true
- needs_language_terminology_polish: true
- needs_publish_readiness_qc: true

2. addable_hold_source_gap

Use when:

- fact_sources are missing or incomplete
- source_quote is missing
- source_quote is not body-level/official-material
- source_quote_status is hard-fail
- source is inaccessible and quote cannot be verified
- fact_sources are URL-only
- evidence_role/supports/source_name missing in a way that blocks evidence completeness
- single-source evidence is insufficient

3. addable_hold_claim_gap

Use when:

- evidence exists but visible claims are not fully covered
- title/sub/fact/numeric/causal claim mapping is weak or missing
- source_quote supports a narrower claim than visible field states
- implication introduces unsupported factual dependency
- card may be saved by narrowing visible fields in content enrichment or source augmentation

4. needs_source_augmentation

Use when:

- current source package is insufficient
- likely official/body-level source exists
- QC found possible new evidence but source augmentation was not authorized
- source conflict needs additional evidence
- visible claim could be supported only with an additional source

5. evidence_qc_rejected

Use when:

- core event cannot be supported
- source quote hard-fail cannot be repaired
- fact_sources are URL-only and no body-level evidence exists
- headline-only evidence is the only support
- core claim is false or contradicted by source
- card requires speculation to survive
- source direction reversal is discovered

6. review_pool_deferred

Use when:

- evidence status cannot be resolved in current step
- source access requires manual work
- quote verification is blocked
- source conflict requires human review
- source language/document extraction is uncertain

Accounting rule:

Every addable_merge_safe item must appear exactly once in one of:

- evidence_complete_and_source_claim_covered
- addable_hold_source_gap
- addable_hold_claim_gap
- needs_source_augmentation
- evidence_qc_rejected
- review_pool_deferred

No silent skip is allowed.

Report:

- addable_merge_safe_input_count
- evidence_complete_and_source_claim_covered_count
- addable_hold_source_gap_count
- addable_hold_claim_gap_count
- needs_source_augmentation_count
- evidence_qc_rejected_count
- review_pool_deferred_count
- outcome_total_count
- evidence_qc_accounting_matches_input_count

If accounting does not match, mark output invalid and report:

- status: BLOCKED_EVIDENCE_QC_ACCOUNTING_MISMATCH

Content handling:

Do not rewrite visible fields in this step.

Do not edit:

- title
- sub
- gate
- fact
- implication

unless the user explicitly authorizes claim-narrowing edits inside evidence QC.

Default behavior:
- identify unsupported claims
- map them
- hold or flag them
- do not silently rewrite them

Source handling:

Do not rewrite fact_sources by default.

Do not modify source_quote by default.

If existing source fields contain obvious schema gaps but evidence is otherwise valid, record:

- source_schema_gap
- required_schema_fix

If source augmentation is not explicitly authorized, do not add new fact_sources.

If source augmentation is authorized, record all changes in:

- source_change_diff

Output files:

1. evidence_qc_results_{{RUN_TAG}}.json
2. evidence_qc_report_{{RUN_TAG}}.md
3. evidence_qc_decisions_{{RUN_TAG}}.csv
4. source_claim_coverage_map_{{RUN_TAG}}.json
5. evidence_complete_source_claim_covered_PENDING_CONTENT_QC_{{RUN_TAG}}.json
6. evidence_qc_hold_manifest_{{RUN_TAG}}.json

Do not use FINAL, PR_CANDIDATE, GitHub-ready, merge-ready, or publish-ready in filenames.

The phrase evidence_complete may be used only for cards that also clearly include publish_ready=false and pending content/language/final QC flags.

JSON output requirements:

The main JSON must include:

- stage
- run_tag
- run_label
- input_baseline_revalidation_file
- input_addable_merge_safe_file
- baseline_file
- baseline_source_declaration
- baseline_count
- required_docs_check
  - docs_expected
  - docs_read_from_github_main
  - docs_missing_or_unreadable
  - status
- addable_merge_safe_input_count
- mixed_input_excluded_count
- evidence_complete_and_source_claim_covered_count
- addable_hold_source_gap_count
- addable_hold_claim_gap_count
- needs_source_augmentation_count
- evidence_qc_rejected_count
- review_pool_deferred_count
- outcome_total_count
- evidence_qc_accounting_matches_input_count
- hard_fail_summary
- quote_quality_summary
- claim_coverage_summary
- single_source_summary
- source_accessibility_summary
- evidence_complete_and_source_claim_covered[]
- addable_hold_source_gap[]
- addable_hold_claim_gap[]
- needs_source_augmentation[]
- evidence_qc_rejected[]
- review_pool_deferred[]
- mixed_input_excluded[]
- source_claim_coverage_map[]
- decision_ledger[]

Each evidence_complete_and_source_claim_covered item must include:

- state: evidence_complete_and_source_claim_covered
- previous_state: addable_merge_safe
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
- content_enriched: false
- language_terminology_polished: false
- publish_ready: false
- needs_content_enrichment: true
- needs_language_terminology_polish: true
- needs_publish_readiness_qc: true
- evidence_qc_findings
  - quote_quality
  - fact_sources_schema
  - source_role_sufficiency
  - single_source_status
  - numeric_claim_audit
  - causal_claim_audit
  - source_accessibility
- claim_coverage_summary
- publish_ready_reset
- reset_reason
- notes

Each addable_hold_source_gap item must include:

- state: addable_hold_source_gap
- previous_state: addable_merge_safe
- draft_id
- source_spec_id
- hold_reason_code
- hold_reason_detail
- missing_or_invalid_evidence
- source_quote_status_findings
- fact_sources_schema_findings
- affected_visible_fields
- required_fix
- recommended_next_action

Allowed hold_reason_code values:

- source_quote_missing
- source_quote_headline_only
- source_quote_snippet_only
- source_quote_rss_only
- source_quote_listing_only
- source_quote_not_found
- source_quote_status_hard_fail
- fact_sources_url_only
- missing_source_name
- missing_evidence_role
- missing_supports
- single_source_insufficient
- source_inaccessible
- quote_verification_failed
- background_context_only
- other

Each addable_hold_claim_gap item must include:

- state: addable_hold_claim_gap
- previous_state: addable_merge_safe
- draft_id
- source_spec_id
- hold_reason_code
- hold_reason_detail
- uncovered_claims
- weak_claims
- affected_visible_fields
- required_fix
- can_be_fixed_by_content_narrowing
- needs_source_augmentation
- recommended_next_action

Allowed hold_reason_code values:

- title_claim_uncovered
- sub_claim_uncovered
- fact_claim_uncovered
- numeric_claim_uncovered
- causal_claim_uncovered
- timeline_claim_uncovered
- implication_claim_uncovered
- source_quote_supports_narrower_claim
- source_conflict
- other

Each needs_source_augmentation item must include:

- state: needs_source_augmentation
- previous_state: addable_merge_safe
- draft_id
- source_spec_id
- augmentation_reason
- missing_claim_support
- candidate_source_hint, if discovered
- source_change_authorization_required: true
- recommended_next_action

Each evidence_qc_rejected item must include:

- state: evidence_qc_rejected
- previous_state: addable_merge_safe
- draft_id
- source_spec_id
- rejection_reason_code
- rejection_reason_detail
- fatal_evidence_issue
- affected_visible_fields
- recommended_next_action

Allowed rejection_reason_code values:

- unsupported_core_event
- headline_only_core_evidence
- snippet_only_core_evidence
- rss_only_core_evidence
- listing_only_core_evidence
- url_only_fact_sources_unrepairable
- source_contradicts_core_claim
- source_direction_reversal_discovered
- no_body_or_official_evidence
- speculation_required
- other

Each review_pool_deferred item must include:

- state: review_pool_deferred
- previous_state: addable_merge_safe
- draft_id
- source_spec_id
- defer_reason
- unresolved_evidence_questions
- required_manual_checks
- recommended_next_action
- not_publish_ready: true

Each source_claim_coverage_map item must include:

- draft_id
- field
- visible_claim
- claim_type
- covered_by_fact_sources
- supporting_source_names
- supporting_source_urls
- supporting_source_quotes
- coverage_strength
- issue
- action

Allowed claim_type values:

- title_core
- sub_core
- gate_core
- fact_core
- numeric
- date
- entity
- causal
- stage_or_timeline
- implication_dependency

Allowed coverage_strength values:

- strong
- adequate
- weak
- missing

Allowed action values:

- keep
- narrow
- remove
- source_augmentation_needed
- hold
- reject

Each decision_ledger row must include:

- draft_id
- source_spec_id
- prior_state
- evidence_qc_outcome
- evidence_complete
- source_claim_covered
- source_quote_status_summary
- hard_fail_detected
- claim_coverage_status
- single_source_status
- publish_ready_reset
- reason
- notes

Hard-fail summary must count:

- source_quote_missing
- source_quote_headline_only
- source_quote_snippet_only
- source_quote_rss_only
- source_quote_listing_only
- source_quote_status_fail
- fact_sources_url_only
- claim_copied_from_headline
- missing_source_name
- missing_evidence_role
- missing_supports
- background_context_only_core_claim
- single_source_headline_only
- unsupported_numeric_claim
- unsupported_causal_claim
- unsupported_timeline_claim
- source_conflict
- publish_ready_true_reset_count

Report requirements:

The Markdown report must include:

1. Run metadata

   - baseline revalidation input file
   - addable merge-safe input file
   - baseline file/source
   - baseline source declaration
   - baseline count
   - run tag
   - run label
   - addable_merge_safe input count

2. Required docs check

   - list all 8 required docs
   - confirm each was read from GitHub main
   - if any doc was not read, this step must not proceed

3. Method

   - addable_merge_safe-only confirmation
   - mixed input exclusion confirmation
   - evidence completeness tests
   - source-claim coverage method
   - source_quote verification method
   - single-source rule
   - no content rewrite confirmation
   - no publish_ready confirmation
   - source augmentation authorization status

4. Summary table

   - addable_merge_safe input count
   - evidence_complete_and_source_claim_covered count
   - addable_hold_source_gap count
   - addable_hold_claim_gap count
   - needs_source_augmentation count
   - evidence_qc_rejected count
   - review_pool_deferred count
   - mixed_input_excluded count
   - outcome total count
   - accounting match: yes/no

5. evidence_complete_and_source_claim_covered manifest

   For each passed item:
   - draft_id
   - source_spec_id
   - short event anchor
   - quote quality result
   - claim coverage result
   - single-source status
   - hard-fail count
   - next required gate: content enrichment and language/terminology polish

6. Hold manifest

   Include:
   - addable_hold_source_gap
   - addable_hold_claim_gap
   - needs_source_augmentation
   - evidence_qc_rejected
   - review_pool_deferred

   For each item:
   - draft_id
   - hold/rejection/defer reason
   - affected visible fields
   - missing or weak evidence
   - recommended next action

7. Source quote hard-fail summary

   Include counts for:
   - missing source_quote
   - headline-only
   - snippet-only
   - RSS-only
   - listing-only
   - source_quote_status fail
   - URL-only fact_sources
   - missing evidence_role/supports/source_name

8. Source-claim coverage summary

   Include:
   - strong count
   - adequate count
   - weak count
   - missing count
   - cards with title/sub/fact missing coverage
   - cards with unsupported numeric claims
   - cards with unsupported causal/stage claims

9. Single-source caution summary

   Include:
   - single-source count
   - single-source passed count
   - single-source hold count
   - single-source rejected count
   - reason for each hold/rejection

10. Source augmentation candidates

   Include:
   - draft_id
   - missing claim support
   - candidate source hint, if any
   - why source augmentation authorization is required

11. Explicit boundary statement

   Include this exact statement:

   “Evidence QC decided evidence_complete and source_claim_covered status only. It did not decide content_enriched, language_terminology_polished, publish_ready, PR readiness, or GitHub readiness.”

12. Next-step statement

   Include this exact statement:

   “The next step is content enrichment and language/terminology polish. Only evidence_complete_and_source_claim_covered cards may enter that step. source_claim_covered is not publish_ready.”

## Operational integrated rule — upstream lineage and execution-anchor guard for evidence QC

Evidence QC must not launder a weak or invalid Stage A selection into evidence_complete/source_claim_covered status.

Before evaluating `addable_merge_safe[]`, verify that the baseline revalidation output explicitly preserved upstream lineage status from Stage A/B/C/0.4.

Required lineage fields in the baseline revalidation JSON, or in an attached lineage manifest referenced by that JSON:

- `stage_a_validity_status = PASS`
- `artifact_consistency_status = PASS`
- `enhanced_selector_precision_version = 20260505_safe_execution_anchor` or later/equivalent
- `stage_b_validity_guard_applied = true`
- `stage_c_strict_gate_acceptance_guard_applied = true`
- `baseline_revalidation_lineage_guard_status = PASS`
- `accepted_fact_safe_with_missing_strict_gate_count = 0`
- `accepted_fact_safe_with_failed_strict_gate_count = 0`
- `accepted_fact_safe_with_unresolved_execution_anchor_gap_count = 0`

For every candidate in `addable_merge_safe[]`, require either:

1. `strict_pass_gate.status = PASS`, or
2. an equivalent lineage field showing that the candidate passed Stage A strict-gate validation and Stage C strict-gate acceptance validation.

For every candidate with `format_risk_tags` such as product/demo/PoC/component/interview/roundup/commentary/speech/personnel/partnership, require:

- `execution_anchor_type` is not null;
- `execution_anchor_strength` is `adequate` or `strong`; and
- Stage C did not leave unresolved `execution_anchor_gap`, `selection_defect`, or `source_direction_reversal` findings.

If any required upstream lineage field is missing, contradictory, or failed, stop and report:

```json
{
  "status": "BLOCKED_INVALID_UPSTREAM_LINEAGE_FOR_EVIDENCE_QC",
  "no_evidence_qc_work_performed": true,
  "reason": "Evidence QC cannot repair or launder Stage A/B/C selector-lineage defects.",
  "recommended_next_call": "rerun Stage A with enhanced selector precision or repair upstream artifact lineage"
}
```

If only individual candidates have lineage or execution-anchor gaps while the overall lineage is valid, exclude those candidates from evidence QC and record them as:

- `addable_hold_selection_lineage_gap`, or
- `addable_hold_execution_anchor_gap`

Do not mark any such candidate as `evidence_complete` or `source_claim_covered`.

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

## Operational integrated rule — evidence QC next-call recommendation

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

1. If evidence_complete_and_source_claim_covered_count > 0:
   - recommended_next_call = "content enrichment and language/terminology polish"
   - recommended_prompt_id = "Prompt 0.6"
   - recommended_input_universe = "evidence_complete_and_source_claim_covered[] only"

2. If holds dominate:
   - recommend source augmentation, claim narrowing, manual review, or retrospective based on hold_reason_code and evidence_qc outcome distribution

Do not proceed automatically to content enrichment or language polish.
Stop after evidence completeness and source-claim coverage QC.

Do not proceed to content enrichment or language polish until I explicitly say “content enrichment” or “language polish”.

---

## Execution-anchor and selector-lineage safety overlay — 2026-05-05

This overlay is downstream of the Stage A safe-selector integrated rule. It prevents post-acceptance steps from laundering a weak or superseded Stage A/B/C lineage into publish-ready or production status.

Terminology lock:

- Do not use or enforce a format-based hard-exclude rule.
- Product, demo, PoC, component, interview, commentary, roundup, speech, or personnel formats are not automatically rejected by format alone.
- They are subject to a strict-pass presumption block: without a concrete fresh execution anchor, they must not have entered `strict_passed_spec[]`; if they did, the downstream step must hold, reject, or return the item to the appropriate prior stage rather than polishing it forward.
- Concrete execution anchors include signed contract, binding customer order, offtake, commercial deployment, field installation, commissioning, production start, facility opening, certification, regulatory decision, public funding approval, binding procurement, measurable capacity addition, safety recall/regulatory action, or named customer adoption.

### Required upstream lineage gate for Evidence QC

Before Evidence QC begins, verify that `BASELINE_REVALIDATION_JSON` carries a valid current-run lineage declaration. It should either contain these fields directly or preserve them through a nested `upstream_lineage` / `stage_a_lineage` object:

- `stage_a_validity_status: PASS`
- `artifact_consistency_gate.status: PASS`
- the Stage A selector marker includes `20260505_safe_execution_anchor`, `execution_anchor_presumption_block`, or later equivalent
- every addable candidate originated from Stage C `accepted_fact_safe[]` in the same run
- no candidate came from Stage A `review_pool[]`, Stage B `draft_blocked[]`, Stage C `revise_required[]`, `rejected[]`, `support_source_only[]`, or any superseded r0/r1 lineage

If any field is missing, contradictory, or indicates a superseded/invalid lineage, stop and report:

```text
status: BLOCKED_UPSTREAM_LINEAGE_INVALID
reason: [...]
no evidence QC work performed
```

### Execution-anchor evidence check

For every `addable_merge_safe[]` item with any of the following markers, Evidence QC must verify body-level or official evidence for the execution anchor before assigning `evidence_complete_and_source_claim_covered`:

- `format_risk_tags` is non-empty
- `execution_anchor_type` is present
- `execution_anchor_strength` is `candidate`, `weak`, `uncertain`, or missing
- `strict_pass_gate.format_risk_handled` is not `pass`
- the visible fields imply execution, deployment, certification, funding, procurement, or commercial scale

If the evidence does not support the execution anchor, route the card to one of:

- `addable_hold_claim_gap`
- `addable_hold_source_gap`
- `needs_source_augmentation`
- `evidence_qc_rejected`

Do not fix this by rewriting prose alone. Evidence QC cannot convert a format-risk candidate into `source_claim_covered` unless the concrete execution anchor is source-backed.

### Output requirement

Add to the Evidence QC JSON:

```json
"upstream_lineage_validation": {
  "stage_a_validity_status": "PASS|FAIL|MISSING",
  "artifact_consistency_status": "PASS|FAIL|MISSING",
  "stage_a_selector_marker": "enhanced_selector_precision_version: 20260505_safe_execution_anchor | selector_policy_version: execution_anchor_presumption_block | later equivalent",
  "superseded_lineage_detected": false,
  "decision": "pass|blocked"
},
"execution_anchor_qc_summary": {
  "format_risk_input_count": 0,
  "execution_anchor_supported_count": 0,
  "execution_anchor_hold_count": 0,
  "execution_anchor_rejected_count": 0
}
```

Final override: if `upstream_lineage_validation.decision != "pass"`, the next recommended call must not be Prompt 0.6. It must be upstream repair or rerun from the last valid stage.

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

## Operational integrated rule — MANDATORY_EVIDENCE_QC_HOLD_RESCUE_20260507

Prompt 0.5 must not finalize `addable_hold_source_gap`, `addable_hold_claim_gap`, `needs_source_augmentation`, or `evidence_qc_rejected` until a bounded hold-rescue pass has been attempted and logged.

Rescue requirements by failure type:

### source_gap / RSS-only / snippet-only / listing-only

Check, in order:

1. official issuer/company/regulator/agency/project-owner newsroom or filing,
2. official report/tender/consultation/document page,
3. Tier 1 or Tier 2 same-event body article,
4. credible specialty press body article.

### claim_gap

For each missing visible-field claim, search for direct support in:

1. already-fetched evidence package,
2. official/body-level source for the same event,
3. same-event Tier 1/Tier 2 alternate source.

### quote/schema gap

If the underlying source evidence exists but metadata enum/schema is invalid, perform metadata/schema repair only; do not treat enum mismatch as a factual failure.

0.5 output must include:

- `hold_rescue_attempted_count`
- `hold_rescue_success_count`
- `hold_rescue_failed_count`
- `hold_rescue_ledger[]`
- per-card `rescue_attempted`
- per-card `rescue_attempt_log[]`
- per-card `final_hold_after_rescue: true|false`

Only after this pass may a card remain on hold.

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


## Prompt 0.5 v4 output schema additions

Prompt 0.5 JSON output must include these fields in addition to existing fields:

- source_strength_clean_pass[]
- recommended_0_5R_source_strength_review[]
- mandatory_0_5R_evidence_rescue[]
- source_strength_caveat[]
- source_strength_caveat_count
- caveat_triggered_0_5R_count
- caveat_waived_by_user
- caveat_waiver_reason, if applicable

Every item in recommended_0_5R_source_strength_review[] must include:

- source_spec_id
- card_id
- caveat_type
- caveat_detail
- recommended_source_classes_to_check[]
- official_or_original_source_candidate_terms[]
- reason_not_clean_pass
- recommended_next_action: run_0_5R_source_strength_review

Every item in mandatory_0_5R_evidence_rescue[] must include the full rescue metadata required by NO_UNVERIFIED_HOLD_OR_DELETE_RULE and FIND_AND_INTEGRATE_WITH_VALIDATION_RULE.


## Operational integrated rule — REVIEW_TREASURE_RESCUE_AUDIT_STATUS_GATE_20260507_V5

This rule operationalizes the Review Pool + Treasure Rescue Audit requirement.

Stage A review pools, TRIAGE_FILTERED items, DROPPED treasure candidates, newsletter-expanded treasure items, and any missed-treasure candidates must not be treated as exhausted unless a rescue audit is completed or explicitly deferred.

### Trigger

A Review Pool + Treasure Rescue Audit is required when any of the following are true:

- `candidate_review_pool_count > 0`
- `TRIAGE_FILTERED_count > 0`
- `DROPPED_count > 0` and `dropped_review_treasure_hunt` is triggered
- `missed_treasure` or `newsletter_expanded_added_treasure` items exist
- the user asks to audit review pool, treasure, false holds, false rejects, or missed candidates

### Required status fields

Every Stage A output and every downstream stage that claims the current source universe is complete must carry:

- `rescue_audit_required: true|false`
- `rescue_audit_status: PASS|EXPLICITLY_DEFERRED|BLOCKED_RESCUE_AUDIT_MISSING|NOT_APPLICABLE`
- `rescue_audit_trigger_reason[]`
- `rescue_audit_input_universe_count`
- `rescue_audit_completed_at`, if PASS
- `rescue_audit_artifacts[]`, if PASS
- `rescue_candidate_strict_spec_count`, if PASS
- `rescue_audit_deferral_reason`, if EXPLICITLY_DEFERRED
- `rescue_audit_recommended_next_action`

If `rescue_audit_required=true` and `rescue_audit_status` is missing, stale, contradictory, or not PASS/EXPLICITLY_DEFERRED, the stage must stop with:

- `status: BLOCKED_REVIEW_TREASURE_RESCUE_AUDIT_MISSING`
- `no next-stage recommendation`
- `blocked_reason: review_or_treasure_universe_not_audited`

### Placement in workflow

This audit does not promote items directly to Stage B.

It produces one of:

- `rescue_candidate_strict_spec[]`
- `confirmed_review_hold[]`
- `confirmed_support_only[]`
- `confirmed_duplicate_or_existing_reinforcement[]`
- `confirmed_rejected_after_review[]`

A `rescue_candidate_strict_spec[]` item may enter Stage B only through an explicit user-authorized rescue/promotion pass. It must then follow Stage B, Stage C, 0.4, 0.5, 0.6, and 0.7 like any normal card candidate.

### Deferral

An operator may defer the audit only by recording:

- `rescue_audit_status: EXPLICITLY_DEFERRED`
- `rescue_audit_deferral_reason`
- `deferred_item_count`
- `deferred_item_ids[]` or documented sampling boundary
- `next_required_action`
- `sample_only_not_exhaustive`, if sampling was used
- `source_universe_completion_status: PARTIAL_STRICT_SUBSET_ONLY`

A deferred audit means the current merge/package may be valid for the processed strict-pass subset, but must not be described as source-universe-complete.

Deferral is not closure. `EXPLICITLY_DEFERRED` must include a concrete return condition and owner-facing next action. It cannot be used when the user explicitly asked to review the pool/treasure universe now. If deferral is based on sampling, the output must state `sample_only_not_exhaustive: true` and must list the unsampled boundary. Deferred items remain open until a later authorized review resolves them or closes them with hard-reject/support-only ledger evidence.


## Operational integrated rule — PROMPT_0_5R_SUPPLEMENTAL_FACT_SOURCE_METADATA_COMPLETE_20260508_V6

This v6 integrated rule closes the clean-v5 defect where 0.5R supplemental fact_sources could be returned downstream without `fetched_at` / `checked_at` metadata.

Every new, repaired, supplemental, strengthened, or metadata-repaired `fact_sources[]` entry introduced or touched by Prompt 0.5R must include all publish-forward fields before the item may return to 0.6, 0.6 supplemental, or 0.7.

Required fields for every 0.5R new/supplemental/touched fact_source:

```text
source_name
source_url
claim
source_quote
source_quote_status
evidence_role
supports
fetch_method
fetched_at or checked_at
```

Allowed `source_quote_status` values for publish-forward 0.5R output remain:

```text
body_quote_verified
official_material_quote_verified
document_quote_verified
```

0.5R JSON output must include:

```json
"supplemental_fact_source_metadata_qc": {
  "status": "PASS",
  "supplemental_fact_source_count": 0,
  "fact_source_required_metadata_gap_count": 0,
  "fact_source_required_metadata_gap[]": [],
  "all_supplemental_fact_sources_have_fetched_at_or_checked_at": true,
  "all_supplemental_fact_sources_have_source_quote_status": true,
  "all_supplemental_fact_sources_have_evidence_role_and_supports": true
}
```

If any required metadata field is missing, Prompt 0.5R must stop and report:

```text
status = BLOCKED_0_5R_SUPPLEMENTAL_FACT_SOURCE_METADATA_INCOMPLETE
fact_source_required_metadata_gap_count > 0
no return to 0.6, 0.6 supplemental, or 0.7
```

A metadata-only repair is allowed only when it does not change visible fields, source_quote meaning, claim scope, or source direction. It must be explicitly marked:

```text
repair_type = metadata_only
visible_fields_changed = false
source_quote_text_changed = false
claim_scope_changed = false
```


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


## Prompt 0.5 source diversity / corroboration review

Prompt 0.5 must perform source diversity and corroboration review separately from evidence completeness and source-claim coverage.

Every `addable_merge_safe[]` item must receive a `source_diversity_review` entry:

```json
{
  "card_id": "...",
  "source_diversity_required": true,
  "requirement_reason_codes": ["policy_or_regulatory_claim", "high_signal"],
  "source_diversity_status": "PASS_MULTI_SOURCE | PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION | HOLD_NEEDS_SOURCE_AUGMENTATION | HOLD_NEEDS_SOURCE_AUGMENTATION | FAIL_SOURCE_DIVERSITY",
  "distinct_source_urls": 0,
  "distinct_source_domains": 0,
  "core_event_source_count": 0,
  "primary_event_evidence_count": 0,
  "secondary_event_evidence_count": 0,
  "background_context_count": 0,
  "official_or_primary_present": false,
  "single_source_exception": {
    "allowed": false,
    "reason": null,
    "limits": []
  },
  "augmentation_required": false,
  "required_next_action": null,
  "source_url_urls_sync_status": "PASS | FAIL_SOURCE_URL_NOT_IN_URLS",
  "background_context_misuse_detected": false
}
```

Required status logic:

- `PASS_MULTI_SOURCE`: at least two independent body-level or official/primary sources support the core event/claim.
- `PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION`: a single official/primary/regulatory/filing/primary dataset/report source directly supports all core visible claims.
- `HOLD_NEEDS_SOURCE_AUGMENTATION`: source structure is insufficient but likely repairable through official/primary or independent corroboration search.
- `FAIL_SOURCE_DIVERSITY`: source diversity cannot support the visible claim even after required rescue attempt.

Cards with `source_diversity_status` of `HOLD_NEEDS_SOURCE_AUGMENTATION` or `FAIL_SOURCE_DIVERSITY` must not enter `evidence_complete_and_source_claim_covered[]`.

Cards with `HOLD_NEEDS_SOURCE_AUGMENTATION` must not proceed to content polish or final QC. They may only return after source augmentation, renewed source-diversity review, and explicit PASS status.

Prompt 0.5 summary must include:

```json
"source_diversity_summary": {
  "input_count": 0,
  "pass_multi_source_count": 0,
  "pass_official_or_primary_single_source_exception_count": 0,
  "hold_single_source_caveat_count": 0,
  "hold_needs_source_augmentation_count": 0,
  "fail_source_diversity_count": 0,
  "source_url_urls_sync_fail_count": 0
}
```

## R3C_P03 — Evidence QC V8 mechanical check

> run 20260516_012728 retrospective integrated rule. P0.

0.5 Evidence QC 는 "Source Diversity & Corroboration QC Rule v8" 을 **기계적으로
실행**해야 한다. 결론을 눈으로 보고 "0 issues" 라고 적는 것은 금지 (FACT_DISCIPLINE §9 참조).

- 동반 스크립트: `validation_scripts/evidence_qc_v8_check.py`
- 실행: `python3 validation_scripts/evidence_qc_v8_check.py <cards_or_qc_output.json>`
- 검사 항목:
  - (a) landing-page source_url (host 루트, article 경로 없음) flag
  - (b) fact_sources 의 distinct source_url 수 < entry 수 → fake-diversity flag
  - (c) 1-source 카드는 `single_source_exception` 객체 필수
  - (d) high-signal / safety / market-share / ranking 카드는 2개 독립 body-level
    source 또는 official source 필요
  - (e) visible-source URL sync — fact_sources.source_url ⊆ urls[]
- 스크립트는 **flag 만** 한다. 2nd source 를 조작해 만들지 않는다 — flag 된 항목은
  사람/assistant 가 실제 검증한다.
- flag 가 1건이라도 있으면 0.5 는 PASS 가 아니다.

근거: 1차 시도 0.5 가 generic URL·fake-diversity·single_source_exception 누락이
있는데도 "0 issues" 로 통과 (PV_005, EFP_001, EFP_003). V8 규칙은 있었으나 실행되지 않았다.

## Operational integrated rule — source_url resolution integrity (third verification axis)

This integrated rule adds a THIRD source_url verification axis to Evidence QC: **resolution integrity**. The first two axes already exist — (1) the quote exists at the URL (Test 9 — accessibility / quote verification), and (2) every visible-claim `source_url` is a member of `urls[]` (v8/v9 visible-source URL sync hard gate). Neither verifies that `source_url` is the **full canonical article permalink that resolves to the exact article the quote was extracted from**. That missing axis is the root cause of EFP-01 (truncated `source_url`s that pass the membership gate) and EFP-02 (wrong-article URLs attached by post-0.7 augmentation).

Prompt 0.5 is the **primary owner** of this axis. It runs the full 3-check resolution-integrity test for every `fact_sources[].source_url` that supports a visible field, on every `addable_merge_safe[]` candidate, before that candidate may become `evidence_complete_and_source_claim_covered`.

This axis is **distinct from** the v8/v9 `source_url_urls_sync_status` membership gate (`PASS | FAIL_SOURCE_URL_NOT_IN_URLS`). Membership in `urls[]` does not prove canonical completeness or correct article resolution. A truncated prefix or a generic listing endpoint can be a member of `urls[]` and still fail this axis.

### CHECK 1 — Canonical completeness

For every `fact_sources[].source_url` that supports a visible field, confirm it is the **full article permalink, byte-identical** to the `urls[]` / source-packet entry the quote was extracted from.

HARD-FAIL if `source_url` is:

- (a) a **truncated prefix** of a longer `urls[]` entry (the longer entry shares `source_url` as an exact leading substring), or
- (b) a **generic endpoint with no article identifier** — no numeric id and no slug of 8+ characters. Treat as generic-endpoint failures: `read.do`, `article.html`, `view.php`, `list`, `index`, `board`, or a bare domain root.

### CHECK 2 — Article resolution

Fetch `source_url` (reuse the Test 9 fetch where possible) and confirm the fetched page resolves to the **SAME article that contains `source_quote`** — same headline / actor / event — not a section index, listing page, syndication hub, or a different article.

Record per source: `resolved_article_matches_quote: true|false`.

### CHECK 3 — Prefix-laundering block + propagation

- If `urls[]` contains a longer URL that has `source_url` as an exact prefix, **replace** `source_url` with the full URL and re-run Check 1, Check 2, and Test 9.
- **Propagation rule (the EFP-01 non-propagation fix):** whenever an upstream stage restores or normalizes a `urls[]` entry — 0.4 baseline revalidation, or 0.6 content polish — the corresponding `fact_sources[].source_url` **MUST be overwritten with the full canonical URL in the same pass**. 0.6 previously restored `urls[]` but left `source_url` truncated; that split state is prohibited. If Evidence QC observes a restored/normalized `urls[]` entry whose matching `source_url` is still truncated, treat it as a Check 1 HARD-FAIL and propagate the fix here.

This propagation **EDITS an existing `source_url`** to its full canonical form. It does **not** add a new `fact_sources` entry and is therefore permitted even when source augmentation is not authorized (see Conflict note below). A prefix→full-URL correction is a metadata/identity repair of an already-cited source, not a new source. It must not change `source_quote` text, claim scope, or source direction; mark it `repair_type = source_url_canonicalization`, `source_quote_text_changed = false`, `claim_scope_changed = false`, and record it in `source_change_diff`.

### HARD-FAIL routing

A `source_url` that fails Check 1, Check 2, or Check 3 (and cannot be repaired by in-`urls[]` prefix promotion) routes the card to `addable_hold_source_gap` with the matching `hold_reason_code`. This integrated rule **extends** the `addable_hold_source_gap` `hold_reason_code` enum with the following values (in addition to the existing list ending in `other`):

- `source_url_truncated` — Check 1(a)
- `source_url_generic_endpoint` — Check 1(b)
- `source_url_resolves_to_wrong_article` — Check 2, `resolved_article_matches_quote: false` (different article)
- `source_url_resolves_to_listing` — Check 2, resolved page is a section index / listing / syndication hub

If resolution cannot be determined because the page is inaccessible / paywalled / js-blocked, do not silently pass: route to `review_pool_deferred` (or `needs_source_augmentation` if a better canonical source likely exists), consistent with Test 9 and Test 10.

### Augmentation rule (the EFP-02 fix)

Any source attached by augmentation — **including any post-0.7 augmentation pass** — must pass all three checks above before it may support visible text.

- A `web_search_snippet` URL must **never** be attached as `source_url` without a body fetch confirming `source_quote` appears in the resolved article (Check 2 = true).
- A post-0.7 augmentation that attaches or changes a `source_url` **without re-running this resolution axis AND Evidence QC** is prohibited. When detected, set `publish_ready=false` and route to the file-appropriate return state: `needs_return_to_evidence_qc` and/or `needs_source_augmentation`. This is consistent with `NO_SILENT_DOWNSTREAM_ENRICHMENT_RULE` — an unvalidated later-attached `source_url` is `BLOCKED_SILENT_DOWNSTREAM_ENRICHMENT_ATTEMPT`.

This axis only validates, propagates the full form of, and routes on already-cited sources; it does **not** authorize Prompt 0.5 to add brand-new `fact_sources` without the existing source-augmentation authorization.

### Required output object

Prompt 0.5 JSON output must include, using this EXACT field name so Prompt 0.7 can gate on it:

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

Per supporting source, also record:

- `source_url_canonical_complete: true|false`
- `resolved_article_matches_quote: true|false`
- `source_url_prefix_promoted: true|false` (Check 3 in-`urls[]` promotion applied)
- `source_url_resolution_hold_reason_code`, if HARD-FAIL

A card with any unresolved Check 1 / Check 2 / Check 3 HARD-FAIL on a visible-claim source must NOT enter `evidence_complete_and_source_claim_covered[]`, and must keep `publish_ready: false`.

# 07_PROMPT_0_5_Evidence_QC.md — Source Diversity source-diversity integrated rule

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

## Evidence QC source-diversity hard gate

Recalculate source identity from raw URLs and ownership/syndication evidence.

Hard fails:

1. `fact_sources.length >= 2` but `source_independent_owner_count = 1`;
2. multiple rows from the same canonical URL counted as multiple sources;
3. mirrored, syndicated or same-owner copies counted as independent;
4. `PASS_MULTI_SOURCE` without two independent owners;
5. missing `source_role` or non-specific `source_contribution`;
6. an additional source is present but contributes nothing to visible fields;
7. quote display date is `fetched_at` or `checked_at`;
8. a single-source exception lacks bounded-search evidence and scope limitations.

Required output:

```json
{
  "source_diversity_qc": {
    "source_evidence_entry_count": 0,
    "source_unique_url_count": 0,
    "source_unique_domain_count": 0,
    "source_independent_owner_count": 0,
    "same_url_row_inflation_count": 0,
    "syndication_inflation_count": 0,
    "source_role_coverage": {},
    "source_contribution_coverage": "PASS|FAIL",
    "source_synthesis_coverage": "PASS|FAIL",
    "visible_source_date_check": "PASS|FAIL",
    "single_source_exception_check": "PASS|FAIL|NOT_APPLICABLE"
  }
}
```

Default pass requires `source_independent_owner_count >= 2`. Otherwise route to
`needs_source_augmentation[]`, except for a separately approved narrow exception.

Required blockers:

```text
BLOCKED_FALSE_MULTI_SOURCE
BLOCKED_SOURCE_DIVERSITY_OR_SYNTHESIS_GAP
BLOCKED_VISIBLE_QUOTE_DATE_USES_FETCH_DATE
```

    Stop after Evidence QC. Do not assign publish_ready.

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


## Evidence QC extra

Evidence QC must check single-source waiver validity and stale blocker conflicts before any card can proceed to content polish.
