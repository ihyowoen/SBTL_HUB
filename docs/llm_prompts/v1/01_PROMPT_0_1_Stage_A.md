<!-- REPLACE_ALL_CLEAN_VERSION: LLM_PROMPT_GITHUB_CANONICAL_V1_SOURCE_DIVERSITY_IB_CODEX -->
<!-- Generated KST: 2026-07-08T21:33:49.790191+09:00 -->
<!-- This file is a full clean replacement file. It is not a patch stub. -->

Prompt 0.1v — Reusable Default / Replace All / Strict Stage A Mode

Start a new SBTL_HUB card-generation run from Stage A.

This is a fresh run.

Do not continue from, trust, import, integrated rule, or reuse any previous Stage A/B/C/post-QC outputs unless the user explicitly declares them as current-run authoritative inputs.

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
- no Stage A work performed

Do not infer replacement rules from memory.
Do not use archived docs.
Do not use branch-only docs.
Do not use local snippets unless the user explicitly provides them as current-run authoritative docs.

Important scope note:

docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md must be read before the run because it defines downstream state discipline and naming restrictions.

However, Stage A must not perform post-acceptance QC.
Post-acceptance QC applies only after Prompt C has produced accepted_fact_safe cards.

Input files:

- Source input: {{SOURCE_INPUT_FILE}}
- Baseline cards: {{BASELINE_CARDS_SOURCE}}
- Baseline source declaration: {{BASELINE_SOURCE_DECLARATION}}
- Run tag: {{RUN_TAG}}
- Run label: {{RUN_LABEL_KST}}
- Source universe: final_news_llm_input.stories[]

Required input rule:

The source input must contain the current-run story universe and run metadata.

The baseline source must be explicitly declared.

Allowed baseline sources:

1. GitHub main → public/data/cards.json
2. A user-uploaded baseline explicitly declared by the user as the current-run baseline
3. A local final candidate explicitly declared by the user as the current-run baseline

Default baseline rule:

If the user does not explicitly declare a user-uploaded baseline or local final candidate as the current-run baseline, use GitHub main → public/data/cards.json.

If the baseline source is unclear, stop and report:

- status: BLOCKED_BASELINE_AMBIGUOUS
- no Stage A work performed

Do not substitute a prior merged file, prior payload, helper file, branch-only file, previous-run output, or memory-based baseline.

If the baseline is not GitHub main, record that GitHub main sync gate will still be required before PR/merge.

Metadata derivation rule:

Derive the following directly from the current source input file:

- story_count
- KEEP count
- REVIEW count
- STEP2_PENDING count
- DROPPED count
- INPUT_ONLY count
- excluded_story_count
- integrity mode
- recommended_for
- generated_kst
- run_tag, if encoded in the source input
- run_label, if encoded in the source input
- schema version

If required metadata is missing or internally inconsistent, stop and report:

- status: BLOCKED_INPUT_SCHEMA_INVALID
- missing_or_inconsistent_fields: [...]
- no Stage A work performed

Core reset rule:

This run starts from Stage A.

Do not reuse:

- previous dry-run outputs
- previous Stage A outputs
- previous Stage B drafts
- previous Stage C accepted outputs
- previous accepted payloads
- previous addable payloads
- previous post-QC outputs
- previous PR candidates
- previous manually integrated files

unless the user explicitly declares that exact file as a current-run authoritative input.

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

Critical workflow rules:

1. KEEP is not an automatic editorial pass.

   Prompt A must rerun lane-sanity inside KEEP before producing strict_passed_spec.

2. Stage A is selector-only.

   Stage A must not:
   - write cards
   - fetch article bodies
   - perform external web search
   - generate source_quote
   - generate fact_sources
   - generate title/sub/gate/fact/implication copy
   - decide accepted_fact_safe
   - decide addable_merge_safe
   - decide evidence_complete
   - decide source_claim_covered
   - decide content_enriched
   - decide language_terminology_polished
   - decide publish_ready

3. Stage A may use only:
   - current source input file
   - active baseline
   - upstream metadata
   - triage labels
   - headline
   - site
   - URL
   - source_packets metadata
   - upstream content previews
   - usable_text
   - integrity labels

   These may be used only for:
   - candidate selection
   - lane-sanity
   - relevance screening
   - staleness pre-check
   - duplicate-risk screening
   - outcome ledger creation

   These upstream fields are not final evidence and must not be treated as publishable fact support.

4. Web search / fetch boundary:

   Stage A:
   - external web search prohibited
   - article body fetch prohibited
   - source_quote generation prohibited
   - fact_sources generation prohibited

   Stage B:
   - web_fetch begins only for Stage A strict_passed_spec[]
   - every strict_passed_spec must receive an evidence package before any card draft is created
   - if evidence cannot be secured, the spec must be draft_blocked, not forced into a card

   Stage C:
   - limited spot-check may be used only for QC

   Post-acceptance:
   - final web QC may be used only for verification, conflict detection, duplicate detection, source accessibility, and source-strength checking
   - do not use web search as silent content enrichment

5. Stage A must separate editorial buckets into:

   - legacy_keep
   - strict_passed_spec
   - needs_review / review_pool
   - rejected
   - existing_reinforcement
   - support_source_only
   - dropped_treasure_hunt_result

6. Stage A ledger decision and editorial bucket must be separated.

   Ledger decision may use:
   - passed
   - merged
   - discarded
   - existing_reinforcement

   Editorial bucket must use:
   - legacy_keep
   - strict_passed_spec
   - needs_review / review_pool
   - rejected
   - existing_reinforcement
   - support_source_only
   - dropped_treasure_hunt_result

7. Stage B must use only Stage A strict_passed_spec unless explicitly instructed otherwise.

   Stage A needs_review / review_pool must not be auto-fetched, auto-promoted, or treated as Stage B input.

8. Stage B terminology discipline:

   Use only:
   - source_availability
   - fetch_coverage
   - evidence_package
   - evidence_candidate
   - fact_source_candidate
   - draft_card
   - draft_blocked

   Do not use in Stage B:
   - evidence_complete
   - source_claim_covered
   - addable_merge_safe
   - publish_ready
   - final
   - PR_CANDIDATE
   - GitHub-ready
   - merge-ready

9. Stage C accepted means accepted_fact_safe only.

   accepted_fact_safe is not:
   - addable
   - addable_merge_safe
   - evidence_complete
   - source_claim_covered
   - content_enriched
   - language_terminology_polished
   - publish_ready

10. The required downstream state ladder is:

   accepted_fact_safe
   → addable_merge_safe
   → evidence_complete
   → source_claim_covered
   → content_enriched
   → language_terminology_polished
   → publish_ready

   Do not collapse these states.

11. Full baseline revalidation decides addable/hold only.

   It must reset publish_ready=false for all surviving addable cards.

   Publish_ready may be assigned only after surviving addable cards pass:
   - evidence completeness QC
   - source-claim coverage QC
   - content enrichment QC
   - language/terminology polish QC
   - final publish-readiness QC
   - GitHub main sync gate, if applicable

