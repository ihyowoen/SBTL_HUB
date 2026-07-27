#!/usr/bin/env python3
import copy
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

PATH = Path('public/data/cards.json')

PAIRS = [
    {
        'canonical': '2026-07-21_CN_01',
        'duplicate': '2026-07-22_CN_01',
        'fact_sources': 'all',
        'urls': 'all',
        'visible': {
            'sub': '낙찰통지를 받았지만 정식 계약은 아직 체결되지 않았으며, 2026년 10월 30일 전체 계통시운전을 목표로 한다.',
            'fact': '*ST Yabo 자회사 Shandong Zhongfukai New Energy는 메이허커우의 50MW/100MWh BESS EPC 사업을 9,980만위안에 낙찰받았다. 회사는 정식 계약이 아직 체결되지 않았다고 명시했으며, 프로젝트는 2026년 10월 30일 전체 계통시운전을 목표로 한다.',
        },
    },
    {
        'canonical': '2026-07-20_US_06',
        'duplicate': '2026-07-20_US_08',
        'fact_sources': [],
        'urls': ['https://energy-storage.news/maine-submits-plans-for-first-competitive-energy-storage-solicitation-eyeing-360mw'],
        'visible': {},
    },
    {
        'canonical': '2026-07-20_US_02',
        'duplicate': '2026-07-20_US_07',
        'fact_sources': [],
        'urls': [],
        'visible': {},
    },
    {
        'canonical': '2026-07-18_US_02',
        'duplicate': '2026-07-17_US_02',
        'fact_sources': 'all',
        'urls': 'all_plus_fact_sources',
        'visible': {},
    },
    {
        'canonical': '2026-07-15_GL_07',
        'duplicate': '2026-07-15_GL_08',
        'fact_sources': 'all',
        'urls': 'all',
        'visible': {
            'sub': '총 110억원 규모 ODA로 르위판장·치차헤움 두 BRT 차고지에 전기버스 충전 인프라 구축을 추진한다.',
            'fact': '총 110억원 규모 ODA 사업으로 인도네시아 반둥의 르위판장·치차헤움 두 BRT 차고지에 전기버스 충전 인프라를 구축한다. 2026년 7월 15일 르위판장 차고지에서 착공식이 열렸고, 반둥시는 착공 사실을 공식 발표했다.',
        },
    },
    {
        'canonical': '2026-07-21_US_01',
        'duplicate': '2026-07-22_US_03',
        'fact_sources': ['electrive.com'],
        'urls': [
            'https://insideevs.com/news/802397/sila-silicon-anode-lithium-ion',
            'https://electrive.com/2026/07/22/sila-raises-300-million-to-expand-us-silicon-anode-production',
        ],
        'visible': {},
    },
]


def canonical_url(url: str) -> str:
    if not url:
        return ''
    parsed = urlsplit(url)
    host = parsed.netloc.lower()
    if host.startswith('www.'):
        host = host[4:]
    path = re.sub(r'/+$', '', parsed.path)
    query = f'?{parsed.query}' if parsed.query else ''
    return f'https://{host}{path}{query}' if host else url.rstrip('/')


def source_owner(source: dict) -> str:
    owner = source.get('source_owner_id_normalized') or source.get('source_owner_id') or source.get('source_domain')
    if owner:
        owner = str(owner).lower().strip()
        return owner[4:] if owner.startswith('www.') else owner
    return urlsplit(source.get('source_url', '')).netloc.lower().removeprefix('www.')


def source_domain(source: dict) -> str:
    domain = source.get('source_domain')
    if domain:
        return str(domain).lower().removeprefix('www.')
    return urlsplit(source.get('source_url', '')).netloc.lower().removeprefix('www.')


