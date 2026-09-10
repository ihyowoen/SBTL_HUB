# SBTL 9/3 retained candidate 39 — Corrected 0.1P carryforward re-review v3

**This supersedes the earlier v2 artifact that incorrectly promoted four items.**

- Source authority: recovered GitHub Actions R7 Prompt 0.1P artifact (`run 34013275047`, head `e4480035...`)
- Baseline at rereview: main `e19f6c1...`, canonical **1,599**, blob `cc5bc78...`
- Original accounting: **52 candidate → 13 original promotion → 39 retained**
- Corrected current result: **PROMOTE 0 / KEEP 2 / WATCH 16 / CLOSE 21**
- Stage-B eligible from this retained cohort: **0**
- Unassigned: **0**

## KEEP_CANDIDATE — 2
- **E0002 — Sigenergy H1 residential ESS 글로벌 1위·14% 점유 주장**
  - story IDs: `US_2026-09-03_C02`
  - repair: S&P Global tracker 직접 문구/표 또는 독립 market-share dataset으로 #1·14% 확인
- **E0374 — California VPP 법안 + Uplight 투자**
  - story IDs: `TF_0063`
  - repair: SB905/SB913 legislative event와 Octopus/Uplight investment event를 별도 fingerprint로 분리·source-bind

## DOWNGRADE_WATCH — 16
- **E0024 — PowerBank Ontario BESS development agreement** — IESO LT2(c-2) award, permit, NTP 또는 EPC 전환
- **E0032 — 채비–코빌리지 오프그리드 solar+ESS 충전소** — SPC/FID, ESS·충전설비 발주, 착공 또는 운영 개시
- **E0074 — LGES–현대차 인니 JV 공장 근로자 사망 의혹** — 경찰/회사/규제기관 공식 확인, shutdown·시정명령·안전 프로세스 변경
- **E0084 — KT cloud–LS Electric AI DC 전력 인프라 협력** — named AIDC 공급계약, 설비발주, 프로젝트 금액/용량 또는 commissioning
- **E0098 — 한·호주 경제계 핵심광물·AI·방산 협력** — named critical-mineral offtake/JV, 금융지원, 투자 또는 프로젝트 계약
- **E0149 — 산업부 배터리 삼각벨트 본격 가동** — 예산 확정, 사업선정, 계약 또는 착공
- **E0154 — 일본 V2X로 고층아파트 엘리베이터 방재 실증** — 상용 도입, 다수 사이트 보급, 조달/보조사업 또는 계약
- **E0162 — 일본 FY2027 예산요구 — 계통용 ESS·수소 증액** — FY2027 최종예산 성립, 프로그램 공고·배정 또는 award
- **E0220 — 인도네시아 중국계 니켈 제련소 감산 검토** — named plant 실제 production/operating-rate cut, 공식 가이던스 또는 quota 변화
- **E0231 — SHERLOCK black-mass 표준화 프로젝트** — DIN/ISO technical specification/standard 제출·채택 또는 시장접근 규칙 반영
- **E0249 — Altilium 영국 EV 배터리 재활용 특허** — EcoCathode 상업가동, named license/customer 또는 처리량 실적
- **E0264 — Asahi Kasei 실리콘 음극 lithium pre-doping** — named customer PoC/qualification, licensing, pilot 또는 양산 적용
- **E0290 — Geely Galaxy NP3.0 열폭주 안전 실차 테스트** — 독립 인증·시험, 양산차 field safety data 또는 대규모 상용 적용
- **E0299 — GWh급 sodium-ion ESS 프로젝트备案** — Mojiang project construction/NTP/commissioning 또는 same-project equipment/order execution
- **E0300 — BYD 후베이 전해액 프로젝트 가동 임박** — trial production 또는 commercial operation 실제 확인
- **E0306 — Capchem 홍콩 재상장 신청** — HKEX hearing 통과, pricing/listing 또는 확정 조달금액·use-of-proceeds

