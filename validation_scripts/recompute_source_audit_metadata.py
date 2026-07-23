#!/usr/bin/env python3
"""Recompute all source-derived audit metadata from current fact_sources.

The command is metadata-only. It never rewrites visible claims or source quotes.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any

from card_audit_utils import (
    USABLE_QUOTE_STATUSES,
    canonical_domain,
    canonical_url,
    is_landing_page,
    load_owner_registry,
    source_audit_measure,
    source_owner,
    usable_sources,
)

PASS_MULTI = "PASS_MULTI_SOURCE"
PASS_SINGLE = "PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION"
HOLD = "HOLD_NEEDS_SOURCE_AUGMENTATION"


def iter_cards(payload: Any):
    if isinstance(payload, list):
        yield from payload
        return
    if not isinstance(payload, dict):
        return
    if isinstance(payload.get("cards"), list):
        yield from payload["cards"]
        return
    for value in payload.values():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict) and ("fact_sources" in item or "title" in item):
                    yield item


def source_is_primary(source: dict[str, Any]) -> bool:
    if source.get("is_official") is True or source.get("is_primary_source") is True:
        return True
    role = str(source.get("evidence_role", "")).lower()
    origin = " ".join(
        str(source.get(key, "")).lower()
        for key in ("source_origin_type", "source_role", "source_type", "source_kind")
    )
    return role in {
        "official_material_evidence",
        "official_source",
        "primary_source",
        "regulatory_filing",
        "original_dataset",
        "primary_event_evidence",
    } or any(
        term in origin
        for term in (
            "official", "government", "regulatory", "filing", "company_primary",
            "contracting_party", "research_institution", "original_data",
        )
    )


def valid_existing_exception(card: dict[str, Any]) -> dict[str, Any] | None:
    for key in ("single_source_exception", "final_qc_single_source_exception"):
        value = card.get(key)
        if isinstance(value, dict) and value.get("allowed") is True and value.get("reason"):
            return deepcopy(value)
    return None


def build_resolution_entries(
    card: dict[str, Any],
    registry: dict[str, list[dict[str, Any]]],
):
    grouped: dict[str, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    for index, source in enumerate(usable_sources(card)):
        grouped[canonical_url(str(source.get("source_url", "")))].append((index, source))
    entries = []
    for canonical, rows in sorted(grouped.items()):
        sources = [source for _, source in rows]
        entries.append({
            "source_url": sources[0].get("source_url"),
            "canonical_complete": bool(canonical) and all(
                source.get("source_url_canonical_complete", True) is True for source in sources
            ),
            "resolved_article_matches_quote": all(
                bool(source.get("source_quote"))
                and source.get("source_quote_status") in USABLE_QUOTE_STATUSES
                and source.get("resolved_article_matches_quote", True) is True
                for source in sources
            ),
            "resolution_basis": (
                "recomputed from current fact_sources; "
                f"indices={','.join(str(index) for index, _ in rows)}; "
                f"owners={';'.join(sorted({source_owner(source, registry) for source in sources}))}"
            ),
            "source_url_propagation_performed": False,
        })
    return entries


def recompute(
    card: dict[str, Any],
    registry: dict[str, list[dict[str, Any]]],
    strict: bool,
):
    before = deepcopy(card)
    sources = usable_sources(card)
    measure = source_audit_measure(card, registry)

    for source in sources:
        source["source_owner_id_normalized"] = source_owner(source, registry)
        source["source_url_canonical_complete"] = bool(canonical_url(str(source.get("source_url", ""))))
        source["resolved_article_matches_quote"] = (
            bool(source.get("source_quote"))
            and source.get("source_quote_status") in USABLE_QUOTE_STATUSES
        )

    for field in (
        "source_evidence_entry_count",
        "source_unique_url_count",
        "source_unique_domain_count",
        "source_independent_owner_count",
    ):
        card[field] = measure[field]

    exception = valid_existing_exception(card)
    if measure["visible_source_url_count"] >= 2 and measure["source_independent_owner_count"] >= 2:
        card["source_diversity_status"] = PASS_MULTI
        card["single_source_exception"] = {"allowed": False, "reason": "not applicable: multi-owner evidence"}
    elif any(source_is_primary(source) for source in sources):
        if exception is None:
            if strict:
                card["source_diversity_status"] = HOLD
                card["single_source_exception"] = {
                    "allowed": False,
                    "reason": "primary single-source candidate lacks an approved bounded-discovery exception",
                }
            else:
                card["source_diversity_status"] = HOLD
        else:
            card["source_diversity_status"] = PASS_SINGLE
            card["single_source_exception"] = exception
    else:
        card["source_diversity_status"] = HOLD

    resolution_entries = build_resolution_entries(card, registry)
    card["source_url_resolution"] = {
        "supporting_fact_source_count": len(sources),
        "canonical_complete": all(entry["canonical_complete"] for entry in resolution_entries),
        "resolved_article_matches_quote": all(
            entry["resolved_article_matches_quote"] for entry in resolution_entries
        ),
        "source_url_propagation_performed": False,
        "resolution_entries": resolution_entries,
    }
    card["source_diversity_measure"] = {
        **measure,
        "status": card["source_diversity_status"],
    }

    generated_ledger = []
    used_canonical_urls = set()
    for entry in resolution_entries:
        canonical = canonical_url(str(entry["source_url"]))
        used_canonical_urls.add(canonical)
        matching = [
            source for source in sources
            if canonical_url(str(source.get("source_url", ""))) == canonical
        ]
        generated_ledger.append({
            "source_url": entry["source_url"],
            "canonical_url": canonical,
            "source_name": " / ".join(
                sorted({str(source.get("source_name", "")) for source in matching})
            ),
            "source_owner": source_owner(matching[0], registry) if matching else "",
            "source_domain": canonical_domain(str(entry["source_url"])),
            "outcome": "used_in_fact_sources",
            "unique_contribution": " | ".join(
                str(source.get("source_contribution") or source.get("claim") or "")
                for source in matching
            ),
            "visible_supports": sorted({
                support
                for source in matching
                for support in (source.get("supports") or [])
            }),
        })

    preserved_discovery_rows = []
    for row in before.get("source_discovery_ledger", []) or []:
        if not isinstance(row, dict):
            continue
        canonical = canonical_url(str(row.get("source_url", "")))
        if row.get("outcome") == "used_in_fact_sources" and canonical in used_canonical_urls:
            continue
        preserved_discovery_rows.append(row)
    card["source_discovery_ledger"] = generated_ledger + preserved_discovery_rows

    landing_hits = [
        str(source.get("source_url"))
        for source in sources
        if is_landing_page(str(source.get("source_url", "")))
    ]
    return before, card, landing_hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--output")
    parser.add_argument("--owner-registry")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    registry = load_owner_registry(args.owner_registry)
    changes = []
    landing = []
    for card in iter_cards(payload):
        before, after, landing_hits = recompute(card, registry, args.strict)
        if before != after:
            changes.append(card.get("id") or card.get("source_spec_id") or card.get("spec_id"))
        landing.extend((card.get("id"), url) for url in landing_hits)

    report = {"cards_changed": len(changes), "landing_page_hits": landing}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.check:
        return 1 if changes or landing else 0
    if not args.output:
        parser.error("--output is required unless --check is used")
    Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
