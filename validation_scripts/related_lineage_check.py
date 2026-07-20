#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cards_json")
    args = ap.parse_args()
    data = json.loads(Path(args.cards_json).read_text(encoding="utf-8"))
    cards = data.get("cards", [])
    active = {card.get("id"): card for card in cards}
    errors, unresolved = [], []

    for card in cards:
        card_id = card.get("id")
        related = card.get("related", [])
        if card_id in related:
            errors.append({"source": card_id, "code": "SELF_LINK"})
        if len(related) != len(set(related)):
            errors.append({
                "source": card_id,
                "code": "DUPLICATE_RELATED_TARGET",
            })
        for target in related:
            if target not in active:
                unresolved.append({"source": card_id, "target": target})

    print(json.dumps({
        "status": "PASS_WITH_UNRESOLVED_HISTORY" if not errors else "FAIL",
        "errors": errors,
        "unresolved_historical_references": unresolved,
        "deletion_authorized": False,
    }, ensure_ascii=False, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    sys.exit(main())
