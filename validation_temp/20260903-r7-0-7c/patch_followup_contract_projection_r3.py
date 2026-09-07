#!/usr/bin/env python3
import hashlib, json
from pathlib import Path

ROOT=Path('runs/2026-09-06/r7-20260903-production-r1')
RUN=ROOT/'card-run.json'
C=ROOT/'stage-0-7c.json'
S07=ROOT/'stages/stage-0-7.json'
SB=ROOT/'stages/stage-b.json'
EXPECTED_OLD='80b214b597b36dc3c6821a61328d219efc694350b2c0a8e68f2df4ce5e955415'
EXPECTED_NEW='203f788ac48796fe9e790a70a30afa7bfcc8dd7143e56011548f00150d2e80a7'
FOLLOW={'STD26_R7_003','STD26_R7_015'}
FIELDS=(
 'fresh_follow_up_anchor_class',
 'fresh_follow_up_anchor',
 'incremental_fact_vs_predecessor',
 'changed_judgment_vs_predecessor',
)
ALLOWED_CATS={
 'Battery','ESS','Materials','EV','Charging','Policy','Manufacturing','AI','Robotics','PowerGrid','SupplyChain','Other'
}
# Prompt 0.8 production-shape normalization under FUTURE_CARD_FULL_SCHEMA_V2_20260829.
# This mapping is explicit and operation-bound; no keyword inference occurs at runtime.
CAT_BY_SPEC={
 'STD26_R7_001':'PowerGrid',
 'STD26_R7_002':'ESS',
 'STD26_R7_003':'Battery',
 'STD26_R7_004':'Materials',
 'STD26_R7_005':'ESS',
 'STD26_R7_009':'PowerGrid',
 'STD26_R7_011':'Policy',
 'STD26_R7_015':'ESS',
 'STD26_R7_017':'ESS',
 'STD26_R7_018':'ESS',
 'STD26_R7_019':'ESS',
 'STD26_R7_020':'Materials',
 'STD26_R7_021':'Materials',
 'STD26_R7_022':'Policy',
 'STD26_R7_023':'Materials',
 'STD26_R7_027':'ESS',
 'STD26_R7_028':'Policy',
 'STD26_R7_031':'ESS',
 'STD26_R7_038':'ESS',
 'STD26_R7_040':'Manufacturing',
 'STD26_R7_043':'Materials',
 'STD26_R7_P01P_001':'PowerGrid',
 'STD26_R7_P01P_002':'Materials',
 'STD26_R7_P01P_003':'ESS',
 'STD26_R7_P01P_004':'ESS',
 'STD26_R7_P01P_005':'ESS',
 'STD26_R7_P01P_006':'ESS',
 'STD26_R7_P01P_008':'ESS',
 'STD26_R7_P01P_009':'Policy',
 'STD26_R7_P01P_010':'ESS',
 'STD26_R7_P01P_011':'Charging',
 'STD26_R7_P01P_012':'PowerGrid',
 'STD26_R7_P01P_013':'ESS',
}

def stable(v):
    if isinstance(v,list): return [stable(x) for x in v]
    if isinstance(v,dict): return {k:stable(v[k]) for k in sorted(v)}
    return v

def digest(ops):
    raw=json.dumps(stable(ops),ensure_ascii=False,separators=(',',':')).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()

run=json.loads(RUN.read_text(encoding='utf-8'))
c=json.loads(C.read_text(encoding='utf-8'))
s07=json.loads(S07.read_text(encoding='utf-8'))
sb=json.loads(SB.read_text(encoding='utf-8'))
assert digest(run['operations'])==EXPECTED_OLD
assert c['reviewed_operations_sha256']==EXPECTED_OLD
rows={x['source_spec_id']:x for x in s07['publish_ready']}
assert FOLLOW <= set(rows)
assert len(run['operations']['insert'])==33
assert set(CAT_BY_SPEC)=={x['card']['source_spec_id'] for x in run['operations']['insert']}
assert set(CAT_BY_SPEC.values()) <= ALLOWED_CATS

# Stage B carries the certified Stage A strict specs, including the selector sub-category.
# Stage C drafts dropped this field, so recover it from the governed upstream copy rather
# than inventing or inferring a replacement at production time.
specidx={(x.get('spec_id') or x.get('source_spec_id')):x for x in sb['strict_passed_spec']}
assert set(CAT_BY_SPEC) <= set(specidx)
subcat_by_spec={sid:specidx[sid].get('sub_cat') for sid in CAT_BY_SPEC}
assert all(isinstance(v,str) and v.strip() for v in subcat_by_spec.values())

projected=[]
taxonomy=[]
for ins in run['operations']['insert']:
    card=ins['card']; sid=card.get('source_spec_id')
    old_cat=card.get('cat'); old_sub=card.get('sub_cat')
    card['cat']=CAT_BY_SPEC[sid]
    card['sub_cat']=subcat_by_spec[sid]
    taxonomy.append({'source_spec_id':sid,'old_cat':old_cat,'new_cat':card['cat'],'old_sub_cat':old_sub,'new_sub_cat':card['sub_cat']})
    if sid not in FOLLOW: continue
    source_lineage=rows[sid]['related_lineage']
    lineage=card['related_lineage']
    assert lineage['relation_type']=='new_unrelated_event' and lineage['related_ids']==[]
    for field in FIELDS:
        value=source_lineage.get(field)
        assert isinstance(value,str) and value.strip(),(sid,field,value)
        assert field not in lineage,(sid,field)
        lineage[field]=value
        projected.append((sid,field))

assert len(projected)==8,projected
assert len(taxonomy)==33
assert all(x['new_cat'] in ALLOWED_CATS for x in taxonomy)
assert all(isinstance(x['new_sub_cat'],str) and x['new_sub_cat'].strip() for x in taxonomy)
assert digest(run['operations'])==EXPECTED_NEW
# No relation target is prelinked in the insert; only already-validated follow-up proof
# metadata is preserved so the post-apply distinct_follow_up contract can be evaluated.
for ins in run['operations']['insert']:
    card=ins['card']; sid=card.get('source_spec_id')
    assert card['cat']==CAT_BY_SPEC[sid]
    assert card['sub_cat']==subcat_by_spec[sid]
    if sid in FOLLOW:
        assert card['related']==[]
        assert card['related_lineage']['related_ids']==[]
        for field in FIELDS: assert card['related_lineage'][field]==rows[sid]['related_lineage'][field]

c['reviewed_operations_sha256']=EXPECTED_NEW
c['operation_freeze']['operations_sha256']=EXPECTED_NEW
c['production_schema_projection']={
 'status':'PASS',
 'schema_authority':'docs/FUTURE_CARD_STANDARD_FULL_SCHEMA.md',
 'schema_version':'FUTURE_CARD_FULL_SCHEMA_V2_20260829',
 'card_count':33,
 'sub_cat_projection':'restored_from_stage_b_certified_stage_a_strict_spec',
 'primary_cat_projection':'explicit_source_spec_id_mapping_no_runtime_inference',
 'allowed_primary_categories':sorted(ALLOWED_CATS),
 'taxonomy_rows':taxonomy,
}
RUN.write_text(json.dumps(run,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
C.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('RESULT: PATCHED_FOLLOWUP_AND_FULL_SCHEMA_PROJECTION_R4',{'followup_fields':projected,'taxonomy_cards':len(taxonomy),'operations_sha256':EXPECTED_NEW})