12. Hard evidence fail conditions for downstream stages include:

   - source_quote missing
   - source_quote is headline-only
   - source_quote is RSS-only
   - source_quote is snippet-only
   - source_quote is listing-title text
   - source_quote equals article title
   - source_quote merely paraphrases article title without body-level or official-material support
   - source_quote_status is missing
   - source_quote_status is unknown
   - source_quote_status is headline_only
   - source_quote_status is snippet_only
   - source_quote_status is not_generated
   - source_quote_status is not_generated_no_direct_quote_extraction
   - fact_sources is URL-only
   - claim is copied from headline rather than supported by body or official material
   - claim is a label rather than a concrete factual claim
   - missing source_name
   - missing evidence_role
   - missing supports
   - single-source card relies on headline-only evidence
   - visible-field core claim is not covered by fact_sources
   - source_quote does not support the specific claim it is attached to

13. No FINAL / PR_CANDIDATE / GitHub-ready / merge-ready / publish-ready naming is allowed unless both merge safety and evidence completeness pass and the downstream QC report supports publish_ready=true.

   Stage A output must not use final-publication naming.

14. Duplicate/event screening must compare candidate stories against the active baseline using:

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
   - existing card theme
   - event fingerprint

15. Staleness pre-check is mandatory in Stage A.

   Use upstream metadata and available text signals only.

   Do not fetch article bodies.

   If event_date is unclear, mark staleness as unknown and keep that uncertainty in the spec or review_pool.

   Do not invent event dates.

16. Stage A spec uncertainty terminology:

   Use:
   - needs_review / review_pool

   Do not use:
   - revise_required

   revise_required is reserved for Stage C card/draft-level issues that are fixable without reopening candidate selection.

   If Stage A spec is uncertain, stale-warm, source-weak, lane-ambiguous, or duplicate-risk uncertain, place it in needs_review / review_pool or reject it.


16A. Product/demo/PoC/component/interview/roundup strict-pass presumption block:

   Do not hard-exclude a story solely because its format is product news, demo, PoC, component launch, interview, event roundup, commentary, explainer, speech, personnel item, or partnership/integration coverage.

   Instead, apply a strict-pass presumption block:

   - If no concrete execution anchor is visible in upstream metadata, source_packets, usable_text, or the available content preview, the story must not enter strict_passed_spec[].
   - Route strategically relevant but incomplete format-risk items to needs_review / review_pool.
   - Route background-only format-risk items to support_source_only.
   - Reject only when the item is promotional, stale, out-of-scope, evidence-poor, duplicate, generic/static, internally contradictory beyond repair, or lacks SBTL_HUB decision value.

   Concrete execution anchors include:

   - signed contract
   - binding customer order
   - offtake agreement
   - price floor or binding risk-sharing facility
   - commercial deployment
   - field installation
   - commissioning
   - production start
   - facility opening
   - certification or regulatory approval
   - regulatory decision or enforcement action
   - public funding approval
   - binding procurement
   - measurable capacity addition
   - safety recall or regulatory safety action
   - named customer adoption
   - named deployment site with measurable pilot scale, duration, and objective
   - factory/project groundbreaking or final investment decision

   For interview or roundup formats, evaluate the fresh event inside the article, not the wrapper format.

   - If an interview contains a new or newly surfaced contract, price floor, government support, investment, partnership, facility, production, regulatory, or named deployment claim, evaluate that event as the candidate anchor.
   - If a roundup contains multiple events, do not pass the roundup as a generic card. Split or route only the specific fresh event anchor if it is independently cardable.

   Stage A must record format-risk handling in each affected strict_passed_spec or review_pool item using:

   - format_risk_tags
   - execution_anchor_type
   - execution_anchor_strength
   - strict_pass_gate

   strict_pass_gate.status must be one of:

   - pass
   - blocked_to_review_pool
   - blocked_to_support_source_only
   - blocked_to_rejected

   A format-risk item may enter strict_passed_spec only when strict_pass_gate.status = "pass" and execution_anchor_strength is "strong" or "moderate".

   Do not use the phrases hard-exclude, automatic exclusion, or categorical exclusion in Stage A reasoning for these formats. The correct reasoning is: strict-pass blocked unless a concrete fresh execution anchor is visible.

17. Stage B spec failure terminology:

   If Stage B later discovers that a strict_passed_spec is unsupported, stale, source-direction mismatched, or lacks body-level/official-material evidence, mark it draft_blocked.

   Do not force a draft.

18. Stage C correction terminology:

   Use revise_required only when a drafted card has fixable card-level issues.

   Use rejected when the issue is fatal:
   - source direction reversal
   - unsupported core fact
   - unsupported number/date/company roadmap
   - stale republication without fresh follow-up
   - headline-only evidence
   - no body-level or official-material support
   - non-cardable lane fit

19. DROPPED treasure hunt rule:

   Perform dropped_review_treasure_hunt when:
   - the source input recommended_for includes dropped_review_treasure_hunt, or
   - the user explicitly requests dropped treasure hunt

   Use a documented sample strategy.

   Recommended sample strategy may include:
   - keyword-based sampling
   - high-integrity-score sampling
   - battery/materials/ESS/grid/supply-chain keyword sampling
   - source-tier sampling
   - random control sample

   Do not promote DROPPED items unless they are clearly relevant to:
   - batteries
   - ESS
   - EV charging
   - battery materials
   - critical minerals
   - recycling / EOL
   - power grid where storage or load structure is directly relevant
   - policy/regulation affecting the above
   - supply chain affecting the above

   Macro, climate, AI, data center, or industrial items may be promoted only when the battery/ESS/grid/supply-chain link is concrete, not merely thematic.

20. Silent loss prohibition:

   Every story in final_news_llm_input.stories[] must appear exactly once in decision_ledger.

   DROPPED stories outside the treasure-hunt sample must still appear in decision_ledger with an explicit reason such as:
   - dropped_not_sampled_in_treasure_hunt
   - upstream_dropped_not_reopened
   - out_of_scope_by_upstream_and_not_sampled
   - low_priority_dropped_not_sampled

   Do not silently omit non-sampled DROPPED stories.

Now perform Stage A only.

Stage A tasks:

A. Read all 8 required docs from GitHub main.

B. If all 8 required docs are confirmed, load {{SOURCE_INPUT_FILE}}.

C. Confirm run metadata and story counts from the source input:

   - story_count
   - KEEP count
   - REVIEW count
   - STEP2_PENDING count
   - DROPPED count
   - INPUT_ONLY count
   - excluded_story_count
   - integrity mode
   - recommended_for
   - generated_kst
   - schema version
   - run_tag
   - run_label

D. Load the active baseline.

   Confirm:
   - baseline file/source
   - baseline source declaration
   - baseline count
   - whether GitHub main sync gate will later be required

E. Apply lane-sanity gate across:

   - KEEP
   - REVIEW
   - STEP2_PENDING
   - INPUT_ONLY
   - selected DROPPED sample when dropped_review_treasure_hunt is triggered

F. Do not auto-pass KEEP.

   Re-check KEEP against:
   - scope relevance
   - event freshness
   - source quality
   - duplicate risk
   - evidence availability risk
   - strategic signal
   - full-schema viability
   - format-risk status for product/demo/PoC/component/interview/roundup/commentary/speech/personnel/partnership items
   - concrete execution-anchor viability when format-risk is present

