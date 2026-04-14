# Fix Proposal — 2026-04-14

`ENHANCED_RED_TEAM_FULLSTACK_AUDIT_20260414.md` (30개 발견) + 재훑기(6개 추가 발견)을 실행 단위로 변환한 문서.

원칙:
- **진단 ≠ 처방.** audit는 진단. 이 문서는 처방.
- **"적은 공수로 큰 효과" 우선순위.** 5분짜리 fix가 1일짜리 구조 개편보다 먼저.
- **진짜 원인을 확정 못한 것은 진단부터.** 추측으로 1시간 쓰지 말 것.

---

## 🆕 재훑기에서 추가 발견 (#31~#36)

### #31. `cards.json` 마지막 카드 — 편집 정책 위반
- 2026.03.16 Jackery 플래시 세일 카드 (`s:"i"`, r:"GL")
- `CARD_WORKFLOW_VFINAL` Hard-stop 중 "과도한 홍보성" 해당
- 산업 직접성 0, 단순 세일 광고

**조치:** 삭제. 이후 editorial 기준 재확인.

### #32. `cards.json` region 값 체계적 느슨함
- `r:"US/KR"` 카드 3개 (이전 audit에 1개로 적었으나 실제 3개 확인)
- `r:"GL"` 남발 (캄보디아 ESS, DOI 공식 확인 같은 특정 지역성 카드도 GL)
- region 분류 기준 문서 없음

**조치:** `docs/DATA_CONTRACT.md` 신설 (OPERATIONS.md §9 권장 문서). region enum 확정.

### #33. `cards.json` `src`/`url` 공란 카드
- `src:""` 3건 확인 (원자력연 LFP, 채비 UAE, 죽도 에너지섬)
- `url:""` 1건 (죽도 에너지섬) — `CARD_WORKFLOW_VFINAL` Hard-stop "원문 URL 불명확" 직접 위반
- merge_cards.py에 validator 부재라 통과

