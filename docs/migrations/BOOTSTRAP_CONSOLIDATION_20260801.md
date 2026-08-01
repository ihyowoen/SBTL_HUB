# Bootstrap Consolidation Migration

**Status:** `ACTIVE_MIGRATION`  
**Migration ID:** `BOOTSTRAP_CONSOLIDATION_20260801`  
**Ordinary-run applicability:** `NONE`

## 0. Purpose

This document governs one bounded transition only: consolidating multiple approved but unmerged editorial runs into a single canonical baseline before ordinary incremental operation begins.

It is not a permanent operating rule.

## 1. Scope

This migration may contain:

- the current main baseline commit and full blob SHA;
- the explicitly approved unmerged run list;
- the reason a one-time consolidation is required;
- cross-run duplicate, reinforcement, follow-up, correction, and related review;
- preservation of existing related edges;
- the final consolidation PR and production-verification records.

All exact dates, counts, run names, branches, and transition-specific facts belong here or in its audit artifacts, not in permanent governance documents.

## 2. Required principles

- current main `data/cards.full.json` is the baseline;
- original run inputs and audits remain separately identifiable;
- cross-run items are not concatenated without re-evaluation;
- existing related edges are preserved;
- verified new relations may be added;
- card deletion and related removal are outside this migration unless separately approved under remediation;
- the final merged result becomes the next canonical baseline only after production verification.

## 3. Completion condition

Set status to `COMPLETED_REFERENCE` only when:

- the consolidation PR is merged;
- the canonical full and lean projection pass validation;
- production verification passes;
- the new baseline SHAs are recorded;
- all source runs retain independent audit references;
- subsequent runs return to ordinary one-run incremental operation.

After completion, this document must not be applied to later ordinary runs.
