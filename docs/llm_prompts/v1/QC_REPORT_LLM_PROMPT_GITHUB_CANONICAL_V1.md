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

It also reads every Stage A terminal or lineage container used by the current contract:

- `decision_ledger[]`
- `strict_passed_spec[]`
- `candidate_review_pool[]`
- `watchlist_context_pool[]`
- `existing_reinforcement[]`
- `support_source_only[]`
- `rejected[]`
- `reject_or_support_only_pool[]`

Accepted URL fields:

- `primary_url`
- `url`
- `source_urls[]`
- `urls[]`
- `fact_sources[].source_url`
- `fact_sources[].url`

Every discovered story ID is registered even when no URL exists. A reused baseline story ID with no independently matching URL therefore enters the block/quarantine flow rather than disappearing from the validator universe.

Canonical URL matching removes known tracking parameters and sorts all remaining query-parameter key/value pairs before lookup. Equivalent URLs therefore match even when their query parameters appear in a different order.

A representative `story_id` does not terminate grouped processing. Every member of `source_story_ids[]` remains in the validator universe. Equal-length `source_story_ids[]` and `source_urls[]` or `urls[]` arrays are paired by position. When no safe one-to-one mapping exists, only an explicitly named representative story may receive the representative URL; every other story ID remains URL-unmapped.

## Per-record and per-baseline-card identity

The validator no longer unions all URLs under one `story_id` before identity classification.

- every run record is evaluated independently;
- every baseline card sharing that story ID is evaluated independently;
- one exact record cannot trust another missing or mismatched record;
- a match to one baseline card cannot trust another baseline card that reuses the same story ID without its own matching URL;
- a partially matched record remains a collision and reports both trusted and unmatched baseline-card IDs.

For Stage A compatibility, `collision_count` remains the number of unique collision story IDs. The validator additionally reports:

- `collision_record_count`
- `collision_pair_count`
- `trusted_record_count`
- `trusted_pair_count`
- `partial_identity_match_record_count`

Quarantine verification accepts the Stage A count from any of these compatible locations:

- `story_id_lineage_audit.collision_count`
- `story_id_lineage_audit.story_id_collision_count`
- top-level `story_id_collision_count`
- `summary.story_id_collision_count`

This preserves existing hardened artifacts while honoring the canonical Stage A addendum field `story_id_collision_count`.

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
| raw run, 353 stories, no quarantine artifact | 41 collision story IDs blocked, exit 2 | PASS |
| same run + hardened Stage A artifact | 41 collision story IDs quarantined, exit 0 | PASS |
| Stage A artifact with only `summary.story_id_collision_count` | quarantine count accepted, exit 0 | PASS |
| existing run baseline-card pair expansion | 48 unmatched record/card pairs retained | PASS |
| canonical nested `final_news_llm_input.stories[]` | stories enumerated; reused IDs evaluated | PASS |
| nested story ID with missing URL | untrusted collision blocked, exit 2 | PASS |
| `reject_or_support_only_pool[]` only | reused ID registered and blocked | PASS |
| grouped item with representative `story_id` plus `source_story_ids[]` | every grouped ID evaluated | PASS |
| same story ID in exact and mismatched run records | mismatched record remains collision | PASS |
| same story ID on two baseline cards, only one URL match | unmatched baseline-card pair remains collision | PASS |
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
