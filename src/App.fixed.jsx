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
      {
        id: 101,
        title: "EP.01 LFP의 두 가지 착각",
        subtitle: "좋은 배터리일 수 있다. 그런데 너무 쉽게 보면 핵심을 놓친다.",
        date: "2026.04.05",
        isNew: true,
        color: "#F85149",
        url: "/webtoon/lfp-two-misconceptions-ep1.html",
        tag: "START",
      },
      {
        id: 102,
        title: "EP.02 덜 타 보인다고, 덜 위험한 건 아니다",
        subtitle: "보이는 화재 위험과 보이지 않는 off-gas 위험은 같은 말이 아니다.",
        date: "2026.04.05",
        isNew: true,
        color: "#D29922",
        url: "/webtoon/lfp-two-misconceptions-ep2.html",
        tag: "PART 2",
      },
      {
        id: 103,
        title: "BONUS.01 누가 진짜 돈을 내나?",
        subtitle: "끝날 때 비용은 존재한다. 그 돈을 누가 떠안는지 묻는 보너스 에피소드.",
        date: "2026.04.05",
        isNew: true,
        color: "#58A6FF",
        url: "/webtoon/who-pays-bonus1.html",
        tag: "BONUS",
      },
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

const SC = {
  ACTIVE: "#F85149",
  UPCOMING: "#D29922",
  WATCH: "#388BFD",
  DONE: "#7D8590",
};

const SL = {
  ACTIVE: "ACTIVE",
  UPCOMING: "UPCOMING",
  WATCH: "WATCH",
  DONE: "DONE",
};

const sigC = { t: "#F85149", h: "#D29922", m: "#388BFD", i: "#7D8590" };
const sigL = { t: "TOP", h: "HIGH", m: "MID", i: "INFO" };
const regFlag = {
  US: "🇺🇸",
  KR: "🇰🇷",
  EU: "🇪🇺",
  CN: "🇨🇳",
  JP: "🇯🇵",
  GL: "🌐",
  "US/KR": "🇺🇸",
};

const trackerRegionMeta = {
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

const fmtCardDate = (date) => {
  const f = fmtDate(date);
  if (f === "-" || f.length < 10) return f;
  return f.slice(5);
};

const pct = (num, total) =>
  `${Math.max(0, Math.min(100, ((Number(num) || 0) / Math.max(1, Number(total) || 0)) * 100))}%`;

const T = (dk = true) =>
  dk
    ? {
        bg: "#0D1117",
        card: "#161B26",
        card2: "#1C2333",
        tx: "#E6EDF3",
        sub: "#7D8590",
        brd: "#21293A",
        sh: "0 2px 8px rgba(0,0,0,0.4)",
        cyan: "#58A6FF",
      }
    : {
        bg: "#F4F6FA",
        card: "#FFFFFF",
        card2: "#F8F9FC",
        tx: "#1A1A2A",
        sub: "#6B7280",
        brd: "#E0E3EA",
        sh: "0 2px 10px rgba(0,0,0,0.06)",
        cyan: "#2D5A8E",
      };

function useKnowledgeBase() {
  const [cards, setCards] = useState([]);
  const [faq, setFaq] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch("/data/cards.json")
        .then((r) => r.json())
        .then((d) => d.cards || d)
        .catch(() => []),
      fetch("/data/faq.json")
        .then((r) => r.json())
        .catch(() => []),
    ]).then(([c, f]) => {
      setCards(Array.isArray(c) ? c : []);
      setFaq(Array.isArray(f) ? f : []);
      setLoading(false);
    });
  }, []);

  return {
    cards,
    faq,
    loading,
    cardCount: cards.length,
    faqCount: faq.length,
  };
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
    const fallback = {
      meta: { lastUpdated: "-", totalItems: 0 },
      summary: { ACTIVE: 0, UPCOMING: 0, WATCH: 0, DONE: 0 },
      regions: [],
      upcoming: [],
      items: [],
    };
    if (!raw || !Array.isArray(raw.items)) return fallback;

    const items = raw.items;
    const summary = items.reduce(
      (acc, item) => {
        const k = item?.s;
        if (acc[k] !== undefined) acc[k] += 1;
        return acc;
      },
      { ACTIVE: 0, UPCOMING: 0, WATCH: 0, DONE: 0 }
    );

    const regions = Object.keys(trackerRegionMeta)
      .map((code) => {
        const list = items.filter((i) => i.r === code);
        if (!list.length) return null;
        return {
          code,
          flag: trackerRegionMeta[code].flag,
          name: trackerRegionMeta[code].name,
          total: list.length,
          ACTIVE: list.filter((i) => i.s === "ACTIVE").length,
        };
      })
      .filter(Boolean);

    const upcoming = items
      .filter((i) => i.s === "UPCOMING")
      .sort((a, b) => String(a.dt || "").localeCompare(String(b.dt || "")))
      .slice(0, 8)
      .map((i) => ({
        date: i.dt || "-",
        title: i.t || "-",
        region: i.r || "-",
      }));

    return {
      meta: {
        lastUpdated: raw.meta?.lastUpdated || "-",
        totalItems: Number(raw.meta?.totalItems ?? items.length) || items.length,
      },
      summary,
      regions,
      upcoming,
      items,
    };
  }, [raw]);

  return { tracker, loading };
}

