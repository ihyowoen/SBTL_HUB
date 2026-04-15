// ============================================================================
// retrieve/general.js — 잡의도 (topic=general)
// ============================================================================
// lexical 검색 4장, 없으면 최신 4장.
// ============================================================================

import { lexicalSearchCards, cardsOnLatestAvailableDate } from "./shared.js";

export function retrieveGeneral({ rawMessage, scope, data }) {
  const scored = lexicalSearchCards(data?.cards || [], rawMessage, 4, scope || {});
  if (scored.length) {
    return {
      source: "general",
      cards: scored,
      _reasons: [`general_lexical:${scored.length}`],
    };
  }
  const latest = cardsOnLatestAvailableDate(data?.cards || [], scope?.region || null, 4);
  return {
    source: "general",
    cards: latest.cards,
    news_meta: { date_mode: "fallback_latest", requested_date: null, actual_date: latest.actual_date },
    _reasons: [`general_latest_fallback:${latest.cards.length}`],
  };
}
