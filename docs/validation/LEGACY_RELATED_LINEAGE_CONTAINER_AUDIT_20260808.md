# Legacy Related Lineage Container Audit — 2026-08-08

## Baseline

- repository: `ihyowoen/SBTL_HUB`
- main commit audited: `33068a273dc4fb6585b62ce99c29d7a792532662`
- canonical: `data/cards.full.json`
- canonical card count: `1,343`
- canonical full blob: `ba7e680c9a3c3425f212ef29bcfd9055113cbdb0`

The audit was executed on a non-main audit branch with a read-only GitHub Actions token. No canonical data was modified.

## Full inventory result

| Check | Result |
|---|---:|
| total cards | 1,343 |
| duplicate card IDs | 0 |
| cards with non-empty `related[]` | 212 |
| cards already carrying valid `related[]` + `related_lineage.related_ids` containers | 94 |
| cards missing/invalid `related_lineage.related_ids` | 1,249 |
| non-empty `related[]` but missing lineage container | 200 |
| empty `related[]` and missing lineage container | 1,049 |
| published dangling Related edges | 14 |
| cards carrying those dangling edges | 13 |
| new dangling cards beyond the 2026-07-23 legacy manifest | 0 |
| self-links | 0 |
| duplicate Related links | 0 |
| mismatch between `related[]` and already-present `related_lineage.related_ids` | 0 |

The historical 2026-07-23 snapshot remains exact for dangling relations: all 13 previously identified cards still carry the same 14 missing targets, and no additional dangling edge was found in the current 1,343-card baseline.

## Dry-run migration tested

A neutral initialization candidate was generated without touching main:

- already ready: 94 cards
- newly initialized in dry-run: 1,236 cards
- initialized cards with pre-existing non-empty `related[]`: 187
- skipped: exactly the 13 dangling-remediation cards
- final ready after dry-run: 1,330 / 1,343
- remaining missing lineage containers: exactly 13 / 1,343

For each initialized card, the candidate added only:

```json
{
  "related_lineage": {
    "related_ids": ["<exact existing related[] values in existing order>"]
  }
}
```

No relation type, reason, direction, event stage, fresh anchor, new edge, deletion, or removal was inferred.

## Dry-run validation

The dry-run candidate passed:

- `scripts/validate_cards.mjs` on full candidate: PASS, errors 0
- generated lean projection validation: PASS, errors 0
- post-migration relation-container re-audit: PASS
- card count remained 1,343
- published dangling edges remained the frozen 14 legacy edges only
- no lineage dangling edge was introduced because the 13 dangling cards were excluded

Projected lean impact:

- changed lean cards: 1,236
- lean size delta: +53,092 bytes

The full candidate serialization used by the dry-run was regenerated with pretty JSON and therefore is not used as a byte-size comparison for the eventual PR; the semantic validator compares card fields and the final PR must be generated from the actual canonical bytes/output procedure.

## Conclusion

A broad but mechanically bounded migration is justified for the 1,236 non-dangling legacy cards. The 13 cards with dangling published edges must remain untouched and continue through separate item-specific remediation.

The ordinary card-run engine intentionally cannot create missing parent lineage containers. A dedicated, separately reviewed migration path is therefore required before the data migration can be submitted without weakening ordinary `insert / update / related_add` governance.
