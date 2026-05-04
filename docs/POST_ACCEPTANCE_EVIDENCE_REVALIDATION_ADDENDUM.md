# Post-Acceptance Evidence Revalidation Addendum

## 0. Role of this addendum

This addendum hardens the post-acceptance workflow added in PR #104.

It is based on the 2026-05-04 dry run, where the A/B/C stages worked as intended but the post-acceptance layer allowed a duplicate-safe addable file to be treated as if it were publish-ready before evidence completeness had been revalidated.

This document must be read together with:

1. `docs/FACT_DISCIPLINE.md`
2. `docs/PROMPT_ABC_DEFAULT_MODE.md`
3. `docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md`
4. `docs/WORKFLOW.md`
5. `docs/OPERATIONS.md`

If this addendum conflicts with `FACT_DISCIPLINE.md`, follow `FACT_DISCIPLINE.md`.
If this addendum conflicts with the earlier post-acceptance QC document, this addendum is the stricter downstream rule for evidence revalidation after baseline duplicate checks.

---

## 1. Dry-run finding being fixed

The 2026-05-04 dry run showed the following state progression:

```text
5,101 stories
→ Stage A strict passed_spec 54
→ Stage B clean candidates 27
→ Stage C accepted_fact_safe 13
→ post-QC addable candidates 10
→ full baseline revalidation addable_merge_safe 6
→ evidence-complete publish-ready cards: not yet proven
```

The Stage A/B/C filtering was directionally correct.
The failure occurred after post-acceptance QC:

```text
full baseline revalidation reduced 10 addable candidates to 6 duplicate-safe addable cards,
but the surviving 6 were treated as final PR candidates before evidence completeness was rerun.
```

Hard lesson:

```text
accepted_fact_safe != addable_merge_safe != evidence_complete != publish_ready
```

---

## 2. P0 hard gates

These rules are mandatory. Any violation blocks `publish_ready=true` and blocks `FINAL` / `PR_CANDIDATE` naming.

### P0-1. Full baseline revalidation is merge-safety only

Full baseline revalidation may decide only:

- `addable_merge_safe`
- `duplicate_hold`
- `existing_reinforcement`
- `withheld_reinforcement`
- `baseline_conflict`

It must not assign or preserve `publish_ready=true`.

After full baseline revalidation, all surviving addable cards must be reset to:

```json
"publish_ready": false
```

They may become `publish_ready=true` only after evidence completeness QC passes.

### P0-2. Addable is not publish-ready

A card may be safe to append by duplicate/event rules and still fail source/claim evidence rules.

```text
addable_merge_safe != publish_ready
```

Never use expected final count to force evidence-failed cards into the final file.
If only four of six addable cards pass evidence QC, the final count must reflect four added cards, not six.

### P0-3. Evidence completeness QC is mandatory after revalidation

Every surviving addable card must rerun evidence completeness QC after full baseline revalidation.

Hard fail if any of the following is true:

- `source_quote` is missing
- `source_quote` is headline-only
- `source_quote` is RSS-only
- `source_quote` is snippet-only
- `source_quote` is listing-card text only
- `source_quote` is exact title text
- `source_quote` is a near-title paraphrase without body-level support
- `source_quote_status` is missing, unknown, `headline_only`, `snippet_only`, `not_generated`, or `not_generated_no_direct_quote_extraction`
- `fact_sources` is URL-only
- `claim` is copied from the headline
- `claim` is a label rather than a concrete factual claim
- visible-field numeric claims lack source support
- single-source justification relies on headline-only evidence

No override is allowed for headline-only evidence.

### P0-4. Stage B coverage is not final evidence coverage

Stage B coverage describes source availability or fetch quality. It must not be carried forward as final evidence coverage.

Use separate concepts:

| Stage | Preferred field | Meaning |
|---|---|---|
| Stage B | `fetch_coverage` or `source_availability` | Whether the source/article appears available enough for Prompt C review |
| Post-acceptance final QC | `evidence_coverage` | Whether final card claims are backed by non-headline `source_quote` and valid `fact_sources` |

A Stage B value such as `source_coverage=strong` cannot become final `evidence_coverage=strong` unless the final card-level evidence independently passes this addendum.

### P0-5. Publish-ready fact_sources schema

For any card marked `publish_ready=true`, each core `fact_sources` entry must include:

```json
{
  "source_name": "...",
  "source_url": "...",
  "claim": "concrete factual claim supported by this source",
  "source_quote": "body-level or official/primary quote, not a headline",
  "evidence_role": "primary_event_evidence | secondary_event_evidence | background_context",
  "supports": ["title", "sub", "fact", "implication"],
  "checked_at": "...",
  "fetch_method": "..."
}
```

`fetched_at` may be used instead of `checked_at` if that is the existing schema.

Invalid for publish-ready:

- URL-only source
- title-only `source_quote`
- headline copied into `claim`
- missing `evidence_role`
- missing `supports`
- `source_quote_status = not_generated_no_direct_quote_extraction`

### P0-6. Single-source exception is narrow

