#!/usr/bin/env python3
"""
Stage B evidence gate.

Validates the evidence-before-draft rule and Stage B accounting:
- every draft card must have a valid evidence package;
- every strict-passed spec must be accounted for by draft_cards, draft_blocked,
  or draft_blocked_schema;
- duplicate output rows for the same strict spec are blocked;
- Stage B must not silently promote downstream states such as publish_ready.
"""
import json
import re
import sys
from collections import Counter
from urllib.parse import urlparse

LANDING_RE = re.compile(r'^/?$|^/(index|home|main)\.?\w*/?$', re.I)
OK_QUOTE_STATUS = {'body_quote_verified', 'official_material_quote_verified', 'document_quote_verified'}
FETCH_METADATA_KEYS = {
    'fetched', 'fetched_at', 'checked_at', 'body', 'body_text',
    'document_text', 'official_material_text'
}
SOURCE_DISCOVERY_LEDGER_KEYS = {
    'source_discovery_ledger', 'official_source_search_ledger',
    'cited_primary_search_ledger', 'alternate_source_search_ledger',
    'fetch_attempt_ledger', 'fetch_ledger', 'rescue_attempt_log'
}
SOURCE_DISCOVERY_LEDGER_REFERENCE_KEYS = {
    'source_discovery_ledger_reference', 'source_discovery_ledger_ref',
    'official_source_search_ledger_reference', 'official_source_search_ledger_ref',
    'fetch_attempt_ledger_reference', 'fetch_attempt_ledger_ref',
    'fetch_ledger_reference', 'fetch_ledger_ref',
    'rescue_attempt_log_reference', 'rescue_attempt_log_ref'
}
ALLOWED_BLOCKED_SOURCE_DISCOVERY_STATUS = {
    'completed_no_verified_source',
    'incomplete',
    'completed_verified_source_found',
    'completed_verified_with_source_strength_caveat',
}
FORBIDDEN_STAGE_B_TRUE_FLAGS = {
    'accepted_fact_safe', 'addable_merge_safe', 'evidence_complete',
    'source_claim_covered', 'content_enriched',
    'language_terminology_polished', 'publish_ready', 'github_merge_ready'
}


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def as_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return list(value.values())
    return []


def first_present(obj, *keys, default=None):
    if not isinstance(obj, dict):
        return default
    for key in keys:
        if key in obj and obj[key] is not None:
            return obj[key]
    return default


def item_key(obj):
    return first_present(obj, 'source_spec_id', 'spec_id', 'id', 'story_id', 'key', default='<unknown>')


def known_output_key(obj):
    key = item_key(obj)
    return key if key and key != '<unknown>' else None


def is_landing_page(url):
    if not url or not isinstance(url, str):
        return True
    try:
        parsed = urlparse(url.strip())
    except Exception:
        return True
    if not parsed.scheme or not parsed.netloc:
        return True
    path = (parsed.path or '').strip()
    return bool(LANDING_RE.match(path) and not parsed.query)


def has_fetch_metadata(source):
    return isinstance(source, dict) and any(bool(source.get(key)) for key in FETCH_METADATA_KEYS)


def collect_ledgers(*scopes):
    rows = []
    for scope in scopes:
        if not isinstance(scope, dict):
            continue
        for key in SOURCE_DISCOVERY_LEDGER_KEYS:
            if isinstance(scope.get(key), list):
                rows.extend(scope[key])
    return rows


def has_ledger_reference(row):
    return isinstance(row, dict) and any(bool(row.get(key)) for key in SOURCE_DISCOVERY_LEDGER_REFERENCE_KEYS)


def source_list_from_evidence_package(evidence_package):
    sources = []
    for key in ('sources', 'fetched_sources', 'body_sources', 'fact_source_candidates', 'fact_sources'):
        value = evidence_package.get(key)
        if isinstance(value, list):
            sources.extend(value)
    return sources


