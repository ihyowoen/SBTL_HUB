# Full canonical primary-URL exact overlap check (2026-10-08 KST)

> **URL equality only — NO semantic event or Related acceptance.** This is additional evidence on the draft operational intake checkpoint, not permission to apply cards.

## Exact inputs

- Collector 4 ZIPs, 1,157 rows; tracking-aware URL normalization → 1,045 unique **primary** candidate URLs.
- GitHub `main` observational baseline `c09c1bc5112216a617903a2d572662342bcd857c`.
- `data/cards.full.json` 1,674 cards, blob `d847e2d53bfe27a2b61bac023a82d2009c313356`.
- Every existing canonical card's `urls[]`: 3,443 distinct normalized URLs.

Method: exact normalized string comparison, not a 16-bit fingerprint proxy. Normalize scheme/www/trailing slash/case/fragments, drop **only** recognized tracking query parameters while preserving article identity keys (`no`, `idxno`, `newsId`, etc.).

## Verified exact primary-URL intersections

| Candidate UID | Candidate | Canonical card ID | Interpretation |
| --- | --- | --- | --- |
| `20260923_132732:TF_0043` | [Vattenfall German BESS FID](https://group.vattenfall.com/press-and-media/pressreleases/2026/vattenfall-takes-final-investment-decision-on-major-battery-project-in-germany) | `2026-09-10_EU_02` | Existing exact URL; do not insert as a new event |
| `20260923_132732:TF_0005` | [CATL–BME Egypt battery packs](https://www.catl.com/en/news/6998.html) | `2026-09-14_GL_01` | Existing exact URL; do not insert as a new event |

- **2 / 1,045** candidate primary URLs already appear as canonical source URLs.
- **1,043 / 1,045** have *no exact primary-URL match*, **NOT** 1,043 new events.
- 12 provisional event shortlist's first-party URL comparisons: **0/12 exact canonical URL matches**, but same-event/multi-source matching remains outstanding.
- Other articles listed in `source_urls` are NOT part of this primary-URL-only check, so this report is deliberately narrower than complete source-collision accounting.

## Release restriction

Many different URLs report the same event, including syndicated text with different publisher URLs. No exact match does not mean distinct event or new fact. Confirm actor, asset, date, counterparty, stage, event lineage, and prior `related` before any operation, and complete the entire current production gate chain. All **1,157** original source rows must retain terminal lineage; the two URL matches are review flags, not authorization to silently delete source rows.

**No canonical or public lean data modified.**
