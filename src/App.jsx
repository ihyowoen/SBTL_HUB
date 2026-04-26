import { useEffect, useMemo, useRef, useState, Component } from "react";
import StoryNewsItem from "./story/StoryNewsItem";
import { buildCardConsultContext } from "./story/buildCardConsultContext";
import { getCardId } from "./story/normalizeCard";
import {
  createConsultation,
  appendMessage,
  getAllCardConsultationSummaries,
  getRecentOpenerIds,
} from "./consultation/consultationStorage";

// Error Boundary Component
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Error caught by boundary:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      const { dark } = this.props;
      const t = T(dark);

      return (
        <div style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          minHeight: "100vh",
          background: t.bg,
          padding: "20px",
          fontFamily: "'Pretendard',-apple-system,sans-serif"
        }}>
          <div style={{
            maxWidth: 480,
            width: "100%",
            background: t.card,
            borderRadius: 16,
            padding: "32px 24px",
            border: `1px solid ${t.brd}`,
            textAlign: "center"
          }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>⚠️</div>
            <h1 style={{ fontSize: 20, fontWeight: 800, color: t.tx, margin: "0 0 8px" }}>
              앗, 문제가 발생했습니다
            </h1>
            <p style={{ fontSize: 13, color: t.sub, lineHeight: 1.6, margin: "0 0 24px" }}>
              예기치 않은 오류가 발생했습니다. 페이지를 새로고침하거나 홈으로 돌아가주세요.
            </p>
            <div style={{ display: "flex", gap: 8, justifyContent: "center" }}>
              <button
                onClick={() => window.location.reload()}
                style={{
                  flex: 1,
                  maxWidth: 200,
                  padding: "12px 20px",
                  borderRadius: 10,
                  border: "none",
                  background: t.cyan,
                  color: "#000",
                  fontSize: 13,
                  fontWeight: 800,
                  cursor: "pointer",
                  fontFamily: "'Pretendard',sans-serif"
                }}
              >
                새로고침
              </button>
              <button
                onClick={() => {
                  this.setState({ hasError: false, error: null });
                  window.location.href = "/";
                }}
                style={{
                  flex: 1,
                  maxWidth: 200,
                  padding: "12px 20px",
                  borderRadius: 10,
                  border: `1px solid ${t.brd}`,
                  background: "transparent",
                  color: t.tx,
                  fontSize: 13,
                  fontWeight: 800,
                  cursor: "pointer",
                  fontFamily: "'Pretendard',sans-serif"
                }}
              >
                홈으로
              </button>
            </div>
            {this.state.error && (
              <details style={{ marginTop: 20, textAlign: "left" }}>
                <summary style={{ fontSize: 11, color: t.sub, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>
                  오류 세부정보
                </summary>
                <pre style={{
                  fontSize: 10,
                  color: t.sub,
                  background: t.bg,
                  padding: 12,
                  borderRadius: 8,
                  overflow: "auto",
                  marginTop: 8,
                  fontFamily: "'JetBrains Mono',monospace"
                }}>
                  {this.state.error.toString()}
                </pre>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

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

const REGION_POLICY = {
  NA: {
    flag: "🇺🇸",
    title: "미국 정책",
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
    flag: "🇪🇺",
    title: "유럽 정책",
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
    flag: "🇨🇳",
    title: "중국 정책",
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
    flag: "🇰🇷",
    title: "한국 정책",
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
    flag: "🇯🇵",
    title: "일본 정책",
    policies: [
      { name: "GX (Green Transformation)", desc: "GX 추진법 기반 20조엔 투자. 배터리·수소·원자력 포함한 에너지 전환 가속." },
      { name: "배터리 지원", desc: "METI 대규모 축전시스템 보조금 (보조율 33~66%). 도쿄도 별도 20억엔 지원." },
      { name: "전력정책", desc: "재생에너지 주력전원화 + 계통유연성 확보. ESS를 조정력 수단으로 본격 활용." },
    ],
    why: "일본은 에너지 안보 관점에서 ESS를 전략자산화 — 보조금 규모가 시장 형성 속도를 결정한다.",
    watchpoints: ["METI 축전 보조금 2차 공모 시기", "GX 채권 발행·집행 진도", "계통용 ESS 접속 규칙 개정"],
  },
  GL: {
    flag: "🌐",
    title: "글로벌 공통",
    policies: [
      { name: "공급망 재편", desc: "미·중 디커플링 가속. 중간재 가공 거점이 동남아·중동·아프리카로 분산." },
      { name: "광물 확보 경쟁", desc: "리튬·니켈·코발트·흑연 확보전. 자원국 수출 규제 확대 추세." },
    ],
    why: "글로벌 밸류체인 재편은 모든 지역 정책의 배경이 된다 — 공급망 지도가 바뀌고 있다.",
    watchpoints: ["인도네시아 니켈 수출 정책 변화", "칠레·아르헨티나 리튬 국유화 동향"],
  },
};


/* KST (UTC+9) 기준 현재 시각 */
const kstNow = () => {
  const now = new Date();
  const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
  return new Date(utc + (9 * 60 * 60 * 1000));
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
  ? { bg: "#0D1117", card: "#161B26", card2: "#1C2333", tx: "#E6EDF3", sub: "#9198A1", brd: "#21293A", cyan: "#58A6FF", sh: "0 2px 8px rgba(0,0,0,0.4)" }
  : { bg: "#F4F6FA", card: "#FFFFFF", card2: "#F8F9FC", tx: "#1A1A2A", sub: "#57606A", brd: "#E0E3EA", cyan: "#0969DA", sh: "0 2px 10px rgba(0,0,0,0.06)" };

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

const buildFetchUrl = (path, requestKey = 0) => {
  if (!requestKey) return path;
  const sep = path.includes("?") ? "&" : "?";
  return `${path}${sep}_ts=${requestKey}`;
};

const LEGACY_SIGNAL = { top: "t", high: "h", mid: "m", info: "i", t: "t", h: "h", m: "m", i: "i" };

function toCompatCard(card) {
  if (!card || typeof card !== "object") return card;
  const signal = card.signal || card.s || "i";
  const source = card.source || card.src || "";
  const primaryUrl = Array.isArray(card.urls) ? card.urls[0] : (card.url || "");
  const implicationText = Array.isArray(card.implication)
    ? card.implication.filter(Boolean).join("\n\n")
    : String(card.implication || "");
  const gateText = String(card.gate || "");
  return {
    ...card,
    T: card.T || card.title || "",
    sub: card.sub || "",
    s: card.s || LEGACY_SIGNAL[signal] || "i",
    signal: card.signal || signal,
    r: card.r || card.region || "GL",
    region: card.region || card.r || "GL",
    d: card.d || card.date || "",
    date: card.date || card.d || "",
    src: card.src || source,
    source,
    url: card.url || primaryUrl,
    urls: Array.isArray(card.urls) ? card.urls : (primaryUrl ? [primaryUrl] : []),
    g: card.g || gateText || implicationText || card.sub || "",
  };
}


async function fetchJsonFile(path, requestKey = 0, hardRefresh = false) {
  const response = await fetch(buildFetchUrl(path, requestKey), {
    cache: hardRefresh ? "reload" : "no-cache",
    headers: hardRefresh
      ? { "Cache-Control": "no-cache, no-store, max-age=0", Pragma: "no-cache" }
      : { "Cache-Control": "no-cache" },
  });
  if (!response.ok) throw new Error(`Failed to fetch ${path}`);
  return response.json();
}

async function clearBrowserCaches() {
  if (!("caches" in window)) return;
  const cacheKeys = await window.caches.keys();
  await Promise.all(cacheKeys.map((key) => window.caches.delete(key)));
}

function useKnowledgeBase(refreshKey = 0, hardRefresh = false) {
  const [cards, setCards] = useState([]);
  const [faq, setFaq] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let ignore = false;
    setLoading(true);

    Promise.all([
      fetchJsonFile("/data/cards.json", refreshKey, hardRefresh).then((d) => d.cards || d).catch(() => []),
      fetchJsonFile("/data/faq.json", refreshKey, hardRefresh).catch(() => []),
    ])
      .then(([c, f]) => {
        if (ignore) return;
        setCards(Array.isArray(c) ? c.map(toCompatCard) : []);
        setFaq(Array.isArray(f) ? f : []);
      })
      .finally(() => {
        if (!ignore) setLoading(false);
      });

    return () => {
      ignore = true;
    };
  }, [refreshKey, hardRefresh]);

  return { cards, faq, loading, cardCount: cards.length, faqCount: faq.length };
}

function useTrackerData(refreshKey = 0, hardRefresh = false) {
  const [raw, setRaw] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let ignore = false;
    setLoading(true);

    fetchJsonFile("/data/tracker_data.json", refreshKey, hardRefresh)
      .then((data) => {
        if (!ignore) setRaw(data);
      })
      .catch(() => {
        if (!ignore) setRaw(null);
      })
      .finally(() => {
        if (!ignore) setLoading(false);
      });

    return () => {
      ignore = true;
    };
  }, [refreshKey, hardRefresh]);

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

function latestCards(cards, limit = 3, region = null, targetDate = null, fallbackToLatest = false) {
  // When region is specified, filter by region FIRST then find latest date within that subset
  const pool = region ? cards.filter((c) => c.r === region) : cards;
  const rank = { t: 3, h: 2, m: 1, i: 0 };

  if (targetDate) {
    const target = fmtDate(targetDate);
    const list = pool.filter((c) => c.d && fmtDate(c.d) === target);
    if (list.length) return list.sort((a, b) => (rank[b.s] || 0) - (rank[a.s] || 0)).slice(0, limit);
    if (!fallbackToLatest) return [];
    // fall through to latest-date logic when no same-day cards exist
  }

  // No targetDate (or fallback): use latest date within the (possibly region-filtered) pool
  const ld = latestDate(pool);
  if (!ld) return pool.sort((a, b) => (rank[b.s] || 0) - (rank[a.s] || 0)).slice(0, limit);
  const list = pool.filter((c) => c.d === ld);
  return list.sort((a, b) => (rank[b.s] || 0) - (rank[a.s] || 0)).slice(0, limit);
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
        {isForeign && <span style={{ fontSize: 8, fontWeight: 700, color: "#58A6FF", background: "rgba(88,166,255,0.22)", padding: "2px 6px", borderRadius: 999, fontFamily: "'JetBrains Mono',monospace" }}>해외</span>}
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
          <button onClick={(e) => { e.stopPropagation(); if (!showSummary && !summaryContent) fetchAnalysis('summary'); setShowSummary(!showSummary); setShowWhy(false); setShowGist(false); }} aria-label={showSummary ? "Hide Korean summary" : "Show Korean summary"} style={{ fontSize: 9, color: "#58A6FF", background: "transparent", border: `1px solid ${t.brd}`, borderRadius: 999, padding: "8px 12px", minHeight: "44px", cursor: "pointer", fontFamily: "'JetBrains Mono',monospace", fontWeight: 700 }}>
            {showSummary ? "△ 요약 닫기" : "한국어 요약"}
          </button>
        )}
        {card.g && (
          <button onClick={(e) => { e.stopPropagation(); if (!showWhy && !whyContent) fetchAnalysis('why'); setShowWhy(!showWhy); setShowSummary(false); setShowGist(false); }} aria-label={showWhy ? "Hide importance" : "Show why important"} style={{ fontSize: 9, color: "#D29922", background: "transparent", border: `1px solid ${t.brd}`, borderRadius: 999, padding: "8px 12px", minHeight: "44px", cursor: "pointer", fontFamily: "'JetBrains Mono',monospace", fontWeight: 700 }}>
            {showWhy ? "△ 닫기" : "왜 중요한지"}
          </button>
        )}
        {card.g && (
          <button onClick={(e) => { e.stopPropagation(); if (!showGist && !analysisContent) fetchAnalysis('analysis'); setShowGist(!showGist); setShowSummary(false); setShowWhy(false); }} aria-label={showGist ? "Close analysis" : "Show analysis"} style={{ fontSize: 9, color: "#A855F7", background: "transparent", border: `1px solid ${dark ? "rgba(168,85,247,0.3)" : "rgba(168,85,247,0.2)"}`, borderRadius: 999, padding: "8px 12px", minHeight: "44px", cursor: "pointer", fontFamily: "'JetBrains Mono',monospace", fontWeight: 700 }}>
            {showGist ? "△ 닫기" : "🤖 AI 해설"}
          </button>
        )}
      </div>
    </div>
  );
}

