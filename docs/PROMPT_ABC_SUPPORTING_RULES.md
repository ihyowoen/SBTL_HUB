<!-- REPLACE_ALL_CLEAN_VERSION: LLM_PROMPT_GITHUB_CANONICAL_V1_SOURCE_DIVERSITY_IB_CODEX -->
<!-- Generated KST: 2026-07-08T21:33:49.790191+09:00 -->
<!-- This file is a full clean replacement file. It is not a patch stub. -->

# PROMPT ABC — Supporting Rules

## 0. Purpose

This document defines judgment criteria for the SBTL_HUB A/B/C pipeline.

If this document conflicts with `docs/FACT_DISCIPLINE.md`, Fact Discipline prevails.

## 1. Signal Rubric

Signal is `top | high | mid`.

Axis A — Market size / impact:
- 2: revenue impact ≥ US$1B, GWh-scale capacity, or material market impact
- 1: revenue impact US$100M–1B, MWh-scale project, or material strategic signal
- 0: below

Axis B — Policy / regulation:
- 2: government/federal/EU mandate enacted, material tariff/subsidy/regulatory change
- 1: draft policy, consultation, guideline, standardization approval, subnational decision
- 0: no policy dimension

Axis C — Technology / supply chain:
- 2: mass production start, factory groundbreaking, M&A, first public technical standard, major capacity execution
- 1: pilot, prototype, MOU, joint R&D, product launch with execution anchor
- 0: none

Mapping:

| Total | signal |
|---|---|
| ≥5 | top |
| 3–4 | high |
| 1–2 | mid |
| 0 | not cardable |

Tier 3 single-source items cannot receive `top`.

## 2. Source Tier Map

Tier 1:
- government/regulator official announcements
- listed-company IR/filings/official newsroom
- Reuters, Bloomberg, FT, WSJ, Nikkei
- verified industry specialty press / primary research reports

Tier 2:
- national economic/industry press
- credible industry specialty press
- public reports from major agencies/consultancies

Tier 3:
- aggregators, blogs, social media quotes, small sole-source outlets, PR distribution pages unless original issuer is identified

## 3. Pipeline Scope

Covered lanes:

- battery cell/pack/materials
- ESS
- EV
- charging
- cathode/anode/separator/electrolyte/pouch film/critical minerals
- recycling/EOL/second-life
- power grid when linked to storage, EV, renewables, or data-center load
- industrial policy affecting the above
- adjacent supply-chain structures

Adjacent topics are included only with a direct lane hook:

- renewable energy: only when storage/grid economics or BESS is concrete
- AI/data centers: only when power demand, grid structure, battery/ESS procurement, or data-center energy infrastructure is concrete
- robotics: only with battery/charging/power interface relevance
- general finance/geopolitics: only with direct battery/materials/ESS/EV/charging/grid execution

## 4. Discard / hold categories

Reject or support-only when the item is:

- generic landing/static product page
- reference/wiki/evergreen explainer
- event participation/publicity without operational signal
- routine personnel appointment without strategic restructuring
- unverified rumor
- pure opinion with no factual anchor
- stale republication without fresh follow-up
- out of SBTL_HUB lane
- too weak to support a full-schema card

Do not automatically reject by format alone; apply the strict-pass presumption block in the structural default contract.

## 5. Evidence package preparation

Before Prompt B drafts, each strict spec must receive an evidence package based on fetched body-level or official-material sources.

Extract only:

- numbers and quantities
- named entities
- direct quotes
- explicit comparisons/context stated in source

Do not extract reporter speculation or implied context as fact anchors.

## 6. Framing direction lock

The card direction must match the source direction.

Reject or revise when:

- semi-solid becomes solid-state
- pilot/MOU becomes commercial deployment
- consideration/plan becomes confirmed execution
- company statement becomes industry consensus
- corporate investment becomes policy-driven outcome without policy source

## 7. Date and staleness

`date` is event day, not publication day.

Staleness thresholds:

- ≤7 days: fresh
- 8–30 days: stale-warm, requires fresh-signal justification
- >30 days: stale, default reject unless distinct fresh follow-up is documented

Stage A pre-checks staleness from metadata/previews; Stage B confirms by fetched source; Stage C validates.

