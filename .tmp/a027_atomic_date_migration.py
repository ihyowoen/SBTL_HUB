from pathlib import Path
import datetime, json

BASE_SHA='233da6c88bd7f7f41cf7968269e4d9e50e40f84d'
BASE_BLOB='0e30034280304895c3d5cb9ad450bbabbeffb432'
OLD='2026-09-07_CN_01'
NEW='2026-09-06_CN_02'
NEW_DATE='2026-09-06'

p=Path('data/cards.full.json')
doc=json.loads(p.read_text(encoding='utf-8'))
cards=doc['cards']
ids={c['id'] for c in cards}
assert OLD in ids, f'missing {OLD}'
assert NEW not in ids, f'collision {NEW}'

refs=[]
for c in cards:
    if c['id']==OLD:
        continue
    if OLD in (c.get('related') or []): refs.append((c['id'],'related'))
    if OLD in (c.get('related_ids') or []): refs.append((c['id'],'related_ids'))
    rl=c.get('related_lineage')
    if isinstance(rl,dict):
        for k in ('related_ids','target_ids','related_candidate_ids'):
            v=rl.get(k)
            if isinstance(v,list) and OLD in v: refs.append((c['id'],f'related_lineage.{k}'))
        for k in ('target_id','predecessor_id','successor_id'):
            if rl.get(k)==OLD: refs.append((c['id'],f'related_lineage.{k}'))
assert not refs, f'inbound relation refs block migration: {refs}'

c=next(c for c in cards if c['id']==OLD)
assert c['date']=='2026-09-07'
assert isinstance(c.get('date_role'),dict), 'date_role missing'
assert isinstance(c.get('event_fingerprint'),dict), 'event_fingerprint missing'

c['id']=NEW
c['date']=NEW_DATE
for k in ('representative_event_date','representative_date','event_date'):
    assert k in c['date_role'], f'date_role.{k} missing'
    c['date_role'][k]=NEW_DATE
assert 'event_date' in c['event_fingerprint'], 'event_fingerprint.event_date missing'
c['event_fingerprint']['event_date']=NEW_DATE

now=datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
doc['updated']=now
doc['total']=len(cards)
p.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

out=Path('direct-adds/2026-09-09-a027-date-id-migration')
out.mkdir(parents=True,exist_ok=True)
manifest={
  'schema':'manual_direct_add_v2',
  'status':'PASS',
  'direct_add_id':'A027_ATOMIC_DATE_ID_MIGRATION_20260909_R2',
  'review_mode':'already_reviewed_bounded_direct_add',
  'formal_full_run_claimed':False,
  'base_main_commit_sha':BASE_SHA,
  'base_full_blob_sha':BASE_BLOB,
  'expected_before':len(cards),
  'expected_after':len(cards),
  'output_updated':now,
  'operations':{
    'add':[],
    'update':[],
    'id_migration':[{
      'old_id':OLD,
      'new_id':NEW,
      'reason':'Representative event date correction: original Cailianshe report was published on 2026-09-06 before the Reuters 2026-09-07 re-report; migrate identity and synchronize canonical representative-date metadata atomically.',
      'synchronized_fields':['date_role','event_fingerprint']
    }]
  },
  'editorial_attestation':{
    'policy_version':'EMBEDDED_NEWS_VALUE_SELECTION_V4',
    'additions':[],
    'updates':[]
  }
}
(out/'direct-add.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'old_id':OLD,'new_id':NEW,'new_date':NEW_DATE,'inbound_related_refs':refs,'output_updated':now},ensure_ascii=False,indent=2))
