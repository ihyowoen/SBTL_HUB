# R12 — Current-main full canonical URL crosswalk (2026-10-12)

**STRICTLY READ-ONLY RECONCILIATION / NOT 0.0C PASS / NOT STAGE A / NOT RELEASE AUTHORITY**

## Immutable baseline and input
- GitHub `main` SHA verified at read: `b7847ca9885f6f27ae0566455b0a476ef1059d24`.
- `data/cards.full.json` Git blob: `d0b472e4173e565284616bb7eec0e4b28e1a42b9`; full object parsed, **1674 cards**.
- Collector source-row UID/candidate identity: **1157/1157 preserved**.
- Canonicalized primary Collector URL groups: **1045**. Same original URL across distinct run UIDs is preserved; no deletion and no claim of independent event identity.

## Direct URL comparison against the *complete current full canonical*
- Unique normalized **card.urls** citations: **3448**.
- Unique normalized **fact_sources** citations: **2747**.
- Unique normalized **source_discovery_ledger** citations: **777**.
- Unique normalized **event_fingerprint.primary_source_urls** citations: **39**.
- Distinct normalized URL union across all four scopes: **3502**. This union must not be confused with card.urls-only count or earlier R3's differently scoped URL counter.
- Original Collector URL groups matched exactly in the full canonical URL citation union: **2/1045**.
- Original source UIDs with a direct URL match: **2/1157**.
- Remaining URL groups with *no exact citation URL match*: **1043** — **NOT a count of new events or addable cards**.

### Exact citation URL hits
- Source UID `20260923_132732:TF_0043` → existing card **`2026-09-10_EU_02`**. Scope: card_urls, fact_sources, discovery, fingerprint. Source headline: Vattenfall takes final investment decision on major battery project in Germany
- Source UID `20260923_132732:TF_0005` → existing card **`2026-09-14_GL_01`**. Scope: card_urls, fact_sources, discovery, fingerprint. Source headline: CATL Partners with BME to Advance Battery Pack Manufacturing in Egypt Through Technology Licensing 9/16/2026

## Normalization and hard guards
- Comparison-only scheme http→https, www removal, trailing path slash removal, fragment removal, tracking-only query field drop, remaining query parts sorted.
- Substantive item identifiers (e.g. `idxno`, `newsId`, `no`, article IDs) retained.
- This is URL-key equality against existing *citations*, not event-fingerprint adjudication.
- No direct match **does not prove no canonical same event / related event / update**. Syndication, alternative article sources, changed URLs, multi-event articles, historical follow-ups and translated headlines require separate first-party evidence + event fingerprint.
- The direct URL matched sources are also **not** automatically independent new events.
- No headline-only decision used to issue a terminal event disposition.
- Full/lean data changes **0**; production-card operations **0**; source UID removals **0**.

## Next gate still not satisfied
1. 0.0D formal executable validator with semantic authority conflict QC remains unproven (registry 96/96 and required reads 43/43 are preflight, not final PASS).
2. Event-level 1,045 URL→article→event semantic clustering, existing-card updates and `related[]` traversal/identity still pending.
3. 1,157 original candidates still lack governed Stage 0.0C terminal decisions.
4. Mandatory six-region/fourteen-topic Sep29–Oct12 scoped discovery remains not formally complete.
5. **PR #386 remains Draft and unmerged.** This file is append-only audit only, no masterfile/downstream/production modification.

Supporting original-UID crosswalk: `R12_FULL_CANONICAL_URL_CROSSWALK_1157.csv`.
