# SBTL Historical Candidate 243 — Reconciliation Progress (225/243)

- Historical derivation: `264 needs_user_decision - 18 later-promoted unique story IDs = 246 - 3 exact canonical = 243`
- Membership authority for this correction batch: **final 0.1P review-pool promotion artifact**, not the earlier pre-0.1P Stage A disposition.
- Current relock: main `3bb929004ff8b547b86e5f1beab0efb3dac19d62`
- Current canonical: **1,617 cards**, `data/cards.full.json` blob `beb2aa7615b583b4c9c0c269974601a0b26c2684`
- Materialized/adjudicated: **225 / 243**
- Cumulative: **PROMOTE 93 / KEEP 44 / WATCH 32 / CLOSE 56**
- Remaining: **18**
- These remain partial counts until 243/243 is terminally assigned and batches 1–50 receive their final 1,617-card collision relock.

## Membership correction / supersession

Earlier reconciliation passes excluded a set of source-augmentation items because the merged Stage A rescue audit had placed them in `watchlist_only_after_review`. That was not the final governance state. The later **0.1P review-pool promotion artifact** explicitly re-tiered these items to `needs_user_decision_after_review` with `source_augmentation_queue=true`.

Therefore this checkpoint **supersedes the earlier exclusion rationale** for these lineages. In particular, `U0335`, `U1219`, `U1660` and the other re-tiered source-queue items are valid members of the 243 working universe unless a still-later terminal artifact removes them.

## Batch 201–225 exact membership

`U2070, U0499, U0596, U0568, U1084, U1085, U1293, U1270, U1271, U1278, U1774, U1775, U0147, U0909, U0903, U0904, U1512, U1513, U1502, U1495, U1731, U1993, U1516, U0414, U0426`

- Batch result: **PROMOTE 6 / KEEP 7 / WATCH 4 / CLOSE 8**
- Unassigned within batch: **0**
- Duplicate membership within batch: **0**

## PROMOTE — 6

- **U1293 — Xos Hub UL 2202 certification** — Xos source-owner material binds UL 2202 certification to the Xos Hub family, including the 210–630kWh configurations. Current canonical contains a later September operating-throughput milestone for Xos Hub, so this should re-enter only as a distinct earlier compliance/commercialisation milestone with explicit same-product lineage rather than as an unrelated card.
- **U1270 — InVert Graphite / RapidGraphite acquisition and maiden MRE** — The acquisition became unconditional and company/ASX material binds a maiden 32.2Mt @ 8.0% TGC resource (about 2.56Mt contained graphite), creating a concrete acquisition-plus-resource state for a battery/defence graphite supply-chain platform. No current-canonical exact event was found in the 1,617-card baseline search.
- **U1278 — SOLRITE Illinois residential storage/VPP expansion** — SOLRITE launched a live Illinois offering in ComEd and Ameren territories using 60kWh Duracell home batteries, a no-upfront-cost commercial model and VPP/grid-services participation. This is an operative distributed-storage market deployment rather than a product announcement alone.
- **U0147 — David Energy / Wonder batteries across 21 NYC commercial kitchens** — The batteries were actually deployed across 21 commercial-kitchen locations and used for behind-the-meter tariff optimisation. The original deployment blocker is resolved; downstream should preserve the modest site count and avoid extrapolating system-wide scale.
- **U1495 — BeGreen Ingerslev Å BESS lineage, re-anchor to commissioning** — The August optimisation agreement is followed by an August 27 commissioning/inauguration of the co-located 40MWh BESS. Rematerialize on the stronger physical-execution milestone and retain the earlier Danske Commodities optimisation agreement as predecessor/context. Solar figures reported as 48MW versus 65MWp must be normalized before downstream publication; the battery 40MWh anchor is stable.
- **U1731 — Schaeffler–CATL BMS / Integrated PowerBox cooperation** — Schaeffler source-owner material confirms an MoU for joint BMS and X-in-1 Integrated PowerBox development and states that the cooperation builds on an already-secured customer project. Preserve the MoU stage and do not imply a named customer or production volume that is not disclosed.

## KEEP_CANDIDATE — 7

