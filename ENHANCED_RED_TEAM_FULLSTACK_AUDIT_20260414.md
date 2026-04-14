# Enhanced Red-Team Fullstack Audit — 2026-04-14

이 문서는 `ENHANCED_RED_TEAM_AUDIT_CURRENT_STATE.md` / `ENHANCED_RED_TEAM_FUNCTIONAL_BRIEF.md` / `QC_BACKLOG_AND_NEXT_STEPS.md`의 후속 audit이다.
챗봇만 까는 기존 문서 흐름에서 벗어나, SBTL_HUB **전체 스택**을 line-by-line으로 훑으며 잡은 것들을 정리한다.

Scope (이번 라운드에서 직접 읽은 것):
- `src/App.jsx` (1,200줄)
- `src/main.jsx`
- `api/chat.js`, `api/analysis.js`, `api/brave.js`, `api/translate.js`
- `lib/chat/*` 8개 모듈
- `public/data/cards.json` (337 cards — 샘플 + 전체 schema)
- `public/data/faq.json` (40 entries, 100%)
- `public/data/tracker_data.json` (50 items + sources, 100%)
- `merge_cards.py`
- `package.json`, `vercel.json`, `env.example`
- `docs/` 7개 마크다운

Scope 제외 (다음 라운드):
- `public/webtoon/*.html`
- `docs/card_payloads/`

원칙: 기존 audit가 "좋은 아키텍처, 지능 부재"까지 잡았다면, 이번엔 **실제 운영을 깨는 데이터 무결성 + 배포 환경 버그 + line 단위 로직 결함**을 잡는다.

---

## 🟥 P0 — 운영 중단급

### #1. `cards.json` 9일째 stale — "라이브 인텔리전스" 정체성 붕괴

- `cards.json`의 최신 카드 날짜 = `2026.04.13`
- 오늘 = `2026.04.14`
- 하지만 `meta.updated`는 프론트 UI에 `updated 2026.04.13`로 노출되며, 카드 추가는 `2026.04.05`에 벌크로 멈춘 뒤 `04.06~04.08` 일부 + `04.12~04.13`만 산발적.
- SBTL_HUB의 가치 제안은 "live feed"인데, 사용자가 오늘 들어오면 **어제 뉴스**만 본다.
- Home 컴포넌트의 `latestCards(kb.cards, 3, null, kstToday())`가 오늘 카드 없으면 빈 배열 반환 → **"오늘의 핵심 카드" 섹션에 "오늘 기준 등록된 뉴스카드가 아직 없습니다"** 메시지.
- 자동화 파이프라인(사용자의 W5/Vol.7 triage pipeline)과 cards.json이 **연결 끊긴 상태**.

**조치:** 오늘자 카드 병합, 또는 "live" 표기 제거.

---

### #2. `tracker_data.json` 9일째 stale — 정책 트래커 정지

```json
"meta": {
  "lastUpdated": "2026-04-05T15:00:00+09:00",
  "totalItems": 50
}
```

- 모든 50개 item의 `lastChecked: "2026-04-05"`.
- Vercel 앱 헤더에 `LAST CHECKED 2026.04.05` 노출 중.
- 사용자가 stale 정책 데이터로 의사결정 가능한 상태.

특히 위험한 항목:
- `JP-004`: 가격상한 `¥19.51→¥15.00` 4.01 시행 — "진행 중" 모니터링 항목인데 9일 업데이트 없음.
- `NA-002`: Treasury proposed regulation "Q2 2026 개시" — 이미 Q2 진입, 상태 전환 추적 불가.
- `EU-003` / `EU-006`: Battery Booster "Q1 마지막 주" → 현재 Q2 14일차, 발표 여부 미확인.

**조치:** tracker 운영 루틴 강제화. 사용자 메모리의 "2A+2B 일일 업데이트 프로토콜" 프로세스가 repo에 반영 안 됨.

---

### #3. `lib/chat/common.js`의 `loadKnowledge()` — Vercel에서 카드 못 읽을 가능성

```js
import fs from "node:fs/promises";
import path from "node:path";

function projectRoot() {
  return process.cwd();
}

export async function loadKnowledge() {
  const root = projectRoot();
  const cardsPath = path.join(root, "public", "data", "cards.json");
  // ...
  const [cardsRaw, faqRaw, trackerRaw] = await Promise.all([
    readJsonFile(cardsPath, []),       // ← fallback: []
    readJsonFile(faqPath, []),         // ← fallback: []
    readJsonFile(trackerPath, { meta: {}, items: [] }),  // ← fallback: {meta:{}, items:[]}
  ]);
```

