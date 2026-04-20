# 배터리 상담소 — 3차 상담 구조 설계 v0.1

**작성일**: 2026-04-20
**브랜치**: phase1-consult-redesign
**상태**: 설계 리뷰 대기 (구현 전)

---

## 1. 왜 이 구조로 가는가

### 지금까지의 문제

- 단일 prompt에 opener + hook + 말투 + JSON + coverage + SBTL Chain 다 담음 → Flash가 섞어버림
- 두더지잡기 루프: "이 카드는" 금지 → Flash 무시 → regex로 잡음 → 새 이상 패턴 → 또 추가
- 품질 측정 불가능: "opener가 잘 됐는지"의 기준이 모호. 291개 카드 중 사람 눈 검증은 매 commit마다 1~2개만.
- 재방문 동인은 있으나 **종료점이 없어** followup 루프가 끝없이 이어짐

### 3단계가 해결하는 것

| 문제 | 3단계가 해결하는 방식 |
|---|---|
| 단일 prompt 과부하 | 각 stage가 한 가지만 함. Flash 부담 ↓ |
| 품질 측정 불가 | 각 stage 독립적 gold test 가능 (JSON schema 검증) |
| 종료점 없음 | 3차 = 명시적 상담 종료 |
| 재방문 동인 약함 | 레벨업 구조 자체가 보상. 3차 도달이 "깊이 판 증거" |
| 없는 사실 만들기 | 1차에서 팩트 확정 → 2차는 1차 facts 내에서만 해석 → 3차는 2차 검증 |
| Claire 애널리스트 사고 흐름 재현 | "무슨 일이야 → 왜 중요해 → 잠깐, 놓친 거 없나" |

---

## 2. 각 단계 Role 정의

### 1차 — 정찰병 강차장 (Scout)

**역할**: 사실 확인. 카드 내용을 정확히 정리.
**금지**: 해석, 추측, 함의 언급, SBTL 관점 언급.
**허용**: 팩트 나열, 숫자/날짜/주체 추출, 카드에 없어서 모르는 것 명시.

**Input**:
- `card`: { title, sub, gate, fact, implication[], region, date, category, source }

**Output (JSON only)**:
```json
{
  "summary": "무슨 일인지 2~3문장 반말",
  "facts": ["핵심 숫자/주체/일정 3~5개"],
  "unknowns": ["카드에 없어서 모르는 것 0~2개"]
}
```

**말투**: 팩트 정리 톤. "~했어", "~돼", "~야"
**금지 표현**: "~일 것 같아", "~로 볼 수 있어", "~인 듯해", "~할 가능성이 있어"

---

### 2차 — 분석가 강차장 (Analyst)

**역할**: 왜 중요한지 해석. 한 각도 잡아서 깊이.
**제약**: 1차에서 정리된 facts 내에서만 해석. 새 사실 추가 금지.

**Input**:
- `card`
- `stage1_output` (1차 JSON 통째)
- `related_cards[]`

**Output (JSON only)**:
```json
{
  "angle": "어떤 각도인지 한 줄 (예: '타이밍', '숫자 규모', '구조 의도')",
  "interpretation": "해석 2~3문장",
  "sbtl_link": "Chain 3경로 중 하나에 해당하면 짧게, 아니면 null",
  "key_tension": "핵심 쟁점 1개 한 줄"
}
```

**각도 선택지** (한 개만):
- 타이밍 — 발표/거래/규제 시점이 다른 움직임과 어떻게 연결되는지
- 숫자 — 금액/규모가 업계 기준 대비 의미
- 대비 — 이전 조치·경쟁사와 다른 점
- 구조 — 거래/지분/계약 구조의 회계·전략 의도

**SBTL Chain 언급 조건**:
- (1) K-3사 수요 / (2) 파우치형 점유율 / (3) 알루미늄 원가 중 하나에 **명확히** 해당할 때만
- 애매하면 `sbtl_link: null`

**말투**: 판단 톤. "여기서 걸리는 건", "~가 핵심이야"

---

### 3차 — 빨간펜 강차장 (Red Team)

**역할**: 1차+2차 자기 검증. 구멍 찾기.
**출력 의무**: 4개 필수 항목 모두 채워야 함.

**Input**:
- `card`
- `stage1_output` (1차)
- `stage2_output` (2차)

**Output (JSON only)**:
```json
{
  "premature_interpretations": ["2차 해석 중 성급할 수 있는 부분 1~2개"],
  "unverified_premises": ["아직 확인 안 된 전제 1~2개"],
  "counter_scenario": "2차 해석이 틀렸다면 어떤 그림인지 2~3문장",
  "next_checkpoints": ["앞으로 확인할 포인트 1", "포인트 2"]
}
```

