# _deprecated/ — Phase 1 legacy chat pipeline

Phase 2 (`2026-04-15`)에서 5-layer 아키텍처로 재작성되면서 이 폴더로 이동됨.

## 이동된 파일

| 파일 | 대체 |
|---|---|
| `intent.js` | `lib/chat/parseRequest.js` (3축 action/topic/scope) |
| `retrieval.js` | `lib/chat/retrieve/*.js` (topic별 분리) |
| `compose.js` | `lib/chat/synthesize.js` + `lib/chat/respond.js` |
| `fallback.js` | 흡수 (source_mode는 action+topic으로 결정론적) |
| `confidence.js` | 제거 (D10 조사 — fallback_triggered 의미 불명확했음) |

## 제거 해결 결함

Phase 2에서 구조적으로 해결된 결함들 (`docs/CHATBOT_ARCHITECTURE.md` 참조):

- **D5** — FAQ 매치가 retrieval 내부에 숨어 intent와 독립 작동 → topic dispatch로 통일
- **D7** — FAQ/Policy 분기가 intent보다 먼저 → parseRequest에서 topic 단일 결정
- **D9** — "왜 중요한지" → analysis_why 먼저 매치되는 우선순위 순서 의존 버그 → analyze_card action으로 명시화
- **D10** — `fallback_triggered` 의미 불명확 (실제로는 "Brave 조회했다"일 뿐) → 제거
- **D11** — `follow_up` intent가 rephrase/drill_down/실제 follow_up 전부 처리 → 3개 action으로 분리
- **D12** — compose.js가 FAQ 응답을 `answer_type: "general"`로 마스킹 → respond.js에서 action 반영
- **D13** — FAQ + Policy rewrite 중복 호출 (topic 축 불일치) → synthesize.js에서 topic 단일 경로

## 참조만 하고 import 금지

`api/chat.js`는 더 이상 이 폴더를 import하지 않음. Phase 4에서 삭제 예정.
