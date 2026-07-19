# LLM Prompt GitHub Canonical v1 — Integrity-Hardened QC

Updated KST: `2026-07-19`

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

## Story-ID validator behavior

`story_id_lineage_check.py` must not return a generic PASS when a cross-run story-ID collision is present.

- no collision: `PASS_NO_COLLISIONS`, exit `0`
- collision with complete Stage A quarantine evidence: `PASS_COLLISIONS_QUARANTINED`, exit `0`
- collision without complete quarantine evidence: `BLOCKED_STORY_ID_COLLISIONS_UNQUARANTINED`, exit `2`

The validator must be rerun with `--stage-a-results` after Stage A whenever collisions are detected.

## Story input and URL compatibility

The story-ID validator reads both canonical source-input shapes:

- top-level `stories[]`
- nested `final_news_llm_input.stories[]`

It also reads Stage A artifact containers including `decision_ledger[]`, strict/review pools, reinforcement, support-only, and rejected pools.

Accepted URL fields:

- `primary_url`
- `url`
- `source_urls[]`
- `urls[]`
- `fact_sources[].source_url`
- `fact_sources[].url`

Every discovered story ID is registered even when no URL exists. A reused baseline story ID with no independently matching URL therefore enters the block/quarantine flow rather than disappearing from the validator universe.

Canonical URL matching removes known tracking parameters and sorts all remaining query-parameter key/value pairs before lookup. Equivalent URLs therefore match even when their query parameters appear in a different order.

For grouped specs, equal-length `source_story_ids[]` and `source_urls[]` or `urls[]` arrays are paired by position. The validator does not assign every grouped URL to every story ID.

## Validation-scope separation

Package-integrity checks and card-data checks are separate gates.

### Required for this docs/validator package

- all three Python validators compile;
- all three manifests parse;
- every path listed by `UPLOAD_MANIFEST.json` exists;
- story-ID detection/quarantine behavior passes its run-specific contract;
- `git diff --quiet` proves `public/data/cards.json` is unchanged from the branch merge base.

The unchanged-card check is what authorizes the docs-only exception. If the card file changes, the exception is unavailable and data validators become blocking.

### Hard gate for card-data operations

`date_role_alignment_check.py` and `related_lineage_check.py` are hard gates when:

- `public/data/cards.json` changes;
- Prompt 0.8 merge preparation runs;
- Prompt 0.9 production verification runs;
- baseline remediation is performed.

This PR does not modify `public/data/cards.json`. The unchanged baseline currently reports five historical date-integrity findings. They are recorded for separate lineage-safe remediation and do not represent a syntax, manifest, or package-assembly failure in this docs-only PR. This exception does not permit new card-data errors and does not waive the hard gate for future card changes or production verification.

## Regression checks

| Case | Expected | Result |
|---|---|---|
| raw run, 353 stories, no quarantine artifact | 41 collisions blocked, exit 2 | PASS |
| same run + hardened Stage A artifact | 41 collisions quarantined, exit 0 | PASS |
| canonical nested `final_news_llm_input.stories[]` | stories enumerated; reused IDs evaluated | PASS |
| nested story ID with missing URL | untrusted collision blocked, exit 2 | PASS |
| raw story identity supplied only in `urls[]` | trusted exact URL | PASS |
| Stage A decision ledger identity supplied only in `url` | trusted exact URL | PASS |
| grouped strict spec using `source_story_ids[] + urls[]` | positional exact-URL matching | PASS |
| equivalent query parameters in different order | same canonical URL | PASS |
| docs-only cards diff check | unchanged card file required | PASS |
| unchanged baseline date audit | five historical findings recorded for remediation | PASS_WITH_RECORDED_FINDINGS |
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
