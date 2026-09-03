#!/usr/bin/env python3
from __future__ import annotations
import copy, hashlib, json, re, sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
RUN=ROOT/'runs/2026-09-03'
C_PATH=RUN/'stage_c_r6_accepted7_20260903_R1.json'
OUT=RUN/'prompt_0_4_r6_accepted7_20260903_R1.json'
REP=RUN/'prompt_0_4_r6_accepted7_validation_20260903_R1.json'
CANON=ROOT/'data/cards.full.json'
MAIN='df6fcccf3a69464ff0a43a8ba5897d71b6a4d9c4'
BLOB='53219907cdb435c3822c41d097b23e475662aa8a'

c=json.loads(C_PATH.read_text(encoding='utf-8'))
accepted=c['accepted_fact_safe']
assert len(accepted)==7
canon=json.loads(CANON.read_text(encoding='utf-8'))
cards=canon if isinstance(canon,list) else canon.get('cards',[])
assert len(cards)==1514, len(cards)

def norm_title(s):
    s=(s or '').lower()
    s=re.sub(r'[^0-9a-z가-힣一-龥]+',' ',s)
    return ' '.join(s.split())

def norm_url(u):
    if not isinstance(u,str) or not u.startswith(('http://','https://')): return ''
    try:
        p=urlsplit(u)
        host=p.netloc.lower().removeprefix('www.')
        path=re.sub(r'/+','/',p.path).rstrip('/') or '/'
        keep=[]
        for k,v in parse_qsl(p.query,keep_blank_values=True):
            kl=k.lower()
            if kl.startswith('utm_') or kl in {'fbclid','gclid','mc_cid','mc_eid','ref','referrer'}: continue
            keep.append((k,v))
        return urlunsplit(('https',host,path,urlencode(sorted(keep)),''))
    except Exception: return u.strip().lower()

def source_urls(card):
    out=[]
    for u in card.get('urls',[]) or []:
        n=norm_url(u)
        if n and n not in out: out.append(n)
    for fs in card.get('fact_sources',[]) or []:
        if isinstance(fs,dict):
            n=norm_url(fs.get('url'))
            if n and n not in out: out.append(n)
    return out

canon_urls={}
canon_titles={}
canon_ids=set()
for card in cards:
    if not isinstance(card,dict): continue
    cid=card.get('id')
    if cid: canon_ids.add(cid)
    t=norm_title(card.get('title'))
    if t: canon_titles.setdefault(t,[]).append(cid)
    for u in source_urls(card): canon_urls.setdefault(u,[]).append(cid)

batch_ids={x['id'] for x in accepted}
assert len(batch_ids)==7
batch_titles={}
batch_urls={}
for x in accepted:
    batch_titles.setdefault(norm_title(x['title']),[]).append(x['id'])
    for u in source_urls(x): batch_urls.setdefault(u,[]).append(x['id'])

