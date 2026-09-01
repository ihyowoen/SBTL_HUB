# Prompt 0.5 — Evidence & Source-Claim Completeness V4

**Status:** `ACTIVE_CANONICAL`  
**Version:** `PROMPT_0_5_V4_20260901`

Use only 0.4 addable candidates. Recompute source audit from current `fact_sources`. Verify durable endpoints, owner independence, official-source search, discovery ledger, quotes, all visible claims/numbers/dates/entities, source synthesis, and bounded single-source exceptions.

Recheck selected route evidence and Related/date freshness. When stronger/earlier evidence changes event identity or shows prior canonical coverage, return upstream as duplicate/reinforcement/update rather than allowing strong evidence to launder a selection defect.

## Required passing output bucket

A candidate that passes both evidence completeness and source-claim coverage must be emitted under the exact combined bucket:

`evidence_complete_and_source_claim_covered[]`

Each item in that bucket must preserve:

- `source_spec_id`;
- `source_diversity_status`;
- `source_discovery_ledger`;
- `related_lineage`;
- `date_role`;
- claim/source coverage and source-audit metadata required by the active Source Audit contract;
- unresolved downstream issues, if any;
- prompt provenance.

Do not represent a passed item only in separate `evidence_complete[]` and `source_claim_covered[]` arrays. Those names may be used as internal booleans/states, but the stage artifact consumed by the active checker must contain the exact combined passing bucket above so the validator cannot report PASS with `item_count: 0`.

If a candidate does not satisfy both states, do not place it in the combined bucket. Instead augment, narrow, revise, hold, or route upstream with explicit reason.

Prompt 0.5 must run the active stage-artifact contract against its final artifact before recommending 0.6. Preserve the integrated selection package, date role, lineage, source-claim map, source-audit result, freshness/Related backstop, and prompt provenance.