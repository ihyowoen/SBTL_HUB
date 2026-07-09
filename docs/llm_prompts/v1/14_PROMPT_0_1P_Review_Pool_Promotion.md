<!-- REPLACE_ALL_CLEAN_VERSION: LLM_PROMPT_GITHUB_CANONICAL_V1_SOURCE_DIVERSITY_IB_CODEX -->
<!-- Generated KST: 2026-07-08T21:33:49.790191+09:00 -->
<!-- This file is a full clean replacement file. It is not a patch stub. -->

# Prompt 0.1P — Authorized Review Pool / Treasure Promotion

## Purpose

This is an optional, user-authorized pass that runs after a valid Stage A output
and before Stage B.

It exists to review selected `candidate_review_pool[]`,
`treasure_candidate_review_pool[]`, or explicitly named review-pool items without
mixing them into the normal Stage B queue.

This prompt must not be used to rescue items silently. The current run may
continue through Stage B on the existing `strict_passed_spec[]` while this pass
produces a separate promotion artifact.

## Required Inputs

1. A schema-valid Stage A output from the same run.
2. The exact input universe for this pass:
   - `candidate_review_pool[]` only, or
   - `treasure_candidate_review_pool[]` only, or
   - a named list of `story_id` / `grouped_story_ids`.
3. Current baseline cards file or an explicit baseline declaration.
4. User authorization text naming this as a review-pool / treasure promotion
   pass.

If the input universe is not explicit, stop with:

```text
BLOCKED_PROMOTION_UNIVERSE_NOT_EXPLICIT
```

## Hard Boundaries

- Do not process Stage A `strict_passed_spec[]`; those belong to Stage B.
- Do not process the whole Stage A universe unless the user explicitly named it.
- Do not promote because an item is interesting, high-scoring, TREASURE_A, or in
  `newsletter_expanded`.
- Do not use `primary_url` as evidence by itself.
- Do not write cards.
- Do not mark items accepted, evidence_complete, source_claim_covered,
  content_enriched, publish_ready, addable, PR-ready, or GitHub-ready.
- Do not erase non-promoted items; every reviewed item must remain visible in the
  promotion ledger.

## Review Standard

For each reviewed item, perform bounded same-event source discovery before any
promotion decision.

Required source discovery:

1. Inspect the provided source candidate.
2. Search for source-owner / official confirmation where plausible.
3. Search for at least one independent corroborating source where plausible.
4. Check current baseline for exact URL duplicate and same-event duplicate.
5. Check whether the event is fresh enough or has a fresh hook.
6. Decide whether the item can satisfy the same six Stage A strict-pass
   conditions as an ordinary strict candidate.

Single-source promotion is exception-only and requires:

```json
{
  "single_source_exception": true,
  "single_source_exception_reason": "...",
  "source_owner_or_primary_source": true,
  "why_second_source_not_reasonably_available": "..."
}
```

## Promotion Gate

Promotion requires a fresh strict-pass gate object. A promoted item must satisfy:

1. Direct SBTL lane relevance.
2. Concrete execution / policy / funding / capacity / order / facility /
   regulatory / market-data anchor.
3. Fresh event date or fresh implementation hook.
4. No unresolved same-event baseline duplicate.
5. Evidence path sufficient for Stage B source package construction.
6. No unresolved source-quality, date, metric, or scope defect that would make
   the draft misleading.

If any condition fails, do not promote. Route the item to one of:

- `not_cardable_after_review`
- `support_source_only_after_review`
- `watchlist_only_after_review`
- `duplicate_or_reinforcement_after_review`
- `needs_user_decision_after_review`

## Output Schema

Return one JSON object with:

