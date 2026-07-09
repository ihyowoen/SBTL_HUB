# Prompt Validation Scripts

This directory contains optional mechanical QC helpers for the SBTL_HUB LLM prompt pipeline.

## Scope

These scripts are **not imported by the app runtime** and do not modify `public/data/cards.json`.
They are intended to be run manually or in CI against JSON artifacts produced by the prompt stages.

## Scripts

| Script | Purpose |
|---|---|
| `stage_lineage_contract_check.py` | Checks Stage A/B/C lineage schema contracts. |
| `stage_b_evidence_gate.py` | Checks Stage B evidence-before-draft and no-silent-skip accounting. |
| `evidence_qc_v8_check.py` | Checks Prompt 0.5 evidence/source-diversity outputs. |
| `content_audit_check.py` | Checks Prompt 0.6/0.7 content audit coverage. |

## Fixture smoke test

```bash
bash validation_scripts/run_fixture_smoke_tests.sh
```

The smoke test only verifies representative PASS/FAIL behavior. It is not a substitute for human review or source verification.

## Important rule

These scripts **flag** mechanical inconsistencies. They must never be used to fabricate sources, silently promote cards, or bypass prompt-stage human/assistant review.
