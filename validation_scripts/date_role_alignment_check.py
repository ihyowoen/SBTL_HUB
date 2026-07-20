#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STANDARD_ID_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})_(KR|US|CN|JP|EU|GL)_")


def valid_iso_date(value: Any) -> tuple[bool, str | None]:
    if not isinstance(value, str) or not DATE_RE.fullmatch(value):
        return False, "invalid_shape"
    try:
        date.fromisoformat(value)
    except ValueError:
        return False, "invalid_calendar_date"
    return True, None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cards_json")
    args = parser.parse_args()

    try:
        data = json.loads(Path(args.cards_json).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({
            "status": "VALIDATOR_INPUT_ERROR",
            "error": str(exc),
        }, ensure_ascii=False, indent=2))
        return 3

    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    for card in data.get("cards", []) or []:
        if not isinstance(card, dict):
            errors.append({"code": "INVALID_CARD_RECORD"})
            continue

        card_id = card.get("id")
        card_date = card.get("date")
        region = card.get("region")
        card_date_valid, card_date_reason = valid_iso_date(card_date)
        if not card_date_valid:
            errors.append({
                "id": card_id,
                "code": "INVALID_EVENT_DATE",
                "value": card_date,
                "reason": card_date_reason,
            })

        match = STANDARD_ID_RE.match(card_id or "")
        if match:
            id_date, id_region = match.groups()
            id_date_valid, id_date_reason = valid_iso_date(id_date)
            if not id_date_valid:
                errors.append({
                    "id": card_id,
                    "code": "INVALID_ID_DATE",
                    "value": id_date,
                    "reason": id_date_reason,
                })
            if card_date_valid and id_date != card_date:
                errors.append({
                    "id": card_id,
                    "code": "ID_EVENT_DATE_MISMATCH",
                })
            if id_region != region:
                errors.append({
                    "id": card_id,
                    "code": "ID_REGION_MISMATCH",
                    "id_region": id_region,
                    "card_region": region,
                })
        elif isinstance(card_id, str):
            warnings.append({
                "id": card_id,
                "code": "LEGACY_ID_FORMAT_NOT_DATE_CHECKED",
            })

        fingerprint = card.get("event_fingerprint", {})
        if isinstance(fingerprint, dict):
            fingerprint_date = fingerprint.get("event_date")
            if fingerprint_date is not None:
                fp_valid, fp_reason = valid_iso_date(fingerprint_date)
                if not fp_valid:
                    errors.append({
                        "id": card_id,
                        "code": "INVALID_FINGERPRINT_EVENT_DATE",
                        "value": fingerprint_date,
                        "reason": fp_reason,
                    })
                elif card_date_valid and fingerprint_date != card_date:
                    errors.append({
                        "id": card_id,
                        "code": "FINGERPRINT_EVENT_DATE_MISMATCH",
                    })

        for source in card.get("fact_sources", []) or []:
            if not isinstance(source, dict):
                continue
            source_ref = source.get("source_url") or source.get("url")
            source_date = source.get("source_published_date")
            visible_date = source.get("visible_quote_date")

            source_date_valid = source_date is None
            visible_date_valid = visible_date is None

            if source_date is not None:
                source_date_valid, reason = valid_iso_date(source_date)
                if not source_date_valid:
                    errors.append({
                        "id": card_id,
                        "code": "INVALID_SOURCE_PUBLISHED_DATE",
                        "source": source_ref,
                        "value": source_date,
                        "reason": reason,
                    })

            if visible_date is not None:
                visible_date_valid, reason = valid_iso_date(visible_date)
                if not visible_date_valid:
                    errors.append({
                        "id": card_id,
                        "code": "INVALID_VISIBLE_QUOTE_DATE",
                        "source": source_ref,
                        "value": visible_date,
                        "reason": reason,
                    })

            if (
                source_date is not None
                and visible_date is not None
                and source_date_valid
                and visible_date_valid
                and source_date != visible_date
            ):
                errors.append({
                    "id": card_id,
                    "code": "VISIBLE_SOURCE_DATE_MISMATCH",
                    "source": source_ref,
                })

    print(json.dumps({
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
    }, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
