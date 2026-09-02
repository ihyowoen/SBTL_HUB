# Upload / Governance Change Instructions V4

**Status:** `ACTIVE_CANONICAL`  
**Version:** `UPLOAD_INSTRUCTIONS_V4_20260829`

Recurring governance changes are clean replacements of active canonical documents, named prompts, machine manifests, validators, and tests. Do not create a new permanent override/addendum/overlay.

A governance/runtime-contract PR must not modify `data/cards.full.json` or `public/data/cards.json` unless explicitly a separate governed data mutation.

Validate JSON manifests/schemas, Python/Node syntax, workflow contract tests, V4 architecture check, compatible stage/schema tests, and lean projection. Verify card data is unchanged in governance-only PRs.

Active package source: `RUN_GOVERNANCE_INDEX.md`, lifecycle registry, `PROMPT_MANIFEST.md`, stable machine manifest, upload manifest, complete V4 named prompts, active validators/workflows.

V3 machine schemas/validators may remain temporarily for compatible historical fields; they do not require retired V3 policy files to be active.

Formal card-run and manual direct-add are mutually exclusive within one data PR. Direct add uses latest active schema/validator and never claims formal 0.7C/0.8 completion.