#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_cards(path: str) -> list[dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("cards"), list):
        raise ValueError(f"Expected a cards[] JSON object: {path}")
    return [card for card in data["cards"] if isinstance(card, dict)]


def unresolved_pairs(cards: list[dict[str, Any]]) -> set[tuple[str, str]]:
    active = {
        card.get("id")
        for card in cards
        if isinstance(card.get("id"), str) and card.get("id")
    }
    pairs: set[tuple[str, str]] = set()
    for card in cards:
        source = card.get("id")
        if not isinstance(source, str) or not source:
            continue
        related = card.get("related", []) or []
        if not isinstance(related, list):
            continue
        for target in related:
            if isinstance(target, str) and target and target not in active:
                pairs.add((source, target))
    return pairs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cards_json")
    parser.add_argument(
        "--previous-baseline",
        help=(
            "Previous active cards JSON. Required to classify dangling related "
            "references as pre-existing history versus newly introduced."
        ),
    )
    args = parser.parse_args()

    try:
        cards = load_cards(args.cards_json)
        previous_cards = (
            load_cards(args.previous_baseline)
            if args.previous_baseline
            else None
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({
            "status": "VALIDATOR_INPUT_ERROR",
            "error": str(exc),
        }, ensure_ascii=False, indent=2))
        return 3

    active = {
        card.get("id"): card
        for card in cards
        if isinstance(card.get("id"), str) and card.get("id")
    }
    errors: list[dict[str, Any]] = []

    for card in cards:
        card_id = card.get("id")
        related = card.get("related", []) or []
        if not isinstance(related, list):
            errors.append({
                "source": card_id,
                "code": "INVALID_RELATED_ARRAY",
            })
            continue
        if card_id in related:
            errors.append({"source": card_id, "code": "SELF_LINK"})
        normalized = [target for target in related if isinstance(target, str)]
        if len(normalized) != len(set(normalized)):
            errors.append({
                "source": card_id,
                "code": "DUPLICATE_RELATED_TARGET",
            })

    current_unresolved = unresolved_pairs(cards)
    previous_unresolved = (
        unresolved_pairs(previous_cards)
        if previous_cards is not None
        else set()
    )
    historical = sorted(current_unresolved.intersection(previous_unresolved))
    newly_missing = sorted(current_unresolved - previous_unresolved)

    if errors:
        status = "FAIL"
        exit_code = 1
    elif current_unresolved and previous_cards is None:
        status = "BLOCKED_UNRESOLVED_RELATED_TARGETS_UNCLASSIFIED"
        exit_code = 2
    elif newly_missing:
        status = "BLOCKED_NEW_MISSING_RELATED_TARGETS"
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
        "unresolved_historical_references": [
            {"source": source, "target": target}
            for source, target in historical
        ],
        "newly_missing_related_targets": [
            {"source": source, "target": target}
            for source, target in newly_missing
        ],
        "unclassified_unresolved_references": [
            {"source": source, "target": target}
            for source, target in sorted(current_unresolved)
        ] if previous_cards is None else [],
        "previous_baseline_supplied": previous_cards is not None,
        "deletion_authorized": False,
        "required_action_when_blocked": (
            "Rerun with --previous-baseline to distinguish historical dangling "
            "references from newly introduced missing targets."
            if status == "BLOCKED_UNRESOLVED_RELATED_TARGETS_UNCLASSIFIED"
            else (
                "Fix or explicitly remap every newly missing related target."
                if status == "BLOCKED_NEW_MISSING_RELATED_TARGETS"
                else None
            )
        ),
    }, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
