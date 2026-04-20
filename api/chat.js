// ============================================================================
// POST /api/chat — Phase 2 5-layer orchestrator
// ============================================================================
// 업데이트: 2026-04-19 — 배터리 상담소 재설계 Phase 1.
//
// Pipeline:
//   Layer 1: parseRequest    → { action, topic, scope, rawMessage }
//   Layer 2: resolveContext  → { ok, clarification?, resolved }
//   Layer 3: retrieve        → { source, cards, faq?, policy?, news_meta? }
//   Layer 4: synthesize      → { answer, used_llm, meta, delegate? }
//   Layer 5: respond         → ChatResponse
//
// 특수 경로:
// - body.consultation 있으면  → 배터리 상담소 경로 (NEW, 2026-04-19)
// - action=analyze_card      → Layer 4에서 delegate marker → /api/analysis 위임
// - Layer 2 clarification    → Layer 3/4 skip, respondClarification
// - [카드상담] prefix (legacy) → consultation 경로로 흡수 (backward-compat 유지)
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

// ============================================================================
// 배터리 상담소 경로 (2026-04-19 신설)
// ============================================================================
//
// 입력: req.body.consultation = buildCardConsultContext output
//       {
//         card: leanCard,
//         related_cards: [leanRelated],
//         opener_category: "kbattery",
//         few_shot_examples: [{id, text}],
//         data_fence: {enabled: true},
//         schema_version: 1
//       }
// + req.body.is_opener      (bool)
// + req.body.message        (후속 답변 시 유저 질문, opener는 빈 문자열 허용)
// + req.body.ticket_id      (client가 관리, debug에만 echo)
//
// 출력: 기존 ChatResponse 모양 유지 (answer, cards, suggestions, next_context, ...)
//       단, cards는 받은 카드 하나로 구성된 UI card (뉴스 탭에서 넘어온 것이라 중복 노출 주의 —
//       client는 msgs에 렌더 시 중복 방지 가능; 여기선 안전하게 return)

function leanCardToUiCard(leanCard) {
  if (!leanCard) return null;
  return {
    title: leanCard.title || "",
    subtitle: leanCard.sub || "",
    gist: leanCard.gate || "",
    // SIG_L에서 인식 가능한 signal short-code 유지
    signal: (leanCard.signal || "i").toString().slice(0, 1).toLowerCase(),
    date: leanCard.date || "",
    region: leanCard.region || "GL",
    source: leanCard.source || "",
    url: leanCard.primary_url || "",
  };
}

// In-character error fallback — LLM 완전 실패 시 강차장 voice로 전달.
// 유저 경험에서 "Error 500" 덤프 되지 않도록.
const IN_CHARACTER_ERRORS = [
  "강차장 잠시 자리 비웠어. 잠깐 뒤에 다시 제출해줘.",
  "접수 꼬였네. 새로고침하고 한 번만 다시 보내줘.",
  "지금 다른 상담 중이야. 1분만.",
];

function pickInCharacterError() {
  return IN_CHARACTER_ERRORS[Math.floor(Math.random() * IN_CHARACTER_ERRORS.length)];
}

