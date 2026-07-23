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
COLLECTION_SEGMENTS = {
    "article", "articles", "blog", "blogs", "media", "news", "newsroom",
    "press", "press-release", "press-releases", "publication", "publications",
    "resource", "resources", "stories", "updates",
}
LISTING_PREFIX_SEGMENTS = {
    "archive", "archives", "category", "categories", "search", "tag", "tags",
    "topic", "topics",
}
LISTING_CHILD_SEGMENTS = LISTING_PREFIX_SEGMENTS | {"page", "pages"}
SEARCH_QUERY_KEYS = {"q", "query", "s", "search", "keyword", "keywords"}
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
    if not isinstance(url, str) or not url.strip():
        return ""
    parsed = urlparse(url.strip())
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        return ""
    host = parsed.netloc.lower()
    for prefix in ("www.", "m.", "mobile."):
        if host.startswith(prefix):
            host = host[len(prefix):]
    return host


def _is_listing_or_search_endpoint(url: str) -> bool:
    if not isinstance(url, str) or not url.strip():
        return True
    parsed = urlparse(url.strip())
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        return True

    path = (parsed.path or "").strip()
    segments = [segment.lower() for segment in path.split("/") if segment]
    query_keys = {
        key.lower()
        for key, _ in parse_qsl(parsed.query, keep_blank_values=True)
    }

    if not segments:
        return not parsed.query or bool(query_keys & SEARCH_QUERY_KEYS)
    if bool(LANDING.match(path)) and not parsed.query:
        return True

    first = segments[0]
    if first in LISTING_PREFIX_SEGMENTS:
        return True
    if len(segments) == 1 and first in COLLECTION_SEGMENTS:
        return True
    if (
        first in COLLECTION_SEGMENTS
        and len(segments) >= 2
        and segments[1] in LISTING_CHILD_SEGMENTS
    ):
        return True
    if (
        query_keys & SEARCH_QUERY_KEYS
        and first in (COLLECTION_SEGMENTS | LISTING_PREFIX_SEGMENTS)
    ):
        return True
    return False


def canonical_url(url: str) -> str:
    if not isinstance(url, str) or not url.strip():
        return ""
    parsed = urlparse(url.strip())
    host = canonical_domain(url)
    if not host or _is_listing_or_search_endpoint(url):
        return ""
    query = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if not key.lower().startswith("utm_")
        and key.lower() not in TRACKING_KEYS
    ]
    path = re.sub(r"/+$", "", parsed.path)
    return urlunsplit(("https", host, path, urlencode(sorted(query)), ""))


def is_landing_page(url: str) -> bool:
    """Return true for non-durable home, listing, category, tag or search endpoints."""
    return _is_listing_or_search_endpoint(url)


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


def source_metadata_blob(source: dict[str, Any]) -> str:
    keys = (
        "source_name", "source_type", "source_kind", "source_origin_type",
        "source_role", "publisher_type", "origin_type", "official_source_type",
        "source_category", "source_contribution", "claim",
        "source_owner_id", "source_owner_id_normalized",
    )
    return " ".join(str(source.get(key, "")).lower() for key in keys)


def load_owner_registry(path: str | Path | None) -> dict[str, list[dict[str, Any]]]:
    mapping: dict[str, list[dict[str, Any]]] = {}
    if path is None:
        return mapping
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    for rule in payload.get("rules", []):
        owner = str(rule.get("owner_id", "")).strip()
        if not owner:
            continue
        normalized_rule = {
            "owner_id": owner,
            "requires_metadata_contains_any": [
                str(value).lower()
                for value in rule.get("requires_metadata_contains_any", [])
                if value
            ],
            "reason": rule.get("reason", ""),
        }
        for domain in rule.get("domains", []):
            normalized = canonical_domain("https://" + str(domain))
            if normalized:
                mapping.setdefault(normalized, []).append(normalized_rule)
    return mapping


def source_owner(
    source: dict[str, Any],
    registry: dict[str, list[dict[str, Any]]],
) -> str:
    source_url = str(source.get("source_url", ""))
    canonical = canonical_url(source_url)
    if not canonical:
        return ""
    domain = canonical_domain(canonical)
    blob = source_metadata_blob(source)
    for rule in registry.get(domain, []):
        required = rule.get("requires_metadata_contains_any", [])
        if not required or any(value in blob for value in required):
            return str(rule["owner_id"])
    return (
        str(source.get("source_owner_id_normalized") or "").strip()
        or str(source.get("source_owner_id") or "").strip()
        or domain
    )


def usable_sources(card: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        source
        for source in card.get("fact_sources", [])
        if isinstance(source, dict) and source.get("evidence_role") != "not_used"
    ]


def source_audit_measure(
    card: dict[str, Any],
    registry: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    sources = usable_sources(card)
    visible = [source for source in sources if is_visible_source(source)]

    canonical_urls = {
        value
        for source in sources
        if (value := canonical_url(str(source.get("source_url", ""))))
    }
    domains = {
        value
        for canonical in canonical_urls
        if (value := canonical_domain(canonical))
    }
    owners = {
        value
        for source in visible
        if (value := source_owner(source, registry))
    }
    visible_urls = {
        value
        for source in visible
        if (value := canonical_url(str(source.get("source_url", ""))))
    }
    missing_source_url_count = sum(
        not canonical_url(str(source.get("source_url", "")))
        for source in sources
    )
    missing_visible_source_url_count = sum(
        not canonical_url(str(source.get("source_url", "")))
        for source in visible
    )

    return {
        "source_evidence_entry_count": len(sources),
        "source_unique_url_count": len(canonical_urls),
        "source_unique_domain_count": len(domains),
        "source_independent_owner_count": len(owners),
        "visible_source_url_count": len(visible_urls),
        "missing_source_url_count": missing_source_url_count,
        "missing_visible_source_url_count": missing_visible_source_url_count,
        "canonical_urls": sorted(canonical_urls),
        "canonical_domains": sorted(domains),
        "independent_owners": sorted(owners),
    }


def card_identifier(card: dict[str, Any]) -> str:
    return str(card.get("id") or card.get("card_id") or "").strip()


def select_scoped_cards(
    cards: Iterable[dict[str, Any]],
    selected_ids: set[str] | None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = list(cards)
    if selected_ids is None:
        return rows, {
            "applied": False,
            "status": "NOT_APPLIED",
            "requested_count": None,
            "matched_count": len(rows),
            "missing_ids": [],
            "errors": [],
        }

    requested = {str(value).strip() for value in selected_ids if str(value).strip()}
    available = {card_identifier(card) for card in rows if card_identifier(card)}
    matched = requested & available
    missing = sorted(requested - available)
    errors: list[str] = []
    if not requested:
        errors.append("ID scope is empty")
    elif not matched:
        errors.append("ID scope matched zero cards")
    if missing:
        errors.append(f"ID scope has {len(missing)} unmatched ID(s)")

    selected_rows = [card for card in rows if card_identifier(card) in matched]
    return selected_rows, {
        "applied": True,
        "status": "PASS" if not errors else "FAIL",
        "requested_count": len(requested),
        "matched_count": len(matched),
        "missing_ids": missing,
        "errors": errors,
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
