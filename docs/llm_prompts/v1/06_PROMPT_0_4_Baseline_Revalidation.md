<!-- REPLACE_ALL_CLEAN_VERSION: LLM_PROMPT_GITHUB_CANONICAL_V1_SOURCE_DIVERSITY_IB_CODEX -->
<!-- Generated KST: 2026-07-08T21:33:49.790191+09:00 -->
<!-- This file is a full clean replacement file. It is not a patch stub. -->

Prompt 0.4v — Reusable Default / Replace All / Post-Acceptance Full Baseline Revalidation

Proceed to post-acceptance full baseline revalidation only.

Use the current run’s Stage C r0 output and Stage C revise outputs as the only candidate input universe for this step.

This step starts after Stage C.

Do not continue from, trust, import, integrated rule, or reuse any previous post-QC, addable, final, PR candidate, or GitHub-ready outputs unless the user explicitly declares them as current-run authoritative inputs.

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
- no baseline revalidation work performed

Do not infer replacement rules from memory.
Do not use archived docs.
Do not use branch-only docs.
Do not use local snippets unless the user explicitly provides them as current-run authoritative docs.

Input files:

- Stage A JSON: {{STAGE_A_RESULTS_JSON}}
- Stage B JSON: {{STAGE_B_DRAFTS_JSON}}
- Stage C JSON: {{STAGE_C_RESULTS_JSON}}
- Stage C report: {{STAGE_C_REPORT_MD}}
- Stage C revise r1 JSON: {{STAGE_C_REVISE_R1_RESULTS_JSON}}, if applicable
- Stage C revise r2 JSON: {{STAGE_C_REVISE_R2_RESULTS_JSON}}, if applicable
- Stage C revise r3 JSON: {{STAGE_C_REVISE_R3_RESULTS_JSON}}, if applicable
- Active baseline cards: {{BASELINE_CARDS_SOURCE}}
- Baseline source declaration: {{BASELINE_SOURCE_DECLARATION}}
- Run tag: {{RUN_TAG}}
- Run label: {{RUN_LABEL_KST}}

Required input rule:

This step requires a valid Stage C r0 JSON from the same run. If Stage C revise passes occurred, it also requires the corresponding Stage C revise JSON outputs from the same run.

The Stage C JSON must include:

- required_docs_check
- run_tag
- run_label
- draft_cards_input_count
- accepted_fact_safe[]
- revise_required[]
- rejected[]
- support_source_only[]
- deferred_review_pool[]
- decision_ledger[]
- stage_c_accounting_matches_draft_cards_input_count

If Stage C r0 JSON is missing, invalid, incomplete, not from the same run, or has accounting mismatch, stop and report:

- status: BLOCKED_STAGE_C_INVALID
- reason: [...]
- no baseline revalidation work performed

If any supplied Stage C revise JSON is missing, invalid, incomplete, not from the same run, or has accounting mismatch, stop and report:

- status: BLOCKED_STAGE_C_REVISE_INVALID
- revision_pass: [...]
- reason: [...]
- no baseline revalidation work performed

Candidate input rule:

## Operational integrated rule — revision-aware accepted_fact_safe pool assembly

Accepted_fact_safe input may come from:

- Stage C r0 accepted_fact_safe[]
- Stage C revise r1 accepted_fact_safe[]
- Stage C revise r2 accepted_fact_safe[]
- Stage C revise r3 accepted_fact_safe[]

But only the latest accepted version of each source_spec_id may enter baseline revalidation.

If both an earlier draft and revised accepted version exist for the same source_spec_id, use the latest accepted revised version and mark the earlier version superseded_by_revise_pass.

Assembly rules:

1. Build accepted_fact_safe_pool_candidates[] from all current-run Stage C r0 and Stage C revise accepted_fact_safe[] arrays.
2. Group accepted_fact_safe_pool_candidates[] by source_spec_id.
3. For each source_spec_id, select exactly one latest accepted version using revision order:
   - Stage C revise r3 accepted version, if present
   - otherwise Stage C revise r2 accepted version, if present
   - otherwise Stage C revise r1 accepted version, if present
   - otherwise Stage C r0 accepted version
4. Exclude all earlier accepted versions for that same source_spec_id and record supersession metadata:
   - superseded_by_revise_pass
   - superseded_by_revised_draft_id, if available
   - superseded_source_spec_id
   - superseded_reason: earlier_accepted_version_replaced_by_latest_revision
5. Only the assembled latest_accepted_fact_safe_pool[] may enter this post-acceptance baseline revalidation step.

Do not include:

- duplicate earlier accepted versions for the same source_spec_id
- revise_required
- revise_required_again
- rejected
- support_source_only
- deferred_review_pool
- Stage B draft_blocked
- Stage A review_pool
- Stage A rejected
- previous accepted payloads
- previous addable payloads
- previous final files
- previous PR candidates

If any non-accepted_fact_safe item is mixed into the candidate input, remove it and report it as mixed_input_excluded.

If duplicate accepted_fact_safe versions for the same source_spec_id are found, keep only the latest version and report all excluded versions in superseded_accepted_versions[].


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

This step is full baseline revalidation.

It decides only:

- addable_merge_safe
- duplicate_hold
- existing_reinforcement
- withheld_reinforcement
- baseline_conflict
- review_pool_deferred

This step must not decide:

- evidence_complete
- source_claim_covered
- content_enriched
- language_terminology_polished
- publish_ready
- PR readiness
- GitHub readiness

Hard rule:

Full baseline revalidation decides addable/hold only.

It must reset publish_ready=false for every surviving addable card.

Do not preserve publish_ready=true from any upstream file.

If any candidate enters this step with publish_ready=true, reset it to false and record:

- publish_ready_reset: true
- reset_reason: full_baseline_revalidation_does_not_decide_publish_ready

State ladder reminder:

accepted_fact_safe
→ addable_merge_safe
→ evidence_complete
→ source_claim_covered
→ content_enriched
→ language_terminology_polished
→ publish_ready

This step may move accepted_fact_safe only to addable_merge_safe or a hold state.

It cannot move any card beyond addable_merge_safe.

Web search / fetch boundary:

This step should primarily use:

- Stage C accepted_fact_safe card data
- active baseline cards
- URLs
- titles
- actors
- projects/assets/policies
- dates
- event fingerprints
- related metadata

External web search is not required by default.

Limited web checking is allowed only when needed for:

- canonical URL clarification
- duplicate event confirmation
- conflict detection
- source accessibility check relevant to duplicate/event identity

Do not use web search for:

- evidence completeness
- source augmentation
- adding new facts
- strengthening weak cards
- rewriting visible fields
- discovering new card candidates
- rescuing non-accepted items

If new source evidence appears useful, do not insert it.
Record it as:

- needs_source_augmentation: true
- recommended_next_action: source_augmentation_pass

Baseline rule:

Use the active baseline declared by the user.

Allowed baseline sources:

1. GitHub main → public/data/cards.json
2. User-uploaded baseline explicitly declared as current-run baseline
3. Local final candidate explicitly declared as current-run baseline

If the baseline is not GitHub main, record:

- github_main_sync_required_later: true

Do not call any output GitHub-ready unless GitHub main sync gate has later passed.

Duplicate/event screening method:

Compare each accepted_fact_safe candidate against:

A. Current accepted_fact_safe batch internally

B. Active baseline cards

Use all of the following:

- exact ID
- exact URL
- canonical URL
- normalized title
- title similarity
- actor/company/project
- asset or policy
- event type
- region
- event date / representative date
- factual anchor
- source story IDs
- primary URL
- event fingerprint
- broad-card vs follow-up-card relation

Event fingerprint:

Create or infer an event_fingerprint for each candidate:

- actor
- asset_or_policy
- location
- event_type
- event_date
- source_url_cluster
- factual_anchor

Recommended event_type values:

- policy_change
- regulation
- funding
- financing
- investment
- plant_construction
- production_start
- capacity_ramp
- contract
- partnership
- MOU
- pilot
- product_launch
- earnings
- resource_assessment
- project_approval
- safety_incident
- supply_disruption
- trade_action
- certification
- technology_milestone
- other

Duplicate classification:

Use these baseline_relation values:

- new
- follow_up
- duplicate_of_main
- reinforcement_of_main
- already_covered_by_broader_card
- baseline_conflict
- uncertain

Internal batch duplicate outcomes:

If two accepted_fact_safe cards are the same event:

- keep the stronger card as addable candidate
- move the weaker one to duplicate_hold or withheld_reinforcement
- record duplicate_cluster_id
- record kept_card_id or kept_draft_id
- record duplicate_reason

Same URL is a strong duplicate signal but not the only signal.

Different URL does not mean different event.

Different title does not mean different event.

Follow-up rule:

A candidate may remain addable_merge_safe as a follow_up only if it has a distinct new event anchor.

Allowed follow-up examples:

- new official approval after prior proposal
- construction start after prior plan
- financing close after prior MOU
- production start after prior plant announcement
- new policy enactment after consultation
- new contract after pilot
- new capacity/market data after earlier broad trend card

Not enough for follow_up:

- same event re-reported by another outlet
- same press release summarized later
- translated repost
- article with no new factual anchor
- same project with only background details
- same announcement with slightly different title

Reinforcement rule:

Use existing_reinforcement or withheld_reinforcement when:

- candidate is useful as a source/background
- event is already covered by existing baseline card
- candidate adds context but not a distinct standalone event
- candidate should support another card rather than become a new card

support_source_only from Stage C remains excluded unless explicitly authorized for a separate source support process.

Staleness awareness:

This step does not reperform Stage B/C staleness QC from scratch.

However, if duplicate/event screening reveals that the candidate is actually an old event already covered or stale relative to baseline, move it to:

- duplicate_hold
- existing_reinforcement
- withheld_reinforcement
- baseline_conflict
- review_pool_deferred

Do not keep stale duplicate republications as addable_merge_safe.

Output state definitions:

1. addable_merge_safe

Use only when:

- candidate is Stage C accepted_fact_safe
- not an internal duplicate
- not a baseline duplicate
- not merely reinforcement
- not already covered by broader baseline card
- no unresolved baseline conflict
- event fingerprint is distinct enough to add
- GitHub/main baseline caveat is recorded if applicable

Important:
addable_merge_safe is not evidence_complete and not publish_ready.

Every addable_merge_safe card must include:

- state: addable_merge_safe
- previous_state: accepted_fact_safe
- publish_ready: false
- evidence_complete: false
- source_claim_covered: false
- content_enriched: false
- language_terminology_polished: false
- needs_evidence_completeness_qc: true
- needs_source_claim_coverage_qc: true
- needs_content_enrichment: true
- needs_language_terminology_polish: true

2. duplicate_hold

Use when:

- same event already exists in baseline
- same event duplicated internally
- same URL/canonical URL already exists
- event fingerprint matches existing card
- candidate is covered by broader card and has no distinct new event

3. existing_reinforcement

Use when:

- useful as supporting context for an existing baseline card
- source strengthens a known theme
- no independent card value remains after baseline comparison

4. withheld_reinforcement

Use when:

- candidate has some value but should not be added as a new card now
- may be useful for later source augmentation
- may support future content but not current addable set

5. baseline_conflict

Use when:

- candidate conflicts with existing baseline card
- baseline has a similar event but data/date/actor differs materially
- cannot safely decide duplicate vs follow-up without manual review
- baseline count/source appears inconsistent
- active baseline may not match GitHub main and sync risk is material

6. review_pool_deferred

Use when:

- addable/hold decision cannot be safely made
- duplicate/follow-up relation is uncertain
- event fingerprint is incomplete
- candidate needs manual baseline review

Accounting rule:

Every Stage C accepted_fact_safe item must appear exactly once in one of:

- addable_merge_safe
- duplicate_hold
- existing_reinforcement
- withheld_reinforcement
- baseline_conflict
- review_pool_deferred

No silent skip is allowed.

Report:

- accepted_fact_safe_input_count
- addable_merge_safe_count
- duplicate_hold_count
- existing_reinforcement_count
- withheld_reinforcement_count
- baseline_conflict_count
- review_pool_deferred_count
- outcome_total_count
- baseline_revalidation_accounting_matches_input_count

If accounting does not match, mark output invalid and report:

- status: BLOCKED_BASELINE_REVALIDATION_ACCOUNTING_MISMATCH

ID handling:

Do not assign final production IDs in this step unless the current workflow explicitly requires it.

If draft_id exists, preserve draft_id.

If card id exists from Stage C, keep it but do not treat it as final GitHub-safe ID until publish-ready stage.

Check for:

- duplicate ID within candidate batch
- duplicate ID against baseline
- date-region numbering collision risk
- legacy ID collision

If collision exists, do not silently rename.
Record:

- id_collision: true
- collision_with: [...]
- recommended_next_action: assign_id_after_publish_ready_or_manual_id_resolution

Content handling:

Do not rewrite visible fields in this step.

Do not edit:

- title
- sub
- gate
- fact
- implication
- fact_sources
- source_quote

unless the only change is adding non-reader-facing state metadata.

If visible content appears weak, do not fix it here.
Record:

- needs_content_enrichment: true

Evidence handling:

Do not decide evidence_complete here.

Do not treat Stage B or Stage C source quality as final evidence completeness.

Do not run source-claim coverage as final.

For every addable_merge_safe item, set:

- evidence_complete: false
- source_claim_covered: false
- needs_evidence_completeness_qc: true
- needs_source_claim_coverage_qc: true

Output files:

1. post_acceptance_baseline_revalidation_{{RUN_TAG}}.json
2. post_acceptance_baseline_revalidation_report_{{RUN_TAG}}.md
3. post_acceptance_baseline_revalidation_decisions_{{RUN_TAG}}.csv
4. addable_merge_safe_PENDING_EVIDENCE_QC_{{RUN_TAG}}.json
5. baseline_hold_manifest_{{RUN_TAG}}.json

Do not use FINAL, PR_CANDIDATE, GitHub-ready, merge-ready, publish-ready, evidence_complete, or source_claim_covered in filenames.

The phrase addable_merge_safe may be used only if evidence/publish-ready disclaimers are included.

JSON output requirements:

The main JSON must include:

- stage
- run_tag
- run_label
- input_stage_c_file
- baseline_file
- baseline_source_declaration
- baseline_count
- github_main_sync_required_later
- required_docs_check
  - docs_expected
  - docs_read_from_github_main
  - docs_missing_or_unreadable
  - status
- accepted_fact_safe_input_count
- mixed_input_excluded_count
- addable_merge_safe_count
- duplicate_hold_count
- existing_reinforcement_count
- withheld_reinforcement_count
- baseline_conflict_count
- review_pool_deferred_count
- outcome_total_count
- baseline_revalidation_accounting_matches_input_count
- internal_duplicate_summary
- baseline_duplicate_summary
- event_fingerprint_summary
- id_collision_summary
- addable_merge_safe[]
- duplicate_hold[]
- existing_reinforcement[]
- withheld_reinforcement[]
- baseline_conflict[]
- review_pool_deferred[]
- mixed_input_excluded[]
- decision_ledger[]

Each addable_merge_safe item must include:

- state: addable_merge_safe
- previous_state: accepted_fact_safe
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
- event_fingerprint
- baseline_relation
- duplicate_risk
- duplicate_screening
  - exact_url_match
  - canonical_url_match
  - title_similarity_match
  - actor_asset_event_match
  - baseline_event_fingerprint_match
  - internal_batch_duplicate_match
  - already_covered_by_broader_card
- id_collision
- id_collision_notes
- publish_ready: false
- evidence_complete: false
- source_claim_covered: false
- content_enriched: false
- language_terminology_polished: false
- needs_evidence_completeness_qc: true
- needs_source_claim_coverage_qc: true
- needs_content_enrichment: true
- needs_language_terminology_polish: true
- needs_publish_readiness_qc: true
- publish_ready_reset
- reset_reason
- notes

Each duplicate_hold item must include:

- state: duplicate_hold
- draft_id
- source_spec_id
- duplicate_type
- duplicate_reason
- matched_baseline_card_id
- matched_baseline_title
- matched_baseline_url
- matched_internal_draft_id
- event_fingerprint
- recommended_next_action

Allowed duplicate_type values:

- exact_url_duplicate
- canonical_url_duplicate
- same_event_fingerprint
- internal_batch_duplicate
- already_covered_by_broader_card
- translated_repost
- followup_not_distinct
- other

Each existing_reinforcement item must include:

- state: existing_reinforcement
- draft_id
- source_spec_id
- matched_baseline_card_id
- reinforcement_type
- reason_not_new_card
- possible_use
- recommended_next_action

Each withheld_reinforcement item must include:

- state: withheld_reinforcement
- draft_id
- source_spec_id
- reason_withheld
- possible_future_use
- recommended_next_action

Each baseline_conflict item must include:

- state: baseline_conflict
- draft_id
- source_spec_id
- conflict_type
- conflict_detail
- matched_baseline_card_id
- recommended_next_action

Allowed conflict_type values:

- duplicate_vs_followup_uncertain
- event_date_conflict
- actor_or_asset_conflict
- baseline_count_or_source_conflict
- id_collision
- canonical_url_uncertain
- other

Each review_pool_deferred item must include:

- state: review_pool_deferred
- draft_id
- source_spec_id
- defer_reason
- unresolved_questions
- required_manual_checks
- recommended_next_action
- not_addable_in_current_step: true

Each mixed_input_excluded item must include:

- item_id
- prior_state
- exclusion_reason

Each decision_ledger row must include:

- draft_id
- source_spec_id
- prior_state
- baseline_revalidation_outcome
- baseline_relation
- duplicate_risk
- matched_baseline_card_id
- matched_internal_draft_id
- event_fingerprint
- id_collision
- publish_ready_reset
- reason
- notes

Report requirements:

The Markdown report must include:

1. Run metadata

   - Stage C input file
   - baseline file/source
   - baseline source declaration
   - baseline count
   - GitHub main sync required later: yes/no
   - run tag
   - run label
   - accepted_fact_safe input count

