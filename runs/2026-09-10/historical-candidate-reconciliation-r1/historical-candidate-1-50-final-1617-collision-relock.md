# Historical Candidate 1–50 — Final 1,617-Card Collision Relock

**Status: PASS**

## Scope

- Historical memberships checked: **50 / 50**
- Original review baseline: main `e19f6c113ccb62906e7fdefaf3bae657c58b5637`
- Original canonical cardinality: **1,599**
- Current relock baseline: main `3bb929004ff8b547b86e5f1beab0efb3dac19d62`
- Current canonical cardinality: **1,617**
- Current canonical blob: `beb2aa7615b583b4c9c0c269974601a0b26c2684`
- Canonical delta: **18 inserts / 0 updates**
- Sep8 production audit base: `e19f6c113ccb62906e7fdefaf3bae657c58b5637`
- Exact/same-event collisions created by the 18-card delta against historical items 1–50: **0**
- Decision supersessions required: **0**

## Why a delta-only relock is sufficient

Both the 1–25 and 26–50 historical checkpoints were adjudicated on the same 1,599-card `e19f6c113…` baseline. The Sep8 production audit explicitly records `expected_before=1599`, `expected_after=1617`, `insert=18`, `update=0`. Therefore the only new collision surface is the 18 inserted canonical cards; unchanged pre-existing canonical content does not need to be re-adjudicated.

## 18-card canonical delta reviewed

The inserted set and its event identities were read from the authoritative Sep8 `id-allocation`, `card-run-audit` and Stage 0.8 lineage artifacts:

1. `2026-09-08_KR_02` — Deoksan Electera North America electrolyte commercial-supply disclosure.
2. `2026-09-08_KR_03` — DRT Gunsan high-efficiency BM mass-production system operation.
3. `2026-08-31_JP_02` — Nishimu/partner battery participation in Japan balancing/adjustment market.
4. `2026-09-08_GL_01` — Samsung Mangoplah BESS formal grid-connection clearance in Australia.
5. `2026-09-07_GL_02` — DRC EGC artisanal cobalt supplier reaches top-five H1 exporter ranking.
6. `2026-09-04_GL_05` — Pakistan procurement/regulatory requirement for at least 10% BESS in the relevant bid structure.
7. `2026-09-07_EU_01` — EUPD European storage outlook, 2026 annual installations forecast at 57GWh.
8. `2026-09-06_CN_03` — CATL strategic cooperation with Taijin New Energy / Shenzhen HKC and partners.
9. `2026-09-07_CN_01` — Chinese independent-storage subproject reaches full-capacity grid connection.
10. `2026-08-31_CN_02` — Xinlun pouch-film hot-process line No.2 production start.
11. `2026-08-26_CN_04` — Mingguan pouch-film H1 filing / revenue growth disclosure.
12. `2026-09-08_EU_01` — EU CRMA strategic-project developers flag liquidity/funding pressure.
13. `2026-09-08_KR_01` — Korean ministerial quantified AI-driven power-demand outlook.
14. `2026-09-08_GL_02` — Blackstone 500MW/2,000MWh BESS EPBC referral/open-assessment milestone.
15. `2026-09-08_US_02` — EPA final-phase Moss Landing post-fire battery cleanup start.
16. `2026-09-08_JP_01` — Digital Grid first low-voltage grid BESS energisation.
17. `2026-09-08_JP_02` — Daiwa House / ENEOS 50MW-class grid-storage EPC business-entry contract milestone.
18. `2026-09-08_US_01` — U.S. DOT pressure on Ford’s CATL licensed-technology dependency; authoritative Stage 0.8 classifies this as a distinct follow-up to canonical `2026-06-30_US_02`.

## Collision result against historical 1–50

### PROMOTE items — no new collision

The 15 PROMOTE lineages from the first 50 remain distinct from the 18-card delta: Minnesota Xcel VPP/flexible interconnection, Japan PSE power-bank safety rule, NSW data-centre framework, Italy Capacity Market battery rating, Lower Wonga grid-connection EPC, Boliden Laver concession appeals, AER NEM battery-market report, SolarPower Europe 2025 storage installations, Czech H1 storage connections, SNE ex-China EV dataset, Hebei storage cleanup, Canada lithium investment review, Suzhou solid-state industrialisation, IEC solid-state standardisation, and Hithium Heze LDES production.

### KEEP items — no new collision

The 10 KEEP lineages remain distinct: Romania battery incentives, Korea critical-mineral/materials policy, Hungary recycling-site law, Brazil storage-auction domestic-content rule, H1 global ESS cell-shipment ranking, China flow-battery additions forecast, Chinese overseas-storage dataset, BNEF Australia arbitrage-spread dataset, LGES–Lopal/Longpan cathode framework, and Gotion Robovan partnership/order claim.

### WATCH items — no new collision

The 9 WATCH lineages remain distinct: Lexus/GS Yuasa battery adoption, CATL ESS integration-equipment order, Austria storage subsidy redesign, Port of Southampton BESS planning application, Ireland EV Flex pilot, Hunan Yuneng HK listing, Lygend A-share IPO, NIO swap-station asset transfer, and Hongqi/BYD Blade nomination.

### CLOSE items — no decision reversal

The 16 CLOSE lineages remain closed. Any newer lineage that motivated a prior CLOSE was already incorporated in the original adjudication logic and does not create a reason to reopen the historical membership. In particular, this relock found no delta card that converts a closed historical item back into an independently active candidate.

## Final gate

- historical 243 membership accounting: **COMPLETE**
- final decision counts: **PROMOTE 95 / KEEP 49 / WATCH 37 / CLOSE 62**
- 1–50 final 1,617-card collision relock: **PASS**
- decision changes from relock: **0**
- canonical mutation in PR #369: **0**

PR #369 may now leave draft status and enter review. `PROMOTE` decisions still require a separate rematerialization/production workflow and do not authorize direct canonical edits.