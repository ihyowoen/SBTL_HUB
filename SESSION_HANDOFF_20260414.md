# Session Handoff — 2026-04-14

오늘 세션 마무리 정리. 다음 세션이 바로 이어갈 수 있도록.

---

## 오늘 한 일 요약

챗봇("강차장")이 stupid했던 원인을 구조적으로 진단하고, 긴급 수정 + 아키텍처 재설계 문서까지 마쳤다. Phase 2(backend 재작성) + Phase 3(App.jsx) 착수만 남음.

---

## 오늘 Commit 목록 (시간순 13개)

| # | SHA | 내용 | 종류 |
|---|---|---|---|
| 1 | `8c8c6b6` | ENHANCED_RED_TEAM_FULLSTACK_AUDIT_20260414.md — 30개 결함 진단 | 문서 |
| 2 | `70bd7c5` | FIX_PROPOSAL_20260414.md — 36건 → 7 quick + 2 diag + 9 structural | 문서 |
| 3 | `1fac400` | F1~F3 quick wins — .gitignore 하드닝, .env.example 신설, vercel.json dead route 제거 | 수정 |
| 4 | `4932ec4` | D1 진단 로그 — loadKnowledge cwd/length 측정 | 디버그 |
| 5 | `7b879ba` | **S1 hybrid fs+fetch loadKnowledge** — "내부 카드 못 읽어" 해결 🔥 | 핵심 수정 |
| 6 | `c67bb5c` | retrieval.js 전면 재작성 — news_meta, matchFaq 스코어, isRegionMatch 확장 | 핵심 수정 |
| 7 | `15c793e` | compose.js news 분기 — date_mode 반영, 날짜 태그, isCleanGist | 수정 |
| 8 | `9bba7dc` | scope.js — 어제/그제/내일/모레/N일전/美中日韓 파싱 + stopword 확장 | 수정 |
| 9 | `b024e28` | **S2 Groq LLM 주입** — synthesizeChatAnswer + synthesizeCardAnalysis | 핵심 수정 |
| 10 | `13732d7` | 톤 통일 — compose 이모지/불릿 제거, policy rewrite 추가 | 수정 |
| 11 | `d6e6930` | TONE_RULE 강화 — CJK 한자 hallucination 방지 + g 필드 반말 변환 명시 | 수정 |
| 12 | `d8e4bd2` → `a97185e` → `8a3eade` | **CHATBOT_ARCHITECTURE.md** — 3개 payload 측정 기반 재설계 스펙 | 문서 |

---

## 해결된 것 (체감 개선)

### 🔥 P0 — 심각한 버그
- **내부 카드 못 읽음** (S1 fs+fetch): 사용자 체감 가장 큰 원인. 해결 확인.
- **"오늘 뉴스"가 과거 뉴스 반환** (retrieval + compose): 최신 가용 날짜로 솔직히 fallback. 해결.
- **"어제 뉴스" 미지원** (scope 확장): 상대 날짜 전부 파싱. 해결.
- **챗봇 답변이 템플릿 문자열** (S2 Groq 주입): LLM 기반 맥락 답변. 해결.
- **톤 혼재 (존댓말/반말/기사체)** (TONE_RULE + rewriteToCasual): 반말 통일. 해결.

### 🧹 P1 — 정리
- `.gitignore` .env 패밀리 미포함
- `.env.example` 부재 (실제로는 파일 자체가 repo에 없었음)
- `vercel.json` dead rewrite 3개
- tracker URL 오타 (F4 — 다음 tracker 업데이트에 bundle)

---

## 해결 안 된 것 (Phase 2+ 대상)

### 구조적 결함 (`docs/CHATBOT_ARCHITECTURE.md` 참조)

| # | 결함 | 우선순위 |
|---|---|---|
| D1 | frontend가 response `cards` 객체를 저장 안 함 → 다음 요청에 URL만 | P0 |
| D2 | `last_answer` 본문 전송 안 함 → rephrase 불가 | P0 |
| D3 | backend가 `selected_item_id` 무시 | P1 |
| D4 | `last_answer_type` 매 턴 덮어써짐 | P1 |
| D5 | intent.js regex linear — "feoc"가 policy로 오분류 | P1 |
| D6 | follow_up이 lexical + latestCards fallback | P0 |
| D7 | FAQ/Policy 분기가 intent보다 먼저 결정 | P2 |
| D8 | context 참조가 analysis_* 3개 intent로만 제한 | P1 |
| D9 | "왜 중요한지 설명해줘" → 응답 `answer_type: follow_up` (코드상 analysis_why여야 함). **미스터리** | P0 조사 |
| D10 | confidence 0.48 + fallback_triggered: true인데 정상 답변 — flag 의미 불명 | P1 조사 |
| **D11** | **follow_up intent가 rephrase + drill_down + 실제 follow_up 전부 삼킴** | **P0 재설계 핵심** |
| D12 | compose.js가 FAQ 응답을 `answer_type: "general"`로 마스킹 | P1 |
| D13 | FAQ rewrite + Policy rewrite 중복 LLM 호출 (1.3s 낭비) | P1 |