G. Do not perform external web search.

H. Do not fetch article bodies.

I. Do not generate source_quote.

J. Do not generate fact_sources.

K. Do not generate card copy.

L. Identify strict_passed_spec candidates for Stage B.

   A story may enter strict_passed_spec only if it passes all applicable strict gates:
   - lane/scope fit
   - fresh or justified stale-warm timing
   - acceptable duplicate/follow-up relation
   - source tier and evidence availability risk not fatal
   - full-schema viability
   - concrete execution anchor when format-risk tags are present

   Do not promote a product/demo/PoC/component/interview/roundup/commentary/speech/personnel/partnership item to strict_passed_spec merely because it is interesting or thematically aligned.

M. Keep uncertain candidates as needs_review / review_pool.

   Do not promote review_pool into Stage B unless the user later explicitly authorizes it.

## Structural default — review_pool partition is a first-class output, not a report-only note

Stage A must not treat `review_pool[]` as a single operational bucket in any output artifact.

The default Stage A output model is:

- `strict_passed_spec[]`
- `candidate_review_pool[]`
- `watchlist_context_pool[]`
- `reject_or_support_only_pool[]`
- `rejected[]`
- `existing_reinforcement[]`
- `support_source_only[]`
- `decision_ledger[]`

`review_pool[]` may remain only as a backward-compatible aggregate container.
If `review_pool[]` is emitted, every item inside it must duplicate the exact `review_pool_partition` used in the first-class partition arrays.

Partition definitions:

1. `candidate_review_pool[]`
   - Plausibly cardable after bounded clarification.
   - Must have direct SBTL_HUB lane fit.
   - Must have a plausible concrete execution anchor or a clearly checkable path to one.
   - Must have a specific unresolved issue that can be resolved by a later review/promotion run.
   - Must include `promotion_precondition` and `bounded_review_question`.

2. `watchlist_context_pool[]`
   - Useful as industry context, trend context, source background, or future monitoring.
   - Not an independent current-run card candidate.
   - Must not be recommended for Stage B.
   - May only be reopened by a future fresh Stage A run or explicit user-authorized context review.

3. `reject_or_support_only_pool[]`
   - Too weak for candidate review, but either useful as support_source_only or clearly rejectable.
   - Must not be recommended for Stage B or candidate promotion.
   - Use for product/demo/PoC/partnership/commentary/macro items where the execution anchor is absent or too weak.

Stage A validity rule:

- If any non-strict, non-rejected, non-existing_reinforcement, non-support_source_only item lacks a partition, set:
  - `stage_a_validity_status = FAIL`
  - `review_pool_partition_status = FAIL`
  - `status = BLOCKED_STAGE_A_REVIEW_POOL_UNPARTITIONED`
  - `recommended_next_call = Stage A artifact repair/revalidation`
  - no Stage B recommendation

This is a structural default rule for every run, not a one-run remediation rule.


N. Apply obvious duplicate/event/reinforcement screening against the active baseline using:

   - title
   - URL
   - canonical URL
   - actor
   - project
   - asset or policy
   - event type
   - region
   - date
   - factual anchor
   - event fingerprint

O. If dropped_review_treasure_hunt is triggered:

   - document the trigger reason
   - document the sample strategy
   - record sample size
   - record sampled story IDs
   - record rescued count
   - record rescue IDs
   - record non-sampled DROPPED items in decision_ledger
   - do not promote dropped items unless clearly relevant and not stale/redundant

P. Produce a Stage A report and machine-readable Stage A JSON.

Stage A output files:

1. stage_a_prompt_a_results_{{RUN_TAG}}_main_revalidated.json
2. stage_a_prompt_a_report_{{RUN_TAG}}_main_revalidated.md
3. stage_a_prompt_a_decisions_{{RUN_TAG}}_main_revalidated.csv

Do not use FINAL, PR_CANDIDATE, GitHub-ready, merge-ready, publish-ready, or evidence_complete in Stage A filenames.

Stage A JSON requirements:

The JSON must include:

- stage
- run_tag
- run_label
- input_file
- baseline_file
- baseline_source_declaration
- baseline_count
- github_main_sync_required_later
- source_universe
- story_count
- original_status_counts
- integrity_summary
- recommended_for
- required_docs_check
  - docs_expected
  - docs_read_from_github_main
  - docs_missing_or_unreadable
  - status
- lane_sanity_rules_applied
- dropped_treasure_hunt
  - performed
  - trigger_reason
  - sample_strategy
  - sample_size
  - sampled_story_ids
  - rescued_count
  - rescue_ids
  - non_sampled_dropped_count
  - non_sampled_ledger_policy
- summary
  - legacy_keep_count
  - strict_passed_spec_count
  - needs_review_count
  - rejected_count
  - existing_reinforcement_count
  - support_source_only_count
  - duplicate_or_reinforcement_count
  - stale_discarded_count
  - stale_warm_review_count
  - total_ledger_count
  - ledger_matches_story_count
- legacy_keep[]
- strict_passed_spec[]
- review_pool[]
- existing_reinforcement[]
- support_source_only[]
- rejected[]
- dropped_treasure_hunt_result[]
- decision_ledger[]

Each strict_passed_spec must include:

- spec_id
- source_story_ids
- source_origin
- merge_status
- merged_story_ids
- baseline_relation
- duplicate_risk
- region
- representative_date
- representative_source
- source_tier_estimate
- cat
- sub_cat
- signal_estimate
- signal_rubric_estimate
- strategic_lens
- primary_url
- urls
- event_anchor
- format_risk_tags
- execution_anchor_type
- execution_anchor_strength
- strict_pass_gate
- title_raw
- summary_hint
- context_text
- why_now
- market_relevance
- source_priority_notes
- upstream_labels
  - triage_status
  - matched_buckets
  - drop_reason
  - integrity_group_id
  - integrity_is_best
  - drop_reason_overridden
- staleness
  - event_date
  - publication_date
  - staleness_gap_days
  - staleness_suspected
  - fresh_followup
  - staleness_override
  - decision
- needs_review
- review_reason
- stage_b_requirement_note

stage_b_requirement_note must state:

“Stage B must verify the provided source-candidate URL and build a valid evidence package before drafting. This Stage A spec is not evidence_complete, and primary_url is not evidence by itself.”

strict_pass_gate must include:

- status: pass | blocked_to_review_pool | blocked_to_support_source_only | blocked_to_rejected
- reason
- anchor_supported_by_upstream_text: true | false | unknown
- why_not_review_pool, when status = pass
- rescue_path, when status is not pass

format_risk_tags should use one or more of:

- product_news
- demo
- poc
- pilot
- prototype
- component_launch
- interview
- commentary
- explainer
- speech
- roundup
- partnership_integration
- personnel
- consumer_field_data
- none

execution_anchor_strength must be one of:

- strong
- moderate
- weak
- none
- unknown

Each review_pool item must include:

- review_pool_item_id
- story_id or grouped_story_ids
- upstream_status
- source_universe_index, if available
- reason_for_review
- review_type
- what_must_be_checked_before_promotion
- why_not_strict_passed_spec
- format_risk_tags, if applicable
- execution_anchor_status, if applicable
- promotion_conditions, if applicable
- baseline_relation_if_known
- staleness_decision
- recommended_next_action
- carry_forward_policy
- next_action_condition
- review_pool_resolution_status

Stage A must also write `review_pool_resolution_ledger[]`. This ledger is not
optional. It must contain one row for every item in `candidate_review_pool[]`,
`watchlist_context_pool[]`, `reject_or_support_only_pool[]`, and any legacy
`review_pool[]` aggregate.

Each `review_pool_resolution_ledger[]` row must include:

- review_pool_item_id
- story_id or grouped_story_ids
- original_review_pool_partition
- current_disposition
- disposition_basis
- carry_forward_policy
- next_action_condition
- whether_user_authorization_required

If the output has review_pool items but no complete ledger, set:

- `review_pool_carry_forward_ledger_status = FAIL`
- `blocked_reason = BLOCKED_REVIEW_POOL_LEDGER_GAP`

Do not recommend Stage B until `review_pool_carry_forward_ledger_status = PASS`.

Stage A JSON must expose the review-pool status both inside any status-gate
object and as top-level machine-readable aliases:

- `review_pool_partition_summary`
- `review_pool_carry_forward_ledger_status`

Do not leave these only in Markdown, CSV, `summary`, or `status_gates`. Stage B
and validation scripts are allowed to treat missing top-level aliases as
`BLOCKED_STAGE_A_REVIEW_POOL_LEDGER_METADATA_MISSING`.

Each rejected item must include:

- story_id or grouped_story_ids
- upstream_status
- rejected_reason_code
- rejected_reason_detail
- hard_reject_basis
- hard_reject_confidence
- hard_reject_positive_test_passed
- hard_reject_anti_overclosure_check
- why_not_review_pool
- baseline_match, if any
- staleness_decision
- notes

Rejected is a closed state only when `hard_reject_basis` is specific and
item-level. Do not use broad labels such as "low signal" or "not interesting"
as the only basis. If the story is weak but plausibly SBTL-relevant, route it to
`candidate_review_pool[]`, `watchlist_context_pool[]`, or
`reject_or_support_only_pool[]` with a ledger row instead of deleting it.

`hard_reject_basis` must use only the enumerated v13 basis values below.
Do not use risk/category labels such as `general_politics`, `politics`,
`memorial`, `sports`, `consumer_general`, `low_signal`, or `not_interesting` as
`hard_reject_basis`. If politics or memorial content is truly outside SBTL, use
`out_of_scope` or `not_sbtl_lane` and preserve the more specific risk label in
`rejected_reason_code`, `rejected_reason_detail`, `risk_category`, or `notes`.
If the story has any SBTL-adjacent policy, tariff, subsidy, trade, critical
minerals, supply-chain, battery, EV, charging, grid, storage, manufacturing, or
industrial actor angle, do not hard-reject; route to review/watchlist/support.

Stage A may close an item as rejected only when:

- `hard_reject_confidence = high`
- `hard_reject_positive_test_passed = true`
- `hard_reject_anti_overclosure_check = PASS`
- `why_not_review_pool` explains why review/watchlist/support-only would add no value

Each existing_reinforcement item must include:

- story_id or grouped_story_ids
- baseline_card_id, if identifiable
- reinforcement_type
- reason_not_new_card
- notes

Each support_source_only item must include:

- story_id or grouped_story_ids
- potential_supported_topic
- reason_not_independent_card
- possible_target_card_or_spec, if any
- notes

Each decision_ledger row must include:

- story_id
- upstream_status
- upstream_drop_reason
- headline
- site
- url
- integrity_group_id
- integrity_is_best
- ledger_decision
- editorial_bucket
- reason
- spec_id
- merged_into_spec_id
- baseline_match
- baseline_relation
- duplicate_risk
- staleness_decision
- treasure_hunt_sampled
- notes

Decision ledger rule:

- Every story in final_news_llm_input.stories[] must appear exactly once.
- total_ledger_count must equal story_count.
- If total_ledger_count does not equal story_count, mark Stage A output invalid and report status: BLOCKED_LEDGER_INCOMPLETE.


## Structural default — Stage A CSV required columns

Stage A decisions CSV is an operational artifact, not a summary-only artifact.
It must expose the same routing/gate metadata needed to audit Stage A without opening the full JSON.

The Stage A decisions CSV must include at minimum:

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

Row rules:

For `stage_a_bucket = strict_passed_spec`:
- `strict_pass_gate_status` must be `pass`.
- `baseline_relation` must not be `duplicate_of_main`.
- `duplicate_risk` must not be `fatal`.
- `staleness_decision` must not be `stale`.
- If `format_risk_tags` is not empty/none, `execution_anchor_strength` must be `strong` or `moderate`.

For `stage_a_bucket = review_pool`:
- `review_pool_partition` must be exactly one of:
  - `candidate_review_pool`
  - `watchlist_context_pool`
  - `reject_or_support_only_pool`
- `review_pool_partition_reason` must not be empty.
- `promotion_precondition` must not be empty for `candidate_review_pool`.
- `recommended_next_action` must not recommend Stage B for `watchlist_context_pool` or `reject_or_support_only_pool`.

CSV schema gate:

If any required CSV column is missing or any row violates these rules, set:
- `csv_schema_status = FAIL`
- `stage_a_validity_status = FAIL`
- `status = BLOCKED_STAGE_A_CSV_SCHEMA_INCOMPLETE`
- no Stage B recommendation

The Markdown report must include a `CSV schema status` line and a mismatch table if any CSV field is missing.

Stage A report requirements:

The Markdown report must include:

1. Run metadata

   - input file name
   - baseline file/source
   - baseline source declaration
   - baseline count
   - GitHub main sync required later: yes/no
   - run tag
   - run label
   - generated_kst
   - story count
   - original status counts
   - recommended_for
   - schema version

2. Required docs check

   - list all 8 required docs
   - confirm each was read from GitHub main
   - if any doc was not read, Stage A must not proceed

3. Method

   - governance hierarchy applied
   - lane-sanity rules applied
   - no-web-search confirmation
   - no-fetch confirmation
   - no-card-copy confirmation
   - no-source_quote/fact_sources confirmation
   - baseline duplicate screening method
   - event fingerprint method
   - staleness pre-check method
   - format-risk strict-pass presumption block method
   - dropped treasure hunt trigger and sample strategy

4. Summary table

   - legacy KEEP count
   - strict_passed_spec count
   - needs_review count
   - rejected count
   - existing_reinforcement count
   - support_source_only count
   - stale discarded count
   - stale-warm review count
   - duplicate/reinforcement count
   - dropped_treasure_hunt performed
   - dropped_treasure_hunt sample size
   - dropped_treasure_hunt rescued count
   - total decision ledger count
   - ledger equals story count: yes/no

