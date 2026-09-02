# Card ID Standard V2

**Status:** `ACTIVE_CANONICAL`  
**Version:** `CARD_ID_STANDARD_V2_20260829`

## 1. Standard format

New production IDs use:

`YYYY-MM-DD_REGION_NN`

- date = representative **event date**, not article publication date;
- region = `KR | US | CN | JP | EU | GL` and must match the card region;
- `NN` = two-digit sequence within the `(date, region)` group.

## 2. Representative event date

Use the date of the event actually represented by the card: signing, approval, publication/effect where legally operative as appropriate, construction, production, shipment, results event, etc. Do not use a later re-report date merely because it is newer.

The evidence package must state date role and supporting source.

## 3. Region

Region is the direct event arena, not media nationality or company domicile by default.

- event in KR/US/CN/JP → that region;
- EU institution or European allowed-surface event → EU;
- equally material multi-region event, global event, or event outside the badge set → GL.

Specific policy/project facts may require a more precise jurisdiction in visible text even when badge region is GL.

## 4. NN allocation

Before IDs are first committed for a current batch, rank new cards within the same `(date, region)` by `top → high → mid`, then editorial importance, and assign unused NN values deterministically.

**No retroactive renumbering merely to restore priority order.** Once an ID is on main, a later-discovered same-date card takes a new unused NN. Priority ordering governs initial allocation, not historical ID reshuffling.

## 5. Identity immutability and correction

ID is identity, not a display sort key. Existing IDs are preserved by default.

A proven representative-event-date/region/ID factual error may be corrected only through an explicitly governed one-to-one `id_migration` path that:

- names old and new IDs;
- provides a reason/evidence basis;
- preserves stable event identity;
- updates affected references where required;
- keeps count neutral;
- passes collision and Related checks.

A correction is not permission for cosmetic renumbering.

## 6. Related

Do not hard-code predecessor IDs in visible prose as the relation mechanism. Production lineage uses `related[]` under `RELATED_LIFECYCLE_CONTRACT.md`. Shared topic/actor does not create an ID relation.

## 7. Ordering

Frontend/editorial chronology uses card `date`, not lexical ID order. Canonical inventory remains latest-first under the active card validators.

## 8. Legacy

Legacy IDs already on main are preserved unless an explicit governed factual correction is authorized. New-card rules are not a mandate for retroactive bulk renaming.