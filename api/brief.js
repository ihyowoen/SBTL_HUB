// ============================================================================
// POST /api/brief — 필터된 카드 범위를 "흐름 브리프"로 합성
// 출력은 보고서 붙여넣기용 문어체 + 문장별 [n] 카드 인용 (챗봇 반말 톤 미적용)
// ============================================================================

import { callLLM } from "../lib/chat/llm.js";

const MAX_CARDS = 40;

function setCors(res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
}

function clip(v, n) {
  return String(v || "").replace(/\s+/g, " ").trim().slice(0, n);
}

function leanCards(raw) {
  if (!Array.isArray(raw)) return [];
  return raw.slice(0, MAX_CARDS).map((c, i) => ({
    n: i + 1,
    date: clip(c.date, 10),
    region: clip(c.region, 6),
    title: clip(c.title, 120),
    fact: clip(c.fact, 420),
    implication: clip(c.implication, 260),
    quote: clip(c.quote, 220),
    quoteSource: clip(c.quoteSource, 60),
  }));
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

export default async function handler(req, res) {
  setCors(res);
  if (req.method === "OPTIONS") return res.status(200).end();
  if (req.method !== "POST") return res.status(405).json({ ok: false, error: "method-not-allowed" });

  let payload = req.body;
  if (typeof payload === "string") {
    try { payload = JSON.parse(payload); } catch { payload = null; }
  }
  const scopeLabel = clip(payload?.scopeLabel, 120) || "선택 범위";
  const cards = leanCards(payload?.cards);
  if (cards.length < 2) {
    return res.status(400).json({ ok: false, error: "need-at-least-2-cards" });
  }

  const cardLines = cards.map((c) => {
    const bits = [`[${c.n}] ${c.date} ${c.region} — ${c.title}`];
    if (c.fact) bits.push(`  사실: ${c.fact}`);
    if (c.implication) bits.push(`  함의: ${c.implication}`);
    if (c.quote) bits.push(`  원문인용(${c.quoteSource || "출처"}): "${c.quote}"`);
    return bits.join("\n");
  }).join("\n");

  const system = [
    "너는 배터리·ESS·EV 공급망 산업의 주간동향 브리프 작성자다.",
    "규칙:",
    "1. 반드시 아래 제공된 카드의 사실만 사용한다. 새로운 사실·수치·해석을 만들어내지 않는다.",
    "2. 모든 문장의 끝에 근거 카드 번호를 [n] 또는 [n,m] 형식으로 붙인다. 인용 없는 문장 금지.",
    "3. 문체: 보고서용 문어체(~했다, ~이다). 반말·이모지·마크다운 금지.",
    "4. narrative는 사건을 시간 흐름 순으로 엮은 4~6문장 한 문단. 나열이 아니라 인과·전개가 보이게 쓴다.",
    "5. watch는 카드의 함의에서 뽑은 '지켜볼 것' 2~4개. 각 항목도 [n] 인용.",
    '6. 출력은 순수 JSON 하나만: {"narrative":"...","watch":["...","..."]}',
  ].join("\n");

  const user = `범위: ${scopeLabel} (카드 ${cards.length}장)\n\n${cardLines}\n\n위 카드들로 JSON 브리프를 작성하라.`;

  const result = await callLLM({ system, user, maxTokens: 900, temperature: 0.3, timeoutMs: 20000 });
  if (!result?.text) {
    return res.status(502).json({ ok: false, error: result?.error || "llm-failed", provider: result?.provider || null });
  }

  const parsed = parseJsonLoose(result.text);
  if (!parsed?.narrative) {
    // JSON 파싱 실패 시 원문 텍스트라도 반환 (클라이언트가 fallback 렌더)
    return res.status(200).json({ ok: true, narrative: clip(result.text, 2000), watch: [], degraded: true, provider: result.provider || null });
  }

  return res.status(200).json({
    ok: true,
    narrative: clip(parsed.narrative, 2400),
    watch: Array.isArray(parsed.watch) ? parsed.watch.slice(0, 4).map((w) => clip(w, 240)) : [],
    provider: result.provider || null,
  });
}
