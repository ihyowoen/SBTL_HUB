#!/usr/bin/env python3
"""Prompt 0.5 Evidence QC mechanical checker.

Checks source-diversity status, bucket semantics, landing-page/fake diversity,
owner-level independence, official/primary single-source exceptions, and required
visible source/discovery ledgers. This script flags only; it does not mutate
artifacts or fabricate sources.
"""
import json
import re
import sys
from urllib.parse import urlparse

PASS_STATUSES = {'PASS_MULTI_SOURCE', 'PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION'}
HOLD_FAIL_STATUSES = {'HOLD_NEEDS_SOURCE_AUGMENTATION', 'FAIL_SOURCE_DIVERSITY'}
ALLOWED_STATUSES = PASS_STATUSES | HOLD_FAIL_STATUSES
COMPLETE_BUCKETS = {'accepted', 'accepted_fact_safe', 'accepted_fact_safe_with_warnings', 'evidence_complete_and_source_claim_covered'}
EVIDENCE_QC_BUCKETS = (
    'addable_merge_safe', 'cards', 'draft_cards', 'qc_cards', 'payload', 'accepted',
    'accepted_fact_safe', 'accepted_fact_safe_with_warnings',
    'evidence_complete_and_source_claim_covered', 'addable_hold_source_gap',
    'addable_hold_claim_gap', 'needs_source_augmentation', 'evidence_qc_rejected',
    'source_claim_gap', 'single_source_exception_review', 'deferred_review_pool',
    'review_pool_deferred',
)
OWNER_FIELDS = ('independent_owner', 'owner', 'source_owner', 'publisher_owner', 'canonical_owner', 'parent_owner')
LANDING_RE = re.compile(r'^/?$|^/(index|home|main)\.?\w*/?$', re.I)
HIGH_SIGNAL = {'top', 'high'}
CORROBORATION_RE = re.compile(r'safety|recall|리콜|점유율|market\s*share|시장\s*점유|ranking|순위|1위|최대|최초|world.?first|업계\s*최', re.I)
OFFICIAL_HINTS = ('.gov', '.go.kr', 'sec.gov', '/ir', 'ir.', 'investor', '.go.jp', 'europa.eu', '.go.uk')
OFFICIAL_PRIMARY_TERMS = (
    'official', 'regulatory', 'regulator', 'filing', 'sec_filing', 'court',
    'original_dataset', 'original_data', 'contracting_party', 'project_owner',
    'source_owner', 'research_institution', 'company_primary', 'primary_announcement',
    'government', 'ministry', 'agency', 'issuer_release', 'press_release_owner',
)
MEDIA_TERMS = ('media', 'news_article', 'media_article', 'trade_press', 'wire', 'syndication')


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


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


def host_key(url):
    if not isinstance(url, str):
        return ''
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith('www.') else host


def is_official_url(url):
    if not isinstance(url, str):
        return False
    host = urlparse(url).netloc.lower()
    text = url.lower()
    return any(hint in host or hint in text for hint in OFFICIAL_HINTS)


def int_field(obj, *keys):
    if not isinstance(obj, dict):
        return None
    for key in keys:
        value = obj.get(key)
        if isinstance(value, int) and not isinstance(value, bool):
            return value
    return None


def owner_count_from_ledger(card):
    ledger = card.get('source_independence_ledger') if isinstance(card, dict) else None
    if not isinstance(ledger, list):
        return None
    owners, independent_rows = set(), 0
    for row in ledger:
        if not isinstance(row, dict):
            continue
        if row.get('is_independent') is False or row.get('independent') is False:
            continue
        for field in OWNER_FIELDS:
            if row.get(field):
                owners.add(str(row[field]).strip().lower())
                break
        else:
            if row.get('is_independent') is True or row.get('independent') is True:
                independent_rows += 1
    if owners:
        return len(owners)
    if independent_rows:
        return independent_rows
    return None


def independent_owner_count(card, independent_hosts):
    count = int_field(card, 'source_independent_owner_count', 'independent_owner_count')
    if count is not None:
        return count
    measure = card.get('source_diversity_measure') if isinstance(card, dict) else None
    count = int_field(measure, 'source_independent_owner_count', 'independent_owner_count')
    if count is not None:
        return count
    count = owner_count_from_ledger(card)
    if count is not None:
        return count
    return len(independent_hosts)


def metadata_blob(source):
    keys = (
        'source_type', 'source_kind', 'source_origin_type', 'source_role',
        'publisher_type', 'origin_type', 'official_source_type', 'source_category',
    )
    return ' '.join(str(source.get(key, '')).lower() for key in keys if isinstance(source, dict))


def source_has_primary_or_official_metadata(source):
    if not isinstance(source, dict):
        return False
    if source.get('is_official') is True or source.get('official_source') is True or source.get('is_primary_source') is True:
        return True
    role = str(source.get('evidence_role') or '').lower()
    if role in {'official_material_evidence', 'official_source', 'primary_source', 'regulatory_filing', 'original_dataset'}:
        return True
    blob = metadata_blob(source)
    if any(term in blob for term in MEDIA_TERMS) and not any(term in blob for term in OFFICIAL_PRIMARY_TERMS):
        return False
    return any(term in blob for term in OFFICIAL_PRIMARY_TERMS)


def has_passing_single_source_exception(card):
    exception = card.get('single_source_exception')
    return isinstance(exception, dict) and exception.get('allowed') is True and bool(exception.get('reason'))


