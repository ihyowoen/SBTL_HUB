# Manual Direct Add v1

`manual_direct_add_v1` is the governed path for intentional card changes that do not need the full Stage A/B/C `card-run` artifact chain.

Use it for already-reviewed, source-supported changes such as:

- direct addition of one or more publishable cards;
- reinforcement or correction of existing cards;
- one-to-one story-ID / representative-event-date correction.

It does **not** convert a direct add into a formal Prompt 0.7C/0.8 run. The manifest records a separate governance mode instead of fabricating missing stage artifacts.

## Required PR shape

A direct-add PR must contain exactly:

- `data/cards.full.json`
- `public/data/cards.json`
- one `direct-adds/<batch>/direct-add.json`

The `apply-card-run` gate rejects mixing a manual direct add with a normal `card-run` or legacy lineage migration.

## Manifest

```json
{
  "schema": "manual_direct_add_v1",
  "status": "PASS",
  "direct_add_id": "20260828_EXAMPLE",
  "base_main_commit_sha": "<exact PR base main SHA>",
  "base_full_blob_sha": "<git blob SHA of base data/cards.full.json>",
  "expected_before": 1496,
  "expected_after": 1497,
  "output_updated": "2026-08-28T22:30:00+09:00",
  "operations": {
    "add": [
      "2026-08-28_KR_01"
    ],
    "update": [
      "2026-08-20_KR_01"
    ],
    "id_migration": [
      {
        "old_id": "2024-04-03_KR_01",
        "new_id": "2024-04-02_KR_01",
        "reason": "representative event date correction"
      }
    ]
  }
}
```

`expected_after = expected_before + operations.add.length`. ID migrations are strictly one-to-one and count-neutral.

## What CI proves

`validate_manual_direct_add.mjs` locks the manifest to the exact base commit and canonical blob, then checks that:

1. lost IDs equal the declared `id_migration.old_id` set;
2. introduced IDs equal `add + id_migration.new_id`;
3. every declared update existed before and after and actually changed;
4. every undeclared existing card is byte-equivalent as JSON;
5. an ID migration retains stable identity evidence (source-spec, source URL, or title overlap);
6. no new dangling `related` edge is introduced;
7. canonical count and `updated` match the manifest;
8. lean remains an exact deterministic projection of canonical full.

For a declared ID migration only, the ordinary `validate_cards.mjs` deletion guard is run with its existing `CARDS_ALLOW_DELETE=1` escape hatch. That exception is safe here because the direct-add validator has already proven the exact old→new one-to-one migration. Ordinary direct adds do not receive that exception.

## Operating rule

Use the full governed `card-run` whenever Stage A/B/C artifacts are part of the publication claim. Use `manual_direct_add_v1` when the editorial/evidence decision is already complete and the remaining job is a bounded canonical mutation.
