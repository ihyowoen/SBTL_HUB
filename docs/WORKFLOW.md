<!-- REPLACE_ALL_CLEAN_VERSION: LLM_PROMPT_GITHUB_CANONICAL_V1_SOURCE_DIVERSITY_IB_CODEX -->
<!-- Generated KST: 2026-07-08T21:33:49.790191+09:00 -->
<!-- This file is a full clean replacement file. It is not a patch stub. -->

# SBTL_HUB 운영 워크플로

## 0. 목적

이 문서는 SBTL_HUB 카드 생성부터 production verification까지의 표준 운영 흐름을 잠근다.

핵심 원칙:

1. 생산 파이프라인과 편집 판단을 분리한다.
2. raw/final input을 바로 merge하지 않는다.
3. cards.json은 최신 main 기준에서만 수정한다.
4. 배포 확인은 main + production 기준으로 본다.
5. 신규 카드는 full schema only.
6. Prompt C accepted는 publish-ready가 아니다.

## 1. 시스템 이해

- 표시층: `public/data/cards.json`, `public/data/faq.json`, `public/data/tracker_data.json`
- 편집층: final input, A/B/C outputs, accepted/revise/rejected states
- 병합층: addable/publish-ready payload only
- Git/배포층: GitHub main, Vercel production

## 2. 금지

- raw final input 직접 merge
- 오래된 cards.json 덮어쓰기
- branch preview만 보고 완료 판단
- expected count를 맞추기 위해 중복/weak card 강제 추가
- rejected/revise/review_pool을 post-acceptance에서 조용히 되살리기
- Prompt C accepted를 publish-ready로 부르기

## 3. 표준 흐름

0.0 Run intake / preflight
0.1 Stage A selector
0.2 Stage B evidence package + draft
0.3 Stage C fact-safe validation
0.2R/0.3R revise loops, if authorized
0.4 full baseline revalidation
0.5 evidence completeness/source-claim QC
0.6 content polish/language terminology
0.7 final publish-readiness QC
0.8 GitHub merge prep
0.9 production verification
1.0 remediation, if needed
1.1 retrospective

## 3A. Per-stage prompt-read gate — HARD RULE

> R3C_P02 integrated rule (run 20260516_012728 retrospective). 모든 stage 에 무조건 적용.

각 stage N 을 실행하기 **전에**:

1. 해당 stage 의 프롬프트 파일 `0N_PROMPT_*.md` 를 **실제로 열어서 읽는다.**
2. 그 프롬프트가 요구하는 **출력 schema 를 stage 출력에 복창**한다 (요구 필드 목록 명시).
3. stage 출력에 `stage_prompt_file` 와 `stage_prompt_sha256` 를 기록한다.

검증:
- stage 출력이 프롬프트가 요구한 필드를 포함하지 않으면 그 stage 는 **무효**다.
- 프롬프트 파일을 읽지 않고 이전 run 기억으로 실행한 stage 는 run 전체를 무효화한다.

근거: run 20260516_012728 1차 시도는 01_/02_/03_ 프롬프트를 읽지 않고
이전 run 기억으로 실행 → 모든 하류 결함의 단일 상류 원인 (PV_008).

## 4. State ladder

```text
accepted_fact_safe
→ addable_merge_safe
→ evidence_complete
→ source_claim_covered
→ content_enriched
→ language_terminology_polished
→ publish_ready
→ github_merge_ready
→ production_verified
```

Do not collapse these states.

## 4A. Named-stage discipline — HARD RULE

> R3C_P05 integrated rule (run 20260516_012728 retrospective).

- ladder 의 각 state transition 은 **해당 named stage 프롬프트가 생성**해야 한다.
- ad-hoc / 이름 바꾼 / 병합한 pass 가 named stage 를 대체할 수 없다.
- red-team·deep-dive 리뷰는 stage **내부의 추가 검사**이지, stage 자체의 대체가 아니다.
- 어떤 named stage 도 건너뛰거나 다른 pass 로 갈음할 수 없다. 건너뛴 stage 가 있으면
  그 state 는 생성되지 않은 것이고 하류는 진행 불가다.

근거: run 20260516_012728 1차 시도는 Stage C 를 이름 없는 pass 로 대체 →
`accepted_fact_safe` state 가 생성된 적 없음 (PV_004).

## 5. Stage A default

Stage A must produce partitioned review pools and output-schema-complete artifacts as required by `docs/PROMPT_ABC_DEFAULT_MODE.md` and `docs/run_prompts/01_PROMPT_0.1_Stage_A.md`.

