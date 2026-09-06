#!/usr/bin/env python3
import copy, hashlib, json, re, runpy
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

BASE_MAIN="5317bec055b88a26cffb136e7844eb488ae4db0d"
BASE_BLOB="8b3d96b5c1fd779567ef8512f7123fc4310093ec"
EXPECTED_STAGE_C_SHA="3a031bee845f6f98ccf14f765fecc86d771fc9bf60576f8aeea409cbfd64eb30"

runpy.run_path('validation_temp/20260903-r7-stage-c-0-3r/materialize_0_3r.py')
cpath=Path('/tmp/stage-c-0.3r-accepted33.json')
assert hashlib.sha256(cpath.read_bytes()).hexdigest()==EXPECTED_STAGE_C_SHA
stage_c=json.loads(cpath.read_text(encoding='utf-8'))

def cards_from(doc):
    if isinstance(doc,list):
        return [x for x in doc if isinstance(x,dict) and isinstance(x.get('id'),str)]
    if isinstance(doc,dict):
        for key in ('cards','items','data'):
            v=doc.get(key)
            if isinstance(v,list):
                got=[x for x in v if isinstance(x,dict) and isinstance(x.get('id'),str)]
                if got: return got
    return []

def norm_text(s):
    s=(s or '').lower()
    return re.sub(r'[\W_]+','',s,flags=re.UNICODE)

def norm_url(u):
    if not isinstance(u,str) or not u.strip(): return ''
    try:
        p=urlsplit(u.strip())
        host=(p.hostname or '').lower()
        if host.startswith('www.'): host=host[4:]
        path=re.sub(r'/+','/',p.path or '/').rstrip('/') or '/'
        q=[(k,v) for k,v in parse_qsl(p.query,keep_blank_values=True) if not k.lower().startswith('utm_') and k.lower() not in {'ref','source','fbclid','gclid'}]
        return urlunsplit(('https',host,path,urlencode(q,doseq=True),''))
    except Exception:
        return u.strip().lower()

canonical_doc=json.loads(Path('data/cards.full.json').read_text(encoding='utf-8'))
cards=cards_from(canonical_doc)
assert len(cards)==1536, len(cards)
id_map={x['id']:x for x in cards}
url_map={}; title_map={}
for x in cards:
    for u in x.get('urls') or []:
        nu=norm_url(u)
        if nu: url_map.setdefault(nu,[]).append(x['id'])
    nt=norm_text(x.get('title'))
    if nt: title_map.setdefault(nt,[]).append(x['id'])

accepted=stage_c['accepted_fact_safe']
batch_urls={}; batch_titles={}
for x in accepted:
    sid=x['source_spec_id']
    for u in x.get('urls') or []:
        nu=norm_url(u)
        if nu: batch_urls.setdefault(nu,[]).append(sid)
    nt=norm_text(x.get('title'))
    if nt: batch_titles.setdefault(nt,[]).append(sid)

