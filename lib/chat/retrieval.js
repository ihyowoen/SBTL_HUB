import { fmtDate, kstToday } from "./common.js";

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

// 의사 점수 — latestCards fallback 카드에 부여해서 confidence.js의 top<18 함정 방지
const FALLBACK_PSEUDO_SCORE = 18;

function isRegionMatch(cardRegion, scopeRegion) {
  if (!scopeRegion) return true;
  if (cardRegion === scopeRegion) return true;
  // 양방향 대칭: US ↔ NA, 그리고 "US/KR" 같은 복합 region도 포함
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

// scope.date를 엄격히 맞춘 카드만 반환. 없으면 빈 배열.
function cardsOnExactDate(cards, targetDate, region = null, limit = 4) {
  const target = fmtDate(targetDate);
  const rank = { t: 3, h: 2, m: 1, i: 0 };
  const pool = region ? cards.filter((c) => isRegionMatch(c.r, region)) : cards;
  const list = pool.filter((c) => c.d && fmtDate(c.d) === target);
  return list
    .sort((a, b) => (rank[b.s] || 0) - (rank[a.s] || 0))
    .slice(0, limit)
    .map((c) => ({ ...c, _score: FALLBACK_PSEUDO_SCORE }));
}

// 데이터셋 내 최신 날짜 카드 반환.
function cardsOnLatestAvailableDate(cards, region = null, limit = 4) {
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

// news intent의 핵심 로직 — date 스코프를 엄격히 반영하고,
// 오늘 카드가 없으면 최신 가용 날짜로 graceful fallback하면서 메타를 남긴다.
function selectNewsCards(cards, query, scope = {}, limit = 4) {
  const today = kstToday();
  const requestedDate = scope?.date || null;
  const isTodayRequest = requestedDate === today ||
    /(오늘|금일|today)/i.test(String(query || ""));

  // 1) 특정 날짜 요청 (오늘 포함)
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
    // 오늘 카드 없음 → 최신 가용 날짜로 fallback
    const latest = cardsOnLatestAvailableDate(cards, scope?.region || null, limit);
    if (latest.cards.length) {
      return {
        cards: latest.cards,
        date_mode: "fallback_latest",
        requested_date: effectiveDate,
        actual_date: latest.actual_date,
      };
    }
    return {
      cards: [],
      date_mode: "empty",
      requested_date: effectiveDate,
      actual_date: null,
    };
  }

  // 2) 날짜 스코프 없음 — lexical 먼저 시도, 없으면 최신 카드
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

function matchFaq(faq = [], query = "") {
  const l = String(query || "").toLowerCase();
  let best = { f: null, hits: 0 };
  for (const f of faq) {
    const hits = (f.k || []).filter((k) => l.includes(String(k).toLowerCase())).length;
    if (hits > best.hits) best = { f, hits };
  }
  if (best.f) return { answer: best.f.a, keywords: best.f.k || [] };
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
  let newsMeta = null;

  if (intent === "news") {
    const result = selectNewsCards(data?.cards || [], message, scope, 4);
    cards = result.cards;
    newsMeta = {
      date_mode: result.date_mode,
      requested_date: result.requested_date,
      actual_date: result.actual_date,
    };
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
    news_meta: newsMeta,
    policy: getPolicyContext(scope, data?.tracker),
    ranked: cards.map((c) => ({ id: c.url || c.T, score: c._score || 0, date: c.d || "" })),
  };
}
