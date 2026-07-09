<!-- REPLACE_ALL_CLEAN_VERSION: LLM_PROMPT_GITHUB_CANONICAL_V1_SOURCE_DIVERSITY_IB_CODEX -->
<!-- Generated KST: 2026-07-08T21:33:49.790191+09:00 -->
<!-- This file is a full clean replacement file. It is not a patch stub. -->

Prompt 1.1v — Reusable Default / Replace All / Run Retrospective & Post-Mortem

Proceed to run retrospective and post-mortem only.

Use the current run’s completed workflow outputs as the only analysis universe for this retrospective.

This step starts after one of the following:

- production verification passed
- production verification failed and remediation decision was completed
- the user explicitly stops the run and requests retrospective
- the run is blocked and the user requests post-mortem

Do not use this step to continue the card-generation workflow.

Do not create new cards.
Do not revise cards.
Do not fetch article bodies for new evidence.
Do not perform source augmentation.
Do not prepare PRs.
Do not modify GitHub.
Do not claim production completion.

Use GitHub main workflow docs as the process reference.

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
- no retrospective performed

Input files / references:

- Run intake/preflight JSON: {{RUN_INTAKE_PREFLIGHT_JSON}}
- Stage A JSON: {{STAGE_A_RESULTS_JSON}}
- Stage B JSON: {{STAGE_B_DRAFTS_JSON}}
- Stage C JSON: {{STAGE_C_RESULTS_JSON}}
- Baseline revalidation JSON: {{BASELINE_REVALIDATION_JSON}}
- Evidence QC JSON: {{EVIDENCE_QC_RESULTS_JSON}}
- Content polish JSON: {{CONTENT_POLISH_RESULTS_JSON}}
- Final QC JSON: {{FINAL_QC_RESULTS_JSON}}
- GitHub merge prep JSON: {{GITHUB_MERGE_PREP_RESULTS_JSON}}
- Production verification JSON: {{PRODUCTION_VERIFICATION_RESULTS_JSON}}
- Remediation decision JSON: {{PRODUCTION_REMEDIATION_DECISION_JSON}}, if applicable
- Run tag: {{RUN_TAG}}
- Run label: {{RUN_LABEL_KST}}

If some later-stage files do not exist because the run stopped earlier, do not infer them.

Record missing later-stage files as:

- not_reached
- not_applicable
- blocked_before_stage

Role of this step:

This step is a red-team retrospective.

It must answer:

1. Where did the run stop or degrade?
2. Which stage produced the most holds/rejections?
3. Which rules worked correctly?
4. Which rules were ambiguous or caused friction?
5. Were any workflow violations attempted or prevented?
6. Did any prompt language create escape hatches?
7. Did evidence failures come from source collection, Stage A selection, Stage B fetch, Stage C judgment, post-QC, or production?
8. What should be integrated ruleed before the next run?
9. What should not be changed because the process worked as intended?
10. Did Stage A review_pool partitioning work correctly?
    - candidate_review_pool_count
    - watchlist_context_pool_count
    - reject_or_support_only_pool_count
    - unpartitioned_review_pool_count
    - false-positive candidate_review_pool examples
    - false-negative rejected/support_source_only examples

Governance hierarchy:

When judging process correctness, apply this hierarchy:

1. docs/FACT_DISCIPLINE.md
2. docs/PROMPT_ABC_DEFAULT_MODE.md
3. docs/PROMPT_ABC_SUPPORTING_RULES.md
4. docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md
5. docs/CARD_ID_STANDARD.md
6. docs/WORKFLOW.md
7. docs/OPERATIONS.md
8. docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md

Analysis scope:

Analyze every reached stage:

0.0 Run intake / preflight
0.1 Stage A
0.2 Stage B
0.3 Stage C

## Operational integrated rule — include revise-loop stages in retrospective scope

When analyzing reached stages, include revise-loop stages when present:

- 0.2R Stage B revise r1/r2/r3
- 0.3R Stage C revise r1/r2/r3

Do not treat revise loops as new candidate-generation stages.
Analyze them as constrained repair/validation loops for Stage C revise_required cards only.

