#!/usr/bin/env python3
"""Prompt 0.6/0.7 content audit coverage checker.

Requires card_claim_diversity_audit[] and related_coverage_audit[] coverage for
every output card bucket, including hold/deferred buckets.
"""
import json
import sys

CONTENT_OUTPUT_BUCKETS = (
    'cards', 'draft_cards', 'payload', 'accepted',
    'content_enriched_and_language_polished', 'content_enriched',
    'language_terminology_polished', 'publish_ready_candidates',
    'content_hold_claim_narrowing_needed', 'content_hold_language_issue',
    'content_hold_schema_issue', 'needs_return_to_evidence_qc',
    'review_pool_deferred', 'addable_hold_source_gap', 'needs_source_augmentation',
    'deferred_review_pool', 'content_polish_rejected',
)
ID_FIELDS = ('card_id', 'id', 'source_spec_id', 'spec_id', 'draft_id')


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def row_id(row):
    if not isinstance(row, dict):
        return None
    for field in ID_FIELDS:
        value = row.get(field)
        if value:
            return value
    return None


def load_cards(data):
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    if not isinstance(data, dict):
        return []
    rows, seen = [], set()
    for bucket in CONTENT_OUTPUT_BUCKETS:
        if not isinstance(data.get(bucket), list):
            continue
        for row in data[bucket]:
            if not isinstance(row, dict):
                continue
            marker = row_id(row) or id(row)
            if marker in seen:
                continue
            seen.add(marker)
            rows.append(row)
    return rows


def audit_ids(rows):
    ids = set()
    if isinstance(rows, list):
        for row in rows:
            value = row_id(row)
            if value:
                ids.add(value)
    return ids


def main():
    if len(sys.argv) != 2:
        print('usage: content_audit_check.py <content_output.json>')
        return 2
    data = load(sys.argv[1])
    cards = load_cards(data)
    diversity_audit = data.get('card_claim_diversity_audit') if isinstance(data, dict) else None
    related_audit = data.get('related_coverage_audit') if isinstance(data, dict) else None
    problems = []

    if not isinstance(diversity_audit, list) or not diversity_audit:
        problems.append('card_claim_diversity_audit[] missing or empty')
    if not isinstance(related_audit, list) or not related_audit:
        problems.append('related_coverage_audit[] missing or empty')

    card_ids = [row_id(card) for card in cards if row_id(card)]
    diversity_ids = audit_ids(diversity_audit)
    related_ids = audit_ids(related_audit)
    missing_diversity = [card_id for card_id in card_ids if card_id not in diversity_ids]
    missing_related = [card_id for card_id in card_ids if card_id not in related_ids]

    if missing_diversity:
        problems.append(f'{len(missing_diversity)} card(s) absent from card_claim_diversity_audit[]')
    if missing_related:
        problems.append(f'{len(missing_related)} card(s) absent from related_coverage_audit[]')

    print('=== Content audit gate ===')
    print(f'cards                      : {len(cards)}')
    print(f'card_claim_diversity_audit : {len(diversity_audit) if isinstance(diversity_audit, list) else "MISSING"}')
    print(f'related_coverage_audit     : {len(related_audit) if isinstance(related_audit, list) else "MISSING"}')
    if missing_diversity:
        print('missing diversity audit ids:')
        for card_id in missing_diversity[:30]:
            print(f'  - {card_id}')
    if missing_related:
        print('missing related audit ids:')
        for card_id in missing_related[:30]:
            print(f'  - {card_id}')
    if problems:
        print('RESULT: BLOCKED - 0.7 must not grant publish_ready.')
        for problem in problems:
            print('-', problem)
        return 1
    print('RESULT: PASS - both audits present and all cards covered.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