def evidence_ok(evidence_package, row=None, root=None):
    if not isinstance(evidence_package, dict):
        return False, ['missing evidence_package']

    issues = []
    sources = source_list_from_evidence_package(evidence_package)
    if not sources:
        issues.append('no source list in evidence_package')

    discovery_disabled = (
        evidence_package.get('external_source_discovery_disabled_by_user') is True
        or (isinstance(row, dict) and row.get('external_source_discovery_disabled_by_user') is True)
        or (isinstance(root, dict) and root.get('external_source_discovery_disabled_by_user') is True)
    )
    if not collect_ledgers(evidence_package, row, root) and not discovery_disabled:
        issues.append('missing source discovery/fetch ledger')

    status = evidence_package.get('source_discovery_status') or (row or {}).get('source_discovery_status')
    if status in (None, '', 'not_checked'):
        issues.append('missing source_discovery_status')

    good_urls = set()
    for source in sources:
        if not isinstance(source, dict):
            continue
        url = source.get('source_url') or source.get('url')
        if is_landing_page(url):
            issues.append(f'landing-page source_url is not allowed: {url!r}')
            continue
        quote_status = source.get('source_quote_status') or source.get('quote_status')
        has_quote = bool(source.get('source_quote') or source.get('quote'))
        if has_fetch_metadata(source) and has_quote and quote_status in OK_QUOTE_STATUS:
            good_urls.add(url)

    if not good_urls:
        issues.append('no fetched body/official/document-level core source with verified quote')
    if len(good_urls) <= 1:
        exception = evidence_package.get('single_source_exception') or (row or {}).get('single_source_exception')
        if not isinstance(exception, dict) or exception.get('allowed') is not True or not exception.get('reason'):
            issues.append('single-source evidence package missing explicit single_source_exception.allowed/reason')

    return not issues, issues


def blocked_ok(row, root=None):
    ledgers = collect_ledgers(row)
    if not ledgers and has_ledger_reference(row):
        ledgers = collect_ledgers(root)
    reason = first_present(row, 'final_hold_or_reject_reason', 'blocked_reason', 'blocked_source_reason', 'draft_blocked_reason', 'reason')
    status = row.get('source_discovery_status')
    rescue = row.get('rescue_attempted') is True or bool(ledgers) or has_ledger_reference(row)
    ok = bool(rescue and ledgers and reason and status in ALLOWED_BLOCKED_SOURCE_DISCOVERY_STATUS)
    return ok, {'rescue': rescue, 'ledger_count': len(ledgers), 'reason': bool(reason), 'source_discovery_status': status, 'ledger_reference': has_ledger_reference(row)}


def schema_blocked_ok(row):
    reason = first_present(row, 'schema_blocked_reason', 'blocked_reason', 'self_check_failure_reason', 'reason')
    return bool(reason), {'reason': bool(reason)}


def downstream_flags(row):
    found = []
    if not isinstance(row, dict):
        return found
    for field in FORBIDDEN_STAGE_B_TRUE_FLAGS:
        if row.get(field) is True:
            found.append(field)
        if row.get('state') == field:
            found.append('state=' + field)
    return found


def duplicate_output_keys(*buckets):
    keys = []
    for bucket in buckets:
        for row in bucket:
            key = known_output_key(row)
            if key:
                keys.append(key)
    counts = Counter(keys)
    return sorted(key for key, count in counts.items() if count > 1)


