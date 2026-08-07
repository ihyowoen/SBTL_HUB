# Bootstrap Consolidation Migration

**Status:** `ACTIVE_MIGRATION`  
**Migration ID:** `BOOTSTRAP_CONSOLIDATION_20260801`  
**Ordinary-run applicability:** `NONE`  
**Scope revision:** `2026-08-07_PRE_FIRST_APPLICATION_BACKLOG_EXTENSION`

## 0. Purpose

This document governs one bounded transition only: consolidating multiple approved or accumulated but unmerged editorial runs into a single canonical baseline before ordinary incremental operation begins.

It is not a permanent operating rule.

The migration had not reached its completion condition before additional raw/editorial runs accumulated. Before first application, its bounded source-run scope was therefore extended on 2026-08-07 so that the initial canonical transition can close the full pre-incremental backlog once, rather than creating overlapping transitional baselines.

## 1. Migration-specific scope

The source runs authorized for this one-time consolidation are:

- `2026-07-29`;
- `2026-07-30`;
- `2026-08-01`;
- `2026-08-03`;
- `2026-08-05`;
- `2026-08-06`.

The exact input artifacts, historical checkpoint artifacts, baseline count, candidate/event counts, branch, current main commit SHA, and canonical full blob SHA must be recorded in the execution audit and reverified immediately before application.

No preliminary count or previously downloaded file is authoritative if current `main` differs.

The later raw runs may contain overlapping observation windows. Their inclusion authorizes reconciliation, not concatenation. Exact-source, same-article, same-event, reinforcement, update, material-follow-up, and direct-lineage decisions must be re-evaluated across the full bounded scope.

### 1.1 Activation condition

This migration applies only when the run intake explicitly activates:

```text
BOOTSTRAP_CONSOLIDATION_20260801
```

for the bounded 2026-07-29 through 2026-08-06 backlog-recovery transition, records the activation authority, and Stage 0.0D classifies this migration as activated for that run.

Mere presence of this file or its `ACTIVE_MIGRATION` lifecycle status does not activate it.

### 1.2 Historical-state preservation

The consolidation must preserve each source run independently enough to distinguish:

- original raw/input identity;
- prior Stage A/B/C or later checkpoint decisions when they exist;
- frozen/completed decisions;
- blocked or remediation-pending decisions;
- later same-event republication;
- later material follow-up;
- source reinforcement;
- current-canonical reconciliation outcome.

A previously completed or frozen item must not be restarted from Stage A merely because it participates in this consolidation. It resumes from the latest valid checkpoint unless current contracts require bounded revalidation.

## 2. Why consolidation is exceptional

These runs accumulated before the first ordinary governed incremental data operation established a new canonical baseline. They may therefore be processed together once, with explicit approval, rather than creating multiple overlapping transitional or replacement-file PRs.

The scope extension does not create a rolling multi-run rule. It is permitted only because the original migration remains incomplete and no completed transition baseline has yet been established.

The consolidation must not become the default operating pattern.

## 3. Required review

The consolidation must re-evaluate across all authorized source runs and the current canonical full:

- exact duplicates;
- same-article republication or syndication;
- same-event reporting across sources or languages;
- existing-card reinforcement;
- existing-card correction or update;
- material follow-up;
- execution-stage transition;
- policy/regulatory stage transition;
- material data, financial, strategic-behavior, or technology-commercialisation follow-up;
- correction or reversal;
- distinct new event;
- verified `related_add`;
- source reinforcement;
- evidence/date anomalies requiring hold or remediation.

Simple concatenation is prohibited.

## 4. Required principles

- current main `data/cards.full.json` is the baseline;
- original run inputs, decisions, and audits remain separately identifiable;
- cross-run items are not concatenated without re-evaluation;
- frozen or completed historical items remain comparison baselines and preserve their prior valid lineage;
- existing related edges are preserved;
- verified new relations may be added only under the current Related lifecycle contract and relation-container validators;
- card deletion and related removal are outside this migration unless separately approved under remediation;
- legacy cards that lack required relation containers are not silently initialized by an ordinary `related_add`; any required canonical-data initialization remains a separately reviewed migration;
- the final merged result becomes the next canonical baseline only after production verification.

## 5. Required audit

The migration audit must record:

- verified baseline main commit SHA;
- verified canonical full blob SHA and count;
- explicit migration activation authority;
- source-run input and historical checkpoint artifact references;
- per-run preservation and recovery status;
- cross-run duplicate and event-clustering ledger;
- canonical reconciliation ledger;
- inserts;
- updates;
- related additions;
- holds and separately routed remediation candidates;
- zero ordinary deletion assertion;
- zero ordinary related-removal assertion;
- final full and lean hashes;
- PR and production-verification references.

## 6. Completion condition

Set status to `COMPLETED_REFERENCE` only when:

- the bounded consolidation PR is merged;
- the canonical full and lean projection pass validation;
- production verification passes;
- the new baseline SHAs are recorded;
- all source runs retain independent audit references;
- all authorized source runs have an explicit final reconciliation disposition;
- subsequent runs return to ordinary one-run incremental operation.

After completion, this document must not be applied to later ordinary runs.
