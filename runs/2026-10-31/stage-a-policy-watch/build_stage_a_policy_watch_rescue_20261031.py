#!/usr/bin/env python3
"""Create-only evidence-anchored Stage A 0.1P bounded rescue cohort, NOT native PASS.

One source observation is not necessarily one economic event. Keep the original
source universe immutable, attach individually reasoned review overlays, and
never infer formal Stage A acceptance from score or presence of an issuer link.
"""
import copy
import hashlib
import json
from collections import Counter
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parent
BASE=ROOT/'STAGE_A_1330_SOURCE_INTEGRATED_EVIDENCE_OVERLAY_V4_20261030.json'
PREV=ROOT/'STAGE_A_LAST16_FOUR_JUDGMENTS_PRE_NATIVE_20261031.json'
OUT=ROOT/'STAGE_A_0_1P_POLICY_MARKET_WATCH_RESCUE_CASES_20261031.json'
OVERLAY=ROOT/'STAGE_A_1330_SOURCE_INTEGRATED_EVIDENCE_OVERLAY_V5_POLICY_WATCH_20261031.json'
EXPECTED_BASE_SHA='0646b280eac1963e6889410529d1b1f92a2b485077982677527612c176201104'
EXPECTED_PREV_SHA='1faf426f340e8c8c2bd2570c6d84697cd062397e25bee478c2e139b2aba2cb1e'
ORIGINAL_CSV_SHA='5e78420916b0c1d70ff56bf928779cd969b94fbb15dd4119c841872997486116'
FIELDS=['market_structure_competition','supply_demand_price_utilisation','technology_performance_safety',
        'cashflow_asset_value','law_policy_market_access','systemic_scale','persistence_irreversibility',
        'decision_urgency_actionability']
MAXS=[25,25,20,10,10,5,3,2]
TECH_CAPS={'not_applicable':0,'company_target_or_unsupported_claim':4,'laboratory_unvalidated':7,
           'pilot_precommercial':11,'independent_test_or_customer_qualification':15,
           'commercial_scale_or_long_duration_field':20,'material_failure_evidence':20}
NOV_CAPS={'repeated_announcement_no_new_fact':39,'routine_progression_no_material_uncertainty':54,
          'company_target_without_validation_or_effect':54,'unsupported_political_rhetoric':39}
POLICY_CAPS={0:39,1:54,2:69}

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def case(key,idx,rep,anchor,anchor_owner,anchor_url,date0,event,prior,change,risk,full,score,
         tech='not_applicable',stage=None,nov='none',urgency='near_term',
         extra_urls=None,units=None,lenses=None,denominator=None,missing=None,notes=None):
    assert rep in idx
    return dict(case_id=key,source_row_indices=idx,representative_source_row_index=rep,
                original_anchor_owner=anchor_owner,source_anchor_class=anchor,
                original_first_party_or_owner_url=anchor_url,source_additional_urls=extra_urls or [],
                event_date=date0,original_economic_event=event,prior_state=prior,
                changed_verifiable_fact=change,must_not_claim=risk,full_identity_prepass=full,
                decision_value_parts=score,technology_evidence_level=tech,policy_stage=stage,
                novelty_cap_basis=nov,publication_urgency=urgency,
                event_units=units or [key],lenses=lenses or [],
                systemic_scale_denominator=denominator,
                remaining_evidence=missing or [],special_source_notes=notes or {})

