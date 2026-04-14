# Chatbot Architecture — Redesign Spec

작성: 2026-04-14  
목적: 현재 `api/chat.js` + `lib/chat/*`가 누적된 fallback/휴리스틱으로 엉킨 상태를 구조적으로 재설계.

---

## 1. 관찰된 결함 (payload 실측 기반)

### Frontend가 실제로 보내는 context
```json
{
  "message": "왜 중요한지 설명해줘",
  "context": {
    "date": "2026.04.08",
    "region": "KR",
    "last_answer_type": "follow_up",
    "last_result_ids": ["https://www.businesskorea.co.kr/..."],
    "selected_item_id": "https://www.businesskorea.co.kr/..."
  }
}
```

### Backend가 기대하는 context (코드상)
```js
context.last_cards[0]        // 카드 객체 배열 — frontend는 안 보냄
context.last_answer_type     // 직전 intent — 원본 의도 아님 (2턴 소실)
context.last_answer          // 직전 답변 텍스트 — 존재 안 함
// context.selected_item_id   // frontend가 보내는데 backend가 안 읽음
// context.last_result_ids    // frontend가 보내는데 backend가 안 읽음
```

### 결함 목록

| # | 결함 | 영향 |
|---|---|---|
| D1 | Frontend: `last_cards` 객체가 아니라 `last_result_ids` URL만 보냄 | `analysis_why` intent가 `topCard`를 못 찾아 400 에러 |
| D2 | Frontend: `last_answer` (본문)을 안 보냄 | rephrase/재작성 action 불가능 |
| D3 | Backend: `selected_item_id` 필드를 무시 | 사용자가 명시적으로 선택한 카드를 못 씀 |
| D4 | `last_answer_type`이 매 턴 덮어써짐 → 2턴 전 원본 의도 소실 | FAQ → follow_up → follow_up 체인에서 원본 FAQ 컨텍스트 완전 손실 |
| D5 | `intent.js`가 regex linear match — FEOC가 FAQ인데 "feoc" 키워드 때문에 policy로 분류 | FAQ 매치 로직이 `retrieveInternal` 안에 숨어서 intent와 독립 작동 |
| D6 | `follow_up` intent가 컨텍스트 없이 lexical 검색 + 최신 카드 fallback | "더 쉽게"에 최신 뉴스 카드가 답변으로 나옴 |
| D7 | FAQ vs Policy 분기가 intent보다 먼저 결정됨 (`retrieveInternal`) | intent 값이 쓸모 없어짐. 중복 판정 |
| D8 | `analysis_why/summary/deep` 3개만 context 참조 | 나머지 intent는 컨텍스트 무시 |

---

## 2. 사용자 행동 분류 — 3축 모델

지금 `intent.js`가 하나의 평면에 regex를 나열하는데, 실제 사용자 행동은 **직교하는 3개 축**의 조합이다.

### Axis A: Action (무엇을 할 것인가)
```
new_query     — 새 검색/질의 시작
rephrase      — 직전 답변을 다른 방식으로 재작성
analyze_card  — 특정 카드 1장을 깊이 분석
follow_up     — 직전 대화 주제를 이어서 확장/보충
```

### Axis B: Topic (무엇에 대한 것인가)
```
faq_concept   — 개념 질문 ("FEOC 뭐야", "CBAM 언제")
news          — 최근 뉴스 요청
policy        — 정책 체계 질문
comparison    — 둘 이상 대상 비교
general       — 잡의도
```

### Axis C: Scope (어떤 필터)
```
region   — US/KR/CN/EU/JP
date     — 절대/상대 날짜
entity   — 기업/제품 엔티티
```

### 예시 매핑
| 사용자 입력 | action | topic | scope |
|---|---|---|---|
| "FEOC 뭐야" | new_query | faq_concept | — |
| "오늘 한국 뉴스" | new_query | news | KR, today |
| "이 카드 왜 중요?" (selected 있음) | analyze_card | — | selected |
| "더 쉽게 설명해줘" (last_answer 있음) | rephrase | — | — |
| "방금 거 관련 SK온도 있어?" | follow_up | news | SK온 |
| "미국 vs 중국 정책" | new_query | comparison | US+CN |

---

## 3. Pipeline 재설계

