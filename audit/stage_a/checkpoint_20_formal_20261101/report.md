# Stage A 체크포인트 #20 — 원발행 문서 기반 27개 Source ID 정식 판정

**판정·독립 검증 기준일:** 2026-11-01 (UTC)  
**기준 파일:** CP19 (1,330행), SHA256 `bf30369c00bd528b4ab32c628a388b48a56471ac5e8f34fd22631bcb8eaead7d`  
**동결 Full:** 1,676장, SHA256 `d22f0d4e39e035b9537b3e9abdf48abe6b7eb80f7e477e87aff1284f9e27e0d9`  
**CP20 1,330행 산출물:** SHA256 `b0b06dae8fd3ac19950772479ba087e0c8b661f3388899b9bbd370f789cd21c1`

## 결론과 경계

**Stage A 전체 판정은 HOLD**다. CP20에서는 Source ID 27개를 정식 판정하여 **새 Strict 경제사건 대표 출처 12개**, 동일 사건 보강·중복 출처 **14개**, 이미 Full에 있던 사건의 보강 증거 **1개**로 처분했다. 기존 126개 정식 판정은 그대로 유지했다. 신규 확정 기사·최종 카드 편입은 **0개**다. Stage B 검사/진입, `main`·Full·Related·프로덕션 변경은 수행하지 않았다.

| 항목 | CP19 | CP20 | 변화 |
|---|---:|---:|---:|
| 보존 Source ID | 1,330 | **1,330** | 0 |
| 누적 정식 0.1P 판정 | 126 | **153** | +27 |
| 정식 미완료 | 1,204 | **1,177** | −27 |
| 누적 Strict 사건 대표 | 30 | **42** | +12 |
| 후보 검토 풀 | 563 | **538** | −25 |
| WATCH 풀 | 660 | **658** | −2 |
| Reject/Support 풀 | 47 | **61** | +14 |
| 기존 Full 사건 보강 | 30 | **31** | +1 |

## 독립 Strict 경제사건 대표 12개

