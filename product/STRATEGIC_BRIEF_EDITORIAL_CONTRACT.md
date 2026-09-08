# SBTL Strategic Brief Editorial Publication Contract

**Status:** `ACTIVE_PRODUCT_CONTRACT`  
**Version:** `STRATEGIC_BRIEF_EDITORIAL_CONTRACT_V1_20260908`  
**Scope:** official SBTL monthly Strategic Brief publication only

## 1. Decision

The official monthly SBTL Strategic Brief is an editorial publication, not an automatically generated time-window brief.

The system MUST distinguish two independent concepts:

- **time window** — weekly, rolling 30 days, or a calendar month;
- **publication class** — exploratory automated analysis versus official editorial publication.

A calendar-month or rolling-30-day analysis MAY be generated automatically for research and discovery. It MUST NOT acquire the identity or authority of an official SBTL Strategic Brief merely because its time window is monthly.

## 2. Publication classes

### 2.1 `exploratory_auto`

Automated briefing is allowed for:

- daily flow;
- weekly briefing;
- rolling 30-day analysis;
- calendar-month exploratory analysis;
- region/theme/watch/custom analytical compositions.

These outputs are working intelligence. They may help the editorial team discover clusters, follow-up chains, divergence and emerging themes.

They MUST NOT:

- use an official `VOL.xx` edition identity;
- call themselves `SBTL STRATEGIC BRIEFING` or an official monthly Strategic Brief;
- set `publication_class=official_editorial`;
- be promoted to the official publication library without the editorial publication workflow below.

### 2.2 `official_editorial`

The official monthly Strategic Brief MUST be separately produced and published as an approved static artifact.

It is expected to include a human-led / editor-led deep-dive process such as:

1. lock the source card baseline;
2. review the full monthly card universe and material late additions;
3. inspect missed-event discovery and relevant follow-up chains;
4. separate same-event duplication, reinforcement, update and distinct follow-up;
5. reassess decision/news value across the month rather than by article count;
6. form higher-order structural-signal candidates;
7. test counter-evidence, regional divergence and alternative explanations;
8. validate important numbers, dates, policy stages and causal wording;
9. write the executive diagnosis and structural signals;
10. perform editorial and factual red-team QC;
11. explicitly approve the issue;
12. commit the approved artifact for publication.

The automated axis/LLM brief engine MAY be used as an analyst assistant during steps 2–6. It is not the publisher.

## 3. Canonical official publication channel

Published official issues live in:

`public/data/strategic_briefs.json`

The file MUST validate against:

`schemas/strategic-brief.v1.schema.json`

The automated brief library (`public/data/briefs.json`), browser/localStorage brief archive, and `/api/brief` outputs are NOT authoritative sources for official Strategic Brief publication.

## 4. Required provenance

Every official issue MUST carry enough provenance to reconstruct its editorial baseline:

- edition (`VOL.xx`);
- month;
- revision;
- publication date;
- `publication_class=official_editorial`;
- `publication_mode=manual_editorial`;
- source `main` commit SHA;
- source `data/cards.full.json` blob SHA;
- source month card count;
- source card IDs used by the issue;
- explicit approval metadata;
- structural signals and their supporting card IDs;
- reference list.

The baseline SHA records are publication provenance, not a claim that the card database can never change after publication.

## 5. Drift policy

Late card additions, corrections or backfilled events after publication are a **review signal**, not an automatic rewrite command.

If the source-month universe changes after publication:

- the product MAY show a drift indicator;
- the issue remains the published snapshot until editorial review;
- automated regeneration MUST NOT replace it;
- material changes are handled by an explicit editorial revision (`revision` increment and status `revised`) or by the next issue.

## 6. Reader and UX contract

Target product terminology:

- automated 7-day output: **주간 브리프**;
- automated rolling-30-day output: **30일 빠른 분석**;
- automated calendar-month output: **월별 빠른 분석**;
- official publication: **월간 전략 브리핑 / SBTL STRATEGIC BRIEFING / VOL.xx**.

The official reader MUST prefer the official static artifact and MUST NOT fall back to automatic generation when the official issue is absent.

Absence of an official issue means `편집 중 / 아직 발행되지 않음`, not `generate one automatically`.

## 7. API boundary

`/api/brief` is an exploratory synthesis engine. It may generate analysis over any allowed time window, including a calendar month, but its output is non-official by definition.

Future API/UI work SHOULD carry an explicit `publication_class` or equivalent metadata so this distinction is visible end-to-end. Any request that attempts to mint an official editorial issue directly through the automatic generator must be rejected.

## 8. Red-team rationale

A blanket ban on `period=monthly` was rejected because `monthly` currently encodes both a time window and a product identity. Blocking the period would remove useful 30-day/calendar-month research, region/theme comparisons and custom analytical compositions.

The durable boundary is therefore **authority, not duration**:

`automated monthly-window analysis != official monthly Strategic Brief`

This preserves discovery speed while protecting the quality and editorial identity of the official publication.
