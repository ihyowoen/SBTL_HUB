<!-- REPLACE_ALL_CLEAN_VERSION: LLM_PROMPT_GITHUB_CANONICAL_V1_SOURCE_DIVERSITY_IB_CODEX -->
<!-- Generated KST: 2026-07-08T21:33:49.790191+09:00 -->
<!-- This file is a full clean replacement file. It is not a patch stub. -->

Prompt 0.7v — Reusable Default / Replace All / Final Publish-Readiness QC

Proceed to final publish-readiness QC only.

Use the current run’s content enrichment and language/terminology polish output as the only candidate input universe for this step.

This step starts after content enrichment and language/terminology polish.

Do not continue from, trust, import, integrated rule, or reuse any previous final, PR candidate, GitHub-ready, publish-ready, or manually integrated outputs unless the user explicitly declares them as current-run authoritative inputs.

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
- no final QC work performed

Do not infer replacement rules from memory.
Do not use archived docs.
Do not use branch-only docs.
Do not use local snippets unless the user explicitly provides them as current-run authoritative docs.

Input files:

- Content polish JSON: {{CONTENT_POLISH_RESULTS_JSON}}
- Content-enriched payload: {{CONTENT_ENRICHED_LANGUAGE_POLISHED_PENDING_FINAL_QC_JSON}}
- Content polish hold manifest: {{CONTENT_POLISH_HOLD_MANIFEST_JSON}}
- Evidence QC JSON: {{EVIDENCE_QC_RESULTS_JSON}}
- Source-claim coverage map: {{SOURCE_CLAIM_COVERAGE_MAP_JSON}}
- Baseline revalidation JSON: {{BASELINE_REVALIDATION_JSON}}
- Stage C JSON: {{STAGE_C_RESULTS_JSON}}
- Active baseline cards: {{BASELINE_CARDS_SOURCE}}
- Baseline source declaration: {{BASELINE_SOURCE_DECLARATION}}
- Run tag: {{RUN_TAG}}
- Run label: {{RUN_LABEL_KST}}

Required input rule:

This step requires a valid content polish output from the same run.

The content polish JSON must include:

- required_docs_check
- run_tag
- run_label
- evidence_complete_and_source_claim_covered_input_count
- content_enriched_and_language_polished[]
- content_hold_claim_narrowing_needed[]
- content_hold_language_issue[]
- content_hold_schema_issue[]
- needs_return_to_evidence_qc[]
- review_pool_deferred[]
- visible_field_change_log[]
- content_polish_accounting_matches_input_count

If content polish JSON is missing, invalid, incomplete, not from the same run, or has accounting mismatch, stop and report:

- status: BLOCKED_CONTENT_POLISH_INVALID
- reason: [...]
- no final QC work performed


## Upstream lineage integrity gate

This prompt is downstream of selector, evidence, content, and/or production gates. It must not repair or launder an invalid upstream lineage.

Before doing any work, validate that the current-run content enrichment output carries a lineage integrity statement from the immediately previous step.

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


For Prompt 0.7 specifically, content enrichment is the last visible-field rewrite checkpoint. It must prove that:
- every candidate has content_enriched_and_language_polished state
- evidence_complete and source_claim_covered remain true after visible-field rewriting
- format-risk / execution-anchor metadata was preserved or explicitly marked not_applicable
- no source-locked claim was expanded beyond the evidence universe

If any required lineage field is missing, false, contradictory, stale, not from the same run, or inconsistent with the candidate payload, stop immediately and report:

- status: BLOCKED_UPSTREAM_LINEAGE_INVALID
- reason: [...]
- invalid_or_missing_lineage_fields: [...]
- no final publish-readiness QC performed

Do not infer lineage validity from memory.
Do not continue just because candidate counts look correct.
Do not use this prompt to fix Stage A/B/C selection defects or post-QC evidence defects.

Candidate input rule:

Only content_enriched_and_language_polished[] may enter final publish-readiness QC.

Do not include:

- content_hold_claim_narrowing_needed
- content_hold_language_issue
- content_hold_schema_issue
- needs_return_to_evidence_qc
- review_pool_deferred
- addable_hold_source_gap
- addable_hold_claim_gap
- needs_source_augmentation
- evidence_qc_rejected
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

If any non-content_enriched_and_language_polished item is mixed into the candidate input, exclude it and report it as mixed_input_excluded.


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


Final QC execution-anchor publish gate:

A card may receive publish_ready=true only if final QC confirms that any Stage A format-risk / execution-anchor risk was resolved with source-backed evidence.

Hard fail for publish_ready:

