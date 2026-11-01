# Stage A 체크포인트 #19 — 원발행 문서 기반 21개 Source ID 정식 판정

**작성/검증 기준일:** 2026-11-01 (UTC)  
**기준 파일:** Stage A CP18, SHA256 `4b9039f9f045e92ae5485ddab4ab0ab40bb19da8fdf59bb02c6c0b5adba44b66`  
**Full 동결 참조:** 1,676장, SHA256 `d22f0d4e39e035b9537b3e9abdf48abe6b7eb80f7e477e87aff1284f9e27e0d9`  
**CP19 1,330행 산출물 SHA256:** `bf30369c00bd528b4ab32c628a388b48a56471ac5e8f34fd22631bcb8eaead7d`

## 결론과 범위

Stage A 글로벌 판정은 **HOLD**다. 이번 21개 Source ID에서 정식 Strict 사건 10개, 동일 사건 지원 출처 6개, WATCH 3개, 원문을 확인한 비산업 범위 제외 2개로 분기했다. 기존 105개 정식 판정은 불변으로 보존하여 총 정식 판정이 **126개**가 되었고, 정식 미완료는 **1,204개**다. 새로 발행·승인된 최종 기사는 **0개**이며 Stage B, `main`, Full, Related, 프로덕션 변경도 **0개**다.

| 구분 | CP18 | CP19 | 변화 |
|---|---:|---:|---:|
| 보존 Source ID | 1,330 | 1,330 | 0 |
| 누적 정식 개별 판정 | 105 | **126** | +21 |
| 정식 0.1P 미완료 | 1,225 | **1,204** | −21 |
| Strict 사건 대표 출처 | 20 | **30** | +10 |
| 후보 검토 풀 | 581 | 563 | −18 |
| WATCH 풀 | 660 | 660 | ±0 (3건 대체 반영) |
| Reject/Support 풀 | 39 | 47 | +8 |
| Full 기왕 사건 보강 | 30 | 30 | 0 |

## Strict: 독립 사건 대표 10개

