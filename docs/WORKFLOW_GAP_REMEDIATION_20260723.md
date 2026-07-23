# Workflow Gap Remediation Plan — 2026-07-23

This document consolidates the 20260721 run retrospective and PR #206 review findings into implementation workstreams.

## Workstream A — Evidence repair routing

Covers `WG_001`, `WG_002`, `WG_005`, `WG_007`, `WG_011`.

Actions:

- add defect classes: `same_url_quote_repair`, `date_only_repair`, `metadata_only_materialization`, `new_source_augmentation`, `visible_claim_change`, `selection_or_staleness_defect`;
- allow bounded same-URL quote repair without consuming a full revise-loop count;
- allow date-only repair only when every other visible/evidence field is byte-stable;
- add stage-exit materialization for verified aliases and lineage fields;
- prohibit schema bridges when underlying PASS evidence is missing or contradictory.

## Workstream B — Date, freshness, and same-event control

Covers `WG_004`, `WG_009`, `WG_010`, `WG_014`.

Actions:

- require publication, event, and representative date roles with direct evidence;
- require earliest-same-event checking at Stage B and 0.5R;
- return stale republications to Stage A/0.4 even when evidence is strong;
- reject landing/listing/generic endpoints as durable article evidence;
- propagate a repaired URL to `urls`, `fact_sources`, resolution metadata, and all derived counters.

## Workstream C — Source-audit single source of truth

Covers `WG_008`, `WG_013`, PR #206 review cycles.

Actions:

- centralize canonical URL, domain, owner, syndication, and landing-page logic;
- derive all source counters only from current `fact_sources`;
- keep domain count separate from independent editorial-owner count;
- require allowed `source_diversity_status` and a source-discovery ledger before publish-ready;
- recompute source metadata after every source add/remove/URL repair and before 0.7/0.8 exit;
- run the repository evidence validator before emitting a replace-all file.

## Workstream D — Related lifecycle

Covers expanded `WG_003` and new `WG_016`.

Actions:

- make Related pre-pass mandatory after Stage A selection and before Stage B full drafting;
- carry candidate-to-baseline and candidate-to-candidate edges through all stages;
- use one relation enum across Stage A, B, C, 0.4, 0.7, and 0.8;
- require a fresh execution anchor for follow-up cards;
- route same-event duplicates to reinforcement instead of silent deletion;
- resolve candidate spec IDs to production IDs at 0.8;
- run a merged-candidate Related validator.

## Workstream E — Artifact naming and production verification

Covers `WG_012`, `WG_015`.

Actions:

- reserve `pr_candidate_payload` for Prompt 0.8 post-ID output;
- name Prompt 0.7 output `publish_ready_PENDING_MERGE_PREP`;
- support `PASS_WITH_LIMITATIONS` in Prompt 0.9 with separate data/deployment/HTML/interactive/mobile proof;
- never set `production_verified=true` while mandatory interactive or mobile checks remain unexecuted.

## Implementation order

1. Shared contracts and common validation utilities.
2. Related lifecycle and date/freshness validators.
3. Source-audit recomputation and Evidence QC validator integration.
4. Stage A/B/C and 0.4 output-schema updates.
5. 0.5/0.5R repair routing updates.
6. 0.6/0.7 lineage and source-audit exit contract updates.
7. 0.8 merge-prep and production-ID resolution updates.
8. 0.9 partial-verification state update.
9. Fixture-based tests using the 20260721 run and PR #206 failure cases.

## Completion criteria

- no schema-only full revise loop where a bounded metadata repair is valid;
- no publication-date contamination of event dates;
- no stale same-event republication promoted by strong evidence;
- no source counter or diversity drift after augmentation;
- no landing page counted as durable evidence;
- no publish-ready card without allowed diversity status and discovery ledger;
- no dangling, self, duplicate, unexplained, or unresolved Related links;
- no pre-ID payload mistaken for the final replace-all file;
- production verification reports exact tested and untested surfaces.
