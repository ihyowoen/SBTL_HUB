#!/usr/bin/env python3
from pathlib import Path

OLD_SHA='a810e964e298a627b7edc65d28805b03f29a371a016b0aece5053f4589c87407'
NEW_SHA='a1957c8cac140083029bbcff41e96980c740a03ab8d47bfefae55a8e91fc240c'
OLD_COUNT="'related_add':3"
NEW_COUNT="'related_add':4"
OLD_PRINT='related_add=3'
NEW_PRINT='related_add=4'
p=Path('../builder/validation_temp/20260903-r7-0-8/materialize_production_0_8.py')
if not p.exists():
    p=Path('validation_temp/20260903-r7-0-8/materialize_production_0_8.py')
s=p.read_text(encoding='utf-8')
assert s.count(OLD_SHA)==1,s.count(OLD_SHA)
assert s.count(OLD_COUNT)==3,s.count(OLD_COUNT)
assert s.count(OLD_PRINT)==1,s.count(OLD_PRINT)
s=s.replace(OLD_SHA,NEW_SHA).replace(OLD_COUNT,NEW_COUNT).replace(OLD_PRINT,NEW_PRINT)
exec(compile(s,str(p)+'[R5_CODEX_REVIEW_SHA_AND_COUNT_BINDING]','exec'),{'__name__':'__main__','__file__':str(p)})
