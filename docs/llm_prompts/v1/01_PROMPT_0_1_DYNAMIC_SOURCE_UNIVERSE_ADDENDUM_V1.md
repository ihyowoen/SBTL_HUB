# Stage 0.1 Dynamic Source-Universe Addendum

**Status:** `ACTIVE_MANDATORY_ADDENDUM`  
**Applies to:** `01_PROMPT_0_1_Stage_A.md`

## 0. Supersession scope

This addendum supersedes every Stage A clause that permits any of the following to act as an independent baseline:

- `public/data/cards.json`;
- a user-uploaded baseline;
- a local final candidate;
- a branch-only, prior-run, helper, or remembered inventory.

Such a file may be used only as a transport copy after it is proved byte-equivalent to the current GitHub `main` content identified by the recorded `data/cards.full.json` Git blob SHA. It never becomes a separate source of authority.

## 1. Preconditions

Stage A must not begin unless the current run includes:

- a passing Stage 0.0D document-universe artifact;
- a passing Stage 0.0C coverage-discovery artifact;
- the current GitHub `main` commit SHA;
- the current `data/cards.full.json` Git blob SHA;
- the complete current `data/cards.full.json` content read and parsed from that locked main state;
- an expanded Stage A input ledger accounting for the original input and every discovered candidate.

If the canonical full cannot be read, parsed, counted, or matched to its recorded Git blob SHA, stop with:

```text
BLOCKED_CANONICAL_FULL_UNREADABLE
```

If the repository head or canonical full blob moved after the Stage 0.0D lock, or a supplied snapshot is not byte-equivalent to the locked canonical full, stop with:

```text
BLOCKED_BASELINE_MOVED_REBASE_REQUIRED
```

If the expanded source-universe artifact or ledger is missing, stop with:

```text
BLOCKED_STAGE_A_EXPANDED_SOURCE_UNIVERSE_MISSING
```

## 2. Authoritative baseline and input universe

Stage A’s sole duplicate, reinforcement, correction, follow-up, stage-transition, and related-lineage baseline is:

```text
GitHub main → data/cards.full.json
```

The baseline is the verified canonical full content, not merely its filename or SHA declaration.

`public/data/cards.json` is a generated lean application projection and must not be used for Stage A screening because it omits full-only evidence, lineage, workflow, and audit metadata.

A user-uploaded or local copy may be used for processing convenience only when the Stage 0.0D artifact records:

- the locked main commit SHA;
- the canonical full Git blob SHA;
- the copy’s computed content identity;
- `canonical_full_snapshot_equivalent=true`;
- the method used to prove byte equivalence.

Stage A’s authoritative candidate universe is:

```text
original source input
+ Stage 0.0C discovered missing candidates
+ baseline follow-up candidates
+ existing-card reinforcement candidates
+ correction or reversal candidates
+ explicitly carried review-pool and rescue candidates
```

The original input file alone is not the complete candidate universe.

Stage A must preserve the Stage 0.0C item IDs and terminal discovery ledger. No item may disappear silently.

## 3. Stage A boundary remains unchanged

This addendum does not authorize Stage A to:

- perform external web search;
- fetch article bodies;
- create `fact_sources` or `source_quote`;
- draft cards;
- decide evidence completeness or publish readiness.

All discovery search is performed in Stage 0.0C. Stage A remains selector-only.

## 4. Required relationship classification

For every candidate that resembles an existing canonical full card, Stage A must emit one preliminary classification:

- `exact_duplicate`;
- `non_material_repetition`;
- `existing_card_reinforcement`;
- `material_follow_up`;
- `stage_transition`;
- `correction_or_reversal`;
- `distinct_new_event`;
- `uncertain_needs_review`.

A candidate may not be rejected solely because the same actor or broad topic already exists in the full.

All relationship classifications must be computed against the verified current canonical full, including its existing `related`, `related_lineage`, evidence, and workflow metadata where applicable.

## 5. Required output additions

```json
{
  "stage_0_0d_manifest_ref": "",
  "stage_0_0c_discovery_ref": "",
  "canonical_main_commit_sha": "",
  "canonical_full_blob_sha": "",
  "canonical_full_read_status": "READ_COMPLETE",
  "canonical_full_card_count": 0,
  "baseline_content_source": "GITHUB_MAIN_CANONICAL_FULL|VERIFIED_BYTE_EQUIVALENT_COPY",
  "canonical_full_snapshot_equivalent": true,
  "canonical_full_snapshot_equivalence_method": "",
  "expanded_source_universe_count": 0,
  "original_input_count": 0,
  "discovered_candidate_count": 0,
  "expanded_source_universe_accounted": true,
  "baseline_relation_classification_complete": true,
  "missing_stage_0_0c_items": [],
  "stage_b_authorized": false
}
```

Stage B may be recommended only when:

- the canonical full baseline verification passes;
- the expanded universe is fully accounted;
- strict specs are selected from that expanded universe.