- missing strict_pass_gate / strict_gate_check metadata
- Stage A selector validity not PASS
- artifact consistency not PASS
- format-risk card has no execution_anchor_type or no source-backed execution anchor
- execution anchor was inflated in title, sub, gate, fact, or implication
- card entered the pipeline from review_pool, support_source_only, rejected, duplicate_hold, existing_reinforcement, or any non-addable state without an explicit authorized reopen

If any hard fail is present, route to final_qc_hold or needs_return_to_evidence_qc. Do not set publish_ready=true.

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

This step decides only final publish-readiness for already content-enriched and language-polished cards.

This step may assign:

- publish_ready
- final_qc_hold
- final_qc_rejected
- needs_return_to_evidence_qc
- needs_return_to_content_polish
- needs_github_main_sync
- review_pool_deferred

This step may produce:

- publish_ready_payload
- final_qc_report
- final_hold_manifest
- final_cards_candidate_PENDING_GITHUB_SYNC, only if baseline is not confirmed as GitHub main

This step must not:

- create new cards
- promote held cards
- rescue rejected/revise_required/deferred items
- silently add sources
- silently rewrite visible fields
- silently alter fact_sources
- force expected final count
- call a file GitHub-ready unless GitHub main sync gate passes
- call a file PR_CANDIDATE unless publish_ready and GitHub main sync gate pass

State ladder reminder:

accepted_fact_safe
→ addable_merge_safe
→ evidence_complete
→ source_claim_covered
→ content_enriched
→ language_terminology_polished
→ publish_ready

Only this step may assign publish_ready=true.

Publish_ready may be assigned only when all final gates pass.

Final publish gates:

Gate 1 — Fact Safety

PASS only if:

- every core visible claim is supported by fact_sources
- every number/date/entity/project/stage claim is source-supported
- no unsupported causal claim exists
- no unsupported benefit claim exists
- no unsupported company intention exists
- no unsupported market impact claim exists
- no memory-based claim exists
- fact and implication are separated

Gate 2 — Merge Safety

PASS only if:

- candidate came from addable_merge_safe
- duplicate ID check passes
- duplicate URL/canonical URL check passes
- duplicate event fingerprint check passes
- baseline duplicate event check passes
- internal batch duplicate check passes
- expected final count is not forced
- duplicate/hold/reinforcement items are not mixed in

Gate 3 — Evidence Completeness

PASS only if:

- evidence_complete=true
- source_claim_covered=true
- source_quote exists for every core source
- source_quote is body-level or official/document material
- source_quote is not headline-only
- source_quote is not snippet-only
- source_quote is not RSS-only
- source_quote is not listing-title only
- source_quote_status is usable
- fact_sources are not URL-only
- source_name exists
- evidence_role exists
- supports exists
- single-source exception is valid, if applicable

Gate 4 — Claim Coverage

PASS only if:

- title core claim is covered
- sub core claim is covered
- fact core claims are covered
- numeric/date claims are covered
- causal/stage/timeline claims are covered or removed
- implication factual dependencies are covered
- no weak/missing core coverage remains

Gate 5 — Content Depth

PASS only if:

- content_enriched=true
- title is specific and source-locked
- sub is exactly one sentence
- gate is 2–3 sentences and strategically useful
- fact has at least 2 source-backed sentences
- implication has at least 2 items
- card reads as SBTL_HUB strategic intelligence, not raw article summary
- no unsupported enrichment was introduced

Gate 6 — Language & Tone

PASS only if:

- language_terminology_polished=true
- raw Chinese/Japanese visible residue is zero
- raw foreign article headline residue is zero
- units are normalized
- company/institution names are consistent
- banned workflow/meta phrases are zero
- hype/promotional tone is zero
- forced SBTL benefit claims are zero
- terminology is suitable for external-facing newsletter/app use

Gate 7 — Schema / Type / Runtime Safety

PASS only if:

- full schema required fields exist
- field types are valid
- implication is array with 2+ items
- urls is array
- related is array
- fact_sources is array
- date format is valid
- region is one of KR / US / CN / JP / EU / GL
- cat is one of locked categories
- signal is top / high / mid
- no schema/type drift
- JSON is valid

Gate 8 — Sort / ID / Baseline Sync

PASS only if:

- latest-first sort is verified or can be applied deterministically
- ID collision is zero
- URL collision is zero
- canonical URL collision is zero
- event fingerprint duplicate is zero
- baseline source declaration is clear
- if baseline is GitHub main, GitHub main sync gate is confirmed
- if baseline is not GitHub main, output must be marked needs_github_main_sync and must not be called GitHub-ready or PR_CANDIDATE

Gate 9 — Output Integrity

PASS only if:

- no rejected/revise_required/hold/deferred/non-accepted cards are mixed into publish_ready output
- all candidate input items appear exactly once in final QC decision ledger
- hard-fail count is zero for publish_ready items
- QC report supports the final decision
- no expected-count forcing occurred

Web search / fetch boundary:

