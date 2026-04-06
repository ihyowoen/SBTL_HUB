# AI Chatbot Implementation Checklist

## 목적

이 문서는 `docs/AI_CHATBOT_REFACTOR_PLAN.md`를 실제 구현 단계로 옮길 때,
무엇을 어떤 순서로 바꿔야 하는지에 대한 실전 체크리스트다.

이 문서는 아이디어 문서가 아니라 **실행 문서**다.
즉, 구현자는 아래 항목을 위에서부터 차례대로 처리하면 된다.

---

## 최종 목표

현재 프론트에 과도하게 몰려 있는 챗봇 로직을 줄이고,
새로운 `api/chat.js`를 중심으로 아래 흐름을 서버 오케스트레이션으로 재구성한다.

```text
user question
-> api/chat
-> intent detection
-> scope extraction
-> internal retrieval
-> confidence scoring
-> fallback decision
-> evidence bundle
-> response composition
-> frontend rendering
```

---

## Phase 0 — 구현 전 원칙 고정

### must keep
- 현재 UI 렌더링 경험은 가능한 유지
- 카드 렌더링 형식은 되도록 깨지지 않게 유지
- 전체 앱을 한 번에 갈아엎지 않기
- incremental refactor 우선

### must avoid
- 프론트/백엔드에 동일한 판단 로직 중복
- low-confidence internal answer를 단정적으로 출력
- Brave 검색을 계속 수동 옵션으로만 두기
- answer shape를 매 응답마다 흔들리게 두기

---

## Phase 1 — `/api/chat.js` 신설

## 목표
프론트에 있던 챗봇 판단 로직을 서버로 옮길 첫 진입점을 만든다.

### 작업 항목
- [ ] `api/chat.js` 파일 생성
- [ ] POST request만 허용
- [ ] request body 기본 shape 정의
- [ ] response shape 고정
- [ ] 에러 응답 shape 통일

### request 권장 shape
```json
{
  "message": "사용자 입력",
  "context": {
    "last_answer_type": "news",
    "selected_item_id": "card-123",
    "last_result_ids": ["card-123", "card-456"],
    "region": "US",
    "date": "2026-04-06"
  }
}
```

### response 권장 shape
```json
{
  "answer": "최종 답변",
  "answer_type": "news|policy|compare|summary|follow_up|general",
  "source_mode": "internal|external|hybrid",
  "confidence": 0.0,
  "cards": [],
  "external_links": [],
  "suggestions": [],
  "debug": {
    "fallback_triggered": false,
    "confidence_bucket": "high"
  }
}
```

### acceptance criteria
- [ ] frontend가 이 응답만 받아도 렌더링 가능
- [ ] `answer_type`, `source_mode`, `confidence`가 항상 내려옴
- [ ] error response도 일관적임

---

## Phase 2 — intent / scope 분리

## 목표
질문 분류와 검색 준비 단계를 분리한다.

### helper module 권장
- `lib/chat/intent.js`
- `lib/chat/scope.js`

### intent categories
- [ ] news
- [ ] policy
- [ ] compare
- [ ] summary
- [ ] follow_up
- [ ] general

### scope extraction 항목
- [ ] region
- [ ] date
- [ ] entity/company
- [ ] topic
- [ ] explicit external-search intent

### acceptance criteria
- [ ] intent 로직이 App.jsx 밖에 있음
- [ ] scope extraction이 retrieval과 독립적으로 동작
- [ ] 디버그 시 intent/scope를 각각 확인 가능

---

## Phase 3 — internal retrieval 서버 이동

## 목표
현재 프론트에 있는 카드 검색 로직을 서버에서 담당하게 만든다.

### helper module 권장
- `lib/chat/retrieval.js`
- `lib/chat/ranking.js`

### retrieval input
- message
- intent
- scope(region/date/entity/topic)
- available data(cards, faq, tracker, policy)

### ranking factors (first pass)
- [ ] title lexical score
- [ ] subtitle score
- [ ] gist score
- [ ] keyword overlap score
- [ ] region alignment bonus
- [ ] date alignment bonus
- [ ] recency bonus
- [ ] signal strength bonus
- [ ] exact entity bonus

### acceptance criteria
- [ ] App.jsx 내 `searchCards` 의존도가 줄어듦
- [ ] retrieval 결과 top-k를 서버에서 반환 가능
- [ ] ranking factor를 디버그 가능

---

## Phase 4 — confidence scoring 추가

## 목표
"답할 수 있나"를 판단하는 layer를 추가한다.

### helper module 권장
- `lib/chat/confidence.js`

### score inputs
- [ ] top result score
- [ ] top1 vs top2 gap
- [ ] result count
- [ ] explicit freshness demand 여부
- [ ] region/date mismatch 여부
- [ ] follow-up continuity 여부

### recommended buckets
- [ ] high: >= 0.80
- [ ] medium: 0.55 ~ 0.79
- [ ] low: < 0.55

### acceptance criteria
- [ ] response에 confidence 포함
- [ ] low confidence 시 same-path answer 금지
- [ ] fallback 분기가 confidence 기반으로 작동

---

## Phase 5 — automatic fallback

## 목표
internal retrieval이 약하면 자동으로 external 또는 hybrid mode로 넘어간다.

### helper module 권장
- `lib/chat/fallback.js`

### fallback trigger conditions
- [ ] low confidence
- [ ] user asked for latest / real-time / original article
- [ ] internal coverage insufficient
- [ ] no strong region/date aligned evidence

### modes
- [ ] internal only
- [ ] external only
- [ ] hybrid internal + external

