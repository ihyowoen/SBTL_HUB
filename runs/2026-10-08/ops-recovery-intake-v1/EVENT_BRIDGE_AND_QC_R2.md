# R2 companion / R3 event-bridge addendum (2026-10-08 KST)

> **HOLD: NO CARD APPLY, NO MERGE.** This is an additional diagnostic receipt for Draft PR #386, not Stage A or a production approval. All original source-archive rows and R1 evidence remain unchanged.

## Lock & source accounting
- Current observational `main`: `c09c1bc5112216a617903a2d572662342bcd857c`, canonical `data/cards.full.json` 1,674, full blob `d847e2d53bfe27a2b61bac023a82d2009c313356`. **Re-lock before formal operations.**
- Four original Collector ZIPs (2026-09-20/23/26/28): 1,157 expanded rows, 1,045 identity-safe normalized primary URLs, 112 URL-repeat rows. **1,045 is not the number of independent events.**
- All original Triage statuses preserved: 919 KEEP / 234 TRIAGE_FILTERED / 4 REVIEW. No filtered candidate is silently deleted.
- High-threshold near-title clustering found **11 tentative two-URL groups (22 URLs, 11 possible redundancies)**, plus **6 ambiguous title pairs**. This is **title similarity only**, not approved semantic identity or a new event count.
- Collector `region` codes cannot alone prove place-of-event coverage (e.g., a 2026-09-20 story about an Argentinian solar train appeared under `US` via Euronews). No 6-region × 8-lens coverage PASS is claimed.

