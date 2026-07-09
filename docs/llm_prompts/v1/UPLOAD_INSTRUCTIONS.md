# Upload Instructions — LLM Prompt GitHub Canonical v1

Generated KST: `2026-07-09T15:33:00+09:00`

```bash
git checkout main
git pull
git checkout -b docs/llm-prompt-canonical-v1
unzip LLM_PROMPT_GITHUB_CANONICAL_V1_FINAL_REPO_READY_*.zip
git add docs
git commit -m "docs: add LLM prompt canonical v1"
git push -u origin docs/llm-prompt-canonical-v1
```

PR title:

```text
docs: add LLM prompt canonical v1
```

PR body:

```text
Adds the first GitHub-canonical LLM prompt package v1.

Scope:
- Replaces live prompt governance docs under docs/
- Adds numbered A/B/C and post-acceptance prompt files under docs/llm_prompts/v1/
- Adds source-diversity and IB/Codex master rules
- Adds entity alias map and manifests
- Keeps GitHub canonical version at v1

Notes:
- Documentation/prompt-governance PR only
- No validation scripts in this PR
- No public/data/cards.json change
- No app runtime code change
```

Validator follow-up:

```text
The validator work from PR #151 was preserved on branch chore/prompt-validation-scripts-hardening-from-pr151 and should be opened later as a separate PR with fixtures/tests.
```