| 행 / Source ID | 사건과 원발행 근거 | 정식 경제행위 경계 |
|---|---|---|
| **1263** / `WK26-VOL03-013` | [NIO IR: NIO–Geely](https://ir.nio.com/news-releases/news-release-details/nio-announces-definitive-agreements-strategic-transaction-geely), 9/27 확정적 거래계약 서명 | Geely의 자산·현금 출자와 NIO의 별도 지분 참여, 조건부 후속 투자 등 **거래계약의 서로 다른 하위 경제행위** 보존. 거래 종결·지분 이전·현금 집행 완료 아님. 같은 사건 출처 869·870·1082 지원. |
| **683** / `SRC26-20260926_120143-0185` | [Global Lithium ASX 공시](https://newswire.iguana2.com/2fee0049d633f441/announcements/gl1.asx/6A1344840/GL1_Global_Lithium_enters_into_binding_SID_with_Titan.pdf), 9/22 Titan과 총 **A$3억3,300만** 인수 관련 구속력 있는 Scheme Implementation Deed | 예정 인수·기업가치·최대 A$1억2,000만 지원가능 시설은 각각 분리. 주주·법원·규제 승인 전으로 인수 종결·전액 인출 아님. 기사 337·338·342·343 지원. |
| **497** / `SRC26-20260923_132732-0295` | [Gotion](https://www.gotion.com.cn/newsInfo/979), 사우디 3개 ESS 부지 대상 **6GWh 주문** 발표 | 기업 수주 공표 사건; 6GWh 납품·설치·상업운전 완료 아님. 기존 사우디의 별개 설비/위탁 사건과 중복 합산 금지. |
| **728** / `SRC26-20260926_120143-0230` | [Sungrow](https://www.sungrowpower.com/eu/en/delta-karppio-akkuone), 핀란드 Kärppiö + AKKU One, 각 125MW/300MWh에 대한 **총 600MWh 공급 실행분** | 기존 **1GWh 기본계약의 이행 배분**이지 새 1GWh 추가 계약 아님. 2027년 예상 운영은 미래. 기사 1068 지원. |
| **367** / `SRC26-20260923_132732-0165` | [Delta Capacity](https://www.deltacapacity.com/post/covenergo-and-delta-capacity-partner-on-125-mw---300-mwh-akku-one-bess-project-in-lapinlahti-finlan), 핀란드 AKKU One **125MW/300MWh 착공** | 공급 실행(행728)과 **서로 다른 사업 단계 사건**이되 같은 설비 300MWh가 위 600MWh에 포함되므로 총량 중복 합산 금지. 상업운전 예정 시점은 2027년 4분기. |
| **865** / `SRC26-20260926_120143-0367` | [CATL–Kuehne+Nagel](https://www.catl.com/en/news/7012.html), 9/18 물류 전기화·배터리 스와핑 협력 MoU | MoU 체결만 확인. 설비 발주·납품·배치 아님. 동일 원발행 URL 기사 행1156 지원. |
| **165** / `SRC26-20260920_142928-0165` | [CATL–DHL](https://www.catl.com/en/news/6999.html), 9/14 유럽 녹색물류 회랑 협력 MoU | 2024년 세계적 협업과 구분되는 유럽 세부 MoU. 실증·차량/ESS 신규 설치 실적 미확인. Kuehne+Nagel 사건과도 상대방·행위가 다름. |
| **1167** / `R17_DISC_005` | [Canadian Solar e-STORAGE–OX2](https://investors.canadiansolar.com/news-releases/news-release-details/e-storage-supply-and-commission-100-mw200-mwh-battery-storage), 호주 Muswellbrook **100MW/200MWh 공급·시운전 계약** 및 20년 서비스 | 계약 체결 사건. 2027년 예정 출하, 2028년 예정 COD와 구분. |
| **97** / `SRC26-20260920_142928-0097` | [Jupiter Power](https://jupiterpower.io/jupiter-power-secures-1-4-billion-in-project-financing-for-ten-utility-scale-battery-energy-storage-projects/), ESS 10개 프로젝트 금융 **미화 14억 달러**, 4개 금융종결 | 금융 종결은 2026년 **4–7월**에 이뤄졌고 9/16에 사후 발표. 기업 발표 프로젝트 총량 **1,500MW/3,600MWh**로 정정, 기사 제목의 3.8GWh 불채택. 보조금·상업운전 개시로 오인 금지. |
| **146** / `SRC26-20260920_142928-0146` | [EVE Energy](https://www.evebattery.com/en/news-1900), IAA 관련 복수 업체와 상용차 배터리 **30GWh 초과 전략적 협력 주문** 발표 | 기업이 총량을 주장하는 전략적 협력 단계. 상대방별 확정 구매주문·대금 수령·납품 물량으로 치환 불가. 9/29 원발행 추후 발표를 추가 신규 계약으로 세지 않음. |
| **1259** / `WK26-VOL03-009` | [Volkswagen/PowerCo–Gotion](https://www.volkswagen-group.com/en/press-releases/volkswagen-group-powerco-and-gotion-deepen-strategic-partnership-20710), 스페인·슬로바키아·모로코 **3개 합작사 계획** 및 별도 5.3% Gotion 보유지분 매각 계약 | 프레임워크/기대 지분비율/2030년까지의 계획 투자와 **5.3% 지분 매각 조건부 계약**을 별도 하위 행위로 보존. 법인 설립·실제 투자 집행·공장 가동·지분 매각 종결로 오인 금지. |
| **772** / `SRC26-20260926_120143-0274` | [Geely Auto](https://www.geelyautogroup.com/en/media/202609231/), 9/23 AI 초고속 충전기 **2,250kW** 및 수명 개선 **20%** 발표 | 발표 사실만 확인된 **기업 자체 성능 주장**. 독립 실증·보급 규모·시판 배치나 검증된 셀 수명 개선 수치 아님. 지원 행498·741·784·812·881을 사건 하나로 묶음. |

## 동일 사건 출처 14개 및 기존 Full 보강 1개

| 사건군 | 보강 Source ID의 행 | 처분 |
|---|---|---|
| NIO–Geely | 869, 870, 1082 | 대표 1263에 지원 연결, 카드 3개 증가 금지 |
| Global Lithium–Titan | 337, 338, 342, 343 | 대표 683에 지원 연결, 인수 미종결 |
| Sungrow–Delta | 1068 | 대표 728에 지원 연결 |
| CATL–Kuehne+Nagel | 1156 | 대표 865의 같은 회사 발표, 중복 카드 금지 |
| Geely 충전 기술 | 498, 741, 784, 812, 881 | 대표 772의 기업 자체 기술 주장에 병합 |
| [CATL 9/6 동박 협약](https://www.catl.com/en/news/6993.html) | **1184** / `WK26-VOL01-018` | 기왕 Full 카드 `2026-09-06_CN_03`와 같은 경제사건 보강. 신규 Strict·카드 **0개** |

## 검증·재현·HOLD 조건

- **네이티브 산출물 계약 검사 PASS** — Strict 42건, 누락 0건.
- **네이티브 계보 계약 검사 PASS_STAGE_A_SCHEMA_CONTRACT**.
- **독립 QC PASS** — 정확히 27개 행만 추가 처분했음을 검사. 원본 Source ID 1,330개, 행 순서, 제목, 기사 URL, 기존 정식 126건, 기존 Strict 30건을 해시·내용 기반으로 대조했고 사건 단계의 주요 오독 방지 조건을 검증했다.
- CP20 판정 원장, 판정 영수증, 독립 QC, 빌더, 검증기를 압축본에 보존했다. 판정 영수증 자체는 검증 전 생성되므로 `PENDING_NATIVE_AND_INDEPENDENT_QC`로 기록되며, 이후 실제 통과 사실은 **독립 QC 파일의 `independent_qc: PASS`**가 증명한다.
- 서명 계약과 거래 종결, MoU와 납품, 공급계약과 착공, 프로젝트 용량과 독립된 증설 규모, 기업의 목표치와 검증된 성능을 반드시 구분한다.
- **Stage B는 실행하지 않았다.** 남은 1,177개 Source ID에 대해 같은 수준의 사건별 판정·처분이 필요하다. 전체 Stage A HOLD 해제·Stage B 진입은 이후 별도 검토한다.

### 재현 명령

동일한 CP19 원장과 동결 Full JSON을 확보한 뒤 해시 일치 시에만 실행할 수 있다.

```bash
python build_stage_a_checkpoint_20_20261101.py --base STAGE_A_CP19_FORMAL_20261101.json --full /tmp/sbtl-stage-a-native-20261101/data/cards.full.json --output STAGE_A_CP20_FORMAL_20261101.json --receipt STAGE_A_CP20_RECEIPT_20261101.json
python verify_stage_a_checkpoint_20_20261101.py --base STAGE_A_CP19_FORMAL_20261101.json --full /tmp/sbtl-stage-a-native-20261101/data/cards.full.json --artifact STAGE_A_CP20_FORMAL_20261101.json --receipt STAGE_A_CP20_RECEIPT_20261101.json --native-dir /tmp/sbtl-stage-a-native-20261101 --out STAGE_A_CP20_INDEPENDENT_QC_20261101.json
```

**다음 병목:** 1,177개 Source ID의 사건군별 원발행 대조, 고유 경제행위 추출, 지원/제외/WATCH의 완료 처분. 산업적 중요도를 메타데이터 점수만으로 결정하거나 기사 수만큼 카드를 생성하지 않는다.
