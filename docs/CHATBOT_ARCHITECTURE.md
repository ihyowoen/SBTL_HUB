# Chatbot Architecture — Redesign Spec

작성: 2026-04-14  
목적: 현재 `api/chat.js` + `lib/chat/*`가 누적된 fallback/휴리스틱으로 엉킨 상태를 구조적으로 재설계.

---

## 1. 관찰된 결함 (payload 실측 기반)

### 1A. Turn 1 — "미국 FEOC 쉽게 설명해줘" (새 세션)

**Request:**
```json
{
  "message": "미국 FEOC 쉽게 설명해줘",
  "context": {
    "date": null, "region": null,
    "last_answer_type": null,
    "last_result_ids": [],
    "selected_item_id": null
  }
}
```

**Response:**
```json
{
  "answer": "FEOC는 중국이나 러시아나 북한이나 이란 정부가...",
  "answer_type": "general",
  "confidence": 0.92,
  "cards": [],
  "debug": {
    "llm": null,
    "faq_tone_rewrite": { "used": true, "skipped": false, "latency_ms": 843 },
    "policy_tone_rewrite": { "used": true, "skipped": false, "latency_ms": 505 }
  }
}
```

**분석:** Turn 1은 **정상 작동**. 단 3가지 관찰:
- `answer_type: "general"` — FAQ 매치인데 compose.js가 general로 마스킹 (D12)
- FAQ rewrite + Policy rewrite **둘 다** 돌아감 → 중복 latency 1.3s. intent가 policy와 FAQ 양쪽에 걸려 두 번 LLM 호출
- LLM chat synthesis는 null (FAQ 모드이므로 shouldTryLLM 조건 실패 — 설계상 의도)

### 1B. Turn 2 — "방금 답변을 더 쉽게 설명해줘" (Turn 1에 이어서)

**Request:**
```json
{
  "message": "방금 답변을 더 쉽게 설명해줘",
  "context": {
    "last_answer_type": "general",
    "last_result_ids": [],
    "date": null, "region": null, "selected_item_id": null
  }
}
```

**Response (추정):** FAQ 답변이 다시 와야 하는데 **최신 뉴스 카드들 + follow_up 답변**이 옴.

**분석 — 실행 흐름:**
1. intent.js 처음부터 정렬:
   - `/왜\s*중요|...|의미|...|영향|.../` → X (match 없음)
   - `/심층|분석|해설|.../` → X
   - `/그\s*기사|방금|직전|.../` + `hasCtx` → **O** (`방금` 매치 + last_answer_type="general"로 hasCtx=true)
   - → intent = `follow_up`
2. retrieve(`follow_up`) → `retrieveInternal` → FAQ 매치 실패 → intent.follow_up 분기 → `lexicalSearchCards(message, scope)`
3. message 토큰: `"방금", "답변을", "더", "쉽게", "설명해줘"` → 전부 stopword → 빈 결과
4. fallback → `cardsOnLatestAvailableDate()` → 최신 날짜 카드 4장
5. LLM synthesize(`follow_up`) → 카드들 넘기고 "직전 맥락을 이어받아..." instruction
6. 결과: "이번에 나온 카드들은 이전에 논의했던 내용의 후속 근거야..." — **FAQ 재설명이 아니라 뉴스 맥락 답변**

### 1C. Backend가 기대하는 context (코드상)

```js
context.last_cards[0]        // 카드 객체 배열 — frontend는 URL만 보냄
context.last_answer_type     // 직전 intent — 원본 의도 아님 (D12)
context.last_answer          // 직전 답변 텍스트 — 존재 안 함 (D2)
// context.selected_item_id   // frontend 보내는데 backend 안 읽음 (D3)
// context.last_result_ids    // frontend 보내는데 backend 안 읽음 (D1')
```

### 결함 목록 (확정)

