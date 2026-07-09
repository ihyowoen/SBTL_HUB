#!/usr/bin/env python3
"""
R3C_P03 - Evidence QC V8 mechanical check.
run 20260516_012728 retrospective patch.

Mechanically runs the Source Diversity & Corroboration QC Rule (v8) over a card
set. Flags, per card:
  (a) landing-page source_url (host root, no article path)
  (b) fake diversity - distinct source_url count < fact_sources entry count
  (c) missing single_source_exception object on a 1-source card
  (d) weak corroboration - high-signal / safety / market-share / ranking card
      with < 2 independent sources and no official source
  (e) visible-source URL desync - fact_sources.source_url not in urls[]
  (f) invalid source_diversity_status / single-source exception laundering

The script FLAGS ONLY. It never fabricates a second source. Every flag must be
verified by a human/assistant. Any flag means 0.5 is not PASS.

Usage:
    python3 evidence_qc_v8_check.py <cards_or_qc_output.json>

Exit codes: 0 = PASS, 1 = flags found, 2 = usage error.
"""
import json
import re
import sys
from urllib.parse import urlparse

LANDING_RE = re.compile(r'^/?$|^/(index|home|main)\.?\w*/?$', re.I)
HIGH_SIGNAL = {'top', 'high'}
CORROBORATION_RE = re.compile(
    r'safety|recall|리콜|점유율|market\s*share|시장\s*점유|ranking|순위'
    r'|1위|최대|최초|world.?first|업계\s*최',
    re.I)
OFFICIAL_HINTS = ('.gov', '.go.kr', 'sec.gov', '/ir', 'ir.', 'investor',
                  '.go.jp', 'europa.eu', '.go.uk', '.gob.', '.gov.', 'regulator',
                  'exchange', 'filing', 'tender')
SOURCE_DIVERSITY_PASS = {
    'PASS_MULTI_SOURCE',
    'PASS_OFFICIAL_OR_PRIMARY_SINGLE_SOURCE_EXCEPTION',
}
SOURCE_DIVERSITY_HOLD_FAIL = {
    'HOLD_NEEDS_SOURCE_AUGMENTATION',
    'FAIL_SOURCE_DIVERSITY',
}


def is_landing_page(url):
    if not url or not isinstance(url, str):
        return True
    try:
        p = urlparse(url.strip())
    except Exception:
        return True
    if not p.scheme or not p.netloc:
        return True
    path = (p.path or '').strip()
    if LANDING_RE.match(path) and not p.query:
        return True
    return False


def is_official(url):
    if not isinstance(url, str):
        return False
    host = urlparse(url).netloc.lower()
    return any(h in host or h in url.lower() for h in OFFICIAL_HINTS)


def host_key(url):
    if not isinstance(url, str):
        return ''
    host = urlparse(url).netloc.lower()
    if host.startswith('www.'):
        host = host[4:]
    return host


def supports_visible_claim(source):
    if not isinstance(source, dict):
        return False
    if source.get('supporting_context_only_not_visible_claim_support') is True:
        return False
    role = source.get('evidence_role')
    supports = source.get('supports') or []
    if role in ('primary_event_evidence', 'secondary_event_evidence'):
        return True
    if isinstance(supports, list) and any(x in supports for x in ('title', 'sub', 'gate', 'fact', 'implication')):
        return True
    return False


def load_cards(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for k in ('cards', 'draft_cards', 'qc_cards', 'payload', 'accepted'):
            v = data.get(k)
            if isinstance(v, list):
                return v
    return []


def main():
    if len(sys.argv) < 2:
        print("usage: evidence_qc_v8_check.py <cards_or_qc_output.json>")
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

    for c in cards:
        if not isinstance(c, dict):
            continue
        cid = c.get('id', '<no-id>')
        fs = c.get('fact_sources', []) or []
        urls = c.get('urls', []) or []
        signal = str(c.get('signal', '')).lower()
        fs_urls = [s.get('source_url') for s in fs
                   if isinstance(s, dict) and s.get('source_url')]
        distinct_urls = set(fs_urls)
        visible_fs = [s for s in fs if supports_visible_claim(s)]
        visible_urls = [s.get('source_url') for s in visible_fs if s.get('source_url')]
        independent_hosts = {host_key(u) for u in visible_urls if host_key(u)}
        diversity_status = c.get('source_diversity_status')
        discovery_ledger = c.get('source_discovery_ledger') or c.get('source_discovery_ledger_ref') or c.get('source_discovery_ledger_reference')

        # (a) landing-page URLs
        for u in fs_urls:
            if is_landing_page(u):
                flags['landing_page'].append((cid, u))

        # (b) fake diversity
        if fs and len(distinct_urls) < len(fs):
            flags['fake_diversity'].append(
                (cid, f"{len(fs)} entries / {len(distinct_urls)} distinct urls"))

        # (c) single_source_exception required for 1-source cards
        if len(set(visible_urls)) <= 1 and not c.get('single_source_exception'):
            flags['missing_single_source_exception'].append(
                (cid, f"{len(set(visible_urls))} distinct visible-claim source"))
        if len(set(visible_urls)) <= 1:
            exc = c.get('single_source_exception')
            if not isinstance(exc, dict) or exc.get('allowed') is not True or not exc.get('reason'):
                flags['invalid_source_diversity_status'].append(
                    (cid, 'single-source exception missing allowed=true/reason'))
            if diversity_status == 'PASS_SINGLE_SOURCE':
                flags['invalid_source_diversity_status'].append(
                    (cid, 'PASS_SINGLE_SOURCE is not an allowed v9 status'))
            if diversity_status not in SOURCE_DIVERSITY_PASS | SOURCE_DIVERSITY_HOLD_FAIL:
                flags['invalid_source_diversity_status'].append(
                    (cid, f'missing/invalid source_diversity_status={diversity_status}'))
            if not discovery_ledger:
                flags['missing_source_discovery_ledger'].append(
                    (cid, 'single-source card lacks source_discovery_ledger/ref'))

        # (d) corroboration for high-signal / safety / market-share / ranking
        text_blob = ' '.join(str(c.get(k, ''))
                             for k in ('title', 'sub', 'gate', 'fact'))
        needs = signal in HIGH_SIGNAL or bool(CORROBORATION_RE.search(text_blob))
        if needs:
            independent = len(independent_hosts)
            has_official = any(is_official(u) for u in distinct_urls)
            if independent < 2 and not has_official:
                flags['weak_corroboration'].append(
                    (cid, f"signal={signal or '?'}, {independent} independent visible-source host, "
                          f"no official"))

        # (e) visible-source URL sync
        urlset = set(urls)
        for u in visible_urls:
            if u not in urlset:
                flags['url_desync'].append((cid, u))

        if diversity_status in SOURCE_DIVERSITY_PASS and not discovery_ledger:
            flags['missing_source_discovery_ledger'].append(
                (cid, f'{diversity_status} requires source_discovery_ledger/ref'))

    total = sum(len(v) for v in flags.values())
    print("=== R3C_P03 Evidence QC V8 mechanical check ===")
    print(f"cards checked: {len(cards)}")
    for name, items in flags.items():
        print(f"  {name}: {len(items)}")
        for cid, detail in items[:30]:
            print(f"      - {cid}: {detail}")
        if len(items) > 30:
            print(f"      ... (+{len(items) - 30} more)")
    print()
    if total:
        print(f"RESULT: {total} flag(s) - 0.5 is NOT pass. Each flag must be "
              f"verified by a human/assistant. Do NOT fabricate sources.")
        return 1
    print("RESULT: PASS - no V8 flags.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