2. Required docs check

   - list all 8 required docs
   - confirm each was read from GitHub main
   - if any doc was not read, this step must not proceed

3. Method

   - accepted_fact_safe-only confirmation
   - revise_required/rejected/support_source_only/deferred exclusion confirmation
   - duplicate/event fingerprint method
   - baseline comparison method
   - internal batch duplicate method
   - ID collision method
   - publish_ready reset confirmation
   - no evidence_complete decision confirmation
   - no content rewrite confirmation
   - limited web-check policy, if used

4. Summary table

   - accepted_fact_safe input count
   - addable_merge_safe count
   - duplicate_hold count
   - existing_reinforcement count
   - withheld_reinforcement count
   - baseline_conflict count
   - review_pool_deferred count
   - mixed_input_excluded count
   - outcome total count
   - accounting match: yes/no

5. addable_merge_safe manifest

   For each addable item:
   - draft_id
   - source_spec_id
   - short event anchor
   - region / cat / signal
   - baseline relation
   - duplicate risk
   - event fingerprint
   - ID collision status
   - publish_ready reset status
   - next required gate: evidence completeness QC

6. hold manifest summary

   Include:
   - duplicate_hold
   - existing_reinforcement
   - withheld_reinforcement
   - baseline_conflict
   - review_pool_deferred

   For each item:
   - draft_id
   - reason
   - matched baseline card, if any
   - recommended next action

7. Duplicate/event screening notes

   Include:
   - exact URL duplicates
   - canonical URL duplicates
   - same event fingerprint cases
   - broader-card coverage cases
   - uncertain duplicate vs follow-up cases
   - internal batch duplicate clusters

8. ID collision notes

   Include:
   - duplicate IDs
   - date-region sequence risks
   - baseline ID collision risks
   - recommended next action

9. Explicit boundary statement

   Include this exact statement:

   “Full baseline revalidation decided addable/hold only. It reset publish_ready=false for all surviving addable cards. It did not decide evidence_complete, source_claim_covered, content_enriched, language_terminology_polished, publish_ready, PR readiness, or GitHub readiness.”

10. Next-step statement

   Include this exact statement:

   “The next step is evidence completeness QC. Only addable_merge_safe cards may enter that step. addable_merge_safe is not evidence_complete and not publish_ready.”



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

## Operational integrated rule — baseline revalidation next-call recommendation

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

1. If addable_merge_safe_count > 0:
   - recommended_next_call = "evidence completeness QC"
   - recommended_prompt_id = "Prompt 0.5"
   - recommended_input_universe = "addable_merge_safe[] only"

2. If addable_merge_safe_count = 0:
   - recommended_next_call = "retrospective or review holds"
   - recommended_prompt_id = "Prompt 1.1 or manual hold review"

Do not proceed automatically to evidence QC.
Stop after full baseline revalidation.

Do not proceed to evidence completeness QC until I explicitly say “evidence QC” or “evidence completeness QC”.

## V2 lineage guard before baseline revalidation

Baseline revalidation must not proceed from a Stage C output whose Stage A lineage is invalid.

Before evaluating `accepted_fact_safe[]`, verify from the provided Stage A/B/C artifacts that:

- Stage A had `enhanced_selector_precision_version=20260505_v2` or later/equivalent;
- `stage_a_validity_status=PASS`;
- `artifact_consistency_status=PASS`;
- Stage B applied `stage_a_validity_guard_applied=true`;
- Stage C applied `strict_gate_acceptance_guard_applied=true`;
- `accepted_fact_safe_with_missing_strict_gate_count=0`;
- no `accepted_fact_safe` card carries unresolved selection guard findings.

If any check fails, stop and report:

```json
{
  "status": "BLOCKED_INVALID_STAGE_A_LINEAGE",
  "no_baseline_revalidation_performed": true,
  "recommended_next_call": "rerun Stage A with enhanced selector precision"
}
```

Do not use baseline revalidation to launder a weak Stage A selection into addable_merge_safe.

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

## Operational integrated rule — NO_UNVERIFIED_HOLD_OR_DELETE_BOUNDARY_FOR_DOWNSTREAM_STAGES_20260507_V2

This stage is not a general evidence-rescue stage unless its prompt explicitly authorizes source augmentation or remediation.

The NO_UNVERIFIED_HOLD_OR_DELETE rule applies here only within this stage's own authority:

- 0.4: duplicate, baseline relation, conflict, and accepted-pool lineage verification.
- 0.8: GitHub main sync, merge-prep integrity, PR-candidate naming, and publish-ready lineage preservation.
- 0.9: deployed production data verification only.
- 1.0: production issue classification, rollback/redeploy/data-fix recommendation only.

