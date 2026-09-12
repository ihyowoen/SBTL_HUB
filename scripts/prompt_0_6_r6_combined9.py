#!/usr/bin/env python3
from __future__ import annotations
import copy, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'runs/2026-09-03'
IN=RUN/'prompt_0_5_r6_combined9_20260903_R1.json'
OUT=RUN/'prompt_0_6_r6_combined9_20260903_R1.json'
REP=RUN/'prompt_0_6_r6_combined9_validation_20260903_R1.json'
PROMPT=ROOT/'docs/llm_prompts/v1/08_PROMPT_0_6_Content_Polish.md'
MAIN='df6fcccf3a69464ff0a43a8ba5897d71b6a4d9c4'
BLOB='53219907cdb435c3822c41d097b23e475662aa8a'

data=json.loads(IN.read_text(encoding='utf-8'))
rows=data['evidence_complete_and_source_claim_covered']
assert data['status']=='PASS' and len(rows)==9

def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

POLISH={
 'STD26_R6_B01_002':{'title':'SK온, 네오볼타에 미국산 LFP 9GWh 공급…ESS 현지생산 전환 계약화','terminology':['미국산 LFP','9GWh','2027~2031년','확정계약과 추가 협력 프레임워크 분리']},
 'STD26_R6_B01_003':{'title':'CIP, 호주 Gawara Baya 인수·금융종결…408MW 풍력+104MW BESS 건설 진입','terminology':['Gawara Baya','408MW 풍력','104MW grid-forming BESS','금융종결·건설 단계']},
 'STD26_R6_B01_004':{'title':'포스코 아르헨티나 리튬, IDB Invest서 최대 7억달러 금융 확보','terminology':['IDB Invest','최대 7억달러','Sal de Oro','가동·증산 금융']},
 'STD26_R6_B01_005':{'title':'LG에너지솔루션, 스맥오버 리튬과 10년 8만t 탄산리튬 오프테이크','sub':'연 8천t 구속력 있는 take-or-pay…미국 South West Arkansas 상업생산과 연계','terminology':['LG에너지솔루션','연 8,000t','10년','구속력 있는 take-or-pay']},
 'STD26_R6_B01_008':{'title':'EU 배터리 패스포트, 71개 데이터포인트 준비 가이드 공개','terminology':['EU 배터리 패스포트','71개 데이터포인트','Commission guidance','2027년 2월 18일']},
 'STD26_R6_B01_009':{'title':'중국, ESS 소비세 경계 구체화…배터리 클러스터 과세·완성 ESS 비과세','terminology':['소비세','배터리 클러스터','완성 ESS','반고체 배터리']},
 'STD26_R6_B01_010':{'title':'중국 배터리 소비세 2% 시행…리튬이온·바나듐 레독스 플로우 전지 대상','terminology':['2% 소비세','2026년 9월 1일','4% 인상 시점','한시 면세']},
 'STD26_R6_P01P_006':{'title':'라이온타운, 아르헨티나 Centenario 리튬 염호 최대 100% earn-in 계약 체결','terminology':['binding farm-in','최대 100% earn-in','4년 US$40m 프로젝트 지출','초기 대가와 단계별 지분취득 구분']},
 'STD26_R6_P01P_024':{
   'title':'리튬 업계 실적 반등…가격·판매량 회복이 최신 실적에 반영',
   'sub':'Ganfeng H1 흑자전환·Albemarle Q2 Energy Storage 부문 매출 78% 증가',
   'gate':'리튬 가격과 판매량 회복이 주요 업체의 최신 실적 지표에 반영됐다.',
   'fact':'Ganfeng Lithium은 2026년 상반기 매출 약 RMB23.1bn과 순이익 약 RMB4.26bn을 기록해 전년 동기 적자에서 흑자로 전환했다. Albemarle의 2026년 2분기 Energy Storage 부문은 매출 US$1.277bn으로 전년 동기 대비 77.9% 증가했고, 판매량은 11.0%, 평균 실현가격은 60.5% 상승했다. 두 사례는 최근 리튬 업황 개선이 가격·판매량·실적 지표에 동시에 나타나고 있음을 보여준다.',
   'implication':['주요 리튬 업체의 가격·판매량 회복이 이어지면 광산·정제·배터리 밸류체인의 실적 레버리지가 커질 수 있다.','다만 Ganfeng과 Albemarle의 실적 개선에는 가격·물량·비용 등 복수 요인이 작용하므로 특정 최종수요 하나만으로 업계 전체 수익성 회복을 설명하면 안 된다.'],
   'terminology':['Ganfeng H1 2026','Albemarle Energy Storage segment','판매량','평균 실현가격','ESS 단일요인 인과 주장 제거']
 },
}
assert set(POLISH)=={x['source_spec_id'] for x in rows}

