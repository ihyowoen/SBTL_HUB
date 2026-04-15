import { synthesizeCardAnalysis } from "../lib/chat/llm.js";
import { generateWhyImportant, generateKoreanSummary, generateDeepAnalysis } from "../lib/chat/curated.js";

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

    // ─── Curated modes: why / analysis ────────────────────────────────────
    // card.g 필드에 사용자가 작성한 '왜 중요한지' 분석이 담겨있다. LLM이 이를
    // 재해석하면 voice·정확도 모두 희석되므로 curated 원본을 그대로 내보낸다.
    if (mode === "why") {
      const result = generateWhyImportant(card);
      console.log(`[analysis] mode=why source=curated`);
      return res.status(200).json({ result, mode, source: "curated" });
    }
    if (mode === "analysis") {
      const result = generateDeepAnalysis(card);
      console.log(`[analysis] mode=analysis source=curated`);
      return res.status(200).json({ result, mode, source: "curated" });
    }

    // ─── LLM mode: summary (해외 원문 한국어 요약·번역) ──────────────────
    const llmRes = await synthesizeCardAnalysis(card, mode);
    if (llmRes.text) {
      console.log(`[analysis] mode=${mode} source=ai latency=${llmRes.latencyMs}ms`);
      return res.status(200).json({ result: llmRes.text, mode, source: "ai", latency_ms: llmRes.latencyMs });
    }

    // summary LLM 실패 시 deterministic fallback
    console.warn(`[analysis] mode=${mode} source=fallback reason=${llmRes.error || "unknown"}`);
    const result = generateKoreanSummary(card);
    return res.status(200).json({ result, mode, source: "fallback", fallback_reason: llmRes.error || "unknown" });
  } catch (error) {
    return res.status(500).json({ error: "ANALYSIS_ERROR", message: error.message });
  }
}

// curated generators는 lib/chat/curated.js로 이동 (api/chat.js의 analyze_card 경로와 공유).
