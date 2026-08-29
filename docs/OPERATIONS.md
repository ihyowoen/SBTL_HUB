# SBTL_HUB Operations V4

**Status:** `ACTIVE_CANONICAL`  
**Version:** `SBTL_OPERATIONS_V4_20260829`

## 1. Start an ordinary new-news run

Use `docs/llm_prompts/v1/00_NEW_RUN_MASTER_PROMPT.md` as the launcher.

1. Read current `main` HEAD.
2. Lock `data/cards.full.json` blob SHA and card count.
3. Verify `public/data/cards.json` is the current deterministic projection.
4. Run 0.0D active-governance preflight.
5. Audit raw input.
6. Run 0.0C coverage discovery.
7. Lock the authoritative expanded event universe.
8. Reconcile the event universe against the complete canonical full before Stage A.
9. Continue through named stages without skipping state transitions.

Unmerged PRs are not baseline.

## 2. 0.0D operating model

0.0D inventories every `docs/**` file but does not deep-read every historical document as if it were active.

Required order:

1. read `RUN_GOVERNANCE_INDEX.md` and lifecycle registry;
2. inventory all `docs/**` paths;
3. classify every path by registered lifecycle or authoritative header;
4. fully read every `ACTIVE_CANONICAL`, `ACTIVE_VALIDATOR_CONTRACT`, applicable `OPEN_REMEDIATION`, and their direct dependency closure;
5. confirm all `SUPERSEDED`, `REFERENCE_ONLY`, archived, or completed-migration files are non-operative;
6. block on unregistered active-looking files or unresolved authority conflicts.

This makes active authority front-loaded and prevents a late-read historical document from changing an already-started stage.

## 3. Raw input audit

Record schema, run tag, generated timestamp, story count, status counts, usable-text/source-packet coverage, date distribution, regions, sources, exact/canonical URL duplicates, headline duplicates, cross-run story-ID collision risk, future dates, stale recollection, publication/event-date confusion, source/body mismatch, and quarantine dispositions.

`KEEP`, `REVIEW`, `TRIAGE_FILTERED`, newsletter flags, and upstream recommendations are not card approval.

## 4. 0.0C coverage discovery

Search the supplied raw, current canonical full, trackers/watchlists/review pools, unresolved holds, official sources, and high-quality independent sources.

Required regions: Korea, North America, China, Japan, Europe, and material global markets.

Required topics include cells/chemistries, materials/components, pouch/pouch-film signals, ESS/BESS, EV/charging, manufacturing/capacity/utilisation, AI/data-centre power and grids, critical minerals, recycling, policy/trade/localisation, competitors/customers, prices/costs/margins, financing, safety, commissioning, and operating validation.

Every discovered item receives a terminal discovery disposition before Stage A.

## 5. Event clustering and reconciliation

Treat articles, events, and cards as different objects.

Classify:

- same article;
- same event / multi-source evidence cluster;
- existing-card reinforcement;
- existing-card update candidate;
- distinct material follow-up;
- new unrelated event;
- correction or reversal;
- hold/review.

Use event fingerprint, not actor/topic similarity.

## 6. Stage A integrated selector

Stage A uses only metadata/source-candidate information available in the expanded universe. It performs no web/body fetch.

For every strict or high-potential review candidate emit:

- credibility gate;
- cardability gate;
- anchor classes;
- decision-news-value score and breakdown;
- publication urgency;
- prior state → new fact → changed judgment chain;
- baseline relation and related pre-pass;
- Stage B evidence targets;
- next confirmation points;
- review-pool disposition when not strict.

No separate news-value override prompt is loaded.

## 7. Stage B / C

Stage B verifies body-level/official evidence, date role, source owner independence, and Related evidence before drafting.

Stage C independently red-teams visible claims and locks `related_lineage` for accepted new cards. Acceptance means fact-safe only.

Revise loops repair bounded defects; selection/staleness defects return upstream.

## 8. 0.4 Addability

Use the exact latest full baseline. Re-run duplicate/follow-up/program-lineage screening and preserve candidate-to-candidate edges.

Allowed conceptual outcomes:

- addable new unrelated event;
- addable distinct follow-up;
- addable program lineage;
- same-event duplicate hold;
- existing reinforcement/update;
- baseline conflict;
- relation-uncertain deferred review.

All surviving new cards remain not publish-ready.

## 9. 0.5–0.7C

0.5 proves source-claim completeness and can send stale/duplicate defects upstream.

0.6 improves density, terminology, and strategic read-through without creating facts or changing lineage.

0.7 creates `publish_ready` only after schema, evidence, date, source, lineage, terminology, and selection-route checks pass.

0.7C independently challenges completeness and exclusions. Formal 0.8 requires `PASS_WITH_DECLARED_RESIDUAL_RISK` and explicit authorization.

## 10. Formal 0.8 merge path

Lock current main and full blob again. Generate declared `insert`, `update`, and `related_add` operations only. Resolve provisional candidate relations to final production IDs. Apply the card-run engine, generate lean from full, run all validators, inspect diff, open one PR, and merge only after required checks/review.

## 11. Manual direct add

Use the current active manual-direct-add schema for already-reviewed bounded changes. A direct add must be one PR and must declare all mutation scope. New direct-added cards carry editorial/news-value attestation. ID correction is an explicit one-to-one migration. Direct add is never reported as a formal full-run pass.

## 12. After merge

Run 0.9 against new main and production. Verify counts, endpoint data, introduced/updated IDs, rendering, Related resolution, deployment, and available UI/mobile surfaces. Record limitations rather than claiming an untested surface passed.

## 13. Failure routing

Route a defect to the earliest responsible stage:

- discovery/coverage → 0.0C;
- selection/news value → A;
- evidence/date/source → B;
- fact safety/lineage lock → C;
- latest-baseline collision → 0.4;
- claim coverage → 0.5;
- copy/terminology → 0.6;
- final publish gate → 0.7;
- completeness → 0.7C;
- mutation/ID resolution → 0.8;
- live deployment → 0.9/1.0.

Never weaken a validator merely to make a known defect green.