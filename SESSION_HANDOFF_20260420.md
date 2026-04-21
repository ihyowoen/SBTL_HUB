# Session Handoff — 2026-04-20

2026-04-18 핸드오프 이후 Phase 1 (배터리상담소 재설계) 구현 세션. **결론: single-prompt 구조의 근본 한계 확인 → 3차 상담 (정찰병/분석가/빨간펜) 레벨업 구조로 전환 결정**. 설계 문서 `docs/CONSULTATION_3STAGE_DESIGN.md` v0.1 커밋.

**다음 세션 시작 시:** 이 문서 → `docs/CONSULTATION_3STAGE_DESIGN.md` → `SESSION_HANDOFF_20260418.md` 순서로 읽을 것. memory stale 위험 여전하니 실물 코드 대조 필수.

---

## 섹션 A — TL;DR

1. **Groq → Gemini 2.5 Flash 전환 완료** (phase1-consult-redesign 브랜치). 무료 tier rate limit 해결 목적. Gemini 503 시 Groq 자동 fallback 포함 3중 방어 구축.

2. **Flash-Lite 시도 → 실패 → Flash 복귀**. Lite가 system prompt 섹션 라벨을 응답에 echo. 지시 따름 능력 부족.

3. **품질 이슈 반복 발견**: 문어체 어미 (~있다/~된다), remaining_points가 카드 함의 문장 그대로 복사, task hint가 opener 본문으로 leak, "이 카드는" 템플릿 말투. prompt 패치 → regex 패치 → 새 이상 패턴 → 또 패치의 **두더지잡기 루프**.

4. **근본 진단**: single prompt에 opener + hook + 말투 + JSON + coverage + SBTL Chain 전부 담은 게 root cause. Flash가 다 섞어버림. **품질관리 불가능 구조**.

5. **Claire 제안 → 3차 상담 레벨업 구조**:
   - 1차 **정찰병 강차장** — 사실만 정리, 해석 금지
   - 2차 **분석가 강차장** — 한 각도 해석 (1차 facts 내에서만)
   - 3차 **빨간펜 강차장** — Red team: 성급한 해석 / 확인 안 된 전제 / 반대 시나리오 / 다음 체크포인트 2개

6. **설계 문서 v0.1** `docs/CONSULTATION_3STAGE_DESIGN.md` 작성 완료. Q1~Q6 Claire 결정 대기.

7. **재미 요소 재확인**: ReceiptBubble 날짜+티켓 번호는 유지 ("귀엽게 상담기록 하는거 재밋자나"). 레벨업 구조 자체가 재방문 동인.

8. **구현 시작 전**. 오늘 세션은 실패한 구현 + 근본 구조 전환 결정까지. 실제 3단계 구현은 다음 세션.

---

## 섹션 B — 오늘 시도한 것 (chronological)

### B.1 Groq 문제 → Gemini 전환

**배경**: 4/18 이후 Phase 1 구현 중 Groq rate limit (llama-3.3-70b TPM 12K) 자주 터짐. 70b → 8b-instant 전환 시도했으나 품질 저하 체감.

**해결**: Gemini 2.5 Flash 도입.
- commit `2a9c7eb`: `callGemini` + `callLLM` dispatcher 추가. GEMINI_API_KEY 있으면 자동 primary.
- commit `7aecc1c`: SYSTEM_CARD_CONSULT에 SBTL Chain 3경로 섹션 신설 (K-3사 수요 / 파우치형 점유율 / 알루미늄 원가). 무관 카드엔 "직접 영향 없어" 명시.
- commit `2c70f00`, `ff88df6`, `19ceab2`: debug 필드 강화 (env_probe, provider, status, detail, finish_reason).

**확인된 Gemini 에러**: `503 UNAVAILABLE — "This model is currently experiencing high demand. Spikes in demand are usually temporary."` → 무료 tier Flash peak time 과부하 (구조적, 코드 문제 아님).

### B.2 Flash-Lite 실험 (실패)

