import { fmtDate } from "./common.js";

const REGION_MAP = { US: "NA", KR: "KR", CN: "CN", EU: "EU", JP: "JP", GL: "GL" };
const REGION_ALIGNMENT_BONUS = 8;
const DATE_ALIGNMENT_BONUS = 6;

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
  const ws = String(query || "")
    .toLowerCase()
    .replace(/[?!.,:;()\[\]{}]/g, " ")
    .split(/\s+/)
    .filter((w) => w.length >= 2);

  if (!ws.length) return [];
  const now = Date.now();

  return cards
    .map((c) => {
      let score = 0;
      const tl = String(c.T || "").toLowerCase();
      const sl = String(c.sub || "").toLowerCase();
      const gl = String(c.g || "").toLowerCase();
      const ks = Array.isArray(c.k) ? c.k.map((k) => String(k).toLowerCase()) : [];

      for (const w of ws) {
        if (tl.includes(w)) score += 10;
        if (sl.includes(w)) score += 6;
        if (gl.includes(w)) score += 4;
        if (ks.some((k) => k.includes(w) || w.includes(k))) score += 5;
      }

      if (scope?.region && isRegionMatch(c.r, scope.region)) score += REGION_ALIGNMENT_BONUS;
      if (scope?.date && c.d && fmtDate(c.d) === fmtDate(scope.date)) score += DATE_ALIGNMENT_BONUS;
      if (scope?.entity) {
        const e = String(scope.entity).toLowerCase();
        if (tl.includes(e) || sl.includes(e)) score += 7;
      }

      if (c.s === "t") score += 3;
      if (c.s === "h") score += 2;

      if (c.d) {
        const cardMs = parseCardDateToMs(c.d);
        if (cardMs !== null) {
          const days = (now - cardMs) / 86400000;
          if (days <= 7) score += 3;
          else if (days <= 30) score += 1;
        }
      }

      return { ...c, _score: score };
    })
    .filter((c) => c._score > 0)
    .sort((a, b) => {
      const diff = b._score - a._score;
      if (diff !== 0) return diff;
      return String(b.d || "").localeCompare(String(a.d || ""));
    })
    .slice(0, limit);
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
    const targetDate = scope?.date || null;
    cards = latestCards(data?.cards || [], 3, scope?.region || null, targetDate);
    if (!cards.length) cards = lexicalSearchCards(data?.cards || [], message, 4, scope);
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
