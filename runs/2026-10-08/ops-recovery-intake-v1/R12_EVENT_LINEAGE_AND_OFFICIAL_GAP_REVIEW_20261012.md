# R12 — Canonical event-lineage and post-Sep28 official evidence

**2026-10-12 | READ-ONLY AUDIT / NO 0.0D OR 0.0C FORMAL PASS / NO STAGE A / NO DATA APPLY**

## Basis
- Frozen GitHub `main`: `b7847ca9885f6f27ae0566455b0a476ef1059d24`.
- Full canonical Git blob `d0b472e4173e565284616bb7eec0e4b28e1a42b9` was parsed as **1,674 cards**. All 1,157 original Collector UIDs and 1,045 normalized primary URL observations preserved in R12 exact URL crosswalk.
- Only two Collector primary URLs have exact current canonical citation URL matches. The remaining 1,043 URL identities **are not 1,043 distinct new events**.
- This document adds bounded **semantic-review** leads; event approval, earliest-event adjudication, full Related traversal and terminal Stage 0.0C dispositions remain withheld.

## Collector article → existing canonical review

### AKKU One, Finland — same-stage reinforcement review
- Collector UID: `20260923_132732:EU_2026-09-22_C11`, candidate `SRC26-20260923_132732-0165`.
- Collected story title: *Covenergo and Delta Capacity begin construction on 300MWh AKKU One BESS in Finland*.
- Existing canonical: `2026-09-16_EU_01` titled *AKKU One, 핀란드 125MW/300MWh BESS 착공*.
- Original reporting was published 2026-09-22. The [Delta Capacity company statement](https://www.deltacapacity.com/post/covenergo-and-delta-capacity-partner-on-125-mw---300-mwh-akku-one-bess-project-in-lapinlahti-finlan) is dated September 17, 2026 and describes **the same 125MW/300MWh construction** with expected Q4 2027 commissioning.
- Provisional: **EXISTING_EVENT_REINFORCEMENT_REVIEW**. New article date alone is not a new construction event. No new card or Related mutation.

### GIGA Storage Green Turtle, Belgium — distinct project-stage follow-up review
- Collector UIDs `20260926_120143:EU_2026-09-25_C11` (candidate `SRC26-20260926_120143-0228`) and `20260928_160143:EU_2026-09-25_C08` (candidate `SRC26-20260928_160143-0200`) are the same 2026-09-25 ESS News article URL observed twice; do **not** create two events.
- Existing canonical: `2026-07-10_EU_02`, *벨기에 그린터틀 700MW/2.8GWh, 4.5억유로 금융종결·9월 착공 예정*.
- [GIGA Storage's live project timeline](https://giga-storage.com/en/projects/green-turtle/) gives **July 9 financial close → September 17 construction start → expected end-March 2028 commissioning**. Its [September 17 official announcement](https://giga-storage.com/en/Construction-starts-on-Green-Turtle--Belgium%27s-largest-energy-storage-facility/) confirms 700MW/2,800MWh and 640 Tesla Megapack 3 units.
- Provisional: **DISTINCT_IMPLEMENTATION_STAGE_FOLLOW_UP_REVIEW**, not a newly initiated project on September 25, and not evidence of plant already commissioning. Stage A/B/C and 0.4 must determine whether to update prior card or make a distinct linked follow-up after formal gating.

## Gap after Sep28 — three primary-source leads

### POSCO Future M × Samsung SDI — existing Aug agreement moved to signed contract
- Existing canonical `2026-08-06_KR_03`: **2027–2032, >190,000t LFP supply agreement with formal contract pending**.
- [POSCO Future M official release, October 7](https://www.poscofuturem.com/pr/view.do?num=1051) confirms an **October 6 signed long-term contract**, approximate KRW 6 trillion, and volume **more than double** the August agreement. Do not mix with POSCO Future M's separate September 22 SK On supply contract.
- Candidate `RC26-021` retained from R1–R3, **SAME_PROGRAM_NEXT_EXECUTION_STAGE_UPDATE_OR_FOLLOWUP_REVIEW**. No automatic update.

### LG Energy Solution × Elevra — source-owner contract term boundary
- Existing `RC26-014` provisional event retained; no new ID.
- [LG official Oct 8 release](https://lgcorp.com/media/release/30655) says **240,000 dry metric tonnes over four years**, first deliveries expected later 2026.
- [Elevra Oct 8 SEC Form 6-K](https://www.sec.gov/Archives/edgar/data/1739016/000114036126039136/ef20083536_6k.htm) specifies **a three-year agreement term commencing on first shipment**, with the base 240,000 dmt scheduled across four calendar years: 2026 30,000; 2027 60,000; 2028 60,000; 2029 90,000. Additional **up to 90,000 dmt is optional** subject to mutual agreement.
- Distinguish **contractual three-year term** from **four-calendar-year scheduled deliveries** rather than representing an unresolved factual contradiction. Optional 90,000 dmt is not base guaranteed volume.
- This contract is distinct from canonical `2026-08-21_GL_01` (Elevra–Mangrove): different counterparty and commodity transaction; company identity alone does not create Related lineage.

### EU Critical Raw Materials Act — October 9 new strategic designations
- [European Commission announcement](https://luxembourg.representation.ec.europa.eu/actualites-et-evenements/actualites/commission-selects-46-new-strategic-projects-bolster-eus-supply-critical-raw-materials-2026-10-09_en) selects **46 additional strategic projects in 16 EU member states** on October 9, 2026. The [Commission's selected-projects register](https://single-market-economy.ec.europa.eu/sectors/raw-materials/areas-specific-interest/critical-raw-materials/strategic-projects-under-crma/selected-projects_en) lists the October 9 action.
- Existing canonical `2026-09-08_EU_01` is about 23 projects **requesting urgent financial assistance**, not this fresh designation itself.
- Candidate `R4_DISC_001` retained; **NEW_OFFICIAL_DESIGNATION_REVIEW**, not confirmed operating capacity, government financing transferred, or final investment decisions.

## 0.0D and 0.0C authoritative hold
- 0.0D locked `docs/**`: 96/96 registry classification; required active-read set 43/43 from R11. Production Node/Python executable validator and full semantic-rule conflict audit remain unproven; **no formal PASS issued**.
- 0.0C: original UID preserved 1,157/1,157, URL-only direct comparison completed against current 1,674-card full. Full semantic article→event→canonical/Related closure, 1,157 terminal dispositions, and formal 6 region +14 topic discovery for Sept 29–Oct 12 remain **BLOCKED**.
- Never mark `original_input_accounted=true`, `stage_a_authorized=true`, or publish ready until formal terminal ledgers and preflight are passed.
- Production `cards.full.json` / lean, Revolution master/downstream, live deployment **unchanged**. PR #386 stays Draft/unmerged.