This stage must preserve prior rescue metadata and must not use hold states to launder unresolved evidence defects. If an evidence/source/claim defect is discovered here, return to the earliest valid upstream stage instead of repairing it silently.

If this stage issues a hold/block/reject/rollback/deploy-hold inside its own authority, it must record:

- `rescue_attempted` or `not_applicable_for_this_stage` with reason
- `blocked_source_reason` when source/evidence related
- `final_hold_or_reject_reason`
- upstream stage to return to, if applicable

## Operational integrated rule — NO_SILENT_DOWNSTREAM_ENRICHMENT_BOUNDARY_FOR_NON_EVIDENCE_STAGES_20260507_V3

This stage must preserve prior rescue and lineage metadata, but it must not perform silent evidence enrichment.

This stage may not add, rewrite, or absorb later-discovered source evidence, source_quote, numeric claims, named-entity claims, or source-derived framing to fix upstream evidence defects.

If a new evidence issue or useful later source is discovered here, record it only as:

- `rescue_candidate_evidence[]`
- `source_augmentation_needed: true`
- `recommended_return_stage`
- `reason_current_stage_cannot_absorb_evidence`

Then stop advancement for the affected item unless the current prompt explicitly authorizes that exact modification.

If this stage attempts to use later-discovered evidence to advance an item, stop and report:

- `status: BLOCKED_SILENT_DOWNSTREAM_ENRICHMENT_ATTEMPT`
- `recommended_return_stage`
- `no next-stage recommendation`

This boundary prevents unresolved evidence defects from being laundered through baseline revalidation, merge prep, production verification, or remediation.



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


## Operational integrated rule — 0.4 collision check authoritative test — 20260514

Run 20260513_083924 의 0.4 초기 logic 이 seq_overlap check 를 포함해 valid empty-slot 할당까지 잘못 reject 함. baseline 이 _01/_02/_03/_05 를 보유할 때 Stage B 의 `next_seq` 는 빈 slot _04 를 정상 할당하는데, max(baseline_seq)=5 > assigned=4 비교로 fail 처리됨. 2026-05-11_GL_04 / 2026-05-08_GL_01 두 카드가 잘못 hold 되어 mid-run 정정 필요.

### HARD RULE — 0.4 baseline collision authoritative test

0.4 의 baseline collision 검사는 다음 세 check 만 사용한다 (seq_overlap 사용 금지):

```
1. id_collision   : spec.id ∈ baseline_ids (정확 일치)
2. url_collision  : spec urls 중 어떤 것이라도 ∈ baseline urls
3. title_collision: spec title.lower().strip() ∈ baseline titles (lower)

3개 중 하나라도 True 면 → baseline_collision_hold
모두 False 면 → addable_merge_safe
```

### 명시적 금지

- `seq_overlap` check 사용 금지: assigned_seq > max(baseline_seq_in_group) 비교는 invalid
- 이유: Stage B `next_seq` 가 (date,region) 그룹의 빈 slot 을 정상 채움. baseline _01/_02/_03/_05 일 때 Stage B 는 _04 할당 가능하며 이는 id_collision False 이므로 valid.

### 이유

- id_collision check 가 sequence overlap 의 authoritative test 임
- Stage B 의 `next_seq` 가 collision-free seq 를 보장하므로 추가 seq_overlap check 는 redundant + over-strict

### P_007 와의 조정

P_007 의 baseline_event_collision_hold (Stage A) 와 0.4 의 baseline_collision_hold 는 **다른 카테고리**:
- Stage A baseline_event_collision_hold: 같은 사건 다른 매체 (event-fingerprint 기반)
- 0.4 baseline_collision_hold: id/url/title 정확 일치 (수정 후 재진입 시 catch)

두 check 모두 유효하며 서로 보완적.

### Event-level duplicate safety fallback

The exact-match rule above prevents false holds from sequence gaps. It must not
be interpreted as permission to ignore a newly discovered same-event duplicate.

If 0.4 sees evidence that a candidate is the same event as an existing baseline
card but does not trip id/url/title exact collision, 0.4 must not mark the item
`addable_merge_safe`. It must set:

```jsonc
{
  "state": "baseline_event_collision_review_required",
  "addable_merge_safe": false,
  "exact_collision_check": "PASS",
  "event_duplicate_signal": "PRESENT",
  "recommended_return_stage": "Stage A event-fingerprint review or 0.5R source-strength review"
}
```

Examples of event duplicate signals include same named actor + same facility or
project + same capacity/amount/date/customer/order/policy decision, even when
title or URL differs.

