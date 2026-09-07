#!/usr/bin/env python3
from pathlib import Path

OLD='a810e964e298a627b7edc65d28805b03f29a371a016b0aece5053f4589c87407'
NEW='6310d929353a63429969a30985e00ffb01f43859d3f57d9e73405f060a02ccb6'
p=Path('../builder/validation_temp/20260903-r7-0-8/materialize_production_0_8.py')
if not p.exists():
    p=Path('validation_temp/20260903-r7-0-8/materialize_production_0_8.py')
s=p.read_text(encoding='utf-8')
assert s.count(OLD)==1,s.count(OLD)
s=s.replace(OLD,NEW)
exec(compile(s,str(p)+'[R3_SHA_BINDING]','exec'),{'__name__':'__main__','__file__':str(p)})
