# Structural News Value V3 Validation — 2026-08-02

## Scope

This rollout upgrades the canonical structural-value policy and aligns the executable selector, evidence, content-polish, final-QC, and Related contracts:

- `docs/STRUCTURAL_NEWS_VALUE_SELECTION.md`
- `docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md`
- `docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md`
- `docs/llm_prompts/v1/02_PROMPT_0_2_Stage_B_r0.md`
- `docs/llm_prompts/v1/03_PROMPT_0_3_Stage_C_r0.md`
- `docs/llm_prompts/v1/07_PROMPT_0_5_Evidence_QC.md`
- `docs/llm_prompts/v1/08_PROMPT_0_6_Content_Polish.md`
- `docs/llm_prompts/v1/09_PROMPT_0_7_Final_QC.md`
- `docs/RELATED_LIFECYCLE_CONTRACT.md`
- `validation_scripts/related_lifecycle_check.py`
- `validation_scripts/tests/test_workflow_contracts.py`

It does not modify card data, the card-run engine, or any production ID.

## V2 framework preservation

V3 preserves and explicitly restates the governing V2 framework:

- credibility, cardability, decision value, and urgency remain separate;
- the before–after and novelty tests remain mandatory;
- V2 novelty classification caps remain enforceable at the total score/classification level;
- the Stage A routing matrix remains explicit;
- `signal = top | high | mid` remains assigned only after the four judgments;
- the narrow `mid` fallback for a credible independently cardable execution event remains available when all other gates pass;
- the 100-point industry-first model remains 25/25/20/10/10/5/3/2;
- the three core industrial dimensions remain 70 points;
- denominator discipline remains mandatory;
- technology-evidence score caps remain mandatory;
- legal-policy Stage 0–6 remains mandatory;
- the twelve mandatory legal-policy questions remain explicit;
- missing instrument, authority, or procedural status and lifecycle-stage conflation are hard blockers in Prompt 0.1S;
- proposal, adoption, effectiveness, implementation, enforcement, and judicial review remain distinct;
- the twelve-question IB-grade decision-useful content test remains explicit;
- blocker output fields remain explicit;
- search-before-delete remains mandatory;
- Stage A remains selector-only and no-fetch;
- high decision value never waives evidence or workflow gates;
- execution form, legal form, transaction size, and corporate prominence remain prohibited importance proxies.

## V3 additions

V3 adds:

1. six explicit anchor classes;
2. Structural Value Override;
3. mandatory AI-power/ESS, policy, economic-security, profitability, strategy, technology, and follow-up lenses;
4. full earnings-release → filing → IR → prepared remarks → call → analyst-Q&A → prior-period comparison workflow;
5. conditional earnings defaults that prevent `qna_status: not_applicable` from bypassing deep-dive review;
6. explicit material-follow-up probability review;
7. structural and earnings-specific review subtypes routed through the supported `candidate_review_pool`;
8. canonical `portfolio_coverage_audit.json` plus zero-domain explanations;
9. anti-regression validator outcome names;
10. mandatory next-confirmation points.

## Related lifecycle alignment

`RELATED_LIFECYCLE_V2_20260802` preserves direct, auditable lineage while allowing a `distinct_follow_up` to use any verified V3 anchor class:

- execution event;
- policy/regulatory;
- data/financial;
- strategic behavior;
- technology commercialisation;
- follow-up probability.

Every distinct follow-up still requires:

- named predecessor IDs;
- direct lineage;
- a current source-supported anchor;
- incremental fact versus predecessor;
- changed judgment versus predecessor;
- independent cardability;
- representative event date;
- proof that reinforcement alone is insufficient.

Shared company, topic, geography, project name, generic management statement, or newer article date remains insufficient.

## Conflict resolution

The V3 canonical policy explicitly supersedes any older rule that requires a conventional corporate execution event as the sole strict-pass form.

Evidence, baseline, duplicate, direct-lineage, state-ladder, source-diversity, and no-silent-enrichment rules remain unchanged.

## Validation checklist

