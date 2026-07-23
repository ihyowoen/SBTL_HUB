#!/usr/bin/env python3
"""Shared URL, source-owner, diversity, date and Related helpers."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import parse_qsl, urlencode, urlparse, urlunsplit

TRACKING_KEYS = {"fbclid", "gclid", "amp", "output"}
LANDING = re.compile(r"^/?$|^/(index|home|main)\.?\w*/?$", re.I)
VISIBLE_SUPPORT_FIELDS = {"title", "sub", "gate", "fact", "implication"}
USABLE_QUOTE_STATUSES = {
    "body_quote_verified",
    "official_material_quote_verified",
    "document_quote_verified",
}
ALLOWED_RELATION_TYPES = {
    "same_event_duplicate",
    "distinct_follow_up",
    "existing_card_reinforcement",
    "program_lineage",
    "new_unrelated_event",
    "uncertain_needs_review",
}


def canonical_domain(url: str) -> str:
    host = urlparse(url or "").netloc.lower()
    for prefix in ("www.", "m.", "mobile."):
        if host.startswith(prefix):
            host = host[len(prefix):]
    return host


def canonical_url(url: str) -> str:
    parsed = urlparse(url or "")
    host = canonical_domain(url)
    query = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if not key.lower().startswith("utm_")
        and key.lower() not in TRACKING_KEYS
    ]
    path = re.sub(r"/+$", "", parsed.path)
    return urlunsplit(("https", host, path, urlencode(sorted(query)), ""))


def is_landing_page(url: str) -> bool:
    if not isinstance(url, str) or not url:
        return True
    parsed = urlparse(url.strip())
    return (
        not parsed.scheme
        or not parsed.netloc
        or bool(LANDING.match((parsed.path or "").strip()) and not parsed.query)
    )


def is_visible_source(source: dict[str, Any]) -> bool:
    if source.get("supporting_context_only_not_visible_claim_support") is True:
        return False
    if source.get("evidence_role") in {
        "primary_event_evidence",
        "secondary_event_evidence",
    }:
        return True
    supports = source.get("supports")
    return isinstance(supports, list) and bool(VISIBLE_SUPPORT_FIELDS & set(supports))


def load_owner_registry(path: str | Path | None) -> dict[str, str]:
    mapping: dict[str, str] = {}
    if path is None:
        return mapping
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    for rule in payload.get("rules", []):
        owner = str(rule.get("owner_id", "")).strip()
        for domain in rule.get("domains", []):
            if owner and domain:
                mapping[canonical_domain("https://" + domain)] = owner
    return mapping


def source_owner(source: dict[str, Any], registry: dict[str, str]) -> str:
    domain = canonical_domain(str(source.get("source_url", "")))
    return (
        registry.get(domain)
        or str(source.get("source_owner_id_normalized") or "").strip()
        or str(source.get("source_owner_id") or "").strip()
        or domain
    )


def usable_sources(card: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        source
        for source in card.get("fact_sources", [])
        if isinstance(source, dict) and source.get("evidence_role") != "not_used"
    ]


def source_audit_measure(card: dict[str, Any], registry: dict[str, str]) -> dict[str, Any]:
    sources = usable_sources(card)
    visible = [source for source in sources if is_visible_source(source)]
    canonical_urls = {canonical_url(str(source.get("source_url", ""))) for source in sources}
    domains = {canonical_domain(str(source.get("source_url", ""))) for source in sources}
    owners = {source_owner(source, registry) for source in visible}
    return {
        "source_evidence_entry_count": len(sources),
        "source_unique_url_count": len(canonical_urls),
        "source_unique_domain_count": len(domains),
        "source_independent_owner_count": len(owners),
        "visible_source_url_count": len({str(source.get("source_url", "")) for source in visible}),
        "canonical_urls": sorted(canonical_urls),
        "canonical_domains": sorted(domains),
        "independent_owners": sorted(owners),
    }


def dedupe(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            output.append(value)
    return output


def parse_date(value: Any):
    from datetime import date

    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None