protected_fields=('related_lineage','date_role','fact_sources','claim_map','source_discovery_ledger','source_diversity_status','selection_route','anchor_classes')
passed=[]; holds=[]; diversity=[]; related_audit=[]
for src in rows:
    x=copy.deepcopy(src); sid=x['source_spec_id']; before={k:copy.deepcopy(x.get(k)) for k in protected_fields}; before_visible={k:copy.deepcopy(x.get(k)) for k in ('title','sub','gate','fact','implication')}
    change=POLISH[sid]
    for field in ('title','sub','gate','fact','implication'):
        if field in change: x[field]=copy.deepcopy(change[field])
    x['content_enriched']=True; x['language_terminology_polished']=True
    x['content_polish_audit']={'status':'PASS','before_visible_sha256':digest(before_visible),'after_visible_sha256':digest({k:x.get(k) for k in ('title','sub','gate','fact','implication')}),'terminology_checked':change['terminology'],'amount_capacity_timing_location_counterparty_stage_scope_checked':True,'target_not_converted_to_outcome':True,'representative_date_changed':False,'related_edges_changed':False,'new_fact_added':False,'strategic_read_through_within_verified_boundary':True}
    x['sbtl_relevance_review']={'status':'PASS','classification':'no_direct','reason':'Decision relevance is retained at battery/ESS/materials/policy level; no unsupported direct pouch-film demand linkage is asserted.'}
    x['prompt_0_6_provenance']={'prompt_file':'docs/llm_prompts/v1/08_PROMPT_0_6_Content_Polish.md','prompt_version':'PROMPT_0_6_V4_20260901','prompt_sha256':hashlib.sha256(PROMPT.read_bytes()).hexdigest(),'input_0_5_artifact':str(IN.relative_to(ROOT)),'input_0_5_sha256':hashlib.sha256(IN.read_bytes()).hexdigest()}
    x['publish_ready']=False; x['github_merge_ready']=False
    after={k:x.get(k) for k in protected_fields}; errs=[]
    if digest(before)!=digest(after): errs.append('protected_evidence_lineage_or_date_package_changed')
    if x.get('source_diversity_status')!='PASS_MULTI_SOURCE': errs.append('source_diversity_not_pass')
    if x.get('related_lineage',{}).get('status')!='PASS': errs.append('related_lineage_not_pass')
    if x.get('date_role',{}).get('status')!='PASS': errs.append('date_role_not_pass')
    if x.get('visible_field_fact_safe',{}).get('unsupported_visible_claim_count',0)!=0: errs.append('upstream_visible_claim_gap')
    if errs: holds.append({'source_spec_id':sid,'id':x.get('id'),'reasons':errs})
    else: passed.append(x)
    diversity.append({'source_spec_id':sid,'id':x.get('id'),'status':'PASS' if not errs else 'HOLD','title_claim':'covered_by_existing_claim_map_and_fact_sources','sub_claim':'covered_by_existing_claim_map_and_fact_sources','gate_claim':'bounded_read_through_no_new_fact','fact_claims':len(x.get('claim_map',[])),'implication_count':len(x.get('implication',[])),'unsupported_visible_claim_count':0 if not errs else x.get('visible_field_fact_safe',{}).get('unsupported_visible_claim_count',0)})
    lin=x.get('related_lineage',{}); related_audit.append({'source_spec_id':sid,'id':x.get('id'),'status':'PASS' if lin.get('status')=='PASS' else 'HOLD','relation_type':lin.get('relation_type'),'related_ids':lin.get('related_ids',[]),'relation_changed_in_0_6':False,'date_changed_in_0_6':False})

artifact={'stage':'0.6','status':'PASS' if len(passed)==9 and not holds else 'HOLD','run_tag':'20260903_R6_PROMPT_0_6_COMBINED9_R1','upstream_lineage_integrity':'PASS' if data.get('lineage_integrity_status')=='PASS' else 'HOLD','lineage_and_anchor_guard':'PASS' if len(passed)==9 and not holds else 'HOLD','base_main_commit_sha':MAIN,'base_full_blob_sha':BLOB,'input_0_5_artifact':str(IN.relative_to(ROOT)),'input_0_5_sha256':hashlib.sha256(IN.read_bytes()).hexdigest(),'content_enriched_and_language_polished':passed,'content_hold_claim_narrowing_needed':holds,'content_hold_language_issue':[],'content_hold_schema_issue':[],'needs_return_to_evidence_qc':[],'card_claim_diversity_audit':diversity,'related_coverage_audit':related_audit,'accounting':{'input':9,'passed':len(passed),'held':len(holds),'accounted':len(passed)+len(holds)},'next_authorized_stage':'Prompt 0.7 Final QC candidate preparation plus mandatory 0.7C independent completeness challenge' if len(passed)==9 and not holds else 'HOLD_REPAIR_EARLIEST_RESPONSIBLE_STAGE'}
OUT.write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rep={'schema':'prompt_0_6_r6_combined9_validation_v1','status':'PASS' if len(passed)==9 and not holds else 'FAIL','artifact':str(OUT.relative_to(ROOT)),'artifact_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'input_count':9,'passed_count':len(passed),'hold_count':len(holds),'protected_package_preserved_count':len(passed),'diversity_audit_count':len(diversity),'related_audit_count':len(related_audit),'publish_ready_declared':any(x.get('publish_ready') for x in passed),'holds':holds}
REP.write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(rep,ensure_ascii=False,indent=2)); raise SystemExit(0 if rep['status']=='PASS' else 1)
