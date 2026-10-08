"""Pinned-base replay and negative regressions for the bounded IAA correction.
Run: python scripts/test_iaa_correction.py
No network, credentials, writes, or live legal-status inference.
"""
import copy
import json
import pathlib
import subprocess
import unittest
import tempfile
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PACKET = ROOT / 'direct-adds/2026-10-08-iaa-proposal-correction'
ID = '2026-05-13_EU_01'
PATCH = json.loads((PACKET / 'correction.json').read_text())
MANIFEST_PATH = PACKET / 'direct-add.json'
if not MANIFEST_PATH.exists():
    MANIFEST_PATH = PACKET / 'direct-add.template.json'
MANIFEST = json.loads(MANIFEST_PATH.read_text())
BASE = PATCH['base_main_commit_sha']


def baseline(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


def current(path):
    return json.loads((ROOT / path).read_text())


def replay():
    full = baseline('data/cards.full.json')
    index = next(i for i, c in enumerate(full['cards']) if c['id'] == ID)
    assert full['cards'][index] == PATCH['before_card']
    full['cards'][index] = copy.deepcopy(PATCH['after_card'])
    full['updated'] = MANIFEST['output_updated']
    briefs = baseline('public/data/briefs.json')
    for revision in PATCH['brief_revisions']:
        index = next(i for i, b in enumerate(briefs['items']) if b['id'] == revision['id'])
        assert briefs['items'][index] == revision['before']
        briefs['items'][index] = copy.deepcopy(revision['after'])
    briefs['generated_at'] = '2026.10.08'
    return full, briefs


def validate_surface(card, briefs):
    before = PATCH['before_card']
    for key in ('id', 'date', 'region', 'related', 'related_lineage', 'baseline_id_assignment'):
        assert card[key] == before[key], key
    assert '제안 심의' in card['title']
    assert '미시행' in card['sub']
    assert 'Awaiting committee decision' in card['fact']
    assert '2026/0068(COD)' in card['fact']
    assert '채택·발효된 규정이 아니다' in card['fact']
    assert '40%를 초과' in card['fact'] and '1억 유로를 초과' in card['fact']
    assert 'EU 근로자 최소 50%' in card['fact'] and '12개월' in card['fact']
    text = json.dumps({k: card[k] for k in ('title','sub','gate','fact','implication')}, ensure_ascii=False)
    for bad in ('발효 진입', 'NCM 으로 강제', 'EU NCM 우선 정책', '6 of 4', '중국 supply chain 격리'):
        assert bad not in text, bad
    assert card['source_tier'] == 'primary'
    for source in card['fact_sources']:
        assert source['verification_status'] == 'verified_official_document'
        assert source['source_document_support'] and source['source_locator'] and source['audit_fetched_at']
    assert any('oeil.europarl.europa.eu' in s['source_url'] for s in card['fact_sources'])
    assert any('Annex III' in s['source_locator'] for s in card['fact_sources'])
    assert before['urls'][0] in card['urls']  # old event anchor retained as historical source
    affected = [b for b in briefs['items'] if any(r.get('id') == ID for r in b.get('refs', []))]
    assert len(affected) == 2
    for brief in affected:
        assert '시행 중인 IAA 의무가 아니다' in brief['narrative']
        assert '확정 수순' not in brief['narrative']
        assert any('제안 단계' in w and '단정하지 않는다' in w for w in brief['watch'])
        for ref in brief['refs']:
            if ref.get('id') == ID:
                assert ref['title'] == card['title'] and ref['url'] == card['urls'][0]
                assert ref['date'] == before['date']


class IAACorrectionTests(unittest.TestCase):
    def test_exact_replay_and_unrelated_inventory_preservation(self):
        full, briefs = replay()
        self.assertEqual(full, current('data/cards.full.json'))
        self.assertEqual(briefs, current('public/data/briefs.json'))
        self.assertEqual(full['total'], 1674)
        self.assertEqual(len(full['cards']), 1674)
        self.assertEqual(subprocess.check_output(['git', 'rev-parse', f"{MANIFEST['base_main_commit_sha']}:data/cards.full.json"], cwd=ROOT).strip(), subprocess.check_output(['git', 'rev-parse', f'{BASE}:data/cards.full.json'], cwd=ROOT).strip())
        blob = subprocess.check_output(['git','rev-parse',f'{BASE}:data/cards.full.json'],cwd=ROOT,text=True).strip()
        self.assertEqual(blob, MANIFEST['base_full_blob_sha'])

    def test_all_public_surfaces(self):
        full = current('data/cards.full.json')
        lean = current('public/data/cards.json')
        card = next(c for c in full['cards'] if c['id'] == ID)
        projected = next(c for c in lean['cards'] if c['id'] == ID)
        self.assertEqual(projected, {k: card[k] for k in projected})
        validate_surface(card, current('public/data/briefs.json'))

    def test_reject_old_enacted_headline(self):
        card = copy.deepcopy(PATCH['after_card']); card['title'] = PATCH['before_card']['title']
        with self.assertRaises(AssertionError): validate_surface(card, current('public/data/briefs.json'))

    def test_reject_identity_or_lineage_mutation(self):
        for key, value in [('id','2026-03-04_EU_01'),('date','2026-03-04'),('related',['new'])]:
            card = copy.deepcopy(PATCH['after_card']); card[key] = value
            with self.assertRaises(AssertionError): validate_surface(card, current('public/data/briefs.json'))

    def test_reject_missing_primary_evidence(self):
        card = copy.deepcopy(PATCH['after_card']); card['fact_sources'] = []
        with self.assertRaises(AssertionError): validate_surface(card, current('public/data/briefs.json'))

    def test_reject_stale_brief_narrative_watch_or_reference(self):
        for field in ('narrative','watch','refs'):
            briefs = current('public/data/briefs.json')
            rev = PATCH['brief_revisions'][0]
            item = next(b for b in briefs['items'] if b['id'] == rev['id'])
            item[field] = rev['before'][field]
            with self.assertRaises(AssertionError): validate_surface(PATCH['after_card'], briefs)

    def test_reject_wrong_threshold_or_missing_mandatory_condition(self):
        for a, b in [('40%를 초과','40% 이상'),('EU 근로자 최소 50%','EU 근로자 조건 선택')]:
            card = copy.deepcopy(PATCH['after_card']); card['fact'] = card['fact'].replace(a,b)
            with self.assertRaises(AssertionError): validate_surface(card, current('public/data/briefs.json'))


    def assert_lock_failure_leaves_outputs_unchanged(self, key, value):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / 'scripts').mkdir()
            shutil.copyfile(ROOT / 'scripts/apply_iaa_correction.py', root / 'scripts/apply_iaa_correction.py')
            packet = root / PACKET.relative_to(ROOT)
            packet.mkdir(parents=True)
            (packet / 'correction.json').write_text(json.dumps(PATCH))
            manifest = copy.deepcopy(MANIFEST)
            manifest[key] = value
            (packet / 'direct-add.json').write_text(json.dumps(manifest))
            # The sandbox only reads the pinned git objects; it never runs git mutation.
            gitdir = subprocess.check_output(['git', 'rev-parse', '--absolute-git-dir'], cwd=ROOT, text=True).strip()
            (root / '.git').write_text(f'gitdir: {gitdir}\n')
            outputs = ['data/cards.full.json', 'public/data/cards.json', 'public/data/briefs.json']
            for path in outputs:
                file = root / path
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_bytes(b'unchanged output sentinel')
            before = {path: (root / path).read_bytes() for path in outputs}
            result = subprocess.run(
                [sys.executable, str(root / 'scripts/apply_iaa_correction.py')],
                cwd=root, capture_output=True, text=True
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('no files written', result.stderr)
            self.assertEqual(before, {path: (root / path).read_bytes() for path in outputs})

    def test_apply_rejects_disagreeing_commit_lock_before_writes(self):
        self.assert_lock_failure_leaves_outputs_unchanged('base_main_commit_sha', '0' * 40)

    def test_apply_rejects_wrong_blob_lock_before_writes(self):
        self.assert_lock_failure_leaves_outputs_unchanged('base_full_blob_sha', '0' * 40)


if __name__ == '__main__':
    unittest.main(verbosity=2)
