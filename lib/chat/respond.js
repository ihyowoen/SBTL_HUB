// ============================================================================
// Layer 5: respond — 최종 응답 조립 + suggestions + next_context
// ============================================================================
// Phase 2 신규. 기존 compose.js의 조립부 + suggestions.js 통합.
//
// 설계 원칙:
// - answer_type은 action을 반영 (D12 해결):
//   · rephrase → "rephrase"  (기존엔 general로 마스킹됨)
//   · analyze_card → "analyze_card"
//   · follow_up → "follow_up"
//   · new_query → topic (news/policy/faq_concept/comparison/general)
// - next_context 힌트 생성 (Phase 3에서 frontend가 last_turn/root_turn으로 저장):
//   · last_turn: { action, topic, answer_text, cards, scope }
//   · root_turn: new_query일 때 갱신, 그 외는 prior 유지
// - suggestions은 action+topic 기반 hint_action 포함 (U3 해결)
// ============================================================================

import { toCardView, toLinkView } from "./common.js";

// ─── Suggestions (hint 포함) ────────────────────────────────────────────

function suggestionsForAction(action, topic, scope = {}) {
  const regionLabel = scope?.region ? ({ US: "미국", KR: "한국", CN: "중국", EU: "유럽", JP: "일본" }[scope.region] || "") : "";

  if (action === "analyze_card") {
    return [
      { label: "이 카드 심층 분석해줘", hint_action: "analyze_card", hint_topic: "deep" },
      { label: "관련 카드 더 보여줘", hint_action: "follow_up" },
      { label: "한국어로 요약해줘", hint_action: "analyze_card", hint_topic: "summary" },
    ];
  }
  if (action === "rephrase") {
    return [
      { label: "더 짧게 정리해줘", hint_action: "rephrase" },
      { label: "예시로 설명해줘", hint_action: "rephrase" },
      { label: "관련 카드 더 보여줘", hint_action: "follow_up" },
    ];
  }
  if (action === "follow_up") {
    return [
      { label: "조금 더 쉽게 설명해줘", hint_action: "rephrase" },
      { label: "왜 중요한지 설명해줘", hint_action: "analyze_card" },
      { label: "다른 관점에서 정리해줘", hint_action: "rephrase" },
    ];
  }

  // new_query — topic 기반
  if (topic === "faq_concept") {
    return [
      { label: "조금 더 쉽게 설명해줘", hint_action: "rephrase" },
      { label: "관련 카드 더 보여줘", hint_action: "follow_up" },
      { label: "정책 일정만 따로 정리해줘", hint_action: "new_query", hint_topic: "policy" },
    ];
  }
  if (topic === "news") {
    const base = [
      { label: "요약해서 다시 정리", hint_action: "rephrase" },
      { label: "관련 카드 더 보여줘", hint_action: "follow_up" },
    ];
    if (!regionLabel || scope.region !== "US") base.push({ label: "미국 뉴스만", hint_action: "new_query", hint_topic: "news" });
    if (!regionLabel || scope.region !== "KR") base.push({ label: "한국 뉴스만", hint_action: "new_query", hint_topic: "news" });
    return base.slice(0, 3);
  }
  if (topic === "policy") {
    return [
      { label: "다가오는 일정만", hint_action: "follow_up", hint_topic: "policy" },
      { label: "관련 카드 더 보여줘", hint_action: "follow_up" },
      { label: "실무 영향만 요약", hint_action: "rephrase" },
    ];
  }
  if (topic === "comparison") {
    return [
      { label: "한 줄 결론만", hint_action: "rephrase" },
      { label: "관련 카드 더 보여줘", hint_action: "follow_up" },
      { label: "왜 중요한지 한 줄로", hint_action: "rephrase" },
    ];
  }
  // general
  return [
    { label: "조금 더 쉽게 설명해줘", hint_action: "rephrase" },
    { label: "관련 카드 더 보여줘", hint_action: "follow_up" },
    { label: "오늘 핵심 뉴스", hint_action: "new_query", hint_topic: "news" },
  ];
}

