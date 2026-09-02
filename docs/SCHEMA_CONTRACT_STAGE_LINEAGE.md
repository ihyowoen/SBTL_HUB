# Stage Lineage Schema Contract V2

**Status:** `ACTIVE_CANONICAL`  
**Version:** `STAGE_LINEAGE_SCHEMA_V2_20260829`

## 1. Purpose

Each named stage must prove its own input/output state so downstream stages do not reconstruct missing decisions from memory. This contract owns stage-to-stage lineage metadata, not source-diversity rules, card taxonomy, or editorial scoring policy.

Missing required lineage blocks advancement with `BLOCKED_STAGE_OUTPUT_SCHEMA_NONCOMPLIANT` or the stage-specific blocker.

## 2. Common provenance

Every named-stage artifact records:

- stage name/version;
- current prompt path and content/blob SHA provenance;
- locked repository/main SHA relevant to the stage;
- run/source universe identifier;
- input artifact references;
- complete input/output accounting.

## 3. Stage A strict lineage

Every strict candidate carries:

- source/spec/story identities;
- `selection_policy_version = EMBEDDED_NEWS_VALUE_SELECTION_V4`;
- `selection_route`;
- execution credibility and independent cardability gates;
- anchor classes;
- decision-news-value score/breakdown/classification;
- publication urgency;
- prior/new/changed-judgment chain;
- incremental information and remaining uncertainty;
- baseline relation, duplicate/freshness disposition;
- `related_prepass`;
- item-specific Stage B evidence targets;
- next confirmation points;
- review-pool lineage where applicable.

Current V3 machine validators may require legacy alias fields such as `structural_value_override_applied`, `structural_selector_policy_version`, `execution_anchor_type`, or `execution_anchor_strength`. Those aliases may be emitted for compatibility but do not create a second active policy contract.

## 4. Stage B lineage

Stage B preserves Stage A selection package and emits:

- Stage A validity/provenance guard;
- evidence/source package references;
- `date_role` and event-date evidence;
- `related_evidence_review`;
- source-audit metadata under Source Audit;
- draft or draft-blocked disposition;
- unresolved evidence/date/lineage questions.

Stage B stops before drafting if required Stage A lineage is absent.

## 5. Stage C lineage

Every outcome preserves source/spec identity and Stage A/B packages. Accepted new cards additionally emit:

- `accepted_fact_safe` state;
- selected-route evidence validation;
- final fact-safe date role;
- `related_lineage.status = PASS` and relation type/targets/reason;
- prior/new ID metadata only if a genuine correction is proposed;
- unresolved downstream issues.

Same-event duplicate/reinforcement/unresolved relation cannot be lineage-locked as an accepted new card.

## 6. Prompt 0.4 addability lineage

0.4 consumes latest Stage C accepted version and latest canonical baseline. It records:

- baseline main/full SHAs;
- accepted input identity/version;
- Stage C lineage preservation;
- duplicate/event-fingerprint checks;
- current baseline relation result;
- addability disposition;
- update/reinforcement routing when applicable.

0.4 does not synthesize missing Stage A/B/C lineage.

## 7. Prompt 0.5–0.7

These stages preserve selection/date/Related lineage unless explicitly returning upstream. Evidence/source changes that alter event identity must trigger upstream revalidation.

0.7 records the final publish-ready state only for the latest valid candidate version and current-run scope.

## 8. Prompt 0.7C

Independent completeness output references the publish-ready set, exclusion/review ledgers, baseline follow-up review, coverage matrices, material exclusions, known unknowns, residual risks, and explicit 0.8 authorization state.

## 9. Prompt 0.8

0.8 records final production-ID assignment/resolution, declared operations, field-level updates, Related ID resolution, exact baseline lock, apply report, full/lean hashes, validator results, and merge-ready state.

## 10. Direct add

Manual direct-add has its own manifest lineage and does not counterfeit this formal stage chain. V2 editorial attestation is review provenance, not a Stage A artifact.

## 11. Legacy isolation

Strict current-run lineage is required for current-run cards. Legacy cards are not retroactively failed or rewritten merely because they predate a newer lineage container; legacy remediation/migration remains separately scoped.