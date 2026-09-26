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

The applied formal operation must materialize the same governed visible copy that Prompt 0.6 audited; a throwaway 0.6 change cannot authorize an unchanged operation. For a non-zero delta, at least one evidence-supported Deep Summary dimension must be bound to an actually changed governed field and concrete evidence token from the bound upstream B/C/0.5 chain. The upstream evidence token must itself be authorized for every mapped governed field; context-only / checked-not-used sources and explicit empty or nonmatching visible-field support (including canonical ledger `visible_supports`) do not qualify, and an explicit exclusion cannot be re-enabled by contradictory claim coverage or older upstream stages; evidence scope, grounding verified quote text, and preserved evidence package resolve from the same nearest authoritative upstream stage (`0.5 → 0.4 → C → B`), so stale older-stage text cannot authorize a nearer-stage contradiction. Multiple distinct usable packages sharing one token at that stage are ambiguous and block. Every claimed dimension must also be expressed by its mapped visible text. Formal full-run validation must additionally detect a newly added/deepened dimension signal versus the effective upstream governed copy as a whole (quantitative anchor, prior-state marker, execution/stage/status marker, boundary/uncertainty marker, transmission-path marker, or next-watchpoint marker), so moving existing information between governed fields is not enrichment. Qualitative synonyms are canonicalized before comparison, including equivalent commencement wording such as `began`/`started`; quantitative anchors preserve full bound/sign/number/magnitude/currency/unit identity, including prefix or suffix currency codes, so `-10 MW` differs from `10 MW`, `>20 MW` differs from `<20 MW`, `10 million USD` differs from `10 billion USD`, and `10 MW` differs from `10 MWh`, while equivalent numeric formatting such as `10`/`10.0`, `1,000`/`1000`, and `1,000,000`/`1000000` normalizes. Presentation formatting may normalize away, including paired Markdown wrappers spanning line breaks, but semantic strikethrough/retraction markup remains meaningful, including Markdown `~~...~~` and HTML `<del>` / `<s>` deletion tags. A terminology-only synonym, numeric-formatting-only edit (including leading-zero rewrites), negated execution/status wording, signal relocation, or new source token injected only at 0.6 is not sufficient. Newly added or semantically deepened dimension signals must be present in the referenced upstream verified source quote at equal or stronger status strength; token identity alone is insufficient. Only repository-approved verified quote statuses (`body_quote_verified`, `official_material_quote_verified`, `document_quote_verified`) with positive fetch metadata may ground claims. Every new governed signal in every changed field must be declared, field-mapped, and evidence-grounded. Evidence refs must be unique after normalization; duplicate refs cannot double-count one source quote. New substantive factual content outside the six signal taxonomies—such as locations, facilities, counterparties, entities, named identifiers, and ordinary lowercase factual predicates such as feedstock/material use—must also be present in the referenced nearest-stage evidence; verified upstream factual identities/predicates may not silently disappear. Verified upstream substantive signals may not silently disappear; only plan/expectation/uncertainty markers may contract when the same edit carries an evidence-grounded realized-state advancement. Evidence-backed modality deepening such as `may be delayed` → `is delayed` is substantive even when the canonical marker name is unchanged, with modality strength tracked per status occurrence rather than by one marker-wide maximum. Repeated canonical status terms are occurrence-aware, so a second distinct evidence-backed `approved` claim is not collapsed into the first. This is a semantic-signal gate, not a character-count rule.

Zero-delta passage is exceptional: it requires an explicit `no_change_required` reason plus a passing six-dimension Deep Summary density audit, and every mapped signal occurrence of every claimed true dimension must be grounded in its referenced upstream verified source quotes, subject to the explicit field-scoped exact-copy reuse rule below. The exception must show at least four evidence-supported dimensions including changed/current state; changed/current state requires an actual execution/status signal and is not satisfied by merely planned/target production wording, and every claimed true dimension must bind to concrete governed visible field(s) plus evidence reference(s) already present in the bound upstream B/C/0.5 evidence chain. Prompt 0.6 may not introduce a new source token solely to justify density. The materialized operation card must preserve the bound evidence refs, mapped field support, and upstream quote/claim plus verification-status package used by `dimension_evidence`; explicitly failed/unverified/mismatched/headline-or-snippet-only evidence cannot ground a claim; otherwise the run blocks. Raw character count is not a content-quality gate.

Explicit historical `PROMPT_0_6_V4_*` artifacts remain valid as historical records; the structured V5+ audit is not retroactively imposed on them. Formal-run validation resolves the applicable Prompt 0.6 version from the prompt file at the run's locked `base_main_commit_sha`, so a new run cannot self-label a V5+ baseline as V4 to bypass the audit. Standalone validation also fails closed when a supplied locked base cannot resolve the prompt/version instead of trusting self-declared provenance.

