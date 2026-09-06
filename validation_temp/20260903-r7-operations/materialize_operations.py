#!/usr/bin/env python3
import copy, hashlib, json, re, runpy
from collections import defaultdict
from pathlib import Path

RUN_ID='card-run-2026-09-06-r7-20260903-production-r1'
RUN_ROOT='runs/2026-09-06/r7-20260903-production-r1'
STAGE_REFS=[f'{RUN_ROOT}/stages/stage-a.json',f'{RUN_ROOT}/stages/stage-b.json',f'{RUN_ROOT}/stages/stage-c.json',f'{RUN_ROOT}/stages/stage-0-4.json',f'{RUN_ROOT}/stages/stage-0-5.json',f'{RUN_ROOT}/stages/stage-0-6.json',f'{RUN_ROOT}/stages/stage-0-7.json']

runpy.run_path('validation_temp/20260903-r7-stage-0-7/materialize_0_7.py')
runpy.run_path('validation_temp/20260903-r7-stage-b-0-2r/materialize_0_2r_r2.py')
p07=Path('/tmp/stage-0-7-r7.json')
assert hashlib.sha256(p07.read_bytes()).hexdigest()=='bb3c708670ec68738bf60b761a822944c2be6f7740dcec8805b038a9d525e30e'
s07=json.loads(p07.read_text(encoding='utf-8'))
sb=json.loads(Path('/tmp/stage-b-0.2r-reestablished34.json').read_text(encoding='utf-8'))
score_by_spec={x['spec_id']:int(x.get('decision_news_value_score') or 0) for x in sb['strict_passed_spec']}
ready=s07['publish_ready']; assert len(ready)==33
canonical=json.loads(Path('data/cards.full.json').read_text(encoding='utf-8'))
assert isinstance(canonical,dict) and len(canonical['cards'])==1536
existing_ids={c['id'] for c in canonical['cards'] if isinstance(c,dict) and c.get('id')}
existing_specs={c.get('source_spec_id') for c in canonical['cards'] if isinstance(c,dict) and c.get('source_spec_id')}
assert not ({x['source_spec_id'] for x in ready}&existing_specs)

signal_rank={'top':0,'high':1,'mid':2,'low':3}
by_group=defaultdict(list)
for row in ready:
    by_group[(row['date'],row['region'])].append(row)

id_map={}
allocation=[]
for group in sorted(by_group):
    date,region=group
    used=set()
    pat=re.compile(rf'^{re.escape(date)}_{re.escape(region)}_(\d{{2}})$')
    for cid in existing_ids:
        m=pat.match(cid)
        if m: used.add(int(m.group(1)))
    rows=sorted(by_group[group],key=lambda r:(signal_rank.get(str(r.get('signal','mid')).lower(),9),-score_by_spec.get(r['source_spec_id'],0),r['source_spec_id']))
    nxt=1
    for row in rows:
        while nxt in used: nxt+=1
        assert nxt<=99
        cid=f'{date}_{region}_{nxt:02d}'
        assert cid not in existing_ids and cid not in id_map.values()
        id_map[row['source_spec_id']]=cid
        allocation.append({'source_spec_id':row['source_spec_id'],'id':cid,'date':date,'region':region,'signal':row.get('signal'),'news_value_score':score_by_spec.get(row['source_spec_id'],0)})
        used.add(nxt); nxt+=1
assert len(id_map)==33

# Canonical insert cards use the post-polish (0.6-equivalent) visible/state surface.
# Related edges are applied explicitly after insert, so insert cards start with the schema-governed neutral container.
insert=[]
for row07 in ready:
    card=copy.deepcopy(row07)
    sid=card['source_spec_id']; card['id']=id_map[sid]
    card['state']='content_enriched_and_language_polished'
    card['publish_ready']=False; card['github_merge_ready']=False
    card['related']=[]
    lineage=copy.deepcopy(card.get('related_lineage') or {})
    lineage.update({'status':'PASS','relation_type':'new_unrelated_event','related_ids':[],'reason':'Neutral insert container; any governed direct lineage is applied by declared related_add after insertion.'})
    # Remove follow-up-only fields from the neutral pre-related container.
    for k in ('fresh_follow_up_anchor_class','fresh_follow_up_anchor','incremental_fact_vs_predecessor','changed_judgment_vs_predecessor','event_stage_relationship','direction'):
        lineage.pop(k,None)
    card['related_lineage']=lineage
    evidence_refs=[]
    for src in card.get('fact_sources',[]):
        url=src.get('source_url') or src.get('url')
        if isinstance(url,str) and url and url not in evidence_refs: evidence_refs.append(url)
    assert evidence_refs
    insert.append({'card':card,'stage_artifacts':STAGE_REFS,'evidence_refs':evidence_refs})