CASES=[
case('KR_RESOURCE_SECURITY_PLAN_20260923',
[222,230,234,250,256,270,281,283,284,429,570,604,606,608,609,612,618,622,1018,1271],222,
'policy_regulatory_anchor','산업통상부','https://www.motir.go.kr/kor/article/ATCL3f49a5a8c/172235/view?mno=&pageIndex=6',
'2026-09-23',
'6차 자원안보 협의회에서 1차 자원안보 기본계획 등 4개 안건 심의·확정',
'핵심광물 관리대상 38종, 비축 대상 24종, 최대 180일 목표; 최초 법정 중장기 계획 이전',
'핵심광물 51종, 비축 품목 29종, 취약광종 최대 365일 목표; 원유 특정지역 의존 2035년 50% 이하 목표',
'51종 전부 365일 재고 확보 완료 또는 2026년 2,000만 배럴 비축시설 완공으로 표현 금지',
'NO_EXACT_SEPT23_DECISION_IN_LOCKED_FULL_1676;RELATED_APR24_RESOURCE_SECURITY_LAW',
[18,21,0,8,9,4,3,2],stage=3,
extra_urls=['https://www.motir.go.kr/kor/article/ATCL03465409b/171730/view?mno=&pageIndex=1'],
units=['기본계획_확정','제5차_석유비축계획_조정','핵심광물_지정계획_확정','제1차_핵심광물비축계획_확정'],
lenses=['policy','critical_materials','supply_chain'],
denominator='핵심광물 기존 38종·신규 51종; 비축기존 24종·신규 29종',
missing=['별첨 기본계획의 품목별 의무·예산·시행단계','기존 2026-04-24_KR_07 법 개정과 후속관계 분리'],
notes={234:'원유 관련 수치는 원유 특정지역 의존 50% 이하 목표, 즉시 비중동산 50% 달성 아님'}),
case('KR_ESS_CENTRAL_TENDER_1180MW_20260922',
[48,235,244,260,271,535,538,614,916,1279],235,
'execution_event_anchor','기후에너지환경부·한국전력거래소',
'https://www.mcee.go.kr/home/web/board/read.do?boardId=1893270&boardMasterId=939&menuId=10598',
'2026-09-22',
'ESS 중앙계약시장 사업자 선정 경쟁입찰 공고(육지 1,100MW, 제주 80MW)',
'2023~2026 상반기 세 차례 시장 운영 및 누적 선정 1,196MW',
'9월 22일 새 1,180MW 입찰 공고; 대상 변전소 확대, 제주 장수명·고빈도 충방전 25년 선택계약 신설',
'1,180MW를 낙찰·계약체결·설치완료로 표기 금지, 2029년 2월은 구축 목표, 25년 조건은 모든 사업 보편 의무 아님',
'NO_EXACT_20260922_TENDER_IN_FULL;PREVIOUS_ESS_PROCUREMENT_DIFFERENT_ROUND',
[18,23,0,8,8,5,3,2],stage=4,
extra_urls=['https://www.kpx.or.kr/board.es?act=view&bid=0042&list_no=78164&mid=a10501010000&nPage=1'],
units=['육지_1100MW_입찰공고','제주_80MW_입찰공고_25년계약옵션'],
lenses=['downstream_ess','grid','policy'],
denominator='이번 육지 1,100MW+제주 80MW=1,180MW; 기존 선정 1,196MW',
missing=['전력거래소 공고 제2026-05/06호 세부 입찰서류·지원자격 및 계통입지','실제 낙찰 발표와 별도 후속관계'],
notes={48:'9월 20일 사전 전망 기사; 9월 22일 입찰 공고 발생 전 보도',
244:'한 기사에 폐차 희토류 회수체계라는 별도 정책행위 포함; 자동 합병 금지',
614:'244와 정확 재수집 가능성 확인 후 동일 기사 source observation edge 보존',
916:'9월 28일 사업자 등록 절차 개시 보도; 새로운 1,180MW 시장으로 추가 계산 금지'}),
case('EVE_FLUENCE_206GWH_FRAMEWORK_20260918',
[16,116,133,158,1265],16,'execution_event_anchor','EVE Energy / Fluence',
'https://static.cninfo.com.cn/finalpage/2026-09-18/1225571033.PDF',
'2026-09-18',
'2027~2031년 EVE Power–Fluence 206GWh 공급 프레임 체결·공시',
'양사 기존 거래관계 및 Fluence 이전 FY26 실적·계약전망은 별개',
'2027년 약정 16GWh 및 2028~2031년 예약 190GWh 구분. Fluence 9월24일 구매자 발표',
'206GWh를 확정 purchase order·매출·출하로 표현 금지; 개별 제품·가격·수량·납기는 후속 PO',
'NO_EXACT_SUPPLY_FRAMEWORK_IN_FULL;2026-09-16_GL_01_IS_FY26_GUIDANCE_NOT_THIS_AGREEMENT',
[20,22,0,8,1,2,3,2],
extra_urls=['https://fluenceenergy.gcs-web.com/news-releases/news-release-details/fluence-secures-long-term-battery-supply-through-multiyear'],
units=['2027_16GWh_약정','2028_2031_190GWh_예약'],
lenses=['cell','downstream_ess','supply_chain'],
missing=['2027년 commitment의 take-or-pay 집행범위','후속 실제 purchase order 및 현지조달 조건']),
case('ESVOLTA_GOOGLE_HOURLY_CERT_PILOT_20260917',
[19,123,468],19,'technology_commercialization_anchor','Quintrace·esVolta·LevelTen Energy / Google pilot',
'https://www.esvolta.com/post/battery-storage-shift-pilot-demonstrates-how-hourly-renewable-certificates-can-power-the-next-phase',
'2026-09-17',
'배터리 시간대별 환경증서(hourly granular certificates) 연계 파일럿 결과 발표',
'ESS 재생에너지 시간별 연계·증서 수익 모델의 파일럿 결과 이전',
'Google 후원 실증에서 태양광 충전과 시간별 증서 배분으로 청정전력 시간대 일치 사례 제시',
'범용 인증시장 법제화·회계기준 확정·전 ESS에 실제 정산수익 발생으로 오인 금지',
'NO_EXACT_ESVOLTA_HOURLY_CERT_FULL_MATCH',
[13,13,10,5,2,2,2,1],tech='pilot_precommercial',nov='company_target_without_validation_or_effect',
units=['후원_실증_결과','환경증서_정산규칙_제안'],
lenses=['downstream_ess','market_structure','grid'],
missing=['실제 제3자 증서 발행·거래 및 회계기준 인정 여부','재현가능 수익단가와 확산상태']),
case('UK_OFGEM_CMP470_COMMITMENT_FEE_CONSULT_20260917',
[122,138],122,'policy_regulatory_anchor','Ofgem',
'https://www.ofgem.gov.uk/consultation/connection-and-use-system-code-cusc-cmp470-introducing-oversubscribed-technologies-commitment-fee-otcf',
'2026-09-17',
'BESS 전력망 접속대기열 Commitment Fee CMP470 승인 검토의견에 대한 공식 협의 개시',
'영국 계통접속 대기 BESS 대규모 과밀, 신규 요금조치 확정 전',
'Ofgem 9월17일 CMP470 consultation 발표, 10월2일 마감, 현재 결정 대기; 약 90GW vs 2035 요구 29GW',
'신규 수수료가 이미 법적 시행되었다고 단정 금지',
'NO_EXACT_CMP470_FULL_MATCH;EARLIER_OFGEM_DYNAMIC_RESPONSE_DIFFERENT_RULE',
[15,18,0,6,9,3,2,1],stage=1,urgency='monitor',
extra_urls=['https://www.ofgem.gov.uk/press-release/ofgem-moves-free-grid-capacity-tackling-excess-battery-projects'],
units=['CMP470_접속보증금_협의','기존대기프로젝트_재진단_정책방향'],
lenses=['policy','grid','downstream_ess'],
denominator='약 90GW 운영·접속대기 용량 vs 2035 필요량 약 29GW',
missing=['Ofgem 최종 CMP470 decision','금액·적용대상·경과 및 면제조건']),
case('PANASONIC_KADOMA_RND_OPEN_20260916',
[78,119],78,'execution_event_anchor','Panasonic Energy',
'https://news.panasonic.com/global/press/en260916-3',
'2026-09-16','Panasonic Energy Energy Innovation Square 가동 발표(오사카 Kadoma)',
'기존 오사카·미국 공장 연구개발 시설 운영',
'소재 연구·셀 설계·시제품의 통합 배터리 R&D 허브 가동, 미국 등 생산거점과 연계',
'Kadoma에서 양산 셀 매출 발생·차세대 기술 검증 완료로 주장 금지',
'NO_EXACT_KADOMA_FACILITY_FULL_MATCH;PRIOR_PANASONIC_BATTERY_QUALIFICATION_DIFFERENT_MILESTONE',
[14,17,4,6,0,2,1,1],tech='company_target_or_unsupported_claim',
units=['신규_R&D_시설_운영개시'],lenses=['cell','materials','technology'],
missing=['연구시설 실증·CAPEX·생산능력 별도 확보','동일기업 다른 Full 카드의 사건중복 추가 확인']),
case('FLOW_POWER_BENNETTS_CREEK_20260918',
[120],120,'execution_event_anchor','Flow Power',
'https://flowpower.com.au/flow-power-celebrates-bennetts-creek-battery-construction-milestone/',
'2026-09-18',
'Bennetts Creek 100MW/223MWh 1단계 건설행사와 300MW/1.2GWh 2단계 구상 공표',
'2025년 12월 금융종결; 실제 공사는 2026년 9월 행사보다 수개월 전에 시작된 것으로 현지 보도',
'9월 공개 행사는 실제 착공일 아님; 2단계 1.2GWh는 인허가 전 계획',
'9월18일 신규 실제 착공 또는 1.423GWh 즉시 건설 중으로 서술 금지',
'NO_EXACT_BENNETTS_FULL_MATCH',
[13,19,0,8,0,2,2,1],nov='routine_progression_no_material_uncertainty',
extra_urls=['https://latrobevalleyexpress.com.au/news/2026/09/22/battery-in-the-works-at-hazelwood-nth/'],
units=['1단계_100MW_223MWh_기존공사_행사','2단계_300MW_1200MWh_제안'],
lenses=['downstream_ess','power'],urgency='monitor',
missing=['1단계 실제 현장 시작일 공식 시계열','2단계 인허가·FID']),
case('CANADA_CITT_PV_CHINA_DUTY_RESCISSION_20260917',
[173],173,'policy_regulatory_anchor','Canadian International Trade Tribunal',
'https://www.canada.ca/en/international-trade-tribunal/news/2026/09/tribunal-terminates-expiry-reviewphotovoltaic-modules-and-laminates-from-china.html',
'2026-09-17',
'중국산 PV 모듈·라미네이트 무역구제 명령 취소, 반덤핑·상계관세 집행 중단',
'2021년 RR-2020-001 명령 유지·2026년 2월부터 만료심사 개시',
'2026년 9월 CITT 만료심사 종료와 관련 명령 취소, CBSA 부과 중단',
'리튬배터리·ESS 완제품 관세 철회로 확대 해석 금지',
'NO_EXACT_CITT_PV_DUTY_RESCISSION_FULL_MATCH;SOLAR_SUPPLY_CHAIN_INDIRECT_BATTERY_LINK',
[14,18,0,5,10,2,2,1],stage=5,
units=['중국산_PV_무역구제_종결'],lenses=['policy','power','trade'],
missing=['반덤핑·상계관세 실제 종료일·수입자 적용상세','SBTL 배터리 산업 독립 카드 적합성']),
case('LG_DATA_CENTER_CHILLER_PRODUCT_20260920',
[176,177,178,179],176,'technology_commercialization_anchor','LG Electronics',
'https://www.lge.co.kr/story/newsroom/236187',
'2026-09-20',
'LG전자 AI 데이터센터 특화 터보 칠러 제품 발표 및 약 30% 효율 주장',
'LG전자 기존 데이터센터 공조·액침냉각 사업',
'고효율 칠러 신제품 소개: 배터리 제품·ESS 설치 계약은 아님',
'30% 절감은 제조사가 수랭식 프리쿨링 대비 제시한 연간 조건부 추정치; 실제 전체 데이터센터 전력·PUE 절감으로 단정 금지',
'NO_EXACT_PRODUCT_FULL_MATCH;INDIRECT_AI_POWER_COOLING_LENS',
[12,11,4,3,0,2,1,1],tech='company_target_or_unsupported_claim',
units=['터보칠러_제품공개'],lenses=['power','AI_datacenter'],urgency='monitor',
missing=['LG전자 공식 제품일자·검증된 시험조건','독립 ESS·배터리 소재 수요 연결']),
case('CHINA_TOPCON_OPIS_WEEKLY_PRICE_20260915',
[172],172,'data_financial_anchor','OPIS / pv magazine',
'https://pv-magazine-usa.com/2026/09/18/china-topcon-solar-cell-prices-fall-for-third-week-as-export-buying-fades-and-wafer-costs-ease/',
'2026-09-15',
'OPIS China TOPCon 셀 가격 지표 3주 연속 하락, 수출주문 둔화·웨이퍼 원가조정',
'8월말 수출 주문 선행매수로 가격 상승',
'9월 15일 OPIS 가격 보고서에서 M10 셀 FOB $0.0469/W(-2.29% w/w), 210R $0.0458/W(-1.72% w/w)',
'분석가 가격 스냅샷을 전세계 실거래 가격 또는 ESS 셀 가격으로 혼동 금지',
'NO_EXACT_OPIS_WEEKLY_PRICE_EVENT_FULL_MATCH;POWER_UPSTREAM_NOT_BATTERY_CELL',
[13,19,0,4,0,2,2,1],nov='none',
units=['TOPCon_가격_주간변화'],lenses=['market_price','power','upstream'],urgency='monitor',
missing=['주간 추세 후속 수치','태양광 공급망이 배터리 수요로 전달되는 직접 메커니즘']),
case('US_ESS_ROUNDUP_EOS_FLEXGEN_GEORGIA_202609',
[86,115],86,'execution_event_anchor','Eos / FlexGen-Lightshift / Georgia Power',
'https://www.georgiapower.com/news-hub/press-releases/georgia-power-robins-battery-storage-achieves-commercial-operation.html',
'2026-09-15',
'복수 ESS 실행 사건 종합: Eos 대출인출, FlexGen/Lightshift 16개 프로젝트, Georgia Power Robins BESS COD',
'Eos DOE 시설 기존 대출약정·FlexGen 16개 프로젝트 기존 Full 각각 반영',
'Robins 128MW ESS 상업운전 개시가 별도 신규 후보; 다른 두 실체는 이미 Full에서 보존',
'종합기사 하나를 세 건 신규카드로 승격 금지; 128MW로부터 정격 에너지용량 512MWh 자동 산출 금지',
'EXISTING_FULL_EOS:2026-09-10_US_01;FLEXGEN:2026-09-16_US_02;GEORGIA_NEW_COD_FULL_NONE_FOUND',
[14,23,0,8,0,2,3,2],
extra_urls=['https://eosenergyenterprises.gcs-web.com/news-releases/news-release-details/eos-energy-enterprises-receives-87-million-advance-under-us',
'https://renewablesnow.com/news/flexgen-lightshift-expand-battery-storage-partnership-in-us-1301365/'],
units=['EOS_DOE_87018K_THIRD_DRAW_ALREADY_FULL','FLEXGEN_LIGHTSHIFT_16_BESS_ALREADY_FULL','GEORGIA_ROBINS_128MW_COD_NEW_CANDIDATE'],
lenses=['downstream_ess','financing','manufacturing'],
missing=['Georgia Power 최초 상업운전 날짜 vs 축하 행사 날짜','Full 기존 Robins 수록/Related 재확인'],
notes={86:'한 종합기사에 독립 경제행위 3건. Eos·FlexGen 기존 Full, Robins 새 COD 후보',
115:'FlexGen 55MW/200MWh 10개 건설 중 사업과 6개 기운영 사업; 기존 Full 2026-09-16_US_02 보강 자료'}),
case('FACTORIAL_MITSUI_SULFIDE_JDA_20260917',
[8,126],8,'execution_event_anchor','Factorial / Mitsui Kinzoku',
'https://factorialenergy.gcs-web.com/news-releases/news-release-details/mitsui-kinzoku-partners-factorial-scale-all-solid-state-battery',
'2026-09-17',
'Factorial 전고체 Solstice용 Mitsui Kinzoku 황화물 전해질·공정 공동개발 계약',
'기존 Factorial 2026년 7월 드론 상업주문은 제품·고객이 다른 사건',
'황화물 전해질 적용 셀 제조공정 공동개발 합의; 양산 상업출하로 검증된 성과 아님',
'전고체 배터리 제조 규모확대 완료 또는 성능표준 통과를 JDA만으로 단정 금지',
'RELATED_OTHER_FULL:2026-07-24_US_01_IS_SEPARATE_DRONE_CELL_ORDER',
[13,12,4,6,0,2,2,1],tech='company_target_or_unsupported_claim',
extra_urls=['https://www.mitsui-kinzoku.com/en/news_a/?TabModule903=0&dispmid=1140&itemid=1993'],
units=['신규_황화물_셀공정_JDA'],lenses=['technology','cell','materials'],
missing=['합의의 계약적 구속력','고객/양산라인 적용 및 독립 qualification']),
case('HIRASOL_ISUMIZAKI_NEGAPOSI_GRID_20260916',
[79],79,'execution_event_anchor','Hirasol Energy',
'https://prtimes.jp/main/html/rd/p/000000027.000085634.html',
'2026-09-16',
'일본 Izumizaki 계통용 ESS의 네가포지 시장 사전심사 통과',
'정격 출력 1,900kW ESS가 조정력 시장에 참여하기 전',
'시장 참여 적격으로 조정력 제출 가능량 3,800kW 승인(정격의 2배)',
'ESS 물리정격이 3,800kW로 증설된 것이 아니며 2배 매출 실현을 의미하지 않음',
'NO_EXACT_HIRASOL_ISUMIZAKI_FULL_MATCH',
[14,16,6,6,2,2,2,1],tech='pilot_precommercial',
units=['Izumizaki_시장사전심사_PASS_1900_3800KW'],lenses=['market_structure','grid','downstream_ess'],
missing=['실제 후속 조정력 입찰·낙찰·지급단가','동일 자산·시장제도 관련 정책 원문']),
]