**문제:**
- Vercel serverless function 환경에서 `process.cwd()` = `/var/task` 또는 `/var/runtime`.
- `public/` 디렉터리는 **정적 호스팅 CDN**으로 이동하고 함수 번들에 포함되지 **않음**이 기본.
- `vercel.json` 또는 `includeFiles` 설정 없음.
- `readJsonFile`의 try/catch가 실패를 삼키고 fallback 반환 → chat API는 **cards = [], faq = [], tracker.items = []** 로 동작.
- 그 결과:
  - `retrieveInternal` → `cards = []` → `ranked: []`
  - `confidence.js` → `no_internal_cards` → score 0.2 → `bucket: "low"`
  - `fallback.js` → `low_confidence` → `sourceMode: "external"` (Brave 키 있으면) or `"internal"` with 빈 답변
  - 사용자에게 "딱 맞는 내부 결과가 바로 안 잡혔어." 반복

**이게 사용자가 챗봇을 "stupid"하다고 느낀 핵심 원인 중 하나일 가능성이 매우 높음.**

**검증 방법:**
1. Vercel 배포 로그에서 chat API의 `[chat] knowledge loaded: cards=X faq=Y tracker=Z` 같은 디버그 로그 확인 (현재 api/chat.js에 로그 없음 — 추가 필요).
2. `api/chat.js`에 `console.log("cwd", process.cwd(), "cards.length", data.cards.length)` 삽입.
3. 또는 로컬 `vercel dev` 에서 Network → /api/chat 응답의 `debug.ranked.length` 확인.

**수정안:**
```js
// Option A: 함수 번들에 정적 파일 포함
// vercel.json:
// "functions": { "api/chat.js": { "includeFiles": "public/data/**" } }

// Option B: fetch로 가져오기
export async function loadKnowledge() {
  const base = process.env.VERCEL_URL
    ? `https://${process.env.VERCEL_URL}`
    : "http://localhost:3000";
  const [cards, faq, tracker] = await Promise.all([
    fetch(`${base}/data/cards.json`).then(r => r.json()),
    fetch(`${base}/data/faq.json`).then(r => r.json()),
    fetch(`${base}/data/tracker_data.json`).then(r => r.json()),
  ]);
  return {
    cards: Array.isArray(cards) ? cards : cards.cards || [],
    faq: Array.isArray(faq) ? faq : [],
    tracker: { meta: tracker?.meta || {}, items: tracker?.items || [] },
  };
}
```

Option B 권장 (public/ 파일은 정적 CDN에서 캐싱되므로 빠르고, 번들 크기도 안 늘림).

---

### #4. `tracker_data.json` 공식 URL 오류 — 사용자 클릭 404

```json
{ "name": "MOTIR 산업부 (영문)", "url": "https://english.motir.go.kr/" },
```

산업통상자원부 영문 도메인은 `motie.go.kr` (Ministry of Trade, Industry and **E**nergy). `motir` 도메인은 존재 안 함.

같은 KR tier2:
```json
{ "name": "The Elec", "url": "https://www.thelec.net/" }
```
실제 도메인 = `thelec.kr`. cards.json의 THE ELEC 출처 URL도 `thelec.kr` 사용 중. tracker sources만 깨짐.

---

### #5. `cards.json` 비표준 region `"US/KR"` — retrieval 누락

```json
{ "s": "t", "r": "US/KR", "d": "2026.03.18", "T": "LG엔솔-테슬라, 6조원 ESS 배터리 공급계약..." }
```

App.jsx의 `REG_FLAG` 는 `"US/KR": "🇺🇸"` 한 줄 추가로 렌더링 문제는 피함. 그러나 `retrieval.js`의 `isRegionMatch`:

```js
function isRegionMatch(cardRegion, scopeRegion) {
  if (!scopeRegion) return true;
  if (cardRegion === scopeRegion) return true;
  if (scopeRegion === "US" && cardRegion === "NA") return true;
  return false;
}
```

- scope.region=`"US"`, card.r=`"US/KR"` → strict 동등성 실패, NA 예외도 실패 → **누락**.
- scope.region=`"KR"`도 동일.
- 사용자 "미국 ESS 최근 뉴스" 질문 시 테슬라-LG 카드가 top signal(`s:"t"`)인데도 찾지 못함.

**추가로 발견:**
- `cards.json`의 `"r":"KR"` 일부 카드가 실제 남아공·EU 건. 예: "Sungrow, 남아프리카 1.1GWh" 카드 r=KR로 오분류.
- `src` 필드 빈 문자열 카드 다수 (원자력연 LFP 리튬 회수 4/06 카드 등).

---

### #6. `src/App.jsx` NewsDesk 검색 — `c.k` 키워드 필드 무시

```js
cards = cards.filter((c) =>
  String(c.T || "").toLowerCase().includes(sw) ||
  String(c.sub || "").toLowerCase().includes(sw) ||
  String(c.g || "").toLowerCase().includes(sw)
);
```

- `c.k` (카드마다 10개 박혀있는 키워드 배열)가 검색에 빠짐.
- "전고체" 검색 → `T`에 "전고체" 있는 카드만 매치. `k: ["전고체","ASSB","전(全)고체"]` 같이 별칭으로 박힌 카드는 누락.
- retrieval.js는 keyword 필드 사용 중 → **프론트/백엔드 검색 로직 비대칭**.

**최소 패치 (5줄):**
```js
cards = cards.filter((c) => {
  const haystack = [c.T, c.sub, c.g, ...(c.k || [])].join(" ").toLowerCase();
  return haystack.includes(sw);
});
```

---

### #7. `api/chat.js` composeCards — LLM 부재 (기존 audit 계승, P0 최우선)

(이전 챗봇 audit의 S1과 동일, 여기서는 간략히만 재명시.)

```js
// lib/chat/compose.js
function composeCards(intent, retrieval, sourceMode, confidence, debug, scope, externalLinks = [], lowConfidence = false) {
  const cards = (retrieval?.cards || []).slice(0, 4);
  // ...
  if (intent === "news") {
    answer = dateLabel ? `${regionLabel}${dateLabel} 기준 핵심 뉴스야.` : `${regionLabel}핵심 뉴스야.`;
    if (cards.length) {
      const whyLines = cards.slice(0, 3).map((c) => c.g ? `• ${c.T}\n  → ${c.g}` : `• ${c.T}`).join("\n\n");
      answer += `\n\n${whyLines}`;
    }
  }
  // ...
```

사용자 질문이 뭐든 상위 3개 카드의 `T + g`를 그대로 문자열 연결. 질문 컨텍스트 반영 0. 이게 "stupid" 체감의 70%.

**최소 PoC (30줄):**
```js
// compose.js 또는 chat.js orchestrator
async function synthesizeNewsAnswer({ message, cards, scope }) {
  const prompt = `사용자 질문: ${message}

관련 카드 (근거로만 사용, 카드에 없는 사실 추가 금지):
${cards.slice(0, 5).map((c, i) => `[${i+1}] ${c.T}
   ${c.sub || ""}
   핵심: ${c.g || ""}`).join("\n\n")}

위 카드들을 근거로 사용자 질문에 2~4문장으로 답해. 톤은 반말("~야", "~해").
카드에 없는 정보는 만들지 말고, 답을 못하면 "카드에 관련 내용이 부족해"라고만 답해.`;

  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": process.env.ANTHROPIC_API_KEY,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model: "claude-haiku-4-5-20251001",
      max_tokens: 400,
      messages: [{ role: "user", content: prompt }],
    }),
  });
  const data = await res.json();
  return data.content?.[0]?.text || null;
}
```

- 비용: Haiku 기준 call당 ~$0.001 (카드 5장 입력 + 짧은 출력).
- Brave와 동일 패턴으로 env var 보관 (`ANTHROPIC_API_KEY`, VITE_ prefix 금지).
- 실패 시 기존 템플릿으로 graceful fallback.

---

### #8. `intent.js` analysis_* vs follow_up 우선순위 버그

```js
// Analysis-type intents that require OpenAI/analysis API
if (/(왜\s*중요|중요한\s*이유|의미|implication|파급|영향|why\s*important)/.test(l)) return "analysis_why";
if (/(한국어\s*요약|요약.*한국어|번역|translate|한국어로)/.test(l)) return "analysis_summary";
if (/(심층|분석|해설|깊이|deep|ai.*분석|ai.*해설)/.test(l)) return "analysis_deep";