**commit `bdd590b`**: Flash → Flash-Lite 전환 + 503 retry + Groq auto-fallback dispatcher.
- 이유: Flash-Lite가 RPM 15/RPD 1000 (Flash 대비 1.5~4배 여유), 과부하 덜함.
- 결과: opener는 작동했으나 **followup에서 대참사**:
  ```
  [few-shot opener] 이 카드, Sunwoda에서 LFP로... ← 섹션 라벨 복사
  [opener] { "opener": "...", "remaining_points": [...] } ← JSON까지 echo
  [후속 답변] 충전 프로토콜이 중요해질 거라는 건...
  ```
- Flash-Lite가 system prompt 섹션 라벨을 응답에 그대로 재생산. 지시 따름 약함.

**commit `14a4b0f`**: Flash로 복귀. 3중 방어 구축:
1. Model: `gemini-2.5-flash-lite` → `gemini-2.5-flash`
2. Prompt 강화 — TONE_RULE + followup task에 "대괄호 라벨/JSON 절대 금지" 명시
3. 서버 후처리 `stripPromptEchoes()` — `[opener]`, `[few-shot opener]`, `[remaining_points]`, `[후속 답변]`, JSON 블록 정규식 제거

**한글 오타 복원**: 이전 push_files 인코딩 깨져서 들어간 오타 10개 수정 (SBTL첫단→첨단, 싰지→쏟지, 나발 예→나쁜 예, 끓어→끊어, 나뉘일→나뉠, 쉽은→쉬운, 한 격→한 겹, 빼았거나→뺏었거나, 바꿰→바꿔, 펄→펌).

### B.3 품질 이슈 발견 (중국 방화벽 카드 테스트)

**test case**: "중국 1300℃급 배터리 '방화벽' 공개 — 열폭주 차단 소재…" (2026-04-17_CN, category: tech?)

**발견된 문제**:
- opener: "...가능성이 있다", "...이동할 가능성이 있다" (문어체 어미)
- Hook 3: "...관찰 포인트다" (문어체)
- Hook label 38자+: "소재 단가 상승에도 규제 대응 비용과 리콜 리스크를 낮추는 방향이면 채택 여지가 커질 수 있다." (카드 implication 배열 통째로 복사)
- Hook label 35자+: "K-배터리도 셀 성능뿐 아니라 안전 부품 체인 경쟁력을 함께 점검해야 한다."

**commit `44426e8`**: 3단 방어 강화
1. TONE_RULE 금지 어미 확대 (~있다/~된다/~적이다/~관찰 포인트다/~필요하다/~중요하다)
2. remaining_points prompt 엄격화 (7-14자, 함의 문장 복사 금지, 명사형 종결 금지)
3. 서버 `softenFormalTone()` 14개 문어체 어미 자동 변환 + `validateAndCleanRemainingPoints()` 18자 초과 drop

### B.4 ma_jv 카드 테스트 — 맛이 감 ㅋ

**test case**: "당승과기, 云天化와 44.93억위안 LFP 일체화 프로젝트 착수" (2026-04-17_CN_ma_jv)

**발견된 치명적 문제**:
- **task hint가 opener 본문으로 leak**. `taskByCategory.ma_jv` prompt 내용("각도: 거래 구조·회계 의도. 금액의 의미, 지분 구조, 무엇을 book에서 털려는지.")을 Flash가 통째로 번역해서 나열:
  - "이번 거래 구조가 경제 논리가 더 세 보여"
  - "매각가 자체가 시그널이야"
  - "숫자 뒤에 회계 의도 있어"
  - "뭐을 털려는 건지가 포인트야" ← "뭐을" 오타까지
- 카드 실제 내용(44.93억위안, 당승과기, 云天化, LFP 일체화) 하나도 안 들어감
- Followup truncation: "...진심인지 보여**주는 지**" (중간 끊김)
- "이 카드는 중국에서 LFP 배터리..." ← prompt 금지 무시

**Claire 판단**: "맛이 제대로 갔어 / 품질관리가 될까?"

### B.5 근본 진단