DUP_SCORE=[5,4,0,1,0,1,0,0]   # per-source incremental new-card value: 11, capped 39

def band(score):
    for threshold,name in [(85,'critical_structural'),(70,'high_decision_value'),(55,'material_industry_signal'),(40,'standard_monitoring'),(25,'context_or_reinforcement'),(0,'low_independent_value')]:
        if score>=threshold:return name


def main():
    for out in [OUT,OVERLAY]:
        if out.exists():raise FileExistsError(f'create-only violation: {out}')
    assert digest(BASE)==EXPECTED_BASE_SHA
    assert digest(PREV)==EXPECTED_PREV_SHA
    base=json.loads(BASE.read_text());prev=json.loads(PREV.read_text())
    assert base['original_csv_sha256']==ORIGINAL_CSV_SHA
    assert len(base['source_rows'])==1330 and base['original_formal_pending_0_1P_unchanged']==1285
    assert len(prev['judgments'])==16
    rows=base['source_rows'];by_idx={r['source_row_index']:r for r in rows};assert len(by_idx)==1330
    known_ids={j['source_id'] for j in prev['judgments']}
    used=set();assessed=[];all_event_units=set()
    for c in CASES:
        assert c['source_anchor_class'] in ['execution_event_anchor','policy_regulatory_anchor','data_financial_anchor','technology_commercialization_anchor']
        assert len(c['source_row_indices'])==len(set(c['source_row_indices']))
        assert c['representative_source_row_index'] in c['source_row_indices']
        for unit in c['event_units']:all_event_units.add(c['case_id']+'::'+unit)
        parts=c['decision_value_parts'];assert len(parts)==8
        for v,m in zip(parts,MAXS):assert 0<=v<=m
        if c['technology_evidence_level'] in TECH_CAPS:assert parts[2]<=TECH_CAPS[c['technology_evidence_level']]
        if c['systemic_scale_denominator'] is None:assert parts[5]<=2
        total=sum(parts)
        if c['policy_stage'] in POLICY_CAPS:assert total<=POLICY_CAPS[c['policy_stage']]
        if c['novelty_cap_basis'] in NOV_CAPS:assert total<=NOV_CAPS[c['novelty_cap_basis']]
        for idx in c['source_row_indices']:
            assert idx not in used,(c['case_id'],idx)
            r=by_idx[idx];sid=r['candidate_id'];assert sid not in known_ids
            assert r['native_0_1P_state']=='NATIVE_INDIVIDUAL_0_1P_PENDING',sid
            used.add(idx)
            representative=idx==c['representative_source_row_index']
            if representative:
                current_score=parts
                novel=c['novelty_cap_basis']
                relation='uncertain_needs_review'
                exec_gate='PASS' if c['source_anchor_class'] in ['execution_event_anchor','data_financial_anchor'] else 'REVIEW'
                card_gate='REVIEW'
                urgency=c['publication_urgency']
                decision='REVIEW_STRUCTURAL_EVENT_UNDER_NATIVE_0_1P_GATE'
            else:
                current_score=DUP_SCORE
                novel='repeated_announcement_no_new_fact'
                relation='same_event_duplicate'
                exec_gate='REVIEW'
                card_gate='FAIL'
                urgency='monitor'
                decision='SOURCE_SUPPORT_OR_RELATED_OBSERVATION_NO_SECOND_NEW_CARD'
            if c['case_id']=='US_ESS_ROUNDUP_EOS_FLEXGEN_GEORGIA_202609' and idx==115:
                decision='EXISTING_FULL_2026-09-16_US_02_SUPPORT_NO_NEW_CARD'
            if c['case_id']=='KR_ESS_CENTRAL_TENDER_1180MW_20260922' and idx in (48,244,614,916):
                decision='RELATED_PROCEDURAL_OR_MULTIEVENT_SOURCE_NOT_DEFINITIVE_DUPLICATE'
                relation='uncertain_needs_review'
            note=c['special_source_notes'].get(idx)
            related_candidates=[]
            if not representative:
                related_candidates.append({
                    'target_candidate_id':by_idx[c['representative_source_row_index']]['candidate_id'],
                    'proposed_relation_type':'same_event_duplicate' if relation=='same_event_duplicate' else 'uncertain_needs_review',
                    'confidence':'medium',
                    'reason':'Same case-level original event anchor with distinct source observation; inspect any separate procedural or additional sub-event',
                    'anchor_class_to_verify':None,'incremental_anchor_question':None})
            if c['case_id']=='US_ESS_ROUNDUP_EOS_FLEXGEN_GEORGIA_202609' and idx==86:
                for prev_id in ('2026-09-10_US_01','2026-09-16_US_02'):
                    related_candidates.append({'target_candidate_id':prev_id,
                        'proposed_relation_type':'existing_card_reinforcement','confidence':'high',
                        'reason':'Separate Eos DOE financing and FlexGen/Lightshift ESS milestone already represented in locked Full',
                        'anchor_class_to_verify':None,'incremental_anchor_question':None})
            outcome={
                'source_id':sid,'source_row_index':idx,'headline_raw_original':r['headline_raw'],
                'source_url_original':r['primary_url_original'],
                'original_pool':r['original_stage_a_pool'],'original_metadata_score_not_selection':r['metadata_score_original_not_selection_decision'],
                'case_id':c['case_id'],'case_representative_source_id':by_idx[c['representative_source_row_index']]['candidate_id'],
                'source_is_case_representative':representative,'date_role':{'economic_event_date':c['event_date'],
                    'source_observation_collection_date':'from_source_id_not_identical_to_event_date',
                    'first_party_owner':c['original_anchor_owner']},
                'execution_credibility_gate':{'status':exec_gate,'reason':c['changed_verifiable_fact'] if representative else 'Secondary observation supports a case already represented elsewhere; source-specific first-publication check remains open'},
                'independent_cardability_gate':{'status':card_gate,'reason':'Distinct economic event requires native Related and source path checks' if representative else 'Do not publish a second card for the same provisional economic event'},
                'decision_news_value_score':sum(current_score),
                'decision_value_breakdown':dict(zip(FIELDS,current_score)),
                'decision_value_classification':band(sum(current_score)),
                'publication_urgency':urgency,'technology_evidence_level':c['technology_evidence_level'] if representative else 'not_applicable',
                'policy_stage':c['policy_stage'] if representative else None,
                'novelty_cap_basis':novel,'systemic_scale_denominator':c['systemic_scale_denominator'] if representative else None,
                'denominator_gap':None if representative and c['systemic_scale_denominator'] else 'No source-specific systemic denominator asserted for this observation.',
                'anchor_classes':[c['source_anchor_class']],
                'selection_route':'execution_anchor_route' if c['source_anchor_class']=='execution_event_anchor' else 'structural_non_execution_route',
                'prior_state':c['prior_state'],'new_verified_fact_bounded_to_primary_case':c['changed_verifiable_fact'],
                'changed_judgment':'Candidate event merits separate review' if representative else 'Same economic event does not create a second new-card claim',
                'uncertainty_resolved':'Issuer/agency anchor, stage and source identity bounded by this case review',
                'remaining_uncertainty':c['remaining_evidence'],
                'incremental_information':'Source-independent new case anchor' if representative else 'No independent incremental economic event established',
                'baseline_expectation_changed':'Subject to Related and stage assessment' if representative else 'No second independent event',
                'decision_relevance':c['lenses'],
                'evidence_needed_for_stage_b':c['remaining_evidence'],
                'next_confirmation_points':c['remaining_evidence'],
                'related_prepass':{'status':'HOLD','same_event_checked':True,
                    'matched_baseline_candidate_ids':[],
                    'matched_current_batch_candidate_ids':([] if representative else [by_idx[c['representative_source_row_index']]['candidate_id']]),
                    'relation_candidates':related_candidates,
                    'duplicate_disposition':relation,'earliest_same_event_check_status':'HOLD',
                    'fresh_anchor_questions':c['remaining_evidence'],'full_relation':c['full_identity_prepass']},
                'structural_non_execution_reason':None if c['source_anchor_class']=='execution_event_anchor' else 'The regulatory, pricing, or technology event may change battery and power-sector decisions without a completed asset transaction.',
                'why_execution_event_not_required':None if c['source_anchor_class']=='execution_event_anchor' else 'Structural non-execution selection permits verified policy, supply-chain and operational-pricing changes with separate source and novelty gates.',
                'provisional_disposition_not_native':decision,
                'economic_event_units_preserved':c['event_units'],
                'primary_case_anchor_url':c['original_first_party_or_owner_url'],
                'primary_source_provenance':'ORIGINAL_ANCHOR_INSPECTED_AT_CASE_LEVEL_SOURCE_ARTICLE_BODIES_NOT_ALL_READ',
                'no_automatic_rejection_by_metadata_score':True,
                'source_specific_warning':note,
                'native_0_1P_approved':False,
            }
            # For exact existing Full matches in the mixed roundup, source 86
            # remains a multi-asset composite. Never assign a single event ID.
            if c['case_id']=='US_ESS_ROUNDUP_EOS_FLEXGEN_GEORGIA_202609':
                outcome['related_prepass']['matched_baseline_candidate_ids']=(['2026-09-10_US_01','2026-09-16_US_02'] if idx==86 else ['2026-09-16_US_02'])
            if c['case_id']=='KR_RESOURCE_SECURITY_PLAN_20260923':
                outcome['related_prepass']['matched_baseline_candidate_ids']=['2026-04-24_KR_07','2026-07-23_KR_01']
            if c['case_id']=='FACTORIAL_MITSUI_SULFIDE_JDA_20260917':
                outcome['related_prepass']['matched_baseline_candidate_ids']=['2026-07-24_US_01']
            assessed.append(outcome)
    assert len(used)==54 and len(assessed)==54
    assert len({a['source_id'] for a in assessed})==54
    assert not (set(x['source_id'] for x in assessed)&known_ids)
    assessed.sort(key=lambda x:x['source_row_index'])
    out={'artifact_type':'STAGE_A_POLICY_MARKET_WATCH_54_SOURCE_BOUNDED_FOUR_JUDGMENTS_PRE_NATIVE_20261031',
        'as_of_kst':'2026-10-31','selection_policy_version':'EMBEDDED_NEWS_VALUE_SELECTION_V4',
        'original_csv_sha256':ORIGINAL_CSV_SHA,'parent_v4_sha256':digest(BASE),'previous16_sha256':digest(PREV),
        'original_sources_untouched':1330,'previous_formally_reviewed_untouched':45,
        'formal_remaining_pending_unchanged':1285,'original_strict_unchanged':8,
        'new_source_ids_bounded_four_judgments':len(assessed),
        'combined_pre_native_individual_four_judgments_count':len(assessed)+len(prev['judgments']),
        'separate_economic_case_groups':len(CASES),'event_unit_definitions':len(all_event_units),
        'all_source_ids_still_require_native_gate':True,'new_native_strict_passes':0,
        'case_definitions':CASES,'source_level_judgments':assessed}
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    overlay=copy.deepcopy(base)
    overlay['artifact_type']='STAGE_A_INTEGRATED_EVIDENCE_OVERLAY_V5_POLICY_WATCH_BOUNDED_20261031'
    overlay['parent_v4_sha256']=digest(BASE)
    overlay['oct31_policy_watch_source_judgments_sha256']=digest(OUT)
    overlay['new_pre_native_individual_review_inputs_oct31']=len(assessed)
    overlay['cumulative_pre_native_individual_review_inputs_oct31']=len(assessed)+len(prev['judgments'])
    overlay['original_formal_pending_0_1P_unchanged']=1285
    overlay['new_promotions']=0
    bysid={a['source_id']:a for a in assessed}
    for r in overlay['source_rows']:
        a=bysid.get(r['candidate_id'])
        if a:
            r['oct31_policy_watch_pre_native_case_ref_NOT_FORMAL']={
                'case_id':a['case_id'],'judgment_artifact':OUT.name,
                'provisional_disposition':a['provisional_disposition_not_native'],
                'native_0_1P_approved':False}
    OVERLAY.write_text(json.dumps(overlay,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'new_source_ids':len(assessed),'combined_pre_native_with_prior16':len(assessed)+16,
          'event_cases':len(CASES),'event_units':len(all_event_units),
          'original_ids':len(overlay['source_rows']),'formal_pending':1285,
          'out_sha256':digest(OUT),'overlay_v5_sha256':digest(OVERLAY)},ensure_ascii=False))

if __name__=='__main__':main()
