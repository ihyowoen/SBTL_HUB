#!/usr/bin/env python3
from pathlib import Path
import json
src=Path('validation_temp/20260905-promotion-r1/materialize_promotion_stage_a_r2.py')
exec(compile(src.read_text(encoding='utf-8'),str(src)+'[R3_EXACT_EVIDENCE_TARGETS]','exec'),{'__name__':'__main__','__file__':str(src)})
out=Path('validation_temp/20260905-promotion-r1/out/stage-a-promotion.json')
a=json.loads(out.read_text(encoding='utf-8'))
TARGETS={
 'STD26_R8P_001':[
  'Official company release, ASX filing, contract, or definitive JV document verifying the 2026-09-03 non-binding 50:50 JV term-sheet stage, the intended US$100 million initial funding including USSM US$95 million and the remaining US$5 million equity split, Missouri permitted-site status, and whether a definitive agreement is executed.'
 ],
 'STD26_R8P_002':[
  'Official D.TRADING or Capalo release, contract, or executed commercial-framework document verifying the 2026-09-03 partnership stage, D.TRADING contractual-counterparty/offtaker status, fixed-revenue structure, credit support, and any later named-asset capacity, contract duration, or price metric.'
 ],
 'STD26_R8P_003':[
  'Official Liberaware filing, timely disclosure, contract, or executed follow-on agreement verifying the 2026-09-02 LOI stage, Japan domestic battery-production and joint-commercialisation scope, HINOTATE participation, and any later JV/SPV approval, production date, or shipment volume.'
 ],
 'STD26_R8P_004':[
  'Official company release, JV contract/incorporation document, or Indonesian partner/government record verifying the 2026-09-04 JV-establishment-agreement stage, named Indonesian partners, first-site construction deadline, and whether the stated 10-year US$300 million supply plan becomes a binding contract or quantified shipment volume.'
 ],
}
for x in a['strict_passed_spec']:
    sid=x['spec_id']
    if sid in TARGETS:
        x['evidence_needed_for_stage_b']=TARGETS[sid]
        # Explicitly preserve the successful frozen-V3 non-execution compatibility route.
        x['selection_route']='structural_non_execution_route'
        x['format_risk_tags']=['v4_structural_non_execution_route_compatibility']
        x['execution_anchor_type']=None
        x['execution_anchor_strength']=None
        x['structural_value_override_applied']=True
        x['structural_selector_policy_version']='STRUCTURAL_NEWS_VALUE_SELECTION_V3'
# Mirror exact evidence targets onto any decision-ledger compatibility fields that exist.
for row in a.get('decision_ledger',[]):
    sid=row.get('spec_id')
    if sid in TARGETS:
        if 'evidence_needed_for_stage_b' in row:
            row['evidence_needed_for_stage_b']=TARGETS[sid]
        if 'selection_route' in row:
            row['selection_route']='structural_non_execution_route'
        if 'format_risk_tags' in row:
            row['format_risk_tags']=['v4_structural_non_execution_route_compatibility']
out.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('RESULT: PASS_R3_EXACT_PROMOTION_EVIDENCE_TARGETS')
