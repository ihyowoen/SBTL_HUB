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

## Handoff when the locked downstream Prompt 0.6 is V5+

Preserve the complete source-bearing `fact_sources` and `source_discovery_ledger`
records. Source presence, permission to support a visible field, and usable
verified quote text are different properties. A paraphrase-only or context-only
source may be preserved but cannot by itself ground a V5 numeric/status claim.
Do not drop it merely because a downstream quote gate cannot use it.

Supply actual literal excerpts and their real verification/fetch metadata for
sources used as V5 grounding, with the existing explicit field-support limits.
Reuse an already verified excerpt and its traceable record when valid; a new
fetch is not required merely to advance a stage. Do not manufacture `fetched=true`,
change `body_level_evidence_verified` into a verified-quote status by name alone,
or put editor-authored claims into an excerpt field to make a run pass.

A declaration at 0.5 supersedes older declarations for the same source identity;
copying only its ID without the required quote does not permit stale-quote
fallback. Complete or correct the owning upstream record before using it for a
new/changed 0.6 claim. Preserve negative/excluded records and their aliases too.

This handoff note describes the V5 consumer boundary, not a retroactive change
to locked historical V4 runs or a claim that a new production V5 run has executed.
When the locked downstream Prompt 0.6 is V5+, a passing 0.5 visible `fact` must now
carry `fact_sources` plus `claim_source_coverage.visible_fact` that resolves each
grounding reference to exactly one explicitly fact-authorized source record. Each
grounding record must carry a literal verified excerpt, an approved quote status,
and `fetched=true`. Context/paraphrase-only records remain preservable but cannot
satisfy that grounding handoff. The machine checker validates this boundary; it
does not treat an earlier PASS or editor-authored claim text as evidence.

### Retained-fact reuse into 0.6

Keep the verified literal quote and its source identity/field-support metadata for
retained visible claims, as well as for new facts. A downstream `field_evidence_refs`
map can reuse those preserved quotes without a new network fetch and without
requiring each source to support unrelated fields. It does not exempt retained
facts from grounding or grant new field rights. If a changed field also contains
retained numbers, keep their supporting references in that field's assignment.
An earlier PASS without a usable quote is insufficient. This handoff instruction
does not itself implement a new claim-level attestation ledger at 0.5.
