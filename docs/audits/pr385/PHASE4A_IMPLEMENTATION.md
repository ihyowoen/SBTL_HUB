# PR #385 — Phase 4A: quantity and non-realized-state observations

## Scope

This is a bounded runtime checkpoint after `ee023a13eb141c594a4e595fbbc4bb1ec134e604`.
It is **not** completion of the semantic redesign or authorization to merge.
No new subscription, service, agent integration, canonical card-data change,
Prompt version change, historical provenance rewrite, or main-branch update is included.

## Runtime boundary

`content_semantic_atoms.py` owns the shared quantity recognizer and state
observations. `QuantityObservation` preserves its raw source span and a typed
identity, including sign, bound, numeric value, magnitude/currency, unit and
denominator. Existing binding entrypoints retain compatibility aliases; they do
not acquire a second quantity parser. Plain dimensionless rates retain their
denominator as well as measured rates.

Unambiguous Unicode minus glyphs normalize to ASCII minus, not to positive
numbers. A single-scale Korean money expression retains the exact amount:
`20억원` is distinct from `20조원`; `1억원` equals `100000000원`.
Decimal shifting is string-based and does not round large values. An unspecified
Korean dollar label is not guessed to be USD. Multiple-scale Korean expressions,
such as `1조 2000억원`, are explicitly unsupported in this checkpoint. The common
coverage policy reports `C06.QUANTITY.UNSUPPORTED` for current visible copy;
unsupported evidence expressions cannot supply their inner partial numbers.
No source or visible card is silently rewritten to make it pass.

`StateObservation` includes strength, classification and the reason. Supported
Korean negative/conditional/prospective constructions are not realized states;
possibility remains tentative; unsupported Korean state syntax returns an
explicit unresolved classification with strength zero. Supported positive
Korean assertions remain usable. English conditional scope is separate from
local and/or negation scope, including numeric decimals and dotted initialisms.
Existing English finite grammar is preserved behind this additional scope check.
This remains bounded linguistic recognition, not an unrestricted truth oracle.

Both content-gate and standalone audit paths use these same quantity/state
observations and the common quantity-coverage policy. Upstream authority,
source exclusions, package preservation, locked contract version, exact delta,
and operation-copy binding remain unchanged. P04 remains a valid changed-copy
case; the zero-delta-only realized requirement is not reapplied to it.

## Verification and limitations

The original `docs/audits/pr385/reproduce.py` and original pinned diagnostic
workflow are unchanged. The original 32-case characterization remains an honest
safety diagnostic, not an expectedFailure suite.

Expected observed changes against Phase 3 are exactly:
`A01`, `A02`, `A03`, `A04`, `R01_unicode_sign`, `R02_korean_scale`,
`R03_korean_negated_zero`, and `R04_conditional_zero`.

The remaining characterization is **23 met / 9 violated / 0 runtime errors**.
Four of the original eleven unsafe synthetic content-gate scenarios are fixed;
**R05–R11 remain open**: Korean descriptive content, quantified Korean relations,
boundary subjects, repetition/novelty, pronoun associations, argument grouping,
and same-entity metric associations. Component/upper-gate violations overlap;
the nine residual violations are not nine independent production incidents.

There are 38 new unittest methods with normal/adversarial subcases. They include
actual standalone CLI executions, grounded sign/scale and Korean realized-state
controls, explicit compound-coverage rejection, conditional-scope boundaries,
immutability, numerical equivalence and no-rounding checks. The intended active
suite total is 984 (existing 946 plus 38). Exact executed totals, return codes,
commit/blob identities and logs are recorded in the checkpoint artifact, not
inferred from this document.

The preparation workflow only publishes a fresh proof branch when this bounded
checkpoint's criteria hold. It uploads the residual safety failures and still
ends failure when the 32-case safety suite is not all green. A connector-mediated
fast-forward of PR #385 is a separate action after reviewing the artifact.

**Not executed here as part of the checkpoint:** complete production-run CLI,
production materializer, real KR/EN artifact replay, or final-main compatibility.
These remain mandatory before merge readiness; synthetic source-status flags
are test inputs, not verification of the truth of any real source.
