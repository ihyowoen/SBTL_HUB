# Source Audit Contract

Version: `SOURCE_AUDIT_V1_20260723`

This contract is authoritative for source-derived counters, URL durability, editorial-owner normalization, diversity status, discovery ledgers and resolution metadata.

It supersedes conflicting source-count definitions in earlier workflow documents.

## 1. Four measures are different

```text
source_evidence_entry_count
= count of usable fact_sources rows

source_unique_url_count
= count of unique canonical article/document URLs

source_unique_domain_count
= count of distinct canonical URL hostnames

source_independent_owner_count
= count of distinct editorial owners or syndication clusters among visible-claim sources
```

Do not copy one measure into another.

Examples:

- three claim rows from one article: rows `3`, URLs `1`, domains `1`, owners `1`;
- `pv-magazine-india.com`, `ess-news.com`, `business-standard.com` where the first two share an editorial group: domains `3`, owners `2`;
- an official company release reproduced by two syndication sites without independent reporting: domains may exceed `1`, owner count remains `1`.

## 2. Canonical URL

Canonicalization must:

- normalize scheme to HTTPS for comparison;
- lowercase and normalize hostnames;
- remove `www.`, mobile and AMP host prefixes when appropriate;
- remove fragments and tracking parameters;
- preserve substantive path and query identifiers;
- group duplicate claim rows from the same article.

A claim row is not an independent source.

## 3. Durable evidence endpoint

A visible-claim source must resolve to a durable article, filing, decision, dataset, report, announcement, court document or other item-specific material.

The following are not sufficient evidence endpoints:

- top-level homepage;
- generic newsroom or listing page;
- search result page;
- category page;
- RSS item title without body text;
- navigation redirect that does not preserve the item-specific URL.

When a landing/listing URL is repaired, propagate the durable URL to:

- `urls[]` when it supports visible text;
- `fact_sources[].source_url`;
- `source_discovery_ledger[]`;
- `source_url_resolution.resolution_entries[]`;
- every derived URL/domain/owner count.

## 4. Editorial owner and syndication

Owner normalization must use `validation_data/source_owner_registry.json` and source-specific metadata.

The registry may group domains only when there is a documented basis, such as:

- common editorial ownership;
- wire-service republication;
- official domains controlled by the same source owner;
- copied press release without independent reporting.

Different hostnames are not automatically independent owners. Same owner does not reduce the actual hostname count.

## 5. Visible source

A source counts toward independent-owner diversity only when it supports a visible field or has one of these roles:

- `primary_event_evidence`
- `secondary_event_evidence`
- another role with `supports[]` containing `title`, `sub`, `gate`, `fact` or `implication`

Background-only sources do not satisfy visible-source diversity.

## 6. Allowed diversity status

Every card advancing through Evidence QC must use one of:

- `PASS_MULTI_SOURCE`
- `PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION`
- `HOLD_NEEDS_SOURCE_AUGMENTATION`
- `FAIL_SOURCE_DIVERSITY`

`PASS_SINGLE_SOURCE` is prohibited.

`PASS_MULTI_SOURCE` requires:

- at least two visible canonical source URLs;
- at least two independent editorial owners;
- distinct source contributions;
- a completed `source_discovery_ledger[]`.

A single-source exception requires:

- an official, regulatory, filing, original-data, contracting-party or original-research source;
- bounded discovery completed;
- reason and mitigation/scope limitation;
- claims limited to what the primary source directly supports;
- separate Evidence QC and Final QC approval.

## 7. Source-discovery ledger

Every PASS status must retain a discovery ledger or a durable reference to one. Each used source row must record:

- source URL and canonical URL;
- source name;
- canonical domain;
- editorial owner;
- source role and origin type;
- outcome;
- unique contribution;
- visible fields supported;
- checked timestamp.

Rejected or unavailable sources should remain in the ledger with a reason when they affected the diversity decision.

## 8. Resolution metadata

`source_url_resolution` is derived, never hand-authored.

Requirements:

- `supporting_fact_source_count` equals usable fact-source row count;
- one resolution entry per canonical article/document URL;
- resolution URLs equal the canonical URL set derived from current `fact_sources`;
- each entry records quote match and URL completeness;
- URL propagation is recorded when a source URL changes.

## 9. Recompute triggers

Run `validation_scripts/recompute_source_audit_metadata.py` after any:

- source add/remove;
- evidence-role change;
- source URL repair;
- claim row split/merge;
- source-owner or syndication decision;
- single-source waiver decision;
- revise pass that changes evidence;
- final merge preparation.

Then run `validation_scripts/evidence_qc_v8_check.py` on the current-run card scope.

Do not manually update only the commented card or one counter.

## 10. Stage responsibilities

- Stage B creates source discovery, evidence rows and initial source audit.
- Stage C recomputes independence and locks fact-safe status.
- Prompt 0.5/0.5R performs the hard diversity and claim-coverage gate.
- Prompt 0.6 preserves evidence and source audit.
- Prompt 0.7 reruns the Evidence QC validator before publish-ready.
- Prompt 0.8 reruns source recomputation and validator on the current merge-ID scope.
- Prompt 0.9 verifies source-group/date rendering where production access permits.

## 11. Legacy scope

A strict new validator may expose legacy cards that predate this contract. New-card and legacy remediation scopes must be reported separately.

- current-run cards must pass before merge;
- legacy failures enter a separate remediation manifest;
- do not waive current-run failures because legacy debt exists;
- do not silently rewrite legacy cards during an unrelated new-card merge.