**조치:** merge_cards.py 검증 추가 (audit #21와 동일 패치).

### #34. `cards.json` 편집적 중복
- 2026.03.21 ESS 골드러시 3부작 → 동일 시리즈 카드 2장 (URL만 다름, 제목 거의 동일)
- 2026.03.17 인터배터리 요꼬가와 → 동일 이벤트 2장 (URL 동일)
- merge_cards.py 제목 35자 prefix dedupe 실패
- `WORKFLOW.md` §4-2 "편집적 중복" 정확히 해당

**조치:** 수동 삭제 + URL 기반 dedupe 추가 (audit #19).

### #35. Helper payload 7일째 repo 잔류
- `merge_cards_raw_payload_20260407_safe_2cards.json` 2026.04.07 생성
- `CARD_WORKFLOW_VFINAL_ADDENDUM_20260407.md` 1절 "helper payload는 repo 영구 보관 대상이 아님" 본인 위반
- 내용 미확인 (민감 정보 가능성)

**조치:** 내용 확인 후 삭제. 또는 `docs/card_payloads/archive/`로 이동.

### #36. `download` 파일 — 오인 생성
- 34바이트, 내용: `node_modules\ndist\n.env\n.env.local`
- 파일명이 `download`인데 `.gitignore` 템플릿
- 누군가 .gitignore 업데이트하려다 파일명 실수로 `download`로 저장한 흔적

**조치:** `download` 삭제 + 해당 내용을 `.gitignore`에 병합.

---

## 🔥 즉시 실행 (5분 × 7건 = 35분)

아래 7건은 리스크 낮고 효과 즉각. 한 번의 push로 처리 가능.

### F1. `.gitignore` 정정 + `download` 삭제
```
# .gitignore (before)
node_modules/
dist/

# .gitignore (after)
node_modules/
dist/
.env
.env.local
*.Zone.Identifier
~*.backup
```
추가: `download` 파일 삭제.

### F2. `env.example` 보안 수정
```bash
# before
VITE_BRAVE_KEY=여기에_새_API_키_입력

# after
# Brave Search API Key (서버 전용 — VITE_ prefix 금지, 클라이언트 번들 노출됨)
BRAVE_KEY=여기에_API_키_입력

# Anthropic API Key (compose.js LLM 주입 시)
ANTHROPIC_API_KEY=sk-ant-...

# OpenAI API Key (api/analysis.js 용)
OPENAI_API_KEY=sk-...
```

### F3. `vercel.json` dead route 제거
```json
{
  "rewrites": [
    { "source": "/((?!api/).*)", "destination": "/index.html" }
  ]
}
```

### F4. `tracker_data.json` URL 오타 수정
```json
// KR tier1
{ "name": "MOTIE 산업부 (영문)", "url": "https://english.motie.go.kr/" }  // r → e

// KR tier2
{ "name": "The Elec", "url": "https://www.thelec.kr/" }  // .net → .kr
```

### F5. `src/App.jsx` NewsDesk 검색 c.k 포함
```js
// before
cards = cards.filter((c) =>
  String(c.T || "").toLowerCase().includes(sw) ||
  String(c.sub || "").toLowerCase().includes(sw) ||
  String(c.g || "").toLowerCase().includes(sw)
);

// after
cards = cards.filter((c) => {
  const haystack = [c.T, c.sub, c.g, ...(c.k || [])].join(" ").toLowerCase();
  return haystack.includes(sw);
});
```

### F6. `cards.json` 편집 정리
- Jackery 플래시 세일 카드 삭제 (#31)
- ESS 골드러시 중복 카드 1장 삭제 (#34)
- 인터배터리 요꼬가와 중복 카드 1장 삭제 (#34)
- URL 공란 카드 (죽도 에너지섬) 삭제 또는 URL 보강 (#33)

### F7. Helper payload 정리
- `merge_cards_raw_payload_20260407_safe_2cards.json` 내용 검토 → 삭제 또는 `docs/card_payloads/archive/` 이동

---

## 🔍 진단 먼저 (검증 → 결정)

### D1. `common.js`의 `process.cwd()` 문제 실재 여부 검증

가설: Vercel serverless function 환경에서 `cwd()`가 `public/`을 못 찾아 챗봇이 빈 데이터로 동작.

**검증 방법:**
```js
// api/chat.js 진입부에 로그 추가
const kb = await loadKnowledge();
console.log(`[chat-debug] cwd=${process.cwd()} cards=${kb.cards.length} faq=${kb.faq.length} tracker=${kb.tracker.items.length}`);
```

commit → Vercel 자동 배포 → 앱에서 아무 질문 하나 → Vercel 대시보드 Function Logs 확인.

**결과 분기:**
- `cards=0 faq=0 tracker=0` → cwd 문제 실재 확정. F8 (fetch 전환) 실행.
- `cards=337 faq=40 tracker=50` → cwd 정상. 챗봇 stupid 원인은 다른 곳. D2로 이동.

### D2. 챗봇 "stupid" 체감의 실제 원인 분리 테스트

D1 결과 cards 정상 로드되는 경우, 다음 질문을 Vercel 배포 앱에 실제 입력 후 응답 확인:

| 테스트 질문 | 기대 분기 | 실패 시 원인 |
|---|---|---|
| "미국 오늘 뉴스" | news intent, region=US, 카드 3장+ | retrieval score 로직 |
| "FEOC 뭐야" | faq match "feoc" entry | matchFaq first-match 버그 |
| "삼성SDI vs LG 비교" | compare intent | intent.js compare regex |
| "방금 그거 왜 중요해" (앞 턴 있을 때) | follow_up+analysis_why | intent.js 우선순위 버그 |
| "요약해줘" (아무 context 없이) | general 또는 low-confidence | fallback trigger |

각 테스트의 실제 응답을 Screen Record해서 어디서 깨지는지 특정. 추측 대신 실측.

---

## 🛠️ 구조 개편 (공수 큼 — 진단 후 결정)

### S1. `lib/chat/common.js` fetch 기반 전환
D1이 cwd 문제 확정 시.

```js
export async function loadKnowledge() {
  const base = process.env.VERCEL_URL
    ? `https://${process.env.VERCEL_URL}`
    : "http://localhost:3000";
  try {
    const [cards, faq, tracker] = await Promise.all([
      fetch(`${base}/data/cards.json`).then(r => r.json()),
      fetch(`${base}/data/faq.json`).then(r => r.json()),
      fetch(`${base}/data/tracker_data.json`).then(r => r.json()),
    ]);
    return {
      cards: Array.isArray(cards) ? cards : cards.cards || [],
      faq: Array.isArray(faq) ? faq : [],
      tracker: { meta: tracker?.meta || {}, items: tracker?.items || [], sources: tracker?.sources || {} },
    };
  } catch (e) {
    console.error("[loadKnowledge] fetch failed:", e.message);
    return { cards: [], faq: [], tracker: { meta: {}, items: [] } };
  }
}
```

공수: 30분. 리스크: 낮음 (fallback 유지).

### S2. composeCards LLM 주입 PoC (audit P0-1)
D1 결과와 무관하게 거의 확실한 개선. 공수 1시간.

- `ANTHROPIC_API_KEY` Vercel env 추가
- `lib/chat/compose.js`에 `synthesizeAnswer()` 추가
- news/summary intent만 먼저 적용 → 안정화 확인 후 확장
- 실패 시 기존 템플릿 graceful fallback

### S3. `intent.js` follow_up/analysis 우선순위 수정
15분.

```js
const isFollowUp = /(그\s*기사|방금|직전|...)/.test(l) && hasCtx;
const isAnalysisIntent = /(왜\s*중요|의미|...)/.test(l);

if (isFollowUp) {
  if (isAnalysisIntent) return "follow_up_analysis_why";
  return "follow_up";
}
if (isAnalysisIntent) return "analysis_why";
// ... rest
```

`retrieval.js`, `compose.js`, `api/chat.js`가 `follow_up_analysis_*` 처리하도록 분기 추가 필요.

### S4. `retrieval.js` `matchFaq` 스코어 기반 전환
15분.

```js
function matchFaq(faq = [], query = "") {
  const l = String(query || "").toLowerCase();
  let best = { f: null, hits: 0 };
  for (const f of faq) {
    const hits = (f.k || []).filter((k) => l.includes(String(k).toLowerCase())).length;
    if (hits > best.hits) best = { f, hits };
  }
  if (best.f) return { answer: best.f.a, keywords: best.f.k || [] };
  return null;
}
```

### S5. `cards.json` region 정규화
30분. `US/KR` → `US`(primary)로 통일, `secondary_r` 추가 필드 신설 검토. DATA_CONTRACT 문서화 선행.

### S6. `merge_cards.py` 안전화
30분. (audit #19, #20, #21 통합)
- URL 기반 dedupe
- 빈 signal IndexError 방어
- schema validator (signal/region/date/url 필수)
- dry-run 모드

### S7. `REGION_POLICY` 중복 제거 + 데이터 외부화
30분. `public/data/region_policy.json` 신설. App.jsx와 common.js 둘 다 fetch.

### S8. 챗봇 톤 통일
1시간. faq.json 40개 entry 전부 반말 리라이트 + api/analysis.js 프롬프트 수정.

### S9. README 현실화
10분. App.jsx 실제 크기(75KB), 카드 DB 분리 반영, STRENGTHENING_PLAN 1번 항목 소진.

---

## 📊 실행 순서 제안

### Week 1 (지금 당장 — 오늘 오후)
1. **F1~F7 일괄 push** (35분) — 즉시 효과, 리스크 없음
2. **D1 디버그 로그 추가** (5분) + Vercel 배포 대기 (5분) + 실제 질문 + 로그 확인 (5분)
3. D1 결과에 따라:
   - cwd 문제 O → S1 실행 (30분)
   - cwd 문제 X → D2 테스트 매트릭스 (15분) → 가장 깨지는 곳 우선 수정

### Week 1 잔여
4. **S2 LLM 주입 PoC** (1시간) — 가장 큰 체감 개선 기대
5. **S3~S4 intent/matchFaq fix** (30분)
6. **S9 README 현실화** (10분)

### Week 2
7. cards.json + tracker_data.json 운영 리듬 회복 (사용자 작업 영역 — Claude 못 함)
8. S5~S8 구조 개선

---

## 🔴 Claude가 할 수 없는 것 — 사용자 명시적 작업

1. **cards.json 일일/주간 merge** — triage pipeline 실행은 Linux 워크스페이스 작업
2. **tracker_data.json 2A+2B 업데이트** — 50개 item 일일 상태 점검
3. **Vercel env var 설정** — `BRAVE_KEY`, `ANTHROPIC_API_KEY` Vercel 대시보드 입력
4. **API 키 발급** — Anthropic Console, Brave Search Developer Portal
5. **production 화면 실측** — D2 테스트 매트릭스 실제 수행
6. **merge_cards.py 로컬 실행** — Python 환경에서 실행·검증

이 6가지는 각 fix의 전제조건. Claude는 코드 생성·commit·문서화까지만 담당.

---

## 🎯 한 줄 요약

> "5분 fix 7개 먼저 쓸어담고, 30분짜리 진단(D1) 돌려서 진짜 원인 확정 후, LLM 주입(S2)으로 체감 개선 — 이 순서면 **반나절 내에 사용자가 느끼는 stupid의 50%+ 해소** 가능."