## 8. Stage B self-verification

After drafting each card, Stage B asks:

1. Does fact direction match source?
2. Does title compress fact faithfully?
3. Does implication remain observational?

If uncertain, flag for Stage C.

## 9. Stage C verification

Stage C checks source direction, fact/source alignment, quote quality, claim coverage, category/region/signal, staleness, and language/tone.


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

Stage B must also block if Stage A provides these only inside nested objects,
Markdown, CSV, or status-gate summaries but not as top-level JSON contract fields:

- `review_pool_partition_summary`
- `review_pool_carry_forward_ledger_status`
- `strict_passed_spec[].staleness_decision`

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

`hard_reject_basis` must be one of those enumerated basis values. Do not use
category/risk labels such as `general_politics`, `politics`, `memorial`,
`sports`, `low_signal`, or `not_interesting` as the hard-reject basis. Preserve
those labels only in reason/detail/risk metadata, and map the actual closure
basis to `out_of_scope`, `not_sbtl_lane`, `consumer_noise`, or another
enumerated basis as appropriate.

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

## CARD_CLAIM_DIVERSITY_AUDIT_RULE_20260507_V7

This rule adds an editorial-quality gate after evidence safety has already been established. It must never override `FACT_DISCIPLINE.md`.

The workflow must audit not only whether each card is fact-safe, but also whether each publish-ready card answers a distinct, source-supported strategic question.

Visible-field writing persona for Stage B drafting, Prompt 0.6 Content Polish,
and Prompt 0.7 Final QC:

Cards must read as Korean SBTL strategy cards written by a top-tier
investment-banking sector veteran with 30 years of battery, ESS, EV,
energy-infrastructure, and industrial supply-chain deal experience. The prose
must be commercially literate, compressed, skeptical, and decision-useful.

This persona never authorizes unsupported investment, valuation, deal,
financing, market-share, causal, or beneficiary claims. It governs only
source-locked framing, information density, and strategic angle selection.

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

<!-- INTEGRATED_RULE_BEGIN: ENTITY_ALIAS_MAP_AUTHORITY_20260514_v2 -->
## P_010 — entity_alias_map authoritative table — 20260514_v2

`entity_alias_map.json` 은 project 의 source-of-truth multi-language alias 테이블.
Stage A event-fingerprint 계산 시 cross-language entity normalization 의 권위 자료.

### 구조

각 entry 는 canonical form + aliases + type + parent (있을 시):

```json
{
  "<canonical_string>": {
    "canonical": "<canonical_string>",
    "aliases": ["alias1", "alias2", "..."],
    "type": "company" | "person" | "research_org" | "place" | "tech_term" | "product",
    "parent": "<optional parent canonical>",
    "parent_region": "<optional regional context for places>"
  }
}
```

### 등록 우선 entry (run 20260513_083924, 20260513_165421 catch 기반)

| canonical | aliases (한·영·중·일) | type |
|---|---|---|
| SoftBank | 소프트뱅크, ソフトバンク, 软银 | company |
| BloombergNEF | BNEF, 블룸버그NEF, 블룸버그 NEF | research_org |
| CATL | 宁德时代, 닝더시대, Contemporary Amperex Technology | company |
| BYD | 비야디, 比亚迪, BYD Auto | company |
| Sakai | 사카이市, 사카이시, Sakai City | place (Osaka prefecture) |
| Ningde | 닝더, 宁德, Ningde City | place |
| Ford Energy | 포드 에너지, Ford 에너지 사업부, Ford Pro Energy | company_division (parent: Ford) |
| Tesla | 테슬라, 特斯拉 | company |
| Toyota | 토요타, トヨタ, 丰田 | company |
| Hyundai | 현대, 现代 | company |
| XPeng | 샤오펑, 小鹏汽车 | company |
| Geely | 지리, 吉利 | company |
| Xiaomi | 샤오미, 小米 | company |
| Zeekr | 지커, 极氪 | company |
| NIO | 니오, 蔚来 | company |
| EVE Energy | 亿纬锂能, 이브 | company |
| Alsym Energy | 알심, Alsym | company |
| Hisai | 海博思创, 하이보스창, 하이박스창 | company |
| QingTao Energy | 清陶能源, 칭타오에너지 | company |
| Ronbay | 容百科技, 룽바이 | company |
| Hunan Yuneng | 湖南裕能, 후난위넝 | company |
| Tianqi Lithium | 天齐锂业, 톈치리튬 | company |
| Tianci | 天赐材料, 톈츠 | company |
| Rongjie | 融捷股份, 룽제 | company |
| Zhongke Electric | 中科电气, 중커전기 | company |
| Zhongke Xingcheng | 中科星城, 중커싱청 | company (parent: Zhongke Electric) |
| Xinyangfeng | 新洋丰, 신양펑 | company |
| GEM Co | 格林美, 거린메이 | company |
| CEEC | 中国能建, 중국에너지건설 | company |
| CSG | 南方电网, 남방전력망 | company |
| Sungrow | 阳光电源, 선그로우 | company |
| Pylon Technologies | 派能科技 | company |
| Narada | 雄韬股份 | company |