If the apparent overlap is merely same sector, same company, same geography, or
same broad topic without a shared concrete event anchor, do not hold for event
collision; continue the normal 0.4 exact collision test.

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

## FIX-005 — Stage A/B must emit required lineage metadata

Prompt 0.4 lineage guard must remain hard. Do not soften it.

The corrected diagnosis from run `20260516_012728` is that Stage A and Stage B failed to emit lineage fields that their own prompts already required. This is execution non-compliance, not a schema-version gap.

Stage A exit must fail if any `strict_passed_spec[]` item lacks required lineage fields from `SCHEMA_CONTRACT_STAGE_LINEAGE.md`, including `enhanced_selector_precision_version`, `selector_policy_version`, `strict_gate_check`, `staleness_decision`, `source_access_risk`, and `strict_pass_gate.all_six_conditions_passed`.

Stage B preflight must run `stage_a_validity_guard` before drafting. Stage B output must include `lineage_integrity_status`, `stage_a_validity_guard_applied`, `strict_gate_metadata_preserved`, `execution_anchor_metadata_preserved`, `superseded_lineage_mixed`, `manual_integrated_rule_mixed`, and `previous_run_output_mixed`.

If required fields are missing, stop with `BLOCKED_STAGE_OUTPUT_SCHEMA_NONCOMPLIANT` or `BLOCKED_STAGE_A_LINEAGE_NONCOMPLIANT`.

## Operational integrated rule — source_url canonical-resolution propagation (EFP-01 / EFP-02) — 20260622

### Why this integrated rule exists

This stage already folds canonical/URL signals into duplicate-and-event screening
(`canonical URL clarification`, `source_url_cluster`, `canonical_url_match`,
`canonical_url_duplicate`). It verifies that URLs *match* for duplicate purposes,
but it never verifies that each `fact_sources[].source_url` is the FULL canonical
article permalink the `source_quote` was extracted from, and — critically — when
0.4 restores or normalizes a `urls[]`/canonical entry, it does **not** propagate
that restoration back into the matching `source_url`. That non-propagation is the
EFP-01 root cause (0.6 restored `urls[]` but left 24 `source_url`s truncated).

This integrated rule adds a third source axis — **resolution integrity** — and makes it a
propagation hard-rule for this stage. It does **not** add new `fact_sources`; it
overwrites an existing, already-authorized `source_url` with its full canonical form.

### Scope clarification vs the content-handling rule

The "Do not edit fact_sources / source_quote" rule above still holds for visible
evidence content. Overwriting a truncated `source_url` with the full URL that is
already present in this card's own `urls[]` is an **identity normalization of an
existing source pointer**, not new evidence, not a new `fact_sources` entry, and
not a `source_quote` change. It is therefore permitted under the existing
exception "unless the only change is adding non-reader-facing state metadata,"
extended here to non-reader-facing source-pointer normalization. No quote, number,
named entity, framing, or `fact_sources` count may change.

### CHECK 1 — canonical completeness (HARD-FAIL)

For every `fact_sources[].source_url` that supports a visible field, require it to
be the full article permalink, byte-identical to the `urls[]` entry the quote was
extracted from. HARD-FAIL if it is either:

- (a) a truncated prefix of a longer `urls[]` entry on the same card, or
- (b) a generic endpoint with no article identifier (no numeric id and no 8+ char
  slug): `read.do`, `article.html`, `view.php`, `list`, `index`, `board`, or a
  bare domain root.

### CHECK 2 — article resolution

Within this stage's limited web-check budget (already permitted for "canonical URL
clarification"), confirm that `source_url` resolves to the SAME article that
contains `source_quote` (same headline / actor / event) — not a section index,
listing page, syndication hub, or a different article. Record per source:
`resolved_article_matches_quote: true|false`.

### CHECK 3 — prefix-laundering block + mandatory propagation (EFP-01 fix)

If this card's `urls[]` contains a longer URL that has `source_url` as a prefix,
overwrite `source_url` with that full URL and re-run CHECK 2. More generally:

> **Propagation hard-rule.** Whenever 0.4 restores, normalizes, de-duplicates, or
> canonicalizes any `urls[]`/canonical entry for a card, the corresponding
> `fact_sources[].source_url` MUST be overwritten with the full canonical URL in
> the SAME pass, and `resolved_article_matches_quote` re-evaluated. 0.4 must never
> leave a normalized `urls[]` next to a truncated `source_url`.

Each propagation must be logged: `source_url_overwritten_from`,
`source_url_overwritten_to`, `propagation_trigger: urls_normalization_0_4`.

### Routing on HARD-FAIL (use this stage's existing authority and states)

