# Bootstrap Consolidation Migration

**Status:** `ACTIVE_MIGRATION`  
**Migration ID:** `BOOTSTRAP_CONSOLIDATION_20260801`  
**Ordinary-run applicability:** `NONE`

## 0. Purpose

This document governs one bounded transition only: consolidating multiple approved but unmerged editorial runs into a single canonical baseline before ordinary incremental operation begins.

It is not a permanent operating rule.

## 1. Migration-specific scope

The source runs authorized for this one-time consolidation are:

- `2026-07-29`;
- `2026-07-30`;
- `2026-08-01`.

The exact input artifacts, baseline count, candidate count, branch, current main commit SHA, and canonical full blob SHA must be recorded in the execution audit and reverified immediately before application.

No preliminary count or previously downloaded file is authoritative if current `main` differs.

## 2. Why consolidation is exceptional

These runs accumulated before ordinary incremental operation was established. They may therefore be processed together once, with explicit approval, rather than creating multiple overlapping replacement-file PRs.

The consolidation must not become the default operating pattern.

## 3. Required review

The consolidation must re-evaluate across all three source runs and the current canonical full:

- exact duplicates;
- same-event republication;
- existing-card reinforcement;
- existing-card correction;
- material follow-up;
- execution-stage transition;
- correction or reversal;
- distinct new event;
- verified `related_add`;
- source reinforcement.

Simple concatenation is prohibited.

## 4. Required principles

- current main `data/cards.full.json` is the baseline;
- original run inputs, decisions, and audits remain separately identifiable;
- cross-run items are not concatenated without re-evaluation;
- existing related edges are preserved;
- verified new relations may be added;
- card deletion and related removal are outside this migration unless separately approved under remediation;
- the final merged result becomes the next canonical baseline only after production verification.

## 5. Required audit

The migration audit must record:

- verified baseline main commit SHA;
- verified canonical full blob SHA and count;
- source-run artifact references;
- cross-run duplicate and lineage ledger;
- inserts;
- updates;
- related additions;
- zero ordinary deletion assertion;
- zero ordinary related-removal assertion;
- final full and lean hashes;
- PR and production-verification references.

## 6. Completion condition

Set status to `COMPLETED_REFERENCE` only when:

- the consolidation PR is merged;
- the canonical full and lean projection pass validation;
- production verification passes;
- the new baseline SHAs are recorded;
- all source runs retain independent audit references;
- subsequent runs return to ordinary one-run incremental operation.

After completion, this document must not be applied to later ordinary runs.
