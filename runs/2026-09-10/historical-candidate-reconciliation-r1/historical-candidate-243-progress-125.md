# SBTL Historical Candidate 243 — Reconciliation Progress (125/243)

- Historical derivation: `264 open - 18 later-promoted = 246 - 3 exact canonical = 243`
- Current relock: main `3bb929004ff8b547b86e5f1beab0efb3dac19d62`
- Current canonical: **1,617 cards**, `data/cards.full.json` blob `beb2aa7615b583b4c9c0c269974601a0b26c2684`
- Main movement from the 100/243 checkpoint was UI/shelf-only; the canonical blob is byte-identical, so completed 51–100 adjudications do not reset.
- Materialized/adjudicated: **125 / 243**
- Cumulative: **PROMOTE 50 / KEEP 20 / WATCH 22 / CLOSE 33**
- Remaining: **118**
- These remain partial counts until 243/243 is terminally assigned and the earlier 1–50 cohort receives its final 1,617-card collision relock.

## Batch 101–125 exact membership

`U0343, U0388, U0746, U1950, U1459, U0404, U0542, U0344, U0587, U1176, U1416, U1922, U1926, U1415, U1915, U1411, U1170, U0980, U0520, U0191, U0666, U1121, U0218, U1828, U1627`

- Batch result: **PROMOTE 11 / KEEP 4 / WATCH 2 / CLOSE 8**
- Unassigned within batch: **0**
- Duplicate membership within batch: **0**
- `U1660` is explicitly excluded: it had already reached `confirmed_watchlist_after_review` and is not a member of the 243 open universe. `U0218` is the validated replacement member.

## PROMOTE — 11

- **U0388 — Nickel Industries / ENC maiden battery-grade MHP production** — Nickel Industries' company-announcement ledger confirms maiden MHP production on 29 July and a subsequent maiden nickel-cathode production milestone on 11 August. The prior primary-source/production-stage blocker is resolved; no exact current-canonical collision was found.
- **U0542 — Mandrake Utah Lithium bulk brine production** — Mandrake's ASX announcement list confirms `Bulk Brine-Production Commences at Utah Lithium Project` on 12 August. This is an actual operating-stage milestone rather than a future drilling plan; no exact current-canonical collision was found.
- **U1926 — EEX TBx / Block power futures for renewables and BESS** — EEX officially announced Top-to-Bottom and standardised Block Futures, targeted at renewable/BESS shape risk, for 21 September 2026 subject to regulatory approval. The exchange notice, storage use case and scheduled launch are source-bound. Downstream wording must preserve `will launch / subject to regulatory approval`, not imply the products were already live on the historical article date.
- **U1915 — KDDI-led Re-CIRCLE closed-loop battery recycling validation** — KDDI and the five partner companies officially report that prototype cells using recovered resources from spent lithium-ion batteries achieved performance comparable with virgin-resource prototype cells. This resolves the project-release and test-result blocker; downstream must keep the result at prototype/validation stage.
- **U1411 — Tama Kosan Hachioji No.1 / No.2 grid-storage operating contract** — Tama Kosan and Nippon Steel Engineering signed a contract covering two named Hachioji storage sites, each 1,999kW PCS output, with operation planned around December 2026 and Think EMXS-based market operation. Binding contract, scope and capacity are verified; no exact current-canonical collision was found.
- **U1170 — REXEV–Remix Point low-voltage BESS aggregation alliance** — REXEV confirms a signed 17 August business-alliance agreement built around Remix Point's roughly 1,000-unit low-voltage BESS sales pipeline and joint aggregation/market operation. Preserve the distinction between a sales pipeline and installed/operating assets; future capital tie-up remains only a possibility.
- **U0980 — Shindengen V2X charger CHAdeMO certification / V2H subsidy eligibility** — Shindengen's own product notices confirm CHAdeMO certification and eligibility under the FY2025 supplementary V2H subsidy program. The prior certification/subsidy blocker is resolved; no exact current-canonical collision was found.
- **U0191 — V-Green–HKR Kemayoran EV charging hub** — Vingroup/V-Green confirms a signed development agreement and lease of an 8,747m² HKR site in Kemayoran, Central Jakarta for an integrated EV charging hub. This is a named site/control-of-land execution commitment; downstream must not overstate it as completed construction.
- **U1121 — DeltaX North American BESS manufacturing HQ in Georgia** — Georgia's governor officially announced a **$141m** DeltaX investment and about **250 jobs** in Walton County, beginning with a 100,000-square-foot BESS assembly facility. State/scale/site blockers are resolved; no exact current-canonical collision was found.
- **U1828 — Nanoteam first ESS insulation order for SK On U.S. project** — Nanoteam confirmed its first ESS thermal-runaway insulation-pad order for an SK On U.S. project, with mass-production supply planned from October. This is a distinct commercial follow-up to the existing Nanoteam battery-safety-material lineage, not a duplicate of the earlier China MOU/domestic-EV supply card.
- **U1627 — Gaon Cable / LSCUS KRW200bn U.S. AI data-center busduct contract** — Company material confirms a roughly **KRW200bn** busduct contract for U.S. AI-cloud data-center projects, including a 250MW-class site, with deliveries through 2027. The contract scale and delivery window are source-bound; no exact current-canonical collision was found.

