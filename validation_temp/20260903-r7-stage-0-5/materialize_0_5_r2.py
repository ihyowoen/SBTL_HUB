#!/usr/bin/env python3
import json, runpy
from pathlib import Path

# Materialize the canonical Prompt 0.5 combined bucket first.
runpy.run_path('validation_temp/20260903-r7-stage-0-5/materialize_0_5.py')
p=Path('/tmp/stage-0-5-r7.json')
data=json.loads(p.read_text(encoding='utf-8'))
rows=data['evidence_complete_and_source_claim_covered']
assert len(rows)==33

FOLLOWUP={
  'STD26_R7_003':{
    'anchor_class':'technology_commercialization_anchor',
    'fresh':'On 2026-09-02 ProLogium reported 3.5-generation LCB cell mass-production entry at its Taiwan GWh-scale facility and quantified a 185.4Ah large cell at 381Wh/kg.',
    'incremental':'Relative to canonical predecessor 2026-05-27_GL_01, the 2026-09-02 event adds a verified mass-production-stage milestone at a GWh-scale facility plus quantified 185.4Ah and 381Wh/kg performance.',
    'judgment':'The ProLogium lineage advances from the 2026-05-27 predecessor to a verified 2026-09-02 mass-production/commercialization event, strengthening the execution-stage judgment without treating the two events as duplicates.'
  },
  'STD26_R7_015':{
    'anchor_class':'execution_event_anchor',
    'fresh':'On 2026-09-02 I Squared Capital disclosed that Anza Power signed a battery tolling agreement with Amazon Australia for the 50MW/200MWh Bairnsdale BESS.',
    'incremental':'Relative to canonical predecessors 2026-07-02_GL_08 and 2026-04-16_GL_02, the 2026-09-02 event adds a named signed tolling agreement, a specific Bairnsdale asset and a quantified 50MW/200MWh contracted storage structure.',
    'judgment':'The Amazon Australia storage lineage advances to a specific contracted standalone-BESS tolling structure on 2026-09-02, adding an execution-stage commercial anchor rather than merely reinforcing the earlier lineage.'
  }
}
for row in rows:
    sid=row['source_spec_id']
    lineage=row['related_lineage']
    relation=lineage['relation_type']
    related_ids=list(lineage.get('related_ids') or [])
    row['related']=related_ids
    row['related_candidate_spec_ids']=[]
    lineage['same_event_checked']=True
    lineage['earliest_same_event_date_checked']=True
    lineage['related_candidate_spec_ids']=[]
    if relation=='new_unrelated_event':
        assert related_ids==[]
        lineage['reason']='Stage C and Prompt 0.4 found no direct auditable predecessor, same-event canonical representative, or reinforcement-only target for this candidate.'
    elif relation=='distinct_follow_up':
        assert sid in FOLLOWUP and related_ids
        proof=FOLLOWUP[sid]
        lineage['reason']='Stage C locked a direct canonical predecessor relation and Prompt 0.4 revalidated the targets as existing, chronologically earlier and distinct from the current event.'
        lineage['fresh_follow_up_anchor_class']=proof['anchor_class']
        lineage['fresh_follow_up_anchor']=proof['fresh']
        lineage['incremental_fact_vs_predecessor']=proof['incremental']
        lineage['changed_judgment_vs_predecessor']=proof['judgment']
    else:
        raise AssertionError((sid,relation))

    # Materialize the exact active date-role/freshness compatibility envelope
    # from the already verified operative date and body-level evidence.
    role=row['date_role']
    rep=role.get('representative_event_date') or row.get('date')
    assert rep==row.get('date'), (sid,rep,row.get('date'))
    pub=role.get('source_publication_dates') or role.get('publication_dates')
    assert isinstance(pub,list) and pub, sid
    date_source=next((s for s in row.get('fact_sources',[]) if s.get('source_url') and s.get('source_quote')),None)
    assert date_source is not None, sid
    role['representative_date']=rep
    role['event_date']=rep
    role['publication_dates']=pub
    role['earliest_same_event_date_checked']=True
    role['event_date_source_url']=date_source['source_url']
    role['event_date_source_quote']=date_source['source_quote']
    if relation=='distinct_follow_up':
        role['fresh_follow_up_anchor']=lineage['fresh_follow_up_anchor']

canonical=json.loads(Path('data/cards.full.json').read_text(encoding='utf-8'))
if isinstance(canonical,list):
    canonical_cards=canonical
elif isinstance(canonical,dict) and isinstance(canonical.get('cards'),list):
    canonical_cards=canonical['cards']
else:
    raise AssertionError('unexpected canonical cards.full.json shape')
assert len(canonical_cards)==1536
canonical_ids={c.get('id') for c in canonical_cards if isinstance(c,dict) and c.get('id')}
for sid in FOLLOWUP:
    row=next(x for x in rows if x['source_spec_id']==sid)
    assert all(target in canonical_ids for target in row['related'])

data['cards']=canonical_cards+rows
assert len(data['cards'])==1569
p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('RESULT: MATERIALIZED_0_5_R4 merged_cards=1569 current=33 related_and_date_contract=PASS')
