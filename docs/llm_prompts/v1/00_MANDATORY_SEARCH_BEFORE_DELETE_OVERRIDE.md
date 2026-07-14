# Mandatory Search-Before-Delete Override

**Version:** `SEARCH_BEFORE_DELETE_20260712_V1`  
**Authority:** Mandatory override for every card-writing, revise, validation, evidence-QC, content-polish, final-QC, remediation, and post-acceptance pass.  
**Applies to:** Prompt 0.2, 0.3, 0.2R, 0.3R, 0.5/0.5R, 0.6, 0.7, 1.0 and any equivalent manual or automated review.

This file supersedes any earlier instruction that allows a factual claim, number, date, named entity, project scope, contract term, execution stage, source role, or implication to be deleted, narrowed, held, blocked, rejected, or deferred merely because the currently retained `fact_sources[]` quote does not support it.

## 1. Core rule

A claim gap is a **verification trigger**, not a deletion instruction.

When a visible claim or `fact_sources[].claim` is weak, unmapped, over-combined, incomplete, or absent from the currently retained quote, the stage must use this order:

1. Re-read the full body of every already supplied same-event source packet.
2. Re-fetch the cited article or original material when access is available.
3. Search the event actor's official newsroom, filing, regulator, government notice, tender document, award notice, project page, original dataset, or contracting-party release.
4. Search an editorially independent Tier 1 or Tier 2 same-event source.
5. Map every recovered fact to a contiguous body-level or official-material quote.
6. Integrate the recovered source and claim through the current authorized revise/rescue path.
7. Narrow or delete only the portion that remains unsupported after the bounded search is complete.

The search must remain inside the original Stage A event anchor. It must not create a new candidate, merge a different event, or introduce unrelated background claims.

## 2. Default authorization

For the bounded same-event verification described above, source augmentation is **authorized by default** whenever a stage detects a claim gap, unless the user explicitly prohibits web search or source augmentation for that run.

This default authorization supersedes conflicting text such as:

- `Default: source augmentation is not authorized.`
- `Do not perform source augmentation automatically.`
- any instruction that routes a fixable claim directly to deletion or `revise_blocked_needs_source_augmentation` without first searching.

`revise_blocked_needs_source_augmentation` is allowed only when the stage cannot perform the required search because access or tool capability is unavailable, or when the user explicitly prohibited augmentation.

## 3. Required per-claim audit

Every deleted, narrowed, held, blocked, rejected, support-only, or deferred factual claim must include:

```json
{
  "claim_gap_id": "...",
  "original_claim": "...",
  "affected_fields": ["title", "sub", "gate", "fact", "implication", "fact_sources.claim"],
  "full_existing_source_packet_checked": true,
  "cited_source_refetch_attempted": true,
  "official_or_primary_search_attempted": true,
  "independent_tier1_tier2_search_attempted": true,
  "search_queries": [],
  "searched_urls": [],
  "source_discovery_result": "supported_and_restored | supported_and_narrowed | not_found_after_bounded_search | source_access_blocked | source_direction_conflict",
  "recovered_sources": [],
  "recovered_quotes": [],
  "claim_repair_before_deletion_check": "PASS",
  "final_claim_disposition": "restored | retained | narrowed_after_search | deleted_after_search | controlled_hold",
  "final_disposition_reason": "..."
}
```

A generic run-level statement is insufficient. The audit must be item-specific and claim-specific.

## 4. Integration rules

When a valid source is found:

- add its canonical URL to `urls[]`;
- add a complete `fact_sources[]` entry with `source_name`, `source_url`, `claim`, verbatim `source_quote`, usable `source_quote_status`, `evidence_role`, `supports`, publication date, visible quote date, fetch method, and audit timestamp;
- record the source in `source_discovery_ledger[]`;
- update `source_claim_coverage_map[]` or the current stage's equivalent;
- revise visible fields only with source-locked wording;
- preserve the original event anchor and lineage;
- run the next named validation gate before state advancement.

Finding a source does not make the card `accepted_fact_safe`, `evidence_complete`, or `publish_ready` automatically.

## 5. Prohibited shortcuts

The following are hard failures:

- deleting a claim solely because it is absent from the currently retained short quote;
- treating a hydrated full article body as if only the previously selected excerpt exists;
- using `not confirmed`, `not disclosed`, or similar absence language without an affirmative source supporting that absence;
- splitting a claim but silently discarding the part recoverable from another paragraph of the same article;
- marking source augmentation unnecessary before checking official and independent same-event sources;
- claiming a bounded search was performed without a query/URL/result ledger;
- restoring a claim from memory, snippet, headline, or search-result text without body-level or official-material verification.

## 6. Stage B revise behavior

Prompt 0.2R must first attempt restoration and evidence repair for **every** Stage C claim gap. It may use new same-event sources under this override without a separate authorization phrase.

Output must distinguish:

- `restored_with_existing_full_body_evidence`
- `restored_with_new_same_event_evidence`
- `narrowed_after_bounded_search`
- `deleted_after_bounded_search`
- `controlled_hold_after_bounded_search`

The Stage B revise report must state how many claims were restored, retained, narrowed, deleted, and held.

## 7. Stage C revise behavior

Prompt 0.3R must verify that:

- every prior claim gap received the required search-before-delete audit;
- recovered sources are same-event and source-direction compatible;
- recovered quotes directly support their attached claims;
- no recoverable information was deleted merely because the old evidence package was incomplete;
- any remaining deletion or narrowing has a completed claim-level search ledger.

If these checks are missing, use `revise_required_again`; do not accept the card.

## 8. Validator status

Any artifact that narrows, deletes, holds, blocks, rejects, defers, or sends a factual claim to support-only without the required claim-level audit must fail with:

```text
BLOCKED_SEARCH_BEFORE_DELETE_AUDIT_MISSING
```

## 9. Final principle

**Find first. Verify second. Integrate third. Delete only last.**