```
POST /api/chat
       ↓
┌──────────────────────────┐
│ Layer 1: parseRequest    │  input → { action, topic, scope, rawMessage }
└──────────────────────────┘
       ↓
┌──────────────────────────┐
│ Layer 2: resolveContext  │  context에서 관련 자료 hydrate
│                          │   - action=rephrase    → need last_answer
│                          │   - action=analyze_card → need selected_card
│                          │   - action=follow_up   → need last_cards + last_topic
│                          │   - context 부족하면 clarification 반환
└──────────────────────────┘
       ↓
┌──────────────────────────┐
│ Layer 3: retrieve        │  action+topic에 따라 소스 선택
│                          │   - faq_concept  → FAQ (엄격 스코어링)
│                          │   - news         → cards + date 스코프
│                          │   - policy       → REGION_POLICY + tracker
│                          │   - comparison   → cards (2+ entity)
│                          │   - analyze_card → 이미 resolveContext에서 확보
│                          │   - rephrase     → 이미 resolveContext에서 확보
└──────────────────────────┘
       ↓
┌──────────────────────────┐
│ Layer 4: synthesize      │  action+topic에 따라 고정 분기
│                          │   - rephrase     → LLM(원문+instruction)
│                          │   - analyze_card → /api/analysis 위임
│                          │   - 나머지       → LLM(retrieved+instruction) + fallback template
└──────────────────────────┘
       ↓
┌──────────────────────────┐
│ Layer 5: respond         │  answer + cards + debug 조립, tone 통일
│                          │   - tone: rewriteToCasual (필요시)
│                          │   - next_context 생성 (frontend에 무엇을 저장할지)
└──────────────────────────┘
```

### 핵심 변화
1. **Intent classification 없앰.** 3축 parseRequest로 교체.
2. **FAQ/Policy 분기가 retrieve Layer에 흡수됨.** 더 이상 retrieval 중간에 숨지 않음.
3. **Context 요구사항이 action별로 명시됨.** 부족하면 "뭘 더 말씀드리지?" 반환.
4. **Rephrase/Analyze가 1급 시민.** 지금처럼 follow_up이 편법으로 처리하는 일 없음.

---

## 4. Context Protocol (신규 규약)

Frontend가 매 요청에 보내야 할 것:

```ts
interface ChatContext {
  // 현재 턴
  region?: Region;
  date?: string;               // YYYY.MM.DD
  selected_item_id?: string;   // URL or card id — 사용자가 명시적으로 고른 카드

  // 직전 턴 (rephrase/follow_up 지원)
  last_turn?: {
    action: Action;            // "new_query" | "rephrase" | ...
    topic: Topic | null;
    answer_text: string;       // 본문 전체
    cards: Card[];             // 객체 배열 (URL만 아니라 전체)
    scope: Scope;
  };

  // 원본 turn (2턴 이상 follow-up 체인 지원)
  root_turn?: {
    action: Action;
    topic: Topic | null;
    user_message: string;      // 최초 질문
  };
}
```

### 기존 필드 매핑

| 기존 | 신규 |
|---|---|
| `last_answer_type` | `last_turn.action` + `last_turn.topic` |
| `last_result_ids` | `last_turn.cards[].url` (객체 내 포함) |
| `selected_item_id` | 그대로 유지 |
| (없음) | `last_turn.answer_text` — **반드시 추가** |
| (없음) | `root_turn` — **반드시 추가** |

### 결정: `last_turn.cards`는 전체 객체
- 지금처럼 URL만 보내면 backend가 cards.json 다시 뒤져서 찾아야 함 (낭비)
- Frontend가 이미 화면에 카드 렌더링하면서 객체를 들고 있음 → 그대로 실어 보내면 됨
- 크기 걱정: 카드 3~4장 × 평균 800 bytes = 3KB. 문제 없음.

---

## 5. Action별 세부 사양

### new_query
- 가장 흔한 경로. 기존 동작과 유사.
- topic에 따라 retrieve 분기 고정.
- LLM synthesis 적용 (카드 있는 경우).

