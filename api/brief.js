// ============================================================================
// POST /api/brief — 필터된 카드 범위를 "흐름 브리프"로 합성
// 출력은 보고서 붙여넣기용 문어체 + 문장별 [n] 카드 인용 (챗봇 반말 톤 미적용)
//
// 두 모드(R10):
//  - flat 모드(기존): { scopeLabel, cards[] } — 좁은 범위(피드 필터 조합·내워치)용.
//  - 축 모드: { scopeLabel, axes: [{key, cards[]}] } — 넓은 범위(전체 주간/월간)용.
//    무관한 40장에서 하나의 서사를 강요하면 나열로 후퇴한다(실측: 커버리지 13~23%,
//    문장당 카드 7~10장 버킷 요약). 클라이언트가 '이야기가 되는 축'을 골라 보내면
//    축마다 한 문단을 쓴다 — 문단당 카드 ≤10장이라 버킷 요약이 구조적으로 불가능.
// 품질 가드: 경어체·무인용 문장(전량 무인용)·JSON 실패를 검출하면 1회 재생성.
//    실측에서 같은 프롬프트가 확률적으로 경어체·총평 문장을 내는 것을 확인 — 프롬프트
//    금지만으로는 안 잡히고, 검출-재시도가 결정적이다.
// ============================================================================

import { callLLM } from "../lib/chat/llm.js";

const MAX_CARDS = 40;
const MAX_AXES = 4;
const MAX_PER_AXIS = 10;

function setCors(res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
}

function clip(v, n) {
  return String(v || "").replace(/\s+/g, " ").trim().slice(0, n);
}

function leanCard(c, n) {
  return {
    n,
    date: clip(c.date, 10),
    region: clip(c.region, 6),
    title: clip(c.title, 120),
    fact: clip(c.fact, 420),
    implication: clip(c.implication, 300),
    quote: clip(c.quote, 220),
    quoteSource: clip(c.quoteSource, 60),
  };
}

// 잘린 서사를 '마지막 완결 문장'까지 자른다. 경계는 인용 + 문장부호("[n]." / "[1, 2]!").
//
// 인용만으로는 경계가 아니다. 프롬프트(규칙 2)는 문장 끝에 [n]을 요구하지만 모델은
// 문장 중간에도 인용을 단다 — 실서사 13편 126개 인용 실측: 마침표가 뒤따르는 것 93개
// (73.8%), 마침표 없는 맨인용 33개인데 33개 전부가 문장 중간이었다("…전환하고 [34],
// 삼성SDI도…", "…준비하는 등 [35] ESS 사업…"). 종결형 뒤 맨인용은 0개.
// 그래서 맨인용을 경계로 받으면 연결형에서 끊긴 꼬리가 나간다(절단점 1549개 시뮬:
// 맨인용 허용 19.4% vs 마침표 필수 0%). 마침표를 필수로 둔다.
//
// 경계를 못 찾으면 통째로 버린다(""). 이게 이번 수정의 본체다 — 예전엔 경계가 없으면
// 원문을 그대로 뒀고(잘린 서사의 2.5%: 첫 완결 문장 전에 상한이 떨어진 경우), 그 반토막이
// 성공 응답으로 나갔다. 빈 문자열은 호출부에서 no-narrative → 재시도로 이어진다.
export function trimToLastCitation(text) {
  const s = String(text);
  let cut = -1;
  for (const m of s.matchAll(/\[\s*\d+(?:\s*,\s*\d+)*\s*\]\s*[.!?]/g)) cut = m.index + m[0].length;
  return cut > 0 ? s.slice(0, cut).trim() : "";
}