A verified quote status certifies only literal source text in `source_quote`, `quote`, `source_excerpt`, or `excerpt` (a non-empty string or list of non-empty strings). `claim`, `source_claim`, `claim_text`, `visible_claim`, and free-form `evidence_text` are editorial metadata, not independent grounding evidence. They remain preserved in the bound package but must not contribute numeric, state, identity, or density signals. A claim-only package is unusable even with positive fetch metadata or a verified-looking `claim_status`; adding an unverified editorial claim must not invalidate an otherwise usable literal quote. Reusing an excerpt still requires the existing quote-status, fetch, authority, exclusion, field-support, and materialized-package checks; these fields do not independently prove a live source was fetched or authenticated.

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

### Bounded quantity and state recognition

The shared quantity recognizer retains a single Korean scale without inventing a currency: `5억` and `5조` differ, and neither implies KRW. Common attached case particles must not erase that scale. Single `십`/`백`/`천`/`만`/`백만`/`억`/`조` scales use exact decimal shifts. Compound quantities such as `6십억원`, `2천억원`, `1조 2000억원`, and bare `1조 2000억` remain unsupported and must report `C06.QUANTITY.UNSUPPORTED`, not authorize an inner numeric token. Attached `30,000t` and spaced `30,000 t` retain the same unit. An explicit ordinal `제5조` is not a trillion-scale amount.

For supported state constructions, `착공에 들어갔다`/`착공에 돌입했다` are realized events; their negated, conditional, or planned forms are not. `가동 중단`/`가동 중지` cannot supply a running-state claim, although an actual suspension can itself be a realized event. A dated nonpast predicate such as `2027년 양산한다` is not proof of realization. A future date attached to the project does not undo an explicit past approval. `whether X was approved` queries X; a later independent `and will decide whether ...` does not make the preceding approval conditional. Genuine enclosing `if`/`unless` conditions remain non-realized.

These are bounded recognizer guarantees, not complete natural-language entailment or runtime-date validation. Unrecognized state syntax, event-subject/metric association, unsupported compositions and evidence-inheritance policy still require separate work. A passing local-row checker does not attest to upstream authority, actual field delta, materialization, or publication readiness.

### Source presence, field authority and grounding are separate

For V5+ content validation, retain three distinct views of the bound upstream
chain: (1) source-bearing records to preserve, (2) permitted visible fields,
and (3) usable verified literal quotes. A source can be present without being
permitted to ground any claim. In particular, paraphrase-only, unverified and
context-only records may remain in the output unchanged without becoming new
sources or usable quote evidence.

The preservation view selects each source identity's nearest declaration in
`0.5 → 0.4 → C → B`, including its source-ID/URL aliases. All distinct source-bearing
records at that stage are retained, with their original `fact_sources` or
`source_discovery_ledger` container and metadata. Dictionary key order and source
record order and explicit field-support set order are immaterial; silently dropping a record, changing its content,
verification flags, field scope, aliases or container role is not permitted at
0.6/materialization. New evidence and corrections belong upstream. Tokenless
search notes are outside this source-identity check; this is not a replacement
for the complete source-audit/ledger schema.

No-new-source and preservation checks compare against that source-record view,
not just the usable-quote subset. Removing an inconvenient paraphrase-only
source is not a way to pass. Conversely, retaining it does not make its claim,
missing quote, non-allowlisted status or failed fetch valid grounding. All
existing mapped-ref, quote-only, exclusion, package-identity and modality checks
continue to apply. A newer unverified declaration must not borrow a stale quote
or verified flag from an older stage.

Field scope and exclusion apply across transitive source aliases. Explicit
scope is a ceiling (intersect conflicting scopes); a claim-coverage reference or
an unscoped alias record cannot widen it. Full and standalone content checks use
the same row-local authority resolver. Standalone PASS still does not verify
upstream authority, actual visible delta, or final source preservation.

This change does not adopt `body_level_evidence_verified` as a verified-quote
alias, does not treat a missing ledger outcome as a successful outcome, and does
not exempt inherited numbers/claims from grounding. Missing ledger vocabulary remains separate; the bounded reuse rules below clarify grounding of retained claims. Historical locked V4 handling is unchanged.

## Field-scoped quote reuse — optional V5 audit extension

A retained fact is **not exempt from evidence grounding** merely because it was
present at 0.5 or a prior stage reported PASS. Reuse the already-preserved verified
literal quotes and their authorized field references; do not refetch unchanged
source material solely to repeat the same check. When the retained quote is
missing, unusable, excluded, or no longer supports the current subject/value/state,
repair the evidence upstream. A text hash, editor claim, or earlier PASS is not a
substitute. New and changed claims remain subject to the existing declaration,
novelty, factual identity, modality, and operation-copy checks.

