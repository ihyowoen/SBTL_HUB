# Dynamic Governance and Editorial Completeness Override

**Override ID:** `DYNAMIC_GOVERNANCE_COMPLETENESS_V1`  
**Status:** `ACTIVE_MANDATORY_ADDENDUM`

## 0. Scope

This override supersedes earlier conflicting language only in the following areas:

1. any fixed list presented as the complete document universe;
2. any rule allowing a run to start after reading only a remembered core set;
3. any rule treating the supplied final input as the complete news universe;
4. any workflow that omits Stage 0.0D, Stage 0.0C, or Stage 0.7C;
5. any baseline rule treating `public/data/cards.json` as the canonical full inventory;
6. every Prompt 0.8 clause treating `public/data/cards.json` as the current baseline, merge source of truth, canonical count source, fallback baseline, sole merge target, or authoritative replacement file;
7. any ordinary-run process that permits silent card deletion or related-edge removal;
8. any permanent rule that embeds one-time migration dates, counts, or run names.

All other compatible fact, evidence, schema, stage, source-diversity, related-lineage, and production rules remain in force.

## 1. Mandatory governance entry point

Every run must begin with:

- `docs/RUN_GOVERNANCE_INDEX.md`;
- `docs/DOCUMENT_UNIVERSE_POLICY.md`;
- `docs/llm_prompts/v1/00D_PROMPT_0_0D_DOCUMENT_UNIVERSE_PREFLIGHT.md`.

Stage 0.0D must read or parse every file under `docs/**`, then classify and apply the complete active rule universe from the current GitHub `main`.

A fixed list of core documents is a minimum seed only. It is not proof that all applicable rules were read.

## 2. Expanded source-universe rule

The supplied input is not the complete editorial universe.

After Stage 0.0D, Stage 0.0C must review the canonical full, input stories, trackers, review pools, watchlists, open rescue candidates, regional and topic coverage, material follow-ups, corrections, reversals, and missing must-report events.

Stage A remains selector-only and uses the Stage 0.0C expanded source universe as its authoritative input.

Stage A does not perform the external search itself.

### 2.1 Fact-discipline boundary

Stage 0.0C discovery is not evidence creation and does not weaken `FACT_DISCIPLINE.md`.

A web search result discovered in Stage 0.0C is only a candidate lead. It must still:

1. enter the explicit expanded source-universe ledger;
2. pass Stage A selection;
3. pass Stage B body-level or official-material evidence collection;
4. pass Stage C fact-safe validation;
5. pass every applicable post-acceptance gate.

Any earlier rule that prohibits web search from silently creating a new card or unsupported claim remains fully effective.

For clarity:

- Stage 0.0C may discover a new candidate lead;
- Stage 0.0C may not create a final claim, `fact_sources`, accepted card, or publish state;
- Stage B and later may not use the Stage 0.0C search result as evidence without direct inspection and claim mapping;
- no discovered candidate may bypass Stage A/B/C.

This is a workflow-scope clarification, not an exception to factual accuracy or evidence requirements.

## 3. Independent completeness rule

Prompt 0.8 is blocked until Stage 0.7C independently reviews:

- source-universe completeness;
- regional and topic coverage;
- existing-card reinforcement and correction;
- material follow-ups and execution stages;
- proposed inserts, updates, and related additions;
- material exclusions, holds, and residual risk.

A self-authored statement that the batch is “complete” or “IB-grade” is not sufficient.

## 4. Canonical data rule

The canonical baseline and merge source of truth are:

```text
GitHub main → data/cards.full.json
```

The canonical merge output is also:

```text
data/cards.full.json
```

The application file is:

```text
public/data/cards.json
```

and must be regenerated as a lean projection of the updated canonical full.

`public/data/cards.json` must never be used as a substitute merge baseline, canonical count source, fallback source of truth, or full-metadata preservation source.

If the canonical full cannot be read and verified, Prompt 0.8 must block rather than fall back to the public projection.

Every run must record the current main commit SHA and canonical full blob SHA.

## 5. Incremental operation rule

Ordinary runs use declared operations:

- `insert`;
- `update`;
- `related_add`.

Existing related edges are preserved.

Card deletion and `related_remove` are not ordinary run operations. They require a separate remediation process with item-specific evidence and explicit approval.

## 6. Migration isolation

One-time transition or recovery details belong only under `docs/migrations/`.

A migration applies only when explicitly activated in the run intake and must become `COMPLETED_REFERENCE` after completion.

`COMPLETED_REFERENCE` is non-operative in ordinary runs and remains available only for audit and conflict detection.

Permanent governance documents must remain date-independent and run-independent.

## 7. Mandatory workflow order

```text
0.0D → 0.0C → 0.0 → 0.1 → 0.2 → 0.3
→ authorized revise loops
→ 0.4 → 0.5 → 0.6 → 0.7 → 0.7C → 0.8 → 0.9
→ 1.0 when needed → 1.1
```

## 8. Required blockers

Use the applicable blocker when:

- `BLOCKED_DOCUMENT_UNIVERSE_INCOMPLETE`;
- `BLOCKED_DOCUMENT_AUTHORITY_CONFLICT`;
- `BLOCKED_COVERAGE_DISCOVERY_INCOMPLETE`;
- `BLOCKED_STAGE_A_EXPANDED_SOURCE_UNIVERSE_MISSING`;
- `BLOCKED_EDITORIAL_COMPLETENESS_UNPROVEN`;
- `BLOCKED_INCREMENTAL_MERGE_PRECONDITION_MISSING`;
- `BLOCKED_CANONICAL_FULL_UNREADABLE`;
- `BLOCKED_PROMPT_0_8_PUBLIC_BASELINE_CONFLICT`;
- `BLOCKED_BASELINE_MOVED_REBASE_REQUIRED`;
- `BLOCKED_UNDECLARED_CARD_DIFF`;
- `BLOCKED_EXISTING_RELATED_EDGE_LOSS`;
- `BLOCKED_RETROSPECTIVE_RULE_PROMOTION_INCOMPLETE`.

No downstream stage may waive these blockers through prose or memory.
