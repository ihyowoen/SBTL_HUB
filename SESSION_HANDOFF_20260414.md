# Session Handoff — 2026-04-14

오늘 세션 마무리 정리. 다음 세션이 바로 이어갈 수 있도록.

**중요:** 오늘은 챗봇에 집중했지만 리포지토리 전체의 구조적 이슈 목록이 따로 있다. 섹션 B 참조.

---

## 섹션 A — 챗봇 작업 (오늘 진행분)

챗봇("강차장")이 stupid했던 원인을 구조적으로 진단하고, 긴급 수정 + 아키텍처 재설계 문서까지 마쳤다. Phase 2(backend 재작성) + Phase 3(App.jsx) 착수만 남음.

### 오늘 Commit 목록 (시간순 14개)

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
| 13 | `456c1e6` | SESSION_HANDOFF 초판 | 문서 |

### 해결된 것 (체감 개선)

**🔥 P0 — 심각한 버그**
- **내부 카드 못 읽음** (S1 fs+fetch): 사용자 체감 가장 큰 원인. 해결 확인.
- **"오늘 뉴스"가 과거 뉴스 반환** (retrieval + compose): 최신 가용 날짜로 솔직히 fallback.
- **"어제 뉴스" 미지원** (scope 확장): 상대 날짜 전부 파싱.
- **챗봇 답변이 템플릿 문자열** (S2 Groq 주입): LLM 기반 맥락 답변.
- **톤 혼재 (존댓말/반말/기사체)** (TONE_RULE + rewriteToCasual): 반말 통일.

**🧹 P1 — 정리**
- `.gitignore` .env 패밀리 포함
- `.env.example` 신설
- `vercel.json` dead rewrite 제거
- tracker URL 오타 (F4 — 다음 tracker 업데이트에 bundle)

### 해결 안 된 것 — 챗봇 (Phase 2+ 대상)

`docs/CHATBOT_ARCHITECTURE.md` 참조. D1~D13 결함 목록.

핵심은 **D11: follow_up intent가 rephrase + drill_down + 실제 follow_up 전부 삼킴**. 이게 챗봇 stupid의 진짜 구조적 원인.

---

## 섹션 B — 챗봇 외 구조적 이슈 (미해결, 다음 세션에서도 다룰 것)

오늘 챗봇에 집중하느라 뒤로 미뤄진 항목들. audit 문서 원본 + 재훑기 #31~#36 기반.

### B1. 데이터 파이프라인 (최우선)

| # | 이슈 | 소유자 | 비고 |
|---|---|---|---|
| DP1 | cards.json 9일 stale (`updated: 2026.04.13`) | 사용자 | W6 triage pipeline 로컬 실행 필요 |
| DP2 | tracker_data.json 오늘 59 items로 업데이트 확인됨 (이전 50) | — | `git log public/data/tracker_data.json` 이력 확인 |
| DP3 | faq.json 40→38 감소 | — | `git log public/data/faq.json` 삭제 이력 확인 |
| DP4 | **merge_cards.py validator 부재** | 사용자+Claude | schema 검증, URL 필수 체크, 중복 체크 없음 → #33/#34 결함이 merge 통과 |
| DP5 | **processed_urls.txt 관리 부재** | 사용자 | 주간 carryover rate 32% |
| DP6 | **dropped_rescue_screener.py + tier2_* 미통합** | 사용자 | 개발 완료, 파이프라인 통합만 남음 |
| DP7 | **screener false positive 패치 미적용** | 사용자 | 上市, 폭발, SpaceX IPO, 리콜 오인 패턴 |

### B2. 아키텍처 결함

| # | 이슈 | 소유자 | 비고 |
|---|---|---|---|
| A1 | **App.jsx 75KB monolith** | Claude+사용자 (로컬) | NewsDesk/ChatUI/HomeTab/Tracker/카드상세 한 파일 |
| A2 | **REGION_POLICY 중복** (App.jsx + lib/chat/common.js) | Claude | public/data/region_policy.json로 외부화 |
| A3 | **NewsDesk 검색이 c.k 필드 미포함** (F5) | 사용자 (로컬) | 5줄 패치지만 App.jsx 재업로드 필요 |
| A4 | ErrorBoundary dead prop (`darkMode` 받고 안 씀) | Claude | 사소 |
| A5 | **Chatbot 5-layer 재설계** (Phase 2) | Claude | docs/CHATBOT_ARCHITECTURE.md 청사진 |

