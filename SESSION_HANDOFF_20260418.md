# Session Handoff — 2026-04-18

2026-04-14 핸드오프 이후 가장 중요한 세션. 챗봇 프롬프트 Role 차등 PR (#64) 머지 후, 실제 product intent 재정렬 + 실물 코드 line-by-line 검증 + 배터리상담소 journey 재설계 의제 확정.

**다음 세션 시작 시:** 이 문서 + `SESSION_HANDOFF_20260414.md` + `docs/CHATBOT_ARCHITECTURE.md` 순서로 읽을 것. memory stale 위험 있으니 실물 코드(`api/chat.js`, `lib/chat/*`, `src/App.jsx`, `src/story/*`) 대조 필수.

---

## 섹션 A — TL;DR

1. **PR #64 "Role 차등 페르소나 + 길이 확장" 머지 완료.** 실질 효과 = SYSTEM_CHAT + SYSTEM_CARD_CONSULT만. ANALYSIS_PROMPTS(why/summary/analysis) Role 업그레이드는 **UI trigger 없는 dead code 수정**이었음.

2. **`/api/analysis` endpoint는 dead.** 구현돼있으나 App.jsx 어디서도 호출 안 함. QC_BACKLOG P1 "AI 해설/왜 중요?" 버튼은 아직 **미구현**.

3. **카드 UI 버튼은 4개뿐**: 핵심만 보면 / 강차장 콕 짚기 / 원문 ↗ / 이 카드로 계속 물어보기. 앞 2개는 **로컬 포맷 함수(`makeBriefLines`) — LLM 안 탐**. 깊은 대화는 전부 "이 카드로 계속 물어보기" → **배터리상담소(챗봇)**로 유도하는 설계 (product intent).

4. **배터리상담소 4축 모두 엉망 — patch 아닌 journey 전체 재설계 스코프.** (섹션 C 참조)

5. **재미 요소는 덤이 아닌 필수.** 재방문 동인.

6. **2026-04-14 Audit 30개 결함 현 상태**: 해결 16, 미해결 5, 부분 3, 미확인 6. (섹션 D 참조)

---

## 섹션 B — 실물 상태 맵 (2026-04-18 검증)

### Backend
- `api/chat.js` 12.5KB — Phase 2 5-layer orchestrator (parseRequest → resolveContext → retrieve → synthesize → respond). D11/D12/D13 결함 해결 설계 완료.
- `api/analysis.js` 5.8KB — Groq + deterministic fallback. **Dead endpoint (호출자 없음).**
- `api/brave.js` 1.1KB — CORS proxy. retrieve/*에서 사용 안 함 (respond.js `external_links: []` 고정).
- `api/translate.js` — **삭제 완료** ✅

### Chat library (`lib/chat/`)
- `llm.js` 14.7KB — 5개 persona prompts + TONE_RULE 공통. PR #64로 Role 차등 적용:
  - SYSTEM_CHAT: SBTL 사내 시니어 애널리스트 30+ yrs ✅ 실제 사용됨
  - SYSTEM_CARD_CONSULT: 동일 ✅ 실제 사용됨 (카드 상담 유입)
  - ANALYSIS why: MBB 파트너 ❌ dead (UI trigger 없음)
  - ANALYSIS summary: 브리핑 담당자 중립 ❌ dead
  - ANALYSIS analysis: GS/MS IB 시니어 + Newsletter EIC ❌ dead
  - FAQ_REWRITE, REPHRASE: 유틸리티 (변경 없음)
- `common.js` 10KB — hybrid fs+fetch `loadKnowledge` ✅, REGION_POLICY **hardcoded 잔존** ❌
- `parseRequest.js` 8KB — 3축 모델(action/topic/scope) + frontend hint 우선 처리
- `resolveContext.js` 4.6KB — Layer 2, 필수 context 검증
- `retrieve/{faq,news,policy,comparison,general,shared,index}.js` — topic별 분리, dispatcher 완비
  - `faq.js`: score-based matching ✅ (first-match 버그 해결)
  - `news.js`: region-aware latestCards ✅ (QC_BACKLOG P0 B 해결)
  - `shared.js`: lexical scoring + recency bonus
- `synthesize.js` 10.5KB — LLM 또는 template, graceful fallback
- `respond.js` 8.4KB — suggestions에 `hint_action` 태그 ✅ (U3 해결 기반), next_context 생성
- `scope.js` 4.5KB — 한자 region(韓/美/中/日) 추가됨 ✅, stopword 확장됨 ✅
- `suggestions.js` 1.2KB — respond.js에 중복 로직 있음
- `_deprecated/` — 옛 코드 보관 (Phase 2 정리 후)

### Frontend (`src/`)
- `App.jsx` 91.5KB — 여전히 monolith (Home/NewsDesk/Tracker/Webtoon/Chatbot 전부). **분리 안 됨** ❌
- `story/StoryNewsItem.jsx` 9.9KB — 카드 UI 컴포넌트. 버튼 4개 (위 섹션 A.3 참조)
- `story/buildCardConsultPrompt.js` 435바이트 — 상담소 유입 auto prompt 빌더. **섹션 C.1에서 재설계 대상**
- `story/normalizeCard.js` 2.1KB — 카드 필드 정규화

### Data (`public/data/`)
- `cards.json` 481KB — **273 cards**, `meta.updated: 2026-04-17`. `related` 필드 9.5% 커버 (26/273), 7개 broken ref
- `faq.json` 14KB — 38 entries. 마지막 entry "콘텐츠 허브"에 여전히 "📨뉴스레터" 포함 (App.jsx CATS에 뉴스레터 탭 없음) ❌
- `tracker_data.json` 122KB — **62 items**, 전수 2026-04-18 갱신 ✅

### Webtoon (`public/webtoon/`)
- EP.1, EP.2, BONUS.1, landing HTML 4개 파일 모두 존재 ✅

### 배포
- Vercel sbtl-hub.vercel.app production READY
- 최신 배포 commit: `ceb84196` (PR #64 merge)
- Runtime log: `/api/chat` 정상, 에러 0건, `loadKnowledge` fs 경로 성공 (`cards=273(fs)`)
- Env: GROQ_API_KEY ✅, BRAVE_KEY ✅. Anthropic/OpenAI 키 없음 (Claire 의도적 — 유료 API 금지).

---

## 섹션 C — 배터리상담소 재설계 4축 (**최우선 의제**)

Claire product intent: 카드 UX는 경량(핵심/콕짚기는 로컬 포맷), **깊은 대화는 전부 배터리상담소로 유도**해서 강차장 페르소나 + 대화 맥락 축적. 그래서 "AI 해설/왜 중요?" 같은 카드 레벨 버튼 안 만듦.

**하지만 상담소 자체의 journey가 4축 모두 엉망** — 패치 아닌 전체 재설계 필요.

### C.1 유입 프롬프트 (buildCardConsultPrompt.js)

**현재 실물**:
```js
export function buildCardConsultPrompt(card) {
  const c = normalizeCard(card);
  const lines = [
    '[카드상담]',
    '이 카드 기준으로만 설명해줘. 무슨 일인지, 왜 중요한지, 다음 체크포인트 2개만 말해줘.',
    `카드 제목: ${c.title || '-'}`,
  ];
  if (c.primaryUrl) lines.push(`카드 URL: ${c.primaryUrl}`);
  return lines.join('\n');
}
```

**문제**:
- 유저 실제 궁금증·배경·관점(투자? 기술? 경쟁사?) 들어갈 자리 없음
- 답변 구조("무슨 일 / 왜 중요 / 체크포인트 2")를 유저 대신 먼저 선언해버림
- 이게 SYSTEM_CARD_CONSULT의 3단 구성과 중복 lock → 결과 다양성 0

**재설계 방향 (초안, 확정 아님)**:
- 고정 ask 제거 → 유저가 실제로 뭘 궁금해하는지 **chip 선택 또는 자유 입력** 유도
- 카드 정보는 context로만 전달 (제목/부제/gist/관점) — 답변 구조는 강제하지 않음

### C.2 대답 수준 (SYSTEM_CARD_CONSULT)

**현재 실물** (PR #64 후):
- 3단 구조 lock: 무슨 일 / 왜 중요 / 체크포인트 2
- 5~8문장, 600 tokens
- "30년 경력 시니어" 선언만 있고 **실제 답변은 단일 카드 `fact`/`sub`/`gate` 재배치** 수준
- 다른 관련 카드 참조 없음 (cards.json `related` 필드 활용 안 함)
- SBTL 관점 자발적 언급 약함

**재설계 방향**:
- 단일 카드 fence 해제 — 관련 카드 선별 주입 (`related` 필드 + lexical)
- SBTL 관점을 "관련될 때만" 짧게가 아니라 **강차장의 자연스러운 voice로** 체화
- 3단 구조 lock 해제 → 질문 유형별 유연한 답변

### C.3 UI 디자인 (App.jsx chatbot tab — 실물 미확인)

**추정 현재 상태**:
- 일반 챗봇 버블 UI (강차장 아바타 + 답변)
- Suggestion 버튼 3개 하단
- 입력창
- **카드→상담소 진입 직후 "왜 이 카드를 들고 왔는지" anchoring UI 없음**
- 이전 답변의 카드 reference가 다음 턴에 시각적으로 이어지지 않음
- 카드 여러 장 간 연결을 보여주는 visual primitives 없음

**확인 필요**: 다음 세션 초반에 App.jsx의 Chatbot 섹션만 target read

**재설계 방향**:
- 유입 직후 anchoring 영역 (이 카드에 대해 물었어 — 카드 요약 핀)
- 답변 내 카드 reference가 mini card로 떠서 hover/click으로 연결
- 턴 간 visual continuity (누적 카드 타임라인 등)

### C.4 연결고리 (suggestions · hint_action · related 필드)

**현재 실물**:
- respond.js `suggestionsForAction(action=analyze_card)`:
  ```
  "이 카드 심층 분석해줘" → hint_action: analyze_card, topic: deep
  "관련 카드 더 보여줘" → hint_action: follow_up
  "한국어로 요약해줘" → hint_action: analyze_card, topic: summary
  ```
- `follow_up` → parseRequest → `root_turn.topic` 상속 → retrieve dispatch → **같은 topic의 lexical/region search**
- **cards.json `related` 필드(9.5% 커버) 활용 안 함**
- A→B 카드로 넘어갈 때 **왜 연결되는지** 설명 없음
- B로 analyze_card 다시 하면 A 맥락 날아감

**재설계 방향**:
- `related` 필드 + synthesize 레벨 연결 이유 생성 ("이 카드는 X와 Y 관점에서 이어져" 식 — AI 템플릿 아닌 실제 근거)
- root_turn에 카드 accumulator 추가 (turn별 selected_item_id 배열)
- Suggestion이 현재 답변·이전 카드 맥락 반영

### C.5 재미 요소 — 필수

재방문 동인. 상담소에 또 들어오게 만드는 건 통찰만으로는 부족.

**방향 (초안)**:
- 강차장 고유 voice (단순 "차분한 반말" 이상의 개성 — 비유·말버릇·관점)
- 카드 간 의외의 연결 ("아 이 건 C 카드랑 한 덩어리네" 식의 순간)
- 유저 이전 관심사 기반 수면 아래 thread 유지

---

## 섹션 D — Audit 2026-04-14 현 상태 (30개 중)

### ✅ 해결 (16)
- #2 tracker 50 stale → 62 refresh
- #3 loadKnowledge Vercel fs 실패 → hybrid fs+fetch
- #7 compose LLM 부재 → Groq synthesizeChatAnswer
- #8 intent.js follow_up/analyze 우선순위 → parseRequest 3축
- #9 matchFaq first-match → score-based
- #10 confidence.js news infinite-fallback → confidence.js 제거, used_llm 플래그로 대체
- #13 env.example VITE_BRAVE_KEY → BRAVE_KEY only + 경고
- #16 톤 4가지 혼재 → TONE_RULE 전면
- #17 vercel.json dead routes → 정리 (+ api/translate.js 삭제)
- #26 scope.js 한자 region → 韓/美/中/日 추가
- #27 compose.js c.g 검증 → isCleanGist
- Phase 2 5-layer orchestrator 전체
- retrieve 분리 (faq/news/policy/comparison/general + shared + index)
- QC_BACKLOG P0 B region-aware latestCards
- QC_BACKLOG P0 A 번역 버튼 — StoryNewsItem에 번역 버튼 아예 없음

### ❌ 미해결 (5)
- #4 tracker URL `motir.go.kr` 오타 (tracker_data.json에 여전히)
- #11 faq.json 콘텐츠 허브 entry에 "📨뉴스레터" 잔존 (App.jsx에 뉴스레터 탭 없음)
- #14 REGION_POLICY 중복 (common.js hardcoded, `public/data/region_policy.json` 미외부화)
- #15 App.jsx 91.5KB monolith (분리 안 됨)
- #28 compare regex에 "다르/구별/대조" 누락 (parseRequest.js TOPIC_PATTERNS)
- D3/D4 stale artifacts (`merge_cards_raw_payload_20260407_safe_2cards.json`, `download`) 여전 repo root 잔존 — 사용자 로컬 `git rm` 필요

### 🟡 부분 (3)
- #1 cards.json stale → 273로 덜 stale하지만 W5/W6 auto pipeline 여전히 manual
- #5 US/KR region → isRegionMatch에 `split("/")` 추가 (코드 대응), data 쪽은 search 0 확인
- #25 scope.js entity 노이즈 → stopword 확장 but topicTokens 전수 추가 로직 유지

### ❓ 미확인 (6)
- #6 App.jsx NewsDesk 검색 `c.k` 필드 포함 여부 (search_code short token 한계)
- #12 tracker AMPC `$` 인코딩 (faq.json은 정상, tracker 122KB 미스캔)
- #18 cards.json `g` 필드 잘림 잔존 (481KB 미스캔, isCleanGist 표시 레벨 방어 ✅)
- #19-24 merge_cards.py + PWA 세부
- #29 package.json engines
- #30 docs 드리프트 (신규 5개 문서 추가 — CHATBOT_ARCHITECTURE, AI_CHATBOT_REFACTOR_PLAN, AI_CHATBOT_IMPLEMENTATION_CHECKLIST, CHATBOT_TESTS, FACT_DISCIPLINE)

---

## 섹션 E — PR #64 재평가

**2026-04-18 커밋 `716067b`, 머지 커밋 `ceb84196`.**

### 실제 효과
- SYSTEM_CHAT: "사내 시니어 애널리스트 30+ yrs" Role 업그레이드 → 일반 챗봇 질문에 반영 ✅
- SYSTEM_CARD_CONSULT: 동일 Role 업그레이드 → "이 카드로 계속 물어보기" 유입 답변에 반영 ✅
- max_tokens 증가 (400→500, 450→600) → 실제 답변 길이 소폭 확장 ✅

### 의미 없는 변경 (dead code)
- ANALYSIS_PROMPTS.why: MBB 파트너 Role → **호출자 없음 (App.jsx에서 /api/analysis 호출 안 함)**
- ANALYSIS_PROMPTS.summary: 브리핑 담당자 → 동일
- ANALYSIS_PROMPTS.analysis: GS/MS IB 시니어 + Newsletter EIC → 동일

### 결정 필요
- (a) PR #64의 ANALYSIS 부분 revert
- (b) 놔두기 (나중에 UI 붙이면 자동 적용)
- (c) "AI 해설 / 왜 중요?" UI 트리거 실제로 붙이기 — 단 Claire product intent는 **카드 레벨에 이런 버튼 안 붙이는 것** (상담소로 유도)

Claire 결정: **(b) 놔두기** + 배터리상담소 journey 재설계에 집중.

---

## 섹션 F — 다음 세션 Opening Prompt

다음 세션 시작 시 아래 복붙:

```
SBTL_HUB 작업 이어서.

먼저 다음 순서로 읽기:
1. SESSION_HANDOFF_20260418.md (가장 최신, 이 문서)
2. SESSION_HANDOFF_20260414.md (이전 세션, Phase 2 진행 이력)
3. docs/CHATBOT_ARCHITECTURE.md (챗봇 청사진)

Memory는 stale 위험 있으므로 실물 코드 대조 필수:
- api/chat.js, lib/chat/* 전체
- src/App.jsx (91KB이므로 target read 권장)
- src/story/StoryNewsItem.jsx, buildCardConsultPrompt.js

오늘 세션 핵심 의제: 배터리상담소 재설계 4축 — 패치 아닌 journey 전체.
(1) 유입 프롬프트 buildCardConsultPrompt.js 재설계
(2) 대답 수준 SYSTEM_CARD_CONSULT 단일 카드 fence 해제 + 관련 카드 주입
(3) UI 디자인 App.jsx chatbot tab (실물 미확인 — 먼저 target read)
(4) 연결고리 suggestion + cards.json `related` 필드 활용 + turn accumulator

재미 요소는 덤이 아닌 필수 — 재방문 동인.

환경:
- GROQ_API_KEY 등록됨 (llama-3.3-70b-versatile, 무료)
- OPENAI/ANTHROPIC 키 없음 (유료 API 금지 — Claire 명시 rejection)
- GitHub MCP 삭제 API 없음 — 삭제 필요한 것은 Claire 로컬 git rm

오늘 할 수 있는 옵션:
[A] 4축 중 하나 선정해 설계 스케치 (추천 시작점: C.1 유입 프롬프트 — 가장 작고 영향 큼)
[B] App.jsx chatbot tab 실물 확인 (C.3 UI 재설계 선결 조건)
[C] 남은 미해결 5개 중 motir URL / compare regex 같은 작은 fix 먼저 (warm-up)
[D] PR #64 ANALYSIS_PROMPTS 부분 revert (선택 — 2026-04-18 결정은 놔두기)

어느 옵션 갈지 Claire에게 먼저 묻고, 결정 후 실물 코드 target read부터.
```

---

## 섹션 G — 반복 원칙 (2026-04-14에서 계승 + 추가)

1. **추측 대신 실측** — 문서 의존 금지, 실물 코드 line-by-line
2. **야매 패치 금지** — 구조적 개선 우선
3. **Graceful degrade** — 모든 LLM 호출은 template fallback 보유
4. **Claude 못 하는 것 명시** — W6 pipeline, 대량 App.jsx 수정, git rm은 Claire 작업
5. **chatbot만이 전부가 아님** — 섹션 D의 구조적 이슈도 같은 비중
6. **Claire product intent 우선** — "AI 해설/왜 중요?" 버튼처럼 직관적으로 좋아보이는 것도 **의도적으로 안 만들었을 수 있음**. 확인 없이 구현 PR 만들지 말 것.
7. **재미 요소는 덤이 아닌 필수** — 재방문 동인. 통찰만으로는 상담소 다시 안 옴.
8. **존재하지 않는 UI 상상 금지** — PR #64 ANALYSIS_PROMPTS 같은 dead code 수정 방지.

---

## 세션 종료 상태 (2026-04-18)

- HEAD: `ceb84196` (PR #64 merge) 이후 이 문서 커밋
- 배포: Vercel sbtl-hub.vercel.app READY
- 미해결 prod 이슈: 배터리상담소 4축 전면 재설계 (다음 세션)
- 미해결 repo 위생: D3 (`merge_cards_raw_payload_20260407_safe_2cards.json`), D4 (`download`) — Claire 로컬 `git rm` 필요
- 미해결 audit 미해결 5개: motir URL / faq 콘텐츠 허브 / REGION_POLICY 외부화 / App.jsx monolith / compare regex "다르"
- 데이터: cards 273 (2026-04-17), tracker 62 (2026-04-18), faq 38

끝.
