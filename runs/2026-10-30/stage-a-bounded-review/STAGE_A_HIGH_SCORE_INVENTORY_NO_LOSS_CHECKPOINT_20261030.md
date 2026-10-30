# SBTL_HUB Stage A — 103-source high-metadata review inventory

**2026-10-30 KST · non-decisional queue, not a Round or native PASS.**

The original source CSV has **1,330 unique Source IDs**, of which 636 were originally in candidate review, 658 in WATCH/context, 28 in duplicate/reinforcement, and 8 in strict. The 1,285 initially lacking individual 0.1P economic event decisions still lack **formal** complete Stage A decisions; this audit does not overwrite any of those rows.

The 636 review-pool candidates with original metadata scores at least 60 comprise exactly **103 Source IDs**: 60 with 64, 31 with 63, and 12 with 60. This metadata-only queue flags the **8 Source IDs** investigated in five separate bounded case reviews on October 30, leaving **95** in this >=60 source subset without that new bounded case research. This is source-unit accounting, **not** a count of independent publishable news or a license to skip the 533 remaining lower-scored review-pool entries. Nor may the 654 WATCH Source IDs with identical 26 scores be excluded automatically; the other four WATCH entries also remain open for event-by-event review.

## Query-preservation discovery

An unsafe `split('?')[0]` URL reducer mistakenly suggests **7 duplicate URL groups / 14 source members**. This is **false** because two publisher pages use the query string as the article identifier:

- `SRC26-20260920_142928-0064` (`idxno=62527`, 그리너지 LTO industrial-battery case) versus `SRC26-20260920_142928-0065` (`idxno=62506`, EcoproBM–CATL *negotiation*).
- `SRC26-20260928_160143-0067` (`no=107600`, Bolt EV litigation) versus `SRC26-20260928_160143-0124` (`no=107474`, Tesla charging project).

The corrected query-aware URL normalization preserves `idxno`, `no`, `list_no` and all nontracking query keys; it finds only **5 repeated-source-URL groups / 10 Source IDs** within the 103. The actual five include InoBat/Gotion filing (2), Delta Capacity Finland/Sungrow deal (2), Eneco Papendal operating battery (2), Kuehne+Nagel/CATL battery logistics (2), and a pair of KPX amended datasource records (2). Even an exact URL match is **not** definitive proof of the same economic act, particularly where the web page can be amended.

`build_103_metadata_review_inventory_20261030.py` validates the input SHA256 `5e78420916b0c1d70ff56bf928779cd969b94fbb15dd4119c841872997486116`, current 8 bounded source IDs, all six population counts, candidate-score distribution, preserved query-key differences and the five exact transport-URL groups, then creates a complete 103-record JSON file **once only**. Each record preserves the original ID/title/URL/score/date and an open Stage A individual review instruction; it does not assign final accept/reject or guarantee event-identity clustering. Full remains locked to 1,676 cards and original Git blob `07a91714e56be2a8bfad10ab63822f0c5cb3f06e` in the same day's full case QC.

**QC result:** `PASS_NON_DECISIONAL_SOURCE_INVENTORY` (script assertions), **native Stage A: NOT EXECUTED**. Next bottleneck: resolve remaining Source IDs by identity/Related/execution/cardability before full-universe Stage A native validation, including the nontraditional WATCH cohort and without any fixed article quota.
