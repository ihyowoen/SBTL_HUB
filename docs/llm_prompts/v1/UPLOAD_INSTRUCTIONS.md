# Upload Instructions — LLM Prompt GitHub Canonical v1

Updated KST: `2026-07-19`

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

## Required package pre-commit checks

These checks validate the prompt/validator package itself and must pass for a docs-only package PR:

```bash
python -m py_compile \
  validation_scripts/date_role_alignment_check.py \
  validation_scripts/story_id_lineage_check.py \
  validation_scripts/related_lineage_check.py

python - <<'PY'
import json
from pathlib import Path

manifest_paths = [
    Path("docs/llm_prompts/v1/LLM_PROMPT_GITHUB_CANONICAL_V1_MANIFEST.json"),
    Path("docs/llm_prompts/v1/UPLOAD_MANIFEST.json"),
    Path("docs/llm_prompts/v1/DATE_STORYID_RELATED_INTEGRITY_OVERRIDE_MANIFEST.json"),
]
for path in manifest_paths:
    json.loads(path.read_text(encoding="utf-8"))

upload = json.loads(manifest_paths[1].read_text(encoding="utf-8"))
listed = []
for value in upload.get("paths", {}).values():
    if isinstance(value, list):
        listed.extend(value)
missing = [path for path in listed if not Path(path).exists()]
if missing:
    raise SystemExit(f"missing package files: {missing}")
print("PASS: manifests parse and all listed package paths exist")
PY

BASE_REF="${BASE_REF:-origin/main}"
MERGE_BASE="$(git merge-base HEAD "$BASE_REF")"
git diff --quiet "$MERGE_BASE" HEAD -- public/data/cards.json || {
  echo "FAIL: docs-only baseline exception requires unchanged public/data/cards.json"
  exit 1
}
```

The final command is mandatory for the docs-only exception. If `public/data/cards.json` differs from the merge base, the date and related validators become hard blocking checks and the PR must include the corresponding data remediation.

## Run-bound story-ID check

When a current run and baseline are available, run:

```bash
python validation_scripts/story_id_lineage_check.py \
  RUN_JSON BASELINE_CARDS_JSON
```

The validator supports both canonical source shapes:

- `stories[]`
- `final_news_llm_input.stories[]`

It also reads every current Stage A terminal or lineage container:

- `decision_ledger[]`
- `strict_passed_spec[]`
- `candidate_review_pool[]`
- `watchlist_context_pool[]`
- `existing_reinforcement[]`
- `support_source_only[]`
- `rejected[]`
- `reject_or_support_only_pool[]`

Identity is evaluated for each run record and each baseline card independently. Do not treat a story ID as trusted merely because another record or another baseline card with the same story ID has an exact URL match. The output separates:

- unique collision story IDs: `collision_count`
- colliding run records: `collision_record_count`
- unmatched run-record/baseline-card pairs: `collision_pair_count`
- partially matched records: `partial_identity_match_record_count`

When cross-run collisions exist, detection-only mode intentionally exits with code `2` and status:

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

## Baseline and production data audits

The following checks validate card data rather than the docs/validator package:

```bash
python validation_scripts/date_role_alignment_check.py BASELINE_CARDS_JSON
python validation_scripts/related_lineage_check.py BASELINE_CARDS_JSON
```

They are hard gates when any of the following applies:

- `public/data/cards.json` is changed;
- Prompt 0.8 merge preparation is running;
- Prompt 0.9 production verification is running;
- a baseline date/related remediation PR is being prepared.

For a docs-only package PR that does not modify `public/data/cards.json`, existing baseline findings must be recorded but do not block the package commit. At the time of this hardening PR, the unchanged baseline has five historical date-integrity findings and unresolved historical related references that are preserved for lineage-safe remediation. This exception applies only when the `git diff --quiet` check above proves the baseline card file is unchanged; any card-data change or new finding restores the hard gate.

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
- Existing unchanged-baseline findings are reported separately from package-integrity checks
```

## Historical note

The earlier PR #151 validator set remains a separate historical follow-up. It does not replace or negate the three validators registered by the current date/story-ID/related integrity override.
