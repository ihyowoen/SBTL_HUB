import { useEffect, useMemo, useRef, useState } from "react";

const WEBTOON_COLLECTIONS = [
  {
    id: "lfp-uncomfortable-truths",
    title: "LFP의 불편한 진실",
    subtitle: "LFP를 둘러싼 대표적 오해와 비용 구조를 웹툰 형식으로 정리한 시리즈",
    badge: "FLAGSHIP SERIES",
    color: "#F85149",
    landingUrl: "/webtoon/lfp-uncomfortable-truths.html",
    status: "NOW LIVE",
    hook: "좋은 배터리일 수 있다. 그런데 너무 쉽게 보면 핵심을 놓친다.",
    description: "EP.01부터 Bonus.01까지, LFP 안전성 인식과 비용 구조를 단계적으로 따라가는 시리즈입니다.",
    items: [
      { id: 101, title: "EP.01 LFP의 두 가지 착각", subtitle: "좋은 배터리일 수 있다. 그런데 너무 쉽게 보면 핵심을 놓친다.", date: "2026.04.05", isNew: true, color: "#F85149", likes: 0, url: "/webtoon/lfp-two-misconceptions-ep1.html", tag: "START" },
      { id: 102, title: "EP.02 덜 타 보인다고, 덜 위험한 건 아니다", subtitle: "보이는 화재 위험과 보이지 않는 off-gas 위험은 같은 말이 아니다.", date: "2026.04.05", isNew: true, color: "#D29922", likes: 0, url: "/webtoon/lfp-two-misconceptions-ep2.html", tag: "PART 2" },
      { id: 103, title: "BONUS.01 누가 진짜 돈을 내나?", subtitle: "끝날 때 비용은 존재한다. 그 돈을 누가 떠안는지 묻는 보너스 에피소드.", date: "2026.04.05", isNew: true, color: "#58A6FF", likes: 0, url: "/webtoon/who-pays-bonus1.html", tag: "BONUS" },
    ],
  },
];

const CATS = [
  { key: "all", label: "HOME", icon: "🔋" },
  { key: "news", label: "NEWS", icon: "📰" },
  { key: "webtoon", label: "TOON", icon: "🎨" },
  { key: "tracker", label: "TRCK", icon: "📊" },
  { key: "chatbot", label: "AI", icon: "🤖" },
];

const SC = { ACTIVE: "#F85149", UPCOMING: "#D29922", WATCH: "#388BFD", DONE: "#7D8590" };
const SL = { ACTIVE: "ACTIVE", UPCOMING: "UPCOMING", WATCH: "WATCH", DONE: "DONE" };
const SIG_C = { t: "#F85149", h: "#D29922", m: "#388BFD", i: "#7D8590" };
const SIG_L = { t: "TOP", h: "HIGH", m: "MID", i: "INFO" };
const REG_FLAG = { US: "🇺🇸", KR: "🇰🇷", EU: "🇪🇺", CN: "🇨🇳", JP: "🇯🇵", GL: "🌐", "US/KR": "🇺🇸" };
const TRACKER_REGION = {
  NA: { flag: "🇺🇸", name: "북미" },
  EU: { flag: "🇪🇺", name: "유럽" },
  CN: { flag: "🇨🇳", name: "중국" },
  KR: { flag: "🇰🇷", name: "한국" },
  JP: { flag: "🇯🇵", name: "일본" },
  GL: { flag: "🌐", name: "글로벌" },
};