### rephrase
- Trigger: "더 쉽게", "짧게", "한 줄로", "예시로", "초등학생이 이해하게"
- Required context: `last_turn.answer_text`
- 없으면: `{ clarification: "어떤 답변을 다시 설명할까?" }`
- Flow: `last_turn.answer_text` + user instruction → LLM rewrite → 답변 override, 카드는 `last_turn.cards` 그대로 재사용
- tone: rewriteToCasual 통과

### analyze_card
- Trigger: "왜 중요?", "요약해줘" (single card), "심층 분석"
- Required context: `selected_item_id` OR `last_turn.cards[0]`
- 없으면: `{ clarification: "어떤 카드를 분석할까? 먼저 뉴스를 검색해줘." }`
- Flow: 카드 1장 → /api/analysis 위임 → why/summary/analysis 모드 중 선택
- **중요: 지금 코드는 `last_cards[0]`만 참조. 이걸 `selected_item_id` 우선순위로 바꿔야 함.**

### follow_up
- Trigger: "방금 거 중에", "더 찾아줘", "관련해서 SK온은?"
- Required context: `root_turn` (2턴+ chain에서도 원본 주제 유지)
- topic은 root_turn에서 계승, scope만 새 message에서 재추출
- Flow: retrieve(root_topic + new_scope) → LLM synthesis
- 지금의 "lexical + latestCards fallback" 안티패턴 제거

---

## 6. Topic별 Retrieve 사양

### faq_concept
- FAQ 먼저, 없으면 cards 키워드 매치
- **변경점:** 지금은 모든 intent에서 FAQ 매치가 통과하는 oneshot 구조. 이건 FAQ 우선 의도지만, 결과적으로 "news intent면서 FAQ가 먹히면 FAQ 답변"처럼 예측 불가. 앞으로는 topic=faq_concept일 때만 FAQ 우선.
- cards 매치는 topic=news와 동일 로직

### news
- date 스코프 엄격. 없으면 latest available.
- **결정: "오늘 카드 없음 → 최신 가용 날짜 fallback"은 현재 대로 유지.** UX 유지. 답변에 솔직히 표시.

### policy
- REGION_POLICY 템플릿 + tracker upcoming
- region 없으면 "어떤 지역?" 반문
- tone rewrite 적용 (why 필드가 문어체)

### comparison
- entity 2개+ 추출 필요
- 각 entity별 cards 3장씩 retrieve → LLM 비교 synthesis

### general
- lexical 검색 4장, 없으면 최신 4장

---

## 7. 기존 코드 → 신규 매핑

| 기존 | 신규 | 비고 |
|---|---|---|
| `lib/chat/intent.js::classifyIntent` | `lib/chat/parseRequest.js::parseRequest` | 3축 반환 |
| `lib/chat/scope.js::extractScope` | 유지 (Scope 부분만) | 확장 완료 |
| `lib/chat/retrieval.js::retrieveInternal` | `lib/chat/retrieve.js` (action+topic dispatch) | 재작성 |
| `lib/chat/retrieval.js::matchFaq` | `lib/chat/retrieve/faq.js` | 분리 |
| `lib/chat/retrieval.js::selectNewsCards` | `lib/chat/retrieve/news.js` | 분리, news_meta 유지 |
| `lib/chat/compose.js` | `lib/chat/synthesize.js` + `lib/chat/respond.js` | 2개 레이어로 분리 |
| `lib/chat/confidence.js` | 유지 | 세부 튜닝은 Phase 3 |
| `lib/chat/fallback.js` | 통합되어 respond에 흡수 | Brave fallback 로직만 분리 |
| `lib/chat/llm.js` | 유지 + rephrase 함수 추가 | 재사용 |
| `api/chat.js` | 5-layer orchestrator | 얇아짐 |

---

## 8. Frontend 변경 사항 (App.jsx)

Phase 3에서 처리. 로컬 작업 권장 (75KB 재업로드 비효율).

### 필수 변경
1. 챗봇 POST 시 `last_turn.answer_text` 포함
2. 챗봇 POST 시 `last_turn.cards`를 객체 배열로 (URL 아닌)
3. `root_turn` 저장 및 전달 (최초 질문에서 action이 new_query일 때 세팅, follow-up/rephrase 시 유지)
4. Suggestion 버튼이 명시적 action/topic hint 포함:
   - "더 쉽게" → `{ hint_action: "rephrase" }`
   - "왜 중요?" → `{ hint_action: "analyze_card", hint_topic: "why" }`
   - "관련 카드 더" → `{ hint_action: "follow_up" }`
