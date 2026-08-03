#!/usr/bin/env python3
"""Validate Related structure and future Related lifecycle contracts."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

from card_audit_utils import (
    ALLOWED_RELATION_TYPES,
    dedupe,
    parse_date,
)

PUBLISH_STATES = {"publish_ready", "github_merge_ready", "production_verified"}
DISALLOWED_PUBLISH_RELATIONS = {
    "same_event_duplicate",
    "existing_card_reinforcement",
    "uncertain_needs_review",
}
FRESH_FOLLOW_UP_ANCHOR_CLASSES = {
    "execution_event_anchor",
    "policy_regulatory_anchor",
    "data_financial_anchor",
    "strategic_behavior_anchor",
    "technology_commercialization_anchor",
    "follow_up_probability_anchor",
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
            value = (
                row.get("assigned_id") or row.get("id") or row.get("card_id")
                or row.get("draft_id") or row.get("source_spec_id")
            )
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


def card_identifiers(card: dict[str, Any]) -> set[str]:
    """Identifiers accepted only for selecting the current-run validation scope."""
    return {
        str(card.get(key)).strip()
        for key in ("id", "card_id", "draft_id", "source_spec_id")
        if card.get(key) is not None and str(card.get(key)).strip()
    }


def canonical_card_identifiers(card: dict[str, Any]) -> set[str]:
    """Canonical identifiers permitted for Related target resolution."""
    return {
        str(card.get(key)).strip()
        for key in ("id", "card_id")
        if card.get(key) is not None and str(card.get(key)).strip()
    }


def provisional_card_identifiers(card: dict[str, Any]) -> set[str]:
    """Pre-merge aliases permitted only for current-run scope selection."""
    return {
        str(card.get(key)).strip()
        for key in ("draft_id", "source_spec_id")
        if card.get(key) is not None and str(card.get(key)).strip()
    }


def primary_card_identifier(card: dict[str, Any]) -> str:
    for key in ("id", "card_id", "draft_id", "source_spec_id"):
        value = card.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def select_related_scope(cards: list[dict[str, Any]], selected: set[str] | None):
    rows = list(cards)
    if selected is None:
        return rows, {
            "applied": False,
            "status": "NOT_APPLIED",
            "requested_count": None,
            "matched_count": len(rows),
            "missing_ids": [],
            "ambiguous_ids": [],
            "errors": [],
        }

    requested = {str(value).strip() for value in selected if str(value).strip()}
    selected_rows: list[dict[str, Any]] = []
    matched: set[str] = set()
    ambiguous: list[str] = []

    for identifier in sorted(requested):
        canonical_matches = [
            card for card in rows if identifier in canonical_card_identifiers(card)
        ]
        alias_matches = [
            card for card in rows if identifier in provisional_card_identifiers(card)
        ]

        # Scope identifiers are intentionally untyped. If the same string names a
        # canonical identifier on one row and a provisional alias on another, the
        # requested row cannot be inferred safely and the scope must fail closed.
        if len(canonical_matches) > 1 or len(alias_matches) > 1:
            ambiguous.append(identifier)
            continue

        if len(canonical_matches) == 1:
            if alias_matches and alias_matches[0] is not canonical_matches[0]:
                ambiguous.append(identifier)
                continue
            matched.add(identifier)
            if canonical_matches[0] not in selected_rows:
                selected_rows.append(canonical_matches[0])
            continue

        if len(alias_matches) == 1:
            matched.add(identifier)
            if alias_matches[0] not in selected_rows:
                selected_rows.append(alias_matches[0])

    missing = sorted(requested - matched - set(ambiguous))
    errors = []
    if not requested:
        errors.append("ID scope is empty")
    elif not matched and not ambiguous:
        errors.append("ID scope matched zero cards")
    if missing:
        errors.append(f"ID scope has {len(missing)} unmatched ID(s)")
    if ambiguous:
        errors.append(f"ID scope has {len(ambiguous)} ambiguous ID(s)")

    return selected_rows, {
        "applied": True,
        "status": "PASS" if not errors else "FAIL",
        "requested_count": len(requested),
        "matched_count": len(matched),
        "missing_ids": missing,
        "ambiguous_ids": sorted(ambiguous),
        "errors": errors,
    }


def build_provisional_target_index(
    cards: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], set[str]]:
    """Resolve provisional candidate IDs only within the current-run scope."""
    index: dict[str, dict[str, Any]] = {}
    ambiguous: set[str] = set()
    for card in cards:
        for identifier in provisional_card_identifiers(card):
            existing = index.get(identifier)
            if existing is not None and existing is not card:
                ambiguous.add(identifier)
            else:
                index[identifier] = card
    for identifier in ambiguous:
        index.pop(identifier, None)
    return index, ambiguous


def relation_object(card: dict[str, Any]) -> dict[str, Any] | None:
    for key in ("related_lineage", "related_evidence_review", "related_prepass"):
        value = card.get(key)
        if isinstance(value, dict):
            return value
    return None


def check_card(
    card: dict[str, Any],
    by_id: dict[str, dict[str, Any]],
    require_contract: bool,
    allow_provisional_related: bool = False,
    provisional_by_id: dict[str, dict[str, Any]] | None = None,
    ambiguous_provisional_ids: set[str] | None = None,
):
    related = card.get("related") or []
    provisional_by_id = provisional_by_id or {}
    ambiguous_provisional_ids = ambiguous_provisional_ids or set()
    errors = []
    warnings = []

    if not isinstance(related, list):
        return ["related must be a list"], warnings
    if related != dedupe(related):
        errors.append("related contains duplicate IDs")
    for target in related:
        resolved_target = by_id.get(target)
        if resolved_target is card:
            errors.append("related contains self-reference")
        elif resolved_target is None:
            errors.append(f"dangling related ID: {target}")

    lineage = relation_object(card)
    if require_contract and lineage is None:
        errors.append("missing related lifecycle object")
        return errors, warnings
    if lineage is None:
        return errors, warnings

    if require_contract and lineage.get("status") != "PASS":
        errors.append("related lifecycle status must be PASS")
    if require_contract and lineage.get("same_event_checked") is not True:
        errors.append("same_event_checked must be true")
    if require_contract and lineage.get("earliest_same_event_date_checked") is not True:
        errors.append("earliest_same_event_date_checked must be true")

    relation_type = lineage.get("relation_type") or lineage.get("relation_type_candidate")
    if relation_type not in ALLOWED_RELATION_TYPES:
        errors.append(f"invalid relation_type={relation_type}")
        return errors, warnings

    declared = lineage.get("related_ids")
    if isinstance(declared, list) and set(declared) != set(related):
        errors.append("related_lineage.related_ids does not match related[]")

    provisional = (
        lineage.get("related_candidate_spec_ids")
        or card.get("related_candidate_spec_ids")
        or []
    )
    valid_provisional_edge = False
    resolved_provisional_targets: list[tuple[str, dict[str, Any]]] = []
    if allow_provisional_related and provisional:
        if not isinstance(provisional, list):
            errors.append("related_candidate_spec_ids must be a list")
        else:
            normalized_provisional = []
            for value in provisional:
                if not isinstance(value, str) or not value.strip():
                    errors.append("related_candidate_spec_ids must contain non-empty strings")
                    continue
                normalized_provisional.append(value.strip())
            if normalized_provisional != dedupe(normalized_provisional):
                errors.append("related_candidate_spec_ids contains duplicate IDs")
            for target in normalized_provisional:
                if target in ambiguous_provisional_ids:
                    errors.append(f"ambiguous provisional related ID: {target}")
                    continue
                resolved_target = provisional_by_id.get(target)
                if resolved_target is card:
                    errors.append("related_candidate_spec_ids contains self-reference")
                elif resolved_target is None:
                    errors.append(f"dangling provisional related ID: {target}")
                else:
                    resolved_provisional_targets.append((target, resolved_target))
            valid_provisional_edge = bool(normalized_provisional) and not any(
                message.startswith((
                    "related_candidate_spec_ids",
                    "ambiguous provisional related ID",
                    "dangling provisional related ID",
                ))
                for message in errors
            )

    if relation_type == "new_unrelated_event" and (related or (allow_provisional_related and provisional)):
        errors.append("new_unrelated_event must have empty related[] and no provisional related edges")
    if (
        relation_type in {"distinct_follow_up", "program_lineage"}
        and not related
        and not valid_provisional_edge
    ):
        errors.append(f"{relation_type} requires at least one final or allowed provisional related ID")
    if relation_type == "distinct_follow_up" and not lineage.get("fresh_follow_up_anchor"):
        errors.append("distinct_follow_up requires fresh_follow_up_anchor")
    if require_contract and relation_type == "distinct_follow_up":
        anchor_class = lineage.get("fresh_follow_up_anchor_class")
        if not isinstance(anchor_class, str) or anchor_class not in FRESH_FOLLOW_UP_ANCHOR_CLASSES:
            errors.append("distinct_follow_up requires valid fresh_follow_up_anchor_class")
        incremental_fact = lineage.get("incremental_fact_vs_predecessor")
        if not isinstance(incremental_fact, str) or not incremental_fact.strip():
            errors.append("distinct_follow_up requires incremental_fact_vs_predecessor")
        changed_judgment = lineage.get("changed_judgment_vs_predecessor")
        if not isinstance(changed_judgment, str) or not changed_judgment.strip():
            errors.append("distinct_follow_up requires changed_judgment_vs_predecessor")

    is_publishable = card.get("publish_ready") is True or card.get("state") in PUBLISH_STATES
    if relation_type in DISALLOWED_PUBLISH_RELATIONS and (require_contract or is_publishable):
        errors.append(
            f"validated new-card output may not use relation_type={relation_type}"
        )

    if not lineage.get("reason") and not lineage.get("relation_reason"):
        errors.append("relation reason is required")

    if relation_type == "distinct_follow_up":
        child_date = parse_date(card.get("date"))
        for target in related:
            parent = by_id.get(target)
            parent_date = parse_date(parent.get("date")) if parent else None
            if child_date and parent_date and child_date < parent_date:
                errors.append(f"follow-up date precedes predecessor {target}")
        for target, parent in resolved_provisional_targets:
            parent_date = parse_date(parent.get("date"))
            if child_date and parent_date and child_date < parent_date:
                errors.append(f"follow-up date precedes provisional predecessor {target}")

    unresolved = (
        lineage.get("related_candidate_spec_ids")
        or card.get("related_candidate_spec_ids")
        or []
    )
    if unresolved and card.get("state") in {"github_merge_ready", "production_verified"}:
        errors.append("unresolved related_candidate_spec_ids remain after merge prep")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--new-id-file")
    parser.add_argument("--require-contract", action="store_true")
    parser.add_argument("--allow-provisional-related", action="store_true")
    parser.add_argument("--report")
    args = parser.parse_args()

    if args.allow_provisional_related and not args.require_contract:
        parser.error("--allow-provisional-related requires --require-contract")
    if args.allow_provisional_related and not args.new_id_file:
        parser.error("--allow-provisional-related requires --new-id-file current-run scope")

    _, cards = load_cards(args.input)
    by_id: dict[str, dict[str, Any]] = {}
    for card in cards:
        for identifier in canonical_card_identifiers(card):
            existing = by_id.get(identifier)
            if existing is not None and existing is not card:
                raise ValueError(f"duplicate canonical card identifier: {identifier}")
            by_id[identifier] = card
    selected = load_ids(args.new_id_file)
    rows, scope = select_related_scope(cards, selected)
    if args.allow_provisional_related:
        provisional_by_id, ambiguous_provisional_ids = build_provisional_target_index(rows)
    else:
        provisional_by_id, ambiguous_provisional_ids = {}, set()

    findings = []
    if scope["errors"]:
        findings.append({
            "id": "<id-scope>",
            "source_spec_id": None,
            "errors": scope["errors"],
            "warnings": [],
        })
    for card in rows:
        errors, warnings = check_card(
            card,
            by_id,
            args.require_contract,
            allow_provisional_related=args.allow_provisional_related,
            provisional_by_id=provisional_by_id,
            ambiguous_provisional_ids=ambiguous_provisional_ids,
        )
        if errors or warnings:
            findings.append({
                "id": card.get("id"),
                "source_spec_id": card.get("source_spec_id"),
                "errors": errors,
                "warnings": warnings,
            })
    error_count = sum(len(row["errors"]) for row in findings)
    report = {
        "id_scope": scope,
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
