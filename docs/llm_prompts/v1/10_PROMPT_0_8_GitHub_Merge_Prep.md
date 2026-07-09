<!-- REPLACE_ALL_CLEAN_VERSION: LLM_PROMPT_GITHUB_CANONICAL_V1_SOURCE_DIVERSITY_IB_CODEX -->
<!-- Generated KST: 2026-07-08T21:33:49.790191+09:00 -->
<!-- This file is a full clean replacement file. It is not a patch stub. -->

Prompt 0.8v — Reusable Default / Replace All / GitHub Merge Preparation & PR Candidate

Proceed to GitHub merge preparation and PR candidate creation only.

Use the current run’s final publish-readiness QC output as the only candidate input universe for this step.

This step starts after final publish-readiness QC.

Do not continue from, trust, import, integrated rule, or reuse any previous merge file, PR candidate, GitHub-ready file, branch payload, manually integrated ruleed cards.json, or production file unless the user explicitly declares it as current-run authoritative input.

Use GitHub main as the merge source of truth.

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
- no GitHub merge preparation performed

Do not infer replacement rules from memory.
Do not use archived docs.
Do not use branch-only docs.
Do not use local snippets unless the user explicitly provides them as current-run authoritative docs.

Input files:

- Final QC JSON: {{FINAL_QC_RESULTS_JSON}}
- Publish-ready payload: {{PUBLISH_READY_PAYLOAD_JSON}}
- Final QC report: {{FINAL_PUBLISH_READINESS_QC_REPORT_MD}}
- Final hold manifest: {{FINAL_HOLD_MANIFEST_JSON}}
- Current GitHub main baseline: public/data/cards.json
- Run tag: {{RUN_TAG}}
- Run label: {{RUN_LABEL_KST}}
- Target repo: ihyowoen/SBTL_HUB
- Target branch base: main
- Target data path: public/data/cards.json

Required input rule:

This step requires a valid final QC output from the same run.

The final QC JSON must include:

- required_docs_check
- run_tag
- run_label
- publish_ready[]
- final_qc_hold[]
- final_qc_rejected[]
- needs_return_to_evidence_qc[]
- needs_return_to_content_polish[]
- needs_github_main_sync[]
- review_pool_deferred[]
- final_qc_accounting_matches_input_count
- final_gate_summary
- hard_fail_summary

If Final QC JSON is missing, invalid, incomplete, not from the same run, or has accounting mismatch, stop and report:

- status: BLOCKED_FINAL_QC_INVALID
- reason: [...]
- no GitHub merge preparation performed


## Upstream lineage integrity gate

This prompt is downstream of selector, evidence, content, and/or production gates. It must not repair or launder an invalid upstream lineage.

Before doing any work, validate that the current-run final QC output carries a lineage integrity statement from the immediately previous step.

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


For Prompt 0.8 specifically, final QC is the only upstream step allowed to assign publish_ready=true. It must prove that:
- every input card is state=publish_ready
- GitHub-ready or PR_CANDIDATE naming is used only if GitHub main sync passed
- format-risk / execution-anchor metadata was preserved or explicitly marked not_applicable
- no publish_ready card depends on a failed strict-pass gate, missing execution anchor, or superseded lineage

If any required lineage field is missing, false, contradictory, stale, not from the same run, or inconsistent with the candidate payload, stop immediately and report:

- status: BLOCKED_UPSTREAM_LINEAGE_INVALID
- reason: [...]
- invalid_or_missing_lineage_fields: [...]
- no GitHub merge preparation performed

Do not infer lineage validity from memory.
Do not continue just because candidate counts look correct.
Do not use this prompt to fix Stage A/B/C selection defects or post-QC evidence defects.

Candidate input rule:

Only final QC publish_ready[] may enter GitHub merge preparation.

Do not include:

- final_qc_hold
- final_qc_rejected
- needs_return_to_evidence_qc
- needs_return_to_content_polish
- needs_github_main_sync unless the issue is resolved by this step’s main sync
- review_pool_deferred
- content_hold_claim_narrowing_needed
- content_hold_language_issue
- content_hold_schema_issue
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

