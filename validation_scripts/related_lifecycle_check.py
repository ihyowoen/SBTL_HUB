#!/usr/bin/env python3
"""Validate Related structure and future Related lifecycle contracts."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

from card_audit_utils import ALLOWED_RELATION_TYPES, dedupe, parse_date

PUBLISH_STATES = {"publish_ready", "github_merge_ready", "production_verified"}
DISALLOWED_PUBLISH_RELATIONS = {
    "same_event_duplicate",
    "existing_card_reinforcement",
    "uncertain_needs_review",
}


def load_cards(path: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return {"cards": payload}, payload
    cards = payload.get("cards")
    if not isinstance(cards, list):
        raise ValueError("input must be a card list or an object with cards[]")
    return payload, cards


def load_ids(path: str | None) -> set[str] | None:
    if path is None:
        return None
    if path.endswith(".csv"):
        rows = csv.DictReader(Path(path).open(encoding="utf-8-sig"))
        values = set()
        for row in rows:
            value = row.get("assigned_id") or row.get("id") or row.get("card_id")
            if value:
                values.add(value)
        return values
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return {str(value) for value in payload}
    for key in ("ids", "new_ids", "production_ids"):
        if isinstance(payload.get(key), list):
            return {str(value) for value in payload[key]}
    raise ValueError("new-id file must contain a list or ids[]")


def relation_object(card: dict[str, Any]) -> dict[str, Any] | None:
    for key in ("related_lineage", "related_evidence_review", "related_prepass"):
        value = card.get(key)
        if isinstance(value, dict):
            return value
    return None


def check_card(card: dict[str, Any], by_id: dict[str, dict[str, Any]], require_contract: bool):
    cid = str(card.get("id", ""))
    related = card.get("related") or []
    errors = []
    warnings = []

    if not isinstance(related, list):
        return ["related must be a list"], warnings
    if related != dedupe(related):
        errors.append("related contains duplicate IDs")
    if cid and cid in related:
        errors.append("related contains self-reference")
    for target in related:
        if target not in by_id:
            errors.append(f"dangling related ID: {target}")

    lineage = relation_object(card)
    if require_contract and lineage is None:
        errors.append("missing related lifecycle object")
        return errors, warnings
    if lineage is None:
        return errors, warnings

    relation_type = lineage.get("relation_type") or lineage.get("relation_type_candidate")
    if relation_type not in ALLOWED_RELATION_TYPES:
        errors.append(f"invalid relation_type={relation_type}")
        return errors, warnings

    declared = lineage.get("related_ids")
    if isinstance(declared, list) and set(declared) != set(related):
        errors.append("related_lineage.related_ids does not match related[]")

    if relation_type == "new_unrelated_event" and related:
        errors.append("new_unrelated_event must have empty related[]")
    if relation_type in {"distinct_follow_up", "program_lineage"} and not related:
        errors.append(f"{relation_type} requires at least one related ID")
    if relation_type == "distinct_follow_up" and not lineage.get("fresh_follow_up_anchor"):
        errors.append("distinct_follow_up requires fresh_follow_up_anchor")
    if relation_type in DISALLOWED_PUBLISH_RELATIONS and (
        card.get("publish_ready") is True or card.get("state") in PUBLISH_STATES
    ):
        errors.append(f"publishable card may not use relation_type={relation_type}")
    if not lineage.get("reason") and not lineage.get("relation_reason"):
        errors.append("relation reason is required")

    if relation_type == "distinct_follow_up":
        child_date = parse_date(card.get("date"))
        for target in related:
            parent = by_id.get(target)
            parent_date = parse_date(parent.get("date")) if parent else None
            if child_date and parent_date and child_date < parent_date:
                errors.append(f"follow-up date precedes predecessor {target}")

    unresolved = lineage.get("related_candidate_spec_ids") or []
    if unresolved and card.get("state") in {"github_merge_ready", "production_verified"}:
        errors.append("unresolved related_candidate_spec_ids remain after merge prep")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--new-id-file")
    parser.add_argument("--require-contract", action="store_true")
    parser.add_argument("--report")
    args = parser.parse_args()

    _, cards = load_cards(args.input)
    by_id = {str(card.get("id")): card for card in cards if card.get("id")}
    selected = load_ids(args.new_id_file)
    rows = cards if selected is None else [card for card in cards if card.get("id") in selected]

    findings = []
    for card in rows:
        errors, warnings = check_card(card, by_id, args.require_contract)
        if errors or warnings:
            findings.append({
                "id": card.get("id"),
                "source_spec_id": card.get("source_spec_id"),
                "errors": errors,
                "warnings": warnings,
            })
    error_count = sum(len(row["errors"]) for row in findings)
    report = {
        "status": "PASS" if error_count == 0 else "FAIL",
        "cards_checked": len(rows),
        "error_count": error_count,
        "finding_count": len(findings),
        "findings": findings,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.report:
        Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 1 if error_count else 0


if __name__ == "__main__":
    sys.exit(main())
