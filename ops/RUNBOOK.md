# SBTL_HUB 트래커 운영 RUNBOOK v2

작성 2026-07-17 (최종 개정 2026-07-22). 근거: 2026-06-25 ~ 07-22 세션의 실제 사고 12건 부검.
**운영 체제: 일일 전수(RD) — 매일 전 항목 실검색 + 매일 배포. 자동 스케줄 태스크 실행 전제(§4).**
원칙: **규칙을 문서가 아니라 데이터 구조와 게이트로 옮긴다.** 사람(운영자·모델)의 기억과 성실성에 의존하는 지점은 반드시 뚫린다 — 이번 세션에서 전부 실증됨.

---

## 0. 실패 부검 요약 (설계 근거)

| ID | 사고 | 근본 원인 | 대응 설계 |
|----|------|----------|----------|
| F1 | NA-024 Commerce만 보고 ITC 무시 정정 | 단일 소스 결론 변경 | G1 2-소스 규칙 |
| F2 | 기존 dt/detail의 정답을 안 읽고 t/d 덮어씀 | 수정 전 전문 미독 | G1 전문 출력 강제 |
| F3 | PR#163 리뷰 미확인 머지 | 배포 게이트 기억 의존 | G4 시퀀스 기계화 |
| F4 | IEEPA 낡은 인용 재수정 | 교차 사실 최신성 | refs + watch 큐 |
| F5 | D-day 36건 산문 baked 부패 | 파생값을 데이터에 저장 | milestones 구조화·산문 D-day 금지 |
| F6 | EU-018 정정 미전파·CN-014 참조 오기 | 관계가 자유 텍스트 | refs[] 구조 필드 |
| F7 | "신규 0건" 오판 (ELV·PFAS·PPWR 누락) | 검색축이 기존 항목 종속 | 커버리지 맵 (coverage.json) |
| F8 | lastChecked 기계 bump 검증 위장 | 검증 사실 기록 부재 | 런 원장 (runs/) + 대조 |
| F9 | "채택 대기" flag 방치 | pending이 산문에 묻힘 | watch[] 큐 필드 |
| F10 | 제안이 DONE/ACTIVE | status 의미 암묵 | statusReason + 규칙표 |
| F11 | 벌칙·수치 무근거 기재 | 원문 미확인 | G1 primary-doc 요구 |
| F12 | 대화가 여러 날 걸치며 D-day가 5일 밀림(스탬프≠실제일) | 세션 실제 날짜 미확인 | §6.1 실제 날짜 확인 → RD-0 재계산 |
| F13 | ops/가 데이터보다 먼저 착지 → coverage가 미존재 ID를 covered로 표시(gap 은폐) | 두 계층 착지 순서 미규정 | validate2 검사 #9 + 동시 착지 규칙(G2) |

---

## 1. 데이터 모델 v2 (tracker_data.json 스키마 확장)

기존 필드 유지(호환) + 신규 필드. 이행은 §5 마이그레이션 순서로.

```
item {
  id, r, s, t, d, tip, detail          // 기존 유지
  canonicalId?, supersededBy?          // 기존 유지

  statusReason: string                 // 1줄. "왜 이 status인가" (F10)
  milestones: [                        // D-day의 유일한 원천 (F5)
    { date: "YYYY-MM-DD" | "YYYY-MM" | "YYYY",
      label: string,                   // "Section 122 만료"
      kind: "effective"|"deadline"|"expiry"|"hearing"|"decision"|"application",
      verified: "YYYY-MM-DD" }         // 이 날짜를 마지막으로 소스 확인한 날
  ]
  refs: ["CN-014", ...]                // 구조화 교차참조 (F6)
  watch: [                             // pending 액션 큐 (F9, F4)
    { what: string,                    // "ITC 최종결과 확인"
      due: "YYYY-MM-DD" | null,        // 확인 기한 (null=상시)
      status: "open"|"done"|"dropped",
      added: "YYYY-MM-DD", closed?: "YYYY-MM-DD", note?: string }
  ]
  verify: {                            // lastChecked 대체 (F8)
    date: "YYYY-MM-DD",
    method: "search"|"primary-doc"|"cross-ref"|"mechanical",  // mechanical은 검증으로 안 침
    runId: "2026-07-17-R1"             // 런 원장 참조
  }
  dt: string                           // [이행기] milestones에서 빌드 스크립트가 자동 생성. 손편집 금지
}
```