def main():
    if len(sys.argv) != 2:
        print('usage: stage_b_evidence_gate.py <stage_b_output.json>')
        return 2

    data = load(sys.argv[1])
    strict_specs = as_list(first_present(data, 'strict_passed_spec', 'strict_passed_specs', default=[]))
    draft_cards = as_list(first_present(data, 'draft_cards', 'cards', 'revised_draft_cards', default=[]))
    draft_blocked = as_list(first_present(data, 'draft_blocked', 'blocked_specs', default=[]))
    draft_blocked_schema = as_list(first_present(data, 'draft_blocked_schema', 'schema_blocked_specs', default=[]))
    evidence_packages_raw = first_present(data, 'evidence_packages', 'evidence_package', default=[])

    evidence_index = {}
    if isinstance(evidence_packages_raw, dict):
        evidence_index.update(evidence_packages_raw)
    for package in as_list(evidence_packages_raw):
        if isinstance(package, dict):
            evidence_index[item_key(package)] = package

    problems = []
    card_keys = set()
    blocked_keys = set()
    schema_blocked_keys = set()

    duplicates = duplicate_output_keys(draft_cards, draft_blocked, draft_blocked_schema)
    if duplicates:
        problems.append('duplicate Stage B output rows for spec id(s): ' + ', '.join(duplicates))

    for card in draft_cards:
        key = item_key(card)
        card_keys.add(key)
        flags = downstream_flags(card)
        if flags:
            problems.append(f'draft_card {key}: Stage B must not set downstream state flags {flags}')
        if card.get('stage_a_strict_pass_gate_missing') is True:
            problems.append(f'draft_card {key}: stage_a_strict_pass_gate_missing true is invalid')
        package = evidence_index.get(key) or card.get('evidence_package')
        ok, issues = evidence_ok(package, card, data)
        if not ok:
            problems.append(f'draft_card {key}: ' + '; '.join(issues))

    for row in draft_blocked:
        key = item_key(row)
        blocked_keys.add(key)
        flags = downstream_flags(row)
        if flags:
            problems.append(f'draft_blocked {key}: Stage B must not set downstream state flags {flags}')
        ok, info = blocked_ok(row, data)
        if not ok:
            problems.append(f'draft_blocked {key}: missing rescue/source-discovery ledger or final reason {info}')

    for row in draft_blocked_schema:
        key = item_key(row)
        schema_blocked_keys.add(key)
        flags = downstream_flags(row)
        if flags:
            problems.append(f'draft_blocked_schema {key}: Stage B must not set downstream state flags {flags}')
        ok, info = schema_blocked_ok(row)
        if not ok:
            problems.append(f'draft_blocked_schema {key}: missing schema-block reason {info}')

    expected_count = first_present(data, 'strict_passed_spec_count', 'strict_passed_specs_count')
    emitted_count = len(draft_cards) + len(draft_blocked) + len(draft_blocked_schema)
    accounting_flag = data.get('stage_b_accounting_matches_strict_passed_spec_count')

    if not isinstance(expected_count, int):
        problems.append('strict_passed_spec_count is required for Stage B accounting')
    elif emitted_count != expected_count:
        problems.append(f'Stage B accounting mismatch: strict_passed_spec_count={expected_count}, emitted={emitted_count}')
    if accounting_flag is not True:
        problems.append('stage_b_accounting_matches_strict_passed_spec_count must be true')

    strict_keys = {item_key(spec) for spec in strict_specs}
    missing = strict_keys - card_keys - blocked_keys - schema_blocked_keys
    if missing:
        problems.append('strict specs silently missing from draft_cards/draft_blocked/draft_blocked_schema: ' + ', '.join(sorted(missing)))

    print('=== Stage B evidence gate ===')
    print(f'strict_passed_spec_count : {expected_count}')
    print(f'draft_cards              : {len(draft_cards)}')
    print(f'draft_blocked            : {len(draft_blocked)}')
    print(f'draft_blocked_schema     : {len(draft_blocked_schema)}')
    print(f'problems                 : {len(problems)}')
    if problems:
        for problem in problems[:100]:
            print('-', problem)
        print('RESULT: BLOCKED_STAGE_B_EVIDENCE_OR_ACCOUNTING_INVALID')
        return 1
    print('RESULT: PASS_STAGE_B_EVIDENCE_GATE')
    return 0


if __name__ == '__main__':
    sys.exit(main())