5. strict_passed_spec manifest

   For each candidate:
   - spec_id
   - short event anchor
   - source origin
   - region / cat / signal estimate
   - primary URL
   - baseline relation
   - duplicate risk
   - staleness decision
   - why it can proceed to Stage B
   - execution anchor type and strength
   - format-risk tags, if any
   - strict_pass_gate.status and reason
   - Stage B evidence package required before draft

6. review_pool manifest summary

   For each review item:
   - story_id or grouped ID
   - reason for review
   - what must be checked before promotion
   - why it was not strict_passed_spec
   - execution-anchor gap or source-strength gap, if applicable

7. rejected summary

   Group by reason:
   - out_of_scope
   - stale
   - duplicate
   - weak evidence
   - generic landing/listing page
   - support_source_only
   - low strategic signal
   - source ambiguity
   - other

8. duplicate/event screening notes

   - likely duplicates of existing baseline cards
   - likely follow-ups
   - likely reinforcements
   - uncertain cases
   - event fingerprint collision notes

9. dropped_treasure_hunt notes

   - trigger reason
   - sample strategy
   - sample size
   - rescued count
   - rescued IDs
   - non-sampled DROPPED ledger handling

10. Stage boundary statement

   Include this exact statement:

   “No external web search, no article body fetch, no card copy, no source_quote generation, no fact_sources generation, no evidence_complete decision, and no publish-ready decision were performed in Stage A.”

11. Next-step statement

   Include this exact statement:

   “Stage B may begin only after the user explicitly says ‘Stage B’. Stage B must create an evidence package for every strict_passed_spec before drafting any card.”



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

## Operational integrated rule — Stage A next-call recommendation

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

0. Hard blockers override all count-based recommendations.

   Do not recommend Stage B merely because `strict_passed_spec_count > 0`.

   Recommend Stage B only if all of the following are true:
   - `stage_a_validity_status = PASS`
   - `artifact_consistency_status = PASS`
   - `csv_schema_status = PASS`
   - `review_pool_partition_status = PASS`
   - `review_pool_carry_forward_ledger_status = PASS`
   - `strict_pass_gate_metadata_status = PASS`
   - `baseline_duplicate_screen_status = PASS`
   - `ledger_matches_story_count = true`
   - `strict_passed_spec_count > 0`

   If any required status is missing or not PASS:
   - recommended_next_call = "Stage A artifact repair/revalidation"
   - recommended_prompt_id = "Prompt 0.1 repair/revalidation"
   - recommended_input_universe = "Current Stage A artifacts only"
   - reason = "Stage A output is structurally incomplete or internally inconsistent; Stage B must not start."
   - do_not_proceed_to = ["Stage B", "Stage C", "0.4", "0.5", "0.6", "0.7", "0.8"]

1. If all gates above PASS and strict_passed_spec_count > 0:
   - recommended_next_call = "Stage B r0"
   - recommended_prompt_id = "Prompt 0.2"
   - recommended_input_universe = "Stage A strict_passed_spec[] only"
   - source_universe_completion_status = "PARTIAL_STRICT_SUBSET_ONLY" unless `rescue_audit_status = PASS`
   - if `candidate_review_pool_count > 0`, `TRIAGE_FILTERED_count > 0`, or `newsletter_expanded_added_treasure_count > 0`, include:
     - pending_parallel_or_followup_call = "review_pool/treasure triage"
     - pending_prompt_id = "authorized review_pool/treasure promotion protocol, not Prompt 0.2"
     - pending_input_universe = "candidate_review_pool[] + eligible treasure/review-only universe"
     - pending_reason = "Stage B may process strict_passed_spec[] only; review_pool/treasure remains open and must not be treated as exhausted."

2. If strict_passed_spec_count = 0 and candidate_review_pool_count > 0:
   - recommended_next_call = "candidate_review_pool triage"
   - recommended_prompt_id = "separate review_pool promotion prompt, not Prompt 0.2"
   - recommended_input_universe = "Stage A candidate_review_pool[] only"

3. If strict_passed_spec_count = 0 and candidate_review_pool_count = 0 and watchlist_context_pool_count > 0:
   - recommended_next_call = "retrospective or watchlist context review"
   - recommended_prompt_id = "Prompt 1.1 or separate context review prompt"
   - recommended_input_universe = "watchlist_context_pool[] only, not Stage B"

4. If all candidates are rejected/held/support-only:
   - recommended_next_call = "retrospective"
   - recommended_prompt_id = "Prompt 1.1"

Do not proceed automatically to Stage B.
Stop after Stage A.

Do not proceed to Stage B until I explicitly say “Stage B”.


## Final Stage A boundary restatement

Stop after Stage A.

Do not proceed to Stage B until I explicitly say “Stage B”.

This final boundary restatement applies after all operational integrated rulees above.


<!-- STRUCTURAL_DEFAULT_SOURCE_PROMPT_PROVENANCE_20260506 -->
## Source prompt provenance — required output fields

Every Stage A JSON output must include:

- `source_prompt_file`
- `source_prompt_sha256`
- `source_prompt_version`
- `source_prompt_authority`
- `source_prompt_provenance_status`

For this replace-all package, use:

```text
source_prompt_version = structural_default_review_pool_partition_20260506
source_prompt_authority = uploaded_or_repo_source_file_prompt
source_prompt_provenance_status = PASS | FAIL
```

If `source_prompt_sha256` cannot be computed or recorded, Stage A must set:

```text
source_prompt_provenance_status = FAIL
stage_a_validity_status = FAIL
status = BLOCKED_STAGE_A_SOURCE_PROMPT_PROVENANCE_MISSING
no Stage B recommendation
```
<!-- /STRUCTURAL_DEFAULT_SOURCE_PROMPT_PROVENANCE_20260506 -->

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

`staleness_decision` must be a top-level field on each `strict_passed_spec[]`
item. A nested object such as `staleness.decision` may also be included for
explanation, but it is not a substitute for the top-level contract field.

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

## Operational integrated rule — NO_SILENT_DOWNSTREAM_ENRICHMENT_STAGE_A_BOUNDARY_20260507_V3

Stage A is selector-only and must not fetch article bodies, perform external web search, generate source_quote, generate fact_sources, write card copy, or absorb later-discovered evidence.

If Stage A detects uncertainty, format risk, weak evidence, source thinness, possible duplicate, or lane ambiguity, Stage A must not repair the item with new sources or later evidence. It must route the item to the correct Stage A outcome:

- `strict_passed_spec[]` only if the strict-pass gate fully passes using allowed Stage A inputs.
- `candidate_review_pool[]` if plausibly cardable after bounded source/date/duplicate clarification.
- `watchlist_context_pool[]` if useful context but not a current-run card candidate.
- `reject_or_support_only_pool[]`, `rejected[]`, or `support_source_only[]` when appropriate.

Stage A must record:

- `official_source_checked: NOT_APPLICABLE_STAGE_A_NO_FETCH`
- `alternate_tier1_tier2_checked: NOT_APPLICABLE_STAGE_A_NO_FETCH`
- `rescue_attempted: NOT_APPLICABLE_STAGE_A_NO_FETCH`
- `rescue_candidate_evidence: []`
- `recommended_next_action`
- `bounded_review_question`

