#!/usr/bin/env python3
from pathlib import Path

OLD='a810e964e298a627b7edc65d28805b03f29a371a016b0aece5053f4589c87407'
NEW='80b214b597b36dc3c6821a61328d219efc694350b2c0a8e68f2df4ce5e955415'
p=Path('../builder/validation_temp/20260903-r7-0-8/materialize_production_0_8.py')
if not p.exists():
    p=Path('validation_temp/20260903-r7-0-8/materialize_production_0_8.py')
s=p.read_text(encoding='utf-8')
assert s.count(OLD)==1, s.count(OLD)
s=s.replace(OLD,NEW)
exec(compile(s,str(p)+'[R2_SHA_BINDING]','exec'),{'__name__':'__main__','__file__':str(p)})