function searchCards(cards, q) {
  const ws = q
    .toLowerCase()
    .replace(/[?!.,]/g, "")
    .split(/\s+/)
    .filter((w) => w.length >= 2);
  if (!ws.length) return [];

  return cards
    .map((c) => {
      let sc = 0;
      const tl = String(c.T || "").toLowerCase();
      const gl = String(c.g || "").toLowerCase();
      const ks = Array.isArray(c.k) ? c.k : [];
      for (const w of ws) {
        if (tl.includes(w)) sc += 10;
        if (gl.includes(w)) sc += 5;
        if (
          ks.some((k) => {
            const kk = String(k).toLowerCase();
            return kk.includes(w) || w.includes(kk);
          })
        ) {
          sc += 8;
        }
      }
      if (c.s === "t") sc *= 2;
      else if (c.s === "h") sc *= 1.5;
      return { ...c, _sc: sc };
    })
    .filter((c) => c._sc > 0)
    .sort((a, b) => b._sc - a._sc)
    .slice(0, 3);
}

function SmallActionPill({ label, dark }) {
  const t = T(dark);
  return (
    <span
      style={{
        fontSize: 9,
        fontWeight: 800,
        color: t.cyan,
        background: dark ? "rgba(88,166,255,0.14)" : "rgba(45,90,142,0.10)",
        padding: "4px 8px",
        borderRadius: 999,
        fontFamily: "'JetBrains Mono',monospace",
        letterSpacing: 0.4,
      }}
    >
      {label}
    </span>
  );
}