**status 규칙 (명문화, F10):**
- ACTIVE = 발효·시행 중 / UPCOMING = enacted·미적용(적용일 확정 또는 절차상 확실)
- WATCH = 미제정 제안·전략·조사 중·referent 미확인
- DONE = 종료·확정·대체(orphan 아님). **제안·협의 중은 절대 DONE/ACTIVE 불가.**
- dedup: canonicalId(정본 지시) / supersededBy(대체됨). 정본 선택 기준 = 피참조 수 → 상세도.

**산문 규칙:** t/d/detail/tip 안에 (D-N)/(D+N) 표기 **금지**(validator ERROR). 날짜는 YYYY.MM.DD 절대표기만. 타 항목 언급 시 반드시 refs에도 등재.

---

## 2. 런 원장 (ops/runs/YYYY-MM-DD-<type>.json)

모든 run은 원장 1개를 남긴다. **verify.date 갱신은 원장에 근거가 있을 때만 유효** — "부분검증 금지"의 기계 강제.

```
run {
  runId: "2026-07-17-R1", date, type: "R0"|"R1"|"R2"|"R3",
  searches: [ { query, region|axis, itemsCovered: ["NA-003", ...],
                result: "no-change"|"change"|"new"|"empty-retry" } ],
  primaryDocs: [ { url|citation, itemsCovered: [...] } ],
  changes: [ { id, what } ], newItems: [ids], dedups: [...],
  watchProcessed: [ { id, what, outcome } ],
  coverageCells: ["chemicals/EU", ...],       // 이번에 돈 커버리지 셀
  pendingDecisions: [ ... ]                   // Claire 승인 대기
}
```

규칙:
- 검색 1회가 여러 항목을 커버하면 itemsCovered에 **명시적으로 열거**한다. 열거 안 된 항목의 verify 갱신 금지.
- 빈 검색 결과는 `empty-retry`로 기록하고 **각도를 바꿔 1회 이상 재시도**해야 "없음" 결론 가능 (F7 OJ 스캔 교훈).
- 기계적 편집(D-day·오타·참조 정정)은 changes에 남기되 verify는 `method: "mechanical"` — 검증으로 집계되지 않음.
- 전수 미완 시 `partial: true` + `partialReason` 기재. 미검증 항목의 verify는 **이전 검증일 그대로 유지**(최신일로 밀지 않음).

---

## 3. 커버리지 맵 (ops/coverage.json)

**신규 발굴의 단위는 "기존 항목의 주제"가 아니라 커버리지 셀이다** (F7의 구조적 해법).

