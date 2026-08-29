# SBTL_HUB Run Governance Index V4

**Status:** `ACTIVE_CANONICAL`  
**Version:** `RUN_GOVERNANCE_INDEX_V4_20260829`

## 0. Authority model

This index is the entry authority for every run. The active ordinary-run architecture is **clean named-stage governance**: operative rules are present at stage entry and are not appended later through override, hardening, overlay, or addendum documents.

## 1. Authority precedence

1. `FACT_DISCIPLINE.md` for facts, numbers, quotes, and evidence boundaries.
2. This index and `DOCUMENT_UNIVERSE_POLICY.md` for document lifecycle/applicability.
3. A specifically named active canonical contract for its domain.
4. The current named-stage prompt for stage input/output/state transition.
5. Machine-enforced schema/validator contract within its declared scope.
6. Applicable bounded remediation or migration only when explicitly activated.

Unresolved authority conflict blocks the next stage.

## 2. Active canonical documents

- `docs/WORKFLOW.md`
- `docs/OPERATIONS.md`
- `docs/FACT_DISCIPLINE.md`
- `docs/DOCUMENT_UNIVERSE_POLICY.md`
- `docs/EDITORIAL_VALUE_AND_COMPLETENESS_STANDARD.md`
- `docs/RELATED_LIFECYCLE_CONTRACT.md`
- `docs/SOURCE_AUDIT_CONTRACT.md`
- `docs/SCHEMA_CONTRACT_STAGE_LINEAGE.md`
- `docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md`
- `docs/CARD_ID_STANDARD.md`
- `docs/CARD_INCREMENTAL_RUN_CONTRACT.md`
- `docs/POST_ACCEPTANCE_CONTENT_ENRICHMENT_QC.md`
- `docs/PROMPT_ABC_DEFAULT_MODE.md`
- `docs/llm_prompts/v1/PROMPT_MANIFEST.md`
- `docs/llm_prompts/v1/00_NEW_RUN_MASTER_PROMPT.md`
- the current named-stage prompts registered by `PROMPT_MANIFEST.md`
- the active manual-direct-add contract registered by the lifecycle registry.

## 3. Non-active historical policy families

Files whose names contain historical `OVERRIDE`, `ADDENDUM`, `HARDENING`, or overlay-package terminology are not ordinary-run authorities once marked `SUPERSEDED` or `REFERENCE_ONLY` in the lifecycle registry/header.

They may be retained to explain historical run artifacts. They must not be loaded as an additional active rule after a named stage has begun.

## 4. 0.0D requirement

0.0D must:

- lock repository SHA;
- inventory every `docs/**` file;
- classify every path using registry/header;
- fully read all active canonical docs and active dependency closure before Stage 0.0C;
- verify superseded/reference docs are non-operative;
- identify applicable open remediation/migration;
- detect unregistered active-looking files and unresolved conflicts.

It does **not** need to deep-read every historical reference file after its non-operative lifecycle is authoritatively established.

## 5. Named-stage rule

Every named-stage prompt is a complete operating contract for that stage together with the active canonical domain contracts it explicitly names. A prompt is invalid if it says a later overlay/addendum must be appended to obtain the real rules.

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

Migration and remediation are bounded, explicitly activated, auditable, and non-permanent. Recurring policy belongs in active canonical documents, not in an eternal patch.

## 10. Governance registration

A recurring active rule must be represented in this index/lifecycle registry and, where executable, in CI/validator configuration. An unregistered active-looking governance file blocks 0.0D rather than silently becoming authority.