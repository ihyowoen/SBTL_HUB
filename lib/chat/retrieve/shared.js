// ============================================================================
// retrieve/shared.js — 공통 scoring 유틸
// ============================================================================
// 기존 retrieval.js에서 추출. news/comparison/general이 공유.
// ============================================================================

import { fmtDate } from "../common.js";

export const REGION_ALIGNMENT_BONUS = 8;
export const DATE_ALIGNMENT_BONUS = 6;
export const TITLE_MATCH_WEIGHT = 10;
export const SUBTITLE_MATCH_WEIGHT = 7;
export const GIST_MATCH_WEIGHT = 5;
export const KEYWORD_MATCH_WEIGHT = 6;
export const ENTITY_MATCH_BONUS = 8;
export const SIGNAL_TOP_BONUS = 3;
export const SIGNAL_HIGH_BONUS = 2;
export const RECENCY_7D_BONUS = 2;
export const RECENCY_30D_BONUS = 1;
export const FALLBACK_PSEUDO_SCORE = 18;

export function isRegionMatch(cardRegion, scopeRegion) {
  if (!scopeRegion) return true;
  if (cardRegion === scopeRegion) return true;
  if (scopeRegion === "US" && (cardRegion === "NA" || /(^|\/)US(\/|$)/.test(String(cardRegion || "")))) return true;
  if (scopeRegion === "NA" && cardRegion === "US") return true;
  if (String(cardRegion || "").split("/").includes(scopeRegion)) return true;
  return false;
}

function parseCardDateToMs(cardDate) {
  const ds = String(cardDate || "").replace(/\./g, "-");
  const ms = new Date(ds).getTime();
  return Number.isNaN(ms) ? null : ms;
}

export function lexicalTokens(query = "") {
  return String(query || "")
    .toLowerCase()
    .replace(/[?!.,:;()\[\]{}]/g, " ")
    .split(/\s+/)
    .filter((w) => w.length >= 2);
}

export function scoreCard(card, ws = [], scope = {}, now = Date.now()) {
  let score = 0;
  const tl = String(card.T || "").toLowerCase();
  const sl = String(card.sub || "").toLowerCase();
  const gl = String(card.g || "").toLowerCase();
  const ks = Array.isArray(card.k) ? card.k.map((k) => String(k).toLowerCase()) : [];

  for (const w of ws) {
    if (tl.includes(w)) score += TITLE_MATCH_WEIGHT;
    if (sl.includes(w)) score += SUBTITLE_MATCH_WEIGHT;
    if (gl.includes(w)) score += GIST_MATCH_WEIGHT;
    if (ks.some((k) => k.includes(w) || w.includes(k))) score += KEYWORD_MATCH_WEIGHT;
  }

  if (scope?.region && isRegionMatch(card.r, scope.region)) score += REGION_ALIGNMENT_BONUS;
  if (scope?.date && card.d && fmtDate(card.d) === fmtDate(scope.date)) score += DATE_ALIGNMENT_BONUS;

  const entityCandidates = Array.isArray(scope?.entity_candidates) && scope.entity_candidates.length
    ? scope.entity_candidates
    : (scope?.entity ? [scope.entity] : []);
  for (const eRaw of entityCandidates) {
    const e = String(eRaw || "").toLowerCase();
    if (!e || e.length < 2) continue;
    if (tl.includes(e) || sl.includes(e) || gl.includes(e) || ks.some((k) => k.includes(e) || e.includes(k))) {
      score += ENTITY_MATCH_BONUS;
      break;
    }
  }

  if (card.s === "t") score += SIGNAL_TOP_BONUS;
  if (card.s === "h") score += SIGNAL_HIGH_BONUS;

  if (card.d) {
    const cardMs = parseCardDateToMs(card.d);
    if (cardMs !== null) {
      const days = (now - cardMs) / 86400000;
      if (days <= 7) score += RECENCY_7D_BONUS;
      else if (days <= 30) score += RECENCY_30D_BONUS;
    }
  }

  return score;
}

export function latestDate(cards) {
  return [...cards.map((c) => c?.d).filter(Boolean)].sort((a, b) => String(b).localeCompare(String(a)))[0] || null;
}

export function lexicalSearchCards(cards, query, limit = 5, scope = {}) {
  const ws = lexicalTokens(query);
  if (!ws.length) return [];
  const now = Date.now();
  return cards
    .map((c) => ({ ...c, _score: scoreCard(c, ws, scope, now) }))
    .filter((c) => c._score > 0)
    .sort((a, b) => {
      const diff = b._score - a._score;
      if (diff !== 0) return diff;
      return String(b.d || "").localeCompare(String(a.d || ""));
    })
    .slice(0, limit);
}

export function cardsOnExactDate(cards, targetDate, region = null, limit = 4) {
  const target = fmtDate(targetDate);
  const rank = { t: 3, h: 2, m: 1, i: 0 };
  const pool = region ? cards.filter((c) => isRegionMatch(c.r, region)) : cards;
  const list = pool.filter((c) => c.d && fmtDate(c.d) === target);
  return list
    .sort((a, b) => (rank[b.s] || 0) - (rank[a.s] || 0))
    .slice(0, limit)
    .map((c) => ({ ...c, _score: FALLBACK_PSEUDO_SCORE }));
}

export function cardsOnLatestAvailableDate(cards, region = null, limit = 4) {
  const rank = { t: 3, h: 2, m: 1, i: 0 };
  const pool = region ? cards.filter((c) => isRegionMatch(c.r, region)) : cards;
  const ld = latestDate(pool);
  if (!ld) {
    return {
      cards: pool.sort((a, b) => (rank[b.s] || 0) - (rank[a.s] || 0)).slice(0, limit).map((c) => ({ ...c, _score: FALLBACK_PSEUDO_SCORE })),
      actual_date: null,
    };
  }
  return {
    cards: pool
      .filter((c) => c.d === ld)
      .sort((a, b) => (rank[b.s] || 0) - (rank[a.s] || 0))
      .slice(0, limit)
      .map((c) => ({ ...c, _score: FALLBACK_PSEUDO_SCORE })),
    actual_date: ld,
  };
}
