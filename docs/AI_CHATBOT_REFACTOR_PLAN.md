# AI Chatbot Refactor Plan (Enhanced Red-Team Version)

## 0. 문서 목적

이 문서는 SBTL_HUB의 AI 챗봇이 왜 아직도 "바보같이" 느껴지는지 냉정하게 해부하고,
무엇을 어떤 순서로 바꿔야 실제로 더 똑똑한 제품처럼 느껴지게 되는지를 정리한 설계 문서다.

이 문서는 단순 아이디어 모음이 아니다.
아래 네 가지를 동시에 다룬다.

1. 현재 구조의 핵심 결함
2. 목표 아키텍처
3. 단계별 구현 우선순위
4. Copilot/구현자에게 줄 수 있는 명시적 작업 지시

---

## 1. 현재 상태 한 줄 진단

현재 SBTL_HUB의 챗봇은 **AI 비서**라기보다,
**프론트엔드에 많은 규칙이 박혀 있는 카드 검색기 + 단일 카드 해설기**에 가깝다.

즉, 겉으로는 챗봇처럼 보이지만,
실제로는 아래가 섞여 있다.

- 질문 분류
- 지역/날짜 감지
- 내부 카드 검색
- 외부 기사 검색
- 후속 질문 처리
- 정책 설명
- 카드 기반 응답 조립
- suggestion 생성

이 모든 것이 프론트의 `ChatBot` 내부에 과도하게 몰려 있으면,
부분 개선을 할수록 전체 로직은 더 꼬인다.

---

## 2. Enhanced Red-Team Audit

## 2-1. 가장 큰 구조적 문제

### 문제 A. 오케스트레이션이 프론트에 있다
현재 챗봇의 핵심 두뇌가 `src/App.jsx` 안에 과도하게 집중되어 있다.

이 구조의 문제:
- intent / retrieval / fallback / answer composition이 강하게 결합됨
- 디버깅이 어려움
- 테스트가 어려움
- 개선할수록 회귀(regression) 위험이 커짐
- 같은 판단 로직이 여러 군데에서 암묵적으로 중복되기 쉬움

### 문제 B. Retrieval 품질이 낮다
현재 내부 검색은 카드 title/sub/gist/keywords에 대한 문자열 기반 매칭 비중이 높다.

이 구조의 문제:
- 같은 뜻 다른 표현을 잘 못 잡음
- entity 정규화가 약함
- relevance보다 keyword hit 수가 더 크게 작동할 수 있음
- 강한 카드가 묻히고, 쉬운 카드가 과대 노출될 수 있음

### 문제 C. Confidence layer가 없다
현재 답변 파이프라인에는
"내가 이 질문을 얼마나 잘 이해했는가"
"지금 찾은 카드가 충분히 강한가"
를 평가하는 explicit confidence gate가 없다.

이 구조의 문제:
- 애매한 internal 결과를 자신 있게 말함
- बाह부 검색으로 넘어가야 하는데 내부 카드 몇 개를 대충 보여줌
- 사용자는 "모르는 걸 아는 척한다"고 느끼게 됨

### 문제 D. External fallback이 약하다
현재 Brave 검색은 수동 전환의 비중이 높고,
외부 결과를 단순히 보여주는 성격이 강하다.

이 구조의 문제:
- internal retrieval이 약해도 자동 구제가 안 됨
- external results를 relevance/신뢰도 기준으로 재정렬하지 않음
- 사용자 입장에서는 "찾을 수 있는 것도 못 찾는 봇"처럼 느껴짐

### 문제 E. analysis API가 single-card 기반이다
현재 `/api/analysis`는 본질적으로 카드 1장만 보고 why/summary/analysis를 생성한다.

이 구조의 문제:
- cross-card reasoning이 안 됨
- 맥락 연결이 약함
- 카드 문안 품질에 지나치게 의존함
- fallback 시 상투적인 지역별 설명문이 나오기 쉬움

### 문제 F. 정책 지식이 코드 내부에 하드코딩되어 있다
정책 설명용 region policy 지식이 앱 코드 안에 있으면,
업데이트 누락 시 오래된 설명이 자신 있게 출력될 위험이 크다.

---

## 2-2. 제품 관점에서 체감되는 증상

사용자는 아래와 같은 순간에 "바보같다"고 느낀다.

