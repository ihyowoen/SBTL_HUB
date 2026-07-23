#!/usr/bin/env python3
"""Validate publication/event/representative-date roles and freshness backstops."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

from card_audit_utils import parse_date


def collect_cards(payload: Any):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("cards"), list):
        return payload["cards"]
    output = []
    if isinstance(payload, dict):
        for value in payload.values():
            if isinstance(value, list):
                output.extend(
                    item for item in value
                    if isinstance(item, dict) and "date" in item
                )
    return output


def load_ids(path: str | None) -> set[str] | None:
    if path is None:
        return None
    source = Path(path)
    if source.suffix.lower() == ".csv":
        rows = csv.DictReader(source.open(encoding="utf-8-sig"))
        return {
            str(value)
            for row in rows
            for value in [row.get("assigned_id") or row.get("id") or row.get("card_id")]
            if value
        }
    payload = json.loads(source.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return {str(value) for value in payload}
    if isinstance(payload, dict):
        for key in ("ids", "new_ids", "production_ids"):
            if isinstance(payload.get(key), list):
                return {str(value) for value in payload[key]}
    raise ValueError("ID file must be a list, ids[] JSON, or CSV")


def relation_type(card: dict[str, Any], role: dict[str, Any]) -> str | None:
    lineage = card.get("related_lineage")
    if isinstance(lineage, dict) and lineage.get("relation_type"):
        return str(lineage["relation_type"])
    if role.get("relation_type"):
        return str(role["relation_type"])
    return None


def fresh_anchor(card: dict[str, Any], role: dict[str, Any]) -> str | None:
    lineage = card.get("related_lineage")
    if isinstance(lineage, dict) and lineage.get("fresh_follow_up_anchor"):
        return str(lineage["fresh_follow_up_anchor"])
    if role.get("fresh_follow_up_anchor"):
        return str(role["fresh_follow_up_anchor"])
    return None


def check_card(card: dict[str, Any], require_date_role: bool):
    role = card.get("date_role") or card.get("date_role_alignment")
    errors = []
    if role is None:
        if require_date_role:
            errors.append("missing date_role")
        return errors
    if not isinstance(role, dict):
        return ["date_role must be an object"]

    representative = role.get("representative_date")
    event = role.get("event_date")
    publication_dates = role.get("publication_dates") or role.get("source_publication_dates") or []

    if not representative or parse_date(representative) is None:
        errors.append("representative_date is required and must be YYYY-MM-DD")
    elif card.get("date") != representative:
        errors.append("card.date does not equal representative_date")
    if not event or parse_date(event) is None:
        errors.append("event_date is required and must be YYYY-MM-DD")
    if not isinstance(publication_dates, list) or not publication_dates:
        errors.append("publication_dates[] is required")
    else:
        for value in publication_dates:
            if parse_date(value) is None:
                errors.append(f"invalid publication date: {value}")

    if role.get("earliest_same_event_date_checked") is not True:
        errors.append("earliest_same_event_date_checked must be true")
    if not role.get("event_date_source_url") or not role.get("event_date_source_quote"):
        errors.append("event-date source URL and quote are required")
    if relation_type(card, role) == "distinct_follow_up" and not fresh_anchor(card, role):
        errors.append("distinct_follow_up requires fresh_follow_up_anchor")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--require-date-role", action="store_true")
    parser.add_argument("--id-file", "--new-id-file", dest="id_file")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    rows = collect_cards(payload)
    selected = load_ids(args.id_file)
    if selected is not None:
        rows = [card for card in rows if str(card.get("id", "")) in selected]

    findings = []
    for card in rows:
        errors = check_card(card, args.require_date_role)
        if errors:
            findings.append({
                "id": card.get("id") or card.get("source_spec_id") or card.get("spec_id"),
                "errors": errors,
            })

    result = {
        "status": "PASS" if not findings else "FAIL",
        "cards_checked": len(rows),
        "finding_count": len(findings),
        "findings": findings,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