### B3. 문서/원칙 위반

| # | 이슈 | 소유자 | 비고 |
|---|---|---|---|
| D1 | README 거짓말 ("App.jsx 222KB, 카드 DB 포함") | Claude | 실제 75KB, 카드 분리됨. S9 |
| D2 | **cards.json Hard-stop 위반 카드 존재** | 사용자 | #31 Jackery 세일, #33 URL 공란 죽도, #34 ESS 골드러시/인터배터리 중복 → 편집 정리 |
| D3 | OPERATIONS addendum 본인 위반 — helper payload 7일 잔류 | 사용자 (로컬) | `git rm merge_cards_raw_payload_20260407_safe_2cards.json` |
| D4 | **`download` 34바이트 orphan 파일** | 사용자 (로컬) | gitignore 템플릿 오인 저장. `git rm download` |
| D5 | `date_explorer_home_upgrade_plan.md` repo root 방치 | Claude | docs/로 이동 |

### B4. 보안/운영

| # | 이슈 | 소유자 | 비고 |
|---|---|---|---|
| S1 | **`api/chat.js` L93 `process.env.VITE_BRAVE_KEY` fallback 잔존** | Claude | 옛 위험 패턴. BRAVE_KEY만 남기고 제거 |
| S2 | `api/translate.js` dead feature | Claude | 삭제 가능 |
| S3 | Vercel preview URL이 diag에 찍힘 | — | production(`sbtl-hub.vercel.app`) 아닌 `sbtl-b405khdc2-ihyowoens-projects.vercel.app`. 정상이지만 인지만 |

### B5. 프론트엔드 UX

| # | 이슈 | 소유자 | 비고 |
|---|---|---|---|
| U1 | **배지 이모지 (📋 🔀 TOP/HIGH)** | 사용자 (디자인) | 반말 평문 답변 vs 이모지 과다 UI 일관성 리뷰 |
| U2 | `index.html` body 배경 하드코딩 (`#0d0d0d`) → 라이트 모드 초기 로드 시 1프레임 까만 플래시 | Claude | 한 줄 수정 |
| U3 | **Suggestion 버튼 self-feeding** | Claude (Phase 3) | "왜 중요한지 설명해줘" 버튼 → 또 같은 답 → 재귀. Phase 3 hint_action으로 해결 |

---

## 환경 상태 체크

| 항목 | 상태 |
|---|---|
| Vercel 배포 | 정상 — production: sbtl-hub.vercel.app |
| `GROQ_API_KEY` env | **등록됨** (VITE_ prefix 없음, 확인됨) |
| `BRAVE_KEY` env | 등록됨 |
| `OPENAI_API_KEY` env | 미등록 (사용 안 함 확정) |
| `ANTHROPIC_API_KEY` env | 미등록 (유료 — 사용자 rejection) |
| cards.json | 337 cards, 2026.04.13 기준 (9일 stale) |
| faq.json | 38 entries (40에서 2 감소 — 확인 필요) |
| tracker_data.json | 59 items (50에서 9 증가 — 업데이트 확인됨) |
| loadKnowledge 소스 | `fs` (Vercel 번들에 public/data 포함됨) |

---

## 주요 파일 현재 상태

### Backend (수정 완료)
- `api/chat.js` — 5-layer 재작성 대상 (Phase 2). S1 VITE_BRAVE_KEY fallback 제거도 같이
- `api/analysis.js` — Groq 기반, fallback template 유지
- `api/translate.js` — **삭제 대상** (dead feature)
- `api/brave.js` — 사용 중, 유지
- `lib/chat/llm.js` — TONE_RULE + synthesize* + rewriteToCasual (유지)
- `lib/chat/common.js` — hybrid fs+fetch loadKnowledge (유지). REGION_POLICY 중복은 A2 대상
- `lib/chat/retrieval.js` — **재작성 대상** (Phase 2)
- `lib/chat/scope.js` — 확장 완료 (유지)
- `lib/chat/intent.js` — **재작성 대상 (parseRequest.js로 교체)** (Phase 2)
- `lib/chat/compose.js` — **분리 대상 (synthesize.js + respond.js)** (Phase 2)
- `lib/chat/confidence.js` — **의미 재정의 대상** (Phase 2 조사)
- `lib/chat/fallback.js` — **흡수 대상** (Phase 2)