```json
{
  "stage": "0.1P_review_pool_promotion",
  "run_tag": "",
  "stage_prompt_file": "14_PROMPT_0_1P_Review_Pool_Promotion.md",
  "stage_prompt_sha256": "",
  "user_authorized": true,
  "input_universe_description": "",
  "input_item_count": 0,
  "baseline_file": "",
  "source_discovery_attestation": "bounded_same_event_source_discovery_performed",
  "promoted_strict_passed_spec": [],
  "rescue_candidate_strict_spec": [],
  "not_promoted": [],
  "review_pool_resolution_ledger": [],
  "promotion_summary": {
    "reviewed_count": 0,
    "promoted_count": 0,
    "not_promoted_count": 0,
    "needs_user_decision_count": 0,
    "single_source_exception_count": 0
  },
  "next_call_recommendation": ""
}
```

Each `promoted_strict_passed_spec[]` item must include:

```json
{
  "story_id": "",
  "provisional_spec_id": "",
  "promotion_source_pool": "",
  "promotion_user_authorized": true,
  "promotion_review_artifact_id": "",
  "promotion_reason": "",
  "strict_pass_gate": {
    "lane_relevance": "pass",
    "execution_anchor": "pass",
    "freshness": "pass",
    "baseline_duplicate": "pass",
    "evidence_path": "pass",
    "scope_quality": "pass"
  },
  "staleness_decision": "",
  "source_discovery_ledger": [],
  "baseline_duplicate_check": {},
  "stage_b_ready": true,
  "stage_b_instruction": "send only promoted strict specs to Prompt 0.2"
}
```

Each `not_promoted[]` item must include:

```json
{
  "story_id": "",
  "original_review_pool_partition": "",
  "final_review_pool_disposition": "",
  "disposition_basis": "",
  "blocking_question": "",
  "next_action_condition": "",
  "carry_forward_policy": ""
}
```

Every reviewed item must also appear in `review_pool_resolution_ledger[]` with:

```json
{
  "story_id": "",
  "upstream_status": "",
  "original_review_pool_partition": "",
  "final_review_pool_disposition": "",
  "disposition_basis": "",
  "reviewed_by_stage_or_pass": "0.1P_review_pool_promotion",
  "review_artifact_id": "",
  "carry_forward_policy": "",
  "next_action_condition": ""
}
```

## Next Call Rule

If `promoted_count > 0`, the next call may be Stage B Prompt 0.2 on
`promoted_strict_passed_spec[]` only.

If `promoted_count = 0`, do not call Stage B for this promotion pass.

The existing main run is unaffected unless the user explicitly decides to integrate
promoted specs to a later Stage B batch.

# 14_PROMPT_0_1P_Review_Pool_Promotion.md — Source Diversity source-diversity integrated rule

    This integrated rule is authoritative for source-diversity, source-preservation, synthesis,
    visible-source-date and same-source grouping rules. Earlier language that conflicts with this
    integrated rule is superseded only to the extent of that conflict.

    ## Source Diversity source-diversity — common definitions

### 1. Diversity unit

Source diversity is measured by **canonical source identity and editorial independence**, not by
`fact_sources[]` row count.

The following count as one source:

- multiple claims or quotes from the same canonical article URL;
- print/mobile/AMP/RSS mirrors of the same article;
- the same press release copied by multiple syndication sites without independent reporting;
- multiple pages controlled by the same editorial owner that merely repeat the same source text;
- one article split into several `fact_sources[]` entries.

Required calculations:

```text
source_evidence_entry_count = count(fact_sources[])
source_unique_url_count = count(unique canonical article URLs)
source_unique_domain_count = count(unique canonical domains after ownership/syndication review)
source_independent_owner_count = count(editorially independent source owners)
```

`PASS_MULTI_SOURCE` or any equivalent status is prohibited when
`source_independent_owner_count < 2`.

### 2. Preferred evidence-role structure

For each independently cardable event, target three complementary roles:

1. `primary_event_evidence`
   - official notice, regulator, filing, contracting party, project owner, research institution,
     original dataset or source owner;
2. `independent_event_confirmation`
   - independent news agency, financial press, trade press or local reporting that confirms the
     event and identifies omissions, conditions or execution status;
3. `policy_market_context`
   - policy, market, operational, comparable-project or system-impact evidence that materially
     improves `gate` or `implication`.

Two independent source owners are the minimum default. Three complementary roles are preferred.
A source does not satisfy diversity merely by existing; it must make a distinct contribution.

