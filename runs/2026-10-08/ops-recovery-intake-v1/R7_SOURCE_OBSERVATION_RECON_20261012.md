# R7 incremental source-observation reconciliation — 2026-10-12 KST

> **AUDIT-ONLY / PR #386 DRAFT / DO NOT MERGE / NOT Stage 0.0D PASS / NOT Stage 0.0C PASS / NO CARD APPLY.** Zero changes to `data/cards.full.json`, `public/data/cards.json`, Revolution master/downstream, and Production. This is an observation-layer audit only.

## Locked context and deterministic source accounting
- Exact baseline observed on 2026-10-12: GitHub `main=b7847ca9885f6f27ae0566455b0a476ef1059d24`; full blob `d0b472e4173e565284616bb7eec0e4b28e1a42b9`; lean blob `c39eac64afde20ff0ccacd920e12abbdab1b3d02`.
- Input: R4 saved `R4_SOURCE_ROW_LEDGER_1157.csv`, SHA256 `6fafdd2470cf33c6c58dcda6b7a5cd065faaef6ed5ece2c01302e504de619111`, derived from four Collector ZIPs. R7 did not re-download or mutate ZIP sources.
- 1,157 stable source-row UIDs and candidate IDs retained, KEEP 919 + TRIAGE_FILTERED 234 + REVIEW 4, normalized article-URL groups 1,045.
- A stricter **URL + HTML-unescaped/NFKC normalized headline + published_date** signature yields **1,053 distinct source-observation signatures**; **104 redundant observations by this signature**, *not* 104 confirmed same events or deleted records.
- 110 repeat-URL groups: **103 groups (206 captures)** have same normalized URL, title, and published_date; **7 groups (16 captures)** vary title/date or represent an index. 25 KEEP↔TRIAGE_FILTERED disagreements include **24 stable same-article-observation groups** and **1 Mercedes-Benz recruitment listing date variation**. None receives a governed 0.0C event terminal disposition.
- One repeated OFweek `/CAT-36005-shengchanjianceshebei.html` URL is a dynamic category index (four captures, three assigned dates), not an event article.

## Four same-title, different-URL pairs checked against live source pages
| Cross-URL group | Article-level evidence decision | Required event/date safeguard |
| --- | --- | --- |
| `TITLEPAIR-53067898b550dd7d` | `CONFIRMED_SAME_EDITORIAL_REPORT_REPUBLISHED`: ESS News Sep 24 → pv magazine Sep 26; pv expressly says `From ESS News`, Brian Publicover | Zhejiang grid-side BESS spot market is a **China** policy event, notwithstanding EU/GL Collector feed tags. No second rule on Sep 26 |
| `TITLEPAIR-79a7f501dedfad8f` | `CONFIRMED_SAME_EDITORIAL_REPORT_REPUBLISHED`: Tristan Rayner in ESS News Sep 22 → pv magazine USA Sep 24 | NVIDIA DSX Ready **program** `RC26-003` and LGES qualification `RC26-004` are distinct actor events; don't merge those events |
| `TITLEPAIR-2459405c6b5fb32d` | `CONFIRMED_SAME_EDITORIAL_REPORT_PARALLEL_EDITION`: Pilar Sánchez Molina, ESS/pv, Sep 25 | Spain BORALMAC EUR265m/49.9GWh reflects **two award rounds in 2024–2026**, not a newly awarded whole amount on Sep 25; pumped hydro ≠ battery ESS |
| `TITLEPAIR-58f83672dccf5018` | `AMP_URL_ALIAS_LIKELY_NOT_CONTENT_VERIFIED`: Simply Wall St normal vs `/amp` URL | AMP live page could not be reliably read, so don't close source equivalence; SQM stock-valuation opinion ≠ new supply contract |

Source page references:
- https://www.ess-news.com/2026/09/24/chinese-province-moves-grid-side-batteries-into-spot-market/ ; https://www.pv-magazine.com/2026/09/26/chinese-province-moves-grid-side-batteries-into-spot-market/
- https://www.ess-news.com/2026/09/22/nvidia-launches-bess-qualification-program-for-ai-data-centers-names-just-tesla-lg-hitachi/ ; https://pv-magazine-usa.com/2026/09/24/nvidia-launches-bess-qualification-program-for-ai-data-centers-names-just-tesla-lg-hitachi/
- https://www.ess-news.com/2026/09/25/spain-awards-e265-million-for-49-9-gwh-of-pumped-hydro-storage/ ; https://www.pv-magazine.com/2026/09/25/spain-awards-e265-million-for-49-9-gwh-of-pumped-hydro-storage/

## R3 older-item count hypothesis: possible arithmetic reconciliation, NOT method proof
- Under `published_date < 2026-09-19`: **125 raw rows / 118 distinct normalized URLs**.
- Exactly **one** of the 118 older URLs is the above OFweek dynamic category index, original UID `20260920_142928:TF_0019`. **118 − 1 = 117 article-like URLs**, numerically explaining R3's “117 items”.
- **Open:** R3 original filter and unit were not retrieved. Arithmetic coincidence does not certify R3's definition. The separate R3 “38 list-only” still does not match strict `list_context_only=36` (+ `title_only=1`, `rss_context_only=8`). Do not force-fit.

## Provenance package (offline read-only)
User-facing archive: `SBTL_HUB_R7_RECOVERY_EVIDENCE_20261012.zip`; SHA256 `839a477f99e894230e6b7b2ede8ccf2ad8edba2d24fdb167742d82fe7d7198a9`.
Includes R4 1,157 source UID ledger, R6 four title-pair input, `R7_REBUILD_FROM_R6_LEDGER.py`, all 1,157 row crosswalks, 1,053 strict signatures, 110 URL decisions, 4 editorial provenance pairs, the 117-older-count hypothesis, QC, per-file SHA manifest. Two independent rebuilds returned byte-identical output CSVs/JSONs.

## Formal boundary
- 0.0D still lacks executable production validator PASS and complete authority semantic-conflict attestation.
- 0.0C still lacks native 6-region + 14-topic real search provenance, complete 1,157 original candidate terminal dispositions, discovery additions, full 1,674-card semantic/Related reconciliation. `original_input_accounted=false`, `stage_a_authorized=false`.
- R1–R3 **22 provisional RC IDs remain unchanged**. No new RC IDs, canonical mutations, Related changes, or publication authorization. Any actual release requires a separate governed data PR after Stage A/B/C and 0.4–0.8.
