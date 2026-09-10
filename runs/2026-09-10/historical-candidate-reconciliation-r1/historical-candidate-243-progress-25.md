# SBTL Historical Candidate 243 — Source-Materialization Progress

**Status: PARTIAL — 25 / 243 materialized**

- Historical derivation: `264 open - 18 later-promoted = 246 - 3 exact canonical = 243`
- Baseline at review: main `e19f6c1...` / canonical **1,599**
- First 25 disposition: **PROMOTE 6 / KEEP 7 / WATCH 5 / CLOSE 7**
- Remaining source-materialization: **218**
- These counts are **not** the final 243-universe totals.

## PROMOTE — 6
- **U0593 — Minnesota PUC mandates Xcel VPP + flexible-interconnection pilots** — Minnesota PUC official newsletter confirms July 30 IDP decision requiring Xcel to file a VPP pilot and static flexible-interconnection pilot in 2027. Regulator decision is concrete and current canonical hit was not found.
- **U1810 — 일본 power-bank 제3자 PSE 안전검사 의무화** — 8/31 METI 심의에서 제3자 적합성검사 의무화, ◇PSE 전환, 2027년 3월 시행 목표가 구체화돼 historical candidate의 reopen condition이 실제 충족됐다.
- **U1012 — NSW Data Centre Policy Framework** — NSW가 8/17 공식 framework를 발표했고 추가 energy/water infrastructure cost, consumer net-cost principle, 75-day assessment path 등 operative planning/power obligations가 확인됐다.
- **U0793 — Italy 2028 Capacity Market battery rating geography** — MASE decree 259/2026이 8/6 2028 Capacity Market discipline을 승인했고, Gazzetta/Terna 자료에서 2028 rules와 BESS derating methodology가 확인된다. market-design state change가 source-bound됐다.
- **U0331 — EPEC Lower Wonga 281MW/843MWh grid-connection EPC contract** — EPEC가 275/33kV substation·275kV line 설계~commissioning을 맡는 HV connection package를 수주했고, 843MWh BESS 프로젝트는 실제 construction 단계다. current canonical hit도 발견되지 않았다.
- **U0773 — Boliden Laver mining concession appeals rejected** — 스웨덴 정부가 8/12 두 appeal을 기각해 mining concession을 유지했고 다음 단계 environmental permit로 이동했다. permitting probability가 명확히 바뀐 critical-minerals event다.

## KEEP_CANDIDATE — 7
- **U1503 — Romania battery incentive schemes** — repair: Romanian government/energy ministry official scheme documents, budget and eligibility
- **U0179 — 한국 핵심광물·소부장 탈중 정책** — repair: 산업부 공식 보도자료/계획 문서와 구체 지원·조달·투자 수단 확인
- **U0966 — 헝가리 배터리 재활용 부지지정 법 개정** — repair: Hungarian Gazette exact law text, enactment/effective date and scope
- **U1929 — Brazil battery supply-chain / domestic-content storage auction** — repair: official auction rules 기준으로 event fingerprint를 `National Storage domestic-manufacturing requirement`로 재작성 후 strict gate 재실행
- **U0818 — H1 2026 global ESS cell shipment ranking 467.84GWh** — repair: current canonical exact dataset/follow-up screen 완료 후 strict data-anchor gate
- **U2046 — China flow-battery 2026 additions >1.4GW forecast** — repair: bluebook/association source에서 1.4GW metric·technology scope 직접 확인
- **U0439 — Chinese overseas storage projects exceed PV / 96% BRI / Pakistan 4.6GWh** — repair: project-count dataset compiler와 96% BRI denominator/source methodology 확인 후 event split

## WATCH — 5
- **U0979 — 레ク사스 ES 신형, GS Yuasa/Blue Energy EHW4GA 채택** — reopen: 추가 Toyota/Lexus 차종 채택, 공급량·매출 기여 또는 대규모 양산 확대
- **U0807 — CATL 2.4억위안 ESS integration equipment order** — reopen: named supplier/customer scope, delivery 규모 또는 반복 대형 주문
- **U2006 — Austria storage offensive / 2027 subsidy redesign** — reopen: 2027 EAG funding final rules, dedicated storage/EMS program budget 또는 시행 고시
- **U0890 — Port of Southampton BESS planning application** — reopen: planning approval, FID/NTP, EPC award 또는 construction start
- **U0888 — Ireland EV Flex — ESB Networks + Ohme** — reopen: pilot 규모·flex MW·참여/shift 결과, permanent tariff/program adoption

## CLOSE — 7
- **U0423 — Corvus Energy 40MWh battery contract for BC Ferries** — current canonical에 동일 40MWh BC Ferries contract가 이미 존재한다.
- **U1509 — Clearstone 150MW Axminster BESS appeal rejected** — planning refusal이 appeal에서 유지된 terminal negative project state다. 독립 카드 가치가 부족해 candidate로 계속 보유하지 않는다.
- **U1941 — Ontario electricity/critical-mineral export cutoff threat** — 정치적 retaliatory threat로 실제 operative export restriction이 시행되지 않았고 현 시점 fresh battery/mineral action으로 이어지지 않았다.
- **U1797 — US-Canada trade talks suspended / retaliatory tariffs** — 광범위 macro-trade event이며 battery/ESS-specific independently cardable anchor가 없다.
- **U1103 — California community solar / balcony solar / VPP bills** — 동일 California VPP policy event가 Sep3 E0374 composite repair queue에 이미 살아 있다. 중복 active membership을 금지하고 U1103은 그 policy child의 historical source lineage로 흡수한다.
- **U0705 — 정부 반도체·이차전지·바이오 규제완화 4조원대 투자** — 다부처·다산업 roundup 성격으로 battery-specific clean event fingerprint가 없고 개별 프로젝트로 분해되지 않았다.
- **U0530 — Octopus Australia Fulham 64MW/128MWh BESS** — Fulham은 2025-04 이미 financial close와 construction start를 완료했고, 2026-08 보도는 기존 construction project의 재조명/optimization service 맥락이다. fresh project-stage event로 보기 어렵다.
