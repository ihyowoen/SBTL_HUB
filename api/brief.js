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

function parseJsonLoose(text) {
  if (!text) return null;
  let body = String(text).trim();
  const fence = body.match(/```(?:json)?\s*([\s\S]*?)```/);
  if (fence) body = fence[1].trim();
  const start = body.indexOf("{");
  const end = body.lastIndexOf("}");
  if (start >= 0 && end > start) body = body.slice(start, end + 1);
  try { return JSON.parse(body); } catch { return null; }
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
  if (!result?.text) return { error: result?.error || "llm-failed", provider: result?.provider || null };
  const parsed = parseJsonLoose(result.text);
  return { parsed, raw: result.text, provider: result.provider || null };
}

// 품질 검출 — 실패 사유 목록을 돌려준다 (비면 통과)
function qualityIssues(parsed) {
  if (!parsed?.narrative) return ["no-json"];
  const issues = [];
  const text = String(parsed.narrative);
  if (/(습니다|합니다|입니다|됩니다|어요|에요)[.\s]/.test(text)) issues.push("polite-tone");
  const sents = text.split(/(?<=[.!?])\s+/).map((s) => s.trim()).filter(Boolean);
  const noCite = sents.filter((s) => !/\[\d/.test(s)).length;
  if (sents.length > 0 && noCite / sents.length > 0.34) issues.push("uncited-sentences"); // 1/3 넘게 무인용이면 총평 나열로 후퇴한 것
  return issues;
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
      '7. 출력은 순수 JSON 하나만: {"narrative":"【축1】 ...\\n\\n【축2】 ...","watch":["...","..."]}',
    ].join("\n");
    const axisBlocks = axes.map((ax) => {
      const span = `${ax.cards[0].date} ~ ${ax.cards[ax.cards.length - 1].date}`;
      return `## 축: ${ax.key} (카드 [${ax.cards[0].n}]~[${ax.cards[ax.cards.length - 1].n}], ${span})\n${cardLines(ax.cards)}`;
    }).join("\n\n");
    user = `범위: ${scopeLabel} — 축 ${axes.length}개, 카드 ${n}장\n\n${axisBlocks}\n\n위 축들로 JSON 브리프를 작성하라.`;
    maxTokens = 1600; // 축 3~4개 × 문단 3~5문장 + watch — 900이면 잘린다
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
  if (attempt.error) return res.status(502).json({ ok: false, error: attempt.error, provider: attempt.provider });
  let issues = qualityIssues(attempt.parsed);
  let retried = false;
  if (issues.length) {
    console.log(`[brief] quality issues ${JSON.stringify(issues)} — retrying once`);
    retried = true;
    const strictUser = `${user}\n\n(직전 출력이 다음 규칙을 어겼다: ${issues.join(", ")}. 특히 경어체 금지·모든 문장 [n] 인용을 지켜 다시 작성하라.)`;
    const second = await generateOnce({ system, user: strictUser, maxTokens });
    if (!second.error && second.parsed && qualityIssues(second.parsed).length < issues.length) attempt = second;
    else if (!second.error && second.parsed && !attempt.parsed) attempt = second;
  }

  if (!attempt.parsed?.narrative) {
    // JSON 파싱 실패 시 원문 텍스트라도 반환 (클라이언트가 fallback 렌더)
    return res.status(200).json({ ok: true, narrative: clip(attempt.raw, 2000), watch: [], degraded: true, provider: attempt.provider });
  }

  // 축 모드의 문단 구분(\n\n)은 살려야 한다 — clip이 개행을 공백으로 뭉개므로 문단별 clip
  const narrative = String(attempt.parsed.narrative).split(/\n{2,}/).map((p) => clip(p, 1200)).filter(Boolean).join("\n\n").slice(0, 4800);
  return res.status(200).json({
    ok: true,
    narrative,
    watch: Array.isArray(attempt.parsed.watch) ? attempt.parsed.watch.slice(0, 4).map((w) => clip(w, 240)) : [],
    retried: retried || undefined,
    provider: attempt.provider,
  });
}
