# LLM Prompt GitHub Canonical v1

Generated KST: `2026-07-09T12:20:13.190794+09:00`

This is the first GitHub-canonical SBTL_HUB LLM prompt package.

## Layout

- `docs/` — live governance docs.
- `docs/llm_prompts/v1/` — numbered prompt package, master rules, and manifests.

## Version rule

Use `v1` for GitHub canonical pathing and PR wording. Prior local iteration labels are not repo-version names.

## Scope

- Replaces 9 live governance docs under `docs/`.
- Adds 14 numbered prompt files under `docs/llm_prompts/v1/`.
- Adds source-diversity and IB/Codex master rules.
- Adds entity alias map and manifests.
- Does not add executable validation scripts in this PR.
- Does not modify `public/data/cards.json`.
- Does not modify app runtime code.

## Validator follow-up

Python validation scripts are intentionally excluded from this docs-only canonical v1 PR. The validator work from PR #151 was preserved on branch `chore/prompt-validation-scripts-hardening-from-pr151` for a separate follow-up PR with fixtures/tests.
