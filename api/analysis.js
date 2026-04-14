import { synthesizeCardAnalysis } from "../lib/chat/llm.js";

export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  // 같은 카드+모드 조합은 5분 캐시
  res.setHeader("Cache-Control", "s-maxage=300, stale-while-revalidate=60");

  if (req.method === "OPTIONS") return res.status(200).end();
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  try {
    const { card, mode } = req.body || {};
    if (!card || !mode) return res.status(400).json({ error: "Card and mode required" });
    if (!["why", "summary", "analysis"].includes(mode)) {
      return res.status(400).json({ error: "Invalid mode. Use: why, summary, or analysis" });
    }

    // 1차 시도: Groq LLM
    const llmRes = await synthesizeCardAnalysis(card, mode);
    if (llmRes.text) {
      console.log(`[analysis] mode=${mode} source=ai latency=${llmRes.latencyMs}ms`);
      return res.status(200).json({ result: llmRes.text, mode, source: "ai", latency_ms: llmRes.latencyMs });
    }

    // 2차 fallback: 결정론적 템플릿 (키 없음/타임아웃/레이트리밋 등)
    console.warn(`[analysis] mode=${mode} source=fallback reason=${llmRes.error || "unknown"}`);
    const result = mode === "why" ? generateWhyImportant(card)
      : mode === "summary" ? generateKoreanSummary(card)
      : generateDeepAnalysis(card);
    return res.status(200).json({ result, mode, source: "fallback", fallback_reason: llmRes.error || "unknown" });
  } catch (error) {
    return res.status(500).json({ error: "ANALYSIS_ERROR", message: error.message });
  }
}

// ─── Deterministic fallback generators (LLM 미가용 시) ───

function generateWhyImportant(card) {
  const { T, sub, g, r, s } = card;
  const regionContext = {
    US: "FEOC·IRA 크레딧 구조와 공급망 전략에",
    EU: "EU Battery Regulation·CBAM 규제 대응에",
    CN: "중국발 가격 경쟁과 공급망 통제력 변화에",
    KR: "국내 ESS 시장 성장과 정책 대응에",
    JP: "일본 GX 정책과 에너지 안보 전략에",
  };
  const context = regionContext[r] || "배터리·ESS·EV 밸류체인에";
  const signalNote = {
    t: "구조적 전환을 촉발할 수 있는 TOP 시그널이야.",
    h: "단기 대응이 필요한 HIGH 임팩트 신호야.",
    m: "중기 관점에서 추적이 필요한 변수야.",
    i: "맥락 파악에 유용한 참고 정보야.",
  };
  let implPart = "";
  if (g) {
    const sentences = g.split(/(?<=[.。])\s+/);
    const implSentences = sentences.filter((s) =>
      /(영향|의미|중요|전략|리스크|기회|경쟁|변화|핵심|주목)/i.test(s)
    );
    implPart = implSentences.length ? implSentences.join(" ") : sentences[sentences.length - 1] || "";
  }
  return [
    `⚡ 왜 중요한가`,
    `이 뉴스는 ${context} ${signalNote[s] || "중요한 변화를 나타내."}`,
    implPart || sub || "",
  ].filter(Boolean).join("\n");
}

function generateKoreanSummary(card) {
  const { T, sub, g, src, d } = card;
  let factual = g || "";
  if (factual.includes("—")) factual = factual.split("—")[0].trim();
  return [
    `📰 요약`,
    T || "",
    sub || "",
    factual || "",
    src ? `출처: ${src}${d ? " · " + d : ""}` : "",
  ].filter(Boolean).join("\n");
}

function generateDeepAnalysis(card) {
  const { T, sub, g, r, s, src } = card;
  const regionPerspective = {
    US: "FEOC 준수 여부와 45X 크레딧 확보가 시장 접근을 좌우해. Section 301 관세와 맞물려 비중국 공급망 재편을 가속화하고 있어.",
    EU: "Battery Regulation 여권 의무화(2027)와 CBAM 본격 시행을 앞두고 규제 준수 비용이 진입 장벽으로 작용해.",
    CN: "과잉설비 기반 저가 공세와 흑연·리튬 수출 통제가 맞물려 글로벌 공급망 재편의 핵심 변수야.",
    KR: "ESS 안전기준 강화와 용량시장 입찰 확대가 국내 시장 구조를 바꾸고 있어. 수출 규제 대응과 내수 성장을 동시에 고려해야 해.",
    JP: "GX 20조엔 투자와 METI 보조금이 ESS 시장을 본격 열고 있어. 계통유연성 조정력 수요가 구체화되고 있어.",
  };
  const signalDepth = {
    t: "구조적 전환 신호 — 업계 전반의 방향을 바꿀 수 있는 변화야. 즉각적인 전략 검토가 필요해.",
    h: "고임팩트 신호 — 단기(3~6개월) 내 대응 조치가 필요해.",
    m: "중기 관찰 대상 — 12개월 이상의 추세 변화로 연결될 수 있어.",
    i: "배경 정보 — 맥락 이해와 중장기 추적에 활용해.",
  };
  const watchpointByRegion = {
    US: ["MACR 기준 변화", "Section 301 관세 갱신 여부", "Treasury FEOC 가이드라인"],
    EU: ["Battery Passport 파일럿 일정", "CBAM 전환기 종료 후 실제 부과", "CRM Act 광물 목록 업데이트"],
    CN: ["흑연 수출허가 실제 운용", "LFP 설비 과잉 조정 신호", "제3국 우회 수출 규모"],
    KR: ["ESS 안전기준 개정 시행일", "용량시장 입찰 결과", "배터리 여권 국내 적용 로드맵"],
    JP: ["METI 보조금 2차 공모 시기", "GX 채권 집행 진도", "계통용 ESS 접속 규칙 개정"],
  };
  const wp = watchpointByRegion[r] || ["공급망 변화", "규제 동향", "시장 가격 추이"];
  return [
    `🔍 분석`,
    g || sub || T,
    regionPerspective[r] ? `\n[지역 맥락] ${regionPerspective[r]}` : "",
    `\n[시그널 강도] ${signalDepth[s] || "추가 관찰이 필요해."}`,
    `\n[관전 포인트]\n• ${wp.join("\n• ")}`,
    src ? `\n출처: ${src}` : "",
  ].filter(Boolean).join("\n");
}