If Stage A attempts to use later-discovered evidence or external search/fetch to upgrade an item, stop and report:

- `status: BLOCKED_STAGE_A_NO_FETCH_VIOLATION`
- `no Stage B recommendation`



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


## Operational integrated rule — Stage A event-fingerprint dedupe gate — 20260514

Run 20260513_083924 retrospective 에서 발견된 gap: Stage A baseline collision detection 이 URL + canonical_url + title 매칭만 사용 → 같은 사건을 다른 매체가 보도한 경우 미검출. Ford Energy 출범 사건이 baseline (2026-05-11_US_01, SEC 8-K + Electrek + Solar Power World) 과 신규 (2026-05-12_US_02, InsideEVs + PV Magazine + Energy-Storage.news) 양쪽에 등록되어 production 까지 통과, Codex P2 review 에서야 catch 됨.

### HARD RULE — event-fingerprint dedupe gate

각 spec 후보에 대해 baseline collision 검사 시 URL/title 외에 다음 3-tuple fingerprint 도 검사한다:

```
fingerprint = (
  date_bucket: spec 의 published_date_article ±3일 범위,
  primary_entity_set: sorted(lower(headline + 첫 단락의 named entity 토큰 셋)),
  event_type_token: launch | acquire | ipo | mou | fine | gigafactory |
                    plant_commissioning | partnership | recall | bankruptcy |
                    contract_award | regulatory_decision | ownership_transfer | other
)
```

**매칭 규칙**: 세 dimension 모두 매칭되면 baseline_event_collision_hold 로 분류.
- date_bucket: ±3일 overlap
- primary_entity_set: ≥1 entity 토큰 매칭 (stopword 제외: Battery, EV, BESS, 회사, the 등)
- event_type_token: 동일 토큰 매칭

세 dimension 모두 매칭이 아니면 정상 진행 (overly strict 매칭은 related-event 카드까지 차단할 위험).

### Event_type 분류 가이드

| 키워드/패턴 | event_type |
|---|---|
| launch / unveil / 출범 / 공식 발표 | `launch` |
| acquire / acquisition / 인수 / 매각 | `ownership_transfer` |
| IPO / Form S-1 / list on / 상장 | `ipo` |
| MOU / 양해각서 / partnership | `mou` |
| fine / 과징금 / 제재 | `fine` |
| gigafactory / 기가팩토리 / 양산 시설 | `gigafactory` |
| commission / 가동 시작 / first power | `plant_commissioning` |
| 수주 / contract award | `contract_award` |
| 관세 / 수출통제 / regulatory decision | `regulatory_decision` |
| recall / 리콜 | `recall` |
| 파산 / chapter 11 | `bankruptcy` |
| 외 | `other` |

### Stage A 출력 변경

```
{
  ...
  "baseline_url_collision_count": N,
  "baseline_event_collision_hold_count": M,   // 신규
  "baseline_event_collision_hold": [
    {
      "spec_id": "...",
      "matched_baseline_card_id": "...",
      "fingerprint_match": {
        "date_overlap": "spec 2026-05-12 ↔ baseline 2026-05-11 (within ±3 days)",
        "entity_match": ["Ford","Kentucky","Glendale"],
        "event_type_match": "launch"
      },
      "recommendation": "review for merge vs new card decision"
    }
  ]
}
```

`baseline_event_collision_hold` 는 자동 reject 가 아니라 **human review or 0.4 manual override** 가 필요한 카테고리. 진짜 duplicate 면 reject 또는 baseline 카드를 enrich, related-event 면 새 카드로 진행.

### 예방 효과

- Ford Energy 같은 이중 등록 사례를 Stage A 단계에서 차단
- production 통과 후 codex_followup 으로 fix 하는 round 제거
- baseline evidence 강도 보존 (additive enrichment 옵션)

<!-- INTEGRATED_RULE_BEGIN: STAGE_A_CROSSLANGUAGE_ENTITY_NORMALIZATION_20260514_v2 -->
## Operational integrated rule P_010 — Stage A cross-language entity normalization — 20260514_v2

### 문제 정의

P_007 event-fingerprint dedupe 가 동일 언어 내 정확한 entity 매칭에만 작동.
다음 cross-language pair 가 strong match 안 됨:

| baseline (한국어/한자) | new spec (영문) | 결과 |
|---|---|---|
| 소프트뱅크 사카이市 | SoftBank Sakai | P_007 weak or miss |
| 블룸버그NEF / BNEF | BloombergNEF | P_007 weak or miss |
| 닝더 | Ningde / 宁德 | P_007 weak |
| Ford Energy (한국어 카드) | Ford Energy (영문 source) | P_007 weak (run 20260513_083924 Codex P2 catch) |
| 2026-05-11_JP_01 SoftBank Sakai (한국어 baseline) | 2026-05-12 SoftBank Osaka PV Mag (영문) | P_007 miss (run 20260513_165421 Codex P2 catch) |

run 20260513_165421 의 Codex P2 review 가 2건 catch (JP_02=JP_01, GL_07=GL_02),
Stage B human review 가 3건 추가 catch (Ford, 中科, Alsym). 총 5건 cross-language false-negative.

### HARD RULE — cross-language entity normalization

Stage A 의 event-fingerprint 계산 **전** 다음 normalization 단계 추가:

```
1. detect entity strings in spec headline + body (named-entity recognition)
2. lookup each entity in entity_alias_map (project file)
3. replace each occurrence with canonical form (English preferred)
4. compute event-fingerprint hash on canonical form
5. compare against baseline event-fingerprints (also canonicalized)
```

### entity_alias_map (project 파일로 유지)

회사·인물·기관·지명·기술용어의 multi-language alias map.
canonical form 기본은 **영문**, 영문 없으면 한국어 표준 표기.

예시 entries:

```json
{
  "SoftBank": {
    "canonical": "SoftBank",
    "aliases": ["소프트뱅크", "ソフトバンク", "软银", "SoftBank Corp"],
    "type": "company"
  },
  "BloombergNEF": {
    "canonical": "BloombergNEF",
    "aliases": ["BNEF", "블룸버그NEF", "블룸버그 NEF", "BloombergNEF (BNEF)"],
    "type": "research_org"
  },
  "Sakai": {
    "canonical": "Sakai",
    "aliases": ["사카이市", "사카이시", "Sakai City", "오사카부 사카이"],
    "type": "place",
    "parent_region": "Osaka prefecture, Japan"
  },
  "Ningde": {
    "canonical": "Ningde",
    "aliases": ["닝더", "宁德", "Ningde City"],
    "type": "place"
  },
  "BYD": {
    "canonical": "BYD",
    "aliases": ["비야디", "比亚迪", "BYD Auto", "BYD Company"],
    "type": "company"
  },
  "CATL": {
    "canonical": "CATL",
    "aliases": ["宁德时代", "닝더시대", "컨템포러리 암페렉스", "Contemporary Amperex Technology"],
    "type": "company"
  },
  "Ford Energy": {
    "canonical": "Ford Energy",
    "aliases": ["Ford 에너지 사업부", "포드 에너지", "Ford Pro Energy"],
    "type": "company_division",
    "parent": "Ford"
  }
}
```

