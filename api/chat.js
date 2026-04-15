// ============================================================================
// POST /api/chat — Phase 2 5-layer orchestrator
// ============================================================================
// 재작성: 2026-04-15
//
// Pipeline:
//   Layer 1: parseRequest    → { action, topic, scope, rawMessage }
//   Layer 2: resolveContext  → { ok, clarification?, resolved }
//   Layer 3: retrieve        → { source, cards, faq?, policy?, news_meta? }
//   Layer 4: synthesize      → { answer, used_llm, meta, delegate? }
//   Layer 5: respond         → ChatResponse
//
// 특수 경로:
// - action=analyze_card → Layer 4에서 delegate marker → /api/analysis 위임
// - Layer 2 clarification → Layer 3/4 skip, respondClarification
//
// 해결 결함:
// - D11 (follow_up 오남용) · D12 (answer_type 마스킹) · D13 (중복 rewrite) · S1 (VITE_BRAVE_KEY fallback)
// ============================================================================

import { loadKnowledge } from "../lib/chat/common.js";
import { parseRequest } from "../lib/chat/parseRequest.js";
import { resolveContext } from "../lib/chat/resolveContext.js";
import { retrieve } from "../lib/chat/retrieve/index.js";
import { synthesize } from "../lib/chat/synthesize.js";
import { respond, respondClarification } from "../lib/chat/respond.js";
import { synthesizeCardAnalysis } from "../lib/chat/llm.js";
import { generateWhyImportant, generateDeepAnalysis, generateKoreanSummary } from "../lib/chat/curated.js";

function setCors(res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
}

function stableError(res, status, message, debug = {}) {
  return res.status(status).json({
    answer: message,
    answer_type: "error",
    source_mode: "internal",
    confidence: 0,
    cards: [],
    external_links: [],
    suggestions: [
      { label: "오늘 핵심 카드", hint_action: "new_query", hint_topic: "news" },
      { label: "최근 시그널 TOP", hint_action: "new_query", hint_topic: "news" },
    ],
    next_context: { last_turn: null, root_turn: null },
    debug: { confidence_bucket: "error", ...debug },
  });
}

// analyze_card 전용 처리 — /api/analysis에 위임
async function handleAnalyzeCard({ parsed, resolved, synthesis, context, debugBase }) {
  const card = synthesis?.delegate?.card || resolved?.target_card;
  const mode = synthesis?.delegate?.mode || "why";

  if (!card) {
    return respondClarification({
      parsed,
      resolved: { ...resolved, clarification: "분석할 카드를 찾지 못했어. 먼저 뉴스를 검색해줘." },
      context,
      debug: debugBase,
    });
  }

  // why / analysis 모드는 큐레이터가 작성한 card.g를 그대로 사용 (LLM 재해석 금지).
  // summary 모드만 해외 원문 번역이 필요해 Groq을 통과시킨다.
  let answer = null;
  let synthMeta = { path: "analyze_card_curated", mode, source: "curated" };
  let usedLlm = false;

  if (mode === "summary") {
    const result = await synthesizeCardAnalysis(card, mode);
    if (result?.text) {
      answer = result.text;
      usedLlm = true;
      synthMeta = {
        path: "analyze_card_groq_summary",
        mode,
        source: "ai",
        llm: { used: true, latency_ms: result.latencyMs },
      };
    } else {
      // LLM 실패 시 curated summary로 fallback
      answer = generateKoreanSummary(card);
      synthMeta = {
        path: "analyze_card_summary_fallback",
        mode,
        source: "fallback",
        llm: { used: false, error: result?.error || "unknown" },
      };
    }
  } else if (mode === "analysis") {
    answer = generateDeepAnalysis(card);
  } else {
    // default: why
    answer = generateWhyImportant(card);
  }

  const fakeSynthesis = {
    answer: answer || "분석을 생성하지 못했어. 다시 시도해줘.",
    used_llm: usedLlm,
    meta: synthMeta,
  };

  // retrieval 모양 맞추기 — target card 1장
  const fakeRetrieval = {
    source: "analyze_card",
    cards: [card],
    _reasons: ["analyze_card_single"],
  };

  return respond({
    parsed,
    resolved,
    retrieval: fakeRetrieval,
    synthesis: fakeSynthesis,
    context,
    debug: debugBase,
  });
}

