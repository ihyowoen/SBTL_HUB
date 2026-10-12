"""Materialize the reviewed IAA correction on its exact locked base, without publishing.
Run: python scripts/apply_iaa_correction.py
Then review the data diff, commit on the correction branch, and rerun governed gates.
"""
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
PACKET = ROOT / 'direct-adds/2026-10-08-iaa-proposal-correction'
patch = json.loads((PACKET / 'correction.json').read_text())
manifest_path = PACKET / 'direct-add.json'
if not manifest_path.exists():
    manifest_path = PACKET / 'direct-add.template.json'
manifest = json.loads(manifest_path.read_text())
base = patch['base_main_commit_sha']
# Validate every baseline lock before loading output candidates or writing any file.
if manifest['base_main_commit_sha'] != base:
    # Evidence/briefs may land first; the governed base must descend from the replay base
    # and preserve its exact canonical blob. Reject unknown or unrelated commits before writes.
    try:
        subprocess.run(['git', 'merge-base', '--is-ancestor', base, manifest['base_main_commit_sha']], cwd=ROOT, check=True, capture_output=True)
        locked_blob = subprocess.check_output(['git', 'rev-parse', f"{manifest['base_main_commit_sha']}:data/cards.full.json"], cwd=ROOT, text=True, stderr=subprocess.PIPE).strip()
        replay_blob = subprocess.check_output(['git', 'rev-parse', f'{base}:data/cards.full.json'], cwd=ROOT, text=True).strip()
        if locked_blob != replay_blob:
            raise ValueError('Canonical baseline changed')
    except (subprocess.CalledProcessError, ValueError) as exc:
        raise ValueError('Packet and manifest baseline disagree; no files written') from exc
actual_blob = subprocess.check_output(
    ['git', 'rev-parse', f'{base}:data/cards.full.json'], cwd=ROOT, text=True
).strip()
if actual_blob != manifest['base_full_blob_sha']:
    raise ValueError('Manifest base_full_blob_sha mismatch; no files written')

def load_base(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{base}:{path}'], cwd=ROOT))

full_before = load_base('data/cards.full.json')
full_after = json.loads(json.dumps(full_before))
index = next(i for i, c in enumerate(full_after['cards']) if c['id'] == patch['before_card']['id'])
if full_after['cards'][index] != patch['before_card']:
    raise ValueError('Locked before-card mismatch; no files written')
full_after['cards'][index] = patch['after_card']
full_after['updated'] = manifest['output_updated']
brief_before = load_base('public/data/briefs.json')
brief_after = json.loads(json.dumps(brief_before))
for revision in patch['brief_revisions']:
    index = next(i for i, b in enumerate(brief_after['items']) if b['id'] == revision['id'])
    if brief_after['items'][index] != revision['before']:
        raise ValueError('Locked before-brief mismatch; no files written')
    brief_after['items'][index] = revision['after']
brief_after['generated_at'] = '2026.10.08'
# Check all inputs before any write; fail closed on any undeclared main/inventory drift.
for path, before, after in [('data/cards.full.json', full_before, full_after), ('public/data/briefs.json', brief_before, brief_after)]:
    existing = json.loads((ROOT / path).read_text())
    if existing != before and existing != after:
        raise ValueError(f'{path}: drift; relock and review before apply; no files written')
# Idempotent exact replay, preserving repository formatting.
for path, after, indent in [('data/cards.full.json', full_after, 2), ('public/data/briefs.json', brief_after, 1)]:
    (ROOT / path).write_text(json.dumps(after, ensure_ascii=False, indent=indent) + '\n')
subprocess.run(['node', 'scripts/lean_cards.mjs'], cwd=ROOT, check=True)
subprocess.run(['python', 'scripts/test_iaa_correction.py'], cwd=ROOT, check=True)
print('MATERIALIZED LOCALLY ONLY: review and commit data diff; no merge or deployment performed')