## CLOSE — 21
- **E0003 — Corvus Energy–BYD marine LFP battery** — Blue Whale NxtGen Power의 원 발표는 8월 27일이고 9월 2일은 later coverage다. fresh incremental event가 없다.
- **E0022 — Iowa startup 태양광→수소 효율 10%+ 실증** — solar→hydrogen 10%+ 결과는 precommercial lab result이며 SBTL battery/ESS core lane에서도 간접적이다.
- **E0099 — 포스코 장인화 호주 핵심광물 자원외교** — POSCO 제안은 E0098 한–호 협력 프로그램을 회사 관점에서 보강한 strategic proposal이며 adopted procurement/investment/supply commitment가 없다. parent watch만 남긴다.
- **E0189 — Lynas Rare Earths 과거 인수협상 공개** — Lynas는 연초 takeover talks가 있었음을 확인했지만 live transaction/current negotiation이 없다.
- **E0207 — 중국 연구진 600Wh/kg+ 리튬메탈 셀** — 600Wh/kg+ lithium-metal은 lab research이고 independent/customer/commercial validation이 없다.
- **E0226 — TI grid-scale battery cell diagnostics** — TI BQ79826Z-Q1은 2026년 6월 launch된 제품이며 9월 기사는 stale technical re-coverage다.
- **E0230 — 스페인·폴란드 BESS revenue 변화** — Spain/Poland revenue 기사는 여러 시장의 월별 결과를 묶은 aggregate context로 독립 event fingerprint가 약하다.
- **E0236 — 인도 solar module 233GW 과잉설비 전망** — India solar-module 233GW overcapacity는 solar manufacturing signal로 battery/ESS core lane과 직접성이 부족하다.
- **E0269 — 중국 전선업체 ESS·AI 관련 17.8억위안 월수주** — 17.8억위안 월수주는 cable-company aggregate order roundup이고 battery/ESS-specific denominator/named execution anchor가 없다.
- **E0270 — EVE Energy 대규모 투자·현금흐름/매출 분석** — EVE H1는 8월 19~20일 공식발표된 실적이며 9월 3일 기사는 stale re-analysis다.
- **E0278 — CATL 출신 인력의 대규모 배터리 투자/수주 경쟁** — CATL alumni/Dangzhuo 건은 historical/current context를 섞은 profile/expansion narrative로 clean fresh event가 아니다.
- **E0280 — Desay Battery ESS 매출 급증·중동 진출** — Desay H1는 8월 19일 전후 공개된 실적의 9월 재분석으로 fresh event가 아니다.
- **E0283 — 장시 배터리 공장 화재** — Far East Battery 화재는 후속 공식 확인상 인명피해 없이 일부 작업장 손상, 생산·경영 정상으로 산업적 impact가 낮다.
- **E0286 — Gotion H1 순익 +278% 관련 실적** — Gotion +278% headline은 비경상손익 영향이 크고 storage-system signal을 과장한다. exact R7 bounded review도 strict promotion을 거부했다.
- **E0303 — CALB H1·글로벌 점유율 및 177Ah 이슈** — CALB 한 기사에 H1 ranking과 editorial 177Ah safety concern이 혼합돼 clean event가 아니며, 현 시점 재분리해도 둘 다 fresh strict event가 아니다.
- **E0313 — 상업용 ESS 매출 -94%·첫 반기 적자 기업** — single-company H1 storage revenue/loss signal은 54점 ceiling이고 후속 fresh event 없이 현재까지 carry할 근거가 약하다.
- **E0352 — S-Oil–KTNF–GST AI DC immersion cooling 실증** — S-Oil immersion-cooling test는 기존 PoC/partnership path의 연장으로 새로운 independently material battery/ESS event가 아니다.
- **E0353 — 한국 RE100 국내 재생에너지 사용률 13%** — RE100 국내 재생에너지 사용률 데이터는 grid context이나 battery/ESS-specific discrete event가 아니다.
- **E0403 — 미국 heatwave·대형 grid blackout risk** — heatwave/grid-reliability 건은 시간한정 reliability context로, 대형 blackout/ESS-specific execution event가 확인되지 않았다.
- **E0411 — 가온전선 AI 데이터센터 저마찰 케이블** — Gaon Cable AI-DC low-friction cable은 adjacent power infrastructure이며 battery/ESS/grid-storage impact가 독립 카드 수준에 못 미친다.
- **E0414 — 한국–호주 critical minerals 협력 확대** — 9월 1일 pre-meeting preview는 9월 2일 실제 한–호 committee/joint statement E0098에 의해 superseded됐다.