export default async function handler(req, res) {
  setCors(res);

  if (req.method === "OPTIONS") return res.status(200).end();
  if (req.method !== "POST") {
    return stableError(res, 405, "Method not allowed", { error_code: "METHOD_NOT_ALLOWED" });
  }

  try {
    const message = String(req.body?.message || "").trim();
    const context = req.body?.context || {};
    const hint = req.body?.hint || {};

    if (!message) {
      return stableError(res, 400, "질문을 먼저 입력해줘.", { error_code: "MESSAGE_REQUIRED" });
    }

    // ─── Load knowledge ─────────────────────────────────────────────────
    const _t0 = Date.now();
    const data = await loadKnowledge();
    const _t1 = Date.now();
    const diag = {
      cwd: process.cwd(),
      cards_len: Array.isArray(data?.cards) ? data.cards.length : -1,
      faq_len: Array.isArray(data?.faq) ? data.faq.length : -1,
      tracker_len: Array.isArray(data?.tracker?.items) ? data.tracker.items.length : -1,
      load_ms: _t1 - _t0,
      vercel_url: process.env.VERCEL_URL || null,
      sources: data?._sources || null,
    };
    console.log(`[chat-diag-D1] ${JSON.stringify(diag)}`);

    // ─── Layer 1: parseRequest ──────────────────────────────────────────
    const parsed = parseRequest({ message, context, hint, data });
    console.log(`[chat-parse] action=${parsed.action} topic=${parsed.topic} region=${parsed.scope?.region || "-"} date=${parsed.scope?.date || "-"}`);

    // ─── Layer 2: resolveContext ────────────────────────────────────────
    const resolvedCtx = resolveContext({ parsed, context });
    const debugBase = { diag, pipeline_version: "phase2-5layer" };

    if (!resolvedCtx.ok) {
      console.log(`[chat-clarify] ${resolvedCtx._reasons?.join(",")}`);
      return res.status(200).json(
        respondClarification({ parsed, resolved: resolvedCtx, context, debug: debugBase })
      );
    }

    // ─── Layer 3: retrieve ──────────────────────────────────────────────
    const retrieval = retrieve({ parsed, resolved: resolvedCtx.resolved, data });
    console.log(`[chat-retrieve] source=${retrieval.source} cards=${(retrieval.cards || []).length}`);

    // ─── Layer 4: synthesize ────────────────────────────────────────────
    const synthesis = await synthesize({
      parsed,
      resolved: resolvedCtx.resolved,
      retrieval,
    });
    console.log(`[chat-synth] path=${synthesis?.meta?.path} used_llm=${synthesis?.used_llm} delegate=${synthesis?.delegate?.to || "-"}`);

    // ─── Layer 5: respond ───────────────────────────────────────────────
    // analyze_card 위임 경로
    if (synthesis?.delegate?.to === "analysis_api" || parsed.action === "analyze_card") {
      const resp = await handleAnalyzeCard({
        parsed,
        resolved: resolvedCtx.resolved,
        synthesis,
        context,
        debugBase,
      });
      return res.status(200).json(resp);
    }

    const response = respond({
      parsed,
      resolved: resolvedCtx.resolved,
      retrieval,
      synthesis,
      context,
      debug: debugBase,
    });

    return res.status(200).json(response);
  } catch (error) {
    console.error("[chat-orchestration-error]", error?.message, error?.stack);
    return stableError(res, 500, "채팅 응답 생성 중 오류가 났어.", {
      error_code: "CHAT_ORCHESTRATION_ERROR",
      detail: error?.message || "unknown",
    });
  }
}
