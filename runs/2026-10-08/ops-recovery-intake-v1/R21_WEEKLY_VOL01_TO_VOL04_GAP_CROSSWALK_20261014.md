# R21 — SBTL Weekly Vol.01–Vol.04 gap check and audit-only candidate staging

**Date: 2026-10-14 KST. READ-ONLY REVIEW. PR #386 MUST REMAIN DRAFT AND UNMERGED.**

## Controlled sources and content access
- Vol.01: `SBTL_배터리통신_VOL01_2026년9월첫째주_FINAL.html` — **30 article items fully parsed**.
- Vol.02: `SBTL_배터리통신_VOL02_2026년9월둘째주_FINAL.html` — **42 article items fully parsed** from the Library-extracted text windows; reassembled text, **not claimed byte-equivalent to the original HTML**.
- Vol.03: `SBTL_배터리통신_VOL03_2026년9월셋째주_PUBLICATION_FINAL.html` — located Library version 1, metadata advertises **44 items**, but source access **BLOCKED**: article section in lines 5,001–5,954 returned 401 Unauthorized, and raw-file materialization was not authorized. **0 of 44 items could be fully extracted/compared. No invented or silently omitted Vol.03 candidates. Requires user reupload or an accessible complete source.**
- Vol.04: `SBTL_WEEKLY_VOL04_2026년10월첫째주_FINAL_REVIEWED.html` — **30 fully parsed**, authoritative final reviewed version dated Oct 12 (7 article text changes relative to earlier FINAL, 0 source-href changes).

**Full comparison performed only for Vols.01, 02, 04: 30 + 42 + 30 = 102 items.**

## Frozen baseline and actual source/canonical comparison
- Current locked `main = b7847ca9885f6f27ae0566455b0a476ef1059d24`, Full `d0b472e4173e565284616bb7eec0e4b28e1a42b9` (**1,674 cards**), Lean `c39eac64afde20ff0ccacd920e12abbdab1b3d02`.
- Checked all 102 Weekly items' article source links against the current Full's source URLs and R20's **1,176** candidates with query-identifier-preserving normalized URL rules. **25 Weekly items overlap at least one current Canonical source URL** (Vol.01 13 / Vol.02 11 / Vol.04 1). **One further Vol.04 item** has exact source URL only in the R20 source universe, not in the Full. Vol.02's R20 Vattenfall original UID is also matched to existing Canonical and not counted twice.
- Remaining **76 Weekly items** have no exact canonical or R20 source URL; **8 of the 76 are flagged possible existing-card/programme relations despite different URL**. Exact URL absence **does not prove a distinct new economic event**; original Weekly source/claim may reinforce or update an existing card.
- `Vol01-018` CATL copper foil ↔ `2026-09-06_CN_03`; `Vol01-019` EV battery 725.2GWh ↔ `2026-09-07_GL_01`; `Vol01-021` China battery factory approvals ↔ `2026-09-06_CN_02`; `Vol01-030` Yulchon ESS pouch film ↔ `2026-07-03_KR_01`; `Vol02-017` Fluence guidance ↔ `2026-09-16_GL_01` are cross-source programme/claim checks, **not preapproved duplicates or new cards**.
- Strong source overlap examples already in Canonical: `Vol01-010 / Vol02-039` EU IAA proposed legislation ↔ corrected `2026-05-13_EU_01` (**not enacted**); `Vol01-026 / Vol02-002` Ford–CATL policy challenge ↔ `2026-09-08_US_01`. Source reuse does not automatically erase distinct article contributions.

## Append-only working output, NOT 0.0C authorization
- Original R20 **1,176 candidate IDs** kept exactly in order and preserved, including all **1,157 Collector source UIDs**, 19 independent discovery/carry-in IDs.
- Assigned **76 unique source-review-only IDs** of form `WK26-VOL01-002` (or VOL02/VOL04) to the Weekly items not found by exact source URL. These are **not economic-event approved identities**.
- Private working ledger: **1,176 + 76 = 1,252 nonterminal rows**, with all prior 1,176 preserved and all Weekly rows carrying original headline, specific source URLs, volume, position, structural topic tags, overlap/possible-card checks and next evidence action.
- Of 76, **51 tagged for additional structural nonexecution review** (market volume/price/margins, customer cost-down, supplier payment terms, China localisation/safety/policy, critical-material concentration, grid access, ESS dispatch, battery technology, government policy). This is an editorial coverage protection flag, not 51 accepted cards.
- Sources' original publication dates and action stages need checking. For example, an InfoLink H1 report carried by Vol.04 may be an August original and must not be re-labeled an October launch.
- `R21_...ALL102_CROSSWALK.csv` and `R21_WEEKLY_NEW_NONTERMINAL_76.csv`, `R21_R20_1176_PLUS_WEEKLY_76_APPEND_ONLY_NONTERMINAL_1252.csv`, QC, hashes and rebuild scripts are preserved **outside public GitHub** in `SBTL_HUB_OPS_R21_WEEKLY_VOL01_04_GAP_STAGED_20261014.zip`. No proprietary newsletter text body was committed to this public PR.

## Formal gate status
- Prior R16 native **0.0D standalone PASS** valid as its own audited stage; **formal 0.0C BLOCKED**, independent 6-region+14-topic axes incomplete, separate 12 structural editorial lenses not fully proved, and **all 1,252 working identities remain governed-terminal UNASSIGNED**. `stage_a_authorized=false`.
- Vol.03 incomplete access is an explicit additional blocker. No Stage A, B, C, 0.4–0.8, full/lean/Related mutation, production publish, Revolution Masterfile/Downstream change or PR merge. Keep #386 **Draft, unmerged**.
- Next: obtain readable Vol.03 publication HTML; compare all source items against Full/R21 crosswalk; de-duplicate by actor/contract/project/action-stage, not title or domain; complete 0.0C coverage and final terminal ledger before further stages.