| # | 결함 | 영향 | 증거 |
|---|---|---|---|
| D1 | Frontend가 response `cards` 객체를 받지만 다음 요청에 URL(`last_result_ids`)만 보냄 | `analyze_card` 경로가 topCard 못 찾음 | Turn 1 response vs Turn 2 request |
| D2 | Frontend가 `last_answer` 본문을 안 보냄 | rephrase 불가능 | Payload 필드 부재 |
| D3 | Backend가 `selected_item_id` 필드 무시 | 사용자 명시 선택 카드 미활용 | api/chat.js grep |
| D4 | `last_answer_type`이 매 턴 덮어써짐 | 2턴+ chain 원본 의도 소실 | Turn 1 FAQ → Turn 2에서 "general"로 마스킹됨 |
| D5 | intent.js가 regex linear → FEOC가 FAQ 대상인데 "feoc" 키워드로 policy 매치 | FAQ 매치 로직이 retrieval 내부에 숨어 intent와 독립 작동 | intent.js L14 |
| D6 | `follow_up` intent가 컨텍스트 없이 lexical 검색 + 최신 카드 fallback | "더 쉽게"에 최신 뉴스 카드 답변 | **Turn 2 재현 확인** |
| D7 | FAQ/Policy 분기가 intent보다 먼저 결정됨 | intent 값이 부분적으로 쓸모 없음 | retrieval.js L146 |
| D8 | analysis_why/summary/deep 3개만 context 참조 | 나머지 intent는 컨텍스트 무시 | api/chat.js L168 |
| D9 | "왜 중요한지 설명해줘" → 응답 `answer_type: follow_up` (코드상 analysis_why여야 함) | intent 분류 결과와 실제 동작 불일치 | Turn 2가 아닌 이전 세션 payload |
| D10 | `confidence: 0.48` + `fallback_triggered: true`인데 정상 LLM 답변 | fallback flag 의미 불명확 | 이전 세션 payload |
| **D11** | **`follow_up` intent는 직전 턴이 뭐든 관계없이 최신 카드 검색** | **FAQ/policy 재설명·rephrase 기능 부재** | **Turn 2 실행 흐름 확인** |
| **D12** | **compose.js가 FAQ 응답을 `answer_type: "general"`로 마스킹** | **frontend는 "general 답변"으로 기억 → 컨텍스트 구분 소실** | **Turn 1 response answer_type** |
| **D13** | **Turn 1에서 FAQ rewrite + Policy rewrite 둘 다 LLM 호출 (중복)** | **불필요한 latency 1.3s 추가 + Groq rate-limit 소비** | **faq_tone_rewrite + policy_tone_rewrite 동시 used:true** |

### D11 상세: `follow_up`의 진짜 문제
현재 코드에서 `follow_up`은 단지 "이전 컨텍스트가 있으니 재검색하라"는 flag 역할. 실제로는:
- **follow_up**: 직전 주제 이어서 확장 ("방금 거 중에 SK온은?") → retrieve 필요
- **rephrase**: 직전 답변 다른 방식 재작성 ("더 쉽게") → 직전 답변 재가공
- **drill_down**: 직전 카드 하나 깊이 분석 ("그 카드 왜 중요?") → /api/analysis 위임

이 셋이 **전혀 다른 연산**인데 intent.js는 전부 `follow_up`으로 묶음. retrieval.js는 셋 다 동일 경로로 처리. 그 결과:
- "더 쉽게" → 뉴스 검색 (엉뚱한 답)
- "더 찾아줘" → 뉴스 검색 (OK)
- "그 카드 왜 중요?" → 뉴스 검색 (엉뚱한 답, `analysis_why` regex에 따로 분기되어 있지만 topCard 없으면 400)

---

## 2. 사용자 행동 분류 — 3축 모델

(Phase 1 초안과 동일. 변경 없음.)

### Axis A: Action
```
new_query     — 새 검색/질의 시작
rephrase      — 직전 답변을 다른 방식으로 재작성 (D11 대응)
analyze_card  — 특정 카드 1장을 깊이 분석 (D11 대응)
follow_up     — 직전 주제를 이어서 확장/보충 (축소 재정의)
```

### Axis B: Topic
```
faq_concept   — 개념 질문
news          — 최근 뉴스
policy        — 정책 체계
comparison    — 비교
general       — 잡의도
```

### Axis C: Scope
```
region, date, entity
```

---

## 3. Pipeline 재설계

(Phase 1 초안과 동일.)

