# Workflow Gap Remediation Plan — 2026-07-23

**Classification:** `OPEN_REMEDIATION_WITH_SUPERSEDED_WORKSTREAMS`  
**Current applicability:** only workstreams that remain independently open under the current governance registry. A completed or superseded workstream recorded here must not be re-applied by Stage 0.0D merely because this document remains registered as an open remediation.  
**WG_016 authoritative successor:** `docs/RELATED_LIFECYCLE_CONTRACT.md`  
**Separate legacy Related remediation:** `docs/remediation/RELATED_LEGACY_DANGLING_MANIFEST_20260723.json` and its companion remediation record remain independently open until separately resolved.

This document consolidates the 20260721 run retrospective and PR #206 review findings into implementation workstreams. It is retained because some remediation scope may remain open, but completed or superseded workstreams are historical records only.

## Historical origin and current implementation status

Historical draft origin: `#207 workflow: harden Related lineage and source-audit contracts`.

The original plan included:

- canonical Related lifecycle contract;
- canonical source-audit contract;
- shared URL/domain/editorial-owner utilities and owner registry;
- Related, date/freshness, source-audit recomputation and stage-artifact validators;
- hardened Evidence QC validator with current merge-ID scope;
- idempotent overlay generator for all 11 named prompts;
- unit/regression tests;
- legacy Related dangling manifest and machine-readable `WG_016`.

As of 2026-08-07, the `WG_016` workflow implementation gap is no longer open implementation work. Its active rule source is `docs/RELATED_LIFECYCLE_CONTRACT.md` (`RELATED_LIFECYCLE_V2_20260802`), with the public Related validator and card-run relation/lineage-container validators implemented and stabilized through the subsequent governance/validator PR chain through PR #248.

This closure does **not** close or silently repair legacy data defects. In particular:

- historical dangling Related edges remain a separate bounded remediation under the dedicated legacy dangling manifests;
- legacy cards that require `related_lineage` container initialization remain separate canonical-data migration work;
- neither legacy condition may be interpreted as unfinished implementation of `WG_016`.

Generated prompt overlays and current validators are governed by their present canonical contracts and manifests, not by the historical draft-branch state described in this plan.

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

Historical scope: expanded `WG_003` and `WG_016`.

### Current status

`WG_016` workflow implementation is **COMPLETED / SUPERSEDED** by `docs/RELATED_LIFECYCLE_CONTRACT.md` and the current Related validator chain. Stage 0.0D must not apply the checklist below as unfinished `WG_016` remediation.

The checklist is retained only as historical implementation/audit context:

- make Related pre-pass mandatory after Stage A selection and before Stage B full drafting;
- carry candidate-to-baseline and candidate-to-candidate edges through all stages;
- use one relation enum across Stage A, B, C, 0.4, 0.7, and 0.8;
- require a fresh execution anchor for follow-up cards;
- route same-event duplicates to reinforcement instead of silent deletion;
- resolve candidate spec IDs to production IDs at 0.8;
- run a merged-candidate Related validator.

Any independently open concern associated with older Related gap records must be interpreted through its current active record/contract, not by treating this historical `WG_016` checklist as active implementation work.

The following remain explicitly separate from `WG_016` implementation closure:

- legacy dangling-edge remediation under `docs/remediation/RELATED_LEGACY_DANGLING_MANIFEST_20260723.json` and its companion remediation document;
- legacy `related_lineage` container initialization, if required, as separately reviewed canonical-data migration work.

## Workstream E — Artifact naming and production verification

Covers `WG_012`, `WG_015`.

Actions:

- reserve `pr_candidate_payload` for Prompt 0.8 post-ID output;
- name Prompt 0.7 output `publish_ready_PENDING_MERGE_PREP`;
- support `PASS_WITH_LIMITATIONS` in Prompt 0.9 with separate data/deployment/HTML/interactive/mobile proof;
- never set `production_verified=true` while mandatory interactive or mobile checks remain unexecuted.

## Historical implementation order

The sequence below records the original implementation plan. It does not reactivate any workstream now classified as completed or superseded by current governance.

1. Shared contracts and common validation utilities.
2. Related lifecycle and date/freshness validators.
3. Source-audit recomputation and Evidence QC validator integration.
4. Stage A/B/C and 0.4 output-schema updates.
5. 0.5/0.5R repair routing updates.
6. 0.6/0.7 lineage and source-audit exit contract updates.
7. 0.8 merge-prep and production-ID resolution updates.
8. 0.9 partial-verification state update.
9. Fixture-based tests using the 20260721 run and PR #206 failure cases.

## Historical completion criteria

These criteria remain useful audit context, but current active contracts and validators are authoritative for present runs. A criterion listed here does not by itself make a superseded workstream active.

- no schema-only full revise loop where a bounded metadata repair is valid;
- no publication-date contamination of event dates;
- no stale same-event republication promoted by strong evidence;
- no source counter or diversity drift after augmentation;
- no landing page counted as durable evidence;
- no publish-ready card without allowed diversity status and discovery ledger;
- no dangling, self, duplicate, unexplained, or unresolved Related links;
- no pre-ID payload mistaken for the final replace-all file;
- production verification reports exact tested and untested surfaces.
