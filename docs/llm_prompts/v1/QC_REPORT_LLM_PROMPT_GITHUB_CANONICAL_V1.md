# LLM Prompt GitHub Canonical v1 — Integrity-Hardened QC

Updated KST: `2026-07-19T20:48:00+09:00`

| Item | Value |
|---|---:|
| status | PASS_PENDING_PR_REVIEW |
| total package files | 44 |
| governance docs | 9 |
| stage prompts | 14 |
| integrity override/registry/addenda | 8 |
| package/support docs | 10 |
| validation scripts | 3 |
| runtime code changes | 0 |
| cards.json changes | 0 |
| manifest-registration issues | 0 |

## Integrity components

Mandatory override:

- `00_DATE_STORYID_RELATED_INTEGRITY_OVERRIDE_V1.md`

Dedicated registry:

- `DATE_STORYID_RELATED_INTEGRITY_OVERRIDE_MANIFEST.json`

Registered validators:

- `validation_scripts/date_role_alignment_check.py`
- `validation_scripts/story_id_lineage_check.py`
- `validation_scripts/related_lineage_check.py`

## Validator behavior

`story_id_lineage_check.py` must not return a generic PASS when a cross-run story-ID collision is present.

- no collision: `PASS_NO_COLLISIONS`, exit `0`
- collision with complete Stage A quarantine evidence: `PASS_COLLISIONS_QUARANTINED`, exit `0`
- collision without complete quarantine evidence: `BLOCKED_STORY_ID_COLLISIONS_UNQUARANTINED`, exit `2`

The validator must be rerun with `--stage-a-results` after Stage A whenever collisions are detected.

## Story URL compatibility

The story-ID validator reads both raw-run and Stage A artifact shapes.

Accepted URL fields:

- `primary_url`
- `url`
- `source_urls[]`
- `urls[]`
- `fact_sources[].source_url`
- `fact_sources[].url`

Accepted Stage A containers include `decision_ledger[]`, strict/review pools, reinforcement, support-only, and rejected pools.

Canonical URL matching removes known tracking parameters and sorts all remaining query-parameter key/value pairs before lookup. Equivalent URLs therefore match even when their query parameters appear in a different order.

For grouped specs, equal-length `source_story_ids[]` and `source_urls[]` or `urls[]` arrays are paired by position. The validator does not assign every grouped URL to every story ID.

## Regression checks

| Case | Expected | Result |
|---|---|---|
| raw run, 353 stories, no quarantine artifact | 41 collisions blocked, exit 2 | PASS |
| same run + hardened Stage A artifact | 41 collisions quarantined, exit 0 | PASS |
| raw story identity supplied only in `urls[]` | trusted exact URL | PASS |
| Stage A decision ledger identity supplied only in `url` | trusted exact URL | PASS |
| grouped strict spec using `source_story_ids[] + urls[]` | positional exact-URL matching | PASS |
| equivalent query parameters in different order | same canonical URL | PASS |
| Python syntax compilation | no syntax error | PASS |

## Package consistency

The following documents all declare the same package scope:

- `LLM_PROMPT_GITHUB_CANONICAL_V1_MANIFEST.json`
- `UPLOAD_MANIFEST.json`
- `PROMPT_MANIFEST.md`
- `README_LLM_PROMPT_GITHUB_CANONICAL_V1.md`
- `UPLOAD_INSTRUCTIONS.md`
- this QC report

They require one override, six addenda, and three validators. No included package document instructs uploaders to omit `validation_scripts/`.

## Historical note

The earlier docs-only canonical-v1 QC excluded the PR #151 validator set. That historical exclusion is superseded for the three integrity validators registered by the current date/story-ID/related override.

## QC issues

```json
[]
```