if (/(그\s*기사|방금|직전|저\s*카드|그\s*카드|아까\s*그|첫\s*번째|...)/.test(l) && hasCtx) {
  return "follow_up";
}
```

- "방금 카드 왜 중요해?" → `analysis_why` 먼저 매치, `follow_up` 무시.
- 사용자 의도는 "직전 카드"인데 `last_cards[0]`이 유지되지 않으면 엉뚱한 카드 분석.
- 또한 사용자 메모리의 "object-level follow-up weak" FAIL 항목의 정확한 코드 위치가 여기.

**수정안:** follow_up을 먼저 감지하고, follow_up 안에서 analysis sub-mode를 분기.

```js
const isFollowUp = /(그\s*기사|방금|직전|저\s*카드|그\s*카드|아까\s*그|첫\s*번째|...)/.test(l) && hasCtx;
const isAnalysisIntent = /(왜\s*중요|의미|.../)
  .test(l);

if (isFollowUp) {
  if (isAnalysisIntent) return "follow_up_analysis_why";
  return "follow_up";
}
if (isAnalysisIntent) return "analysis_why";
// ... rest
```

---

### #9. `retrieval.js` `matchFaq` first-match 버그

```js
function matchFaq(faq = [], query = "") {
  const l = String(query || "").toLowerCase();
  for (const f of faq) {
    if ((f.k || []).some((k) => l.includes(String(k).toLowerCase()))) {
      return { answer: f.a, keywords: f.k || [] };  // ← 첫 매치 즉시 반환
    }
  }
  return null;
}
```

faq.json 순회 순서에 답변이 종속. 현재 순서:
1. ampc → 2. feoc → 3. ira → ... → 17. lges → 18. 삼성sdi → 19. sk on → ...

질문: **"삼성SDI의 FEOC 대응은?"**
- l = "삼성sdi의 feoc 대응은?"
- faq iteration: feoc(#2) 매치 → "FEOC는 중국·러시아..." 반환.
- OK. 삼성SDI 무시되지만 그래도 feoc 정보 제공.

질문: **"삼성SDI EV 30D 어떻게 영향?"**
- l = "삼성sdi ev 30d 어떻게 영향?"
- "삼성sdi" 키워드 있는 entry가 #18. 하지만 keyword는 "samsung sdi", "삼성sdi"(소문자), etc.
- 만약 entry #18이 먼저 매치되면 → 30D 질문은 무시되고 삼성SDI 회사 소개 반환.

**수정안:** 스코어 기반 (매칭 키워드 수) 최고값 반환.
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

---

### #10. `confidence.js` news intent infinite-fallback 가능성

```js
if (intent === "news" && tokenCoverage < 0.25 && top < 18) base -= 0.1;
```

`news` intent에서 `selectNewsCards` 로직:
```js
function selectNewsCards(cards, query, scope = {}, limit = 4) {
  const scored = lexicalSearchCards(cards, query, Math.max(limit + 2, 6), scope);
  if (scored.length) return scored.slice(0, limit);
  const targetDate = scope?.date || null;
  return latestCards(cards, limit, scope?.region || null, targetDate);
}
```

- lexical 검색 실패 시 `latestCards`로 fallback.
- `latestCards`의 결과 카드에는 `_score` 없음 (undefined).
- `confidence.js`의 `top = Number(cards[0]?._score || 0)` → top=0.
- `top < 18` → `-0.1`.
- base가 충분히 못 올라가서 `bucket="low"` 또는 `"medium"` → fallback.js trigger → Brave fallback (또는 hybrid).
- **"오늘 뉴스" 같은 질문이 있을 때 내부 카드가 충분히 있어도 fallback 모드로 빠짐.**

**수정안:**
- `latestCards` 반환 카드에 `_score = 15` (의사 점수) 부여.
- 또는 confidence.js에서 `retrieval.mode === "latest_fallback"` 플래그 감지 시 다른 base 공식 사용.
- retrieval.js의 selectNewsCards가 모드를 반환하도록 개선:
```js
function selectNewsCards(...) {
  const scored = lexicalSearchCards(...);
  if (scored.length) return { cards: scored, mode: "scored" };
  const fallback = latestCards(...);
  return { cards: fallback.map(c => ({ ...c, _score: 15 })), mode: "latest" };
}
```

---

### #11. `faq.json` 데이터 품질 — 코드 현실과 lying

마지막 entry ("콘텐츠 허브"):
```json
"a": "🏠홈: ..., 📨뉴스레터: ..., 🎨웹툰: ..., 📊트래커: ..., 🤖챗봇: ..."
```

**App.jsx의 `CATS` 상수:**
```js
const CATS = [
  { key: "all", label: "HOME", icon: "🔋" },
  { key: "news", label: "NEWS", icon: "📰" },
  { key: "webtoon", label: "TOON", icon: "🎨" },
  { key: "tracker", label: "TRCK", icon: "📊" },
  { key: "chatbot", label: "AI", icon: "🤖" },
];
```

Newsletter 탭 없음. FAQ가 과거 UI를 가리키고 있음. 챗봇이 이 FAQ를 답변으로 반환하면 사용자에게 **존재하지 않는 탭을 안내**함.

또 "SBTL 회사소개" entry: "대전 본사 + 연구센터 운영" — 사용자 메모리의 **평촌(대전 평촌산업단지) 신규 거점** 카드 반영 안 됨.

---

### #12. `faq.json` / `tracker_data.json` AMPC `$` 인코딩 손상

`tracker_data.json` KR-001 `detail`:
```
• AMPC 구조: 1kWh당 최대 5 (셀 5 + 모듈 0). 생산량 비례 → 대량 생산 시 수혜 극대화
• AMPC 수혜 극대화. 3사 기준 연간 1조+
• 3사 AMPC 누적 수령액: ~6조 원 (2023-2025)
```

`$35`, `$10`, `$45`가 모두 `5`, `0`으로 뭉개짐. `$` 기호 + 2자리 숫자가 인코딩 단계에서 사라진 것으로 추정. (MDX/escape 이슈 가능성)

`faq.json`에서는 AMPC entry는 정상:
```
"셀 $35/kWh, 모듈 $10/kWh"
```

하지만 동일 파일의 `§30C` entry: "상업용 설비당 최대 USD 100,000." 여기도 tracker detail에서는 `00,000`로 손상됨.

**위험:** 사용자가 tracker 상세 열람 시 "AMPC가 1kWh당 $5인가 $45인가?" 같은 오해 가능. 챗봇이 tracker 데이터를 근거로 답변하면 오답.

---

## 🟧 P1 — 보안 / 구조

### #13. `env.example` — VITE_ prefix 시크릿 유출 위험

```
# env.example 전체
VITE_BRAVE_KEY=여기에_새_API_키_입력
```

- Vite의 `VITE_*` prefix env는 **클라이언트 번들에 주입**됨.
- `api/brave.js`는 `process.env.BRAVE_KEY || process.env.VITE_BRAVE_KEY`로 둘 다 받음.
- 사용자가 env.example 따라 `VITE_BRAVE_KEY`로 설정 → Brave API key가 프론트엔드 JS에 박힘 → 누구나 devtools에서 추출 가능.
- 사용자 메모리에 "Brave API key stored as `VITE_`-less `BRAVE_KEY`"로 되어 있는데 env.example은 그 반대.

**수정안:**
```
# Brave Search API Key
# 1. https://brave.com/search/api 에서 발급
# 2. .env.local 에 BRAVE_KEY=... 입력 (VITE_ prefix 쓰지 말 것 — client bundle에 노출됨)
# 3. Vercel 프로젝트 환경변수에도 BRAVE_KEY 로 등록
BRAVE_KEY=여기에_API_키_입력

