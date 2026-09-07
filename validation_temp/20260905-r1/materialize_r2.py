#!/usr/bin/env python3
from pathlib import Path

SRC=Path('validation_temp/20260905-r1/materialize.py')
s=SRC.read_text(encoding='utf-8')
old_policy="'policy_stage':('effective_or_open_for_application' if c['sid']=='STD26_R8_009' else None)"
new_policy="'policy_stage':(4 if c['sid'] in ('STD26_R8_006','STD26_R8_009') else None)"
old_legal="'legal_policy_stage':('application_window_open' if c['sid']=='STD26_R8_009' else None)"
new_legal="'legal_policy_stage':('stage_4_implementation_budget_guidance_or_registry' if c['sid'] in ('STD26_R8_006','STD26_R8_009') else None)"
assert s.count(old_policy)==1, s.count(old_policy)
assert s.count(old_legal)==1, s.count(old_legal)
s=s.replace(old_policy,new_policy).replace(old_legal,new_legal)
exec(compile(s,str(SRC)+'[R2_POLICY_STAGE_CONTRACT]','exec'),{'__name__':'__main__','__file__':str(SRC)})
