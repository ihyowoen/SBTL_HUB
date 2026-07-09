# SBTL_HUB Prompt Package — Source Diversity IB/Codex Master Rule

Version: `GITHUB_CANONICAL_V1_SOURCE_DIVERSITY_IB_CODEX`  
Generated KST: `2026-07-08T21:18:40.089502+09:00`

## Purpose

This GitHub canonical v1 rule upgrades Source Diversity source-diversity with lessons from the 20260706_130022 run and PR #148:

1. IB-grade / near-IB card tiering.
2. B+ publishable-signal upgrade boundaries.
3. Single-source publish-ready waiver hard gate.
4. Stale `do_not_publish_until` hard gate.
5. Deferred/watchlist retention instead of deletion.
6. Codex review response protocol.
7. PR/production verification against exact PR head.

## Non-negotiables

- Do not overstate weak evidence.
- Do not delete high-value deferred cards merely because evidence is not complete.
- Do not count `fact_sources[]` rows as independent sources.
- Do not leave active blockers on publish-ready cards.
- Do not leave single-source publish-ready cards without a valid waiver.
- Do not use fetch/check dates as visible source dates.
- Do not expand visible claims during metadata-only fixes.

## Applies to

- 14 stage prompts
- 9 governance documents
- downstream card JSON validation scripts

## Required scans before merge

```text
json_parse
total_count
duplicate_id
baseline_url_overlap
single_source_waiver
publish_ready_active_blocker
visible_internal_terms
source_date_rendering
source_grouping
deferred_exclusion
```

## Authoritative status

This document is a GitHub canonical v1 master rule. If it conflicts with an earlier source-diversity integrated rule, GitHub canonical v1 governs only on:

- IB-grade tiering
- Codex response protocol
- single-source waiver metadata
- stale publish blocker metadata
- PR head verification

Source Diversity source-diversity remains authoritative for source grouping, editorial independence, quote/date discipline, and source preservation unless superseded above.
