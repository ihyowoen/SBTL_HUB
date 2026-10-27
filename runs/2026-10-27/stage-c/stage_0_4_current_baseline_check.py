#!/usr/bin/env python3
"""Isolated audit-only 0.4 stage from native Stage C-accepted JSON and checked-out GitHub Full.

Reads canonical Full at exact locked main; does not mutate Full/Lean/Related/production.
"""
import json, hashlib, re, sys, difflib
from pathlib import Path
from urllib.parse import urlsplit, parse_qsl, urlencode

C_PATH=Path('runs/2026-10-27/stage-c/STAGE_C_LATEST_ACCEPTED_NATIVE_SCHEMA_V2_20261027.json')
FULL_PATH=Path('data/cards.full.json')
OUTPUT=Path('runs/2026-10-27/stage-c/STAGE_0_4_CURRENT_BASELINE_ADDABILITY_20261027.json')
EXPECTED_MAIN='805c2718d6daf40a219ae94242d9687e33ac3e88'
EXPECTED_FULL='07a91714e56be2a8bfad10ab63822f0c5cb3f06e'

def blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()

def normalize_url(s):
    if not isinstance(s,str) or not s.strip(): return ''
    v=urlsplit(s.strip());
    host=(v.hostname or '').lower().removeprefix('www.')
    path=re.sub(r'/+','/',v.path).rstrip('/').lower()
    # Ignore known marketing parameters for comparison, preserve substantive article tokens.
    query=urlencode(sorted((k.lower(),val) for k,val in parse_qsl(v.query,keep_blank_values=True) if not k.lower().startswith(('utm_','fbclid','gclid','ref'))))
    return host+path+('?' + query if query else '')

def norm_title(s):
    return ''.join(re.findall(r'[\w가-힣]+',str(s).lower()))

def c_ids(row):
    x=row.get('source_story_ids',[]) or []
    if isinstance(x,list):return [i for i in x if isinstance(i,str)]
    return []