5. 카드 클릭 시 `selected_item_id` 세팅

### 선택 변경
- 배지 이모지(📋🔀TOP/HIGH) 톤 정리 — 아키텍처와 무관, 디자인 결정

---

## 9. 실행 순서

### Phase 1 (완료): 이 문서
- 확정된 결함 목록
- 3축 모델
- 5-layer 파이프라인
- Context protocol

### Phase 2 (다음 세션, backend-only, ~2시간)
1. `parseRequest.js` 신규 작성 (action + topic + scope)
2. `retrieve/*.js` 분리 작성 (faq/news/policy/comparison/general)
3. `synthesize.js` + `respond.js` 분리
4. `api/chat.js` 5-layer로 재작성
5. 기존 `intent.js` / `retrieval.js` / `compose.js` / `fallback.js` deprecated로 태그만 달아두고 일단 유지 (대비용)
6. 단위 테스트: 주요 사용자 시나리오 10개 배치 실행 → 응답 비교

### Phase 3 (다음 세션, frontend, ~1시간)
1. App.jsx 챗봇 호출부 수정 → Context Protocol 준수
2. Suggestion 버튼에 hint 추가
3. 카드 클릭 시 selected_item_id 세팅
4. 로컬 str_replace 권장 (75KB 재업로드 비효율)

### Phase 4 (선택)
- 기존 deprecated 코드 제거
- 배지 이모지 디자인 결정
- confidence 스코어링 재검토

---

## 10. 테스트 시나리오 (Phase 2 검증용)

실 데이터로 돌려서 Before/After 비교:

1. "FEOC 뭐야" → FAQ 답변, 카드 0
2. "오늘 뉴스" → 최신 카드 3~4장 + LLM
3. "어제 미국 정책 뉴스" → 2026.04.13 US 카드 + LLM
4. "LG vs SK" → 2사 카드 각각 + 비교 LLM
5. "미국 정책" → REGION_POLICY.US 템플릿 + rewrite
6. (뉴스 검색 후) "더 쉽게" → rephrase, 카드 유지
7. (뉴스 검색 후) "첫 번째 카드 왜 중요?" → analyze_card, 해당 카드 분석
8. (FAQ 답변 후) "더 쉽게" → FAQ 답변의 rephrase
9. 빈 컨텍스트에서 "더 쉽게" → clarification
10. (뉴스 검색 후) "관련 SK온은?" → follow_up, root_topic=news + scope.entity=SK온

각 시나리오의 기대 결과를 `docs/CHATBOT_TESTS.md`에 베이스라인으로 기록 (Phase 2 시작 시).

---

## 11. 결론

지금 챗봇이 stupid한 진짜 원인은 LLM 품질도, cards 데이터 부족도 아니고 **intent layer의 구조적 결함**. regex 한 줄씩 나열해 놓은 단일 레이어로 "새 검색 vs 재작성 vs 분석 vs 맥락 이어가기"가 전부 섞여서 오동작.

Phase 2에서 3축 모델로 재작성하면 **같은 cards 데이터로도 답변 품질이 한 단계 올라감**. 이게 구조적 개선의 본질.

---

## Appendix: Payload 실측 기록

2026-04-14 13:00 KST, sbtl-hub.vercel.app에서 DevTools → Network → /api/chat POST Payload:

```json
{
  "message": "왜 중요한지 설명해줘",
  "context": {
    "date": "2026.04.08",
    "region": "KR",
    "last_answer_type": "follow_up",
    "last_result_ids": [
      "https://www.businesskorea.co.kr/news/articleView.html?idxno=267322"
    ],
    "selected_item_id": "https://www.businesskorea.co.kr/news/articleView.html?idxno=267322"
  }
}
```

특이사항:
- `last_cards` 객체 배열 없음 → backend `analysis_why` 분기가 원칙상 동작 불가
- `last_answer_type: "follow_up"` → 이전 턴이 follow_up이었으므로 원본 의도 소실
- `selected_item_id` 존재하지만 backend 코드에서 읽지 않음
