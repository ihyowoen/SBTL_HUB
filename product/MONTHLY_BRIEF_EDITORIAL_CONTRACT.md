# SBTL Monthly Brief Editorial Publication Contract

**Status:** `ACTIVE_PRODUCT_CONTRACT`  
**Version:** `MONTHLY_BRIEF_EDITORIAL_CONTRACT_V1_20260908`  
**Scope:** official SBTL Monthly Brief publication in SBTL_HUB

## 1. Product boundary

SBTL_HUB has two briefing classes:

- **Quick Analysis** — automated working intelligence;
- **SBTL Monthly Brief** — editor-led, deeply reviewed, approved monthly publication.

The Monthly Brief is not a newsletter, not a newsletter summary, and not a renamed automated 30-day analysis. Newsletter production/distribution is currently outside SBTL_HUB and is not part of this contract.

The Monthly Brief may use automated research, clustering, axis analysis and LLM drafting as editorial aids. Its publication authority comes from deep-dive review, red-team challenge, evidence validation and explicit approval.

## 2. Quick Analysis

Automated analysis is allowed for:

- weekly briefing;
- rolling 30-day analysis;
- calendar-month analysis;
- region/theme/watch/custom analytical compositions.

Target user-facing terms:

- automated 7-day output: **주간 브리프**;
- automated rolling-30-day output: **30일 빠른 분석**;
- automated calendar-month output: **월별 빠른 분석**.

Quick Analysis outputs MUST NOT:

- call themselves **SBTL Monthly Brief** or **월간 브리프**;
- set `publication_class=official_editorial`;
- be promoted to the official Monthly Brief library without the editorial workflow below.

## 3. Official Monthly Brief

The official product name is:

**SBTL Monthly Brief**

The Korean UI term is:

**월간 브리프**

The official identity is month-based (`YYYY-MM`), not newsletter-style `VOL.xx` edition-based identity.

Each issue is expected to be produced through a deep-dive editorial process such as:

1. lock the source card baseline;
2. review the full monthly card universe and material late additions;
3. inspect missed-event discovery and relevant follow-up chains;
4. separate same-event duplication, reinforcement, update and distinct follow-up;
5. reassess decision/news value across the month rather than by article count;
6. form candidate monthly key flows;
7. test counter-evidence, regional divergence and alternative explanations;
8. validate material numbers, dates, policy stages and causal wording;
9. write the key diagnosis, monthly flows and what changed;
10. define the next watchpoints;
11. perform evidence QC, red-team QC, editorial-coherence QC and language/terminology QC;
12. explicitly approve the issue;
13. commit the approved artifact for publication.

Deep Dive describes the production standard, not the public product name.

## 4. Canonical official publication channel

Published official Monthly Brief issues live in:

`public/data/monthly_briefs.json`

The file MUST satisfy:

`schemas/monthly-brief.v1.schema.json`

and the runtime/publication validator in:

`lib/brief/monthlyPublication.js`

The automated brief library (`public/data/briefs.json`), browser/localStorage brief archive, and `/api/brief` outputs are NOT authoritative Monthly Brief sources.

## 5. Official issue shape

An approved issue is organized around:

- key diagnosis (`executive_diagnosis`);
- monthly key flows (`key_flows`);
- what changed (`what_changed`);
- next watchpoints (`watch`, optional);
- governed evidence (`source_card_ids` + `refs`).

The official Monthly Brief schema intentionally does not use newsletter/legacy fields such as:

- `edition` / `VOL.xx`;
- `structural_signals`;
- `regional_signals`;
- newsletter-style issue `conclusion`.

Those concepts may exist in other editorial products outside the HUB, but they are not part of the Monthly Brief contract.

## 6. Provenance and QC

Every official issue MUST carry:

- `product_name=SBTL Monthly Brief`;
- month;
- revision;
- publication date;
- `publication_class=official_editorial`;
- `publication_mode=editorial_curated`;
- source `main` commit SHA;
- source `data/cards.full.json` blob SHA;
- source month card count;
- governed source card IDs;
- key flows and supporting card IDs;
- public reference list;
- explicit approval metadata;
- `qc.evidence_status=PASS`;
- `qc.red_team_status=PASS`;
- `qc.editorial_coherence_status=PASS`;
- `qc.language_terminology_status=PASS`.

The baseline SHAs are publication provenance, not a claim that the card database can never change after publication.

## 7. Publication merge gate

An official Monthly Brief change is publishable only through a reviewed pull request whose current head passes the `validate-monthly-briefs` workflow.

Before merge:

- current-head validation MUST pass;
- normal unit/build checks MUST pass;
- Codex/reviewer feedback MUST be read;
- unresolved inline review threads MUST be zero;
- the reviewed SHA MUST match the head intended for merge.

A stale green check or a clean review on an older head does not authorize a newer head.

Direct writes to `main` are outside this publication contract. GitHub rulesets/branch protection SHOULD require the publication check where repository administration permits it.

## 8. Drift and revision policy

Late additions, corrections or backfilled events after publication are a review signal, not an automatic rewrite command.

If the source-month universe changes:

- the product MAY show a drift indicator;
- the published issue remains the official snapshot until editorial review;
- automatic regeneration MUST NOT replace it;
- a material correction is handled by an explicit revision (`revision` increment and status `revised`) or by the next Monthly Brief.

## 9. Reader and command contract

The official reader loads only `public/data/monthly_briefs.json` and fails closed when the official library is malformed.

If a requested month is absent:

- show `편집 중 / 아직 공식 발행본 없음`;
- do not substitute another month;
- do not fall back to Quick Analysis;
- do not auto-generate an official issue.

Chat/product semantics:

- `월간 브리프 보여줘` → open the latest approved SBTL Monthly Brief;
- `2026년 8월 월간 브리프 보여줘` → open exactly that approved month or show unavailable;
- `월간 브리프 만들어줘` → MUST NOT invoke the automatic brief generator; the product explains that official Monthly Briefs require editorial approval and points to Quick Analysis if immediate analysis is wanted;
- `30일 빠른 분석 만들어줘` → automated exploratory analysis.

## 10. API boundary

`/api/brief` remains an exploratory synthesis engine. It may generate analysis over any allowed time window, including a calendar month, but its output is non-official by definition.

Any request attempting to mint `official_editorial` / `editorial_curated` output directly through `/api/brief` MUST be rejected.

## 11. Durable principle

The durable boundary is authority and product identity, not duration:

`automated monthly-window analysis != SBTL Monthly Brief`

The Monthly Brief is short enough to function as a brief, but its production standard remains deep-dive, evidence-bound and red-teamed.
