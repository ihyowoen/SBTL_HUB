# Session Handoff — 2026-04-19

**이 문서는 2026-04-18 핸드오프의 업데이트.** 챗봇 탭 자체를 **"배터리 상담소"** product identity로 재구성하는 설계 pivot이 확정됨. 이전 4축 분석(C.1~C.5)은 섹션 C-legacy로 보존, 새 설계는 섹션 C에서 "상담 메타포" 중심으로 통합.

**다음 세션 시작 시:** 이 문서 + `SESSION_HANDOFF_20260418.md` (이전 기록) + `docs/CHATBOT_ARCHITECTURE.md` 순서로 읽을 것. memory stale 위험 있으니 실물 코드(`api/chat.js`, `lib/chat/*`, `src/App.jsx`, `src/story/*`) 대조 필수.

---

## 섹션 A — TL;DR (2026-04-19 기준)

1. **핵심 pivot**: 챗봇 탭 → **"배터리 상담소"** product identity로 전환. "상담" 메타포가 재미·기록·로그 세 가치의 운반체 역할.

2. **상담 메타포의 실질**: 유저가 카드를 통해 **상담을 접수**하면 → 강차장이 **검토 후 의견** → 대화 진행 → **상담 기록으로 자동 아카이브**. 세 기능이 하나의 행위로 통합.

3. **메타포가 디자인 난제를 자동 해결**:
   - "얘기하러 가기" → "**상담카드 제출**": 유저가 뭘 물을지 고민 안 해도 됨 (의뢰인 mode)
   - 유저 풍선 기만 문제 → 접수증 banner로 해결 (시스템 strip)
   - 카드 반복 문제 → 상담사는 접수된 안건을 다시 읽어주지 않음 (Role로 해결)
   - 복귀 flow → 상담은 기록되는 게 자연스러움 (메타포 레벨에서 풀림)
   - Identity 소실 → "접수" 행위 자체가 identity 강화

4. **"재미 요소는 필수"의 진짜 의미 재정의**: 재미는 **기능의 운반체**. 로그 기능을 "저장" 버튼으로 붙이면 유저 안 쓰지만, **"상담 접수"**로 wrapping하면 유저가 자연스럽게 데이터 생성. 재미가 기능을 끌고 가는 구조.

5. **이전 4축 C.1~C.4 분석은 여전히 유효**하지만, 개별 해결 대신 **상담 메타포 아래 통합 해결**. 섹션 C-legacy 참조.

6. **2026-04-18 상태 그대로 계승**: cards 273, tracker 62, faq 38, PR #64 머지, 미해결 audit 5건, D3/D4 repo root 쓰레기.

---

## 섹션 B — 실물 상태 맵 (2026-04-18에서 불변)

**변경 없음.** 2026-04-18 핸드오프 섹션 B 그대로 유효. 주요 포인트:

- `api/chat.js` 12.5KB Phase 2 5-layer orchestrator
- `lib/chat/llm.js` 14.7KB — SYSTEM_CHAT + SYSTEM_CARD_CONSULT만 실사용
- `src/App.jsx` 91.5KB monolith (Home/NewsDesk/Tracker/Webtoon/Chatbot)
- `src/story/StoryNewsItem.jsx` 9.9KB — 카드 UI 컴포넌트, 버튼 4개
- `src/story/buildCardConsultPrompt.js` 435바이트 — **재설계 대상 (이름도 바뀔 예정: `buildCardConsultContext.js`)**
- `public/data/cards.json` 481KB, 273 cards, `related` 9.5% 커버
- Vercel prod READY, GROQ_API_KEY 등록됨

상세는 SESSION_HANDOFF_20260418.md 섹션 B 참조.

---

## 섹션 C — 배터리 상담소 재설계 (상담 메타포 중심 통합 설계)

### C.0 Claire 제품 의도 (핵심 통찰)

Claire의 말 그대로: **"상담인 척하면서 재미요소도 되면서 record도 log도 되겠다."**

