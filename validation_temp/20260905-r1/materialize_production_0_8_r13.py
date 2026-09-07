#!/usr/bin/env python3
from pathlib import Path
import json

base=Path(__file__).resolve().with_name('materialize_production_0_8.py')
src=base.read_text(encoding='utf-8')
repls={
    "OPS_SHA='7899d373343332dac7b4e9e7000edc439a9c2b28ff5990f3d0d7088efbe1cd3e'":"OPS_SHA='6c2ac63e2711adc7247d7dcf9cfbd685be971e11c6ae7790cedbb11d5157c2dd'",
    "'stage_b':'33dcc9600bc5ef60478f4bd8f22c129d22bbf83508676707cbb7b6e6be6583cd'":"'stage_b':'e4b5bffda22ed7bbaaa807b37b6038c61cec512d765ea036a2cb124f47a6a998'",
    "'stage_c':'ce699c68e81af7b29a73e350fc710d66328e42c96951291262db377f09e4ecda'":"'stage_c':'e5ddc8380ee0881830854248a7ff4377021854d76ff3a1f839c4a99f65f4cd77'",
    "'stage_0_4':'c6dd3d2b5493360daf16a0d1b1a55593dbcc163f1be6bba027f7296906289972'":"'stage_0_4':'5ca34fa2b130f7ae0bb84ff0e9abc2af03650f5fc86e4bf8ad0cbc3b6a026f22'",
    "'stage_0_5':'ab5b6033dc105a014ae9616e5f90098b197cd741c8889eeef06197d960436da9'":"'stage_0_5':'480d678454370d982e314786bc154cf83860d01106ed05e06e66a3a109837805'",
    "'stage_0_6':'132e169d4685ad475e98c632e9b9624bc74e7612df2f26fbe3daf04b54c7c06f'":"'stage_0_6':'a4ad98a341e95f176ce4af45f00da2f877d615f0df38ca15b6bbd712b7167188'",
    "'stage_0_7':'ca69e3952e0a617c312d951cdcb8a96244b5ab4188670c0eececbdbe0df0dd08'":"'stage_0_7':'30c6739cf8fbb7b84d15d4f7cca7e5e3d3534383abf9236171808e4dc4474e01'",
    'CERTIFIED_WORKFLOW_RUN_ID=34129245202':'CERTIFIED_WORKFLOW_RUN_ID=34132857088',
    'CERTIFIED_ARTIFACT_ID=10021379057':'CERTIFIED_ARTIFACT_ID=10022790859',
    "CERTIFIED_ARTIFACT_SHA='5fe2a7ba0bec2a99d09a2456d6568cad5d769fe0b8cdcc4ffc31b086c2d8deb8'":"CERTIFIED_ARTIFACT_SHA='68ee36ec131af4e4e0b7ab7f269d80c1608ab581e2b5cb1f6df22fad9c04b073'",
    "'independent_0_7c_r11_verified_source_discovery_ledger'":"'independent_0_7c_r13_nested_round6_reconciled'",
}
for old,new in repls.items():
    assert old in src, old
    src=src.replace(old,new)
exec(compile(src, str(base)+'[R13_EXACT]', 'exec'), {'__name__':'__main__','__file__':str(base)})

# R13-specific fail-closed delivered-artifact invariant.
qpath=Path('runs/2026-09-07/r7-20260905-production-r1/stage-0-7c.json')
q=json.loads(qpath.read_text(encoding='utf-8'))
top=q['round_6_operation_binding']
nested=q['six_round_review']['round_6_operation_binding']
assert top==nested
assert top['reviewed_operations_sha256']=='6c2ac63e2711adc7247d7dcf9cfbd685be971e11c6ae7790cedbb11d5157c2dd'
assert top['stage_hashes']==q['hash_chain']
assert top['binding_authority']=='independent_0_7c_r13_nested_round6_reconciled'
print('RESULT: PASS_R13_PRODUCTION_NESTED_ROUND6_BINDING')