Single-source cards can be `publish_ready=true` only if the single source is:

- official filing
- government release
- company official release
- regulatory document
- primary dataset/statistics page
- article body with direct source text sufficient for all core visible claims

Single-source cards cannot be publish-ready if the only evidence is:

- RSS headline
- search snippet
- paywall headline only
- listing page title
- repost without body details
- `source_quote` not extracted
- headline-only article card

`single_source_reason` is not a waiver. It must explain why the single source itself is body-level or official primary evidence sufficient for the visible claims.

### P0-7. Final naming rule

Do not use these labels in filenames, inventory, or final response unless merge safety and evidence completeness both pass:

- `FINAL`
- `PR_CANDIDATE`
- `publish_ready`
- `GitHub-ready`

If only duplicate/event QC passed, use one of:

- `DUPLICATE_SAFE_ONLY`
- `MERGE_SAFE_PENDING_EVIDENCE`
- `EVIDENCE_QC_HOLD`

---

## 3. P1 stage-operation hardening

These rules are not the direct cause of the 2026-05-04 failure, but they were validated by the same dry run and should be applied in future runs.

### P1-1. KEEP is not an editorial pass

`KEEP` is an upstream recommendation, not a final editorial pass.

Prompt A must run a lane-sanity gate inside KEEP before producing strict `passed_spec`.

Downgrade to `needs_review` or `rejected` when an item is:

- consumer/lifestyle news
- real estate or model-house news
- weather or local life information
- generic education/culture/publicity
- generic finance/insurance/ETF without battery/materials/ESS/grid/supply-chain relevance
- general politics/diplomacy without direct industrial relevance
- weakly connected to SBTL_HUB lanes

Prompt A output should distinguish:

- `legacy_keep`
- `strict_passed_spec`
- `needs_review`
- `rejected`
- `existing_reinforcement`

### P1-2. needs_review is not rejection

Track review pools separately:

| Pool | Meaning |
|---|---|
| Stage A `needs_review` | lane-sanity review pool; do not auto-fetch unless user opens a review run |
| Stage B `needs_review=true` | source/duplicate/lane issue review pool; eligible for later rescue or evidence run |
| Stage C `maybe` | manual review or roundup pool |
| Stage C `dropped` | rejected unless user explicitly reopens |

If a dry run defers review pools, the report must state:

- deferred intentionally
- not included in current accepted/addable count
- eligible or not eligible for later review

### P1-3. Stage C card-value gate

Strong source/fetch coverage does not guarantee card value.

Prompt C must separately evaluate:

1. strategic relevance
2. SBTL_HUB lane fit
3. decision usefulness
4. duplicate cluster role
5. source strength

A candidate with strong source availability may still be `dropped` or `support_source_only` if it is not worth an independent SBTL_HUB card.

---

## 4. P2 reporting and artifact rules

### P2-1. QC report must be data-driven

Final QC reports must compute failure counts from actual JSON fields, not only checklist statements.

At minimum, report counts for:

- source_quote missing
- source_quote headline-only
- source_quote_status fail
- URL-only fact_sources
- claim copied from headline
- missing evidence_role
- missing supports
- single-source cards
- single-source headline-only cards
- publish_ready true despite evidence fail
- addable_hold_source_gap cards

If any hard-fail count is non-zero, final QC cannot be PASS.

### P2-2. Superseded/HOLD manifest reason codes

Every superseded or HOLD file must include a reason code.

Allowed reason codes:

```text
evidence_qc_failed
headline_only_source_quote
claim_coverage_missing
baseline_duplicate_revalidated
merge_safe_pending_evidence
replaced_by_evidence_revalidated_version
```

### P2-3. Final output naming

Preferred output set after evidence revalidation:

```text
evidence_revalidated_addable_payload_{run_tag}_{N}.json
final_cards_{run_tag}_EVIDENCE_REVALIDATED_{final_count}.json
evidence_qc_report_{run_tag}.md
superseded_and_review_pool_manifest_{run_tag}.json
```

Do not produce or advertise a `FINAL` / `PR_CANDIDATE` file before evidence revalidation passes.

---

## 5. Required final decision states

After full baseline revalidation and evidence QC, every surviving candidate must be assigned exactly one state:

| State | Meaning |
|---|---|
| `publish_ready` | merge-safety and evidence completeness both pass |
| `addable_hold_source_gap` | duplicate-safe but evidence incomplete |
| `duplicate_hold` | same URL/event/fingerprint already exists in baseline |
| `support_source_only` | useful only as supporting evidence for another card |
| `review_pool_deferred` | intentionally deferred for later review |
| `rejected` | not suitable for this run |

Do not mix these states.
Do not treat `addable_hold_source_gap` as publish-ready.

---

## 6. Operational final rule

The final locked rule is:

```text
Full baseline revalidation decides addable/hold only.
It must reset publish_ready=false for all surviving addable cards.
Publish-ready may be assigned only after surviving addable cards pass evidence completeness QC.
```

If this rule blocks all addable cards, the correct final output is zero publish-ready additions, not a forced final-count match.
