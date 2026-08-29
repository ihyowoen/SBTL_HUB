# Future Card Standard — Full Schema V2

**Status:** `ACTIVE_CANONICAL`  
**Version:** `FUTURE_CARD_FULL_SCHEMA_V2_20260829`

## 1. Rule

New cards are authored and merged as full-schema cards. `data/cards.full.json` is canonical; lean/public fields are generated downstream.

`FACT_DISCIPLINE.md` governs factual support. `SOURCE_AUDIT_CONTRACT.md` governs source metadata. This file owns card shape/taxonomy only.

## 2. Core card fields

Every new card includes at minimum the current machine-required form of:

```json
{
  "id": "YYYY-MM-DD_REGION_NN",
  "region": "KR|US|CN|JP|EU|GL",
  "date": "YYYY-MM-DD",
  "cat": "Battery|ESS|Materials|EV|Charging|Policy|Manufacturing|AI|Robotics|PowerGrid|SupplyChain|Other",
  "sub_cat": "...",
  "signal": "top|high|mid",
  "title": "...",
  "sub": "...",
  "gate": "...",
  "fact": "...",
  "implication": ["..."],
  "urls": ["https://..."],
  "related": [],
  "fact_sources": []
}
```

Current machine schema/validators may require additional audit/provenance fields for newly authored cards. Those fields must be emitted by their owning stage/contract; they do not become competing card-shape authorities.

## 3. Category taxonomy

New cards use exactly one primary category from:

`Battery | ESS | Materials | EV | Charging | Policy | Manufacturing | AI | Robotics | PowerGrid | SupplyChain | Other`

Use the dominant event domain. Secondary dimensions belong in `sub_cat`/content, not compound primary categories. `Other` is rare.

Legacy categories already on main are preserved as historical data and are not valid templates for new cards.

## 4. Region taxonomy

Region follows the direct event arena under `CARD_ID_STANDARD.md`. Media nationality is irrelevant. Multi-region/global/out-of-badge events use GL.

## 5. Visible fields

Visible fields are concise Korean strategy-note copy with standard industry acronyms/ASCII where appropriate. Do not put internal workflow language, raw stage names, evidence grades, fetch/debug terms, or unsupported certainty into public-facing copy.

Original-language quotations remain in evidence fields, not forced into the visible Korean-only convention.

## 6. `related[]`

Contains only final production IDs representing direct auditable lineage. It is empty for a new unrelated event. Provisional candidate identifiers may exist only in pre-0.8 artifacts, never final canonical `related[]`.

## 7. `fact_sources[]`

Non-empty for new publishable cards and must satisfy Fact Discipline and Source Audit. URLs alone are not evidence rows.

## 8. State/audit metadata

Stage selection/evidence/lineage/QC metadata belongs in governed artifacts and, where current machine schema requires durable card-level provenance, in explicitly named non-visible fields. Do not add uncontrolled top-level fields merely because a run produced them.

## 9. Legacy isolation

Do not rewrite legacy cards to match the latest new-card schema during an unrelated ordinary run. Current-run cards pass current standards; legacy debt is separately remediated.