### 프론트엔드
- App.jsx 챗봇 호출부 Context Protocol 준수 필요 (Phase 3)
- NewsDesk 검색에 `c.k` 포함 (F5, 아직 미처리)
- 배지 이모지 (📋 🔀 TOP/HIGH) — 디자인 결정 필요

### 사용자 작업
- **cards.json W6 pipeline 실행** — 오늘 `updated: "2026.04.13"` 9일 stale. triage pipeline 로컬 실행 필요. Claude 불가.
- **cards.json 편집 정리 (F6)**: Jackery 세일 카드, ESS 골드러시 중복 2장, URL 공란 죽도 카드 삭제. W6 merge에 포함.
- **Manual cleanup**: `download` 파일 + `merge_cards_raw_payload_20260407_safe_2cards.json` 삭제
  ```bash
  git pull
  git rm download merge_cards_raw_payload_20260407_safe_2cards.json
  git commit -m "chore: cleanup stale artifacts"
  git push
  ```

---

## 환경 상태 체크

| 항목 | 상태 |
|---|---|
| Vercel 배포 | 정상 — sbtl-b405khdc2-ihyowoens-projects.vercel.app |
| `GROQ_API_KEY` env | **등록됨** (VITE_ prefix 없음, 확인됨) |
| `BRAVE_KEY` env | 등록됨 |
| `OPENAI_API_KEY` env | 미등록 (사용 안 함 확정) |
| `ANTHROPIC_API_KEY` env | 미등록 (유료 — 사용자 rejection) |
| cards.json | 337 cards, 2026.04.13 기준 (9일 stale) |
| faq.json | 38 entries (이전 40에서 2 감소 — 확인 필요) |
| tracker_data.json | 59 items (이전 50에서 9 증가 — 최근 업데이트됨) |
| loadKnowledge 소스 | `fs` (Vercel 번들에 public/data 포함됨, fetch fallback은 backup으로만) |

---

## 주요 파일 현재 상태

### Backend (수정 완료)
- `api/chat.js` — 5-layer 재작성 대상 (Phase 2)
- `api/analysis.js` — Groq 기반, fallback template 유지
- `lib/chat/llm.js` — TONE_RULE + synthesize* + rewriteToCasual (유지)
- `lib/chat/common.js` — hybrid fs+fetch loadKnowledge (유지)
- `lib/chat/retrieval.js` — **재작성 대상** (Phase 2)
- `lib/chat/scope.js` — 확장 완료 (유지)
- `lib/chat/intent.js` — **재작성 대상 (parseRequest.js로 교체)** (Phase 2)
- `lib/chat/compose.js` — **분리 대상 (synthesize.js + respond.js)** (Phase 2)
- `lib/chat/confidence.js` — **의미 재정의 대상** (Phase 2 조사)
- `lib/chat/fallback.js` — **흡수 대상** (Phase 2)

### Frontend (Phase 3)
- `src/App.jsx` — 챗봇 호출부 Context Protocol 맞춤 (로컬 작업 권장)

### 문서
- `docs/CHATBOT_ARCHITECTURE.md` — **Phase 2/3 청사진** 🎯
- `ENHANCED_RED_TEAM_FULLSTACK_AUDIT_20260414.md` — 원본 audit
- `FIX_PROPOSAL_20260414.md` — 7 quick + 2 diag + 9 structural
- `FIX_F1_F4_F7_NOTES.md` — 수동 작업 안내

---

## Phase 2 실행 체크리스트 (다음 세션)

### Step 0: 선결 조사 (30분)
- [ ] D9 — "왜 중요한지 설명해줘" 분류 미스터리. Vercel 최신 배포 확인 + 실제 intent.js 코드 재검증
- [ ] D10 — `confidence.js::scoreConfidence` 코드 읽고 `fallback_triggered`의 실제 의미 정의
- [ ] D13 — `api/chat.js`에서 FAQ + Policy rewrite 중복 호출 조건 확인 (intent=policy면서 retrieval.mode=faq인 edge case)
- [ ] `git log public/data/faq.json` — 40→38 감소 이력 확인

