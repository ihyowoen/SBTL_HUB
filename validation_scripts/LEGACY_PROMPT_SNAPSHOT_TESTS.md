# Retired Prompt Snapshot Test Policy

**Status:** `REFERENCE_ONLY`  
**Active runner:** `validation_scripts/run_active_workflow_tests.py`  
**Exact retirement registry:** `validation_scripts/retired_prompt_snapshot_tests.json`

## Why this exists

The repository accumulated PR/review-specific tests that sometimes assert exact historical prompt prose, headings, override names, and patch-layer strings. Some of those tests are genuine historical snapshots, but review-numbered files also contain durable machine-validator regressions. A filename therefore cannot determine whether a test is active or retired.

Workflow V4 separates:

- **active semantic/machine regression tests** — current behavior, validators, schemas, Related/date/source/card-run mechanics, supported V3 machine compatibility, and V4 architecture;
- **retired prompt snapshot test methods** — exact historical prose assertions retained only for audit/history.

## Exact-identity rule

There are **no broad legacy filename exclusions**. In particular, `test_review_*.py`, `test_structural_v3_review_*.py`, and PR-numbered modules are imported and discovered like every other test module.

A test may be retired only when its exact stable identity appears in `retired_prompt_snapshot_tests.json`:

```text
validation_scripts/tests/<file>.py::<TestCaseClass>::<test_method>
```

Every registry entry requires a non-empty audit reason describing the superseded prompt/prose contract. The active runner imports every test module before retirement filtering, treats any import error as fatal, rejects stale registry identities that no longer resolve in the current tree, and reports the exact active/retired counts.

A whole file or filename family must never be retired by wildcard, prefix, suffix, review number, or naming convention.

## Classification rule

A method is eligible for retirement only when its assertion is limited to superseded historical prompt prose/heading/overlay/addendum text and the machine behavior it once protected is either no longer operative or is covered by an active semantic/machine regression.

Tests that execute or inspect current validators, schemas, CLIs, stage routing, Related lifecycle, date/source/evidence contracts, card-run mechanics, or current compatibility entrypoints remain active even when their filename contains a review or PR number. If such a test uses a retired prompt API but still protects required behavior, migrate it to the supported compatibility/current API instead of retiring it.

## New-test rule

A new active regression test should use a domain/contract-oriented name and test behavior or the current semantic contract. Do not create a new review-numbered snapshot for a recurring rule; promote the rule into the clean canonical contract and cover it with a durable semantic test.

## Compatibility rule

Retiring a prompt snapshot does not retire machine behavior. Supported V3 machine compatibility remains active until separately migrated, and current V4 machine behavior must always have an active test path.