## 6. Stage B default

Stage B uses only Stage A `strict_passed_spec[]` from a valid Stage A artifact set.

## 7. Stage C default

Stage C uses only Stage B `draft_cards[]` and evidence packages.

## 8. Post-acceptance default

0.4+ stages may use only the precise upstream state allowed by their prompt. Review pools, support-only, rejected, draft-blocked, and deferred items are excluded unless a separate authorized review loop is performed.

## 9. GitHub / production

GitHub main sync and production verification are mandatory before claiming completion.


---

# Structural Default Run Contract — 2026-05-06

This section is part of the replace-all structural default package. It exists to make the required 8 GitHub workflow docs consistent with the current run prompt files.

## A. Source-prompt provenance

Every Stage A output must record:

- `source_prompt_file`
- `source_prompt_sha256`
- `source_prompt_version`
- `source_prompt_authority`
- `source_prompt_provenance_status`

The structural default version is:

```text
structural_default_review_pool_partition_20260506
```

or a later compatible version.

## B. Stage A validity gate

Stage A may recommend Stage B only if all are PASS:

- `source_prompt_provenance_status`
- `stage_a_validity_status`
- `artifact_consistency_status`
- `csv_schema_status`
- `review_pool_partition_status`
- `review_pool_carry_forward_ledger_status`
- `strict_pass_gate_metadata_status`
- `baseline_duplicate_screen_status`
- `summary.ledger_matches_story_count`

If any value is missing or not PASS, Stage A must not recommend Stage B.

## C. Review-pool partition default

`review_pool[]` must not be an undifferentiated operational bucket.

Every input story or candidate must be accounted for in the source-universe ledger.

A genuinely out-of-scope, duplicate, consumer-noise, local-noise, stale, source-broken, or non-SBTL item may be closed as rejected or support-only, but only with an item-specific reason code and ledger row.

Every non-strict candidate that is not item-specifically closed as rejected or support-only must enter exactly one of:

1. `candidate_review_pool[]`
   - plausibly cardable after bounded source/date/duplicate clarification
2. `watchlist_context_pool[]`
   - useful for context/background but not a current-run card candidate
3. `reject_or_support_only_pool[]`
   - too weak for candidate review, but may be rejected or used only as support

The legacy aggregate `review_pool[]` may exist for compatibility, but each item must include:

- `review_pool_partition`
- `review_pool_partition_reason`
- `promotion_precondition`
- `bounded_review_question`
- `recommended_next_action`

Unpartitioned review_pool output is invalid. Missing rejected/support-only ledger rows are also invalid.

## D. Strict-pass gate

A story may enter `strict_passed_spec[]` only if all six conditions pass:

1. SBTL_HUB lane fit
2. concrete fresh execution anchor or accepted data/policy release anchor
3. source direction compatibility
4. freshness / staleness confidence
5. baseline duplicate/follow-up risk acceptable
6. independent card value and full-schema viability

Each strict item must include:

- `strict_pass_gate.status`
- `strict_pass_gate.all_six_conditions_passed`
- `strict_pass_gate.execution_anchor_type`
- `strict_pass_gate.execution_anchor_strength`
- `strict_pass_gate.format_risk_tags`
- `strict_pass_gate.notes`

## E. Format-risk handling

Product/demo/PoC/component/interview/commentary/roundup/speech/personnel/partnership formats are not automatically rejected by format alone.

They are blocked from strict-pass unless a concrete execution anchor is present.

Allowed concrete execution anchors include:

- signed contract
- binding customer order
- offtake
- price floor or risk-sharing facility
- commercial deployment
- field installation
- commissioning
- production start
- facility opening
- certification or regulatory approval
- regulatory decision/enforcement
- public funding approval
- binding procurement
- measurable capacity addition
- safety recall/regulatory action
- named customer adoption
- named deployment site with measurable pilot scale/duration/objective
- factory/project construction, suspension, expansion, or final investment decision
- official or reported data release when the card is clearly a data/policy/statistics event

## F. CSV required schema

Stage A decisions CSV must include at minimum:

- `story_id`
- `region`
- `original_triage_status`
- `status_detail`
- `stage_a_bucket`
- `ledger_decision`
- `headline`
- `reason`
- `baseline_relation`
- `duplicate_risk`
- `staleness_decision`
- `event_date`
- `source_tier_estimate`
- `source_access_risk`
- `format_risk_tags`
- `execution_anchor_type`
- `execution_anchor_strength`
- `strict_pass_gate_status`
- `strict_pass_gate_reason`
- `review_pool_partition`
- `review_pool_partition_reason`
- `promotion_precondition`
- `bounded_review_question`
- `recommended_next_action`