```
POST /api/chat
       ↓
┌──────────────────────────┐
│ Layer 1: parseRequest    │  input → { action, topic, scope, rawMessage }
└──────────────────────────┘
       ↓
┌──────────────────────────┐
│ Layer 2: resolveContext  │  action에 따라 필요한 context hydrate/validate
└──────────────────────────┘
       ↓
┌──────────────────────────┐
│ Layer 3: retrieve        │  action+topic 따라 source 선택
└──────────────────────────┘
       ↓
┌──────────────────────────┐
│ Layer 4: synthesize      │  LLM or 템플릿, action별 고정
└──────────────────────────┘
       ↓
┌──────────────────────────┐
│ Layer 5: respond         │  조립 + tone 통일 + next_context 힌트
└──────────────────────────┘
```

---

## 4. Context Protocol (신규 규약)

```ts
interface ChatContext {
  // 현재 턴
  region?: Region;
  date?: string;               // YYYY.MM.DD
  selected_item_id?: string;   // 사용자가 명시적으로 고른 카드

  // 직전 턴
  last_turn?: {
    action: Action;            // "new_query" | "rephrase" | "analyze_card" | "follow_up"
    topic: Topic | null;
    answer_text: string;       // 본문 전체 (D2 해결)
    cards: Card[];             // 객체 배열 (D1 해결)
    scope: Scope;
  };

  // 원본 turn (2턴 이상 chain에서 원본 의도 유지 — D4 해결)
  root_turn?: {
    action: Action;
    topic: Topic | null;
    user_message: string;
  };
}
```

### 기존 필드 → 신규 매핑

| 기존 | 신규 |
|---|---|
| `last_answer_type` | `last_turn.action` + `last_turn.topic` (D12 해결) |
| `last_result_ids` | `last_turn.cards[].url` (객체 내 포함) |
| `selected_item_id` | 그대로 유지 (backend가 이제 읽음 — D3 해결) |
| (없음) | `last_turn.answer_text` — **신규** |
| (없음) | `root_turn` — **신규** |

---

## 5. Action별 세부 사양

### new_query
- 가장 흔한 경로
- topic에 따라 retrieve 분기 고정
- LLM synthesis 적용 (카드 있는 경우)

### rephrase (D11 해결)
- Trigger: "더 쉽게", "짧게", "한 줄로", "예시로", "초등학생이 이해하게"
- Required: `last_turn.answer_text`
- 없으면: `{ clarification: "어떤 답변을 다시 설명할까?" }`
- Flow: `last_turn.answer_text` + user instruction → LLM rewrite
  - **답변 본문만 재작성, 카드는 `last_turn.cards` 그대로 재사용**
- tone: rewriteToCasual 불필요 (LLM이 이미 반말 프롬프트 준수)

### analyze_card (D3, D11 해결)
- Trigger: "왜 중요?", "이 카드 요약", "심층 분석"
- Required: `selected_item_id` OR `last_turn.cards[0]`
- 우선순위: **selected_item_id > last_turn.cards[0]**
- 없으면: `{ clarification: "어떤 카드를 분석할까? 먼저 뉴스를 검색해줘." }`
- Flow: 카드 1장 → /api/analysis 위임 → why/summary/analysis

### follow_up (축소 재정의)
- Trigger: "방금 거 중에 X는?", "더 찾아줘", "관련해서 Y는?"
- Required: `root_turn` (2턴+ chain에서 원본 주제 유지)
- topic은 root_turn에서 계승, scope만 새 message에서 재추출
- Flow: retrieve(root_topic + new_scope) → LLM synthesis
- **"lexical + latestCards" 안티패턴 제거**

---

## 6. Topic별 Retrieve 사양

### faq_concept
- FAQ 매치 우선, 없으면 cards 키워드 매치
- **변경점 (D5, D7, D13 해결):** topic=faq_concept일 때만 FAQ 우선. 다른 topic에서는 FAQ 매치 안 함
- FAQ rewrite 1회만 (Policy rewrite 중복 제거)

### news
- date 스코프 엄격, 없으면 latest available
- "오늘 카드 없음 → 최신 날짜 fallback" 유지

