#!/usr/bin/env python3
from pathlib import Path

OLD='a810e964e298a627b7edc65d28805b03f29a371a016b0aece5053f4589c87407'
NEW='203f788ac48796fe9e790a70a30afa7bfcc8dd7143e56011548f00150d2e80a7'
p=Path('../builder/validation_temp/20260903-r7-0-8/materialize_production_0_8.py')
if not p.exists():
    p=Path('validation_temp/20260903-r7-0-8/materialize_production_0_8.py')
s=p.read_text(encoding='utf-8')
assert s.count(OLD)==1,s.count(OLD)
s=s.replace(OLD,NEW)
exec(compile(s,str(p)+'[R4_FULL_SCHEMA_SHA_BINDING]','exec'),{'__name__':'__main__','__file__':str(p)})