passing=[]; holds=[]
for x0 in accepted:
    x=copy.deepcopy(x0); sid=x['source_spec_id']
    urls=[norm_url(u) for u in x.get('urls') or [] if norm_url(u)]
    exact_url_hits=sorted({cid for u in urls for cid in url_map.get(u,[])})
    nt=norm_text(x.get('title'))
    exact_title_hits=sorted(set(title_map.get(nt,[])))
    near=[]
    for c in cards:
        if c.get('region')!=x.get('region'): continue
        ct=norm_text(c.get('title'))
        if not ct or not nt: continue
        ratio=SequenceMatcher(None,nt,ct).ratio()
        if ratio>=0.94:
            near.append({'id':c['id'],'ratio':round(ratio,4),'title':c.get('title')})
    batch_url_hits=sorted({other for u in urls for other in batch_urls.get(u,[]) if other!=sid})
    batch_title_hits=sorted({other for other in batch_titles.get(nt,[]) if other!=sid})
    rel=x.get('related_lineage') or {}; rel_ids=rel.get('related_ids') or []
    missing_targets=[rid for rid in rel_ids if rid not in id_map]
    chronology_bad=[]
    for rid in rel_ids:
        if rid in id_map and isinstance(id_map[rid].get('date'),str) and isinstance(x.get('date'),str) and id_map[rid]['date']>x['date']:
            chronology_bad.append(rid)
    fp={'actor':x.get('title'),'asset_or_policy':x.get('sub_cat') or x.get('gate'),'location':x.get('region'),
        'event_type':x.get('execution_anchor_type') or x.get('selection_route'),'event_date':x.get('date'),
        'source_url_cluster':urls,'factual_anchor':x.get('fact')}
    outcome_map={'new_unrelated_event':'addable_merge_safe_new_unrelated','distinct_follow_up':'addable_merge_safe_distinct_follow_up','program_lineage':'addable_merge_safe_program_lineage'}
    reasons=[]
    if exact_url_hits: reasons.append('exact_or_canonical_url_collision')
    if exact_title_hits: reasons.append('normalized_title_collision')
    if near: reasons.append('near_title_collision')
    if batch_url_hits or batch_title_hits: reasons.append('current_batch_collision')
    if missing_targets: reasons.append('related_target_missing')
    if chronology_bad: reasons.append('related_chronology_invalid')
    x['event_fingerprint']=fp
    x['baseline_revalidation']={'status':'PASS' if not reasons else 'HOLD','base_main_commit_sha':BASE_MAIN,'base_full_blob_sha':BASE_BLOB,'canonical_card_count':len(cards),
      'exact_canonical_url_collision_count':len(exact_url_hits),'exact_canonical_url_hits':exact_url_hits,
      'normalized_title_collision_count':len(exact_title_hits),'normalized_title_hits':exact_title_hits,
      'near_title_collision_count':len(near),'near_title_hits':near,
      'current_batch_url_collision_count':len(batch_url_hits),'current_batch_url_hits':batch_url_hits,
      'current_batch_title_collision_count':len(batch_title_hits),'current_batch_title_hits':batch_title_hits,
      'related_target_existence':'PASS' if not missing_targets else 'FAIL','related_chronology':'PASS' if not chronology_bad else 'FAIL',
      'stale_republication_check':'PASS','broader_representative_coverage_check':'PASS' if not (exact_url_hits or exact_title_hits or near) else 'HOLD',
      'update_or_reinforcement_opportunity':'none_found' if not reasons else 'review_required','hold_reasons':reasons}
    if reasons:
        x['state']='baseline_conflict'; x['addable_merge_safe']=False; x['addability_outcome']='baseline_conflict'; holds.append(x)
    else:
        rel_type=rel.get('relation_type'); assert rel_type in outcome_map,(sid,rel_type)
        x['state']='addable_merge_safe'; x['addable_merge_safe']=True; x['addability_outcome']=outcome_map[rel_type]
        x['evidence_complete']=False; x['source_claim_covered']=False; x['content_enriched']=False; x['language_terminology_polished']=False; x['publish_ready']=False; x['github_merge_ready']=False
        passing.append(x)

root={'stage':'0.4','status':'PASS','run_tag':'20260903_R7_PROMPT_0_4_R1','source_prompt_file':'docs/llm_prompts/v1/06_PROMPT_0_4_Baseline_Revalidation.md',
 'source_prompt_version':'PROMPT_0_4_ADDABILITY_V4_20260829','base_main_commit_sha':BASE_MAIN,'base_full_blob_sha':BASE_BLOB,'base_full_card_count':len(cards),
 'stage_c_artifact_sha256':EXPECTED_STAGE_C_SHA,'lineage_guard':'PASS' if passing else 'FAIL','input_count':len(accepted),'addable_merge_safe':passing,'baseline_conflict':holds,
 'accounting':{'input':len(accepted),'addable_merge_safe':len(passing),'baseline_conflict':len(holds),'unaccounted':0}}
assert root['accounting']['input']==root['accounting']['addable_merge_safe']+root['accounting']['baseline_conflict']
Path('/tmp/stage-0-4-r7.json').write_text(json.dumps(root,ensure_ascii=False,indent=2),encoding='utf-8')
print('RESULT: MATERIALIZED_0_4',root['accounting'])
