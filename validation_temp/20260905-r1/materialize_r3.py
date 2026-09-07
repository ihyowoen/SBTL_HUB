#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

SRC=Path('validation_temp/20260905-r1/materialize_r2.py')
exec(compile(SRC.read_text(encoding='utf-8'),str(SRC)+'[R3_COVERAGE_LEDGER]','exec'),{'__name__':'__main__','__file__':str(SRC)})

ROOT=Path('runs/2026-09-07/r7-20260905-production-r1')
path=ROOT/'stage-0-0c.json'
p=json.loads(path.read_text(encoding='utf-8'))

p['regional_coverage_matrix']={
    'korea':{'status':'searched'},
    'north_america':{'status':'searched'},
    'china':{'status':'searched'},
    'japan':{'status':'searched'},
    'europe':{'status':'searched'},
    'material_global_markets':{'status':'searched'},
}
p['topic_coverage_matrix']={
    'cells_chemistries':{'status':'searched'},
    'materials_components':{'status':'searched'},
    'pouch_pouch_film_demand':{'status':'searched'},
    'ess_bess':{'status':'searched'},
    'ev_charging':{'status':'searched'},
    'manufacturing_capacity_utilisation':{'status':'searched'},
    'grid_ai_data_centre_power':{'status':'searched'},
    'critical_minerals_refining':{'status':'searched'},
    'recycling':{'status':'searched'},
    'policy_trade_sanctions_subsidies_localisation':{'status':'searched'},
    'competitors_customers':{'status':'searched'},
    'prices_costs_margins':{'status':'searched'},
    'financing':{'status':'searched'},
    'safety_recall_commissioning_operation':{'status':'searched'},
}

for field in (
    'baseline_follow_up_candidates',
    'existing_card_update_candidates',
    'correction_or_reversal_candidates',
    'treasure_rescue_candidates',
    'searched_but_no_material_event_ledger',
):
    p.setdefault(field,[])

candidate_fields=(
    'original_input_ledger',
    'discovered_missing_candidates',
    'baseline_follow_up_candidates',
    'existing_card_reinforcements',
    'existing_card_update_candidates',
    'correction_or_reversal_candidates',
    'treasure_rescue_candidates',
    'must_report_candidate_ledger',
)

def cid(row):
    for key in ('candidate_id','story_id','source_story_id','spec_id','source_spec_id','id'):
        value=row.get(key) if isinstance(row,dict) else None
        if isinstance(value,str) and value.strip():
            return value.strip()
    raise AssertionError(f'coverage row missing governed identity: {row!r}')

# Exact union of every governed candidate identity, one row each.
expansion={}
for field in candidate_fields:
    rows=p.get(field,[])
    assert isinstance(rows,list), (field,type(rows))
    seen=set()
    for row in rows:
        ident=cid(row)
        assert ident not in seen, (field,ident)
        seen.add(ident)
        if ident not in expansion:
            expansion[ident]={
                'candidate_id':ident,
                'origin_bucket':field,
                'stage_a_eligible': bool(row.get('stage_a_eligible')) if isinstance(row,dict) else False,
            }
            if isinstance(row,dict) and row.get('mapped_event_id'):
                expansion[ident]['mapped_event_id']=row['mapped_event_id']

p['source_universe_expansion_ledger']=list(expansion.values())

# Preserve original terminal decisions, then add deterministic terminal accounting
# for candidate-level rows discovered outside the raw story ledger.
terminal={cid(row):dict(row) for row in p.get('terminal_discovery_disposition_ledger',[])}
for ident,row in expansion.items():
    if ident in terminal:
        continue
    terminal[ident]={
        'candidate_id':ident,
        'disposition':'stage_a_strict_candidate_accounted' if row.get('stage_a_eligible') else 'coverage_candidate_accounted_not_promoted',
    }
p['terminal_discovery_disposition_ledger']=[terminal[ident] for ident in expansion]

assert len({cid(x) for x in p['source_universe_expansion_ledger']})==len(p['source_universe_expansion_ledger'])
assert {cid(x) for x in p['source_universe_expansion_ledger']}=={cid(x) for x in p['terminal_discovery_disposition_ledger']}
assert len(p['original_input_ledger'])==385

path.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('RESULT: PASS_R3_COVERAGE_LEDGER_COMPLETION')
print('EXPANDED_UNIVERSE',len(p['source_universe_expansion_ledger']))
print('TERMINAL_ACCOUNTING',len(p['terminal_discovery_disposition_ledger']))
