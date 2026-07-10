#!/usr/bin/env python3
"""Stage B evidence/accounting gate.

This script validates only mechanical Stage B invariants:
- every draft card has a verified evidence package;
- blocked rows carry or reference a source-discovery ledger and final reason;
- strict_passed_spec_count is accounted for without duplicate output keys;
- Stage B does not set downstream publish/acceptance flags.
"""
import json
import re
import sys
from collections import Counter
from urllib.parse import urlparse

OK_QUOTE_STATUS = {'body_quote_verified', 'official_material_quote_verified', 'document_quote_verified'}
FETCH_METADATA_KEYS = {'fetched', 'fetched_at', 'checked_at', 'body', 'body_text', 'document_text', 'official_material_text'}
LEDGER_KEYS = {
    'source_discovery_ledger', 'official_source_search_ledger', 'cited_primary_search_ledger',
    'alternate_source_search_ledger', 'fetch_attempt_ledger', 'fetch_ledger', 'rescue_attempt_log',
}
LEDGER_REF_KEYS = {
    'source_discovery_ledger_reference', 'source_discovery_ledger_ref',
    'official_source_search_ledger_reference', 'official_source_search_ledger_ref',
    'fetch_attempt_ledger_reference', 'fetch_attempt_ledger_ref', 'fetch_ledger_reference',
    'fetch_ledger_ref', 'rescue_attempt_log_reference', 'rescue_attempt_log_ref',
}
ALLOWED_BLOCKED_STATUS = {
    'completed_no_verified_source', 'incomplete', 'completed_verified_source_found',
    'completed_verified_with_source_strength_caveat',
}
FORBIDDEN_STAGE_B_FLAGS = {
    'accepted_fact_safe', 'addable_merge_safe', 'evidence_complete', 'source_claim_covered',
    'content_enriched', 'language_terminology_polished', 'publish_ready', 'github_merge_ready',
}
LANDING_RE = re.compile(r'^/?$|^/(index|home|main)\.?\w*/?$', re.I)


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


def known_key(obj):
    key = item_key(obj)
    return key if key and key != '<unknown>' else None


def is_landing_page(url):
    if not isinstance(url, str) or not url:
        return True
    try:
        parsed = urlparse(url.strip())
    except Exception:
        return True
    if not parsed.scheme or not parsed.netloc:
        return True
    return bool(LANDING_RE.match((parsed.path or '').strip()) and not parsed.query)


def has_fetch_metadata(source):
    return isinstance(source, dict) and any(bool(source.get(key)) for key in FETCH_METADATA_KEYS)


def collect_ledgers(*scopes):
    rows = []
    for scope in scopes:
        if not isinstance(scope, dict):
            continue
        for key in LEDGER_KEYS:
            if isinstance(scope.get(key), list):
                rows.extend(scope[key])
    return rows


def has_ledger_reference(row):
    return isinstance(row, dict) and any(bool(row.get(key)) for key in LEDGER_REF_KEYS)


def evidence_sources(package):
    sources = []
    for key in ('sources', 'fetched_sources', 'body_sources', 'fact_source_candidates', 'fact_sources'):
        if isinstance(package.get(key), list):
            sources.extend(package[key])
    return sources


def evidence_package_ok(package, row=None, root=None):
    if not isinstance(package, dict):
        return False, ['missing evidence_package']
    issues = []
    sources = evidence_sources(package)
    if not sources:
        issues.append('no source list in evidence_package')

    discovery_disabled = (
        package.get('external_source_discovery_disabled_by_user') is True
        or (isinstance(row, dict) and row.get('external_source_discovery_disabled_by_user') is True)
        or (isinstance(root, dict) and root.get('external_source_discovery_disabled_by_user') is True)
    )
    if not discovery_disabled and not collect_ledgers(package, row, root):
        issues.append('missing source discovery/fetch ledger')

    status = package.get('source_discovery_status') or (row or {}).get('source_discovery_status')
    if status in (None, '', 'not_checked'):
        issues.append('missing source_discovery_status')

    verified_urls = set()
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
            verified_urls.add(url)
    if not verified_urls:
        issues.append('no fetched body/official/document-level source with verified quote')
    if len(verified_urls) <= 1:
        exception = package.get('single_source_exception') or (row or {}).get('single_source_exception')
        if not isinstance(exception, dict) or exception.get('allowed') is not True or not exception.get('reason'):
            issues.append('single-source evidence missing single_source_exception.allowed/reason')
    return not issues, issues


def blocked_ok(row, root):
    ledgers = collect_ledgers(row)
    if not ledgers and has_ledger_reference(row):
        ledgers = collect_ledgers(root)
    reason = first_present(row, 'final_hold_or_reject_reason', 'blocked_reason', 'blocked_source_reason', 'draft_blocked_reason', 'reason')
    status = row.get('source_discovery_status')
    rescue = row.get('rescue_attempted') is True or bool(ledgers) or has_ledger_reference(row)
    ok = bool(rescue and ledgers and reason and status in ALLOWED_BLOCKED_STATUS)
    return ok, {'rescue': rescue, 'ledger_count': len(ledgers), 'reason': bool(reason), 'source_discovery_status': status, 'ledger_reference': has_ledger_reference(row)}