### 매칭 정책 — case-insensitive, whitespace-tolerant

> R3C_P07 integrated rule (run 20260516_012728 retrospective).

- **ASCII alias 매칭은 word-boundary 매칭**을 쓴다 (raw substring 금지).
  - `SoftBank Corp` 는 `SoftBank` 에 매핑되지만, `Genex` / `Envision Energy` 안의
    `Energy` 같은 부분 문자열 일치는 매칭으로 보지 않는다.
- **CJK(한자·일본어) alias 는 substring 매칭 유지** — CJK 는 띄어쓰기가 없어 word-boundary 가 성립하지 않는다.
- Korean spacing variation 허용: `블룸버그NEF` ↔ `블룸버그 NEF`.
- 한자 simplified ↔ traditional 양방향 매핑 (필요 시 추가 entry).
- **generic-token blocklist** — 아래 토큰은 그 자체만으로는 entity-overlap 점수 계산에서 제외한다
  (다른 고유 토큰과 결합됐을 때만 유효):
  `Energy, Power, Battery, BESS, ESS, New Energy, Solar, Grid, Storage, Tech, Materials, Group, Holdings`.

근거: run 20260516_012728 0.4 단계에서 P_010 이 alias `EVE Energy` 의 `Energy` 를
`Genex` / `Envision Energy` 안에서 substring 으로 매칭 → GL_03~GL_05 를 중복으로 false-flag.
word-boundary recheck 시 0 matches 로 확인됨 (무관한 별개 이벤트).
`entity_alias_map.json` 의 `_meta.policy` 도 이 규칙과 동기화 상태로 유지한다.

### 유지보수

- run 마다 retrospective 에서 새 cross-language pair 발견 시 PR 로 alias_map 갱신
- alias_map 자체는 baseline cards.json 의 wrapper 와는 분리된 별도 project 파일
- Stage A 호출 시 load, runtime 변경 금지 (run 내 일관성)

## FIX-009 — URL canonicalization must preserve article IDs

For duplicate/event-fingerprint URL normalization, preserve article identity query parameters and remove tracking parameters only.

Preserve examples: `idxno`, `aid`, `articleid`, `articleId`, `no`, `articleView`, `newsid`, `seq`, `id`.

Remove examples: `utm_*`, `fbclid`, `gclid`, `ref`, `source`, `campaign`, `spm`.

Do not strip entire query strings for Korean CMS/news URLs where the query string carries the article identifier.

# PROMPT_ABC_SUPPORTING_RULES.md — Source Diversity source-diversity integrated rule

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

## Canonicalization and independence rules

Canonicalization must preserve article identity parameters and remove tracking parameters only.

Independence review must consider:

- canonical domain;
- editorial owner or corporate parent;
- press-release source;
- wire-service attribution;
- identical or near-identical body text;
- publication time and syndication pattern;
- mobile/AMP/RSS/print variants.

Two domains are not automatically independent. One domain is not automatically non-diverse when it
contains truly separate official and editorial entities, but such exceptions require explicit owner
analysis and are not the default.

Maintain an optional `source_owner_alias_map` separately from cards data. Do not infer ownership
solely from substrings.

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