0.4 Full baseline revalidation
0.5 Evidence completeness / source-claim QC
0.6 Content enrichment / language polish
0.7 Final publish-readiness QC
0.8 GitHub merge prep
0.9 Production verification
1.0 Remediation, if applicable

Do not penalize a stage for not running if the run correctly stopped earlier.

Retrospective dimensions:

For each reached stage, evaluate:

- input validity
- required docs check
- accounting completeness
- correct candidate universe
- correct state terminology
- prohibited input leakage
- prohibited output naming
- evidence discipline
- duplicate/event discipline
- staleness handling
- source/body quote handling
- content/source-lock handling
- language/terminology handling
- GitHub/main sync handling
- production verification handling
- blocker handling
- report quality
- machine-readable output quality

Core red-team questions:

A. Required docs discipline

- Were all 8 docs read from GitHub main?
- Did any prompt use “if present” or similar optional language for mandatory docs?
- Did any stage proceed despite missing docs?
- Were branch/local/archive docs used incorrectly?

B. Candidate universe discipline

- Did Stage A use only source input and active baseline?
- Did Stage B use only strict_passed_spec?
- Did Stage C use only Stage B draft_cards?
- Did baseline revalidation use only accepted_fact_safe?
- Did evidence QC use only addable_merge_safe?
- Did content polish use only evidence_complete_and_source_claim_covered?
- Did final QC use only content_enriched_and_language_polished?
- Did merge prep use only publish_ready?
- Did production verification use only merged PR/main/production data?

C. State ladder discipline

Check whether the run preserved:

accepted_fact_safe
→ addable_merge_safe
→ evidence_complete
→ source_claim_covered
→ content_enriched
→ language_terminology_polished
→ publish_ready
→ github_merge_ready
→ production_verified

Flag any collapsed states.

D. Web search / fetch discipline

- Was Stage A free of external web search and article body fetch?
- Did Stage B fetch every strict_passed_spec before drafting?
- Were weak specs draft_blocked rather than forced into cards?
- Was Stage C web use limited to spot-check/QC?
- Was post-acceptance web use limited to verification/conflict/duplicate/source checks?
- Was any web search used as silent content enrichment?

E. Evidence discipline

- Were source_quote and fact_sources body-level or official-material?
- Were headline-only, snippet-only, RSS-only, listing-only evidence blocked?
- Were source_quote_status hard-fails correctly held?
- Were URL-only fact_sources blocked?
- Were evidence_role/supports/source_name required?
- Did single-source cards have valid single_source_reason?
- Were visible claims mapped to fact_sources?
- Did hard-fail count block publish_ready?

F. Duplicate/event discipline

- Were duplicates checked by URL, canonical URL, title, actor, asset/policy, event type, date, event fingerprint?
- Were baseline duplicates held?
- Were follow-ups distinguished from reposts?
- Was expected final count never forced?

G. Content/language discipline

- Were visible fields source-locked?
- Were fact_sources/source_quote preserved?
- Were foreign-language titles cleaned?
- Were units and terminology normalized?
- Were banned workflow/meta phrases removed?
- Was SBTL benefit forced anywhere?

H. GitHub / production discipline

- Was GitHub main used as merge source of truth?
- Was main drift revalidated?
- Were only intended files changed?
- Was production verification based on production app/data, not preview only?
- Was production success claimed only after all gates passed?

Failure pattern taxonomy:

## Operational integrated rule — revise-loop failure pattern taxonomy

Also classify revise-loop-specific issues:

- revise_loop_overuse
- revise_loop_limit_missing
- revise_required_mixed_into_post_acceptance
- accepted_pool_supersession_gap
- source_augmentation_performed_without_authorization
- revised_card_introduced_new_claim
- revised_card_changed_core_event_anchor
- revise_blocked_but_auto_promoted
- revise_required_again_not_deferred_after_loop_limit


Classify issues into:

- prompt_escape_hatch
- required_doc_gap
- baseline_ambiguity
- source_input_schema_gap
- stage_a_overpass
- stage_a_overfilter
- stage_b_fetch_failure
- stage_b_evidence_package_gap
- stage_b_forced_draft
- stage_c_overacceptance
- stage_c_overrejection
- baseline_duplicate_gap
- evidence_quote_gap
- claim_coverage_gap
- single_source_gap
- content_overreach
- language_terminology_gap
- final_qc_gate_gap
- github_main_sync_gap
- production_deployment_gap
- runtime_rendering_gap
- reporting_or_accounting_gap
- tool_access_gap
- no_issue_process_worked

