# R11 — Captured-body reconciliation and governance preflight (2026-10-12)

**READ-ONLY AUDIT / NO CANONICAL MUTATION / NOT STAGE A / NOT PUBLISH-READY**

## Immutable observational baseline
- GitHub `main` commit: `b7847ca9885f6f27ae0566455b0a476ef1059d24`.
- Full canonical blob: `d0b472e4173e565284616bb7eec0e4b28e1a42b9`; lean blob `c39eac64afde20ff0ccacd920e12abbdab1b3d02`.
- All four original Collector ZIPs (Sep 20, 23, 26, 28) were re-fetched from the existing Drive archive folder and **all SHA-256 digests matched** the R4 source receipts.
- Exactly **1,157 original source-row UIDs / 1,157 candidate IDs** preserved. KEEP **919**, TRIAGE_FILTERED **234**, REVIEW **4**; normalized primary URLs **1,045** (these are *not* independent event counts). Nonempty captured bodies **1,156/1,157**; missing body is explicitly retained as one review UID.

## R8 remaining 19 mixed-triage URL groups — now captured-body-audited
The R8 six groups / twelve UIDs are retained unchanged. For the **remaining 19 groups / 38 original UIDs**, the exact original expanded Collector records were read and compared:
- **17/19** pairs have byte-identical captured article bodies.
- **2/19** Japanese BESS webinar pairs differ **only** in timestamp presentation; replacing the earlier `21時間前` label with `2026年9月19日 18時30分` or `18時00分` yields exact text identity.
- No original UID was dropped or collapsed. These checks establish *article observation relations* only, not independent event identity, baseline collision clearance, or Stage 0.0C terminal decisions.
- 4 Geely-related commentary articles were traced to [Geely's single September 23 smart-charging launch](https://www.geelyautogroup.com/en/media/202609231/); no fourfold new launch tally.
- CATL 9/21 ESS online store price adjustments / 587Ah price listing are separable from its 9/21 A-share buyback despite appearing within one article. [Price reported with company confirmation](https://www.jiemian.com/article/15123126.html); [buyback filing reported](https://www.yicai.com/brief/103372660.html). Displayed asking prices are not executed transaction prices.
- Li Auto's battery in-house design / *contract-manufactured cell* supplier shift is a meaningful OEM supply-chain lead (Sep 21 executive briefing; [Caixin source](https://www.caixin.com/2026-09-23/102488077.html)). Do not equate it with complete own-factory cell manufacture.
- The Ningbo Ronbay Bijie 34kt x10 LFP project and Hunan Yuneng Weng'an 40kt x10 LFP EIA stage are two legal actors / distinct implementation stages, not 740,000 tonnes already produced; the original joint article receives a **two-event split review only**, never silent duplication.
- Four PR TIMES Japan items are dated *webinar announcements*, not new BESS build/operation confirmations. The Mercedes cell engineer item is a job posting, not a capacity expansion.
- 7 other market commentary/price/equipment items retain review / source-context handling; embedded concrete actions must be separated instead of discarding every item on headline type alone.

## R7 variant URL groups (7) and REVIEW source UIDs (4)
- **7 changing same-URL groups** checked against the original captured body/date roles: Seoul Economic Daily headline editing, The Guru excerpt shortening, OFweek dynamic non-durable category index (4 observations), Reuters nickel commentary reported-date disagreement, Mercedes recruitment date disagreement, Petromindo publisher suffix, Ajunews changing unrelated recommendation/sidebar block. These are *not* seven new independent events.
- **4 REVIEW input UID rows** retained. Two concern one Korean Government / media policy diplomacy about **proposed** EU Industrial Accelerator Act. The unrelated UK security article and parliamentary witnesses news are provisional off-topic holds. None has an unauthorized formal terminal Stage 0.0C disposition.

## Fresh 0.0D current-main source-level verification
- GitHub `docs/**` tree: **96 files**; current `GOVERNANCE_LIFECYCLE_REGISTRY.json`: exactly **96 unique registered paths**, no missing/unregistered; distribution **19 active canonical +17 named prompts +3 validator contracts +2 open remediations +2 activation-required migrations +21 superseded +32 reference-only**.
- Required closure **43/43** file bodies re-read from the locked commit, Stage A `EMBEDDED_NEWS_VALUE_SELECTION_V4` and Related pre-pass present; active named-stage prompt reading showed no later-overlay requirement.
- This is a **READ-ONLY source/registry precheck**. The production executable 0.0D validator and independent complete semantic-conflict audit have not been run. Therefore **no formal 0.0D PASS or Stage 0.0C authorization** is claimed.

## Exact 0.0C formal blockers
- **1,157** original candidates preserved but **1,157 remain without governed terminal event dispositions** (not unaccounted/deleted).
- Semantic **1,045 URL → article → event → entire 1,674-card canonical + Related** reconciliation remains incomplete.
- **6 exact region +14 exact topic** mandatory axes: an R5 exploratory web attempt is not exhaustive searched provenance for **Sep 29–Oct 12**; all formal axes remain blocked pending 0.0D PASS and complete discovery ledger.
- No Stage A/B/C, 0.4–0.8, merge, canonical/full-lean mutation, Vercel action, or Revolution master/downstream work authorized.

## Evidence persistence
Reproducible internal R11 bundle (CSV ledgers, per-UID captured-body SHA, 19/7/4 review, read-only 0.0D/blocked 0.0C receipts and rebuild script) is preserved outside GitHub. Full scraped article excerpts must **not** be added to this public repository. Existing R1–R8 audit docs remain untouched.

**PR #386 MUST remain DRAFT and unmerged.** This additional file is append-only audit evidence, not production release code.