1. 질문을 조금만 다르게 표현해도 못 알아듣는다.
2. 관련은 있지만 정답은 아닌 카드들을 보여준다.
3. 최신 이슈를 물었는데 내부 카드만 고집한다.
4. 후속 질문에서 문맥을 안정적으로 못 이어간다.
5. AI 해설이 깊이 있는 분석이 아니라 문장 재가공처럼 느껴진다.
6. 정책 설명이 깔끔해 보여도 실제론 고정문구처럼 느껴진다.

즉 문제는 모델 성능 이전에,
**오케스트레이션 + retrieval + confidence + state management**에 있다.

---

## 3. 리팩터링 목표

## Goal 1. 프론트는 renderer, 서버는 orchestrator
프론트는 입력/출력 렌더링에 집중하고,
질문 해석과 답변 조립은 서버에서 담당한다.

## Goal 2. retrieval 품질 향상
단순 lexical match에서 벗어나,
질문 의도와 evidence quality를 같이 본다.

## Goal 3. low-confidence 답변 금지
애매한 internal answer를 authoritative하게 말하지 않는다.
대신 external fallback 또는 narrowing question으로 간다.

## Goal 4. single-card 답변에서 evidence-bundle 답변으로 이동
primary card + support cards + policy context + optional external links를 묶어서 답한다.

## Goal 5. answer shape 고정
똑똑함은 reasoning만이 아니라 **일관된 answer format**에서 온다.

---

## 4. Target Architecture

```text
User Input
  -> /api/chat
      -> intent classification
      -> scope extraction (region/date/entity/topic)
      -> internal retrieval (cards.json / faq / tracker / policy context)
      -> confidence scoring
      -> fallback decision
         -> internal only
         -> hybrid internal + external
         -> external search
      -> evidence bundle construction
      -> response composition
      -> suggestions generation
  -> frontend renderer
```

### 프론트 역할
- 텍스트 입력
- 답변 렌더링
- 카드 렌더링
- 외부 링크 렌더링
- suggestion 버튼 렌더링
- 세션 표시

### 서버 역할
- 질문 해석
- evidence search
- confidence 판단
- fallback 선택
- answer generation

---

## 5. 권장 파일 구조

```text
api/
  brave.js
  analysis.js
  chat.js

lib/chat/
  intent.js
  scope.js
  retrieval.js
  confidence.js
  fallback.js
  compose.js
  suggestions.js
  followup.js
  ranking.js

public/data/
  cards.json
  faq.json
  tracker_data.json
  policy_context.json
```

설계 원칙:
- chat orchestration은 `api/chat.js`
- pure helper logic는 `lib/chat/*`
- data는 `public/data/*` 또는 별도 관리 data 파일

---

## 6. `/api/chat` 응답 스키마

```json
{
  "answer": "최종 한국어 답변",
  "answer_type": "news|policy|compare|summary|follow_up|general",
  "source_mode": "internal|external|hybrid",
  "confidence": 0.84,
  "reasoning_basis": {
    "intent": "news",
    "region": "US",
    "date": "2026-04-06",
    "used_internal_cards": 3,
    "used_external_links": 0,
    "fallback_triggered": false
  },
  "cards": [],
  "external_links": [],
  "suggestions": []
}
```

이 응답 shape는 가능한 한 안정적으로 유지한다.
프론트는 이 contract를 기준으로만 렌더링한다.

---

## 7. Core Logic Design

## 7-1. Intent classification
질문을 최소 아래 타입으로 나눈다.

- `news`
- `policy`
- `compare`
- `summary`
- `follow_up`
- `general`

주의:
현재처럼 단순 regex 분기만으로는 한계가 있다.
초기에는 deterministic rule로 가더라도,
나중에 confidence-aware classification으로 확장 가능한 구조여야 한다.

## 7-2. Scope extraction
질문에서 아래를 뽑는다.

- region
- date
- company/entity
- topic
- explicit external-search intent
- whether the question is follow-up to previous answer

중요:
질문 해석과 검색은 분리해야 한다.
현재처럼 한 함수 안에서 동시에 처리하면 디버깅이 어려워진다.

## 7-3. Internal retrieval
retrieval은 최소한 아래 신호를 함께 고려한다.

- title match
- subtitle match
- gist match
- keyword match
- region alignment
- date alignment
- freshness
- signal strength
- source quality (가능하다면 later phase)

