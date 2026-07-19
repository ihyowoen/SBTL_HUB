#!/usr/bin/env python3
import argparse, json, re, sys
from pathlib import Path

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cards_json")
    args = ap.parse_args()
    data = json.loads(Path(args.cards_json).read_text(encoding="utf-8"))
    errors, warnings = [], []
    for card in data.get("cards", []):
        cid, date, region = card.get("id"), card.get("date"), card.get("region")
        if not isinstance(date, str) or not DATE_RE.match(date):
            errors.append({"id": cid, "code": "INVALID_EVENT_DATE", "value": date})
            continue
        if isinstance(cid, str) and re.match(r"^\d{4}-\d{2}-\d{2}_(KR|US|CN|JP|EU|GL)_", cid):
            parts = cid.split("_")
            if cid[:10] != date:
                errors.append({"id": cid, "code": "ID_EVENT_DATE_MISMATCH"})
            if len(parts) >= 3 and parts[1] != region:
                errors.append({"id": cid, "code": "ID_REGION_MISMATCH"})
        elif isinstance(cid, str):
            warnings.append({"id": cid, "code": "LEGACY_ID_FORMAT_NOT_DATE_CHECKED"})
        fp = card.get("event_fingerprint", {})
        if fp.get("event_date") and fp.get("event_date") != date:
            errors.append({"id": cid, "code": "FINGERPRINT_EVENT_DATE_MISMATCH"})
        for source in card.get("fact_sources", []):
            spd = source.get("source_published_date")
            vqd = source.get("visible_quote_date")
            if spd and vqd and spd != vqd:
                errors.append({
                    "id": cid,
                    "code": "VISIBLE_SOURCE_DATE_MISMATCH",
                    "source": source.get("source_url"),
                })
    print(json.dumps({
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
    }, ensure_ascii=False, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    sys.exit(main())