**말투**: 의심·겸손 톤. "근데 잠깐", "만약 반대라면", "아직 확실하지 않은 건"

**왜 Flash가 이 단계에서 잘할 거라고 보는가**:
- 자기 비판은 창작 아닌 **논리 작업**
- "반대 시나리오" 같은 구조화된 prompt는 LLM이 일관성 유지 잘함
- Input이 2차 output이라 hallucination 여지 작음

---

## 3. 유저 플로우

```
[카드 접수 — ReceiptBubble 그대로]
        │
        ▼
[1차: 무슨 일이야 — Scout]
        │
        │ [강차장 더 깊이 물어보기 →] 버튼
        ▼
[2차: 왜 중요해 — Analyst]
        │
        │ [최종 판단 받기 →] 버튼
        ▼
[3차: 근데 잠깐 — Red Team]
        │
        ▼
[─── 상담 종료 ───]
[다른 카드로 상담 가기]
```

### 유저 선택권

- 1차만 읽고 "충분해" → 닫기 (아무 버튼도 안 누름, UI는 1차 bubble에서 멈춤)
- 2차까지 보고 닫기 → OK (2차 bubble에서 멈춤)
- 3차까지 가면 "상담 종료" 명시적 표시 → 다른 카드 유도

### 추천 정책 — 순차 강제

- **2차 버튼은 1차 bubble 아래에만**, 3차 버튼은 2차 bubble 아래에만 표시
- 건너뛰기 허용 안 함 (consulting metaphor 살리기)
- 이유: "사실 못 잡고 해석만 하는 상담사"는 컨셉 파괴

---

## 4. Rendering (UI)

### ReceiptBubble (유지)

Claire 피드백: "귀엽게 상담기록 하는 건 재밌자나" → 날짜·티켓 번호 유지

### 1차 bubble — Scout

```
📋 1차 상담 · 사실 확인
[카드 제목]
[region · signal · date]
────
{summary}

[확인한 사실]
· {facts[0]}
· {facts[1]}
· {facts[2]}

{unknowns.length > 0 이면:}
[카드에 없어서 모르는 것]
· {unknowns[0]}
────
[강차장 더 깊이 물어보기 →]
```

### 2차 bubble — Analyst

```
🔍 2차 상담 · 핵심 각도
[{angle}]
────
{interpretation}

— 핵심은 {key_tension}

{sbtl_link 있으면:}
[SBTL 관점] {sbtl_link}
────
[최종 판단 받기 →]
```

### 3차 bubble — Red Team

```
🧪 3차 상담 · 빨간펜
────
[성급할 수 있는 부분]
· {premature_interpretations[0]}

[확인 안 된 전제]
· {unverified_premises[0]}

[반대 시나리오]
{counter_scenario}

[다음 체크포인트]
· {next_checkpoints[0]}
· {next_checkpoints[1]}
────
─── 상담 종료 ───
[다른 카드로 상담 가기]
```

---

## 5. 데이터 흐름 / API

### consultation payload 확장

```ts
// frontend → POST /api/chat
{
  consultation: {
    card: { ... },
    stage: 1 | 2 | 3,           // NEW
    prev_outputs: {              // NEW
      stage1?: { summary, facts, unknowns },
      stage2?: { angle, interpretation, sbtl_link, key_tension }
    },
    related_cards?: [...]        // 2차에서만 사용
  },
  ticket_id: number
}
```

### api/chat.js 라우팅

```js
if (consultation?.stage === 1) → synthesizeScout
if (consultation?.stage === 2) → synthesizeAnalyst
if (consultation?.stage === 3) → synthesizeRedTeam
```

### Response

```ts
{
  stage: 1|2|3,
  stage_output: {...},       // 해당 stage JSON
  next_stage_label: "강차장 더 깊이 물어보기" | "최종 판단 받기" | null,  // 3차는 null
  debug: { llm: {...}, ... }
}
```

---

## 6. Prompts (draft v0.1)

### SYSTEM_SCOUT

