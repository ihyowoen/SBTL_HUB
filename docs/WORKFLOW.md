# SBTL_HUB Canonical Workflow V4

**Status:** `ACTIVE_CANONICAL`  
**Version:** `SBTL_WORKFLOW_V4_20260829`

## 0. Purpose

This document is the single operational map for ordinary SBTL_HUB news runs. Named stage prompts contain their complete operative rules. Ordinary runs do not assemble policy by appending override, hardening, or addendum files after a stage has started.

## 1. Canonical ownership

- `data/cards.full.json` is the sole canonical card inventory.
- `public/data/cards.json` is a deterministic lean projection generated from canonical full.
- Current GitHub `main` outranks chat memory, prior run artifacts, downloaded ZIPs, and local copies.
- Every run locks the current main commit SHA and canonical full blob SHA before editorial work begins.
- A baseline move requires revalidation before mutation.

## 2. Ordinary full-run lifecycle

```text
New Run Master Prompt
→ current main baseline lock
→ 0.0D Active Governance Preflight
→ Raw Input Audit
→ 0.0C Coverage Discovery
→ authoritative expanded event universe lock
→ pre-Stage-A canonical reconciliation and event clustering
→ 0.1 Stage A Integrated Selector
→ 0.2 Stage B Evidence + Draft
   ↔ 0.2R Stage B Controlled Revise, only when a bounded B-owned defect requires repair
→ 0.3 Stage C Fact-Safe + Lineage Lock
   ↔ 0.3R Stage C Controlled Revalidation, only when a bounded C-owned defect requires repair
→ 0.4 Current-Baseline Addability Revalidation
→ 0.5 Evidence / Source-Claim QC
→ 0.6 Content / Terminology Polish
→ 0.7 Final Publish-Readiness QC
→ 0.7C Independent Completeness Review
→ 0.8 Incremental Operation / Merge Preparation
→ repository validators and PR review
→ GitHub merge
→ 0.9 Production Verification
→ 1.0 bounded remediation when needed
→ 1.1 retrospective / rule promotion
```

0.2R and 0.3R are **conditional repair loops**, not mandatory sequential stages. No named stage is silently substituted by an ad-hoc review.

## 3. State ladder

```text
stage_a_selected_strict
→ draft_evidence_complete_enough_for_red_team
→ accepted_fact_safe
→ addable_merge_safe
→ evidence_complete
→ source_claim_covered
→ content_enriched
→ language_terminology_polished
→ publish_ready
→ github_merge_ready
→ production_verified
```

These states must not be collapsed. In particular:

- `accepted_fact_safe` is not `addable_merge_safe`.
- `addable_merge_safe` is not `publish_ready`.
- `publish_ready` is not `production_verified`.

## 4. Discovery and completeness

Raw input is a source-candidate universe, not proof of completeness. Stage 0.0C independently searches required regions and topics, challenges material existing-card follow-ups, and records terminal dispositions for all discovered candidates.

Search first, verify second, narrow third, abandon last.

## 5. Integrated news-value selection

The active Stage A prompt contains the complete news-value policy. There is no separate active Structural News Value or Structural Value Override prompt.

Every candidate receives four independent judgments:

1. execution credibility;
2. independent cardability;
3. decision news value;
4. publication urgency.

Valid anchor classes are:

- `execution_event_anchor`;
- `policy_regulatory_anchor`;
- `data_financial_anchor`;
- `strategic_behavior_anchor`;
- `technology_commercialization_anchor`;
- `follow_up_probability_anchor`.

A conventional execution event is not mandatory when another current, source-plausible anchor materially changes a decision-relevant judgment. Evidence standards are not lowered.

The authoritative scoring and novelty caps are embedded in Stage A and `EDITORIAL_VALUE_AND_COMPLETENESS_STANDARD.md`.

## 6. Related lineage is not addability

Related lifecycle begins before drafting and persists through production:

```text
Stage A: metadata-only related pre-pass
→ Stage B: body/official-evidence relation resolution
→ Stage C: fact-safe lineage lock
→ 0.4: latest-baseline addability revalidation
→ 0.5 / 0.7 / 0.7C: backstop and red-team
→ 0.8: final production-ID resolution
→ 0.9: live relation verification
```

`related[]` means direct auditable event lineage, not topical similarity. Same company, chemistry, country, sector, or theme is insufficient.

Prompt 0.4 does not create lineage for the first time. It asks whether an already lineage-audited accepted card is still addable against the latest canonical baseline.

## 7. Stage role boundaries

