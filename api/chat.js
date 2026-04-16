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
// - [카드상담] handoff → 단일 카드 LLM 상담 경로
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
import { synthesizeCardAnalysis, synthesizeCardConsult } from "../lib/chat/llm.js";

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

function parseCardConsultRequest(message) {
  const raw = String(message || "").trim();
  if (!raw.startsWith("[카드상담]")) return null;

  const lines = raw.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  const ask = lines.find((line) => !line.startsWith("[카드상담]") && !line.startsWith("카드 제목:") && !line.startsWith("카드 URL:")) || "이 카드 기준으로만 설명해줘.";
  const title = lines.find((line) => line.startsWith("카드 제목:"))?.replace(/^카드 제목:\s*/, "") || "";
  const url = lines.find((line) => line.startsWith("카드 URL:"))?.replace(/^카드 URL:\s*/, "") || "";

  return { ask, title, url };
}

function getCardPrimaryUrl(card) {
  if (!card || typeof card !== "object") return "";
  if (card.url) return String(card.url);
  if (Array.isArray(card.urls) && card.urls[0]) return String(card.urls[0]);
  return "";
}

function findCardForConsult(consult, cards = []) {
  const targetUrl = String(consult?.url || "").trim();
  const targetTitle = String(consult?.title || "").trim().toLowerCase();

  if (targetUrl) {
    const byUrl = cards.find((card) => getCardPrimaryUrl(card) === targetUrl);
    if (byUrl) return { card: byUrl, matchedBy: "url" };
  }

  if (targetTitle) {
    const byTitle = cards.find((card) => {
      const title = String(card?.T || card?.title || "").trim().toLowerCase();
      return title && title === targetTitle;
    });
    if (byTitle) return { card: byTitle, matchedBy: "title" };
  }

  return { card: null, matchedBy: null };
}

function buildUiCard(card) {
  return {
    title: card?.T || card?.title || "",
    subtitle: card?.sub || "",
    gist: card?.g || "",
    signal: card?.s || card?.signal || "i",
    date: card?.d || card?.date || "",
    region: card?.r || card?.region || "GL",
    source: card?.src || card?.source || "",
    url: getCardPrimaryUrl(card),
  };
}

function fallbackCardConsultAnswer(card) {
  const title = card?.T || card?.title || "이 카드";
  const fact = card?.sub || "카드에 적힌 사실 중심으로 보면 돼.";
  const gate = card?.g || "카드 기준으로는 추가 의미 해석은 제한적이야.";
  return `${title} 얘기야. ${fact} 왜 중요한지는 ${gate} 다음 체크포인트는 원문이랑 후속 공시나 기사 업데이트가 붙는지 보는 거야.`;
}

function buildCardConsultResponse({ card, answer, llmResult, consult, debugBase }) {
  const uiCard = buildUiCard(card);
  const answerText = answer || fallbackCardConsultAnswer(card);
  const scope = {
    region: uiCard.region || null,
    date: uiCard.date || null,
  };
  const nextTurn = {
    topic: "news",
    scope,
    answer_text: answerText,
    cards: [uiCard],
  };

  return {
    answer: answerText,
    answer_type: "news",
    source_mode: "internal",
    confidence: llmResult?.text ? 0.86 : 0.55,
    cards: [uiCard],
    external_links: [],
    suggestions: [
      { label: "이 카드 쉽게 다시 설명해줘", hint_action: "rephrase" },
      { label: "왜 중요한지 한 줄로", hint_action: "new_query" },
      { label: "관련 카드 더 보여줘", hint_action: "follow_up" },
    ],
    next_context: {
      last_turn: nextTurn,
      root_turn: nextTurn,
    },
    debug: {
      ...debugBase,
      card_consult: true,
      consult_lookup: {
        title: consult?.title || null,
        url: consult?.url || null,
      },
      llm: {
        used: !!llmResult?.text,
        error: llmResult?.error || null,
        latency_ms: llmResult?.latencyMs || 0,
      },
    },
  };
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

  // Groq 직접 호출 (llm.js의 synthesizeCardAnalysis 재사용) — /api/analysis HTTP 왕복 회피
  const result = await synthesizeCardAnalysis(card, mode);
  const answer = result?.text || null;

  const fakeSynthesis = {
    answer: answer || "분석을 생성하지 못했어. 다시 시도해줘.",
    used_llm: !!answer,
    meta: { llm: { used: !!answer, error: result?.error, latency_ms: result?.latencyMs, mode }, path: "analyze_card_groq" },
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

    const debugBase = { diag, pipeline_version: "phase2-5layer" };

    // ─── Dedicated card consult handoff ────────────────────────────────
    const consult = parseCardConsultRequest(message);
    if (consult) {
      const { card, matchedBy } = findCardForConsult(consult, data?.cards || []);
      if (!card) {
        return res.status(200).json({
          answer: "상담할 카드를 다시 찾지 못했어. 카드에서 다시 한번 눌러줘.",
          answer_type: "news",
          source_mode: "internal",
          confidence: 0.2,
          cards: [],
          external_links: [],
          suggestions: [
            { label: "오늘 핵심 카드", hint_action: "new_query", hint_topic: "news" },
            { label: "최근 시그널 TOP", hint_action: "new_query", hint_topic: "news" },
          ],
          next_context: { last_turn: null, root_turn: null },
          debug: {
            ...debugBase,
            card_consult: true,
            consult_lookup_failed: true,
            consult_lookup: consult,
          },
        });
      }

      const llmResult = await synthesizeCardConsult({ card, userAsk: consult.ask });
      return res.status(200).json(
        buildCardConsultResponse({
          card,
          answer: llmResult?.text,
          llmResult,
          consult: { ...consult, matchedBy },
          debugBase,
        })
      );
    }

    // ─── Layer 1: parseRequest ──────────────────────────────────────────
    const parsed = parseRequest({ message, context, hint, data });
    console.log(`[chat-parse] action=${parsed.action} topic=${parsed.topic} region=${parsed.scope?.region || "-"} date=${parsed.scope?.date || "-"}`);

    // ─── Layer 2: resolveContext ────────────────────────────────────────
    const resolvedCtx = resolveContext({ parsed, context });

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