def schema_blocked_ok(row):
    reason = first_present(row, 'schema_blocked_reason', 'blocked_reason', 'self_check_failure_reason', 'reason')
    return bool(reason), {'reason': bool(reason)}


def downstream_flags(row):
    found = []
    if not isinstance(row, dict):
        return found
    for field in FORBIDDEN_STAGE_B_FLAGS:
        if row.get(field) is True:
            found.append(field)
        if row.get('state') == field:
            found.append('state=' + field)
    return found


def duplicate_keys(*buckets):
    counts = Counter(key for bucket in buckets for key in (known_key(row) for row in bucket) if key)
    return sorted(key for key, count in counts.items() if count > 1)


def main():
    if len(sys.argv) != 2:
        print('usage: stage_b_evidence_gate.py <stage_b_output.json>')
        return 2
    data = load(sys.argv[1])
    strict_specs = as_list(data.get('strict_passed_spec') or data.get('strict_passed_specs') or [])
    draft_cards = as_list(data.get('draft_cards') or data.get('cards') or data.get('revised_draft_cards') or [])
    draft_blocked = as_list(data.get('draft_blocked') or data.get('blocked_specs') or [])
    draft_blocked_schema = as_list(data.get('draft_blocked_schema') or data.get('schema_blocked_specs') or [])
    evidence_raw = data.get('evidence_packages') or data.get('evidence_package') or []

    evidence_index = {}
    if isinstance(evidence_raw, dict):
        evidence_index.update(evidence_raw)
    for package in as_list(evidence_raw):
        if isinstance(package, dict):
            evidence_index[item_key(package)] = package

    problems = []
    duplicates = duplicate_keys(draft_cards, draft_blocked, draft_blocked_schema)
    if duplicates:
        problems.append('duplicate Stage B output rows for spec id(s): ' + ', '.join(duplicates))

    card_keys, blocked_keys, schema_keys = set(), set(), set()
    for card in draft_cards:
        key = item_key(card)
        card_keys.add(key)
        flags = downstream_flags(card)
        if flags:
            problems.append(f'draft_card {key}: Stage B must not set downstream flags {flags}')
        if card.get('stage_a_strict_pass_gate_missing') is True:
            problems.append(f'draft_card {key}: stage_a_strict_pass_gate_missing true is invalid')
        ok, issues = evidence_package_ok(evidence_index.get(key) or card.get('evidence_package'), card, data)
        if not ok:
            problems.append(f'draft_card {key}: ' + '; '.join(issues))

    for row in draft_blocked:
        key = item_key(row)
        blocked_keys.add(key)
        flags = downstream_flags(row)
        if flags:
            problems.append(f'draft_blocked {key}: Stage B must not set downstream flags {flags}')
        ok, info = blocked_ok(row, data)
        if not ok:
            problems.append(f'draft_blocked {key}: missing rescue/source-discovery ledger or final reason {info}')

    for row in draft_blocked_schema:
        key = item_key(row)
        schema_keys.add(key)
        flags = downstream_flags(row)
        if flags:
            problems.append(f'draft_blocked_schema {key}: Stage B must not set downstream flags {flags}')
        ok, info = schema_blocked_ok(row)
        if not ok:
            problems.append(f'draft_blocked_schema {key}: missing schema-block reason {info}')

    expected_count = data.get('strict_passed_spec_count') if isinstance(data.get('strict_passed_spec_count'), int) else data.get('strict_passed_specs_count')
    emitted_count = len(draft_cards) + len(draft_blocked) + len(draft_blocked_schema)
    if not isinstance(expected_count, int):
        problems.append('strict_passed_spec_count is required for Stage B accounting')
    elif emitted_count != expected_count:
        problems.append(f'Stage B accounting mismatch: strict_passed_spec_count={expected_count}, emitted={emitted_count}')
    if data.get('stage_b_accounting_matches_strict_passed_spec_count') is not True:
        problems.append('stage_b_accounting_matches_strict_passed_spec_count must be true')

    strict_keys = {item_key(spec) for spec in strict_specs}
    missing = strict_keys - card_keys - blocked_keys - schema_keys
    if missing:
        problems.append('strict specs silently missing from output buckets: ' + ', '.join(sorted(missing)))

    print('=== Stage B evidence gate ===')
    print(f'strict_passed_spec_count : {expected_count}')
    print(f'draft_cards              : {len(draft_cards)}')
    print(f'draft_blocked            : {len(draft_blocked)}')
    print(f'draft_blocked_schema     : {len(draft_blocked_schema)}')
    print(f'problems                 : {len(problems)}')
    if problems:
        for problem in problems[:120]:
            print('-', problem)
        print('RESULT: BLOCKED_STAGE_B_EVIDENCE_OR_ACCOUNTING_INVALID')
        return 1
    print('RESULT: PASS_STAGE_B_EVIDENCE_GATE')
    return 0


if __name__ == '__main__':
    sys.exit(main())