const AUTO_IMAGES = {
  POLICY: 'https://images.unsplash.com/photo-1589829085413-56de8ae18c73?auto=format&fit=crop&w=1200&q=80',
  FINANCE: 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=1200&q=80',
  FACTORY: 'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=1200&q=80',
  AUTO: 'https://images.unsplash.com/photo-1560958089-b8a1929cea89?auto=format&fit=crop&w=1200&q=80',
  BATTERY: 'https://images.unsplash.com/photo-1581092335397-9583eb92d232?auto=format&fit=crop&w=1200&q=80',
  TECH: 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80',
  DEFAULT: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1200&q=80',
};

function pickHomeCover(card) {
  const text = [card?.T, card?.title, card?.sub, card?.g, card?.gate, card?.source, card?.src]
    .filter(Boolean)
    .join(' ')
    .toLowerCase();

  if (/(ira|feoc|crma|보조금|관세|규제|법안|정부|정책|세액공제)/.test(text)) return AUTO_IMAGES.POLICY;
  if (/(실적|영업이익|매출|주가|투자|적자|흑자|m&a|상장)/.test(text)) return AUTO_IMAGES.FINANCE;
  if (/(공장|양산|생산|가동|캐파|capa|증설|설비|수율)/.test(text)) return AUTO_IMAGES.FACTORY;
  if (/(테슬라|전기차|ev|완성차|현대차|기아|포드|gm|bmw|폭스바겐)/.test(text)) return AUTO_IMAGES.AUTO;
  if (/(배터리|lfp|전고체|리튬|니켈|코발트|흑연|양극재|음극재|분리막|전해액|ess|bess|catl|byd|엔솔|sdi)/.test(text)) return AUTO_IMAGES.BATTERY;
  if (/(기술|r&d|특허|연구|차세대|효율|혁신|개발|테스트|파일럿)/.test(text)) return AUTO_IMAGES.TECH;
  return AUTO_IMAGES.DEFAULT;
}

function Home({ kb, tracker, onNav, onSubmitConsultation, consultSummaries = {}, dark }) {
  const t = T(dark);
  const featured = WEBTOON_COLLECTIONS[0];
  const todayPicks = latestCards(kb.cards, 4, null, kstToday());
  const picks = todayPicks.length ? todayPicks : latestCards(kb.cards, 4, null, null);
  const isFromToday = todayPicks.length > 0;
  const today = kstNow();
  const dayNames = ["일", "월", "화", "수", "목", "금", "토"];
  const todayStr = `${kstToday()} (${dayNames[today.getDay()]})`;
  const lead = picks[0] || null;
  const rest = picks.slice(1, 4);
  const leadDateLabel = lead?.d ? fmtDate(lead.d) : "-";

  return (
    <div style={{ padding: "0 14px 120px", display: "flex", flexDirection: "column", gap: 12 }}>
      <div style={{ background: `linear-gradient(135deg, ${dark ? "#151B2B" : "#ffffff"}, ${dark ? "#1F2840" : "#EEF3FF"})`, borderRadius: 18, padding: "18px 16px", border: `1px solid ${dark ? "#2C3550" : t.brd}`, boxShadow: t.sh }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap", marginBottom: 8 }}>
          <SmallPill label={isFromToday ? "TODAY" : "LATEST"} dark={dark} />
          <span style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>
            {isFromToday ? todayStr : `최근 업데이트 ${leadDateLabel}`}
          </span>
        </div>
        <div style={{ fontSize: 24, fontWeight: 900, color: t.tx, lineHeight: 1.2 }}>
          {isFromToday ? "오늘의 뉴스" : "최근 뉴스"}
        </div>
        <div style={{ fontSize: 12, color: t.sub, lineHeight: 1.65, marginTop: 8 }}>
          오늘 봐야 할 흐름만 먼저 읽고, 필요하면 뉴스 피드나 강차장 상담으로 이어집니다.
        </div>
      </div>

      {lead ? (
        <StoryNewsItem
          card={lead}
          dark={dark}
          onSubmitConsultation={onSubmitConsultation}
          consultationHint={consultSummaries[getCardId(lead)] || null}
          coverImage={pickHomeCover(lead)}
          featured
        />
      ) : (
        <div style={{ background: t.card2, borderRadius: 14, padding: "16px", border: `1px solid ${t.brd}`, fontSize: 12, color: t.sub, lineHeight: 1.6 }}>
          오늘 기준 등록된 뉴스카드가 아직 없습니다.
        </div>
      )}

      {rest.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {rest.map((card, i) => (
            <StoryNewsItem
              key={`${card.id || card.T || card.title}-${i}`}
              card={card}
              dark={dark}
              onSubmitConsultation={onSubmitConsultation}
              consultationHint={consultSummaries[getCardId(card)] || null}
              coverImage=""
            />
          ))}
        </div>
      )}

      <div style={{ display: "flex", gap: 8 }}>
        <button onClick={() => onNav("news")} style={{ flex: 1, border: "none", borderRadius: 10, padding: "12px 14px", minHeight: "44px", background: t.cyan, color: "#000", fontSize: 11, fontWeight: 900, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>NEWS FEED →</button>
        <button onClick={() => onNav("tracker")} style={{ flex: 1, border: `1px solid ${t.brd}`, borderRadius: 10, padding: "12px 14px", minHeight: "44px", background: "transparent", color: t.tx, fontSize: 11, fontWeight: 900, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>TRACKER →</button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8 }}>
        <div onClick={() => onNav("webtoon")} style={{ background: t.card2, borderRadius: 14, padding: 14, border: `1px solid ${t.brd}`, cursor: "pointer" }}>
          <div style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginBottom: 6 }}>TOON</div>
          <div style={{ fontSize: 15, fontWeight: 900, color: t.tx, lineHeight: 1.3 }}>웹툰</div>
          <div style={{ fontSize: 11, color: t.sub, lineHeight: 1.5, marginTop: 8 }}>{featured.title}</div>
        </div>

        <div onClick={() => onNav("chatbot")} style={{ background: t.card2, borderRadius: 14, padding: 14, border: `1px solid ${t.brd}`, cursor: "pointer" }}>
          <div style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginBottom: 6 }}>AI DESK</div>
          <div style={{ fontSize: 15, fontWeight: 900, color: t.tx, lineHeight: 1.3 }}>상담소</div>
          <div style={{ fontSize: 11, color: t.sub, lineHeight: 1.5, marginTop: 8 }}>카드 기준으로 바로 대화</div>
        </div>

        <div onClick={() => onNav("tracker")} style={{ background: t.card2, borderRadius: 14, padding: 14, border: `1px solid ${t.brd}`, cursor: "pointer" }}>
          <div style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginBottom: 6 }}>TRACKER</div>
          <div style={{ fontSize: 15, fontWeight: 900, color: t.tx, lineHeight: 1.3 }}>정책</div>
          <div style={{ fontSize: 11, color: t.sub, lineHeight: 1.5, marginTop: 8 }}>{tracker.meta.totalItems} items</div>
        </div>
      </div>
    </div>
  );
}

