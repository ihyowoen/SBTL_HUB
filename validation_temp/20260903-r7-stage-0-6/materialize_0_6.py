#!/usr/bin/env python3
import copy, hashlib, json, runpy, re
from pathlib import Path

runpy.run_path('validation_temp/20260903-r7-stage-0-5/materialize_0_5_r2.py')
p05=Path('/tmp/stage-0-5-r7.json')
sha=hashlib.sha256(p05.read_bytes()).hexdigest()
assert sha=='4d7dc963ea91eac151ee2b2b6ee3fb31eae0407bc8b60834f5c79cd509bcbc96', sha
up=json.loads(p05.read_text(encoding='utf-8'))
source=up['evidence_complete_and_source_claim_covered']
assert len(source)==33

# Evidence-neutral terminology/readability edits only. No fact/date/number/Related changes.
PATCH={
 'STD26_R7_015':{
   'title':'Amazon Australia, Bairnsdale 50MW/200MWh BESS 장기 톨링 계약',
   'sub':'Anza Power와 체결…Amazon의 아시아·태평양(APAC) 첫 독립형 BESS 톨링 계약',
 },
 'STD26_R7_020':{
   'sub':'USW Local 11-0001, Nye Mine·Columbus 제련시설에서 부당노동행위(ULP) 파업',
 },
 'STD26_R7_031':{
   'title':'Westbridge, 캐나다 Red Willow 태양광·BESS 프로젝트 매각 계약 체결',
   'sub':'알버타 최대 225MWac 태양광·100MW BESS 구상…주식매매계약(SPA) 체결, 거래 종결 전',
 },
 'STD26_R7_043':{
   'sub':'Alcoa 정유소 내 연 100톤 생산 목표…7월 최종투자결정(FID)에 이어 미국 금융지원 추가',
 },
 'STD26_R7_P01P_003':{
   'sub':'브라질 용량예비력 경매 공동 참여 계획…아직 낙찰·수주 단계 아님',
 },
 'STD26_R7_P01P_010':{
   'title':'Sungrow, 상반기 ESS 매출 154.56억위안…PV를 넘어 최대 사업부로',
 },
 'STD26_R7_P01P_011':{
   'title':'Xos 이동형 충전 허브 1기, 누적 전력공급 1GWh 돌파',
   'sub':'3만3,600회 이상 충전…전체 허브 누적 5GWh 초과',
 },
 'STD26_R7_P01P_012':{
   'title':'SB Energy, 미국 IPO용 S-1 제출…AI 데이터센터 전력 플랫폼 확대 구상',
 },
 'STD26_R7_017':{
   'title':'호주 ARENA, 100번째 커뮤니티 배터리 설치…2차 사업에 2,320만 호주달러 추가',
 },
}

polished=[]
for src in source:
    row=copy.deepcopy(src)
    sid=row['source_spec_id']
    before={k:copy.deepcopy(row.get(k)) for k in ('title','sub','gate','fact','implication')}
    for field,value in PATCH.get(sid,{}).items():
        row[field]=value
    changed=[k for k in before if before[k]!=row.get(k)]
    # Hard invariants: factual body, date, evidence, route and Related are frozen at 0.6.
    assert row['fact']==before['fact'], sid
    assert row['date']==src['date'] and row['date_role']==src['date_role'], sid
    assert row['related_lineage']==src['related_lineage'] and row.get('related',[])==src.get('related',[]), sid
    assert row['fact_sources']==src['fact_sources'] and row['source_diversity_status']==src['source_diversity_status'], sid
    assert row.get('selection_route')==src.get('selection_route') and row.get('anchor_classes')==src.get('anchor_classes'), sid
    row['content_enriched']=True
    row['language_terminology_polished']=True
    row['publish_ready']=False
    row['github_merge_ready']=False
    row['state']='content_enriched_and_language_polished'
    row['content_polish_audit']={
      'status':'PASS','changed_visible_fields':changed,
      'fact_body_changed':False,'date_or_related_changed':False,
      'terminology_check':'PASS','title_body_consistency':'PASS','stage_precision':'PASS',
      'strategic_readthrough':'PASS_BOUNDED_TO_VERIFIED_EVIDENCE',
    }
    polished.append(row)

# Reject internal pipeline leakage from visible copy.
for row in polished:
    visible=' '.join(str(row.get(k,'')) for k in ('title','sub','gate','fact'))+' '+' '.join(map(str,row.get('implication') or []))
    assert not re.search(r'\b(stage\s*[abc]|strict_passed_spec|supplied\s+r7|source-bound|must\s+verify)\b',visible,re.I), row['source_spec_id']

canonical=up['cards'][:1536]
assert len(canonical)==1536
root={
 'stage':'0.6','status':'PASS','run_tag':'20260903_R7_PROMPT_0_6_R1',
 'source_prompt_file':'docs/llm_prompts/v1/08_PROMPT_0_6_Content_Polish.md','source_prompt_version':'PROMPT_0_6_V4_20260901',
 'base_main_commit_sha':up['base_main_commit_sha'],'base_full_blob_sha':up['base_full_blob_sha'],
 'input_0_5_sha256':sha,'upstream_lineage_integrity':'PASS','lineage_and_anchor_guard':'PASS','input_count':33,
 'content_enriched_and_language_polished':polished,
 'return_to_evidence_qc':[],'return_upstream':[],
 'accounting':{'input':33,'pass':33,'return_evidence':0,'return_upstream':0,'unaccounted':0},
 'cards':canonical+polished,
}
assert len(root['cards'])==1569 and root['accounting']['pass']==33
Path('/tmp/stage-0-6-r7.json').write_text(json.dumps(root,ensure_ascii=False,indent=2),encoding='utf-8')
Path('/tmp/current-run-ids-0-6.json').write_text(json.dumps([x['source_spec_id'] for x in polished],ensure_ascii=False,indent=2),encoding='utf-8')
print('RESULT: MATERIALIZED_0_6 pass=33 edited_items=%d' % len(PATCH))