### 통합 매칭 알고리즘 — strong vs weak

**strong match** 조건 (모두 충족):
- canonical entity overlap: 신규 spec 과 baseline 카드의 canonical entities 가 **≥2 개** 일치
- numeric overlap: capacity (GWh/MW), 금액 (위안/달러/원), percent 중 **≥1 개** 일치
- date proximity: ±7일 이내

**weak match**: canonical entity overlap 1개 + numeric overlap 1개 + date proximity ±14일

strong → `baseline_event_collision_hold` (자동 hold)
weak → spec output 에 `event_fp_strength: "weak"` flag (Stage B human review 필수)

### Stage A 출력 schema 확장

```jsonc
{
  "spec_id": "...",
  "event_fingerprint_canonical": "sha1(canonical_entities + numeric_values + date)",
  "entity_canonicalization_log": [
    {"original": "소프트뱅크", "canonical": "SoftBank"},
    {"original": "사카이市", "canonical": "Sakai"}
  ],
  "event_fp_match": {
    "baseline_id": "2026-05-11_JP_01",
    "match_strength": "strong" | "weak",
    "canonical_entity_overlap": ["SoftBank", "Sakai", "Cosmos Lab"],
    "numeric_overlap": ["1GWh"],
    "date_diff_days": 1
  }
}
```

### entity_alias_map 갱신 프로세스

- Stage B Codex review 또는 retrospective 에서 새 cross-language pair 발견 시 alias_map 에 항목 추가
- 주요 글로벌 회사 (Tesla, Toyota, VW, Hyundai 등) 와 한국 시장 친숙 음역명 (비야디, 샤오펑, 니오, 지커, 칭타오에너지) 우선 등록
- map 자체는 Stage A 첫 호출 시 load, 매 run 시작 시 git pull 으로 최신화

### 예방 효과

- run 20260513_083924 Ford 케이스 + run 20260513_165421 JP_02/GL_07 케이스 같은 cross-language 이중 등록 0건 목표
- codex_followup_v2 type round 제거
- Stage B 의 human review 부담 감소

<!-- INTEGRATED_RULE_BEGIN: STAGE_A_CANDIDATE_AUTO_PROMOTION_20260514_v2 -->
## Operational integrated rule P_013 — DEPRECATED / superseded by review-only expanded input discipline — 20260519

### 문제 정의

run 20260513_083924, 20260513_165421 모두 strict_passed_spec 가 8개 내외에 그침
(190 stories 중 ~5%). candidate_review_pool 가 60+ specs 로 Stage B 워크로드 과중.
run 20260513_165421 의 경우 candidate 61 중 21건 silent drop 발생.

분석 결과: 일부 candidate spec 은 strict 기준 미달이지만 실제 카드화 가치 높은
경우 — named industry actor + numeric specificity + signal_estimate high/top
조합이 있는 spec.

### 20260519 red-team ruling

This integrated rule is no longer an active promotion rule.

Do not auto-promote any item from `candidate_review_pool`, `TRIAGE_FILTERED`,
`missed_treasure`, or `newsletter_expanded_added_treasure` based on classifier
score, treasure score, anchor count, signal estimate, named actor, or numeric
specificity.

The former P_013 signal bundle may be used only as a review-priority hint:

- `candidate_review_pool` priority ordering
- `treasure_candidate_review_pool` priority ordering
- `watchlist_context_pool` rationale
- bounded review question generation

It must not create `strict_passed_spec[]`.

### Deprecated criteria retained only for audit memory

The following former criteria are historical notes only and must not be applied
as an OR path into strict pass:

1. `anchor_categories_count` >= 1
2. `nl_clean_score` >= 12
3. `signal_estimate` in {`top`, `high`}
4. `named_industry_actor_present` = true
5. `numeric_specificity_present` = true

### If an item is later promoted

Promotion requires an explicit user-authorized review/promotion run. The item
must then pass the same six-condition Stage A strict-pass gate as any normal
candidate. The output must not use `auto_promoted_via_p_013`.

Allowed route labels:

```jsonc
{
  "spec_id": "...",
  "partition_decision": "candidate_review_pool",
  "review_priority_hint": "former_p_013_signal_bundle",
  "promotion_precondition": "requires_explicit_review_run_and_full_stage_a_strict_pass_gate"
}
```

### Stage A 출력 accounting

```jsonc
{
  "strict_passed_via_p_013_count": 0,
  "auto_promotion_disabled": true,
  "candidate_review_pool_prioritized_by_p_013_signal_count": N
}
```

### Stage B 처리

Stage B must reject or route back any item whose only Stage A route is
`auto_promoted_via_p_013`.

### 예방 효과

- Prevents classifier-score laundering into Stage B.
- Preserves high-signal candidates for bounded review without treating them as
  accepted.
- Keeps `strict_passed_spec[]` aligned with the six-condition Stage A gate.

## FIX-002 — Stage A input is pre-filtered, not a keyword selector

When the input is `final_news_llm_input_newsletter_expanded_*.json`, Stage A must treat `newsletter_clean_score`, `newsletter_anchor_categories`, `newsletter_anchor_matches`, `matched_buckets`, `positive_signals`, and `newsletter_positive_signals` as upstream pre-filtering signals only.

They are not sufficient for `strict_pass`.

Stage A `strict_pass` requires story-level editorial judgment: concrete event anchor, direct SBTL_HUB lane relevance, baseline duplicate/event-fingerprint screen, source discoverability, bounded strategic question, and no generic keyword-only pass.

Keyword/rule-based classifiers may be used only for triage/recall sampling, never as the final basis for partition or strict-pass decisions. Rule 19 treasure-hunt keyword sampling remains allowed because it selects what to review, not what to pass.

## FIX-006 — newsletter_expanded is a review universe, not an acceptance universe

`final_news_llm_input_newsletter_expanded_*.json` is formed as:

```text
newsletter_expanded
= newsletter_clean kept stories
+ selected TRIAGE_FILTERED treasure card leads
```

The added treasure portion is not a pipeline acceptance signal. It is a
second-pass review/recall surface for items that were already marked
`TRIAGE_FILTERED` upstream.

### Required Stage A interpretation

If a story has any of the following markers, Stage A must treat it as
review-only unless it independently passes the full Stage A strict-pass gate:

- `triage_status: "TRIAGE_FILTERED"`
- `status_detail: "REFINER_KEEP_TRIAGE_FILTERED"`
- `newsletter_clean_reason: "TRIAGE_FILTERED_TREASURE_CARD_LEAD"`
- `newsletter_clean_selection_role: "TREASURE_CARD_LEAD"`
- `treasure_source_status: "TRIAGE_FILTERED"`
- `treasure_tier`, `treasure_score`, or `treasure_review_group_id`

These markers mean "do not miss this during review." They do not mean:

- accepted
- strict pass
- evidence complete
- source verified
- Stage B ready
- addable

### Partition rule

Default routing for added treasure items:

- `candidate_review_pool[]`, if the item has a concrete event anchor and a
  plausible SBTL_HUB lane question but lacks full strict-pass confidence.
