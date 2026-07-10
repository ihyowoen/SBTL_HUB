# Prompt Validation Scripts

Contract-driven mechanical QC helpers for the SBTL_HUB LLM prompt pipeline.

## Scope

These scripts are optional validators for JSON artifacts produced by the prompt stages. They are not imported by the app runtime, do not mutate artifacts, and do not modify `public/data/cards.json`.

## Scripts

| Script | Purpose |
|---|---|
| `stage_lineage_contract_check.py` | Checks Stage A/B/C lineage contract conformance. |
| `stage_b_evidence_gate.py` | Checks Stage B evidence-before-draft and no-silent-skip accounting. |
| `evidence_qc_v8_check.py` | Checks Prompt 0.5 evidence/source-diversity artifacts. |
| `content_audit_check.py` | Checks Prompt 0.6/0.7 per-card content audit coverage. |
| `run_fixture_smoke_tests.sh` | Runs representative PASS/FAIL fixtures. |

## Run

```bash
bash validation_scripts/run_fixture_smoke_tests.sh
```

## Design principles

- Contract constants are declared at the top of each script.
- Presence-only fields are separated from non-empty fields.
- PASS, HOLD, and FAIL bucket semantics are intentionally different.
- Root-level and per-package Stage B lineage shapes are both supported.
- Source diversity is evaluated by independent owner count first, domain/host only as fallback.
- These scripts flag mechanical inconsistencies only. They must never fabricate sources, silently promote cards, or replace human/assistant review.