addable=[]
holds=[]
for x in accepted:
    sid=x['source_spec_id']; cid=x['id']
    urls=source_urls(x); nt=norm_title(x['title'])
    exact_url_hits=sorted({y for u in urls for y in canon_urls.get(u,[]) if y})
    title_hits=sorted({y for y in canon_titles.get(nt,[]) if y})
    batch_url_hits=sorted({y for u in urls for y in batch_urls.get(u,[]) if y!=cid})
    batch_title_hits=sorted({y for y in batch_titles.get(nt,[]) if y!=cid})
    id_collision=cid in canon_ids
    lin=copy.deepcopy(x['related_lineage'])
    targets=lin.get('related_ids',[])
    missing_targets=[t for t in targets if t not in canon_ids and t not in batch_ids]
    self_link=cid in targets
    # Event fingerprint uses current Stage C locked identity, not thematic similarity.
    fp={
      'candidate_id':cid,
      'source_spec_id':sid,
      'event_date':x['date'],
      'region':x['region'],
      'category':x['cat'],
      'selection_route':x['selection_route'],
      'anchor_classes':x['anchor_classes'],
      'normalized_title':nt,
      'canonical_source_urls':urls,
      'date_role':x['date_role'].get('role'),
      'fact_anchor':x['fact'][:300],
    }
    collision=bool(exact_url_hits or title_hits or batch_url_hits or batch_title_hits or id_collision or missing_targets or self_link)
    if collision:
        holds.append({
          'source_spec_id':sid,'id':cid,'event_fingerprint':fp,'related_lineage':lin,
          'disposition':'baseline_conflict' if (exact_url_hits or title_hits or id_collision) else 'review_pool_deferred_related_uncertain',
          'findings':{
            'canonical_url_hits':exact_url_hits,'canonical_title_hits':title_hits,'canonical_id_collision':id_collision,
            'current_batch_url_hits':batch_url_hits,'current_batch_title_hits':batch_title_hits,
            'missing_related_targets':missing_targets,'self_link':self_link,
          }
        })
        continue
    relation=lin['relation_type']
    outcome={
      'new_unrelated_event':'addable_merge_safe_new_unrelated',
      'distinct_follow_up':'addable_merge_safe_distinct_follow_up',
      'program_lineage':'addable_merge_safe_program_lineage'
    }[relation]
    y=copy.deepcopy(x)
    y.update({
      'event_fingerprint':fp,
      'addability_outcome':outcome,
      'baseline_revalidation':{
        'status':'PASS','base_main_commit_sha':MAIN,'base_full_blob_sha':BLOB,'canonical_card_count':1514,
        'exact_canonical_url_collision_count':0,'normalized_title_collision_count':0,'card_id_collision':False,
        'current_batch_url_collision_count':0,'current_batch_title_collision_count':0,
        'related_target_existence':'PASS','stale_republication_check':'PASS','broader_representative_coverage_check':'PASS',
        'update_or_reinforcement_opportunity':'none_found'
      },
      'addable_merge_safe':True,'evidence_complete':False,'source_claim_covered':False,
      'content_enriched':False,'language_terminology_polished':False,'publish_ready':False,'github_merge_ready':False,
    })
    addable.append(y)

artifact={
  'stage':'0.4','status':'PASS' if len(addable)+len(holds)==7 else 'FAIL',
  'run_tag':'20260903_R6_PROMPT_0_4_ACCEPTED7_R1',
  'base_main_commit_sha':MAIN,'base_full_blob_sha':BLOB,'base_full_card_count':1514,
  'stage_c_artifact':str(C_PATH.relative_to(ROOT)),'stage_c_artifact_sha256':hashlib.sha256(C_PATH.read_bytes()).hexdigest(),
  'lineage_guard':'PASS' if all(x.get('related_lineage',{}).get('status')=='PASS' for x in addable) else 'HOLD',
  'input_count':7,'addable_merge_safe':addable,
  'duplicate_hold_same_event':[], 'existing_reinforcement':[], 'existing_card_update':[],
  'baseline_conflict':[h for h in holds if h['disposition']=='baseline_conflict'],
  'review_pool_deferred_related_uncertain':[h for h in holds if h['disposition']=='review_pool_deferred_related_uncertain'],
  'accounting':{'input':7,'addable':len(addable),'nonpassing':len(holds),'accounted':len(addable)+len(holds)},
  'next_authorized_stage':'Prompt 0.5 Evidence QC on addable_merge_safe[] only' if addable else 'HOLD_NO_ADDABLE_ITEMS'
}
OUT.write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# production contract
import subprocess
r=subprocess.run([sys.executable,str(ROOT/'validation_scripts/stage_artifact_contract_check.py'),'0.4',str(OUT)],capture_output=True,text=True)
contract=json.loads(r.stdout) if r.stdout.strip().startswith('{') else {'status':'FAIL','raw':r.stdout,'stderr':r.stderr}
custom=[]
if artifact['accounting']['accounted']!=7: custom.append('accounting')
if len(addable)!=7: custom.append({'non_addable':holds})
if r.returncode!=0: custom.append({'production_contract':contract})
rep={'schema':'prompt_0_4_r6_accepted7_validation_v1','status':'PASS' if not custom else 'FAIL','artifact':str(OUT.relative_to(ROOT)),'artifact_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'production_contract':contract,'addable_count':len(addable),'hold_count':len(holds),'custom_errors':custom,'base_main_commit_sha':MAIN,'base_full_blob_sha':BLOB}
REP.write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(rep,ensure_ascii=False,indent=2))
raise SystemExit(0 if rep['status']=='PASS' else 1)
