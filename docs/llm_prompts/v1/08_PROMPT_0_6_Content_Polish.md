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

Determine the effective upstream value of each field using the nearest **non-empty normalized visible copy** in this order:

`0.5 → 0.4 → Stage C`.

A field omitted, null, empty, or presentation-only-empty at 0.5 or 0.4 is therefore **not** allowed to mask an earlier substantive copy and is not automatically a new 0.6 change when the same copy already existed at Stage C.

A passing V5+ 0.6 item must record `content_enrichment_audit`. Its `changed_fields` must equal the actual governed visible-copy delta calculated against that effective upstream baseline.

Whitespace-only and presentation-markup-only differences (for example Markdown emphasis/link wrappers or HTML emphasis tags) do not count as substantive enrichment. Removing, nulling, or emptying an upstream governed field also does not count as enrichment and must fail closed.

The visible copy carried by the applied formal operation must match the audited 0.6 governed fields. A throwaway 0.6 edit that is not actually materialized by the operation is invalid.

If at least one governed field changed, `no_change_required` must be `false`. A raw string delta alone is insufficient: at least one Deep Summary dimension must be evidence-supported, `dimension_evidence` must bind every true dimension to concrete governed visible field(s) and upstream evidence reference(s), and at least one supported dimension must bind to a field that actually changed.

For formal full-run validation, that changed-field binding must also show a **newly added/deepened machine-detectable signal versus the effective upstream copy** for the claimed dimension: a new quantitative anchor; a new prior-state marker; a new execution/stage/status marker; a new boundary/uncertainty marker; a new transmission-path marker; or a new next-watchpoint marker. A terminology-only synonym rewrite that preserves the same state/number/boundary/transmission/watchpoint information does not qualify. This check is fail-closed and is not a character-count or minimum-length rule.

If none of the governed fields changed, `content_enriched=true` is allowed only as a narrow exception when all of the following are true:

- `no_change_required=true`;
- `no_change_reason` is explicit and non-empty;
- `density_audit.status="PASS"`;
- all six Deep Summary dimensions are audited as booleans;
- `supported_dimension_count` is a non-boolean integer that exactly matches the true dimensions;
- at least four dimensions are evidence-supported, including `changed_state`;
- `evidence_notes` is non-empty and explains why the unchanged copy is already sufficiently decision-useful;
- every true density dimension is bound through `dimension_evidence` to at least one non-empty governed visible field and at least one concrete evidence token already present in the bound upstream B/C/0.5 evidence chain; Prompt 0.6 may not introduce a new source token solely to justify density.

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
      "dimension_evidence": {
        "prior_state": {
          "fields": ["fact"],
          "evidence_refs": ["<fact_source source_id>"]
        },
        "changed_state": {
          "fields": ["fact"],
          "evidence_refs": ["<fact_source source_id>"]
        },
        "quantitative_anchor": {
          "fields": ["fact"],
          "evidence_refs": ["<fact_source source_id>"]
        },
        "transmission_path": {
          "fields": ["fact"],
          "evidence_refs": ["<fact_source source_id>"]
        }
      }
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

Explicit historical `PROMPT_0_6_V4_*` artifacts remain valid historical records. In a formal card run, the applicable 0.6 contract is resolved from the Prompt 0.6 file stored at the run's locked `base_main_commit_sha`; an item-level version label cannot downgrade a V5+ locked baseline to V4. A standalone checker supplied with a locked base must fail closed if that prompt file/version cannot be resolved; it may not trust a self-declared V4 label in that case. The new structured audit contract applies to V5+ and fail-closed unversioned new artifacts.
