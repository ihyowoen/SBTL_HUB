# LLM Prompt GitHub Canonical v1

Updated KST: `2026-07-19T20:35:00+09:00`

This is the GitHub-canonical SBTL_HUB LLM prompt package.

## Layout

- `docs/` — live governance docs.
- `docs/llm_prompts/v1/` — numbered prompt package, master rules, manifests, mandatory integrity overrides, and stage addenda.
- `validation_scripts/` — executable integrity validators registered by the package manifests.

## Version rule

Use `v1` for GitHub canonical pathing and PR wording. Prior local iteration labels are not repo-version names.

## Current package scope

- 9 live governance documents under `docs/`.
- 14 numbered stage prompt files under `docs/llm_prompts/v1/`.
- Source-diversity and IB/Codex master rules.
- Entity alias map and package manifests.
- 1 mandatory date/story-ID/related integrity override.
- 6 stage-specific hardening addenda for Stage A and Prompts 0.5–0.9.
- 3 executable integrity validators:
  - `validation_scripts/date_role_alignment_check.py`
  - `validation_scripts/story_id_lineage_check.py`
  - `validation_scripts/related_lineage_check.py`
- No change to `public/data/cards.json`.
- No app runtime-code change.

## Mandatory integrity registration

Prompt assemblers and upload tooling must read:

- `DATE_STORYID_RELATED_INTEGRITY_OVERRIDE_MANIFEST.json`
- `LLM_PROMPT_GITHUB_CANONICAL_V1_MANIFEST.json`
- `UPLOAD_MANIFEST.json`

The override, six addenda, and three validators are mandatory package components. Omitting any of them produces an incomplete package.

## Story-ID validator contract

Detection-only invocation:

```bash
python validation_scripts/story_id_lineage_check.py RUN_JSON BASELINE_CARDS_JSON
```

When collisions are detected, the command returns:

```text
BLOCKED_STORY_ID_COLLISIONS_UNQUARANTINED
```

with exit code `2`.

After Stage A has quarantined those collisions, verify the quarantine artifact:

```bash
python validation_scripts/story_id_lineage_check.py \
  RUN_JSON BASELINE_CARDS_JSON \
  --stage-a-results STAGE_A_RESULTS_JSON
```

Only `PASS_NO_COLLISIONS` or `PASS_COLLISIONS_QUARANTINED` is an acceptable success state.

## Historical validator note

Earlier canonical-v1 packaging intentionally excluded the PR #151 validator set. That historical note does not apply to the three integrity validators registered by the current date/story-ID/related override.
