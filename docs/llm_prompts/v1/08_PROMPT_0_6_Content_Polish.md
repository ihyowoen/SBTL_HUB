# Prompt 0.6 — Content, Terminology & Strategic Read-Through V4

**Status:** `ACTIVE_CANONICAL`  
**Version:** `PROMPT_0_6_V4_20260901`

Use only evidence-complete/source-claim-covered candidates. Improve title, sub, fact, gate, implication, terminology, density, strategic read-through, and decision-useful context inside the verified evidence boundary.

Check amount/capacity/timing/location/counterparty/stage/policy scope/effective dates, what changed versus prior state, and direct/indirect/conditional/background/no-direct SBTL relevance without manufacturing a pouch-film link.

Do not create facts, upgrade stage, change Related edges, change representative date without evidence route, or convert targets into outcomes. Preserve selection-route package, `related_lineage`, date role, source audit, fact sources, and claim coverage.

## Machine output contract

A passing Prompt 0.6 artifact emits the **single combined production bucket** `content_enriched_and_language_polished`. Do not emit `content_enriched` and `language_terminology_polished` as separate passing buckets.

Each item in `content_enriched_and_language_polished[]` must preserve the required lineage/source/date fields and set both component attestations:

```json
{
  "source_spec_id": "<upstream source spec id>",
  "content_enriched": true,
  "language_terminology_polished": true,
  "related_lineage": {},
  "date_role": {},
  "source_diversity_status": "<preserved upstream status>"
}
```

Only place an item in the combined passing bucket after both content enrichment and terminology/language consistency checks pass. If either component is unresolved, keep the item outside the passing bucket and route it to the earliest responsible repair stage.