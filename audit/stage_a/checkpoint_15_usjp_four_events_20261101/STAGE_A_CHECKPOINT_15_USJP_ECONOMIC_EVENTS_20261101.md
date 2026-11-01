# SBTL_HUB — Stage A 체크포인트 #15

**작성 기준:** 2026-11-01 KST / 2026-11-01 UTC  
**출발 기준선:** Stage A 체크포인트 #14, 전체 1,330 Source ID 유지  
**거버넌스:** Stage A 전체 **HOLD** / Stage B 실행 **0** / 신규 발행 카드 **0** / GitHub main·Full·Related·프로덕션 변경 **0**

## 정식 심사: 네 개 독립 사건·열 개 Source ID

| 신규 정식 Stage A 경제적 사건 | 대표 Source row | 동종 보강 row | 공식 행위 및 경계 |
|---|---:|---|---|
| Georgia Power Robins 128MW ESS 상업운전 확인 | 86 | 없음 | 2026-09-15 공식 자료 기준 이미 상업운전; 정확한 최초 COD일 미확인 |
| EVE Power–Fluence 206GWh 공급 프레임워크 | 1265 | 16, 116, 133, 158 | 2027년 16GWh 약정 + 2028~2031년 190GWh 예약; 개별 PO는 후속 |
| Factorial–Mitsui Kinzoku 황화물 전해질 JDA | 126 | 없음 | 2026-09-17 공동개발 합의; 양산·상업출하·독립 검증 완료 아님 |
| Panasonic Energy Kadoma 배터리 R&D 허브 가동 | 78 | 119 | 2026-09-16 연구개발 시설 가동; 상업용 GWh 생산시설 아님 |

별도 1개 Source ID `SRC26-20260920_142928-0115`(row 115)는 **FlexGen–Lightshift 16개 프로젝트**의 기존 Full **`2026-09-16_US_02`** 보강 출처로 확정했다. 해당 Full은 기존 운영 6개 25MW/85MWh 및 건설 중 10개 55MW/200MWh라는 단계를 이미 구분한다. 이번 기사에서 16개 전부 신규 상업운전으로 재해석하지 않았다.

### 다중 경제행위 분리: Source row 86

하나의 미국 ESS 종합기사에 세 기업 사건이 존재한다.

1. **Eos Energy**: DOE 보증대출 기존 두 번째 트랜치에서 $87,018,601 실제 인출 → Full **`2026-09-10_US_01`** 이미 수록. 신규 보조금이나 제조 생산량 달성으로 오인하지 않음.
2. **FlexGen–Lightshift**: 16개 EMS 프로젝트 확대 → Full **`2026-09-16_US_02`** 이미 수록. 운영·건설 단계를 분리.
3. **Georgia Power**: Robins 128MW ESS **상업운전 상태** → 해당 경제행위가 Full1676에 없어 새 strict spec 1건으로 편입. 원문은 9월15일 운영 상태를 확인하지만 개시 정확일을 명시하지 않고, 2025년 5월 자료의 2026년 6월 예상 COD와는 다름. 128MW × 최대 4시간을 공인된 정격 MWh로 자동 환산하지 않음.

대표 Source ID 하나를 보존하면서 세 자산·기업의 사건 계보를 분기하여 저장했다. 기사 한 건을 기계적으로 신규 카드 세 장으로 만들지 않았다.

### 구매계약 단계 구분: EVE–Fluence

- EVE Energy 공시 **2026-118**호(9월18일): 총 206GWh, 2027년 **16GWh commitment**, 2028~2031년 **190GWh reservation**. 제품, 모델, 가격, 납기, 구체 구매수량은 후속 PO에 따르며 재무 영향도 불확실.
- Fluence 9월24일 원발표는 같은 멀티이어 공급 프레임워크 구매자 측 확인. 9월24일자를 신규 206GWh 계약 사건으로 다시 세지 않음.
- Source row **133, 158**의 중국어 제목은 전체 206GWh를 ‘초대형 확정 주문’으로 읽게 하는 위험이 있으므로 별도 정정 경고를 해당 Source ID에 보존.
- 글로벌 공급 협력이라고 해서 미국 시장으로 전량 유입하거나 FEOC·국산화 요건 충족 또는 실제 매출로 표현하지 않음.

### 전고체·연구 시설의 상업화 경계

- Factorial–Mitsui: 두 회사의 공개 발표가 황화물 전해질 소재·층 형성 연구 JDA를 뒷받침. 목표는 대량생산 적합성 검증이며 양산 성공 사실이 아님. 기존 Full의 Factorial 드론 셀 주문·차량 실증 사건과 별도.
- Panasonic Kadoma: 약 **24,500㎡** 규모 연구·시제품·분석 기능이 있는 거점. 운영 인력 약 500명은 신규 채용 수로 자동 환산하지 않음. Suminoe 및 미국 공장의 후속 공정 이전·양산 성과는 별도 확인 필요.
- Source row **8**(InsideEVs CEO 인터뷰)은 Mitsui 외 기존 PowerCo·현대차·SK온·포스코퓨처엠 파트너십과 Karma 2028 목표, 기술 지표도 함께 다룸. 기사 전체를 단순 보강으로 억지 판정하지 않고 **원래 WATCH 상태 그대로 보존**, 하위 경제행위의 선행 발표·신규성 추가 확인 대상으로 표기.