# Anthropic API Key (compose.js LLM 주입 시)
ANTHROPIC_API_KEY=sk-ant-...

# OpenAI API Key (api/analysis.js 용)
OPENAI_API_KEY=sk-...
```

그리고 `api/brave.js`에서 `VITE_BRAVE_KEY` fallback 제거.

---

### #14. `REGION_POLICY` 중복 — App.jsx + lib/chat/common.js

두 파일에 같은 이름 상수가 다른 내용으로 존재:

**`src/App.jsx`의 REGION_POLICY:** 키는 `NA/EU/CN/KR/JP/GL`. `NA`가 "미국 정책" 전체 (policies 4개, watchpoints 3개).

**`lib/chat/common.js`의 REGION_POLICY:** 키는 `US/EU/CN/KR/JP/GL/NA`. `US`와 `NA`가 둘 다 있음. `NA`는 `US`의 요약 버전 (policies 2개, watchpoints 2개).

결과:
- Tracker UI (App.jsx 사용) → `NA`로 상세 데이터 렌더.
- Chatbot (lib/chat/compose.js → common.js 사용) → scope.region=`"US"`면 US 풀 데이터, scope.region=`"NA"`면 약식 NA 데이터. **같은 정책 질문에 다른 답.**

`tracker_data.json`의 item `r` 필드는 전부 `NA` 코드 사용 → chat이 tracker 연동하면서 region=`NA`로 들어갈 수 있음 → 약식 답변 노출.

**수정안:** `public/data/region_policy.json`으로 외부화. 둘 다 fetch.

---

### #15. `src/App.jsx` 1,200줄 monolith — 기존 audit 계승

(자세한 건 이전 audit. 여기서는 추가 발견만.)

- `ErrorBoundary` 내 `T(dark)` 호출 — 에러 발생 시점에 dark prop이 stale일 가능성.
- `App = () => { const [dark, setDark] = useState(true); return <ErrorBoundary dark={dark}><AppContent /></ErrorBoundary>; }` — **ErrorBoundary의 dark는 항상 true**. AppContent 내부 setDark는 ErrorBoundary까지 전파 안 됨. 라이트 모드에서 에러 발생 시 ErrorBoundary만 다크로 그림.
- `AppContent` 내부에 자체 `dark` 상태 있음. 상위 App의 `dark`는 **dead state**.

---

### #16. 톤 불일치 — 한 대화에 4가지 화자

- ChatBot 초기 메시지 (App.jsx): "안녕, 강차장이야 🔋" — **반말**.
- composeCards: "핵심 뉴스야", "비교할 내부 카드가 부족해" — **반말**.
- composeFromFaq: "관련 FAQ를 찾지 못했어" — 반말. but faq.a 자체는 "...수령했습니다" — **존댓말**.
- api/analysis.js 프롬프트 (이전 audit에서 본 거): "...입니다", "...하세요" — **격식**.

사용자가 "LFP 뭐야" 묻고 → FAQ 매치 → "LFP는 리튬인산철입니다" (존댓말). 다음 질문 "왜 중요?" → analysis_why → "LFP는 NCM 대비 ... 중요합니다" (존댓말). 다음 질문 "오늘 뉴스" → composeCards → "핵심 뉴스야" (반말). **같은 상담사가 톤을 네 번 바꿈.** 신뢰감 붕괴.

**수정안:** 전역 톤 = 반말("-야/-해"). faq.a 전부 리라이트 + analysis 프롬프트 수정.

---

### #17. `vercel.json` dead routes

```json
{
  "rewrites": [
    { "source": "/api/brave", "destination": "/api/brave" },
    { "source": "/api/claude", "destination": "/api/claude" },
    { "source": "/api/translate", "destination": "/api/translate" },
    { "source": "/((?!api/).*)", "destination": "/index.html" }
  ]
}
```

- 처음 3개는 자동 매핑되는 걸 명시 — **무효**.
- `/api/claude` 목적지는 `api/claude.js` 파일 자체 없음 — **dead**.
- `/api/translate`는 `api/translate.js` 파일 존재하지만 **어디서도 호출 안 됨** — dead feature.

**수정안:**
```json
{
  "rewrites": [
    { "source": "/((?!api/).*)", "destination": "/index.html" }
  ]
}
```

api/translate.js는 삭제 또는 유지. 사용자가 외국어 카드 원문 번역 필요하면 `original` 필드 추가가 더 맞음.

---

## 🟨 P2 — 작은 것들

### #18. `cards.json` `g` 필드 잘림 여러 건

다수 카드의 `g`가 문장 중간에 끝남:
- "...이라는 새로운\"" (빈 따옴표만 남음)
- "...확인한\" 신호다" 같은 깨짐
- "이 카드는 ... 기회다" 없이 "이 카드는 ... 기"로 끝

원인 추정: merge_cards.py의 `build_compact`에서 `g` 길이 제한:
```python
'g': c.get('gate','')[:120] if sig in ('t','h') else c.get('gate','')[:60],
```
120자 / 60자로 자르는데 중간에 끊김. 시그널 별 길이 차이도 있어서 TOP 카드는 완성되고 MID 카드는 잘림.

**수정안:** 문장 경계로 자르기 (`. `, `다.`, `。` 기준). 또는 자르지 말고 원문 유지.

---

### #19. `merge_cards.py` 중복 제거 robustness

현재: `key = c.get('T','')[:35].lower().replace(" ","")`

- 한국어 카드 기준 35자는 애매 (영어 혼용 카드는 늘어남).
- `.lower()`는 한국어에 영향 없음.
- "LG엔솔" vs "LG에너지솔루션" vs "LGES" → 서로 다른 key로 처리 → 같은 사건 중복 입력 가능.
- URL 기반 dedupe가 더 안전.

**수정안:**
```python
def dedupe_key(card):
    url = card.get('url', '')
    if url:
        return ('url', url.split('?')[0].rstrip('/'))  # query/trailing slash 정규화
    return ('title', card.get('T','')[:50].lower().replace(" ","").replace("-",""))
