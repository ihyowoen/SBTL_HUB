# Workflow Contract Validation — 2026-07-23

## Scope

Validated against the 20260721 run outputs and the PR #206 final 1,250-card file.

Current-run and legacy scopes are intentionally separated.

## Current-run hard checks

| Check | Result |
|---|---|
| Python compile | PASS |
| Unit tests | **13/13 PASS** |
| Evidence QC — new 35 ID scope | PASS, 0 flags |
| Related structure — new 35 ID scope | PASS, 0 findings |
| Date-role legacy compatibility — new 35 ID scope | PASS, 0 findings |
| Prompt overlays present | **11/11 named prompt files changed** |
| Overlay application idempotence | PASS |

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
- single-source exception validation;
- resolution URL synchronization;
- current merge-ID scoping.

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

Before the draft PR is marked ready:

- run PR-level review on the final diff;
- address any review findings;
- rerun the 13 tests and current-run scoped suite;
- keep legacy Related remediation as a separate audited change.