Final QC may use web search/fetch only for verification.

Allowed purposes:

- verify source access
- verify quote status
- verify duplicate/canonical URL conflict
- verify baseline/event conflict
- verify source contradiction
- verify official source if already cited or required to resolve a conflict

Prohibited purposes:

- discovering new card candidates
- expanding card scope
- adding new facts
- adding new sources silently
- rewriting visible fields
- rescuing held/rejected cards
- forcing publish_ready count
- creating PR_CANDIDATE before GitHub main sync gate

If new evidence is needed, do not add it silently.

Mark:

- needs_return_to_evidence_qc
- recommended_next_action: source_augmentation_or_evidence_qc_rerun

Content handling:

Do not rewrite visible fields in final QC by default.

Final QC is validation, not enrichment.

If visible-field issue is discovered:

- mark needs_return_to_content_polish
- do not silently integrated rule unless the user explicitly authorizes a final micro-fix pass

Source handling:

Do not modify fact_sources in final QC by default.

If source issue is discovered:

- mark needs_return_to_evidence_qc
- do not silently integrated rule unless the user explicitly authorizes source augmentation / source fix

Publish-ready assignment rule:

A card may receive publish_ready=true only if:

- state entering this step = content_enriched_and_language_polished
- previous required states are true:
  - evidence_complete=true
  - source_claim_covered=true
  - content_enriched=true
  - language_terminology_polished=true
- all final gates PASS
- hard_fail_count=0
- no unresolved GitHub main sync issue prevents PR/GitHub-ready naming

If baseline is not GitHub main:

- publish_ready may be assigned for content/data quality
- but GitHub-ready and PR_CANDIDATE must not be assigned
- output must state github_main_sync_required_later=true

Output state definitions:

1. publish_ready

Use only when all final gates pass.

Every publish_ready item must include:

- state: publish_ready
- previous_state: content_enriched_and_language_polished
- evidence_complete: true
- source_claim_covered: true
- content_enriched: true
- language_terminology_polished: true
- publish_ready: true
- github_ready: true/false
- pr_candidate_ready: true/false
- github_main_sync_required_later: true/false
- final_qc_gates
- hard_fail_count: 0

2. final_qc_hold

Use when:

- card is close but one or more final gates fail
- issue is likely fixable
- card should not publish yet

3. final_qc_rejected

Use when:

- final QC reveals fatal issue
- card should be removed from current run
- source/evidence/fact/schema issue cannot be repaired in this run

4. needs_return_to_evidence_qc

Use when:

- source/fact/claim coverage issue is discovered
- source_quote/fact_sources issue is discovered
- new source augmentation is needed
- evidence_complete/source_claim_covered appears invalid

5. needs_return_to_content_polish

Use when:

- visible-field language/content issue remains
- banned phrase remains
- claim needs narrowing
- tone/terminology is not publishable
- content depth is insufficient

6. needs_github_main_sync

Use when:

- baseline was not GitHub main
- GitHub main changed after baseline was declared
- final candidate cannot be called GitHub-ready until main sync revalidation

7. review_pool_deferred

Use when:

- final decision cannot be safely made
- manual editorial/user decision is required

Accounting rule:

Every content_enriched_and_language_polished item must appear exactly once in one of:

- publish_ready
- final_qc_hold
- final_qc_rejected
- needs_return_to_evidence_qc
- needs_return_to_content_polish
- needs_github_main_sync
- review_pool_deferred

No silent skip is allowed.

Report:

- content_enriched_and_language_polished_input_count
- publish_ready_count
- final_qc_hold_count
- final_qc_rejected_count
- needs_return_to_evidence_qc_count
- needs_return_to_content_polish_count
- needs_github_main_sync_count
- review_pool_deferred_count
- outcome_total_count
- final_qc_accounting_matches_input_count

If accounting does not match, mark output invalid and report:

- status: BLOCKED_FINAL_QC_ACCOUNTING_MISMATCH

Output files:

Allowed filenames if GitHub main sync is confirmed:

1. publish_ready_payload_{{RUN_TAG}}.json
2. final_publish_readiness_qc_report_{{RUN_TAG}}.md
3. final_publish_readiness_qc_decisions_{{RUN_TAG}}.csv
4. final_hold_manifest_{{RUN_TAG}}.json
5. pr_candidate_payload_{{RUN_TAG}}.json, only if publish_ready_count > 0 and GitHub main sync gate passed

Allowed filenames if GitHub main sync is not confirmed:

1. publish_ready_payload_PENDING_GITHUB_SYNC_{{RUN_TAG}}.json
2. final_publish_readiness_qc_report_{{RUN_TAG}}.md
3. final_publish_readiness_qc_decisions_{{RUN_TAG}}.csv
4. final_hold_manifest_{{RUN_TAG}}.json
5. github_sync_required_manifest_{{RUN_TAG}}.json

