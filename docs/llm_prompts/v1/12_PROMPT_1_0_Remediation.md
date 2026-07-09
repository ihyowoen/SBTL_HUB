<!-- REPLACE_ALL_CLEAN_VERSION: LLM_PROMPT_GITHUB_CANONICAL_V1_SOURCE_DIVERSITY_IB_CODEX -->
<!-- Generated KST: 2026-07-08T21:33:49.790191+09:00 -->
<!-- This file is a full clean replacement file. It is not a patch stub. -->

Prompt 1.0v — Reusable Default / Replace All / Production Issue Remediation, Redeploy, and Rollback Decision

Proceed to production issue remediation decision only.

Use the current run’s production verification output as the only issue universe for this step.

This step starts only after production verification produced one of:

- deployment_pending
- deployment_failed
- data_not_updated
- cache_or_cdn_issue
- app_runtime_failure
- rendering_issue
- production_hold
- needs_redeploy
- needs_rollback_review

Do not use this step if production verification passed.

Do not continue from, trust, import, integrated rule, or reuse any previous remediation, rollback, redeploy, manually integrated ruleed output, or local-only diagnosis unless the user explicitly declares it as current-run authoritative input.

Use GitHub main, Vercel production, and the production verification report as the source of truth.

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
- no remediation decision performed

Input files / references:

- Production verification JSON: {{PRODUCTION_VERIFICATION_RESULTS_JSON}}
- Production verification report: {{PRODUCTION_VERIFICATION_REPORT_MD}}
- Production issue manifest: {{PRODUCTION_HOLD_OR_REDEPLOY_MANIFEST_JSON}}
- GitHub merge prep JSON: {{GITHUB_MERGE_PREP_RESULTS_JSON}}
- PR number or PR URL: {{PR_NUMBER_OR_URL}}
- Merge commit SHA: {{MERGE_COMMIT_SHA}}
- Target repo: ihyowoen/SBTL_HUB
- Target branch: main
- Target data path: public/data/cards.json
- Production app URL: {{PRODUCTION_APP_URL}}
- Production data URL: {{PRODUCTION_APP_URL}}/data/cards.json
- Run tag: {{RUN_TAG}}
- Run label: {{RUN_LABEL_KST}}

Required input rule:

This step requires valid production verification output from the same run.

If production verification JSON is missing, invalid, incomplete, not from the same run, or has accounting mismatch, stop and report:

- status: BLOCKED_PRODUCTION_VERIFICATION_INVALID
- reason: [...]
- no remediation decision performed


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


Remediation lineage guard:

If a production issue is caused by invalid upstream lineage, stale selector output, artifact mismatch, missing execution anchor evidence, or non-publish-ready card leakage, remediation must recommend the safest rollback, data-fix PR, or rerun point.

Do not integrated rule card content directly in remediation. Do not convert held/rejected/review_pool cards into production fixes. Return to the earliest defective stage:

- Stage A for selector, staleness, duplicate, lane-fit, or execution-anchor selection defects
- Stage B for source fetch or evidence extraction defects
- Stage C for fact-safe validation defects
- 0.4 baseline revalidation for merge-safety defects
- 0.5 evidence QC for source-claim coverage defects
- 0.6 content polish for language/content-depth defects
- 0.7 final QC for publish-ready gate defects
- 0.8 merge prep for GitHub baseline sync defects


## Upstream lineage integrity gate

This prompt is downstream of selector, evidence, content, and/or production gates. It must not repair or launder an invalid upstream lineage.

Before doing any work, validate that the current-run production verification output carries a lineage integrity statement from the immediately previous step.

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


For Prompt 1.0 specifically, production verification is the only upstream issue source. It must prove that:
- remediation is diagnosing the current run's production verification failure only
- no prompt is allowed to use remediation to edit cards, rescue candidates, integrated rule fact_sources, or bypass publish-ready gates
- rollback, redeploy, or fix PR actions remain recommendations only unless explicitly authorized by the user

If any required lineage field is missing, false, contradictory, stale, not from the same run, or inconsistent with the candidate payload, stop immediately and report:

- status: BLOCKED_UPSTREAM_LINEAGE_INVALID
- reason: [...]
- invalid_or_missing_lineage_fields: [...]
- no remediation decision performed