def main():
    C=json.loads(C_PATH.read_text(encoding='utf-8'))
    raw=FULL_PATH.read_bytes()
    blob_sha=blob(raw)
    FULL=json.loads(raw.decode('utf-8'))
    if isinstance(FULL,dict):cards=FULL.get('cards',[])
    elif isinstance(FULL,list):cards=FULL
    else: raise ValueError('Unexpected Full JSON type')
    if blob_sha != EXPECTED_FULL or C['base_full_blob_sha'] != EXPECTED_FULL:
        raise AssertionError('Full baseline has moved or mismatched')
    if C['base_main_commit_sha'] != EXPECTED_MAIN:
        raise AssertionError('Main commit mismatch')
    if len(cards)!=1676 or len(C['accepted_fact_safe'])!=7:
        raise AssertionError('Card source population changed')

    existing_by_id={str(c['id']):c for c in cards if isinstance(c,dict) and c.get('id')}
    if len(existing_by_id)!=1676: raise AssertionError('Non-unique Full IDs')
    url_index={}; title_index={}; source_id_index={}
    for card in cards:
        for url in (card.get('urls') or []):
            norm=normalize_url(url)
            if norm:url_index.setdefault(norm,set()).add(card['id'])
        t=norm_title(card.get('title',''))
        if t:title_index.setdefault(t,set()).add(card['id'])
        for sid in c_ids(card):source_id_index.setdefault(sid,set()).add(card['id'])

    seen_urls={};seen_titles={}; accepted=[]; held=[]; item_receipts=[]
    for candidate in C['accepted_fact_safe']:
        spec=candidate['source_spec_id']
        rel=candidate['related_lineage'];typ=rel['relation_type']
        candurls=sorted({normalize_url(u) for u in candidate.get('urls',[]) if normalize_url(u)})
        matches={z for u in candurls for z in url_index.get(u,())}
        ids={z for sid in c_ids(candidate) for z in source_id_index.get(sid,())}
        title=norm_title(candidate.get('title',''))
        same_title=title_index.get(title,set())
        self_batch_url_matches={n for u in candurls for n in seen_urls.get(u,())}
        self_batch_title_matches=set(seen_titles.get(title,[]))
        same_day_existing=[]
        for id in matches|same_title|ids:
            other=existing_by_id[id]
            if other.get('date')==candidate.get('date'):
                same_day_existing.append(id)
        problem=[]
        # A repeated source URL alone is not proof of a duplicate, but all observed clashes are escalated.
        if matches: problem.append('BASELINE_CANONICAL_URL_COLLISION:'+','.join(sorted(matches)))
        if ids:problem.append('BASELINE_SOURCE_STORY_ID_COLLISION:'+','.join(sorted(ids)))
        if same_title:problem.append('BASELINE_EXACT_NORMALIZED_TITLE_COLLISION:'+','.join(sorted(same_title)))
        if same_day_existing:problem.append('BASELINE_SAME_DATE_COLLISION:'+','.join(sorted(same_day_existing)))
        if self_batch_url_matches:problem.append('CURRENT_BATCH_CANONICAL_URL_COLLISION:'+','.join(sorted(self_batch_url_matches)))
        if self_batch_title_matches:problem.append('CURRENT_BATCH_TITLE_COLLISION:'+','.join(sorted(self_batch_title_matches)))
        if rel.get('status')!='PASS':problem.append('RELATED_NOT_STAGE_C_PASS')
        if typ=='distinct_follow_up':
            predecessors=rel.get('related_ids',[])
            missing=[z for z in predecessors if z not in existing_by_id]
            if missing:problem.append('MISSING_DIRECT_PREDECESSOR:'+','.join(missing))
            for key in ['fresh_follow_up_anchor_class','fresh_follow_up_anchor','incremental_fact','changed_judgment']:
                if not rel.get(key):problem.append('MISSING_FOLLOWUP_ANCHOR:'+key)
            if not predecessors:problem.append('FOLLOWUP_NO_DIRECT_PREDECESSOR')
        elif typ=='new_unrelated_event':
            if rel.get('related_ids'):problem.append('UNRELATED_HAS_TARGETS')
        else:problem.append('NON_ADDABLE_RELATION_TYPE:'+str(typ))
        if not candidate.get('event_fingerprint'):problem.append('MISSING_FINGERPRINT')
        if candidate.get('state')!='accepted_fact_safe':problem.append('NOT_ACCEPTED_FACT_SAFE')
        # Full database has no approved production ID for these new candidates.
        if candidate.get('production_id_assigned') is True:problem.append('UNAUTHORIZED_PRODUCTION_ID')

        row=dict(candidate)
        row['addability_outcome']={
            'distinct_follow_up':'addable_merge_safe_distinct_follow_up',
            'new_unrelated_event':'addable_merge_safe_new_unrelated',
            'program_lineage':'addable_merge_safe_program_lineage',
        }.get(typ,'review_pool_deferred_related_uncertain')
        row['baseline_revalidation']={
           'current_full_card_count':1676,'current_full_blob':EXPECTED_FULL,'source_spec_id':spec,
           'canonical_url_matches':sorted(matches),'source_story_id_matches':sorted(ids),'exact_title_matches':sorted(same_title),
           'current_batch_url_matches':sorted(self_batch_url_matches),'current_batch_title_matches':sorted(self_batch_title_matches),
           'direct_relation_targets':rel.get('related_ids',[]),'candidate_title':candidate.get('title'),
           'outcome':'PASS_EXACT_BASELINE_BOUNDED' if not problem else 'HOLD_COLLISION_OR_LINEAGE',
           'review_basis':'Actual locked Full bytes, exact/canonical URL+title+source-story collisions, exact predecessor existence, Stage C fingerprint and prior identity adjudication. Not an exhaustive fuzzy semantic corpus search.'
        }
        if problem:
            held.append({'source_spec_id':spec,'candidate':row,'reason':problem,'disposition':'review_pool_deferred_related_uncertain'})
        else:accepted.append(row)
        for u in candurls:seen_urls.setdefault(u,set()).add(spec)
        seen_titles.setdefault(title,set()).add(spec)
        item_receipts.append({'source_spec_id':spec,'baseline_collision_count':len(matches),'current_batch_collision_count':len(self_batch_url_matches),'problem_count':len(problem),'problems':problem})
    complete=(len(accepted)+len(held)==7)
    result={
        'schema':'STAGE_0_4_V4_BASELINE_REVALIDATION_AUDIT',
        'stage':'0.4','status':'PASS' if complete and len(held)==0 else 'BLOCKED_ADDABILITY_PENDING_RESOLUTION',
        'base_main_commit_sha':EXPECTED_MAIN,'base_full_blob_sha':EXPECTED_FULL,
        'lineage_guard':'PASS' if complete and not held else 'HOLD',
        'input_stage_c_artifact':'STAGE_C_LATEST_ACCEPTED_NATIVE_SCHEMA_V2_20261027.json',
        'input_stage_c_native_run':'https://github.com/ihyowoen/SBTL_HUB/actions/runs/40448333376',
        'input_stage_c_accepted_count':7,'checked_canonical_full_count':len(cards),
        'candidate_accounted':len(accepted)+len(held),'addable_merge_safe':accepted,
        'review_pool_deferred_related_uncertain':held,
        'other_dispositions':[],'addability_item_receipts':item_receipts,
        'zero_publish_ready':True,'zero_canonical_writes':True,'no_github_main_full_lean_related_production_mutations':True,
        'limitations':['Same event can reuse a URL, and different events can share topic; semantic identities inherit Stage B/C manual event fingerprint adjudication.','0.4 addability does not authorize publication/merge.','Current accepted 7 are only a subset of Stage A 1330 source observations; LGES remains Stage B blocked.'],
    }
    OUTPUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('CURRENT_MAIN_PINNED',EXPECTED_MAIN)
    print('CURRENT_FULL_SHA',blob_sha,'CARDS',len(cards))
    print('0.4 accounted',len(accepted)+len(held),'ADDABLE',len(accepted),'HELD',len(held))
    for z in item_receipts:print('ITEM',z['source_spec_id'],'CLASHES',z['problem_count'],z['problems'])
    print('OUTPUT',str(OUTPUT),'BYTES',OUTPUT.stat().st_size)
    if not complete or held:
        return 1
    return 0
if __name__=='__main__':sys.exit(main())