Do not use PR_CANDIDATE, GitHub-ready, or merge-ready filenames unless GitHub main sync gate has passed.

JSON output requirements:

The main JSON must include:

- stage
- run_tag
- run_label
- input_content_polish_file
- input_content_enriched_payload_file
- baseline_file
- baseline_source_declaration
- baseline_count
- github_main_sync_required_later
- github_main_sync_status
- required_docs_check
  - docs_expected
  - docs_read_from_github_main
  - docs_missing_or_unreadable
  - status
- content_enriched_and_language_polished_input_count
- mixed_input_excluded_count
- publish_ready_count
- final_qc_hold_count
- final_qc_rejected_count
- needs_return_to_evidence_qc_count
- needs_return_to_content_polish_count
- needs_github_main_sync_count
- review_pool_deferred_count
- outcome_total_count
- final_qc_accounting_matches_input_count
- final_gate_summary
- hard_fail_summary
- schema_runtime_summary
- duplicate_id_url_event_summary
- language_tone_summary
- publish_ready[]
- final_qc_hold[]
- final_qc_rejected[]
- needs_return_to_evidence_qc[]
- needs_return_to_content_polish[]
- needs_github_main_sync[]
- review_pool_deferred[]
- mixed_input_excluded[]
- decision_ledger[]

Each publish_ready item must include:

- state: publish_ready
- previous_state: content_enriched_and_language_polished
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
- publish_ready: true
- github_ready
- pr_candidate_ready
- github_main_sync_required_later
- final_qc_gates
  - fact_safety
  - merge_safety
  - evidence_completeness
  - claim_coverage
  - content_depth
  - language_tone
  - schema_runtime
  - sort_id_baseline_sync
  - output_integrity
- hard_fail_count
- final_qc_notes

Each final_qc_hold item must include:

- state: final_qc_hold
- previous_state: content_enriched_and_language_polished
- draft_id
- source_spec_id
- failed_gates
- hold_reason_code
- hold_reason_detail
- affected_fields
- required_fix
- recommended_next_action

Allowed hold_reason_code values:

- fact_safety_gap
- merge_safety_gap
- evidence_completeness_gap
- claim_coverage_gap
- content_depth_gap
- language_tone_gap
- schema_runtime_gap
- sort_id_baseline_sync_gap
- output_integrity_gap
- other

Each final_qc_rejected item must include:

- state: final_qc_rejected
- previous_state: content_enriched_and_language_polished
- draft_id
- source_spec_id
- rejection_reason_code
- rejection_reason_detail
- failed_gates
- fatal_issue
- recommended_next_action

Allowed rejection_reason_code values:

- unsupported_core_fact_discovered
- source_quote_hard_fail_discovered
- duplicate_event_discovered
- schema_unrepairable
- non_publishable_language_or_claim
- source_conflict_unresolved
- baseline_conflict_unresolved
- other

Each needs_return_to_evidence_qc item must include:

- state: needs_return_to_evidence_qc
- previous_state: content_enriched_and_language_polished
- draft_id
- source_spec_id
- evidence_issue
- affected_claims
- required_evidence_qc_action
- recommended_next_action

Each needs_return_to_content_polish item must include:

- state: needs_return_to_content_polish
- previous_state: content_enriched_and_language_polished
- draft_id
- source_spec_id
- content_or_language_issue
- affected_visible_fields
- required_content_polish_action
- recommended_next_action

Each needs_github_main_sync item must include:

- state: needs_github_main_sync
- previous_state: content_enriched_and_language_polished
- draft_id
- source_spec_id
- reason
- baseline_source_declaration
- required_sync_action
- not_github_ready: true

Each review_pool_deferred item must include:

- state: review_pool_deferred
- previous_state: content_enriched_and_language_polished
- draft_id
- source_spec_id
- defer_reason
- unresolved_questions
- required_manual_checks
- recommended_next_action
- not_publish_ready: true

Each decision_ledger row must include:

- draft_id
- source_spec_id
- prior_state
- final_qc_outcome
- publish_ready
- github_ready
- pr_candidate_ready
- failed_gates
- hard_fail_count
- reason
- notes

Hard-fail summary must count:

- unsupported_core_claim
- source_quote_missing
- source_quote_headline_only
- source_quote_snippet_only
- source_quote_rss_only
- source_quote_listing_only
- source_quote_status_fail
- fact_sources_url_only
- missing_source_name
- missing_evidence_role
- missing_supports
- unsupported_numeric_claim
- unsupported_causal_claim
- unsupported_timeline_claim
- duplicate_id
- duplicate_url
- duplicate_canonical_url
- duplicate_event_fingerprint
- rejected_or_hold_mixed_in
- schema_type_drift
- foreign_language_residue
- banned_phrase_remaining
- forced_sbtl_claim
- publish_ready_true_despite_hard_fail