Do not infer lineage validity from memory.
Do not continue just because candidate counts look correct.
Do not use this prompt to fix Stage A/B/C selection defects or post-QC evidence defects.

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

Role of this step:

This step diagnoses production verification failure and recommends the safest next action.

This step may decide:

- no_action_wait_for_deployment
- redeploy_recommended
- cache_wait_or_purge_recommended
- data_fix_pr_required
- runtime_fix_pr_required
- rollback_review_required
- rollback_not_required
- rerun_production_verification_required
- blocked_manual_investigation_required

This step must not:

- automatically rollback production
- automatically redeploy unless explicitly authorized by the user
- edit cards.json
- edit source code
- create a new PR
- change card content
- change fact_sources
- rescue held/rejected cards
- mark production_verified
- force success because the issue “looks minor”

Safety rule:

Rollback or redeploy requires explicit user instruction unless the user’s original instruction clearly authorized it.

If rollback is considered, first produce a rollback decision memo.

Do not perform rollback in this prompt by default.

Issue classification:

Classify each issue from production verification into one or more categories:

1. Deployment timing issue

Examples:
- deployment_pending
- production deployment not complete
- production still serving previous build shortly after merge

Default action:
- no_action_wait_for_deployment
- rerun_production_verification_required

2. Vercel deployment failure

Examples:
- deployment_failed
- build failed
- production deployment not READY

Default action:
- inspect deployment logs
- runtime_fix_pr_required or redeploy_recommended depending on cause

3. Data freshness / cache issue

Examples:
- GitHub main correct
- production /data/cards.json stale
- cache-busted endpoint correct but normal endpoint stale

Default action:
- cache_wait_or_purge_recommended
- rerun_production_verification_required
- do not rollback unless app availability/data integrity is harmed

4. Data mismatch issue

Examples:
- GitHub main has cards
- production data missing cards even after deployment/cache checks
- count mismatch
- wrong cards.json served

Default action:
- redeploy_recommended or data_fix_pr_required
- rerun production verification

5. Schema/runtime issue

Examples:
- production data correct
- app fails due schema/type drift
- React runtime error
- cards fail to render
- category/region/signal field breaks UI

Default action:
- runtime_fix_pr_required
- rollback_review_required if production is materially broken

6. Rendering/content display issue

Examples:
- card visible but layout broken
- long text breaks card
- implication not rendering
- source links render badly

Default action:
- runtime_fix_pr_required or data_fix_pr_required
- rollback only if severe

7. Duplicate/data integrity issue

Examples:
- duplicate ID
- duplicate URL
- duplicate event
- count formula fails
- rejected/hold item appears in production

Default action:
- data_fix_pr_required
- rollback_review_required if production data integrity is materially compromised

8. Unknown/manual issue

Examples:
- tool could not verify
- inconsistent production responses
- partial outage
- unclear app behavior

Default action:
- blocked_manual_investigation_required

Severity levels:

Assign severity:

- S0 critical: production app unavailable, data JSON invalid, runtime blocks app
- S1 high: cards page broken, severe schema issue, wrong data in production
- S2 medium: new cards missing, stale data, card rendering issue, duplicate issue
- S3 low: cache delay, minor layout issue, non-blocking visual issue

Action guidance:

S0:
- rollback_review_required
- runtime_fix_pr_required or data_fix_pr_required
- do not claim production_verified

S1:
- rollback_review_required if user-facing availability or core data integrity is affected
- otherwise targeted fix PR
- rerun production verification

S2:
- targeted fix or redeploy/cache resolution
- rollback usually not required

S3:
- wait/cache/redeploy as appropriate
- rerun production verification

Decision output states:

1. no_action_wait_for_deployment

Use when:
- PR/main are correct
- deployment is pending
- no evidence of failed deployment or broken production
- safest action is to wait for deployment completion and rerun 0.9

2. redeploy_recommended

Use when:
- main data is correct
- production did not pick it up
- no code/data fix is needed
- redeploy is likely sufficient

3. cache_wait_or_purge_recommended

Use when:
- cache-busted data is correct
- normal production path is stale
- issue is likely cache/CDN

4. data_fix_pr_required

Use when:
- public/data/cards.json on main is wrong
- duplicate/schema/data issue exists
- correction requires PR

5. runtime_fix_pr_required