If required columns are missing:

```text
csv_schema_status = FAIL
stage_a_validity_status = FAIL
status = BLOCKED_STAGE_A_CSV_SCHEMA_INCOMPLETE
no Stage B recommendation
```

## G. Stage B blocker

Stage B must block before fetch or draft if any Stage A gate is missing or not PASS:

- `stage_a_validity_status`
- `artifact_consistency_status`
- `csv_schema_status`
- `review_pool_partition_status`
- `review_pool_carry_forward_ledger_status`
- `strict_pass_gate_metadata_status`
- `baseline_duplicate_screen_status`
- `summary.ledger_matches_story_count`

Blocked state:

```text
BLOCKED_STAGE_A_ARTIFACT_OR_PARTITION_INVALID
```

## H. Post-acceptance laundering prevention

No later stage may promote any of the following unless an explicit, current-run authorized promotion/review loop has occurred:

- Stage A `review_pool[]`
- `candidate_review_pool[]`
- `watchlist_context_pool[]`
- `reject_or_support_only_pool[]`
- `support_source_only[]`
- `rejected[]`
- Stage B `draft_blocked[]`
- Stage C `deferred_review_pool[]`

The normal ladder remains:

```text
accepted_fact_safe
→ addable_merge_safe
→ evidence_complete
→ source_claim_covered
→ content_enriched
→ language_terminology_polished
→ publish_ready
```

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


## Stage A boundary — no-fetch handling for v4 rescue/review rules

Stage A is selector-only. The v4 rescue and review rules do not authorize Stage A to perform external web search, article body fetch, source_quote generation, fact_sources generation, or card drafting.

For Stage A only:

- official_source_checked = NOT_APPLICABLE_STAGE_A_NO_FETCH
- alternate_tier1_tier2_checked = NOT_APPLICABLE_STAGE_A_NO_FETCH
- source_strength_review_log = NOT_APPLICABLE_STAGE_A_NO_FETCH

Stage A satisfies v4 by partitioning and documenting bounded review paths, not by fetching.

If a Stage A item looks promising but not strict-pass ready, Stage A must not reject it simply because verification is not yet complete. It must place it in the correct bounded pool with:

- review_pool_partition
- review_pool_partition_reason
- promotion_precondition
- bounded_review_question
- recommended_next_action

If dropped_review_treasure_hunt is triggered, Stage A must account for sampled and non-sampled treasure candidates as required by REVIEW_POOL_AND_TREASURE_MUST_BE_REVIEWED_RULE_20260507_V4.


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


## Operational integrated rule — STAGE_A_FALSE_POSITIVE_QA_REGRESSION_EXAMPLES_20260508_V6

This v6 integrated rule converts clean-v5 Stage A false-positive patterns into reusable QA regression examples.

Stage A reports must include at least three `strict_false_positive_risk_examples[]` when any non-strict pools are non-empty. These examples should explain why superficially relevant items were not strict-passed.

Required example categories when present in the source universe:

```text
generic_ai_platform_without_battery_grid_ess_execution_anchor
consumer_or_component_product_publicity_without_deployment_anchor
general_finance_insurance_macro_or_oil_lng_without_direct_battery_grid_ess_anchor
local_event_or_expo_participation_without_operational_signal
research_or_explainer_without_fresh_execution_anchor
personnel_or_litigation_item_without strategic battery/ESS/material execution consequence
```

Each example must include:

```json
{
  "story_id": "...",
  "headline": "...",
  "negative_filter_applied": "...",
  "strict_false_positive_risk_reason": "...",
  "routed_to": "candidate_review_pool|watchlist_context_pool|reject_or_support_only_pool|rejected|support_source_only",
  "reopen_condition": "...|not_applicable"
}
```

This integrated rule must not cause automatic rejection of adjacent AI/grid/robotics/power items. If an item is weak but plausibly relevant after bounded clarification, route it to `candidate_review_pool[]` with a promotion precondition rather than deleting it.

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


# Baseline & Push Integrity Rule — 20260513

이번 운영 패치는 두 가지 실패 모드를 차단한다:

1. **Baseline drift on session resume** — compacted summary 의 baseline 수치를 actual GitHub main 상태와 비교 없이 신뢰하는 케이스
2. **cards.json push corruption** — 의도치 않은 file overwrite/truncate 가 검증 없이 production 으로 흘러가는 케이스

## A. Session Resume Baseline Validation — HARD RULE

매 새 turn 시작 시 / compacted resume 직후 / 가설 기반 분석 직전에 다음을 수행한다:

1. GitHub MCP `get_file_contents` 로 `public/data/cards.json` 의 현재 metadata 확인 (size, blob SHA)
2. 다음 두 수치를 비교:
   - 컨텍스트 / compacted summary 에 기록된 `baseline_count` 또는 `cards in main`
   - actual GitHub main 의 cards.json 실제 카드 수 (size 와 blob SHA 로 추정 가능; 정확 카운트는 file 직접 parse)
3. 차이가 의미있는 수준 (예: > 10% 또는 절대값 > 50) 이면 **STOP** — user 에게 baseline 재확인 요청; downstream 단계 (0.4 / 0.5 / 0.7) 진행 금지
4. compacted summary 의 수치는 "기록" 으로 받되 "현재 상태" 로 자동 신뢰하지 않는다

근거: run 20260512_134524 retrospective. compacted summary 가 "main = 23 cards" 로 기록했으나 실제 main 은 707 cards 였음. 가설 기반으로 0.4/0.5 단계 진행하다가 발견.

## B. cards.json Push Integrity — HARD RULE

`public/data/cards.json` 을 commit/push 하기 전에 다음 routine 을 **모두** 수행한다:

```bash
# 1. JSON 정합성 + cards 배열 수 = total
python3 -c "
import json, os
p='public/data/cards.json'
d=json.load(open(p))
assert len(d['cards'])==d['total'], f\"mismatch: cards={len(d['cards'])} total={d['total']}\"
assert d['total']>=700, f\"suspicious low total: {d['total']}\"
sz=os.path.getsize(p)
assert sz>1_000_000, f\"file too small: {sz} bytes (expected > 1 MB)\"
print(f'PASS — total={d[\"total\"]} cards, size={sz:,} bytes')
"

# 2. 위 명령이 PASS 되었을 때만 git add/commit/push 진행
```

Push 완료 후 **60초 이내**에 GitHub MCP `get_file_contents` 로 새 commit SHA 의 cards.json metadata 확인:

- size 가 push 직전 로컬 size 와 일치하는지 (±10% 이내; CRLF/LF 변환 고려)
- 의도한 cards 수 변화량이 반영됐는지 (예: +15 cards 추가했으면 size 도 그에 맞게 증가)

불일치 시 즉시 user 에게 보고하고 revert 또는 follow-up 결정.

근거: run 20260512_134524 codex_followup_v2 push 과정에서 cards.json 이 한 차례 27,659 bytes (cards 배열 0개) 로 truncate 되어 PR head 에 commit 됨. 다음 iteration 의 size audit 으로 발견 후 복구.

## C. 적용 범위

- 본 rule 은 Prompt 0.4 / 0.5 / 0.7 / 0.8 / 0.9 의 시작 step (required-doc check 직후) 와 0.8 / 0.9 의 push 단계에 자동 적용된다.
- 위반 시 해당 stage 의 boundary_statement 에 "baseline_validation_skipped" 또는 "push_integrity_skipped" 를 명시 기록한다.

## FIX-007 — Shared schema contract and stage-exit conformance check

All stages must reference `SCHEMA_CONTRACT_STAGE_LINEAGE.md`.

Each named stage must run or explicitly satisfy a stage-exit artifact conformance check before recommending the next stage. Missing required fields must stop the stage with:

```text
BLOCKED_STAGE_OUTPUT_SCHEMA_NONCOMPLIANT
```

Do not wait until Prompt 0.4 to discover Stage A/B lineage omissions.

# WORKFLOW.md — Source Diversity source-diversity integrated rule

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

## Workflow integration

Mandatory flow:

```text
Stage A: preserve same-event source cluster and diversity path
Stage B: bounded multi-source discovery + evidence package + synthesis draft
Stage C: recompute independence + fact-safe decision
0.4: preserve duplicate-event reinforcement
0.5: hard source-identity/diversity/claim-coverage QC
0.6: visible-field synthesis and density preservation
0.7: final source-diversity publish gate
0.8: metadata/UI merge readiness
0.9: production source-grouping/date rendering verification
```

No later stage may repair an earlier-stage source loss silently. Return to the earliest defective
named stage.

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
