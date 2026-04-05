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
  "오늘 뉴스 3개",
  "LFP 리스크 한 번에",
  "한국 정책 일정 뭐 있어?",
  "미국 FEOC 쉽게 설명해줘",
  "이번주 ESS 시그널 요약",
  "전고체 어디까지 왔어?",
  "중국 가격 흐름 체크",
  "먼저 봐야 할 카드 추천",
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
  const ld = targetDate || latestDate(cards);
  let list = targetDate
    ? cards.filter((c) => c.d && String(c.d).startsWith(targetDate))
    : cards.filter((c) => c.d === ld);
  if (region) list = list.filter((c) => c.r === region);
  const rank = { t: 3, h: 2, m: 1, i: 0 };
  const sorted = list.sort((a, b) => (rank[b.s] || 0) - (rank[a.s] || 0)).slice(0, limit);
  if (targetDate && !sorted.length && !region) {
    const nearby = cards.filter((c) => c.d && String(c.d) <= targetDate).sort((a, b) => String(b.d).localeCompare(String(a.d)));
    return nearby.sort((a, b) => (rank[b.s] || 0) - (rank[a.s] || 0)).slice(0, limit);
  }
  return sorted;
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
      return { ...c, _score: score };
    })
    .filter((c) => c._score > 0)
    .sort((a, b) => b._score - a._score)
    .slice(0, limit);
}

