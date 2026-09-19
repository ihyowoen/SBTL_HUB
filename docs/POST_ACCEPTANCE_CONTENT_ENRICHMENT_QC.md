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

A V5+ `content_enriched=true` transition requires a machine-checked substantive delta in `sub/gate/fact/implication` against the nearest non-empty normalized upstream visible copy, resolved field-by-field in the order `0.5 → 0.4 → Stage C`. Omission, null, empty intermediate values, whitespace-only differences, presentation-markup-only changes, and removals/emptying do not qualify as substantive enrichment.

The applied formal operation must materialize the same governed visible copy that Prompt 0.6 audited; a throwaway 0.6 change cannot authorize an unchanged operation. For a non-zero delta, at least one evidence-supported Deep Summary dimension must be bound to an actually changed governed field and concrete evidence token from the bound upstream B/C/0.5 chain; a terminology-only/formatting-only string difference or a new source token injected only at 0.6 is not sufficient.

Zero-delta passage is exceptional: it requires an explicit `no_change_required` reason plus a passing six-dimension Deep Summary density audit. The exception must show at least four evidence-supported dimensions including changed/current state, and every claimed true dimension must bind to concrete governed visible field(s) plus evidence reference(s) already present in the 0.6 evidence package. Raw character count is not a content-quality gate.

Explicit historical `PROMPT_0_6_V4_*` artifacts remain valid as historical records; the structured V5+ audit is not retroactively imposed on them. Formal-run validation resolves the applicable Prompt 0.6 version from the prompt file at the run's locked `base_main_commit_sha`, so a new run cannot self-label a V5+ baseline as V4 to bypass the audit. Standalone validation also fails closed when a supplied locked base cannot resolve the prompt/version instead of trusting self-declared provenance.

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