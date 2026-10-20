# R27 — Source-to-canonical recovery after PR #394 (AUDIT ONLY)

**2026-10-20 KST | REVIEW, NOT CARD APPROVAL | NO MERGE/AUTOMERGE**

## Current baseline
- Post-#394 `main=805c2718d6daf40a219ae94242d9687e33ac3e88`, Full blob `07a91714e56be2a8bfad10ab63822f0c5cb3f06e`, Lean blob `8ebad37e98639ad97a30e52063d7325da77be650`; **1,676** cards. September 22 SK On and October 6 Samsung SDI LFP are the two already accepted new cards.
- Current R26 private 1,296-row CSV was verified at SHA-256 `124134c481fdefb8f146d8bd0b4860b6d2ba55607143dbab67eb3ef73b1938be`; R27 preserves **all 1,296 candidate IDs and all 60 R26 columns and values** in order and appends only 13 separately named *observation* fields. All 1,296 formal terminals remain `UNASSIGNED`.
- Seven Collector ESS observations + one Weekly Vol03 item reflect the **same 2026 1,180MW tender programme**, not eight awards. Nine original SK On articles belong to one card already present.

## Source-checked current catch-up candidates, NOT publication instructions

1. **China EV export VAT rebate (official 2026-10-12 notice No.29):** [State Taxation Administration](https://fgk.chinatax.gov.cn/zcfgk/c102416/c5252906/content.html) cuts NEV rebate 13% to 9% **effective 2027-04-01**, determined by export declaration date. [JETRO](https://www.jetro.go.jp/biznews/2026/10/0f956ecd3698a53a.html) reports 67 covered goods lines; official Annex 1 needs original PDF line-by-line checking. Different from existing ESS consumption-tax card `2026-08-27_CN_02` and the separate battery rebate policy. **Review candidate, not PASS**.
2. **Korean central ESS tender (2026-09-22):** [MCEE](https://www.mcee.go.kr/home/web/board/read.do?boardId=1893270&boardMasterId=939&menuId=10598) and KPX separate land/Jeju notices show **1,100MW land + 80MW Jeju**, eligible substation expansion and a Jeju optional 25-year two-daily-cycle model, not awarded or COD. Beware contradictory secondary numbers 1,048+148 and 100MW land typo. KPX PDF annexes need original full read. **Review candidate, not PASS**.
3. **LG Energy Solution 2026 Q3 preliminary earnings (2026-10-08):** [Issuer](https://lg.co.kr/media/release/30650) / [Yonhap](https://en.yna.co.kr/view/AEN20261008001451320) confirm `₩756bn` operating profit incl `₩416.9bn` 45X etc credits, `₩339.1bn` excluding. Prior `2026-07-07_KR_01` is Q2. [Reuters](https://www.reuters.com/world/asia-pacific/lg-energy-solution-flags-26-rise-q3-operating-profit-2026-10-07/) notes possible one-off North American customer settlement; unquantified and not sustainable ESS margin proof. Original DART/IR/Q&A still pending. **Review candidate, not PASS**.
4. **Samsung SBB2.0 LFP LSFT:** Sept28 [issuer report](https://news.samsungsdi.com/ko/click?seq=499) concerns ESS container, distinct from July UPS test `2026-07-14_KR_01`. No original UL report or general certificate verified. **HOLD**.
5. **Electra–WMC Oct13 term sheet:** [SEC exhibit](https://www.sec.gov/Archives/edgar/data/1907184/000117184326006595/exh_991.htm) expressly calls most commercial terms **non-binding** pending definitive docs/approvals; distinct proposed inventory working capital path from existing Aug20 Glencore feedstock and Aug26 Ontario aid cards. **HOLD/WATCH**, not settled investment or supply.

Private full R27 overlay, source-owner matrix, 26-lens incomplete screen and checksum receipt are stored under the R26 project Drive folder in `R27_SOURCE_EVENT_QC`. No private 1,296-row file or protected source-body collection is committed to this public PR.

## Formal release restrictions

- **Current `main` Stage 0.0D re-certification NOT RUN**. Historical R16 stage-only PASS applies only to earlier `b7847ca`.
- Formal 0.0C remains **BLOCKED**, 6 region +14 topic machine coverage incomplete, separate 12 structural lenses pending. All **26 v6.2 discovery routes remain OPEN_INCOMPLETE** (No Single-Hit Stop).
- Stage A/B/C → 0.5 → Prompt 0.6 V5 and downstream publication gates **NOT PASS** for these catch-up candidates. R27 observational files are **NOT accepted card operations**. No score padding, card quotas, force merge, or false `content_enriched`.
- PR #386 remains **audit-only**. No edits to canonical Full, Lean, Related, Production, Revolution Masterfile/Downstream or `main`. Future fully governed new cards belong in a separate PR under freshly relocked main and explicit user-controlled merge.
