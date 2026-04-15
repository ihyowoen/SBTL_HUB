// ============================================================================
// retrieve/news.js — news intent retrieval
// ============================================================================
// 기존 retrieval.js::selectNewsCards 로직 유지. date 스코프 엄격, 없으면
// latest available로 graceful fallback. news_meta로 date_mode/actual_date 전달.
// ============================================================================

import { kstToday } from "../common.js";
import {
  lexicalSearchCards,
  cardsOnExactDate,
  cardsOnLatestAvailableDate,
} from "./shared.js";

function selectNewsCards(cards, query, scope = {}, limit = 4) {
  const today = kstToday();
  const requestedDate = scope?.date || null;
  const isTodayRequest = requestedDate === today ||
    /(오늘|금일|today)/i.test(String(query || ""));

  if (requestedDate || isTodayRequest) {
    const effectiveDate = requestedDate || today;
    const exact = cardsOnExactDate(cards, effectiveDate, scope?.region || null, limit);
    if (exact.length) {
      return {
        cards: exact,
        date_mode: "exact",
        requested_date: effectiveDate,
        actual_date: effectiveDate,
      };
    }
    const latest = cardsOnLatestAvailableDate(cards, scope?.region || null, limit);
    if (latest.cards.length) {
      return {
        cards: latest.cards,
        date_mode: "fallback_latest",
        requested_date: effectiveDate,
        actual_date: latest.actual_date,
      };
    }
    return { cards: [], date_mode: "empty", requested_date: effectiveDate, actual_date: null };
  }

  const scored = lexicalSearchCards(cards, query, Math.max(limit + 2, 6), scope);
  if (scored.length) {
    return {
      cards: scored.slice(0, limit),
      date_mode: "lexical",
      requested_date: null,
      actual_date: null,
    };
  }

  const latest = cardsOnLatestAvailableDate(cards, scope?.region || null, limit);
  return {
    cards: latest.cards,
    date_mode: latest.cards.length ? "fallback_latest" : "empty",
    requested_date: null,
    actual_date: latest.actual_date,
  };
}

export function retrieveNews({ rawMessage, scope, data }) {
  const result = selectNewsCards(data?.cards || [], rawMessage, scope || {}, 4);
  return {
    source: "news",
    cards: result.cards,
    news_meta: {
      date_mode: result.date_mode,
      requested_date: result.requested_date,
      actual_date: result.actual_date,
    },
    _reasons: [`news_date_mode:${result.date_mode}`, `news_cards:${result.cards.length}`],
  };
}