```
너는 SBTL첨단소재 '배터리 상담소'의 강차장이야. 이 단계에서는 **정찰병 모드**.

역할: 카드에 있는 사실만 정리해. 해석·추측·함의는 금지.

금지 표현: "~일 것 같아", "~로 볼 수 있어", "~인 듯해",
         "~할 가능성이 있어", "~가 예상돼", "~으로 보여"

허용 표현: "~했어", "~야", "~돼", "~이야"

카드에 없는 것은 절대 만들지 마. 모르면 unknowns에 담아.

[출력 형식 — JSON only]
{
  "summary": "무슨 일인지 2~3문장 반말",
  "facts": ["핵심 숫자/주체/일정 3~5개"],
  "unknowns": ["카드에 없어서 모르는 것 0~2개"]
}
```

### SYSTEM_ANALYST

```
너는 SBTL첨단소재 '배터리 상담소'의 강차장이야. 이 단계에서는 **분석가 모드**.

1차에서 사실은 이미 정리됐어. 너의 역할은 **한 각도 잡아서 왜 중요한지 해석**.

규칙:
- 1차 facts에 없는 사실 추가 금지
- 각도 1개만 선택. 여러 각도 나열 금지
- 가능한 각도: 타이밍 / 숫자 / 대비 / 구조 중 하나

SBTL Chain 언급 조건:
- K-3사 수요 / 파우치형 점유율 / 알루미늄 원가 중 하나에 명확히 해당할 때만
- 애매하면 sbtl_link: null

말투: 반말. 판단 톤. "여기서 걸리는 건", "~가 핵심이야"

[출력 형식 — JSON only]
{
  "angle": "타이밍" | "숫자" | "대비" | "구조",
  "interpretation": "해석 2~3문장",
  "sbtl_link": "Chain 관점 짧게 또는 null",
  "key_tension": "핵심 쟁점 1개 한 줄"
}
```

### SYSTEM_REDTEAM

```
너는 SBTL첨단소재 '배터리 상담소'의 강차장이야. 이 단계에서는 **빨간펜 모드**.

1차+2차에서 말한 걸 다시 보고 **구멍을 찾는다**.

4개 필수 항목:
1. 성급한 해석일 수 있는 부분 — 2차 interpretation 중 단정적인 부분
2. 확인 안 된 전제 — 2차가 당연시한 가정
3. 반대 시나리오 — 2차 해석이 틀렸다면 어떤 그림
4. 다음 체크포인트 2개 — 앞으로 어떤 뉴스/데이터로 확인 가능한지

규칙:
- 1차 facts·2차 interpretation 안에서만 비판
- 새 사실 추가 금지
- 겸손 톤: "이게 맞다면", "반대로 보면", "아직 확실하지 않은 건"
- 반말

[출력 형식 — JSON only]
{
  "premature_interpretations": ["1~2개"],
  "unverified_premises": ["1~2개"],
  "counter_scenario": "2~3문장",
  "next_checkpoints": ["체크포인트 1", "체크포인트 2"]
}
```

---

## 7. Gold regression test 전략

### MVP: 15 test cases (5 카테고리 × 3 stages)

카테고리: `ma_jv`, `tech`, `policy`, `kbattery`, `catl_cn`
각 카테고리마다 대표 카드 1개 골라서 3 stage 다 돌림.

### Test schema

```json
{
  "card_id": "2026-04-17_CN_ma_jv_01",
  "stage": "scout",
  "card": { ... },
  "prev_outputs": null,
  "expected": {
    "schema_valid": true,
    "forbidden_phrases": ["~일 것 같아", "~로 볼 수 있어"],
    "must_contain_anywhere": ["44.93억위안", "당승과기"],
    "facts_min_count": 3,
    "summary_max_chars": 150
  }
}
```

### Run command

```bash
node scripts/test_consultation_stages.js
```

각 카드 LLM 호출 → JSON schema validation → 금지 표현 검색 → 필수 키워드 검색 → pass/fail

**배포 전 gate**: 15 test 중 13+ pass 필수

---

## 8. 삭제할 것 / 유지할 것

### 삭제

- `synthesizeCardConsult` 의 기존 opener + remaining_points 로직
- `mapRemainingPointsToSuggestions` (api/chat.js)
- `FALLBACK_OPENER_HOOKS`, `FALLBACK_FOLLOWUP_HOOKS`
- `validateAndCleanRemainingPoints`
- `SYSTEM_CARD_CONSULT` (3개 system prompt로 분리)
- `buildConsultUserPrompt`의 isOpener 분기
- App.jsx의 `composeSessionSuggestions`, `sessionHooksRef`, `usedTopicsRef`
- cardOpenerPool.js 의 few-shot examples (3 stage에서는 anchor 불필요)

### 유지