### 3. Source contribution requirement

Every retained source must record:

```json
{
  "source_role": "",
  "source_contribution": "",
  "source_origin_type": "",
  "source_published_date": "YYYY-MM-DD",
  "visible_quote_date": "YYYY-MM-DD"
}
```

`source_contribution` must explain the unique information supplied by that source. Generic values
such as `corroboration`, `additional source`, `supports card`, or `same event` are insufficient.

### 4. Visible-field synthesis requirement

When an additional source supplies material information, at least one of the following visible
fields must be revised using source-locked wording:

- `fact`
- `gate`
- `implication`

The output must record:

```json
{
  "source_synthesis_applied": true,
  "source_synthesis_fields": ["fact", "gate", "implication"],
  "source_synthesis_audit": [
    {
      "source_domain": "",
      "source_role": "",
      "unique_contribution": "",
      "affected_visible_fields": []
    }
  ]
}
```

A card that merely integrates URLs while its visible content still reflects only one article has not
passed source-diversity synthesis.

### 5. Publication date and audit timestamps

The date shown beside a quote must be the article or official-material publication date:

```text
visible date = source_published_date
```

`fetched_at` and `checked_at` are audit timestamps only. They must be preserved but must never be
used as the visible news date.

### 6. Rescue-before-delete rule

A weak, blocked or duplicate source must not be silently discarded when it contains unique useful
information.

Use this order:

1. refetch or locate the source owner/original material;
2. find an independent same-event source;
3. narrow unsupported wording;
4. move unique information into an existing card as reinforcement;
5. place unresolved items in `needs_source_augmentation` or a controlled remediation queue;
6. use hard rejection only when the item is false, irrelevant, irreparable, promotional noise or
   lacks any defensible decision value.

Duplicate-event articles are not separate cards, but their unique facts and quotes must follow the
representative event as support-source candidates.

### 7. Single-source exception

A single-source exception is narrow and rare. It may pass only when all conditions are true:

- the source is official, regulatory, a filing, original dataset, court decision, contracting-party
  release, or original research institution;
- bounded discovery was performed and no independent body-level source was available;
- the card contains only claims supported by that source;
- no broad causal, comparative, first/largest, market-impact or strategic implication is asserted
  unless the source explicitly supports it;
- the exception reason, search ledger and scope limitation are recorded;
- downstream Evidence QC and Final QC separately approve the exception.

A media article alone does not qualify merely because it is detailed.

## Review-pool promotion — source-diversity path requirement

Promotion requires a fresh source-cluster and diversity-path review.

Each promoted spec must include:

```json
{
  "same_event_source_cluster": [],
  "support_source_candidates": [],
  "source_domain_candidates": [],
  "source_diversity_path": {
    "status": "viable",
    "probable_independent_owner_count": 0,
    "official_or_source_owner_candidate_present": false,
    "independent_confirmation_candidate_present": false
  }
}
```

A strategically valuable item with an uncertain but plausible source path belongs in a controlled
source-augmentation queue, not silent rejection. Promotion itself does not prove source diversity;
Stage B must still perform bounded discovery and synthesis.

    Stop after review-pool promotion.

# Source Diversity / IB-grade + Codex Hardening Integrated rule

Version: `GITHUB_CANONICAL_V1_SOURCE_DIVERSITY_IB_CODEX`  
Generated KST: `2026-07-08T21:18:40.089502+09:00`

This integrated section supersedes earlier conflicting language only to the extent of conflict.  
It does **not** weaken Source Diversity source-diversity. It adds downstream hardening learned from PR #148 and the 20260706_130022 run.

## 1. IB-grade editorial upgrade rule

Cards should not be treated as publishable merely because they are fact-safe.

Before `publish_ready=true`, the pipeline must classify each card into one of the following:

| Tier | Meaning | Publish rule |
|---|---|---|
| `A` / `A-` | IB-grade or near-IB anchor | May be used as lead/anchor signal |
| `B+` | publishable supporting signal | May publish, but must not be described as top-tier anchor |
| below `B+` | insufficient | Must remain deferred, remediation, or support-only |