- `watchlist_context_pool[]`, if strategically relevant but not cardable today.
- `reject_or_support_only_pool[]`, if generic, duplicate, source-thin,
  consumer/local/noise-heavy, or only useful as background.

Promotion from any of these pools requires an explicit user-authorized
review/promotion run and then the normal six-condition Stage A strict-pass gate.

### Required accounting

Stage A output must include:

```jsonc
{
  "newsletter_expanded_input_detected": true,
  "newsletter_expanded_added_treasure_count": "...",
  "triage_filtered_treasure_reviewed_count": "...",
  "triage_filtered_treasure_promoted_to_strict_count": 0,
  "triage_filtered_treasure_candidate_review_pool_count": "...",
  "triage_filtered_treasure_watchlist_context_pool_count": "...",
  "triage_filtered_treasure_reject_or_support_only_pool_count": "...",
  "auto_promotion_from_expanded_disabled": true
}
```

If the stage cannot account for the added treasure universe, it must report
`BLOCKED_NEWSLETTER_EXPANDED_TREASURE_UNACCOUNTED` rather than silently passing
or silently dropping those items.

## FIX-003 — PRIMARY_URL_TERM_COLLISION_RULE

In Stage A outputs, `primary_url` is not a primary source and not verified evidence.

`primary_url` means only the provided/source-candidate URL selected as the representative starting point for Stage B source discovery. It must not be interpreted as Tier 1, official, primary evidence, or an evidence package.

Preferred schema annotation for every `strict_passed_spec[]` item:

```json
{
  "provided_source_candidate_url": "...",
  "primary_url_semantics": "provided_source_candidate_not_evidence",
  "stage_a_evidence_status": "not_evidence_complete_no_fetch",
  "stage_b_evidence_package_required": true
}
```

Replace any wording equivalent to “fetch primary_url and prepare an evidence package” with: Stage B must build a valid `evidence_package` before drafting; `primary_url` is only one provided source candidate and must be independently verified or replaced via the source-discovery ladder.

## FIX-005 — Stage A/B must emit required lineage metadata

Prompt 0.4 lineage guard must remain hard. Do not soften it.

The corrected diagnosis from run `20260516_012728` is that Stage A and Stage B failed to emit lineage fields that their own prompts already required. This is execution non-compliance, not a schema-version gap.

Stage A exit must fail if any `strict_passed_spec[]` item lacks required lineage fields from `SCHEMA_CONTRACT_STAGE_LINEAGE.md`, including `enhanced_selector_precision_version`, `selector_policy_version`, `strict_gate_check`, `staleness_decision`, `source_access_risk`, and `strict_pass_gate.all_six_conditions_passed`.

Stage B preflight must run `stage_a_validity_guard` before drafting. Stage B output must include `lineage_integrity_status`, `stage_a_validity_guard_applied`, `strict_gate_metadata_preserved`, `execution_anchor_metadata_preserved`, `superseded_lineage_mixed`, `manual_integrated_rule_mixed`, and `previous_run_output_mixed`.

If required fields are missing, stop with `BLOCKED_STAGE_OUTPUT_SCHEMA_NONCOMPLIANT` or `BLOCKED_STAGE_A_LINEAGE_NONCOMPLIANT`.

## FIX-007 — Shared schema contract and stage-exit conformance check

All stages must reference `SCHEMA_CONTRACT_STAGE_LINEAGE.md`.

Each named stage must run or explicitly satisfy a stage-exit artifact conformance check before recommending the next stage. Missing required fields must stop the stage with:

```text
BLOCKED_STAGE_OUTPUT_SCHEMA_NONCOMPLIANT
```

Do not wait until Prompt 0.4 to discover Stage A/B lineage omissions.

## FIX-008 — Stage A review_pool item-level reasoning

Stage A must write genuinely item-specific `why_not_strict_passed_spec` and, where useful, `bounded_review_question` for every `candidate_review_pool[]` entry.

The reasoning must name the actual event or actor, the unresolved issue, why it is not strict-pass now, and what would promote it later.

Allowed reason categories include: concrete anchor but unresolved scope/date/duplicate; plan/intention without confirmed anchor; roundup needing event isolation; lane-fit borderline; out-of-lane/support-only; pilot/demo needing site/scale/duration/objective; research/tech claim without execution anchor.

## FIX-009 — URL canonicalization must preserve article IDs

For duplicate/event-fingerprint URL normalization, preserve article identity query parameters and remove tracking parameters only.

Preserve examples: `idxno`, `aid`, `articleid`, `articleId`, `no`, `articleView`, `newsid`, `seq`, `id`.

Remove examples: `utm_*`, `fbclid`, `gclid`, `ref`, `source`, `campaign`, `spm`.

Do not strip entire query strings for Korean CMS/news URLs where the query string carries the article identifier.

# 01_PROMPT_0_1_Stage_A.md — Source Diversity source-diversity integrated rule

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

## Stage A source-cluster preservation — HARD RULE

Stage A remains selector-only and must not fetch article bodies. Using current-run metadata,
`source_packets`, previews, `usable_text`, URL, site, headline and integrity metadata, it must build
a same-event source cluster before choosing a representative candidate.

For every event candidate, emit:

```json
{
  "same_event_source_cluster": [
    {
      "story_id": "",
      "url": "",
      "canonical_url": "",
      "domain": "",
      "site": "",
      "probable_editorial_owner": "",
      "same_event_binding_basis": [],
      "probable_source_role": "",
      "preserve_for_stage_b": true
    }
  ],
  "representative_story_id": "",
  "support_source_candidates": [],
  "source_domain_candidates": [],
  "source_role_hypotheses": [],
  "source_diversity_path": {
    "status": "viable|uncertain|not_viable",
    "probable_independent_owner_count": 0,
    "official_or_source_owner_candidate_present": false,
    "independent_confirmation_candidate_present": false,
    "context_candidate_present": false
  }
}
```

Selecting one representative story must not delete or detach the remaining same-event sources.
Every support source must remain linked to the representative `spec_id` and pass to Stage B.

### Strict-pass gate addition

A `strict_passed_spec[]` item must include:

```text
source_cluster_preserved = true
source_diversity_path.status = viable | uncertain
support_source_candidates_accounted = true
```

If the event anchor is strong but the source-diversity path is uncertain, place the item in
`candidate_review_pool[]` with `source_augmentation_path`, not in hard reject.

### Stage A blockers

Block Stage A output when:

- a same-event cluster was collapsed to one story without preserving support candidates;
- duplicate-event stories were discarded without an `existing_reinforcement` or
  `support_source_only` linkage;
- `source_domain_candidates[]` counts article rows instead of canonical domains;
- probable copies of the same release are described as independent sources.

Required blocker:

```text
status = BLOCKED_STAGE_A_SOURCE_CLUSTER_OR_DIVERSITY_PATH_INVALID
```

    Stop after Stage A. Do not fetch sources or proceed to Stage B without explicit authorization.

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


## Stage A extra

Stage A must preserve source clusters and must not promote review-pool items because they are high-value. It can only route them with explicit promotion path.
