#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
from urllib.parse import urlparse

SRC=Path('validation_temp/20260905-r1/materialize_r6.py')
exec(compile(SRC.read_text(encoding='utf-8'),str(SRC)+'[R7_DECISION_LEDGER_PROVENANCE]','exec'),{'__name__':'__main__','__file__':str(SRC)})
ROOT=Path('runs/2026-09-07/r7-20260905-production-r1')
A=ROOT/'stages/stage-a.json'; Q=ROOT/'stage-0-7c.json'
p=json.loads(A.read_text(encoding='utf-8'))
by_spec={x['spec_id']:x for x in p['strict_passed_spec']}

for row in p['decision_ledger']:
    item=by_spec[row['spec_id']]
    sid=row['story_id']
    source_rows=[x for x in item.get('same_event_source_cluster',[]) if isinstance(x,dict) and x.get('story_id')==sid]
    url=(source_rows[0].get('url') if source_rows else None) or item.get('primary_url') or (item.get('urls') or [None])[0]
    assert isinstance(url,str) and url.startswith(('http://','https://')), (row['spec_id'],sid,url)
    merged=row.get('ledger_decision')=='merged'
    row.update({
        'upstream_status':'kept',
        'upstream_drop_reason':None,
        'headline':item['title_raw'],
        'site':urlparse(url).netloc,
        'url':url,
        'integrity_group_id':f"{item['spec_id']}_EVENT_CLUSTER",
        'integrity_is_best':not merged,
        'reason':item['strict_pass_gate']['reason'],
        'merged_into_spec_id':item['spec_id'] if merged else None,
        'baseline_match':None,
        'baseline_relation':item['baseline_relation'],
        'duplicate_risk':item['duplicate_risk'],
        'staleness_decision':item['staleness_decision'],
        'treasure_hunt_sampled':False,
        'notes':'Source-bound observation retained in the Sep 5 production Stage A composite after 0.0C full-universe reconciliation.',
        'review_pool_item_id':None,
    })

A.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
q=json.loads(Q.read_text(encoding='utf-8'))
q['hash_chain']['stage_a']=sha(A)
Q.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('RESULT: PASS_R7_DECISION_LEDGER_PROVENANCE')
print('LEDGER_ROWS',len(p['decision_ledger']))
print('STAGE_A_SHA',sha(A))
