# Stage 0.1 Dynamic Source-Universe Addendum

**Status:** `ACTIVE_MANDATORY_ADDENDUM`  
**Applies to:** `01_PROMPT_0_1_Stage_A.md`

## 1. Preconditions

Stage A must not begin unless the current run includes:

- a passing Stage 0.0D document-universe artifact;
- a passing Stage 0.0C coverage-discovery artifact;
- the current canonical full SHA;
- an expanded Stage A input ledger accounting for the original input and every discovered candidate.

If any precondition is missing, stop with:

```text
BLOCKED_STAGE_A_EXPANDED_SOURCE_UNIVERSE_MISSING
```

## 2. Authoritative input universe

Stage A’s authoritative input is:

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

For every candidate that resembles an existing full card, Stage A must emit one preliminary classification:

- `exact_duplicate`;
- `non_material_repetition`;
- `existing_card_reinforcement`;
- `material_follow_up`;
- `stage_transition`;
- `correction_or_reversal`;
- `distinct_new_event`;
- `uncertain_needs_review`.

A candidate may not be rejected solely because the same actor or broad topic already exists in the full.

## 5. Required output additions

```json
{
  "stage_0_0d_manifest_ref": "",
  "stage_0_0c_discovery_ref": "",
  "expanded_source_universe_count": 0,
  "original_input_count": 0,
  "discovered_candidate_count": 0,
  "expanded_source_universe_accounted": true,
  "baseline_relation_classification_complete": true,
  "missing_stage_0_0c_items": [],
  "stage_b_authorized": false
}
```

Stage B may be recommended only for strict specs selected from this expanded universe.