### Step 1: parseRequest 작성 (30분)
- `lib/chat/parseRequest.js` 신규
- 3축 반환: `{ action, topic, scope, raw }`
- Frontend hint 존중 (suggestion 버튼에서 `hint_action` 오면 그대로)
- Hint 없으면 rule-based (기존 intent.js 규칙 재활용)

### Step 2: resolveContext 작성 (20분)
- `lib/chat/resolveContext.js` 신규
- action별 필수 context 검증
- 부족 시 `{ clarification: "..." }` 반환 (Layer 5에서 그대로 passthrough)

### Step 3: retrieve/* 분리 (30분)
- `lib/chat/retrieve/faq.js`
- `lib/chat/retrieve/news.js` (news_meta 유지)
- `lib/chat/retrieve/policy.js`
- `lib/chat/retrieve/comparison.js`
- `lib/chat/retrieve/general.js`
- `lib/chat/retrieve/index.js` — action+topic dispatch

### Step 4: synthesize/respond 분리 (30분)
- `lib/chat/synthesize.js` — LLM 호출 (rephrase 포함 신규) + 템플릿 fallback
- `lib/chat/respond.js` — 조립 + tone rewrite + next_context 힌트 생성

### Step 5: api/chat.js 5-layer 재작성 (20분)
- 기존 로직 deprecated 폴더로 이동 (`lib/chat/_deprecated/`)
- 새 5-layer orchestrator로 교체

### Step 6: 시나리오 10개 실측 (30분)
- `docs/CHATBOT_TESTS.md` 생성
- 시나리오별 Before/After payload 기록
- D11 해결 여부 검증 (FAQ 후 "더 쉽게" 시나리오 #8 핵심)

---

## Phase 3 실행 체크리스트 (로컬 권장)

- [ ] `src/App.jsx` 챗봇 호출부에서 `last_turn.answer_text` 전송
- [ ] `last_turn.cards` 객체 배열로 전송
- [ ] `root_turn` maintain
- [ ] Suggestion 버튼에 `hint_action` 추가
- [ ] 카드 클릭 시 `selected_item_id` 세팅
- [ ] NewsDesk 검색에 `c.k` 포함 (F5 bundle)

---

## 다음 세션 Opening Prompt

다음 세션 시작할 때 아래 prompt 복붙:

```
SBTL_HUB 챗봇 재설계 Phase 2를 이어서 한다.

배경: github.com/ihyowoen/SBTL_HUB 에서 어제(2026-04-14) 세션에 
챗봇 진단 + 긴급 수정 + 아키텍처 재설계 문서까지 끝냈음.

다음 두 문서 먼저 읽어:
1. docs/CHATBOT_ARCHITECTURE.md — 재설계 청사진
2. SESSION_HANDOFF_20260414.md — 오늘 남긴 상태 + Phase 2 체크리스트

Phase 2 목표: lib/chat/* 5-layer 재작성 (parseRequest → resolveContext 
→ retrieve → synthesize → respond). 기존 intent.js/retrieval.js/compose.js 
/fallback.js는 _deprecated 폴더로 이동, 새로 작성.

선결 조사 3개 먼저:
- D9: "왜 중요한지" 요청 분류 미스터리
- D10: confidence.js fallback_triggered 의미 정의  
- D13: FAQ + Policy rewrite 중복 호출 근본 원인

조사 후 parseRequest.js부터 시작. 진행 순서는 핸드오프 체크리스트 대로.

환경: GROQ_API_KEY 등록됨 (llama-3.3-70b-versatile 사용 중, 무료).
OPENAI/ANTHROPIC 키 없음 — 유료 API 금지. Groq fallback만.
```

---

## 반복 원칙 — 다음 세션도 지킬 것

1. **추측 대신 실측** — payload 받아서 검증 후 작성
2. **야매 패치 금지** — 구조적 개선 우선 (이 원칙이 Phase 1 재설계의 출발)
3. **Graceful degrade** — 모든 LLM 호출은 template fallback 보유
4. **Claude가 못 하는 것 명시** — cards.json merge, tracker 업데이트, App.jsx 75KB 재업로드는 사용자 작업
5. **Git rm은 로컬** — GitHub MCP는 파일 삭제 API 없음

---

## 세션 종료 상태

- HEAD: `8a3eade` (CHATBOT_ARCHITECTURE.md 최종 수정)
- 이 commit 이후 `SESSION_HANDOFF_20260414.md` 추가 예정
- 배포 상태: 정상 (Vercel 자동 배포)
- 미해결 prod 이슈: follow-up 답변 혼선 (D11) — Phase 2 해결 예정

끝.
