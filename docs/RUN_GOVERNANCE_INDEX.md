# SBTL_HUB Run Governance Index V4.1

**Status:** `ACTIVE_CANONICAL`  
**Version:** `RUN_GOVERNANCE_INDEX_V4_1_20260902`

## 0. Authority model

This index is the entry authority for every run. The active ordinary-run architecture is **clean named-stage governance with deterministic authority locking**.

Operative rules are fixed at run start by repository path + git blob SHA. They are not appended later through override, hardening, overlay, or addendum documents, and they are not all forced into the model context at once.

## 1. Authority precedence

1. locked GitHub `main` commit + deterministic governance lock for identity/version;
2. `FACT_DISCIPLINE.md` for facts, numbers, quotes, and evidence boundaries;
3. this index and `DOCUMENT_UNIVERSE_POLICY.md` for lifecycle/applicability;
4. a specifically named active canonical contract for its domain;
5. the current locked named-stage prompt for stage input/output/state transition;
6. machine-enforced schema/validator contract within its declared scope;
7. applicable bounded remediation or migration only when explicitly activated.

Unresolved authority conflict blocks the next stage.

## 2. Active canonical documents

The lifecycle registry is the machine-readable authority list. It registers active canonical domains, active named prompts, validator contracts, remediation/migration, superseded references, and the small `bootstrap_read[]` set.

The full active set is **locked** at 0.0D. Locking does not mean every body must be deep-read before 0.0C.

## 3. Non-active historical policy families

Files whose names contain historical `OVERRIDE`, `ADDENDUM`, `HARDENING`, or overlay-package terminology are not ordinary-run authorities once marked `SUPERSEDED` or `REFERENCE_ONLY` in the lifecycle registry/header.

They may be retained to explain historical artifacts. They must not become an additional rule because they are opened later.

## 4. 0.0D requirement

0.0D must:

- lock repository SHA and canonical full blob SHA;
- deterministically inventory every `docs/**` file;
- classify every path using the locked lifecycle registry;
- bind every active authority to its exact git blob SHA;
- emit and replay-verify `governance_lock_v1`;
- verify active runtime override/addendum count is zero;
- verify Stage A contains embedded news value + Related pre-pass;
- load only the exact registry `bootstrap_read[]` context before 0.0C;
- block on missing/unclassified/duplicated lifecycle registration or blob/baseline mismatch.

0.0D must **not** use a model-generated `active_full_read_count` as evidence that the active universe was read.

## 5. Named-stage JIT rule

Every named-stage prompt is a complete operating contract for that stage together with any active canonical domain contract it explicitly requires.

The prompt is locked at 0.0D but loaded just before the stage executes. The loaded path/blob must match the governance lock. A future-stage prompt is not mandatory context for an earlier stage.

A prompt is invalid if it requires a later overlay/addendum to obtain the real rules.

## 6. News-value rule

Item-level news-value selection is embedded in Stage A. Portfolio-level news value/completeness is in `EDITORIAL_VALUE_AND_COMPLETENESS_STANDARD.md`. `STRUCTURAL_NEWS_VALUE_SELECTION.md` and the historical Stage A Structural Value Override prompt are superseded references, not active dependencies.

## 7. Related/addability rule

Related lifecycle starts at Stage A and locks at Stage C. Prompt 0.4 is current-baseline addability revalidation, not first-lineage creation.

## 8. Mutation modes

Two ordinary governed mutation modes exist:

- formal full-run `card-run` after authorized 0.8;
- bounded `manual_direct_add` for already-reviewed changes.

They are mutually exclusive within one data PR. A manual direct add never inherits or claims missing full-run stages.

## 9. Migration/remediation

Migration and remediation are bounded, explicitly activated, auditable, and non-permanent. They are blob-locked at 0.0D and loaded only when applicable.

Recurring policy belongs in active canonical documents, not in an eternal patch.

## 10. Governance registration

A recurring active rule must be represented in this index/lifecycle registry and, where executable, in CI/validator configuration. An unregistered active-looking governance file blocks 0.0D rather than silently becoming authority.

The deterministic lock must be reproducible from the exact declared baseline commit; a self-reported read list, count, excerpt hash, or remembered closure cannot substitute for that replay.
