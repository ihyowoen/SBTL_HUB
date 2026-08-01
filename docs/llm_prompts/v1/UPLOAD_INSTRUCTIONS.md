# Upload Instructions — Dynamic Governance Prompt Package

**Stable package path:** `docs/llm_prompts/v1/`  
**Active package version:** `LLM_PROMPT_GITHUB_CANONICAL_V2_DYNAMIC_GOVERNANCE_COMPLETENESS`

## 1. Required package roots and registered runtime files

The package must include:

```text
docs/
validation_scripts/
scripts/lean_cards.mjs
.github/workflows/lean-cards.yml
```

Do not upload a remembered subset of governance files, validators, runtime contracts, or regression tests.

The package must include the current paths registered by:

- `docs/llm_prompts/v1/LLM_PROMPT_GITHUB_CANONICAL_V1_MANIFEST.json`
- `docs/llm_prompts/v1/UPLOAD_MANIFEST.json`
- `docs/llm_prompts/v1/DATE_STORYID_RELATED_INTEGRITY_OVERRIDE_MANIFEST.json`
- `docs/llm_prompts/v1/DYNAMIC_GOVERNANCE_COMPLETENESS_OVERRIDE_MANIFEST.json`
- `docs/llm_prompts/v1/GOVERNANCE_LIFECYCLE_REGISTRY.json`

Static counts are informational. Stage 0.0D reconciles the actual repository universe at run time.

## 2. Mandatory governance entry

Every ordinary run must execute:

```text
0.0D Document Universe Preflight
→ 0.0C Coverage Discovery
```

before Stage A.

Stage 0.0D reads or parses every file under `docs/**` in full, classifies applicability, and verifies the current repository SHA.

Stage 0.0C performs missing-news, follow-up, correction, and existing-card reinforcement discovery. Stage A remains selector-only.

## 3. Upload workflow

```bash
git checkout main
git pull --ff-only
git checkout -b agent/dynamic-governance-completeness

# Copy the complete intended governance, validator, runtime-contract, workflow, and test changes.
git add \
  docs \
  validation_scripts \
  scripts/lean_cards.mjs \
  .github/workflows/lean-cards.yml

git status --short
git diff --cached --stat
```

Do not stage card data in this package PR. Registered runtime contract files must be staged; otherwise the manifest and uploaded package diverge.

## 4. Required JSON, path, and staging validation

```bash
python - <<'PY'
import json
import subprocess
from pathlib import Path

manifest_paths = [
    Path("docs/llm_prompts/v1/LLM_PROMPT_GITHUB_CANONICAL_V1_MANIFEST.json"),
    Path("docs/llm_prompts/v1/UPLOAD_MANIFEST.json"),
    Path("docs/llm_prompts/v1/DATE_STORYID_RELATED_INTEGRITY_OVERRIDE_MANIFEST.json"),
    Path("docs/llm_prompts/v1/DYNAMIC_GOVERNANCE_COMPLETENESS_OVERRIDE_MANIFEST.json"),
    Path("docs/llm_prompts/v1/GOVERNANCE_LIFECYCLE_REGISTRY.json"),
]

for path in manifest_paths:
    json.loads(path.read_text(encoding="utf-8"))

upload = json.loads(manifest_paths[1].read_text(encoding="utf-8"))
listed = []
for value in upload.get("paths", {}).values():
    if isinstance(value, list):
        listed.extend(value)
registered = sorted(set(listed))

missing = [path for path in registered if not Path(path).exists()]
if missing:
    raise SystemExit(f"missing registered package files: {missing}")

staged = set(
    subprocess.check_output(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        text=True,
    ).splitlines()
)

required_staged = {
    "scripts/lean_cards.mjs",
    ".github/workflows/lean-cards.yml",
    "validation_scripts/tests/test_lean_cards_exporter.py",
}
missing_staged = sorted(required_staged - staged)
if missing_staged:
    raise SystemExit(f"registered runtime/test files not staged: {missing_staged}")

canonical = json.loads(manifest_paths[0].read_text(encoding="utf-8"))
required_overrides = {
    "DATE_STORYID_RELATED_INTEGRITY_V1",
    "DYNAMIC_GOVERNANCE_COMPLETENESS_V1",
}
registered_overrides = {
    row.get("override_id")
    for row in canonical.get("override_registrations", [])
}
if not required_overrides <= registered_overrides:
    raise SystemExit(
        f"missing mandatory override registration: "
        f"{sorted(required_overrides - registered_overrides)}"
    )

print("PASS: manifests parse, registered files exist, runtime/test paths are staged")
PY
```