| 대표 Source ID / 행 | 독립 경제 사건 및 공식 증빙 | 확정한 진행 단계 / 금지할 오독 |
|---|---|---|
| `WK26-VOL03-029` / 1277 | [산업부 9/22 나트륨·전고체 배터리 기술 로드맵](https://www.motir.go.kr/kor/article/ATCL3f49a5a8c/172230/view). 2027–2031 정부 신규 R&D 약 4,000억 원, 민간 투자 2026–2030년 8조 원 **추진 목표** | 전략·로드맵 발표는 확정 사건, 연구비 집행·투자 집행·목표 성능 검증 아님. 관련 행 226·302는 하나의 사건으로 보조 연결 |
| `WK26-VOL04-022` / 1244 | [산업부 9/30 전남 광양·여수·순천 이차전지 기초원료 특화단지 지정](https://www.motir.go.kr/kor/article/ATCL3f49a5a8c/172252/view). 2036년까지 민간 약 **5조 3,724억 원 투자계획** | 지역 지정 사실과 향후 제련·인프라 투자 집행을 구분; 앞선 4월 유치 신청과 다른 시점의 사건 |
| `WK26-VOL03-005` / 1255 | [영국 OPSS Powerwall 2 제품 안전 보고서 2609-0219](https://www.gov.uk/product-safety-alerts-reports-recalls/product-safety-report-tesla-powerwall-2-2609-0219) | 일부 제품의 셀 결함 위험, 원격 방전·무료교체 프로그램 시작. 전체 제품 리콜·전량 교체 완료·셀 업체 식별은 미확인 |
| `WK26-VOL03-019` / 1267 | [미 DOE SPARK 9/24 26개 주 31개 전력망 프로젝트 선정 의향](https://www.energy.gov/articles/energy-department-announces-speed-power-investments-across-26-states-lower-electricity). 예정 총 **52.5억 달러** = DOE 19억 + 참여자 33.5억 | 사업 선정·예정 지원은 실제 52.5억 달러 연방보조금 집행, 23GW ESS 설치 완료가 아님 |
| `WK26-VOL03-033` / 1280 | [SEC 제출 Nth Cycle–Glencore Project SHIELD 구속력 있는 텀시트](https://www.sec.gov/Archives/edgar/data/2102713/000119312526397915/d159150d425.htm) | 10년간 10억 달러 초과는 전망 가격 기반 *예상 계약 가치*. 공급·구매 최종 계약은 2026년 말 목표, 납품·매출 확정 아님. 기사 행 349의 과도한 `offtake deal` 표현 보정 |
| `WK26-VOL03-047` / 1294 | [미 EPA Moss Landing 9/18 잔존 배터리 재발화](https://www.epa.gov/ca/moss-landing-vistra-battery-fire-updates). 추가 약 1,300 모듈 소실 추정 | 2025년 대화재 및 9/8 기존 해체 경과와 구분되는 2026년 신규 안전 사건. 신규 상업운전 사고·해체 완료 아님 |
| `C0_DISC_20261005_EU_INDUSTRIAL_BATTERY_DRAFT` / 1324 | [EC WTO TBT G/TBT/N/EU/1242 위임규정 초안 통보](https://technical-barriers-trade.ec.europa.eu/en/notification/40734), 접수 10/5, 의견 마감 12/4 | 산업용 배터리 성능·ESS 내구·배터리여권 등 초안 공개는 실제 규정 채택·발효와 구분 |
| `SRC26-20260926_120143-0202` / 700 | [Glencore](https://www.glencore.com/media-and-insights/news/glencore-partners-with-us-exim-bank-to-build-strategic-minerals-reserve-fund)와 [Mercuria](https://mercuria.com/mercuria-commits-500-million-to-vaultco-u-s-critical-mineral-stockpile-in-partnership-with-the-u-s-export-import-bank/) 각각 VaultCo **5억 달러 약정**. [EXIM](https://www.exim.gov/news/fact-sheet/project-vault) 기존 최대 100억 달러 융자 승인 참조 | 하나의 전략비축 프로그램 사건군 아래 기업별 약정 2개를 별도 경제행위로 보존. 자금 인출·광물 실제 납입·9월 신규 EXIM 대출 승인 아님. 관련 행 709·851·852 지원 연결. Nth–Glencore 텀시트는 별개 |
| `WK26-VOL02-013` / 1200 | [미 하원 H.R.9340 9/16 417:3 통과](https://energycommerce.house.gov/posts/ratepayer-protection-act-passes-house-with-strong-bipartisan-support) | 법안 하원 통과는 확인; 연방법 발효·주별 100MW 데이터센터 전력요금 확정은 아님 |
| `SRC26-20260923_132732-0223` / 425 | [미 PHMSA DOT Form 5800.1 리튬전지 열폭주·UAS 정보수집 개정안 의견수렴](https://www.federalregister.gov/documents/2026/09/21/2026-19276/hazardous-materials-information-collection-activities) | 9/21 제안·12/21 의견 마감. OMB 승인 및 개정 서식 발효 전이며 기존 규제 의무는 별개 |

### Source ID는 보존하고 경제행위는 분리

- 로드맵: 대표 1277 + 지원 226·302 → 사건군 하나.
- Nth Cycle–Glencore: 대표 1280 + 지원 349 → 구속력 텀시트 한 건. 기사만으로 확정 오프테이크 2건을 만들지 않음.
- VaultCo: 대표 700 + 지원 709·851·852 → 동일 정책·사업군 아래 Glencore와 Mercuria의 **서로 다른 5억 달러 약정**을 각각 하위 경제행위로 기록. 기존 2월 EXIM 최대 100억 달러 승인 사건과도 구별.

## WATCH 3개 및 제외 2개

| Source ID / 행 | 판정 | 원발행 근거와 보존 조건 |
|---|---|---|
| `SRC26-20260923_132732-0221` / 423 | WATCH | [OSHA Federal Register](https://www.federalregister.gov/documents/2026/09/21/2026-19268/tuv-sud-america-inc-application-for-expansion-of-recognition): TÜV SÜD의 UL2580·UL2743 시험기관 범위 확장에 대한 **예비적 긍정 판단**. 최종 NRTL 승인 아님 |
| `R27_DISC_004` / 1299 | WATCH | [SEC Electra–WMC](https://www.sec.gov/Archives/edgar/data/1907184/000117184326006595/exh_991.htm): 5년 **비구속적 텀시트**. 코발트 정제소 자금 조달·독점 마케팅 최종 계약 미확인 |
| `WK26-VOL04-014` / 1236 | WATCH·보호지표 | [산업부 10/1 발표](https://www.motir.go.kr/kor/article/ATCL3f49a5a8c/172254/view): 9월 한국 배터리 수출 **7억 2,000만 달러, 전년 대비 +14%**. 산업 지표로 유지; 독립 기업 계약 사건으로 오인 금지 |
| `SRC26-20260926_120143-0357` / 855 | OUT OF SCOPE | [EC 원문](https://commission.europa.eu/news-and-media/news/train-trainers-programme-successfully-delivered-its-first-edition-2026-09-25_en): 해외 정보조작 대응 공무원 훈련 보도. 배터리·ESS 행위 없음 |
| `SRC26-20260928_160143-0267` / 1133 | OUT OF SCOPE | 위와 **동일 원문**의 두 번째 수집 Source ID. ID 삭제 없이 별도 제외 근거와 동일 사건 연계 보존 |

## 검증과 미완료 조건

1. `stage_artifact_contract_check.py A` 결과 **PASS**: Strict 총 30개, 스키마 누락 0개.
2. `stage_lineage_contract_check.py stage_a` 결과 **PASS_STAGE_A_SCHEMA_CONTRACT**.
3. 독립 QC `verify_stage_a_checkpoint_19_20261101.py` 결과 **INDEPENDENT_QC_PASS**: 1,330개 Source ID·원문 제목·원본 URL·행 순서 보존, 기존 정식 판정 105개 불변, 변경 21행 정확 일치, 지원·WATCH·제외 분기 및 사건군/기업별 경제행위 연결, 새 Strict 10개 모두 Stage B 미허가 확인.
4. 두 네이티브 검사의 통과는 **결정된 126건의 형식·계보 유효성**을 뜻하며, 전체 1,330건 심사 완료나 Stage B 진입 허가는 아니다. 남은 **1,204건**에 원문 사건별 판단·중복·처분을 끝낸 후 글로벌 HOLD 해제 및 다음 단계 네이티브 검사를 재평가해야 한다.

### 재현

CP19 ZIP의 기준 JSON을 원본 CP18 및 잠금 Full1676과 함께 놓고 다음 명령을 실행한다. 두 기준 파일의 SHA256이 위 값과 같지 않으면 빌더·검증기는 즉시 중단한다.

```bash
python build_stage_a_checkpoint_19_20261101.py --base STAGE_A_CP18_FORMAL_20261101.json --full /tmp/sbtl-stage-a-native-20261101/data/cards.full.json --output STAGE_A_CP19_FORMAL_20261101.json --receipt STAGE_A_CP19_RECEIPT_20261101.json
python verify_stage_a_checkpoint_19_20261101.py --base STAGE_A_CP18_FORMAL_20261101.json --full /tmp/sbtl-stage-a-native-20261101/data/cards.full.json --artifact STAGE_A_CP19_FORMAL_20261101.json --receipt STAGE_A_CP19_RECEIPT_20261101.json --native-dir /tmp/sbtl-stage-a-native-20261101 --out STAGE_A_CP19_INDEPENDENT_QC_20261101.json
```

**다음 병목:** 1,204개 미완료 Source ID에 대한 공통 사건군 판정 및 최초 발행자 단계 확인. 자동 분류 점수·기사 건수를 카드 수로 치환하지 않는다.
