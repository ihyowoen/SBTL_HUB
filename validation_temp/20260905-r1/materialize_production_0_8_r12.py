#!/usr/bin/env python3
from pathlib import Path

base=Path(__file__).resolve().with_name('materialize_production_0_8.py')
src=base.read_text(encoding='utf-8')
repls={
    'CERTIFIED_WORKFLOW_RUN_ID=34129245202':'CERTIFIED_WORKFLOW_RUN_ID=34130243312',
    'CERTIFIED_ARTIFACT_ID=10021379057':'CERTIFIED_ARTIFACT_ID=10021773658',
    "CERTIFIED_ARTIFACT_SHA='5fe2a7ba0bec2a99d09a2456d6568cad5d769fe0b8cdcc4ffc31b086c2d8deb8'":"CERTIFIED_ARTIFACT_SHA='a8a08eabb56eb8715a6800dafee4a1f37fe1a3a39bd74d11517cf1747e7351ee'",
}
for old,new in repls.items():
    assert old in src, old
    src=src.replace(old,new)
exec(compile(src, str(base)+'[R12]', 'exec'), {'__name__':'__main__','__file__':str(base)})
