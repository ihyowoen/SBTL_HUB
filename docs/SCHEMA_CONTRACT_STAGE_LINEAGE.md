<!-- REPLACE_ALL_CLEAN_VERSION: LLM_PROMPT_GITHUB_CANONICAL_V1_SOURCE_DIVERSITY_IB_CODEX -->
<!-- Generated KST: 2026-07-08T21:33:49.790191+09:00 -->
<!-- This file is a full clean replacement file. It is not a patch stub. -->

# SCHEMA_CONTRACT_STAGE_LINEAGE.md

Authoritative shared schema contract for SBTL_HUB stage lineage and artifact conformance.

This file is imported by reference by Stage A, Stage B, Stage C, Prompt 0.4, WORKFLOW, and OPERATIONS.

## Purpose

The pipeline must not discover required lineage omissions only at Prompt 0.4. Each named stage must verify its own output before recommending the next stage.

If a stage artifact is missing required schema fields, the stage must stop with:

```text
BLOCKED_STAGE_OUTPUT_SCHEMA_NONCOMPLIANT
```

Prompt 0.4 lineage guard remains hard. Do not weaken it to tolerate fields that the upstream prompt could and should have emitted.

---

## Stage A strict_passed_spec[] required lineage fields

Every `strict_passed_spec[]` item must include:

```text
spec_id
source_story_ids
strict_pass_gate
strict_pass_gate.status
strict_pass_gate.reason
strict_pass_gate.all_six_conditions_passed
enhanced_selector_precision_version
selector_policy_version
strict_gate_check
format_risk_tags
execution_anchor_type
execution_anchor_strength
baseline_relation
duplicate_risk
staleness_decision
source_access_risk
stage_a_evidence_status
stage_b_evidence_package_required
primary_url_semantics
```

`staleness_decision` is required as a top-level field. A nested explanatory
object such as `staleness.decision` may be present, but it does not satisfy this
contract by itself.

`stage_a_evidence_status` must be:

```text
not_evidence_complete_no_fetch
```

`primary_url_semantics` must be:

```text
provided_source_candidate_not_evidence
```

## Stage A top-level review-pool contract fields

Stage A output must include these top-level fields when any review/carry-forward
pool exists:

```text
review_pool_partition_summary
review_pool_carry_forward_ledger_status
review_pool_resolution_ledger
```

Do not expose these only in Markdown, CSV, `summary`, or nested `status_gates`.
Downstream stages and validators may block when the top-level aliases are
missing.

## Stage A hard-reject basis contract

`rejected[].hard_reject_basis` must be one of:

```text
out_of_scope
not_sbtl_lane
consumer_noise
local_noise
duplicate_without_incremental_value
stale_without_fresh_angle
source_broken_unrecoverable
generic_keyword_only
```

Risk/category labels such as `general_politics`, `politics`, `memorial`,
`sports`, `low_signal`, or `not_interesting` are not valid
`hard_reject_basis` values. Preserve them in detail/risk metadata if useful, but
map the closure basis to one of the allowed basis values.

---

## Stage B required lineage fields

Stage B output must include:

```text
lineage_integrity_status
stage_a_validity_guard_applied
strict_gate_metadata_preserved
execution_anchor_metadata_preserved
superseded_lineage_mixed
manual_integrated_rule_mixed
previous_run_output_mixed
```

Stage B must run `stage_a_validity_guard` before drafting. If Stage A strict specs are missing required lineage fields, Stage B must stop before evidence discovery with:

```text
BLOCKED_STAGE_A_LINEAGE_NONCOMPLIANT
```

---

## Stage C required lineage / id preservation

Every Stage C item in `accepted_fact_safe[]`, `revise_required[]`, `rejected[]`, and related validation pools must preserve:

```text
id
prior_id if changed
id_change_reason if changed
id_collision_recheck_required if changed
spec_id
source_story_ids
stage_b_lineage
strict_gate_acceptance_guard_applied
accepted_pool_lineage_status
```

If Stage C intentionally changes or removes an `id`, it must record:

```text
prior_id
new_id
id_change_reason
id_collision_recheck_required=true
```

---

## Prompt 0.4 preflight

Prompt 0.4 must verify:

```text
Stage A lineage fields complete
Stage B lineage flags complete
Stage C id preserved
Stage C lineage preserved
ID collision screening possible
```

If upstream required fields are missing, Prompt 0.4 must block. This is correct behavior.

---

## Provided-source/evidence distinction

Provided URLs, `primary_url`, source hints, Stage A `usable_text`, and Stage A `context_text` are not evidence.

They become evidence only after Stage B fetch/direct inspection, source_quote extraction, claim mapping, fetch_ledger recording, and evidence_package creation.

# SCHEMA_CONTRACT_STAGE_LINEAGE.md — Source Diversity source-diversity integrated rule

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

## Source-diversity lineage contract

Required Stage A lineage:

```text
same_event_source_cluster
support_source_candidates
source_domain_candidates
source_diversity_path
source_cluster_preserved
```

Required Stage B lineage:

```text
stage_a_support_sources_attempted
source_independence_ledger
source_unique_url_count
source_unique_domain_count
source_independent_owner_count
source_role_coverage
source_synthesis_plan
```

Required Stage C and downstream lineage:

```text
source_diversity_status
source_diversity_measure
source_diversity_roles
source_synthesis_applied
source_synthesis_fields
source_synthesis_audit
single_source_exception
source_published_date
visible_quote_date
```

Every downstream stage must preserve these fields or explicitly mark them not applicable with a
reason. Missing fields block state advancement with:

```text
BLOCKED_SOURCE_DIVERSITY_LINEAGE_MISSING
```

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
