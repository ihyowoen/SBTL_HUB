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

The applied formal operation must materialize the same governed visible copy that Prompt 0.6 audited; a throwaway 0.6 change cannot authorize an unchanged operation. For a non-zero delta, at least one evidence-supported Deep Summary dimension must be bound to an actually changed governed field and concrete evidence token from the bound upstream B/C/0.5 chain. The upstream evidence token must itself be authorized for every mapped governed field; context-only / checked-not-used sources and explicit empty or nonmatching visible-field support (including canonical ledger `visible_supports`) do not qualify, and an explicit exclusion cannot be re-enabled by contradictory claim coverage or older upstream stages; evidence scope, grounding quote/claim text, and preserved evidence package resolve from the same nearest authoritative upstream stage (`0.5 → 0.4 → C → B`), so stale older-stage text cannot authorize a nearer-stage contradiction. Multiple distinct usable packages sharing one token at that stage are ambiguous and block. Every claimed dimension must also be expressed by its mapped visible text. Formal full-run validation must additionally detect a newly added/deepened dimension signal versus the effective upstream governed copy as a whole (quantitative anchor, prior-state marker, execution/stage/status marker, boundary/uncertainty marker, transmission-path marker, or next-watchpoint marker), so moving existing information between governed fields is not enrichment. Qualitative synonyms are canonicalized before comparison, including equivalent commencement wording such as `began`/`started`; quantitative anchors preserve full bound/sign/number/magnitude/currency/unit identity, including prefix or suffix currency codes, so `-10 MW` differs from `10 MW`, `>20 MW` differs from `<20 MW`, `10 million USD` differs from `10 billion USD`, and `10 MW` differs from `10 MWh`, while equivalent numeric formatting such as `10`/`10.0`, `1,000`/`1000`, and `1,000,000`/`1000000` normalizes. Presentation formatting may normalize away, but semantic strikethrough/retraction markup remains meaningful, including Markdown `~~...~~` and HTML `<del>` / `<s>` deletion tags. A terminology-only synonym, numeric-formatting-only edit (including leading-zero rewrites), negated execution/status wording, signal relocation, or new source token injected only at 0.6 is not sufficient. Newly added or semantically deepened dimension signals must be present in the referenced upstream source quote/claim package at equal or stronger status strength; token identity alone is insufficient. Only repository-approved verified quote statuses (`body_quote_verified`, `official_material_quote_verified`, `document_quote_verified`) with positive fetch metadata may ground claims. Every new governed signal in every changed field must be declared, field-mapped, and evidence-grounded. Evidence refs must be unique after normalization; duplicate refs cannot double-count one source quote. New substantive factual identities outside the six signal taxonomies—such as locations, facilities, counterparties, entities, or named identifiers—must also be present in the referenced nearest-stage evidence. Verified upstream substantive signals may not silently disappear; only plan/expectation/uncertainty markers may contract when the same edit carries an evidence-grounded realized-state advancement. Evidence-backed modality deepening such as `may be delayed` → `is delayed` is substantive even when the canonical marker name is unchanged. Repeated canonical status terms are occurrence-aware, so a second distinct evidence-backed `approved` claim is not collapsed into the first. This is a semantic-signal gate, not a character-count rule.

Zero-delta passage is exceptional: it requires an explicit `no_change_required` reason plus a passing six-dimension Deep Summary density audit, and every claimed true dimension must have a matching signal in both the mapped visible text and its referenced upstream source quote/claim evidence. The exception must show at least four evidence-supported dimensions including changed/current state; changed/current state requires an actual execution/status signal and is not satisfied by merely planned/target production wording, and every claimed true dimension must bind to concrete governed visible field(s) plus evidence reference(s) already present in the bound upstream B/C/0.5 evidence chain. Prompt 0.6 may not introduce a new source token solely to justify density. The materialized operation card must preserve the bound evidence refs, mapped field support, and upstream quote/claim plus verification-status package used by `dimension_evidence`; explicitly failed/unverified/mismatched/headline-or-snippet-only evidence cannot ground a claim; otherwise the run blocks. Raw character count is not a content-quality gate.

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