```

---

### #20. `merge_cards.py` IndexError 위험

```python
sig = c.get('signal','mid').lower()[0]
```

`c['signal']`이 빈 문자열이면 `"".lower()[0]` → `IndexError`.

**수정안:**
```python
sig_raw = c.get('signal') or 'mid'
sig = sig_raw.lower()[0] if sig_raw else 'm'
```

---

### #21. `cards.json` schema 검증 부재

merge 후 검증 없음:
- `s` 필드 값이 `t/h/m/i` 외 값일 수 있음 (SIG_C lookup 실패 → 렌더 색상 undefined).
- `r` 필드 값이 REG_FLAG에 없는 값일 수 있음 (이미 `US/KR` 케이스 있음).
- `d` 필드 포맷 불일치 (`2026.04.13` vs `2026-04-13` 섞일 가능성).

**수정안:** merge_cards.py 마지막에 간단한 validator:
```python
VALID_SIG = {'t','h','m','i'}
VALID_REGION = {'KR','US','CN','EU','JP','GL','NA','US/KR'}
errors = []
for c in merged:
    if c.get('s') not in VALID_SIG: errors.append(('bad_signal', c.get('T','')[:30]))
    if c.get('r') not in VALID_REGION: errors.append(('bad_region', c.get('T','')[:30], c.get('r')))
    if not c.get('d'): errors.append(('no_date', c.get('T','')[:30]))
    if not c.get('url'): errors.append(('no_url', c.get('T','')[:30]))