- **U1084 — Blink EnergyConnect charging-site energy-management software** — Product launch is verified, but the original question asks for an operative deployed-site/customer anchor. **Repair:** bind a named live deployment, contracted fleet/site roll-out or quantified grid-capacity outcome.
- **U1271 — NoMIS Power 6.5kV SiC MOSFET customer sampling** — Device performance and U.S. customer sampling are source-bound, but broad commercial production/customer design-in remains prospective. **Repair:** production start, named design win or material shipment scale.
- **U1774 — Vatrer LiFePO4 UL 2271 / UL 1973 certification** — Certification is concrete, but no meaningful deployment/order scale is yet bound. **Repair:** commercial fleet/ESS deployment, material order or distribution scale linked to the certified configurations.
- **U0904 — WETOX D2 ISO 15118-20 / V2X certification** — Certification evidence exists, but the product remains an early third-party adapter/commercialisation effort without material installed-base evidence. **Repair:** commercial shipment, OEM/utility integration or deployed V2X program.
- **U1512 — PHENOGY–HD Advanced Technologies sodium-ion manufacturing cooperation** — Industrial partnership is verified and includes manufacturing of storage systems plus groundwork for a sodium-ion cell JV, but the original site/capacity question remains unresolved. **Repair:** bind manufacturing site, capacity, definitive JV/production agreement or physical production start.
- **U1993 — ZNL Energy–HPB separator supply LOI** — Preferred-supply intent and qualification path are source-bound, but deliveries remain conditional on qualification/industrialisation and a definitive agreement. **Repair:** completed qualification, binding supply contract, committed volume or shipment start.
- **U0414 — Deye 2.5MW-class C&I storage product launch** — Product specifications and launch are credible, but no named customer deployment or shipment scale was established. **Repair:** commercial installation, order book or meaningful shipment/deployment data.

## DOWNGRADE_WATCH — 4

- **U0596 — Tesla proposed 124-stall V4 Supercharger, San Francisco** — This is a permit/proposal-stage charging-site event; construction and commissioning are not established. **Reopen:** permit approval plus construction start, or commissioning.
- **U0568 — Enphase full home-energy platform launch in Italy** — Italy availability of storage, backup, three-phase support and EV charging is verified, but the event remains a product-market rollout without quantified adoption or contracted deployment. **Reopen:** material installation/order volume, VPP/utility integration or contracted storage scale.
- **U1085 — Qnetic flywheel / EPRI validation program** — Entry into an EPRI/SMUD validation program is real, but the candidate is still at independent-test/pilot stage rather than a validated result or commercial deployment. **Reopen:** published independent performance result, utility procurement or commercial field deployment.
- **U0909 — YASA Project Resilience rare-earth-reduction motor R&D** — UK DRIVE35-backed R&D is verified, but it remains a development program. **Reopen:** validated prototype result, OEM adoption, production program or materially binding customer award.

## CLOSE — 8

- **U2070 — USITC crystalline-silicon PV trade-remedy hearing** — Procedural solar-PV trade case without a battery/ESS-specific state change. / `solar_procedural_lane_mismatch`
- **U0499 — Tesla California EV-rebate allocation exhaustion** — Short-lived consumer-incentive demand signal; no durable battery/ESS policy or supply-state change remains to carry as an independent historical card. / `stale_short_lived_demand_signal`
- **U1775 — ABB E-mobility / UK local channel partnership** — Channel/managed-service partnership is verified but lacks a named material deployment, contracted scale or new rule. / `channel_partnership_without_execution_scale`
- **U0903 — Tesla Model Y V2L feature / adapter** — Consumer vehicle feature announcement without a broader grid/storage deployment or structural supply-chain state change. / `routine_product_feature`
- **U1513 — IONITY first urban London charging site** — Real site opening but a routine single-site network expansion below independent structural-card materiality. / `routine_charging_network_progression`
- **U1502 — Fastned UK 40th hub / Liverpool opening** — Real network milestone but routine charging-site progression rather than a new structural battery/ESS event. / `routine_charging_network_progression`
- **U1516 — Translucent Energy 1.2GW South Carolina solar-module plant** — Solar-module manufacturing event with no material battery/storage component. / `solar_manufacturing_lane_mismatch`
- **U0426 — Mercedes VLE China production-preparation claim** — The source-bound execution milestone is actual VLE series production in Vitoria, Spain; the historical China-preparation claim was not separately source-bound into a distinct operative production milestone. / `unbound_preparation_claim_superseded_by_execution`

## Remaining 18 after this checkpoint

Source-queue correction tail: `U0891, U0335, U1219, U1660`

Earnings-deep-dive tail: `U0920, U1518, U0617, U0675, U1139, U0626, U1350, U0503, U0897, U1047, U1655, U0794, U1036, U1746`

## Governance note

`PROMOTE` in this reconciliation PR means **authorized for ordinary Stage A rematerialization only**. It does not authorize a canonical edit. Each promoted item must still pass the normal Stage A/B/C → 0.4 → 0.5 → 0.6 → 0.7 → 0.7C → 0.8 chain before a separate production/apply PR can modify `data/cards.full.json`.