function NewsItem({ card, dark }) {
  const t = T(dark);
  const sig = card.s || "i";
  const flag = regFlag[card.r] || "🌐";

  return (
    <div
      onClick={() => card.url && window.open(card.url, "_blank")}
      style={{
        background: t.card2,
        borderRadius: 12,
        padding: "12px 14px",
        borderLeft: `3px solid ${sigC[sig] || t.cyan}`,
        border: `1px solid ${t.brd}`,
        cursor: card.url ? "pointer" : "default",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 5 }}>
        <span
          style={{
            fontSize: 8,
            fontWeight: 800,
            color: sigC[sig] || t.cyan,
            background: `${sigC[sig] || t.cyan}20`,
            padding: "2px 6px",
            borderRadius: 999,
            fontFamily: "'JetBrains Mono',monospace",
            letterSpacing: 1,
          }}
        >
          {sigL[sig] || "INFO"}
        </span>
        <span style={{ fontSize: 9, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>
          {flag} {fmtCardDate(card.d)}
        </span>
        {card.src && (
          <span
            style={{
              fontSize: 8,
              color: t.sub,
              marginLeft: "auto",
              fontFamily: "'JetBrains Mono',monospace",
            }}
          >
            {card.src}
          </span>
        )}
      </div>
      <h3 style={{ fontSize: 13, fontWeight: 700, color: t.tx, margin: 0, lineHeight: 1.45 }}>
        {card.T}
      </h3>
      {card.sub && (
        <p style={{ fontSize: 11, color: t.sub, margin: "4px 0 0", lineHeight: 1.45 }}>
          {card.sub}
        </p>
      )}
      {card.url && (
        <div style={{ marginTop: 6, fontSize: 9, color: t.cyan, fontFamily: "'JetBrains Mono',monospace" }}>
          open source ↗
        </div>
      )}
    </div>
  );
}

function Home({ onNav, kb, tracker, dark }) {
  const t = T(dark);
  const featured = WEBTOON_COLLECTIONS[0];
  const latestTop = kb.cards.filter((c) => c.s === "t").slice(0, 3);

  return (
    <div style={{ padding: "0 14px 120px", display: "flex", flexDirection: "column", gap: 12 }}>
      <div
        style={{
          background: `linear-gradient(135deg, ${dark ? "#151B2B" : "#ffffff"}, ${
            dark ? "#1F2840" : "#EEF3FF"
          })`,
          borderRadius: 18,
          padding: "18px 16px",
          border: `1px solid ${dark ? "#2C3550" : t.brd}`,
          boxShadow: t.sh,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap", marginBottom: 10 }}>
              <SmallActionPill label="SBTL CONTENT HUB" dark={dark} />
              <span style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>
                BATTERY · ESS · EV
              </span>
            </div>
            <div style={{ fontSize: 24, fontWeight: 900, color: t.tx, lineHeight: 1.2 }}>
              SBTL Strategic Intelligence Brief
            </div>
            <div style={{ fontSize: 12, color: t.sub, lineHeight: 1.65, marginTop: 8 }}>
              배터리·ESS·EV 밸류체인을 중심으로 정책, 공급망, 기술, 기업 이슈를 선별해 정리하는 인텔리전스 허브입니다. 경영진, 투자자, 실무자가 핵심 시그널을 빠르게 확인할 수 있도록 구성했습니다.
            </div>
          </div>
          <div
            style={{
              width: 56,
              height: 56,
              borderRadius: 16,
              background: dark ? "rgba(88,166,255,0.12)" : "rgba(88,166,255,0.08)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 28,
              flexShrink: 0,
            }}
          >
            🏢
          </div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 8, marginTop: 14 }}>
          {[
            { label: "CARDS", value: kb.cardCount },
            { label: "FAQ", value: kb.faqCount },
            { label: "REGIONS", value: 5 },
            { label: "TRACKER", value: tracker.meta.totalItems },
          ].map((item) => (
            <div
              key={item.label}
              style={{
                background: dark ? "rgba(10,14,20,0.55)" : "rgba(255,255,255,0.88)",
                border: `1px solid ${t.brd}`,
                borderRadius: 12,
                padding: "10px 8px",
                textAlign: "center",
              }}
            >
              <div style={{ fontSize: 16, fontWeight: 900, color: t.tx, fontFamily: "'JetBrains Mono',monospace" }}>
                {item.value}
              </div>
              <div style={{ fontSize: 9, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginTop: 4 }}>
                {item.label}
              </div>
            </div>
          ))}
        </div>

        <div style={{ display: "flex", gap: 8, marginTop: 14 }}>
          <button
            onClick={() => onNav("news")}
            style={{
              flex: 1,
              border: "none",
              borderRadius: 10,
              padding: "10px 12px",
              background: t.cyan,
              color: "#000",
              fontSize: 11,
              fontWeight: 900,
              cursor: "pointer",
              fontFamily: "'JetBrains Mono',monospace",
            }}
          >
            OPEN NEWS
          </button>
          <button
            onClick={() => onNav("tracker")}
            style={{
              flex: 1,
              border: `1px solid ${t.brd}`,
              borderRadius: 10,
              padding: "10px 12px",
              background: "transparent",
              color: t.tx,
              fontSize: 11,
              fontWeight: 900,
              cursor: "pointer",
              fontFamily: "'JetBrains Mono',monospace",
            }}
          >
            OPEN TRACKER
          </button>
        </div>
      </div>