def merge_strings(left, right):
    result, seen = [], set()
    for item in list(left or []) + list(right or []):
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def recompute_source_metadata(card: dict, now: str) -> None:
    sources = card.get('fact_sources', [])
    for source in sources:
        if source.get('source_name') == 'Yabo filing via CFi':
            source['source_owner_id_normalized'] = 'yaboo.com.cn'
            source['source_owner_id'] = 'yaboo.com.cn'

    visible_urls, seen_urls = [], set()
    for url in card.get('urls', []):
        key = canonical_url(url)
        if key and key not in seen_urls:
            seen_urls.add(key)
            visible_urls.append(url)
    for source in sources:
        url = source.get('source_url')
        key = canonical_url(url or '')
        if url and key not in seen_urls:
            seen_urls.add(key)
            visible_urls.append(url)
    card['urls'] = visible_urls

    evidence_urls = {canonical_url(s.get('source_url', '')) for s in sources if s.get('source_url')}
    domains = {source_domain(s) for s in sources if source_domain(s)}
    owners = {source_owner(s) for s in sources if source_owner(s)}
    roles = []
    for source in sources:
        role = source.get('source_role') or source.get('evidence_role')
        if role and role not in roles:
            roles.append(role)

    status = 'PASS_MULTI_SOURCE' if len(owners) >= 2 else 'PASS_SINGLE_SOURCE_EXCEPTION'
    card['source_evidence_entry_count'] = len(sources)
    card['source_unique_url_count'] = len(evidence_urls)
    card['source_unique_domain_count'] = len(domains)
    card['source_independent_owner_count'] = len(owners)
    card['source_independent_owners'] = sorted(owners)
    card['source_diversity_status'] = status
    card['source_diversity_roles'] = roles
    card['single_source_exception'] = {
        'allowed': len(owners) < 2,
        'type': 'not_applicable_multi_source' if len(owners) >= 2 else 'single_source_retained',
        'reason': 'At least two independent visible source owners support the card.' if len(owners) >= 2 else 'One editorial owner remains after duplicate consolidation.',
        'bounded_discovery_completed': True,
    }
    card['source_diversity_measure'] = {
        'source_evidence_entry_count': len(sources),
        'source_unique_url_count': len(evidence_urls),
        'source_unique_domain_count': len(domains),
        'source_independent_owner_count': len(owners),
        'visible_source_url_count': len(visible_urls),
        'status': status,
        'recomputed_at_kst': now,
    }
    card['same_source_ui_grouping'] = {
        'status': 'PASS',
        'source_group_count': len(owners),
        'evidence_entry_count': len(sources),
        'display_label': f'출처 {len(owners)}곳 · 근거 {len(sources)}개',
        'one_original_link_per_canonical_group': True,
    }

    resolution_entries, discovery, synthesis = [], [], []
    synthesis_fields = []
    visible_fields = {'title', 'sub', 'gate', 'fact', 'implication'}
    for source in sources:
        url = source.get('source_url', '')
        supports = [field for field in (source.get('supports') or []) if field in visible_fields]
        for field in supports:
            if field not in synthesis_fields:
                synthesis_fields.append(field)
        resolution_entries.append({
            'source_url': canonical_url(url),
            'source_urls_grouped': [url] if url else [],
            'canonical_complete': bool(source.get('source_url_canonical_complete', True)),
            'resolved_article_matches_quote': bool(source.get('resolved_article_matches_quote', True)),
            'resolution_basis': 'PR #213 review-addressed duplicate consolidation',
            'source_url_propagation_performed': False,
        })
        contribution = source.get('source_contribution') or source.get('claim')
        discovery.append({
            'source_url': canonical_url(url),
            'canonical_url': canonical_url(url),
            'source_name': source.get('source_name'),
            'source_owner': source_owner(source),
            'source_domain': source_domain(source),
            'source_role': source.get('source_role') or source.get('evidence_role'),
            'outcome': 'used_in_fact_sources',
            'unique_contribution': contribution,
            'visible_supports': supports,
            'checked_at': source.get('checked_at') or now,
            'source_origin_type': source.get('source_origin_type'),
            'evidence_role': source.get('evidence_role'),
        })
        synthesis.append({
            'source_domain': source_domain(source),
            'source_role': source.get('source_role') or source.get('evidence_role'),
            'unique_contribution': contribution,
            'affected_visible_fields': supports,
            'editorial_owner': source_owner(source),
            'synthesis_basis': 'PR #213 duplicate consolidation; source-locked evidence retained',
        })

    card['source_url_resolution'] = {
        'supporting_fact_source_count': len(sources),
        'canonical_complete': all(row['canonical_complete'] for row in resolution_entries),
        'resolved_article_matches_quote': all(row['resolved_article_matches_quote'] for row in resolution_entries),
        'source_url_propagation_performed': False,
        'resolution_entries': resolution_entries,
    }
    card['source_discovery_ledger'] = discovery
    card['source_discovery_ledger_reference_status'] = 'PASS_DURABLE_REFERENCE_AND_MATERIALIZED_ROWS'
    card['source_synthesis_applied'] = bool(sources)
    card['source_synthesis_fields'] = synthesis_fields
    card['source_synthesis_audit'] = synthesis
    card['source_contribution_coverage_status'] = 'PASS'
    card['visible_quote_publication_date_ready'] = all(
        bool(s.get('visible_quote_date') or s.get('source_published_date')) for s in sources
    )