Report requirements:

The Markdown report must include:

1. Run metadata

   - content polish input file
   - content-enriched payload file
   - baseline file/source
   - baseline source declaration
   - baseline count
   - GitHub main sync status
   - run tag
   - run label
   - content_enriched_and_language_polished input count

2. Required docs check

   - list all 8 required docs
   - confirm each was read from GitHub main
   - if any doc was not read, this step must not proceed

3. Method

   - content_enriched_and_language_polished-only confirmation
   - mixed input exclusion confirmation
   - final gate checklist
   - no silent source augmentation confirmation
   - no silent visible-field rewrite confirmation
   - GitHub main sync gate status
   - expected final count not forced confirmation

4. Summary table

   - input count
   - publish_ready count
   - final_qc_hold count
   - final_qc_rejected count
   - needs_return_to_evidence_qc count
   - needs_return_to_content_polish count
   - needs_github_main_sync count
   - review_pool_deferred count
   - mixed_input_excluded count
   - outcome total count
   - accounting match: yes/no

5. Publish-ready manifest

   For each publish_ready item:
   - draft_id
   - source_spec_id
   - short event anchor
   - region / cat / signal
   - all gate result summary
   - hard-fail count
   - GitHub-ready status
   - PR candidate status

6. Hold/reject/return manifest

   Include:
   - final_qc_hold
   - final_qc_rejected
   - needs_return_to_evidence_qc
   - needs_return_to_content_polish
   - needs_github_main_sync
   - review_pool_deferred

   For each item:
   - draft_id
   - failed gate
   - reason
   - required fix
   - recommended next action

7. Final gate summary

   Include counts for PASS/FAIL:
   - Gate 1 Fact Safety
   - Gate 2 Merge Safety
   - Gate 3 Evidence Completeness
   - Gate 4 Claim Coverage
   - Gate 5 Content Depth
   - Gate 6 Language & Tone
   - Gate 7 Schema / Runtime Safety
   - Gate 8 Sort / ID / Baseline Sync
   - Gate 9 Output Integrity

8. Hard-fail summary

   Include every hard-fail count.
   If any hard-fail count is non-zero among publish_ready items, final QC must FAIL.

9. GitHub sync statement

   If baseline source declaration is github_main and sync is confirmed:

   “GitHub main sync gate is confirmed for this final QC output.”

   If not confirmed:

   “GitHub main sync gate is not confirmed. This output may be content publish-ready but is not GitHub-ready or PR_CANDIDATE.”

10. Explicit boundary statement

   Include this exact statement:

   “Final publish-readiness QC decided publish_ready status only. GitHub-ready or PR_CANDIDATE status was assigned only if GitHub main sync gate passed. No new candidates were added, no held/rejected cards were rescued, and no expected final count was forced.”

11. Next-step statement

   If publish_ready_count > 0 and GitHub main sync gate passed, include:

   “The next step is GitHub merge preparation using only publish_ready cards.”

   If publish_ready_count > 0 but GitHub main sync gate did not pass, include:

   “The next step is GitHub main sync and revalidation before PR or merge preparation.”

   If publish_ready_count = 0, include:

   “No cards are publish-ready. Do not prepare a PR candidate from this run.”

## Operational integrated rule — final QC upstream-lineage publish gate

Final publish-readiness QC is the last data-quality gate before GitHub merge preparation. It must fail any candidate whose upstream selection lineage is missing or unresolved.

Before assigning `publish_ready=true`, verify for every candidate:

- Stage A strict-gate lineage is present and passed;
- Stage B source verification lineage is present and passed;
- Stage C strict-gate acceptance guard is present and passed;
- Baseline revalidation lineage guard is present and passed;
- Evidence QC lineage guard is present and passed;
- Content polish lineage guard is present and passed;
- no unresolved `selection_defect`, `artifact_mismatch`, `execution_anchor_gap`, `source_direction_reversal`, `staleness_gap_unresolved`, or `baseline_increment_unclear` remains.

For candidates with `format_risk_tags`, final QC must explicitly confirm that the visible `title`, `sub`, `gate`, `fact`, and `implication` do not overstate the verified execution anchor.

If a candidate lacks the required upstream-lineage proof, classify it as:

- `final_qc_hold_selection_lineage_gap`, or
- `final_qc_hold_execution_anchor_gap`

Do not mark it `publish_ready`.

If any candidate is marked `publish_ready=true` despite missing/failed lineage, final QC status must be:

```json
{
  "status": "FAIL_UPSTREAM_LINEAGE_HARD_FAIL",
  "publish_ready_true_despite_lineage_fail_count": "nonzero"
}
```