## 7-4. Confidence scoring
confidence는 binary가 아니라 score 기반으로 본다.

예시:
- `>= 0.80` → internal answer 가능
- `0.55 ~ 0.79` → internal answer 가능하지만 hedge 필요 / hybrid 고려
- `< 0.55` → external fallback 또는 clarification

## 7-5. Fallback decision
fallback은 수동 버튼이 아니라 로직 단계여야 한다.

조건 예시:
- top result score가 낮다
- top1/top2 차이가 너무 작다
- 질문이 최신/실시간/원문/기사 탐색 성격이다
- 내부 cards coverage가 부족하다
- 정책 정보가 너무 오래되었다

## 7-6. Evidence bundle
answer는 single evidence가 아니라 bundle을 사용한다.

권장 구성:
- primary card 1
- support cards 2~3
- optional tracker item
- optional policy snippet
- optional brave links 1~3

## 7-7. Response composition
answer는 question type별로 정해진 template를 쓴다.

---

## 8. Answer Templates

### A. News
구성:
1. 한 줄 결론
2. 핵심 의미 2~3문장
3. 관련 카드 2~3장
4. 필요 시 external links

### B. Policy
구성:
1. 정책 개요
2. 왜 중요한지
3. 다가오는 일정
4. watchpoints

### C. Compare
구성:
1. 한 줄 결론
2. 차이 3개
3. implications
4. 관련 카드

### D. Summary
구성:
1. 3줄 요약
2. 더 볼 카드
3. deeper dive suggestion

### E. Follow-up
구성:
1. 직전 선택 항목 기준 재답변
2. ambiguity 있으면 좁혀주기
3. 관련 추가 evidence 제시

원칙:
**answer shape는 흔들리지 않게 유지한다.**

---

## 9. `/api/analysis` 개선 방향

현재 analysis endpoint는 single-card input 위주다.
다음 단계에서는 evidence bundle input으로 확장해야 한다.

### 현재 입력
```json
{
  "card": {...},
  "mode": "why|summary|analysis"
}
```

### 목표 입력
```json
{
  "question": "사용자 질문",
  "mode": "why|summary|analysis",
  "primary_card": {...},
  "support_cards": [{...}, {...}],
  "policy_context": {...}
}
```

효과:
- 카드 재문장화가 아니라 reasoning-like output 가능
- cross-card implication 연결 가능
- watchpoints 품질 개선

---

## 10. Policy knowledge 분리

현재 하드코딩 정책 설명은 별도 data file로 분리하는 것이 맞다.

예:
`public/data/policy_context.json`

권장 필드:
- region
- title
- policies[]
- why
- watchpoints[]
- sources[]
- last_updated
- confidence

원칙:
정책 설명은 코드 상수라기보다 **관리 가능한 지식 데이터**가 되어야 한다.

---

## 11. Retrieval 강화 제안

초기 단계에서는 full semantic search까지 안 가더라도,
아래 조합으로 충분히 품질을 많이 올릴 수 있다.

### Phase 1 hybrid scoring
- lexical score
- region/date boost
- recency boost
- signal strength boost
- keyword overlap score
- exact entity bonus

### Phase 2 richer ranking
- alias normalization
- entity extraction
- topic clusters
- similarity embedding layer (later)

주의:
처음부터 임베딩으로 과하게 가지 말고,
지금은 **confidence-aware deterministic ranking**만 해도 체감 개선이 크다.

---

## 12. Follow-up state redesign

현재 follow-up는 brittle rule 기반에 머물 가능성이 높다.

최소한 상태는 아래처럼 분리해 갖고 가야 한다.

```json
{
  "last_answer_type": "news",
  "selected_item_id": "card-123",
  "last_result_ids": ["card-123", "card-456"],
  "region": "US",
  "date": "2026-04-06",
  "ambiguity_flag": false
}
```

효과:
- "그 기사"
- "두 번째"
- "그거 왜 중요해"
- "같은 주제로 더"
같은 follow-up 품질이 크게 좋아진다.

---

## 13. Implementation Priority

## P0 — must do first
1. `api/chat.js` 신설
2. frontend `ChatBot` logic를 UI shell로 축소
3. intent/scope/retrieval/confidence/fallback/composition 분리
4. low-confidence internal answer를 authoritative하게 출력하지 않도록 변경

