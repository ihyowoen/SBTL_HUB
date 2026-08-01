# Prompt 1.1 Canonical Rule-Promotion Addendum

**Status:** `ACTIVE_MANDATORY_ADDENDUM`  
**Applies to:** `13_PROMPT_1_1_Retrospective.md`

## 1. Document-universe precondition

The retrospective must use the current Stage 0.0D document-universe artifact, not a fixed list of core documents.

If the run stopped before Stage 0.0D completed, the retrospective must report the document-universe failure explicitly and must not claim process-wide rule compliance.

## 2. Retrospective scope additions

The retrospective must evaluate:

- whether every `docs/**` file was read or parsed in full;
- whether active rules were classified and applied correctly;
- whether Stage 0.0C found missing news, follow-ups, corrections, and reinforcements;
- whether Stage A used the expanded source universe;
- whether Stage 0.7C independently challenged completeness and news value;
- whether ordinary operations were limited to `insert`, `update`, and `related_add`;
- whether existing related edges were preserved;
- whether any migration contaminated permanent rules;
- whether any newly discovered recurring rule remains only in a patch or comment.

## 3. Mandatory rule disposition

Every proposed workflow rule from the retrospective must receive exactly one disposition:

- `PROMOTE_TO_EXISTING_CANONICAL`;
- `CREATE_NEW_CANONICAL_CONTRACT`;
- `REGISTER_TEMPORARY_MANDATORY_ADDENDUM`;
- `OPEN_BOUNDED_REMEDIATION`;
- `MIGRATION_ONLY`;
- `REFERENCE_ONLY`;
- `REJECT_RULE_CHANGE`.

No recurring rule may be left as `TODO`, informal chat memory, PR comment only, or an unregistered patch.

## 4. Canonical promotion checklist

For every recurring rule promoted to canonical status, complete all applicable actions:

1. update the relevant canonical document;
2. register the document or rule in `RUN_GOVERNANCE_INDEX.md` or the canonical manifest;
3. assign authority and applicable stages;
4. update every affected named-stage prompt or addendum;
5. add or update a validator when machine-testable;
6. mark replaced patches or language as `SUPERSEDED`;
7. update upload/package manifests;
8. test that the next Stage 0.0D discovers the rule automatically;
9. confirm no one-time date, count, branch, or run detail entered permanent governance.

## 5. Temporary addendum requirements

A temporary mandatory addendum must include:

- owner;
- creation reason;
- affected stages;
- authority scope;
- expiry or canonical-promotion condition;
- superseded rule scope;
- validator impact;
- manifest registration.

An addendum without an exit condition is invalid.

## 6. Migration disposition

A one-time transition belongs under `docs/migrations/` and must not be promoted into permanent governance merely because it was operationally important.

The retrospective must verify migration status changes from `ACTIVE_MIGRATION` to `COMPLETED_REFERENCE` after its completion conditions are satisfied.

## 7. Required output additions

```json
{
  "document_universe_retrospective": {},
  "coverage_and_completeness_retrospective": {},
  "incremental_operation_retrospective": {},
  "new_rule_proposals": [],
  "rule_disposition_ledger": [],
  "canonical_promotions_completed": [],
  "temporary_addenda_registered": [],
  "open_remediations_created": [],
  "migration_only_findings": [],
  "superseded_patches": [],
  "unregistered_recurring_rule_count": 0,
  "next_run_stage_0_0d_discovery_test": "PASS|REQUIRED"
}
```

If a recurring rule remains unregistered, the retrospective status is:

```text
BLOCKED_RETROSPECTIVE_RULE_PROMOTION_INCOMPLETE
```