A `B+` card may be upgraded only through supported visible-field refinement:

- stronger strategic framing;
- clearer `sub`;
- sharper `gate`;
- implication rewritten toward market / policy / supply-chain decision use;
- no unsupported new numbers, contracts, capacity, pricing, or customer claims.

Never upgrade a weak source into a strong source by language alone.

## 2. Visible-field upgrade boundary

When improving title, sub, fact, gate, or implication:

- preserve all source boundaries;
- do not add a new factual claim unless it is directly supported by an existing `fact_sources[]` quote or an added source;
- do not convert `prequalified` into `awarded`;
- do not convert `pilot` into commercial performance;
- do not convert product showcase into customer order, certification, delivery, or revenue;
- do not convert policy award/achievement material into implementing notice unless the notice text is present;
- do not convert “focus / plan / report says” into confirmed CAPEX, customer, chemistry, or production start.

## 3. Single-source publish-ready waiver rule

If a card has:

```text
publish_ready = true
source_independent_owner_count = 1
```

then it must satisfy one of the following:

1. official / regulator / company primary source;
2. reputable market data provider with bounded data claim;
3. reputable trade or mainstream media with body-level evidence and bounded claims;
4. explicit user-provided official body text.

A valid waiver must include:

```json
"single_source_exception": {
  "allowed": true,
  "type": "...",
  "reason": "...",
  "mitigation": "..."
}
```

Invalid patterns:

```json
"single_source_exception": {
  "allowed": false,
  "reason": "two or more source owners..."
}
```

on a publish-ready single-source card is a blocker.

Required blocker:

```text
status = BLOCKED_PUBLISH_READY_SINGLE_SOURCE_WITHOUT_VALID_WAIVER
```

## 4. Stale publish blocker removal rule

No card may be both publish-ready and actively blocked.

Invalid:

```json
{
  "publish_ready": true,
  "state": "publish_ready",
  "do_not_publish_until": "..."
}
```

If the blocker has been satisfied, remove the active field entirely.

Permitted audit trail:

```json
"prior_publish_blocker_removed": {
  "field": "do_not_publish_until",
  "old_value": "...",
  "reason": "...",
  "removed_at_kst": "..."
}
```

Required blocker:

```text
status = BLOCKED_PUBLISH_READY_CARD_HAS_ACTIVE_DO_NOT_PUBLISH_UNTIL
```

## 5. Deferred/watchlist discipline

Do not delete high-value deferred cards simply because official/independent evidence is not yet available.

Use:

- `deferred_watchlist_high_value`
- `conditional_watchlist`
- `support_only_pending`
- `deprioritized_not_deleted`

A deferred card can be promoted only when the missing source-claim coverage is actually satisfied.

## 6. PR / GitHub merge hardening

Before PR or merge:

- verify total count;
- verify latest baseline;
- verify `publish_ready` cards have no active blockers;
- verify single-source publish cards have valid waiver;
- verify no visible internal terms remain:
  - `fetch`
  - `stage`
  - `quote mapping`
  - `baseline` unless user-facing context explicitly requires it;
- verify `source_independent_owner_count` is editorial-owner based, not `fact_sources[]` row count;
- verify UI display groups same canonical URL once;
- verify quote date is article/publication date, not fetch/check date.

## 7. Codex response protocol

If Codex flags metadata inconsistency:

1. Determine whether the issue is a visible claim problem or metadata/QC state problem.
2. Do not expand visible claims unless evidence requires it.
3. Prefer minimal metadata fix if the card is already fact-safe.
4. Add an audit record only if it is non-blocking.
5. Re-run:
   - JSON parse
   - publish-ready blocker scan
   - single-source waiver scan
   - visible internal-term scan
   - total count check

## 8. Required final statuses

A card may be merged only when:

```text
accepted_fact_safe = true
addable_merge_safe = true
evidence_complete = true
source_claim_covered = true
content_enriched = true
language_terminology_polished = true
publish_ready = true
github_ready = true
```

Any waiver or exception must be explicit, bounded, and auditable.
