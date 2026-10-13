# R13 — Current canonical Full URL reconciliation & 10/13 gap spotchecks
**2026-10-13 KST | READ-ONLY AUDIT | NOT 0.0D PASS | NOT STAGE A | NO CARD WRITES**

## Locked baseline and full-card read
- GitHub main: `b7847ca9885f6f27ae0566455b0a476ef1059d24`
- Full blob: `d0b472e4173e565284616bb7eec0e4b28e1a42b9`; **1,674** cards read in full through authenticated GitHub Blob API.
- Lean blob: `c39eac64afde20ff0ccacd920e12abbdab1b3d02` (no writes).
- Original Collector source UID **1,157/1,157**, canonicalized primary URLs **1,045**, upstream KEEP **919** / TRIAGE_FILTERED **234** / REVIEW **4**. Raw R11 source bodies/candidate ledger remain outside public GitHub.

## Canonical exact primary-source URL overlap
Exactly **2/1,045** distinct Collector primary URLs match an existing card's cited source URL:
1. `20260923_132732:TF_0043` → `2026-09-10_EU_02` (Vattenfall Brunsbüttel BESS final investment decision).
2. `20260923_132732:TF_0005` → `2026-09-14_GL_01` (CATL–BME Egypt technology/licensing).

**1,043 URLs without an exact match are NOT 1,043 independent news events.** Row-level no-exact-match count is **1,155**. Original UID disposition is still UNASSIGNED. Same-event syndication, event identity, date roles, complete Related and publishability require formal editorial review.

Existing `related[]` graph has **14 dangling edges from 13 source cards**, a pre-existing legacy remediation inventory, not a new R13 defect. These are not repaired by this intake PR. A lexical crosscheck showed hard negatives: OFweek article IDs, different SNE report IDs, Commission speech vs press release; path/template similarity is insufficient. Spain pumped-hydro May vs Sep articles are a program-follow-up review, not an automatic same event.

## 10/09–10/13 official-source exploratory additions (NOT authorized publication)
- `R13_DISC_001` EnergyX–Trafigura 10/12 **binding** 10-year/100,000t lithium offtake; Chile/Texas production targets **2028/2029**, not deliveries now. Existing Black Giant equity card `2026-07-06_GL_05` potentially relevant predecessor. Two first-party sources: [Trafigura](https://www.trafigura.com/news-and-insights/press-releases/2026/trafigura-signs-10-year-lithium-offtake-agreement-with-energyx/) and [EnergyX](https://energyx.com/press-release/energyx-signs-10-year-lithium-deal-with-trafigura/); EnergyX header/dateline date-role discrepancy retained (Oct12/Oct13).
- `R13_DISC_002` CATL–SERES 10/10 signed long-term strategic cooperation; 10–12 GWh phase 2 **planned**, not live production. [CATL first-party](https://www.catl.com/en/news/7014.html).
- `R13_DISC_003` CATL 10/12 GBA battery passport **voluntary pilot** results; not EU statutory compliance proof. [CATL](https://www.catl.com/en/news/7016.html).
- `R4_DISC_001` EU CRMA 10/09 46 second-round strategic-project designations: **reuse R4 ID**, designation not subsidy disbursement or start of operations. [European Commission](https://single-market-economy.ec.europa.eu/sectors/raw-materials/areas-specific-interest/critical-raw-materials/strategic-projects-under-crma/selected-projects_en).
- `R13_DISC_004` Benchmark 10/09 **CAM** Q3 prices, distinct from R5 battery **cell** price review. [Benchmark](https://source.benchmarkminerals.com/article/bearish-battery-feedstock-markets-weigh-on-cathode-prices-cathode-q3-2026-price-review).
- `R13_DISC_005` US DOE Oct9 Puerto Rico Amanecer final EA/FONSI; not a loan guarantee or BESS commissioning. [DOE](https://www.energy.gov/nepa/articles/doeea-2300-final-environmental-assessment-and-finding-no-significant-impact-october).

R13 partial bookkeeping = 1,157 original source UID + 6 above candidate identities = **1,163 rows**; this **does not incorporate all prior R1–R5 event-review queues** and cannot be called an authoritative completed expanded universe. All six are subject to later evidence/novelty/Related review.

## Gate decisions (fail-closed)
- 0.0D: Registry/tree 96/96; active read closure 43/43 from R11; Stage A embedded selector and Related prepass verified. **Exact production executable machine gate was NOT run**, independent semantic-conflict certification incomplete; therefore **BLOCKED**, not PASS.
- 0.0C: Exact machine coverage keys 6 regions +14 topics represented but all **BLOCKED** (full 9/29–10/13 discovery not complete, no 0.0D PASS). Original-input event-terminal ledger incomplete; `original_input_accounted=false`; `stage_a_authorized=false`.
- Stage A/B/C, 0.4–0.8, separate card PR, merge and Vercel 0.9 remain NOT AUTHORIZED.

**No canonical/lean edits; no Related edits; no Source UID deletion; no Revolution master/downstream changes; PR #386 remains DRAFT/unmerged.** Detailed 1,157 UID crosswalk, 14 legacy references, 6 discovery records, blocked 20-axis matrix and reproducibility script are in the separate audit ZIP, not published as scraped article bodies in this repository.
