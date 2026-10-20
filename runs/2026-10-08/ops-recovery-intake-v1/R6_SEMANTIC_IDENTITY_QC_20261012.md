# R6 operating recovery — governance header / URL-identity audit (2026-10-12 KST)

> **AUDIT-ONLY / PR #386 DRAFT / NO MERGE / NOT PUBLISH-READY.** This addendum changes no canonical cards, public lean cards, validators, Revolution master/downstream, deployment, or accepted Stage states.

## 1. Exact production baseline (observational)
- GitHub `main`: `b7847ca9885f6f27ae0566455b0a476ef1059d24` (re-lock before any operational act).
- `data/cards.full.json` blob: `d0b472e4173e565284616bb7eec0e4b28e1a42b9`, count 1,674 according to R4.
- `public/data/cards.json` blob: `c39eac64afde20ff0ccacd920e12abbdab1b3d02`.
- R4/R5 independent Collector checkpoint: four ZIPs, 1,157 expanded source rows (919 KEEP, 234 TRIAGE_FILTERED, 4 REVIEW), 1,045 identity-preserving normalized primary article URLs.

## 2. 0.0D remaining audit gap narrowed: 53 nonactive documents read
- The existing R4 read receipt covered all 43 active/dependency files and a 96/96 lifecycle registry inventory. R6 newly fetched **all 53/53** registry-classified `superseded` or `reference_only` files at the locked main SHA, recorded the exact per-file blob SHA and observed status in [R6_REFERENCE_HEADER_AUDIT_20261012.csv](./R6_REFERENCE_HEADER_AUDIT_20261012.csv).
- **Direct contradictory active lifecycle headers: 0/53**. Observed header/status classes: `SUPERSEDED` 16; `SUPERSEDED_REFERENCE` 2; `REFERENCE_ONLY` 1; other artifact-specific status 2; **no explicit lifecycle header/status 32**. A missing explicit header is not by itself evidence of current active authority; these 32 have registry classification and still deserve provenance-aware interpretation.
- **Do not claim formal 0.0D PASS**: machine production validator and full active-rule semantic-conflict authorization have not been reproduced. `stage_0_0c_authorized=false`.

## 3. 0.0C source identity diagnostics (R6 deterministic re-run)
The R6 offline evidence packet, computed from the preserved R4 source UID ledger SHA256 `6fafdd2470cf33c6c58dcda6b7a5cd065faaef6ed5ece2c01302e504de619111`, contains an exact 1,157 UID → 1,045 URL group mapping, per-group risk flags, and a reproducible stdlib Python script. Re-run produced byte-identical 8 generated audit files.

| Measure | R6 result | Meaning |
| --- | ---: | --- |
| Original input UIDs / preserved rows | 1,157 | 0 silent row loss |
| Identity-preserving normalized URLs | 1,045 | article-URL groups, NOT independent events |
| Repeated URL groups / member observations | 110 / 222 | 112 redundant URL observations |
| Same URL with KEEP vs TRIAGE_FILTERED across runs | **25 groups / 50 UIDs** | MUST review: DO NOT auto DROP from a later filtered record |
| Same URL with simple-normalized headline changes | 4 groups | title mutation ≠ proved new event |
| Same URL, date variations | 3 groups | date-role conflict possible |
| Known non-static category/index URL repeated | 1 group | OFweek `/CAT-36005-shengchanjianceshebei.html` 4 captures / 3 dates |
| Equal normalized headline across different URLs | 4 groups / 8 representative URLs | possible syndication; no auto merge |

The 25 mixed triage groups include LGES–B2U (both source UIDs preserved). `2026-08-06_KR_03` and October POSCO–Samsung follow-up `RC26-021` remain a source-specific lineage question. The Sept 22 POSCO–SK On contract is a separate counterparty. **R3's 22 provisional RC IDs are unchanged.**

## 4. New external source spotcheck and existing discovery reinforcement
- **`R6_DISC_001` (new provisional, not RC-numbered)**: NESR–Saudi Aramco signed an agreement **Oct 8** for the Aramco 2027 Lithium Demonstration Project. NESR targets **2,000 tpa battery-grade lithium carbonate**, possible contract value ~USD **$200M over up to five years**; start/commissioning is **planned for late 2027**, not operating production. [Company first-party release](https://investors.nesr.com/news/nesr-and-aramco-sign-agreement-to-deliver-the-regions-first-direct-lithium-extraction-project/c433042b-b362-4d5d-be4f-b50df439085e). Canonical/Related match remains unresolved.
- **`R4_DISC_001`**: strengthen the existing Oct 9 European Commission CRMA designation with official sector breakdown of **46 projects across 16 Member States** (8 extraction, 11 processing, 19 recycling, 8 integrated). No new candidate ID; designation is not plant commissioning or unconditional funding. [European Commission first party](https://luxembourg.representation.ec.europa.eu/actualites-et-evenements/actualites/commission-selects-46-new-strategic-projects-bolster-eus-supply-critical-raw-materials-2026-10-09_en).

## 5. Formal next gate / no unauthorized transition
- 0.0D **BLOCKED** until semantic authority check and executable run-document validation.
- 0.0C **BLOCKED** until all 1,157 UIDs → articles → events → canonical full/Related have *governed* terminal outcome and 6 region + 14 topic axes have evidence-backed terminal searched/blocked provenance. Preserved input != accepted terminal disposition.
- Stage A/B/C and 0.4 → 0.8 **not run** for recovery. New discoveries are review candidates only. Separate governed card PR after gates, not this audit-only draft.
