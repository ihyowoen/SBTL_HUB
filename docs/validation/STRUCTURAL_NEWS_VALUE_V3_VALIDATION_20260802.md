# Structural News Value V3 Validation — 2026-08-02

## Scope

This governance change upgrades the two canonical files introduced by PR #176:

- `docs/STRUCTURAL_NEWS_VALUE_SELECTION.md`
- `docs/llm_prompts/v1/01A_PROMPT_0_1S_Structural_Value_Override.md`

It does not modify card data, the card-run engine, or any production ID.

## V2 framework preservation

V3 preserves and explicitly restates the governing V2 framework:

- credibility, cardability, decision value, and urgency remain separate;
- the before–after and novelty tests remain mandatory;
- the Stage A routing matrix remains explicit;
- `signal = top | high | mid` remains assigned only after the four judgments;
- the 100-point industry-first model remains 25/25/20/10/10/5/3/2;
- the three core industrial dimensions remain 70 points;
- denominator discipline remains mandatory;
- technology-evidence score caps remain mandatory;
- legal-policy Stage 0–6 remains mandatory;
- the twelve mandatory legal-policy questions remain explicit;
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
5. explicit material-follow-up probability review;
6. structural and earnings-specific review pools;
7. portfolio coverage and zero-domain explanations;
8. anti-regression validator outcome names;
9. mandatory next-confirmation points.

## Conflict resolution

The V3 canonical policy explicitly supersedes any older rule that requires a conventional corporate execution event as the sole strict-pass form.

Evidence, baseline, duplicate, lineage, state-ladder, source-diversity, and no-silent-enrichment rules remain unchanged.

## Validation checklist

- canonical version is `STRUCTURAL_NEWS_VALUE_SELECTION_V3`;
- Prompt 0.1S version matches V3;
- both files preserve 25/25/20 core weighting;
- Stage A routing matrix is present;
- signal-assignment rules are present;
- legal-policy Stage 0–6 is present;
- mandatory legal-policy questions are present;
- technology score caps are present;
- IB-grade decision-useful content questions are present;
- blocker output fields are present;
- earnings call and Q&A status fields are present;
- follow-up and incremental-information fields are present;
- mandatory structural domains and zero-coverage treatment are present;
- Stage A no-fetch boundary remains present;
- card data is unchanged.

## Declared implementation boundary

This PR establishes governance authority and the Stage A override.

A follow-up implementation PR must align the downstream executable contracts, including where applicable:

- base Stage A prompt required-doc list and strict-gate wording;
- Stage B/C and post-acceptance prompt field preservation;
- Stage A JSON/CSV schemas;
- structural-value, earnings-Q&A, follow-up, coverage, and content-depth validators;
- artifact contracts and regression fixtures.

The follow-up implementation must not weaken Fact Discipline or the card-run safety engine.
