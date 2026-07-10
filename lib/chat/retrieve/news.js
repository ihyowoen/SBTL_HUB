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

// 날짜 스코프 경로는 signal/date로만 랭크되므로, 워치 부스트 등으로 들어온
// entity 후보가 있으면 더 큰 풀에서 뽑아 엔티티 매칭 카드를 앞으로 보낸다.
function scopeEntities(scope = {}) {
  const list = Array.isArray(scope?.entity_candidates) && scope.entity_candidates.length
    ? scope.entity_candidates
    : (scope?.entity ? [scope.entity] : []);
  return list.map((e) => String(e || "").toLowerCase()).filter((e) => e.length >= 2);
}

function entityPrefer(cards, ents) {
  if (!ents.length) return cards;
  const hit = (c) => {
    const hay = `${c.T || ""} ${c.sub || ""} ${c.g || ""}`.toLowerCase();
    return ents.some((e) => hay.includes(e));
  };
  // 안정 정렬: 매칭 카드 우선, 그룹 내 기존(신호/날짜) 순서 유지
  return [...cards].sort((a, b) => (hit(b) ? 1 : 0) - (hit(a) ? 1 : 0));
}

function selectNewsCards(cards, query, scope = {}, limit = 4) {
  const today = kstToday();
  const requestedDate = scope?.date || null;
  const isTodayRequest = requestedDate === today ||
    /(오늘|금일|today)/i.test(String(query || ""));
  const ents = scopeEntities(scope);
  const datedPool = ents.length ? Math.max(limit * 3, 12) : limit;

  if (requestedDate || isTodayRequest) {
    const effectiveDate = requestedDate || today;
    const exact = cardsOnExactDate(cards, effectiveDate, scope?.region || null, datedPool);
    if (exact.length) {
      return {
        cards: entityPrefer(exact, ents).slice(0, limit),
        date_mode: "exact",
        requested_date: effectiveDate,
        actual_date: effectiveDate,
      };
    }
    const latest = cardsOnLatestAvailableDate(cards, scope?.region || null, datedPool);
    if (latest.cards.length) {
      return {
        cards: entityPrefer(latest.cards, ents).slice(0, limit),
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