If any non-publish_ready item is mixed into the candidate input, exclude it and report it as mixed_input_excluded.


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


GitHub merge-prep lineage guard:

Before preparing any PR candidate or merged cards file, verify that final QC publish_ready[] includes lineage proof for:

- Stage A V2 selector PASS
- Stage A artifact consistency PASS
- Stage B source verification performed
- Stage C accepted_fact_safe only, not publish_ready
- baseline revalidation passed
- evidence completeness and source-claim coverage passed
- content/language polish passed
- final QC publish_ready=true assigned only after all gates

If lineage proof is missing for any publish_ready card, exclude it from merge prep and report publish_ready_lineage_hold. Do not merge it into public/data/cards.json.

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

This step prepares a GitHub-safe PR candidate by merging publish_ready cards into the current GitHub main baseline.

This step may decide:

- github_main_sync_passed
- github_merge_ready
- pr_candidate_ready
- merge_prep_hold
- needs_revalidation_against_updated_main
- id_assignment_required
- id_collision_hold
- duplicate_hold_after_main_sync
- schema_runtime_hold

This step must not:

- create new editorial candidates
- rescue held/rejected cards
- change source facts
- add new sources
- rewrite visible fields
- perform content enrichment
- perform evidence QC
- force expected final count
- bypass GitHub main
- merge into an old baseline
- call a file PR_CANDIDATE unless GitHub main sync and final gates pass

State ladder reminder:

accepted_fact_safe
→ addable_merge_safe
→ evidence_complete
→ source_claim_covered
→ content_enriched
→ language_terminology_polished
→ publish_ready
→ github_merge_ready
→ PR candidate
→ production verified

This step may move publish_ready cards to github_merge_ready / pr_candidate_ready only after GitHub main sync gate passes.

GitHub main sync gate:

Before preparing any PR candidate:

1. Fetch latest GitHub main.
2. Read current main public/data/cards.json.
3. Confirm current main baseline count.
4. Compare current main baseline with the baseline used in prior steps.
5. Re-run duplicate ID / URL / canonical URL / event fingerprint checks against current main.
6. Re-run latest-first sort check.
7. Re-run schema/runtime check on the merged candidate.
8. Confirm no main drift invalidates the publish_ready candidates.

If current GitHub main differs materially from the baseline used in final QC:

- do not merge blindly
- re-run main-sync duplicate/event/ID checks
- if conflict exists, hold affected cards
- if conflict is material and cannot be resolved in this step, stop and report:
  - status: BLOCKED_MAIN_DRIFT_REVALIDATION_REQUIRED
  - affected_cards: [...]
  - no PR candidate created

Allowed GitHub actions in this step:

Only after all gates pass:

- create a new branch from latest main
- update public/data/cards.json
- commit only intended files
- open a PR

If the user did not explicitly ask to open a PR in this step, prepare files and report ready-to-PR status without opening PR.

If this prompt is being run in an environment with GitHub write access and the user’s instruction includes PR creation, then create the branch and PR.

Branch naming rule:

Use a deterministic branch name:

- data/add-publish-ready-cards-{{RUN_TAG}}

If branch already exists:

- do not overwrite blindly
- use:
  - data/add-publish-ready-cards-{{RUN_TAG}}-r2
  - data/add-publish-ready-cards-{{RUN_TAG}}-r3

Commit message rule:

Use:

- data: add publish-ready cards for {{RUN_TAG}}

PR title rule:

Use:

- data: add publish-ready SBTL_HUB cards for {{RUN_TAG}}

PR body must include:

- run_tag
- run_label
- baseline source
- main baseline count before merge
- publish_ready input count
- actually added count
- hold count after main sync
- final cards count
- files changed
- QC report summary
- confirmation that only publish_ready cards were used
- confirmation that rejected/hold/review items were excluded
- confirmation that evidence_complete/source_claim_covered/content_enriched/language_polished/publish_ready all passed
- confirmation that GitHub main sync gate passed
- confirmation that production verification is still required after merge