- 축 12종 × 권역 6 = 72셀. 초판 기준 gap 32셀 — ELV·PFAS·PPWR이 전부 gap 셀에서 나왔음.
- 축: trade(통상·관세) / subsidy(보조금·세제) / product_std(제품표준·안전) / chemicals(화학물질) / recycle(재활용·순환) / supply_chain(공급망·자원안보) / transport(운송·물류·저장) / carbon(탄소·ESG) / packaging(포장) / waste_ship(폐기물 이동) / data_dpp(정보·여권) / energy_market(전력시장·ESS)
- 각 셀: { items[], status: covered|gap|na, lastSwept, sweepDay, queries[3~6] } — 쿼리는 셀에 **사전 정의**(현 항목과 무관하게), 언어 규칙 적용(CN=간체, JP=일본어)
- 셀 운영 규칙:
  - RD-3에서 요일 슬라이스별 로테이션(§4), **lastSwept 오래된 순 + gap 셀 우선**
  - 전 셀 주 1회 스윕 보장 (일요일에 미스윕 보충)
  - gap 셀에서 2회 연속 아무것도 안 나오면 status를 na(해당 규범 부재) 후보로 — Claire 승인 후 na 처리, 분기 1회 재확인
  - **items에 적는 ID는 tracker에 실재해야 함**(검사 #9 ERROR). 신규 항목을 셀에 넣을 땐 데이터 파일과 **같은 PR**로 착지 (F13)

---

## 4. 런 타입 + 게이트 — **일일 전수 체제 (RD)**

운영 결정(2026-07-17): **매일 전 항목 실검색 + 매일 배포.** 목표 = 누락 제로·오정보 제로·최신성. 부하 감수.
사람이 수동으로 굴릴 볼륨이 아님(아래) → **자동 스케줄 태스크로 실행** 전제. (스케줄: 매일 13:00 KST)

### 일일 부하 (실측 기반)
- 클러스터 검색 1회 ≈ 3항목 커버(원장 실측) → 115항목 1회 명중에 **≈38 클러스터 검색**
- + 신규발굴 셀 슬라이스 6~10 + 경계 표적 3~5 = **약 30~50 검색/일** (주간 환산 기존의 4~5배)
- 이 볼륨 때문에 "무변화" 유혹이 매일 옴 → **G2(원장 대조)가 매일 강제**되는 게 핵심 안전장치

### RD (일일 전수) 구성 — 매일 순서
| 단계 | 내용 |
|------|------|
| RD-0 롤오버 | **실제 날짜 확인**(§6.1) → milestones→dt 재생성(`ops/build_dt.mjs`) + 오늘 기준 D-day 재계산 |
| RD-1 경계 우선 | D≤10·D+≤7 항목 먼저 실검증(변화 확률 최고) + watch 큐 due 순 전수 처리 |
| RD-2 항목 전수 | 6권역 클러스터 검색으로 **전 항목이 당일 원장에 최소 1회 명중**. 미명중 잔존 = run 미완(G2가 차단) |
| RD-3 신규발굴 | 오늘의 **커버리지 슬라이스**(아래 7일 로테이션)만 신규 스캔 — 전 셀 매일은 과부하, 7일 완주 |
| RD-4 region_policy | tracker 당일 변화(신규·status·경계 진전·정정)를 **region_policy.json**에 전파: 권역별 headline·summary·watchpoints 재작성, `_meta.lastUpdated`·cycleNote 갱신. **두 파일 정합 필수** (§4a) |
| RD-5 게이트·배포 | G2→G3→present→G4. tracker + region_policy **2파일 동시** 배포. **무변화일도 verify 날짜 갱신분 커밋**(매일 배포 결정) |

**§4a region_policy 정합 규칙 (RD-4):** tracker와 region_policy는 항상 같은 상태를 반영해야 함(둘 다 public/data, 앱이 둘 다 렌더). 매 RD에서:
- 신규 항목 추가 → 해당 권역 summary에 1줄 편입 + headline 반영 여부 판단
- status 변경·경계 진전(D-day 임박/경과) → 해당 권역 watchpoints 갱신
- 정정 → 관련 권역 서술 수정
- `_meta.lastUpdated`는 tracker `meta.lastUpdated`와 **동일 날짜** 유지(불일치 시 G3 WARN — validator v2 검사 #8)
- 무변화일도 `_meta.lastUpdated`만 갱신(tracker와 동기)

### 7일 신규발굴 로테이션 (RD-3) — 72셀을 요일 슬라이스로
전 항목 재검증(RD-2)은 매일이지만, **신규 표면 발굴**은 셀이 많아 요일 분산. 각 셀 주 1회 스윕 보장.
| 요일 | 슬라이스 (축) |
|------|--------------|
| 월 | trade + subsidy (전 권역) |
| 화 | product_std + chemicals |
| 수 | recycle + waste_ship |
| 목 | supply_chain + data_dpp |
| 금 | carbon + energy_market |
| 토 | transport + packaging |
| 일 | gap 셀 전량 재확인 + na 후보 판정 + 지난주 미스윕 보충 |
- 급변 이벤트(관세 발효일 등)는 요일 무관 RD-1에서 당일 처리.
- lastSwept 7일 초과 셀이 생기면 일요일에 강제 보충.

### 배포 정책 (매일)
- **매일 PR — tracker_data.json + region_policy.json 2파일.** 변화 있으면 변경분, 무변화일은 두 파일 verify/lastUpdated 갱신 커밋("YYYY-MM-DD RD 무변화 확인").
- 무변화일 PR도 G4 전 시퀀스 준수(리뷰 확인 포함) — 자동화라도 게이트는 동일.
- 대용량 tracker(~400KB 한글)는 **웹UI 업로드 유지** — MCP 인라인은 전사 손상 위험. ops/ 텍스트 파일은 MCP 푸시 후 raw diff 검증 가능(2026-07-22 실증).
- **ops/ 변경이 신규 항목을 전제하면 데이터 파일과 같은 PR로 착지**(F13, 검사 #9).

### 자동화 실패 안전장치
- 스케줄 run이 G2/G3 FAIL이면 **배포 중단·원장에 FAIL 기록·운영자 알림**. 절대 FAIL 상태로 머지 금지.
- 검색 rate limit·소스 접근 실패로 RD-2 미완이면 그날은 **부분 run으로 명시 기록**(verify 갱신은 명중분만) — 다음날 미명중 항목 우선.
- 신규 항목·status 변경·병합·na 처리는 **자동 반영 금지, 승인 큐로**(pendingDecisions). 자율 반영은 기계적 정정·무변화 verify·D-day 롤오버까지만.

### 게이트 (체크리스트가 아니라 스크립트로 강제)

**G1 편집 게이트 — 기존 항목 수정 전:**
1. 해당 항목 **전 필드 출력 후** 수정 (F2). 스크립트 `ops/edit.py <id>`가 전문 출력 → 수정 diff 제시.
2. status·결론(t/d의 사실 방향) 변경은 **독립 소스 2개 또는 원문(primary-doc) 1개** 필요. 원장에 기재.
3. 다단계 절차(AD/CVD, 입법)는 **전 단계 확인** 후에만 결론 기재 — Commerce+ITC, EP+이사회+OJ (F1).
4. 수치·벌칙·조문은 원문 확인 없이는 기재 금지 — 미확인 시 watch-point로만 (F11).

**G2 검증 게이트 — run 종료 전:**
- verify 갱신분 ↔ 원장 itemsCovered 대조 (스크립트, validate2 검사 #6 = ERROR).
- watch 큐에 due 경과 open이 있으면 run 종료 불가 — 처리하거나 due 연기(사유 기재). **validate2 검사 #5가 ERROR로 차단**(경고 아님).
- coverage.json이 참조하는 항목 ID는 tracker에 실재해야 함 — **검사 #9가 ERROR**. ops/와 데이터 파일은 **같은 PR로 동시 착지**시킬 것(분리 착지 시 신규 항목 셀이 covered로 잘못 표시돼 gap을 가림, F13).

**G3 정합 게이트 — validator v1 + v2 (커밋 전 필수):**
- v1(scripts/validate.mjs) 기존 검사 + v2(ops/validate2.mjs) 검사 9종: 산문 D-day(WARN) / refs dangling(ERROR)·미등재(WARN) / 동일 법령번호 중복 후보(WARN) / 제안 키워드+ACTIVE·DONE(WARN) / **watch due 경과(ERROR)** / **verify↔원장 대조(ERROR)** / pending 미이관(WARN) / region_policy 정합(WARN) / **coverage↔tracker ID 동기(ERROR)**
- 실행(**리포 루트 기준**):
  ```
  node scripts/validate.mjs public/data/tracker_data.json public/data/region_policy.json
  RP_PATH=public/data/region_policy.json COV_PATH=ops/coverage.json \
    node ops/validate2.mjs public/data/tracker_data.json ops/runs/<오늘원장>.json
  ```
- 샌드박스에서 데이터 파일을 작업 디렉토리 루트로 내려받아 쓰는 경우엔 basename만 넘겨도 동작(경로 인자가 그대로 전달됨).

**G4 배포 게이트 — PR 머지 시퀀스 (F3):**
```
get_files → get_check_runs → get → get_reviews → get_review_comments
   → 코멘트 0이 아니면: 전 코멘트 내용 확인·타당성 판정·반영 → (재리뷰) → merge
```
- 대상 파일: `public/data/tracker_data.json` + `public/data/region_policy.json` (둘 다 변경 확인).
- comments/reviews 카운트가 0이 아닌 상태에서 내용 미확인 머지 금지.
- Codex 봇은 COMMENTED 상태로만 옴 — 본문은 래퍼, 실지적은 인라인(get_review_comments)에 있음.
- 머지 커밋 메시지에 runId 기재.

---

## 5. 마이그레이션 (호환 유지 순서)

| 단계 | 내용 | 앱 영향 |
|------|------|--------|
| M1 (완료 2026-07-22) | ops/ 디렉토리 신설: RUNBOOK.md·coverage.json·validate2.mjs·runs/ 시작. 이후 모든 run은 원장 필수 | 없음 (public/data 밖) |
| M2 | validator v2 — CI 편입. 산문 D-day는 우선 WARN→2주 후 ERROR 승격 | 없음 |
| M3 | 데이터 필드 도입: statusReason·milestones·refs·watch·verify. dt는 빌드 스크립트(`ops/build_dt.mjs`)가 milestones에서 자동 생성 — 앱은 계속 dt를 읽으므로 무영향. checkNote의 pending 문장을 watch로 이관 | 없음 |
| M4 (UX 개편과 병행) | 앱이 milestones에서 D-day 실시간 계산(dt 소멸), canonicalId 숨김, watch 큐·NOW 밴드 표면, pillar(=coverage 축 재사용) 필터 | App.jsx 개정 |

주: M4의 pillar는 별도 발명하지 않고 **coverage.json의 축을 그대로 쓴다** — 데이터 층과 화면 층이 같은 분류를 공유.

---

## 6. 세션 프로토콜 (운영자·모델 공통)

1. **세션 시작 시 실제 날짜부터 확인**(F12) — 대화가 여러 날에 걸치면 이전 턴의 날짜 감각이 남아 D-day가 조용히 밀린다. GitHub 커밋 타임스탬프 등 외부 신호로 오늘 날짜를 확정한 뒤 RD-0 재계산.
2. main에서 tracker_data.json·region_policy.json·validate.mjs·ops/ 재취득 → 최근 원장 확인 → RD-0 롤오버.
3. 모든 결론 변경엔 근거 소스를 원장에 남긴다. "찾지 못함"도 기록이다(empty-retry).
4. **미검증 항목의 verify/lastChecked를 오늘 날짜로 밀지 않는다** — 이전 검증일 유지가 정직하고, 다음 run이 우선 처리할 대상을 드러낸다.
5. 신규 항목 추가 전: 법령·규정 번호로 트래커 전문 검색(중복 방지) → ID는 dedup 재부여 스크립트로.
6. 신규 항목·status 변경·병합·na 처리 = Claire 승인. 나머지 자율.
7. run 종료: G2·G3 통과 → present → 배포 절반(브랜치→업로드→PR→G4). **ops/와 데이터는 같은 PR로**(F13).
8. 이월: pendingDecisions와 due 임박 watch를 다음 run 첫 작업으로.