// 배터리 상담소 — 접수증 A안 (미니카드 + 받음 stamp)
function ReceiptBubble({ meta, openedAt, dark }) {
  const t = T(dark);
  const d = openedAt ? new Date(openedAt) : null;
  const dateLabel = d && !isNaN(d.getTime()) ? `${d.getMonth() + 1}/${d.getDate()}` : "";
  const metaParts = [];
  if (meta?.region) metaParts.push(meta.region);
  const sigShort = (meta?.signal || "i").toString().slice(0, 1).toLowerCase();
  metaParts.push((SIG_L[sigShort] || "INFO"));
  if (meta?.date) metaParts.push(fmtDate(meta.date));
  const metaLine = metaParts.join(" · ");

  return (
    <div
      role="note"
      aria-label="상담 접수증"
      style={{
        margin: "10px auto",
        maxWidth: "92%",
        padding: "10px 14px",
        background: dark ? "rgba(88,166,255,0.07)" : "rgba(88,166,255,0.05)",
        border: `1px dashed ${t.cyan}`,
        borderRadius: 10,
      }}
    >
      <div style={{
        fontSize: 10, color: t.cyan, fontWeight: 800, marginBottom: 6,
        fontFamily: "'JetBrains Mono',monospace",
        display: "flex", alignItems: "center", gap: 6,
      }}>
        <span aria-hidden="true">📥</span>
        <span>받음{dateLabel ? ` · ${dateLabel}` : ""}</span>
      </div>
      <div style={{
        fontSize: 13, color: t.tx, fontWeight: 700, lineHeight: 1.4, marginBottom: 4,
        fontFamily: "'Pretendard',sans-serif",
      }}>
        {meta?.title || "(제목 없음)"}
      </div>
      {metaLine && (
        <div style={{
          fontSize: 9, color: t.sub, fontWeight: 700,
          fontFamily: "'JetBrains Mono',monospace",
        }}>
          {metaLine}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// 배터리 상담소 — 3-stage v2 bubble 컴포넌트들 (Step 2-A + 2-B)
// ============================================================================

// 1차 — Scout (정찰병): 사실 확인
function ScoutBubble({ stageOutput, dark }) {
  const t = T(dark);
  const { summary, facts = [], unknowns = [] } = stageOutput || {};

  return (
    <div style={{
      margin: "8px 0",
      padding: "14px 16px",
      background: dark ? "#1A2333" : "#FFFFFF",
      border: `1px solid ${t.brd}`,
      borderRadius: "18px 18px 18px 6px",
      borderLeft: `3px solid #58A6FF`,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8 }}>
        <span style={{
          fontSize: 10, fontWeight: 800, color: "#58A6FF",
          background: dark ? "rgba(88,166,255,0.14)" : "rgba(45,90,142,0.10)",
          padding: "3px 8px", borderRadius: 999,
          fontFamily: "'JetBrains Mono',monospace",
        }}>
          📋 1차 · 사실 확인
        </span>
      </div>

      {summary && (
        <div style={{
          fontSize: 13, lineHeight: 1.6, color: t.tx, marginBottom: 12,
          fontFamily: "'Pretendard',sans-serif",
        }}>
          {summary}
        </div>
      )}

      {facts.length > 0 && (
        <div style={{ marginBottom: unknowns.length > 0 ? 12 : 0 }}>
          <div style={{
            fontSize: 9, color: t.sub, fontWeight: 700, marginBottom: 6,
            fontFamily: "'JetBrains Mono',monospace",
          }}>
            FACTS · {facts.length}
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {facts.map((f) => (
              <div key={f.id} style={{
                padding: "8px 10px",
                background: dark ? "rgba(88,166,255,0.05)" : "rgba(88,166,255,0.03)",
                borderRadius: 8,
                border: `1px solid ${dark ? "rgba(88,166,255,0.12)" : "rgba(88,166,255,0.08)"}`,
              }}>
                <div style={{
                  display: "flex", alignItems: "center", gap: 6, marginBottom: 3,
                  flexWrap: "wrap",
                }}>
                  <span style={{
                    fontSize: 9, fontWeight: 800, color: "#58A6FF",
                    fontFamily: "'JetBrains Mono',monospace",
                  }}>
                    {f.id}
                  </span>
                  <span style={{
                    fontSize: 9, color: t.sub,
                    fontFamily: "'JetBrains Mono',monospace",
                  }}>
                    {f.subject}
                    {f.time ? ` · ${f.time}` : ""}
                    {f.place ? ` · ${f.place}` : ""}
                  </span>
                </div>
                <div style={{ fontSize: 12, color: t.tx, lineHeight: 1.5 }}>
                  {f.raw}
                </div>
                {f.value && (
                  <div style={{
                    fontSize: 10, color: t.cyan, marginTop: 3, fontWeight: 700,
                    fontFamily: "'JetBrains Mono',monospace",
                  }}>
                    {f.value}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {unknowns.length > 0 && (
        <div style={{
          padding: "8px 10px",
          background: dark ? "rgba(125,133,144,0.06)" : "rgba(125,133,144,0.04)",
          borderRadius: 8,
          borderLeft: `2px solid ${t.sub}`,
        }}>
          <div style={{
            fontSize: 9, color: t.sub, fontWeight: 700, marginBottom: 4,
            fontFamily: "'JetBrains Mono',monospace",
          }}>
            아직 모르는 것
          </div>
          {unknowns.map((u, i) => (
            <div key={i} style={{
              fontSize: 11, color: t.sub, lineHeight: 1.5, marginTop: 2,
            }}>
              · {u}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// 2차 — Analyst (분석가): 한 각도 해석
function AnalystBubble({ stageOutput, dark }) {
  const t = T(dark);
  const { angle, interpretation, key_tension } = stageOutput || {};

  // fact id (f1, f2 ...) 자동 하이라이트
  const renderInterpretation = (text) => {
    if (!text) return null;
    const parts = text.split(/(\bf\d+\b)/g);
    return parts.map((part, i) =>
      /^f\d+$/.test(part)
        ? <span key={i} style={{
            color: "#58A6FF", fontWeight: 800,
            fontFamily: "'JetBrains Mono',monospace",
            background: dark ? "rgba(88,166,255,0.12)" : "rgba(45,90,142,0.08)",
            padding: "1px 5px", borderRadius: 4,
          }}>{part}</span>
        : <span key={i}>{part}</span>
    );
  };

  return (
    <div style={{
      margin: "8px 0",
      padding: "14px 16px",
      background: dark ? "#1A2333" : "#FFFFFF",
      border: `1px solid ${t.brd}`,
      borderRadius: "18px 18px 18px 6px",
      borderLeft: `3px solid #D29922`,
    }}>
      <div style={{
        display: "flex", alignItems: "center", gap: 6, marginBottom: 8,
        flexWrap: "wrap",
      }}>
        <span style={{
          fontSize: 10, fontWeight: 800, color: "#D29922",
          background: dark ? "rgba(210,153,34,0.14)" : "rgba(210,153,34,0.10)",
          padding: "3px 8px", borderRadius: 999,
          fontFamily: "'JetBrains Mono',monospace",
        }}>
          🔍 2차 · 핵심 각도
        </span>
        {angle && (
          <span style={{
            fontSize: 10, fontWeight: 700, color: t.tx,
            background: dark ? "rgba(210,153,34,0.08)" : "rgba(210,153,34,0.06)",
            padding: "3px 8px", borderRadius: 999,
            fontFamily: "'JetBrains Mono',monospace",
            border: `1px solid ${dark ? "rgba(210,153,34,0.2)" : "rgba(210,153,34,0.15)"}`,
          }}>
            {angle}
          </span>
        )}
      </div>

      {interpretation && (
        <div style={{
          fontSize: 13, lineHeight: 1.65, color: t.tx, marginBottom: 12,
          fontFamily: "'Pretendard',sans-serif",
        }}>
          {renderInterpretation(interpretation)}
        </div>
      )}

      {key_tension && (
        <div style={{
          padding: "10px 12px",
          background: dark ? "rgba(210,153,34,0.07)" : "rgba(210,153,34,0.05)",
          borderRadius: 8,
          borderLeft: `2px solid #D29922`,
        }}>
          <div style={{
            fontSize: 9, color: "#D29922", fontWeight: 800, marginBottom: 4,
            fontFamily: "'JetBrains Mono',monospace",
          }}>
            ⚡ 핵심 쟁점
          </div>
          <div style={{
            fontSize: 12, color: t.tx, lineHeight: 1.5, fontWeight: 600,
          }}>
            {key_tension}
          </div>
        </div>
      )}
    </div>
  );
}

// 3차 — RedTeam (빨간펜): 자기 검증
function RedTeamBubble({ stageOutput, dark }) {
  const t = T(dark);
  const {
    premature_interpretations = [],
    unverified_premises = [],
    counter_scenario,
    next_checkpoints = [],
  } = stageOutput || {};

  // fact id (f1, f2 ...) 자동 하이라이트 — counter_scenario 안에서 사용
  const renderWithFactIds = (text) => {
    if (!text) return null;
    const parts = text.split(/(\bf\d+\b)/g);
    return parts.map((part, i) =>
      /^f\d+$/.test(part)
        ? <span key={i} style={{
            color: "#58A6FF", fontWeight: 800,
            fontFamily: "'JetBrains Mono',monospace",
            background: dark ? "rgba(88,166,255,0.12)" : "rgba(45,90,142,0.08)",
            padding: "1px 5px", borderRadius: 4,
          }}>{part}</span>
        : <span key={i}>{part}</span>
    );
  };

  return (
    <div style={{
      margin: "8px 0",
      padding: "14px 16px",
      background: dark ? "#1A2333" : "#FFFFFF",
      border: `1px solid ${t.brd}`,
      borderRadius: "18px 18px 18px 6px",
      borderLeft: `3px solid #F85149`,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 10 }}>
        <span style={{
          fontSize: 10, fontWeight: 800, color: "#F85149",
          background: dark ? "rgba(248,81,73,0.14)" : "rgba(248,81,73,0.10)",
          padding: "3px 8px", borderRadius: 999,
          fontFamily: "'JetBrains Mono',monospace",
        }}>
          🧪 3차 · 빨간펜
        </span>
      </div>

      {/* (a) 성급한 해석 — red */}
      {premature_interpretations.length > 0 && (
        <div style={{
          marginBottom: 10,
          padding: "10px 12px",
          background: dark ? "rgba(248,81,73,0.06)" : "rgba(248,81,73,0.04)",
          borderRadius: 8,
          borderLeft: `2px solid #F85149`,
        }}>
          <div style={{
            fontSize: 9, color: "#F85149", fontWeight: 800, marginBottom: 5,
            fontFamily: "'JetBrains Mono',monospace",
          }}>
            성급한 해석
          </div>
          {premature_interpretations.map((p, i) => (
            <div key={i} style={{
              fontSize: 12, color: t.tx, lineHeight: 1.6, marginTop: i > 0 ? 6 : 0,
              display: "flex", gap: 6, alignItems: "flex-start",
            }}>
              <span style={{ color: "#F85149", flexShrink: 0, marginTop: 1 }}>·</span>
              <span>{p}</span>
            </div>
          ))}
        </div>
      )}

      {/* (b) 확인 안 된 전제 — amber */}
      {unverified_premises.length > 0 && (
        <div style={{
          marginBottom: 10,
          padding: "10px 12px",
          background: dark ? "rgba(210,153,34,0.06)" : "rgba(210,153,34,0.04)",
          borderRadius: 8,
          borderLeft: `2px solid #D29922`,
        }}>
          <div style={{
            fontSize: 9, color: "#D29922", fontWeight: 800, marginBottom: 5,
            fontFamily: "'JetBrains Mono',monospace",
          }}>
            확인 안 된 전제
          </div>
          {unverified_premises.map((p, i) => (
            <div key={i} style={{
              fontSize: 12, color: t.tx, lineHeight: 1.6, marginTop: i > 0 ? 6 : 0,
              display: "flex", gap: 6, alignItems: "flex-start",
            }}>
              <span style={{ color: "#D29922", flexShrink: 0, marginTop: 1 }}>·</span>
              <span>{p}</span>
            </div>
          ))}
        </div>
      )}

      {/* (c) 반대 시나리오 — cyan + fact id 하이라이트 (주 본문) */}
      {counter_scenario && (
        <div style={{
          marginBottom: 10,
          padding: "10px 12px",
          background: dark ? "rgba(88,166,255,0.05)" : "rgba(88,166,255,0.03)",
          borderRadius: 8,
          borderLeft: `2px solid #58A6FF`,
        }}>
          <div style={{
            fontSize: 9, color: "#58A6FF", fontWeight: 800, marginBottom: 5,
            fontFamily: "'JetBrains Mono',monospace",
          }}>
            반대 시나리오
          </div>
          <div style={{
            fontSize: 12, color: t.tx, lineHeight: 1.65,
            fontFamily: "'Pretendard',sans-serif",
          }}>
            {renderWithFactIds(counter_scenario)}
          </div>
        </div>
      )}

      {/* (d) 다음 체크포인트 — neutral, numbered */}
      {next_checkpoints.length > 0 && (
        <div style={{
          padding: "10px 12px",
          background: dark ? "rgba(125,133,144,0.07)" : "rgba(125,133,144,0.04)",
          borderRadius: 8,
        }}>
          <div style={{
            fontSize: 9, color: t.sub, fontWeight: 800, marginBottom: 6,
            fontFamily: "'JetBrains Mono',monospace",
          }}>
            ✅ 다음 체크포인트
          </div>
          {next_checkpoints.map((cp, i) => (
            <div key={i} style={{
              fontSize: 12, color: t.tx, lineHeight: 1.55, marginTop: i > 0 ? 6 : 0,
              display: "flex", gap: 8, alignItems: "flex-start",
            }}>
              <span style={{
                color: t.sub, fontFamily: "'JetBrains Mono',monospace",
                fontWeight: 800, flexShrink: 0, marginTop: 1, minWidth: 16,
              }}>
                {i + 1}.
              </span>
              <span>{cp}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Wrapper: avatar + bubble + suggestions row
function StageWrapper({ m, dark, runSuggestion, BubbleComponent, errorFallback }) {
  const t = T(dark);
  return (
    <div style={{ display: "flex", flexDirection: "column", marginBottom: 10 }}>
      <div style={{ display: "flex", justifyContent: "flex-start", width: "100%" }}>
        <img src="/data/kang.png" alt="강차장" style={{
          width: 28, height: 28, borderRadius: 14, marginRight: 7,
          flexShrink: 0, marginTop: 2, border: "2px solid #2a1a40",
        }} />
        <div style={{ maxWidth: "88%" }}>
          {m.stage_output
            ? <BubbleComponent stageOutput={m.stage_output} dark={dark} />
            : (
              <div style={{
                padding: "11px 14px", fontSize: 13, color: t.sub,
                background: dark ? "#1A2333" : "#FFFFFF",
                border: `1px solid ${t.brd}`,
                borderRadius: "18px 18px 18px 6px",
              }}>
                {errorFallback || "응답 생성에 문제가 있었어. 다시 시도해줘."}
                {m.stage_error && (
                  <div style={{
                    fontSize: 9, color: t.sub, marginTop: 6,
                    fontFamily: "'JetBrains Mono',monospace", opacity: 0.6,
                  }}>
                    [{m.stage_error}]
                  </div>
                )}
              </div>
            )
          }
        </div>
      </div>
      {m.suggestions?.length > 0 && (
        <div style={{
          display: "flex", gap: 6, flexWrap: "wrap",
          marginTop: 8, marginBottom: 4, paddingLeft: 35,
        }}>
          {m.suggestions.map((s) => {
            const isAdvance = s.hint_action === "advance_stage";
            return (
              <button key={s.label} onClick={() => runSuggestion(s)} style={{
                background: isAdvance ? t.cyan : (dark ? "#1A2333" : "#fff"),
                color: isAdvance ? "#000" : t.cyan,
                border: isAdvance ? "none" : `1px solid ${t.brd}`,
                borderRadius: 999,
                padding: isAdvance ? "12px 20px" : "10px 16px",
                minHeight: "44px",
                fontSize: isAdvance ? 12 : 11,
                fontWeight: isAdvance ? 800 : 600,
                cursor: "pointer",
                fontFamily: "'Pretendard',sans-serif",
              }}>
                {isAdvance ? `${s.label} →` : s.label}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

function ChatBot({ dark, initialConsultation = null, initialConsultationNonce = 0 }) {
  const t = T(dark);
  const [msgs, setMsgs] = useState([{ role: "assistant", content: "안녕, 강차장이야. 🔋\n\n궁금한 주제를 편하게 보내줘.\n핵심부터 짧게 정리해주고,\n관련 카드나 최근 이슈도 같이 찾아줄게." }]);
  const [input, setInput] = useState("");
  // loadingMode: 'none' | 'typing_normal' | 'typing_consult'
  const [loadingMode, setLoadingMode] = useState("none");
  const [searchMode, setSearchMode] = useState("internal");
  const [extQuery, setExtQuery] = useState("");
  const endRef = useRef(null);
  // ChatContext Protocol (Phase 2)
  const chatCtxRef = useRef({ last_turn: null, root_turn: null, selected_item_id: null, region: null, date: null });
  // 현재 active consultation — 후속 유저 메시지는 이 consultation followup으로 처리
  // v2 형태: { id, cardContext, stage1_output, stage2_output, current_stage }
  // current_stage: 0=시작 전, 1/2/3=완료한 stage
  const currentConsultRef = useRef(null);
  // 세션 hook agenda — opener가 선언한 hook을 유저가 탭할 때까지 유지 (legacy v1)
  const sessionHooksRef = useRef([]);          // [{label, hint_action, hint_topic}]
  const usedTopicsRef = useRef(new Set());     // Set<string> (hint_topic)

  // 미사용 opener hook + 서버 hook dedupe 병합 (label 기준) — legacy v1 only
  const composeSessionSuggestions = (serverSugs = []) => {
    const carried = sessionHooksRef.current.filter(
      (h) => h && h.hint_topic && !usedTopicsRef.current.has(h.hint_topic)
    );
    const seen = new Set();
    const out = [];
    for (const s of [...carried, ...(serverSugs || [])]) {
      if (s?.label && !seen.has(s.label)) {
        out.push(s);
        seen.add(s.label);
      }
    }
    return out;
  };

  const isLoading = loadingMode !== "none";

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs, loadingMode]);

  const toUiMessage = (data) => ({
    role: "assistant",
    content: data?.answer || "응답을 생성하지 못했어.",
    sourceBadge: ({ external: "external", hybrid: "hybrid", internal: "internal" }[data?.source_mode] || "internal"),
    cards: Array.isArray(data?.cards) ? data.cards : [],
    braveLinks: Array.isArray(data?.external_links) ? data.external_links : [],
    suggestions: Array.isArray(data?.suggestions) ? data.suggestions : [],
  });

  const updateContextFromResponse = (data) => {
    const nc = data?.next_context || {};
    chatCtxRef.current = {
      last_turn: nc.last_turn || null,
      root_turn: nc.root_turn || chatCtxRef.current.root_turn || null,
      selected_item_id: null,
      region: nc.last_turn?.scope?.region || chatCtxRef.current.region,
      date: nc.last_turn?.scope?.date || chatCtxRef.current.date,
    };
  };

  // typing ceremony — min 500ms 보장, max 2s cap
  const ceremonyWait = async (t0, minMs = 500, maxMs = 2000) => {
    const elapsed = Date.now() - t0;
    if (elapsed >= maxMs) return;
    const wait = Math.max(0, minMs - elapsed);
    if (wait > 0) await new Promise((r) => setTimeout(r, wait));
  };

  // ─── 일반 chat POST ──────────────────────────────────────────────────
  const postChat = async (body) => {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      return {
        answer: err?.answer || "요청 처리 중 오류가 발생했어.",
        answer_type: "general",
        source_mode: "internal",
        confidence: 0,
        cards: [],
        external_links: [],
        suggestions: [
          { label: "오늘 핵심 카드", hint_action: "new_query", hint_topic: "news" },
        ],
        next_context: { last_turn: null, root_turn: chatCtxRef.current.root_turn || null },
      };
    }
    return res.json();
  };

  const sendToChatApi = async (txt, mode = "internal", hint = null) => {
    const body = {
      message: mode === "external" ? `${txt} 외부 기사 링크 중심으로 찾아줘` : txt,
      context: chatCtxRef.current,
    };
    if (hint && (hint.hint_action || hint.hint_topic)) {
      body.hint = {
        action: hint.hint_action || undefined,
        topic: hint.hint_topic || undefined,
      };
    }
    return postChat(body);
  };

  // ─── Consultation v2 — Stage 1 (Scout) opener ─────────────────────────
  const startConsultation = async (init) => {
    if (!init?.cardContext?.card) return;
    currentConsultRef.current = {
      id: init.consultationId,
      cardContext: init.cardContext,
      stage1_output: null,
      stage2_output: null,
      current_stage: 0,
    };

    // 1) 접수증 push
    setMsgs((prev) => [...prev, {
      role: "receipt",
      card_meta: init.card_meta,
      opened_at: init.opened_at,
    }]);

    // 2) Stage 1 (Scout) 호출
    setLoadingMode("typing_consult");
    const t0 = Date.now();
    try {
      const data = await postChat({
        consultation: {
          ...init.cardContext,
          stage: 1,
        },
        ticket_id: init.consultationId,
        context: chatCtxRef.current,
      });
      await ceremonyWait(t0);
      updateContextFromResponse(data);

      if (data?.stage_output) {
        currentConsultRef.current.stage1_output = data.stage_output;
        currentConsultRef.current.current_stage = 1;
      }

      setMsgs((prev) => [...prev, {
        role: "scout",
        stage_output: data?.stage_output || null,
        suggestions: Array.isArray(data?.suggestions) ? data.suggestions : [],
        stage_error: data?.debug?.stage_error || null,
      }]);

      if (init.consultationId) {
        appendMessage(init.consultationId, {
          role: "assistant",
          content: data?.answer || "",
          stage: 1,
        });
      }
    } catch {
      setMsgs((prev) => [...prev, {
        role: "assistant",
        content: "강차장 잠시 자리 비웠어. 잠깐 뒤에 다시 제출해줘.",
        suggestions: [],
      }]);
    } finally {
      setLoadingMode("none");
    }
  };

  // ─── Consultation v2 — Stage advance (2 or 3) ────────────────────────
  const advanceConsultationStage = async (toStage) => {
    const consult = currentConsultRef.current;
    if (!consult) return;
    if (toStage !== 2 && toStage !== 3) return;
    if (toStage === 2 && !consult.stage1_output) return;
    if (toStage === 3 && (!consult.stage1_output || !consult.stage2_output)) return;

    setLoadingMode("typing_consult");
    const t0 = Date.now();
    try {
      const data = await postChat({
        consultation: {
          ...consult.cardContext,
          stage: toStage,
          prev_stage1: consult.stage1_output,
          prev_stage2: toStage === 3 ? consult.stage2_output : undefined,
        },
        ticket_id: consult.id,
        context: chatCtxRef.current,
      });
      await ceremonyWait(t0);
      updateContextFromResponse(data);

      if (data?.stage_output && toStage === 2) {
        currentConsultRef.current.stage2_output = data.stage_output;
        currentConsultRef.current.current_stage = 2;
      } else if (data?.stage_output && toStage === 3) {
        currentConsultRef.current.current_stage = 3;
      }

      const role = toStage === 2 ? "analyst" : "redteam";
      setMsgs((prev) => [...prev, {
        role,
        stage_output: data?.stage_output || null,
        suggestions: Array.isArray(data?.suggestions) ? data.suggestions : [],
        stage_error: data?.debug?.stage_error || null,
      }]);

      if (consult.id) {
        appendMessage(consult.id, {
          role: "assistant",
          content: data?.answer || "",
          stage: toStage,
        });
      }
    } catch {
      setMsgs((prev) => [...prev, {
        role: "assistant",
        content: "강차장 잠시 자리 비웠어. 잠깐 뒤에 다시.",
        suggestions: [],
      }]);
    } finally {
      setLoadingMode("none");
    }
  };

  // ─── Consultation legacy v1 followup (사용 안 됨, Step 4에서 제거) ───
  const sendConsultFollowup = async (txt, consult) => {
    setMsgs((prev) => [...prev, { role: "user", content: txt }]);
    if (consult.id) appendMessage(consult.id, { role: "user", content: txt });

    setLoadingMode("typing_consult");
    const t0 = Date.now();
    try {
      const data = await postChat({
        message: txt,
        consultation: consult.cardContext,
        is_opener: false,
        ticket_id: consult.id,
        context: chatCtxRef.current,
      });
      await ceremonyWait(t0);
      updateContextFromResponse(data);
      const uiMsg = toUiMessage(data);
      uiMsg.suggestions = composeSessionSuggestions(data?.suggestions);
      setMsgs((prev) => [...prev, uiMsg]);
      if (consult.id) appendMessage(consult.id, { role: "assistant", content: data?.answer || "" });
    } catch {
      setMsgs((prev) => [...prev, {
        role: "assistant",
        content: "강차장 잠시 자리 비웠어. 잠깐 뒤에 다시.",
      }]);
    } finally {
      setLoadingMode("none");
    }
  };

  // ─── 일반 chat (loadingMode만 전환) ─────────────────────────────────
  const sendWithText = async (rawText, hint = null) => {
    const txt = String(rawText || "").trim();
    if (!txt || isLoading) return;

    setInput("");

    // v2 consultation 진행 중: 텍스트 입력은 consultation 모드 종료 → 일반 chat fallback
    const consult = currentConsultRef.current;
    if (consult && consult.current_stage > 0) {
      currentConsultRef.current = null;
    } else if (consult) {
      // legacy v1 (current_stage 없음): 기존 followup 흐름 (사실상 안 탐 — v2 진입 시 항상 stage>0)
      await sendConsultFollowup(txt, consult);
      return;
    }

    // 일반 chat
    setMsgs((prev) => [...prev, { role: "user", content: txt }]);
    setLoadingMode("typing_normal");
    try {
      const data = await sendToChatApi(txt, "internal", hint);
      updateContextFromResponse(data);
      setMsgs((prev) => [...prev, toUiMessage(data)]);
    } catch {
      setMsgs((prev) => [...prev, {
        role: "assistant",
        content: "채팅 응답 중 네트워크 오류가 발생했어.",
        suggestions: [
          { label: "오늘 핵심 카드", hint_action: "new_query", hint_topic: "news" },
          { label: "관련 카드 더 보여줘", hint_action: "follow_up" },
        ],
      }]);
    } finally {
      setLoadingMode("none");
    }
  };

  // consultation seed 변경 감지 → opener 시작
  // StrictMode double-invoke 방어: 같은 nonce 재실행 금지
  const consultedNonceRef = useRef(0);
  useEffect(() => {
    if (!initialConsultation || !initialConsultationNonce) return;
    if (consultedNonceRef.current === initialConsultationNonce) return;
    consultedNonceRef.current = initialConsultationNonce;
    void startConsultation(initialConsultation);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialConsultation, initialConsultationNonce]);

  const sendExternal = async (rawText, hint = null) => {
    const txt = String(rawText || "").trim();
    if (!txt || isLoading) return;

    setLoadingMode("typing_normal");
    setExtQuery("");
    setMsgs((prev) => [...prev, { role: "user", content: `🔗 외부 검색: ${txt}` }]);

    try {
      const data = await sendToChatApi(txt, "external", hint);
      updateContextFromResponse(data);
      setMsgs((prev) => [...prev, toUiMessage(data)]);
    } catch {
      setMsgs((prev) => [...prev, {
        role: "assistant",
        content: "외부 검색 응답 중 네트워크 오류가 발생했어.",
        suggestions: [{ label: "내부 카드로 검색", hint_action: "new_query" }],
      }]);
    } finally {
      setLoadingMode("none");
    }
  };

  const markCardSelected = (card) => {
    const id = card?.url || card?.title || null;
    if (!id) return;
    chatCtxRef.current = { ...chatCtxRef.current, selected_item_id: id };
  };

  const runSuggestion = (suggestion) => {
    const label = typeof suggestion === "string" ? suggestion : (suggestion?.label || "");
    const hint = typeof suggestion === "object" ? suggestion : null;

    // ★ v2: advance_stage hint
    if (hint?.hint_action === "advance_stage" && hint?.hint_stage) {
      void advanceConsultationStage(hint.hint_stage);
      return;
    }

    // 세션 agenda 탭 추적 — legacy v1 consultation일 때만 의미 있음
    const tappedTopic = hint?.hint_topic;
    if (tappedTopic && currentConsultRef.current && !currentConsultRef.current.current_stage) {
      usedTopicsRef.current.add(tappedTopic);
    }
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
    const isExternalLabel = label === "외부 기사 링크 검색" || label.includes("외부 검색");
    if (searchMode === "external" || isExternalLabel) {
      void sendExternal(next, hint);
      return;
    }
    void sendWithText(next, hint);
  };

  // input placeholder 동적 — consultation v2 진행 중이면 안내 변경
  const consult = currentConsultRef.current;
  const consultActive = !!consult && consult.current_stage > 0;

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "calc(100vh - 190px)" }}>
      <div role="log" aria-live="polite" aria-atomic="false" aria-label="대화 내역" style={{ flex: 1, overflowY: "auto", padding: "12px 14px 8px" }}>
        {msgs.length <= 1 && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginTop: 6, marginBottom: 12 }}>
            {quickPrimary.map((q) => (
              <button key={q} onClick={() => runSuggestion(q)} style={{ background: dark ? "#1A2333" : "#FFFFFF", border: `1px solid ${t.brd}`, borderRadius: 999, padding: "12px 16px", minHeight: "44px", fontSize: 12, color: t.tx, cursor: "pointer", fontFamily: "'Pretendard',sans-serif", fontWeight: 600, textAlign: "left" }}>{q}</button>
            ))}
          </div>
        )}

        {msgs.map((m, i) => {
          // 접수증 (receipt) 렌더 — user/assistant 풍선 아님
          if (m.role === "receipt") {
            return <ReceiptBubble key={`receipt-${i}`} meta={m.card_meta} openedAt={m.opened_at} dark={dark} />;
          }
          // v2 stage bubbles
          if (m.role === "scout") {
            return <StageWrapper key={`scout-${i}`} m={m} dark={dark} runSuggestion={runSuggestion} BubbleComponent={ScoutBubble} errorFallback="1차 접수 중에 문제가 있었어. 다시 시도해줘." />;
          }
          if (m.role === "analyst") {
            return <StageWrapper key={`analyst-${i}`} m={m} dark={dark} runSuggestion={runSuggestion} BubbleComponent={AnalystBubble} errorFallback="2차 분석 중에 문제가 있었어. 다시 시도해줘." />;
          }
          if (m.role === "redteam") {
            return <StageWrapper key={`redteam-${i}`} m={m} dark={dark} runSuggestion={runSuggestion} BubbleComponent={RedTeamBubble} errorFallback="3차 검증 중에 문제가 있었어. 다시 시도해줘." />;
          }
          return (
            <div key={i} role="article" aria-label={m.role === "user" ? "내 질문" : "AI 답변"} style={{ display: "flex", flexDirection: "column", alignItems: m.role === "user" ? "flex-end" : "flex-start", marginBottom: 10 }}>
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
                    {m.sourceBadge === "hybrid" && (
                      <span style={{ display: "inline-block", fontSize: 10, fontWeight: 800, color: "#A855F7", background: dark ? "rgba(168,85,247,0.14)" : "rgba(168,85,247,0.10)", padding: "3px 8px", borderRadius: 999, marginBottom: 6, fontFamily: "'JetBrains Mono',monospace" }}>
                        🔀 내부+외부 근거
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
                      ? <a key={j} href={card.url} target="_blank" rel="noopener noreferrer" aria-label={`Open article: ${card.title}`} onClick={() => markCardSelected(card)} style={cardStyle}>{cardContent}</a>
                      : <div key={j} style={cardStyle} onClick={() => markCardSelected(card)}>{cardContent}</div>;
                  })}
                </div>
              </div>
              {m.role === "assistant" && m.suggestions?.length > 0 && (
                <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 8, marginBottom: 4, paddingLeft: 35 }}>
                  {m.suggestions.map((s) => (
                    <button key={s.label} onClick={() => runSuggestion(s)} style={{ background: dark ? "#1A2333" : "#fff", border: `1px solid ${t.brd}`, borderRadius: 999, padding: "10px 16px", minHeight: "44px", fontSize: 11, color: t.cyan, cursor: "pointer", fontFamily: "'Pretendard',sans-serif", fontWeight: 600 }}>{s.label}</button>
                  ))}
                </div>
              )}
            </div>
          );
        })}

        {isLoading && (
          <div role="status" aria-live="polite" aria-atomic="true" style={{ display: "flex", gap: 7, marginBottom: 10 }}>
            <img src="/data/kang.png" alt="강차장" style={{ width: 28, height: 28, borderRadius: 14, flexShrink: 0, border: "2px solid #2a1a40" }} />
            <div style={{ padding: "10px 14px", borderRadius: "18px 18px 18px 6px", background: dark ? "#1A2333" : "#FFFFFF", border: `1px solid ${t.brd}`, fontSize: 12, color: t.sub }}>
              {loadingMode === "typing_consult" ? "검토 중..." : "찾아보는 중..."}
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>
      <div style={{ padding: "8px 12px 14px", background: "#0A0E14", borderTop: `1px solid ${t.brd}` }}>
        <div style={{ display: "flex", gap: 0, marginBottom: 8, background: dark ? "#151B26" : "#f0f0f5", borderRadius: 8, padding: 2 }}>
          <button onClick={() => setSearchMode("internal")} style={{ flex: 1, padding: "6px 0", borderRadius: 6, border: "none", background: searchMode === "internal" ? (dark ? "#1A2333" : "#fff") : "transparent", color: searchMode === "internal" ? "#58A6FF" : t.sub, fontSize: 11, fontWeight: 700, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace", boxShadow: searchMode === "internal" ? "0 1px 3px rgba(0,0,0,0.15)" : "none", transition: "all 0.15s" }}>📋 내부 카드</button>
          <button onClick={() => setSearchMode("external")} style={{ flex: 1, padding: "6px 0", borderRadius: 6, border: "none", background: searchMode === "external" ? (dark ? "#1A2333" : "#fff") : "transparent", color: searchMode === "external" ? "#D29922" : t.sub, fontSize: 11, fontWeight: 700, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace", boxShadow: searchMode === "external" ? "0 1px 3px rgba(0,0,0,0.15)" : "none", transition: "all 0.15s" }}>🔗 외부 기사</button>
        </div>
        <div style={{ display: "flex", gap: 6 }}>
          <input
            type="text"
            value={searchMode === "external" ? extQuery : input}
            onChange={(e) => searchMode === "external" ? setExtQuery(e.target.value) : setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                searchMode === "external" ? void sendExternal(extQuery) : void sendWithText(input);
              }
            }}
            placeholder={
              searchMode === "external"
                ? "외부 기사 검색어 입력 (예: LFP 화재 리스크)"
                : consultActive
                  ? "다음 단계 버튼 → 또는 자유롭게 질문해"
                  : "궁금한 주제를 입력해줘"
            }
            aria-label={searchMode === "internal" ? "Ask AI assistant" : "Search external articles"}
            style={{ flex: 1, padding: "12px 14px", minHeight: "44px", borderRadius: 10, border: `1px solid ${searchMode === "external" ? (dark ? "rgba(210,153,34,0.3)" : "rgba(210,153,34,0.2)") : t.brd}`, background: searchMode === "external" ? (dark ? "#1A1E2A" : "#FFFBF0") : t.card2, color: t.tx, fontSize: 13, outline: "none", fontFamily: "'Pretendard',sans-serif" }}
          />
          <button
            onClick={() => searchMode === "external" ? void sendExternal(extQuery) : void sendWithText(input)}
            disabled={isLoading || (searchMode === "external" ? !extQuery.trim() : !input.trim())}
            aria-label={searchMode === "external" ? "Search external articles" : "Send message"}
            style={{ padding: "12px 18px", minHeight: "44px", minWidth: "44px", borderRadius: 10, border: "none", background: searchMode === "external" ? "#D29922" : t.cyan, color: "#000", fontWeight: 800, cursor: "pointer", fontSize: 13, fontFamily: "'Pretendard',sans-serif" }}
          >
            {searchMode === "external" ? "🔍" : "→"}
          </button>
        </div>
      </div>
    </div>
  );
}


function TrackerItemCard({ item, dark, expanded, onToggle }) {
  const t = T(dark);
  const flag = TRACKER_REGION[item.r]?.flag || "🌐";
  const regionName = TRACKER_REGION[item.r]?.name || item.r;
  const statusColor = SC[item.s] || t.tx;
  const statusLabel = SL[item.s] || item.s;
  const sources = Array.isArray(item.src) ? item.src : [];
  const hasDetail = item.detail && String(item.detail).trim().length > 0;

  return (
    <div style={{
      background: t.card2,
      borderRadius: 10,
      border: `1px solid ${t.brd}`,
      borderLeft: `3px solid ${statusColor}`,
      padding: "12px 14px",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap", marginBottom: 6 }}>
        <span style={{ fontSize: 9, fontWeight: 800, color: statusColor, background: `${statusColor}22`, padding: "2px 7px", borderRadius: 999, fontFamily: "'JetBrains Mono',monospace" }}>{statusLabel}</span>
        {item.id && <span style={{ fontSize: 9, color: t.sub, fontFamily: "'JetBrains Mono',monospace", fontWeight: 700 }}>{item.id}</span>}
        <span style={{ fontSize: 12 }}>{flag}</span>
        <span style={{ fontSize: 9, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>{regionName}</span>
        {item.dt && <span style={{ fontSize: 9, color: t.sub, marginLeft: "auto", fontFamily: "'JetBrains Mono',monospace", fontWeight: 700 }}>{fmtDate(item.dt)}</span>}
      </div>

      <h3 style={{ fontSize: 13, fontWeight: 800, color: t.tx, margin: "0 0 6px", lineHeight: 1.4 }}>{item.t}</h3>

      {item.d && <p style={{ fontSize: 11, color: t.sub, margin: "0 0 8px", lineHeight: 1.6 }}>{item.d}</p>}

      {item.tip && (
        <div style={{
          background: dark ? "rgba(210,153,34,0.07)" : "rgba(210,153,34,0.05)",
          borderLeft: "2px solid #D29922",
          padding: "6px 10px",
          borderRadius: "0 6px 6px 0",
          marginBottom: 8,
        }}>
          <span style={{ fontSize: 10, color: "#D29922", fontWeight: 800, fontFamily: "'JetBrains Mono',monospace" }}>💡 </span>
          <span style={{ fontSize: 11, color: t.tx, lineHeight: 1.5 }}>{item.tip}</span>
        </div>
      )}

      {sources.length > 0 && (
        <div style={{ marginBottom: 8, display: "flex", flexWrap: "wrap", gap: 4 }}>
          {sources.map((s, i) => {
            const label = s.n || s.label || s.name || `source ${i + 1}`;
            const url = s.u || s.url || s.href;
            if (!url) return null;
            return (
              <a key={i} href={url} target="_blank" rel="noopener noreferrer" style={{
                fontSize: 10,
                color: t.cyan,
                padding: "4px 9px",
                borderRadius: 999,
                background: dark ? "rgba(88,166,255,0.10)" : "rgba(88,166,255,0.06)",
                textDecoration: "none",
                fontFamily: "'JetBrains Mono',monospace",
                fontWeight: 700,
                border: `1px solid ${dark ? "rgba(88,166,255,0.2)" : "rgba(88,166,255,0.15)"}`,
              }}>📎 {label} ↗</a>
            );
          })}
        </div>
      )}

      {hasDetail && (
        <>
          <button onClick={onToggle} style={{
            fontSize: 10,
            color: t.cyan,
            background: "transparent",
            border: `1px solid ${t.brd}`,
            borderRadius: 6,
            cursor: "pointer",
            fontFamily: "'JetBrains Mono',monospace",
            padding: "6px 10px",
            fontWeight: 700,
          }}>{expanded ? "△ 자세히 접기" : "▽ 자세히 보기"}</button>
          {expanded && (
            <div style={{
              marginTop: 8,
              padding: "10px 12px",
              background: dark ? "rgba(88,166,255,0.05)" : "rgba(88,166,255,0.03)",
              borderRadius: 8,
              border: `1px solid ${dark ? "rgba(88,166,255,0.12)" : "rgba(88,166,255,0.08)"}`,
              fontSize: 11,
              color: t.tx,
              lineHeight: 1.7,
              whiteSpace: "pre-line",
            }}>{item.detail}</div>
          )}
        </>
      )}

      {(item.lastChecked || item.checkNote) && (
        <div style={{
          fontSize: 9,
          color: t.sub,
          marginTop: 10,
          paddingTop: 7,
          borderTop: `1px solid ${t.brd}`,
          fontFamily: "'JetBrains Mono',monospace",
          lineHeight: 1.5,
        }}>
          🔍 {item.lastChecked ? `last checked: ${fmtDate(item.lastChecked)}` : "check note"}
          {item.checkNote && <span> — {item.checkNote}</span>}
        </div>
      )}
    </div>
  );
}

function Tracker({ tracker, dark }) {
  const t = T(dark);
  const d = tracker;
  const updatedLabel = fmtDate(d.meta.lastUpdated);
  const [expandedRegion, setExpandedRegion] = useState(null);
  const [expandedItemId, setExpandedItemId] = useState(null);
  const [statusFilter, setStatusFilter] = useState("all");
  const [regionFilter, setRegionFilter] = useState("all");
  const [search, setSearch] = useState("");

  const toggleRegion = (code) => {
    setExpandedRegion((prev) => (prev === code ? null : code));
  };

  const policyData = REGION_POLICY[expandedRegion] || null;

  // ITEMS filtering + sorting
  const statusRank = { ACTIVE: 0, UPCOMING: 1, WATCH: 2, DONE: 3 };
  const filteredItems = useMemo(() => {
    const sw = search.trim().toLowerCase();
    return (d.items || [])
      .filter((it) => {
        if (statusFilter !== "all" && it.s !== statusFilter) return false;
        if (regionFilter !== "all" && it.r !== regionFilter) return false;
        if (sw) {
          const hay = [it.id, it.t, it.d, it.tip, it.detail].filter(Boolean).join(" ").toLowerCase();
          if (!hay.includes(sw)) return false;
        }
        return true;
      })
      .sort((a, b) => {
        const sa = statusRank[a.s] ?? 9;
        const sb = statusRank[b.s] ?? 9;
        if (sa !== sb) return sa - sb;
        // UPCOMING: ascending by date; others: descending
        const da = String(a.dt || "");
        const db = String(b.dt || "");
        if (a.s === "UPCOMING") return da.localeCompare(db);
        return db.localeCompare(da);
      });
  }, [d.items, statusFilter, regionFilter, search]);

  const regionFilterOptions = ["all", ...Object.keys(TRACKER_REGION).filter((code) => (d.items || []).some((it) => it.r === code))];
  const statusFilterOptions = ["all", "ACTIVE", "UPCOMING", "WATCH", "DONE"];

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
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}><span style={{ fontSize: 10, color: "#3a6090", fontFamily: "'JetBrains Mono',monospace" }}>REGIONS — 클릭하면 권역 개요</span><div style={{ flex: 1, height: 1, background: t.brd }} /></div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
          {d.regions.map((r) => {
            const isExpanded = expandedRegion === r.code;
            return (
              <div key={r.code} onClick={() => toggleRegion(r.code)} style={{ background: isExpanded ? (dark ? "#1A2333" : "#EEF3FF") : t.card2, borderRadius: 8, padding: "10px 12px", border: `1px solid ${isExpanded ? t.cyan : t.brd}`, cursor: "pointer", transition: "border 0.2s" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}><span style={{ fontSize: 14 }}>{r.flag}</span><span style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>{r.ACTIVE} ACTIVE</span></div>
                <div style={{ fontSize: 13, fontWeight: 700, color: t.tx, marginTop: 4 }}>{r.name}</div>
                <div style={{ marginTop: 6, height: 3, borderRadius: 2, background: t.brd }}><div style={{ height: "100%", borderRadius: 2, background: SC.ACTIVE, width: pct(r.ACTIVE, r.total) }} /></div>
                <div style={{ fontSize: 9, color: isExpanded ? t.cyan : t.sub, marginTop: 4, fontFamily: "'JetBrains Mono',monospace", textAlign: "center" }}>{isExpanded ? "△ 접기" : "▽ 개요 보기"}</div>
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
          <div style={{ marginTop: 10, fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace", fontStyle: "italic" }}>※ 위 내용은 권역 개요이며, 개별 정책 항목은 아래 POLICY ITEMS에서 확인하세요.</div>
        </div>
      )}

      {/* POLICY ITEMS — 개별 정책 카드 전체 렌더링 */}
      <div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
          <span style={{ fontSize: 10, color: "#3a6090", fontFamily: "'JetBrains Mono',monospace" }}>POLICY ITEMS — {filteredItems.length} / {d.items.length}</span>
          <div style={{ flex: 1, height: 1, background: t.brd }} />
        </div>

        {/* 검색 */}
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="🔍 정책 검색 (제목·설명·ID)..."
          aria-label="Search policy items"
          style={{
            width: "100%",
            padding: "10px 14px",
            borderRadius: 10,
            border: `1px solid ${t.brd}`,
            fontSize: 12,
            outline: "none",
            fontFamily: "inherit",
            background: t.card2,
            color: t.tx,
            boxSizing: "border-box",
            marginBottom: 8,
          }}
        />

        {/* 상태 필터 */}
        <div style={{ position: "relative", marginBottom: 6 }}>
          <div style={{ display: "flex", gap: 4, overflowX: "auto", paddingBottom: 4, scrollbarWidth: "thin" }}>
            {statusFilterOptions.map((s) => {
              const active = statusFilter === s;
              const label = s === "all" ? `ALL ${d.items.length}` : `${SL[s] || s} ${d.summary[s] || 0}`;
              const color = s === "all" ? t.cyan : (SC[s] || t.cyan);
              return (
                <button key={s} onClick={() => setStatusFilter(s)} style={{
                  background: active ? color : t.card2,
                  color: active ? "#000" : t.sub,
                  border: `1px solid ${active ? "transparent" : t.brd}`,
                  borderRadius: 999,
                  padding: "8px 12px",
                  minHeight: "36px",
                  fontSize: 10,
                  fontWeight: 700,
                  cursor: "pointer",
                  whiteSpace: "nowrap",
                  fontFamily: "'JetBrains Mono',monospace",
                }}>{label}</button>
              );
            })}
          </div>
        </div>

        {/* 권역 필터 */}
        <div style={{ position: "relative", marginBottom: 10 }}>
          <div style={{ display: "flex", gap: 4, overflowX: "auto", paddingBottom: 4, scrollbarWidth: "thin" }}>
            {regionFilterOptions.map((r) => {
              const active = regionFilter === r;
              const label = r === "all" ? "ALL REGIONS" : `${TRACKER_REGION[r]?.flag || "🌐"} ${TRACKER_REGION[r]?.name || r}`;
              return (
                <button key={r} onClick={() => setRegionFilter(r)} style={{
                  background: active ? t.cyan : t.card2,
                  color: active ? "#000" : t.sub,
                  border: `1px solid ${active ? "transparent" : t.brd}`,
                  borderRadius: 999,
                  padding: "8px 12px",
                  minHeight: "36px",
                  fontSize: 10,
                  fontWeight: 700,
                  cursor: "pointer",
                  whiteSpace: "nowrap",
                  fontFamily: "'JetBrains Mono',monospace",
                }}>{label}</button>
              );
            })}
          </div>
        </div>

        {filteredItems.length === 0 ? (
          <div style={{ padding: "20px", borderRadius: 10, background: t.card2, border: `1px solid ${t.brd}`, textAlign: "center" }}>
            <div style={{ fontSize: 24, marginBottom: 8 }}>🔍</div>
            <div style={{ fontSize: 12, color: t.sub, lineHeight: 1.5 }}>조건에 맞는 정책이 없습니다.</div>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {filteredItems.map((item) => (
              <TrackerItemCard
                key={item.id || `${item.r}-${item.t}`}
                item={item}
                dark={dark}
                expanded={expandedItemId === (item.id || `${item.r}-${item.t}`)}
                onToggle={() => {
                  const key = item.id || `${item.r}-${item.t}`;
                  setExpandedItemId((prev) => (prev === key ? null : key));
                }}
              />
            ))}
          </div>
        )}
      </div>

      <div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}><span style={{ fontSize: 10, color: "#3a6090", fontFamily: "'JetBrains Mono',monospace" }}>KEY DATES</span><div style={{ flex: 1, height: 1, background: t.brd }} /></div>
        <div style={{ background: t.card2, borderRadius: 8, padding: "4px 0", border: `1px solid ${t.brd}` }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 12px 6px", borderBottom: `1px solid ${t.brd}` }}>
            <span style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>WATCHLIST — UPCOMING TOP 8</span>
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

function NewsDesk({ kb, onSubmitConsultation, consultSummaries = {}, dark }) {
  const t = T(dark);
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [showCount, setShowCount] = useState(60);
  const regions = ["all", "top", "high", "KR", "US", "CN", "EU", "JP"];

  let cards = filter === "all" ? kb.cards : filter === "top" ? kb.cards.filter((c) => c.s === "t") : filter === "high" ? kb.cards.filter((c) => c.s === "h") : kb.cards.filter((c) => c.r === filter);

  if (search) {
    const sw = search.toLowerCase();
    cards = cards.filter((c) => {
      if (String(c.T || "").toLowerCase().includes(sw)) return true;
      if (String(c.sub || "").toLowerCase().includes(sw)) return true;
      if (String(c.g || "").toLowerCase().includes(sw)) return true;
      // A3/F5: keyword 배열(c.k)도 검색 대상 — FAQ/시그널 키워드 hit 보장.
      if (Array.isArray(c.k) && c.k.some((k) => String(k).toLowerCase().includes(sw))) return true;
      return false;
    });
  }

  const rank = { t: 3, h: 2, m: 1, i: 0 };
  cards = [...cards].sort((a, b) => {
    const da = String(a.d || "");
    const db = String(b.d || "");
    if (db !== da) return db.localeCompare(da);   // 최신 날짜 먼저
    return (rank[b.s] || 0) - (rank[a.s] || 0);   // 같은 날짜면 TOP/HIGH 우선
  });

  const visible = cards.slice(0, showCount);
  const dates = [...new Set(visible.map((c) => c.d))];
  const todayHighlights = latestCards(kb.cards, 4, null, kstToday());
  const highlights = todayHighlights.length ? todayHighlights : latestCards(kb.cards, 4, null, null);
  const highlightsIsToday = todayHighlights.length > 0;
  return (
    <div style={{ padding: "0 14px 110px", display: "flex", flexDirection: "column", gap: 12 }}>
      <div style={{ background: t.card2, borderRadius: 14, padding: 16, border: `1px solid ${t.brd}` }}>
        <h2 style={{ fontSize: 22, fontWeight: 900, color: t.tx, margin: "0 0 6px", lineHeight: 1.25 }}>날짜별 시그널 피드</h2>
        <p style={{ fontSize: 12, color: t.sub, margin: 0, lineHeight: 1.6 }}>최신 카드부터 날짜 기준으로 정렬했습니다. 같은 날짜 안에서는 중요도가 높은 이슈를 먼저 보여줍니다.</p>
      </div>
      <div style={{ background: t.card2, borderRadius: 14, padding: 16, border: `1px solid ${t.brd}` }}>
        <div style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginBottom: 4 }}>EDITOR'S PICKS</div>
        <h3 style={{ fontSize: 18, fontWeight: 900, color: t.tx, margin: "0 0 12px" }}>
          {highlightsIsToday ? "오늘의 핵심 카드" : "최신 핵심 카드"}
        </h3>
        {highlights.length
          ? <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {highlights.map((card, i) => (
                <StoryNewsItem
                  key={`${card.id || card.T || card.title}-${i}`}
                  card={card}
                  dark={dark}
                  onSubmitConsultation={onSubmitConsultation}
                  consultationHint={consultSummaries[getCardId(card)] || null}
                />
              ))}
            </div>
          : <div style={{ fontSize: 12, color: t.sub, lineHeight: 1.6 }}>오늘 기준 등록된 뉴스카드가 아직 없습니다.</div>}
      </div>
      <div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="🔍 카드 검색..."
            aria-label="Search cards by title, description, or content"
            style={{
              flex: 1,
              padding: "10px 14px",
              borderRadius: 10,
              border: `1px solid ${t.brd}`,
              fontSize: 12,
              outline: "none",
              fontFamily: "inherit",
              background: t.card2,
              color: t.tx,
              boxSizing: "border-box"
            }}
          />
          {(search || filter !== "all") && (
            <div style={{
              padding: "8px 12px",
              borderRadius: 8,
              background: cards.length === 0 ? "rgba(248,81,73,0.1)" : t.card,
              border: `1px solid ${cards.length === 0 ? "rgba(248,81,73,0.3)" : t.brd}`,
              fontSize: 11,
              fontWeight: 800,
              color: cards.length === 0 ? "#F85149" : t.cyan,
              fontFamily: "'JetBrains Mono',monospace",
              whiteSpace: "nowrap"
            }}>
              {cards.length}개 결과
            </div>
          )}
        </div>
        {cards.length === 0 && (search || filter !== "all") && (
          <div style={{
            padding: "16px",
            borderRadius: 10,
            background: t.card,
            border: `1px solid ${t.brd}`,
            textAlign: "center"
          }}>
            <div style={{ fontSize: 24, marginBottom: 8 }}>🔍</div>
            <div style={{ fontSize: 13, fontWeight: 700, color: t.tx, marginBottom: 4 }}>
              검색 결과가 없습니다
            </div>
            <div style={{ fontSize: 11, color: t.sub, lineHeight: 1.6 }}>
              다른 검색어나 필터를 시도해보세요
            </div>
          </div>
        )}
      </div>
      <div style={{ position: "relative" }}>
        <div style={{ display: "flex", gap: 4, overflowX: "auto", paddingBottom: 4, scrollbarWidth: "thin" }}>
          {regions.map((r) => {
            const label = r === "all" ? `ALL ${kb.cardCount}` : r === "top" ? "TOP" : r === "high" ? "HIGH" : r;
            return <button key={r} onClick={() => { setFilter(r); setShowCount(60); }} style={{ background: filter === r ? t.cyan : t.card2, color: filter === r ? "#000" : t.sub, border: `1px solid ${filter === r ? "transparent" : t.brd}`, borderRadius: 999, padding: "10px 14px", minHeight: "44px", fontSize: 10, fontWeight: 700, cursor: "pointer", whiteSpace: "nowrap", fontFamily: "'JetBrains Mono',monospace" }}>{label}</button>;
          })}
        </div>
        <div style={{ position: "absolute", right: 0, top: 0, bottom: 0, width: "32px", background: `linear-gradient(to left, ${t.bg}, transparent)`, pointerEvents: "none" }} />
      </div>
      {dates.map((date) => (
        <div key={date}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}><span style={{ fontSize: 10, color: "#3a6090", fontFamily: "'JetBrains Mono',monospace" }}>{fmtDate(date)}</span><div style={{ flex: 1, height: 1, background: t.brd }} /></div>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {visible.filter((c) => c.d === date).map((card, i) => (
              <StoryNewsItem
                key={`${card.id || date}-${i}`}
                card={card}
                dark={dark}
                onSubmitConsultation={onSubmitConsultation}
                consultationHint={consultSummaries[getCardId(card)] || null}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function AppContent() {
  const [tab, setTab] = useState("all");
  const [dark, setDark] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);
  const [hardRefresh, setHardRefresh] = useState(false);
  const [refreshPending, setRefreshPending] = useState(false);
  const [refreshLabel, setRefreshLabel] = useState("");
  const [consultationSeed, setConsultationSeed] = useState({ data: null, nonce: 0 });
  const [consultSummaries, setConsultSummaries] = useState(() =>
    typeof window !== "undefined" ? getAllCardConsultationSummaries() : {}
  );
  const kb = useKnowledgeBase(refreshKey, hardRefresh);
  const { tracker, loading: trackerLoading } = useTrackerData(refreshKey, hardRefresh);
  const t = T(dark);
  const lastCardDate = latestDate(kb.cards) || "-";

  useEffect(() => {
    if (!refreshPending || kb.loading || trackerLoading) return;

    setRefreshLabel(hardRefresh ? "강력 새로고침 완료" : "새로고침 완료");
    setRefreshPending(false);
    if (hardRefresh) setHardRefresh(false);

    const timer = window.setTimeout(() => setRefreshLabel(""), 2200);
    return () => window.clearTimeout(timer);
  }, [refreshPending, kb.loading, trackerLoading, hardRefresh]);

  const triggerRefresh = async (mode = "soft") => {
    if (kb.loading || trackerLoading || refreshPending) return;

    const nextHard = mode === "hard";
    setRefreshLabel(nextHard ? "강력 새로고침 중..." : "새로고침 중...");

    if (nextHard) {
      try {
        await clearBrowserCaches();
      } catch (error) {
        console.error("Cache clear error:", error);
      }
    }

    setHardRefresh(nextHard);
    setRefreshPending(true);
    setRefreshKey(Date.now());
  };

  const handleSubmitConsultation = (card) => {
    if (!card) return;

    // 1) build context on client (cards.json + recent openers for few-shot 배제)
    const recentOpenerIds = getRecentOpenerIds(5);
    const cardContext = buildCardConsultContext({
      card,
      allCards: kb.cards,
      recentOpenerIds,
    });
    if (!cardContext) return;

    // 2) create consultation record in localStorage
    const created = createConsultation({
      card,
      openerCategory: cardContext.opener_category,
      openerIdUsed: null,
    });
    if (!created) return;

    // 3) seed ChatBot (nonce로 재트리거)
    setConsultationSeed({
      data: {
        consultationId: created.id,
        cardContext,
        card_meta: created.card_meta,
        opened_at: created.opened_at,
      },
      nonce: Date.now(),
    });

    // 4) B안 footer 즉시 반영
    setConsultSummaries(getAllCardConsultationSummaries());

    // 5) chatbot tab 전환
    setTab("chatbot");
  };

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
      <style dangerouslySetInnerHTML={{ __html: `@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&display=swap');body{margin:0;background:${t.bg}}*{box-sizing:border-box}button:focus-visible,a:focus-visible,input:focus-visible{outline:2px solid #58A6FF;outline-offset:2px}.skip-link{position:absolute;left:-9999px;z-index:999;padding:12px 20px;background:#58A6FF;color:#000;text-decoration:none;font-weight:800;border-radius:8px;font-size:14px}.skip-link:focus{left:50%;transform:translateX(-50%);top:10px}` }} />

      {/* Skip to main content link */}
      <a href="#main-content" className="skip-link">
        메인 콘텐츠로 이동
      </a>

      <div style={{ background: "#161B26", padding: "14px 16px 16px", position: "relative", borderBottom: `1px solid #21293A` }}>
        <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: "linear-gradient(90deg,#58A6FF,#BC8CFF,#58A6FF)" }} />
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <img src="/data/logo_light.png" alt="SBTL" style={{ height: 32, objectFit: "contain" }} onError={(e) => { e.currentTarget.style.display = "none"; }} />
            <div style={{ display: "flex", alignItems: "center", gap: 4, background: "#0B2A0B", borderRadius: 4, padding: "2px 7px" }}><div style={{ width: 5, height: 5, borderRadius: 3, background: "#3FB950" }} /><span style={{ fontSize: 9, color: "#3FB950", fontFamily: "'JetBrains Mono',monospace", fontWeight: 700 }}>LIVE</span></div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: 10, color: "#7D8590", fontFamily: "'JetBrains Mono',monospace" }}>{kb.cardCount}</span>
            <button
              onClick={() => void triggerRefresh("soft")}
              disabled={kb.loading || trackerLoading || refreshPending}
              title="최신 데이터 다시 불러오기"
              aria-label="Refresh latest data"
              style={{
                background: "#21293A",
                border: "none",
                borderRadius: 8,
                minWidth: 44,
                minHeight: 44,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: kb.loading || trackerLoading || refreshPending ? "not-allowed" : "pointer",
                fontSize: 14,
                color: "#E6EDF3",
                opacity: kb.loading || trackerLoading || refreshPending ? 0.45 : 1,
              }}
            >
              ↻
            </button>
            <button
              onClick={() => void triggerRefresh("hard")}
              disabled={kb.loading || trackerLoading || refreshPending}
              title="캐시까지 무시하고 강하게 다시 불러오기"
              aria-label="Hard refresh latest data"
              style={{
                background: "#21293A",
                border: "1px solid rgba(248,81,73,0.35)",
                borderRadius: 8,
                minWidth: 44,
                minHeight: 44,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: kb.loading || trackerLoading || refreshPending ? "not-allowed" : "pointer",
                fontSize: 14,
                color: "#F85149",
                opacity: kb.loading || trackerLoading || refreshPending ? 0.45 : 1,
              }}
            >
              ⚡
            </button>
            <button onClick={() => setDark(!dark)} aria-label={dark ? "Switch to light mode" : "Switch to dark mode"} style={{ background: "#21293A", border: "none", borderRadius: 8, minWidth: 44, minHeight: 44, display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", fontSize: 16 }}>{dark ? "☀️" : "🌙"}</button>
          </div>
        </div>
        <div style={{ marginTop: 10 }}>
          {tab !== "all" && <h1 style={{ color: "#E6EDF3", fontSize: 18, fontWeight: 800, margin: 0 }}>{headerTitle}</h1>}
          <p style={{ color: "#7D8590", fontSize: 10, margin: "2px 0 0", fontFamily: "'JetBrains Mono',monospace" }}>{headerSub}</p>
          {refreshLabel && (
            <p style={{ color: refreshLabel.includes("강력") ? "#F85149" : "#58A6FF", fontSize: 10, margin: "6px 0 0", fontFamily: "'JetBrains Mono',monospace" }}>
              {refreshLabel}
            </p>
          )}
        </div>
      </div>

      <main id="main-content" role="main" aria-label="SBTL 콘텐츠 허브">
        {tab === "all" && <div style={{ paddingTop: 10 }}><Home kb={kb} tracker={tracker} onNav={setTab} onSubmitConsultation={handleSubmitConsultation} consultSummaries={consultSummaries} dark={dark} /></div>}
        {tab === "news" && <NewsDesk kb={kb} onSubmitConsultation={handleSubmitConsultation} consultSummaries={consultSummaries} dark={dark} />}
        {tab === "chatbot" && <ChatBot dark={dark} initialConsultation={consultationSeed.data} initialConsultationNonce={consultationSeed.nonce} />}
        {tab === "tracker" && <div style={{ paddingTop: 10 }}><Tracker tracker={tracker} dark={dark} /></div>}
        {tab === "webtoon" && <WebtoonLibrary dark={dark} />}
      </main>

      <div style={{ position: "fixed", bottom: 0, left: "50%", transform: "translateX(-50%)", width: "100%", maxWidth: 480, background: dark ? t.card : "#fff", borderTop: `1px solid ${t.brd}`, display: "flex", paddingBottom: "env(safe-area-inset-bottom, 8px)" }} role="navigation" aria-label="Main navigation">
        {CATS.map((cat) => {
          const active = tab === cat.key;
          return (
            <button key={cat.key} onClick={() => setTab(cat.key)} aria-label={`Navigate to ${cat.label}`} aria-current={active ? "page" : undefined} style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 2, padding: "8px 0", minHeight: "56px", cursor: "pointer", border: "none", background: "transparent", flex: 1, position: "relative" }}>
              {active && <div style={{ position: "absolute", top: 0, left: "50%", transform: "translateX(-50%)", width: 20, height: 2, borderRadius: 1, background: t.cyan }} />}
              <span style={{ fontSize: 22, lineHeight: 1, filter: active ? "none" : "grayscale(0.3) opacity(0.7)" }} aria-hidden="true">{cat.icon}</span>
              <span style={{ fontSize: 9, fontWeight: active ? 700 : 500, color: active ? t.cyan : t.sub, fontFamily: "'JetBrains Mono',monospace" }}>{cat.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

// Export App wrapped in Error Boundary
export default function App() {
  const [dark, setDark] = useState(true);

  return (
    <ErrorBoundary dark={dark}>
      <AppContent />
    </ErrorBoundary>
  );
}
