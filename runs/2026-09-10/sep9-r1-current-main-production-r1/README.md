# Sep 9 R1 Current-Main Governed Run

Status: **IN PROGRESS — PREFLIGHT / RAW INPUT RECONCILIATION**

This branch is the dedicated governed run for the Sep 9 raw input and is intentionally separate from historical carryforward reconciliation PR #369.

## Locked restart point

- source run: `2026-09-09 13:58 KST`
- source file: `final_news_llm_input_newsletter_expanded_20260909_135804.json`
- source schema: `final_news_llm_input_v4_newsletter_expanded`
- raw stories: **393**
- KEEP: **298**
- REVIEW: **3**
- TRIAGE_FILTERED treasure: **92**
- input orphan: **0**
- dropped: **0**
- upstream integrity groups: **7 groups / 25 flagged stories / 0 excluded**

## Current authoritative baseline

- main: `3bb929004ff8b547b86e5f1beab0efb3dac19d62`
- canonical card count: **1,617**
- canonical full Git blob: `beb2aa7615b583b4c9c0c269974601a0b26c2684`

The main move after the Sep 8 production run includes the bounded two-card Monthly Brief canonical remediation plus Monthly Brief publication/UI work. This Sep 9 run therefore starts from the current 1,617-card canonical state and must not reuse the older Sep 8 baseline bindings.

## Required chain

`0.0D → Raw Input Audit → 0.0C → Stage A → 0.1P → Stage B → Stage C → 0.4 → 0.5 → 0.6 → 0.7 → 0.7C → 0.8 → apply/merge → 0.9`

No canonical card mutation is authorized by this checkpoint. Production IDs and card-run operations are created only after the upstream chain passes.

## Scope guard

- Historical carryforward reconciliation remains in draft PR #369 and is paused while this current run is processed.
- Existing Related edges are preserve-by-default. No `related_remove` or delete operation is authorized here.
- Upstream integrity grouping must not silently discard the 25 flagged rows; they remain individually reviewable during event-universe construction.
