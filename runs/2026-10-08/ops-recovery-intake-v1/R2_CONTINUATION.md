# SBTL_HUB operating recovery — R2 continuation (2026-10-08 KST)

> **DRAFT EVIDENCE ONLY — NOT FOR MERGE / NOT PUBLISH-READY.**
> Revolution master/downstream is separately in development. This document does not authorize card updates, related-edge mutation, migration, or deployment.

## Source accounts (four byte-exact archives in the linked Drive folder)
- 2026-09-20, 09-23, 09-26, 09-28 Collector/Refiner/Triage expanded outputs.
- **1,157 expanded source rows → 1,045 unique normalized primary article URLs**, keeping 112 URL repeat rows in provenance.
- URL normalization strips tracking tags only and **preserves identity-bearing query parameters** (`no`, `idxno`, `newsId`, etc.).
- 1,674-card main snapshot `c09c1bc5112216a617903a2d572662342bcd857c` with canonical full blob `d847e2d53bfe27a2b61bac023a82d2009c313356`.
- Against 3,443 distinct canonical URLs: **2 exact primary-URL overlaps** (`2026-09-10_EU_02` Vattenfall and `2026-09-14_GL_01` CATL). **1,043 URL nonmatches are NOT independent new events.**
- Local R2 working ledger accounts for all **1,045** unique source URLs; full semantic event dedup, original/related lineage, and formal triage accounting still pending.

## Explicit follow-up on source REVIEW rows (4/4 intake dispositions)
| Candidate UID | Preliminary disposition | Reason |
|---|---|---|
| `20260923_132732:REVIEW_4` | RETAIN/MERGE → RC26-016 | 2026-09-23 Ministry of Trade press release on Korea's response to proposed EU IAA |
| `20260923_132732:REVIEW_5` | MERGE SOURCE → RC26-016 | Secondary article on the same minister / European Parliament IMCO meeting |
| `20260928_160143:REVIEW_2` | OFF-TOPIC HOLD-DROP | UK RAF-base terrorism arrest reporting; no proven battery/ESS supply-chain event |
| `20260928_160143:REVIEW_4` | OFF-TOPIC HOLD-DROP | National Assembly testimony on delivery-service/Google tax matters; no proven battery/ESS link |

The two proposed drops are **intake-level justifications**, not canonical deletes or completed Stage A DROP resolutions. Ministry evidence: https://m.korea.kr/briefing/pressReleaseView.do?newsId=156783123&pWise=mSub&pWiseSub=C5

## High-materiality triage-filtered records recovered for targeted review
- `20260928_160143:TF_0064`: Media report (MoneyToday, 2026-09-27) on LGES 3rd ESS central-contract tender domestic LFP materials/cell strategy. **Media-only, plan—not legal domestic sourcing mandate, award, or binding supplier order.**
- `20260928_160143:TF_0018`: Shanshan expansion/investment article; reserve until company filing validates size and stage.
- `20260923_132732:TF_0054`: Indonesian nickel-ore trade-volume allegation; reserve for trade-data verification.
- `20260923_132732:TF_0068`: LFP cathode shipment projection; reserve for source-definition/methodology check.
- `20260923_132732:TF_0043` and `TF_0005`: Exact-canonical-URL reinforcements, **not new cards**.

## R2 provisional event additions: RC26-013 through RC26-019 (7)
| ID | Event / primary reporting date | Execution stage, gate |
|---|---|---|
| RC26-013 | **2026-09-28**, Volkswagen–PowerCo–Gotion LFP battery cells and cathode material collaboration, Spain/Slovakia/Morocco | ANNOUNCED JOINT PRODUCTION/JV PLANS; **NOT operating capacity** |
| RC26-014 | **2026-10-08**, LGES–Elevra binding off-take for **240,000 dry metric tonnes of spodumene concentrate over four years**, first deliveries intended from end-2026 | SIGNED CONTRACT; **NOT delivered tonnes** |
| RC26-015 | **2026-10-02**, USTR starts public comments ahead of 2027 USMCA joint review, deadline Jan. 12, 2027 | PUBLIC CONSULTATION; **NOT tariff rule** |
| RC26-016 | **2026-09-23**, Korean trade ministry conveyed views on draft EU Industrial Accelerator Act | DIPLOMATIC POSITION; **NOT final EU law** |
| RC26-017 | **2026-09-27**, media report of LGES local battery inputs and cells for Korea ESS tender | **MEDIA-ONLY planned sourcing**; no official supplier commitment proved |
| RC26-018 | **2026-10-06**, Reuters reports Google–Constellation 3.59 GW US power agreement | ELECTRICITY PPA; **NOT BESS order** |
| RC26-019 | **2026-10-07**, Reuters reports EU–China talks on trade imbalance | NEGOTIATIONS; **NOT announced duty change** |

These bring the **provisional event queue to 19** (12 R1 + 7 R2). All 19 remain **FORMAL STAGES NOT RUN / NOT ACCEPTED FOR RELEASE**.

Primary references:
- VW official: https://www.volkswagen-group.com/en/press-releases/volkswagen-group-powerco-and-gotion-deepen-strategic-partnership-20710
- LG Energy Solution official (English): https://www.lgcorp.com/media/release/30655
- LG Energy Solution official (Korean): https://lg.co.kr/media/release/30651
- USTR official: https://www.ustr.gov/about/policy-offices/press-office/press-releases/2026/october/ustr-seeks-public-comment-2027-joint-review-usmca
- Korean ministry official: https://m.korea.kr/briefing/pressReleaseView.do?newsId=156783123&pWise=mSub&pWiseSub=C5
- LGES supply-localization media: https://www.mt.co.kr/index.php/industry/2026/09/27/2026092713121442441
- Google–Constellation Reuters: https://www.reuters.com/business/energy/google-enters-massive-36-gw-power-deal-with-constellation-energy-2026-10-06/
- EU–China Reuters: https://www.reuters.com/world/china/eu-seeks-cut-trade-deficit-china-talks-with-beijing-2026-10-07/

## Unclosed gap and formal release blockers
- 2026-09-29 to 10-08: targeted live news searches have been performed, **NOT** an authoritative complete native 6-region × 8-lens Collector coverage re-run.
- **48 / 48** region-lens formal 0.0C terminals remain NOT PASS. Some axes have spot-check observations; these do not satisfy terminal search provenance.
- Cross-source same-event grouping, multilingual near-duplicates, canonical historical lineage and Related edges still require full review.
- All 1,045 source URL records require explicit event identity or justified reserve/watch/drop; publication is prohibited until Stage 0.0D/0.0C → A/B/C → 0.4–0.8 and CI pass.
- Draft PR #386 remains intentionally open/unmerged. Do **not** merge this audit PR as a substitute for a **separate** governed, card-only production PR.

**Change safety:** zero canonical writes, zero public lean-card writes, zero experimental Revolution code changes, zero deployments from this checkpoint.