- canonical version is `STRUCTURAL_NEWS_VALUE_SELECTION_V3`;
- Prompt 0.1S version matches V3;
- Related lifecycle is `RELATED_LIFECYCLE_V2_20260802`;
- both selector files preserve 25/25/20 core weighting;
- novelty total-score/classification caps are present;
- Stage A routing matrix is present;
- signal-assignment rules and narrow execution fallback are present;
- legal-policy Stage 0–6 is present;
- mandatory legal-policy questions are present;
- legal-policy missing-field and stage-conflation blockers are present in the operational override;
- technology score caps are present;
- IB-grade decision-useful content questions are present;
- blocker output fields are present;
- listed-company earnings defaults require `not_checked_stage_a`, availability fields, prior-period comparison, and rescue questions;
- `portfolio_coverage_audit.json` is required in the canonical policy and Prompt 0.1S;
- follow-up and incremental-information fields are present;
- non-execution follow-ups have a defined Related evidence contract;
- the production Related validator enforces the V2 anchor-class, incremental-fact, and changed-judgment fields;
- Stage A review subtypes remain inside the supported candidate partition;
- Stage B, Stage C, Evidence QC, Content Polish, and Final QC all implement the same two-path anchor model;
- mandatory structural domains and zero-coverage treatment are present;
- Stage A no-fetch boundary remains present;
- card data is unchanged.

## Executable alignment completed in this PR

This PR aligns the central V3 feature with the full active execution path:

- base Stage A accepts either a concrete execution anchor or a complete V3 non-execution override for format-risk strict items;
- structural and earnings review categories are subtypes of the supported `candidate_review_pool`, not unsupported top-level partitions;
- the Stage A JSON and CSV contracts carry and validate the subtype and override fields;
- Stage B verifies the exact non-execution anchor claims and evidence targets instead of demanding an execution event;
- Stage C validates exactly one source-backed route and carries `anchor_path_validation` forward;
- Evidence QC verifies route-specific source coverage and emits `anchor_path_qc_summary.item_results[]`;
- Content Polish consumes those item results without switching or inflating the selected route and emits exact root/item `lineage_and_anchor_guard` objects;
- Final QC consumes the same selected-path and route-status schema and hard-fails incomplete, contradictory, or inflated packages;
- the Related production validator enforces fresh anchor class, incremental fact, and changed judgment for every current-run `distinct_follow_up` under `--require-contract`, while preserving legacy unflagged validation behavior;
- regression fixtures cover missing and invalid anchor classes, missing incremental fact, missing changed judgment, legacy unflagged behavior, execution-only gate regression, route-status producer/consumer mismatch, and stale eight-document accounting.

Remaining future implementation may add dedicated structural-value, earnings-Q&A, portfolio-coverage, and content-depth validators, but it must not reintroduce an execution-only gate or unsupported review partition. Fact Discipline and the card-run safety engine remain unchanged.

## Review 4837529388 closure

The review findings are addressed as follows:

- Stage A, Stage B, and Final QC share the execution-or-V3-non-execution eligibility model;
- the active Stage A format-risk presumption gate, strict-pass condition, required item object, lineage metadata, report contract, and CSV contract carry the override fields;
- structural and earnings review categories are `candidate_review_pool` subtypes, not unsupported top-level partitions;
- Related V2 fields are enforced only for current-run strict validation with `--require-contract`;
- legacy unflagged inventory validation is unchanged;
- temporary patch workflows, helper scripts, and generated Python bytecode are absent from the final diff.

## Review 4837763004 downstream residual closure

- Stage B source-direction and draft-blocked lists reject format-risk items only when neither the source-backed execution path nor the complete source-backed V3 non-execution path is available.
- Final QC's later safety overlay and publish-ready checklist validate both source-backed paths and carry explicit anchor-path QC status.
- Stage B and Final QC required-doc accounting consistently requires all ten governance documents.
- Regression tests fail on removed execution-only blocker phrases or any return to eight-document accounting.

## Review 4838008669 full-pipeline closure