## 5. Required syntax and regression checks

```bash
python -m py_compile \
  validation_scripts/date_role_alignment_check.py \
  validation_scripts/story_id_lineage_check.py \
  validation_scripts/related_lineage_check.py \
  validation_scripts/date_role_freshness_check.py \
  validation_scripts/evidence_qc_v8_check.py \
  validation_scripts/related_lifecycle_check.py \
  validation_scripts/stage_artifact_contract_check.py \
  validation_scripts/run_workflow_contract_suite.py \
  validation_scripts/tests/test_lean_cards_exporter.py

python -m unittest discover -s validation_scripts/tests -v
node scripts/lean_cards.mjs --check
```

The exporter regression suite must cover malformed-public recovery, direct path collision, and hard-link path collision without modifying the canonical full.

## 6. Card-data isolation check

```bash
BASE_REF="${BASE_REF:-origin/main}"
MERGE_BASE="$(git merge-base HEAD "$BASE_REF")"

for path in data/cards.full.json public/data/cards.json; do
  git diff --quiet "$MERGE_BASE" HEAD -- "$path" || {
    echo "FAIL: governance/runtime-contract package PR must not modify $path"
    exit 1
  }
done
```

This package may change registered runtime contract code and CI workflow, but not card data.

Recommended separation:

- governance/runtime-contract package PR: documents, manifests, prompts, validators, exporter, exporter workflow, and their tests;
- migration/data PR: explicitly activated transition data;
- incremental-engine PR: run schema, generic apply logic, declared-diff validation, and additional CI automation;
- ordinary data PR: governed run operations only.

## 7. Migration handling

Files under `docs/migrations/` are included for traceability but do not apply automatically.

A migration affects a run only when the run intake explicitly records:

- migration path;
- activation authority;
- bounded scope;
- baseline SHAs;
- completion condition.

Do not copy migration-specific dates, counts, run IDs, or branch details into permanent governance documents.

## 8. Card-data validation when data is later changed

When a separate data or incremental-operation PR changes the canonical full or public projection, run all applicable data validators, including:

```bash
python validation_scripts/date_role_alignment_check.py CURRENT_FULL_JSON
python validation_scripts/story_id_lineage_check.py RUN_JSON CURRENT_FULL_JSON \
  --stage-a-results STAGE_A_RESULTS_JSON
python validation_scripts/related_lineage_check.py \
  CURRENT_FULL_JSON \
  --previous-baseline PREVIOUS_FULL_JSON
python validation_scripts/related_lifecycle_check.py \
  CURRENT_FULL_JSON \
  --require-contract
node scripts/validate_cards.mjs data/cards.full.json
node scripts/lean_cards.mjs --check
```

Use exact current command options supported by the validator version on the target branch.

## 9. Canonical data rule

```text
data/cards.full.json      canonical full inventory
public/data/cards.json    generated lean projection
```

Ordinary operations are:

```text
insert
update
related_add
```

Ordinary runs do not delete cards or remove existing related edges.

## 10. PR scope

Recommended title:

```text
docs: add dynamic governance and canonical full-to-lean contracts
```

The PR body should state:

- fixed-document governance is replaced by Stage 0.0D dynamic discovery;
- Stage 0.0C searches for missing news and follow-ups before Stage A;
- Stage 0.7C independently challenges completeness and news value;
- canonical full and lean projection roles are separated;
- the exporter and workflow are changed to enforce full-to-lean ownership;
- exporter regression tests protect malformed-public recovery and filesystem-path isolation;
- ordinary run operations are insert, update, and related_add;
- one-time migration facts are isolated under `docs/migrations/`;
- card data is unchanged.