지금까지 루프 분석:
- Prompt 금지 추가 → Flash 무시 → regex 추가 → 새 이상 패턴 → 또 추가
- 오늘만 9개 commit. 문제 해결보다 새 문제 발견 속도가 빠름.
- Flash 출력 확률적. 291개 카드 중 수동 검증 매번 1~2개. 나머지 289개 품질 예측 불가능.
- 근본 설계 문제:
  - Task hint prose가 prompt에 섞여 본문으로 leak 가능
  - Negative instruction ("이 카드는" 금지) 일관성 유지 어려움
  - 카드 데이터 anchor가 약함 — 힌트가 카드 내용 밀어냄
- Regression test 없음. 매 commit마다 Claire 수동 테스트 = production quality gate 아님.

**결론**: 현재 방식으로는 품질관리 불가능.

---

## 섹션 C — 3차 상담 레벨업 구조 (핵심 결정)

Claire 제안 (원문 인용):
> 1차 상담 / 2차 상담 / 3차 상담: 상담 종료
> - 1차: 무슨 일인지
> - 2차: 왜 중요한지, 핵심 쟁점
> - 3차: 최종 판단 + Red team 점검
> - 없는 사실은 쓰지 말 것
> - 불확실하면 불확실하다고 쓸 것
> - 짧고 명확하게 쓸 것
> 3차 상담에는 반드시 포함:
> - 성급한 해석일 수 있는 부분
> - 아직 확인 안 된 전제
> - 반대 시나리오
> - 다음 체크포인트 2개

### C.1 왜 이 구조가 품질관리 가능한가

| 현재 single-prompt | 3-stage |
|---|---|
| "opener가 잘 됐는지" 기준 모호 | 각 stage 독립 JSON schema 검증 |
| 모든 규칙 한 prompt에 담음 → 섞임 | 각 stage는 한 가지만 함 → Flash 부담 ↓ |
| 종료점 없음 → followup 루프 | 3차 = 명시적 종료 |
| 팩트 + 해석 동시 생성 → hallucination 위험 | 1차 팩트 확정 → 2차는 facts 내 해석만 |
| 재방문 동인 약함 | 레벨업 자체가 보상, 다른 카드로 다시 1차부터 |
| Red team 없음 | 3차가 자기 검증 역할 (Flash 논리 작업엔 강함) |

### C.2 각 단계 요약

**1차 — 정찰병** (SCOUT)
- Output: `{ summary, facts[3~5], unknowns[0~2] }`
- 말투: 팩트 정리 톤. "~했어", "~야"
- 금지: 해석 표현, 추측

**2차 — 분석가** (ANALYST)
- Input: 카드 + 1차 output
- Output: `{ angle, interpretation, sbtl_link, key_tension }`
- 각도 1개 선택 (타이밍 / 숫자 / 대비 / 구조)
- SBTL Chain은 명확히 해당할 때만 언급

**3차 — 빨간펜** (RED TEAM)
- Input: 카드 + 1차 + 2차 output
- Output: `{ premature_interpretations, unverified_premises, counter_scenario, next_checkpoints[2] }`
- 자기 비판 역할 — Flash 논리 작업은 강함

### C.3 UI 플로우

```
[카드 접수 ReceiptBubble]
        ↓
[1차 bubble: 📋 사실 확인]
        ↓ [강차장 더 깊이 물어보기 →]
[2차 bubble: 🔍 핵심 각도]
        ↓ [최종 판단 받기 →]
[3차 bubble: 🧪 빨간펜]
        ↓
[─── 상담 종료 ─── / 다른 카드로 상담하기]
```

유저 선택권: 1차만 읽고 닫기 OK, 2차까지만도 OK, 3차까지 가면 "상담 종료" 명시.

**추천 정책**: 순차 강제 (건너뛰기 X).

### C.4 설계 문서 위치

전체 상세 설계: **`docs/CONSULTATION_3STAGE_DESIGN.md`** (commit `826f0ba`)

11개 섹션:
1. 왜 이 구조
2. 각 단계 Role 정의
3. 유저 플로우
4. Rendering (UI)
5. 데이터 흐름 / API
6. Prompts (draft v0.1)
7. Gold regression test 전략
8. 삭제할 것 / 유지할 것
9. 구현 순서 (Phase 2, 1~1.5일 예상)
10. Claire 결정 필요 Q1~Q6
11. 다음 액션

### C.5 Claire 결정 필요 (Q1~Q6)

