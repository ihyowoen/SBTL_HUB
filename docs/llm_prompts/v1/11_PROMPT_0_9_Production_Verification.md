<!-- REPLACE_ALL_CLEAN_VERSION: LLM_PROMPT_GITHUB_CANONICAL_V1_SOURCE_DIVERSITY_IB_CODEX -->
<!-- Generated KST: 2026-07-08T21:33:49.790191+09:00 -->
<!-- This file is a full clean replacement file. It is not a patch stub. -->

Prompt 0.9v — Reusable Default / Replace All / Production Verification

Proceed to production verification only.

This step starts only after the GitHub PR has been merged into main.

Use the current run’s GitHub merge preparation output and the merged GitHub main state as the only verification universe for this step.

Do not continue from, trust, import, integrated rule, or reuse any previous production verification, deployment check, manually integrated app state, preview result, or local-only output unless the user explicitly declares it as current-run authoritative input.

Use GitHub main and Vercel production as the verification source of truth.

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
- no production verification performed

Do not infer replacement rules from memory.
Do not use archived docs.
Do not use branch-only docs.
Do not use local snippets unless the user explicitly provides them as current-run authoritative docs.

Input files / references:

- GitHub merge prep JSON: {{GITHUB_MERGE_PREP_RESULTS_JSON}}
- GitHub merge prep report: {{GITHUB_MERGE_PREP_REPORT_MD}}
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

This step requires:

- a valid GitHub merge prep output from the same run
- a merged PR or merge commit on main
- the publish_ready cards that were actually merged
- the expected current main card count after merge
- the production app URL

If the PR is not merged, stop and report:

- status: BLOCKED_PR_NOT_MERGED
- no production verification performed

If the merge commit cannot be confirmed on main, stop and report:

- status: BLOCKED_MERGE_COMMIT_NOT_ON_MAIN
- no production verification performed

If the production app URL is missing, stop and report:

- status: BLOCKED_PRODUCTION_URL_MISSING
- no production verification performed


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


Production verification lineage guard:

Production verification must verify only the cards that were actually merged from final QC publish_ready[] and GitHub merge prep.

If production data contains a card that lacks required publish_ready lineage metadata, flag it as production_hold_lineage_gap. Do not mark production_verified until the mismatch is explained or remediated.

This step must not rewrite content, add evidence, or reinterpret execution anchors. It checks deployed state only.


## Upstream lineage integrity gate

This prompt is downstream of selector, evidence, content, and/or production gates. It must not repair or launder an invalid upstream lineage.

Before doing any work, validate that the current-run GitHub merge prep output carries a lineage integrity statement from the immediately previous step.

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


For Prompt 0.9 specifically, GitHub merge prep is the upstream production data source. It must prove that:
- every verified card was actually included in the merged GitHub main data candidate
- the merge prep output came from current-run publish_ready[] only
- no post-QC hold, rejected, duplicate, review_pool, or manually integrated card was merged
- format-risk / execution-anchor metadata and required evidence/content flags remain present in main data for newly added cards

If any required lineage field is missing, false, contradictory, stale, not from the same run, or inconsistent with the candidate payload, stop immediately and report:

- status: BLOCKED_UPSTREAM_LINEAGE_INVALID
- reason: [...]
- invalid_or_missing_lineage_fields: [...]
- no production verification performed

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

FACT_DISCIPLINE.md always wins for facts, numbers, quotes, and evidence discipline.

Role of this step:

This step verifies that the merged publish_ready cards are actually live and functioning in production.

This step may decide:

- production_verified
- production_hold
- deployment_pending
- deployment_failed
- data_not_updated
- app_runtime_failure
- rendering_issue
- cache_or_cdn_issue
- needs_redeploy
- needs_rollback_review

This step must not:

- create new cards
- rescue held/rejected cards
- edit cards.json
- edit source code
- rewrite visible fields
- modify fact_sources
- add sources
- change PR contents
- force production verification when app/data does not match
- claim production success based only on PR merge
- claim production success based only on Vercel build success
- claim production success based only on branch preview

Production verification source hierarchy:

1. GitHub main public/data/cards.json after merge
2. Vercel production deployment tied to the merge commit
3. Production /data/cards.json response
4. Production app UI rendering the new cards
5. Browser/runtime smoke test

Preview deployment is not sufficient.