0.4 decides addable/hold only. A source_url-resolution failure that cannot be
fixed by in-card prefix propagation must NOT be marked `addable_merge_safe`. Route
it inside this stage's existing vocabulary:

- If the full canonical URL is not present on the card and must be fetched/added,
  do not insert it here. Set `needs_source_augmentation: true` and
  `recommended_next_action: source_augmentation_pass`, and route the item to
  `review_pool_deferred` (or `baseline_conflict` when the resolution mismatch also
  creates duplicate/identity ambiguity) with:
  - `hold_reason_code` ∈ { `source_url_truncated`, `source_url_generic_endpoint`,
    `source_url_resolves_to_wrong_article`, `source_url_resolves_to_listing` }
  - `recommended_return_stage` (earliest valid evidence stage, e.g. Stage B
    evidence package or 0.5 evidence completeness QC).

For `baseline_conflict` routing, reuse the existing `conflict_type` slot with the
value `canonical_url_uncertain` plus the `hold_reason_code` above.

### Augmentation rule (EFP-02)

Any source attached by augmentation — INCLUDING any post-0.7 augmentation pass —
must pass CHECK 1, CHECK 2, and CHECK 3 before it may support visible text. A
`web_search_snippet` URL must never become `source_url` without a body fetch that
confirms `source_quote` appears in the resolved article. If 0.4 detects that an
upstream/parallel augmentation attached or changed a `source_url` without re-running
this resolution axis and Evidence QC, treat it as a silent-enrichment defect:
do not advance the item, set `addable_merge_safe: false`, and report
`status: BLOCKED_SILENT_DOWNSTREAM_ENRICHMENT_ATTEMPT` with `recommended_return_stage`.

### Required output object

Emit `source_url_resolution_summary` in BOTH the JSON and the report (use this exact
field name so 0.7 can gate on it):

```jsonc
{
  "source_url_resolution_summary": {
    "checked": 0,
    "canonical_complete": 0,
    "truncated_prefix_fixed": 0,
    "generic_endpoint_failed": 0,
    "wrong_article_failed": 0,
    "resolves_to_listing_failed": 0
  }
}
```

Carry `source_url_resolution_summary` and each card's
`resolved_article_matches_quote` forward to 0.5/0.7. Any card that survives to
`addable_merge_safe` must have every supporting `source_url` canonical-complete
with `resolved_article_matches_quote: true`; otherwise it is held, not addable.

# 06_PROMPT_0_4_Baseline_Revalidation.md — Source Diversity source-diversity integrated rule

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

## Baseline revalidation — source reinforcement preservation

Baseline duplicate detection must separate:

- duplicate card event;
- independent reinforcement source;
- follow-up event;
- context-only source.

When a candidate is a duplicate event, do not create a second card, but preserve unique sources and
facts in:

```json
{
  "existing_reinforcement": {
    "matched_baseline_card_id": "",
    "reinforcement_sources": [],
    "unique_information": [],
    "recommended_existing_card_fields": [],
    "reinforcement_status": "ready|needs_source_augmentation|withheld"
  }
}
```

A duplicate hold that drops all additional sources without a reinforcement ledger is invalid.

This stage must carry forward, unchanged:

- source diversity metrics;
- source roles and contributions;
- source publication dates;
- source synthesis audit;
- single-source exception status.

Block with `BLOCKED_BASELINE_REVALIDATION_SOURCE_REINFORCEMENT_LOSS` if useful source evidence is
lost.

    Stop after baseline revalidation. Do not assign publish_ready.

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

<!-- WORKFLOW_CONTRACT_OVERLAY_20260723:BEGIN -->
Mandatory shared contracts for this stage:

- `docs/RELATED_LIFECYCLE_CONTRACT.md`
- `docs/SCHEMA_CONTRACT_STAGE_LINEAGE.md`
- `docs/SOURCE_AUDIT_CONTRACT.md`
- `validation_data/source_owner_registry.json` when source-owner counting is performed

The shared contracts supersede conflicting wording only for Related lifecycle, date-role/freshness,
source-audit metadata derivation, stage-exit artifact conformance, and production-verification proof.

Prompt 0.4 Related baseline overlay:

- Re-run Related and duplicate screening against current main and the current candidate batch.
- Classify candidates as new unrelated, distinct follow-up, program lineage, same-event duplicate,
  existing reinforcement, or Related-uncertain hold.
- Preserve candidate-to-candidate edges for production-ID resolution.
- Strong evidence does not override a stale or duplicate selection defect.
- Run `related_lifecycle_check.py` structurally before emitting addable candidates.
<!-- WORKFLOW_CONTRACT_OVERLAY_20260723:END -->