### Frontend (Phase 3 + B1~B5 일부)
- `src/App.jsx` — 챗봇 호출부 Context Protocol 맞춤 (Phase 3) + NewsDesk c.k (A3) + monolith 분할 (A1, 선택)
- `index.html` — body 배경 플래시 수정 (U2)

### 문서
- `docs/CHATBOT_ARCHITECTURE.md` — **Phase 2/3 청사진** 🎯
- `ENHANCED_RED_TEAM_FULLSTACK_AUDIT_20260414.md` — 원본 audit
- `FIX_PROPOSAL_20260414.md` — 7 quick + 2 diag + 9 structural
- `FIX_F1_F4_F7_NOTES.md` — 수동 작업 안내
- `SESSION_HANDOFF_20260414.md` — 본 문서

---

## 사용자 수동 작업 (Claude 불가)

다음 세션 시작 전 혹은 시작과 동시에 처리 권장:

```bash
# 1. stale artifacts 정리 (D3, D4)
git pull
git rm download merge_cards_raw_payload_20260407_safe_2cards.json
git commit -m "chore: cleanup stale artifacts"
git push

# 2. (선택) 데이터 변경 이력 확인 — 다음 세션 Phase 2 선결 조사에 활용
git log --oneline -5 public/data/faq.json
git log --oneline -5 public/data/tracker_data.json
git log --oneline -5 public/data/cards.json
```

그 외:
- **W6 triage pipeline 실행** → cards.json 업데이트 (DP1)
- **F6 cards.json 편집 정리** (Jackery, ESS 골드러시 중복, 죽도 URL 공란) — W6 merge에 포함 (D2)

---

## Phase 2 실행 체크리스트 (챗봇, 다음 세션 backend ~2시간)

### Step 0: 선결 조사 (30분)
- [ ] D9 — "왜 중요한지 설명해줘" 분류 미스터리. Vercel 최신 배포 확인 + 실제 intent.js 코드 재검증
- [ ] D10 — `confidence.js::scoreConfidence` 코드 읽고 `fallback_triggered`의 실제 의미 정의
- [ ] D13 — `api/chat.js`에서 FAQ + Policy rewrite 중복 호출 조건 확인
- [ ] `git log` 데이터 파일 이력 확인 (DP2, DP3)

### Step 1: parseRequest 작성 (30분)
- `lib/chat/parseRequest.js` 신규
- 3축 반환: `{ action, topic, scope, raw }`
- Frontend hint 존중 (hint_action 오면 그대로)

### Step 2: resolveContext 작성 (20분)
- `lib/chat/resolveContext.js` 신규
- action별 필수 context 검증, 부족 시 clarification 반환

### Step 3: retrieve/* 분리 (30분)
- `lib/chat/retrieve/{faq,news,policy,comparison,general}.js`
- `lib/chat/retrieve/index.js` — dispatch

### Step 4: synthesize/respond 분리 (30분)
- `lib/chat/synthesize.js` + `lib/chat/respond.js`

### Step 5: api/chat.js 5-layer 재작성 (20분)
- 기존 로직 `lib/chat/_deprecated/`로 이동
- **VITE_BRAVE_KEY fallback 제거 (S1 동시 처리)**
- `api/translate.js` 삭제 (S2 동시 처리)

### Step 6: 시나리오 10개 실측 (30분)
- `docs/CHATBOT_TESTS.md` 생성
- Before/After payload 기록

---

## Phase 3 실행 체크리스트 (App.jsx, 로컬 권장)

- [ ] 챗봇 호출부에서 `last_turn.answer_text` 전송
- [ ] `last_turn.cards` 객체 배열로 전송
- [ ] `root_turn` maintain
- [ ] Suggestion 버튼에 `hint_action` 추가 (U3 해결)
- [ ] 카드 클릭 시 `selected_item_id` 세팅
- [ ] NewsDesk 검색에 `c.k` 포함 (A3)
- [ ] `index.html` body 배경 (U2)

