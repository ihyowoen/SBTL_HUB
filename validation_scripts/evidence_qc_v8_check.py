#!/usr/bin/env python3
"""
Evidence QC mechanical checker for Prompt 0.5 artifacts.

Flags only. Does not fabricate sources, promote cards, or mutate outputs.
"""
import json
import re
import sys
from urllib.parse import urlparse

LANDING_RE = re.compile(r'^/?$|^/(index|home|main)\.?\w*/?$', re.I)
HIGH_SIGNAL = {'top', 'high'}
CORROBORATION_RE = re.compile(
    r'safety|recall|리콜|점유율|market\s*share|시장\s*점유|ranking|순위|1위|최대|최초|world.?first|업계\s*최',
    re.I,
)
OFFICIAL_HINTS = ('.gov', '.go.kr', 'sec.gov', '/ir', 'ir.', 'investor', '.go.jp', 'europa.eu', '.go.uk')
SOURCE_DIVERSITY_PASS = {'PASS_MULTI_SOURCE', 'PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION'}
SOURCE_DIVERSITY_HOLD_FAIL = {'HOLD_NEEDS_SOURCE_AUGMENTATION', 'FAIL_SOURCE_DIVERSITY'}
COMPLETE_BUCKETS = {
    'accepted',
    'accepted_fact_safe',
    'accepted_fact_safe_with_warnings',
    'evidence_complete_and_source_claim_covered',
}
EVIDENCE_QC_BUCKETS = (
    'cards', 'draft_cards', 'qc_cards', 'payload', 'accepted',
    'accepted_fact_safe', 'accepted_fact_safe_with_warnings',
    'evidence_complete_and_source_claim_covered', 'addable_hold_source_gap',
    'needs_source_augmentation', 'evidence_qc_rejected', 'source_claim_gap',
    'single_source_exception_review', 'deferred_review_pool',
)


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


def host_key(url):
    if not isinstance(url, str):
        return ''
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith('www.') else host


def is_official(url):
    if not isinstance(url, str):
        return False
    host = urlparse(url).netloc.lower()
    text = url.lower()
    return any(hint in host or hint in text for hint in OFFICIAL_HINTS)


def supports_visible_claim(source):
    if not isinstance(source, dict):
        return False
    if source.get('supporting_context_only_not_visible_claim_support') is True:
        return False
    role = source.get('evidence_role')
    supports = source.get('supports') or []
    if role in ('primary_event_evidence', 'secondary_event_evidence'):
        return True
    return isinstance(supports, list) and any(field in supports for field in ('title', 'sub', 'gate', 'fact', 'implication'))


def row_marker(row):
    return row.get('id') or row.get('card_id') or row.get('source_spec_id') or row.get('spec_id') or id(row)


def load_cards(data):
    if isinstance(data, list):
        return data
    if not isinstance(data, dict):
        return []
    rows = []
    seen = set()
    for bucket in EVIDENCE_QC_BUCKETS:
        value = data.get(bucket)
        if not isinstance(value, list):
            continue
        for row in value:
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


def main():
    if len(sys.argv) != 2:
        print('usage: evidence_qc_v8_check.py <cards_or_evidence_qc_output.json>')
        return 2
    with open(sys.argv[1], encoding='utf-8') as f:
        data = json.load(f)
    cards = load_cards(data)

    flags = {
        'landing_page': [],
        'fake_diversity': [],
        'missing_single_source_exception': [],
        'weak_corroboration': [],
        'url_desync': [],
        'invalid_source_diversity_status': [],
        'missing_source_discovery_ledger': [],
    }

    for card in cards:
        cid = card.get('id') or card.get('card_id') or card.get('source_spec_id') or card.get('spec_id') or '<no-id>'
        bucket = card.get('__qc_bucket')
        fact_sources = card.get('fact_sources') or []
        urls = card.get('urls') or []
        signal = str(card.get('signal', '')).lower()
        source_urls = [src.get('source_url') for src in fact_sources if isinstance(src, dict) and src.get('source_url')]
        distinct_urls = set(source_urls)
        visible_sources = [src for src in fact_sources if supports_visible_claim(src)]
        visible_urls = [src.get('source_url') for src in visible_sources if src.get('source_url')]
        visible_url_count = len(set(visible_urls))
        independent_hosts = {host_key(url) for url in visible_urls if host_key(url)}
        independent_count = len(independent_hosts)
        diversity_status = card.get('source_diversity_status')
        discovery_ledger = (
            card.get('source_discovery_ledger')
            or card.get('source_discovery_ledger_ref')
            or card.get('source_discovery_ledger_reference')
        )

        if bucket in COMPLETE_BUCKETS and diversity_status in SOURCE_DIVERSITY_HOLD_FAIL:
            flags['invalid_source_diversity_status'].append((cid, f'{diversity_status} may not appear in complete bucket {bucket}'))
        if diversity_status == 'PASS_MULTI_SOURCE' and independent_count < 2:
            flags['invalid_source_diversity_status'].append((cid, f'PASS_MULTI_SOURCE requires >=2 independent visible-source hosts, got {independent_count}'))

        for url in source_urls:
            if is_landing_page(url):
                flags['landing_page'].append((cid, url))

        if fact_sources and len(distinct_urls) < len(fact_sources):
            flags['fake_diversity'].append((cid, f'{len(fact_sources)} entries / {len(distinct_urls)} distinct urls'))

        if visible_url_count <= 1:
            exception = card.get('single_source_exception')
            if not exception:
                flags['missing_single_source_exception'].append((cid, f'{visible_url_count} distinct visible-claim source'))
            if not isinstance(exception, dict) or exception.get('allowed') is not True or not exception.get('reason'):
                flags['invalid_source_diversity_status'].append((cid, 'single-source exception missing allowed=true/reason'))
            if diversity_status == 'PASS_SINGLE_SOURCE':
                flags['invalid_source_diversity_status'].append((cid, 'PASS_SINGLE_SOURCE is not an allowed status'))
            if diversity_status not in SOURCE_DIVERSITY_PASS | SOURCE_DIVERSITY_HOLD_FAIL:
                flags['invalid_source_diversity_status'].append((cid, f'missing/invalid source_diversity_status={diversity_status}'))
            if not discovery_ledger:
                flags['missing_source_discovery_ledger'].append((cid, 'single-source card lacks source_discovery_ledger/ref'))

        text_blob = ' '.join(str(card.get(k, '')) for k in ('title', 'sub', 'gate', 'fact'))
        needs_corroboration = signal in HIGH_SIGNAL or bool(CORROBORATION_RE.search(text_blob))
        if needs_corroboration:
            has_official_visible_source = any(is_official(url) for url in set(visible_urls))
            if independent_count < 2 and not has_official_visible_source:
                flags['weak_corroboration'].append((cid, f'signal={signal or "?"}, {independent_count} independent visible-source host, no official'))

        url_set = set(urls)
        for url in visible_urls:
            if url not in url_set:
                flags['url_desync'].append((cid, url))

        if diversity_status in SOURCE_DIVERSITY_PASS and not discovery_ledger:
            flags['missing_source_discovery_ledger'].append((cid, f'{diversity_status} requires source_discovery_ledger/ref'))

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
