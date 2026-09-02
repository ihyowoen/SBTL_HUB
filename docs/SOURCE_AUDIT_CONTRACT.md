# Source Audit Contract V2

**Status:** `ACTIVE_CANONICAL`  
**Version:** `SOURCE_AUDIT_V2_20260829`

## 1. Purpose

This contract owns source identity, durable URLs, editorial-owner independence, discovery ledgers, source contributions, source synthesis, single-source exceptions, and all source-derived counters. Other canonical documents must not duplicate these rules.

## 2. Distinct source measures

- `source_evidence_entry_count`: usable evidence rows;
- `source_unique_url_count`: distinct canonical item URLs;
- `source_unique_domain_count`: distinct canonical hostnames;
- `source_independent_owner_count`: distinct editorial owners/syndication clusters among visible-claim sources.

Rows, URLs, domains, and owners are not interchangeable.

## 3. Durable endpoint

Visible-claim evidence resolves to an item-specific article, filing, decision, dataset, report, announcement, court document, tender, transcript, or equivalent durable source. Homepages, search/listing/category pages, RSS titles, snippets, and redirects that lose item identity do not qualify.

When repairing a URL, propagate the canonical URL to all evidence/discovery/resolution metadata and recompute derived counters.

## 4. Canonical URL and owner independence

Canonicalization normalizes comparison-only scheme/host/tracking variants while preserving substantive identifiers. Multiple rows from one article remain one URL/source owner. Syndicated copies or domains under one editorial owner do not create independent owners.

Use the repository owner registry and documented source metadata; never infer independence from hostname count alone.

## 5. Source roles and contributions

Each retained source states its role and unique contribution. Preferred roles are primary/original event evidence, independent event confirmation, and policy/market/operating context when it materially supports visible interpretation.

Generic `corroboration` is not a sufficient contribution description when no unique information is supplied.

Background-only sources do not satisfy visible-claim diversity.

## 6. Diversity states

Allowed Evidence-QC states:

- `PASS_MULTI_SOURCE`;
- `PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION`;
- `HOLD_NEEDS_SOURCE_AUGMENTATION`;
- `FAIL_SOURCE_DIVERSITY`.

`PASS_MULTI_SOURCE` requires at least two visible canonical URLs, at least two independent owners, distinct contributions, and a completed discovery ledger.

A single-source exception requires an authoritative/original source, bounded alternative-source search, bounded claims, explicit reason/scope/mitigation, and downstream Evidence + Final QC approval. A detailed media article alone is not automatically an exception.

## 7. Discovery ledger

Record used, rejected, unavailable, and repaired source candidates that affected the decision, including canonical URL, name/domain/owner, role/origin type, outcome, unique contribution, visible fields supported, and check timestamp.

## 8. Source synthesis

When an additional source materially changes understanding, source-locked information must appear in an appropriate visible field or explicit gate/implication, with synthesis audit. Merely adding URLs is not multi-source synthesis.

## 9. Derived metadata

`source_url_resolution` and all counts are derived from current evidence, not hand-maintained. Recompute after source add/remove, URL repair, role/owner decision, claim-row changes, exception decision, revise pass, and final merge preparation.

## 10. Stage ownership

- Stage B creates discovery/evidence/source audit.
- Stage C recomputes and fact-safe red-teams it.
- 0.5 is the hard source/claim completeness gate.
- 0.6 preserves it unless authorized evidence routing occurs.
- 0.7 reruns applicable source validator.
- 0.8 recomputes on current merge scope.
- 0.9 checks rendered source/date grouping where accessible.

## 11. Legacy isolation

Current-run failures are blockers even if legacy inventory has debt. Legacy source-audit failures belong to separate remediation and are not silently rewritten in unrelated runs.