### acceptance criteria
- [ ] Brave search가 manual-only가 아님
- [ ] fallback 여부가 response debug에 보임
- [ ] external fallback 이유 설명 가능

---

## Phase 6 — answer composition 고정

## 목표
질문 타입별 답변 형식을 통일한다.

### helper module 권장
- `lib/chat/compose.js`
- `lib/chat/suggestions.js`

### formats
#### news
- [ ] 한 줄 결론
- [ ] 핵심 의미 2~3문장
- [ ] 관련 카드 2~3장
- [ ] 필요 시 external links

#### policy
- [ ] 정책 개요
- [ ] 왜 중요한지
- [ ] 다가오는 일정
- [ ] watchpoints

#### compare
- [ ] 한 줄 결론
- [ ] 차이 3개
- [ ] implications
- [ ] 관련 카드

#### summary
- [ ] 3줄 요약
- [ ] deeper dive entry

#### follow_up
- [ ] 직전 선택 항목 기준 재답변
- [ ] ambiguity 있으면 먼저 좁히기

### acceptance criteria
- [ ] answer shape 흔들림 감소
- [ ] 카드/링크 렌더링이 일관적
- [ ] suggestions 생성 규칙이 중앙화됨

---

## Phase 7 — frontend ChatBot slimming

## 목표
App.jsx 안의 ChatBot을 UI shell 수준으로 줄인다.

### 프론트가 남겨야 할 것
- [ ] input state
- [ ] message list rendering
- [ ] card rendering
- [ ] link rendering
- [ ] suggestion button rendering
- [ ] context state 최소 보관

### 프론트에서 제거해야 할 것
- [ ] intent classification
- [ ] retrieval core logic
- [ ] fallback decision
- [ ] response composition
- [ ] 복잡한 follow-up routing

### acceptance criteria
- [ ] ChatBot component 길이/복잡도 현저히 감소
- [ ] backend response contract 중심 렌더링으로 전환
- [ ] regression 없이 기존 UX 유지

---

## Phase 8 — policy context 분리

## 목표
정책 지식을 코드 상수에서 데이터 파일로 이동한다.

### 새 파일 제안
- `public/data/policy_context.json`

### 권장 필드
- [ ] region
- [ ] title
- [ ] policies[]
- [ ] why
- [ ] watchpoints[]
- [ ] sources[]
- [ ] last_updated
- [ ] confidence

### acceptance criteria
- [ ] App.jsx에서 하드코딩 policy 상수 제거 시작
- [ ] stale policy 설명 위험 감소
- [ ] policy answer가 data-driven 구조로 이동

---

## Phase 9 — `/api/analysis.js` 다음 단계

## 목표
single-card 기반 분석에서 evidence-bundle 기반 분석으로 이동한다.

### next input shape
```json
{
  "question": "사용자 질문",
  "mode": "why|summary|analysis",
  "primary_card": {...},
  "support_cards": [{...}, {...}],
  "policy_context": {...}
}
```

### 개선 포인트
- [ ] cross-card reasoning
- [ ] watchpoint 품질 향상
- [ ] 단일 카드 재문장화에서 탈피
- [ ] fallback 템플릿도 evidence-aware하게 개선

---

## 테스트 체크리스트

### retrieval
- [ ] 표현만 바꾼 같은 질문에도 유사 결과가 나온다
- [ ] region/date 언급 시 더 정확한 카드가 올라온다
- [ ] 약한 카드가 강한 카드보다 앞서지 않는다

### fallback
- [ ] 최신 기사 요청 시 필요하면 external/hybrid로 간다
- [ ] internal 근거가 약하면 hedge 또는 fallback이 작동한다

### follow-up
- [ ] “그 기사” / “두 번째” / “아까 그거” 문맥이 개선된다
- [ ] ambiguity 있을 때 잘못 단정하지 않고 좁혀준다

### UX
- [ ] source_mode가 이해 가능하다
- [ ] cards / external_links / suggestions가 안정적으로 렌더링된다
- [ ] answer style이 덜 흔들린다

---

## red-team failure cases

다음 실패 케이스가 남아 있으면 구현이 아직 덜 된 것이다.

- [ ] internal 결과가 약한데 자신있게 답한다
- [ ] Brave fallback이 수동일 때만 된다
- [ ] 질문 타입에 따라 answer shape가 들쭉날쭉하다
- [ ] App.jsx와 api/chat.js에 비슷한 로직이 동시에 남아 있다
- [ ] policy 답변이 stale data를 확신형으로 말한다
- [ ] analysis가 여전히 카드 한 장 문구 재가공 수준이다

---

## Copilot에 바로 줄 구현 지시 요약

```text
Implement the chatbot refactor in safe phases.

Phase 1:
- create `api/chat.js`
- define stable request/response contracts
- move intent/scope/retrieval/confidence/fallback/composition out of `src/App.jsx`
- keep frontend as rendering shell

Phase 2:
- add hybrid internal retrieval scoring
- add automatic Brave fallback on low confidence
- stabilize answer templates by question type

Phase 3:
- move policy knowledge out of App.jsx into data file
- prepare `/api/analysis.js` for evidence-bundle input

Important:
- do not rewrite everything at once
- do not duplicate backend and frontend logic
- do not return low-confidence internal results as authoritative
- keep response shape stable for UI rendering
```

---

## 최종 한 줄

이 구현의 핵심은 더 좋은 문장을 뽑는 것이 아니라,

**더 좋은 답변 파이프라인을 만드는 것**이다.