Local build is not sufficient.

GitHub main file alone is not sufficient.

Production verification gates:

Gate 1 — PR Merge Confirmation

PASS only if:

- PR is merged
- merge commit is on main
- changed files match intended files
- public/data/cards.json was updated
- no unexpected files were merged

Gate 2 — Main Data Confirmation

PASS only if:

- latest GitHub main public/data/cards.json is readable
- JSON is valid
- cards array exists
- expected merged card IDs are present
- final main count equals pre-merge main count + actually_added_count
- no duplicate IDs
- no duplicate URLs
- no duplicate canonical URLs where checkable
- no duplicate event fingerprints among new/main where checkable
- latest-first sort passes
- all newly added cards preserve publish_ready=true and required evidence/content flags

Gate 3 — Vercel Production Deployment Confirmation

PASS only if:

- production deployment exists
- deployment is tied to main or the merge commit
- deployment status is READY / successful
- deployment completed after the merge commit
- production URL resolves successfully

If Vercel production deployment is pending, return deployment_pending.

If Vercel production deployment failed, return deployment_failed.

Gate 4 — Production Data Endpoint Confirmation

PASS only if:

- {{PRODUCTION_APP_URL}}/data/cards.json returns HTTP 200
- response is valid JSON
- card count matches latest GitHub main cards.json
- expected merged card IDs are present
- newest cards appear in expected latest-first order
- no stale pre-merge data is being served

Use cache-busting query if needed:

- /data/cards.json?run_tag={{RUN_TAG}}&t={{CURRENT_TIMESTAMP}}

If normal endpoint is stale but cache-busted endpoint is correct, mark cache_or_cdn_issue but do not claim full production_verified until the normal production path is acceptable or the cache issue is explicitly accepted.

Gate 5 — Production App UI Smoke Test

PASS only if:

- production app loads successfully
- no blocking runtime error appears
- NEWS/HOME screen renders
- new cards are visible or searchable/filterable according to app behavior
- new card titles/subs/facts render without schema break
- implication array renders correctly
- urls/source links do not break card rendering
- Korean/English/Chinese/Japanese visible text cleanup remains acceptable
- layout is not obviously broken by long fields
- latest-first ordering appears correct in UI

Gate 6 — Runtime Console / Network Check

PASS only if:

- /data/cards.json network request succeeds
- no blocking JS runtime error prevents cards from loading
- no 404/500 for required data assets
- no JSON parse error
- no React rendering error caused by new card schema
- no CORS/data path error

Gate 7 — Regression Check

PASS only if:

- existing cards still render
- filters/tabs affected by cards.json still work
- categories/regions/signals do not break UI
- no visible duplicate caused by the new merge
- no obvious frontend fallback/error state remains

Gate 8 — Output Integrity

PASS only if:

- verification ledger accounts for every merged publish_ready card
- all new cards are verified in main data and production data
- all new cards are either visible in app or confirmed reachable by app search/filter path
- no production-only mismatch remains
- report supports production_verified

State definitions:

1. production_verified

Use only when all production verification gates pass.

Every production_verified run must include:

- pr_merged: true
- merge_commit_on_main: true
- github_main_data_verified: true
- vercel_production_ready: true
- production_data_endpoint_verified: true
- production_ui_verified: true
- runtime_smoke_test_passed: true
- production_verified: true

2. deployment_pending

Use when:

- PR merged
- main data is correct
- production deployment has not completed yet
- production app still serves previous build/data

3. deployment_failed

Use when:

- PR merged
- Vercel production deployment failed
- production app is not updated or broken

4. data_not_updated

Use when:

- PR merged
- GitHub main has new cards
- production /data/cards.json does not show new cards
- deployment may be stale or cache issue exists

5. cache_or_cdn_issue

Use when:

- production data differs between normal and cache-busted requests
- stale data appears to be served
- app may not reflect latest cards due cache

6. app_runtime_failure

Use when:

- production data is correct
- app fails to load cards due JS/runtime/schema issue

7. rendering_issue

Use when:

- app loads
- data is present
- but cards render incorrectly, break layout, or hide critical fields

8. production_hold

Use when:

- any production verification gate fails
- issue is not clearly deployment_pending/cache/runtime/redeploy-specific
- do not declare production success

9. needs_redeploy

Use when:

- main data is correct
- deployment did not pick up latest main
- Vercel redeploy is likely required

10. needs_rollback_review

Use when:

- production is broken in a way that affects app availability or data integrity
- rollback or revert PR should be considered
- do not perform rollback unless user explicitly instructs

Accounting rule:

Every publish_ready card that was merged must appear exactly once in production verification ledger as:

- verified_in_main_and_production
- verified_in_main_not_production
- verified_in_data_not_ui
- missing_from_main
- missing_from_production
- rendering_issue
- duplicate_or_schema_issue

No silent skip is allowed.

Report:

- publish_ready_merged_count
- verified_in_main_count
- verified_in_production_data_count
- verified_in_ui_count
- missing_from_main_count
- missing_from_production_count
- rendering_issue_count
- duplicate_or_schema_issue_count
- production_verification_accounting_matches_merged_count

If accounting does not match, report:

- status: BLOCKED_PRODUCTION_VERIFICATION_ACCOUNTING_MISMATCH

Verification steps:

A. Confirm PR merge status.

B. Confirm merge commit is on main.

C. Read latest GitHub main public/data/cards.json.

D. Validate GitHub main data:

- JSON valid
- cards array valid
- count formula
- new IDs present
- no duplicate IDs
- no duplicate URLs
- no schema/type drift for new cards
- latest-first sort

E. Check Vercel production deployment:

- production deployment status
- deployment commit/SHA
- deployment time after merge
- deployment URL

F. Fetch production data endpoint:

- {{PRODUCTION_APP_URL}}/data/cards.json
- cache-busted variant

G. Compare production data to GitHub main data:

- count
- new IDs
- new titles
- ordering
- schema

H. Run production app UI smoke test:

- load production URL
- verify app renders
- verify NEWS/HOME cards load
- verify new cards are visible or reachable
- verify filters/search do not hide all new cards unexpectedly
- verify no critical runtime error

I. Produce production verification report and JSON.

Output files:

1. production_verification_results_{{RUN_TAG}}.json
2. production_verification_report_{{RUN_TAG}}.md
3. production_verification_ledger_{{RUN_TAG}}.csv
4. production_hold_or_redeploy_manifest_{{RUN_TAG}}.json, if any issue exists

Do not use “completed” or “production_verified” in filenames unless all gates pass.

If all gates pass, allowed extra output:

5. production_verified_manifest_{{RUN_TAG}}.json

JSON output requirements:

The main JSON must include:

- stage
- run_tag
- run_label
- repo
- main_branch
- pr_number
- pr_url
- merge_commit_sha
- production_app_url
- production_data_url
- required_docs_check
  - docs_expected
  - docs_read_from_github_main
  - docs_missing_or_unreadable
  - status
- pr_merge_confirmation
  - pr_merged
  - merge_commit_on_main
  - changed_files
  - unexpected_files
- github_main_data_check
  - main_cards_count
  - expected_final_count
  - count_formula_pass
  - json_valid
  - cards_array_valid
  - new_card_ids_present
  - duplicate_id_count
  - duplicate_url_count
  - schema_type_drift_count
  - latest_first_sort_pass
- vercel_production_check
  - deployment_found
  - deployment_status
  - deployment_commit_sha
  - deployment_after_merge
  - production_url_status
- production_data_check
  - normal_endpoint_status
  - cache_busted_endpoint_status
  - production_cards_count
  - production_matches_main
  - new_card_ids_present
  - stale_data_detected
  - cache_or_cdn_issue
- production_ui_check
  - app_load_status
  - cards_render_status
  - new_cards_visible_or_reachable
  - runtime_error_detected
  - network_error_detected
  - rendering_issue_detected
- regression_check
  - existing_cards_render
  - filters_or_tabs_work
  - category_region_signal_safe
  - no_obvious_duplicate_in_ui
- verification_summary
  - publish_ready_merged_count
  - verified_in_main_count
  - verified_in_production_data_count
  - verified_in_ui_count
  - missing_from_main_count
  - missing_from_production_count
  - rendering_issue_count
  - duplicate_or_schema_issue_count
  - production_verification_accounting_matches_merged_count
- final_status
- production_verified
- recommended_next_action
- card_verification_ledger[]
- issue_manifest[]

Each card_verification_ledger row must include:

- card_id
- title
- source_spec_id
- publish_ready_input_status
- present_in_github_main
- present_in_production_data
- visible_or_reachable_in_ui
- render_status
- duplicate_status
- schema_status
- verification_outcome
- notes

Allowed verification_outcome values:

- verified_in_main_and_production
- verified_in_main_not_production
- verified_in_data_not_ui
- missing_from_main
- missing_from_production
- rendering_issue
- duplicate_or_schema_issue

Each issue_manifest item must include:

- issue_type
- severity
- affected_card_ids
- affected_system
- evidence
- recommended_next_action

Allowed issue_type values:

- pr_not_merged
- merge_commit_not_on_main
- unexpected_file_diff
- main_data_invalid
- count_mismatch
- duplicate_id
- duplicate_url
- schema_type_drift
- sort_failure
- vercel_deployment_pending
- vercel_deployment_failed
- production_data_stale
- production_data_missing_cards
- cache_or_cdn_issue
- app_runtime_failure
- card_rendering_issue
- network_error
- regression_detected
- other

Final status rules:

Set final_status to one of:

- production_verified
- deployment_pending
- deployment_failed
- data_not_updated
- cache_or_cdn_issue
- app_runtime_failure
- rendering_issue
- production_hold
- needs_redeploy
- needs_rollback_review

Set production_verified=true only when final_status=production_verified.

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

3. PR merge confirmation

   - PR merged: yes/no
   - merge commit on main: yes/no
   - changed files
   - unexpected files, if any

4. GitHub main data verification

   - main cards count
   - expected final count
   - count formula result
   - new card IDs present
   - duplicate ID/URL results
   - schema/type result
   - latest-first sort result

5. Vercel production deployment verification

   - deployment status
   - deployment commit
   - deployment time relative to merge
   - production URL status

6. Production data endpoint verification

   - normal /data/cards.json status
   - cache-busted /data/cards.json status
   - production count
   - production data matches main: yes/no
   - stale/cache issue: yes/no

7. Production UI smoke test

   - app load result
   - card rendering result
   - new cards visible/reachable result
   - runtime/network errors
   - layout/rendering issues

8. Regression check

   - existing cards render
   - filters/tabs/search safe
   - category/region/signal safe
   - no obvious duplicate in UI

9. Card verification ledger summary

   - merged publish_ready count
   - verified in main
   - verified in production data
   - verified in UI
   - missing from main
   - missing from production
   - rendering issues

10. Issue manifest

   If any issue exists:
   - issue type
   - severity
   - affected card IDs
   - recommended next action

11. Final decision

   If all gates pass, state:

   “Production verification PASS. The merged cards are live in GitHub main, production /data/cards.json, and the production app UI.”

   If any gate fails, state:

   “Production verification is not complete. Do not treat this run as production_verified until the listed issues are resolved and verification is rerun.”

12. Explicit boundary statement

   Include this exact statement:

   “Production verification checked GitHub main, Vercel production, production /data/cards.json, and production UI rendering. It did not create new cards, rewrite card content, modify fact_sources, or force production success.”

13. Next-step statement

   If production_verified:

   “The run is production-verified. Future work should start as a new run or a separate improvement task.”

   If deployment_pending:

   “Wait for deployment completion or trigger a redeploy, then rerun production verification.”

   If deployment_failed or app_runtime_failure:

   “Investigate deployment/runtime logs before declaring completion. Consider rollback only if production availability or data integrity is affected.”

   If data_not_updated or cache_or_cdn_issue:

   “Resolve data freshness/cache issue, then rerun production verification.”

## Operational integrated rule — production verification lineage consistency check

Production verification verifies deployment and rendering. It must also confirm that the cards being verified are the exact `publish_ready[]` cards that passed final QC lineage gates and GitHub merge prep.

Before reporting production success, verify that the GitHub merge prep output includes:

- `github_merge_prep_status = PASS` or equivalent;
- `final_qc_lineage_gate_confirmed = true`, or equivalent;
- `publish_ready_true_despite_lineage_fail_count = 0`;
- the merged card IDs and event fingerprints match the Final QC `publish_ready[]` set exactly.

If production contains a new card that was not in the lineage-valid `publish_ready[]` set, classify as:

- `production_hold_unapproved_card_present`

If a lineage-invalid card appears in GitHub main or production, production verification must not return PASS. Report:

```json
{
  "status": "PRODUCTION_HOLD_LINEAGE_INVALID_CARD_PRESENT",
  "recommended_next_call": "production remediation decision"
}
```

Do not treat a rendered card as valid merely because it appears in production.

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

## Operational integrated rule — production verification next-call recommendation

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

1. If final_status = production_verified:
   - recommended_next_call = "retrospective or new run"
   - recommended_prompt_id = "Prompt 1.1 or Prompt 0.0"

2. If final_status = deployment_pending:
   - recommended_next_call = "wait for deployment completion or trigger redeploy if authorized, then rerun production verification"
   - recommended_prompt_id = "Prompt 0.9"

3. If final_status is deployment_failed, data_not_updated, cache_or_cdn_issue, app_runtime_failure, rendering_issue, production_hold, needs_redeploy, or needs_rollback_review:
   - recommended_next_call = "production remediation decision"
   - recommended_prompt_id = "Prompt 1.0"

Do not proceed automatically to remediation, redeploy, rollback, or new run.
Stop after production verification.

Do not proceed to rollback, redeploy, or new run unless the user explicitly instructs it.

---

## Execution-anchor and selector-lineage safety overlay — 2026-05-05

This overlay is downstream of the Stage A safe-selector integrated rule. It prevents post-acceptance steps from laundering a weak or superseded Stage A/B/C lineage into publish-ready or production status.

Terminology lock:

- Do not use or enforce a format-based hard-exclude rule.
- Product, demo, PoC, component, interview, commentary, roundup, speech, or personnel formats are not automatically rejected by format alone.
- They are subject to a strict-pass presumption block: without a concrete fresh execution anchor, they must not have entered `strict_passed_spec[]`; if they did, the downstream step must hold, reject, or return the item to the appropriate prior stage rather than polishing it forward.
- Concrete execution anchors include signed contract, binding customer order, offtake, commercial deployment, field installation, commissioning, production start, facility opening, certification, regulatory decision, public funding approval, binding procurement, measurable capacity addition, safety recall/regulatory action, or named customer adoption.

### Production lineage verification gate

Production verification must confirm that the cards actually merged and rendered in production are the same `publish_ready[]` cards that passed Final QC and GitHub Merge Prep lineage gates.

For every merged card, verify where possible:

- card ID exists in GitHub main `public/data/cards.json`;
- the same card ID appears in GitHub Merge Prep output;
- `publish_ready=true` is preserved;
- evidence/content/source-claim flags are preserved;
- no card from `review_pool`, `support_source_only`, `rejected`, `draft_blocked`, or superseded lineage appears in production;
- format-risk cards still preserve the narrowed stage/caveat language approved by Final QC.

If production contains a card from invalid or superseded lineage, return:

```text
status: production_hold
issue_type: selector_lineage_or_anchor_integrity_issue
```

Do not call production verified until the lineage issue is remediated.

### Output requirement

Add to Production Verification JSON:

```json
"production_lineage_gate": {
  "merged_cards_lineage_checked_count": 0,
  "invalid_lineage_in_production_count": 0,
  "format_risk_cards_render_checked_count": 0,
  "decision": "pass|production_hold"
}
```

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

# 11_PROMPT_0_9_Production_Verification.md — Source Diversity source-diversity integrated rule

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

## Production source-rendering verification

Production verification must inspect rendered source drawers for sampled cards, including:

- one card with multiple claims from one URL;
- one card with at least two independent source domains;
- one card with official + independent + context roles;
- one validated single-source exception, if any.

Verify:

1. same canonical URL appears once;
2. all claim/quote entries remain visible under that source group;
3. label shows `출처 N곳 · 근거 M개`;
4. quote date equals article publication date;
5. `fetched_at` and `checked_at` are not displayed;
6. each original link opens the correct source;
7. production data preserves diversity/synthesis metadata.

A rendered but source-inflated or fetch-date-displaying card is not production-verified.

Use statuses:

```text
PRODUCTION_HOLD_SOURCE_GROUPING_FAILED
PRODUCTION_HOLD_VISIBLE_SOURCE_DATE_FAILED
PRODUCTION_HOLD_SOURCE_DIVERSITY_METADATA_MISSING
```

    Stop after production verification.

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


## PR/Production extra

Before merge, re-run metadata blocker scans against the exact PR head, not only local candidate files.
