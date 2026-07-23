#!/usr/bin/env python3
"""Validate publication/event/representative-date roles and freshness backstops."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from card_audit_utils import parse_date


def cards(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("cards"), list):
        return payload["cards"]
    output = []
    if isinstance(payload, dict):
        for value in payload.values():
            if isinstance(value, list):
                output.extend(item for item in value if isinstance(item, dict) and "date" in item)
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--require-date-role", action="store_true")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    rows = cards(payload)
    findings = []
    for card in rows:
        cid = card.get("id") or card.get("source_spec_id") or card.get("spec_id")
        role = card.get("date_role") or card.get("date_role_alignment")
        errors = []
        if role is None:
            if args.require_date_role:
                errors.append("missing date_role")
        elif not isinstance(role, dict):
            errors.append("date_role must be an object")
        else:
            representative = role.get("representative_date")
            event = role.get("event_date")
            if representative and card.get("date") != representative:
                errors.append("card.date does not equal representative_date")
            if event and parse_date(event) is None:
                errors.append("invalid event_date")
            if role.get("earliest_same_event_date_checked") is not True:
                errors.append("earliest_same_event_date_checked must be true")
            if role.get("relation_type") == "distinct_follow_up" and not role.get("fresh_follow_up_anchor"):
                errors.append("follow-up requires fresh_follow_up_anchor")
            if not role.get("event_date_source_url") or not role.get("event_date_source_quote"):
                errors.append("event-date source URL and quote are required")
        if errors:
            findings.append({"id": cid, "errors": errors})

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
