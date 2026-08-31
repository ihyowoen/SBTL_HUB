# Legacy Prompt Snapshot Test Policy

**Status:** `REFERENCE_ONLY`  
**Active runner:** `validation_scripts/run_active_workflow_tests.py`

## Why this exists

The repository accumulated many PR/review-specific tests that asserted exact historical prompt prose, headings, override names, and patch-layer strings. Those tests were useful when each PR was being stabilized, but they are not durable semantic governance. Keeping them in the ordinary `unittest discover` gate would force current prompts to preserve superseded V3/override/overlay wording forever.

Workflow V4 therefore separates:

- **active semantic/machine regression tests** — current behavior, validators, schemas, Related/date/source/card-run mechanics, V3 machine compatibility while still supported, and V4 architecture;
- **legacy prompt snapshot tests** — historical exact-prose expectations retained only for audit/history.

## Legacy naming families

The active runner classifies these existing historical families as `LEGACY_PROMPT_SNAPSHOT`:

- `test_review_*.py`
- `test_structural_v3_review_*.py`
- `test_pr233_latest_review_contracts.py`

They remain syntax-compiled by CI and remain in Git history/current tree. They are not ordinary active governance and are not allowed to force retired prompt prose back into V4.

## New-test rule

A new active regression test must use a domain/contract-oriented name and test behavior or current semantic contract. Do not create a new `test_review_*` file for a recurring rule; promote the rule into the clean canonical contract and add a semantic test under a durable domain name.

## Compatibility rule

Retiring a prompt snapshot does not retire the machine behavior it once protected. Where behavior remains needed, it must be covered by active validator/schema tests or a new V4 semantic test. V3 compatibility scripts/tests remain active until that machine compatibility is separately migrated.