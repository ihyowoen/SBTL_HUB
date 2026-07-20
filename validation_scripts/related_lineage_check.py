#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_cards(path: str) -> list[dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    cards = data.get("cards", []) or []
    if not isinstance(cards, list):
        raise ValueError(f"Expected cards[] in: {path}")
    return [card for card in cards if isinstance(card, dict)]


def missing_pairs(cards: list[dict[str, Any]]) -> set[tuple[str, str]]:
    active_ids = {
        card.get("id") for card in cards
        if isinstance(card.get("id"), str) and card.get("id")
    }
    pairs: set[tuple[str, str]] = set()
    for card in cards:
        card_id = card.get("id")
        related = card.get("related", []) or []
        if not isinstance(card_id, str) or not isinstance(related, list):
            continue
        for target in related:
            if isinstance(target, str) and target not in active_ids:
                pairs.add((card_id, target))
    return pairs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cards_json")
    parser.add_argument(
        "--previous-cards-json",
        help=(
            "Previous baseline used to distinguish preserved historical "
            "dangling references from newly introduced missing targets."
        ),
    )
    args = parser.parse_args()

    try:
        cards = load_cards(args.cards_json)
        previous_cards = (
            load_cards(args.previous_cards_json)
            if args.previous_cards_json
            else None
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({
            "status": "VALIDATOR_INPUT_ERROR",
            "error": str(exc),
        }, ensure_ascii=False, indent=2))
        return 3

    active_ids = {
        card.get("id") for card in cards
        if isinstance(card.get("id"), str) and card.get("id")
    }
    previous_missing = missing_pairs(previous_cards or [])

    errors: list[dict[str, Any]] = []
    historical: list[dict[str, str]] = []
    unclassified: list[dict[str, str]] = []

    for card in cards:
        card_id = card.get("id")
        related = card.get("related", []) or []
        if not isinstance(card_id, str) or not card_id:
            errors.append({"code": "INVALID_CARD_ID", "value": card_id})
            continue
        if not isinstance(related, list):
            errors.append({
                "source": card_id,
                "code": "INVALID_RELATED_LIST",
            })
            continue

        normalized_targets = [
            target for target in related if isinstance(target, str)
        ]
        if len(normalized_targets) != len(related):
            errors.append({
                "source": card_id,
                "code": "INVALID_RELATED_TARGET_TYPE",
            })
        if card_id in normalized_targets:
            errors.append({"source": card_id, "code": "SELF_LINK"})
        if len(normalized_targets) != len(set(normalized_targets)):
            errors.append({
                "source": card_id,
                "code": "DUPLICATE_RELATED_TARGET",
            })

        for target in normalized_targets:
            if target in active_ids:
                continue
            finding = {"source": card_id, "target": target}
            if previous_cards is None:
                unclassified.append(finding)
            elif (card_id, target) in previous_missing:
                historical.append(finding)
            else:
                errors.append({
                    **finding,
                    "code": "NEW_MISSING_RELATED_TARGET",
                })

    if errors:
        status = "FAIL"
        exit_code = 1
    elif unclassified:
        status = "BLOCKED_RELATED_HISTORY_UNCLASSIFIED"
        exit_code = 2
    elif historical:
        status = "PASS_WITH_UNRESOLVED_HISTORY"
        exit_code = 0
    else:
        status = "PASS"
        exit_code = 0

    print(json.dumps({
        "status": status,
        "errors": errors,
        "unresolved_historical_references": historical,
        "unresolved_unclassified_references": unclassified,
        "previous_baseline_supplied": previous_cards is not None,
        "deletion_authorized": False,
        "required_action_when_blocked": (
            "Rerun with --previous-cards-json PREVIOUS_BASELINE_JSON so "
            "historical dangling references can be distinguished from new "
            "broken related targets."
            if exit_code == 2 else None
        ),
    }, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