- Stage C's reject rules, source-direction check, and Pass 2A now use the same two-path gate and emit route-specific validation metadata.
- Evidence QC requires the V3 selector marker, verifies exactly one source-backed route per format-risk item, and emits route-specific item results.
- Content Polish consumes the Evidence QC route results, preserves the selected path, and emits a root accounting guard plus per-item route statuses.
- Final QC consumes `selected_anchor_path`, `execution_anchor_qc_status`, `structural_value_override_qc_status`, and `non_applicable_anchor_path_reason` rather than requiring an execution-only boolean.
- Stage C, Evidence QC, and Content Polish required-doc lists and governance hierarchies include the two V3 documents and require all ten documents.
- Regression tests cover all intervening-stage and producer-consumer schema requirements.

## Latest verified head

- Intervening-stage patch commit before this record: `7086883fceeacd284851764707bd769fa9195582`.
- The one-shot patch workflow completed successfully and removed all temporary workflow/helper files.
- The next standard workflow-contract validation is triggered by this documentation commit against the final branch state.


## Review 4838068572 end-to-end lineage closure

- Stage C's mandatory `accepted_fact_safe[]` schema now emits `anchor_path_validation`.
- Prompt 0.4 requires that object on format-risk inputs and preserves it byte-for-byte into `addable_merge_safe[]`; missing or contradictory metadata is blocked before Evidence QC.
- Prompt 0.9 verifies both execution and V3 non-execution routes after merge and does not misclassify a valid non-execution route as an execution defect.
- Prompt 1.0 remediates confirmed selected-route, route-status, source-coverage, or lineage defects only.
- The legacy `distinct_follow_up` fresh-anchor presence check remains unconditional; only the new V2 class, incremental-fact, and changed-judgment requirements are scoped to `--require-contract`.
- Regression tests cover Stage C → Prompt 0.4 preservation, production/remediation two-path handling, and legacy fresh-anchor enforcement.

## Review 4838143604 closure

- Prompt 0.8 canonical and subordinate legacy merge-prep overlays now preserve exactly one source-backed execution or V3 non-execution route.
- Stage C certifies a passing route only for `accepted_fact_safe`; format-risk `revise_required` items may honestly carry an unresolved/failed route object until a revise pass resolves it.
- `fresh_follow_up_anchor_class` is type-checked before membership validation, so malformed arrays or objects return findings instead of aborting the validator.
- Regression tests cover merge-prep route compatibility, revise-required unresolved status, and malformed anchor-class types.

## REVIEW_4838187744_ADDRESSING

The review's four findings are addressed as one end-to-end contract correction:

- Final QC now emits item-level anchor-path metadata required by Prompt 0.8.
- Stage B/C revise prompts consume, preserve, resolve, validate, and carry `anchor_path_validation` into Baseline Revalidation.
- Stage C validates the canonical `anchor_classes[]` array rather than an undefined singular key.
- Prompt 1.1 retrospective recognizes a complete source-backed V3 non-execution override as the alternative to an execution anchor.

Regression coverage is included in `validation_scripts/tests/test_workflow_contracts.py`.

## REVIEW_4838372817_ADDRESSING

The review's two findings are addressed as linked contract fixes:

- Prompt 0.2R now accepts `revise_required[]` only for r1 and the immediately previous Prompt 0.3R `revise_required_again[]` for r2+, with explicit generation, mixing, accounting, and anchor-path preservation rules.
- Prompt 1.1 now reads the two governing V3 contracts and uses the same 10-document preflight as other V3-aware stages before auditing Structural Value Override completeness.

Focused regression coverage is provided in `validation_scripts/tests/test_review_4838372817_contracts.py`.

## Review 4838393180 follow-up

- Evidence QC의 초기 format-risk guard를 execution-only에서 exactly-one two-path gate로 정렬했다.
- 유효한 V3 non-execution route는 conventional execution anchor 부재만으로 hold되지 않는다.
- Prompt 1.1 retrospective의 red-team question과 Markdown report contract를 모두 10 required docs 기준으로 통일했다.



## Review 4839991362

- Prompt 0.5 promoted-item producer contract now preserves the complete canonical V3 non-execution package byte-for-byte.
- Prompt 0.6 polished-item producer contract preserves the same package and may not reconstruct or summarize it away.
- Prompt 0.7 and the overlay generator invoke `related_lifecycle_check.py --require-contract` for current V3 Final QC while legacy inventory mode remains permissive.
- Regression coverage blocks package-field loss and non-strict Final QC invocation.