이 한 문장이 설계의 전부. 해체:

```
"상담인 척"           → 재미 (ceremony, ritual)
"record도"           → 유저 관심사 history (재탐색 경로)
"log도"              → Claire 분석 자산 (cards.json 품질 피드백)
```

세 기능을 **하나의 UX**로 통합. **기능 리스트를 만들면 유저 안 씀. 메타포가 행위를 이끌어야 자연스럽게 데이터가 쌓임.**

### C.1 상담 Flow (MVP)

```
STEP 1. 상담 신청
  카드 UI 버튼: "이 카드로 계속 물어보기" → [📋 상담카드 제출] 로 wording 변경
  (문구 확정 필요 — 섹션 C.6 결정 1)

STEP 2. 접수 (상담소 진입)
  transition: "접수 중..." 0.5s
  ↓
  접수증 banner (chat 상단):
  ┌─────────────────────────────┐
  │ 📋 상담 #0047 접수           │
  │ 건: LG엔솔 헝가리 ESS 전환   │
  │ EU · TOP · 2026-04-19       │
  └─────────────────────────────┘
  (포맷 확정 필요 — 섹션 C.6 결정 2)

STEP 3. 검토 (강차장 선발화)
  강차장 typing indicator 0.5-1s (검토 연출, 결정 3)
  ↓
  opener 2-3문장 + 미끼 1개 (선택지 아님)
  "접수됐어. 여기서 걸리는 건 타이밍이야 —
   EU 정책 움직임이랑 묘하게 맞물려. 우연 아닐 걸."

STEP 4. 후속
  유저 reply → 심층 답변 (related 카드 자연 인용)
  유저 무반응 → 다음 방문 시 "그 건 그 뒤에..."로 이어감
```

### C.2 기능 매트릭스 (메타포 → 구현)

| 메타포 요소 | UX 표현 | 구현 | 가치 |
|---|---|---|---|
| 상담 신청 | [📋 상담카드 제출] 버튼 | StoryNewsItem.jsx wording + dispatch | 재미(ritual 시작) |
| 접수 | 접수증 banner + ID | App.jsx chatbot tab + localStorage counter | 재미(ceremony) + 기록(id) |
| 검토 연출 | typing indicator 0.5-1s | App.jsx | 재미(micro-moment) |
| 상담사 voice | SYSTEM_CARD_CONSULT 재설계 | llm.js | 재미(personality) |
| 첫 발화 opener | Pool + rule 매칭 | cardOpenerPool.js 신규 | 재미(variation) |
| 카드 반복 금지 | 상담사 Role | llm.js rule | 품질(R4 해결) |
| 미끼 던지기 | opener 끝에 hint | llm.js + opener pool | 재미(호기심) + 연결고리 |
| 상담 기록 | localStorage consultation[] | App.jsx Phase 2 | 기록(history) |
| 재열람 | [상담 기록] 탭 | App.jsx Phase 2 | 기록(재탐색) |
| 이어서 대화 | 기록에서 reopen | App.jsx Phase 2 | 재미(연속성) |
| meta-comment | 관심사 패턴 인식 | llm.js Phase 3 | 재미(기억해주는 느낌) |
| Claire 분석 | consultation export | Phase 3 | 로그(품질 피드백) |

### C.3 Phase 분리

**Phase 1 (MVP — 기본 상담 flow)**
- StoryNewsItem 버튼 wording + dispatch
- 접수증 banner + 강차장 선발화
- buildCardConsultContext (이전 buildCardConsultPrompt 대체)
- SYSTEM_CARD_CONSULT 재설계 (상담사 Role, 카드 반복 금지, 첫 턴 짧게, 미끼)
- Opener pool 15-20개 (카테고리별)
- **localStorage consultation 객체 저장** (list UI 없어도 저장은 시작)

**Phase 2 (상담 기록 탭)**
- [상담 기록] 탭 UI
- 과거 상담 list + 재열람
- 이어서 대화 기능
- 화제 전환 선언 (새 상담 유입 시 이전 대화 맥락 언급)

