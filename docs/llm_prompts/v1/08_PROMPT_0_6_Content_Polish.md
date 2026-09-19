# Prompt 0.6 — Content, Terminology & Strategic Read-Through V5

**Status:** `ACTIVE_CANONICAL`  
**Version:** `PROMPT_0_6_V5_20260919`

Use only evidence-complete/source-claim-covered candidates. Improve title, sub, fact, gate, implication, terminology, density, strategic read-through, and decision-useful context inside the verified evidence boundary.

Check amount/capacity/timing/location/counterparty/stage/policy scope/effective dates, what changed versus prior state, and direct/indirect/conditional/background/no-direct SBTL relevance without manufacturing a pouch-film link.

Do not create facts, upgrade stage, change Related edges, change representative date without evidence route, or convert targets into outcomes. Preserve selection-route package, `related_lineage`, date role, source audit, fact sources, and claim coverage.

## Deep Summary rule

Content enrichment is a **substantive visible-copy transition**, not a boolean attestation.

For each passing candidate, evaluate the evidence-supported Deep Summary dimensions below. Include only dimensions supported by the verified upstream record:

1. prior state;
2. changed/current state;
3. quantitative anchor;
4. boundary, caveat, or remaining uncertainty;
5. industry transmission path;
6. next confirmation number, milestone, or stage.

Do not lengthen copy merely to satisfy a density target. Concision is allowed when the evidence is narrow.

## Visible-copy delta rule

The governed content fields are:

`sub`, `gate`, `fact`, `implication`.

Determine the effective upstream value of each field using the nearest available ordinary-stage copy in this order:

`0.5 → 0.4 → Stage C`.

A field omitted by 0.5 or 0.4 is therefore **not** automatically a new 0.6 change when the same copy already existed at Stage C.

A passing V5+ 0.6 item must record `content_enrichment_audit`. Its `changed_fields` must equal the actual governed visible-copy delta calculated against that effective upstream baseline.

Whitespace-only/formatting-only differences do not count as substantive enrichment. Removing, nulling, or emptying an upstream governed field also does not count as enrichment and must fail closed.

The visible copy carried by the applied formal operation must match the audited 0.6 governed fields. A throwaway 0.6 edit that is not actually materialized by the operation is invalid.

If at least one governed field changed, `no_change_required` must be `false`.

If none of the governed fields changed, `content_enriched=true` is allowed only as a narrow exception when all of the following are true:

- `no_change_required=true`;
- `no_change_reason` is explicit and non-empty;
- `density_audit.status="PASS"`;
- all six Deep Summary dimensions are audited as booleans;
- `supported_dimension_count` exactly matches the true dimensions;
- at least four dimensions are evidence-supported, including `changed_state`;
- `evidence_notes` is non-empty and explains why the unchanged copy is already sufficiently decision-useful;
- every true density dimension is bound through `dimension_evidence` to at least one non-empty governed visible field and at least one concrete upstream evidence reference already present in the 0.6 evidence package.

Title-only or terminology-only edits do not satisfy the content-enrichment delta.

## Machine output contract

A passing Prompt 0.6 artifact emits the **single combined production bucket** `content_enriched_and_language_polished`. Do not emit `content_enriched` and `language_terminology_polished` as separate passing buckets.

Each item in `content_enriched_and_language_polished[]` must preserve the required lineage/source/date fields and set both component attestations plus the enrichment audit:

```json
{
  "source_spec_id": "<upstream source spec id>",
  "content_enriched": true,
  "language_terminology_polished": true,
  "content_enrichment_audit": {
    "baseline_strategy": "nearest_upstream_visible_copy_0.5_0.4_C",
    "changed_fields": ["fact"],
    "no_change_required": false,
    "no_change_reason": "",
    "density_audit": {
      "status": "PASS",
      "dimensions": {
        "prior_state": true,
        "changed_state": true,
        "quantitative_anchor": true,
        "boundary_or_uncertainty": false,
        "transmission_path": true,
        "next_watchpoint": false
      },
      "supported_dimension_count": 4,
      "evidence_notes": "Brief evidence-bounded explanation of the supported dimensions.",
      "dimension_evidence": {}
    }
  },
  "related_lineage": {},
  "date_role": {},
  "source_diversity_status": "<preserved upstream status>"
}
```

Only place an item in the combined passing bucket after content enrichment, delta/no-change audit, density audit, and terminology/language consistency checks pass. If any component is unresolved, keep the item outside the passing bucket and route it to the earliest responsible repair stage.


### Zero-delta exception mapping example

When `changed_fields=[]`, `density_audit.dimension_evidence` must contain exactly the dimensions marked `true`. Each entry has a non-empty `fields[]` subset of `sub/gate/fact/implication` and non-empty `evidence_refs[]` that resolve to the preserved 0.6 evidence package, for example:

```json
{
  "changed_state": {
    "fields": ["fact"],
    "evidence_refs": ["<fact_source source_id>"]
  },
  "quantitative_anchor": {
    "fields": ["fact"],
    "evidence_refs": ["<fact_source source_id>"]
  }
}
```

Explicit historical `PROMPT_0_6_V4_*` artifacts remain valid historical records; the new audit contract applies to V5+ and unversioned new artifacts.