## Four Collector REVIEW dispositions — proposed, with provenance retained
| Original Collector UID | Proposed disposition | Reason |
|---|---|---|
| `20260923_132732:REVIEW_4` | `RESERVE_POLICY_EVENT_AND_MERGE_SOURCE` | Korean ministry's [2026-09-23 IAA meeting briefing](https://admin2.korea.kr/briefing/pressReleaseView.do?newsId=156783123&pWise=mSub&pWiseSub=C5); legislative discussion, **not enacted law** |
| `20260923_132732:REVIEW_5` | `MERGE_REPORT_WITH_REVIEW_4` | [Newsis](https://www.newsis.com/view/NISX20260923_0003802247) reporting on same Korean–European Parliament meeting; second source, not a new rule |
| `20260928_160143:REVIEW_2` | `DROP_SCOPE_RETAIN_PROVENANCE` | UK terror-arrest article; no demonstrated battery/ESS/supply-chain nexus |
| `20260928_160143:REVIEW_4` | `DROP_SCOPE_RETAIN_PROVENANCE` | Baemin / Google Korea parliamentary witnesses; no battery/ESS/supply-chain nexus |

## Confirmed execution-stage bridge: POSCO Future M
1. **2026-08-06**: existing `2026-08-06_KR_03` describes agreement with **unnamed** Korean buyer for over **190,000 t** of LFP cathode materials over 2027–2032, with formal contract then pending. [August POSCO newsroom](https://newsroom.posco.com/kr/%ED%8F%AC%EC%8A%A4%EC%BD%94%ED%93%A8%EC%B2%98%EC%97%A0-%EB%93%9C%EB%94%94%EC%96%B4-lfp-%EC%8B%9C%EC%9E%A5-%EB%9A%AB%EC%97%88%EB%8B%A4-%EB%B0%B0%ED%84%B0%EB%A6%AC%EC%82%AC%EC%99%80-%EB%8C%80/).
2. **2026-09-22**: `RC26-001` is **distinct SK On** LFP cathode supply contract of about **KRW 1.1 trillion**, 2027–2029, extendable. The company's Sept 22 release explicitly says this is *in addition to* last month's agreement. [POSCO Sept release](https://www.poscofuturem.com/pr/view.do?num=1049).
3. **Contract signed Oct 6, announced Oct 7**: `RC26-021` **Samsung SDI** approximately KRW **6 trillion** long-term materials contract; official source **explicitly identifies Samsung SDI as the August 190,000 t counterparty** and says quantities were increased more than twofold. This is the **stage-advancing follow-up to the August canonical card**, separate from SK On. [POSCO October release](https://newsroom.posco.com/kr/%ED%8F%AC%EC%8A%A4%EC%BD%94%ED%93%A8%EC%B2%98%EC%97%A0-%EC%82%BC%EC%84%B1sdi%EC%99%80-lfp-6%EC%A1%B0%EC%9B%90-%EA%B7%9C%EB%AA%A8-%EA%B3%B5%EA%B8%89%EA%B3%84%EC%95%BD-%EC%B2%B4%EA%B2%B0-non/).

**Do not** merge the Samsung contract with the SK On contract. Do not describe August's nonbinding agreement as already signed. Do not imply the entire October 6-trillion commitment corresponds to precisely the August 190,000 t base quantity; the October announcement also describes other materials.

## Existing R2 cross-check + three new R3 provisional events (not Stage A)

**Canonical candidate-ID crosswalk:** The existing `R2_CONTINUATION.md` already owns RC26-013 through RC26-019. This companion **reuses RC26-014** for LGES–Elevra and **introduces only RC26-020** (LGES–indiGOtech), **RC26-021** (POSCO–Samsung SDI), and **RC26-022** (LGES–B2U). No provisional event ID is overwritten or counted twice. Existing R2 RC26-016 denotes the EU IAA meeting, not B2U.
| ID | Event / announcement date | Stage | Primary evidence | Existing-card context |
|---|---|---|---|---|
| **RC26-014** | Oct 8 / Oct 8 | `SIGNED_BINDING_OFFTAKE` | [LGES–Elevra](https://www.lgcorp.com/media/release/30655): 240,000 dry metric tonnes of spodumene concentrate from Quebec over 4 years | `2026-08-21_GL_01` is Elevra–**Mangrove**, different counterparty; no same-contract merger |
| **RC26-020** | Oct 1 / Oct 1 | `NONBINDING_MOU` | [LGES–indiGOtech](https://lgcorp.com/media/release/30626): explore 46-series NCM cylindrical cell supply 2027–2030 | No firm purchase order or volume proven |
| **RC26-021** | Oct 6 / Oct 7 | `SIGNED_UPSIZED_SUPPLY_CONTRACT` | [POSCO–Samsung SDI](https://newsroom.posco.com/kr/%ED%8F%AC%EC%8A%A4%EC%BD%94%ED%93%A8%EC%B2%98%EC%97%A0-%EC%82%BC%EC%84%B1sdi%EC%99%80-lfp-6%EC%A1%B0%EC%9B%90-%EA%B7%9C%EB%AA%A8-%EA%B3%B5%EA%B8%89%EA%B3%84%EC%95%BD-%EC%B2%B4%EA%B2%B0-non/) | Same-counterparty/advanced-stage candidate Related to `2026-08-06_KR_03`; pending formal Related gate |
| **RC26-022** | Sept 22 dateline / Sept 28 page | `PARTNERSHIP_PRIORITY_ACCESS` | [LGES–B2U](https://lgcorp.com/media/release/30606): battery repurposing/BESS collaboration | Collector UIDs `20260926_120143:KR_2026-09-24_C09`, `20260928_160143:TF_0057`; date-role conflict needs resolution |

**RC26-014/014/015 are post-Sep28 targeted source discoveries, not products of a completed 6 × 8 regional/lens crawl.** The existing 19 R1/R2 events plus the three nonduplicate R3 additions are **22 provisional candidates**; not the 1,045-URL universe disposition. ID RC26-014 is a verified cross-reference, not a 23rd event.

## Existing published-card accuracy blocker — urgent separate UPDATE review
Current canonical `2026-05-13_EU_01` headline: **"EU 산업가속법(IAA) 발효 진입 — 동력전지 본지화 강제 + 중국 자본 진입 제한 6 of 4 조건"**. Its body itself says the Commission's proposal was in Parliament/Council consideration, and it relies on a single secondary [OFweek piece](https://libattery.ofweek.com/2026-05/ART-36001-8480-30687365.html).
**Current official status**: [European Parliament procedure 2026/0068(COD)](https://oeil.europarl.europa.eu/oeil/en/procedure-file?reference=2026%2F0068%28COD%29): `Awaiting committee decision`; [EU Commission proposal](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A52026PC0100) dated **2026-03-04**. Enacted/entered into force cannot be claimed from this source. Treat `2026-05-13_EU_01` as **CORRECTION_CANDIDATE / HIGH_PRIORITY**, verify proposed-versus-enacted provisions in primary text, and submit through a **separate governed update**. No direct mutation is authorized here.

## Formal blockers unchanged
1. Event-level normalization and full 1,674-card semantic / Related reconciliation incomplete; name similarity and URL checks are insufficient.
2. All 234 TRIAGE_FILTERED and all remaining archive candidates retain unresolved governed terminal statuses; above four REVIEW rows are only **proposed** dispositions.
3. Full authoritative 2026-09-29→10-08 catch-up coverage across KR/CN/JP/EU/NA/Global and all eight lenses not completed.
4. Formal Stage 0.0D/0.0C, Stage A/B/C, 0.4→0.8 have **not** passed.
5. This draft remains **unmerged**. This file changes no cards, validators, runtime, Vercel deployment, or Revolution master/downstream components.

**Proposed next action:** prioritize PR-independent card correction gate for IAA, verify the POSCO Samsung stage bridge and Oct 8 LGES Elevra source; then continue exhaustive ledger reconciliation and scoped catch-up under current production validators.