**Phase 3 (고급)**
- 강차장 meta-comment (관심사 패턴)
- 상담 export (Claire 분석용 JSON)
- 카드별 상담 빈도 → cards.json 품질 피드백

**Phase 1만 해도 기록은 자동 축적.** 2는 가치를 UI로 가시화. 3은 폭발.

### C.4 재설계 원칙 (Red Team 결과)

이전 세션 enhanced red team에서 도출된 11개 결함 중 메타포로 풀리는 것:

| # | 결함 | 메타포가 풀어주는 방식 |
|---|------|---|
| R1 | 유저 풍선 기만 | 접수증 banner (시스템 strip) |
| R2 | Hook을 선택지로 만들면 Chip 회귀 | 미끼(호기심 hint)로 변경, 선택지 아님 |
| R3 | 자동 "얘기 좀 해줘"는 3단 lock 소환 | system_hint entry_mode로 대체, 유저 메시지 아님 |
| R4 | 카드 반복 문제 | 상담사 Role = 접수 안건 재요약 안 함 |
| R5 | C.1+C.2 분리 불가 | 메타포 아래 자연 통합 |
| R6 | 첫 턴 너무 길면 역효과 | 상담사는 먼저 **의견**만 (2-3문장 + 미끼) |
| R7 | 상담소 identity 소실 | 접수 행위 자체가 identity |
| R8 | 카드 pin 공간 비용 | 접수증은 대화 위로 스크롤 아웃 자연 |
| R9 | 세션 history 처리 | 화제 전환 선언 (Phase 2) |
| R10 | Opener 반복 질림 | Pool 크기 + 최근 중복 배제 localStorage |
| R11 | 복귀 flow | 상담 기록 탭이 메타포 레벨에서 해결 |

### C.5 Opener Pool 작성 방향

Rule matcher (카드 특성 → 카테고리):

```
카테고리            trigger                       샘플 voice (감각용)
─────────────────────────────────────────────────────────────────
EU policy          region=eu & cat=정책           "유럽 칼춤 또네. 타이밍이 묘한데 —"
CN/CATL            entity~catl                    "CATL 또 CATL. 이번 각도가 재밌어 —"
K-battery          entity~LG/SDI/SK온             "우리 쪽 플레이어야. 해석 두 갈래 나뉠 건데 —"
Tech/신소재        cat=기술                       "기술 건이네. 양산까지 얼마 남았을까?"
JV/M&A             keyword=해체|해지              "JV 결별은 정치 냄새 먼저인데, 여기선 경제 논리가 보여."
ESS/그리드         cat=ESS                        "ESS야. 수익성부터 갈까 입찰부터 갈까?"
SBTL-adjacent      sbtl_tag=high                  "이 건 우리 고객사야. 조심히 봐야 해."
Default            fallback                       "이 건 들고 왔네. 여기서 걸리는 건 —"
```

원칙:
- Opener는 **미끼로 끝남** (선택지 X, hint O)
- "이 카드는 X가 아니라 Y다" 패턴 금지 (Claire가 명시적으로 극혐)
- 각 카테고리 2-3개 → 총 ~15-20개
- 최근 중복 배제 localStorage (N=5 정도)
- Rule fail → Default pool

### C.6 결정 필요 (다음 세션 시작 직후)

**1. 상담 신청 버튼 wording**
- (a) "이 건으로 상담 신청"
- (b) "상담카드 제출" ← Claire 제안한 표현
- (c) "강차장한테 넘기기"
- (d) "강차장 불러"

**2. 접수증 포맷 (formal 수위)**
- (a) `📋 상담 #0047 접수 · EU/TOP · 2026-04-19` (번호 있음, 쌓이는 맛)
- (b) `📋 [LG엔솔 헝가리] 건 접수` (가볍게)
- (c) `📋 검토 요청` (최소)
- 내부 id만, UI 숨김