- Gemini Flash + Groq auto-fallback dispatcher (`callLLM`)
- `stripPromptEchoes`, `softenFormalTone` (안전망 유지, 범위는 stage별로 조정)
- ReceiptBubble UI
- Data integrity 원칙
- Tone rule 핵심 (반말, 한자 금지)
- `buildCardConsultContext` (card + related_cards 조합 로직은 재사용)
- `consultationStorage` (localStorage 구조는 stage output 담도록 확장만)

---

## 9. 구현 순서 (Phase 2)

### Step 1 — Backend (llm.js + api/chat.js)
1. `synthesizeScout`, `synthesizeAnalyst`, `synthesizeRedTeam` 3개 함수 추가
2. `api/chat.js`에서 `consultation.stage` 기반 라우팅
3. Response에 `stage_output` 필드 통일

### Step 2 — Frontend (App.jsx)
1. `consultation` state에 `stage`, `stage1_output`, `stage2_output` 필드 추가
2. 1차/2차/3차 bubble 컴포넌트 3개 (ScoutBubble, AnalystBubble, RedTeamBubble)
3. 전환 버튼 (ReceiptBubble 스타일 유지)
4. "상담 종료" 상태 처리 — 3차 bubble 아래에서 다른 카드로 가는 CTA만

### Step 3 — Gold test
1. `scripts/test_consultation_stages.js` 작성
2. 5개 카테고리 대표 카드 3 stage씩 돌려서 결과 수동 리뷰
3. Forbidden phrase / must-contain 기준 확정
4. CI에 넣을지는 별도 결정 (지금은 수동 trigger)

### Step 4 — Production merge
1. Gold test 13/15 pass 확인
2. PR 정리
3. main merge + vercel 배포

**예상 시간**: Step 1~2가 4~6시간. Step 3이 2~3시간. 합쳐서 1~1.5일 작업.

---

## 10. Claire 결정 필요 — 열린 질문

### Q1. 단계 건너뛰기?

**옵션 A (추천)**: 순차 강제. 1차 → 2차 → 3차 고정.
**옵션 B**: 2차 직행 버튼 allow (빠른 답 필요한 날).

내 의견: **A**. 컨셉 일관성 + Flash 부담 ↓.

---

### Q2. 3차 자동 시작 vs 수동?

**옵션 A (추천)**: 수동. 2차 끝나면 `[최종 판단 받기]` 버튼.
**옵션 B**: 2차 완료 직후 자동 3차.

내 의견: **A**. 유저가 3차 필요한지 스스로 판단. Red team 자체가 "더 파고 싶은 사람"의 보상.

---

### Q3. LLM 호출 비용 3배

- 현재 평균 세션당 opener 1 + followup 1~2 = 2~3 호출
- 3단계 풀 시: 3 호출
- **실질 차이 거의 없음**. Flash 무료 tier는 RPM 10 기준으로 여유 있음.
- Groq fallback도 그대로 작동

내 의견: **문제 없음**.

---

### Q4. 캐릭터 분리 수준?

**옵션 A (추천)**: 같은 강차장. 모드만 다르게 (정찰병 모드 / 분석가 모드 / 빨간펜 모드).
**옵션 B**: 3명의 다른 캐릭터 (예: "정차장 / 강차장 / 박차장").

내 의견: **A**. 캐릭터 일관성. SBTL 세계관 복잡해지는 거 방지. 단, bubble 아이콘은 다르게 (📋 / 🔍 / 🧪).

---

### Q5. Stage 간 데이터 전달

**옵션 A (추천)**: 이전 stage JSON 통째로 다음 prompt에 주입.
**옵션 B**: 정제해서 요약만 전달.

내 의견: **A**. 구현 간단. Token 늘어도 3 stage 합쳐 ~2K tokens 수준.

---

### Q6. 세션 persistence

**옵션 A (추천)**: 세션 내에서만 유지. 새 세션이면 1차부터.
**옵션 B**: localStorage에 stage 진행도 저장 → 다음에 이어서.

내 의견: **A**. 이어서 가는 건 복잡도 대비 가치 낮음. 3 stage 합쳐 최대 30초면 다시 돌릴 수 있음.

---

## 11. 다음 액션

이 문서 읽고 Claire가 결정할 것:
1. Q1~Q6 답변 (추천값 다 OK면 "ㅇㅋ" 한 줄로도 됨)
2. 구현 시작 시점 (내일 / 이번 주말 / 언제)
3. 빠진 것 / 수정할 것

구현 시작 전에 이 문서에 Claire의 입장 추가로 커밋하고, 그 다음 Phase 2 Step 1부터 진행.