Use when:
- data is correct but app rendering/runtime fails
- frontend code change likely needed

6. rollback_review_required

Use when:
- production availability or data integrity is materially harmed
- fastest safe path may be revert/rollback
- user must explicitly authorize rollback

7. rollback_not_required

Use when:
- issue is non-critical
- redeploy/cache/fix PR is safer than rollback

8. rerun_production_verification_required

Use when:
- issue may be transient
- deployment/cache/fix needs verification after action

9. blocked_manual_investigation_required

Use when:
- automated verification cannot determine safe action
- issue is ambiguous or tool access is insufficient

Output files:

1. production_remediation_decision_{{RUN_TAG}}.json
2. production_remediation_report_{{RUN_TAG}}.md
3. production_issue_decision_ledger_{{RUN_TAG}}.csv
4. rollback_review_memo_{{RUN_TAG}}.md, only if rollback_review_required

JSON output requirements:

The main JSON must include:

- stage
- run_tag
- run_label
- repo
- pr_number
- pr_url
- merge_commit_sha
- production_app_url
- production_data_url
- production_verification_status
- required_docs_check
  - docs_expected
  - docs_read_from_github_main
  - docs_missing_or_unreadable
  - status
- issue_summary
  - total_issues
  - s0_count
  - s1_count
  - s2_count
  - s3_count
- issue_classification[]
- remediation_decision
- rollback_required
- rollback_authorized: false
- redeploy_required
- redeploy_authorized: false
- fix_pr_required
- rerun_production_verification_required
- recommended_next_action
- decision_ledger[]

Each issue_classification item must include:

- issue_id
- issue_type
- severity
- affected_system
- affected_card_ids
- observed_evidence
- likely_cause
- recommended_action
- rollback_considered
- rollback_reasoning
- next_verification_required

Each decision_ledger row must include:

- issue_id
- issue_type
- severity
- decision
- reason
- requires_user_authorization
- recommended_next_action
- notes

Report requirements:

The Markdown report must include:

1. Run metadata

   - repo
   - PR number / URL
   - merge commit SHA
   - production URL
   - run tag
   - run label

2. Required docs check

   - list all 8 required docs
   - confirm each was read from GitHub main
   - if any doc was not read, this step must not proceed

3. Production verification failure summary

   - final_status from production verification
   - failed gates
   - affected systems
   - affected card IDs
   - observed evidence

4. Issue classification table

   For each issue:
   - issue type
   - severity
   - likely cause
   - recommended action

5. Remediation decision

   State one primary recommendation:

   - wait and rerun production verification
   - redeploy and rerun verification
   - cache purge/wait and rerun verification
   - data fix PR
   - runtime fix PR
   - rollback review
   - manual investigation

6. Rollback decision memo, if applicable

   Include:
   - why rollback is being considered
   - impact if no rollback
   - safer alternative, if any
   - whether rollback is recommended
   - explicit statement that rollback requires user authorization

7. Explicit boundary statement

   Include this exact statement:

   “This remediation step diagnosed production verification failure and recommended next action only. It did not modify GitHub, redeploy, rollback, edit cards.json, edit source code, rewrite card content, or change fact_sources.”

8. Next-step statement

   If waiting/redeploy/cache:
   “After the recommended deployment/cache action completes, rerun production verification.”

   If fix PR required:
   “Prepare a focused fix PR, merge it, then rerun production verification.”

   If rollback review required:
   “Rollback must not be performed unless explicitly authorized by the user.”

## Operational integrated rule — remediation handling for lineage-invalid production issues

If production verification reports a lineage-invalid card, an unapproved card, or a card whose selection/execution-anchor lineage is missing, remediation must treat it as a data-governance issue, not a cosmetic deployment issue.

Classify such issues as one or more of:

- `data_fix_pr_required`
- `rollback_review_required`
- `manual_investigation_required`
- `retrospective_required_before_next_run`

Remediation must not:

- rewrite the card in place without a focused fix PR;
- call the card valid because it renders correctly;
- redeploy to hide a data-lineage issue;
- continue to a new run before the lineage defect is logged in retrospective;
- rollback automatically without explicit user authorization.

If the safest action is to remove or revert lineage-invalid cards, recommend a focused data fix PR or rollback review, but do not execute it automatically.

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