**3. 검토 뜸 (typing indicator)**
- 넣음 (재미 +, 약간 느림)
- 안 넣음 (빠름)

**4. 상담 ID 포맷**
- 전역 `#0047` (누적 체감, 초기엔 "텅텅해 보임" 리스크)
- 유저별 `#3` ("내 상담 3건째")
- 날짜 `4/19 상담`
- 숨김 (내부만)

**5. MVP 범위**
- Phase 1만 (접수 flow + localStorage 저장까지)
- Phase 1+2 같이 (상담 기록 탭까지 — "쌓이는 맛" 즉시 가시화)

**6. Opener pool 초안**
- Claude가 20개 뽑아서 Claire 리뷰
- 또는 Claire가 voice 감 잡아서 직접 작성

### C.7 구현 범위 (MVP, Phase 1 가정)

| 파일 | 변경 | 크기 |
|---|---|---|
| `src/story/StoryNewsItem.jsx` | "이 카드로 계속 물어보기" → "상담카드 제출"(가정). onClick = chat tab nav + dispatch consultation context | 소 |
| `src/story/buildCardConsultContext.js` | **신규** (기존 `buildCardConsultPrompt.js` 대체). consultation context 객체 반환 (카드 + related + opener_category + ticket_id) | 소 |
| `src/story/cardOpenerPool.js` | **신규**. Rule matcher + pool + 최근 중복 배제 | 중 |
| `src/App.jsx` chatbot tab | pending consultation 확인 → 접수증 banner + typing indicator + 강차장 선발화 + localStorage save | 중~대 |
| `lib/chat/llm.js` SYSTEM_CARD_CONSULT | "상담사" Role 재구성. 카드 반복 금지, 첫 턴 2-3문장 + 미끼, 3단 lock 해제 | 소~중 |
| `lib/chat/parseRequest.js` or `resolveContext.js` | consultation entry_mode 인식 (유저 메시지 아닌 card+opener 기반 turn 시작) | 중 |

**App.jsx monolith 문제 재언급**: 91.5KB 파일에 접수증/검토 연출/상담 기록 로직 추가는 monolith 문제 악화. 이 참에 **chatbot section만 `src/chatbot/Consultation.jsx`로 분리** 고려. 단, Phase 1은 monolith 유지하고 Phase 2에서 분리.

### C-legacy — 이전 4축 분석 (2026-04-18)

4축 분석 자체는 여전히 유효. 각 축의 실물 진단은 아래 그대로 보존, 해결은 상담 메타포 아래 통합:

- C.1-legacy 유입 프롬프트 → **상담카드 제출 + system_hint entry_mode**로 해결
- C.2-legacy 대답 수준 → **SYSTEM_CARD_CONSULT 상담사 Role + 관련 카드 주입**으로 해결
- C.3-legacy UI 디자인 → **접수증 banner + breadcrumb + 상담 기록 탭**으로 해결
- C.4-legacy 연결고리 → **related 필드 활용 + root_turn accumulator + 화제 전환 선언**으로 해결
- C.5-legacy 재미 요소 → **메타포 전체가 재미의 운반체**

상세 진단은 SESSION_HANDOFF_20260418.md 섹션 C 참조. 이 문서는 그 위에 **해결 방법**을 얹은 것.

---

## 섹션 D — Audit 2026-04-14 현 상태

**변경 없음.** 2026-04-18 핸드오프 섹션 D 그대로. 해결 16 / 미해결 5 / 부분 3 / 미확인 6.

상세는 SESSION_HANDOFF_20260418.md 섹션 D 참조.

---

## 섹션 E — PR #64 재평가

**변경 없음.** 2026-04-18 결정 유지: (b) ANALYSIS_PROMPTS dead code 부분 놔두기 + 상담소 재설계에 집중.

---

## 섹션 F — 다음 세션 Opening Prompt