REL={
 'STD26_R7_003':{
  'targets':['2026-05-27_GL_01'],
  'reason':'The Sep. 2 ProLogium mass-production milestone is a distinct follow-up to the May 27 canonical ProLogium predecessor, adding verified GWh-scale production entry and quantified 185.4Ah/381Wh/kg performance.',
  'stage':'predecessor_to_mass_production',
 },
 'STD26_R7_015':{
  'targets':['2026-07-02_GL_08','2026-04-16_GL_02'],
  'reason':'The Sep. 2 Anza Power–Amazon Australia 50MW/200MWh Bairnsdale tolling agreement is a distinct execution-stage follow-up to the earlier Amazon Australia storage lineage represented by the July 2 and April 16 canonical predecessors.',
  'stage':'prior_storage_lineage_to_signed_tolling_agreement',
 },
}
related_add=[]
ready_by_sid={r['source_spec_id']:r for r in ready}
for sid,cfg in REL.items():
    source_id=id_map[sid]
    evidence=[]
    for src in ready_by_sid[sid].get('fact_sources',[]):
        u=src.get('source_url') or src.get('url')
        if isinstance(u,str) and u and u not in evidence: evidence.append(u)
    for target in cfg['targets']:
        assert target in existing_ids
        op={'source_id':source_id,'target_id':target,'source_spec_id':sid,'identity_card_id':source_id,'relation_type':'distinct_follow_up','lineage_reason':cfg['reason'],'event_stage_relationship':cfg['stage'],'direction':'directional','stage_artifacts':STAGE_REFS,'evidence_refs':evidence,'patches':[]}
        op['patches']=[
          {'card_id':source_id,'op':'add','path':'/related/-','value':target},
          {'card_id':source_id,'op':'add','path':'/related_lineage/related_ids/-','value':target},
          {'card_id':source_id,'op':'replace','path':'/related_lineage/relation_type','value':'distinct_follow_up'},
          {'card_id':source_id,'op':'replace','path':'/related_lineage/reason','value':cfg['reason']},
          {'card_id':source_id,'op':'add','path':'/related_lineage/event_stage_relationship','value':cfg['stage']},
          {'card_id':source_id,'op':'add','path':'/related_lineage/direction','value':'directional'},
        ]
        related_add.append(op)

operations={'insert':insert,'update':[],'related_add':related_add}
assert len(insert)==33 and len(related_add)==3

def stable(v):
    if isinstance(v,list): return [stable(x) for x in v]
    if isinstance(v,dict): return {k:stable(v[k]) for k in sorted(v)}
    return v
ops_bytes=json.dumps(stable(operations),ensure_ascii=False,separators=(',',':')).encode('utf-8')
ops_sha=hashlib.sha256(ops_bytes).hexdigest()

run={
 'schema':'card_run_v1','run_id':RUN_ID,
 'base_main_commit_sha':'5317bec055b88a26cffb136e7844eb488ae4db0d','base_full_blob_sha':'8b3d96b5c1fd779567ef8512f7123fc4310093ec','expected_before':1536,
 'output_updated':'2026-09-06T17:30:00+09:00','operations':operations,'expected_after':1569,
 'audit_refs':[f'{RUN_ROOT}/card-run-audit.json',f'{RUN_ROOT}/stage-0-8.json'],
 'document_universe_manifest_ref':f'{RUN_ROOT}/stage-0-0d.json','coverage_discovery_ref':f'{RUN_ROOT}/stage-0-0c.json','independent_completeness_ref':f'{RUN_ROOT}/stage-0-7c.json',
 'notes':'R7 Sep.3 intake governed production run; operation set reviewed before canonical mutation.'
}
ledger={'schema':'prompt_0_8_current_run_id_ledger_v1','ids':[id_map[x['source_spec_id']] for x in ready],'operation_ids':[id_map[x['source_spec_id']] for x in ready]}
assert len(set(ledger['ids']))==33 and ledger['ids']==ledger['operation_ids']

Path('/tmp/r7-operations.json').write_text(json.dumps(operations,ensure_ascii=False,indent=2),encoding='utf-8')
Path('/tmp/r7-operations-sha.txt').write_text(ops_sha+'\n',encoding='utf-8')
Path('/tmp/r7-id-allocation.json').write_text(json.dumps({'run_id':RUN_ID,'count':33,'allocations':allocation,'id_map':id_map},ensure_ascii=False,indent=2),encoding='utf-8')
Path('/tmp/r7-card-run-draft.json').write_text(json.dumps(run,ensure_ascii=False,indent=2),encoding='utf-8')
Path('/tmp/r7-id-ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2),encoding='utf-8')
print('RESULT: OPERATIONS_DRY_RUN',{'insert':33,'update':0,'related_add':3,'expected_after':1569,'operations_sha256':ops_sha})
for row in allocation: print(row['id'],row['source_spec_id'],row['signal'],row['news_value_score'])
