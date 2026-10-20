# R5 incremental recovery audit — 2026-10-12 KST

> **DRAFT AUDIT ONLY. DO NOT MERGE PR #386. NOT STAGE 0.0D/0.0C PASS. NOT PUBLISH-READY.** This is an append-only reconciliation note. The reproducible offline R5 evidence bundle remains separate; **no cards, validators, Revolution master/downstream code, or Production deploy were changed** by this note.

## Immutable input references / decision boundary
- Source: R4 preserved `R4_SOURCE_ROW_LEDGER_1157.csv`, whose 1,157 stable source UIDs cover the 4 archived Collector expanded outputs (919 KEEP + 234 TRIAGE_FILTERED + 4 REVIEW). Exactly 1,045 identity-preserving primary URL groups, not unique event IDs.
- Observed canonical main on Oct 12: `b7847ca9885f6f27ae0566455b0a476ef1059d24`; full blob `d0b472e4173e565284616bb7eec0e4b28e1a42b9`; lean blob `c39eac64afde20ff0ccacd920e12abbdab1b3d02`. Re-lock before any operational mutation.
- Vercel Production deployment `dpl_Duj3iRcCHCC6oXEwEHd6Tjz7QMdk` READY at that SHA, `sbtl-hub.vercel.app` alias. **This proves deployment metadata, not the rendered card UI**.
- IAA `2026-05-13_EU_01` corrected in main Full/Lean; remove from unresolved *card-correction action* but **do not subtract from the 22 provisional RC26 event IDs**. POSCO `2026-08-06_KR_03` still needs Oct Samsung SDI contract lineage review.

## Reproduced count-definition discrepancy (source UID grain)
| Check | R4/R5 direct source-row computation | R3 checkpoint | Disposition |
| --- | ---: | ---: | --- |
| `published_date < 2026-09-19` | **125 source rows** | 117 "items" | definition not reconciled |
| distinct normalized primary URLs in those 125 rows | **118** | unspecified | do not force-fit |
| repeated observations in older slice | **7**, from 7 URL groups (14 member rows) | unspecified | retain both UIDs |
| strict `list_context_only` | **36 rows** | 38 "list-only" | definitions differ |
| separate `title_only` / `rss_context_only` | **1** / **8** rows | unspecified | no silent addition |

R5 offline bundle contains an exception-UID CSV (161 unique source rows in union of older or low-coverage states), the 14 repeat member UIDs, reproducible re-count script, and search provenance. The 117/38 values are not labelled typos until R3's original exact filters/grain can be replayed. **No rows were deleted or assigned terminal event dispositions.**

## Event identity separation / new gap spot-checks
- `LGES_NVIDIA_DSX_READY_BESS_20260922`: [LGES first party Sep 22](https://lgcorp.com/media/release/30596). NVIDIA DSX Ready **BESS product qualification**, not an award of sales volume.
- `LGE_NVIDIA_NPN_POWER_COOLING_20260928`: [LG Electronics first party Sep 28](https://www.lg.com/global/newsroom/news/eco-solution/lg-electronics-becomes-an-nvidia-preferred-partner-for-power-and-cooling-solutions/). Distinct company, partner type, and product from LGES BESS.
- `RC26-021`: [POSCO Future M](https://www.poscofuturem.com/pr/view.do?num=1051) **Oct 6 executed Samsung SDI contract**, webpage date Oct 7, expansion from August 190kt *agreement* by >2x; **not** [Sep 22 SK On](https://www.poscofuturem.com/pr/view.do?num=1049). Preserve three event-stage/date/counterparty roles.
- `R4_DISC_001`: [EC Oct 9](https://luxembourg.representation.ec.europa.eu/actualites-et-evenements/actualites/commission-selects-46-new-strategic-projects-bolster-eus-supply-critical-raw-materials-2026-10-09_en) selected 46 CRMA strategic projects in 16 Member States. Designation **is not** automatic funding or commissioning.
- Provisional `R5_DISC_001`: [EC commissioner press remarks Oct 9](https://audiovisual.ec.europa.eu/en/media/video/I-295803): EU-China shared understanding to moderate exports of Chinese hybrid/PHEV to EU, with non-enacted trade implementation details and rare-earth export licensing discussions. **Do not publish as finalized enforceable quota.**
- Provisional `R5_DISC_002`: [Benchmark Oct 9](https://source.benchmarkminerals.com/article/lithium-cost-pass-through-drives-volatile-quarter-for-energy-storage-cells-cell-price-review-q3-2026) Sept 314Ah LFP battery cell EXW China USD 51.62/kWh versus CIF North America USD 61.99/kWh, with different delivery bases. **Market price evidence, not supply agreement or equal-base plant cost.**
- Secondary only / pending first-party: Oct 9 Mana sodium-battery funding and Oct 9 India BSES Rajdhani 57.5MW/115MWh reported LOI. Do not assign formal RC numbers; classify as WATCH until verified.
- **False recency:** NTPC Barh / Pace Digitek INR 488.46 crore contract appearing in an Oct 10 article was [already reported on Sep 22](https://www.sahi.com/news/pace-digitek-subsidiary-receives-488-46-crore-bess-order-from-ntpc-ge-power); do not treat Oct 10 retelling as a fresh awarded contract without new milestone.

## Stage hold / required next action
- Explorer performed preliminary queries spanning **6 exact region keys and 14 exact topic keys**, but native 0.0C terminal search receipts and complete evidence-linkage remain missing. **All formal 20 axes remain BLOCKED**, despite some first-party spot-checks.
- R4 preliminary 0.0D document read 43/43 is not the executable validator/semantic-conflict PASS. 0.0D BLOCKED, 0.0C BLOCKED, Stage A not authorized.
- Still need per-source 1,157 UID terminal accounting; 1,045 URL → article → event → 1,674-card canonical/Related reconciliation; all 234 TRIAGE_FILTERED and 4 REVIEW reasons; accepted A/B/C and 0.4→0.8 stages.
- Only after those gates may a **separate small production-card PR** be created. Keep this PR Draft/unmerged, with zero production card writes and zero Revolution code changes.

**Current decision**: R5 evidence-only continuation; newly confirmed facts **do not** mean R5 publication or any Stage PASS.