Recommendations taxonomy:

Each recommendation must be classified as:

1. prompt_integrated rule_required

A prompt should be changed.

2. docs_integrated rule_required

GitHub workflow docs should be changed.

3. source_collector_integrated rule_required

The upstream collector or final_news_llm_input structure should be changed.

4. validation_script_required

A script/check should be added.

5. manual_operator_check_required

A human/operator checklist item is needed.

6. no_change_recommended

The process blocked correctly; do not weaken it.

Integrated rule recommendation format:

For each recommended integrated rule, include:

- integrated rule_id
- integrated rule_type
- affected_prompt_or_doc
- problem
- evidence_from_run
- proposed_change
- expected_benefit
- risk_if_not_changed
- risk_of_overcorrecting
- priority: P0 / P1 / P2 / P3
- should_integrated rule_now: true/false

Priority definitions:

P0:
- causes false publish_ready
- causes evidence failure to pass
- causes wrong baseline merge
- causes production break
- causes mandatory docs to be skipped

P1:
- causes significant hold/rework
- creates ambiguity likely to recur
- weakens evidence or state discipline

P2:
- improves efficiency or reporting quality
- reduces manual checking burden

P3:
- polish / minor clarity improvement

Do-not-change analysis:

Also identify rules that were annoying but correct.

For each, include:

- rule
- why_it_felt_strict
- why_it_should_remain
- example_from_run

Output files:

1. run_retrospective_{{RUN_TAG}}.json
2. run_retrospective_report_{{RUN_TAG}}.md
3. run_retrospective_integrated rule_recommendations_{{RUN_TAG}}.json
4. run_retrospective_stage_metrics_{{RUN_TAG}}.csv

JSON output requirements:

The JSON must include:

- stage: run_retrospective
- run_tag
- run_label
- required_docs_check
  - docs_expected
  - docs_read_from_github_main
  - docs_missing_or_unreadable
  - status
- run_completion_status
  - last_reached_stage
  - final_status
  - production_verified
  - stopped_reason
- stage_metrics[]
- issue_taxonomy_summary
- prompt_escape_hatch_findings[]
- process_violation_findings[]
- evidence_failure_patterns[]
- duplicate_failure_patterns[]
- production_failure_patterns[]
- integrated rule_recommendations[]
- do_not_change_recommendations[]
- final_retro_decision
- recommended_next_action

Each stage_metrics item must include:

- stage_name
- reached: true/false
- input_count
- output_counts
- hold_count
- reject_count
- pass_count
- accounting_pass
- major_failure_reason
- notes

Each process_violation_finding must include:

- finding_id
- stage
- violation_type
- description
- severity
- evidence
- prevented_by_process: true/false
- recommendation

Each evidence_failure_pattern must include:

- pattern_id
- affected_stage
- count
- examples
- likely_root_cause
- recommended_fix

Each integrated rule_recommendation must follow the integrated rule recommendation format above.

Report requirements:

The Markdown report must include:

1. Run summary

   - run tag
   - run label
   - last reached stage
   - final status
   - production verified: yes/no
   - stopped reason

2. Required docs check

   - list all 8 required docs
   - read status
   - blocker, if any

3. Stage-by-stage metrics table

   Include:
   - input count
   - pass count
   - hold/reject/defer count
   - accounting status
   - main issue

4. What worked

   Include rules that correctly prevented bad output.

5. What failed or created rework

   Group by:
   - input/source issues
   - Stage A issues
   - Stage B evidence issues
   - Stage C judgment issues
   - baseline duplicate issues
   - evidence QC issues
   - content/language issues
   - final QC issues
   - GitHub/production issues

6. Evidence failure pattern analysis

   Include:
   - headline-only issues
   - source_quote missing
   - URL-only fact_sources
   - claim coverage gaps
   - single-source issues
   - source accessibility issues

7. Prompt/doc/source collector integrated rule recommendations

   Include table:
   - priority
   - integrated rule type
   - affected prompt/doc/system
   - problem
   - proposed change
   - integrated rule now yes/no