## P1 — high impact
5. internal retrieval hybrid scoring 도입
6. automatic brave fallback 도입
7. answer templates 고정
8. policy context data 분리

## P2 — next wave
9. `/api/analysis` evidence-bundle 확장
10. source quality / trust ranking 추가
11. debug mode / telemetry 추가
12. semantic retrieval or embedding layer 검토

---

## 14. What NOT to do

다음은 지금 하면 안 되는 것들이다.

### 금지 1. 프론트 로직에 기능을 더 덧대기
이건 상태를 더 복잡하게 만들 뿐이다.

### 금지 2. 모델만 바꾸고 구조는 그대로 두기
문제의 핵심은 모델보다 orchestration이다.

### 금지 3. Brave 검색을 계속 수동 모드에만 묶어두기
low confidence 시 자동 fallback이 필요하다.

### 금지 4. single-card 분석을 AI 고도화라고 착각하기
single-card analysis는 깊이 한계가 명확하다.

### 금지 5. 정책 지식을 계속 App.jsx 안에 두기
운영 누수와 stale answer 위험이 커진다.

---

## 15. Success Criteria

리팩터링 성공 기준은 아래다.

1. 사용자 질문 표현이 조금 달라도 관련 카드가 더 안정적으로 나온다.
2. internal coverage가 약한 질문에서 auto fallback이 작동한다.
3. follow-up 답변이 문맥을 더 잘 잇는다.
4. AI 해설이 카드 문구 재가공이 아니라 맥락형 답변처럼 느껴진다.
5. 프론트 코드가 훨씬 얇아진다.
6. 디버깅 포인트(intent/retrieval/confidence)가 분리된다.

---

## 16. Copilot Prompt (Implementation)

```text
You are refactoring the chatbot architecture of SBTL_HUB.

Goal:
Move chatbot intelligence out of `src/App.jsx` into a new server-side orchestrator endpoint `api/chat.js`, while preserving current UI behavior as much as possible.

Problems to solve:
1. ChatBot logic in App.jsx is monolithic.
2. Intent classification, internal card retrieval, external Brave fallback, follow-up resolution, and response composition are mixed together.
3. The bot feels unintelligent because retrieval is brittle and response shapes are inconsistent.
4. `/api/analysis.js` currently works on a single-card basis and should later support evidence bundles.

Implement first:
1. Create `api/chat.js`
2. Move the following responsibilities from frontend to backend:
   - intent classification
   - region/date/topic/entity extraction
   - internal retrieval from cards.json / faq / tracker / policy context
   - confidence scoring
   - automatic Brave fallback on low confidence
   - response composition
   - suggestions generation
3. Keep the frontend ChatBot as a rendering shell only.
4. Preserve current rendering format where possible.
5. Return a stable response shape:

{
  "answer": "...",
  "answer_type": "news|policy|compare|summary|follow_up|general",
  "source_mode": "internal|external|hybrid",
  "confidence": 0.0,
  "cards": [],
  "external_links": [],
  "suggestions": []
}

Implementation requirements:
- Refactor incrementally.
- Do not rewrite the whole app at once.
- Do not duplicate logic in frontend and backend.
- Prefer deterministic logic first.
- Make fallback explicit and debuggable.
- Keep code modular and readable.
- Add helper modules if useful.
- Preserve backward compatibility where reasonable.

Enhanced red-team requirements:
- Isolate brittle logic currently embedded in App.jsx.
- Do not keep Brave search manual-only.
- Do not return low-confidence internal answers as authoritative.
- Make answer shape stable so UI can render consistently.
- Add clear comments explaining orchestration flow.

Deliverables:
1. `api/chat.js`
2. minimal frontend changes in `src/App.jsx`
3. helper modules if added
4. short architecture explanation
5. explicit note on next follow-up work for `/api/analysis.js`
```

---

## 17. Final Recommendation

지금 가장 효과 큰 개선은 모델 교체가 아니라,

**프론트 규칙봇 -> 서버 오케스트레이터 전환**

이다.

즉 다음 스프린트의 핵심 목표는 아래 한 줄로 정리된다.

> `App.jsx` 안의 챗봇 두뇌를 `/api/chat`으로 분리하고,
> retrieval + confidence + fallback + answer composition을 독립 레이어로 재구성한다.
