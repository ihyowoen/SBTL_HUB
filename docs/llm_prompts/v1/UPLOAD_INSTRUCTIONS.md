# Upload Instructions — LLM Prompt GitHub Canonical v1

Updated KST: `2026-07-19T20:35:00+09:00`

## Package contents

The upload package includes prompt/governance documents and three executable integrity validators. Both directories are mandatory:

- `docs/`
- `validation_scripts/`

The required package inventory is defined by:

- `docs/llm_prompts/v1/LLM_PROMPT_GITHUB_CANONICAL_V1_MANIFEST.json`
- `docs/llm_prompts/v1/UPLOAD_MANIFEST.json`
- `docs/llm_prompts/v1/DATE_STORYID_RELATED_INTEGRITY_OVERRIDE_MANIFEST.json`

## Upload

```bash
git checkout main
git pull
git checkout -b docs/llm-prompt-canonical-v1
unzip LLM_PROMPT_GITHUB_CANONICAL_V1_FINAL_REPO_READY_*.zip
git add docs validation_scripts
git commit -m "docs: add LLM prompt canonical v1"
git push -u origin docs/llm-prompt-canonical-v1
```

Do not use `git add docs` alone. That would omit the registered validators and produce an incomplete package.

## Required pre-commit checks

```bash
python validation_scripts/date_role_alignment_check.py BASELINE_CARDS_JSON
python validation_scripts/related_lineage_check.py BASELINE_CARDS_JSON
python validation_scripts/story_id_lineage_check.py RUN_JSON BASELINE_CARDS_JSON
```

The story-ID command is detection-only. When cross-run collisions exist, it intentionally exits with code `2` and status:

```text
BLOCKED_STORY_ID_COLLISIONS_UNQUARANTINED
```

After Stage A has recorded collision quarantine fields, rerun:

```bash
python validation_scripts/story_id_lineage_check.py \
  RUN_JSON BASELINE_CARDS_JSON \
  --stage-a-results STAGE_A_RESULTS_JSON
```

Acceptable story-ID validator success states are:

- `PASS_NO_COLLISIONS`
- `PASS_COLLISIONS_QUARANTINED`

## PR title

```text
docs: add LLM prompt canonical v1
```

## PR body scope

```text
Adds or updates the GitHub-canonical LLM prompt package v1.

Scope:
- Replaces live prompt governance docs under docs/
- Adds numbered A/B/C and post-acceptance prompt files under docs/llm_prompts/v1/
- Adds source-diversity and IB/Codex master rules
- Adds mandatory integrity override and stage addenda
- Adds registered date, story-ID, and related-lineage validators
- Keeps GitHub canonical version at v1

Notes:
- No public/data/cards.json change
- No app runtime-code change
- Omitting registered validators is a package failure
```

## Historical note

The earlier PR #151 validator set remains a separate historical follow-up. It does not replace or negate the three validators registered by the current date/story-ID/related integrity override.