async function handleConsultation({ consultation, isOpener, userMessage, ticketId, debugBase }) {
  const uiCard = leanCardToUiCard(consultation?.card);

  // cardContext validation
  if (!consultation || !consultation.card || !consultation.card.title) {
    return {
      answer: "상담 카드 정보가 깨져 있어. 카드에서 다시 한번 눌러줘.",
      answer_type: "news",
      source_mode: "internal",
      confidence: 0.1,
      cards: [],
      external_links: [],
      suggestions: [
        { label: "오늘 핵심 카드", hint_action: "new_query", hint_topic: "news" },
      ],
      next_context: { last_turn: null, root_turn: null },
      debug: { ...debugBase, consultation: true, consult_error: "invalid-context", ticket_id: ticketId || null },
    };
  }

  // LLM 호출
  const llmResult = await synthesizeCardConsult({
    cardContext: consultation,
    isOpener: !!isOpener,
    userMessage: userMessage || "",
  });

  const answerText = llmResult?.text || pickInCharacterError();

  const scope = {
    region: uiCard?.region || null,
    date: uiCard?.date || null,
  };

  const nextTurn = {
    topic: "news",
    scope,
    answer_text: answerText,
    cards: uiCard ? [uiCard] : [],
    // 상담 맥락 추적 — 후속 턴에서 ChatContext 흐름에 활용
    consultation_ticket_id: ticketId || null,
    consultation_card_id: consultation.card.id || null,
  };

  // Suggestions — Phase 1은 hardcoded (Phase 2에서 related 카드 연동)
  const suggestions = isOpener
    ? [
        { label: "조금 더 쉽게 설명해줘", hint_action: "rephrase" },
        { label: "왜 중요한지 한 줄로", hint_action: "new_query" },
        { label: "관련 카드 더 보여줘", hint_action: "follow_up" },
      ]
    : [
        { label: "조금 더 쉽게 설명해줘", hint_action: "rephrase" },
        { label: "관련 카드 더 보여줘", hint_action: "follow_up" },
      ];

  return {
    answer: answerText,
    answer_type: "news",
    source_mode: "internal",
    confidence: llmResult?.text ? 0.86 : 0.35,
    // UI cards는 client가 이미 접수증에서 카드 메타 보여주므로 중복 주지 않음.
    // 단 후속 턴에서 다른 관련 카드 인용이 필요해지면 Phase 2에서 확장.
    cards: [],
    external_links: [],
    suggestions,
    next_context: {
      last_turn: nextTurn,
      root_turn: nextTurn,
    },
    debug: {
      ...debugBase,
      consultation: true,
      ticket_id: ticketId || null,
      card_id: consultation.card.id || null,
      is_opener: !!isOpener,
      opener_category: consultation.opener_category || null,
      related_cards_count: Array.isArray(consultation.related_cards) ? consultation.related_cards.length : 0,
      llm: {
        used: !!llmResult?.text,
        error: llmResult?.error || null,
        latency_ms: llmResult?.latencyMs || 0,
      },
    },
  };
}

// ============================================================================
// Legacy "[카드상담]" prefix handoff (backward-compat, deprecated)
// ============================================================================
// 이전 flow는 StoryNewsItem이 prompt string을 user message로 post 했었음.
// 새 flow는 body.consultation object로 옴. 옛 path는 에러 대신 guidance 반환.

function parseCardConsultRequest(message) {
  const raw = String(message || "").trim();
  if (!raw.startsWith("[카드상담]")) return null;
  return { legacy: true };
}

// ============================================================================
// analyze_card 전용 처리 — /api/analysis에 위임 (기존 유지, dead code이나 경로는 보존)
// ============================================================================
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

  const result = await synthesizeCardAnalysis(card, mode);
  const answer = result?.text || null;

  const fakeSynthesis = {
    answer: answer || "분석을 생성하지 못했어. 다시 시도해줘.",
    used_llm: !!answer,
    meta: { llm: { used: !!answer, error: result?.error, latency_ms: result?.latencyMs, mode }, path: "analyze_card_groq" },
  };

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

// ============================================================================
// Main handler
// ============================================================================
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
    const consultation = req.body?.consultation || null;
    const isOpener = !!req.body?.is_opener;
    const ticketId = req.body?.ticket_id || null;

    // message OR consultation 필수 (opener는 message 빈 문자열 허용)
    if (!message && !consultation) {
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

    // ─── NEW: 배터리 상담소 경로 ────────────────────────────────────────
    if (consultation) {
      console.log(`[chat-consultation] ticket=${ticketId} is_opener=${isOpener} card_id=${consultation?.card?.id} cat=${consultation?.opener_category}`);
      const resp = await handleConsultation({
        consultation,
        isOpener,
        userMessage: message,
        ticketId,
        debugBase,
      });
      return res.status(200).json(resp);
    }

    // ─── Legacy "[카드상담]" prefix — 상담소 경로로 유도 ────────────────
    const legacy = parseCardConsultRequest(message);
    if (legacy) {
      return res.status(200).json({
        answer: "상담소 경로가 갱신됐어. 뉴스 카드에서 '상담카드 제출' 버튼으로 다시 보내줘.",
        answer_type: "news",
        source_mode: "internal",
        confidence: 0.3,
        cards: [],
        external_links: [],
        suggestions: [
          { label: "오늘 핵심 카드", hint_action: "new_query", hint_topic: "news" },
        ],
        next_context: { last_turn: null, root_turn: null },
        debug: { ...debugBase, legacy_card_consult: true },
      });
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
