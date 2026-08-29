# Post-Acceptance QC Contract V2

**Status:** `ACTIVE_CANONICAL`  
**Version:** `POST_ACCEPTANCE_QC_V2_20260829`

## 1. Purpose

Own the formal transitions after Stage C fact-safe acceptance and before mutation. It does not contain Stage A selector rules or duplicate copies of Source Audit/Fact Discipline.

State ladder:

`accepted_fact_safe → addable_merge_safe → evidence_complete → source_claim_covered → content_enriched → language_terminology_polished → publish_ready`

## 2. 0.4 — addability

Revalidate latest accepted cards against exact current canonical full/current batch. Confirm duplicate/reinforcement/update/follow-up/program-lineage identity and baseline collisions. Preserve Stage C lineage; route changed identity upstream. Reset publish-ready state.

## 3. 0.5 — evidence/source-claim completeness

Verify every material visible claim, number, date, entity, source quote/status, durable URL, editorial-owner diversity, discovery ledger, source synthesis, and valid single-source exception under Fact Discipline + Source Audit.

If stronger/earlier evidence changes event identity, return upstream. Evidence quality cannot launder stale/duplicate selection.

## 4. 0.6 — content/terminology

Improve only evidence-safe visible copy and decision-useful framing. Preserve verified facts, source audit, date role, selection route, and Related lineage. Do not silently add new evidence or mutate event identity.

## 5. 0.7 — publish readiness

Revalidate full schema, fact/source coverage, source synthesis, date/ID, event identity, selection route, Related lineage, terminology, unsupported inference, active blockers, and latest-version status.

No card may be both `publish_ready=true` and carry an active do-not-publish blocker. A single-source publish-ready card requires a valid allowed exception.

## 6. 0.7C — independent completeness

A separate reviewer challenges missing-news coverage, exclusions, baseline follow-ups, duplicate/follow-up errors, corrections/reinforcements, news value, and residual risk. Formal 0.8 remains blocked without explicit authorization.

## 7. No downstream laundering

Post-acceptance stages cannot silently resurrect Stage A review/watch/reject pools, Stage B draft-blocked items, or Stage C deferred/rejected items. Promotion uses an authorized upstream review path.

A later-discovered source that changes claims/date/identity is routed to the appropriate owning stage rather than silently inserted into a higher state.

## 8. Rescue

Fetch-enabled post-acceptance stages perform bounded rescue before evidence-based hold/reject where the named prompt permits it. Rescue does not authorize unsupported enrichment.

## 9. Naming

Do not call an artifact final, PR candidate, merge-ready, or production-verified before the named state exists. Prompt 0.7 output is publish-ready only; Prompt 0.8 creates merge-ready; Prompt 0.9 creates production verification.