An entry in `density_audit.dimension_evidence` may explicitly provide
`field_evidence_refs` to assign different source references to different visible
fields. For example, a retained fact can reuse S_OLD while a changed sub uses S_NEW:

```json
{
  "fields": ["sub", "fact"],
  "evidence_refs": ["S_NEW", "S_OLD"],
  "field_evidence_refs": {
    "sub": ["S_NEW"],
    "fact": ["S_OLD"]
  }
}
```

The optional map must have exactly the keys in `fields`. Each value is a non-empty
list of unique trimmed references, and their union must equal `evidence_refs`.
All references must resolve in the same authoritative upstream evidence context;
source-ID/URL aliases may not multiply a package. Every reference must be authorized
for every field **to which it is assigned**, without widening the source's explicit
support ceiling. Every mapped field must be grounded by its own assigned quotes;
quotes assigned only to another field cannot lend facts, numbers or modality.
Materialization must preserve the same references, permissions and complete source
records. Malformed maps fail closed, rather than falling back to the legacy mode.

Each field's observed signals are checked, including retained signals. An additional
combined occurrence budget protects distinct claims from sharing one occurrence.
Only identical **complete normalized field values** among the explicitly mapped
fields may reuse one quote occurrence. Different subjects, predicates, periods,
qualifiers or wording are not merged just because a number or marker is equal.
Repeats inside one field are not deduplicated. An implication array is not treated
as identical to a scalar string joined with a separator. Semantic retraction markup
is not removed to manufacture identity. Copying an existing complete field into
another field does not, by itself, create new enrichment; an unmapped destination
cannot borrow this reuse permission.

Zero-delta retains the four-dimension minimum and evidence-grounded realized state.
**All observed mapped claims**, not just one convenient number per dimension, must
be grounded subject to the exact-copy reuse rule. This deliberately rejects the
unsafe reading that one matching number authorizes another ungrounded retained
number. There is no automatic exemption for inherited clauses within a changed
field: include their retained verified reference alongside references for new facts.

When `field_evidence_refs` is absent, the existing fields-by-refs cross-product
and occurrence behavior is preserved. Existing audits are not silently migrated;
use the optional map only with validators that implement this extension. Historical
locked V4 handling is unchanged. This is bounded quote reuse, not a claim-ledger
verification cache or complete natural-language entailment. Differently worded
versions of the same fact, sub-sentence inheritance and unrecognized relations are
not automatically certified as equivalent. Standalone verifies only its supplied
row; it does not attest to upstream provenance, actual delta or final application.


### Ordered relation and exact-repeat checks

V5 grounding must not assemble a claim from unrelated occurrences of its subject,
object, counterparty or metric. The bounded machine observer preserves Korean
subject/object/predicate relations even when a numeric process qualifier intervenes;
it also observes explicit Korean subject/attribute descriptive clauses. English
transaction observations keep the whole ordered argument sequence, including
`to`/`from`, polarity and auxiliaries, rather than separate subject/object token pairs.
An immediately preceding explicit named-topic sentence (such as `Alpha project.`)
can bind `It` in the following sentence; this binding cannot cross separate quote
texts or field separators. A newly introduced ambiguous pronoun relation is a
`C06.RELATION.UNRESOLVED` repair requirement, not an inferred matching actor.

Explicit named-entity metric/period/quantity associations must match assigned
verified quotes, including when global number counts have not changed. A metric
reassignment must still declare/map `quantitative_anchor`. Boundary/uncertainty
subjects remain bound in the no-change path and legacy unscoped dimension maps;
field-scoped source authority and occurrence budgets remain unchanged. Technology
or product labels are not newly promoted to entity roles merely because they appear
next to a number.

Exact repeated or relocated normalized clauses cannot by themselves qualify as
newly added/deepened information, even if a quote repeats the same sentence. Distinct
named subjects, periods and metric roles remain distinct; other genuine enrichment
is not invalidated just because an existing sentence is also repeated. Numeric,
state, evidence-authority and deletion rules remain in force.

These are finite observed patterns, not a multilingual entailment engine. They do
not certify arbitrary passive/active paraphrases, translation, long-distance
coreference or every unrecognized predicate. Bound content validation compares
changed factual relations with the nearest upstream baseline and quotes. Standalone
validation shares mapped metric/boundary grounding, but cannot certify factual
novelty, actual prior/current changes or materialization without the bound chain.
A PASS on a finite probe set is not production or merge approval.