### policy
- REGION_POLICY 템플릿 + tracker upcoming
- region 없으면 반문
- **topic이 policy일 때만 Policy rewrite** (D13 해결)

### comparison
- entity 2+ 추출
- 각 entity별 cards 3장 → LLM 비교 synthesis

### general
- lexical 검색 4장, 없으면 최신 4장

---

## 7. 기존 코드 → 신규 매핑

| 기존 | 신규 | 비고 |
|---|---|---|
| `intent.js::classifyIntent` | `parseRequest.js::parseRequest` | 3축 반환 |
| `scope.js::extractScope` | 유지 (Scope 부분만) | 확장 완료 |
| `retrieval.js::retrieveInternal` | `retrieve.js` (action+topic dispatch) | 재작성 |
| `retrieval.js::matchFaq` | `retrieve/faq.js` | 분리 |
| `retrieval.js::selectNewsCards` | `retrieve/news.js` | 분리, news_meta 유지 |
| `compose.js` | `synthesize.js` + `respond.js` | 2개 레이어로 분리 |
| `confidence.js` | **의미 재정의 후 유지/제거 결정** | D10 선결 |
| `fallback.js` | `respond`에 흡수 + Brave는 별도 | 단순화 |
| `llm.js` | 유지 + rephrase 함수 추가 | 재사용 |
| `api/chat.js` | 5-layer orchestrator | 얇아짐 |

---

## 8. Frontend 변경 사항 (App.jsx)

Phase 3. 로컬 권장 (75KB 재업로드 비효율).

### 필수
1. Response의 `cards` 객체를 저장하고 다음 요청에 `last_turn.cards`로 전달 (D1)
2. Response의 `answer` 본문을 저장하고 `last_turn.answer_text`로 전달 (D2)
3. `last_turn.action`, `last_turn.topic` 전달 (D4, D12)
4. `root_turn` 저장 및 maintain (new_query 시 세팅, rephrase/follow_up 시 유지)
5. Suggestion 버튼에 명시적 hint 포함:
   - "더 쉽게" → `{ hint_action: "rephrase" }`
   - "왜 중요?" → `{ hint_action: "analyze_card", hint_topic: "why" }`
   - "관련 카드 더" → `{ hint_action: "follow_up" }`
6. 카드 클릭 시 `selected_item_id` 세팅 (D3)

---

## 9. 실행 순서

### Phase 1 (완료): 이 문서

### Phase 2 (다음 세션, backend-only, ~2시간)
1. **선결 조사 (30분)**
   - D9: "왜 중요한지" 요청이 왜 follow_up으로 분류됐는지 vercel 빌드 확인
   - D10: confidence.js의 fallback_triggered 의미 정의
   - D13: FAQ + Policy rewrite 중복 호출 근본 원인 확인
2. `parseRequest.js` 작성 — frontend hint 존중 (suggestion 버튼에서 hint_action 오면 그대로, 없으면 rule-based)
3. `retrieve/*.js` 분리 작성
4. `synthesize.js` + `respond.js` 분리
5. `api/chat.js` 5-layer 재작성
6. 기존 `intent.js`/`retrieval.js`/`compose.js`/`fallback.js` deprecated 태그 유지
7. 시나리오 10개 Before/After 비교

### Phase 3 (다음 세션, frontend, ~1시간)
1. App.jsx 챗봇 호출부 수정
2. Suggestion 버튼 hint 추가
3. 카드 클릭 selected_item_id 세팅

### Phase 4 (선택)
- deprecated 코드 제거
- 배지 이모지 디자인 결정

---

## 10. 테스트 시나리오 (Phase 2 검증용)

실 데이터 Before/After 비교:

1. "FEOC 뭐야" → FAQ, 카드 0 (현재 OK, rewrite 중복만 해결)
2. "오늘 뉴스" → 최신 카드 3~4장 + LLM
3. "어제 미국 정책 뉴스" → 2026.04.13 US 카드 + LLM
4. "LG vs SK" → 2사 카드 각각 + 비교 LLM
5. "미국 정책" → REGION_POLICY.US + rewrite 1회
6. (뉴스 후) "더 쉽게" → **rephrase**, 기존 뉴스 답변 재작성, 카드 유지 (D11 해결 검증)
7. (뉴스 후) "첫 번째 카드 왜 중요?" → **analyze_card**, 해당 카드 /api/analysis
8. **(FAQ 후) "더 쉽게" → rephrase (D11 핵심 검증)** — 현재 엉뚱한 답, 신규는 FAQ 답변 재작성
9. 빈 컨텍스트에서 "더 쉽게" → clarification
10. (뉴스 후) "관련 SK온은?" → **follow_up**, root_topic=news + scope.entity=SK온