---

## Phase 4 실행 체크리스트 (차순위 정리)

### 챗봇 외 정리
- [ ] README 현실화 (D1, S9)
- [ ] REGION_POLICY 외부화 → `public/data/region_policy.json` (A2)
- [ ] `date_explorer_home_upgrade_plan.md` → `docs/`로 이동 (D5)
- [ ] App.jsx monolith 분할 (A1, 선택 — 대규모)
- [ ] merge_cards.py validator 추가 (DP4)
- [ ] screener 패치 통합 (DP6, DP7)
- [ ] 배지 이모지 디자인 결정 (U1)

### 챗봇 후속
- [ ] `_deprecated/` 폴더 코드 제거 (Phase 2 안정화 후)
- [ ] confidence 재검토 (D10 선결 조사 결과 기반)

---

## 다음 세션 Opening Prompt

다음 세션 시작할 때 아래 prompt 복붙:

```
SBTL_HUB 작업을 이어서 한다.

배경: github.com/ihyowoen/SBTL_HUB 에서 어제(2026-04-14) 세션에 
챗봇 진단 + 긴급 수정 + 아키텍처 재설계 문서까지 끝냈음. 14개 commit.

먼저 다음 문서 세 개 읽어:
1. SESSION_HANDOFF_20260414.md — 전체 현황 + 체크리스트 + 섹션 B (챗봇 외 이슈) 
2. docs/CHATBOT_ARCHITECTURE.md — 챗봇 재설계 청사진 (D1~D13)
3. ENHANCED_RED_TEAM_FULLSTACK_AUDIT_20260414.md + FIX_PROPOSAL_20260414.md 
   — 챗봇 외 원본 audit + fix proposal

오늘 세션 목표 (우선순위 정해서 시작):

[옵션 A] 챗봇 재설계 Phase 2 (backend 2시간)
  선결 조사 3개 (D9/D10/D13) → parseRequest → resolveContext → retrieve → 
  synthesize → respond → api/chat.js 5-layer 재작성 → 시나리오 10개 검증

[옵션 B] 챗봇 외 구조적 정리 (1~2시간)
  SESSION_HANDOFF 섹션 B 목록 처리. 우선순위:
  - DP4 merge_cards.py validator 추가
  - A2 REGION_POLICY 외부화
  - S1 VITE_BRAVE_KEY fallback 제거
  - S2 api/translate.js 삭제
  - D1/S9 README 현실화
  - U2 index.html body 플래시 수정
  - D5 date_explorer 문서 이동

[옵션 C] 사용자 수동 작업 후 Phase 2+B 혼합
  git rm download 등 선제 정리 → 그다음 결정

어느 옵션 갈지 먼저 묻고, 결정되면 선결 조사부터 시작.

환경: GROQ_API_KEY 등록됨 (llama-3.3-70b-versatile, 무료).
OPENAI/ANTHROPIC 키 없음 — 유료 API 금지. Groq만.
GitHub MCP는 파일 삭제 API 없음 — 삭제 필요한 것은 사용자 로컬 git rm.
```

---

## 반복 원칙 — 다음 세션도 지킬 것

1. **추측 대신 실측** — payload 받아서 검증 후 작성
2. **야매 패치 금지** — 구조적 개선 우선
3. **Graceful degrade** — 모든 LLM 호출은 template fallback 보유
4. **Claude 못 하는 것 명시** — W6 pipeline, App.jsx 75KB 대량 수정, git rm은 사용자 작업
5. **챗봇만이 전부가 아님** — 섹션 B의 구조적 이슈도 같은 비중으로 다룸

---

## 세션 종료 상태

- HEAD: 이 commit 이후
- 배포: 정상 (Vercel 자동)
- 미해결 prod 이슈: follow_up 혼선 (D11) — Phase 2 해결 예정
- 미해결 repo 위생: D3/D4 사용자 로컬 git rm 필요
- 데이터 stale: cards.json 9일 — 사용자 W6 pipeline 실행 필요

끝.