function classifyQuestion(txt) {
  const l = txt.toLowerCase();
  if (/(최신|뉴스|소식|현황|지금|오늘|최근|이번)/.test(l)) return "news";
  if (/(일정|정책|규제|시행|법안|언제|예정|스케줄)/.test(l)) return "policy";
  if (/(비교|차이|vs|대비|어떤 게|뭐가 더)/.test(l)) return "compare";
  if (/(요약|정리|핵심|브리핑|한 줄|한줄)/.test(l)) return "summary";
  return "general";
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

function followUps(type) {
  if (type === "news") return ["요약해서 다시 정리", "카드에서도 찾아봐", "한국 뉴스만", "미국 뉴스만"];
  if (type === "policy") return ["다가오는 일정만", "한국/EU 비교", "실무 영향만 요약"];
  if (type === "compare") return ["한 줄 결론만", "관련 카드 더 보여줘", "최신 기사 링크로 보여줘"];
  return ["조금 더 쉽게 설명해줘", "관련 카드 더 보여줘", "최신 기사 링크로 보여줘", "정책 일정만 따로 정리해줘"];
}

function SmallPill({ label, dark }) {
  const t = T(dark);
  return <span style={{ fontSize: 9, fontWeight: 800, color: t.cyan, background: dark ? "rgba(88,166,255,0.14)" : "rgba(45,90,142,0.10)", padding: "4px 8px", borderRadius: 999, fontFamily: "'JetBrains Mono',monospace" }}>{label}</span>;
}

function NewsItem({ card, dark }) {
  const t = T(dark);
  const sig = card.s || "i";
  return (
    <div onClick={() => card.url && window.open(card.url, "_blank")} style={{ background: t.card2, borderRadius: 12, padding: "12px 14px", borderLeft: `3px solid ${SIG_C[sig]}`, border: `1px solid ${t.brd}`, cursor: card.url ? "pointer" : "default" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 5 }}>
        <span style={{ fontSize: 8, fontWeight: 800, color: SIG_C[sig], background: `${SIG_C[sig]}20`, padding: "2px 6px", borderRadius: 999, fontFamily: "'JetBrains Mono',monospace" }}>{SIG_L[sig]}</span>
        <span style={{ fontSize: 9, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>{REG_FLAG[card.r] || "🌐"} {shortDate(card.d)}</span>
        {card.src && <span style={{ fontSize: 8, color: t.sub, marginLeft: "auto", fontFamily: "'JetBrains Mono',monospace" }}>{card.src}</span>}
      </div>
      <h3 style={{ fontSize: 13, fontWeight: 700, color: t.tx, margin: 0, lineHeight: 1.45 }}>{card.T}</h3>
      {card.sub && <p style={{ fontSize: 11, color: t.sub, margin: "4px 0 0", lineHeight: 1.45 }}>{card.sub}</p>}
      {card.url && <div style={{ marginTop: 6, fontSize: 9, color: t.cyan, fontFamily: "'JetBrains Mono',monospace" }}>open source ↗</div>}
    </div>
  );
}

function Home({ kb, tracker, onNav, dark }) {
  const t = T(dark);
  const featured = WEBTOON_COLLECTIONS[0];
  const picks = latestCards(kb.cards, 3);
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
            <div style={{ fontSize: 12, color: t.sub, lineHeight: 1.65, marginTop: 8 }}>배터리·ESS·EV 밸류체인을 중심으로 정책, 공급망, 기술, 기업 이슈를 선별해 정리하는 인텔리전스 허브입니다.</div>
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

function ChatBot({ kb, dark }) {
  const t = T(dark);
  const [msgs, setMsgs] = useState([{ role: "assistant", content: "안녕, 강차장이야. 🔋\n\n궁금한 주제를 편하게 보내줘.\n핵심부터 짧게 정리해주고,\n관련 카드나 최근 이슈도 같이 찾아줄게." }]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef(null);

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

  const searchBrave = async (q, qType = "general", region = null, targetDate = null) => {
    try {
      const regionKeyword = { US: "US America", KR: "Korea", CN: "China", EU: "Europe", JP: "Japan" }[region] || "";
      let searchQuery;
      if (qType === "news" && region) {
        const datePart = targetDate ? targetDate.replace(/\./g, "-") : "2026";
        searchQuery = `${regionKeyword} battery ESS EV news ${datePart}`;
      } else {
        searchQuery = `${q} battery ESS 2026`;
      }
      const r = await fetch("/api/brave", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ query: searchQuery }) });
      const d = await r.json();
      const results = (d.web?.results || []).slice(0, 3);
      if (!results.length) return null;
      return results.map((item) => ({ title: item.title, description: item.description, url: item.url }));
    } catch {
      return null;
    }
  };

  const buildCardMessage = (cards, textType = "general", targetDate = null) => {
    const dateLabel = targetDate || fmtDate(cards[0]?.d);
    return {
      role: "assistant",
      content: textType === "news" ? `${dateLabel} 기준 핵심 뉴스야.` : `관련 카드 ${cards.length}건을 찾았어.`,
      cards: cards.map((c) => ({ title: c.T, subtitle: c.sub, signal: c.s, url: c.url, region: c.r, date: c.d, source: c.src })),
      suggestions: followUps(textType).map((label) => ({ label })),
    };
  };

  const buildLinkMessage = (links, type = "general", targetDate = null, region = null) => {
    const regionLabel = { US: "미국", KR: "한국", CN: "중국", EU: "유럽", JP: "일본" }[region] || "";
    const dateLabel = targetDate ? ` (${targetDate} 전후)` : "";
    return {
      role: "assistant",
      content: `${regionLabel}${regionLabel ? " " : ""}최신 링크를 정리했어.${dateLabel}`,
      links,
      suggestions: followUps(type).map((label) => ({ label })),
    };
  };

  const sendWithText = async (rawText) => {
    const txt = String(rawText || "").trim();
    if (!txt || loading) return;
    setLoading(true);
    setInput("");
    setMsgs((prev) => [...prev, { role: "user", content: txt }]);

    const qType = classifyQuestion(txt);
    const region = detectRegion(txt);
    const targetDate = detectDate(txt);
    const faq = matchFaq(txt);
    if (faq) {
      setMsgs((prev) => [...prev, { role: "assistant", content: faq, suggestions: followUps(qType).map((label) => ({ label })) }]);
      setLoading(false);
      return;
    }

    if (qType === "news") {
      const cards = latestCards(kb.cards, 3, region, targetDate);
      if (cards.length) {
        setMsgs((prev) => [...prev, buildCardMessage(cards, "news", targetDate)]);
        setLoading(false);
        return;
      }
    }

    const cardHits = searchCards(kb.cards, txt, 4);
    if (cardHits.length) {
      setMsgs((prev) => [...prev, buildCardMessage(cardHits, qType, targetDate)]);
      setLoading(false);
      return;
    }

    const brave = await searchBrave(txt, qType, region, targetDate);
    if (brave?.length) {
      setMsgs((prev) => [...prev, buildLinkMessage(brave, qType, targetDate, region)]);
      setLoading(false);
      return;
    }

    setMsgs((prev) => [...prev, { role: "assistant", content: "딱 맞는 결과가 바로 안 잡혔어.\n\n주제를 조금 더 짧게 보내보자. 예: LFP 리스크 / 오늘 핵심 뉴스 / 한국 정책 일정", suggestions: followUps(qType).map((label) => ({ label })) }]);
    setLoading(false);
  };

  const runSuggestion = (label) => {
    const map = {
      "오늘 핵심 뉴스 3개": "오늘 뉴스 3개",
      "오늘 뉴스 3개": "오늘 뉴스 3개",
      "요약해서 다시 정리": "방금 답변을 3줄로 다시 요약해줘",
      "카드에서도 찾아봐": "방금 주제와 관련된 카드도 같이 찾아줘",
      "조금 더 쉽게 설명해줘": "방금 답변을 더 쉽게 설명해줘",
      "관련 카드 더 보여줘": "방금 주제와 관련된 카드 더 보여줘",
      "최신 기사 링크로 보여줘": "방금 주제 기준 최신 기사 링크 3개 보여줘",
      "정책 일정만 따로 정리해줘": "방금 주제와 관련된 정책 일정만 따로 정리해줘",
      "한국 뉴스만": "오늘 한국 뉴스 3개",
      "미국 뉴스만": "오늘 미국 뉴스 3개",
      "다가오는 일정만": "다가오는 정책 일정만 정리해줘",
      "한국/EU 비교": "한국과 EU 정책을 비교해줘",
      "실무 영향만 요약": "실무 영향만 요약해줘",
      "한 줄 결론만": "한 줄 결론만 말해줘",
    };
    const next = map[label] || label;
    void sendWithText(next);
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
                <div style={{ padding: "11px 14px", fontSize: 13, lineHeight: 1.6, whiteSpace: "pre-wrap", wordBreak: "keep-all", borderRadius: m.role === "user" ? "18px 18px 6px 18px" : "18px 18px 18px 6px", background: m.role === "user" ? "#4C8DFF" : (dark ? "#1A2333" : "#FFFFFF"), color: m.role === "user" ? "#fff" : t.tx, border: m.role === "user" ? "none" : `1px solid ${t.brd}`, fontFamily: "'Pretendard', sans-serif" }}>{m.content}</div>
                {m.cards?.map((card, j) => (
                  <div key={j} onClick={() => card.url && window.open(card.url, "_blank")} style={{ background: dark ? "#151B26" : "#f8f9fc", borderRadius: 10, padding: "10px 12px", marginTop: 6, cursor: card.url ? "pointer" : "default", border: `1px solid ${t.brd}` }}>
                    <div style={{ fontSize: 12, fontWeight: 700, color: t.tx }}>{SIG_L[card.signal] || "INFO"} {card.title}</div>
                    {card.subtitle && <div style={{ fontSize: 11, color: t.sub, marginTop: 3 }}>{card.subtitle}</div>}
                    <div style={{ fontSize: 10, color: t.sub, marginTop: 4, fontFamily: "'JetBrains Mono',monospace" }}>{fmtDate(card.date)} · {card.region} · {card.source || "source"}</div>
                    {card.url && <div style={{ fontSize: 10, color: t.cyan, marginTop: 4 }}>→ 원문 보기</div>}
                  </div>
                ))}
                {m.links?.map((link, j) => (
                  <a key={j} href={link.url} target="_blank" rel="noopener noreferrer" style={{ display: "block", background: dark ? "#151B26" : "#f8f9fc", borderRadius: 10, padding: "10px 12px", marginTop: 6, textDecoration: "none", border: `1px solid ${t.brd}` }}>
                    <div style={{ fontSize: 12, fontWeight: 700, color: t.cyan }}>{link.title}</div>
                    {link.description && <div style={{ fontSize: 11, color: t.sub, marginTop: 3, lineHeight: 1.4 }}>{link.description}</div>}
                    <div style={{ fontSize: 10, color: t.sub, marginTop: 4, fontFamily: "'JetBrains Mono',monospace" }}>{link.url}</div>
                  </a>
                ))}
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
        <div style={{ display: "flex", gap: 6 }}>
          <input type="text" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && void sendWithText(input)} placeholder="궁금한 주제를 입력해줘" style={{ flex: 1, padding: "10px 12px", borderRadius: 10, border: `1px solid ${t.brd}`, background: t.card2, color: t.tx, fontSize: 13, outline: "none", fontFamily: "'Pretendard',sans-serif" }} />
          <button onClick={() => void sendWithText(input)} disabled={loading || !input.trim()} style={{ padding: "10px 16px", borderRadius: 10, border: "none", background: t.cyan, color: "#000", fontWeight: 800, cursor: "pointer", fontSize: 13, fontFamily: "'Pretendard',sans-serif" }}>→</button>
        </div>
      </div>
    </div>
  );
}

function Tracker({ tracker, dark }) {
  const t = T(dark);
  const d = tracker;
  const updatedLabel = fmtDate(d.meta.lastUpdated);
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
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}><span style={{ fontSize: 10, color: "#3a6090", fontFamily: "'JetBrains Mono',monospace" }}>REGIONS</span><div style={{ flex: 1, height: 1, background: t.brd }} /></div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
          {d.regions.map((r) => (
            <div key={r.code} style={{ background: t.card2, borderRadius: 8, padding: "10px 12px", border: `1px solid ${t.brd}` }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}><span style={{ fontSize: 14 }}>{r.flag}</span><span style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>{r.ACTIVE} ACTIVE</span></div>
              <div style={{ fontSize: 13, fontWeight: 700, color: t.tx, marginTop: 4 }}>{r.name}</div>
              <div style={{ marginTop: 6, height: 3, borderRadius: 2, background: t.brd }}><div style={{ height: "100%", borderRadius: 2, background: SC.ACTIVE, width: pct(r.ACTIVE, r.total) }} /></div>
            </div>
          ))}
        </div>
      </div>

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
      {tab === "chatbot" && <ChatBot kb={kb} dark={dark} />}
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
