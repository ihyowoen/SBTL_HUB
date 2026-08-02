# Structural News Value V3 Validation — 2026-08-02

## Scope

This rollout upgrades the canonical structural-value policy and aligns the executable selector, evidence, final-QC, and Related contracts:

- `docs/STRUCTURAL_NEWS_VALUE_SELECTION.md`
- `docs/llm_prompts/v1/01_PROMPT_0_1_Stage_A.md`
- `docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md`
- `docs/llm_prompts/v1/02_PROMPT_0_2_Stage_B_r0.md`
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
- Stage B and Final QC accept only fully evidenced V3 non-execution anchor packages;
- mandatory structural domains and zero-coverage treatment are present;
- Stage A no-fetch boundary remains present;
- card data is unchanged.

## Executable alignment completed in this PR

This PR aligns the central V3 feature with the active execution path:

- base Stage A accepts either a concrete execution anchor or a complete V3 non-execution override for format-risk strict items;
- structural and earnings review categories are subtypes of the supported `candidate_review_pool`, not unsupported top-level partitions;
- the Stage A JSON and CSV contracts carry and validate the subtype and override fields;
- Stage B verifies the exact non-execution anchor claims and evidence targets instead of demanding an execution event;
- Final QC accepts a source-backed V3 non-execution path and hard-fails incomplete or inflated overrides;
- the Related production validator enforces fresh anchor class, incremental fact, and changed judgment for every current-run `distinct_follow_up` under `--require-contract`, while preserving legacy unflagged validation behavior;
- regression fixtures cover missing and invalid anchor classes, missing incremental fact, missing changed judgment, and legacy unflagged behavior.

Remaining future implementation may add dedicated structural-value, earnings-Q&A, portfolio-coverage, and content-depth validators, but it must not reintroduce an execution-only gate or unsupported review partition. Fact Discipline and the card-run safety engine remain unchanged.

## Review 4837529388 closure

The review findings are addressed as follows:

- Stage A, Stage B, and Final QC now share the same execution-or-V3-non-execution eligibility model;
- the active Stage A format-risk presumption gate, strict-pass condition, required item object, lineage metadata, report contract, and CSV contract carry the override fields;
- structural and earnings review categories are `candidate_review_pool` subtypes, not unsupported top-level partitions;
- Related V2 fields are enforced only for current-run strict validation with `--require-contract`;
- legacy unflagged inventory validation is unchanged;
- temporary patch workflows, helper scripts, and generated Python bytecode are absent from the final diff.

## Review 4837763004 downstream residual closure

- Stage B source-direction and draft-blocked lists now reject format-risk items only when neither the source-backed execution path nor the complete source-backed V3 non-execution path is available.
- Final QC's later safety overlay and publish-ready checklist now validate both source-backed paths and carry explicit anchor-path QC status.
- Stage B and Final QC required-doc accounting now consistently requires all ten governance documents.
- Regression tests fail on the removed execution-only blocker phrases or any return to eight-document accounting.

## Latest verified head

- Review-fix commit before this record: `54313c7d44f321faa421b9c8688a6813ae42c79b`.
- One-shot patch workflow completed successfully and removed all temporary workflow/helper files.
- The next normal commit exists solely to record this closure and trigger the standard workflow-contract validation on the final branch state.
