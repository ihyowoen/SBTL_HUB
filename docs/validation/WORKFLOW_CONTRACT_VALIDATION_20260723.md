# Workflow Contract Validation — 2026-07-23

## Scope

Validated against the 20260721 run outputs and the PR #206 final 1,250-card file.

Current-run and legacy scopes are intentionally separated.

## Current-run hard checks

| Check | Result |
|---|---|
| Python compile | PASS |
| Unit tests | **19/19 PASS** |
| Evidence QC — new 35 ID scope | PASS, 0 flags |
| Related structure — new 35 ID scope | PASS, 0 findings |
| Date-role legacy compatibility — new 35 ID scope | PASS, 0 findings |
| Prompt overlays present | **11/11 named prompt files changed** |
| Overlay application idempotence | PASS |
| GitHub Actions workflow-contract validation | PASS |

## PR #207 review remediation

Codex review on the final pre-review head produced three actionable validator findings and one early-head observation.

### Actionable findings addressed

1. **Current-run ID scope could match zero cards and still pass**
   - Added an explicit `current_run_scope_validation` hard check.
   - Empty scope, zero matches, or any requested ID absent from `cards[]` now fails the suite.
   - The suite records requested, matched, and missing ID counts.

2. **Blank source URLs could count as diversity**
   - `canonical_url` and `canonical_domain` now return an empty value for blank, malformed, or non-HTTP(S) endpoints.
   - Empty canonical URLs, domains, and owners are excluded from diversity sets.
   - Missing visible-source URL counts are measured separately.
   - A real source plus a URL-less visible row cannot satisfy `PASS_MULTI_SOURCE`.

3. **Non-cardable Related states could survive before publish flags existed**
   - With `--require-contract`, `same_event_duplicate`, `existing_card_reinforcement`, and `uncertain_needs_review` now fail immediately.
   - The validator no longer waits for `publish_ready` or a publish state to appear.

### Early-head observation

The first review stated that `validation_scripts/related_lifecycle_check.py` did not exist. That review targeted commit `74987faf68`; the validator was added in later commits and is now referenced by the contracts, prompt overlays, suite, tests, and CI.

## GitHub Actions proof

Workflow: `Workflow contract validation`

- Run ID: `29979376929`
- Conclusion: **success**
- Compile validators: PASS
- Workflow-contract tests: PASS
- Prompt overlay check: PASS

## Legacy inventory

Full 1,250-card Related structural inventory reports:

- affected legacy cards: **13**
- dangling Related edges: **14**
- current-run new 35 affected: **0**

The legacy result is not waived and is not mixed into the current-run pass. It is preserved in:

- `docs/remediation/RELATED_LEGACY_DANGLING_MANIFEST_20260723.json`
- `docs/remediation/RELATED_LEGACY_DANGLING_MANIFEST_20260723.md`

## Source-audit regression

The PR #206 cases were used as regressions for:

- evidence rows versus canonical URL counts;
- canonical hostname count versus editorial-owner count;
- conditional Bloomberg/Bernama syndication grouping;
- source-discovery ledger preservation;
- landing-page detection;
- blank or malformed source-URL exclusion;
- single-source exception validation;
- resolution URL synchronization;
- current merge-ID scoping;
- stale or partially missing ID-scope rejection.

Result for the new 35 fixture: **0 Evidence QC flags**.

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

The one-time generation workflow was removed after prompt files were produced. The idempotent overlay tool remains for future controlled updates.

## Remaining acceptance step

- rerun Codex review against the latest head;
- address any new findings;
- keep legacy Related remediation as a separate audited change;
- merge only after the latest review is clean or all remaining comments are explicitly dispositioned.
