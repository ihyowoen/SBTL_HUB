# Stage A Checkpoint #13 — formal 0.1P duplicate disposition

Date: 2026-11-01 UTC  
Authority: `docs/llm_prompts/v1/14_PROMPT_0_1P_Review_Pool_Promotion.md` and `01_PROMPT_0_1_Stage_A.md` from locked main `805c2718d6daf40a219ae94242d9687e33ac3e88`.  
Global release state: **HOLD**. This checkpoint represents one formal *non-promotion*, not completion of 1,330 individual adjudications.

## Decision

- Source ID: `SRC26-20260920_142928-0145`; original ledger row 145.
- Source: China Automotive New Energy Signs Agreement with Leapmotor to Promote Battery Technologies (Gasgoo Sept 19 secondary report).
- Economic act: September 17 signed FAW/China Automotive New Energy Battery Technology–Leapmotor advanced-battery cooperation/R&D agreement.
- Locked Full same-event card: `2026-09-17_CN_01` (agreement signed Sept 17; same counterparties, instrument and technology scope).
- Formal Stage A disposition: `existing_reinforcement`, *no new card*. Execution credibility `PASS`; independent cardability `FAIL`, because the original act already exists in Full. Score 15; urgency `monitor`.
- A distinct FAW Qixin Power investment LOI must not be represented as another battery R&D agreement; it is a separate parallel instrument.
- All 1,330 original Source IDs, primary URLs, raw headlines and row indexes preserved. The 70 pre-native attached assessments remain available as historical, non-authoritative evidence. This source's former live review-pool resolution row was moved into the closure receipt.

## Accounting

| Field | Before | After |
|---|---:|---:|
| Original Source IDs | 1,330 | 1,330 |
| Formal individually adjudicated | 45 | 46 |
| Formal outstanding | 1,285 | 1,284 |
| `strict_passed_spec` | 8 | 8 |
| `candidate_review_pool` | 636 | 635 |
| `watchlist_context_pool` | 658 | 658 |
| `existing_reinforcement` | 28 | 29 |
| New strict promotions | 0 | 0 |
| Stage B additional entry | No | No |

## Verification

1. `python validation_scripts/stage_artifact_contract_check.py A STAGE_A_1330_NATIVE_FORMAL_0145_20261101.json` → `PASS` (8 strict, zero missing).
2. `python validation_scripts/stage_lineage_contract_check.py stage_a STAGE_A_1330_NATIVE_FORMAL_0145_20261101.json` → `PASS_STAGE_A_SCHEMA_CONTRACT`.
3. `verify_stage_a_formal_0145_20261101.py` → `PASS`, **30/30 independent delta checks**, including unchanged judgments for the other 1,329 IDs and full source identity.
4. Main branch/Full/Related/production have not been edited; audit documents are isolated to the audit branch and Drive.

## Content-addressed files

| File | SHA256 |
|---|---|
| Prior 70-attachment full Stage A | `e42097f6f17495ff24550b2c72dba9d5874e7a835090c95cae4881750116d109` |
| **Formal Stage A, 1,330 rows** | **`1d2c8ccbd01b40aef7de512969281043a59cdb866d2a6dfbdd52bf997edf95c1`** |
| `STAGE_A_FORMAL_0145_RECEIPT_20261101.json` | `6ec081afa1fc92e536aa9340775eecb6a3537e71efc8c2d8ceb24beb9f416ffb` |
| `STAGE_A_FORMAL_0145_INDEPENDENT_QC_20261101.json` | `c6f8f2ccea4eb276e9b03fd7705a8b11816cf49bb4418010e3c891ffae98d941` |
| Build script | `2b33b4e0bfc46c6d4b56ea2d83d7688ef8c7f4c5c9adefe90fb48b4379bf70ce` |
| QC script | `62cb99e808dd16eb8b2ac8bc8a3d54ecb96e8530080b9930afdc577bd20ed25d` |

## Sources and boundaries

- Original Gasgoo observation: <https://autonews.gasgoo.com/articles/news/china-automotive-new-energy-signs-agreement-with-leapmotor-to-promote-battery-technologies-2101180788380209153>
- Gasgoo event reporting: <https://autonews.gasgoo.com/articles/ev/2101180788380209153>
- Reuters initial agreement context: <https://www.reuters.com/world/asia-pacific/leapmotor-plans-join-series-funding-faw-subsidiary-2026-09-17/>
- This is an editorial Stage A duplication finding. It does not authorize a Full edit or claim completion of the other 1,284 formal source dispositions.

## Next condition

Continue individual four-gate 0.1P adjudication over remaining 1,284 Sources, recompute one economic act per source/event family, run both native checks after formal batch updates, and only then assess Stage B entry on genuinely new strict cards. Korea resource-security planning, Korea ESS tender, Eos drawdown, FlexGen operating-versus-construction split, and Robins commercial operation remain separate relevant event families; their pre-native evidence is not itself formal promotion.