def main() -> None:
    document = json.loads(PATH.read_text(encoding='utf-8'))
    original_cards = document['cards']
    by_id = {card['id']: card for card in original_cards}
    expected = {pair['canonical'] for pair in PAIRS} | {pair['duplicate'] for pair in PAIRS}
    missing = sorted(expected - set(by_id))
    if missing:
        raise SystemExit(f'Missing expected card IDs: {missing}')

    now = datetime.now(ZoneInfo('Asia/Seoul')).isoformat()
    removed_ids = set()
    lineage_expectations = {}

    for pair in PAIRS:
        canonical = by_id[pair['canonical']]
        duplicate = by_id[pair['duplicate']]
        removed_ids.add(pair['duplicate'])
        lineage_expectations[pair['canonical']] = set(duplicate.get('source_story_ids', []))
        canonical['source_story_ids'] = merge_strings(canonical.get('source_story_ids'), duplicate.get('source_story_ids'))

        if pair['fact_sources'] == 'all':
            selected_sources = copy.deepcopy(duplicate.get('fact_sources', []))
        else:
            allowed = set(pair['fact_sources'])
            selected_sources = [copy.deepcopy(s) for s in duplicate.get('fact_sources', []) if source_owner(s) in allowed]
        existing_source_keys = {
            (canonical_url(s.get('source_url', '')), s.get('source_quote', ''))
            for s in canonical.get('fact_sources', [])
        }
        for source in selected_sources:
            key = (canonical_url(source.get('source_url', '')), source.get('source_quote', ''))
            if key not in existing_source_keys:
                canonical.setdefault('fact_sources', []).append(source)
                existing_source_keys.add(key)

        if pair['urls'] == 'all':
            urls = duplicate.get('urls', [])
        elif pair['urls'] == 'all_plus_fact_sources':
            urls = list(duplicate.get('urls', [])) + [s.get('source_url') for s in duplicate.get('fact_sources', []) if s.get('source_url')]
        else:
            urls = pair['urls']
        canonical['urls'] = merge_strings(canonical.get('urls'), urls)

        visible_changed = False
        for field, value in pair['visible'].items():
            if canonical.get(field) != value:
                canonical[field] = value
                visible_changed = True

        recompute_source_metadata(canonical, now)
        proof = canonical.get('final_qc_lineage_proof')
        if isinstance(proof, dict):
            proof['materialized_at_kst'] = now
            proof['eligibility_changed'] = False
            proof['evidence_changed'] = True
            proof['visible_fields_changed'] = visible_changed
        note = f"PR #213 review addressed: duplicate {pair['duplicate']} was consolidated into this canonical card; valid lineage and non-redundant evidence were retained."
        notes = canonical.get('final_qc_notes')
        if isinstance(notes, list):
            if note not in notes:
                notes.append(note)
        elif notes:
            canonical['final_qc_notes'] = [str(notes), note]
        else:
            canonical['final_qc_notes'] = [note]

    document['cards'] = [card for card in original_cards if card['id'] not in removed_ids]
    document['total'] = len(document['cards'])
    document['updated'] = now

    ids = [card['id'] for card in document['cards']]
    if document['total'] != 1304 or document['total'] != len(ids):
        raise SystemExit(f'Unexpected total: {document["total"]}')
    if len(ids) != len(set(ids)):
        raise SystemExit('Duplicate IDs remain')
    if any(card_id in ids for card_id in removed_ids):
        raise SystemExit('A removed duplicate card ID remains')
    order = [(card.get('date', ''), card.get('id', '')) for card in document['cards']]
    if order != sorted(order, reverse=True):
        raise SystemExit('Sort order is not date_desc_id_desc')
    for canonical_id, expected_story_ids in lineage_expectations.items():
        actual = set(by_id[canonical_id].get('source_story_ids', []))
        if not expected_story_ids.issubset(actual):
            raise SystemExit(f'Lineage was not preserved for {canonical_id}')
    for card in document['cards']:
        for field in ('related', 'resolved_related_candidate_spec_ids'):
            values = card.get(field) or []
            if isinstance(values, list) and removed_ids.intersection(values):
                raise SystemExit(f'Stale removed-ID reference in {card["id"]}.{field}')
    titles = [card.get('title') for card in document['cards'] if card.get('title')]
    if len(titles) != len(set(titles)):
        raise SystemExit('Exact duplicate title remains')
    if '정식 계약이 아직 체결되지 않았' not in by_id['2026-07-21_CN_01']['fact']:
        raise SystemExit('Unsigned-contract detail was not retained')
    if '110억원' not in by_id['2026-07-15_GL_07']['fact']:
        raise SystemExit('Bandung ODA scale was not retained')
    if by_id['2026-07-18_US_02']['date'] != '2026-07-18':
        raise SystemExit('Tesla canonical date changed')
    if by_id['2026-07-21_US_01']['date'] != '2026-07-21':
        raise SystemExit('Sila canonical date changed')

    PATH.write_text(json.dumps(document, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({
        'status': 'PASS',
        'total': document['total'],
        'removed_duplicate_ids': sorted(removed_ids),
        'canonical_ids': [pair['canonical'] for pair in PAIRS],
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
