# Structural News Value V3 Validation — 2026-08-02

## Scope

This governance change upgrades the canonical structural-value and Stage A override files introduced by PR #176 and aligns the Related lifecycle contract:

- `docs/STRUCTURAL_NEWS_VALUE_SELECTION.md`
- `docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md`
- `docs/RELATED_LIFECYCLE_CONTRACT.md`

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
7. structural and earnings-specific review pools;
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
- mandatory structural domains and zero-coverage treatment are present;
- Stage A no-fetch boundary remains present;
- card data is unchanged.

## Declared implementation boundary

This PR establishes governance authority, the Stage A override, and the Related lifecycle semantic contract.

A follow-up implementation PR must align the downstream executable contracts, including where applicable:

- base Stage A prompt required-doc list and strict-gate wording;
- Stage B/C and post-acceptance prompt field preservation;
- Stage A JSON/CSV schemas;
- Related JSON/schema and validators for the new anchor-class fields;
- structural-value, earnings-Q&A, follow-up, coverage, and content-depth validators;
- artifact contracts and regression fixtures.

The follow-up implementation must not weaken Fact Discipline or the card-run safety engine.