/* KST (UTC+9) 기준 현재 시각 */
const kstNow = () => {
  const now = new Date();
  return new Date(now.getTime() + (now.getTimezoneOffset() + 540) * 60000);
};
const kstToday = () => {
  const d = kstNow();
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, "0")}.${String(d.getDate()).padStart(2, "0")}`;
};

const fmtDate = (date) => {
  if (!date) return "-";
  const s = String(date).trim();
  const m = s.match(/^(\d{4})[.-](\d{2})[.-](\d{2})/);
  if (m) return `${m[1]}.${m[2]}.${m[3]}`;
  return s;
};

const shortDate = (date) => {
  const f = fmtDate(date);
  return f.length >= 10 ? f.slice(5) : f;
};

const pct = (num, total) => `${Math.max(0, Math.min(100, ((Number(num) || 0) / Math.max(1, Number(total) || 0)) * 100))}%`;

const T = (dark = true) => dark
  ? { bg: "#0D1117", card: "#161B26", card2: "#1C2333", tx: "#E6EDF3", sub: "#7D8590", brd: "#21293A", cyan: "#58A6FF", sh: "0 2px 8px rgba(0,0,0,0.4)" }
  : { bg: "#F4F6FA", card: "#FFFFFF", card2: "#F8F9FC", tx: "#1A1A2A", sub: "#6B7280", brd: "#E0E3EA", cyan: "#2D5A8E", sh: "0 2px 10px rgba(0,0,0,0.06)" };

const quickPrimary = [
  "오늘 핵심 카드",
  "오늘의 시그널 TOP",
  "외부 기사로 전환 →",
  "한국 정책 일정 뭐 있어?",
  "미국 FEOC 쉽게 설명해줘",
  "이번주 ESS 시그널 요약",
  "전고체 어디까지 왔어?",
  "중국 가격 흐름 체크",
];

function useKnowledgeBase() {
  const [cards, setCards] = useState([]);
  const [faq, setFaq] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch("/data/cards.json").then((r) => r.json()).then((d) => d.cards || d).catch(() => []),
      fetch("/data/faq.json").then((r) => r.json()).catch(() => []),
    ]).then(([c, f]) => {
      setCards(Array.isArray(c) ? c : []);
      setFaq(Array.isArray(f) ? f : []);
      setLoading(false);
    });
  }, []);

  return { cards, faq, loading, cardCount: cards.length, faqCount: faq.length };
}

function useTrackerData() {
  const [raw, setRaw] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/data/tracker_data.json")
      .then((r) => r.json())
      .then(setRaw)
      .catch(() => setRaw(null))
      .finally(() => setLoading(false));
  }, []);

  const tracker = useMemo(() => {
    const fallback = { meta: { lastUpdated: "-", totalItems: 0 }, summary: { ACTIVE: 0, UPCOMING: 0, WATCH: 0, DONE: 0 }, regions: [], upcoming: [], items: [] };
    if (!raw || !Array.isArray(raw.items)) return fallback;
    const items = raw.items;
    const summary = items.reduce((acc, item) => {
      const k = item?.s;
      if (acc[k] !== undefined) acc[k] += 1;
      return acc;
    }, { ACTIVE: 0, UPCOMING: 0, WATCH: 0, DONE: 0 });
    const regions = Object.keys(TRACKER_REGION)
      .map((code) => {
        const list = items.filter((i) => i.r === code);
        if (!list.length) return null;
        return { code, flag: TRACKER_REGION[code].flag, name: TRACKER_REGION[code].name, total: list.length, ACTIVE: list.filter((i) => i.s === "ACTIVE").length };
      })
      .filter(Boolean);
    const upcoming = items
      .filter((i) => i.s === "UPCOMING")
      .sort((a, b) => String(a.dt || "").localeCompare(String(b.dt || "")))
      .slice(0, 8)
      .map((i) => ({ date: fmtDate(i.dt), title: i.t, region: i.r }));
    return {
      meta: { lastUpdated: raw.meta?.lastUpdated || "-", totalItems: Number(raw.meta?.totalItems ?? items.length) || items.length },
      summary,
      regions,
      upcoming,
      items,
    };
  }, [raw]);

  return { tracker, loading };
}

function latestDate(cards) {
  return [...cards.map((c) => c?.d).filter(Boolean)].sort((a, b) => String(b).localeCompare(String(a)))[0] || null;
}

function latestCards(cards, limit = 3, region = null, targetDate = null) {
  // When region is specified, filter by region FIRST then find latest date within that subset
  const pool = region ? cards.filter((c) => c.r === region) : cards;
  const rank = { t: 3, h: 2, m: 1, i: 0 };

  if (targetDate) {
    let list = pool.filter((c) => c.d && String(c.d).startsWith(targetDate));
    if (list.length) return list.sort((a, b) => (rank[b.s] || 0) - (rank[a.s] || 0)).slice(0, limit);
    // fallback: nearest earlier date — find the single closest date first
    const nearbyDates = [...new Set(pool.filter((c) => c.d && String(c.d) <= targetDate).map((c) => c.d))].sort((a, b) => String(b).localeCompare(String(a)));
    if (nearbyDates.length) {
      const closestDate = nearbyDates[0];
      const closestCards = pool.filter((c) => c.d === closestDate);
      return closestCards.sort((a, b) => (rank[b.s] || 0) - (rank[a.s] || 0)).slice(0, limit);
    }
    return pool.sort((a, b) => (rank[b.s] || 0) - (rank[a.s] || 0)).slice(0, limit);
  }

  // No targetDate: use latest date within the (possibly region-filtered) pool
  const ld = latestDate(pool);
  if (!ld) return pool.sort((a, b) => (rank[b.s] || 0) - (rank[a.s] || 0)).slice(0, limit);
  const list = pool.filter((c) => c.d === ld);
  return list.sort((a, b) => (rank[b.s] || 0) - (rank[a.s] || 0)).slice(0, limit);
}

function detectDate(txt) {
  const m = txt.match(/(\d{4})[년.\-\/]?\s*(\d{1,2})[월.\-\/]?\s*(\d{1,2})/);
  if (m) {
    const y = m[1], mo = m[2].padStart(2, "0"), d = m[3].padStart(2, "0");
    return `${y}.${mo}.${d}`;
  }
  return null;
}

function searchCards(cards, query, limit = 5) {
  const ws = query.toLowerCase().replace(/[?!.,]/g, " ").split(/\s+/).filter((w) => w.length >= 2);
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
      if (c.s === "t") score += 3;
      if (c.s === "h") score += 2;
      // Freshness bonus: recent cards get a small boost
      if (c.d) {
        const ds = String(c.d).replace(/\./g, "-");
        const cardMs = new Date(ds).getTime();
        if (!isNaN(cardMs)) {
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
      // Tie-break: most recent date first
      return String(b.d || "").localeCompare(String(a.d || ""));
    })
    .slice(0, limit);
}

// Keywords that trigger Brave external article search instead of internal cards
const BRAVE_KEYWORDS = /(실시간|외부|원문|링크|기사\s*검색|brave|외부\s*기사|최신\s*기사|검색해|찾아줘.*기사|뉴스\s*링크|외부\s*링크)/;
const BRAVE_SEARCH_SUFFIX = "battery ESS EV";

function isBraveQuery(txt) {
  const l = txt.toLowerCase();
  return BRAVE_KEYWORDS.test(l);
}

function classifyQuestion(txt) {
  const l = txt.toLowerCase();
  if (/(최신|뉴스|소식|현황|지금|오늘|최근|이번)/.test(l)) return "news";
  if (/(일정|정책|규제|시행|법안|언제|예정|스케줄)/.test(l)) return "policy";
  if (/(비교|차이|vs|대비|어떤 게|뭐가 더)/.test(l)) return "compare";
  if (/(요약|정리|핵심|브리핑|한 줄|한줄)/.test(l)) return "summary";
  return "general";
}

async function fetchBraveResults(query) {
  try {
    const res = await fetch("/api/brave", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: `${query} ${BRAVE_SEARCH_SUFFIX}` }),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      // Differentiate error types from API response
      if (res.status === 500 && data.error === 'Brave API key not configured') {
        return { error: 'auth-config', message: 'Brave API 키가 설정되지 않았어. 관리자에게 문의해줘.' };
      }
      if (res.status === 429) {
        return { error: 'rate-limit', message: 'Brave 검색 한도 초과. 잠시 후 다시 시도해줘.' };
      }
      if (res.status >= 500) {
        return { error: 'provider-error', message: 'Brave 서비스에 일시적 문제가 있어. 내부 카드로 검색할게.' };
      }
      return { error: 'no-result', message: '외부 기사를 찾지 못했어. 검색어를 바꿔보거나, 내부 카드에서 찾아볼게.' };
    }
    const data = await res.json();
    const results = data?.web?.results || [];
    if (!results.length) {
      return { error: 'no-result', message: '외부 기사를 찾지 못했어. 검색어를 바꿔보거나, 내부 카드에서 찾아볼게.' };
    }
    return results.slice(0, 4).map((r) => ({
      title: r.title || "",
      description: r.description || "",
      url: r.url || "",
    }));
  } catch (err) {
    return { error: 'network-error', message: '네트워크 오류로 외부 검색 실패. 내부 카드로 검색할게.' };
  }
}


function parseOrdinal(str) {
  const s = str.replace(/\s+/g, "");
  if (s === "첫번째" || s === "1번") return 0;
  if (s === "두번째" || s === "2번") return 1;
  if (s === "세번째" || s === "3번") return 2;
  if (s === "네번째" || s === "4번") return 3;
  return 0;
}

function resolveFollowUp(txt, ctx) {
  if (!ctx) return null;
  const l = txt.toLowerCase();

  const ordinalMatch = l.match(/(첫\s*번째|두\s*번째|세\s*번째|네\s*번째|1번|2번|3번|4번)/);
  if (ordinalMatch) {
    const idx = parseOrdinal(ordinalMatch[1]);
    const pool = ctx.lastLinks?.length ? ctx.lastLinks : ctx.lastCards;
    if (pool && pool[idx]) return { type: "selected", item: pool[idx] };
  }

  if (/(그\s*기사|방금|직전|저\s*카드|그\s*카드|아까\s*그)/.test(l)) {
    if (ctx.selected) return { type: "selected", item: ctx.selected };
    const pool = ctx.lastLinks?.length ? ctx.lastLinks : ctx.lastCards;
    if (pool?.length === 1) return { type: "selected", item: pool[0] };
    if (pool?.length) return { type: "list", items: pool };
  }

  if (/(더\s*찾|더\s*보여|관련.*더)/.test(l)) {
    return { type: "expand", context: ctx };
  }

  return null;
}

function detectRegion(txt) {
  const l = txt.toLowerCase();
  if (/(한국|국내|kr)/.test(l)) return "KR";
  if (/(미국|북미|us|america)/.test(l)) return "US";
  if (/(중국|cn|china)/.test(l)) return "CN";
  if (/(유럽|eu|europe)/.test(l)) return "EU";
  if (/(일본|jp|japan)/.test(l)) return "JP";
  return null;
}

function followUps(type, depth = 1, ctx = null) {
  const regionLabel = ctx?.region ? ({ US: "미국", KR: "한국", CN: "중국", EU: "유럽", JP: "일본" }[ctx.region] || "") : "";
  if (depth <= 1) {
    if (type === "news") {
      const base = ["요약해서 다시 정리", "관련 카드 더 보여줘", "외부 기사 링크 검색"];
      // Suggest other regions, not the current one
      if (!regionLabel) base.push("한국 뉴스만", "미국 뉴스만");
      else {
        if (ctx?.region !== "US") base.push("미국 뉴스만");
        if (ctx?.region !== "KR") base.push("한국 뉴스만");
      }
      return base;
    }
    if (type === "policy") return ["다가오는 일정만", "한국/EU 비교", "실무 영향만 요약", "관련 카드 더 보여줘"];
    if (type === "compare") return ["한 줄 결론만", "관련 카드 더 보여줘", "왜 중요한지 한 줄로"];
    if (type === "summary") return ["조금 더 쉽게 설명해줘", "관련 카드 더 보여줘", "왜 중요한지 한 줄로"];
    return ["조금 더 쉽게 설명해줘", "관련 카드 더 보여줘", "정책 일정만 따로 정리해줘"];
  }
  // 3rd-level: context-dependent
  if (type === "news") {
    const items = ["오늘 기준으로 다시", "관련 카드 더 보여줘"];
    if (ctx?.region !== "US") items.push("미국만 따로");
    if (ctx?.region !== "CN") items.push("중국만 따로");
    return items;
  }
  if (type === "policy") return ["다가오는 일정만", "한국/EU 비교", "실무 영향만 요약"];
  if (type === "compare") return ["쉽게 비유해서 설명", "LFP랑 비교", "왜 중요한지 한 줄로"];
  if (type === "summary") return ["왜 중요한지 한 줄로", "LFP랑 비교", "관련 카드 더 보여줘"];
  return ["쉽게 비유해서 설명", "LFP랑 비교", "왜 중요한지 한 줄로", "정책 일정만 따로 정리해줘"];
}

function SmallPill({ label, dark }) {
  const t = T(dark);
  return <span style={{ fontSize: 9, fontWeight: 800, color: t.cyan, background: dark ? "rgba(88,166,255,0.14)" : "rgba(45,90,142,0.10)", padding: "4px 8px", borderRadius: 999, fontFamily: "'JetBrains Mono',monospace" }}>{label}</span>;
}

function NewsItem({ card, dark }) {
  const t = T(dark);
  const sig = card.s || "i";
  const [showGist, setShowGist] = useState(false);
  const [showSummary, setShowSummary] = useState(false);
  const [showWhy, setShowWhy] = useState(false);
  const [summaryContent, setSummaryContent] = useState("");
  const [whyContent, setWhyContent] = useState("");
  const [analysisContent, setAnalysisContent] = useState("");
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const isForeign = card.r && card.r !== "KR";

  const fetchAnalysis = async (mode) => {
    setLoadingAnalysis(true);
    try {
      const res = await fetch("/api/analysis", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ card, mode }),
      });
      const data = await res.json();
      if (mode === "why") setWhyContent(data.result);
      else if (mode === "summary") setSummaryContent(data.result);
      else if (mode === "analysis") setAnalysisContent(data.result);
    } catch (err) {
      console.error("Analysis fetch error:", err);
      // Fallback to existing field data
      if (mode === "why") setWhyContent(card.g || card.sub || "");
      else if (mode === "summary") setSummaryContent(card.T + "\n\n" + (card.sub || ""));
      else if (mode === "analysis") setAnalysisContent(card.g || "");
    } finally {
      setLoadingAnalysis(false);
    }
  };

  return (
    <div onClick={() => card.url && window.open(card.url, "_blank")} style={{ background: t.card2, borderRadius: 12, padding: "12px 14px", borderLeft: `3px solid ${SIG_C[sig]}`, border: `1px solid ${t.brd}`, cursor: card.url ? "pointer" : "default" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 5 }}>
        <span style={{ fontSize: 8, fontWeight: 800, color: SIG_C[sig], background: `${SIG_C[sig]}20`, padding: "2px 6px", borderRadius: 999, fontFamily: "'JetBrains Mono',monospace" }}>{SIG_L[sig]}</span>
        <span style={{ fontSize: 9, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>{REG_FLAG[card.r] || "🌐"} {shortDate(card.d)}</span>
        {isForeign && <span style={{ fontSize: 8, fontWeight: 700, color: "#58A6FF", background: "rgba(88,166,255,0.12)", padding: "2px 6px", borderRadius: 999, fontFamily: "'JetBrains Mono',monospace" }}>해외</span>}
        {card.src && <span style={{ fontSize: 8, color: t.sub, marginLeft: "auto", fontFamily: "'JetBrains Mono',monospace" }}>{card.src}</span>}
      </div>
      <h3 style={{ fontSize: 13, fontWeight: 700, color: t.tx, margin: 0, lineHeight: 1.45 }}>{card.T}</h3>
      {card.sub && <p style={{ fontSize: 11, color: t.sub, margin: "4px 0 0", lineHeight: 1.45 }}>{card.sub}</p>}

      {/* On-demand analysis panels - only shown when clicked */}
      {showSummary && isForeign && (
        <div style={{ marginTop: 6, padding: "8px 10px", background: dark ? "rgba(88,166,255,0.06)" : "rgba(88,166,255,0.04)", borderRadius: 8, border: `1px solid ${dark ? "rgba(88,166,255,0.15)" : "rgba(88,166,255,0.1)"}` }}>
          <div style={{ fontSize: 9, fontWeight: 800, color: "#58A6FF", marginBottom: 4, fontFamily: "'JetBrains Mono',monospace" }}>📰 한국어 요약</div>
          {loadingAnalysis && !summaryContent ? (
            <div style={{ fontSize: 10, color: t.sub, fontStyle: "italic" }}>분석 생성 중...</div>
          ) : (
            <div style={{ fontSize: 11, color: t.tx, lineHeight: 1.6, whiteSpace: "pre-wrap" }}>
              {summaryContent}
            </div>
          )}
          {card.src && <div style={{ fontSize: 9, color: t.sub, marginTop: 4, fontFamily: "'JetBrains Mono',monospace" }}>출처: {card.src} · {fmtDate(card.d)}</div>}
        </div>
      )}
      {showWhy && card.g && (
        <div style={{ marginTop: 6, padding: "8px 10px", background: dark ? "rgba(209,153,34,0.06)" : "rgba(209,153,34,0.04)", borderRadius: 8, border: `1px solid ${dark ? "rgba(209,153,34,0.15)" : "rgba(209,153,34,0.1)"}` }}>
          <div style={{ fontSize: 9, fontWeight: 800, color: "#D29922", marginBottom: 4, fontFamily: "'JetBrains Mono',monospace" }}>⚡ 왜 중요한지</div>
          {loadingAnalysis && !whyContent ? (
            <div style={{ fontSize: 10, color: t.sub, fontStyle: "italic" }}>분석 생성 중...</div>
          ) : (
            <div style={{ fontSize: 11, color: t.tx, lineHeight: 1.6, whiteSpace: "pre-wrap" }}>
              {whyContent}
            </div>
          )}
          {card.src && <div style={{ fontSize: 9, color: t.sub, marginTop: 4, fontFamily: "'JetBrains Mono',monospace" }}>출처: {card.src} · {fmtDate(card.d)}</div>}
        </div>
      )}
      {showGist && card.g && (
        <div style={{ marginTop: 8, padding: "10px 12px", background: dark ? "rgba(168,85,247,0.07)" : "rgba(168,85,247,0.04)", borderRadius: 8, border: `1px solid ${dark ? "rgba(168,85,247,0.2)" : "rgba(168,85,247,0.12)"}`, borderLeft: "3px solid #A855F7" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8 }}>
            <span style={{ fontSize: 9, fontWeight: 800, color: "#A855F7", fontFamily: "'JetBrains Mono',monospace" }}>🤖 AI 해설</span>
            <span style={{ fontSize: 8, color: dark ? "rgba(168,85,247,0.6)" : "rgba(168,85,247,0.5)", fontStyle: "italic", fontFamily: "'JetBrains Mono',monospace" }}>※ AI 해석 기반 분석</span>
          </div>
          {loadingAnalysis && !analysisContent ? (
            <div style={{ fontSize: 10, color: t.sub, fontStyle: "italic" }}>AI 해설 생성 중...</div>
          ) : (
            <div style={{ fontSize: 11, color: t.tx, lineHeight: 1.7, whiteSpace: "pre-wrap" }}>
              {analysisContent}
            </div>
          )}
          {(card.src || card.d) && <div style={{ marginTop: 6, fontSize: 8, color: t.sub, opacity: 0.6, fontFamily: "'JetBrains Mono',monospace" }}>{card.src}{card.d ? ` · ${fmtDate(card.d)}` : ""}</div>}
        </div>
      )}

      <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 6, flexWrap: "wrap" }}>
        {card.url && <span style={{ fontSize: 9, color: t.cyan, fontFamily: "'JetBrains Mono',monospace" }}>open source ↗</span>}
        {/* On-demand analysis buttons - click to reveal */}
        {isForeign && (card.T || card.sub) && (
          <button onClick={(e) => { e.stopPropagation(); if (!showSummary && !summaryContent) fetchAnalysis('summary'); setShowSummary(!showSummary); setShowWhy(false); setShowGist(false); }} aria-label={showSummary ? "Hide Korean summary" : "Show Korean summary"} style={{ fontSize: 9, color: "#58A6FF", background: "transparent", border: `1px solid ${t.brd}`, borderRadius: 999, padding: "2px 8px", cursor: "pointer", fontFamily: "'JetBrains Mono',monospace", fontWeight: 700 }}>
            {showSummary ? "△ 요약 닫기" : "한국어 요약"}
          </button>
        )}
        {card.g && (
          <button onClick={(e) => { e.stopPropagation(); if (!showWhy && !whyContent) fetchAnalysis('why'); setShowWhy(!showWhy); setShowSummary(false); setShowGist(false); }} aria-label={showWhy ? "Hide importance" : "Show why important"} style={{ fontSize: 9, color: "#D29922", background: "transparent", border: `1px solid ${t.brd}`, borderRadius: 999, padding: "2px 8px", cursor: "pointer", fontFamily: "'JetBrains Mono',monospace", fontWeight: 700 }}>
            {showWhy ? "△ 닫기" : "왜 중요한지"}
          </button>
        )}
        {card.g && (
          <button onClick={(e) => { e.stopPropagation(); if (!showGist && !analysisContent) fetchAnalysis('analysis'); setShowGist(!showGist); setShowSummary(false); setShowWhy(false); }} aria-label={showGist ? "Close analysis" : "Show analysis"} style={{ fontSize: 9, color: "#A855F7", background: "transparent", border: `1px solid ${dark ? "rgba(168,85,247,0.3)" : "rgba(168,85,247,0.2)"}`, borderRadius: 999, padding: "2px 8px", cursor: "pointer", fontFamily: "'JetBrains Mono',monospace", fontWeight: 700 }}>
            {showGist ? "△ 닫기" : "🤖 AI 해설"}
          </button>
        )}
      </div>
    </div>
  );
}

function Home({ kb, tracker, onNav, dark }) {
  const t = T(dark);
  const featured = WEBTOON_COLLECTIONS[0];
  const picks = latestCards(kb.cards, 3);
  const today = kstNow();
  const dayNames = ["일", "월", "화", "수", "목", "금", "토"];
  const todayStr = `${kstToday()} (${dayNames[today.getDay()]})`;
  return (
    <div style={{ padding: "0 14px 120px", display: "flex", flexDirection: "column", gap: 12 }}>
      <div style={{ background: `linear-gradient(135deg, ${dark ? "#151B2B" : "#ffffff"}, ${dark ? "#1F2840" : "#EEF3FF"})`, borderRadius: 18, padding: "18px 16px", border: `1px solid ${dark ? "#2C3550" : t.brd}`, boxShadow: t.sh }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap", marginBottom: 10 }}>
              <SmallPill label="SBTL HUB" dark={dark} />
              <span style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>BATTERY · ESS · EV</span>
            </div>
            <div style={{ fontSize: 24, fontWeight: 900, color: t.tx, lineHeight: 1.2 }}>SBTL Strategic Intelligence Brief</div>
            <div style={{ fontSize: 11, color: t.cyan, fontFamily: "'JetBrains Mono',monospace", marginTop: 8 }}>📅 {todayStr}</div>
            <div style={{ fontSize: 12, color: t.sub, lineHeight: 1.65, marginTop: 6 }}>배터리·ESS·EV 밸류체인을 중심으로 정책, 공급망, 기술, 기업 이슈를 선별해 정리하는 인텔리전스 허브입니다.</div>
          </div>
          <div style={{ width: 56, height: 56, borderRadius: 16, background: dark ? "rgba(88,166,255,0.12)" : "rgba(88,166,255,0.08)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 28 }}>🔋</div>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 8, marginTop: 14 }}>
          {[{ label: "CARDS", value: kb.cardCount }, { label: "FAQ", value: kb.faqCount }, { label: "REGIONS", value: 5 }, { label: "TRACKER", value: tracker.meta.totalItems }].map((item) => (
            <div key={item.label} style={{ background: dark ? "rgba(10,14,20,0.55)" : "rgba(255,255,255,0.88)", border: `1px solid ${t.brd}`, borderRadius: 12, padding: "10px 8px", textAlign: "center" }}>
              <div style={{ fontSize: 16, fontWeight: 900, color: t.tx, fontFamily: "'JetBrains Mono',monospace" }}>{item.value}</div>
              <div style={{ fontSize: 9, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginTop: 4 }}>{item.label}</div>
            </div>
          ))}
        </div>
        <div style={{ display: "flex", gap: 8, marginTop: 14 }}>
          <button onClick={() => onNav("news")} style={{ flex: 1, border: "none", borderRadius: 10, padding: "10px 12px", background: t.cyan, color: "#000", fontSize: 11, fontWeight: 900, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>NEWS FEED →</button>
          <button onClick={() => onNav("tracker")} style={{ flex: 1, border: `1px solid ${t.brd}`, borderRadius: 10, padding: "10px 12px", background: "transparent", color: t.tx, fontSize: 11, fontWeight: 900, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>TRACKER →</button>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
        <div onClick={() => onNav("webtoon")} style={{ background: t.card2, borderRadius: 14, padding: 14, border: `1px solid ${t.brd}`, cursor: "pointer" }}>
          <div style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginBottom: 6 }}>FEATURED SERIES</div>
          <div style={{ fontSize: 18, fontWeight: 900, color: t.tx, lineHeight: 1.3 }}>{featured.title}</div>
          <div style={{ fontSize: 11, color: t.sub, lineHeight: 1.55, marginTop: 8 }}>{featured.subtitle}</div>
        </div>
        <div onClick={() => onNav("chatbot")} style={{ background: t.card2, borderRadius: 14, padding: 14, border: `1px solid ${t.brd}`, cursor: "pointer" }}>
          <div style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginBottom: 6 }}>AI DESK</div>
          <div style={{ fontSize: 18, fontWeight: 900, color: t.tx, lineHeight: 1.3 }}>강차장의 배터리 상담소</div>
          <div style={{ fontSize: 11, color: t.sub, lineHeight: 1.55, marginTop: 8 }}>질문하면 핵심 요약, 관련 카드, 최신 링크를 이어서 보여줍니다.</div>
        </div>
      </div>

      <div style={{ background: t.card2, borderRadius: 14, padding: "14px 16px", border: `1px solid ${t.brd}` }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8, marginBottom: 10 }}>
          <div>
            <div style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginBottom: 4 }}>EDITOR'S PICKS</div>
            <div style={{ fontSize: 16, fontWeight: 900, color: t.tx }}>오늘의 핵심 카드</div>
          </div>
          <button onClick={() => onNav("news")} style={{ border: `1px solid ${t.brd}`, background: "transparent", color: t.sub, borderRadius: 8, padding: "7px 10px", fontSize: 10, fontWeight: 800, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>OPEN NEWS</button>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>{picks.map((card, i) => <NewsItem key={`${card.T}-${i}`} card={card} dark={dark} />)}</div>
      </div>
    </div>
  );
}

function ChatBot({ kb, tracker, dark }) {
  const t = T(dark);
  const [msgs, setMsgs] = useState([{ role: "assistant", content: "안녕, 강차장이야. 🔋\n\n궁금한 주제를 편하게 보내줘.\n핵심부터 짧게 정리해주고,\n관련 카드나 최근 이슈도 같이 찾아줄게." }]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [searchMode, setSearchMode] = useState("internal"); // "internal" | "external"
  const [extQuery, setExtQuery] = useState("");
  const endRef = useRef(null);
  const depthRef = useRef(0);
  const lastCtxRef = useRef({ qType: null, region: null, date: null, cards: [], links: [], query: "", selected: null, lastCards: [], lastLinks: [] });

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs, loading]);

  const matchFaq = (txt) => {
    const l = txt.toLowerCase();
    for (const f of kb.faq) {
      if ((f.k || []).some((k) => l.includes(String(k).toLowerCase()))) return f.a;
    }
    return null;
  };

  const updateCtx = (patch) => {
    lastCtxRef.current = { ...lastCtxRef.current, ...patch };
  };

  const makeSuggestions = (qType) => {
    const depth = depthRef.current;
    return followUps(qType, depth, lastCtxRef.current).map((label) => ({ label }));
  };

  const buildCardMessage = (cards, textType = "general", targetDate = null) => {
    const regionLabel = lastCtxRef.current.region ? ({ US: "미국", KR: "한국", CN: "중국", EU: "유럽", JP: "일본" }[lastCtxRef.current.region] || "") : "";
    const dateLabel = targetDate || fmtDate(cards[0]?.d);
    let content;
    if (textType === "news") {
      content = `${regionLabel ? regionLabel + " " : ""}${dateLabel} 기준 핵심 뉴스야.`;
      if (cards.length) {
        const whyLines = cards.slice(0, 3).map((c) => c.g ? `• ${c.T}\n  → ${c.g}` : `• ${c.T}`).join("\n\n");
        content += `\n\n${whyLines}`;
      }
    } else if (textType === "summary") {
      const lines = cards.slice(0, 3).map((c, i) => `${i + 1}. ${c.T}`).join("\n");
      content = `핵심 3줄 요약이야.\n\n${lines}`;
      if (cards[0]?.url) content += "\n\n관련 카드 링크도 같이 확인해봐.";
    } else if (textType === "compare") {
      const diffs = cards.slice(0, 3).map((c, i) => `${i + 1}. ${c.T}`).join("\n");
      content = `비교 관련 카드야.\n\n${diffs}`;
      if (cards.length >= 2) content += `\n\n한 줄 결론: 위 카드들은 관점이 다르지만 배터리·ESS 밸류체인에서 연결되는 이슈야. 카드를 눌러서 자세히 확인해봐.`;
    } else if (textType === "policy") {
      content = `관련 정책 카드를 정리했어.`;
    } else {
      content = `관련 카드 ${cards.length}건을 찾았어.`;
    }
    depthRef.current += 1;
    updateCtx({ qType: textType, cards, date: targetDate || cards[0]?.d });
    return {
      role: "assistant",
      content,
      sourceBadge: "internal",
      cards: cards.map((c) => ({ title: c.T, subtitle: c.sub, signal: c.s, url: c.url, region: c.r, date: c.d, source: c.src, gist: c.g })),
      suggestions: makeSuggestions(textType),
    };
  };

  const sendWithText = async (rawText) => {
    const txt = String(rawText || "").trim();
    if (!txt || loading) return;
    setLoading(true);
    setInput("");
    setMsgs((prev) => [...prev, { role: "user", content: txt }]);

    // Follow-up resolution: check if the message refers to a previous card/link
    const followUp = resolveFollowUp(txt, lastCtxRef.current);
    if (followUp) {
      depthRef.current += 1;
      if (followUp.type === "selected") {
        const item = followUp.item;
        const isLink = !!item.url && !item.T;
        const title = item.title || item.T || "";
        const desc = item.subtitle || item.sub || item.description || "";
        const gist = item.gist || item.g || "";
        const content = `📌 선택된 항목:\n${title}${desc ? "\n" + desc : ""}${gist ? "\n\n💡 " + gist : ""}${item.url ? "\n\n→ " + item.url : ""}`;
        updateCtx({ selected: item });
        setMsgs((prev) => [...prev, {
          role: "assistant",
          content,
          ...(item.url ? { braveLinks: [{ title, description: desc, url: item.url }] } : {}),
          suggestions: [{ label: "왜 중요한지 설명해줘" }, { label: "관련 카드 더 보여줘" }, { label: "요약해서 다시 정리" }],
        }]);
        setLoading(false);
        return;
      }
      if (followUp.type === "list") {
        const items = followUp.items;
        const lines = items.map((it, i) => `${i + 1}. ${it.title || it.T || ""}`).join("\n");
        setMsgs((prev) => [...prev, {
          role: "assistant",
          content: `어떤 항목을 말하는 거야?\n\n${lines}`,
          suggestions: items.slice(0, 4).map((it, i) => ({ label: `${i + 1}번째` })),
        }]);
        setLoading(false);
        return;
      }
      if (followUp.type === "expand") {
        const ctx = followUp.context;
        const expandQuery = ctx.query || txt;
        const expandRegion = ctx.region;
        const more = searchCards(kb.cards, expandQuery, 5);
        if (more.length) {
          updateCtx({ lastCards: more });
          setMsgs((prev) => [...prev, {
            role: "assistant",
            content: `"${expandQuery}" 관련 카드를 더 찾았어.`,
            cards: more.map((c) => ({ title: c.T, subtitle: c.sub, signal: c.s, url: c.url, region: c.r, date: c.d, source: c.src, gist: c.g })),
            sourceBadge: "internal",
            suggestions: [{ label: "외부 기사 링크 검색" }, { label: "요약해서 다시 정리" }],
          }]);
          setLoading(false);
          return;
        }
      }
    }

    const qType = classifyQuestion(txt);
    const region = detectRegion(txt) || (/(방금|이전|직전|아까)/.test(txt) ? lastCtxRef.current.region : null);
    const targetDate = detectDate(txt);
    updateCtx({ query: txt, region: region || lastCtxRef.current.region });

    const faq = matchFaq(txt);
    if (faq) {
      depthRef.current += 1;
      updateCtx({ qType });
      setMsgs((prev) => [...prev, { role: "assistant", content: faq, suggestions: makeSuggestions(qType) }]);
      setLoading(false);
      return;
    }

    // Brave external article search: triggered by specific keywords
    if (isBraveQuery(txt)) {
      const braveResponse = await fetchBraveResults(txt);
      depthRef.current += 1;

      // Handle Brave API errors
      if (braveResponse.error) {
        // Log error details for debugging
        console.warn("[Brave] API error:", braveResponse.errorType, "|", braveResponse.errorMessage, "| status:", braveResponse.statusCode);

        const errorMessages = {
          UNAUTHORIZED: "⚠️ 외부 검색 API 인증에 문제가 있어. 관리자에게 확인이 필요해. 내부 카드로 대체할게.",
          FORBIDDEN: "⚠️ 외부 검색 API 인증에 문제가 있어. 관리자에게 확인이 필요해. 내부 카드로 대체할게.",
          RATE_LIMIT: "⚠️ 외부 검색 요청이 많아서 잠시 제한됐어. 잠시 후 다시 시도하거나 내부 카드를 확인해봐.",
          SERVER_ERROR: "⚠️ 외부 검색 서버에 일시적인 문제가 있어. 내부 카드로 대체할게.",
          NETWORK_ERROR: "⚠️ 외부 검색 서비스에 연결할 수 없어. 네트워크를 확인하거나 내부 카드를 확인해봐.",
        };

        const errorMsg = errorMessages[braveResponse.errorType] || "⚠️ 외부 검색 중 문제가 발생했어. 내부 카드로 대체할게.";

        // Fallback to internal cards with error context
        const cards = latestCards(kb.cards, 3, region, targetDate);
        if (cards.length) {
          updateCtx({ lastCards: cards });
          setMsgs((prev) => [...prev, {
            role: "assistant",
            content: `${errorMsg}\n\n관련 내부 카드를 찾았어.`,
            cards: cards.map((c) => ({ title: c.T, subtitle: c.sub, signal: c.s, url: c.url, region: c.r, date: c.d, source: c.src, gist: c.g })),
            sourceBadge: "internal",
            suggestions: [{ label: "오늘 핵심 카드" }, { label: "관련 카드 더 보여줘" }],
          }]);
        } else {
          setMsgs((prev) => [...prev, {
            role: "assistant",
            content: errorMsg,
            suggestions: [{ label: "오늘 핵심 카드" }, { label: "최근 시그널 TOP" }],
          }]);
        }
        setLoading(false);
        return;
      }

      // Handle no results (successful API call but empty results)
      if (braveResponse.noResults) {
        const cards = latestCards(kb.cards, 3, region, targetDate);
        if (cards.length) {
          updateCtx({ lastCards: cards });
          setMsgs((prev) => [...prev, {
            role: "assistant",
            content: "해당 주제의 외부 기사를 찾지 못했어. 검색어를 바꿔보거나 내부 카드를 확인해봐.",
            cards: cards.map((c) => ({ title: c.T, subtitle: c.sub, signal: c.s, url: c.url, region: c.r, date: c.d, source: c.src, gist: c.g })),
            sourceBadge: "internal",
            suggestions: [{ label: "검색어 바꿔보기" }, { label: "관련 카드 더 보여줘" }],
          }]);
        } else {
          setMsgs((prev) => [...prev, {
            role: "assistant",
            content: "해당 주제의 외부 기사를 찾지 못했어. 검색어를 바꿔보거나 내부 카드를 확인해봐.",
            suggestions: [{ label: "오늘 핵심 카드" }, { label: "최근 시그널 TOP" }],
          }]);
        }
        setLoading(false);
        return;
      }

      // Success: display external results
      if (braveResponse.results.length) {
        const lines = braveResponse.results.map((r, i) => `${i + 1}. ${r.title}\n   ${r.description?.slice(0, 80) || ""}`).join("\n\n");
        updateCtx({ qType: "news", links: braveResponse.results, lastLinks: braveResponse.results, selected: braveResponse.results[0] });
        setMsgs((prev) => [...prev, {
          role: "assistant",
          content: `외부 기사 검색 결과야.\n\n${lines}`,
          sourceBadge: "external",
          braveLinks: braveResponse.results,
          suggestions: [{ label: "오늘 핵심 카드" }, { label: "관련 카드 더 보여줘" }, { label: "요약해서 다시 정리" }],
        }]);
      }
      setLoading(false);
      return;
    }

    // Translation request detection — show Korean gist of foreign cards
    // Note: '원문' is handled by isBraveQuery above for external search, not translation
    const isTranslateReq = /(번역|translate|통역|한국어로|영어로)/.test(txt.toLowerCase());
    if (isTranslateReq) {
      const foreignCards = kb.cards.filter((c) => c.r && c.r !== "KR").slice(0, 3);
      if (foreignCards.length) {
        depthRef.current += 1;
        const gistLines = foreignCards.map((c) => c.g ? `• ${c.T}\n  → ${c.g}` : `• ${c.T}`).join("\n\n");
        updateCtx({ qType, cards: foreignCards });
        setMsgs((prev) => [...prev, {
          role: "assistant",
          content: `최근 해외 기사의 한국어 분석이야.\n\n${gistLines}`,
          sourceBadge: "internal",
          cards: foreignCards.map((c) => ({ title: c.T, subtitle: c.sub, signal: c.s, url: c.url, region: c.r, date: c.d, source: c.src, gist: c.g })),
          suggestions: [{ label: "미국만 따로" }, { label: "중국만 따로" }, { label: "관련 카드 더 보여줘" }, { label: "조금 더 쉽게 설명해줘" }],
        }]);
        setLoading(false);
        return;
      }
    }

    // News-type requests → internal cards (latestCards with proper date ordering)
    if (qType === "news") {
      const effectiveDate = targetDate || kstToday();
      const cards = latestCards(kb.cards, 3, region, effectiveDate);
      if (cards.length) {
        updateCtx({ lastCards: cards, selected: cards[0] });
        setMsgs((prev) => [...prev, buildCardMessage(cards, "news", targetDate)]);
        setLoading(false);
        return;
      }
    }

    // Policy type: use tracker data + cards + REGION_POLICY intelligence
    if (qType === "policy") {
      const policyCards = searchCards(kb.cards, txt, 3);
      const trackerItems = tracker?.items || [];
      const upcoming = trackerItems
        .filter((i) => i.s === "UPCOMING")
        .sort((a, b) => String(a.dt || "").localeCompare(String(b.dt || "")))
        .slice(0, 5);

      // Keyword-based region inference when detectRegion didn't match
      const inferRegionFromKeywords = (t) => {
        const l = t.toLowerCase();
        if (/(feoc|ira|section\s*301|45x|북미|north\s*america)/.test(l)) return "US";
        if (/(battery\s*regulation|battery\s*passport|cbam|crm\s*act|northvolt)/.test(l)) return "EU";
        if (/(ess\s*안전|용량시장|k-배터리|전고체|리튬황|한전)/.test(l)) return "KR";
        if (/(catl|byd|흑연\s*수출|과잉설비|lfp\s*가격)/.test(l)) return "CN";
        if (/(gx|meti|축전|계통유연|전력정책.*일본)/.test(l)) return "JP";
        return null;
      };

      const effectiveRegion = region || inferRegionFromKeywords(txt);

      // Extract relevant REGION_POLICY data
      let policyOverview = "";
      let whyImportant = "";
      let watchpoints = [];

      if (effectiveRegion) {
        const regionMap = { US: "NA", KR: "KR", CN: "CN", EU: "EU", JP: "JP" };
        const policyKey = regionMap[effectiveRegion];
        const policyData = REGION_POLICY[policyKey];

        if (policyData) {
          const regionLabel = { US: "미국", KR: "한국", CN: "중국", EU: "유럽", JP: "일본" }[effectiveRegion] || effectiveRegion;

          // Build policy overview from top policies (2~4개)
          if (policyData.policies && policyData.policies.length > 0) {
            policyOverview = `📋 ${regionLabel} 정책 개요\n`;
            policyData.policies.slice(0, 3).forEach((p) => {
              policyOverview += `• ${p.name}: ${p.desc}\n`;
            });
          }

          // Add why important
          if (policyData.why) {
            whyImportant = `\n⚡ 왜 중요한지\n${policyData.why}`;
          }

          // Add watchpoints
          if (policyData.watchpoints && policyData.watchpoints.length > 0) {
            watchpoints = policyData.watchpoints;
          }
        }
      }

      let content = "";

      // If region detected: structured response (overview + why + watchpoints first, schedule after)
      if (effectiveRegion && policyOverview) {
        content = policyOverview;
        if (whyImportant) content += whyImportant;
        if (watchpoints.length > 0) {
          content += `\n\n👁️ 주요 관전 포인트\n`;
          watchpoints.forEach((w) => { content += `• ${w}\n`; });
        }
        // Add relevant upcoming schedule items for this region
        const regionTrackerKey = { US: "NA", KR: "KR", CN: "CN", EU: "EU", JP: "JP" }[effectiveRegion];
        const regionUpcoming = upcoming.filter((i) => i.r === regionTrackerKey || i.r === effectiveRegion);
        if (regionUpcoming.length) {
          content += `\n📅 다가오는 일정\n`;
          regionUpcoming.slice(0, 3).forEach((item) => {
            content += `• ${fmtDate(item.dt)} — ${item.t}\n`;
          });
        }
      } else if (!effectiveRegion) {
        // No region detected: show brief overview of all regions + region quick-select buttons
        content = "어떤 지역 정책이 궁금해? 아래에서 선택해줘.\n\n";
        const regionKeys = [{ key: "NA", label: "미국 🇺🇸" }, { key: "EU", label: "유럽 🇪🇺" }, { key: "KR", label: "한국 🇰🇷" }, { key: "CN", label: "중국 🇨🇳" }, { key: "JP", label: "일본 🇯🇵" }];
        regionKeys.forEach(({ key, label }) => {
          const pd = REGION_POLICY[key];
          if (pd) content += `${label}: ${pd.why || pd.policies?.[0]?.desc || ""}\n`;
        });

        depthRef.current += 1;
        updateCtx({ qType: "policy", region: null });
        setMsgs((prev) => [...prev, {
          role: "assistant",
          content,
          suggestions: [
            { label: "미국 정책 설명해줘" },
            { label: "EU 정책 설명해줘" },
            { label: "한국 정책 설명해줘" },
            { label: "중국 정책 설명해줘" },
          ],
        }]);
        setLoading(false);
        return;
      } else {
        // Schedule section as fallback when no structured policy data
        if (upcoming.length) {
          content = "다가오는 정책 일정을 정리했어.\n\n";
          upcoming.forEach((item) => {
            const rName = TRACKER_REGION[item.r]?.name || item.r || "";
            content += `📅 ${fmtDate(item.dt)} — ${item.t} (${rName})\n`;
          });
        }
      }

      if (policyCards.length) {
        if (!content) content = "관련 정책 카드를 찾았어.\n";
        depthRef.current += 1;
        updateCtx({ qType: "policy", cards: policyCards, region: effectiveRegion, lastCards: policyCards });
        setMsgs((prev) => [...prev, {
          role: "assistant",
          content: content + "\n\n📰 관련 카드",
          cards: policyCards.map((c) => ({ title: c.T, subtitle: c.sub, signal: c.s, url: c.url, region: c.r, date: c.d, source: c.src, gist: c.g })),
          suggestions: makeSuggestions("policy"),
        }]);
        setLoading(false);
        return;
      }
      if (content) {
        depthRef.current += 1;
        updateCtx({ qType: "policy", region: effectiveRegion });
        setMsgs((prev) => [...prev, { role: "assistant", content, suggestions: makeSuggestions("policy") }]);
        setLoading(false);
        return;
      }
    }

    // Summary type: format as 3-line summary with card links
    if (qType === "summary") {
      const cardHits = searchCards(kb.cards, txt, 3);
      if (cardHits.length) {
        updateCtx({ lastCards: cardHits, selected: cardHits[0] });
        setMsgs((prev) => [...prev, buildCardMessage(cardHits, "summary", targetDate)]);
        setLoading(false);
        return;
      }
    }

    // Compare type: search and format comparison
    if (qType === "compare") {
      const cardHits = searchCards(kb.cards, txt, 4);
      if (cardHits.length) {
        updateCtx({ lastCards: cardHits, selected: cardHits[0] });
        setMsgs((prev) => [...prev, buildCardMessage(cardHits, "compare", targetDate)]);
        setLoading(false);
        return;
      }
    }

    // General card search
    const cardHits = searchCards(kb.cards, txt, 4);
    if (cardHits.length) {
      updateCtx({ lastCards: cardHits, selected: cardHits[0] });
      setMsgs((prev) => [...prev, buildCardMessage(cardHits, qType, targetDate)]);
      setLoading(false);
      return;
    }

    depthRef.current += 1;
    setMsgs((prev) => [...prev, { role: "assistant", content: "딱 맞는 결과가 바로 안 잡혔어.\n\n주제를 조금 더 짧게 보내보자. 예: LFP 리스크 / 오늘 핵심 뉴스 / 한국 정책 일정", suggestions: makeSuggestions(qType) }]);
    setLoading(false);
  };

  const runSuggestion = (label) => {
    if (label === "외부 기사로 전환 →") { setSearchMode("external"); return; }
    if (label === "내부 카드로 검색") { setSearchMode("internal"); return; }
    const map = {
      "오늘 핵심 카드": "오늘 뉴스 3개",
      "오늘의 시그널 TOP": "오늘 TOP 시그널 카드 보여줘",
      "외부 기사 링크 검색": "실시간 배터리 ESS 기사 검색해줘",
      "오늘 핵심 뉴스 3개": "오늘 뉴스 3개",
      "오늘 뉴스 3개": "오늘 뉴스 3개",
      "요약해서 다시 정리": "방금 답변을 3줄로 다시 요약해줘",
      "카드에서도 찾아봐": "방금 주제와 관련된 카드도 같이 찾아줘",
      "조금 더 쉽게 설명해줘": "방금 답변을 더 쉽게 설명해줘",
      "관련 카드 더 보여줘": "방금 주제와 관련된 카드 더 보여줘",
      "정책 일정만 따로 정리해줘": "방금 주제와 관련된 정책 일정만 따로 정리해줘",
      "한국 뉴스만": "오늘 한국 뉴스 3개",
      "미국 뉴스만": "오늘 미국 뉴스 3개",
      "다가오는 일정만": "다가오는 정책 일정만 정리해줘",
      "한국/EU 비교": "한국과 EU 정책을 비교해줘",
      "실무 영향만 요약": "실무 영향만 요약해줘",
      "한 줄 결론만": "한 줄 결론만 말해줘",
      "오늘 기준으로 다시": "오늘 기준 뉴스 3개",
      "미국만 따로": "미국 뉴스 3개",
      "중국만 따로": "중국 뉴스 3개",
      "쉽게 비유해서 설명": "방금 주제를 쉽게 비유해서 설명해줘",
      "LFP랑 비교": "방금 주제를 LFP와 비교해줘",
      "왜 중요한지 한 줄로": "방금 주제가 왜 중요한지 한 줄로 설명해줘",
    };
    const next = map[label] || label;
    void sendWithText(next);
  };

  const sendExternal = async (rawText) => {
    const txt = String(rawText || "").trim();
    if (!txt || loading) return;
    setLoading(true);
    setExtQuery("");
    setMsgs((prev) => [...prev, { role: "user", content: `🔗 외부 검색: ${txt}` }]);
    const braveResponse = await fetchBraveResults(txt);
    depthRef.current += 1;
    if (braveResponse.error) {
      const errorMessages = {
        UNAUTHORIZED: "⚠️ 외부 검색 API 인증에 문제가 있어. 관리자에게 확인이 필요해.",
        FORBIDDEN: "⚠️ 외부 검색 API 인증에 문제가 있어. 관리자에게 확인이 필요해.",
        RATE_LIMIT: "⚠️ 외부 검색 요청이 많아서 잠시 제한됐어. 잠시 후 다시 시도해봐.",
        SERVER_ERROR: "⚠️ 외부 검색 서버에 일시적인 문제가 있어.",
        NETWORK_ERROR: "⚠️ 외부 검색 서비스에 연결할 수 없어.",
      };
      setMsgs((prev) => [...prev, { role: "assistant", content: errorMessages[braveResponse.errorType] || "⚠️ 외부 검색 중 문제가 발생했어.", suggestions: [{ label: "내부 카드로 검색" }] }]);
      setLoading(false);
      return;
    }
    if (braveResponse.noResults || !braveResponse.results?.length) {
      setMsgs((prev) => [...prev, { role: "assistant", content: "해당 주제의 외부 기사를 찾지 못했어. 검색어를 바꿔보거나 내부 카드를 확인해봐.", suggestions: [{ label: "내부 카드로 검색" }] }]);
      setLoading(false);
      return;
    }
    const lines = braveResponse.results.map((r, i) => `${i + 1}. ${r.title}\n   ${r.description?.slice(0, 80) || ""}`).join("\n\n");
    updateCtx({ qType: "news", links: braveResponse.results, lastLinks: braveResponse.results, selected: braveResponse.results[0] });
    setMsgs((prev) => [...prev, {
      role: "assistant",
      content: `외부 기사 검색 결과야.\n\n${lines}`,
      sourceBadge: "external",
      braveLinks: braveResponse.results,
      suggestions: [{ label: "오늘 핵심 카드" }, { label: "관련 카드 더 보여줘" }, { label: "요약해서 다시 정리" }],
    }]);
    setLoading(false);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "calc(100vh - 190px)" }}>
      <div style={{ flex: 1, overflowY: "auto", padding: "12px 14px 8px" }}>
        {msgs.length <= 1 && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginTop: 6, marginBottom: 12 }}>
            {quickPrimary.map((q) => (
              <button key={q} onClick={() => runSuggestion(q)} style={{ background: dark ? "#1A2333" : "#FFFFFF", border: `1px solid ${t.brd}`, borderRadius: 999, padding: "8px 12px", fontSize: 12, color: t.tx, cursor: "pointer", fontFamily: "'Pretendard',sans-serif", fontWeight: 600, textAlign: "left" }}>{q}</button>
            ))}
          </div>
        )}

        {msgs.map((m, i) => (
          <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: m.role === "user" ? "flex-end" : "flex-start", marginBottom: 10 }}>
            <div style={{ display: "flex", justifyContent: m.role === "user" ? "flex-end" : "flex-start", width: "100%" }}>
              {m.role === "assistant" && <img src="/data/kang.png" alt="강차장" style={{ width: 28, height: 28, borderRadius: 14, marginRight: 7, flexShrink: 0, marginTop: 2, border: "2px solid #2a1a40" }} />}
              <div style={{ maxWidth: "88%" }}>
                <div style={{ padding: "11px 14px", fontSize: 13, lineHeight: 1.6, whiteSpace: "pre-wrap", wordBreak: "keep-all", borderRadius: m.role === "user" ? "18px 18px 6px 18px" : "18px 18px 18px 6px", background: m.role === "user" ? "#4C8DFF" : (dark ? "#1A2333" : "#FFFFFF"), color: m.role === "user" ? "#fff" : t.tx, border: m.role === "user" ? "none" : `1px solid ${t.brd}`, fontFamily: "'Pretendard', sans-serif" }}>
                  {m.sourceBadge === "internal" && (
                    <span style={{ display: "inline-block", fontSize: 10, fontWeight: 800, color: "#58A6FF", background: dark ? "rgba(88,166,255,0.14)" : "rgba(45,90,142,0.10)", padding: "3px 8px", borderRadius: 999, marginBottom: 6, fontFamily: "'JetBrains Mono',monospace" }}>
                      📋 내부 카드 기반
                    </span>
                  )}
                  {m.sourceBadge === "external" && (
                    <span style={{ display: "inline-block", fontSize: 10, fontWeight: 800, color: "#D29922", background: dark ? "rgba(210,153,34,0.14)" : "rgba(210,153,34,0.10)", padding: "3px 8px", borderRadius: 999, marginBottom: 6, fontFamily: "'JetBrains Mono',monospace" }}>
                      🔗 외부 기사 링크
                    </span>
                  )}
                  {m.sourceBadge ? <div>{m.content}</div> : m.content}
                </div>
                {m.braveLinks?.map((link, j) => (
                  <a key={`brave-${j}`} href={link.url} target="_blank" rel="noopener noreferrer" aria-label={`Open external article: ${link.title}`} style={{ display: "block", background: dark ? "#1A1E2A" : "#FFFBF0", borderRadius: 10, padding: "10px 12px", marginTop: 6, cursor: "pointer", border: `1px solid ${dark ? "rgba(210,153,34,0.25)" : "rgba(210,153,34,0.2)"}`, textDecoration: "none" }}>
                    <div style={{ fontSize: 12, fontWeight: 700, color: t.tx, lineHeight: 1.4 }}>{link.title}</div>
                    {link.description && <div style={{ fontSize: 11, color: t.sub, marginTop: 3, lineHeight: 1.45 }}>{link.description.slice(0, 120)}{link.description.length > 120 ? "..." : ""}</div>}
                    <div style={{ fontSize: 10, color: "#D29922", marginTop: 4, fontWeight: 700, fontFamily: "'JetBrains Mono',monospace" }}>🔗 외부 기사 ↗</div>
                  </a>
                ))}
                {m.cards?.map((card, j) => {
                  const cardStyle = { display: "block", background: dark ? "#151B26" : "#f8f9fc", borderRadius: 10, padding: "10px 12px", marginTop: 6, cursor: card.url ? "pointer" : "default", border: `1px solid ${t.brd}`, textDecoration: "none" };
                  const cardContent = (<>
                    <div style={{ fontSize: 12, fontWeight: 700, color: t.tx }}>{SIG_L[card.signal] || "INFO"} {card.title}</div>
                    {card.subtitle && <div style={{ fontSize: 11, color: t.sub, marginTop: 3 }}>{card.subtitle}</div>}
                    {card.gist && <div style={{ fontSize: 10, color: t.cyan, marginTop: 4, lineHeight: 1.5, opacity: 0.85 }}>💡 {card.gist}</div>}
                    <div style={{ fontSize: 10, color: t.sub, marginTop: 4, fontFamily: "'JetBrains Mono',monospace" }}>{fmtDate(card.date)} · {card.region} · {card.source || "source"}</div>
                    {card.url && <div style={{ fontSize: 10, color: t.cyan, marginTop: 4, fontWeight: 700 }}>→ 원문 보기 ↗</div>}
                  </>);
                  return card.url
                    ? <a key={j} href={card.url} target="_blank" rel="noopener noreferrer" aria-label={`Open article: ${card.title}`} style={cardStyle}>{cardContent}</a>
                    : <div key={j} style={cardStyle}>{cardContent}</div>;
                })}
              </div>
            </div>
            {m.role === "assistant" && m.suggestions?.length > 0 && (
              <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 8, marginBottom: 4, paddingLeft: 35 }}>
                {m.suggestions.map((s) => (
                  <button key={s.label} onClick={() => runSuggestion(s.label)} style={{ background: dark ? "#1A2333" : "#fff", border: `1px solid ${t.brd}`, borderRadius: 999, padding: "6px 12px", fontSize: 11, color: t.cyan, cursor: "pointer", fontFamily: "'Pretendard',sans-serif", fontWeight: 600 }}>{s.label}</button>
                ))}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div style={{ display: "flex", gap: 7, marginBottom: 10 }}>
            <img src="/data/kang.png" alt="강차장" style={{ width: 28, height: 28, borderRadius: 14, flexShrink: 0, border: "2px solid #2a1a40" }} />
            <div style={{ padding: "10px 14px", borderRadius: "18px 18px 18px 6px", background: dark ? "#1A2333" : "#FFFFFF", border: `1px solid ${t.brd}`, fontSize: 12, color: t.sub }}>찾아보는 중...</div>
          </div>
        )}
        <div ref={endRef} />
      </div>
      <div style={{ padding: "8px 12px 14px", background: "#0A0E14", borderTop: `1px solid ${t.brd}` }}>
        {/* Mode segmented control */}
        <div style={{ display: "flex", gap: 0, marginBottom: 8, background: dark ? "#151B26" : "#f0f0f5", borderRadius: 8, padding: 2 }}>
          <button onClick={() => setSearchMode("internal")} style={{ flex: 1, padding: "6px 0", borderRadius: 6, border: "none", background: searchMode === "internal" ? (dark ? "#1A2333" : "#fff") : "transparent", color: searchMode === "internal" ? "#58A6FF" : t.sub, fontSize: 11, fontWeight: 700, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace", boxShadow: searchMode === "internal" ? "0 1px 3px rgba(0,0,0,0.15)" : "none", transition: "all 0.15s" }}>📋 내부 카드</button>
          <button onClick={() => setSearchMode("external")} style={{ flex: 1, padding: "6px 0", borderRadius: 6, border: "none", background: searchMode === "external" ? (dark ? "#1A2333" : "#fff") : "transparent", color: searchMode === "external" ? "#D29922" : t.sub, fontSize: 11, fontWeight: 700, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace", boxShadow: searchMode === "external" ? "0 1px 3px rgba(0,0,0,0.15)" : "none", transition: "all 0.15s" }}>🔗 외부 기사</button>
        </div>
        {/* External search dedicated row */}
        {searchMode === "external" && (
          <div style={{ display: "flex", gap: 6, marginBottom: 6 }}>
            <input type="text" value={extQuery} onChange={(e) => setExtQuery(e.target.value)} onKeyDown={(e) => e.key === "Enter" && void sendExternal(extQuery)} placeholder="외부 기사 검색어 입력 (예: LFP 화재 리스크)" style={{ flex: 1, padding: "8px 10px", borderRadius: 8, border: `1px solid ${dark ? "rgba(210,153,34,0.3)" : "rgba(210,153,34,0.2)"}`, background: dark ? "#1A1E2A" : "#FFFBF0", color: t.tx, fontSize: 12, outline: "none", fontFamily: "'Pretendard',sans-serif" }} />
            <button onClick={() => void sendExternal(extQuery)} disabled={loading || !extQuery.trim()} style={{ padding: "8px 12px", borderRadius: 8, border: "none", background: "#D29922", color: "#000", fontWeight: 800, cursor: "pointer", fontSize: 12, fontFamily: "'Pretendard',sans-serif" }}>🔍</button>
          </div>
        )}
        {/* Main chat input */}
        <div style={{ display: "flex", gap: 6 }}>
          <input type="text" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && void sendWithText(input)} placeholder={searchMode === "internal" ? "궁금한 주제를 입력해줘" : "AI에게 질문하기"} style={{ flex: 1, padding: "10px 12px", borderRadius: 10, border: `1px solid ${t.brd}`, background: t.card2, color: t.tx, fontSize: 13, outline: "none", fontFamily: "'Pretendard',sans-serif" }} />
          <button onClick={() => void sendWithText(input)} disabled={loading || !input.trim()} style={{ padding: "10px 16px", borderRadius: 10, border: "none", background: t.cyan, color: "#000", fontWeight: 800, cursor: "pointer", fontSize: 13, fontFamily: "'Pretendard',sans-serif" }}>→</button>
        </div>
      </div>
    </div>
  );
}

const REGION_POLICY = {
  NA: {
    title: "미국 정책",
    flag: "🇺🇸",
    policies: [
      { name: "IRA / FEOC", desc: "IRA §45X·§48E 제조·투자 세액공제 — FEOC 규정으로 중국산 배터리·소재 사용 시 크레딧 박탈. MACR 55% 기준(2026) 적용 중." },
      { name: "관세 (Section 301)", desc: "대중국 배터리셀 관세 54~58%. BOS 부품에도 §232 관세 50% 별도 → 실질 80%+ 차단벽." },
      { name: "제조 인센티브", desc: "45X 첨단제조 크레딧으로 미국 내 셀·모듈·광물 가공 공장 유치. 2030년 MACR 85% 목표." },
      { name: "ESS / 전력", desc: "ITC(§48E) standalone ESS 30~50% + 커뮤니티 보너스. FERC Order 2222로 분산자원 시장참여 확대." },
    ],
    why: "미국 에너지 전환 정책은 K-배터리에 기회이자 리스크 — FEOC 준수 여부가 시장 접근 자체를 결정한다.",
    watchpoints: ["Treasury proposed regulation Q2 발표 여부", "Section 301 관세 8월 만료·연장 결정", "45X MACR 2027 기준 60% 전환 대비"],
  },
  EU: {
    title: "유럽 정책",
    flag: "🇪🇺",
    policies: [
      { name: "Battery Regulation", desc: "2027년부터 배터리 여권(Battery Passport) 의무화. 탄소발자국 등급 공개, 재활용률 의무 부과." },
      { name: "CBAM", desc: "탄소국경조정메커니즘 — 수입품에 EU 탄소가격 부과. 배터리 소재·철강·알루미늄 대상." },
      { name: "CRM Act", desc: "핵심원자재법 — 리튬·코발트·니켈 등 전략광물 EU 내 가공 40%, 재활용 25% 목표." },
      { name: "보조금", desc: "IPCEI 배터리 프로젝트 + 각국 개별 보조금. Northvolt 사태 이후 보조금 심사 강화 추세." },
    ],
    why: "EU는 규제 중심 접근 — 규정 준수 비용이 시장 진입 장벽이 되므로 조기 대응이 핵심이다.",
    watchpoints: ["Battery Passport 파일럿 일정", "CBAM 전환기 종료(2026.12) 이후 본 부과 시작", "CRM Act 광물 목록 업데이트"],
  },
  CN: {
    title: "중국 정책",
    flag: "🇨🇳",
    policies: [
      { name: "산업정책", desc: "국가 차원 배터리 산업 육성. CATL·BYD 등 대형사 보조금·세제 혜택. 내수 EV 보급 세계 1위 유지." },
      { name: "공급망 통제", desc: "흑연·리튬·희토류 수출 통제 강화. 가공 단계 독점적 지위를 지렛대로 활용." },
      { name: "가격 경쟁", desc: "LFP 셀 가격 $50/kWh 이하 진입. 과잉설비 기반 저가 공세로 글로벌 시장 점유율 확대." },
      { name: "수출 전략", desc: "BESS 수출 급증 — 미국 관세 우회 위해 모로코·헝가리 등 제3국 가공기지 확대." },
    ],
    why: "중국은 가격과 공급망을 동시에 장악 — 비중국 플레이어의 생존 전략 수립에 가장 큰 변수다.",
    watchpoints: ["흑연 수출허가제 실제 운용 강도", "LFP 과잉설비 조정 신호", "제3국 우회 수출 규모 추이"],
  },
  KR: {
    title: "한국 정책",
    flag: "🇰🇷",
    policies: [
      { name: "ESS 정책", desc: "산업부 ESS 안전기준 개정 + 대규모 ESS 실증사업. 화재 안전 인증 강화." },
      { name: "입찰 / 조달", desc: "한전 ESS 용량시장 입찰. 재생에너지 연계 ESS 의무화 확대." },
      { name: "실증 / R&D", desc: "전고체·리튬황 차세대 배터리 국가 R&D. K-배터리 2030 로드맵 추진." },
      { name: "규제 방향", desc: "EU Battery Regulation 대응 — 배터리 여권 국내 도입 검토. 재활용 의무 강화 로드맵." },
    ],
    why: "K-배터리의 본거지 — 내수 ESS 시장 성장과 수출 규제 대응을 동시에 준비해야 한다.",
    watchpoints: ["ESS 안전기준 개정안 시행 시점", "용량시장 ESS 입찰 결과", "배터리 여권 국내 적용 로드맵 발표"],
  },
  JP: {
    title: "일본 정책",
    flag: "🇯🇵",
    policies: [
      { name: "GX (Green Transformation)", desc: "GX 추진법 기반 20조엔 투자. 배터리·수소·원자력 포함한 에너지 전환 가속." },
      { name: "배터리 지원", desc: "METI 대규모 축전시스템 보조금 (보조율 33~66%). 도쿄도 별도 20억엔 지원." },
      { name: "전력정책", desc: "재생에너지 주력전원화 + 계통유연성 확보. ESS를 조정력 수단으로 본격 활용." },
    ],
    why: "일본은 에너지 안보 관점에서 ESS를 전략자산화 — 보조금 규모가 시장 형성 속도를 결정한다.",
    watchpoints: ["METI 축전 보조금 2차 공모 시기", "GX 채권 발행·집행 진도", "계통용 ESS 접속 규칙 개정"],
  },
  GL: {
    title: "글로벌 공통",
    flag: "🌐",
    policies: [
      { name: "공급망 재편", desc: "미·중 디커플링 가속. 중간재 가공 거점이 동남아·중동·아프리카로 분산." },
      { name: "광물 확보 경쟁", desc: "리튬·니켈·코발트·흑연 확보전. 자원국 수출 규제 확대 추세." },
    ],
    why: "글로벌 밸류체인 재편은 모든 지역 정책의 배경이 된다 — 공급망 지도가 바뀌고 있다.",
    watchpoints: ["인도네시아 니켈 수출 정책 변화", "칠레·아르헨티나 리튬 국유화 동향"],
  },
};

function Tracker({ tracker, dark }) {
  const t = T(dark);
  const d = tracker;
  const updatedLabel = fmtDate(d.meta.lastUpdated);
  const [expandedRegion, setExpandedRegion] = useState(null);

  const toggleRegion = (code) => {
    setExpandedRegion((prev) => (prev === code ? null : code));
  };

  const policyData = REGION_POLICY[expandedRegion] || null;

  return (
    <div style={{ padding: "0 14px 110px", display: "flex", flexDirection: "column", gap: 12 }}>
      <div style={{ background: t.card2, borderRadius: 10, padding: 14, border: `1px solid ${t.brd}` }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 10, marginBottom: 10 }}>
          <div>
            <div style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>STATUS</div>
            <div style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginTop: 4 }}>LAST CHECKED {updatedLabel}</div>
          </div>
          <span style={{ background: t.brd, borderRadius: 4, padding: "3px 10px", fontSize: 12, fontWeight: 800, color: t.tx, fontFamily: "'JetBrains Mono',monospace" }}>{d.meta.totalItems}</span>
        </div>
        <div style={{ display: "flex", gap: 5 }}>
          {Object.entries(d.summary).map(([s, n]) => (
            <div key={s} style={{ flex: 1, background: t.bg, borderRadius: 6, padding: "8px 6px", textAlign: "center" }}>
              <div style={{ fontSize: 16, fontWeight: 900, color: SC[s] || t.tx }}>{n}</div>
              <div style={{ fontSize: 8, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginTop: 2 }}>{SL[s] || s}</div>
            </div>
          ))}
        </div>
      </div>

      <div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}><span style={{ fontSize: 10, color: "#3a6090", fontFamily: "'JetBrains Mono',monospace" }}>REGIONS — 클릭하면 정책 설명</span><div style={{ flex: 1, height: 1, background: t.brd }} /></div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
          {d.regions.map((r) => {
            const isExpanded = expandedRegion === r.code;
            return (
              <div key={r.code} onClick={() => toggleRegion(r.code)} style={{ background: isExpanded ? (dark ? "#1A2333" : "#EEF3FF") : t.card2, borderRadius: 8, padding: "10px 12px", border: `1px solid ${isExpanded ? t.cyan : t.brd}`, cursor: "pointer", transition: "border 0.2s" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}><span style={{ fontSize: 14 }}>{r.flag}</span><span style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>{r.ACTIVE} ACTIVE</span></div>
                <div style={{ fontSize: 13, fontWeight: 700, color: t.tx, marginTop: 4 }}>{r.name}</div>
                <div style={{ marginTop: 6, height: 3, borderRadius: 2, background: t.brd }}><div style={{ height: "100%", borderRadius: 2, background: SC.ACTIVE, width: pct(r.ACTIVE, r.total) }} /></div>
                <div style={{ fontSize: 9, color: isExpanded ? t.cyan : t.sub, marginTop: 4, fontFamily: "'JetBrains Mono',monospace", textAlign: "center" }}>{isExpanded ? "△ 접기" : "▽ 정책 보기"}</div>
              </div>
            );
          })}
        </div>
      </div>

      {policyData && (
        <div style={{ background: t.card2, borderRadius: 12, padding: "14px 16px", border: `1px solid ${t.cyan}`, animation: "fadeIn 0.2s ease" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
            <span style={{ fontSize: 18 }}>{policyData.flag}</span>
            <span style={{ fontSize: 14, fontWeight: 900, color: t.tx }}>{policyData.title}</span>
            <button onClick={() => setExpandedRegion(null)} style={{ marginLeft: "auto", background: "transparent", border: `1px solid ${t.brd}`, borderRadius: 999, padding: "2px 8px", fontSize: 9, color: t.sub, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>닫기</button>
          </div>
          {policyData.policies.map((p, i) => (
            <div key={i} style={{ marginBottom: 10, padding: "8px 10px", background: dark ? "rgba(88,166,255,0.04)" : "rgba(88,166,255,0.02)", borderRadius: 8, border: `1px solid ${dark ? "rgba(88,166,255,0.08)" : "rgba(88,166,255,0.06)"}` }}>
              <div style={{ fontSize: 11, fontWeight: 800, color: t.cyan, marginBottom: 3, fontFamily: "'JetBrains Mono',monospace" }}>{p.name}</div>
              <div style={{ fontSize: 11, color: t.tx, lineHeight: 1.55 }}>{p.desc}</div>
            </div>
          ))}
          <div style={{ marginTop: 6, padding: "8px 10px", background: dark ? "rgba(210,153,34,0.06)" : "rgba(210,153,34,0.04)", borderRadius: 8, border: `1px solid ${dark ? "rgba(210,153,34,0.12)" : "rgba(210,153,34,0.08)"}` }}>
            <div style={{ fontSize: 10, fontWeight: 800, color: "#D29922", marginBottom: 3, fontFamily: "'JetBrains Mono',monospace" }}>⚡ 왜 중요한지</div>
            <div style={{ fontSize: 11, color: t.tx, lineHeight: 1.55 }}>{policyData.why}</div>
          </div>
          <div style={{ marginTop: 8 }}>
            <div style={{ fontSize: 10, fontWeight: 800, color: t.sub, marginBottom: 4, fontFamily: "'JetBrains Mono',monospace" }}>👁 WATCHPOINTS</div>
            {policyData.watchpoints.map((wp, i) => (
              <div key={i} style={{ fontSize: 11, color: t.tx, lineHeight: 1.55, paddingLeft: 8, borderLeft: `2px solid ${t.cyan}`, marginBottom: 4 }}>{wp}</div>
            ))}
          </div>
        </div>
      )}

      <div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}><span style={{ fontSize: 10, color: "#3a6090", fontFamily: "'JetBrains Mono',monospace" }}>KEY DATES</span><div style={{ flex: 1, height: 1, background: t.brd }} /></div>
        <div style={{ background: t.card2, borderRadius: 8, padding: "4px 0", border: `1px solid ${t.brd}` }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 12px 6px", borderBottom: `1px solid ${t.brd}` }}>
            <span style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>WATCHLIST</span>
            <span style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>LAST CHECKED {updatedLabel}</span>
          </div>
          {d.upcoming.map((ev, i) => (
            <div key={i} style={{ padding: "8px 12px", display: "flex", alignItems: "center", gap: 8, borderTop: i > 0 ? `1px solid ${t.brd}` : "none" }}>
              <span style={{ width: 72, fontSize: 10, fontWeight: 700, color: t.sub, fontFamily: "'JetBrains Mono',monospace", flexShrink: 0, lineHeight: 1.35, whiteSpace: "normal", wordBreak: "keep-all" }}>{ev.date}</span>
              <span style={{ flex: 1, fontSize: 12, fontWeight: 700, color: t.tx, lineHeight: 1.45 }}>{ev.title}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function SeriesActionButton({ label, onClick, primary = false, dark }) {
  const t = T(dark);
  return <button onClick={onClick} style={{ flex: 1, border: primary ? "none" : `1px solid ${t.brd}`, borderRadius: 10, padding: "10px 14px", background: primary ? t.cyan : "transparent", color: primary ? "#000" : t.tx, fontSize: 11, fontWeight: 800, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>{label}</button>;
}

function EpisodeCard({ item, dark }) {
  const t = T(dark);
  return (
    <div onClick={() => item.url && window.open(item.url, "_blank")} style={{ background: t.card2, borderRadius: 10, padding: "12px 14px", border: `1px solid ${t.brd}`, cursor: item.url ? "pointer" : "default" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6, flexWrap: "wrap" }}>
        <span style={{ fontSize: 10, color: t.sub }}>🎨 웹툰</span>
        {item.tag && <SmallPill label={item.tag} dark={dark} />}
        {item.isNew && <span style={{ fontSize: 8, fontWeight: 800, color: "#000", background: t.cyan, padding: "2px 6px", borderRadius: 999, fontFamily: "'JetBrains Mono',monospace" }}>NEW</span>}
      </div>
      <h3 style={{ fontSize: 14, fontWeight: 800, color: t.tx, margin: "0 0 4px", lineHeight: 1.35 }}>{item.title}</h3>
      <p style={{ fontSize: 11, color: t.sub, margin: 0, lineHeight: 1.5 }}>{item.subtitle}</p>
      <div style={{ display: "flex", gap: 10, fontSize: 10, color: t.sub, marginTop: 8, fontFamily: "'JetBrains Mono',monospace" }}><span>{item.date}</span>{item.url && <span>OPEN ↗</span>}</div>
    </div>
  );
}

function CollectionFolder({ collection, dark, defaultOpen = false }) {
  const t = T(dark);
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div style={{ background: t.card2, borderRadius: 16, border: `1px solid ${t.brd}`, overflow: "hidden" }}>
      <div style={{ height: 4, background: `linear-gradient(90deg,${collection.color},${collection.color}66)` }} />
      <div style={{ padding: 16 }}>
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 12 }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap", marginBottom: 6 }}>
              <SmallPill label={collection.badge} dark={dark} />
              <span style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>{collection.items.length} EPISODES</span>
            </div>
            <h3 style={{ fontSize: 20, fontWeight: 900, color: t.tx, margin: "0 0 6px", lineHeight: 1.28 }}>{collection.title}</h3>
            <p style={{ fontSize: 12, color: t.sub, margin: 0, lineHeight: 1.58 }}>{collection.subtitle}</p>
            <p style={{ fontSize: 11, color: t.sub, opacity: 0.95, margin: "8px 0 0", lineHeight: 1.55 }}>{collection.description}</p>
          </div>
          <button onClick={() => setOpen((v) => !v)} style={{ border: "none", background: "transparent", color: t.sub, cursor: "pointer", fontSize: 18, paddingTop: 6 }}>{open ? "▾" : "▸"}</button>
        </div>
        <div style={{ display: "flex", gap: 8, marginTop: 14 }}>
          <SeriesActionButton label="시리즈 소개 보기 ↗" onClick={() => window.open(collection.landingUrl, "_blank")} primary dark={dark} />
          <SeriesActionButton label="EP.1 시작 ↗" onClick={() => window.open(collection.items[0].url, "_blank")} dark={dark} />
        </div>
      </div>
      {open && <div style={{ padding: "0 16px 16px", display: "flex", flexDirection: "column", gap: 10 }}>{collection.items.map((item) => <EpisodeCard key={item.id} item={item} dark={dark} />)}</div>}
    </div>
  );
}

function WebtoonLibrary({ dark }) {
  const t = T(dark);
  const featured = WEBTOON_COLLECTIONS[0];
  return (
    <div style={{ padding: "10px 14px 110px", display: "flex", flexDirection: "column", gap: 12 }}>
      <div style={{ background: `linear-gradient(135deg, ${dark ? "#151B2B" : "#ffffff"}, ${dark ? "#232D47" : "#EEF3FF"})`, borderRadius: 16, padding: "18px 16px", border: `1px solid ${dark ? "#2C3550" : t.brd}` }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap", marginBottom: 8 }}>
          <SmallPill label="FEATURED SERIES" dark={dark} />
          <span style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>{featured.status}</span>
        </div>
        <h2 style={{ fontSize: 22, fontWeight: 900, color: t.tx, margin: "0 0 6px", lineHeight: 1.25 }}>{featured.title}</h2>
        <p style={{ fontSize: 12, color: t.sub, margin: 0, lineHeight: 1.62 }}>{featured.hook}</p>
      </div>
      <div style={{ background: t.card2, borderRadius: 12, padding: "14px 16px", border: `1px solid ${t.brd}` }}>
        <div style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginBottom: 4 }}>WEBTOON LIBRARY</div>
        <h2 style={{ fontSize: 18, fontWeight: 900, color: t.tx, margin: 0 }}>웹툰 라이브러리</h2>
        <p style={{ fontSize: 12, color: t.sub, lineHeight: 1.6, margin: "8px 0 0" }}>공개된 웹툰을 시리즈 단위로 정리한 아카이브입니다. 같은 주제의 회차를 한곳에서 순서대로 확인할 수 있습니다.</p>
      </div>
      {WEBTOON_COLLECTIONS.map((collection, idx) => <CollectionFolder key={collection.id} collection={collection} dark={dark} defaultOpen={idx === 0} />)}
    </div>
  );
}

function NewsDesk({ kb, dark }) {
  const t = T(dark);
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [showCount, setShowCount] = useState(60);
  const regions = ["all", "top", "high", "KR", "US", "CN", "EU", "JP"];
  let cards = filter === "all" ? kb.cards : filter === "top" ? kb.cards.filter((c) => c.s === "t") : filter === "high" ? kb.cards.filter((c) => c.s === "h") : kb.cards.filter((c) => c.r === filter);
  if (search) {
    const sw = search.toLowerCase();
    cards = cards.filter((c) => String(c.T || "").toLowerCase().includes(sw) || String(c.sub || "").toLowerCase().includes(sw) || String(c.g || "").toLowerCase().includes(sw));
  }
  const visible = cards.slice(0, showCount);
  const dates = [...new Set(visible.map((c) => c.d))];
  const highlights = latestCards(kb.cards, 4);
  return (
    <div style={{ padding: "0 14px 110px", display: "flex", flexDirection: "column", gap: 12 }}>
      <div style={{ background: t.card2, borderRadius: 14, padding: 16, border: `1px solid ${t.brd}` }}>
        <h2 style={{ fontSize: 22, fontWeight: 900, color: t.tx, margin: "0 0 6px", lineHeight: 1.25 }}>날짜별 시그널 피드</h2>
        <p style={{ fontSize: 12, color: t.sub, margin: 0, lineHeight: 1.6 }}>최신 카드부터 날짜 기준으로 정렬했습니다. 같은 날짜 안에서는 중요도가 높은 이슈를 먼저 보여줍니다.</p>
      </div>
      <div style={{ background: t.card2, borderRadius: 14, padding: 16, border: `1px solid ${t.brd}` }}>
        <div style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginBottom: 4 }}>EDITOR'S PICKS</div>
        <h3 style={{ fontSize: 18, fontWeight: 900, color: t.tx, margin: "0 0 12px" }}>오늘의 핵심 카드</h3>
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>{highlights.map((card, i) => <NewsItem key={`${card.T}-${i}`} card={card} dark={dark} />)}</div>
      </div>
      <div>
        <input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="🔍 카드 검색..." style={{ width: "100%", padding: "10px 14px", borderRadius: 10, border: `1px solid ${t.brd}`, fontSize: 12, outline: "none", fontFamily: "inherit", background: t.card2, color: t.tx, boxSizing: "border-box" }} />
      </div>
      <div style={{ display: "flex", gap: 4, overflowX: "auto", paddingBottom: 4 }}>
        {regions.map((r) => {
          const label = r === "all" ? `ALL ${kb.cardCount}` : r === "top" ? "TOP" : r === "high" ? "HIGH" : r;
          return <button key={r} onClick={() => { setFilter(r); setShowCount(60); }} style={{ background: filter === r ? t.cyan : t.card2, color: filter === r ? "#000" : t.sub, border: `1px solid ${filter === r ? "transparent" : t.brd}`, borderRadius: 999, padding: "6px 10px", fontSize: 10, fontWeight: 700, cursor: "pointer", whiteSpace: "nowrap", fontFamily: "'JetBrains Mono',monospace" }}>{label}</button>;
        })}
      </div>
      {dates.map((date) => (
        <div key={date}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}><span style={{ fontSize: 10, color: "#3a6090", fontFamily: "'JetBrains Mono',monospace" }}>{fmtDate(date)}</span><div style={{ flex: 1, height: 1, background: t.brd }} /></div>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>{visible.filter((c) => c.d === date).map((card, i) => <NewsItem key={`${date}-${i}`} card={card} dark={dark} />)}</div>
        </div>
      ))}
    </div>
  );
}

export default function App() {
  const [tab, setTab] = useState("all");
  const [dark, setDark] = useState(true);
  const kb = useKnowledgeBase();
  const { tracker, loading: trackerLoading } = useTrackerData();
  const t = T(dark);
  const lastCardDate = latestDate(kb.cards) || "-";

  if (kb.loading || trackerLoading) {
    return <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "100vh", background: t.bg, color: t.sub }}>Loading...</div>;
  }

  const headerTitle = { news: "날짜별 시그널 피드", tracker: "Policy Tracker", chatbot: "강차장의 배터리 상담소", webtoon: "웹툰 라이브러리" }[tab];
  const headerSub = {
    news: `Cards ${kb.cardCount} · updated ${fmtDate(lastCardDate)} · live feed`,
    tracker: `Items ${tracker.meta.totalItems} · LAST CHECKED ${fmtDate(tracker.meta.lastUpdated)}`,
    chatbot: "배터리·ESS 이슈를 빠르게 찾고 정리해주는 AI 데스크",
    webtoon: `${WEBTOON_COLLECTIONS.length} SERIES`,
  }[tab] || `Cards ${kb.cardCount} · ESS · EV · Policy`;

  return (
    <div style={{ maxWidth: 480, margin: "0 auto", background: t.bg, minHeight: "100vh", fontFamily: "'Pretendard',-apple-system,sans-serif", position: "relative" }}>
      <style dangerouslySetInnerHTML={{ __html: `@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&display=swap');body{margin:0;background:${t.bg}}*{box-sizing:border-box}` }} />
      <div style={{ background: "#161B26", padding: "14px 16px 16px", position: "relative", borderBottom: `1px solid #21293A` }}>
        <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: "linear-gradient(90deg,#58A6FF,#BC8CFF,#58A6FF)" }} />
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <img src="/data/logo_light.png" alt="SBTL" style={{ height: 32, objectFit: "contain" }} onError={(e) => { e.currentTarget.style.display = "none"; }} />
            <div style={{ display: "flex", alignItems: "center", gap: 4, background: "#0B2A0B", borderRadius: 4, padding: "2px 7px" }}><div style={{ width: 5, height: 5, borderRadius: 3, background: "#3FB950" }} /><span style={{ fontSize: 9, color: "#3FB950", fontFamily: "'JetBrains Mono',monospace", fontWeight: 700 }}>LIVE</span></div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: 10, color: "#7D8590", fontFamily: "'JetBrains Mono',monospace" }}>{kb.cardCount}</span>
            <button onClick={() => setDark(!dark)} style={{ background: "#21293A", border: "none", borderRadius: 8, width: 32, height: 32, display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", fontSize: 16 }}>{dark ? "☀️" : "🌙"}</button>
          </div>
        </div>
        <div style={{ marginTop: 10 }}>
          {tab !== "all" && <h1 style={{ color: "#E6EDF3", fontSize: 18, fontWeight: 800, margin: 0 }}>{headerTitle}</h1>}
          <p style={{ color: "#7D8590", fontSize: 10, margin: "2px 0 0", fontFamily: "'JetBrains Mono',monospace" }}>{headerSub}</p>
        </div>
      </div>

      {tab === "all" && <div style={{ paddingTop: 10 }}><Home kb={kb} tracker={tracker} onNav={setTab} dark={dark} /></div>}
      {tab === "news" && <NewsDesk kb={kb} dark={dark} />}
      {tab === "chatbot" && <ChatBot kb={kb} tracker={tracker} dark={dark} />}
      {tab === "tracker" && <div style={{ paddingTop: 10 }}><Tracker tracker={tracker} dark={dark} /></div>}
      {tab === "webtoon" && <WebtoonLibrary dark={dark} />}

      <div style={{ position: "fixed", bottom: 0, left: "50%", transform: "translateX(-50%)", width: "100%", maxWidth: 480, background: dark ? t.card : "#fff", borderTop: `1px solid ${t.brd}`, display: "flex", padding: "6px 0 8px" }}>
        {CATS.map((cat) => {
          const active = tab === cat.key;
          return (
            <button key={cat.key} onClick={() => setTab(cat.key)} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 2, padding: "4px 0", cursor: "pointer", border: "none", background: "transparent", flex: 1, position: "relative" }}>
              {active && <div style={{ position: "absolute", top: 0, left: "50%", transform: "translateX(-50%)", width: 20, height: 2, borderRadius: 1, background: t.cyan }} />}
              <span style={{ fontSize: 22, lineHeight: 1, filter: active ? "none" : "grayscale(0.3) opacity(0.7)" }}>{cat.icon}</span>
              <span style={{ fontSize: 9, fontWeight: active ? 700 : 500, color: active ? t.cyan : t.sub, fontFamily: "'JetBrains Mono',monospace" }}>{cat.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