export function parseJsonLoose(text) {
  if (!text) return null;
  let body = String(text).trim();
  const fence = body.match(/```(?:json)?\s*([\s\S]*?)```/);
  if (fence) body = fence[1].trim();
  else body = body.replace(/^```(?:json)?\s*/, ""); // 토큰 상한에 잘려 닫는 fence가 없는 응답
  const start = body.indexOf("{");
  const end = body.lastIndexOf("}");
  if (start >= 0 && end > start) body = body.slice(start, end + 1);
  try { return JSON.parse(body); } catch { /* 아래에서 잘린 JSON 구제 */ }
  // 잘린 응답 구제 — narrative만이라도 살린다. 토큰 상한에 걸리면 문자열 리터럴이 닫히지도
  // 않은 채 끝나므로(실측: 축 3개가 1600토큰에서 잘려 ```json 원문이 그대로 degraded로 나가고
  // watch가 통째로 사라짐), 닫힌 경우와 안 닫힌 경우를 모두 처리한다.
  const key = body.search(/"narrative"\s*:\s*"/);
  if (key < 0) return null;
  const open = body.indexOf('"', body.indexOf(":", key)) + 1;
  // 이스케이프되지 않은 종료 따옴표 탐색 (없으면 끝까지 = 잘린 응답)
  let close = -1;
  for (let i = open; i < body.length; i += 1) {
    if (body[i] === "\\") { i += 1; continue; }
    if (body[i] === '"') { close = i; break; }
  }
  const truncated = close < 0;
  const lit = body.slice(open, truncated ? body.length : close).replace(/\\+$/, ""); // 끝에 걸친 이스케이프 제거
  let narrative = null;
  for (let cut = lit.length; cut > 0 && narrative === null; cut = lit.lastIndexOf("\\n", cut - 1) > 0 ? lit.lastIndexOf("\\n", cut - 1) : -1) {
    try { narrative = JSON.parse(`"${lit.slice(0, cut).replace(/\\+$/, "")}"`); } catch { /* 더 짧게 재시도 */ }
  }
  if (narrative === null) { try { narrative = JSON.parse(`"${lit}"`); } catch { return null; } }
  if (truncated) narrative = trimToLastCitation(narrative);
  if (!narrative.trim()) return null;
  const watch = [];
  const wIdx = body.indexOf('"watch"');
  if (wIdx >= 0) {
    for (const w of body.slice(wIdx + 7).matchAll(/"((?:[^"\\]|\\.)*)"/g)) {
      try { const s = JSON.parse(`"${w[1]}"`); if (s) watch.push(s); } catch { /* 미완결 리터럴은 버린다 */ }
    }
  }
  return { narrative, watch: watch.slice(0, 4), salvaged: true };
}

// 축 모드 narrative의 JSON 뼈대 — '실제 축 이름'으로 만든 템플릿을 프롬프트에 박는다.
// generic 예시("【축1】 ...\n\n【축2】 ...")만 주면 모델이 확률적으로 첫 축만 쓰고 멈춘다
// (실측: 2026-06 지역별 4축 요청 6회 중 3회가 1문단 — 재시도 가드가 발동해도 재시도본까지
// 붕괴하면 1축이 그대로 나간다). 요구 문단 수·이름·순서를 출력 형식 자체에 새겨 앵커한다.
export function axisSkeleton(keys) {
  return (keys || []).map((k) => `【${k}】 ...`).join("\\n\\n");
}

function cardLines(cards) {
  return cards.map((c) => {
    const bits = [`[${c.n}] ${c.date} ${c.region} — ${c.title}`];
    if (c.fact) bits.push(`  사실: ${c.fact}`);
    if (c.implication) bits.push(`  함의: ${c.implication}`);
    if (c.quote) bits.push(`  원문인용(매체 표현 — 검증된 사실 아님, ${c.quoteSource || "출처"}): "${c.quote}"`);
    return bits.join("\n");
  }).join("\n");
}