// ─── answer_type 결정 (D12 해결) ────────────────────────────────────────

function resolveAnswerType({ action, topic }) {
  if (action === "rephrase") return "rephrase";
  if (action === "analyze_card") return "analyze_card";
  if (action === "follow_up") return "follow_up";
  // new_query
  return topic || "general";
}

// ─── next_context 힌트 (Phase 3 frontend 활용) ──────────────────────────

function buildNextContext({ parsed, retrieval, cards, answer, priorContext }) {
  const { action, topic, scope, rawMessage } = parsed;

  const last_turn = {
    action,
    topic,
    answer_text: answer || "",
    cards: cards.map(toCardView),
    scope: {
      region: scope?.region || null,
      date: scope?.date || null,
      entity: scope?.entity || null,
    },
  };

  // root_turn: new_query일 때 갱신, 그 외는 prior 유지
  let root_turn;
  if (action === "new_query") {
    root_turn = { action, topic, user_message: rawMessage };
  } else {
    root_turn = priorContext?.root_turn || { action, topic, user_message: rawMessage };
  }

  return { last_turn, root_turn };
}

// ─── Main respond ──────────────────────────────────────────────────────

/**
 * @param {object} input
 * @param {object} input.parsed       parseRequest 결과
 * @param {object} input.resolved     resolveContext 결과
 * @param {object} input.retrieval    retrieve 결과
 * @param {object} input.synthesis    synthesize 결과 ({ answer, used_llm, meta })
 * @param {object} input.context      원본 ChatContext (root_turn 유지용)
 * @param {object} [input.debug]      추가 debug 정보 (diag, timings)
 * @returns {object} ChatResponse
 */
export function respond({ parsed, resolved, retrieval, synthesis, context = {}, debug = {} } = {}) {
  const { action, topic, scope } = parsed;
  const answer = synthesis?.answer || "";
  const cards = retrieval?.cards || [];

  const answer_type = resolveAnswerType({ action, topic });
  const next_context = buildNextContext({
    parsed,
    retrieval,
    cards,
    answer,
    priorContext: context,
  });

  const suggestions = suggestionsForAction(action, topic, scope);

  return {
    answer,
    answer_type,
    source_mode: "internal",
    confidence: synthesis?.used_llm ? 0.9 : (retrieval?.source === "faq" ? 0.92 : 0.7),
    cards: cards.map(toCardView),
    external_links: [],
    suggestions,
    next_context,
    debug: {
      confidence_bucket: synthesis?.used_llm ? "high" : (cards.length ? "medium" : "low"),
      action,
      topic,
      retrieve_source: retrieval?.source || "none",
      synthesize_meta: synthesis?.meta || null,
      parse_reasons: parsed?._reasons || [],
      resolve_reasons: resolved?._reasons || [],
      retrieve_reasons: retrieval?._reasons || [],
      news_meta: retrieval?.news_meta || null,
      ...debug,
    },
  };
}

/**
 * clarification 전용 응답 — resolveContext가 필수 context 부족으로 되묻기 필요할 때.
 */
export function respondClarification({ parsed, resolved, context = {}, debug = {} } = {}) {
  const { action, topic, scope } = parsed || {};
  const clarification = resolved?.clarification || "질문을 좀 더 구체적으로 해줄래?";

  return {
    answer: clarification,
    answer_type: "clarification",
    source_mode: "internal",
    confidence: 0,
    cards: [],
    external_links: [],
    suggestions: suggestionsForAction(action || "new_query", topic || "general", scope || {}),
    next_context: {
      last_turn: null,
      root_turn: context?.root_turn || null,
    },
    debug: {
      confidence_bucket: "clarification",
      action,
      topic,
      clarification_reason: resolved?._reasons?.join(",") || "missing_context",
      parse_reasons: parsed?._reasons || [],
      resolve_reasons: resolved?._reasons || [],
      ...debug,
    },
  };
}