8. Do-not-change list

   Include rules that should remain strict even if they reduced card count.

9. Final retrospective decision

   Choose one:

   - PROCESS_HEALTHY_NO_INTEGRATED_RULE_REQUIRED
   - INTEGRATED_RULE_RECOMMENDED_BEFORE_NEXT_RUN
   - INTEGRATED_RULE_REQUIRED_BEFORE_NEXT_RUN
   - SOURCE_COLLECTOR_FIX_REQUIRED
   - WORKFLOW_DOC_UPDATE_REQUIRED
   - MANUAL_INVESTIGATION_REQUIRED

10. Explicit boundary statement

   Include this exact statement:

   “This retrospective analyzed the completed or stopped run only. It did not create new cards, revise card content, modify fact_sources, perform source augmentation, prepare a PR, or change GitHub.”

11. Next-step statement

   If no integrated rule required:

   “The next run may start from Prompt 0.0 or Prompt 0.1.”

   If integrated rule recommended:

   “Apply the recommended prompt/doc/source-collector integrated rulees before the next run, then restart from Prompt 0.0.”



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

## Operational integrated rule — retrospective next-call recommendation

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

1. If final_retro_decision = PROCESS_HEALTHY_NO_INTEGRATED_RULE_REQUIRED:
   - recommended_next_call = "new run"
   - recommended_prompt_id = "Prompt 0.0 or Prompt 0.1"

2. If integrated rule is recommended or required:
   - recommended_next_call = "apply prompt/doc/source-collector integrated rulees before the next run"
   - recommended_prompt_id = "Prompt 0.0 after integrated rulees are applied"

3. If manual investigation is required:
   - recommended_next_call = "manual investigation"
   - do_not_proceed_to = "new run until blockers are resolved"
Stop after retrospective.

Do not proceed to a new run, integrated rule, PR, or remediation unless the user explicitly instructs it.

## V2 retrospective addendum — Stage A selector-forensic audit

When reviewing a run affected by Stage A selection quality, the retrospective must audit:

1. Whether `enhanced_selector_precision_version=20260505_v2` or later/equivalent was applied.
2. Whether Stage A JSON, CSV, and Markdown were generated from the same result object.
3. Whether `stage_a_validity_status` and `artifact_consistency_status` were PASS before Stage B started.
4. Whether every strict_passed_spec had a complete all-pass `strict_gate_check`.
5. Whether any product/demo/PoC/component/interview/commentary/personnel/consumer anecdote entered strict_passed_spec without a hard commercial/policy event.
6. Whether stale-warm or unknown event_date items entered strict_passed_spec.
7. Whether source-tier-3 or access-risk candidates entered strict_passed_spec without official/source-body alternatives.
8. Whether baseline incremental-scope cases were correctly routed to existing_reinforcement or review_pool_follow_up_check.
9. Whether user watchlist URLs were audited without auto-promotion.
10. Whether timeline sovereignty was preserved without memory-based political or geopolitical corrections.

The retrospective must output:

- `stage_a_v2_compliance_status: PASS|FAIL|NOT_APPLIED`
- `stage_a_v2_failure_table[]`
- `rerun_required_before_stage_b: true|false`
- `superseded_outputs[]`

If V2 was not applied and selector precision or artifact consistency failed, recommend `Prompt 0.1 Stage A rerun`; do not recommend Stage B revise or post-acceptance continuation.



## Structural default retrospective check — Stage A output completeness

When Stage A was reached, retrospective must audit Stage A structural output validity, not only editorial outcomes.

Check and report:

- `stage_a_validity_status`
- `artifact_consistency_status`
- `csv_schema_status`
- `review_pool_partition_status`
- `review_pool_carry_forward_ledger_status`
- `strict_pass_gate_metadata_status`
- `baseline_duplicate_screen_status`
- whether Stage A JSON/report/CSV counts match
- whether Stage A CSV exposed all required partition/gate columns
- whether `review_pool[]` was partitioned into:
  - `candidate_review_pool[]`
  - `watchlist_context_pool[]`
  - `reject_or_support_only_pool[]`