// 공통 규칙 — flat/축 모드가 공유. 실측 실패 사례에서 역산한 금지 조항 포함.
const COMMON_RULES = [
  "1. 반드시 아래 제공된 카드의 사실만 사용한다. 새로운 사실·수치·해석을 만들어내지 않는다. 카드에 원인이 명시되지 않은 결과에 원인을 붙이지 않는다. '~할 예정'을 '~했다'로 바꾸지 않는다(시제·확실성 유지).",
  "2. 모든 문장 끝에 근거 카드 번호를 [n] 또는 [n, m] 형식으로 붙인다(문장당 최대 3개). 인용을 붙일 수 없는 총평·도입·맺음 문장은 아예 쓰지 않는다 — 첫 문장부터 특정 카드의 사실로 시작한다. 두 사건을 인과로 잇는 문장은 두 카드를 함께 인용한다.",
  "3. 문체: 보고서용 문어체. 모든 서술어를 '~했다/~이다/~한다' 평서형으로 통일한다. 경어체('~습니다', '~ㅂ니다', '~에요')·반말·이모지·마크다운 금지. 다음 상투구 금지: '~하는 모습을 보였다', '~움직임을 보였다', '~의지를 보였다', '~노력을 기울였다', '활발하게 전개', '~요약입니다'.",
  "4. 지역·국가를 주어로 쓸 때는 그 카드의 사실이 실제로 그 지역 것인지 확인한다(카드의 region과 사실 본문 기준). 업계 단체·기업의 행위를 정부의 행위로 쓰지 않는다. '원문인용'은 매체 표현이므로 '세계 최초' 같은 수식을 사실로 승격하지 않는다.",
  "5. watch는 '지켜볼 것' 2~4개. 각 항목은 카드의 함의에 명시된 후속 단계·판단 기준을 근거로, 확인할 주체·시점·지표가 드러나게 쓴다. '~동향', '~추이', '~주목해야 한다'처럼 확인 방법이 없는 문구 금지. 각 항목 끝에 [n] 인용(최대 3개).",
].join("\n");

async function generateOnce({ system, user, maxTokens }) {
  const result = await callLLM({ system, user, maxTokens, temperature: 0.3, timeoutMs: 25000 });
  // status·detail(업스트림 에러 본문 스니펫)을 그대로 올린다 — 502만 보고는 폴백 실패의
  // 실원인(모델 폐기 404 vs 단일요청 TPM 초과 413 vs 요청 거부 400)을 구별할 수 없다.
  if (!result?.text) return { error: result?.error || "llm-failed", provider: result?.provider || null, status: result?.status || null, detail: result?.detail || null };
  const parsed = parseJsonLoose(result.text);
  return { parsed, raw: result.text, provider: result.provider || null };
}