---

## 11. 결론

지금 챗봇이 stupid한 진짜 원인은 LLM 품질도, cards 데이터 부족도 아니고 **intent layer의 구조적 결함**. 특히 `follow_up` intent가 **rephrase·drill_down·실제 follow_up을 전부 다 처리하려다 셋 다 망가뜨림** (D11).

Phase 2에서 3축 모델 + 5-layer pipeline으로 재작성하면 같은 cards 데이터로도 답변 품질이 한 단계 올라감. 이게 구조적 개선의 본질.

---

## Appendix A: Turn 1 payload (FAQ 정상 케이스)

**Request:**
```json
{
  "message": "미국 FEOC 쉽게 설명해줘",
  "context": { "date": null, "region": null, "last_answer_type": null, "last_result_ids": [], "selected_item_id": null }
}
```

**Response:**
```json
{
  "answer": "FEOC는 중국이나 러시아나 북한이나 이란 정부가 소유하거나 통제하는 기업을 말해. ...",
  "answer_type": "general",
  "source_mode": "internal",
  "confidence": 0.92,
  "cards": [],
  "suggestions": [
    { "label": "조금 더 쉽게 설명해줘" },
    { "label": "관련 카드 더 보여줘" },
    { "label": "정책 일정만 따로 정리해줘" }
  ],
  "debug": {
    "fallback_triggered": false,
    "confidence_bucket": "high",
    "fallback_reason": "internal_confident",
    "llm": null,
    "faq_tone_rewrite": { "used": true, "skipped": false, "latency_ms": 843 },
    "policy_tone_rewrite": { "used": true, "skipped": false, "latency_ms": 505 }
  }
}
```

관찰:
- answer는 반말 정상 (rewrite 작동)
- answer_type=general (D12: FAQ 마스킹)
- FAQ rewrite + Policy rewrite 중복 호출 (D13: 총 1.35s 추가 latency)
- Suggestion 버튼이 "조금 더 쉽게 설명해줘" 포함 → 누르면 Turn 2의 재앙 시작

## Appendix B: Turn 2 payload (D11 재현)

**Request:**
```json
{
  "message": "방금 답변을 더 쉽게 설명해줘",
  "context": {
    "last_answer_type": "general",
    "last_result_ids": [],
    "date": null, "region": null, "selected_item_id": null
  }
}
```

Backend 실행 흐름:
1. `classifyIntent` → "방금" 매치 + hasCtx=true → **follow_up**
2. `retrieveInternal(follow_up)` → matchFaq 실패 → cards 분기 → lexicalSearchCards → empty (전부 stopword) → latestCards fallback
3. LLM synthesize(follow_up) → "직전 맥락을 이어받아..." instruction + 최신 카드 4장
4. **결과: FAQ 답변 재작성이 아니라 최신 뉴스 맥락 답변**

**근본 원인:** D11 — follow_up intent는 rephrase 기능을 포함하지 않음. 직전이 FAQ였어도 최신 카드 검색으로 대체됨.

## Appendix C: diag로 확인된 환경 사실

- `cwd: /var/task` → Vercel serverless 표준
- `sources: { cards: "fs", faq: "fs", tracker: "fs" }` → public/data가 번들에 포함됨, S1 fetch는 안 쓰임 (안전장치로만)
- `cards_len: 337, faq_len: 38, tracker_len: 59`
- `faq_len: 38` → 이전 40에서 2 감소. Phase 2 시작 시 `git log public/data/faq.json` 확인
- `tracker_len: 59` → 이전 50에서 9 증가. tracker 업데이트 확인
- `load_ms: 6` → fs 읽기 극히 빠름