## KEEP_CANDIDATE — 4

- **U0343 — Eramet Centenario-Ratones lithium ramp / expansion option** — Eramet confirms 90% of nameplate output in June and ongoing expansion studies, while the current 24kt-LCE plant targets near-full capacity by end-2026. The historical claim of expansion toward ~150kt/y is not yet cleanly bound in current Eramet primary material with phase, capex/FID and timing. **Repair:** bind the exact Eramet expansion option/tonnage and decision stage before promotion.
- **U1416 — Japan sodium-ion startup partnership / 200MWh three-year target** — The Nikkei headline identifies a potentially material 200MWh scale-up target, but the two company identities and primary partnership/capacity statement remain insufficiently source-bound. **Repair:** recover both company releases or equivalent primary evidence and exact capacity/timing.
- **U1922 — Eurus Energy ReEra VPP storage-service 100MW target** — Eurus primary material confirms ReEra and ongoing VPP/storage demonstrations, but the historical `100MW within FY2026` service-scale target and current contracted capacity are not cleanly confirmed in the source-owner material recovered here. **Repair:** bind company-primary target/current contracted MW and market-operation scope.
- **U0218 — PNT Q2 2026 earnings** — Q2 revenue **KRW117.6bn**, operating profit **KRW3.7bn** and H1 results are reported, with delivery delays/fixed-cost pressures and new-business ramp context. The original earnings-deep-dive blocker remains because backlog, order/mix bridge and segment contribution are not fully reconciled to filing/IR materials. **Repair:** complete the formal earnings deep dive before any promotion.

## DOWNGRADE_WATCH — 2

- **U0587 — Australian Vanadium–Alcoa vanadium-flow battery study** — The parties' 18-month non-binding MOU/scoping study covers a potential roughly 50–80MW / 400–640MWh VFB application at Alcoa's WA refineries, but there is no FID, binding procurement or construction. **Reopen:** completed study plus binding project/FID/award/notice to proceed.
- **U1176 — Terra Charge FY2030 105,000-point charging target** — Terra Charge officially states the 105,000-point FY2030 ambition, but it remains a corporate rollout target rather than a new binding project or procurement event. **Reopen:** material annual installation milestone, binding multi-site award or operating-network step-change.

## CLOSE — 8

- **U0746 — Albemarle La Negra pipeline-leak disruption claim** — The temporary lithium-carbonate-line disruption could not be source-owner verified and no durable production/supply effect was found in later evidence. Close the historical transient claim rather than carry an unresolved outage indefinitely.
- **U1950 — Ivanhoe Santa Cruz US EXIM potential $1.1bn financing** — **Already canonicalized** on current main as the 24 August preliminary-project-letter event, explicitly bounded as potential financing rather than final loan approval.
- **U1459 — Appalachian Power Virginia BESS RFP** — **Already canonicalized** on current main as the 17 August up-to-800MW BESS RFP, with program lineage to Virginia's earlier storage mandate.
- **U0404 — DRC cobalt / uranium investigation reporting** — Same-event evidence/support lineage for **U0060**, already promoted in batch 51–75. Separate active membership would duplicate the DRC uranium-contamination compliance event.
- **U0344 — NioCorp Elk Creek 2026 feasibility study** — **Already canonicalized** on current main as the 10 August feasibility-study update with pre-tax NPV8 of **$4.1bn**.
- **U1415 — Digital Grid low-voltage BESS aggregation launch** — Superseded by the stronger **8 September current-canonical execution follow-up**: Digital Grid's first low-voltage grid BESS began receiving power and the company plans to aggregate 100 Fukushima sites for balancing-market participation.
- **U0520 — KPX Osong next-generation EMS commissioning** — The operative Osong/K-EMS commissioning occurred in mid-June; the August article is later feature/re-coverage rather than a fresh August execution event. Close as stale re-coverage.
- **U0666 — Hanjung NCS 'exit auto parts / all-in ESS' profile** — The August item is a strategy/profile synthesis around an already-running Samsung SDI water-cooled ESS supply and U.S.-expansion path, not a clean new contract, plant start or customer milestone. Close as strategy re-coverage; future U.S. plant/SBB shipment milestones can reopen as new events.

## Governance note

`PROMOTE` in this reconciliation PR means **authorized for ordinary Stage A rematerialization only**. It does not authorize a canonical edit. Each promoted item must still pass the normal Stage A/B/C → 0.4 → 0.5 → 0.6 → 0.7 → 0.7C → 0.8 chain before a separate production/apply PR can modify `data/cards.full.json`.