This guard is independent of evidence completeness. A card can have complete evidence and still fail final QC if its upstream selection lineage is invalid.

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

## Operational integrated rule — final QC next-call recommendation

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

1. If publish_ready_count > 0 and GitHub main sync gate passed:
   - recommended_next_call = "GitHub merge prep"
   - recommended_prompt_id = "Prompt 0.8"
   - recommended_input_universe = "publish_ready[] only"

2. If publish_ready_count > 0 but GitHub main sync gate did not pass:
   - recommended_next_call = "GitHub main sync and revalidation before PR or merge preparation"
   - recommended_prompt_id = "Prompt 0.8 after sync issue is resolved"

3. If publish_ready_count = 0:
   - recommended_next_call = "retrospective or resolve holds"
   - recommended_prompt_id = "Prompt 1.1 or relevant return step"

Do not proceed automatically to GitHub merge preparation.
Stop after final publish-readiness QC.

Do not proceed to GitHub merge preparation until I explicitly say “GitHub merge prep” or “PR prep”.

---

## Execution-anchor and selector-lineage safety overlay — 2026-05-05

This overlay is downstream of the Stage A safe-selector integrated rule. It prevents post-acceptance steps from laundering a weak or superseded Stage A/B/C lineage into publish-ready or production status.

Terminology lock:

- Do not use or enforce a format-based hard-exclude rule.
- Product, demo, PoC, component, interview, commentary, roundup, speech, or personnel formats are not automatically rejected by format alone.
- They are subject to a strict-pass presumption block: without a concrete fresh execution anchor, they must not have entered `strict_passed_spec[]`; if they did, the downstream step must hold, reject, or return the item to the appropriate prior stage rather than polishing it forward.
- Concrete execution anchors include signed contract, binding customer order, offtake, commercial deployment, field installation, commissioning, production start, facility opening, certification, regulatory decision, public funding approval, binding procurement, measurable capacity addition, safety recall/regulatory action, or named customer adoption.

### Required upstream lineage gate for Final QC

Before final publish-readiness QC begins, verify that `CONTENT_POLISH_RESULTS_JSON` includes:

- a passed Evidence QC lineage declaration
- a passed execution-anchor QC summary
- `lineage_and_anchor_guard.evidence_qc_lineage_passed: true`
- `lineage_and_anchor_guard.execution_anchor_qc_passed: true`
- content polish accounting matches input

If missing or failed, stop and report:

```text
status: BLOCKED_CONTENT_POLISH_LINEAGE_OR_ANCHOR_INVALID
reason: [...]
no final QC work performed
```

### Publish-ready hard gate for format-risk items

A card with `format_risk_tags`, `execution_anchor_type`, or an execution/deployment implication may receive `publish_ready=true` only if Final QC confirms all of the following:

1. the execution anchor is explicitly covered by `fact_sources` and `source_claim_coverage_map`;
2. the visible fields do not overstate stage, scale, causality, market effect, or commercialization;
3. the card retains any necessary caveat when the event is pilot, demo, PoC, early deployment, or review-stage policy;
4. no selector-lineage defect is unresolved.

If any condition fails, put the card in `final_qc_hold` or `needs_return_to_evidence_qc`; do not assign `publish_ready=true`.

### Output requirement

Add to Final QC JSON:

```json
"selector_lineage_final_gate": {
  "upstream_lineage_passed": true,
  "artifact_consistency_passed": true,
  "superseded_lineage_detected": false,
  "format_risk_publish_ready_checked_count": 0,
  "format_risk_publish_ready_blocked_count": 0
}
```

Final override: if `selector_lineage_final_gate.upstream_lineage_passed != true`, `publish_ready_count` must be 0 and the next recommended call must not be Prompt 0.8.

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

## Prompt 0.7 final gate — claim diversity

Before assigning `publish_ready`, Prompt 0.7 must validate the 0.6 `card_claim_diversity_audit[]`.

Required final QC fields:

- `claim_diversity_gate_status`: `PASS | PASS_WITH_WARNINGS | BLOCKED_CARD_CLAIM_DIVERSITY_AUDIT_MISSING | BLOCKED_CLAIM_OVERLAP_REQUIRES_REPOSITIONING`
- `claim_type_distribution`
- `high_overlap_cards[]`
- `accepted_overlap_cards[]`
- `claim_overlap_accepted_reasons[]`
- `claim_diversity_hard_fail_count`

Final QC may pass with warnings only when:
- overlap remains but is source-locked and honestly documented, or
- source-safe repositioning is not possible without unsupported claims.

Final QC must block when:
- `card_claim_diversity_audit[]` is missing or incomplete,
- high overlap remains and source-safe repositioning was possible but not attempted,
- visible fields claim a distinct strategic angle that is not supported by validated evidence.