Candidate merge rules:

Use only publish_ready[] items.

For each publish_ready card:

- preserve visible fields from final QC
- preserve fact_sources
- preserve urls
- preserve related
- preserve evidence flags
- preserve publish_ready=true
- preserve final_qc_gates
- do not rewrite title/sub/gate/fact/implication
- do not alter source_quote
- do not add new claims

Allowed modifications:

- assign or normalize production id according to CARD_ID_STANDARD, only if required
- add merge metadata fields only if compatible with current schema
- remove temporary draft-only fields if they are not part of production schema and would break runtime
- ensure arrays/types are valid
- sort latest-first

Production schema rule:

The merged card must remain full schema compatible.

Required card fields:

- id
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

Allowed extra metadata fields only if they do not break frontend/runtime and are already tolerated by current cards.json schema.

If extra Stage fields create schema/runtime drift, remove or move them to QC report, not production cards.json.

ID assignment rule:

Use docs/CARD_ID_STANDARD.md.

ID format:

- YYYY-MM-DD_REGION_NN

Rules:

- date = event date, not publication date
- REGION = card region
- NN = 2-digit zero-padded sequence within date+region
- do not reuse existing NN
- do not rename historical legacy IDs
- do not silently change IDs after assignment
- if ID collision occurs, stop or assign next available NN only if the event date/region are confirmed and no collision remains

If production ID is missing:

- assign ID after checking current main date+region group
- record assigned_id
- record id_assignment_reason

If production ID exists:

- verify it does not collide with current main
- verify date/region match ID format unless legacy exception applies
- if collision exists, hold the card as id_collision_hold unless safe reassignment is explicitly allowed by CARD_ID_STANDARD and recorded

Duplicate/event check after main sync:

For every candidate, check against current main:

- exact ID duplicate
- exact URL duplicate
- canonical URL duplicate
- normalized title duplicate
- actor + asset/policy + event_type + event_date duplicate
- event fingerprint duplicate
- already covered by broader card
- translated repost
- follow-up not distinct

If duplicate found:

- do not merge that card
- move to duplicate_hold_after_main_sync
- record matched main card ID and reason

If uncertain:

- move to needs_revalidation_against_updated_main
- do not merge that card

Sort rule:

Final merged cards.json must be sorted latest-first.

Sort keys:

1. date descending
2. signal priority: top → high → mid
3. region order: KR → US → CN → JP → EU → GL → other
4. id ascending

If the existing production sort uses a repo-specific helper or documented sort, follow the repo’s current standard if it conflicts with the above.

Do not change existing baseline card content except for deterministic full-file sort if necessary.

File-change discipline:

Default allowed file change:

- public/data/cards.json

Do not modify:

- src/*
- docs/*
- package files
- scripts/*
- public/data/faq.json
- public/data/tracker_data.json
- other data files

unless the user explicitly requests it.

If any unexpected file is changed, stop and report:

- status: BLOCKED_UNEXPECTED_FILE_DIFF
- unexpected_files: [...]

Validation checks:

Before PR candidate is created, run or simulate the following checks:

1. JSON parse valid
2. cards array exists
3. final count = current_main_count + actually_added_count
4. no duplicate IDs
5. no duplicate URLs
6. no duplicate canonical URLs when canonicalization is possible
7. no duplicate event fingerprints among new and baseline
8. all new cards are publish_ready=true
9. all new cards have evidence_complete=true
10. all new cards have source_claim_covered=true
11. all new cards have content_enriched=true
12. all new cards have language_terminology_polished=true
13. all new cards have fact_sources
14. no URL-only fact_sources
15. no source_quote hard-fail status
16. no rejected/hold/review cards mixed in
17. full schema fields present
18. implication is array with 2+ items
19. urls is array
20. related is array
21. latest-first sort passes
22. changed files are expected only
23. GitHub main sync gate passes

If any hard validation fails, do not create PR candidate.

Output state definitions:

1. github_merge_ready

Use when:

- publish_ready input card passed current main sync
- no duplicate/ID/schema/runtime issue remains
- card can be merged into public/data/cards.json
- production verification still pending

2. pr_candidate_ready

Use when:

- github_merge_ready cards exist
- merged cards.json candidate is valid
- expected changed files are clean
- GitHub branch/commit/PR is ready or created
- no blocking validation issue remains

3. duplicate_hold_after_main_sync

Use when:

- card was publish_ready but current main already contains same event/URL/fingerprint
- do not merge

4. id_collision_hold

Use when:

- card ID collides with current main or internal batch
- ID cannot be safely assigned/resolved in this step

5. needs_revalidation_against_updated_main

Use when:

- GitHub main changed materially
- duplicate/follow-up relation is uncertain
- baseline drift affects addability
- card must return to baseline revalidation

6. schema_runtime_hold

Use when:

- card data would break production schema/runtime
- required fields/types are invalid
- temporary fields cannot be safely normalized

7. merge_prep_hold

Use when:

- issue is fixable but not safe to merge now
- no PR candidate should be created for that item

Accounting rule:

Every final QC publish_ready item must appear exactly once in one of:

- github_merge_ready
- duplicate_hold_after_main_sync
- id_collision_hold
- needs_revalidation_against_updated_main
- schema_runtime_hold
- merge_prep_hold

No silent skip is allowed.

Report:

- publish_ready_input_count
- github_merge_ready_count
- duplicate_hold_after_main_sync_count
- id_collision_hold_count
- needs_revalidation_against_updated_main_count
- schema_runtime_hold_count
- merge_prep_hold_count
- outcome_total_count
- merge_prep_accounting_matches_input_count
- actually_added_count
- current_main_count_before
- final_cards_count_after

If accounting does not match, stop and report:

- status: BLOCKED_MERGE_PREP_ACCOUNTING_MISMATCH

Output files:

If PR candidate is ready:

1. github_merge_prep_results_{{RUN_TAG}}.json
2. github_merge_prep_report_{{RUN_TAG}}.md
3. github_merge_prep_decisions_{{RUN_TAG}}.csv
4. pr_candidate_payload_{{RUN_TAG}}.json
5. cards_json_candidate_{{RUN_TAG}}.json
6. merge_prep_hold_manifest_{{RUN_TAG}}.json

If PR candidate is not ready:

1. github_merge_prep_results_{{RUN_TAG}}.json
2. github_merge_prep_report_{{RUN_TAG}}.md
3. github_merge_prep_decisions_{{RUN_TAG}}.csv
4. merge_prep_hold_manifest_{{RUN_TAG}}.json
5. github_sync_or_revalidation_required_manifest_{{RUN_TAG}}.json

Do not use production-verified naming in this step.

Do not say production is complete.

JSON output requirements:

The main JSON must include:

- stage
- run_tag
- run_label
- repo
- base_branch
- target_branch
- target_data_path
- final_qc_input_file
- publish_ready_payload_file
- current_main_cards_source
- current_main_count_before
- publish_ready_input_count
- github_merge_ready_count
- duplicate_hold_after_main_sync_count
- id_collision_hold_count
- needs_revalidation_against_updated_main_count
- schema_runtime_hold_count
- merge_prep_hold_count
- outcome_total_count
- merge_prep_accounting_matches_input_count
- actually_added_count
- final_cards_count_after
- github_main_sync_gate
  - status
  - main_sha_before
  - baseline_count_matched
  - drift_detected
  - drift_resolution
- required_docs_check
  - docs_expected
  - docs_read_from_github_main
  - docs_missing_or_unreadable
  - status
- validation_summary
- changed_files
- branch_info
- pr_info
- github_merge_ready[]
- duplicate_hold_after_main_sync[]
- id_collision_hold[]
- needs_revalidation_against_updated_main[]
- schema_runtime_hold[]
- merge_prep_hold[]
- mixed_input_excluded[]
- decision_ledger[]

Each github_merge_ready item must include:

- state: github_merge_ready
- previous_state: publish_ready
- original_draft_id
- source_spec_id
- assigned_or_verified_id
- id_assignment_reason
- region
- date
- cat
- sub_cat
- signal
- title
- urls
- event_fingerprint
- duplicate_check
- schema_runtime_check
- sort_check
- publish_ready: true
- github_ready: true
- pr_candidate_ready: true/false
- production_verified: false
- notes

Each duplicate_hold_after_main_sync item must include:

- state: duplicate_hold_after_main_sync
- previous_state: publish_ready
- original_draft_id
- source_spec_id
- duplicate_reason
- matched_main_card_id
- matched_main_card_title
- matched_main_card_url
- event_fingerprint
- recommended_next_action

Each id_collision_hold item must include:

- state: id_collision_hold
- previous_state: publish_ready
- original_draft_id
- source_spec_id
- attempted_id
- collision_with
- safe_next_available_id, if determinable
- recommended_next_action

Each needs_revalidation_against_updated_main item must include:

- state: needs_revalidation_against_updated_main
- previous_state: publish_ready
- original_draft_id
- source_spec_id
- reason
- affected_baseline_cards
- required_revalidation
- recommended_next_action

Each schema_runtime_hold item must include:

- state: schema_runtime_hold
- previous_state: publish_ready
- original_draft_id
- source_spec_id
- schema_issue
- affected_fields
- required_fix
- recommended_next_action

Each merge_prep_hold item must include:

- state: merge_prep_hold
- previous_state: publish_ready
- original_draft_id
- source_spec_id
- hold_reason
- affected_fields
- recommended_next_action

Each decision_ledger row must include:

- original_draft_id
- source_spec_id
- prior_state
- merge_prep_outcome
- assigned_or_verified_id
- duplicate_status
- id_status
- schema_status
- github_main_sync_status
- merged_into_candidate
- reason
- notes

Validation summary must include:

- json_valid
- cards_array_valid
- current_main_count_before
- publish_ready_input_count
- actually_added_count
- final_cards_count_after
- final_count_formula_pass
- duplicate_id_count
- duplicate_url_count
- duplicate_canonical_url_count
- duplicate_event_fingerprint_count
- schema_missing_required_fields_count
- schema_type_drift_count
- non_publish_ready_mixed_count
- evidence_flags_valid_count
- source_hard_fail_count
- latest_first_sort_pass
- unexpected_file_diff_count
- github_main_sync_pass

Report requirements:

The Markdown report must include:

1. Run metadata

   - final QC input file
   - publish-ready payload file
   - repo
   - base branch
   - target branch
   - target data path
   - run tag
   - run label

2. Required docs check

   - list all 8 required docs
   - confirm each was read from GitHub main
   - if any doc was not read, this step must not proceed

3. GitHub main sync gate

   - current main SHA
   - current main cards count
   - prior baseline count used in final QC
   - drift detected: yes/no
   - drift handling result
   - sync gate pass/fail

4. Candidate input summary

   - publish_ready input count
   - mixed input excluded count
   - only publish_ready cards used: yes/no
   - held/rejected/review cards excluded: yes/no

5. Merge-prep summary table

   - publish_ready input count
   - github_merge_ready count
   - duplicate_hold_after_main_sync count
   - id_collision_hold count
   - needs_revalidation_against_updated_main count
   - schema_runtime_hold count
   - merge_prep_hold count
   - outcome total count
   - accounting match: yes/no
   - actually added count
   - current main count before
   - final cards count after

6. github_merge_ready manifest

   For each ready item:
   - assigned/verified ID
   - source_spec_id
   - short event anchor
   - region / cat / signal
   - duplicate check result
   - schema/runtime result
   - publish_ready status
   - production_verified=false

7. Hold manifest

   Include:
   - duplicate_hold_after_main_sync
   - id_collision_hold
   - needs_revalidation_against_updated_main
   - schema_runtime_hold
   - merge_prep_hold

   For each:
   - source_spec_id
   - reason
   - matched main card, if any
   - required fix
   - recommended next action

8. Validation summary

   Include:
   - JSON validity
   - count formula
   - duplicate ID/URL/canonical/event result
   - schema/type drift result
   - latest-first sort result
   - source hard-fail result
   - unexpected file diff result
   - changed files list

9. Branch / PR result

   If PR created:
   - branch name
   - commit SHA
   - PR number
   - PR URL
   - files changed

   If PR not created:
   - reason
   - ready-to-PR status
   - next required action

10. Explicit boundary statement

   Include this exact statement:

   “GitHub merge preparation used only final QC publish_ready cards and the latest GitHub main public/data/cards.json. It did not add new candidates, rescue held/rejected cards, rewrite visible fields, change fact_sources, or force expected final count. Production verification is still required after merge.”

11. Next-step statement

   If PR was created:

   “The next step is PR review, merge, and production verification.”

   If PR candidate is ready but PR was not created:

   “The next step is to create a PR from the prepared candidate, then run production verification after merge.”

   If PR candidate is blocked:

   “No PR candidate should be created until the listed holds are resolved.”

## Operational integrated rule — GitHub merge prep upstream-lineage guard

GitHub merge preparation must not merge cards whose final QC publish_ready status was produced from invalid or incomplete upstream lineage.

Before preparing a PR candidate, verify that Final QC JSON includes:

- `final_qc_status = PASS`;
- `upstream_lineage_publish_gate_status = PASS`, or equivalent;
- `publish_ready_true_despite_lineage_fail_count = 0`;
- `final_qc_hold_selection_lineage_gap[]` and `final_qc_hold_execution_anchor_gap[]` were excluded from `publish_ready[]`;
- every `publish_ready[]` card has a traceable chain from Stage A strict gate through Stage B, Stage C, 0.4, 0.5, 0.6, and 0.7.

If Final QC lacks lineage gate proof or contains any publish_ready item with lineage/execution-anchor gaps, stop and report:

```json
{
  "status": "BLOCKED_FINAL_QC_LINEAGE_INVALID",
  "no_github_merge_prep_performed": true,
  "recommended_next_call": "return to final QC or rerun upstream lineage"
}
```

Do not use GitHub merge prep to remove, rewrite, or silently repair these cards. Exclude or block only.

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

## Operational integrated rule — GitHub merge prep next-call recommendation

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

1. If PR was created:
   - recommended_next_call = "PR review, merge, then production verification"
   - recommended_prompt_id = "Prompt 0.9 after PR is merged"

2. If PR candidate is ready but PR was not created:
   - recommended_next_call = "create PR from prepared candidate, then production verification after merge"

3. If PR candidate is blocked:
   - recommended_next_call = "resolve merge prep holds"
   - do_not_proceed_to = "production verification"

Do not proceed automatically to production verification.
Stop after GitHub merge preparation.

Do not proceed to production verification until the PR is merged and I explicitly say “production verification”.

---

## Execution-anchor and selector-lineage safety overlay — 2026-05-05

This overlay is downstream of the Stage A safe-selector integrated rule. It prevents post-acceptance steps from laundering a weak or superseded Stage A/B/C lineage into publish-ready or production status.

Terminology lock:

- Do not use or enforce a format-based hard-exclude rule.
- Product, demo, PoC, component, interview, commentary, roundup, speech, or personnel formats are not automatically rejected by format alone.
- They are subject to a strict-pass presumption block: without a concrete fresh execution anchor, they must not have entered `strict_passed_spec[]`; if they did, the downstream step must hold, reject, or return the item to the appropriate prior stage rather than polishing it forward.
- Concrete execution anchors include signed contract, binding customer order, offtake, commercial deployment, field installation, commissioning, production start, facility opening, certification, regulatory decision, public funding approval, binding procurement, measurable capacity addition, safety recall/regulatory action, or named customer adoption.

### Required upstream lineage gate for GitHub Merge Prep

Before preparing any PR candidate, verify that `FINAL_QC_RESULTS_JSON` includes:

- `selector_lineage_final_gate.upstream_lineage_passed: true`
- `selector_lineage_final_gate.artifact_consistency_passed: true`
- `selector_lineage_final_gate.superseded_lineage_detected: false`
- `final_qc_accounting_matches_input_count: true`
- `publish_ready[]` only from current-run validated lineage

If missing or failed, stop and report:

```text
status: BLOCKED_FINAL_QC_LINEAGE_INVALID
reason: [...]
no GitHub merge preparation performed
```

### Merge-prep no-laundering rule

GitHub Merge Prep must not convert content publish-ready into GitHub-ready if any upstream selector/evidence/content lineage is missing, superseded, or unverifiable.

If a `publish_ready` item lacks the lineage/anchor fields introduced by the safe-selector integrated rule, treat it as `merge_prep_hold`, not `github_merge_ready`, unless the user explicitly declares that the run predates the safe-selector integrated rule and authorizes manual review.

### Output requirement

Add to GitHub Merge Prep JSON:

```json
"lineage_merge_gate": {
  "final_qc_lineage_passed": true,
  "publish_ready_lineage_checked_count": 0,
  "publish_ready_lineage_hold_count": 0,
  "github_ready_allowed": true
}
```

Final override: if `lineage_merge_gate.github_ready_allowed != true`, do not emit PR_CANDIDATE or GitHub-ready filenames.

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


## Operational integrated rule — GITHUB_MAIN_LARGE_BASELINE_FALLBACK_LOCK_20260508_V6

This v6 integrated rule clarifies the large-baseline fallback observed in clean-v5 validation: GitHub connector may return repository/SHA metadata while failing to expose the full `public/data/cards.json` body.

If GitHub main `public/data/cards.json` body is unreadable, empty, truncated, inaccessible, or cannot be parsed, Prompt 0.8 must keep GitHub-ready states blocked.

Allowed local fallback path:

A local merge candidate may be prepared only if the user provides all of the following:

```text
1. A freshly downloaded cards.json explicitly labeled GitHub-main-equivalent baseline.
2. The baseline card count.
3. Latest cards commit SHA, GitHub file timestamp, or explicit user check timestamp.
4. User statement that the uploaded file represents current GitHub main.
5. Acknowledgment that github_ready and pr_candidate_ready remain false until independent GitHub main or production endpoint verification succeeds.
```

0.8 output status must distinguish:

```text
LOCAL_CANDIDATE_PREPARED_BUT_BLOCKED_GITHUB_MAIN_SYNC_UNVERIFIABLE
GITHUB_MAIN_SYNC_CONFIRMED
BLOCKED_GITHUB_MAIN_SYNC_UNREADABLE
```

If fallback is used, output must include:

```json
"github_main_unreadable_fallback": {
  "used": true,
  "uploaded_baseline_file": "...",
  "uploaded_baseline_count": 0,
  "user_declared_main_equivalent": true,
  "commit_or_check_reference": "...",
  "github_ready": false,
  "pr_candidate_ready": false,
  "manual_upload_or_independent_verification_required": true
}
```

Prompt 0.8 must never label a local candidate as GitHub-ready, PR-ready, merge-ready-on-main, or production-ready when GitHub main body sync is unverified.


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


## Prompt 0.8 source diversity preservation check

GitHub merge prep must verify that every `publish_ready[]` card carries final source diversity status from 0.7.

Required preservation fields per incoming card:

- `source_diversity_status`
- `source_diversity_gate_status`
- `source_url_urls_sync_status`
- `single_source_exception`, if applicable

If any publish_ready card lacks these fields, report:

- `status = BLOCKED_SOURCE_DIVERSITY_METADATA_MISSING`
- no GitHub-ready or PR-candidate labeling

0.8 must not fix source diversity. Return to 0.7/0.5 as appropriate.


## Operational integrated rule — Wrapper metadata sync HARD RULE — 20260514

Run 20260513_083924 retrospective 에서 발견된 gap: codex_followup_v3 fix 가 cards array (745→744) 와 top-level total 은 업데이트했지만 wrapper 의 보조 metadata 4개 필드가 stale 상태로 남음 (new_count: 23, merge_qc_scope: '23 new × 745 merged', accepted_content_enriched_count: 23, final_cards_published: 23). 수학 일관성 깨짐 (722 + 23 != 744). Codex P2 review (PR #124) 가 catch.

### HARD RULE — wrapper metadata sync

0.8 초기 merge prep, 그리고 모든 codex_followup fix-up 시점에 cards array 가 변경되면 wrapper 의 모든 derived count 필드를 동기화한다:

**필수 동기화 필드** (cards array 변경 시):
- `total`: `len(cards)`
- `new_count`: 신규 카드 수 (initial drafted; post-fixup: 변경 반영)
- `accepted_content_enriched_count`: `new_count` 와 동일
- `merge_qc_scope`: `"{new_count} new cards × {total} merged total"` 형식 재생성
- `updated`: 현재 timestamp

**보존 필드** (history):
- `baseline_count`: stage A 시점 baseline (변경 안 함)

**Nested wrapper 점검**:
- `merge_prep_{run_tag}_*.final_cards_published`: `new_count` 와 동일
- recursive 검사: `*_count`, `*_scope`, `*_published` 필드 모두

### Pre-push integrity check (확장)

`docs/WORKFLOW.md` 의 기존 push routine 에 다음 assertion 추가:

```bash
python3 -c "
import json
d = json.load(open('public/data/cards.json'))

# 기존 check (P_004)
assert len(d['cards']) == d['total']
assert d['total'] >= 700

# P_008 신규 check
assert d['baseline_count'] + d['new_count'] == d['total'], \
    f'math mismatch: {d["baseline_count"]} + {d["new_count"]} != {d["total"]}'

# nested check
for k in d:
    if k.startswith('merge_prep_') and isinstance(d[k], dict):
        if 'final_cards_published' in d[k]:
            assert d[k]['final_cards_published'] == d['new_count'], \
                f'nested final_cards_published mismatch in {k}'

print(f'PASS — math consistent: {d["baseline_count"]} + {d["new_count"]} = {d["total"]}')
"
```

위 명령이 통과한 경우에만 git add/commit/push 진행. 실패 시 STOP + sync fix.

### 적용 범위

- 0.8 초기 merge prep
- codex_followup v1/v2/v3/v4 등 모든 fix-up round
- 사용자 로컬 push 직전
- GitHub MCP 를 통한 직접 commit 시점

### 예방 효과

- Codex P2 stale-metadata review round (이번 run 의 v4 같은 케이스) 제거
- UI/downstream consumer 가 보는 카운트 일관성 보장

# 10_PROMPT_0_8_GitHub_Merge_Prep.md — Source Diversity source-diversity integrated rule

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

## GitHub merge-prep preservation gate

Before preparing the replacement file or PR, verify that serialization preserves:

- all `fact_sources[]` rows;
- canonical source URLs;
- source roles and unique contributions;
- source publication dates and audit timestamps;
- source diversity counts and status;
- source synthesis audit;
- validated exception metadata.

Recalculate the recent-batch diversity metrics after merge. Any card that falls below its Final QC
state because metadata was lost must be held.

The merge package must also include the UI integrated rule or confirmed existing UI implementation that:

- groups repeated claims by canonical URL;
- displays `출처 N곳 · 근거 M개`;
- displays article publication date;
- keeps fetch/check timestamps non-visible.

Block with:

```text
BLOCKED_MERGE_SOURCE_DIVERSITY_METADATA_LOSS
BLOCKED_MERGE_UI_SOURCE_GROUPING_NOT_READY
```

    Stop after merge preparation. Do not merge or write GitHub without explicit authorization.

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