def supports_visible_claim(source):
    if not isinstance(source, dict):
        return False
    if source.get('supporting_context_only_not_visible_claim_support') is True:
        return False
    role = source.get('evidence_role')
    supports = source.get('supports') or []
    if role in {'primary_event_evidence', 'secondary_event_evidence'}:
        return True
    return isinstance(supports, list) and any(field in supports for field in ('title', 'sub', 'gate', 'fact', 'implication'))


def row_marker(row):
    return row.get('id') or row.get('card_id') or row.get('source_spec_id') or row.get('spec_id') or id(row)


def load_cards(data):
    if isinstance(data, list):
        return data
    if not isinstance(data, dict):
        return []
    rows, seen = [], set()
    for bucket in EVIDENCE_QC_BUCKETS:
        if not isinstance(data.get(bucket), list):
            continue
        for row in data[bucket]:
            if not isinstance(row, dict):
                continue
            marker = row_marker(row)
            if marker in seen:
                continue
            seen.add(marker)
            loaded = dict(row)
            loaded['__qc_bucket'] = bucket
            rows.append(loaded)
    return rows


def has_primary_exception(card, visible_sources):
    return (
        card.get('source_diversity_status') == 'PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION'
        and has_passing_single_source_exception(card)
        and any(source_has_primary_or_official_metadata(source) for source in visible_sources)
    )


def main():
    if len(sys.argv) != 2:
        print('usage: evidence_qc_v8_check.py <evidence_qc_output.json>')
        return 2
    cards = load_cards(load(sys.argv[1]))
    flags = {name: [] for name in (
        'landing_page', 'fake_diversity', 'weak_corroboration', 'url_desync',
        'invalid_source_diversity_status', 'missing_source_discovery_ledger',
    )}

    for card in cards:
        cid = card.get('id') or card.get('card_id') or card.get('source_spec_id') or card.get('spec_id') or '<no-id>'
        bucket = card.get('__qc_bucket')
        status = card.get('source_diversity_status')
        fact_sources = card.get('fact_sources') or []
        urls = card.get('urls') or []
        source_urls = [src.get('source_url') for src in fact_sources if isinstance(src, dict) and src.get('source_url')]
        visible_sources = [src for src in fact_sources if supports_visible_claim(src)]
        visible_urls = [src.get('source_url') for src in visible_sources if src.get('source_url')]
        visible_url_count = len(set(visible_urls))
        independent_hosts = {host_key(url) for url in visible_urls if host_key(url)}
        owner_count = independent_owner_count(card, independent_hosts)
        discovery_ledger = card.get('source_discovery_ledger') or card.get('source_discovery_ledger_ref') or card.get('source_discovery_ledger_reference')
        primary_or_official_source = any(source_has_primary_or_official_metadata(source) for source in visible_sources)

        if status not in ALLOWED_STATUSES:
            flags['invalid_source_diversity_status'].append((cid, f'missing/invalid source_diversity_status={status}'))
        if bucket in COMPLETE_BUCKETS and status in HOLD_FAIL_STATUSES:
            flags['invalid_source_diversity_status'].append((cid, f'{status} may not appear in complete bucket {bucket}'))
        if status == 'PASS_MULTI_SOURCE':
            if visible_url_count < 2:
                flags['invalid_source_diversity_status'].append((cid, f'PASS_MULTI_SOURCE requires >=2 visible source URLs, got {visible_url_count}'))
            if owner_count < 2:
                flags['invalid_source_diversity_status'].append((cid, f'PASS_MULTI_SOURCE requires >=2 independent source owners, got {owner_count}'))
        if status == 'PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION':
            if not has_passing_single_source_exception(card):
                flags['invalid_source_diversity_status'].append((cid, 'single-source pass exception missing allowed=true/reason'))
            elif not primary_or_official_source:
                flags['invalid_source_diversity_status'].append((cid, 'single-source pass exception requires official/primary visible source metadata'))
        if status == 'PASS_SINGLE_SOURCE':
            flags['invalid_source_diversity_status'].append((cid, 'PASS_SINGLE_SOURCE is not an allowed status'))

        for url in source_urls:
            if is_landing_page(url):
                flags['landing_page'].append((cid, url))
        if fact_sources and len(set(source_urls)) < len(fact_sources):
            flags['fake_diversity'].append((cid, f'{len(fact_sources)} entries / {len(set(source_urls))} distinct urls'))

        if status in PASS_STATUSES and not discovery_ledger:
            flags['missing_source_discovery_ledger'].append((cid, f'{status} requires source_discovery_ledger/ref'))

        text_blob = ' '.join(str(card.get(k, '')) for k in ('title', 'sub', 'gate', 'fact'))
        needs_corroboration = str(card.get('signal', '')).lower() in HIGH_SIGNAL or bool(CORROBORATION_RE.search(text_blob))
        if needs_corroboration:
            has_official_url = any(is_official_url(url) for url in set(visible_urls))
            if owner_count < 2 and not has_official_url and not has_primary_exception(card, visible_sources):
                flags['weak_corroboration'].append((cid, f'{owner_count} independent source owner, no official/primary exception'))

        url_set = set(urls)
        for url in visible_urls:
            if url not in url_set:
                flags['url_desync'].append((cid, url))

    total = sum(len(items) for items in flags.values())
    print('=== Evidence QC mechanical check ===')
    print(f'cards checked: {len(cards)}')
    for name, items in flags.items():
        print(f'  {name}: {len(items)}')
        for cid, detail in items[:30]:
            print(f'      - {cid}: {detail}')
        if len(items) > 30:
            print(f'      ... (+{len(items) - 30} more)')
    if total:
        print(f'RESULT: {total} flag(s) - Evidence QC is NOT pass. Do NOT fabricate sources.')
        return 1
    print('RESULT: PASS - no evidence QC flags.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