## 원문·동일 사건 대조 지점

| 구분 | 원발행 자료 |
|---|---|
| Georgia Power 운영확인 | https://www.georgiapower.com/news-hub/press-releases/georgia-power-robins-battery-storage-achieves-commercial-operation.html |
| Georgia Power 기존 건설계획 | https://www.georgiapower.com/news-hub/press-releases/construction-now-underway-on-765-mw-of-new-battery-energy-storage-systems-across-georgia.html |
| Eos 실제 DOE 대출 인출 | https://eosenergyenterprises.gcs-web.com/news-releases/news-release-details/eos-energy-enterprises-receives-87-million-advance-under-us |
| FlexGen 16개 프로젝트 원발행 | https://www.flexgen.com/resources/blog/flexgen-partners-lightshift-energy-its-16-battery-energy-storage-projects-pjm-iso-ne |
| EVE 9월18일 증권 공시 PDF | https://static.cninfo.com.cn/finalpage/2026-09-18/1225571033.PDF |
| Fluence 9월24일 구매자 확인 | https://ir.fluenceenergy.com/news-releases/news-release-details/fluence-secures-long-term-battery-supply-through-multiyear |
| Factorial·Mitsui JDA | https://factorialenergy.gcs-web.com/news-releases/news-release-details/mitsui-kinzoku-partners-factorial-scale-all-solid-state-battery |
| Mitsui 자체 발표 | https://www.mitsui-kinzoku.com/en/news_a/?TabModule903=0&dispmid=1140&itemid=1993 |
| Panasonic Energy 글로벌 발표 | https://news.panasonic.com/global/press/en260916-3 |

## 정식 상태 변화

| 지표 | 체크포인트 #14 | 체크포인트 #15 |
|---|---:|---:|
| 원본 Source ID | 1,330 | **1,330** |
| 누적 정식 개별 판단 | 76 | **86** |
| 정식 미완료 | 1,254 | **1,244** |
| strict_passed_spec | 10 | **14** |
| candidate_review_pool | 605 | **598** |
| watchlist_context_pool | 658 | **655** |
| reject_or_support_only_pool | 28 | **33** |
| existing_reinforcement | 29 | **30** |
| 신규 발행 기사·Stage B 실행 | 0 | **0** |

검토 원장 10건의 최종 분류: **strict 4 / 동일 사건 보강 5 / 기존 Full 보강 1**. WATCH 유지 row 8은 위의 10건에 포함하지 않았다. 네이티브 `needs_review_count`는 1,286이며, 이 수치와 정식 **미완료 1,244**는 개념이 다르다.

## 네이티브·독립 QC

- Native `validation_scripts/stage_artifact_contract_check.py A`: **PASS** (`item_count=14`).
- Native `validation_scripts/stage_lineage_contract_check.py stage_a`: **PASS_STAGE_A_SCHEMA_CONTRACT**.
- 독립 원장 비교: **PASS_1330_NOLOSS_10_SOURCE_DECISIONS_BOTH_NATIVE_CONTRACTS**. 원본 1,330행의 ID·순서·원본 제목·URL 무변경, 신규 수정 행 정확히 10개, 기존 정식 76개 계보·전 70개 사전 입력 해시 그대로 보존, 사용자 Full 실제 수정 없음.
- 정책·자산·기술의 선행 단계와 실제 달성 단계 구분은 Stage B 본문증빙 전에 자동 반영하지 않음. Stage A strict는 향후 증빙 수집 가능한 후보이며 최종 기사가 아니다.
- 네이티브 스키마의 제한된 **`Stage B r0` 추천 필드**와 사용자 발행 거버넌스는 별개. 전체 0.1P는 **1,244개 미완료로 HOLD**이고 Stage B 진입 권한이 아직 없다.

## 해시와 재현

- 입력 체크포인트 #14 SHA256: `32cde5ebdfe5dbb751c8fba2f1cc62c2ef6a3d0647efa00f8c10ff2498cbb69e`.
- 출력 체크포인트 #15 SHA256: `8bd11020fea3c8874837fa2a30b5bab619e0174a7e92b43661d5c5b225a230c6`.
- 동봉 패키지: 전체 1,330행 네이티브 JSON, 10건 판정 Receipt, 생성 코드, 비교·네이티브 QC 코드/결과, 체크포인트 메모. 업로드 후 별도 SHA256 목록으로 재다운로드 검증.

## 다음 병목

이전 70개 사전 판단 입력의 다른 사건군과 원래 미완료 Source ID를 계속 정식 0.1P에 편입하되, 총 기사 수·승격 수를 사전에 정하지 않는다. 같은 URL·같은 기사라도 **기업·자산·날짜·실행 단계별 하위 경제적 행위를 별도로 보존**, 추론만으로 발행하거나 보강 출처를 삭제하지 않는다. 전체 1,330 Source ID 판정 완결·독립 QC·네이티브 2종 재실행 전까지 Stage B **HOLD**.