if errors:
    print(f"⚠️  {len(errors)}건 검증 실패:")
    for e in errors[:10]: print(f"   {e}")
```

---

### #22. `public/webtoon/*.html` 미검증

`WEBTOON_COLLECTIONS[0].items`가 가리키는 4개 URL:
- `/webtoon/lfp-uncomfortable-truths.html` (landing)
- `/webtoon/lfp-two-misconceptions-ep1.html`
- `/webtoon/lfp-two-misconceptions-ep2.html`
- `/webtoon/who-pays-bonus1.html`

실파일 존재 여부 확인 필요. `public/webtoon/`에 디렉터리는 있는데 내용 직접 확인 안 함. 없으면 사용자가 웹툰 카드 클릭 시 404.

---

### #23. `fetchJsonFile` 에러 silence

```js
fetchJsonFile("/data/cards.json", refreshKey, hardRefresh)
  .then((d) => d.cards || d)
  .catch(() => []),  // ← 에러 삼킴
```

네트워크 실패 / JSON 파싱 실패 / 500 에러 → 빈 배열 → UI "카드 0개". 사용자는 원인 모름. 최소한 `console.error` + UI 토스트.

---

### #24. React key `${date}-${i}` 불안정

```jsx
{visible.filter((c) => c.d === date).map((card, i) =>
  <NewsItem key={`${date}-${i}`} card={card} dark={dark} />
)}
```

같은 날짜 안에서 index를 키로 사용 → 필터 바뀌면 같은 키가 다른 카드에 매핑 → React reconciliation 어색. `card.url || card.T` 기반이 안전.

---

### #25. `scope.js` 엔티티 추출 노이즈 폭탄

```js
const entityCandidates = new Set();
for (const rt of rawTokens) {
  if (/[A-Z]/.test(rt) || /\d/.test(rt) || /[&+-]/.test(rt)) {
    entityCandidates.add(rt);
  }
}
for (let i = 0; i < topicTokens.length - 1; i++) {
  const a = topicTokens[i];
  const b = topicTokens[i + 1];
  if (a.length >= 2 && b.length >= 2) entityCandidates.add(`${a} ${b}`);
}
for (const tt of topicTokens) {
  if (tt.length >= 3) entityCandidates.add(tt);
}
```

"오늘 LFP 배터리 상황" 질문:
- rawTokens: ["오늘", "LFP", "배터리", "상황"]
- `[A-Z]` 매치: "LFP" → 1개
- topicTokens (stopword "오늘" 제거 후): ["LFP", "배터리", "상황"]
- 인접 pair: "lfp 배터리", "배터리 상황"
- length >= 3: "LFP", "배터리", "상황"
- 최종 entity_candidates: ["LFP", "lfp 배터리", "배터리 상황", "배터리", "상황"]
- retrieval.js에서 각 candidate가 카드 텍스트와 부분 매치되면 **ENTITY_MATCH_BONUS+8 (중첩 아님, 한 번만)** — 여기는 OK.
- 그러나 "상황"이 카드 제목/본문에 들어간 모든 카드에 +8 부여될 수 있음. **"상황"은 엔티티가 아니라 서술어인데.**

**수정안:**
1. stopword 확장: "상황", "현황", "소식", "이슈", "관련", "한국", "미국", "중국", "유럽", "일본", "최신" 추가.
2. 엔티티 추출은 배터리 도메인 사전 기반으로 제한. 또는 대문자/숫자/특수문자가 **있는 토큰만** (현재 로직 그대로) 유지하고 topicTokens 전수 추가는 제거.

---

### #26. `scope.js`의 `detectRegion` — 한자/별칭 누락

```js
if (/(한국|국내|kr)/.test(l)) return "KR";
if (/(미국|북미|us|america)/.test(l)) return "US";
if (/(중국|cn|china)/.test(l)) return "CN";
if (/(유럽|eu|europe)/.test(l)) return "EU";
if (/(일본|jp|japan)/.test(l)) return "JP";
```

못 잡는 것:
- "美" (미국 한자)
- "中" / "중"
- "日" / "일본"
- "韓"
- "EU", "US" 대소문자는 `toLowerCase()` 선행돼서 OK
- 하지만 cards.json 제목에는 "美", "中" 빈번 사용 ("美 재무부, Ford...")

scope가 region 못 잡으면 retrieval이 region boost 못 줌.

---

### #27. `compose.js`의 `c.g` 검증 없는 출력

```js
const whyLines = cards.slice(0, 3).map((c) =>
  c.g ? `• ${c.T}\n  → ${c.g}` : `• ${c.T}`
).join("\n\n");
```

#18의 잘린 `g` 필드가 그대로 사용자에게 노출. "새로운\"" 같은 깨진 문자열이 챗봇 답변에 그대로 붙음.

**수정안:**
```js
const cleanG = (g) => {
  if (!g) return null;
  const trimmed = g.trim();
  // 미완성 문장 감지 — 마지막 문자가 문장 부호가 아닌 경우
  if (!/[.?!다。]$/.test(trimmed)) return null;
  if (/["']$/.test(trimmed) && !/다["']$/.test(trimmed)) return null;
  return trimmed;
};
// ...
c.g && cleanG(c.g) ? `• ${c.T}\n  → ${cleanG(c.g)}` : `• ${c.T}`
```

---

### #28. `intent.js` regex 한글 변형 누락

- "결국 핵심이 뭐야?" → summary 미매치 ("핵심" 있지만 "요약/정리/브리핑" 패턴은 없음. 아, "핵심"은 포함돼 있음 → OK).
- "이거 어떤 의미야?" → `analysis_why` 매치 ("의미"). OK.
- "방금 그거 해설해줘" → `analysis_deep` 매치 ("해설"). 그런데 "방금" 있어서 follow_up도 매치. **#8 버그.**
- "LFP랑 NCM 뭐가 달라?" → compare 매치? `/(비교|차이|vs|대비|어떤 게|뭐가 더)/` — **"달라"는 없음**. → fallthrough → news 매치? "뉴스" 없음 → general. **compare 의도인데 general로 처리.**

**수정안:** compare regex에 "다르" "구별" "대조" 추가.

---

### #29. `package.json` — dev dep 최소, prod dep 누락

현재:
```json
"dependencies": { "react": "^18.2.0", "react-dom": "^18.2.0" }
```

- `api/analysis.js`는 OpenAI fetch 호출 → OK (SDK 안 씀).
- `api/brave.js`도 fetch → OK.
- `lib/chat/common.js`는 `node:fs/promises`, `node:path` — Node 내장 → OK.
- **위 audit #3에서 fetch 기반으로 loadKnowledge 바꾸면 deps 추가 없음.**

그래도 명시적 `"engines": { "node": ">=18" }` 추가 권장 (top-level await, fetch 기본).

---

### #30. `docs/` 문서와 현실 드리프트

- `WORKFLOW.md`의 "FAQ는 `public/data/faq.json`" — 맞음.
- `OPERATIONS.md`의 "`public/data/cards.json` total 확인" — 맞음.
- `OPERATIONS.md`의 "카드 DB가 App.jsx에 들어있다고 오해" — 이미 분리됐으므로 outdated (과거 흔적).
- `STRENGTHENING_PLAN.md` "README를 실제 구조에 맞게 수정" — README 자체 본 audit에서 미확인. 아마 outdated.
- `CARD_WORKFLOW_VFINAL.md` "현재 GitHub `main`의 `public/data/cards.json` 기준본은 `updated: 2026-04-06`, `total: 298`" — 현재 실제로는 `updated: 2026.04.13`, `total: 337`. 문서 stale.

문서 블록이 서로 일치하지 않아 신규 협업자가 어떤 문서를 신뢰해야 할지 모름.

---

## 부록 — 안 본 것 (다음 라운드)

- `public/webtoon/*.html` 4개 파일 (EP.1, EP.2, bonus, landing)
- `public/manifest.json` PWA 메타데이터 (sw.js 부재는 확인)
- `docs/card_payloads/` 하위 디렉터리
- `README.md` (repo root)
- `merge_cards_raw_payload_20260407_safe_2cards.json` helper payload (OPERATIONS addendum의 정책 위반 — repo에 남아있음)

---

## 우선순위 통합

| # | 제목 | 카테고리 | 영향 | 공수 |
|---|---|---|---|---|
| 1 | cards.json 9일 stale — 오늘자 카드 merge | 🟥 운영 | ★★★★★ | 1h |
| 2 | tracker_data.json 9일 stale — 50 items refresh | 🟥 운영 | ★★★★★ | 2h |
| 3 | common.js cwd() → fetch 전환 | 🟥 인프라 | ★★★★★ | 30m |
| 4 | composeCards LLM 주입 (PoC) | 🟥 챗봇 | ★★★★★ | 1h |
| 5 | NewsDesk 검색 c.k 필드 포함 | 🟥 챗봇 | ★★★★ | 5m |
| 6 | tracker URL 오류 (motir, thelec.net) | 🟥 데이터 | ★★★★ | 5m |
| 7 | intent.js follow_up + analysis 우선순위 | 🟥 챗봇 | ★★★★ | 15m |
| 8 | matchFaq 스코어 기반 전환 | 🟥 챗봇 | ★★★ | 15m |
| 9 | env.example VITE_BRAVE_KEY 제거 | 🟥 보안 | ★★★★ | 5m |
| 10 | cards.json region "US/KR" 정규화 | 🟥 데이터 | ★★★ | 30m |
| 11 | confidence.js news fallback 점수 로직 | 🟥 챗봇 | ★★★ | 20m |
| 12 | faq.json 콘텐츠 허브 entry 업데이트 | 🟥 데이터 | ★★★ | 10m |
| 13 | REGION_POLICY → public/data/region_policy.json | 🟧 구조 | ★★★ | 30m |
| 14 | 챗봇 톤 통일 (전부 반말) | 🟧 UX | ★★ | 1h |
| 15 | vercel.json dead rewrites 제거 | 🟧 코드 | ★ | 2m |
| 16 | App.jsx 모듈 분리 (Phase 1: lib/ 추출) | 🟧 구조 | ★★★ | 1d |
| 17 | merge_cards.py URL dedupe + validator | 🟨 스크립트 | ★★ | 30m |
| 18 | cards.json g 필드 잘림 문장경계 fix | 🟨 데이터 | ★★ | 20m |
| 19 | scope.js entity 노이즈 제거 + region 한자 | 🟨 챗봇 | ★★ | 20m |
| 20 | intent.js compare regex 확장 | 🟨 챗봇 | ★ | 5m |

---

## 한 줄 결론

기존 audit는 **"좋은 아키텍처, 지능 부재"** 까지 잡았음.

이번 audit의 추가 발견은 **"좋은 아키텍처, 지능 부재, 그리고 데이터·배포·보안의 silent 실패"**.

챗봇이 stupid해 보이는 근본 원인은 3개 복합:
1. **compose에 LLM이 없다** (기존 audit P0-1, 70%)
2. **Vercel 함수가 cards.json을 못 읽을 가능성** (이번 audit #3, 20%)
3. **데이터 자체가 9일 stale** (이번 audit #1, #2, 10%)

P0 1~4번을 동시에 해결하지 않으면, 어느 하나만 고쳐도 다른 둘이 여전히 "stupid" 체감을 유지시킨다.
