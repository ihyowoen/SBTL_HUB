# SBTL_HUB Stage A — Evidence-Bound Identity Decomposition V2 Checkpoint

**Date:** 2026-10-29 KST  
**Priority:** formal Stage A exhaustive adjudication (supersedes Stage 0.6 polishing as the current bottleneck)  
**Overall status:** **HOLD, no new formal Stage A/0.1P promotion**

## Locked baseline and no-loss accounting

| Evidence | Verified current state |
| --- | --- |
| GitHub main | `805c2718d6daf40a219ae94242d9687e33ac3e88` (remote read-only check) |
| Audit branch before this new commit | `0d9cb28d3d0b4cd1dc62a72270a1e5c669d23cc9` |
| Canonical Full | Git blob `07a91714e56be2a8bfad10ab63822f0c5cb3f06e`, 1,676 cards |
| Original Stage A 1,330-row CSV | SHA256 `5e78420916b0c1d70ff56bf928779cd969b94fbb15dd4119c841872997486116` |
| Stage A disposition | 8 `strict_passed_spec`, 636 `candidate_review_pool`, 658 WATCH, 28 reinforcement |
| Source ID-level prior 0.1P | 45 judged; **1,285 still lack individual formal 0.1P decision** |
| Original ID loss | **0**; original 1,330-row CSV, current Full and all previously completed artifacts untouched |

## Actual work in this increment

1. Reused 2026-10-28 13 primary-source-bound case packages and added two newly inspected company-original cases: eRex Sanbu BESS commercial operation (20 October 2026, **1,989.6kW / 8,147kWh**, eRex operator/aggregator) and Hitachi Energy London, Ontario planned **C$479m** transformer insulation/pressboard factory (16 October announcement, **2028 target**, not COD).
2. Mapped **25 original Source IDs** to **15 evidence-bound case packages** with **27 underlying economic-act/asset units**. Cases and units do **not** predetermine article counts or constitute formal `economic_event_cluster_id` assignments.
3. Built create-only `STAGE_A_1330_SOURCE_NO_LOSS_IDENTITY_OVERLAY_V2_20261029.csv`, preserving each original source ID in original order, original pool/status/metadata score, hash of original Related and date-role fields, plus any incremental evidence link. All 1,285 formally unadjudicated items **remain 0.1P pending**: 25 have bounded source-linked research, 1,260 have no evidence-bound case link in this increment; none promoted or rejected.
4. Separated NIO issuer's **two conditional equity subscription agreements**: (a) Geely contributes Yiyi Internet Technology 100% equity and **RMB640m cash** for **conditional 30% NIO Power stake**, with **RMB16bn post-money valuation, not deal cash consideration**; (b) NIO China to subscribe for **conditional 10% Haohan Energy** equity. Optional further RMB640m and preliminary technology collaboration are **not executed acts**.
5. Separated **eight named NYSERDA ESS contracted award assets** within one 23 September award announcement; **950MW is ESS-only**, while 13 renewable awards and the combined 1.7GW / $3.7bn figures have different scope. No award is treated as operating or paid yet.
6. Separated Jupiter Power's **four distinct closed project financings** (**April $258m, May $294m, June $281m, July $536m**). The issuer reports **1,500MW/3,600MWh**, not discovery's 3,800MWh. Rounded monthly figures sum to $1,369m against an approximately $1.4bn announcement, without claiming a September financing close.
7. Kept Global Lithium–Titan signed conditional scheme separate from closing; GridStor White Tank $220m finance close separate from 2027 projected COD; KEPCO KPS Indonesia Hasang signed 40% stake purchase in WATCH pending Stage A pool reassessment; KPX mainland/Jeju spreadsheet errata separate from any award decision.
8. Scanned locked Full's 1,676 card texts with case-keyword searches; lexical matches are **search leads only**, not Related determinations. A limited two-case NIO/NYSERDA semantic prepass identifies distinct earlier event/asset context and outstanding KCE NY 5 / KCE NY 37 project identity proof.

## Validation — correctly bounded

| Check | Result |
| --- | --- |
| Primary 1,330 Source IDs, order, uniqueness vs overlay | **PASS** |
| Old 1,285 pending IDs still present | **PASS** |
| Original pool, assessment, reassessment, score per row | **PASS** (V2) |
| Original date-role and Related string per row | **PASS** SHA256 equality (V2) |
| 25 source-to-package edges and 27 units, no duplicate edge/unit IDs | **PASS** |
| NIO 2, NYSERDA 8, Jupiter 4 and KPX 2 child-unit cardinalities | **PASS** |
| Independent QC script versus generator output | **PASS** |
| Formal `stage_artifact_contract_check.py A` | **NOT EXECUTED** — no complete updated Stage A V4 passing artifact |
| Formal `stage_lineage_contract_check.py stage_a` | **NOT EXECUTED** — full-source provenance and passing artifact not prepared |
| Formal new 0.1P strict promotion | **0 — HOLD** |
| Stage B or Stage 0.6/0.7 advance | **NOT AUTHORIZED BY THIS WORK** |

### Corrected draft handling

The first local generated overlay (unversioned `20261029.csv`) incorrectly read `pool` and `status` instead of the source CSV's `stage_a_pool` and `assessment_status`; its original pool and assessment cells were blank. **It must not be used or uploaded.** The independent validator was hardened to compare all original metadata and date-role/Related hashes before V2 acceptance. Both the V2 independent QC and preservation receipt passed. The v1 local draft remains as a nonauthoritative diagnostic record; it has not been substituted for a source or approved artifact.

## Source-owning primary evidence

- NIO 27 September issuer release: https://ir.nio.com/news-releases/news-release-details/nio-announces-definitive-agreements-strategic-transaction-geely
- NYSERDA 23 September award list: https://www.nyserda.ny.gov/About/Newsroom/2026-Announcements/2026-09-23-NYSERDA-Awards-Eight-Bulk-Energy-Storage-Projects-13-LSR-Projects
- Jupiter 16 September four-financing disclosure: https://jupiterpower.io/jupiter-power-secures-1-4-billion-in-project-financing-for-ten-utility-scale-battery-energy-storage-projects/
- eRex 20 October issuer-authored release: https://prtimes.jp/main/html/rd/p/000000179.000029914.html
- Hitachi Energy 16 October issuer press release: https://www.hitachienergy.com/us/en/news-and-events/press-releases/2026/10/hitachi-energy-invests-479-million-cad-to-bring-critical-transformer-manufacturing-capability-to-canada

## Single next practical bottleneck

**Finish exact source-to-source and Full semantic Related and four V4 judgments for the NIO–Geely conditional dual-equity package and NYSERDA eight-award package, including KCE NY 5/37 asset identities; then, for eligible candidates only, construct a complete Stage A-compatible 0.1P promotion artifact and run both native validators.** Continue through the other 1,260 untouched identities without auto-excluding WATCH or lower-scored items. Do not create a new round or force an article count.

**Repository write scope:** only new files under `runs/2026-10-29/stage-a-identity`. All original source files, Full/Lean, Related, main, PR #386, production, Revolution Masterfile and downstream remain unchanged.