// 품질 검출 — 실패 사유 목록을 돌려준다 (비면 통과).
// axisKeys를 주면 축 누락도 검출한다: 축 모드에서 재시도본이 축을 통째로 빠뜨리고도
// 경어체·인용만 깨끗하면 '이슈 0'으로 채택되던 결함이 있었다(실측: 축 4개 요청에
// 재시도본이 【저장장치】 한 문단만 반환 → 커버리지 21%로 baseline 수준 후퇴).
export function qualityIssues(parsed, axisKeys = null) {
  if (!parsed?.narrative) return ["no-narrative"];
  const issues = [];
  const text = String(parsed.narrative);
  if (/(습니다|합니다|입니다|됩니다|어요|에요)[.\s]/.test(text)) issues.push("polite-tone");
  const sents = text.split(/(?<=[.!?])\s+/).map((s) => s.trim()).filter(Boolean);
  const noCite = sents.filter((s) => !/\[\d/.test(s)).length;
  if (sents.length > 0 && noCite / sents.length > 0.34) issues.push("uncited-sentences"); // 1/3 넘게 무인용이면 총평 나열로 후퇴한 것
  if (Array.isArray(axisKeys) && axisKeys.length) {
    const missing = axisKeys.filter((k) => !text.includes(`【${k}】`));
    if (missing.length) issues.push(`missing-axes:${missing.length}`);
  }
  return issues;
}

// 재시도 채택 규칙 — narrative 존재 > 축 완결성 > 이슈 수.
// 첫 응답이 'JSON은 파싱되나 narrative 없음'({"watch":[...]} 류)일 때, 재시도가
// narrative를 가져와도 남은 이슈 수가 같으면(1<1 false) 버려져 degraded 원문으로
// 떨어지는 결함이 있었다 — 재시도의 존재 이유가 바로 그 경로인데.
// 축 모드에선 '축을 더 많이 담은 쪽'이 이슈 수보다 우선한다 — 축 3개를 버리고 얻은
// 무결점 한 문단은 개선이 아니라 후퇴다.
export function pickBetterAttempt(first, second, firstIssues, axisKeys = null) {
  if (!second || second.error || !second.parsed) return first;
  const firstHasNarrative = !!first.parsed?.narrative;
  const secondHasNarrative = !!second.parsed.narrative;
  if (!secondHasNarrative) return first;
  if (!firstHasNarrative) return second; // 유일하게 쓸 수 있는 쪽
  if (Array.isArray(axisKeys) && axisKeys.length) {
    const covered = (p) => axisKeys.filter((k) => String(p.narrative).includes(`【${k}】`)).length;
    const c1 = covered(first.parsed), c2 = covered(second.parsed);
    if (c2 !== c1) return c2 > c1 ? second : first; // 축을 더 담은 쪽이 이긴다
  }
  return qualityIssues(second.parsed, axisKeys).length < firstIssues.length ? second : first;
}

export default async function handler(req, res) {
  setCors(res);
  if (req.method === "OPTIONS") return res.status(200).end();
  if (req.method !== "POST") return res.status(405).json({ ok: false, error: "method-not-allowed" });

  let payload = req.body;
  if (typeof payload === "string") {
    try { payload = JSON.parse(payload); } catch { payload = null; }
  }
  const scopeLabel = clip(payload?.scopeLabel, 120) || "선택 범위";

  // ---- 입력 구성: 축 모드 vs flat 모드 ----
  let system;
  let user;
  let maxTokens;
  let axisKeys = null; // 축 모드일 때 품질 가드가 축 누락을 검출하는 데 쓴다
  const axesIn = Array.isArray(payload?.axes) ? payload.axes.slice(0, MAX_AXES) : null;
  if (axesIn && axesIn.length) {
    // 축 모드 — 전역 연속 번호를 부여하고 축 경계를 프롬프트에 명시
    let n = 0;
    const axes = axesIn.map((ax) => {
      const cards = (Array.isArray(ax.cards) ? ax.cards : []).slice(0, MAX_PER_AXIS).map((c) => leanCard(c, ++n));
      return { key: clip(ax.key, 40) || "축", cards };
    }).filter((ax) => ax.cards.length >= 2);
    if (!axes.length || n < 4) return res.status(400).json({ ok: false, error: "need-axes-with-cards" });
    system = [
      "너는 배터리·ESS·EV 공급망 산업의 동향 브리프 작성자다.",
      "이 브리프는 '축' 단위로 쓴다. 축은 서로 이어지는 사건 묶음이다.",
      "규칙:",
      COMMON_RULES,
      `6. narrative는 축마다 정확히 한 문단, 문단 시작에 【축이름】 을 붙인다. 문단 사이는 빈 줄 하나. 각 문단은 그 축의 카드만 인용한다(다른 축 카드 인용 금지). 축 내부는 시간 순서로 사건을 잇되, 각 문장은 '무엇이 왜/무엇에 이어 어떻게 되었다'가 드러나게 쓴다. 문단은 3~5문장.`,
      // 뼈대는 실제 축 이름으로 — 문단 수·이름·순서를 형식에 새겨 '첫 축만 쓰고 종료'를 막는다
      `7. 출력은 순수 JSON 하나만, narrative는 정확히 ${axes.length}개 문단(아래 뼈대의 ... 부분만 채운다): {"narrative":"${axisSkeleton(axes.map((ax) => ax.key))}","watch":["...","..."]}`,
    ].join("\n");
    const axisBlocks = axes.map((ax) => {
      const span = `${ax.cards[0].date} ~ ${ax.cards[ax.cards.length - 1].date}`;
      return `## 축: ${ax.key} (카드 [${ax.cards[0].n}]~[${ax.cards[ax.cards.length - 1].n}], ${span})\n${cardLines(ax.cards)}`;
    }).join("\n\n");
    user = `범위: ${scopeLabel} — 축 ${axes.length}개, 카드 ${n}장\n\n${axisBlocks}\n\n위 축들로 JSON 브리프를 작성하라.`;
    axisKeys = axes.map((ax) => ax.key);
    // 축 수에 연동 — 한국어는 대략 1자≈1토큰이고 축 하나가 문단(3~5문장, 400~600자)+watch를
    // 만든다. 고정 1600은 축 3개에서 이미 잘려 닫는 fence 없이 끝났다(실측: degraded 응답,
    // watch 0개). 축당 700 + 여유 800, 상한 3600.
    maxTokens = Math.min(3600, 800 + axes.length * 700);
  } else {
    // flat 모드(기존) — 좁은 범위(내워치·피드 필터 조합)
    const rawCards = Array.isArray(payload?.cards) ? payload.cards : [];
    const cards = rawCards.slice(0, MAX_CARDS).map((c, i) => leanCard(c, i + 1));
    if (cards.length < 2) return res.status(400).json({ ok: false, error: "need-at-least-2-cards" });
    const dates = cards.map((c) => c.date).filter(Boolean).sort();
    const span = dates.length ? `${dates[0]} ~ ${dates[dates.length - 1]}` : "";
    system = [
      "너는 배터리·ESS·EV 공급망 산업의 동향 브리프 작성자다.",
      "규칙:",
      COMMON_RULES,
      "6. narrative는 사건을 시간 흐름 순으로 엮은 4~6문장 한 문단. 나열이 아니라 인과·전개가 보이게 쓴다. 서사의 시점 표현은 아래 '실제 수록 기간'만 사용한다.",
      '7. 출력은 순수 JSON 하나만: {"narrative":"...","watch":["...","..."]}',
    ].join("\n");
    user = `범위: ${scopeLabel} (카드 ${cards.length}장, 실제 수록 기간 ${span})\n\n${cardLines(cards)}\n\n위 카드들로 JSON 브리프를 작성하라.`;
    maxTokens = 1100;
  }

  // ---- 생성 + 품질 가드(1회 재시도) ----
  let attempt = await generateOnce({ system, user, maxTokens });
  if (attempt.error) return res.status(502).json({ ok: false, error: attempt.error, provider: attempt.provider, status: attempt.status || null, detail: attempt.detail || null });
  let issues = qualityIssues(attempt.parsed, axisKeys);
  let retried = false;
  if (issues.length) {
    console.log(`[brief] quality issues ${JSON.stringify(issues)} — retrying once`);
    retried = true;
    // 재시도 지시도 뼈대로 — "축 N개를 모두 써라"는 서술만으로는 붕괴 재발을 못 막았다
    // (실측: 재시도본도 1문단). 채워야 할 출력 형식을 그대로 다시 보여준다.
    const axisNote = axisKeys ? ` narrative는 반드시 정확히 ${axisKeys.length}개 문단이어야 한다: "${axisSkeleton(axisKeys)}" — 이 뼈대의 ... 만 채워라. 문단 수가 ${axisKeys.length}개가 아니면 실패다.` : "";
    const strictUser = `${user}\n\n(직전 출력이 다음 규칙을 어겼다: ${issues.join(", ")}. 특히 경어체 금지·모든 문장 [n] 인용을 지켜 다시 작성하라.${axisNote})`;
    const second = await generateOnce({ system, user: strictUser, maxTokens });
    attempt = pickBetterAttempt(attempt, second, issues, axisKeys);
  }

  if (!attempt.parsed?.narrative) {
    // JSON 파싱 실패 시 원문 텍스트라도 반환 (클라이언트가 fallback 렌더)
    return res.status(200).json({ ok: true, narrative: clip(attempt.raw, 2000), watch: [], degraded: true, provider: attempt.provider });
  }

  // 축 모드의 문단 구분(\n\n)은 살려야 한다 — clip이 개행을 공백으로 뭉개므로 문단별 clip.
  // 모델이 문단을 홑 개행으로만 나눠도 【축】 앞에서 문단이 갈리게 정규화한다(pre-line 렌더 전제).
  const narrative = String(attempt.parsed.narrative)
    .replace(/\s*\n?\s*(?=【)/g, "\n\n").trim()
    .split(/\n{2,}/).map((p) => clip(p, 1200)).filter(Boolean).join("\n\n")
    .slice(0, 4800);
  return res.status(200).json({
    ok: true,
    narrative,
    watch: Array.isArray(attempt.parsed.watch) ? attempt.parsed.watch.slice(0, 4).map((w) => clip(w, 240)) : [],
    retried: retried || undefined,
    salvaged: attempt.parsed.salvaged || undefined, // 잘린 응답에서 구제한 경우 — 관측용
    provider: attempt.provider,
  });
}
