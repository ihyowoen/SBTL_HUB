# SBTL Backlog Reconciliation — Persistent Checkpoint

Updated: 2026-08-19 11:29 KST

## Resume rule

In a new chat, read `RUN_STATE.json` first. Do **not** start by reconstructing prior chats or searching arbitrary local files.

## Baseline

- GitHub main: `75e98148ae4c7af6234799cdd0852a181b11081b`
- Canonical: `data/cards.full.json`
- Canonical count: 1,373
- Canonical blob: `0cc4e610f9c1ad105761d399be1cd0e316f95128`

## Accepted 21 checkpoint

The current accepted working pool is 21 cards.

- Prompt 0.4: 21/21 `addable_merge_safe`
- Prompt 0.5 R1 repair: 21/21 pass
- Prompt 0.6 R1 rerun: 21/21 pass
- Prompt 0.7: 21/21 pre-validator eligible
- `publish_ready=true`: intentionally 0 until exact repo-runtime validators execute
- Prompt 0.7C: not started
- Prompt 0.8: not started
- Canonical GitHub card mutation: not started

The 0.5/0.6 repair introduced no visible-copy mutation, no fact-source claim/quote mutation, and no new source URL. It repaired current-contract metadata/transport, including exact URL sync on 2 cards / 3 rows and reapproval of 4 bounded single-source exceptions.

Related lifecycle materialization:

- 19 `new_unrelated_event`
- `STD26_A_015` → `2026-07-01_CN_02` as `distinct_follow_up`
- `STD26_A_024` → `2026-07-21_US_01` as `distinct_follow_up`

## Known non-accepted buckets

These counts are preserved as separate historical/accounting buckets and have **not yet** been re-opened in the accepted21 repair lane:

- A059–A081 provenance quarantine: 23
- Stage-B-blocked: 42
- known rejected: 2
- known support-source-only: 1

Full three-run reconciliation is allowed later. Rewind/re-entry is allowed when evidence requires it, but this checkpoint must not be overwritten; create a new revision/lane.

## Exact remaining gate for accepted21

These exact repo-native validators have not yet been represented as executed:

1. `validation_scripts/evidence_qc_v8_check.py`
2. `validation_scripts/related_lifecycle_check.py`
3. `validation_scripts/date_role_freshness_check.py`
4. `validation_scripts/stage_artifact_contract_check.py 0.7`

Current contract-equivalent prechecks are PASS, but Prompt 0.7 final pass / `publish_ready=true` must not be claimed until the exact runtime gate closes.

## Persistent artifact recovery

The accepted21 R1 artifacts are preserved as a compressed bundle split into base64 parts under `artifact_bundle/`. See `ARTIFACT_MANIFEST.json` for SHA256 and reconstruction instructions.

## Next continuation

1. Read `RUN_STATE.json`.
2. Verify current main has not moved; if moved, record drift before promotion.
3. Reconstruct the accepted21 bundle only if the full artifacts are needed.
4. Close exact repo-runtime validator gate when an executable runtime is available.
5. After that, continue to 0.7C and/or start a separately revisioned three-run item-level reconciliation audit without destroying this checkpoint.
