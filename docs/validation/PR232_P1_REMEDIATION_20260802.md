# PR #232 P1 Remediation Record — 2026-08-02

## Reviewed head

- PR: `#232`
- branch: `agent/card-run-engine-v1`
- remediated head: `8479cebd83503033e70e39063c70a2be37845ec8`
- Actions: `apply-card-run` run `#19`
- result: `validate-engine=PASS`, `apply=PASS`

## P1-1 — Govern canonical-data PRs

Resolved by adding the following workflow triggers:

- `data/cards.full.json`
- `public/data/cards.json`

The run-resolution step now inspects the PR diff. If either canonical path changed and no `runs/**/card-run.json` exists, the job fails. Code-only PRs remain eligible to skip data apply.

## P1-2 — Validate fork PRs

Resolved by running the `apply` job for both same-repository and fork PRs.

- PR head checkout uses `refs/pull/<number>/head`.
- Fork PRs execute run resolution, stage-status validation, baseline locking, apply, full/lean validation and byte-exact verify.
- Credential persistence and generated commit/push remain restricted to same-repository PR branches.

## P1-3 — Explicit stage-artifact PASS allowlist

Resolved with `scripts/validate_card_run_stage_artifacts.mjs`.

The preflight:

- resolves every insert/update/related_add `stage_artifacts` reference;
- requires a non-empty repository JSON file;
- requires an explicit marker from `status`, `artifact_status`, `validation_status`, `state`, or `result`;
- accepts only an enumerated passing state;
- rejects `HOLD`, `SKIPPED`, missing status and unregistered values before engine apply or verify.

The self-test covers:

- `PASS`: accepted;
- `accepted_fact_safe`: accepted;
- `HOLD`: rejected;
- `SKIPPED`: rejected;
- missing status: rejected.

## Scope boundary

This remediation changes no card data. Structural-news-value V3 policy work remains a separate governance PR after PR #232 is independently reviewed and merged.
