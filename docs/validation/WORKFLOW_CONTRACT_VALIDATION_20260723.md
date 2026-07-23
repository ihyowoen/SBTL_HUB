# Workflow Contract Validation — 2026-07-23

## Scope

Validated against the 20260721 run outputs and the PR #206 final 1,250-card file.

Current-run and legacy scopes are intentionally separated.

## Current-run hard checks

| Check | Result |
|---|---|
| Python compile | PASS |
| Unit tests | **31/31 PASS** |
| Evidence QC — new 35 ID scope | PASS, 0 flags |
| Related structure — new 35 ID scope | PASS, 0 findings |
| Date-role legacy compatibility — new 35 ID scope | PASS, 0 findings |
| New-35 durable-endpoint regression | PASS, 0 listing/search false positives |
| Prompt overlays present | **11/11 named prompt files changed** |
| Overlay application idempotence | PASS |
| GitHub Actions workflow-contract validation | PASS |

## PR #207 review remediation

Codex review produced eight actionable validator findings across three review rounds and one early-head observation.

### First review round

1. **Current-run ID scope could match zero cards and still pass the suite**
   - Added explicit suite-level current-run scope validation.
   - Empty scope, zero matches, or any requested ID absent from `cards[]` fails the suite.
   - Requested, matched, and missing ID counts are recorded.

2. **Blank source URLs could count as diversity**
   - `canonical_url` and `canonical_domain` return an empty value for blank, malformed, or non-HTTP(S) endpoints.
   - Empty canonical URLs, domains, and owners are excluded from diversity sets.
   - Missing usable-source and visible-source URL counts are measured separately.
   - A real source plus a URL-less visible row cannot satisfy `PASS_MULTI_SOURCE`.

3. **Non-cardable Related states could survive before publish flags existed**
   - With `--require-contract`, `same_event_duplicate`, `existing_card_reinforcement`, and `uncertain_needs_review` fail immediately.
   - The validator does not wait for `publish_ready` or a publish state.

### Second review round

4. **Direct validator calls could still bypass a stale ID scope**
   - Evidence QC, Related, and date-role validators now each enforce the exact ID scope themselves.
   - Empty, zero-match, and partial-match scopes return non-zero even when the combined suite is not used.
   - Each report includes an `id_scope` object with requested, matched, and missing IDs.

5. **Editorial-owner count was incorrectly ordered below hostname count**
   - Removed the invalid `owner_count <= domain_count` invariant.
   - Hostname and editorial-owner counts remain independent measures.
   - Two independent filing/court owners on one repository host are valid multi-owner evidence when the remaining gates pass.

6. **Incomplete legacy single-source exceptions could be preserved by strict recomputation**
   - Strict recomputation now preserves an exception only when it has `allowed: true`, a reason, and either `mitigation` or `scope_limits`.
   - Incomplete legacy exceptions return to `HOLD_NEEDS_SOURCE_AUGMENTATION`.
   - Resolution-entry generation skips invalid or missing canonical URLs.

### Third review round

7. **Documented singular Stage B `draft_card` output could bypass the schema gate**
   - The stage artifact collector now accepts both list-valued buckets and singular object buckets.
   - Singular and plural representations are de-duplicated by production/spec ID or stable object value.
   - A noncompliant singular `draft_card` now reports `item_count: 1` and blocks on its missing item fields instead of passing with zero items.

8. **Search, newsroom, category, tag, and similar listing endpoints could count as durable evidence**
   - Canonicalization now rejects explicit search/category/tag/topic paths and generic collection roots such as `/newsroom`.
   - Rejected listing endpoints are excluded from canonical URL, hostname, and editorial-owner counts and are counted as missing durable endpoints.
   - Article paths below collection roots remain valid, for example `/newsroom/2026/article-slug`.
   - Archive handling is conservative: `/archives` and archive pagination are listings, while durable document paths such as SEC `/Archives/edgar/...` remain valid.
   - The final rule produced zero listing/search false positives across the PR #206 new-35 `fact_sources` fixture.

### Early-head observation

The first review stated that `validation_scripts/related_lifecycle_check.py` did not exist. That review targeted commit `74987faf68`; the validator was added in later commits and is now referenced by the contracts, prompt overlays, suite, tests, and CI.

## GitHub Actions proof

Workflow: `Workflow contract validation`

- Tested executable-code head: `b3a183ce8e624c17889ff170e606ed47cc574fbd`
- Run ID: `29982150687`
- Conclusion: **success**
- Compile validators: PASS
- Workflow-contract tests: **31/31 PASS**
- Prompt overlay check: PASS

Subsequent commits only finalize this validation record; executable validator code is unchanged.

## Legacy inventory

Full 1,250-card Related structural inventory reports:

- affected legacy cards: **13**
- dangling Related edges: **14**
- current-run new 35 affected: **0**

The legacy result is not waived and is not mixed into the current-run pass. It is preserved in:

- `docs/remediation/RELATED_LEGACY_DANGLING_MANIFEST_20260723.json`
- `docs/remediation/RELATED_LEGACY_DANGLING_MANIFEST_20260723.md`

## Source-audit regression

The PR #206 cases and Codex review cases were used as regressions for:

- evidence rows versus canonical URL counts;
- canonical hostname count versus editorial-owner count;
- multiple independent owners sharing one hostname;
- conditional Bloomberg/Bernama syndication grouping;
- source-discovery ledger preservation;
- home/landing-page detection;
- search, newsroom, category, tag, topic and pagination endpoint rejection;
- preservation of durable article paths below collection roots;
- preservation of SEC EDGAR document paths below `/Archives/edgar/`;
- blank or malformed source-URL exclusion;
- bounded single-source exception validation;
- resolution URL synchronization;
- exact current merge-ID scoping in each validator;
- empty, zero-match, and partially missing scope rejection;
- singular and plural Stage B artifact collection.

Result for the new 35 fixture: **0 Evidence QC flags and 0 listing/search false positives**.

## Prompt coverage

The overlay generator updated:

1. Stage A
2. Stage B r0
3. Stage C r0
4. Stage B Revise
5. Stage C Revise
6. Prompt 0.4
7. Prompt 0.5
8. Prompt 0.6
9. Prompt 0.7
10. Prompt 0.8
11. Prompt 0.9

The one-time generation and review-patching workflows were removed after their changes were produced. The idempotent overlay tool remains for future controlled updates.

## Remaining acceptance step

- rerun Codex review against the latest head;
- address any new findings;
- keep legacy Related remediation as a separate audited change;
- merge only after the latest review is clean or all remaining comments are explicitly dispositioned.
