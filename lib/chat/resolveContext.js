// ============================================================================
// Layer 2: resolveContext — action별 필수 context hydrate/validate
// ============================================================================
// Phase 2 신규.
//
// 역할:
// - parseRequest 결과를 받아 action이 요구하는 context 필드를 검증
// - 부족하면 clarification(사용자에게 되묻기) 반환 — 이 경우 retrieve/synthesize skip
// - 통과하면 정제된 resolved context 반환 (selected card 해석 등)
//
// 설계 원칙:
// - rephrase: last_turn.answer_text 필수
// - analyze_card: selected_item_id 우선, 없으면 last_turn.cards[0]
// - follow_up: root_turn 또는 last_turn 존재 필수
// - new_query: 항상 통과
// ============================================================================

function findCardById(cards = [], id) {
  if (!id) return null;
  for (const c of cards) {
    if (c?.url === id || c?.id === id || c?.T === id) return c;
  }
  return null;
}

/**
 * @param {object} input
 * @param {object} input.parsed   parseRequest 결과
 * @param {object} input.context  원본 ChatContext
 * @returns {{ ok: boolean, clarification?: string, resolved?: object, _reasons: string[] }}
 */
export function resolveContext({ parsed, context = {} } = {}) {
  const reasons = [];
  const { action } = parsed;
  const lastTurn = context?.last_turn || null;
  const rootTurn = context?.root_turn || null;

  // ─── rephrase ───────────────────────────────────────────────────────────
  if (action === "rephrase") {
    const answerText = lastTurn?.answer_text || "";
    if (!answerText) {
      reasons.push("rephrase_missing_last_answer_text");
      return {
        ok: false,
        clarification:
          "어떤 답변을 다시 설명할까? 먼저 뉴스나 개념을 검색하고 난 뒤에 '더 쉽게'를 요청해줘.",
        _reasons: reasons,
      };
    }
    reasons.push("rephrase_context_ok");
    return {
      ok: true,
      resolved: {
        prior_answer_text: answerText,
        prior_cards: lastTurn?.cards || [],
        prior_topic: lastTurn?.topic || parsed.topic,
        prior_action: lastTurn?.action || null,
      },
      _reasons: reasons,
    };
  }

  // ─── analyze_card ───────────────────────────────────────────────────────
  if (action === "analyze_card") {
    // 우선순위: selected_item_id > last_turn.cards[0]
    let targetCard = null;
    const lastCards = lastTurn?.cards || [];

    if (context?.selected_item_id) {
      targetCard = findCardById(lastCards, context.selected_item_id);
      if (targetCard) reasons.push("analyze_card_from_selected_id");
    }
    if (!targetCard && lastCards.length) {
      targetCard = lastCards[0];
      reasons.push("analyze_card_from_last_cards_0");
    }

    if (!targetCard) {
      reasons.push("analyze_card_missing_target");
      return {
        ok: false,
        clarification:
          "어떤 카드를 분석할까? 먼저 뉴스를 검색한 다음 카드를 고르고 '왜 중요한지'를 물어줘.",
        _reasons: reasons,
      };
    }

    return {
      ok: true,
      resolved: { target_card: targetCard },
      _reasons: reasons,
    };
  }

  // ─── follow_up ──────────────────────────────────────────────────────────
  if (action === "follow_up") {
    if (!rootTurn && !lastTurn) {
      reasons.push("follow_up_missing_any_turn");
      return {
        ok: false,
        clarification:
          "이어서 찾을 맥락이 아직 없어. 먼저 궁금한 주제를 구체적으로 물어봐줘.",
        _reasons: reasons,
      };
    }
    reasons.push("follow_up_context_ok");
    return {
      ok: true,
      resolved: {
        root_topic: rootTurn?.topic || lastTurn?.topic || parsed.topic,
        root_user_message: rootTurn?.user_message || "",
        prior_cards: lastTurn?.cards || [],
      },
      _reasons: reasons,
    };
  }

  // ─── new_query ──────────────────────────────────────────────────────────
  reasons.push("new_query_pass_through");
  return {
    ok: true,
    resolved: {},
    _reasons: reasons,
  };
}