**Q1. 단계 건너뛰기?** 순차 강제 (A) vs 2차 직행 (B) — 내 추천 **A**
**Q2. 3차 시작?** 수동 (A) vs 자동 (B) — 내 추천 **A**
**Q3. LLM 3배 호출 비용?** — 문제 없음 (Groq fallback 동작)
**Q4. 캐릭터 분리?** 같은 강차장 모드만 다름 (A) vs 다른 캐릭터 3명 (B) — 내 추천 **A**
**Q5. Stage 간 데이터?** 통째 전달 (A) vs 정제 (B) — 내 추천 **A**
**Q6. 세션 persistence?** 세션 내만 (A) vs localStorage (B) — 내 추천 **A**

---

## 섹션 D — 현재 상태 맵 (2026-04-20)

### 브랜치 상태

- **phase1-consult-redesign** (PR #66, 현재 작업 브랜치, not merged)
  - HEAD: `826f0ba` (설계 문서 커밋)
  - 주요 변경: Gemini 전환 + 3중 방어 + 설계 문서
- **main**: `5ab8c63` 상태 유지 (4/18 PR #68 이후 변경 없음)

### 데이터 상태

- `cards.json` — **291 cards** (4/18 273 → 291, main 브랜치에 cards.json 업데이트 있었음)
- `faq.json` — **38 entries** (변경 없음. "📨뉴스레터" 잔존 이슈 4/18 그대로)
- `tracker_data.json` — **63 items** (4/18 62 → 63)

### Backend (현재 phase1 브랜치)

- `lib/chat/llm.js` 35.9KB — 2026-04-18 14.7KB에서 대폭 확장
  - callGemini + callGroq + callLLM dispatcher (3중 방어)
  - stripPromptEchoes + softenFormalTone + validateAndCleanRemainingPoints
  - SYSTEM_CARD_CONSULT: Coverage Contract v2.2 + SBTL Chain
  - **⚠️ 3-stage 전환 시 대부분 재작성 예정**
- `api/chat.js` 12KB — consultation 라우팅 + debug 강화 (detail/status/finish_reason)
  - **⚠️ 3-stage 전환 시 stage 필드 기반 라우팅 추가 필요**
- `api/analysis.js` — 여전히 dead endpoint
- `api/brave.js`, `api/translate.js` — 4/18과 동일 (translate.js는 이미 삭제됨)

### Frontend (현재 phase1 브랜치)

- `App.jsx` ~92KB — monolith 여전. Phase 1 초기 패치 적용됨:
  - `handleSubmitConsultation` handler
  - `ChatBot` 컴포넌트에 `ReceiptBubble` + `sessionHooksRef` + `usedTopicsRef` 있음
  - **⚠️ 3-stage 전환 시 ChatBot 구조 대폭 수정 (stage state, 3 bubble 컴포넌트)**
- `src/story/StoryNewsItem.jsx` — 4/18과 동일
- `src/story/buildCardConsultContext.js` — Phase 1에서 새로 생김. context 조합 로직은 3-stage에서도 재사용 가능
- `src/story/cardOpenerPool.js` — few-shot examples 포함. 3-stage에서는 anchor 불필요 → 삭제 후보
- `src/consultation/consultationStorage.js` — localStorage. 3-stage는 stage output 담도록 확장

### 환경

- **Vercel**:
  - production: sbtl-hub.vercel.app (main branch, commit `5ab8c63`)
  - preview: sbtl-hub-git-phase1-consult-redesign-ihyowoens-projects.vercel.app (branch alias, 항상 최신 phase1 commit)
- **Env vars**:
  - GEMINI_API_KEY ✅ (오늘 Claire 등록)
  - GROQ_API_KEY ✅ (기존)
  - BRAVE_KEY ✅ (변경 없음)
  - Anthropic/OpenAI 없음 (유료 금지 유지)

### GitHub MCP 제약 확인됨

- Contents: read+write ✅ (create_or_update_file 정상)
- Pull requests: 병합은 Claire 수동
- push_files 한글 인코딩 주의 — create_or_update_file 선호

---

## 섹션 E — 오늘 commits (chronological)

| SHA | Message (요약) |
|---|---|
| `c2d255d` | Phase 1 App.jsx patch + StrictMode nonce guard (4/17~18 사이) |
| `d983aa3` | apply_session_agenda.py — 세션 hook agenda 패치 스크립트 |
| `bbb2768` | 세션 hook agenda 적용 |
| `07df22d` | remaining_points → suggestions 매핑 (api/chat.js) |
| `8454c7a` | Coverage Contract v2.1 (llm.js) |
| `f6806db` | main 머지 (cards.json 273→291) |
| `7aecc1c` | Groq rate-limit 대책 + SBTL Chain + prompt 강화 |
| `2a9c7eb` | **Gemini 2.5 Flash primary + Groq fallback 도입** |
| `2c70f00` | debug env_probe + provider 필드 |
| `ff88df6` | callGemini detail/status 필드 노출 |
| `19ceab2` | debug.llm에 detail/status/finish_reason 매핑 |
| `bdd590b` | Flash-Lite + 503 retry + Groq auto-fallback (Flash-Lite echo 문제 발생) |
| `14a4b0f` | **Flash 복귀 + stripPromptEchoes + typo 복원** |
| `44426e8` | 문어체 어미 확대 + remaining_points 7-14자 강제 |
| `826f0ba` | **docs: 3차 상담 구조 재설계 문서 v0.1** |

---

## 섹션 F — 다음 세션 Opening Prompt

다음 세션 시작 시 아래 복붙:

```
SBTL_HUB 작업 이어서. Phase 2 (3차 상담 구조 구현) 시작 예정.

먼저 다음 순서로 읽기:
1. SESSION_HANDOFF_20260420.md (가장 최신, 이 세션)
2. docs/CONSULTATION_3STAGE_DESIGN.md (v0.1 설계 문서 — 핵심)
3. SESSION_HANDOFF_20260418.md (이전 배터리상담소 4축 분석)

Memory는 stale 위험 있으니 실물 코드 대조 필수:
- lib/chat/llm.js (현재 35.9KB, Gemini + 3중 방어 포함)
- api/chat.js (consultation 라우팅)
- src/App.jsx ChatBot 섹션 (target read)
- src/story/buildCardConsultContext.js (재사용 가능)

브랜치 상태:
- 작업 브랜치: phase1-consult-redesign (PR #66, not merged)
- main: 4/18 이후 변경 없음
- 데이터: cards 291 / faq 38 / tracker 63
- Env: GEMINI_API_KEY ✅, GROQ_API_KEY ✅

오늘 해야 할 일:
[우선] Claire의 Q1~Q6 결정 받기 (설계 문서 섹션 10)
  - 추천값 다 OK면 "ㅇㅋ" 한 줄로 충분
  - 수정하고 싶은 부분 있으면 개별 답변

결정 후 Phase 2 구현 순서:
Step 1 — Backend (lib/chat/llm.js + api/chat.js)
  1. synthesizeScout / synthesizeAnalyst / synthesizeRedTeam 3개 함수 추가
  2. api/chat.js에 consultation.stage 라우팅 추가
  3. Response에 stage_output 필드 통일
  4. 기존 synthesizeCardConsult + coverage contract 관련 코드 제거

Step 2 — Frontend (App.jsx)
  1. consultation state 확장 (stage, stage1_output, stage2_output)
  2. 3개 bubble 컴포넌트 (ScoutBubble, AnalystBubble, RedTeamBubble)
  3. 전환 버튼
  4. "상담 종료" 처리
  5. 기존 sessionHooks / usedTopics 코드 제거

Step 3 — Gold test
  1. scripts/test_consultation_stages.js
  2. 5개 카테고리 × 3 stage = 15 cases
  3. 수동 리뷰 → forbidden phrase / must-contain 기준 확정

예상 시간: Step 1~2가 4~6시간, Step 3가 2~3시간. 합쳐서 1~1.5일.

제약:
- Claude 못 하는 것: App.jsx 대량 수정은 Claire가 확인하며 surgical 진행
- 유료 API 금지 (Claire rejection 유지)
- push_files 한글 인코딩 주의 → create_or_update_file 선호
```

---

## 섹션 G — 반복 원칙 (4/18에서 계승 + 오늘 추가)

1. **추측 대신 실측** — 문서 의존 금지, 실물 코드 line-by-line
2. **야매 패치 금지** — 구조적 개선 우선
3. **Graceful degrade** — 모든 LLM 호출은 template fallback 보유
4. **Claude 못 하는 것 명시** — 대량 App.jsx 수정, git rm은 Claire 작업
5. **chatbot만이 전부가 아님** — 구조적 이슈도 같은 비중
6. **Claire product intent 우선** — 직관적으로 좋아보이는 것도 의도적으로 안 만들었을 수 있음
7. **재미 요소는 덤이 아닌 필수** — 재방문 동인. 레벨업 구조가 대표.
8. **존재하지 않는 UI 상상 금지** — dead code 수정 방지.

### 오늘 추가된 원칙

9. **두더지잡기 루프 감지 → 즉시 중단**. 프롬프트 금지 추가 → LLM 무시 → regex 추가 → 새 패턴 → 또 추가. 이 패턴이 2회 이상 반복되면 **근본 구조 재설계** 시점. 패치 계속하지 말 것.

10. **Single-prompt에 다역할 담지 말 것**. opener + hook + 말투 + JSON + coverage 동시 요구 = Flash가 섞어버림. 역할 하나당 prompt 하나.

11. **Task hint prose → 본문 leak 주의**. `taskByCategory.ma_jv`의 "거래 구조·회계 의도, 금액의 의미, 지분 구조…" 같은 힌트 문장을 LLM이 번역해서 답변에 쓸 수 있음. 구조화된 directive (목록/JSON) 또는 단어 단위 힌트로만.

12. **Negative instruction ("X 금지") 한계 인식**. Positive 예시가 더 효과적. "이렇게 써" 예시 + "이렇게 쓰지 마" 예시 병행.

13. **품질관리는 regression test 없이 불가능**. Gold set + schema validation + forbidden phrase check. 매 commit마다 Claire 수동 테스트는 production gate 아님.

14. **ReceiptBubble 같은 재미 요소는 유지**. Claire 피드백 명시: "귀엽게 상담기록 하는거 재밋자나". UX 귀여움 ≠ 품질 저하.

---

## 섹션 H — 미해결 / 4/18에서 계승

### 여전히 미해결 (prod)

- **배터리상담소 journey 재설계** — 3-stage로 접근 방식 확정되었으나 구현 전
- **motir URL 오타** (tracker_data.json)
- **faq "📨뉴스레터"** (App.jsx CATS에 뉴스레터 탭 없음)
- **REGION_POLICY hardcoded** (common.js) 외부화 안 됨
- **App.jsx 91.5KB monolith** 분리 안 됨
- **compare regex** — "다르/구별/대조" 누락

### 오늘 추가된 미해결

- **Q1~Q6 Claire 결정 대기** (설계 문서 섹션 10)
- **cardOpenerPool.js few-shot examples** — 3-stage 전환 시 제거 후보
- **일부 품질 이슈** — "이 카드는" 템플릿 말투, followup truncation — 3-stage 전환으로 자연 해소 예상 (각 stage가 독립 JSON schema 반환하므로 truncation은 API 레벨 감지 가능)

### GitHub MCP 제약

- 파일 삭제 API 없음 → Claire 로컬 `git rm` 필요
- repo root stale artifacts (`merge_cards_raw_payload_*`, `download`) 여전

---

## 세션 종료 상태 (2026-04-20)

- HEAD: `826f0ba` (phase1-consult-redesign)
- Preview: sbtl-hub-git-phase1-consult-redesign-ihyowoens-projects.vercel.app READY
- Production: sbtl-hub.vercel.app (main `5ab8c63` — phase1 변경 아직 반영 안 됨)
- 데이터: cards 291 / faq 38 / tracker 63
- 미해결 prod 이슈: 3-stage 구현 대기 (Q1~Q6 결정 후)
- Phase 1 실험 결과: Gemini 전환은 성공 (Groq fallback 안정), single-prompt 구조는 한계 확인 → 3-stage 전환 결정

끝.
