import { fmtDate } from "./common.js";

const REGION_MAP = { US: "NA", KR: "KR", CN: "CN", EU: "EU", JP: "JP", GL: "GL" };
const REGION_ALIGNMENT_BONUS = 8;
const DATE_ALIGNMENT_BONUS = 6;
const TITLE_MATCH_WEIGHT = 10;
const SUBTITLE_MATCH_WEIGHT = 7;
const GIST_MATCH_WEIGHT = 5;
const KEYWORD_MATCH_WEIGHT = 6;
const ENTITY_MATCH_BONUS = 8;
const SIGNAL_TOP_BONUS = 3;
const SIGNAL_HIGH_BONUS = 2;
const RECENCY_7D_BONUS = 2;
const RECENCY_30D_BONUS = 1;

function isRegionMatch(cardRegion, scopeRegion) {
  if (!scopeRegion) return true;
  if (cardRegion === scopeRegion) return true;
  if (scopeRegion === "US" && cardRegion === "NA") return true;
  return false;
}

function parseCardDateToMs(cardDate) {
  const ds = String(cardDate || "").replace(/\./g, "-");
  const ms = new Date(ds).getTime();
  return Number.isNaN(ms) ? null : ms;
}

function lexicalTokens(query = "") {
  return String(query || "")
    .toLowerCase()
    .replace(/[?!.,:;()\[\]{}]/g, " ")
    .split(/\s+/)
    .filter((w) => w.length >= 2);
}

function scoreCard(card, ws = [], scope = {}, now = Date.now()) {
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

function latestDate(cards) {
  return [...cards.map((c) => c?.d).filter(Boolean)].sort((a, b) => String(b).localeCompare(String(a)))[0] || null;
}

function latestCards(cards, limit = 3, region = null, targetDate = null) {
  const pool = region ? cards.filter((c) => isRegionMatch(c.r, region)) : cards;
  const rank = { t: 3, h: 2, m: 1, i: 0 };

  if (targetDate) {
    const target = fmtDate(targetDate);
    const list = pool.filter((c) => c.d && fmtDate(c.d) === target);
    if (!list.length) return [];
    return list.sort((a, b) => (rank[b.s] || 0) - (rank[a.s] || 0)).slice(0, limit);
  }

  const ld = latestDate(pool);
  if (!ld) return pool.sort((a, b) => (rank[b.s] || 0) - (rank[a.s] || 0)).slice(0, limit);
  return pool
    .filter((c) => c.d === ld)
    .sort((a, b) => (rank[b.s] || 0) - (rank[a.s] || 0))
    .slice(0, limit);
}

function lexicalSearchCards(cards, query, limit = 5, scope = {}) {
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

function selectNewsCards(cards, query, scope = {}, limit = 4) {
  const scored = lexicalSearchCards(cards, query, Math.max(limit + 2, 6), scope);
  if (scored.length) return scored.slice(0, limit);
  const targetDate = scope?.date || null;
  return latestCards(cards, limit, scope?.region || null, targetDate);
}

function matchFaq(faq = [], query = "") {
  const l = String(query || "").toLowerCase();
  for (const f of faq) {
    if ((f.k || []).some((k) => l.includes(String(k).toLowerCase()))) {
      return { answer: f.a, keywords: f.k || [] };
    }
  }
  return null;
}

function getPolicyContext(scope = {}, tracker = { items: [] }) {
  const items = Array.isArray(tracker.items) ? tracker.items : [];
  const regionKey = scope.region ? REGION_MAP[scope.region] || scope.region : null;
  const upcoming = items
    .filter((i) => i.s === "UPCOMING" && (!regionKey || i.r === regionKey || i.r === scope.region))
    .sort((a, b) => String(a.dt || "").localeCompare(String(b.dt || "")))
    .slice(0, 4);

  return {
    upcoming,
    regionKey,
    totalItems: items.length,
  };
}

export function retrieveInternal({ message, intent, scope, data }) {
  const faqHit = matchFaq(data?.faq || [], message);
  if (faqHit) {
    return {
      mode: "faq",
      faq: faqHit,
      cards: [],
      policy: getPolicyContext(scope, data?.tracker),
      ranked: [],
    };
  }

  let cards = [];
  if (intent === "news") {
    cards = selectNewsCards(data?.cards || [], message, scope, 4);
  } else if (intent === "policy") {
    cards = lexicalSearchCards(data?.cards || [], message, 4, scope);
  } else if (intent === "summary") {
    cards = lexicalSearchCards(data?.cards || [], message, 3, scope);
  } else if (intent === "compare") {
    cards = lexicalSearchCards(data?.cards || [], message, 4, scope);
  } else {
    cards = lexicalSearchCards(data?.cards || [], message, 4, scope);
  }

  return {
    mode: "cards",
    cards,
    policy: getPolicyContext(scope, data?.tracker),
    ranked: cards.map((c) => ({ id: c.url || c.T, score: c._score || 0, date: c.d || "" })),
  };
}
