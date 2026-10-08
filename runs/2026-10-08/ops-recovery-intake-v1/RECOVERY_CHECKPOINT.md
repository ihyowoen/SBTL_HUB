# SBTL_HUB operations recovery intake — 2026-10-08 KST

> **DRAFT / HOLD — NOT publish authorization.** This checkpoint captures evidence and outstanding gates. Do not merge this PR or apply cards from it; it is separate from Revolution masterfile / Downstream remediation.

## Frozen observational baseline (read-only)

- Repo: `ihyowoen/SBTL_HUB`, `main` at `c09c1bc5112216a617903a2d572662342bcd857c` (PR #385).
- `data/cards.full.json`: 1,674 cards, blob `d847e2d53bfe27a2b61bac023a82d2009c313356`, JSON `updated=2026-09-19T05:00:00Z`.
- `public/data/cards.json`: blob `ea608b5b8fcb7070110d466d2aca6df9e4f08d75`.
- These are observations, **not** permanently frozen production pointers; re-lock just before a future actual card-run.

## Original ZIP output evidence (user Drive)

All are stored in [the provided source folder](https://drive.google.com/drive/folders/1lmvWslBhtR266utJNDdxEUQ_L3asXKpC?usp=sharing).

| Collector output | Expanded rows | ZIP SHA256 | Expanded-output SHA256 |
| --- | ---: | --- | --- |
| [09-20](https://drive.google.com/file/d/1ZFJd4i1SfZzwRLtHj4qyDXqq2uVsPnC1/view) `20260920_142928.zip` | 202 | `9e638c0f8ddeda0e3529e4f79001f8e074a864eb491737186143de15987faab6` | `6378018e8e4420d2e868e1e24127f3508c188abb42d38d40c82753679b30bf46` |
| [09-23](https://drive.google.com/file/d/1QohtwYJAzj3bYbzeEnC4Hg89pvulvMQb/view) `20260923_132732.zip` | 296 | `015fa2407b72261b32873e1eb19a1167832085760248cc47886127b760b04d96` | `bee3b3df1571d9c79c18a338e51ae1c123c00143cdd64d1d6c04dc68f822e9f1` |
| [09-26](https://drive.google.com/file/d/1Fko7WrJhGZibJsuodpNFp40pB3k7dl8M/view) `20260926_120143.zip` | 368 | `7cf080eef21310f267a08638dbcddf7085e51edfd8c12b641dd8f487b99f6ca5` | `86ea8023d8a1756d49d8810cf29bf2e8d5cf888085cb09dfe34b4262b2f38d56` |
| [09-28](https://drive.google.com/file/d/1winFOuAVABNcQ0m0N35J2uZl-zRrQgDP/view) `20260928_160143.zip` | 291 | `e422883a286c84445987f65ad3e130c3527f21b16a580e0d4aaf64d77728c19f` | `57a07e1e9fe09d1c36f93ff1408ab034913fd94a813a9e87954731976a9b1e6d` |

The four **expanded Collector/Triage** outputs total **1,157 article rows**. Dedup by *primary article URL* (retaining identity-bearing `?no`, `?idxno`, `?newsId`, removing only known tracking keys) yields **1,045 distinct URLs and 112 repeated URL rows**. These counts do **not** represent distinct events or publishable cards. Earlier 910-URL result was invalid due to dropping all URL query strings and was explicitly discarded.

The unfiltered accounting remains **919 KEEP, 234 TRIAGE_FILTERED, 4 REVIEW** (1,157 total); 38 list-only items and 117 items dated before September 19 require individual resolution. Full row-level provenance and source references are preserved in offline `SBTL_HUB_RECOVERY_20261008/recovery_packet.zip`; the Drive source ZIPs remain authoritative.

## Current state

| Gate | Observed status |
|---|---|
| Four ZIP acquisition, SHA receipts, parse validation | COMPLETE |
| URL normalization and source-row lineage | COMPLETE for these four ZIPs |
| Full semantic same-event, multi-source coalescing | **INCOMPLETE** |
| Current canonical card collision, existing Related edge verification | **INCOMPLETE** |
| Formal 6-region x 8-lens scan since 09-28 (72h → 7d → gap) | **NOT RUN** (spot-check only) |
| Stage 0.0D/0.0C formal PASS | **NOT CLAIMED** |
| Stage A/B/C and 0.4 → 0.5 → 0.6 → 0.7 → 0.7C → 0.8 | **NOT RUN** |
| Canonical/lean mutation, production publish/deploy | **NONE** |

## Next operational release chain

1. Re-lock `main`, exact `cards.full.json` and `public/data/cards.json` blobs before downstream steps.
2. Account for every Collector row and each formal candidate with `NEW / FOLLOW-UP / REINFORCEMENT / CARRY-IN / WATCH`, including deduped and dropped lineage (no silent disappearance).
3. Complete missing 09-29~10-08 source sweeps, deferred lanes, four `REVIEW` cases and filtered candidates with documented reasons.
4. Perform **formal** Stage 0.0D/0.0C then Stage A, B, C, 0.4, 0.5, 0.6, 0.7, 0.7C, 0.8 on existing approved production validators, not experimental Revolution code.
5. Produce a **separate** small production-card PR only for formally accepted operations. Reject unexplained `delete/related_remove`, validate full/lean sync, production UI, and Prompt 0.9 after merge.

The accompanying provisional 12-event shortlist is in [PRELIMINARY_EVENT_QUEUE.md](./PRELIMINARY_EVENT_QUEUE.md); it must **not** be treated as Stage A acceptance or publication authorization. **No merger of this draft, no direct live updates, no mutation of Revolution branches.**