- whether any unpartitioned review_pool item existed
- whether any Stage B recommendation was made despite structural failure

Classify failures as:

- stage_a_csv_schema_gap
- stage_a_review_pool_unpartitioned
- stage_a_next_call_gate_bypassed
- stage_a_artifact_mismatch
- strict_gate_metadata_missing
- baseline_duplicate_screen_gap

If any of these occurred, recommend structural prompt/default repair before another run.

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
- `manual_integrated rule_mixed: false`
- `previous_run_output_mixed: false`

Stage C and Stage C revise outputs must include:

- `strict_gate_acceptance_guard_applied: true`
- `accepted_fact_safe_with_missing_strict_gate_count: 0`
- `accepted_pool_lineage_status: PASS|FAIL`
- `lineage_integrity_status: PASS|FAIL`
- `strict_gate_metadata_preserved: true|false`
- `execution_anchor_metadata_preserved: true|false`
- `superseded_lineage_mixed: false`
- `manual_integrated rule_mixed: false`
- `previous_run_output_mixed: false`

If any accepted_fact_safe item lacks Stage A strict gate metadata, Stage C must not mark it accepted_fact_safe. It must move the item to `deferred_review_pool`, `revise_required`, `support_source_only`, or `rejected` depending on severity and stage rules.

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


## Prompt 1.1 v4 retrospective checks

The retrospective must explicitly evaluate whether the run:

1. abandoned any source/claim/card before good-faith verification was completed,
2. ignored any later-discovered valid evidence,
3. silently absorbed later-discovered evidence into a downstream state,
4. allowed any source-strength caveat to proceed to 0.6 without 0.5R review or explicit user waiver,
5. silently discarded review_pool or treasure candidates without bounded review/accounting,
6. attempted to auto-promote review_pool or treasure without an authorized promotion run.


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


## Operational integrated rule — STAGE_A_FALSE_POSITIVE_RISK_EXAMPLES_20260507_V5

Stage A must actively document how it prevented over-broad strict-pass selection.

Every Stage A report and JSON output must include:

- `lane_sanity_rejected_examples[]`
- `strict_false_positive_risk_examples[]`
- `strict_pass_borderline_examples[]`
- `negative_filter_applied[]`
- `negative_filter_routed_to_review_pool[]`

### Negative filters

The following patterns must not enter `strict_passed_spec[]` unless a concrete battery/grid/ESS/EV/materials execution anchor is present:

- generic finance or insurance items without battery/grid/ESS/EV/material impact
- general AI/data-center items without power, grid, battery, ESS, or energy-infrastructure execution
- publicity/event participation without operational signal
- broad corporate positioning without project, contract, capacity, policy, filing, or data release anchor
- roundups where no single event can support a full-schema card
- trend/explainer items without a fresh execution or data-release anchor

Do not overcorrect by deleting all adjacent items. If a candidate has plausible relevance but lacks strict-pass certainty, route it to `candidate_review_pool[]` with:

- `bounded_review_question`
- `promotion_precondition`
- `recommended_review_method`
- `strict_false_positive_risk_reason`

Stage A must not use this integrated rule to perform web search or article body fetch. Stage A remains selector-only.


## Operational integrated rule — GITHUB_MAIN_UNREADABLE_FALLBACK_RULE_20260507_V5

Prompt 0.8 must normally use GitHub main `public/data/cards.json` as the merge source of truth.

If the connector confirms repository access or metadata but cannot return readable `public/data/cards.json` body content, 0.8 must remain blocked unless the user supplies a fallback baseline that is explicitly declared as GitHub-main-equivalent.

Required fallback fields:

- `fallback_baseline_file`
- `fallback_baseline_declared_as: GitHub-main-equivalent baseline`
- `fallback_baseline_total_count`
- `latest_cards_commit_sha` or `latest_cards_check_timestamp`
- `user_confirmation_current_main_equivalent: true`
- `reason_github_main_body_unreadable`

Without these fields, stop with:

- `status: BLOCKED_GITHUB_MAIN_SYNC_UNREADABLE`
- `no GitHub merge preparation performed`
- `no GitHub-ready or PR-candidate label`

If fallback is accepted, the output status must remain local/sync-qualified, for example:

- `LOCAL_MERGE_PREP_READY_REQUIRES_GITHUB_MAIN_SYNC_CONFIRMATION`

This rule must not weaken the GitHub main sync gate. It only defines an auditable fallback when connector body access fails.

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

## Prompt 1.1 retrospective — claim diversity review

If Prompt 0.6/0.7 reached claim diversity audit, retrospective must include:

- `claim_type_distribution`
- `over_clustered_claim_groups[]`
- `high_overlap_cards[]`
- `accepted_overlap_cards[]`
- `claim_overlap_accepted_reasons[]`
- examples where claim repositioning improved distinction
- examples where source-safe repositioning was not possible
- whether any unsupported strategic variety was attempted or prevented

Do not penalize a batch merely because several cards share a claim type. Penalize only unsupported variety, unexamined overlap, or failure to articulate distinct strategic questions when the source evidence permitted it.



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


## Retrospective source diversity review

Prompt 1.1 must review source diversity separately from claim diversity.

Report:

- source_diversity_summary
- single_source_exception_count
- hold_single_source_caveat_count
- source_url_urls_sync_fail_count
- high_signal_single_source_count
- source_diversity_false_pass_examples
- source_diversity_overcorrection_examples

Do not treat claim diversity as evidence diversity.

## FIX-005 — Stage A/B must emit required lineage metadata

Prompt 0.4 lineage guard must remain hard. Do not soften it.

The corrected diagnosis from run `20260516_012728` is that Stage A and Stage B failed to emit lineage fields that their own prompts already required. This is execution non-compliance, not a schema-version gap.

Stage A exit must fail if any `strict_passed_spec[]` item lacks required lineage fields from `SCHEMA_CONTRACT_STAGE_LINEAGE.md`, including `enhanced_selector_precision_version`, `selector_policy_version`, `strict_gate_check`, `staleness_decision`, `source_access_risk`, and `strict_pass_gate.all_six_conditions_passed`.

Stage B preflight must run `stage_a_validity_guard` before drafting. Stage B output must include `lineage_integrity_status`, `stage_a_validity_guard_applied`, `strict_gate_metadata_preserved`, `execution_anchor_metadata_preserved`, `superseded_lineage_mixed`, `manual_integrated rule_mixed`, and `previous_run_output_mixed`.

If required fields are missing, stop with `BLOCKED_STAGE_OUTPUT_SCHEMA_NONCOMPLIANT` or `BLOCKED_STAGE_A_LINEAGE_NONCOMPLIANT`.

## FIX-007 — Shared schema contract and stage-exit conformance check

All stages must reference `SCHEMA_CONTRACT_STAGE_LINEAGE.md`.

Each named stage must run or explicitly satisfy a stage-exit artifact conformance check before recommending the next stage. Missing required fields must stop the stage with:

```text
BLOCKED_STAGE_OUTPUT_SCHEMA_NONCOMPLIANT
```

Do not wait until Prompt 0.4 to discover Stage A/B lineage omissions.

# 13_PROMPT_1_1_Retrospective.md — Source Diversity source-diversity integrated rule

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

## Retrospective source-diversity metrics

Every retrospective must report:

```text
candidate_same_event_cluster_count
support_sources_preserved_count
support_sources_dropped_count
cards_with_fact_source_rows_ge_2_but_one_independent_owner
single_domain_rate_before_exception
single_source_exception_count
invalid_single_source_exception_count
same_url_row_inflation_count
syndication_inflation_count
source_role_distribution
source_contribution_utilization_rate
cards_with_multi_source_but_no_visible_synthesis
cards_using_fetch_date_as_visible_date
duplicate_event_sources_reinforced_into_existing_cards
```

Required failure taxonomy additions:

- stage_a_source_cluster_loss
- stage_b_representative_source_collapse
- false_multi_source_count
- syndication_counted_as_independent
- source_contribution_not_integrated
- single_source_exception_overuse
- visible_quote_fetch_date_leak
- UI_same_source_repetition
- duplicate_reinforcement_information_loss

If any of these caused false `publish_ready`, the retrospective decision must be
`INTEGRATED_RULE_REQUIRED_BEFORE_NEXT_RUN`.

    Stop after retrospective.

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
