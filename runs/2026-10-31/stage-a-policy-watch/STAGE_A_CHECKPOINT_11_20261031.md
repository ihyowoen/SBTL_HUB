# SBTL_HUB — Stage A 0.1P policy/market/WATCH rescue batch #11

**KST:** 2026-10-31  
**Status:** bounded individual-four-judgment input QC PASS; **native Stage A HOLD**. No Stage B eligibility inferred.

## Baseline and scope

- GitHub `main` locked: `805c2718d6daf40a219ae94242d9687e33ac3e88`; Full blob: `07a91714e56be2a8bfad10ab63822f0c5cb3f06e`, 1,676 cards.
- Original Stage A: **1,330 unique Source IDs**, original CSV SHA256 `5e78420916b0c1d70ff56bf928779cd969b94fbb15dd4119c841872997486116`.
- Original formal individual 0.1P results: **45**; remaining **1,285**; original strict-pass **8**; new strict-pass **0**.
- Previous bounded four-judgment inputs: **16 Source IDs**, checksum `1faf426f340e8c8c2bd2570c6d84697cd062397e25bee478c2e139b2aba2cb1e`.
- This run: **54 additional distinct original Source IDs**, of which **49 candidate-review and 5 WATCH**, provisionally linked to **13 source-to-case groups** and **23 subevent definitions**. Previous 16 + this 54 = **70 pre-native individual judgment inputs**; **not 70 approved Source IDs or 23 new cards**.
- Source IDs and their original row order, metadata scores, pool classification, 45 original individual outcomes, and original strict list have not been overwritten. The 1,330-row V5 overlay only adds new `oct31_policy_watch_pre_native_case_ref_NOT_FORMAL` references to 54 rows.

## High-signal event decisions and errors prevented

| Topic | Primary/case-level verified facts | Decision and scope control |
|---|---|---|
| Korea resource-security plans (20 Source IDs) | Sept 23 ministry: four agenda items adopted; strategic minerals 38→51, reserve product list 24→29, maximum targeted days 180→365 | One Sept government decision with four instrument subunits. Goals are not completed stockpile deliveries. Prior Full April law amendment and July finance coordination are different events |
| Korea ESS central auction (10) | Sept 22 MCEE and KPX mainland announcement: 1,180MW total, 1,100MW mainland + 80MW Jeju; Jeju adds optional 25-year 2-cycle scheme | Procurement **announcement**, not award, contract or COD. Sept 20 preview, mixed-topic brief and Sept 28 registration update carry separate date roles |
| EVE–Fluence (5) | Sept 18 EVE market filing and Sept 24 buyer confirmation: 2027 16GWh committed + 2028–31 190GWh **reserved** | **206GWh not 206GWh executed PO or deliveries**; subsequent order specifications, quantity and price are pending; original Full contains different Fluence FY26 outlook |
| esVolta/Quintrace/Google (3) | Sept 17 pilot on hourly granular clean-energy certificates using batteries | Pilot architecture, not accounting-rule approval or universally realized ESS certificate revenues |
| UK Ofgem CMP470 (2) | Sept 17 consultation on battery queue commitment fee; ~90GW operating/queued vs ~29GW projected need | Formal **consultation**, not active fee. Ofgem consultation now closed and awaiting decision. Stage-1 policy-score ceiling applied |
| Panasonic Kadoma (2) | Sept 16 new battery R&D facility launched | R&D/prototyping capacity, not a new cell mass-production start |
| Flow Power Bennetts Creek (1) | Sept 18 milestone celebration for 100MW/223MWh phase 1; 300MW/1.2GWh phase 2 is proposed | Actual initial construction preceded event; 1.2GWh phase two unapproved. Routine progression novelty ceiling |
| Canada CITT solar import remedies (1) | Sept tribunal order rescission ending anti-dumping and countervailing collection on Chinese PV modules/laminates | Actual solar trade remedy event, **not EV battery import duty elimination** |
| LG Electronics AI chillers (4) | Sept 20 product launch; issuer Sept 21 release explains pre-cooling energy saving comparison | Producer claim of ~30% vs water-based pre-cooling under cited conditions, **not measured whole-data-centre power reduction**. Indirect battery-industry relevance |
| China TOPCon cell prices (1) | OPIS weekly dataset Sep 15 via publisher: M10 $0.0469/W (-2.29% WoW); 210R $0.0458/W (-1.72%) | PV supply/price datapoint; not ESS-cell price, no invented volume effect |
| US ESS multi-event roundup (2) | Eos $87m DOE third draw; FlexGen/Lightshift 16-site program; Georgia Power Robins 128MW COD | Eos exact same event in Full `2026-09-10_US_01`, FlexGen exact same event in Full `2026-09-16_US_02`. **Georgia Robins COD distinct candidate**, not auto 512MWh nameplate |
| Factorial/Mitsui (2) | Sept 17/18 sulfide-electrolyte manufacturing JDA | JDA, not proven commercial cell output; different from July Factorial aerospace battery order |
| Japan Hirasol (1) | Sept 16 Fukushima Izumizaki battery 1,900kW rated / 3,800kW permitted balancing reserve after preassessment | Operational market-qualification innovation; not doubled physical inverter output or proven doubled income |