### 0.1 Stage A
Selector-only. No external body fetch, no `fact_sources`, no source quotes, no card copy, no fact-safe or publish-ready decision.

### 0.2 Stage B
Fetches and verifies evidence, resolves Stage A relation questions, establishes date roles, and drafts only strict Stage A candidates. Evidence gaps may block a draft.

### 0.2R Stage B Controlled Revise
Repairs a bounded B-owned defect such as quote/source repair, date evidence repair, evidence augmentation, or evidence-bounded draft narrowing. After repair, Stage B exit validity is re-established before Stage C. A selection, staleness, duplicate, or material event-identity defect is not a 0.2R wording fix and returns upstream.

### 0.3 Stage C
Independent fact-safe red-team. Locks lineage for accepted new cards. Same-event duplicate, reinforcement-only, or unresolved relation candidates cannot be accepted as new cards.

### 0.3R Stage C Controlled Revalidation
Rechecks an authorized revised item after the identified C-owned defect is repaired. It may re-lock fact-safe lineage, return the item for another bounded repair when allowed, reject/defer it, or route a selection/event-identity defect upstream. Accepted output then continues to 0.4.

### 0.4 Addability
Rechecks accepted cards against the exact current canonical full and current batch. Outcomes distinguish addable new event/follow-up/program lineage from duplicate, reinforcement, conflict, and deferred relation uncertainty.

### 0.5–0.7
Evidence completeness, content polish, and final publish readiness. Strong evidence cannot launder a stale, duplicate, or selection defect.

### 0.7C
Separate completeness reviewer reopens missing-news, exclusion, duplicate/follow-up, reinforcement, correction, regional/topic coverage, and must-report questions. Formal 0.8 is blocked without authorization.

### 0.8
Creates declared incremental operations against a locked current baseline.

### 0.9
Verifies merged main and production. Merge is not run completion.

## 8. Repair and backward-routing rule

R is a repair mechanism, not a second editorial pipeline.

- B-owned evidence/date/source/draft defect → 0.2R, then restore B exit validity and return to C.
- C-owned fact-safe/lineage validation defect after an authorized repair → 0.3R, then continue to 0.4 only if accepted again.
- coverage omission → 0.0C.
- selection/news-value/cardability defect → A or authorized 0.1P where applicable.
- material evidence/date/source defect that changes the represented event → B and then C again.
- fact-safety/lineage-lock defect → C after required upstream repair.
- latest-baseline collision/addability defect → 0.4 or the earlier stage that owns the underlying identity defect.
- claim-coverage defect → 0.5 unless it changes facts/date/identity, in which case route farther upstream.
- copy/terminology-only defect → 0.6.
- completeness omission discovered at 0.7C → re-enter at 0.0C/A/B/C as required by the newly discovered event.

After any upstream re-entry, rerun every affected downstream gate. Do not repair a lower-stage defect inside 0.7 merely to obtain a green result.

There are no separate ordinary `0.4R`, `0.5R`, `0.6R`, or `0.7R` prompt families. Those stages route defects to the earliest responsible named stage instead of accumulating more repair prompts.

## 9. Ordinary canonical operations

Formal ordinary run operations are:

```text
insert
update
related_add
```

Existing IDs and existing related edges are preserved by default. `delete` and `related_remove` require separately authorized remediation. Rescue, repair, reinforcement, and update precede deletion.

## 10. Governed direct-add lane

A bounded direct add is a separate governed mutation lane for changes whose editorial/evidence review is already complete. It does not fabricate Stage A/B/C, 0.7C, or 0.8 completion.

Future direct adds use `MANUAL_DIRECT_ADD_V2` and must include machine-readable editorial/news-value attestation for new cards, exact baseline locking, declared mutation scope, and full-to-lean verification.

## 11. Per-stage prompt-read gate

Before each named stage:

1. open the current named prompt from the locked repository state;
2. record its path and blob/SHA provenance;
3. restate its required input state and output schema;
4. execute only after the prompt and active canonical dependencies are loaded.

A stage executed from memory is invalid.

## 12. Governance architecture rule

Active ordinary-run governance must be complete at stage entry. No active rule may depend on a later-applied override, overlay, hardening addendum, or patch stub.

Historical override/addendum files may remain only as `SUPERSEDED` or `REFERENCE_ONLY` audit records and must not be applied.

## 13. Completion rule

Do not claim `PASS`, `clean`, `complete`, `merge-ready`, or `production_verified` without the executed item-level or repository-level checks that create that state.