## Operational integrated rule — remediation next-call recommendation

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

1. If wait/redeploy/cache action is recommended:
   - recommended_next_call = "rerun production verification after the action completes"
   - recommended_prompt_id = "Prompt 0.9"

2. If fix PR is required:
   - recommended_next_call = "prepare a focused fix PR, merge it, then rerun production verification"
   - recommended_prompt_id = "Prompt 0.9 after fix PR merge"

3. If rollback review is required:
   - recommended_next_call = "explicit rollback authorization or alternative fix decision"
   - do_not_proceed_to = "rollback unless explicitly authorized"

Do not redeploy, rollback, or create a fix PR automatically.
Stop after remediation decision.

Do not redeploy, rollback, or create a fix PR unless the user explicitly instructs it.

---

## Execution-anchor and selector-lineage safety overlay — 2026-05-05

This overlay is downstream of the Stage A safe-selector integrated rule. It prevents post-acceptance steps from laundering a weak or superseded Stage A/B/C lineage into publish-ready or production status.

Terminology lock:

- Do not use or enforce a format-based hard-exclude rule.
- Product, demo, PoC, component, interview, commentary, roundup, speech, or personnel formats are not automatically rejected by format alone.
- They are subject to a strict-pass presumption block: without a concrete fresh execution anchor, they must not have entered `strict_passed_spec[]`; if they did, the downstream step must hold, reject, or return the item to the appropriate prior stage rather than polishing it forward.
- Concrete execution anchors include signed contract, binding customer order, offtake, commercial deployment, field installation, commissioning, production start, facility opening, certification, regulatory decision, public funding approval, binding procurement, measurable capacity addition, safety recall/regulatory action, or named customer adoption.

### Remediation rule for selector-lineage or execution-anchor issues

If Production Verification reports `selector_lineage_or_anchor_integrity_issue`, classify it as a data integrity issue, not a cosmetic rendering issue.

Allowed decisions:

- `data_fix_pr_required`
- `rollback_review_required` if invalid data is live and materially harms trust
- `blocked_manual_investigation_required` if the affected card lineage cannot be reconstructed
- `rerun_production_verification_required` only after a fix or rollback is completed

Not allowed:

- mark production verified
- treat as cache-only issue
- rewrite the card directly in production
- rescue the card through remediation
- remove caveats to make it fit
- integrated rule fact_sources without returning to the appropriate evidence/source step

If the issue traces back to Stage A selection, the remediation memo must identify the earliest invalid stage and recommend rerun from that stage rather than masking the problem downstream.

### Output requirement

Add to Remediation JSON:

```json
"selector_lineage_remediation": {
  "issue_detected": false,
  "earliest_invalid_stage": null,
  "recommended_safe_action": null,
  "rollback_review_required": false
}
```


## Publish-ready state discipline in remediation

Remediation does not create, preserve, or promote `publish_ready=true` candidates.

If a production issue requires card data changes, remediation must recommend the safest rollback, focused data-fix PR, or rerun point. It must not convert `review_pool`, `support_source_only`, `rejected`, `draft_blocked`, or lineage-invalid cards into `publish_ready` cards.

Any remediation output that includes candidate card records must keep or reset:

```json
"publish_ready": false
```

unless the output is simply referencing a card that already passed Final QC and was previously merged; even then, remediation must treat the card as an object under investigation, not as a newly publish-ready candidate.

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

# 12_PROMPT_1_0_Remediation.md — Source Diversity source-diversity integrated rule

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

## Source-diversity remediation routing

When production or final validation reveals a source-diversity defect, return to the earliest
defective stage:

- Stage A: same-event sources were not clustered or preserved;
- Stage B: discovery, independence review, quote extraction or synthesis failed;
- Stage C: false multi-source or invalid exception was accepted;
- 0.4: duplicate-event reinforcement sources were lost;
- 0.5: canonical/ownership hard gate failed;
- 0.6: evidence existed but visible fields were not synthesized;
- 0.7: publish-ready was assigned despite a diversity failure;
- 0.8: merge serialization or UI integrated rule was omitted;
- 0.9: production grouping or visible-date rendering failed.

Remediation must prefer source restoration and controlled revalidation over deletion. It must not
directly edit production cards outside the named stage ladder.

    Stop after the remediation decision.

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