```
SBTL_HUB 작업 이어서. 배터리 상담소 재설계 Phase 1 착수.

먼저 다음 순서로 읽기:
1. SESSION_HANDOFF_20260419.md (가장 최신, 상담 메타포 설계)
2. SESSION_HANDOFF_20260418.md (이전 세션, 4축 분석 원본)
3. docs/CHATBOT_ARCHITECTURE.md (챗봇 청사진)

Memory stale 위험 있으므로 실물 코드 대조 필수:
- api/chat.js, lib/chat/* (특히 llm.js SYSTEM_CARD_CONSULT)
- src/App.jsx chatbot tab 섹션만 target read (91KB)
- src/story/StoryNewsItem.jsx, buildCardConsultPrompt.js

오늘 세션 의제:

[PRIORITY 1] 섹션 C.6 결정 6개 Claire와 확정
  - 버튼 wording, 접수증 포맷, 검토 뜸, 상담 ID, MVP 범위, opener pool

[PRIORITY 2] 결정 확정 후 Phase 1 실장
  - buildCardConsultContext.js 신규
  - cardOpenerPool.js 신규 (pool 20개)
  - SYSTEM_CARD_CONSULT 재설계 (상담사 Role)
  - StoryNewsItem.jsx 버튼 wording + dispatch
  - App.jsx chatbot tab: 접수증 banner + typing + 강차장 선발화
  - localStorage consultation 저장 (list UI 없어도 축적 시작)

[PRIORITY 3] Phase 2 범위 결정
  - 상담 기록 탭을 Phase 1에 포함할지, 별도 할지

환경:
- GROQ_API_KEY ✅ (llama-3.3-70b-versatile, 무료)
- OPENAI/ANTHROPIC 키 없음 (Claire 명시 rejection)
- GitHub MCP 삭제 API 없음 — 삭제는 Claire 로컬 git rm

원칙 (2026-04-14 → 18 → 19 계승):
- 추측 대신 실측 (실물 코드 line-by-line)
- 야매 패치 금지, 구조적 개선 우선
- Graceful degrade (LLM 실패 시 template fallback)
- Claire product intent 우선 — 직관적으로 좋아보이는 것도 의도적으로 안 만들었을 수 있음
- 재미 요소는 덤이 아닌 필수 — 기능의 운반체
- 존재하지 않는 UI 상상 금지

어느 priority부터 갈지 Claire에게 먼저 묻고, 결정 후 실물 코드 target read부터.
```

---

## 섹션 G — 반복 원칙 (2026-04-14 → 18 계승 + 19 추가)

1. 추측 대신 실측 — 실물 코드 line-by-line
2. 야매 패치 금지 — 구조적 개선 우선
3. Graceful degrade — LLM 실패 시 template fallback
4. Claude 못 하는 것 명시 — W6 pipeline, 대량 App.jsx 수정, git rm은 Claire
5. chatbot만이 전부가 아님 — 섹션 D의 구조적 이슈도 같은 비중
6. Claire product intent 우선 — 확인 없이 구현 PR 금지
7. 재미 요소는 덤이 아닌 필수 — **기능의 운반체**로 해석 (2026-04-19 정교화)
8. 존재하지 않는 UI 상상 금지 — dead code 수정 방지
9. **메타포가 기능 리스트를 이긴다** (2026-04-19 신규) — 유저는 기능 나열에 반응하지 않음. 메타포가 행위를 이끌어야 자연스럽게 데이터·참여·재방문이 생김.

---

## 세션 종료 상태 (2026-04-19)

- HEAD: 2026-04-18 이후 이 문서 커밋
- 배포: Vercel sbtl-hub.vercel.app READY (변경 없음)
- 미해결 prod 이슈: 배터리 상담소 Phase 1 실장 (다음 세션)
- 미해결 repo 위생: D3/D4 그대로 (Claire 로컬 git rm 필요)
- 미해결 audit 미해결 5개: 그대로
- 데이터: cards 273, tracker 62, faq 38 (변경 없음)
- 설계 상태: 상담 메타포 pivot 확정. 세부 결정 6개 대기 (섹션 C.6).

끝.