This gate does not authorize source augmentation or visible-field rewriting. If repositioning is needed, return to Prompt 0.6.



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


## Prompt 0.7 Gate 8 — Source Diversity / Corroboration

Final QC must include a hard gate for source diversity and corroboration.

Required gate field:

```json
"source_diversity_gate_status": "PASS | PASS_WITH_HOLD_NEEDS_SOURCE_AUGMENTATION | BLOCKED_SOURCE_DIVERSITY_INSUFFICIENT | BLOCKED_SOURCE_URL_URLS_SYNC_FAIL"
```

PASS conditions:

- `source_diversity_status` is `PASS_MULTI_SOURCE`, or
- `source_diversity_status` is `PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION`, or
- `source_diversity_status` is `HOLD_NEEDS_SOURCE_AUGMENTATION` with a valid single-source exception/caveat and narrowed visible claims.

Hard blocks:

- `source_diversity_required=true` and `augmentation_required=true`
- `source_diversity_status` is `HOLD_NEEDS_SOURCE_AUGMENTATION` or `FAIL_SOURCE_DIVERSITY`
- `fact_sources[].source_url` supporting visible claims is missing from `urls[]`
- background/context sources are used as core event support
- source diversity caveat conflicts with visible claim strength

If blocked, route to:

- `needs_return_to_evidence_qc[]` when additional evidence/source augmentation is needed
- `needs_return_to_content_polish[]` when narrowing visible fields can align claim strength with available sources

0.7 must not repair source diversity itself.

## Prompt 0.7 final gate — source_url resolution integrity (mirror gate)

> Mirror hard-gate. The existing visible-source URL sync gates
> (`SOURCE_DIVERSITY_AND_CORROBORATION_QC_RULE_20260507_V8` line "Visible-source URL sync is a hard gate…",
> the V9 restatement, and `source_diversity_gate_status` block
> `fact_sources[].source_url` missing from `urls[]`) are **membership-only**.
> A truncated or generic `source_url` that is byte-identical in both `source_url`
> and `urls[]` passes all of them. This gate adds the missing third axis:
> the `source_url` must be the full canonical article permalink that **resolves**
> to the same article the quote was extracted from. Root cause of EFP-01
> (24 truncated source_urls) and EFP-02 (2 wrong-article URLs via post-0.7 augmentation).

This gate does not repair sources and does not rewrite visible fields. Like the
source-diversity gate, 0.7 only **validates** and routes; it never augments.

### Required upstream object

Final QC must require, for every candidate carrying a `fact_sources[].source_url`
that supports a visible field (`title`, `sub`, `gate`, `fact`, `implication`), the
upstream-produced object `source_url_resolution_summary`:

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

Each verified source must also carry `resolved_article_matches_quote: true|false`.

### Three checks mirrored at Final QC

1. **Canonical completeness** — each visible-claim `source_url` is the full article
   permalink, byte-identical to the `urls[]` entry the quote was extracted from.
   HARD-FAIL if it is (a) a truncated prefix of a longer `urls[]` entry, or
   (b) a generic endpoint with no article identifier (numeric id or 8+ char slug):
   `read.do`, `article.html`, `view.php`, `list`, `index`, `board`, or a bare domain root.
2. **Article resolution** — `resolved_article_matches_quote` must be `true`: fetching
   `source_url` resolves to the SAME article (same headline/actor/event) that contains
   `source_quote`, not a section index, listing page, syndication hub, or a different article.
3. **Prefix-laundering block + propagation** — if `urls[]` contains a longer URL that has
   `source_url` as a prefix, the upstream pass must have replaced `source_url` with the full
   URL and re-verified. Whenever an upstream stage (0.4 baseline revalidation, 0.6 content
   polish) restored or normalized a `urls[]` entry, the corresponding
   `fact_sources[].source_url` must have been overwritten with the full canonical URL in the
   same pass. If 0.7 detects a `urls[]` entry that is a strict superset of a still-truncated
   `source_url`, this is the EFP-01 non-propagation defect — do not mark `publish_ready`.

### Gate field (mirrors `source_diversity_gate_status`)

```json
"source_url_resolution_gate_status": "PASS | PASS_WITH_HOLD_NEEDS_SOURCE_AUGMENTATION | BLOCKED_SOURCE_URL_RESOLUTION_FAIL"
```

**PASS** only when `source_url_resolution_summary` is present AND
`generic_endpoint_failed = 0` AND `wrong_article_failed = 0` AND
`resolves_to_listing_failed = 0` AND every truncated prefix detected was already
propagated/fixed upstream (`truncated_prefix_fixed` accounts for them and none remain),
AND every checked source has `resolved_article_matches_quote: true`.

**BLOCKED_SOURCE_URL_RESOLUTION_FAIL** when any of the following holds:

- `source_url_resolution_summary` is missing for a candidate whose visible fields rely on `source_url` (and the item is not otherwise held);
- any `*_failed` count is non-zero;
- a still-truncated `source_url` remains while a longer superset URL exists in `urls[]` (non-propagation);
- any visible-claim source has `resolved_article_matches_quote: false`.

A blocked item must not receive `publish_ready=true`. Route it to:

- `needs_return_to_evidence_qc[]` (or `needs_source_augmentation`) with one
  `hold_reason_code` from:
  `{ source_url_truncated, source_url_generic_endpoint, source_url_resolves_to_wrong_article, source_url_resolves_to_listing }`,
  when the correct canonical URL must be fetched/restored or corroboration re-run; or
- the Final-QC source-gap hold `final_qc_hold` when the fix is a known propagation of an
  already-restored `urls[]` entry that 0.7 is not authorized to edit. (Do NOT route 0.7
  output to `addable_hold_source_gap` — that is an upstream Evidence-QC bucket that 0.7
  explicitly excludes from Final-QC input; 0.7's own route-back states are `final_qc_hold`,
  `needs_return_to_evidence_qc`, `needs_return_to_content_polish`, `needs_source_augmentation`,
  `review_pool_deferred`.)

This is independent of the existing `source_diversity_gate_status`. A card can pass
source diversity and the `urls[]` membership sync gate and still BLOCK here because its
`source_url` does not resolve to the quote's article.

### Post-0.7 augmentation prohibition (EFP-02)

Any source attached or changed by augmentation — **including any post-0.7
augmentation pass** — must pass all three checks above before it may support
visible text:

- A `web_search_snippet` URL must never become `source_url` without a body fetch
  confirming `source_quote` appears in the resolved article
  (`resolved_article_matches_quote: true`).
- A post-0.7 augmentation that attaches or changes a `source_url` without re-running
  this resolution axis **and** Evidence QC is prohibited. If detected, set
  `publish_ready=false` and route to `needs_return_to_evidence_qc` /
  `needs_source_augmentation`; the item must re-enter Evidence QC and Final QC before
  it can be `publish_ready` again.

This prohibition EDITS/validates an existing `source_url`; it does not authorize 0.7
to add a new `fact_sources` entry. Propagating a restored `urls[]` value into an
existing `source_url` is a value overwrite, not a new source — consistent with the
"do not silently add sources" rule.

### Final override

If `source_url_resolution_gate_status` is `BLOCKED_SOURCE_URL_RESOLUTION_FAIL` for any
candidate, that candidate's `publish_ready` must be false and it must appear in a
route-back state. Final QC accounting and `decision_ledger[]` must still list every
such item exactly once.

## R3C_P06 — Content audit gate (0.7)

> run 20260516_012728 retrospective integrated rule. P1.

0.7 Final QC 는 0.6 의 `card_claim_diversity_audit[]` 와 `related_coverage_audit[]`
존재를 **하드 게이트**로 검사한다:

- 둘 중 하나라도 없거나 비어 있으면 `publish_ready` 를 부여하지 않는다 (BLOCKED).
- 카드 중 `related_coverage_audit[]` 에 entry 가 없는 카드가 있으면 BLOCKED.
- 동반 스크립트: `validation_scripts/content_audit_check.py` (0.6 와 공용).
- 실행: `python3 validation_scripts/content_audit_check.py <content_output.json>`

근거: run 20260516_012728 retrospective R3C_P06.

# 09_PROMPT_0_7_Final_QC.md — Source Diversity source-diversity integrated rule

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

## Final QC — publish-ready source-diversity gate

A card may receive `publish_ready=true` only when all are true:

```text
source_diversity_status = PASS_MULTI_DOMAIN_SYNTHESIS
source_independent_owner_count >= 2
source_synthesis_applied = true
source_synthesis_fields is non-empty
source_contribution coverage = PASS
visible quote date = article publication date
same-source UI grouping metadata = PASS
```

The only alternative is a fully validated narrow single-source exception.

Final QC must reject source-row inflation:

- multiple claims from one source may remain for traceability;
- those claims count as one source;
- UI-facing metadata must express `출처 N곳 · 근거 M개`;
- the original-link action appears once per canonical source group.

Required final summary fields:

```json
{
  "false_multi_source_count": 0,
  "single_domain_publish_ready_count": 0,
  "single_source_exception_publish_ready_count": 0,
  "same_url_grouping_ready_count": 0,
  "visible_quote_publication_date_ready_count": 0
}
```

Any nonzero false-multi-source or unapproved single-domain count blocks the entire publish-ready
payload.

    Stop after Final QC. GitHub merge preparation requires a separate authorized call.

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


## Final QC extra

Final QC must hard-block publish-ready cards with active blockers or invalid single-source waiver metadata.