## Primary source anchors inspected

- Korea: [Resource-security ministry](https://www.motir.go.kr/kor/article/ATCL3f49a5a8c/172235/view), [MCEE ESS announcement](https://www.mcee.go.kr/home/web/board/read.do?boardId=1893270&boardMasterId=939&menuId=10598), [KPX mainland tender](https://www.kpx.or.kr/board.es?act=view&bid=0042&list_no=78164&mid=a10501010000).
- China/US: [EVE SEC-equivalent company filing](https://static.cninfo.com.cn/finalpage/2026-09-18/1225571033.PDF), [Fluence buyer release](https://fluenceenergy.gcs-web.com/news-releases/news-release-details/fluence-secures-long-term-battery-supply-through-multiyear), [Georgia Power Robins COD](https://www.georgiapower.com/news-hub/press-releases/georgia-power-robins-battery-storage-achieves-commercial-operation.html), [Eos DOE draw](https://eosenergyenterprises.gcs-web.com/news-releases/news-release-details/eos-energy-enterprises-receives-87-million-advance-under-us).
- EU/other: [Ofgem CMP470 consultation](https://www.ofgem.gov.uk/consultation/connection-and-use-system-code-cusc-cmp470-introducing-oversubscribed-technologies-commitment-fee-otcf), [Canadian tribunal](https://www.canada.ca/en/international-trade-tribunal/news/2026/09/tribunal-terminates-expiry-reviewphotovoltaic-modules-and-laminates-from-china.html), [Panasonic](https://news.panasonic.com/global/press/en260916-3), [Flow Power](https://flowpower.com.au/flow-power-celebrates-bennetts-creek-battery-construction-milestone/), [LG official newsroom](https://www.lge.co.kr/story/newsroom/236187), [Hirasol](https://prtimes.jp/main/html/rd/p/000000027.000085634.html), [Factorial](https://factorialenergy.gcs-web.com/news-releases/news-release-details/mitsui-kinzoku-partners-factorial-scale-all-solid-state-battery), [esVolta](https://www.esvolta.com/post/battery-storage-shift-pilot-demonstrates-how-hourly-renewable-certificates-can-power-the-next-phase), [OPIS weekly data](https://pv-magazine-usa.com/2026/09/18/china-topcon-solar-cell-prices-fall-for-third-week-as-export-buying-fades-and-wafer-costs-ease/).

## Independent validation and boundary

- Identity and order **1,330/1,330** identical; changed original source fields **0**; newly annotated rows **54**. The 54 did not overlap the prior 16 individual inputs, and all 54 had no additional case evidence in the previous V4 overlay.
- Score eight-component sums, 0–100 limits, technology-evidence score ceilings, policy-stage ceilings and novelty ceilings verified for all 54; source identity matches original URLs and titles.
- `related_prepass` supplied but **HOLD** (not the strict PASS); all 54 have `native_0_1P_approved=false`. A mixed-source article may retain multiple event units rather than collapsing them into one. All separate new case statuses remain provisional.
- The generator and independent verifier reproduce the same output bytes in a new clean temporary directory; deliberate Source ID tampering was rejected.
- **Native `stage_artifact_contract_check.py A` and `stage_lineage_contract_check.py stage_a` have not been executed on a completed ordinary Stage A artifact in this run.** The previous 45-ID run recorded BLOCKED on the incomplete top-level envelope. This run must not be marked as native PASS or considered a new downstream queue.
- Event-level first-party original materials were inspected, **not the full body of every secondary news article**. All material first-party/actual execution and all current Full lineage gaps are carried explicitly. No arbitrary news-count quota, no automatic score-26 reject.

## Exact output checksums

- `STAGE_A_0_1P_POLICY_MARKET_WATCH_RESCUE_CASES_20261031.json`: `8167bff64e8f0993719df2e8144ce3bdb8c3c4aa2bdd2c15458c27ec47946fb8`.
- `STAGE_A_1330_SOURCE_INTEGRATED_EVIDENCE_OVERLAY_V5_POLICY_WATCH_20261031.json`: `f9bf41c00f6761cdc61150d6fbdde51a3b525d71dbd60d1d809c2853d318d4f5`.
- `STAGE_A_0_1P_POLICY_WATCH_INDEPENDENT_QC_20261031.json`: `9566f0c10afa2c18fc64efd06dfaeccecc7b630f2fbe790115b908fd56af0693`.

**Next single bottleneck:** construct a complete ordinary native 0.1P Stage A artifact with reconciled Source IDs and all unreviewed source-by-source dispositions; run the two exact active contract/lineage validators and only then release eligible events to Stage B. Stage A global HOLD remains in force.
