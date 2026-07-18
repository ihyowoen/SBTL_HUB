import { useEffect, useMemo, useRef, useState, Component } from "react";
import { computeBriefAxes, computeRegionAxes, computeThemeAxes, computeCustomAxes, customAxisCandidates, REGION_AXIS_KEYS, THEME_AXIS_KEYS, cardInMonth, parseBriefSections } from "./briefAxes";
import { buildPinGraph, layoutPinGraph, PIN_GRAPH_MAX_NODES } from "./pinboard";
import StoryNewsItem from "./story/StoryNewsItem";
import { buildCardConsultContext } from "./story/buildCardConsultContext";
import { getCardId } from "./story/normalizeCard";
import {
  createConsultation,
  appendMessage,
  getAllCardConsultationSummaries,
  getRecentOpenerIds,
} from "./consultation/consultationStorage";

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
      const t = T(this.props.dark);
      return (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: "100vh", background: t.bg, padding: 20, fontFamily: "'Pretendard',-apple-system,sans-serif" }}>
          <div style={{ maxWidth: 480, width: "100%", background: t.card, borderRadius: 16, padding: "32px 24px", border: `1px solid ${t.brd}`, textAlign: "center" }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>⚠️</div>
            <h1 style={{ fontSize: 20, fontWeight: 800, color: t.tx, margin: "0 0 8px" }}>앗, 문제가 발생했습니다</h1>
            <p style={{ fontSize: 13, color: t.sub, lineHeight: 1.6, margin: "0 0 24px" }}>예기치 않은 오류가 발생했습니다. 페이지를 새로고침하거나 홈으로 돌아가주세요.</p>
            <div style={{ display: "flex", gap: 8, justifyContent: "center" }}>
              <button onClick={() => window.location.reload()} style={{ flex: 1, maxWidth: 200, padding: "12px 20px", borderRadius: 10, border: "none", background: t.cyan, color: "#000", fontSize: 13, fontWeight: 800, cursor: "pointer", fontFamily: "'Pretendard',sans-serif" }}>새로고침</button>
              <button onClick={() => { this.setState({ hasError: false, error: null }); window.location.href = "/"; }} style={{ flex: 1, maxWidth: 200, padding: "12px 20px", borderRadius: 10, border: `1px solid ${t.brd}`, background: "transparent", color: t.tx, fontSize: 13, fontWeight: 800, cursor: "pointer", fontFamily: "'Pretendard',sans-serif" }}>홈으로</button>
            </div>
            {this.state.error && (
              <details style={{ marginTop: 20, textAlign: "left" }}>
                <summary style={{ fontSize: 11, color: t.sub, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>오류 세부정보</summary>
                <pre style={{ fontSize: 10, color: t.sub, background: t.bg, padding: 12, borderRadius: 8, overflow: "auto", marginTop: 8, fontFamily: "'JetBrains Mono',monospace" }}>{this.state.error.toString()}</pre>
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

// 릴리스 8: 개인 인텔리전스 층(워치·브리프·프로필)에 맞춘 IA 재편 —
// 오늘(관제 대시보드) / 피드(탐색) / 브리핑룸(브리프+내 워치 전부) / 자료실(정책+용어) / 상담소(AI)
// (내부 key는 "watchroom" 유지 — localStorage·seed 등 상태 계약을 건드리지 않는 표시명 변경)
const CATS = [
  { key: "all", label: "오늘", icon: "🌅" },
  { key: "news", label: "피드", icon: "📰" },
  { key: "watchroom", label: "브리핑룸", icon: "📮" },
  { key: "archive", label: "자료실", icon: "📚" },
  { key: "chatbot", label: "상담소", icon: "🤖" },
];

// '오늘' 탭의 날짜는 카드 최신일이 아니라 실제 오늘(KST) — 데이터 갱신이 하루이틀
// 늦어도 앱이 낡아 보이지 않게. 데이터 시점(카드 최신일)은 보조 라벨로 정직하게 병기한다.
function todayLabel() {
  const d = new Date(Date.now() + 9 * 3600000);
  return `${d.getUTCFullYear()}.${String(d.getUTCMonth() + 1).padStart(2, "0")}.${String(d.getUTCDate()).padStart(2, "0")} (${"일월화수목금토"[d.getUTCDay()]})`;
}
function TodayDashboard({ dark, kb, tracker, weeklyBriefs = [], watchVersion = 0, onNav, onOpenProfile, onFeedSearch, onAppCommand }) {
  const t = T(dark);
  // 워치는 명령 버스(executeAppCommand)가 localStorage를 직접 바꾸므로 버전 신호로 재읽기
  const watchTerms = useMemo(() => {
    try { const v = JSON.parse(localStorage.getItem("sbtl_watch_terms") || "[]"); return Array.isArray(v) ? v : []; } catch { return []; }
  }, [watchVersion]);
  const today = latestDate(kb.cards);
  const rank = { t: 3, h: 2, m: 1, i: 0 };
  const todayCards = kb.cards.filter((c) => (c.d || c.date) === today);
  // ---- 오늘의 흐름 서사: /api/brief 재사용, 카드셋 지문 기준 1회 생성 후 캐시 ----
  // 캐시 키는 날짜가 아니라 지문(날짜|장수|서사 입력이 되는 상위 8장 id) — 같은 데이터
  // 날짜에 카드가 추가·정정돼도(새로고침) 낡은 서사를 재사용하지 않는다. 데이터가 안
  // 바뀌면 호출 0회, 생성 실패는 조용히 — 통계 칩·시그널만으로도 성립. 구버전 캐시
  // (sig 없음)는 지문 불일치로 자연 재생성.
  const flowSig = `${today}|${todayCards.length}|${[...todayCards].sort((a, b) => (rank[b.s] || 0) - (rank[a.s] || 0)).slice(0, 8).map((c) => getCardId(c)).join(",")}`;
  const [dailyFlow, setDailyFlow] = useState(() => {
    try { const v = JSON.parse(localStorage.getItem("sbtl_daily_flow") || "null"); return v && v.dataDate ? v : null; } catch { return null; }
  });
  const flowReqRef = useRef(false);
  useEffect(() => {
    if (!today || !todayCards.length) return;
    if (dailyFlow && dailyFlow.sig === flowSig && dailyFlow.narrative) return;
    if (flowReqRef.current) return;
    flowReqRef.current = true;
    (async () => {
      try {
        const src = [...todayCards].sort((a, b) => (rank[b.s] || 0) - (rank[a.s] || 0)).slice(0, 8);
        const payload = {
          scopeLabel: "오늘의 흐름",
          cards: src.map((c) => ({
            date: c.date || c.d || "", region: c.region || c.r || "", title: c.title || c.T || "",
            fact: c.fact || c.gate || c.g || "", implication: cardImplicationText(c),
            quote: "", quoteSource: "",
          })),
        };
        const r = await fetch("/api/brief", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
        const j = await r.json();
        if (j?.ok && j.narrative) {
          const entry = { dataDate: today, sig: flowSig, narrative: String(j.narrative) };
          localStorage.setItem("sbtl_daily_flow", JSON.stringify(entry));
          setDailyFlow(entry);
        }
      } catch { /* 조용히 — 다음 방문에서 재시도 */ }
      finally { flowReqRef.current = false; }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [flowSig, dailyFlow]);
  // ---- 첫 방문 온보딩: 관심사 선택 → 명령 버스로 워치 일괄 등록 (개인화 체인 점화) ----
  const [onboardDone, setOnboardDone] = useState(() => {
    try { return localStorage.getItem("sbtl_onboard_done") === "1"; } catch { return true; }
  });
  const [onboardPick, setOnboardPick] = useState([]);
  const finishOnboard = (picks) => {
    try { localStorage.setItem("sbtl_onboard_done", "1"); } catch { /* noop */ }
    if (picks.length && typeof onAppCommand === "function") picks.forEach((term) => onAppCommand({ type: "watch_add", term }));
    setOnboardDone(true);
  };
  const top = [...todayCards].sort((a, b) => (rank[b.s] || 0) - (rank[a.s] || 0)).slice(0, 4);
  const lead = top[0];
  const rest = top.slice(1);
  // 오늘 구성 통계: 시그널 등급·지역 분포
  const sigCount = todayCards.reduce((a, c) => { a[c.s] = (a[c.s] || 0) + 1; return a; }, {});
  const regionTop = Object.entries(todayCards.reduce((a, c) => { const r = c.r || c.region || "GL"; a[r] = (a[r] || 0) + 1; return a; }, {})).sort((a, b) => b[1] - a[1]).slice(0, 3);
  // 최근 7일 일별 카드 수 — 뉴스 밀도 스파크라인 (기준일 = 최신 카드 날짜)
  const density = (() => {
    const base = new Date(String(today || "").replace(/\./g, "-"));
    if (Number.isNaN(base.getTime())) return [];
    const byDay = kb.cards.reduce((a, c) => { const d = String(c.d || c.date || "").slice(0, 10); if (d) a[d] = (a[d] || 0) + 1; return a; }, {});
    const days = [];
    for (let i = 6; i >= 0; i--) {
      const d = new Date(base.getTime() - i * 86400000);
      const key = d.toISOString().slice(0, 10);
      // getUTCDay — base가 UTC 자정이라 로컬 getDay()는 UTC 서쪽에서 하루 밀린다
      days.push({ key, n: byDay[key] || 0, dow: "일월화수목금토"[d.getUTCDay()] });
    }
    return days;
  })();
  const maxDay = Math.max(1, ...density.map((d) => d.n));
  const watchStats = watchTerms.slice(0, 3).map((w) => {
    const cards = kb.cards.filter((c) => cardMatchesWatch(c, [w]));
    return { term: w, fresh: cards.filter((c) => cardDateWithinDays(c, 7)).length, latest: cards[0] };
  });
  const latestBrief = weeklyBriefs[0];
  const upcoming = (tracker?.upcoming || []).slice(0, 2);
  // 🧵 이슈 스레드 — 프로필이 '기업 축'이라면 이건 '사건 축': 제목의 희소 토큰
  // (df 3~12, 2개 이상 날짜에 걸침)으로 이어지는 카드 묶음을 찾는다. 실구현에선
  // 클러스터링을 서버에서 정제할 예정 — 목업은 실데이터 lexical 근사.
  const threads = useMemo(() => {
    const stop = new Set(["배터리", "전기차", "이차전지", "리튬", "글로벌", "한국", "중국", "미국", "유럽", "일본", "발표", "확대", "계획", "추진", "시장", "산업", "기업", "정부", "신규", "최대", "공장", "생산", "투자", "돌파", "체결", "공급"]);
    const byTok = {};
    kb.cards.slice(0, 400).forEach((c) => {
      // 순수 숫자와 날짜성 토큰(2026년·3분기 등)은 사건 축이 못 된다 — 설비 용량(200MW)류는 유지
      const toks = new Set(String(c.T || c.title || "").split(/[^A-Za-z가-힣0-9]+/).filter((w) => w.length >= 3 && !stop.has(w) && !/^\d+$/.test(w) && !/^\d+(년|월|일|분기|반기)$/.test(w)));
      toks.forEach((w) => { (byTok[w] = byTok[w] || []).push(c); });
    });
    const cands = Object.entries(byTok)
      .filter(([, cs]) => cs.length >= 3 && cs.length <= 12)
      .map(([w, cs]) => {
        const dates = [...new Set(cs.map((c) => c.d || c.date))].sort().reverse();
        return { key: w, n: cs.length, span: dates.length, cards: cs, latest: cs[0], lastDate: dates[0] || "" };
      })
      // 품질 필터: 살아있는 이슈만(최신 카드일 기준 14일 내 마지막 소식) —
      // 오래전 끝난 사건이 '이어지는 이슈'로 남지 않게
      .filter((th) => {
        if (th.span < 2) return false;
        const base = new Date(String(today || "").replace(/\./g, "-"));
        if (Number.isNaN(base.getTime())) return true;
        const floor = new Date(base.getTime() - 14 * 86400000).toISOString().slice(0, 10);
        return String(th.lastDate).replace(/\./g, "-") >= floor;
      })
      // 최신 소식 우선, 같은 날짜면 연속성(장수×날짜 스팬)이 큰 사건 우선
      .sort((a, b) => b.lastDate.localeCompare(a.lastDate) || (b.n * b.span) - (a.n * a.span));
    const picked = [];
    for (const th of cands) {
      // 카드 집합이 절반 넘게 겹치는 스레드는 같은 사건의 다른 토큰 — 하나만
      const ids = new Set(th.cards.map((c) => getCardId(c)));
      const dup = picked.some((p) => {
        const inter = p.cards.reduce((a, c) => a + (ids.has(getCardId(c)) ? 1 : 0), 0);
        return inter / Math.min(p.cards.length, ids.size) > 0.5;
      });
      if (dup) continue;
      picked.push(th);
      if (picked.length >= 3) break;
    }
    return picked;
  }, [kb.cards, today]);
  const sigColor = (s) => (s === "t" ? "#F85149" : s === "h" ? "#D29922" : "#388BFD");
  const linkBtn = { marginTop: 8, padding: 0, border: "none", background: "transparent", color: t.cyan, fontSize: 10.5, fontWeight: 800, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" };
  const W = ({ label, right, children, style }) => (
    <div style={{ borderRadius: 14, background: t.card2, border: `1px solid ${t.brd}`, padding: "12px 14px", ...style }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 8 }}>
        <div style={{ fontSize: 9, fontWeight: 800, letterSpacing: 1.2, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>{label}</div>
        {right && <div style={{ fontSize: 9, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>{right}</div>}
      </div>
      {children}
    </div>
  );
  return (
    // 하단 110px — fixed 하단 네비(+safe-area) 위 공간 예약, 다른 탭 루트와 동일
    <div style={{ padding: "0 16px 110px", display: "flex", flexDirection: "column", gap: 10 }}>
      {!onboardDone && watchTerms.length === 0 && (
        <W label="처음이시죠? 관심사를 골라주세요" right="개인화 시작">
          <div style={{ fontSize: 11.5, color: t.sub, lineHeight: 1.6, marginBottom: 8, wordBreak: "keep-all" }}>고르면 새 카드 배지·매주 📮 브리프·프로필 바로가기가 켜져요. 나중에 브리핑룸이나 상담소에서 바꿀 수 있어요.</div>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            {["CATL", "LG에너지솔루션", "삼성SDI", "SK온", "Tesla", "BYD", "전고체", "ESS"].map((term) => {
              const on = onboardPick.includes(term);
              return <button key={term} onClick={() => setOnboardPick((p) => (on ? p.filter((x) => x !== term) : [...p, term]))} aria-pressed={on} style={{ padding: "9px 13px", borderRadius: 999, border: `1px solid ${on ? "transparent" : t.brd}`, background: on ? t.cyan : t.card, color: on ? "#000" : t.tx, fontSize: 11.5, fontWeight: 800, cursor: "pointer" }}>{on ? "✓ " : ""}{term}</button>;
            })}
          </div>
          <div style={{ display: "flex", gap: 6, marginTop: 10 }}>
            <button onClick={() => finishOnboard(onboardPick)} disabled={!onboardPick.length} style={{ flex: 1, padding: "11px", borderRadius: 10, border: "none", background: onboardPick.length ? t.cyan : t.brd, color: "#000", fontSize: 12, fontWeight: 800, cursor: onboardPick.length ? "pointer" : "not-allowed" }}>{onboardPick.length ? `${onboardPick.length}개 워치로 시작` : "관심사를 골라주세요"}</button>
            <button onClick={() => finishOnboard([])} style={{ padding: "11px 14px", borderRadius: 10, border: `1px solid ${t.brd}`, background: "transparent", color: t.sub, fontSize: 12, fontWeight: 700, cursor: "pointer" }}>나중에</button>
          </div>
        </W>
      )}
      <W label={`TODAY'S FLOW · ${todayLabel()}`} right={`카드 최신 ${fmtDate(today)} · ${todayCards.length}장`}>
        {dailyFlow && dailyFlow.dataDate === today && dailyFlow.narrative
          ? <div style={{ fontSize: 13.5, fontWeight: 700, lineHeight: 1.65, color: t.tx, wordBreak: "keep-all" }}>{String(dailyFlow.narrative).slice(0, 300)}</div>
          : <div style={{ fontSize: 12.5, lineHeight: 1.6, color: t.sub, wordBreak: "keep-all" }}>최신 카드 {todayCards.length}장이 갱신됐어요 — 아래 시그널과 워치 하이라이트로 오늘의 흐름을 확인하세요.</div>}
        <div style={{ display: "flex", gap: 5, flexWrap: "wrap", marginTop: 10 }}>
          {(sigCount.t || 0) > 0 && <span style={{ fontSize: 9, fontWeight: 800, color: "#F85149", border: "1px solid rgba(248,81,73,0.4)", borderRadius: 999, padding: "3px 8px", fontFamily: "'JetBrains Mono',monospace" }}>TOP {sigCount.t}</span>}
          {(sigCount.h || 0) > 0 && <span style={{ fontSize: 9, fontWeight: 800, color: "#D29922", border: "1px solid rgba(210,153,34,0.4)", borderRadius: 999, padding: "3px 8px", fontFamily: "'JetBrains Mono',monospace" }}>HIGH {sigCount.h}</span>}
          {regionTop.map(([r, n]) => <span key={r} style={{ fontSize: 9, fontWeight: 700, color: t.sub, border: `1px solid ${t.brd}`, borderRadius: 999, padding: "3px 8px", fontFamily: "'JetBrains Mono',monospace" }}>{REG_FLAG[r] || ""} {r} {n}</span>)}
        </div>
      </W>
      <W label="주간 뉴스 밀도" right="최근 7일 · 일별 카드 수">
        <div style={{ display: "flex", alignItems: "flex-end", gap: 5, height: 46 }}>
          {density.map((d) => (
            <div key={d.key} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 3, height: "100%", justifyContent: "flex-end" }}>
              {d.n > 0 && <div style={{ fontSize: 8, color: t.sub, fontFamily: "'JetBrains Mono',monospace", lineHeight: 1 }}>{d.n}</div>}
              <div style={{ width: "100%", borderRadius: 3, background: d.key === String(today || "").replace(/\./g, "-") ? t.cyan : t.brd, height: `${Math.max(3, Math.round((d.n / maxDay) * 30))}px` }} />
              <div style={{ fontSize: 8.5, color: t.sub, fontFamily: "'JetBrains Mono',monospace", lineHeight: 1 }}>{d.dow}</div>
            </div>
          ))}
        </div>
      </W>
      <W label="MY WATCH · 최근 7일">
        {watchTerms.length ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 7 }}>
            {watchStats.map(({ term, fresh, latest }) => (
              <button key={term} onClick={() => onOpenProfile(term)} style={{ display: "flex", alignItems: "center", gap: 8, width: "100%", textAlign: "left", padding: "8px 10px", borderRadius: 10, border: `1px solid ${fresh ? t.cyan : t.brd}`, background: t.card, cursor: "pointer" }}>
                <span style={{ fontSize: 11, fontWeight: 800, color: t.tx, whiteSpace: "nowrap" }}>{term}</span>
                {fresh > 0 && <span style={{ fontSize: 9, fontWeight: 800, color: "#000", background: t.cyan, borderRadius: 999, padding: "2px 6px", fontFamily: "'JetBrains Mono',monospace" }}>+{fresh}</span>}
                <span style={{ flex: 1, minWidth: 0, fontSize: 10.5, color: t.sub, lineHeight: 1.4, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{latest ? String(latest.T || latest.title || "") : "매칭 카드 없음"}</span>
                <span style={{ fontSize: 10, color: t.sub }}>›</span>
              </button>
            ))}
            <button onClick={() => onNav("watchroom")} style={{ ...linkBtn, marginTop: 2 }}>브리핑룸 전체 →</button>
          </div>
        ) : (
          <button onClick={() => onNav("watchroom")} style={{ width: "100%", padding: "10px", borderRadius: 8, border: `1px dashed ${t.brd}`, background: "transparent", color: t.sub, fontSize: 11.5, fontWeight: 700, cursor: "pointer" }}>워치가 비어 있어요 — 브리핑룸에서 바로 등록하기</button>
        )}
      </W>
      <W label="TOP SIGNALS" right={`${fmtDate(today)} 기준 상위`}>
        {lead && (
          <button onClick={() => onNav("news")} style={{ display: "block", width: "100%", textAlign: "left", border: "none", background: "transparent", padding: 0, cursor: "pointer", marginBottom: rest.length ? 12 : 0 }}>
            <div style={{ display: "flex", gap: 6, alignItems: "center", marginBottom: 5 }}>
              <span style={{ fontSize: 8.5, fontWeight: 800, color: "#fff", background: sigColor(lead.s), borderRadius: 4, padding: "2px 6px", fontFamily: "'JetBrains Mono',monospace" }}>{SIG_L[lead.s] || "INFO"}</span>
              <span style={{ fontSize: 9.5, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>{REG_FLAG[lead.r || lead.region] || ""} {lead.r || lead.region}{Array.isArray(lead.fact_sources) && lead.fact_sources.length > 0 && ` · 📰 ${lead.fact_sources.length}`}</span>
            </div>
            <div style={{ fontSize: 15, fontWeight: 900, lineHeight: 1.4, color: t.tx, wordBreak: "keep-all" }}>{lead.T || lead.title}</div>
            <div style={{ fontSize: 11.5, color: t.sub, lineHeight: 1.55, marginTop: 4, wordBreak: "keep-all", display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}>{lead.sub || lead.subtitle}</div>
          </button>
        )}
        {rest.length > 0 && (
          <div style={{ display: "flex", flexDirection: "column", gap: 9, borderTop: `1px solid ${t.brd}`, paddingTop: 10 }}>
            {rest.map((c, i) => (
              <button key={`${getCardId(c)}-${i}`} onClick={() => onNav("news")} style={{ display: "block", width: "100%", textAlign: "left", border: "none", background: "transparent", padding: 0, borderLeft: `3px solid ${sigColor(c.s)}`, paddingLeft: 10, cursor: "pointer" }}>
                <div style={{ fontSize: 12, fontWeight: 700, lineHeight: 1.45, color: t.tx, wordBreak: "keep-all" }}>{c.T || c.title}</div>
                <div style={{ fontSize: 9.5, color: t.sub, marginTop: 2, fontFamily: "'JetBrains Mono',monospace" }}>{REG_FLAG[c.r || c.region] || ""} {c.r || c.region}{Array.isArray(c.fact_sources) && c.fact_sources.length > 0 && ` · 📰 ${c.fact_sources.length}`}</div>
              </button>
            ))}
          </div>
        )}
        <button onClick={() => onNav("news")} style={{ ...linkBtn, marginTop: 10 }}>피드 전체 보기 →</button>
      </W>
      {threads.length > 0 && (
        <W label="🧵 이어지는 이슈" right="같은 사건의 카드 묶음 · 탭하면 피드 검색">
          <div style={{ display: "flex", flexDirection: "column", gap: 9 }}>
            {threads.map((th) => (
              <button key={th.key} onClick={() => onFeedSearch && onFeedSearch(th.key)} style={{ display: "block", width: "100%", textAlign: "left", border: "none", background: "transparent", padding: 0, cursor: "pointer" }}>
                <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
                  <span style={{ fontSize: 11, fontWeight: 900, color: t.tx }}>{th.key}</span>
                  <span style={{ fontSize: 9, fontWeight: 800, color: "#000", background: t.cyan, borderRadius: 999, padding: "1px 7px", fontFamily: "'JetBrains Mono',monospace" }}>{th.n}장</span>
                  <span style={{ fontSize: 9, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>~{fmtDate(th.lastDate)}</span>
                </div>
                <div style={{ fontSize: 10.5, color: t.sub, lineHeight: 1.5, marginTop: 2, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{String(th.latest.T || th.latest.title || "")}</div>
              </button>
            ))}
          </div>
        </W>
      )}
      <div style={{ display: "flex", gap: 10 }}>
        <W label="📮 주간 브리프" style={{ flex: 1, minWidth: 0 }}>
          {latestBrief ? (
            <div>
              <div style={{ fontSize: 11, color: t.tx, lineHeight: 1.55, wordBreak: "keep-all" }}>{String(latestBrief.narrative || "").slice(0, 42)}…</div>
              <button onClick={() => onNav("watchroom")} style={linkBtn}>브리핑룸에서 →</button>
            </div>
          ) : (
            <div>
              <div style={{ fontSize: 11, color: t.sub, lineHeight: 1.55, wordBreak: "keep-all" }}>아직 발행본 없음</div>
              <button onClick={() => onNav("watchroom")} style={linkBtn}>지금 발행하기 →</button>
            </div>
          )}
        </W>
        <W label="⏰ 정책 마감 임박" style={{ flex: 1, minWidth: 0 }}>
          {upcoming.length ? upcoming.map((ev, i) => (
            <div key={i} style={{ fontSize: 11, color: i === 0 ? t.tx : t.sub, lineHeight: 1.5, marginTop: i > 0 ? 5 : 0, wordBreak: "keep-all", display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}>{REG_FLAG[ev.region] || ""} {String(ev.title || "").slice(0, 34)} · {ev.date}</div>
          )) : <div style={{ fontSize: 11, color: t.sub }}>임박 일정 없음</div>}
          <button onClick={() => onNav("archive")} style={linkBtn}>트래커 →</button>
        </W>
      </div>
    </div>
  );
}

// 상담소 웰컴 가이드 — 릴리스 6·7 기능(에이전틱 명령·브리프 발행)을 카테고리별
// 예시 명령으로 구체 안내. 모든 예시는 탭하면 그대로 실행되는 칩(기능을 가르치는 UI).
function ChatGuide({ dark, runSuggestion }) {
  const t = T(dark);
  const groups = [
    { icon: "⚡", title: "앱 조작 (말로 시키기)", desc: "워치·프로필·피드 필터를 채팅으로 바로 조작해", chips: ["CATL 워치에 추가해줘", "삼성SDI 프로필 보여줘", "중국 최근 7일 카드만 보여줘"] },
    { icon: "📮", title: "브리프", desc: "매주 자동 발행 + 원하면 주간·월간 즉시 발행 (워치 없으면 전체 기준)", chips: ["주간 브리프 보여줘", "지금 브리프 만들어줘", "월간 브리프 만들어줘"] },
    { icon: "🔍", title: "검색·비교·개인화", desc: "답변엔 [n] 근거 인용이 달려", chips: ["내워치 최근 소식 정리해줘", "LFP랑 NCM 비교해줘", "미국 FEOC 쉽게 설명해줘"] },
  ];
  return (
    <div style={{ marginTop: 6, marginBottom: 12, display: "flex", flexDirection: "column", gap: 8 }}>
      {groups.map((g) => (
        <div key={g.title} style={{ borderRadius: 12, border: `1px solid ${t.brd}`, background: dark ? "#1A2333" : "#fff", padding: "11px 13px" }}>
          <div style={{ fontSize: 12, fontWeight: 800, color: t.tx }}>{g.icon} {g.title}</div>
          <div style={{ fontSize: 10.5, color: t.sub, margin: "3px 0 8px" }}>{g.desc}</div>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            {g.chips.map((q) => <button key={q} onClick={() => runSuggestion(q)} style={{ background: "transparent", border: `1px solid ${t.brd}`, borderRadius: 999, padding: "8px 12px", fontSize: 11, color: t.cyan, cursor: "pointer", fontWeight: 700 }}>{q}</button>)}
          </div>
        </div>
      ))}
    </div>
  );
}

// 📖 브리프 리더(R13) — 텍스트 덩어리 대신 구조를 그대로 보여준다:
// 【축】 문단 → 섹션 카드(아이콘+축 이름 헤더), [n] 인용 → 탭 배지(→하단 출처 각주로
// 점프·하이라이트), 지켜볼 것 → 체크리스트 카드, 출처 카드 → 접이식 각주(원문 링크).
// 데이터 계약은 불변(entry.narrative/watch/refs) — 표시만 바꾼다.
function BriefReader({ entry, dark, pinnedIds = null, onStarRef = null }) {
  const t = T(dark);
  const [refsOpen, setRefsOpen] = useState(false);
  const [citeFocus, setCiteFocus] = useState(null);
  const refsBoxRef = useRef(null);
  const sections = parseBriefSections(entry.narrative);
  const refs = Array.isArray(entry.refs) ? entry.refs : [];
  const onCite = (n) => {
    setRefsOpen(true);
    setCiteFocus(n);
    // 각주 영역이 방금 열린 경우 렌더 후 스크롤
    setTimeout(() => { try { refsBoxRef.current?.querySelector(`[data-ref="${n}"]`)?.scrollIntoView({ block: "center", behavior: "smooth" }); } catch { /* noop */ } }, 80);
  };
  const groupIcon = entry.group === "region" ? "🗺" : entry.group === "theme" ? "🏷" : entry.group === "custom" ? "🧩" : "▦";
  const hasSections = sections.some((s) => s.key);
  return (
    <div style={{ marginTop: 10 }}>
      {/* 메타 — 범위 배지 + 발행일 + 근거 수 */}
      <div style={{ display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap", marginBottom: 10 }}>
        <span style={{ display: "inline-flex", alignItems: "center", gap: 4, border: `1px solid ${t.cyan}`, color: t.cyan, borderRadius: 999, padding: "3px 9px", fontSize: 9.5, fontWeight: 800, fontFamily: "'JetBrains Mono',monospace" }}>{groupIcon} {entry.scope_label || "내워치"}</span>
        <span style={{ fontSize: 9, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>{entry.generated_at} 발행 · 근거 {refs.length}장</span>
      </div>
      {/* 서사 — 축 섹션 카드(무축 flat이면 문단 그대로) */}
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {sections.map((sec, i) => (
          <div key={i} style={{ background: t.card, border: `1px solid ${t.brd}`, borderRadius: 10, padding: "11px 13px" }}>
            {sec.key && (
              <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
                <span style={{ fontSize: 12.5, fontWeight: 900, color: t.tx, wordBreak: "keep-all" }}>{groupIcon === "▦" ? "▍" : groupIcon} {sec.key}</span>
                <span style={{ flex: 1, height: 1, background: t.brd }} />
              </div>
            )}
            <div style={{ fontSize: 12.5, color: t.tx, lineHeight: 1.85, wordBreak: "keep-all" }}>{renderChatCitations(sec.text, refs.length, onCite)}</div>
          </div>
        ))}
        {!sections.length && <div style={{ fontSize: 12, color: t.sub }}>서사가 비어 있어요.</div>}
      </div>
      {/* 지켜볼 것 — 체크리스트 카드 */}
      {entry.watch?.length > 0 && (
        <div style={{ marginTop: 8, background: t.card, border: `1px solid ${t.brd}`, borderRadius: 10, padding: "11px 13px" }}>
          <div style={{ fontSize: 10, fontWeight: 800, color: t.sub, marginBottom: 6, fontFamily: "'JetBrains Mono',monospace" }}>👁 지켜볼 것</div>
          {entry.watch.map((w, i) => (
            <div key={i} style={{ display: "flex", gap: 7, alignItems: "flex-start", padding: "5px 0", borderTop: i ? `1px dashed ${t.brd}` : "none" }}>
              <span aria-hidden="true" style={{ color: t.cyan, fontSize: 11, lineHeight: 1.7 }}>◻</span>
              <span style={{ flex: 1, fontSize: 11.5, color: t.tx, lineHeight: 1.7, wordBreak: "keep-all" }}>{renderChatCitations(w, refs.length, onCite)}</span>
            </div>
          ))}
        </div>
      )}
      {/* 출처 각주 — 접이식, [n] 탭 시 자동 오픈+하이라이트 */}
      {refs.length > 0 && (
        <div style={{ marginTop: 8 }}>
          <button onClick={() => setRefsOpen((v) => !v)} aria-expanded={refsOpen} style={{ width: "100%", textAlign: "left", padding: "8px 12px", borderRadius: 8, border: `1px dashed ${t.brd}`, background: "transparent", color: t.sub, fontSize: 10.5, fontWeight: 800, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>{refsOpen ? "▾" : "▸"} 출처 카드 {refs.length}장</button>
          {refsOpen && (
            <div ref={refsBoxRef} style={{ marginTop: 6, display: "flex", flexDirection: "column", gap: 3, maxHeight: 260, overflowY: "auto", padding: "2px 0" }}>
              {refs.map((r) => (
                <div key={r.n} data-ref={r.n} style={{ display: "flex", gap: 7, alignItems: "baseline", padding: "5px 8px", borderRadius: 6, background: citeFocus === r.n ? "rgba(88,166,255,0.16)" : "transparent" }}>
                  <span style={{ fontSize: 9.5, fontWeight: 800, color: t.cyan, fontFamily: "'JetBrains Mono',monospace", flexShrink: 0 }}>[{r.n}]</span>
                  {r.url
                    ? <a href={r.url} target="_blank" rel="noreferrer" style={{ flex: 1, fontSize: 11, color: t.tx, lineHeight: 1.5, wordBreak: "keep-all", textDecorationColor: t.brd }}>{r.title} <span style={{ color: t.sub, fontSize: 9.5, fontFamily: "'JetBrains Mono',monospace" }}>({r.date})</span></a>
                    : <span style={{ flex: 1, fontSize: 11, color: t.tx, lineHeight: 1.5, wordBreak: "keep-all" }}>{r.title} <span style={{ color: t.sub, fontSize: 9.5, fontFamily: "'JetBrains Mono',monospace" }}>({r.date})</span></span>}
                  {/* 각주 ☆(R17b) — 읽다가 발견한 근거 카드를 핀 보드로 승격. id 있는 카드 근거만
                      (웹 보강 출처·구버전 호수의 refs엔 id가 없어 조용히 미표시) */}
                  {r.id && onStarRef && (pinnedIds && pinnedIds.has(r.id)
                    ? <span title="핀 보드에 저장됨" aria-label={`[${r.n}] 저장됨`} style={{ flexShrink: 0, fontSize: 12, color: t.cyan, lineHeight: 1 }}>★</span>
                    : <button onClick={() => onStarRef(r)} title="핀 보드에 저장" aria-label={`[${r.n}] 카드를 핀 보드에 저장`} style={{ flexShrink: 0, border: "none", background: "transparent", padding: "0 2px", fontSize: 13, color: t.sub, cursor: "pointer", lineHeight: 1 }}>☆</button>)}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// '브리핑룸' 탭 — 개인 인텔리전스의 집: 브리프(발행·보관함)와 워치(관리·새 소식)를 총괄.
// R12: 브리프 선반이 NEWS에서 여기로 이사 — 발행 버튼과 결과물이 같은 방에 산다.
function Watchroom({ dark, kb, weeklyBriefs = [], variant, watchVersion = 0, onOpenProfile, onNav, onWatchAdd, onWatchRemove, onBriefNow, onWatchSeen, onWatchFeed, weeklyGenerating = false, weeklyError = null, onWeeklyBriefsRead = null, briefSeed = null, onBriefSeedConsumed = null, onAdoptLibraryEntry = null, onDeleteBrief = null }) {
  const t = T(dark);
  // 추가/삭제가 executeAppCommand(명령 버스)로 localStorage를 바꾸므로,
  // 버전 신호(watchSeenVersion)로 재읽기해 화면에 즉시 반영한다.
  const watchTerms = useMemo(() => {
    try { const v = JSON.parse(localStorage.getItem("sbtl_watch_terms") || "[]"); return Array.isArray(v) ? v : []; } catch { return []; }
  }, [watchVersion]);
  // 워치룸 진입 시 '워치 새 소식'에 실제로 표시된 카드(최신 5장)만 확인 처리한다.
  // 매칭 전부를 마킹하면 미리보기 밖의 새 카드까지 배지가 꺼져 못 본 소식이 사라진다 —
  // 남은 새 카드는 리스트 아래 '피드 내워치에서 보기'로 열람할 때 NewsDesk가 마저 확인.
  // seen 병합만 하고 sig는 건드리지 않는다(용어 변경 편입은 NewsDesk·명령 버스 몫).
  // 용어는 localStorage에서 직접 읽는다 — watchTerms(useMemo)를 의존성에 넣으면
  // onWatchSeen→watchVersion→새 배열 참조로 effect가 무한 재실행된다.
  useEffect(() => {
    if (!kb.cards.length) return;
    try {
      const terms = JSON.parse(localStorage.getItem("sbtl_watch_terms") || "[]");
      if (!Array.isArray(terms) || !terms.length) return;
      const matchedNow = kb.cards.filter((c) => cardMatchesWatch(c, terms));
      const windowIds = new Set(matchedNow.slice(0, WATCH_SEEN_WINDOW).map((c) => getCardId(c)).filter(Boolean));
      const seen = new Set(JSON.parse(localStorage.getItem("sbtl_watch_seen") || "[]"));
      matchedNow.slice(0, 5).forEach((c) => { const id = getCardId(c); if (id) seen.add(id); });
      localStorage.setItem("sbtl_watch_seen", JSON.stringify([...seen].filter((id) => windowIds.has(id))));
      if (typeof onWatchSeen === "function") onWatchSeen();
    } catch { /* localStorage 불가 환경은 배지 기능만 조용히 비활성 */ }
  }, [kb.cards, onWatchSeen]);
  const [draft, setDraft] = useState("");
  // ---- 📮 브리프 선반 (R12: NewsDesk에서 이사) ----
  const [weeklyOpen, setWeeklyOpen] = useState(true); // 브리핑룸의 중심 콘텐츠 — 기본 펼침
  const [weeklyShownId, setWeeklyShownId] = useState(null); // 보관함에서 선택된 항목 (null=최신)
  const [copiedWeekly, setCopiedWeekly] = useState(false);
  // 호수 삭제 2탭 확인(R15b) — confirm() 다이얼로그 없이 같은 행 안에서 무장→확정.
  // 무장 상태는 2.5초 뒤 자동 해제(다른 호수로 전환·오탭 보호). 대상 id를 저장해
  // 무장 중 칩으로 호수를 바꾸면 확정이 다른 호수를 지우지 않게 한다.
  const [armDelId, setArmDelId] = useState(null);
  const armDelTimer = useRef(null);
  const tapDelete = (id) => {
    if (armDelId === id) {
      if (armDelTimer.current) clearTimeout(armDelTimer.current);
      setArmDelId(null);
      setWeeklyShownId(null); // 삭제 후엔 최신호 표시
      if (typeof onDeleteBrief === "function") onDeleteBrief(id);
      // 폴백으로 표시될 호수가 미확인이면 읽음 처리 — '표시된 것은 읽음' 규약(Codex #181).
      // 고정 열람 중 도착해 일부러 unread로 남겨둔 호수가, 삭제로 자동 표시되는 순간까지
      // NEW를 달고 있으면 화면과 배지가 어긋난다. 다른 미표시 호수의 NEW는 건드리지 않는다.
      const next = weeklyBriefs.find((e) => e && e.id !== id);
      if (next && !next.read && typeof onWeeklyBriefsRead === "function") onWeeklyBriefsRead(next.id);
      return;
    }
    setArmDelId(id);
    if (armDelTimer.current) clearTimeout(armDelTimer.current);
    armDelTimer.current = setTimeout(() => setArmDelId(null), 2500);
  };
  useEffect(() => () => { if (armDelTimer.current) clearTimeout(armDelTimer.current); }, []); // 탭 이탈 시 무장 타이머 정리
  const copyWeeklyBrief = (entry) => {
    if (!entry?.narrative) return;
    const text = [
      `[SBTL ${entry.period === "monthly" ? "월간" : "주간"} 브리프] ${entry.scope_label || "내워치"} — ${entry.generated_at || ""}`,
      "",
      entry.narrative,
      ...(entry.watch?.length ? ["", "지켜볼 것:", ...entry.watch.map((w) => `- ${w}`)] : []),
      "",
      "출처 카드:",
      ...(entry.refs || []).map((r) => `[${r.n}] ${r.title} (${r.date})${r.url ? ` ${r.url}` : ""}`),
    ].join("\n");
    writeClipboard(text, () => { setCopiedWeekly(true); setTimeout(() => setCopiedWeekly(false), 1600); });
  };
  // 브리프 열람 seed 소비 — 챗("5월 브리프 보여줘")·발행 완료가 특정 호수를 지목한다.
  // 소비 즉시 부모 seed를 비활성화해야 탭을 떠났다 돌아와 리마운트될 때 옛 명령이 재생되지 않는다.
  const briefSeedRef = useRef(0);
  const shelfRef = useRef(null); // 📮 선반 컨테이너 — seed 소비 시 결과 위치로 스크롤(빌더는 한참 아래라 완성이 화면 밖에서 일어남)
  useEffect(() => {
    if (!briefSeed || !briefSeed.nonce || briefSeedRef.current === briefSeed.nonce) return;
    briefSeedRef.current = briefSeed.nonce;
    if (!briefSeed.open) return;
    setWeeklyOpen(true);
    // 호수 선택: id(방금 만든 그 호수) > '요청한 면과 정확히 같은' 최신호. 요청한 면
    // (기간·달·구성)은 정확히 일치, 요청하지 않은 면은 부재 요구 — '월간 브리프 보여줘'
    // (기간만)가 더 최근의 5월호·지역별호를 열면 안 되고, '5월 지역별'은 5월 지역별호를
    // 골라야 한다. weeklyBriefs는 최신순이라 .find가 곧 '가장 최근 동일 변형'.
    const wantPeriod = briefSeed.period;
    const wantMonth = briefSeed.month || null;
    const wantGroup = briefSeed.group || null;
    const wantSpecSig = briefSeed.specSig || null;
    const matchesReq = (e) => {
      if (((e && e.month) || null) !== wantMonth) return false;
      if (((e && e.group) || null) !== wantGroup) return false;
      // 커스텀은 spec_sig까지 정확 일치 — '다른 조합=다른 산출물'(쿨다운·게이트와 같은 규약).
      // 다른 조합의 옛 커스텀호를 요청 결과처럼 열고 읽음 처리하면 안 된다.
      if (wantGroup === "custom" && wantSpecSig && ((e && e.spec_sig) || null) !== wantSpecSig) return false;
      if (wantMonth) return true; // 달이 곧 기간(monthly) 함의
      return !wantPeriod || ((e && e.period) || "weekly") === wantPeriod;
    };
    const anyFacet = wantPeriod || wantMonth || wantGroup;
    const pick = (briefSeed.id && weeklyBriefs.find((e) => e.id === briefSeed.id))
      || (anyFacet ? weeklyBriefs.find(matchesReq) : null);
    setWeeklyShownId(pick ? pick.id : null);
    // 특정 호수를 지목해 열 때는 그 호수만 읽음 처리 — 전체를 처리하면 아직 안 본
    // (더 최신) 다른 호수의 NEW가 열람 없이 사라진다. 폴백(최신호 표시)은 전체.
    if (typeof onWeeklyBriefsRead === "function") onWeeklyBriefsRead(pick ? pick.id : undefined);
    // 결과 위치로 스크롤 — 빌더(패널 하단)에서 발행하면 완성 호수가 화면 밖 위 선반에서
    // 열리고, 사용자가 보는 건 쿨다운으로 바뀐 발행 버튼뿐이라 성공이 실패처럼 읽힌다.
    try { shelfRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }); } catch { /* 미지원 환경 무시 */ }
    if (typeof onBriefSeedConsumed === "function") onBriefSeedConsumed();
    // weeklyBriefs는 소비 시점의 보관함을 읽기만 한다 — nonce 가드가 있어 deps에서 제외
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [briefSeed, onBriefSeedConsumed]);
  // 진입 읽음 처리 — 브리핑룸 선반은 기본 펼침이라 '진입만으로' 최신호가 보인다.
  // 예전 NEWS 선반은 기본 접힘이라 펼침 토글에서 처리했는데, 그 규약만 남기면 진입 후
  // NEW 배지가 접었다 펴야 사라진다. seed가 특정 호수를 지목해 들어온 마운트는 seed
  // 소비가 그 호수만 읽음 처리하므로 여기선 건너뛴다(전체 처리하면 R6 규약 위반 —
  // 지목되지 않은 더 최신 호수의 NEW가 열람 없이 사라진다). 마운트 1회.
  useEffect(() => {
    if (briefSeed && briefSeed.open) return; // seed 경로가 처리
    if (weeklyBriefs.some((e) => e && !e.read) && typeof onWeeklyBriefsRead === "function") onWeeklyBriefsRead();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  // 체류 중 도착 읽음 처리 — 선반이 '열린 채로' 새 호수가 도착하면(패시브 완성·다른 탭
  // 발행) 즉시 표시되는데, 마운트(위)·펼침 토글·seed 어느 읽음 경로에도 안 걸려 NEW가
  // 남는다. '마운트 이후 새로 나타난 id'가 최신으로 실제 표시되고 있을 때만 그 호수를
  // 읽음 처리한다. seed 대기 중(briefSeed.open)엔 양보(발행 완료는 seed가 지목 처리),
  // seed가 보존한 기존 unread는 '새 id'가 아니라 여기서도 건드리지 않는다(R6 유지).
  const knownIdsRef = useRef(null);
  useEffect(() => {
    const ids = new Set(weeklyBriefs.map((e) => e && e.id).filter(Boolean));
    if (knownIdsRef.current === null) { knownIdsRef.current = ids; return; } // 마운트분은 진입 처리 몫
    const freshIds = [...ids].filter((id) => !knownIdsRef.current.has(id));
    knownIdsRef.current = ids;
    if (!freshIds.length) return;
    if (briefSeed && briefSeed.open) return;
    if (!weeklyOpen || weeklyShownId) return; // 접힘·과거 호수 고정 중엔 새 호수가 표시되지 않음 — NEW 유지
    const top = weeklyBriefs[0];
    if (top && !top.read && freshIds.includes(top.id) && typeof onWeeklyBriefsRead === "function") onWeeklyBriefsRead(top.id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [weeklyBriefs]);
  const matched = kb.cards.filter((c) => cardMatchesWatch(c, watchTerms)).slice(0, 5);
  // 미리보기 5장 밖에 남은 새(unseen) 카드 수 — 확인 처리 후 리렌더(watchVersion)마다 재계산
  const unseenLeft = (() => {
    try {
      const seen = new Set(JSON.parse(localStorage.getItem("sbtl_watch_seen") || "[]"));
      return kb.cards.filter((c) => cardMatchesWatch(c, watchTerms)).slice(0, WATCH_SEEN_WINDOW).filter((c) => { const id = getCardId(c); return id && !seen.has(id); }).length;
    } catch { return 0; }
  })();
  // ⚡ 즉시 발행 게이팅 — 챗 명령(brief_now)의 서버 게이트와 동일 기준을 버튼에도 적용.
  // 게이트 없이 실행하면 재료 부족 시 NEWS로 이동만 하고 조용히 실패하거나(설명 없음),
  // 방금 발행 직후 연타로 중복 생성될 수 있다. 막힌 이유는 버튼 아래 정직하게 표시.
  // 워치가 비면 차단 대신 '전체' 범위로 폴백(서버·생성기와 동일). 주간·월간은 재료
  // 창(7/30일)과 쿨다운이 각각 분리 — 주간 발행 직후의 월간 발행은 정당하다.
  const briefGate = (period, { month = null, group = null, specSig = null, scopeAll = false } = {}) => {
    const days = period === "monthly" ? 30 : 7;
    const inWin = (c) => (month ? cardInMonth(c, month) : cardDateWithinDays(c, days));
    // 전체 범위 계열(커스텀·scopeAll 재발행)은 항상 전체 창 풀 — 생성기가 워치를 무시하는
    // 경로이므로 게이트도 같은 풀로 세야 한다(뱃지·발행 재료·게이트 삼자 일치). 워치 기준으로
    // 세면 워치 사용자의 전체호 재발행이 '재료 부족'으로 부당 차단된다(Codex #184).
    const fullScope = group === "custom" || scopeAll;
    const useWatch = watchTerms.length > 0 && !fullScope;
    const material = useWatch
      ? kb.cards.filter((c) => cardMatchesWatch(c, watchTerms) && inWin(c)).length
      : kb.cards.filter(inWin).length;
    if (material < 2) return `재료 부족 — ${month ? `${Number(month.slice(5))}월` : `최근 ${days}일`} ${useWatch ? "매칭" : "카드"} ${material}장 (2장 필요)`;
    // 챗 쿨다운(briefAtFor)과 동일 규약 — 기간·범위에 더해 달력월·구성까지 일치하는
    // 최신호로 판정한다(축 월간 직후의 '지역별 월간'·'5월호'는 다른 산출물이라 정당).
    // 범위 비교: 커스텀=spec_sig('같은 조합'), scopeAll=전체 범위 항목(terms_sig "[]"),
    // 그 외=현재 워치 범위 — 워치 사용자의 briefScopeMatches는 "[]"와 항상 불일치라
    // 전체 범위 산출물에 그대로 쓰면 쿨다운이 구멍나거나 무관 호수에 물린다.
    const scopeMatch = (e) => (group === "custom"
      ? ((e && e.spec_sig) || null) === specSig
      : scopeAll ? ((e && e.terms_sig) === "[]" || (e && e.terms_sig) == null) : briefScopeMatches(e, watchTerms));
    const latestSame = weeklyBriefs.find((e) => ((e && e.period) || "weekly") === period
      && ((e && e.month) || null) === month && ((e && e.group) || null) === group
      && scopeMatch(e));
    const ts = Number(String(latestSame?.id || "").replace(/^wb_/, "")) || 0;
    if (ts && Date.now() - ts < 10 * 60000) return "방금 발행했어요 — 10분 뒤에 다시 만들 수 있어요";
    return null;
  };
  // 구성 선택(자동축·지역별·주제별) — 아래 발행 버튼·월 칩에 공통 적용 (R11 지역별·R13 주제별)
  const [briefGroup, setBriefGroup] = useState(null); // null(자동축) | "region" | "theme"
  const briefExtra = briefGroup ? { group: briefGroup } : {};
  // 🧩 브리프 빌더(R14) — 지역·주제 축을 직접 골라 '내맘대로 짜깁기'. 선택 순서 = 서사 순서.
  // 커스텀은 항상 전체 창 풀(워치 무시) — 칩의 카드 수 뱃지와 발행 재료가 같은 식이어야
  // 정직하다(생성기·게이트와 삼자 일치, briefGate group:"custom" 분기 참조).
  const [builderOpen, setBuilderOpen] = useState(false);
  const [builderSpec, setBuilderSpec] = useState([]); // [{type:"region"|"theme", key}] — 최대 6(서버 MAX_AXES)
  const [builderPeriod, setBuilderPeriod] = useState("weekly"); // "weekly" | "monthly" | 달력월 "YYYY-MM"
  const builderMonth = /^\d{4}-\d{2}$/.test(builderPeriod) ? builderPeriod : null;
  const builderPeriodKind = builderMonth ? "monthly" : builderPeriod;
  const builderPool = useMemo(() => {
    const days = builderPeriodKind === "monthly" ? 30 : 7;
    return kb.cards.filter((c) => (builderMonth ? cardInMonth(c, builderMonth) : cardDateWithinDays(c, days)));
  }, [kb.cards, builderPeriod]); // builderMonth·Kind는 builderPeriod 파생 — deps는 원본 하나로 충분
  // 워치 축 칩 목록 — 내 워치 용어 + spec에 남은 워치 키의 합집합. 용어를 워치에서 지워도
  // 이미 고른 축 칩은 보이게 유지한다(안 그러면 '보이지 않는 선택'이 spec에 남아 발행됨).
  const builderWatchKeys = useMemo(() => {
    const set = new Set(watchTerms);
    for (const s of builderSpec) if (s.type === "watch") set.add(s.key);
    return [...set];
  }, [watchTerms, builderSpec]);
  // 워치 '축' 매칭은 경계 인식(cardMatchesProfileTerm — ASCII 단어 경계·한글 substring,
  // R8b 프로필 규약) — 지도가 주입하는 짧은 ASCII 별칭(EVE·Xi)을 substring으로 매칭하면
  // develop의 eve, flexibility의 xi가 브리프 재료로 섞인다(Codex #185 R5). 워치 배지·피드는
  // 기존 substring 유지 — 축은 발행 재료의 정밀도가 수치 일치보다 우선(프로필과 같은 절충).
  const builderWatchMatch = (c, term) => cardMatchesProfileTerm(c, term);
  const builderCounts = useMemo(() => {
    const m = new Map();
    for (const k of REGION_AXIS_KEYS) m.set(`region:${k}`, customAxisCandidates(builderPool, "region", k).length);
    for (const k of THEME_AXIS_KEYS) m.set(`theme:${k}`, customAxisCandidates(builderPool, "theme", k).length);
    for (const k of builderWatchKeys) m.set(`watch:${k}`, customAxisCandidates(builderPool, "watch", k, builderWatchMatch).length);
    return m;
  }, [builderPool, builderWatchKeys]);
  // 발행될 실제 축 미리보기 — 뱃지는 단독 축 기준이라 겹치는 축을 여럿 고르면 greedy 소진
  // 후 수치가 줄 수 있다. 요약·게이트는 반드시 이 소진 후 결과로 계산한다(생성기와 동일 함수·동일 매처).
  const builderAxes = useMemo(() => computeCustomAxes(builderPool, builderSpec, { maxPerAxis: 8, watchMatch: builderWatchMatch }), [builderPool, builderSpec]);
  const builderCardTotal = builderAxes.reduce((a, ax) => a + ax.cards.length, 0);
  // 탈락 축은 원인을 갈라 말한다 — 후보 자체가 3장 미만이면 '재료 부족'(기간 전환으로
  // 선택 당시 활성이던 칩이 미달로 변한 경우), 후보는 충분한데 빠졌으면 '겹침 소진'
  // (앞 축이 카드를 가져감). 지역끼리는 겹침이 원천 불가라 오귀인이 특히 티가 난다.
  // spec↔축 대응은 (specKey, specType) 정확 매칭 — 표시 키(ax.key)는 동명 충돌 시
  // 접미로 유일화되므로(예: 'LFP' 워치 + LFP 주제 → 'LFP(주제)') key 단독 비교는
  // 죽은 축을 산 것으로 오판한다(Codex #179).
  const axisAlive = (s) => builderAxes.some((ax) => ax.specKey === s.key && ax.specType === s.type);
  const builderDroppedThin = [];
  const builderDroppedOverlap = [];
  for (const s of builderSpec) {
    if (axisAlive(s)) continue;
    ((builderCounts.get(`${s.type}:${s.key}`) || 0) < 3 ? builderDroppedThin : builderDroppedOverlap).push(s.key);
  }
  // 발행·시그니처는 '살아남은 축'만 — 죽은 축이 spec_sig에 남으면 entry의 재현 계약이
  // 깨지고, 안내대로 죽은 칩만 해제해 재발행하면 실질 동일 브리프가 쿨다운을 우회한다.
  const builderEffectiveSpec = builderSpec.filter(axisAlive);
  const builderSpecSig = JSON.stringify(builderEffectiveSpec); // 항목이 {type,key}뿐 — 생성기 entry.spec_sig와 동일 직렬화(normalizeCustomSpec)
  const builderBlock = weeklyGenerating ? "🔄 브리프 만드는 중 — 완성되면 발행할 수 있어요"
    : !builderSpec.length ? "축을 골라주세요 — 워치·지역·주제 칩에서 최대 6개"
    : !builderAxes.length ? "고른 축 전부 재료 부족(축당 3장 필요) — 기간을 넓히거나 다른 축을 골라보세요"
    : builderCardTotal < 4 ? `재료 부족 — 축 합계 ${builderCardTotal}장 (4장 필요)`
    : briefGate(builderPeriodKind, { month: builderMonth, group: "custom", specSig: builderSpecSig });
  const toggleBuilderAxis = (type, key) => setBuilderSpec((prev) => {
    const i = prev.findIndex((s) => s.type === type && s.key === key);
    if (i >= 0) return prev.filter((_, j) => j !== i);
    if (prev.length >= 6) return prev; // 서버 MAX_AXES — 초과 탭은 무시(요약에 6축 상한 명시)
    return [...prev, { type, key }];
  });
  // 📌 핀 보드(R15) — ★저장 카드가 연결 지도(🧠)가 된다. pins는 마운트 스냅샷으로 충분
  // (탭 전환=리마운트 구조라 피드에서 ☆한 뒤 돌아오면 새로 읽힌다). 보기 기본은 '목록'
  // — 기존 표시를 바꾸지 않아 읽음·트리거 감사가 불필요하다(교훈⑮). 지도는 표시 전용:
  // 게이트·락·읽음 어디에도 물리지 않는 순수 시각화라 산출물 면 전파 대상이 아니다.
  const [pins, setPins] = useState(() => { try { const v = JSON.parse(localStorage.getItem("sbtl_bookmarks") || "[]"); return Array.isArray(v) ? v : []; } catch { return []; } });
  const [pinView, setPinView] = useState("list"); // "list" | "map"
  const [pinAlias, setPinAlias] = useState(null); // 엔티티 별칭 맵 — 지도 첫 진입 시 1회 로드
  const [pinSel, setPinSel] = useState(null); // 선택 노드 id
  useEffect(() => {
    if (pinView !== "map" || pinAlias != null) return;
    let alive = true;
    loadAliasEntities().then((j) => { if (alive) setPinAlias(j || {}); });
    return () => { alive = false; };
  }, [pinView, pinAlias]);
  // 지도 소스(R17) — ★저장 외에 '내 워치'로도 지도를 그린다. 별표는 능동 습관이라
  // 대부분 0장에서 시작하는데(콜드스타트), 워치는 온보딩에서 이미 생기므로 워치 매칭
  // 최근 30일 카드를 가상 핀으로 쓰면 첫날부터 발견→생산 루프가 열린다. 매칭은 워치
  // 배지·새 소식과 같은 식(cardMatchesWatch) — 지도가 '워치 새 소식'과 같은 집합을 보여야
  // 직관적이다(축 발행 시점의 정밀 매칭은 빌더 경계 규약이 따로 담당).
  const [pinSource, setPinSource] = useState(null); // null=auto | "star" | "watch"
  const effPinSource = pinSource || (pins.length ? "star" : watchTerms.length ? "watch" : "star");
  const watchPins = useMemo(() => {
    if (!watchTerms.length) return [];
    return kb.cards
      .filter((c) => cardMatchesWatch(c, watchTerms) && cardDateWithinDays(c, 30))
      .sort((a, b) => String(b.date || b.d || "").localeCompare(String(a.date || a.d || "")))
      .slice(0, PIN_GRAPH_MAX_NODES)
      .map((c) => ({ id: getCardId(c), title: c.title || c.T || "", date: c.date || c.d || "", url: c.url || c.primaryUrl || (Array.isArray(c.urls) ? c.urls[0] : "") || "" }));
  }, [kb.cards, watchTerms]);
  const boardPins = effPinSource === "watch" ? watchPins : pins;
  const pinLayout = useMemo(() => {
    if (pinView !== "map" || pinAlias == null || !boardPins.length) return null;
    return layoutPinGraph(buildPinGraph(boardPins, kb.cards, pinAlias), { width: 620 });
  }, [pinView, pinAlias, boardPins, kb.cards]);
  // 워치 지도에서 ☆ 저장 — 발견한 카드를 고정 컬렉션으로 승격(수집 유입구). NewsDesk의
  // toggleBookmark와 같은 스키마(sbtl_bookmarks)로 기록해 피드 ☆ 상태와도 일치한다.
  const savePin = (item) => {
    if (!item || !item.id || pins.some((p) => p.id === item.id)) return;
    const next = [{ id: item.id, title: item.title || "", date: item.date || "", url: item.url || "", savedAt: kstToday() }, ...pins].slice(0, 200);
    setPins(next);
    try { localStorage.setItem("sbtl_bookmarks", JSON.stringify(next)); } catch { /* 세션 상태만이라도 반영 */ }
  };
  const starFromMap = (node) => {
    if (!node || pins.some((p) => p.id === node.id)) return;
    // pins 0→1이 되면 자동 소스가 star로 넘어가 보던 워치 지도가 통째로 바뀜 — 현재 뷰 고정
    if (!pinSource) setPinSource("watch");
    savePin(node);
  };
  // 브리프 각주 ☆(R17b)의 저장 대상 판별 — 피드 ☆·지도 저장과 같은 컬렉션(sbtl_bookmarks)
  const pinnedIds = useMemo(() => new Set(pins.map((p) => p.id)), [pins]);
  const unpin = (id) => {
    const next = pins.filter((p) => p.id !== id);
    setPins(next);
    try { localStorage.setItem("sbtl_bookmarks", JSON.stringify(next)); } catch { /* 세션 상태만이라도 반영 */ }
    setPinSel(null);
  };
  // 🧩 성분→빌더(R16) — 지도에서 발견한 '이야기 덩어리'를 한 탭으로 브리프 재료로.
  // 성분의 연결 근거(axisHints)를 빌더 spec으로 매핑한다: entity→워치 축(별칭 매칭 재사용,
  // 워치 미등록 용어도 R14 규약상 칩으로 표시·발행됨), theme→주제 축. 기간은 성분 카드가
  // 가장 많이 속한 달(월 칩에 있는 달이면)을 자동 제안 — 사용자는 칩·카드 수를 보고 발행만.
  const builderPanelRef = useRef(null);
  const sendComponentToBuilder = (comp) => {
    const hints = (comp.axisHints || []).filter((h) => h && (h.key || h.label));
    if (!hints.length) return; // related만으로 묶인 성분 — 축 근거 없음(캡슐이 비활성 안내)
    // 주입 키는 h.key(성분 멤버 제목의 최다 히트 표기) — canonical을 넣으면 빌더의
    // substring 매처가 별칭 표기 제목(소프트뱅크 vs SoftBank)을 못 찾는다(Codex #185).
    const spec = hints.slice(0, 6).map((h) => ({ type: h.kind === "entity" ? "watch" : "theme", key: h.key || h.label }));
    // 성분 카드의 다수 달 — 월 칩 목록에 있으면 그 달로, 아니면 롤링 월간
    const memberDates = pinLayout ? pinLayout.nodes.filter((n) => n.compIndex === comp.index).map((n) => String(n.date || "").slice(0, 7)) : [];
    const cnt = new Map();
    for (const m of memberDates) if (/^\d{4}-\d{2}$/.test(m)) cnt.set(m, (cnt.get(m) || 0) + 1);
    const topMonth = [...cnt.entries()].sort((a, b) => b[1] - a[1] || String(b[0]).localeCompare(String(a[0])))[0]?.[0];
    setBuilderSpec(spec);
    setBuilderPeriod(topMonth && briefMonths.includes(topMonth) ? topMonth : "monthly");
    setBuilderOpen(true);
    // 패널이 이제 막 열리는 리렌더 뒤에 스크롤 — ref는 다음 프레임에 붙는다
    setTimeout(() => { try { builderPanelRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }); } catch { /* noop */ } }, 60);
  };
  // 사전 생성 라이브러리(R13) — 월 칩의 1·2순위 소스: 보관함 → 라이브러리 → 온디맨드 생성
  const [library, setLibrary] = useState(null);
  useEffect(() => { let alive = true; loadBriefLibrary().then((j) => { if (alive) setLibrary(j); }); return () => { alive = false; }; }, []);
  const libFind = (m, g) => (library?.items || []).find((it) => (it.month || null) === m && ((it.group) || null) === g) || null;
  const archiveFind = (m, g) => weeklyBriefs.find((e) => ((e && e.month) || null) === m && ((e && e.group) || null) === g && (e.terms_sig === "[]" || e.terms_sig == null)) || null;
  const weeklyBlock = briefGate("weekly", briefExtra);
  const monthlyBlock = briefGate("monthly", briefExtra);
  // 달력월 칩 — 카드가 실제로 있는 달만(노이즈 달 제외 ≥10장), 최신부터 4개.
  // 진행 중인 이번 달도 카드만 있으면 노출한다(그 달 1일~오늘까지가 재료).
  const briefMonths = useMemo(() => {
    const cnt = new Map();
    for (const c of kb.cards) {
      const m = String(c.d || c.date || "").slice(0, 7);
      if (/^\d{4}-\d{2}$/.test(m)) cnt.set(m, (cnt.get(m) || 0) + 1);
    }
    return [...cnt.entries()].filter(([, n]) => n >= 10).map(([m]) => m).sort().reverse().slice(0, 4);
  }, [kb.cards]);
  const submitDraft = () => { const v = draft.trim(); if (v.length >= 2 && typeof onWatchAdd === "function") { onWatchAdd(v); setDraft(""); } };
  const sectionTitle = (label, desc) => (
    <div style={{ margin: "16px 0 8px" }}>
      <div style={{ fontSize: 10, fontWeight: 800, letterSpacing: 1.1, color: variant === "b" ? "#9dd6ff" : t.sub, fontFamily: "'JetBrains Mono',monospace" }}>{label}</div>
      {desc && <div style={{ fontSize: 10.5, color: t.sub, marginTop: 3, lineHeight: 1.5, wordBreak: "keep-all" }}>{desc}</div>}
    </div>
  );
  return (
    // 하단 110px — fixed 하단 네비(+safe-area) 위 공간 예약 (마지막 섹션인 🔔 알림
    // 미리보기가 네비 밑에 깔리지 않게), 다른 탭 루트와 동일 규약
    <div style={{ paddingBottom: 110 }}>
      {variant === "b" && (
        <div style={{ display: "flex", borderRadius: 16, background: "#07090D", padding: "18px 8px", margin: "2px 0 6px", border: "1px solid rgba(185,198,216,0.14)" }}>
          {[["워치", watchTerms.length], ["새 소식", matched.length], ["브리프", weeklyBriefs.length]].map(([l, n]) => (
            <div key={l} style={{ flex: 1, textAlign: "center" }}>
              <div style={{ fontSize: 26, fontWeight: 900, color: "#F4F9FF", fontFamily: "'JetBrains Mono',monospace", lineHeight: 1 }}>{n}</div>
              <div style={{ fontSize: 10, color: "#8C99AB", marginTop: 5 }}>{l}</div>
            </div>
          ))}
        </div>
      )}
      {sectionTitle("MY WATCH", watchTerms.length ? "칩을 탭하면 프로필 · ×로 바로 삭제 — 상담소에서 말로도 돼요" : "관심 기업·키워드를 등록하면 새 카드 배지, 매주 📮 브리프, 프로필 바로가기가 여기 모여요")}
      {watchTerms.length > 0 && (
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 2 }}>
          {watchTerms.map((w) => (
            <span key={w} style={{ display: "inline-flex", alignItems: "center", borderRadius: 999, border: `1px solid ${variant === "b" ? "rgba(88,166,255,0.5)" : t.brd}`, background: variant === "b" ? "rgba(88,166,255,0.12)" : t.card2, overflow: "hidden" }}>
              <button onClick={() => onOpenProfile(w)} style={{ padding: "9px 4px 9px 13px", border: "none", background: "transparent", color: t.tx, fontSize: 12, fontWeight: 800, cursor: "pointer" }}>🏢 {w}</button>
              <button onClick={() => onWatchRemove && onWatchRemove(w)} aria-label={`${w} 워치에서 삭제`} style={{ padding: "9px 11px 9px 5px", border: "none", background: "transparent", color: t.sub, fontSize: 13, cursor: "pointer", lineHeight: 1 }}>×</button>
            </span>
          ))}
        </div>
      )}
      <div style={{ display: "flex", gap: 6, marginTop: 8 }}>
        <input value={draft} onChange={(e) => setDraft(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") submitDraft(); }} placeholder="기업·키워드 입력 후 추가 (예: LG에너지솔루션)" aria-label="워치 용어 추가" style={{ flex: 1, minWidth: 0, padding: "10px 12px", borderRadius: 10, border: `1px solid ${t.brd}`, background: t.card, color: t.tx, fontSize: 12, outline: "none", fontFamily: "inherit" }} />
        <button onClick={submitDraft} disabled={draft.trim().length < 2} style={{ padding: "10px 15px", borderRadius: 10, border: "none", background: draft.trim().length >= 2 ? t.cyan : t.brd, color: "#000", fontSize: 12, fontWeight: 800, cursor: draft.trim().length >= 2 ? "pointer" : "not-allowed" }}>추가</button>
      </div>
      {/* 위계: 매일 보는 것부터 — 새 소식 → 주간 브리프 → 비교 → 저장 카드 → 알림 */}
      {sectionTitle(`워치 새 소식 (${matched.length})`, matched.length ? "카드를 누르면 해당 기업 프로필로 이동" : undefined)}
      {matched.length ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {matched.map((c, i) => {
            const hitTerm = watchTerms.find((w) => cardMatchesWatch(c, [w]));
            return (
              <button key={`${getCardId(c)}-${i}`} onClick={() => hitTerm && onOpenProfile(hitTerm)} style={{ width: "100%", textAlign: "left", borderRadius: 12, padding: "11px 13px", background: t.card2, border: `1px solid ${t.brd}`, cursor: hitTerm ? "pointer" : "default" }}>
                <div style={{ display: "flex", gap: 6, alignItems: "center", marginBottom: 4 }}>
                  {hitTerm && <span style={{ fontSize: 8.5, fontWeight: 800, color: "#000", background: t.cyan, borderRadius: 999, padding: "2px 7px", fontFamily: "'JetBrains Mono',monospace" }}>{hitTerm}</span>}
                  <span style={{ fontSize: 9, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>{fmtDate(c.d || c.date)} · {c.r || c.region}</span>
                </div>
                <div style={{ fontSize: 12.5, fontWeight: 700, lineHeight: 1.5, color: t.tx, wordBreak: "keep-all" }}>{c.T || c.title}</div>
              </button>
            );
          })}
          {unseenLeft > 0 && (
            <button onClick={() => onWatchFeed && onWatchFeed()} style={{ width: "100%", padding: "10px", borderRadius: 10, border: `1px dashed ${t.brd}`, background: "transparent", color: t.cyan, fontSize: 11, fontWeight: 800, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>새 카드 {unseenLeft}건 더 — 피드 내워치에서 보기 →</button>
          )}
        </div>
      ) : (
        <div style={{ fontSize: 11.5, color: t.sub, lineHeight: 1.6, wordBreak: "keep-all" }}>아직 매칭 카드가 없어요 — 워치를 넓혀보거나 상담소에 물어보세요.</div>
      )}
      {sectionTitle("📮 브리프", `매주 자동 발행${watchTerms.length ? "" : " (워치가 비어 있어 전체 카드 기준)"} — 아래 버튼으로 주간·월간 바로 발행, 달 칩으로 그 달만 끊어서도, 지역별로 묶어서도 돼요`)}
      {(weeklyBriefs.length > 0 || weeklyGenerating || weeklyError) ? (() => {
        const shown = weeklyBriefs.find((e) => e.id === weeklyShownId) || weeklyBriefs[0];
        const hasUnread = weeklyBriefs.some((e) => !e.read);
        return (
          <div ref={shelfRef} style={{ background: t.card2, borderRadius: 12, padding: "12px 14px", border: `1px solid ${hasUnread ? t.cyan : t.brd}`, scrollMarginTop: 12 }}>
            <button onClick={() => { const next = !weeklyOpen; setWeeklyOpen(next); if (next && hasUnread) { setWeeklyShownId(null); /* 미확인이 있으면 최신 호수를 표시하며 읽음 처리 — 낡은 선택이 새 호수를 가리지 않게 */ if (typeof onWeeklyBriefsRead === "function") onWeeklyBriefsRead(); } }} aria-expanded={weeklyOpen} style={{ display: "flex", alignItems: "center", gap: 8, width: "100%", border: "none", background: "transparent", cursor: "pointer", padding: 0, textAlign: "left" }}>
              <span style={{ fontSize: 12, fontWeight: 900, color: t.tx }}>📮 브리프</span>
              <span style={{ fontSize: 9, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>{weeklyBriefs.length > 0 ? `${weeklyBriefs[0].generated_at} 발행 · ${weeklyBriefs.length}부 보관` : "첫 브리프 준비 중"}</span>
              {hasUnread && <span style={{ fontSize: 8, fontWeight: 800, color: "#000", background: t.cyan, padding: "2px 6px", borderRadius: 999, fontFamily: "'JetBrains Mono',monospace" }}>NEW</span>}
              <span style={{ marginLeft: "auto", color: t.sub, fontSize: 13 }}>{weeklyOpen ? "▾" : "▸"}</span>
            </button>
            {weeklyOpen && weeklyGenerating && (
              <div aria-live="polite" style={{ marginTop: 10, display: "flex", alignItems: "center", gap: 8, padding: "8px 10px", borderRadius: 8, border: `1px dashed ${t.brd}`, fontSize: 11, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>
                🔄 새 브리프 만드는 중… (수십 초 걸릴 수 있어요 — 완성되면 여기 맨 위에 꽂혀요)
              </div>
            )}
            {weeklyOpen && !weeklyGenerating && weeklyError && (
              <div aria-live="polite" style={{ marginTop: 10, padding: "8px 10px", borderRadius: 8, border: `1px dashed ${t.brd}`, fontSize: 11, color: t.sub, lineHeight: 1.6, wordBreak: "keep-all" }}>⚠️ {weeklyError}</div>
            )}
            {weeklyOpen && shown && (
              <div style={{ marginTop: 2 }}>
                {(() => {
                  // R15d 신선도 고백 — 달력월호는 발행 시점 스냅샷인데, 카드 날짜가 '사건일'
                  // 기준이라 지난달 소급 편입이 정상 동작이다(예: 7/15 기사 → 6/2 계약 → 6월).
                  // 그 달 카드 수가 발행 후 변했으면 조용히 낡는 대신 배지로 말하고, 같은
                  // 면(범위·구성/spec)의 재발행 경로를 바로 연다.
                  // 비교는 '그 호수의 범위 풀'로만(Codex #184): 전체 범위 호수(라이브러리·
                  // scopeAll·커스텀, terms_sig "[]")는 전 월 카드, 워치 범위 호수는 현재
                  // 워치가 발행 당시와 같을 때만 워치 매칭 수로 — 범위가 달라졌으면 비교
                  // 자체가 무의미하므로 배지를 띄우지 않는다(오발동이 더 나쁘다).
                  if (!shown.month || !Number.isFinite(shown.source_month_count)) return null;
                  const fullScopeEntry = shown.terms_sig === "[]" || shown.terms_sig == null;
                  if (!fullScopeEntry && !briefScopeMatches(shown, watchTerms)) return null;
                  const nowCount = (fullScopeEntry
                    ? kb.cards.filter((c) => cardInMonth(c, shown.month))
                    : kb.cards.filter((c) => cardMatchesWatch(c, watchTerms) && cardInMonth(c, shown.month))).length;
                  const drift = nowCount - shown.source_month_count;
                  if (!drift) return null;
                  // 커스텀은 group을 명시해야 사전 seed(executeAppCommand — cmd.group 탑재)가
                  // 커스텀 spec 매칭 경로를 탄다 — 빼면 seed가 일반 월호로 오매칭돼 보던 호수를
                  // 거부하고 다른 동월 호수를 열거나 전체 읽음 처리한다(Codex #184 R2).
                  const extra = shown.group === "custom"
                    ? { month: shown.month, group: "custom", customSpec: shown.axes_spec }
                    : { month: shown.month, ...(shown.group ? { group: shown.group } : {}), ...(fullScopeEntry ? { scopeAll: true } : {}) };
                  const block = weeklyGenerating ? "🔄 만드는 중" : briefGate("monthly", { month: shown.month, group: shown.group || null, specSig: shown.spec_sig || null, scopeAll: fullScopeEntry && shown.group !== "custom" });
                  return (
                    <div style={{ display: "flex", alignItems: "center", gap: 8, margin: "6px 0 8px", padding: "8px 10px", borderRadius: 8, border: `1px dashed ${t.cyan}`, fontSize: 10.5, color: t.sub, lineHeight: 1.5, fontFamily: "'JetBrains Mono',monospace" }}>
                      <span style={{ flex: 1, wordBreak: "keep-all" }}>📈 발행 후 {Number(shown.month.slice(5))}월 기사 {drift > 0 ? `+${drift}건` : `${drift}건`} 변동 — 이 호수는 그 전 스냅샷이에요</span>
                      <button onClick={() => { if (!block && onBriefNow) onBriefNow("monthly", extra); }} disabled={!!block} title={block || undefined} style={{ padding: "7px 10px", borderRadius: 8, border: `1px solid ${block ? t.brd : t.cyan}`, background: "transparent", color: block ? t.sub : t.cyan, fontSize: 10, fontWeight: 800, cursor: block ? "not-allowed" : "pointer", whiteSpace: "nowrap", fontFamily: "'JetBrains Mono',monospace" }}>새 재료로 재발행</button>
                    </div>
                  );
                })()}
                {/* R13 브리프 리더 — 섹션 카드·탭 인용·체크리스트·출처 각주 */}
                <BriefReader entry={shown} dark={dark} pinnedIds={pinnedIds} onStarRef={savePin} />
                <div style={{ display: "flex", gap: 6, marginTop: 10 }}>
                  <button onClick={() => copyWeeklyBrief(shown)} style={{ flex: 1, padding: "9px 12px", borderRadius: 8, border: `1px solid ${copiedWeekly ? "transparent" : t.brd}`, background: copiedWeekly ? t.cyan : "transparent", color: copiedWeekly ? "#000" : t.cyan, fontSize: 11, fontWeight: 800, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>{copiedWeekly ? "복사됨 ✓" : "브리프 복사 (출처 각주 포함)"}</button>
                  {/* 공유는 '현재 표시 중인 호수'(shown) — 예전엔 발행 버튼 행에서 latest를 공유해,
                      칩으로 옛 호수를 보는 중에도 최신호가 나가는 표시-공유 불일치가 있었다 */}
                  <button
                    onClick={async () => {
                      const text = `[SBTL ${shown.period === "monthly" ? "월간" : "주간"} 브리프] ${shown.scope_label || "내워치"} · ${shown.generated_at}\n\n${String(shown.narrative || "")}`;
                      try {
                        if (navigator.share) await navigator.share({ title: "SBTL 브리프", text });
                        else await navigator.clipboard.writeText(text);
                      } catch { /* 공유 시트 닫음 등 — 무시 */ }
                    }}
                    aria-label="표시 중인 브리프 공유"
                    style={{ padding: "9px 12px", borderRadius: 8, border: `1px solid ${t.brd}`, background: "transparent", color: t.sub, fontSize: 11, fontWeight: 800, cursor: "pointer" }}
                  >↗ 공유</button>
                  {/* 삭제도 공유와 같은 규약 — '현재 표시 중인 호수'(shown)만. 라이브러리
                      채택본은 월 칩 ⚡가 언제든 다시 채택하므로 지워도 잃는 게 없다. */}
                  <button
                    onClick={() => tapDelete(shown.id)}
                    aria-label={armDelId === shown.id ? "한 번 더 누르면 이 브리프 삭제" : "표시 중인 브리프 삭제"}
                    style={{ padding: "9px 12px", borderRadius: 8, border: `1px solid ${armDelId === shown.id ? "#E5534B" : t.brd}`, background: armDelId === shown.id ? "rgba(229,83,75,0.12)" : "transparent", color: armDelId === shown.id ? "#E5534B" : t.sub, fontSize: 11, fontWeight: 800, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}
                  >{armDelId === shown.id ? "삭제 확정?" : "🗑"}</button>
                </div>
                {weeklyBriefs.length > 1 && (
                  <div style={{ marginTop: 10 }}>
                    <div style={{ fontSize: 10, fontWeight: 800, color: t.sub, marginBottom: 4, fontFamily: "'JetBrains Mono',monospace" }}>지난 브리프</div>
                    <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                      {weeklyBriefs.map((e) => (
                        // 칩으로 호수를 바꾸면 그 호수만 읽음 처리 — 특정 호수 열람이 다른 호수의
                        // NEW를 일부러 남겨두므로(markWeeklyBriefsRead(onlyId)), 실제로 그 호수를
                        // 열어보는 이 경로에서 꺼주지 않으면 NEW가 선반을 접었다 펼 때까지 남는다.
                        <button key={e.id} onClick={() => { setWeeklyShownId(e.id); if (!e.read && typeof onWeeklyBriefsRead === "function") onWeeklyBriefsRead(e.id); }} style={{ padding: "5px 10px", borderRadius: 999, border: `1px solid ${shown.id === e.id ? "transparent" : t.brd}`, background: shown.id === e.id ? t.cyan : "transparent", color: shown.id === e.id ? "#000" : t.sub, fontSize: 10, fontWeight: 700, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>{briefChipLabel(e, new Date().getFullYear(), !!e.month && weeklyBriefs.filter((x) => x && x.month === e.month).length > 1)}{e.group === "region" ? "🗺" : e.group === "theme" ? "🏷" : ""}{!e.read ? " ·" : ""}</button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })() : (
        <div style={{ borderRadius: 12, padding: "12px 14px", background: t.card2, border: `1px dashed ${t.brd}`, fontSize: 11.5, color: t.sub, lineHeight: 1.6 }}>아직 발행본이 없어요 — 아래 버튼으로 바로 만들 수 있어요.</div>
      )}
      <div style={{ display: "flex", gap: 6, marginTop: 8 }}>
        <button onClick={() => { if (!weeklyBlock && onBriefNow) onBriefNow("weekly", briefExtra); }} disabled={!!weeklyBlock} style={{ flex: 1, padding: "11px", borderRadius: 10, border: `1px solid ${t.brd}`, background: "transparent", color: weeklyBlock ? t.sub : t.cyan, fontSize: 11.5, fontWeight: 800, cursor: weeklyBlock ? "not-allowed" : "pointer", fontFamily: "'JetBrains Mono',monospace" }}>⚡ 주간 발행</button>
        <button onClick={() => { if (!monthlyBlock && onBriefNow) onBriefNow("monthly", briefExtra); }} disabled={!!monthlyBlock} style={{ flex: 1, padding: "11px", borderRadius: 10, border: `1px solid ${t.brd}`, background: "transparent", color: monthlyBlock ? t.sub : t.cyan, fontSize: 11.5, fontWeight: 800, cursor: monthlyBlock ? "not-allowed" : "pointer", fontFamily: "'JetBrains Mono',monospace" }}>📅 월간 발행</button>
      </div>
      {/* R11: 지역별 구성 토글 + 달력월 발행 칩 — "5월엔 무슨 일이 있었지"를 달 단위로 끊어 만든다 */}
      <div style={{ display: "flex", gap: 6, marginTop: 6, alignItems: "center", flexWrap: "wrap" }}>
        {/* 구성 세그먼트 — 재탭으로 자동축 복귀 */}
        {[["region", "🗺️ 지역별"], ["theme", "🏷️ 주제별"]].map(([g, label]) => {
          const on = briefGroup === g;
          return <button key={g} onClick={() => setBriefGroup(on ? null : g)} aria-pressed={on} style={{ padding: "8px 12px", borderRadius: 999, border: `1px solid ${on ? t.cyan : t.brd}`, background: on ? (dark ? "rgba(88,166,255,0.14)" : "rgba(9,105,218,0.08)") : "transparent", color: on ? t.cyan : t.sub, fontSize: 10.5, fontWeight: 800, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>{label}{on ? " ✓" : ""}</button>;
        })}
        <button onClick={() => setBuilderOpen((v) => !v)} aria-pressed={builderOpen} aria-expanded={builderOpen} style={{ padding: "8px 12px", borderRadius: 999, border: `1px solid ${builderOpen ? t.cyan : t.brd}`, background: builderOpen ? (dark ? "rgba(88,166,255,0.14)" : "rgba(9,105,218,0.08)") : "transparent", color: builderOpen ? t.cyan : t.sub, fontSize: 10.5, fontWeight: 800, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>🧩 빌더{builderOpen ? " ✓" : ""}</button>
        {briefMonths.map((m) => {
          // 소스 우선순위: 보관함(이미 만든 그 호수) → 사전 생성 라이브러리(0초·LLM 0회) →
          // 온디맨드 생성(기존 게이트 적용). 즉시 열람 가능한 칩은 채움 스타일로 구별.
          const inArchive = archiveFind(m, briefGroup);
          const inLib = !inArchive && libFind(m, briefGroup);
          const instant = !!(inArchive || inLib);
          const block = instant ? null : briefGate("monthly", { month: m, ...briefExtra });
          const onTap = () => {
            if (inArchive) { setWeeklyOpen(true); setWeeklyShownId(inArchive.id); if (!inArchive.read && typeof onWeeklyBriefsRead === "function") onWeeklyBriefsRead(inArchive.id); return; }
            if (inLib) {
              const entry = { period: "monthly", terms: [], terms_sig: "[]", read: true, ...inLib };
              if (typeof onAdoptLibraryEntry === "function") onAdoptLibraryEntry(entry);
              setWeeklyOpen(true); setWeeklyShownId(entry.id);
              return;
            }
            if (!block && onBriefNow) onBriefNow("monthly", { month: m, ...briefExtra });
          };
          return (
            <button key={m} onClick={onTap} disabled={!!block} title={instant ? `${Number(m.slice(5))}월호 바로 열기${inLib ? " (사전 생성)" : ""}` : (block || `${Number(m.slice(5))}월 한 달치 브리프 발행`)} style={{ padding: "8px 11px", borderRadius: 999, border: `1px solid ${instant ? t.cyan : t.brd}`, background: instant ? (dark ? "rgba(88,166,255,0.12)" : "rgba(9,105,218,0.07)") : "transparent", color: block ? t.sub : t.cyan, fontSize: 10.5, fontWeight: 800, cursor: block ? "not-allowed" : "pointer", fontFamily: "'JetBrains Mono',monospace" }}>{m.replace("-", ".")}{instant ? " ⚡" : ""}</button>
          );
        })}
      </div>
      {weeklyBlock && <div style={{ fontSize: 10, color: t.sub, marginTop: 5, fontFamily: "'JetBrains Mono',monospace" }}>주간: {weeklyBlock}</div>}
      {monthlyBlock && <div style={{ fontSize: 10, color: t.sub, marginTop: 3, fontFamily: "'JetBrains Mono',monospace" }}>월간: {monthlyBlock}</div>}
      {builderOpen && (() => {
        // 🧩 브리프 빌더(R14) — 칩 스타일 공용 헬퍼. 선택 칩엔 선택 '순서'를 앞에 단다
        // (순서가 곧 서사 순서라는 계약을 UI가 그대로 보여준다).
        const pill = (on, disabled) => ({ padding: "7px 10px", borderRadius: 999, border: `1px solid ${on ? t.cyan : t.brd}`, background: on ? (dark ? "rgba(88,166,255,0.14)" : "rgba(9,105,218,0.08)") : "transparent", color: disabled ? t.brd : on ? t.cyan : t.sub, fontSize: 10.5, fontWeight: 800, cursor: disabled ? "not-allowed" : "pointer", fontFamily: "'JetBrains Mono',monospace" });
        const axisChip = (type, key) => {
          const n = builderCounts.get(`${type}:${key}`) || 0;
          const order = builderSpec.findIndex((s) => s.type === type && s.key === key);
          const on = order >= 0;
          const disabled = !on && n < 3; // 축당 3장 미달은 선택 불가 — 발행 시 조용히 빠지는 것보다 정직
          return (
            <button key={`${type}:${key}`} onClick={() => { if (!disabled) toggleBuilderAxis(type, key); }} aria-pressed={on} disabled={disabled} title={disabled ? "이 기간 카드가 3장 미만이라 축으로 쓸 수 없어요" : undefined} style={pill(on, disabled)}>
              {on ? `${order + 1} · ` : ""}{type === "watch" ? "🏢 " : ""}{key} <span style={{ opacity: 0.7 }}>{n}</span>
            </button>
          );
        };
        return (
          <div ref={builderPanelRef} style={{ marginTop: 8, borderRadius: 12, padding: "12px 14px", background: t.card2, border: `1px solid ${t.brd}`, scrollMarginTop: 12 }}>
            <div style={{ fontSize: 10, fontWeight: 800, letterSpacing: 1.1, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>🧩 브리프 빌더</div>
            <div style={{ fontSize: 10.5, color: t.sub, marginTop: 3, lineHeight: 1.5, wordBreak: "keep-all" }}>내 워치(🏢)·지역·주제 축을 고른 순서대로 엮어 나만의 브리프를 만들어요 — 숫자는 그 기간 카드 수(축당 최대 8장 수록), 최대 6축</div>
            <div style={{ display: "flex", gap: 6, marginTop: 9, flexWrap: "wrap" }}>
              {[["weekly", "주간"], ["monthly", "월간"], ...briefMonths.map((m) => [m, m.replace("-", ".")])].map(([v, label]) => (
                <button key={v} onClick={() => setBuilderPeriod(v)} aria-pressed={builderPeriod === v} style={pill(builderPeriod === v, false)}>{label}</button>
              ))}
            </div>
            {builderWatchKeys.length > 0 && (
              <div style={{ display: "flex", gap: 6, marginTop: 8, flexWrap: "wrap" }}>{builderWatchKeys.map((k) => axisChip("watch", k))}</div>
            )}
            <div style={{ display: "flex", gap: 6, marginTop: builderWatchKeys.length ? 6 : 8, flexWrap: "wrap" }}>{REGION_AXIS_KEYS.map((k) => axisChip("region", k))}</div>
            <div style={{ display: "flex", gap: 6, marginTop: 6, flexWrap: "wrap" }}>{THEME_AXIS_KEYS.map((k) => axisChip("theme", k))}</div>
            <button onClick={() => { if (!builderBlock && onBriefNow) onBriefNow(builderPeriodKind, { group: "custom", customSpec: builderEffectiveSpec, ...(builderMonth ? { month: builderMonth } : {}) }); }} disabled={!!builderBlock} style={{ width: "100%", marginTop: 10, padding: "11px", borderRadius: 10, border: `1px solid ${t.brd}`, background: "transparent", color: builderBlock ? t.sub : t.cyan, fontSize: 11.5, fontWeight: 800, cursor: builderBlock ? "not-allowed" : "pointer", fontFamily: "'JetBrains Mono',monospace" }}>
              {builderBlock ? builderBlock : `🧩 발행 — ${builderAxes.map((ax) => ax.key).join("·")} · ${builderAxes.length}축 ${builderCardTotal}장`}
            </button>
            {!builderBlock && builderDroppedOverlap.length > 0 && (
              <div style={{ fontSize: 10, color: t.sub, marginTop: 5, fontFamily: "'JetBrains Mono',monospace" }}>겹침 소진으로 제외: {builderDroppedOverlap.join("·")} — 앞 축이 카드를 먼저 가져갔어요</div>
            )}
            {!builderBlock && builderDroppedThin.length > 0 && (
              <div style={{ fontSize: 10, color: t.sub, marginTop: 3, fontFamily: "'JetBrains Mono',monospace" }}>재료 부족으로 제외: {builderDroppedThin.join("·")} — 이 기간엔 3장이 안 돼요</div>
            )}
          </div>
        );
      })()}
      {watchTerms.length >= 2 && (() => {
        // ⚖️ 워치 비교 — 앞 2개 텀 나란히 (실구현: 선택 가능하게)
        const pair = watchTerms.slice(0, 2).map((w) => {
          const cs = kb.cards.filter((c) => cardMatchesWatch(c, [w]));
          const sig = cs.reduce((a, c) => { a[c.s] = (a[c.s] || 0) + 1; return a; }, {});
          return { w, total: cs.length, f7: cs.filter((c) => cardDateWithinDays(c, 7)).length, top: sig.t || 0, high: sig.h || 0, latest: cs[0] };
        });
        return (
          <>
            {sectionTitle("⚖️ 워치 비교", "워치 앞 2개 나란히 — 탭하면 프로필")}
            <div style={{ display: "flex", gap: 8 }}>
              {pair.map((p) => (
                <button key={p.w} onClick={() => onOpenProfile(p.w)} style={{ flex: 1, minWidth: 0, textAlign: "left", borderRadius: 12, padding: "11px 12px", background: t.card2, border: `1px solid ${t.brd}`, cursor: "pointer" }}>
                  <div style={{ fontSize: 12, fontWeight: 900, color: t.tx, marginBottom: 6, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>🏢 {p.w}</div>
                  <div style={{ fontSize: 18, fontWeight: 900, color: t.tx, fontFamily: "'JetBrains Mono',monospace", lineHeight: 1 }}>{p.total}<span style={{ fontSize: 9, color: t.sub, fontWeight: 700 }}> 장</span></div>
                  <div style={{ fontSize: 9, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginTop: 4 }}>7일 +{p.f7} · TOP {p.top} · HIGH {p.high}</div>
                  <div style={{ fontSize: 10, color: t.sub, lineHeight: 1.45, marginTop: 5, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{p.latest ? String(p.latest.T || p.latest.title || "") : "카드 없음"}</div>
                </button>
              ))}
            </div>
          </>
        );
      })()}
      {(() => {
        // R1 ☆보고함 → R15 📌 핀 보드 — 저장 카드가 목록을 넘어 '연결 지도'가 된다.
        const saved = pins.slice(0, 5);
        const pill = (on) => ({ padding: "7px 11px", borderRadius: 999, border: `1px solid ${on ? t.cyan : t.brd}`, background: on ? (dark ? "rgba(88,166,255,0.14)" : "rgba(9,105,218,0.08)") : "transparent", color: on ? t.cyan : t.sub, fontSize: 10.5, fontWeight: 800, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" });
        const selNode = pinLayout && pinSel ? pinLayout.nodes.find((n) => n.id === pinSel) : null;
        const selEdges = pinLayout && pinSel ? pinLayout.edges.filter((e) => e.a === pinSel || e.b === pinSel) : [];
        const nodeById = pinLayout ? new Map(pinLayout.nodes.map((n) => [n.id, n])) : null;
        const KIND_LABEL = { related: "편집자 연결", entity: "같은 주체", theme: "같은 주제" };
        return (
          <>
            {sectionTitle(`📌 핀 보드 (${pins.length})`, (pins.length || watchTerms.length)
              ? "피드에서 ☆로 저장한 카드 — 🧠 지도는 내 워치만으로도 그려져요"
              : "피드 카드의 ☆를 누르거나 워치를 등록하면 여기 모여요")}
            {(pins.length > 0 || watchTerms.length > 0) && (
              <div style={{ display: "flex", gap: 6, marginBottom: 8 }}>
                {[["list", "목록"], ["map", "🧠 지도"]].map(([v, label]) => (
                  <button key={v} onClick={() => { setPinView(v); if (v !== "map") setPinSel(null); }} aria-pressed={pinView === v} style={pill(pinView === v)}>{label}</button>
                ))}
              </div>
            )}
            {pinView === "list" && pins.length === 0 && watchTerms.length > 0 && (
              <div style={{ fontSize: 11, color: t.sub, lineHeight: 1.6, wordBreak: "keep-all" }}>저장한 카드가 아직 없어요 — 🧠 지도를 켜면 내 워치 카드로 바로 연결을 볼 수 있어요.</div>
            )}
            {pins.length > 0 && pinView === "list" && (
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                {saved.map((b) => (
                  <div key={b.id} style={{ borderRadius: 10, padding: "9px 12px", background: t.card2, border: `1px solid ${t.brd}` }}>
                    <div style={{ fontSize: 9, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginBottom: 3 }}>{fmtDate(b.date)}{b.savedAt ? ` · 저장 ${b.savedAt}` : ""}</div>
                    <div style={{ fontSize: 12, fontWeight: 700, lineHeight: 1.45, color: t.tx, wordBreak: "keep-all" }}>{b.title}</div>
                  </div>
                ))}
                {pins.length > 5 && <div style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>+ {pins.length - 5}개 더 — 🧠 지도에서 전부(최신 {PIN_GRAPH_MAX_NODES}개) 보여요</div>}
              </div>
            )}
            {(pins.length > 0 || watchTerms.length > 0) && pinView === "map" && (
              <div style={{ borderRadius: 12, background: t.card2, border: `1px solid ${t.brd}`, padding: "10px 8px 6px" }}>
                {/* 지도 소스(R17) — ★저장 | 👁 내 워치. 전환 시 선택 해제(다른 보드의 노드 id) */}
                <div style={{ display: "flex", gap: 6, marginBottom: 6, flexWrap: "wrap" }}>
                  {[["star", `★ 저장 ${pins.length}`], ["watch", `👁 내 워치 ${watchPins.length}`]].map(([v, label]) => (
                    <button key={v} onClick={() => { setPinSource(v); setPinSel(null); }} aria-pressed={effPinSource === v} style={{ padding: "6px 10px", borderRadius: 999, border: `1px solid ${effPinSource === v ? t.cyan : t.brd}`, background: effPinSource === v ? (dark ? "rgba(88,166,255,0.14)" : "rgba(9,105,218,0.08)") : "transparent", color: effPinSource === v ? t.cyan : t.sub, fontSize: 10, fontWeight: 800, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>{label}</button>
                  ))}
                </div>
                {!boardPins.length ? (
                  <div style={{ fontSize: 11, color: t.sub, padding: "10px 8px", lineHeight: 1.6, wordBreak: "keep-all" }}>{effPinSource === "watch" ? "최근 30일에 워치 매칭 카드가 없어요 — 워치를 넓히거나 ★ 저장으로 모아보세요." : "저장한 카드가 없어요 — 👁 내 워치로 전환하거나 피드에서 ☆를 눌러보세요."}</div>
                ) : !pinLayout ? (
                  <div style={{ fontSize: 11, color: t.sub, padding: "14px 8px", fontFamily: "'JetBrains Mono',monospace" }}>🧠 연결 계산 중…</div>
                ) : (
                  <>
                    <div style={{ overflowX: "auto", WebkitOverflowScrolling: "touch" }}>
                      {(() => {
                        // 🧠 지도 도식화(R15c) — 성분별 색·클러스터 blob·곡선 에지·허브 글로우·라벨 헤일로.
                        // 팔레트는 성분 인덱스로 결정적 배정(같은 보드=같은 색). 1인 성분은 무채색 —
                        // 고립 노드까지 색을 주면 색이 정보(연결 묶음)가 아니라 장식이 된다.
                        const PALETTE = ["#58A6FF", "#3FB950", "#D29922", "#BC8CFF", "#F778BA", "#39C5CF"];
                        const compColor = (ci, size) => (size > 1 ? PALETTE[ci % PALETTE.length] : (dark ? "#8B99AC" : "#57606A"));
                        const nodeBg = dark ? "#1C2333" : "#fff";
                        const halo = dark ? "#161B26" : "#fff"; // 라벨 헤일로 = 카드 배경색(글자가 에지 위에서도 읽히게)
                        const sizeOf = new Map(pinLayout.comps.map((c) => [c.index, c.size]));
                        // 곡선 에지 — 중점에서 수직 방향으로 살짝 휘어 유기적으로. 휘는 방향은 인덱스
                        // 짝홀로 교대(결정적), 곡률은 거리에 비례하되 18px 상한.
                        const edgePath = (e, i) => {
                          const mx = (e.x1 + e.x2) / 2, my = (e.y1 + e.y2) / 2;
                          const dx = e.x2 - e.x1, dy = e.y2 - e.y1;
                          const d = Math.hypot(dx, dy) || 1;
                          const k = Math.min(18, d * 0.18) * (i % 2 ? 1 : -1);
                          return `M ${e.x1} ${e.y1} Q ${mx - (dy / d) * k} ${my + (dx / d) * k} ${e.x2} ${e.y2}`;
                        };
                        return (
                          <svg width={pinLayout.width} height={pinLayout.height} viewBox={`0 0 ${pinLayout.width} ${pinLayout.height}`} role="img" aria-label={`핀 보드 지도 — 카드 ${pinLayout.nodes.length}개, 연결 ${pinLayout.edges.length}개`} onClick={() => setPinSel(null)}>
                            {/* 클러스터 배경 blob + 캡슐 라벨 — '이야기 덩어리'가 한눈에 영역으로 보이게 */}
                            {pinLayout.comps.filter((c) => c.size > 1).map((c) => {
                              const col = compColor(c.index, c.size);
                              return (
                                <g key={`comp-${c.index}`}>
                                  <circle cx={c.cx} cy={c.cy} r={c.r} fill={col} opacity={dark ? 0.07 : 0.06} />
                                  <circle cx={c.cx} cy={c.cy} r={c.r} fill="none" stroke={col} strokeWidth="1" strokeDasharray="2 5" opacity={0.35} />
                                  {c.label && (() => {
                                    // 긴 엔티티 라벨(예: Cerberus Capital Management)은 12자 절단 —
                                    // 캡슐 폭이 성분 상자를 넘어 viewBox 밖으로 잘리거나 이웃과 겹친다
                                    // (2+노드 성분 최소 폭 ~220px > 절단 캡슐 최대 ~128px라 항상 안전).
                                    // 전체 라벨은 <title> 툴팁으로 보존한다(Codex #182).
                                    // R16: 축 근거(axisHints)가 있는 캡슐은 탭→빌더로 보낸다 — 🧩 접두가
                                    // 어포던스. related만으로 묶인 성분은 근거 라벨이 없어 비활성(툴팁 안내).
                                    const canBuild = (c.axisHints || []).some((h) => h && h.label);
                                    const disp = (canBuild ? "🧩 " : "") + (c.label.length > 12 ? c.label.slice(0, 11) + "…" : c.label);
                                    return (
                                      <g onClick={canBuild ? (ev) => { ev.stopPropagation(); sendComponentToBuilder(c); } : undefined} onKeyDown={canBuild ? (ev) => { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); ev.stopPropagation(); sendComponentToBuilder(c); } } : undefined} tabIndex={canBuild ? 0 : undefined} style={canBuild ? { cursor: "pointer" } : undefined} role={canBuild ? "button" : undefined} aria-label={canBuild ? `${c.label} 묶음으로 브리프 만들기` : undefined}>
                                        <title>{canBuild ? `${c.label} — 이 묶음으로 브리프 만들기` : `${c.label} — 편집자 연결 묶음이라 축으로 변환할 근거 라벨이 없어요`}</title>
                                        <rect x={c.cx - disp.length * 4.6 - 9} y={c.cy - c.r - 17} width={disp.length * 9.2 + 18} height={17} rx={8.5} fill={halo} stroke={col} strokeWidth="1" opacity={0.95} />
                                        <text x={c.cx} y={c.cy - c.r - 5} textAnchor="middle" fontSize="9.5" fontWeight="800" fill={col} fontFamily="'JetBrains Mono',monospace">{disp}</text>
                                      </g>
                                    );
                                  })()}
                                </g>
                              );
                            })}
                            {pinLayout.edges.map((e, i) => {
                              const hot = pinSel && (e.a === pinSel || e.b === pinSel);
                              const col = compColor(e.compIndex, sizeOf.get(e.compIndex) || 2);
                              return <path key={i} d={edgePath(e, i)} fill="none" stroke={col} strokeWidth={hot ? 2.6 : e.kind === "related" ? 2 : e.kind === "entity" ? 1.3 : 1.1} strokeDasharray={e.kind === "theme" ? "3 4" : undefined} strokeLinecap="round" opacity={pinSel && !hot ? 0.15 : e.kind === "related" ? 0.95 : 0.7} />;
                            })}
                            {pinLayout.nodes.map((n) => {
                              const on = pinSel === n.id;
                              const col = compColor(n.compIndex, n.compSize);
                              const dimmed = pinSel && !on && !selEdges.some((e) => e.a === n.id || e.b === n.id);
                              return (
                                <g key={n.id} onClick={(ev) => { ev.stopPropagation(); setPinSel(on ? null : n.id); }} style={{ cursor: "pointer" }} aria-label={n.title} opacity={dimmed ? 0.3 : 1}>
                                  {(n.isHub || on) && <circle cx={n.x} cy={n.y} r={n.r + 5} fill={col} opacity={on ? 0.3 : 0.18} />}
                                  <circle cx={n.x} cy={n.y} r={n.r} fill={on ? col : nodeBg} stroke={col} strokeWidth={n.isHub ? 2.4 : 1.5} strokeDasharray={n.orphan ? "3 3" : undefined} />
                                  <text x={n.x} y={n.y + 3.5} textAnchor="middle" fontSize="9.5" fontWeight="800" fill={on ? (dark ? "#000" : "#fff") : t.sub}>{{ t: "T", h: "H", m: "M" }[n.signal] || "·"}</text>
                                  {(() => {
                                    // 라벨은 방사 방향(링 바깥쪽)으로 — 전부 노드 '아래'에 두면 허브와
                                    // 좌우 이웃의 라벨이 같은 높이에서 겹쳐 깨져 보인다(실사용 보고).
                                    // 제목은 2줄(11+10자)까지 — 10자 한 줄은 '나오다가 마는' 수준이라
                                    // 지도에서 카드를 알아볼 수 없다(실사용 보고). 그래도 넘치면 ….
                                    const la = n.labelAng;
                                    const l1 = n.title.slice(0, 11);
                                    const l2 = n.title.length > 11 ? n.title.slice(11, 21) + (n.title.length > 21 ? "…" : "") : null;
                                    const common = { fontSize: "9", fill: dark ? "#C9D1D9" : "#24292F", stroke: halo, strokeWidth: "3", paintOrder: "stroke", fontFamily: "'JetBrains Mono',monospace" };
                                    // 12시 근방(sin<-0.85)은 위로 빼면 성분 캡슐 라벨과 겹친다 — 아래(링 안쪽)로
                                    if (la == null || Math.sin(la) < -0.85) {
                                      return (
                                        <text x={n.x} y={n.y + n.r + 13} textAnchor="middle" fontWeight={n.isHub ? 800 : 500} {...common}>
                                          <tspan x={n.x} dy="0">{l1}</tspan>
                                          {l2 && <tspan x={n.x} dy="10">{l2}</tspan>}
                                        </text>
                                      );
                                    }
                                    const cos = Math.cos(la), sin = Math.sin(la);
                                    const anchor = cos > 0.35 ? "start" : cos < -0.35 ? "end" : "middle";
                                    const lx = n.x + cos * (n.r + 7);
                                    const ly = n.y + sin * (n.r + 7) + (anchor === "middle" ? (sin < 0 ? (l2 ? -14 : -5) : 11) : (l2 ? -1.5 : 3.5));
                                    return (
                                      <text x={lx} y={ly} textAnchor={anchor} fontWeight="500" {...common}>
                                        <tspan x={lx} dy="0">{l1}</tspan>
                                        {l2 && <tspan x={lx} dy="10">{l2}</tspan>}
                                      </text>
                                    );
                                  })()}
                                </g>
                              );
                            })}
                          </svg>
                        );
                      })()}
                    </div>
                    <div style={{ display: "flex", gap: 10, padding: "6px 6px 4px", fontSize: 9, color: t.sub, fontFamily: "'JetBrains Mono',monospace", flexWrap: "wrap" }}>
                      <span>━ 편집자 연결</span>
                      <span style={{ opacity: 0.75 }}>─ 같은 주체</span>
                      <span style={{ opacity: 0.75 }}>┄ 같은 주제</span>
                      <span>● 색 = 연결 묶음</span>
                      <span>◌ 데이터에서 빠진 카드</span>
                    </div>
                    {selNode && (
                      <div style={{ margin: "6px 4px 4px", borderRadius: 10, padding: "10px 12px", background: t.card, border: `1px solid ${t.cyan}` }}>
                        <div style={{ fontSize: 9, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginBottom: 3 }}>{fmtDate(selNode.date)}{selNode.orphan ? " · 현재 데이터에 없는 카드(저장본)" : ""}</div>
                        <div style={{ fontSize: 12, fontWeight: 700, lineHeight: 1.45, color: t.tx, wordBreak: "keep-all" }}>{selNode.title}</div>
                        {selEdges.length > 0 && (
                          <div style={{ marginTop: 6, display: "flex", flexDirection: "column", gap: 3 }}>
                            {selEdges.slice(0, 5).map((e, i) => {
                              const other = nodeById.get(e.a === pinSel ? e.b : e.a);
                              // 상대 제목은 자르지 않는다 — HTML이라 줄바꿈이 되는데 24자에서 끊으면
                              // '나오다가 마는' 글이 된다(실사용 보고). keep-all로 어절 단위 줄바꿈.
                              return <div key={i} style={{ fontSize: 10, color: t.sub, lineHeight: 1.5, wordBreak: "keep-all" }}>· <b style={{ color: t.tx }}>{KIND_LABEL[e.kind]}{e.kind !== "related" ? `(${e.label})` : ""}</b> — {other ? other.title : ""}</div>;
                            })}
                            {selEdges.length > 5 && <div style={{ fontSize: 9.5, color: t.sub }}>+ 연결 {selEdges.length - 5}개 더</div>}
                          </div>
                        )}
                        <div style={{ display: "flex", gap: 6, marginTop: 8 }}>
                          {selNode.url && <a href={selNode.url} target="_blank" rel="noreferrer" style={{ padding: "7px 11px", borderRadius: 8, border: `1px solid ${t.brd}`, color: t.cyan, fontSize: 10.5, fontWeight: 800, textDecoration: "none", fontFamily: "'JetBrains Mono',monospace" }}>원문 ↗</a>}
                          {effPinSource === "star" ? (
                            <button onClick={() => unpin(selNode.id)} style={{ padding: "7px 11px", borderRadius: 8, border: `1px solid ${t.brd}`, background: "transparent", color: t.sub, fontSize: 10.5, fontWeight: 800, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>★ 보드에서 빼기</button>
                          ) : pins.some((p) => p.id === selNode.id) ? (
                            <span style={{ padding: "7px 11px", borderRadius: 8, border: `1px solid ${t.brd}`, color: t.sub, fontSize: 10.5, fontWeight: 800, fontFamily: "'JetBrains Mono',monospace" }}>★ 저장됨</span>
                          ) : (
                            // 워치 지도의 수집 유입구 — 발견한 카드를 ★ 고정 컬렉션으로 승격
                            <button onClick={() => starFromMap(selNode)} style={{ padding: "7px 11px", borderRadius: 8, border: `1px solid ${t.cyan}`, background: "transparent", color: t.cyan, fontSize: 10.5, fontWeight: 800, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>☆ 저장하기</button>
                          )}
                        </div>
                      </div>
                    )}
                    {!selNode && <div style={{ padding: "2px 6px 4px", fontSize: 10, color: t.sub }}>노드를 탭하면 카드와 연결 이유가 보여요</div>}
                  </>
                )}
              </div>
            )}
          </>
        );
      })()}
      {sectionTitle("🔔 알림 (미리보기)", "워치 새 카드·브리프 발행을 알림으로 — 앱 꺼져 있을 때 도착하는 실제 푸시는 서버 연동 후 제공")}
      <div style={{ borderRadius: 12, padding: "12px 14px", background: t.card2, border: `1px dashed ${t.brd}`, display: "flex", alignItems: "center", gap: 10 }}>
        <div style={{ flex: 1, fontSize: 11, color: t.sub, lineHeight: 1.5 }}>
          브라우저 알림 상태: <b style={{ color: t.tx }}>{typeof Notification !== "undefined" ? ({ granted: "허용됨", denied: "차단됨", default: "미설정" }[Notification.permission] || Notification.permission) : "미지원"}</b>
        </div>
        <button
          onClick={async () => {
            try {
              if (typeof Notification === "undefined") return;
              const p = await Notification.requestPermission();
              if (p === "granted") new Notification("SBTL — 워치 새 카드", { body: `${watchTerms[0] || "CATL"} 외 워치에 새 카드가 도착했어요 (예시 알림)` });
            } catch { /* noop */ }
          }}
          disabled={typeof Notification === "undefined"}
          style={{ padding: "9px 13px", borderRadius: 10, border: "none", background: t.cyan, color: "#000", fontSize: 11, fontWeight: 800, cursor: "pointer", whiteSpace: "nowrap" }}
        >알림 켜보기</button>
      </div>
    </div>
  );
}

const SC = { ACTIVE: "#F85149", UPCOMING: "#D29922", WATCH: "#388BFD", DONE: "#7D8590" };
const SL = { ACTIVE: "ACTIVE", UPCOMING: "UPCOMING", WATCH: "WATCH", DONE: "DONE" };
const SIG_L = { top: "TOP", high: "HIGH", mid: "MID", info: "INFO", t: "TOP", h: "HIGH", m: "MID", i: "INFO" };
const RANK_MAP = { top: 3, high: 2, mid: 1, info: 0, t: 3, h: 2, m: 1, i: 0 };
const REG_FLAG = { US: "🇺🇸", KR: "🇰🇷", EU: "🇪🇺", CN: "🇨🇳", JP: "🇯🇵", GL: "🌐", NA: "🇺🇸", "US/KR": "🇺🇸" };
const TRACKER_REGION = {
  NA: { flag: "🇺🇸", name: "북미" },
  US: { flag: "🇺🇸", name: "미국" },
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
      { name: "IRA / FEOC", desc: "IRA §45X·§48E 제조·투자 세액공제 — FEOC 규정으로 중국산 배터리·소재 사용 시 크레딧 박탈. MACR 기준이 핵심입니다." },
      { name: "관세 / Section 301", desc: "Section 301 기본축에 Section 232 광물·트럭 derivative가 추가됐고, IEEPA 관세는 2026.02 SCOTUS 위헌 판결로 후퇴했습니다. 다층 관세·우회 수출 리스크가 시장 접근성을 좌우합니다." },
      { name: "제조 인센티브", desc: "45X 첨단제조 크레딧은 미국 내 셀·모듈·광물 가공 투자의 핵심 유인입니다. U.S.-Japan·U.S.-Mexico Critical Minerals Action Plan으로 핵심광물 plurilateral 가격하한 시도가 더해졌습니다." },
      { name: "ESS / 전력", desc: "standalone ESS 세액공제와 분산자원 시장참여 확대가 수요를 견인합니다." },
    ],
    why: "미국은 보조금과 규제가 동시에 작동합니다. FEOC 준수 여부가 시장 접근 자체를 결정합니다.",
    watchpoints: [
      "FEOC 세부 해석 업데이트",
      "Section 232 광물·트럭 derivative 진행",
      "USMCA 6년 검토 결정 (2026.07.01)",
      "Critical Minerals plurilateral price floor 운용",
      "45X/MACR 적용 기준 변화",
    ],
  },
  EU: {
    flag: "🇪🇺",
    title: "유럽 정책",
    policies: [
      { name: "Battery Regulation", desc: "배터리 여권, 탄소발자국, 재활용률 의무가 단계적으로 강화됩니다. Article 11 분리·교체 의무 면제 위임행위가 2026.04 의견수렴 단계에 진입했습니다." },
      { name: "CBAM", desc: "탄소국경조정은 소재·부품 단가와 공급망 선택에 영향을 줄 수 있습니다. 2026.12 전환기 종료 후 본 부과가 예정돼 있습니다." },
      { name: "CRM Act", desc: "핵심원자재의 역내 조달·가공·재활용 목표가 공급망 재편 압력으로 작동합니다." },
      { name: "보조금", desc: "IPCEI와 각국 보조금은 유지되지만, 재정·심사 강도가 변수입니다." },
    ],
    why: "EU는 규제 중심 시장입니다. 인증·탄소·추적성 대응이 진입장벽이 됩니다.",
    watchpoints: [
      "Article 11 분리·교체 면제 위임행위 의견수렴",
      "Battery Passport 파일럿",
      "CBAM 본격 부과 (2026.12 이후)",
      "CRM Act 세부 이행",
    ],
  },
  CN: {
    flag: "🇨🇳",
    title: "중국 정책",
    policies: [
      { name: "산업정책", desc: "대형 배터리 기업 중심의 규모·가격 경쟁력이 이어지고 있습니다. GB 47372-2026 파워뱅크 강제표준(2027.04 시행), GB 36980.1-2025 BEV 에너지소비 한도 등 안전·효율 표준이 강화됐습니다." },
      { name: "공급망 통제", desc: "흑연·리튬·희토류 등 핵심 소재의 수출통제와 허가제가 변수입니다." },
      { name: "가격 경쟁", desc: "LFP·BESS 가격 하락은 글로벌 프로젝트 경제성을 바꾸는 동시에 비중국 업체의 마진을 압박합니다." },
      { name: "수출 전략", desc: "관세·FEOC 회피를 위한 제3국 가공·조립 거점 확대가 감시 포인트입니다." },
    ],
    why: "중국은 가격과 공급망을 동시에 움직입니다. 비중국 공급망 전략의 기준점입니다.",
    watchpoints: [
      "흑연 수출허가 운용",
      "GB 47372 파워뱅크 표준 시행 (2027.04)",
      "LFP 과잉설비 조정",
      "제3국 우회 수출",
    ],
  },
  KR: {
    flag: "🇰🇷",
    title: "한국 정책",
    policies: [
      { name: "ESS 안전", desc: "화재 안전 인증, 설치 기준, 사후관리 기준이 강화되는 흐름입니다." },
      { name: "입찰 / 조달", desc: "전력계통·재생에너지 연계 ESS 입찰과 조달 조건이 시장을 형성합니다." },
      { name: "실증 / R&D", desc: "전고체·리튬황 등 차세대 배터리 R&D와 사업화 일정이 중요합니다." },
      { name: "규제 대응", desc: "EU Battery Regulation·미국 FEOC 대응을 위한 추적성·원산지 관리가 핵심입니다. ICAO 기내 보조배터리 규정 적용이 추가 변수입니다." },
    ],
    why: "한국은 K-배터리 본거지입니다. 수출 규제 대응과 내수 ESS 시장 형성이 동시에 중요합니다.",
    watchpoints: [
      "ESS 안전기준 개정",
      "용량시장/조달 결과",
      "EV 정보공개 입법예고 후속",
      "배터리 여권 국내 적용",
    ],
  },
  JP: {
    flag: "🇯🇵",
    title: "일본 정책",
    policies: [
      { name: "GX", desc: "GX 투자와 에너지 안보 관점에서 배터리·ESS 지원이 이어집니다." },
      { name: "배터리 지원", desc: "METI 보조금과 지자체 지원이 ESS 시장 형성 속도를 결정합니다." },
      { name: "전력정책", desc: "재생에너지 확대와 계통 유연성 확보에서 ESS 활용이 커집니다." },
    ],
    why: "일본은 에너지 안보와 계통 안정성 관점에서 ESS를 전략자산화하고 있습니다.",
    watchpoints: [
      "METI 보조금 공모",
      "GX 집행 진도",
      "MLIT 기내 보조배터리 규정 (2026.04 시행)",
      "계통용 ESS 규칙",
    ],
  },
  GL: {
    flag: "🌐",
    title: "글로벌 공통",
    policies: [
      { name: "공급망 재편", desc: "미·중 디커플링으로 중간재 가공 거점이 분산되고 있습니다." },
      { name: "광물 확보", desc: "리튬·니켈·코발트·흑연 확보전과 자원국 규제가 확대되고 있습니다. U.S.-Japan·U.S.-Mexico Critical Minerals 협정으로 plurilateral 가격하한 시도가 등장했습니다." },
    ],
    why: "글로벌 밸류체인 재편은 모든 권역 정책의 배경입니다.",
    watchpoints: [
      "자원국 수출 정책",
      "광물 가격 변동",
      "Critical Minerals plurilateral 운용",
      "USTR 강제노동 60국 공청회 후속",
    ],
  },
};

const T = (dark = true) => dark
  ? { bg: "#0D1117", card: "#161B26", card2: "#1C2333", tx: "#E6EDF3", sub: "#9198A1", brd: "#21293A", cyan: "#58A6FF", sh: "0 2px 8px rgba(0,0,0,0.4)" }
  : { bg: "#F4F6FA", card: "#FFFFFF", card2: "#F8F9FC", tx: "#1A1A2A", sub: "#57606A", brd: "#E0E3EA", cyan: "#0969DA", sh: "0 2px 10px rgba(0,0,0,0.06)" };

const LEGACY_SIGNAL = { top: "t", high: "h", mid: "m", info: "i", t: "t", h: "h", m: "m", i: "i" };

function kstNow() {
  const now = new Date();
  const utc = now.getTime() + now.getTimezoneOffset() * 60000;
  return new Date(utc + 9 * 60 * 60 * 1000);
}

function kstToday() {
  const d = kstNow();
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, "0")}.${String(d.getDate()).padStart(2, "0")}`;
}

function fmtDate(date) {
  if (!date) return "-";
  const s = String(date).trim();
  const m = s.match(/^(\d{4})[.-](\d{2})[.-](\d{2})/);
  if (m) return `${m[1]}.${m[2]}.${m[3]}`;
  return s;
}

function pct(num, total) {
  return `${Math.max(0, Math.min(100, ((Number(num) || 0) / Math.max(1, Number(total) || 0)) * 100))}%`;
}

function getSignalRank(card) {
  const key = String(card?.s || card?.signal || "i").toLowerCase();
  return RANK_MAP[key] ?? 0;
}

function buildFetchUrl(path, requestKey = 0) {
  if (!requestKey) return path;
  const sep = path.includes("?") ? "&" : "?";
  return `${path}${sep}_ts=${requestKey}`;
}

function toCompatCard(card) {
  if (!card || typeof card !== "object") return card;
  const signal = card.signal || card.s || "i";
  const source = card.source || card.src || "";
  const primaryUrl = card.primaryUrl || card.primary_url || (Array.isArray(card.urls) ? card.urls[0] : "") || card.url || "";
  const implicationText = Array.isArray(card.implication)
    ? card.implication.filter(Boolean).join("\n\n")
    : String(card.implicationText || card.implication || "");
  const gateText = String(card.gate || card.g || implicationText || card.sub || card.subtitle || "");
  return {
    ...card,
    T: card.T || card.title || "",
    title: card.title || card.T || "",
    sub: card.sub || card.subtitle || "",
    subtitle: card.subtitle || card.sub || "",
    s: card.s || LEGACY_SIGNAL[signal] || "i",
    signal: card.signal || signal,
    r: card.r || card.region || "GL",
    region: card.region || card.r || "GL",
    d: card.d || card.date || "",
    date: card.date || card.d || "",
    src: card.src || source,
    source,
    url: card.url || primaryUrl,
    primaryUrl,
    urls: Array.isArray(card.urls) ? card.urls : (primaryUrl ? [primaryUrl] : []),
    g: card.g || gateText,
    gate: gateText,
    implicationText,
  };
}

// ---- Release 1: 워치리스트 / 보고함 (localStorage, 서버 불필요) ----
function useStoredList(storageKey) {
  const [items, setItems] = useState(() => {
    try {
      const v = JSON.parse(localStorage.getItem(storageKey) || "[]");
      return Array.isArray(v) ? v : [];
    } catch { return []; }
  });
  const save = (next) => {
    setItems(next);
    try { localStorage.setItem(storageKey, JSON.stringify(next)); } catch { /* storage full/blocked — state still works this session */ }
  };
  return [items, save];
}

function cardWatchHay(c) {
  return [c.T, c.title, c.sub, c.subtitle, c.fact, c.g, c.gate]
    .map((v) => String(v || "")).join(" ").toLowerCase();
}

// 카드의 함의(implication) — 원본은 3문장 배열, 정규화본은 implicationText 문자열.
// R10 이전엔 브리프 페이로드 4곳이 '원본' 카드에서 c.implicationText(원본에 없는 필드)를
// 읽어 함의가 100% 유실됐다(1082/1082장 보유 → 전달 0%). 인과·후속 단계가 담긴 필드라
// 이 유실이 '나열 서사'와 '공허한 워치'의 근본 원인이었다 — 반드시 이 헬퍼로 읽는다.
function cardImplicationText(c) {
  if (Array.isArray(c?.implication)) return c.implication.filter(Boolean).join(" ");
  return String(c?.implicationText || c?.implication || "");
}

function cardMatchesWatch(c, terms) {
  if (!Array.isArray(terms) || terms.length === 0) return false;
  const hay = cardWatchHay(c);
  return terms.some((term) => hay.includes(String(term).toLowerCase()));
}

// 프로필/엔티티 매칭 — 순수 ASCII 용어는 단어 경계로(Xi≠Flexibility, DOE≠does,
// ESS≠PRESS), 한글 포함 용어는 접사 결합을 살리기 위해 부분 매칭으로(배터리→리튬배터리).
// 엔티티 자동링크가 짧은 ASCII 별칭(Xi 등)을 프로필로 여는 새 경로를 열었기 때문에,
// 워치용 substring(cardMatchesWatch)과 달리 프로필에는 경계 인식이 필요하다.
function termHitBoundary(term, hay) {
  const w = String(term || "").trim().toLowerCase();
  if (!w) return false;
  if (!/^[\x00-\x7f]+$/.test(w)) return hay.includes(w); // 한글 등 비ASCII는 부분 매칭 유지
  let idx = hay.indexOf(w);
  while (idx !== -1) {
    const before = hay[idx - 1];
    const after = hay[idx + w.length];
    if ((!before || !/[a-z0-9]/.test(before)) && (!after || !/[a-z0-9]/.test(after))) return true;
    idx = hay.indexOf(w, idx + 1);
  }
  return false;
}
function cardMatchesProfileTerm(c, term) {
  return termHitBoundary(term, cardWatchHay(c));
}

function cardDateWithinDays(c, days) {
  if (!days) return true;
  const d = String(c.d || c.date || "");
  if (!d) return false;
  const cutoff = new Date(Date.now() - days * 86400000).toISOString().slice(0, 10);
  return d >= cutoff;
}

// ---- 용어 자동링크: faq.json 키워드를 카드 본문에서 탭 가능한 용어로 ----
function escapeGlossaryRegex(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
function buildGlossaryMatcher(faq) {
  if (!Array.isArray(faq) || !faq.length) return null;
  const entries = [];
  faq.forEach((e) => {
    if (!e || !e.a || !Array.isArray(e.k)) return;
    e.k.forEach((kw) => {
      const w = String(kw || "").trim();
      if (w.length < 2) return;
      if (/^[\d.,]+%?$/.test(w)) return; // "55%" 같은 순수 숫자 키워드는 링크 대상에서 제외 (검색·워치용으로만)
      entries.push({ kw: w, entry: e });
    });
  });
  if (!entries.length) return null;
  entries.sort((a, b) => b.kw.length - a.kw.length); // 긴 키워드 우선 매칭 (예: "리튬인산철" > "리튬")
  const regex = new RegExp(entries.map((x) => escapeGlossaryRegex(x.kw)).join("|"), "gi");
  const byLower = new Map();
  entries.forEach((x) => {
    const key = x.kw.toLowerCase();
    const isCanonical = Array.isArray(x.entry.k) && String(x.entry.k[0] || "").trim().toLowerCase() === key;
    // 여러 엔트리가 같은 키워드를 가지면 그 키워드가 k[0](정본)인 엔트리 우선 — 파일 순서 의존 제거
    if (!byLower.has(key) || isCanonical) byLower.set(key, x.entry);
  });
  return { regex, byLower };
}
const GLOSSARY_WORDCHAR = /[A-Za-z0-9]/;
const GLOSSARY_HANGUL = /[가-힣]/;
// 내워치 seen 스냅샷 창 크기 — 쓰는 쪽(NewsDesk)과 읽는 쪽(AppContent 배지)이 반드시 같은 창을 봐야 한다
const WATCH_SEEN_WINDOW = 800;
function splitGlossaryText(text, matcher) {
  const s = String(text || "");
  if (!s || !matcher) return null;
  const parts = [];
  const seen = new Set();
  let last = 0;
  let m;
  matcher.regex.lastIndex = 0;
  while ((m = matcher.regex.exec(s)) !== null) {
    const word = m[0];
    const entry = matcher.byLower.get(word.toLowerCase());
    if (!entry) continue;
    // ASCII 용어는 단어 경계 수동 확인 ("PRESS" 안의 ESS 오매칭 방지)
    const before = s[m.index - 1];
    const after = s[m.index + word.length];
    if (GLOSSARY_WORDCHAR.test(word[0]) && before && GLOSSARY_WORDCHAR.test(before)) continue;
    if (GLOSSARY_WORDCHAR.test(word[word.length - 1]) && after && GLOSSARY_WORDCHAR.test(after)) continue;
    // 한글 용어는 앞경계만 확인 ("불안전"의 안전 오매칭 방지 — "안전기준" 같은 뒤 교착은 허용)
    if (GLOSSARY_HANGUL.test(word[0]) && before && GLOSSARY_HANGUL.test(before)) continue;
    if (seen.has(entry.id || entry.a)) continue; // 같은 용어는 텍스트당 첫 등장만 링크
    seen.add(entry.id || entry.a);
    if (m.index > last) parts.push({ str: s.slice(last, m.index) });
    parts.push({ term: word, entry });
    last = m.index + word.length;
  }
  if (!parts.some((p) => p.entry)) return null;
  if (last < s.length) parts.push({ str: s.slice(last) });
  return parts;
}

// ---- 기업 엔티티 자동링크 매처 — 용어 매처와 동일 구조({regex, byLower})를 만들어
// splitGlossaryText를 그대로 재사용한다. byLower 값은 별칭 그룹({id, name, spellings}) —
// id는 텍스트당 첫 등장만 링크하는 seen 키(용어 entry의 id/a 역할). 경계 규칙(ASCII
// 단어 경계·한글 앞경계)도 재사용돼 Xi≠Flexibility류 오매칭을 막는다.
// 프로필 링크가 유의미한 주체 타입만 — 지명(place)·기술/정책 용어는 프로필 노이즈라 제외
// (용어는 glossary 팝업 영역, 지명은 검색 확장으로만 쓰인다)
const ENTITY_LINK_TYPES = new Set(["company", "company_division", "company_brand", "research_org", "industry_org", "government_agency", "person"]);
function buildEntityMatcher(aliasNames) {
  if (!Array.isArray(aliasNames) || !aliasNames.length) return null;
  const entries = [];
  aliasNames.forEach((g) => {
    if (!g || !g.name) return;
    if (g.type && !ENTITY_LINK_TYPES.has(g.type)) return;
    const spellings = Array.isArray(g.spellings) && g.spellings.length ? g.spellings : [g.name];
    const group = { id: g.name, name: g.name, spellings };
    spellings.forEach((sp) => { const w = String(sp || "").trim(); if (w.length >= 2) entries.push({ kw: w, entry: group }); });
  });
  if (!entries.length) return null;
  entries.sort((a, b) => b.kw.length - a.kw.length); // 긴 표기 우선 (LG에너지솔루션 > LG)
  const regex = new RegExp(entries.map((x) => escapeGlossaryRegex(x.kw)).join("|"), "gi");
  const byLower = new Map();
  entries.forEach((x) => { const key = x.kw.toLowerCase(); if (!byLower.has(key)) byLower.set(key, x.entry); });
  return { regex, byLower };
}

// 축 선별용 별칭맵 — 1회 로드 모듈 캐시. NewsDesk 파인더의 fetch와 별개(이쪽은 AppContent의
// 브리프 생성 경로). 실패해도 null — 엔티티 축만 빠지고 related·테마·지역 생성기는 동작한다.
let aliasEntitiesPromise = null;
function loadAliasEntities() {
  if (!aliasEntitiesPromise) {
    aliasEntitiesPromise = fetch("/data/entity_alias_map.json")
      .then((r) => (r.ok ? r.json() : null))
      .then((j) => (j && (j.entities || j)) || null)
      .catch(() => null);
  }
  return aliasEntitiesPromise;
}

// ---- 사전 생성 브리프 라이브러리(R13) ----
// 지나간 달의 재료는 불변 → 달×구성(전체/지역별/주제별) 호수를 한 번 생성해 정적 파일로
// 커밋해두면 모든 유저가 0초·LLM 0회로 연다(생성은 ~/tools/gen_brief_library.mjs, 배포 후
// 실행). 파일이 없거나 조합이 비면 조용히 null — 월 칩이 온디맨드 생성으로 폴백한다.
let briefLibraryPromise = null;
function loadBriefLibrary() {
  if (!briefLibraryPromise) {
    briefLibraryPromise = fetch("/data/briefs.json")
      .then((r) => (r.ok ? r.json() : null))
      .then((j) => (j && Array.isArray(j.items) ? j : null))
      .catch(() => null);
  }
  return briefLibraryPromise;
}

// ---- 주간 브리프 보관함: 앱 접속 시 내워치 범위로 조용히 생성해 적재 ----
const WEEKLY_BRIEF_KEY = "sbtl_weekly_briefs";
const WEEKLY_BRIEF_CAP = 12; // 약 3개월치
const WEEKLY_BRIEF_LOCK_KEY = "sbtl_weekly_brief_lock";
const WEEKLY_BRIEF_LOCK_TTL = 120000; // 생성 중 탭이 죽어도 2분 후 다음 접속이 재시도

function readWeeklyBriefs() {
  try {
    const v = JSON.parse(localStorage.getItem(WEEKLY_BRIEF_KEY) || "[]");
    return Array.isArray(v) ? v : [];
  } catch { return []; }
}

// 선반 호수 칩 라벨 — '내용'이 먼저다. 발행일이 앞서면 라이브러리 채택본(같은 날 일괄
// 발행)이 전부 같은 날짜로 시작해 구별이 안 되고, "6월호인데 왜 7월?"로 읽힌다(실사용
// 혼란 보고). 달력월호는 달이 정체성(재료 불변 — 언제 만들었든 같은 호수)이라 발행일을
// 아예 빼고, 롤링 주간/월간·커스텀은 발행일이 정체성이라 짧은 날짜(MM.DD)를 뒤에 둔다.
// 커스텀은 🧩가 곧 라벨이라 칩 접미 아이콘을 따로 붙이지 않는다.
function briefChipLabel(e, nowYear, dupMonth = false) {
  const dd = String((e && e.generated_at) || "").slice(5);
  if (e && e.month) {
    const y = Number(e.month.slice(0, 4));
    // 달력월 커스텀(빌더에서 달 칩 선택)은 🧩를 라벨에 포함 — 렌더러의 접미 아이콘이
    // 🗺/🏷만 다루므로 여기서 빼면 커스텀 5월호가 일반 5월호와 똑같아 보인다(Codex #181).
    // 같은 달 호수가 선반에 여럿이면(범위·구성·spec이 달라 공존 — 쿨다운 규약상 정당)
    // 그때만 발행일을 뒤에 복원한다 — 평시엔 깔끔하게, 충돌 시엔 구별 가능하게.
    return `${Number.isFinite(nowYear) && y !== nowYear ? `${y}년 ` : ""}${Number(e.month.slice(5))}월호${e.group === "custom" ? "🧩" : ""}${dupMonth ? ` ${dd}` : ""}`;
  }
  // 롤링 커스텀도 기간을 표기 — 주간·월간 커스텀이 같은 날 발행되면 🧩 MM.DD만으로는 동일해진다
  if (e && e.group === "custom") return `🧩 ${e.period === "monthly" ? "월간" : "주간"} ${dd}`;
  return `${e && e.period === "monthly" ? "월간" : "주간"} ${dd}`;
}

// 패시브 주기 판정은 '일반(plain) 주간' 항목만 본다 — 패시브가 만드는 게 그것뿐이므로.
// 보관함은 주간·월간·달력월·지역별이 섞이는데, 맨 앞의 다른 변형호를 weeklyBriefDue가
// 최신 주간호로 오인하면 일반 주간 자동 발행이 최대 7일 막힌다(일반 주간호가 아예 없거나
// 낡았어도). 그래서 달력월호(month)·지역별호(group)를 함께 제외한다 — 예: 수동으로 만든
// 지역별 주간호가 있어도 일반 주간 자동 발행은 별개로 due 판정되어야 한다.
// period 없는 구 항목은 주간 취급(마이그레이션 없이 기존 이력이 그대로 유효).
function plainWeeklyEntries(entries) {
  return (entries || []).filter((e) => ((e && e.period) || "weekly") === "weekly" && !(e && e.month) && !(e && e.group));
}

// 커스텀 spec 정규화(R14) — 생성기(entry.spec_sig)·발행 seed·빌더 게이트가 '같은 조합'을
// 같은 직렬화로 봐야 하므로 한 곳에서만 정의한다. {type,key}만 남기고 미지 type은
// theme으로 접으며(생성기 규약), 6개 상한(서버 MAX_AXES 페어)까지 여기서 통일한다.
function normalizeCustomSpec(spec) {
  if (!Array.isArray(spec) || !spec.length) return null;
  const norm = spec.slice(0, 6)
    .map((s) => ({ type: s && s.type === "region" ? "region" : s && s.type === "watch" ? "watch" : "theme", key: String((s && s.key) || "") }))
    .filter((s) => s.key);
  return norm.length ? norm : null;
}

// 브리프 항목이 '지금의 워치 범위'로 만들어진 것인지 — terms_sig(R7+)가 정본이고,
// 구 항목은 표시용 terms로 best-effort 비교. 전체 범위 폴백(R9)은 terms_sig "[]"라
// 워치를 등록하면 자연히 불일치가 되어 새 범위로 다시 만들어진다.
function briefScopeMatches(entry, terms) {
  if (!entry) return false;
  if (entry.terms_sig != null) return entry.terms_sig === JSON.stringify(terms);
  const et = entry.terms || [];
  return JSON.stringify(et) === JSON.stringify(terms.slice(0, et.length));
}

// 최신 항목의 생성일로부터 7일이 지났으면 새 주간 브리프 생성 대상
function weeklyBriefDue(entries) {
  if (!entries.length) return true;
  const last = String(entries[0]?.generated_at || "").replace(/\./g, "-");
  const ms = new Date(last).getTime();
  if (Number.isNaN(ms)) return true;
  return Date.now() - ms >= 7 * 86400000;
}

// 클립보드 쓰기(실패 시 prompt 폴백) — NewsDesk(인용·흐름 브리프)와 브리핑룸(주간 브리프)이 공유
function writeClipboard(text, done) {
  if (navigator.clipboard?.writeText) navigator.clipboard.writeText(text).then(done).catch(() => window.prompt("복사해서 사용하세요:", text));
  else window.prompt("복사해서 사용하세요:", text);
}

// ---- 상담소 답변의 [n] 인용을 탭 가능한 배지로 (해당 근거 카드로 점프) ----
function renderChatCitations(text, cardCount, onCite) {
  const s = String(text || "");
  if (!cardCount || !/\[\d/.test(s)) return s;
  const pieces = s.split(/(\[\d+(?:\s*,\s*\d+)*\])/g);
  if (pieces.length === 1) return s;
  return pieces.map((p, i) => {
    const m = p.match(/^\[(\d+(?:\s*,\s*\d+)*)\]$/);
    if (!m) return p;
    const nums = m[1].split(/\s*,\s*/).map(Number).filter((n) => n >= 1 && n <= cardCount);
    if (!nums.length) return p;
    return (
      <button key={`cite-${i}`} type="button" onClick={() => onCite(nums[0])} aria-label={`근거 카드 ${m[1]}번 보기`} style={{ border: "none", background: "rgba(88,166,255,0.15)", color: "#58A6FF", borderRadius: 6, padding: "0 4px", margin: "0 1px", font: "inherit", fontSize: "0.85em", fontWeight: 800, cursor: "pointer", lineHeight: 1.4, verticalAlign: "baseline" }}>[{m[1]}]</button>
    );
  });
}

async function fetchJsonFile(path, requestKey = 0, hardRefresh = false) {
  const response = await fetch(buildFetchUrl(path, requestKey), {
    cache: hardRefresh ? "reload" : "no-cache",
    headers: hardRefresh ? { "Cache-Control": "no-cache, no-store, max-age=0", Pragma: "no-cache" } : { "Cache-Control": "no-cache" },
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
  const [faqError, setFaqError] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let ignore = false;
    setLoading(true);
    setFaqError(false);
    // FAQ fetch는 cards와 분리해서 추적 — 실패 시 faqError true (PR #100 post-merge cleanup).
    // ignore check로 unmount 후 setState 방지.
    const faqPromise = fetchJsonFile("/data/faq.json", refreshKey, hardRefresh).catch(() => {
      if (!ignore) setFaqError(true);
      return [];
    });
    Promise.all([
      fetchJsonFile("/data/cards.json", refreshKey, hardRefresh).then((d) => d.cards || d).catch(() => []),
      faqPromise,
    ]).then(([c, f]) => {
      if (ignore) return;
      setCards(Array.isArray(c) ? c.map(toCompatCard) : []);
      setFaq(Array.isArray(f) ? f : []);
    }).finally(() => {
      if (!ignore) setLoading(false);
    });
    return () => { ignore = true; };
  }, [refreshKey, hardRefresh]);

  return { cards, faq, faqError, loading, cardCount: cards.length, faqCount: faq.length };
}

function useTrackerData(refreshKey = 0, hardRefresh = false) {
  const [raw, setRaw] = useState(null);
  const [policyRaw, setPolicyRaw] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let ignore = false;
    setLoading(true);
    // tracker_data + region_policy 병렬 fetch.
    // region_policy는 운영 중 데이터 업데이트 경로 (Copilot review #98 #1 지적).
    // fetch 실패해도 tracker는 계속 동작해야 하므로 catch는 null로.
    Promise.all([
      fetchJsonFile("/data/tracker_data.json", refreshKey, hardRefresh).catch(() => null),
      fetchJsonFile("/data/region_policy.json", refreshKey, hardRefresh).catch(() => null),
    ]).then(([trackerData, policyData]) => {
      if (ignore) return;
      setRaw(trackerData);
      setPolicyRaw(policyData);
    }).finally(() => { if (!ignore) setLoading(false); });
    return () => { ignore = true; };
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
    const regions = Object.keys(TRACKER_REGION).map((code) => {
      const list = items.filter((i) => i.r === code);
      if (!list.length) return null;
      return { code, flag: TRACKER_REGION[code].flag, name: TRACKER_REGION[code].name, total: list.length, ACTIVE: list.filter((i) => i.s === "ACTIVE").length };
    }).filter(Boolean);
    const upcoming = items.filter((i) => i.s === "UPCOMING").sort((a, b) => String(a.dt || "").localeCompare(String(b.dt || ""))).slice(0, 8).map((i) => ({ date: fmtDate(i.dt), title: i.t, region: i.r }));
    return { meta: { lastUpdated: raw.meta?.lastUpdated || "-", totalItems: Number(raw.meta?.totalItems ?? items.length) || items.length }, summary, regions, upcoming, items };
  }, [raw]);

  // regionPolicy: JSON 우선, 실패 시 하드코드 REGION_POLICY fallback.
  // JSON 형식: { _meta: {...}, NA: {...}, EU: {...}, CN: {...}, KR: {...}, JP: {...}, GL: {...} }
  // _meta만 있고 region 키 없는 경우는 invalid로 봐서 fallback. 일부 region만 있어도
  // 그 region만 JSON, 빠진 region은 하드코드 fallback (region별 fallback).
  const regionPolicy = useMemo(() => {
    if (!policyRaw || typeof policyRaw !== 'object') return REGION_POLICY;
    // _meta 제외하고 region 데이터가 하나라도 있는지
    const regionKeys = Object.keys(policyRaw).filter(k => !k.startsWith('_'));
    if (regionKeys.length === 0) return REGION_POLICY;
    // region별 fallback merge — JSON에 있으면 JSON, 없으면 하드코드
    const merged = { ...REGION_POLICY };
    for (const key of regionKeys) {
      const entry = policyRaw[key];
      // 최소 schema 검증 — policies 배열 + watchpoints 배열 있어야 valid
      if (entry && Array.isArray(entry.policies) && Array.isArray(entry.watchpoints)) {
        merged[key] = entry;
      }
    }
    return merged;
  }, [policyRaw]);

  return { tracker, regionPolicy, loading };
}

function latestDate(cards) {
  return [...cards.map((c) => c?.d || c?.date).filter(Boolean)].sort((a, b) => String(b).localeCompare(String(a)))[0] || null;
}

function latestCards(cards, limit = 3, region = null, targetDate = null, fallbackToLatest = false) {
  const pool = region ? cards.filter((c) => (c.r || c.region) === region) : cards;
  if (targetDate) {
    const target = fmtDate(targetDate);
    const list = pool.filter((c) => (c.d || c.date) && fmtDate(c.d || c.date) === target);
    if (list.length) return [...list].sort((a, b) => getSignalRank(b) - getSignalRank(a)).slice(0, limit);
    if (!fallbackToLatest) return [];
  }
  const ld = latestDate(pool);
  if (!ld) return [...pool].sort((a, b) => getSignalRank(b) - getSignalRank(a)).slice(0, limit);
  const list = pool.filter((c) => (c.d || c.date) === ld);
  return [...list].sort((a, b) => getSignalRank(b) - getSignalRank(a)).slice(0, limit);
}

function SmallPill({ label, dark }) {
  const t = T(dark);
  return <span style={{ fontSize: 9, fontWeight: 800, color: t.cyan, background: dark ? "rgba(88,166,255,0.14)" : "rgba(45,90,142,0.10)", padding: "4px 8px", borderRadius: 999, fontFamily: "'JetBrains Mono',monospace" }}>{label}</span>;
}

const AUTO_IMAGES = {
  POLICY: ["https://images.unsplash.com/photo-1589829085413-56de8ae18c73?auto=format&fit=crop&w=600&q=80", "https://images.unsplash.com/photo-1521791136064-7986c2920216?auto=format&fit=crop&w=600&q=80", "https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=600&q=80"],
  FINANCE: ["https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=600&q=80", "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=600&q=80", "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=600&q=80"],
  FACTORY: ["https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=600&q=80", "https://images.unsplash.com/photo-1565814329452-e1efa11c5b89?auto=format&fit=crop&w=600&q=80", "https://images.unsplash.com/photo-1616423640778-28d1b53229bd?auto=format&fit=crop&w=600&q=80"],
  AUTO: ["https://images.unsplash.com/photo-1560958089-b8a1929cea89?auto=format&fit=crop&w=600&q=80", "https://images.unsplash.com/photo-1593941707882-a5bba14938c7?auto=format&fit=crop&w=600&q=80", "https://images.unsplash.com/photo-1617704548623-340376564e68?auto=format&fit=crop&w=600&q=80"],
  BATTERY: ["https://images.unsplash.com/photo-1581092335397-9583eb92d232?auto=format&fit=crop&w=600&q=80", "https://images.unsplash.com/photo-1620800615556-91eecfc5108f?auto=format&fit=crop&w=600&q=80", "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?auto=format&fit=crop&w=600&q=80"],
  TECH: ["https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=600&q=80", "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=600&q=80", "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=600&q=80"],
  DEFAULT: ["https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=600&q=80", "https://images.unsplash.com/photo-1557683316-973673baf926?auto=format&fit=crop&w=600&q=80", "https://images.unsplash.com/photo-1579546929518-9e396f3cc809?auto=format&fit=crop&w=600&q=80"],
};

function pickHomeCover(card) {
  const text = [card?.T, card?.title, card?.sub, card?.subtitle, card?.g, card?.gate, card?.source, card?.src].filter(Boolean).join(" ").toLowerCase();
  let category = "DEFAULT";
  if (/(ira|feoc|crma|보조금|관세|규제|법안|정부|정책|세액공제)/.test(text)) category = "POLICY";
  else if (/(실적|영업이익|매출|주가|투자|적자|흑자|m&a|상장)/.test(text)) category = "FINANCE";
  else if (/(공장|양산|생산|가동|캐파|capa|증설|설비|수율)/.test(text)) category = "FACTORY";
  else if (/(테슬라|전기차|ev|완성차|현대차|기아|포드|gm|bmw|폭스바겐)/.test(text)) category = "AUTO";
  else if (/(배터리|lfp|전고체|리튬|니켈|코발트|흑연|양극재|음극재|분리막|전해액|ess|bess|catl|byd|엔솔|sdi)/.test(text)) category = "BATTERY";
  else if (/(기술|r&d|특허|연구|차세대|효율|혁신|개발|테스트|파일럿)/.test(text)) category = "TECH";
  const pool = AUTO_IMAGES[category];
  const seed = String(card?.id || card?.T || card?.title || "random_seed");
  let hash = 0;
  for (let i = 0; i < seed.length; i += 1) {
    hash = (hash << 5) - hash + seed.charCodeAt(i);
    hash |= 0;
  }
  return pool[Math.abs(hash) % pool.length];
}

// 카드 list 단위로 unique 커버 이미지 배정.
// pickHomeCover만 쓰면 카테고리당 3장 풀이라 같은 페이지에 20+장 카드면 중복 대량 발생
// (Copilot review #98 #2). list 안에서 round-robin으로 한 풀에서 나눠 쓰고,
// 풀 소진되면 다른 카테고리 풀로 넘김 → 같은 화면에서 인접 중복 최소화.
//
// 반환: { [cardKey]: imageUrl } — getCardId(card) 또는 fallback key 사용.
function assignHomeCovers(cards) {
  const result = {};
  if (!Array.isArray(cards) || cards.length === 0) return result;

  // 카테고리 분류기 (pickHomeCover와 동일 로직)
  const categorize = (card) => {
    const text = [card?.T, card?.title, card?.sub, card?.subtitle, card?.g, card?.gate, card?.source, card?.src].filter(Boolean).join(" ").toLowerCase();
    if (/(ira|feoc|crma|보조금|관세|규제|법안|정부|정책|세액공제)/.test(text)) return "POLICY";
    if (/(실적|영업이익|매출|주가|투자|적자|흑자|m&a|상장)/.test(text)) return "FINANCE";
    if (/(공장|양산|생산|가동|캐파|capa|증설|설비|수율)/.test(text)) return "FACTORY";
    if (/(테슬라|전기차|ev|완성차|현대차|기아|포드|gm|bmw|폭스바겐)/.test(text)) return "AUTO";
    if (/(배터리|lfp|전고체|리튬|니켈|코발트|흑연|양극재|음극재|분리막|전해액|ess|bess|catl|byd|엔솔|sdi)/.test(text)) return "BATTERY";
    if (/(기술|r&d|특허|연구|차세대|효율|혁신|개발|테스트|파일럿)/.test(text)) return "TECH";
    return "DEFAULT";
  };

  const cardKey = (card, idx) => String(card?.id || card?.T || card?.title || `idx_${idx}`);

  // 카테고리별 사용 인덱스 카운터 — 한 카테고리 내에서 round-robin
  const usage = {};
  // 마지막에 배정된 이미지 기록 — 인접 카드 중복 강제 회피
  let lastImage = null;

  cards.forEach((card, idx) => {
    const cat = categorize(card);
    const pool = AUTO_IMAGES[cat] || AUTO_IMAGES.DEFAULT;

    // 1차: 카테고리 풀에서 round-robin
    const startIdx = usage[cat] || 0;
    let chosen = null;
    for (let i = 0; i < pool.length; i += 1) {
      const candidate = pool[(startIdx + i) % pool.length];
      if (candidate !== lastImage) {
        chosen = candidate;
        usage[cat] = (startIdx + i + 1) % pool.length;
        break;
      }
    }
    // 풀이 1장이거나 모두 lastImage인 케이스 — 다른 카테고리 풀에서 차용
    if (!chosen) {
      const altCats = Object.keys(AUTO_IMAGES).filter((c) => c !== cat);
      for (const altCat of altCats) {
        const altPool = AUTO_IMAGES[altCat];
        const candidate = altPool[(usage[altCat] || 0) % altPool.length];
        if (candidate !== lastImage) {
          chosen = candidate;
          usage[altCat] = ((usage[altCat] || 0) + 1) % altPool.length;
          break;
        }
      }
    }
    // 최후 — 어쨌든 풀 첫 항목
    if (!chosen) chosen = pool[0];

    result[cardKey(card, idx)] = chosen;
    lastImage = chosen;
  });

  return result;
}


function ReceiptBubble({ meta, openedAt, dark }) {
  const t = T(dark);
  const d = openedAt ? new Date(openedAt) : null;
  const dateLabel = d && !Number.isNaN(d.getTime()) ? `${d.getMonth() + 1}/${d.getDate()}` : "";
  const metaParts = [];
  if (meta?.region) metaParts.push(meta.region);
  const sigShort = (meta?.signal || "i").toString().slice(0, 1).toLowerCase();
  metaParts.push(SIG_L[sigShort] || "INFO");
  if (meta?.date) metaParts.push(fmtDate(meta.date));
  const metaLine = metaParts.join(" · ");

  return (
    <div role="note" aria-label="상담 접수증" style={{ margin: "10px auto", maxWidth: "92%", padding: "10px 14px", background: dark ? "rgba(88,166,255,0.07)" : "rgba(88,166,255,0.05)", border: `1px dashed ${t.cyan}`, borderRadius: 10 }}>
      <div style={{ fontSize: 10, color: t.cyan, fontWeight: 800, marginBottom: 6, fontFamily: "'JetBrains Mono',monospace", display: "flex", alignItems: "center", gap: 6 }}><span aria-hidden="true">📥</span><span>받음{dateLabel ? ` · ${dateLabel}` : ""}</span></div>
      <div style={{ fontSize: 13, color: t.tx, fontWeight: 700, lineHeight: 1.4, marginBottom: 4, fontFamily: "'Pretendard',sans-serif" }}>{meta?.title || "(제목 없음)"}</div>
      {metaLine && <div style={{ fontSize: 9, color: t.sub, fontWeight: 700, fontFamily: "'JetBrains Mono',monospace" }}>{metaLine}</div>}
    </div>
  );
}

function FactIdText({ text, dark }) {
  if (!text) return null;
  const parts = String(text).split(/(\bf\d+\b)/g);
  return parts.map((part, i) => /^f\d+$/.test(part) ? <span key={i} style={{ color: "#58A6FF", fontWeight: 800, fontFamily: "'JetBrains Mono',monospace", background: dark ? "rgba(88,166,255,0.12)" : "rgba(45,90,142,0.08)", padding: "1px 5px", borderRadius: 4 }}>{part}</span> : <span key={i}>{part}</span>);
}

function ScoutBubble({ stageOutput, dark }) {
  const t = T(dark);
  const { summary, facts = [], unknowns = [] } = stageOutput || {};
  return (
    <div style={{ margin: "8px 0", padding: "14px 16px", background: dark ? "#1A2333" : "#FFFFFF", border: `1px solid ${t.brd}`, borderRadius: "18px 18px 18px 6px", borderLeft: "3px solid #58A6FF" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8 }}><span style={{ fontSize: 10, fontWeight: 800, color: "#58A6FF", background: dark ? "rgba(88,166,255,0.14)" : "rgba(45,90,142,0.10)", padding: "3px 8px", borderRadius: 999, fontFamily: "'JetBrains Mono',monospace" }}>📋 1차 · 사실 확인</span></div>
      {summary && <div style={{ fontSize: 13, lineHeight: 1.6, color: t.tx, marginBottom: 12, fontFamily: "'Pretendard',sans-serif" }}>{summary}</div>}
      {facts.length > 0 && (
        <div style={{ marginBottom: unknowns.length > 0 ? 12 : 0 }}>
          <div style={{ fontSize: 9, color: t.sub, fontWeight: 700, marginBottom: 6, fontFamily: "'JetBrains Mono',monospace" }}>FACTS · {facts.length}</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {facts.map((f, idx) => <div key={f.id || idx} style={{ padding: "8px 10px", background: dark ? "rgba(88,166,255,0.05)" : "rgba(88,166,255,0.03)", borderRadius: 8, border: `1px solid ${dark ? "rgba(88,166,255,0.12)" : "rgba(88,166,255,0.08)"}` }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 3, flexWrap: "wrap" }}><span style={{ fontSize: 9, fontWeight: 800, color: "#58A6FF", fontFamily: "'JetBrains Mono',monospace" }}>{f.id}</span><span style={{ fontSize: 9, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>{f.subject}{f.time ? ` · ${f.time}` : ""}{f.place ? ` · ${f.place}` : ""}</span></div>
              <div style={{ fontSize: 12, color: t.tx, lineHeight: 1.5 }}>{f.raw}</div>
              {f.value && <div style={{ fontSize: 10, color: t.cyan, marginTop: 3, fontWeight: 700, fontFamily: "'JetBrains Mono',monospace" }}>{f.value}</div>}
            </div>)}
          </div>
        </div>
      )}
      {unknowns.length > 0 && <div style={{ padding: "8px 10px", background: dark ? "rgba(125,133,144,0.06)" : "rgba(125,133,144,0.04)", borderRadius: 8, borderLeft: `2px solid ${t.sub}` }}><div style={{ fontSize: 9, color: t.sub, fontWeight: 700, marginBottom: 4, fontFamily: "'JetBrains Mono',monospace" }}>아직 모르는 것</div>{unknowns.map((u, i) => <div key={i} style={{ fontSize: 11, color: t.sub, lineHeight: 1.5, marginTop: 2 }}>· {u}</div>)}</div>}
    </div>
  );
}

function AnalystBubble({ stageOutput, dark }) {
  const t = T(dark);
  const { angle, interpretation, key_tension } = stageOutput || {};
  return (
    <div style={{ margin: "8px 0", padding: "14px 16px", background: dark ? "#1A2333" : "#FFFFFF", border: `1px solid ${t.brd}`, borderRadius: "18px 18px 18px 6px", borderLeft: "3px solid #D29922" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8, flexWrap: "wrap" }}><span style={{ fontSize: 10, fontWeight: 800, color: "#D29922", background: dark ? "rgba(210,153,34,0.14)" : "rgba(210,153,34,0.10)", padding: "3px 8px", borderRadius: 999, fontFamily: "'JetBrains Mono',monospace" }}>🔍 2차 · 핵심 각도</span>{angle && <span style={{ fontSize: 10, fontWeight: 700, color: t.tx, background: dark ? "rgba(210,153,34,0.08)" : "rgba(210,153,34,0.06)", padding: "3px 8px", borderRadius: 999, fontFamily: "'JetBrains Mono',monospace", border: `1px solid ${dark ? "rgba(210,153,34,0.2)" : "rgba(210,153,34,0.15)"}` }}>{angle}</span>}</div>
      {interpretation && <div style={{ fontSize: 13, lineHeight: 1.65, color: t.tx, marginBottom: 12, fontFamily: "'Pretendard',sans-serif" }}>{interpretation}</div>}
      {key_tension && <div style={{ padding: "10px 12px", background: dark ? "rgba(210,153,34,0.07)" : "rgba(210,153,34,0.05)", borderRadius: 8, borderLeft: "2px solid #D29922" }}><div style={{ fontSize: 9, color: "#D29922", fontWeight: 800, marginBottom: 4, fontFamily: "'JetBrains Mono',monospace" }}>⚡ 핵심 쟁점</div><div style={{ fontSize: 12, color: t.tx, lineHeight: 1.5, fontWeight: 600 }}>{key_tension}</div></div>}
    </div>
  );
}

function RedTeamBubble({ stageOutput, dark }) {
  const t = T(dark);
  const { caveat, next_checkpoints = [] } = stageOutput || {};
  return (
    <div style={{ margin: "8px 0", padding: "14px 16px", background: dark ? "#1A2333" : "#FFFFFF", border: `1px solid ${t.brd}`, borderRadius: "18px 18px 18px 6px", borderLeft: "3px solid #F85149" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 10 }}><span style={{ fontSize: 10, fontWeight: 800, color: "#F85149", background: dark ? "rgba(248,81,73,0.14)" : "rgba(248,81,73,0.10)", padding: "3px 8px", borderRadius: 999, fontFamily: "'JetBrains Mono',monospace" }}>🧪 3차 · 빨간펜</span></div>
      {caveat && <div style={{ marginBottom: 12, padding: "12px 14px", background: dark ? "rgba(248,81,73,0.06)" : "rgba(248,81,73,0.04)", borderRadius: 8, borderLeft: "2px solid #F85149" }}><div style={{ fontSize: 13, color: t.tx, lineHeight: 1.7, fontFamily: "'Pretendard',sans-serif" }}>{caveat}</div></div>}
      {next_checkpoints.length > 0 && <div style={{ padding: "10px 12px", background: dark ? "rgba(125,133,144,0.07)" : "rgba(125,133,144,0.04)", borderRadius: 8 }}><div style={{ fontSize: 9, color: t.sub, fontWeight: 800, marginBottom: 6, fontFamily: "'JetBrains Mono',monospace" }}>✅ 다음 체크포인트</div>{next_checkpoints.map((cp, i) => <div key={i} style={{ fontSize: 12, color: t.tx, lineHeight: 1.55, marginTop: i > 0 ? 6 : 0, display: "flex", gap: 8, alignItems: "flex-start" }}><span style={{ color: t.sub, fontFamily: "'JetBrains Mono',monospace", fontWeight: 800, flexShrink: 0, marginTop: 1, minWidth: 16 }}>{i + 1}.</span><span>{cp}</span></div>)}</div>}
    </div>
  );
}

function StageWrapper({ m, dark, runSuggestion, BubbleComponent, errorFallback }) {
  const t = T(dark);
  return (
    <div style={{ display: "flex", flexDirection: "column", marginBottom: 10 }}>
      <div style={{ display: "flex", justifyContent: "flex-start", width: "100%" }}>
        <img src="/data/kang.png" alt="강차장" style={{ width: 28, height: 28, borderRadius: 14, marginRight: 7, flexShrink: 0, marginTop: 2, border: "2px solid #2a1a40" }} />
        <div style={{ maxWidth: "88%" }}>{m.stage_output ? <BubbleComponent stageOutput={m.stage_output} dark={dark} /> : <div style={{ padding: "11px 14px", fontSize: 13, color: t.sub, background: dark ? "#1A2333" : "#FFFFFF", border: `1px solid ${t.brd}`, borderRadius: "18px 18px 18px 6px" }}>{errorFallback || "응답 생성에 문제가 있었어. 다시 시도해줘."}{m.stage_error && <div style={{ fontSize: 9, color: t.sub, marginTop: 6, fontFamily: "'JetBrains Mono',monospace", opacity: 0.6 }}>[{m.stage_error}]</div>}</div>}</div>
      </div>
      {m.suggestions?.length > 0 && <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 8, marginBottom: 4, paddingLeft: 35 }}>{m.suggestions.map((s) => { const isAdvance = s.hint_action === "advance_stage"; return <button key={s.label} onClick={() => runSuggestion(s)} style={{ background: isAdvance ? t.cyan : (dark ? "#1A2333" : "#fff"), color: isAdvance ? "#000" : t.cyan, border: isAdvance ? "none" : `1px solid ${t.brd}`, borderRadius: 999, padding: isAdvance ? "12px 20px" : "10px 16px", minHeight: 44, fontSize: isAdvance ? 12 : 11, fontWeight: isAdvance ? 800 : 600, cursor: "pointer", fontFamily: "'Pretendard',sans-serif" }}>{isAdvance ? `${s.label} →` : s.label}</button>; })}</div>}
    </div>
  );
}

const CHAT_WELCOME = [{ role: "assistant", content: "안녕, 강차장이야. 🔋\n\n궁금한 주제를 편하게 보내줘.\n핵심부터 짧게 정리해주고,\n관련 카드나 최근 이슈도 같이 찾아줄게." }];

function ChatBot({ dark, initialConsultation = null, initialConsultationNonce = 0, onAppCommand = null, onConsultationConsumed = null }) {
  const t = T(dark);
  // 대화 세션 보존 — 탭 이동(언마운트)에도 대화가 유지되도록 sessionStorage에서 복원.
  // 브라우저(탭)를 닫으면 자연 초기화. 컨텍스트(chatCtx)도 함께 보존해 복원 후
  // 후속 질문("그거 더 자세히")이 이어진다.
  const [msgs, setMsgs] = useState(() => {
    try { const v = JSON.parse(sessionStorage.getItem("sbtl_chat_msgs") || "null"); if (Array.isArray(v) && v.length) return v; } catch { /* noop */ }
    return CHAT_WELCOME;
  });
  const [input, setInput] = useState("");
  const [loadingMode, setLoadingMode] = useState("none");
  const [searchMode, setSearchMode] = useState("internal");
  const [extQuery, setExtQuery] = useState("");
  const endRef = useRef(null);
  const chatCtxRef = useRef({ last_turn: null, root_turn: null, selected_item_id: null, region: null, date: null });
  // 대화·컨텍스트 세션 보존 (마운트 시 복원, 변경 시 저장 — 최근 40개만).
  // 웰컴 상태(대화 없음)는 저장하지 않는다 — '새 대화' 리셋 직후 재저장으로 초기화가 무효화되지 않게.
  useEffect(() => {
    try { const c = JSON.parse(sessionStorage.getItem("sbtl_chat_ctx") || "null"); if (c && typeof c === "object") chatCtxRef.current = c; } catch { /* noop */ }
  }, []);
  useEffect(() => {
    try {
      if (msgs.length <= 1) return;
      sessionStorage.setItem("sbtl_chat_msgs", JSON.stringify(msgs.slice(-40)));
      sessionStorage.setItem("sbtl_chat_ctx", JSON.stringify(chatCtxRef.current || {}));
    } catch { /* noop */ }
  }, [msgs]);
  // 상담 진행 상태도 세션에 미러 — receipt/scout 메시지만 복원되고 상태가 없으면
  // 단계 칩(2차/3차)이 조용히 죽고 후속 질문이 상담 밖으로 새는 '보이는데 못 쓰는'
  // 세션이 된다. 복원은 대화가 실제 복원될 때만(웰컴-only면 유령 상담 방지).
  // undefined 센티널로 첫 렌더 전에 1회 복원 — consultActive가 첫 렌더부터 정확하다.
  const currentConsultRef = useRef(undefined);
  if (currentConsultRef.current === undefined) {
    let restored = null;
    try {
      const m = JSON.parse(sessionStorage.getItem("sbtl_chat_msgs") || "null");
      if (Array.isArray(m) && m.length) {
        const v = JSON.parse(sessionStorage.getItem("sbtl_chat_consult") || "null");
        if (v && typeof v === "object" && v.cardContext) restored = v;
      }
    } catch { /* noop */ }
    currentConsultRef.current = restored;
  }
  const persistConsult = () => {
    try {
      const v = currentConsultRef.current;
      if (v) sessionStorage.setItem("sbtl_chat_consult", JSON.stringify(v));
      else sessionStorage.removeItem("sbtl_chat_consult");
    } catch { /* noop */ }
  };
  const sessionHooksRef = useRef([]);
  const usedTopicsRef = useRef(new Set());
  const consultedNonceRef = useRef(0);
  const isLoading = loadingMode !== "none";

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [msgs, loadingMode]);

  const composeSessionSuggestions = (serverSugs = []) => {
    const carried = sessionHooksRef.current.filter((h) => h && h.hint_topic && !usedTopicsRef.current.has(h.hint_topic));
    const seen = new Set();
    const out = [];
    for (const s of [...carried, ...(serverSugs || [])]) {
      if (s?.label && !seen.has(s.label)) { out.push(s); seen.add(s.label); }
    }
    return out;
  };

  const toUiMessage = (data) => {
    // 에이전틱 명령 — 서버가 감지한 app_command를 앱 상태로 실행 (모든 응답 경로 공통 지점)
    if (data?.app_command && typeof onAppCommand === "function") {
      try { onAppCommand(data.app_command); } catch { /* noop */ }
    }
    return toUiMessageInner(data);
  };
  const toUiMessageInner = (data) => ({
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
      selected_item_id: nc.selected_item_id || nc.last_turn?.cards?.[0]?.id || nc.last_turn?.cards?.[0]?.url || chatCtxRef.current.selected_item_id || null,
      region: nc.last_turn?.scope?.region || chatCtxRef.current.region,
      date: nc.last_turn?.scope?.date || chatCtxRef.current.date,
    };
  };

  const ceremonyWait = async (t0, minMs = 500, maxMs = 2000) => {
    const elapsed = Date.now() - t0;
    if (elapsed >= maxMs) return;
    const wait = Math.max(0, minMs - elapsed);
    if (wait > 0) await new Promise((r) => setTimeout(r, wait));
  };

  const postChat = async (body) => {
    const res = await fetch("/api/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      const fetchError = new Error(err?.answer || "요청 처리 중 오류가 발생했어.");
      fetchError.status = res.status;
      throw fetchError;
    }
    return res.json();
  };

  const readWatchTermsSafe = () => {
    try {
      const t = JSON.parse(localStorage.getItem("sbtl_watch_terms") || "[]");
      // 전체 워치 목록 전송(과다 방지용 200 상한만). 서버는 개인화엔 앞 12개만 쓰지만
      // (api/chat.js), 에이전틱 삭제 게이팅엔 전체가 필요 — 12개 초과 사용자의 13번째+
      // 용어 삭제가 watch_absent로 오판되지 않게.
      return Array.isArray(t) ? t.slice(0, 200) : [];
    } catch { return []; }
  };

  const sendToChatApi = async (txt, mode = "internal", hint = null) => {
    // watch_terms: '내 워치 기준으로 정리해줘' 같은 개인화 질의를 서버가 처리할 수 있게 동봉.
    // last_brief_at(epoch ms, 최신 브리프 id의 wb_ 타임스탬프): brief_now 10분 쿨다운 게이팅용 —
    // 방금 발행본이 있으면 서버가 재생성 대신 열람으로 응답한다. 구형/무발행이면 0(쿨다운 없음).
    // 단, 쿨다운은 '같은 워치 범위'로 방금 만든 브리프에만 적용한다 — 워치를 바꾼 직후
    // 재발행 요청을 옛 범위 브리프로 막지 않도록, 범위가 바뀌었으면 0을 보내 재생성을 허용한다.
    // 범위 비교는 브리프와 라이브 워치 목록을 모두 네이티브로 가진 클라이언트에서 수행한다.
    const watchNow = readWatchTermsSafe();
    // 주간·월간은 별개 쿨다운 — 기간별 최신 항목을 각각 찾아 같은 범위일 때만 타임스탬프를 보낸다.
    // (period 없는 구 항목은 주간 취급. 빈 워치 범위도 terms_sig "[]" 비교로 동일하게 동작.)
    const briefAtFor = (period) => {
      // 기간·범위가 '모두' 일치하는 최신호를 찾는다 — 기간만으로 find하면 범위를 A→B→A로
      // 바꿨을 때 맨 앞의 B호에서 멈춰 범위 불일치(0)가 되고, 방금 만든 A호가 뒤에 있는데도
      // A를 다시 생성해버린다. 보관함은 최신순이라 두 조건 동시 find가 곧 '최신 동일호'.
      // 달력월호(month)·지역별호(group)는 롤링(일반) 쿨다운에서 제외 — 이 타임스탬프의
      // 유일한 소비처가 서버의 '일반' 주간/월간 쿨다운이라(달력월·지역별 요청은 서버가
      // lastAt을 아예 안 본다), 지역별 월간 발행 직후의 "월간 브리프 만들어줘"나 달력월호
      // 직후의 롤링 요청을 다른 산출물인데도 열람으로 강등시키면 안 된다.
      const latestBrief = readWeeklyBriefs().find((e) => ((e && e.period) || "weekly") === period && !(e && e.month) && !(e && e.group) && briefScopeMatches(e, watchNow));
      if (!latestBrief) return 0;
      return Number(String(latestBrief.id || "").replace(/^wb_/, "")) || 0;
    };
    const body = { message: mode === "external" ? `${txt} 외부 기사 링크 중심으로 찾아줘` : txt, context: { ...chatCtxRef.current, watch_terms: watchNow, last_brief_at: briefAtFor("weekly"), last_monthly_brief_at: briefAtFor("monthly") } };
    if (hint && (hint.hint_action || hint.hint_topic)) body.hint = { action: hint.hint_action || undefined, topic: hint.hint_topic || undefined };
    return postChat(body);
  };

  const startConsultation = async (init) => {
    if (!init?.cardContext?.card) return;
    currentConsultRef.current = { id: init.consultationId, cardContext: init.cardContext, stage1_output: null, stage2_output: null, current_stage: 0 };
    persistConsult();
    setMsgs((prev) => [...prev, { role: "receipt", card_meta: init.card_meta, opened_at: init.opened_at }]);
    setLoadingMode("typing_consult");
    const t0 = Date.now();
    try {
      const data = await postChat({ consultation: { ...init.cardContext, stage: 1 }, ticket_id: init.consultationId, context: chatCtxRef.current });
      await ceremonyWait(t0);
      updateContextFromResponse(data);
      if (data?.stage_output) {
        currentConsultRef.current.stage1_output = data.stage_output;
        currentConsultRef.current.current_stage = 1;
        persistConsult();
      }
      setMsgs((prev) => [...prev, { role: "scout", stage_output: data?.stage_output || null, suggestions: Array.isArray(data?.suggestions) ? data.suggestions : [], stage_error: data?.debug?.stage_error || null }]);
      if (init.consultationId) appendMessage(init.consultationId, { role: "assistant", content: data?.answer || "", stage: 1 });
    } catch {
      setMsgs((prev) => [...prev, { role: "assistant", content: "강차장 잠시 자리 비웠어. 잠깐 뒤에 다시 제출해줘.", suggestions: [] }]);
    } finally {
      setLoadingMode("none");
    }
  };

  const advanceConsultationStage = async (toStage) => {
    const consult = currentConsultRef.current;
    if (!consult || (toStage !== 2 && toStage !== 3)) return;
    if (toStage === 2 && !consult.stage1_output) return;
    if (toStage === 3 && (!consult.stage1_output || !consult.stage2_output)) return;
    setLoadingMode("typing_consult");
    const t0 = Date.now();
    try {
      const data = await postChat({ consultation: { ...consult.cardContext, stage: toStage, prev_stage1: consult.stage1_output, prev_stage2: toStage === 3 ? consult.stage2_output : undefined }, ticket_id: consult.id, context: chatCtxRef.current });
      await ceremonyWait(t0);
      updateContextFromResponse(data);
      if (data?.stage_output && toStage === 2) {
        currentConsultRef.current.stage2_output = data.stage_output;
        currentConsultRef.current.current_stage = 2;
      } else if (data?.stage_output && toStage === 3) currentConsultRef.current.current_stage = 3;
      persistConsult();
      setMsgs((prev) => [...prev, { role: toStage === 2 ? "analyst" : "redteam", stage_output: data?.stage_output || null, suggestions: Array.isArray(data?.suggestions) ? data.suggestions : [], stage_error: data?.debug?.stage_error || null }]);
      if (consult.id) appendMessage(consult.id, { role: "assistant", content: data?.answer || "", stage: toStage });
    } catch {
      setMsgs((prev) => [...prev, { role: "assistant", content: "강차장 잠시 자리 비웠어. 잠깐 뒤에 다시.", suggestions: [] }]);
    } finally {
      setLoadingMode("none");
    }
  };

  const sendConsultFollowup = async (txt, consult) => {
    setMsgs((prev) => [...prev, { role: "user", content: txt }]);
    if (consult.id) appendMessage(consult.id, { role: "user", content: txt });
    setLoadingMode("typing_consult");
    const t0 = Date.now();
    try {
      const data = await postChat({ message: txt, consultation: consult.cardContext, is_opener: false, ticket_id: consult.id, context: chatCtxRef.current });
      await ceremonyWait(t0);
      updateContextFromResponse(data);
      const uiMsg = toUiMessage(data);
      uiMsg.suggestions = composeSessionSuggestions(data?.suggestions);
      setMsgs((prev) => [...prev, uiMsg]);
      if (consult.id) appendMessage(consult.id, { role: "assistant", content: data?.answer || "" });
    } catch {
      setMsgs((prev) => [...prev, { role: "assistant", content: "강차장 잠시 자리 비웠어. 잠깐 뒤에 다시." }]);
    } finally {
      setLoadingMode("none");
    }
  };

  const sendWithText = async (rawText, hint = null) => {
    const txt = String(rawText || "").trim();
    if (!txt || isLoading) return;
    setInput("");
    const consult = currentConsultRef.current;
    if (consult && consult.current_stage > 0) { currentConsultRef.current = null; persistConsult(); }
    else if (consult) { await sendConsultFollowup(txt, consult); return; }
    setMsgs((prev) => [...prev, { role: "user", content: txt }]);
    setLoadingMode("typing_normal");
    try {
      const data = await sendToChatApi(txt, "internal", hint);
      updateContextFromResponse(data);
      // toUiMessage()는 app_command을 부모(onAppCommand→AppContent setState)로 디스패치하는
      // 부수효과가 있다. setMsgs 업데이터 안에서 호출하면 그 부수효과가 렌더 단계(업데이터 실행
      // 시점)에 일어나 "Cannot update AppContent while rendering ChatBot" setState-in-render
      // 경고가 뜬다. 핸들러 본문(await 이후 이벤트 컨텍스트)에서 먼저 만들어 순수 값만 넣는다.
      const uiMsg = toUiMessage(data);
      setMsgs((prev) => [...prev, uiMsg]);
    } catch {
      setMsgs((prev) => [...prev, { role: "assistant", content: "채팅 응답 중 네트워크 오류가 발생했어.", suggestions: [{ label: "오늘 핵심 카드", hint_action: "new_query", hint_topic: "news" }, { label: "관련 카드 더 보여줘", hint_action: "follow_up" }] }]);
    } finally {
      setLoadingMode("none");
    }
  };

  useEffect(() => {
    if (!initialConsultation || !initialConsultationNonce) return;
    if (consultedNonceRef.current === initialConsultationNonce) return;
    consultedNonceRef.current = initialConsultationNonce;
    void startConsultation(initialConsultation);
    // 시작했으면 seed 소비 통지 — 부모가 seed를 비워야 탭 이동 후 복귀(재마운트,
    // consultedNonceRef 초기화) 때 세션 복원과 겹쳐 같은 상담이 중복 시작되지 않는다.
    if (typeof onConsultationConsumed === "function") onConsultationConsumed();
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
      // 부수효과(app_command 디스패치)를 setMsgs 업데이터 밖 핸들러 본문에서 실행 —
      // 렌더 단계에서 부모 setState가 호출되는 setState-in-render 방지. (sendWithText 주석 참고)
      const uiMsg = toUiMessage(data);
      setMsgs((prev) => [...prev, uiMsg]);
    } catch (err) {
      let errMsg = "외부 검색 중 네트워크 오류가 발생했어.";
      if (err.status === 401 || err.status === 403) errMsg = "외부 검색 API 설정에 문제가 있는 것 같아.";
      else if (err.status === 429) errMsg = "검색 요청이 너무 많아. 잠시 후에 다시 시도해줘.";
      else if (err.status === 404) errMsg = "관련된 기사를 찾을 수 없었어.";
      setMsgs((prev) => [...prev, { role: "assistant", content: errMsg, suggestions: [{ label: "내부 카드로 검색", hint_action: "new_query" }] }]);
    } finally {
      setLoadingMode("none");
    }
  };

  const markCardSelected = (card) => {
    const id = card?.id || card?.url || card?.title || null;
    if (!id) return;
    chatCtxRef.current = { ...chatCtxRef.current, selected_item_id: id };
  };

  const runSuggestion = (suggestion) => {
    const label = typeof suggestion === "string" ? suggestion : (suggestion?.label || "");
    const hint = typeof suggestion === "object" ? suggestion : null;
    if (hint?.hint_action === "advance_stage" && hint?.hint_stage) { void advanceConsultationStage(hint.hint_stage); return; }
    const tappedTopic = hint?.hint_topic;
    if (tappedTopic && currentConsultRef.current && !currentConsultRef.current.current_stage) usedTopicsRef.current.add(tappedTopic);
    const map = {
      "오늘 핵심 카드": "오늘 뉴스 3개",
      "오늘의 시그널 TOP": "오늘 TOP 시그널 카드 보여줘",
      "외부 기사로 전환 →": "실시간 배터리 ESS 기사 검색해줘",
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
    const isExternalLabel = label === "외부 기사 링크 검색" || label === "외부 기사로 전환 →" || label.includes("외부 검색");
    if (searchMode === "external" || isExternalLabel) { void sendExternal(next, hint); return; }
    void sendWithText(next, hint);
  };

  const consult = currentConsultRef.current;
  const consultActive = !!consult && consult.current_stage > 0;

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "calc(100vh - 190px)" }}>
      <div role="log" aria-live="polite" aria-atomic="false" aria-label="대화 내역" style={{ flex: 1, overflowY: "auto", padding: "12px 14px 8px" }}>
        {msgs.length > 1 && (
          <button onClick={() => { setMsgs(CHAT_WELCOME); chatCtxRef.current = { last_turn: null, root_turn: null, selected_item_id: null, region: null, date: null }; currentConsultRef.current = null; persistConsult(); try { sessionStorage.removeItem("sbtl_chat_msgs"); sessionStorage.removeItem("sbtl_chat_ctx"); } catch { /* noop */ } }} style={{ alignSelf: "center", margin: "2px 0 8px", padding: "6px 12px", borderRadius: 999, border: `1px solid ${t.brd}`, background: "transparent", color: t.sub, fontSize: 10, fontWeight: 700, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace", display: "block", marginLeft: "auto", marginRight: "auto" }}>🧹 새 대화 시작 (이전 대화는 세션 동안 유지돼요)</button>
        )}
        {msgs.length <= 1 && <ChatGuide dark={dark} runSuggestion={runSuggestion} />}
        {msgs.map((m, i) => {
          if (m.role === "receipt") return <ReceiptBubble key={`receipt-${i}`} meta={m.card_meta} openedAt={m.opened_at} dark={dark} />;
          if (m.role === "scout") return <StageWrapper key={`scout-${i}`} m={m} dark={dark} runSuggestion={runSuggestion} BubbleComponent={ScoutBubble} errorFallback="1차 접수 중에 문제가 있었어. 다시 시도해줘." />;
          if (m.role === "analyst") return <StageWrapper key={`analyst-${i}`} m={m} dark={dark} runSuggestion={runSuggestion} BubbleComponent={AnalystBubble} errorFallback="2차 분석 중에 문제가 있었어. 다시 시도해줘." />;
          if (m.role === "redteam") return <StageWrapper key={`redteam-${i}`} m={m} dark={dark} runSuggestion={runSuggestion} BubbleComponent={RedTeamBubble} errorFallback="3차 검증 중에 문제가 있었어. 다시 시도해줘." />;
          return (
            <div key={i} role="article" aria-label={m.role === "user" ? "내 질문" : "AI 답변"} style={{ display: "flex", flexDirection: "column", alignItems: m.role === "user" ? "flex-end" : "flex-start", marginBottom: 10 }}>
              <div style={{ display: "flex", justifyContent: m.role === "user" ? "flex-end" : "flex-start", width: "100%" }}>
                {m.role === "assistant" && <img src="/data/kang.png" alt="강차장" style={{ width: 28, height: 28, borderRadius: 14, marginRight: 7, flexShrink: 0, marginTop: 2, border: "2px solid #2a1a40" }} />}
                <div style={{ maxWidth: "88%" }}>
                  <div style={{ padding: "11px 14px", fontSize: 13, lineHeight: 1.6, whiteSpace: "pre-wrap", wordBreak: "keep-all", borderRadius: m.role === "user" ? "18px 18px 6px 18px" : "18px 18px 18px 6px", background: m.role === "user" ? "#4C8DFF" : (dark ? "#1A2333" : "#FFFFFF"), color: m.role === "user" ? "#fff" : t.tx, border: m.role === "user" ? "none" : `1px solid ${t.brd}`, fontFamily: "'Pretendard', sans-serif" }}>
                    {m.sourceBadge === "internal" && <span style={{ display: "inline-block", fontSize: 10, fontWeight: 800, color: "#58A6FF", background: dark ? "rgba(88,166,255,0.14)" : "rgba(45,90,142,0.10)", padding: "3px 8px", borderRadius: 999, marginBottom: 6, fontFamily: "'JetBrains Mono',monospace" }}>📋 내부 카드 기반</span>}
                    {m.sourceBadge === "external" && <span style={{ display: "inline-block", fontSize: 10, fontWeight: 800, color: "#D29922", background: dark ? "rgba(210,153,34,0.14)" : "rgba(210,153,34,0.10)", padding: "3px 8px", borderRadius: 999, marginBottom: 6, fontFamily: "'JetBrains Mono',monospace" }}>🔗 외부 기사 링크</span>}
                    {m.sourceBadge === "hybrid" && <span style={{ display: "inline-block", fontSize: 10, fontWeight: 800, color: "#A855F7", background: dark ? "rgba(168,85,247,0.14)" : "rgba(168,85,247,0.10)", padding: "3px 8px", borderRadius: 999, marginBottom: 6, fontFamily: "'JetBrains Mono',monospace" }}>🔀 내부+외부 근거</span>}
                    {m.sourceBadge ? <div>{renderChatCitations(m.content, m.cards?.length || 0, (n) => { const el = document.getElementById(`chat-card-${i}-${n}`); if (el) { el.scrollIntoView({ behavior: "smooth", block: "center" }); el.style.boxShadow = "0 0 0 2px #58A6FF"; setTimeout(() => { el.style.boxShadow = "none"; }, 1400); } })}</div> : m.content}
                  </div>
                  {m.braveLinks?.map((link, j) => <a key={`brave-${j}`} href={link.url} target="_blank" rel="noopener noreferrer" aria-label={`Open external article: ${link.title}`} style={{ display: "block", background: dark ? "#1A1E2A" : "#FFFBF0", borderRadius: 10, padding: "10px 12px", marginTop: 6, cursor: "pointer", border: `1px solid ${dark ? "rgba(210,153,34,0.25)" : "rgba(210,153,34,0.2)"}`, textDecoration: "none" }}><div style={{ fontSize: 12, fontWeight: 700, color: t.tx, lineHeight: 1.4 }}>{link.title}</div>{link.description && <div style={{ fontSize: 11, color: t.sub, marginTop: 3, lineHeight: 1.45 }}>{link.description.slice(0, 120)}{link.description.length > 120 ? "..." : ""}</div>}<div style={{ fontSize: 10, color: "#D29922", marginTop: 4, fontWeight: 700, fontFamily: "'JetBrains Mono',monospace" }}>🔗 외부 기사 ↗</div></a>)}
                  {m.cards?.map((card, j) => {
                    const cardStyle = { display: "block", background: dark ? "#151B26" : "#f8f9fc", borderRadius: 10, padding: "10px 12px", marginTop: 6, cursor: card.url ? "pointer" : "default", border: `1px solid ${t.brd}`, textDecoration: "none" };
                    const cardContent = <><div style={{ fontSize: 12, fontWeight: 700, color: t.tx }}>{SIG_L[card.signal] || SIG_L[card.s] || "INFO"} {card.title}</div>{card.subtitle && <div style={{ fontSize: 11, color: t.sub, marginTop: 3 }}>{card.subtitle}</div>}{card.gist && <div style={{ fontSize: 10, color: t.cyan, marginTop: 4, lineHeight: 1.5, opacity: 0.85 }}>💡 {card.gist}</div>}<div style={{ fontSize: 10, color: t.sub, marginTop: 4, fontFamily: "'JetBrains Mono',monospace" }}>{fmtDate(card.date)} · {card.region} · {card.source || "source"}</div>{card.url && <div style={{ fontSize: 10, color: t.cyan, marginTop: 4, fontWeight: 700 }}>→ 원문 보기 ↗</div>}</>;
                    return card.url ? <a key={j} id={`chat-card-${i}-${j + 1}`} href={card.url} target="_blank" rel="noopener noreferrer" aria-label={`Open article: ${card.title}`} onClick={() => markCardSelected(card)} style={cardStyle}>{cardContent}</a> : <div key={j} id={`chat-card-${i}-${j + 1}`} style={cardStyle} onClick={() => markCardSelected(card)}>{cardContent}</div>;
                  })}
                </div>
              </div>
              {m.role === "assistant" && m.suggestions?.length > 0 && <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 8, marginBottom: 4, paddingLeft: 35 }}>{m.suggestions.map((s) => <button key={s.label} onClick={() => runSuggestion(s)} style={{ background: dark ? "#1A2333" : "#fff", border: `1px solid ${t.brd}`, borderRadius: 999, padding: "10px 16px", minHeight: 44, fontSize: 11, color: t.cyan, cursor: "pointer", fontFamily: "'Pretendard',sans-serif", fontWeight: 600 }}>{s.label}</button>)}</div>}
            </div>
          );
        })}
        {isLoading && <div role="status" aria-live="polite" aria-atomic="true" style={{ display: "flex", gap: 7, marginBottom: 10 }}><img src="/data/kang.png" alt="강차장" style={{ width: 28, height: 28, borderRadius: 14, flexShrink: 0, border: "2px solid #2a1a40" }} /><div style={{ padding: "10px 14px", borderRadius: "18px 18px 18px 6px", background: dark ? "#1A2333" : "#FFFFFF", border: `1px solid ${t.brd}`, fontSize: 12, color: t.sub }}>{loadingMode === "typing_consult" ? "검토 중..." : "찾아보는 중..."}</div></div>}
        <div ref={endRef} />
      </div>
      <div style={{ padding: "8px 12px 14px", background: dark ? "#0A0E14" : "#FFFFFF", borderTop: `1px solid ${t.brd}` }}>
        <div style={{ display: "flex", gap: 0, marginBottom: 8, background: dark ? "#151B26" : "#f0f0f5", borderRadius: 8, padding: 2 }}>
          <button onClick={() => setSearchMode("internal")} style={{ flex: 1, padding: "6px 0", borderRadius: 6, border: "none", background: searchMode === "internal" ? (dark ? "#1A2333" : "#fff") : "transparent", color: searchMode === "internal" ? "#58A6FF" : t.sub, fontSize: 11, fontWeight: 700, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace", boxShadow: searchMode === "internal" ? "0 1px 3px rgba(0,0,0,0.15)" : "none", transition: "all 0.15s" }}>📋 내부 카드</button>
          <button onClick={() => setSearchMode("external")} style={{ flex: 1, padding: "6px 0", borderRadius: 6, border: "none", background: searchMode === "external" ? (dark ? "#1A2333" : "#fff") : "transparent", color: searchMode === "external" ? "#D29922" : t.sub, fontSize: 11, fontWeight: 700, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace", boxShadow: searchMode === "external" ? "0 1px 3px rgba(0,0,0,0.15)" : "none", transition: "all 0.15s" }}>🔗 외부 기사</button>
        </div>
        <div style={{ display: "flex", gap: 6 }}>
          <input type="text" value={searchMode === "external" ? extQuery : input} onChange={(e) => searchMode === "external" ? setExtQuery(e.target.value) : setInput(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") searchMode === "external" ? void sendExternal(extQuery) : void sendWithText(input); }} placeholder={searchMode === "external" ? "외부 기사 검색어 입력 (예: LFP 화재 리스크)" : consultActive ? "다음 단계 버튼 → 또는 자유롭게 질문해" : "궁금한 주제를 입력해줘"} aria-label={searchMode === "internal" ? "Ask AI assistant" : "Search external articles"} style={{ flex: 1, padding: "12px 14px", minHeight: 44, borderRadius: 10, border: `1px solid ${searchMode === "external" ? (dark ? "rgba(210,153,34,0.3)" : "rgba(210,153,34,0.2)") : t.brd}`, background: searchMode === "external" ? (dark ? "#1A1E2A" : "#FFFBF0") : t.card2, color: t.tx, fontSize: 13, outline: "none", fontFamily: "'Pretendard',sans-serif" }} />
          <button onClick={() => searchMode === "external" ? void sendExternal(extQuery) : void sendWithText(input)} disabled={isLoading || (searchMode === "external" ? !extQuery.trim() : !input.trim())} aria-label={searchMode === "external" ? "Search external articles" : "Send message"} style={{ padding: "12px 18px", minHeight: 44, minWidth: 44, borderRadius: 10, border: "none", background: searchMode === "external" ? "#D29922" : t.cyan, color: "#000", fontWeight: 800, cursor: "pointer", fontSize: 13, fontFamily: "'Pretendard',sans-serif", opacity: isLoading || (searchMode === "external" ? !extQuery.trim() : !input.trim()) ? 0.55 : 1 }}>{searchMode === "external" ? "🔍" : "→"}</button>
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
    <div style={{ background: t.card2, borderRadius: 10, border: `1px solid ${t.brd}`, borderLeft: `3px solid ${statusColor}`, padding: "12px 14px" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap", marginBottom: 6 }}><span style={{ fontSize: 9, fontWeight: 800, color: statusColor, background: `${statusColor}22`, padding: "2px 7px", borderRadius: 999, fontFamily: "'JetBrains Mono',monospace" }}>{statusLabel}</span>{item.id && <span style={{ fontSize: 9, color: t.sub, fontFamily: "'JetBrains Mono',monospace", fontWeight: 700 }}>{item.id}</span>}<span style={{ fontSize: 12 }}>{flag}</span><span style={{ fontSize: 9, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>{regionName}</span>{item.dt && <span style={{ fontSize: 9, color: t.sub, marginLeft: "auto", fontFamily: "'JetBrains Mono',monospace", fontWeight: 700 }}>{fmtDate(item.dt)}</span>}</div>
      <h3 style={{ fontSize: 13, fontWeight: 800, color: t.tx, margin: "0 0 6px", lineHeight: 1.4 }}>{item.t}</h3>
      {item.d && <p style={{ fontSize: 11, color: t.sub, margin: "0 0 8px", lineHeight: 1.6 }}>{item.d}</p>}
      {item.tip && <div style={{ background: dark ? "rgba(210,153,34,0.07)" : "rgba(210,153,34,0.05)", borderLeft: "2px solid #D29922", padding: "6px 10px", borderRadius: "0 6px 6px 0", marginBottom: 8 }}><span style={{ fontSize: 10, color: "#D29922", fontWeight: 800, fontFamily: "'JetBrains Mono',monospace" }}>💡 </span><span style={{ fontSize: 11, color: t.tx, lineHeight: 1.5 }}>{item.tip}</span></div>}
      {sources.length > 0 && <div style={{ marginBottom: 8, display: "flex", flexWrap: "wrap", gap: 4 }}>{sources.map((s, i) => { const label = s.n || s.label || s.name || `source ${i + 1}`; const url = s.u || s.url || s.href; if (!url) return null; return <a key={i} href={url} target="_blank" rel="noopener noreferrer" style={{ fontSize: 10, color: t.cyan, padding: "4px 9px", borderRadius: 999, background: dark ? "rgba(88,166,255,0.10)" : "rgba(88,166,255,0.06)", textDecoration: "none", fontFamily: "'JetBrains Mono',monospace", fontWeight: 700, border: `1px solid ${dark ? "rgba(88,166,255,0.2)" : "rgba(88,166,255,0.15)"}` }}>📎 {label} ↗</a>; })}</div>}
      {hasDetail && <><button onClick={onToggle} style={{ fontSize: 10, color: t.cyan, background: "transparent", border: `1px solid ${t.brd}`, borderRadius: 6, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace", padding: "6px 10px", fontWeight: 700 }}>{expanded ? "△ 자세히 접기" : "▽ 자세히 보기"}</button>{expanded && <div style={{ marginTop: 8, padding: "10px 12px", background: dark ? "rgba(88,166,255,0.05)" : "rgba(88,166,255,0.03)", borderRadius: 8, border: `1px solid ${dark ? "rgba(88,166,255,0.12)" : "rgba(88,166,255,0.08)"}`, fontSize: 11, color: t.tx, lineHeight: 1.7, whiteSpace: "pre-line" }}>{item.detail}</div>}</>}
      {(item.lastChecked || item.checkNote) && <div style={{ fontSize: 9, color: t.sub, marginTop: 10, paddingTop: 7, borderTop: `1px solid ${t.brd}`, fontFamily: "'JetBrains Mono',monospace", lineHeight: 1.5 }}>🔍 {item.lastChecked ? `last checked: ${fmtDate(item.lastChecked)}` : "check note"}{item.checkNote && <span> — {item.checkNote}</span>}</div>}
    </div>
  );
}

function Tracker({ tracker, regionPolicy, dark }) {
  const t = T(dark);
  const d = tracker;
  const updatedLabel = fmtDate(d.meta.lastUpdated);
  const [expandedRegion, setExpandedRegion] = useState(null);
  const [expandedItemId, setExpandedItemId] = useState(null);
  const [statusFilter, setStatusFilter] = useState("all");
  const [regionFilter, setRegionFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [bookmarks, setBookmarks] = useStoredList("sbtl_bookmarks");
  const [copiedShelf, setCopiedShelf] = useState(false);
  const copyShelf = () => {
    const text = [`★ SBTL 보고함 (${bookmarks.length}건)`, ...bookmarks.map((b) => `- [${b.date}] ${b.title}${b.url ? `\n  ${b.url}` : ""}`)].join("\n");
    const done = () => { setCopiedShelf(true); setTimeout(() => setCopiedShelf(false), 1600); };
    if (navigator.clipboard?.writeText) navigator.clipboard.writeText(text).then(done).catch(() => window.prompt("복사해서 사용하세요:", text));
    else window.prompt("복사해서 사용하세요:", text);
  };
  // regionPolicy: useTrackerData가 region_policy.json을 우선 fetch하고
  // 실패 시 하드코드 REGION_POLICY로 fallback (Copilot review #98 #1).
  // prop이 없는 호출부도 안전하게 — 마지막 fallback.
  const policySource = regionPolicy || REGION_POLICY;
  const policyData = policySource[expandedRegion] || null;
  const statusRank = { ACTIVE: 0, UPCOMING: 1, WATCH: 2, DONE: 3 };
  const filteredItems = useMemo(() => {
    const sw = search.trim().toLowerCase();
    return (d.items || []).filter((it) => {
      if (statusFilter !== "all" && it.s !== statusFilter) return false;
      if (regionFilter !== "all" && it.r !== regionFilter) return false;
      if (sw) {
        const hay = [it.id, it.t, it.d, it.tip, it.detail].filter(Boolean).join(" ").toLowerCase();
        if (!hay.includes(sw)) return false;
      }
      return true;
    }).sort((a, b) => {
      const sa = statusRank[a.s] ?? 9;
      const sb = statusRank[b.s] ?? 9;
      if (sa !== sb) return sa - sb;
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
      {bookmarks.length > 0 && (
        <div style={{ background: t.card2, borderRadius: 12, padding: "12px 14px", border: `1px solid ${t.brd}` }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
            <span style={{ fontSize: 12, fontWeight: 900, color: t.tx }}>★ 보고함 <span style={{ color: t.cyan }}>{bookmarks.length}</span></span>
            <span style={{ fontSize: 9, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>NEWS에서 ☆로 저장한 카드</span>
            <button onClick={copyShelf} style={{ marginLeft: "auto", padding: "6px 10px", borderRadius: 8, border: `1px solid ${copiedShelf ? "transparent" : t.brd}`, background: copiedShelf ? t.cyan : "transparent", color: copiedShelf ? "#000" : t.cyan, fontSize: 10, fontWeight: 800, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>{copiedShelf ? "복사됨 ✓" : "목록 복사"}</button>
          </div>
          <div style={{ display: "flex", flexDirection: "column" }}>
            {bookmarks.map((b, i) => (
              <div key={b.id || i} style={{ display: "flex", alignItems: "flex-start", gap: 8, padding: "8px 0", borderTop: i > 0 ? `1px solid ${t.brd}` : "none" }}>
                <span style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace", flexShrink: 0, marginTop: 2 }}>{fmtDate(b.date)}</span>
                <span style={{ flex: 1, fontSize: 12, fontWeight: 700, color: t.tx, lineHeight: 1.45 }}>{b.title}{b.url && <a href={b.url} target="_blank" rel="noopener noreferrer" style={{ marginLeft: 6, fontSize: 10, color: t.cyan, textDecoration: "none", fontFamily: "'JetBrains Mono',monospace" }}>원문 ↗</a>}</span>
                <button onClick={() => setBookmarks(bookmarks.filter((x) => x.id !== b.id))} aria-label="보고함에서 제거" style={{ border: "none", background: "transparent", color: t.sub, fontSize: 12, cursor: "pointer", padding: "2px 4px", flexShrink: 0 }}>✕</button>
              </div>
            ))}
          </div>
        </div>
      )}
      <div style={{ background: t.card2, borderRadius: 10, padding: 14, border: `1px solid ${t.brd}` }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 10, marginBottom: 10 }}><div><div style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>STATUS</div><div style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginTop: 4 }}>LAST CHECKED {updatedLabel}</div></div><span style={{ background: t.brd, borderRadius: 4, padding: "3px 10px", fontSize: 12, fontWeight: 800, color: t.tx, fontFamily: "'JetBrains Mono',monospace" }}>{d.meta.totalItems}</span></div>
        <div style={{ display: "flex", gap: 5 }}>{Object.entries(d.summary).map(([s, n]) => <div key={s} style={{ flex: 1, background: t.bg, borderRadius: 6, padding: "8px 6px", textAlign: "center" }}><div style={{ fontSize: 16, fontWeight: 900, color: SC[s] || t.tx }}>{n}</div><div style={{ fontSize: 8, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginTop: 2 }}>{SL[s] || s}</div></div>)}</div>
      </div>
      <div><div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}><span style={{ fontSize: 10, color: "#3a6090", fontFamily: "'JetBrains Mono',monospace" }}>REGIONS — 클릭하면 권역 개요</span><div style={{ flex: 1, height: 1, background: t.brd }} /></div><div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>{d.regions.map((r) => { const isExpanded = expandedRegion === r.code; return <div key={r.code} onClick={() => setExpandedRegion((prev) => prev === r.code ? null : r.code)} style={{ background: isExpanded ? (dark ? "#1A2333" : "#EEF3FF") : t.card2, borderRadius: 8, padding: "10px 12px", border: `1px solid ${isExpanded ? t.cyan : t.brd}`, cursor: "pointer", transition: "border 0.2s" }}><div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}><span style={{ fontSize: 14 }}>{r.flag}</span><span style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>{r.ACTIVE} ACTIVE</span></div><div style={{ fontSize: 13, fontWeight: 700, color: t.tx, marginTop: 4 }}>{r.name}</div><div style={{ marginTop: 6, height: 3, borderRadius: 2, background: t.brd }}><div style={{ height: "100%", borderRadius: 2, background: SC.ACTIVE, width: pct(r.ACTIVE, r.total) }} /></div><div style={{ fontSize: 9, color: isExpanded ? t.cyan : t.sub, marginTop: 4, fontFamily: "'JetBrains Mono',monospace", textAlign: "center" }}>{isExpanded ? "△ 접기" : "▽ 개요 보기"}</div></div>; })}</div></div>
      {policyData && <div style={{ background: t.card2, borderRadius: 12, padding: "14px 16px", border: `1px solid ${t.cyan}` }}><div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}><span style={{ fontSize: 18 }}>{policyData.flag}</span><span style={{ fontSize: 14, fontWeight: 900, color: t.tx }}>{policyData.title}</span><button onClick={() => setExpandedRegion(null)} style={{ marginLeft: "auto", background: "transparent", border: `1px solid ${t.brd}`, borderRadius: 999, padding: "2px 8px", fontSize: 9, color: t.sub, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>닫기</button></div>{policyData.policies.map((p, i) => <div key={i} style={{ marginBottom: 10, padding: "8px 10px", background: dark ? "rgba(88,166,255,0.04)" : "rgba(88,166,255,0.02)", borderRadius: 8, border: `1px solid ${dark ? "rgba(88,166,255,0.08)" : "rgba(88,166,255,0.06)"}` }}><div style={{ fontSize: 11, fontWeight: 800, color: t.cyan, marginBottom: 3, fontFamily: "'JetBrains Mono',monospace" }}>{p.name}</div><div style={{ fontSize: 11, color: t.tx, lineHeight: 1.55 }}>{p.desc}</div></div>)}<div style={{ marginTop: 6, padding: "8px 10px", background: dark ? "rgba(210,153,34,0.06)" : "rgba(210,153,34,0.04)", borderRadius: 8, border: `1px solid ${dark ? "rgba(210,153,34,0.12)" : "rgba(210,153,34,0.08)"}` }}><div style={{ fontSize: 10, fontWeight: 800, color: "#D29922", marginBottom: 3, fontFamily: "'JetBrains Mono',monospace" }}>⚡ 왜 중요한지</div><div style={{ fontSize: 11, color: t.tx, lineHeight: 1.55 }}>{policyData.why}</div></div><div style={{ marginTop: 8 }}><div style={{ fontSize: 10, fontWeight: 800, color: t.sub, marginBottom: 4, fontFamily: "'JetBrains Mono',monospace" }}>👁 WATCHPOINTS</div>{policyData.watchpoints.map((wp, i) => <div key={i} style={{ fontSize: 11, color: t.tx, lineHeight: 1.55, paddingLeft: 8, borderLeft: `2px solid ${t.cyan}`, marginBottom: 4 }}>{wp}</div>)}</div><div style={{ marginTop: 10, fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace", fontStyle: "italic" }}>※ 위 내용은 권역 개요이며, 개별 정책 항목은 아래 POLICY ITEMS에서 확인하세요.</div></div>}
      <div><div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}><span style={{ fontSize: 10, color: "#3a6090", fontFamily: "'JetBrains Mono',monospace" }}>POLICY ITEMS — {filteredItems.length} / {d.items.length}</span><div style={{ flex: 1, height: 1, background: t.brd }} /></div><input type="text" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="🔍 정책 검색 (제목·설명·ID)..." aria-label="Search policy items" style={{ width: "100%", padding: "10px 14px", borderRadius: 10, border: `1px solid ${t.brd}`, fontSize: 12, outline: "none", fontFamily: "inherit", background: t.card2, color: t.tx, boxSizing: "border-box", marginBottom: 8 }} />
        <div style={{ position: "relative", marginBottom: 6 }}><div style={{ display: "flex", gap: 4, overflowX: "auto", paddingBottom: 4, scrollbarWidth: "thin" }}>{statusFilterOptions.map((s) => { const active = statusFilter === s; const label = s === "all" ? `ALL ${d.items.length}` : `${SL[s] || s} ${d.summary[s] || 0}`; const color = s === "all" ? t.cyan : (SC[s] || t.cyan); return <button key={s} onClick={() => setStatusFilter(s)} style={{ background: active ? color : t.card2, color: active ? "#000" : t.sub, border: `1px solid ${active ? "transparent" : t.brd}`, borderRadius: 999, padding: "8px 12px", minHeight: 36, fontSize: 10, fontWeight: 700, cursor: "pointer", whiteSpace: "nowrap", fontFamily: "'JetBrains Mono',monospace" }}>{label}</button>; })}</div></div>
        <div style={{ position: "relative", marginBottom: 10 }}><div style={{ display: "flex", gap: 4, overflowX: "auto", paddingBottom: 4, scrollbarWidth: "thin" }}>{regionFilterOptions.map((r) => { const active = regionFilter === r; const label = r === "all" ? "ALL REGIONS" : `${TRACKER_REGION[r]?.flag || "🌐"} ${TRACKER_REGION[r]?.name || r}`; return <button key={r} onClick={() => setRegionFilter(r)} style={{ background: active ? t.cyan : t.card2, color: active ? "#000" : t.sub, border: `1px solid ${active ? "transparent" : t.brd}`, borderRadius: 999, padding: "8px 12px", minHeight: 36, fontSize: 10, fontWeight: 700, cursor: "pointer", whiteSpace: "nowrap", fontFamily: "'JetBrains Mono',monospace" }}>{label}</button>; })}</div></div>
        {filteredItems.length === 0 ? <div style={{ padding: 20, borderRadius: 10, background: t.card2, border: `1px solid ${t.brd}`, textAlign: "center" }}><div style={{ fontSize: 24, marginBottom: 8 }}>🔍</div><div style={{ fontSize: 12, color: t.sub, lineHeight: 1.5 }}>조건에 맞는 정책이 없습니다.</div></div> : <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>{filteredItems.map((item) => { const key = item.id || `${item.r}-${item.t}`; return <TrackerItemCard key={key} item={item} dark={dark} expanded={expandedItemId === key} onToggle={() => setExpandedItemId((prev) => prev === key ? null : key)} />; })}</div>}
      </div>
      <div><div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}><span style={{ fontSize: 10, color: "#3a6090", fontFamily: "'JetBrains Mono',monospace" }}>KEY DATES</span><div style={{ flex: 1, height: 1, background: t.brd }} /></div><div style={{ background: t.card2, borderRadius: 8, padding: "4px 0", border: `1px solid ${t.brd}` }}><div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 12px 6px", borderBottom: `1px solid ${t.brd}` }}><span style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>WATCHLIST — UPCOMING TOP 8</span><span style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>LAST CHECKED {updatedLabel}</span></div>{d.upcoming.map((ev, i) => <div key={i} style={{ padding: "8px 12px", display: "flex", alignItems: "center", gap: 8, borderTop: i > 0 ? `1px solid ${t.brd}` : "none" }}><span style={{ width: 72, fontSize: 10, fontWeight: 700, color: t.sub, fontFamily: "'JetBrains Mono',monospace", flexShrink: 0, lineHeight: 1.35, whiteSpace: "normal", wordBreak: "keep-all" }}>{ev.date}</span><span style={{ flex: 1, fontSize: 12, fontWeight: 700, color: t.tx, lineHeight: 1.45 }}>{ev.title}</span></div>)}</div></div>
    </div>
  );
}

function SeriesActionButton({ label, onClick, primary = false, dark }) {
  const t = T(dark);
  return <button onClick={onClick} style={{ flex: 1, border: primary ? "none" : `1px solid ${t.brd}`, borderRadius: 10, padding: "10px 14px", background: primary ? t.cyan : "transparent", color: primary ? "#000" : t.tx, fontSize: 11, fontWeight: 800, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>{label}</button>;
}

function EpisodeCard({ item, dark }) {
  const t = T(dark);
  return <div onClick={() => item.url && window.open(item.url, "_blank")} style={{ background: t.card2, borderRadius: 10, padding: "12px 14px", border: `1px solid ${t.brd}`, cursor: item.url ? "pointer" : "default" }}><div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6, flexWrap: "wrap" }}><span style={{ fontSize: 10, color: t.sub }}>🎨 웹툰</span>{item.tag && <SmallPill label={item.tag} dark={dark} />}{item.isNew && <span style={{ fontSize: 8, fontWeight: 800, color: "#000", background: t.cyan, padding: "2px 6px", borderRadius: 999, fontFamily: "'JetBrains Mono',monospace" }}>NEW</span>}</div><h3 style={{ fontSize: 14, fontWeight: 800, color: t.tx, margin: "0 0 4px", lineHeight: 1.35 }}>{item.title}</h3><p style={{ fontSize: 11, color: t.sub, margin: 0, lineHeight: 1.5 }}>{item.subtitle}</p><div style={{ display: "flex", gap: 10, fontSize: 10, color: t.sub, marginTop: 8, fontFamily: "'JetBrains Mono',monospace" }}><span>{item.date}</span>{item.url && <span>OPEN ↗</span>}</div></div>;
}

function CollectionFolder({ collection, dark, defaultOpen = false }) {
  const t = T(dark);
  const [open, setOpen] = useState(defaultOpen);
  return <div style={{ background: t.card2, borderRadius: 16, border: `1px solid ${t.brd}`, overflow: "hidden" }}><div style={{ height: 4, background: `linear-gradient(90deg,${collection.color},${collection.color}66)` }} /><div style={{ padding: 16 }}><div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 12 }}><div style={{ flex: 1 }}><div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap", marginBottom: 6 }}><SmallPill label={collection.badge} dark={dark} /><span style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>{collection.items.length} EPISODES</span></div><h3 style={{ fontSize: 20, fontWeight: 900, color: t.tx, margin: "0 0 6px", lineHeight: 1.28 }}>{collection.title}</h3><p style={{ fontSize: 12, color: t.sub, margin: 0, lineHeight: 1.58 }}>{collection.subtitle}</p><p style={{ fontSize: 11, color: t.sub, opacity: 0.95, margin: "8px 0 0", lineHeight: 1.55 }}>{collection.description}</p></div><button onClick={() => setOpen((v) => !v)} style={{ border: "none", background: "transparent", color: t.sub, cursor: "pointer", fontSize: 18, paddingTop: 6 }}>{open ? "▾" : "▸"}</button></div><div style={{ display: "flex", gap: 8, marginTop: 14 }}><SeriesActionButton label="시리즈 소개 보기 ↗" onClick={() => window.open(collection.landingUrl, "_blank")} primary dark={dark} /><SeriesActionButton label="EP.1 시작 ↗" onClick={() => window.open(collection.items[0].url, "_blank")} dark={dark} /></div></div>{open && <div style={{ padding: "0 16px 16px", display: "flex", flexDirection: "column", gap: 10 }}>{collection.items.map((item) => <EpisodeCard key={item.id} item={item} dark={dark} />)}</div>}</div>;
}

function WebtoonLibrary({ dark, faq = [], faqError = false }) {
  const t = T(dark);
  const featured = WEBTOON_COLLECTIONS[0];

  // Phase B2: 5 sub-tab structure for LEARN. Default BASIC.
  const [learnSubTab, setLearnSubTab] = useState("basic");
  const [glossarySearch, setGlossarySearch] = useState("");
  const [glossaryCategoryFilter, setGlossaryCategoryFilter] = useState("all");

  // Phase B1.1: per-FAQ expand/collapse keyed by entry.id. Survives sub-tab switch and sort/filter changes.
  const [expandedFaqKeys, setExpandedFaqKeys] = useState(() => new Set());

  const FAQ_PREVIEW_LIMIT = 100;
  const truncateKo = (text, max = FAQ_PREVIEW_LIMIT) => {
    const s = String(text || "").trim();
    if (s.length <= max) return s;
    return s.slice(0, max).replace(/\s+\S*$/, "") + "…";
  };
  const toggleFaqExpand = (key) => {
    setExpandedFaqKeys((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  // Phase B2: search normalization — lowercase + zero-width chars + hyphen/underscore + whitespace removed.
  // "삼성 sdi" === "samsung_sdi" === "samsung-sdi" === "삼성SDI" 모두 같은 검색 키.
  const normalizeSearchText = (text) => String(text || "")
    .toLowerCase()
    .replace(/[\u200B-\u200D\uFEFF]/g, "")
    .replace(/[-_]/g, "")
    .replace(/\s+/g, "");

  const faqList = useMemo(() => Array.isArray(faq) ? faq : [], [faq]);
  const sortFaqByK = (list) => [...list].sort((a, b) =>
    String(a?.k?.[0] || "").localeCompare(String(b?.k?.[0] || ""), "ko")
  );

  // Phase B2: faq grouping by category (faq.json schema v2.0).
  const POLICY_REGIONS = [
    { key: "us_policy", flag: "🇺🇸", name: "미국" },
    { key: "eu_policy", flag: "🇪🇺", name: "유럽" },
    { key: "cn_policy", flag: "🇨🇳", name: "중국" },
    { key: "kr_policy", flag: "🇰🇷", name: "한국" },
    { key: "jp_policy", flag: "🇯🇵", name: "일본" },
  ];

  const basicEntries = useMemo(
    () => sortFaqByK(faqList.filter((e) => e?.category === "tech")),
    [faqList]
  );
  const companyEntries = useMemo(
    () => sortFaqByK(faqList.filter((e) => e?.category === "company")),
    [faqList]
  );
  const industryEntries = useMemo(
    () => sortFaqByK(faqList.filter((e) => e?.category === "industry")),
    [faqList]
  );
  const policyByRegion = useMemo(() => {
    const out = {};
    for (const region of POLICY_REGIONS) {
      out[region.key] = sortFaqByK(faqList.filter((e) => e?.category === region.key));
    }
    return out;
  }, [faqList]);
  const policyTotalCount = useMemo(
    () => POLICY_REGIONS.reduce((sum, r) => sum + (policyByRegion[r.key]?.length || 0), 0),
    [policyByRegion]
  );

  // GLOSSARY: 전체 entries with optional search + category filter.
  const glossaryCategoriesPresent = useMemo(() => {
    const seen = new Set();
    for (const e of faqList) if (e?.category) seen.add(e.category);
    return Array.from(seen);
  }, [faqList]);
  const glossaryFiltered = useMemo(() => {
    const norm = normalizeSearchText(glossarySearch);
    let list = faqList;
    if (glossaryCategoryFilter !== "all") {
      list = list.filter((e) => e?.category === glossaryCategoryFilter);
    }
    if (norm) {
      list = list.filter((e) => {
        const haystack = [
          e?.id || "",
          ...(Array.isArray(e?.k) ? e.k : []),
          e?.a || "",
        ].map(normalizeSearchText).join(" ");
        return haystack.includes(norm);
      });
    }
    return sortFaqByK(list);
  }, [faqList, glossarySearch, glossaryCategoryFilter]);

  // Shared FAQ card renderer (used by 4 sub-tabs).
  const renderFaqCard = (entry, i) => {
    const key = entry?.id || `faq-${i}-${entry?.k?.[0] || i}`;
    const fullText = String(entry?.a || "").trim();
    const isLong = fullText.length > FAQ_PREVIEW_LIMIT;
    const isExpanded = expandedFaqKeys.has(key);
    const displayText = isLong && !isExpanded ? truncateKo(fullText) : fullText;
    return (
      <div key={key} style={{ background: t.card2, borderRadius: 10, padding: "12px 14px", border: `1px solid ${t.brd}` }}>
        <div style={{ fontSize: 13, fontWeight: 800, color: t.tx, lineHeight: 1.4, marginBottom: 6 }}>
          {entry?.k?.[0] || "(제목 없음)"}
        </div>
        <div style={{ fontSize: 11, color: t.sub, lineHeight: 1.65, whiteSpace: "pre-wrap", wordBreak: "keep-all" }}>
          {displayText}
        </div>
        {isLong && (
          <button
            type="button"
            onClick={() => toggleFaqExpand(key)}
            aria-expanded={isExpanded}
            aria-label={isExpanded ? "전체 답변 접기" : "전체 답변 보기"}
            style={{
              marginTop: 8,
              fontSize: 10,
              color: t.cyan,
              background: "transparent",
              border: `1px solid ${t.brd}`,
              borderRadius: 6,
              cursor: "pointer",
              fontFamily: "'JetBrains Mono',monospace",
              padding: "6px 10px",
              fontWeight: 700,
              minHeight: 32
            }}
          >
            {isExpanded ? "△ 접기" : "▽ 펼쳐보기"}
          </button>
        )}
      </div>
    );
  };

  const subTabs = [
    { key: "basic", label: "BASIC", count: basicEntries.length },
    { key: "policy", label: "POLICY", count: policyTotalCount },
    { key: "companies", label: "COMPANIES", count: companyEntries.length + industryEntries.length },
    { key: "series", label: "SERIES", count: WEBTOON_COLLECTIONS.length },
    { key: "glossary", label: "GLOSSARY", count: faqList.length },
  ];

  // Hard error state — FAQ fetch 실패 + 데이터 0건. Series sub-tab은 여전히 작동해야 하므로 series만 active일 때는 통과.
  if (faqError && faqList.length === 0 && learnSubTab !== "series") {
    return (
      <div style={{ padding: "10px 14px 110px", display: "flex", flexDirection: "column", gap: 12 }}>
        <div style={{ position: "relative" }}>
          <div style={{ display: "flex", gap: 4, overflowX: "auto", paddingBottom: 4, scrollbarWidth: "thin" }}>
            {subTabs.map((st) => {
              const active = learnSubTab === st.key;
              return (
                <button
                  key={st.key}
                  type="button"
                  onClick={() => setLearnSubTab(st.key)}
                  aria-current={active ? "page" : undefined}
                  style={{
                    background: active ? t.cyan : t.card2,
                    color: active ? "#000" : t.sub,
                    border: `1px solid ${active ? "transparent" : t.brd}`,
                    borderRadius: 999,
                    padding: "10px 14px",
                    minHeight: 40,
                    fontSize: 11,
                    fontWeight: 800,
                    cursor: "pointer",
                    whiteSpace: "nowrap",
                    fontFamily: "'JetBrains Mono',monospace"
                  }}
                >
                  {st.label} {st.count}
                </button>
              );
            })}
          </div>
        </div>
        <div style={{ background: t.card2, borderRadius: 12, padding: 20, border: `1px solid ${t.brd}`, textAlign: "center" }}>
          <div style={{ fontSize: 24, marginBottom: 8 }}>⚠️</div>
          <div style={{ fontSize: 12, color: t.sub, lineHeight: 1.6 }}>FAQ 데이터를 불러오지 못했습니다.</div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: "10px 14px 110px", display: "flex", flexDirection: "column", gap: 12 }}>
      {/* Phase B2: 5 sub-tab navigation */}
      <div style={{ position: "relative" }}>
        <div style={{ display: "flex", gap: 4, overflowX: "auto", paddingBottom: 4, scrollbarWidth: "thin" }}>
          {subTabs.map((st) => {
            const active = learnSubTab === st.key;
            return (
              <button
                key={st.key}
                type="button"
                onClick={() => setLearnSubTab(st.key)}
                aria-current={active ? "page" : undefined}
                style={{
                  background: active ? t.cyan : t.card2,
                  color: active ? "#000" : t.sub,
                  border: `1px solid ${active ? "transparent" : t.brd}`,
                  borderRadius: 999,
                  padding: "10px 14px",
                  minHeight: 40,
                  fontSize: 11,
                  fontWeight: 800,
                  cursor: "pointer",
                  whiteSpace: "nowrap",
                  fontFamily: "'JetBrains Mono',monospace"
                }}
              >
                {st.label} {st.count}
              </button>
            );
          })}
        </div>
      </div>

      {/* BASIC — tech entries */}
      {learnSubTab === "basic" && (
        <>
          <div style={{ background: t.card2, borderRadius: 12, padding: "14px 16px", border: `1px solid ${t.brd}` }}>
            <div style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginBottom: 4 }}>BASIC · 입문</div>
            <h2 style={{ fontSize: 18, fontWeight: 900, color: t.tx, margin: 0 }}>배터리 기본 개념</h2>
            <p style={{ fontSize: 12, color: t.sub, lineHeight: 1.6, margin: "8px 0 0" }}>
              배터리·ESS를 이해하는 데 필요한 기본 용어와 개념을 모았습니다. 셀·모듈·팩 구조부터 양극재·음극재 같은 핵심 소재까지.
            </p>
          </div>
          {basicEntries.length === 0 ? (
            <div style={{ background: t.card2, borderRadius: 12, padding: 20, border: `1px solid ${t.brd}`, textAlign: "center" }}>
              <div style={{ fontSize: 24, marginBottom: 8 }}>📖</div>
              <div style={{ fontSize: 12, color: t.sub, lineHeight: 1.6 }}>등록된 항목이 없습니다.</div>
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {basicEntries.map((entry, i) => renderFaqCard(entry, i))}
            </div>
          )}
        </>
      )}

      {/* POLICY — region grouped */}
      {learnSubTab === "policy" && (
        <>
          <div style={{ background: t.card2, borderRadius: 12, padding: "14px 16px", border: `1px solid ${t.brd}` }}>
            <div style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginBottom: 4 }}>POLICY · 정책</div>
            <h2 style={{ fontSize: 18, fontWeight: 900, color: t.tx, margin: 0 }}>권역별 배터리 정책</h2>
            <p style={{ fontSize: 12, color: t.sub, lineHeight: 1.6, margin: "8px 0 0" }}>
              미국·유럽·중국·한국·일본의 핵심 배터리 정책을 권역별로 정리했습니다. 정책 일정과 시그널은 TRCK 탭에서 확인하세요.
            </p>
          </div>
          {POLICY_REGIONS.map((region) => {
            const items = policyByRegion[region.key] || [];
            if (items.length === 0) return null;
            return (
              <div key={region.key}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                  <span style={{ fontSize: 14 }}>{region.flag}</span>
                  <span style={{ fontSize: 12, fontWeight: 800, color: t.tx, fontFamily: "'JetBrains Mono',monospace" }}>
                    {region.name} · {items.length}
                  </span>
                  <div style={{ flex: 1, height: 1, background: t.brd }} />
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {items.map((entry, i) => renderFaqCard(entry, i))}
                </div>
              </div>
            );
          })}
        </>
      )}

      {/* COMPANIES — company + industry (industry visually labeled as 시장·경쟁 구도) */}
      {learnSubTab === "companies" && (
        <>
          <div style={{ background: t.card2, borderRadius: 12, padding: "14px 16px", border: `1px solid ${t.brd}` }}>
            <div style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginBottom: 4 }}>COMPANIES · 기업</div>
            <h2 style={{ fontSize: 18, fontWeight: 900, color: t.tx, margin: 0 }}>주요 기업·시장 구도</h2>
            <p style={{ fontSize: 12, color: t.sub, lineHeight: 1.6, margin: "8px 0 0" }}>
              한국·중국·미국·일본의 배터리 셀 메이커, ESS 인테그레이터, 파우치 필름 경쟁사를 정리했습니다.
            </p>
          </div>
          {companyEntries.length > 0 && (
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                <span style={{ fontSize: 12, fontWeight: 800, color: t.tx, fontFamily: "'JetBrains Mono',monospace" }}>
                  기업 · {companyEntries.length}
                </span>
                <div style={{ flex: 1, height: 1, background: t.brd }} />
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {companyEntries.map((entry, i) => renderFaqCard(entry, i))}
              </div>
            </div>
          )}
          {industryEntries.length > 0 && (
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                <span style={{ fontSize: 12, fontWeight: 800, color: "#D29922", fontFamily: "'JetBrains Mono',monospace" }}>
                  시장·경쟁 구도 · {industryEntries.length}
                </span>
                <div style={{ flex: 1, height: 1, background: t.brd }} />
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {industryEntries.map((entry, i) => renderFaqCard(entry, i))}
              </div>
            </div>
          )}
        </>
      )}

      {/* SERIES — webtoon collections (기존 hero + library label + folders) */}
      {learnSubTab === "series" && (
        <>
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
          {WEBTOON_COLLECTIONS.map((collection, idx) => (
            <CollectionFolder key={collection.id} collection={collection} dark={dark} defaultOpen={idx === 0} />
          ))}
        </>
      )}

      {/* GLOSSARY — full searchable list with category filter */}
      {learnSubTab === "glossary" && (
        <>
          <div style={{ background: t.card2, borderRadius: 12, padding: "14px 16px", border: `1px solid ${t.brd}` }}>
            <div style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginBottom: 4 }}>GLOSSARY · 사전</div>
            <h2 style={{ fontSize: 18, fontWeight: 900, color: t.tx, margin: 0 }}>전체 용어 사전</h2>
            <p style={{ fontSize: 12, color: t.sub, lineHeight: 1.6, margin: "8px 0 0" }}>
              {faqList.length}개 항목 전체에서 검색하고 카테고리별로 필터할 수 있습니다.
            </p>
          </div>
          <input
            type="text"
            value={glossarySearch}
            onChange={(e) => setGlossarySearch(e.target.value)}
            placeholder="🔍 용어·내용 검색..."
            aria-label="Search FAQ glossary"
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
              boxSizing: "border-box"
            }}
          />
          <div style={{ position: "relative" }}>
            <div style={{ display: "flex", gap: 4, overflowX: "auto", paddingBottom: 4, scrollbarWidth: "thin" }}>
              {[{ key: "all", label: `ALL ${faqList.length}` }, ...glossaryCategoriesPresent.map((c) => ({
                key: c,
                label: `${c.toUpperCase().replace(/_/g, " ")} ${faqList.filter((e) => e?.category === c).length}`,
              }))].map((opt) => {
                const active = glossaryCategoryFilter === opt.key;
                return (
                  <button
                    key={opt.key}
                    type="button"
                    onClick={() => setGlossaryCategoryFilter(opt.key)}
                    style={{
                      background: active ? t.cyan : t.card2,
                      color: active ? "#000" : t.sub,
                      border: `1px solid ${active ? "transparent" : t.brd}`,
                      borderRadius: 999,
                      padding: "8px 12px",
                      minHeight: 36,
                      fontSize: 10,
                      fontWeight: 700,
                      cursor: "pointer",
                      whiteSpace: "nowrap",
                      fontFamily: "'JetBrains Mono',monospace"
                    }}
                  >
                    {opt.label}
                  </button>
                );
              })}
            </div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: 10, color: "#3a6090", fontFamily: "'JetBrains Mono',monospace" }}>
              {glossaryFiltered.length} / {faqList.length}
            </span>
            <div style={{ flex: 1, height: 1, background: t.brd }} />
          </div>
          {glossaryFiltered.length === 0 ? (
            <div style={{ background: t.card2, borderRadius: 12, padding: 20, border: `1px solid ${t.brd}`, textAlign: "center" }}>
              <div style={{ fontSize: 24, marginBottom: 8 }}>🔍</div>
              <div style={{ fontSize: 12, color: t.sub, lineHeight: 1.6 }}>조건에 맞는 항목이 없습니다.</div>
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {glossaryFiltered.map((entry, i) => renderFaqCard(entry, i))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

function NewsDesk({ kb, onSubmitConsultation, consultSummaries = {}, dark, onWatchSeen = null, agentSeed = null, onAgentSeedConsumed = null }) {
  const t = T(dark);
  const [filter, setFilter] = useState("all");
  // 시그널(TOP/HIGH)은 지역/워치와 결합 가능한 별도 축 — "중국 TOP만"이 실제로 교집합이 되게.
  // (R8a에선 단일 축이라 서버가 시그널 면을 접었음 — 이제 서버도 복합 면을 그대로 보낸다.)
  const [sigFilter, setSigFilter] = useState(null); // null | "top" | "high"
  const [search, setSearch] = useState("");
  const [showCount, setShowCount] = useState(60);
  const [watchTerms, setWatchTerms] = useStoredList("sbtl_watch_terms");
  const [bookmarks, setBookmarks] = useStoredList("sbtl_bookmarks");
  const [watchInput, setWatchInput] = useState("");
  const [dateRange, setDateRange] = useState(0); // 0=전체, 7, 30 (일)
  const [brief, setBrief] = useState(null);
  const [briefLoadingKey, setBriefLoadingKey] = useState(null); // 진행 중 요청의 scopeKey — 다른 범위에선 로딩 표시 안 함
  const [copiedBrief, setCopiedBrief] = useState(false);
  const [copiedCiteId, setCopiedCiteId] = useState(null);
  const [profileTerm, setProfileTerm] = useState(null); // 기업/키워드 프로필 서브뷰
  const [glossaryPop, setGlossaryPop] = useState(null); // 용어 정의 바텀시트 (faq 엔트리)
  const regions = ["all", "watch", "KR", "US", "NA", "CN", "EU", "JP", "GL"]; // TOP/HIGH는 sigFilter 축으로 분리

  // 파인더 자동완성 — 기업 별칭맵(123 엔티티, 별칭으로 매치해도 canonical 제안)
  // + 용어사전(faq k[0]) + 내 워치. LLM 없이 기존 데이터 재사용.
  const [aliasNames, setAliasNames] = useState([]);
  useEffect(() => {
    let alive = true;
    fetch("/data/entity_alias_map.json").then((r) => r.json()).then((j) => {
      if (!alive) return;
      const ents = j && j.entities && typeof j.entities === "object" ? j.entities : {};
      const out = [];
      for (const key of Object.keys(ents)) {
        const e = ents[key] || {};
        const canonical = String(e.canonical || key).trim();
        if (canonical.length < 2) continue;
        const spellings = [canonical, ...(Array.isArray(e.aliases) ? e.aliases : [])].map((s) => String(s || "").trim()).filter((s) => s.length >= 2);
        out.push({ name: canonical, type: String(e.type || ""), hay: spellings.map((s) => s.toLowerCase()), spellings });
      }
      setAliasNames(out);
    }).catch(() => { /* 별칭맵 없으면 용어·워치 제안만 */ });
    return () => { alive = false; };
  }, []);
  const finderSuggests = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (q.length < 1) return [];
    const out = [];
    const push = (name, type) => { if (name && !out.some((o) => o.name === name)) out.push({ name, type }); };
    watchTerms.forEach((w) => { const lw = String(w).toLowerCase(); if (lw.includes(q) && lw !== q) push(w, "내 워치"); });
    aliasNames.forEach((e) => { if (e.name.toLowerCase() !== q && e.hay.some((h) => h.includes(q))) push(e.name, "기업"); });
    (kb.faq || []).forEach((f) => { const term = Array.isArray(f?.k) && f.k[0] ? String(f.k[0]).trim() : ""; const lt = term.toLowerCase(); if (term.length >= 2 && lt.includes(q) && lt !== q) push(term, "용어"); });
    return out.slice(0, 6);
  }, [search, aliasNames, kb.faq, watchTerms]);
  // 자동완성 키보드 조작 — ↑↓ 하이라이트 / Enter 선택 / Escape·바깥 클릭 닫기.
  // 입력이 바뀌면 하이라이트를 리셋하고 다시 연다(닫힘은 명시적 행동에만).
  const [suggestIdx, setSuggestIdx] = useState(-1);
  const [suggestOpen, setSuggestOpen] = useState(true);
  const finderRef = useRef(null);
  const pickSuggest = (s) => { if (!s) return; setSearch(s.name); setShowCount(60); setSuggestIdx(-1); };
  const onFinderKeyDown = (e) => {
    if (e.key === "Escape") { setSuggestOpen(false); setSuggestIdx(-1); return; }
    if (!finderSuggests.length || !suggestOpen) return;
    if (e.key === "ArrowDown") { e.preventDefault(); setSuggestIdx((i) => (i + 1) % finderSuggests.length); }
    else if (e.key === "ArrowUp") { e.preventDefault(); setSuggestIdx((i) => (i <= 0 ? finderSuggests.length - 1 : i - 1)); }
    else if (e.key === "Enter" && suggestIdx >= 0 && suggestIdx < finderSuggests.length) { e.preventDefault(); pickSuggest(finderSuggests[suggestIdx]); }
  };
  useEffect(() => {
    const onDown = (e) => { if (finderRef.current && !finderRef.current.contains(e.target)) { setSuggestOpen(false); setSuggestIdx(-1); } };
    document.addEventListener("mousedown", onDown);
    return () => document.removeEventListener("mousedown", onDown);
  }, []);

  // 프로필 모드에서는 해당 용어 매칭이 필터를 대체한다 (기간 칩·브리프는 그대로 적용).
  // 프로필은 경계 인식 매처 — ASCII 단어경계로 Xi/DOE/ESS 같은 짧은 표기의 오매칭 차단.
  let cards = profileTerm ? kb.cards.filter((c) => cardMatchesProfileTerm(c, profileTerm)) : filter === "all" ? kb.cards : kb.cards.filter((c) => {
    if (filter === "watch") return cardMatchesWatch(c, watchTerms);
    return (c.r || c.region) === filter;
  });

  // 시그널 축은 지역/워치 축과 교집합 (프로필 모드에선 칩이 숨어 있으므로 미적용)
  if (sigFilter && !profileTerm) {
    cards = cards.filter((c) => {
      const s = String(c.s || c.signal || "i").toLowerCase();
      return sigFilter === "top" ? (s === "t" || s === "top") : (s === "h" || s === "high");
    });
  }

  if (dateRange) cards = cards.filter((c) => cardDateWithinDays(c, dateRange));

  if (search.trim() && !profileTerm) {
    const sw = search.trim().toLowerCase();
    // 별칭 확장 — 검색어가 별칭맵의 한 그룹 표기(canonical 포함)와 정확히 일치하면
    // 그룹 표기 전체로 OR 매칭. 자동완성이 canonical(Samsung SDI)을 넣어도 카드의
    // 국문 표기(삼성SDI)가 그대로 잡히고, 별칭(닝더)을 직접 쳐도 CATL 카드가 나온다.
    // 부분어("삼성")는 그룹 확장 없이 기존 부분 매칭 그대로.
    const aliasGroup = aliasNames.find((e) => e.hay.includes(sw));
    const needles = aliasGroup ? [...new Set([sw, ...aliasGroup.hay])] : [sw];
    cards = cards.filter((c) => {
      const fields = [c.T, c.title, c.sub, c.subtitle, c.g, c.gate, c.fact, c.src, c.source, c.implicationText, Array.isArray(c.implication) ? c.implication.join(" ") : c.implication, Array.isArray(c.urls) ? c.urls.join(" ") : c.url];
      if (fields.some((v) => { const h = String(v || "").toLowerCase(); return needles.some((n) => h.includes(n)); })) return true;
      if (Array.isArray(c.k) && c.k.some((k) => { const h = String(k).toLowerCase(); return needles.some((n) => h.includes(n)); })) return true;
      if (Array.isArray(c.keywords) && c.keywords.some((k) => { const h = String(k).toLowerCase(); return needles.some((n) => h.includes(n)); })) return true;
      return false;
    });
  }

  cards = [...cards].sort((a, b) => {
    const da = String(a.d || a.date || "");
    const db = String(b.d || b.date || "");
    if (db !== da) return db.localeCompare(da);
    return getSignalRank(b) - getSignalRank(a);
  });

  const visible = cards.slice(0, showCount);
  const dates = [...new Set(visible.map((c) => c.d || c.date))].filter(Boolean);
  const todayHighlights = latestCards(kb.cards, 4, null, kstToday());
  const highlights = todayHighlights.length ? todayHighlights : latestCards(kb.cards, 4, null, null);
  const highlightsIsToday = todayHighlights.length > 0;
  // 화면 내 unique 커버 배정 — highlights와 visible 합쳐서 한 번에 (Copilot review #98 #2)
  const coverMap = useMemo(() => assignHomeCovers([...highlights, ...visible]), [highlights, visible]);
  const coverFor = (card, idx) => coverMap[String(card?.id || card?.T || card?.title || `idx_${idx}`)] || pickHomeCover(card);

  const isBookmarked = (card) => bookmarks.some((b) => b.id === getCardId(card));
  const toggleBookmark = (card) => {
    const id = getCardId(card);
    if (bookmarks.some((b) => b.id === id)) {
      setBookmarks(bookmarks.filter((b) => b.id !== id));
    } else {
      setBookmarks([{ id, title: card.title || card.T || "", date: card.date || card.d || "", url: card.url || card.primaryUrl || "", savedAt: kstToday() }, ...bookmarks].slice(0, 200));
    }
  };
  // 카드 우상단 ☆ 오버레이 — StoryNewsItem 무수정 (key는 래퍼로 이동)
  const withStar = (card, key, node) => {
    const on = isBookmarked(card);
    return (
      <div key={key} style={{ position: "relative" }}>
        {node}
        <button
          onClick={(e) => { e.stopPropagation(); toggleBookmark(card); }}
          aria-label={on ? "보고함에서 제거" : "보고함에 저장"}
          aria-pressed={on}
          style={{ position: "absolute", top: 8, right: 8, zIndex: 2, width: 34, height: 34, borderRadius: 999, border: `1px solid ${on ? "transparent" : t.brd}`, background: on ? t.cyan : (dark ? "rgba(13,17,23,0.72)" : "rgba(255,255,255,0.85)"), color: on ? "#000" : t.sub, fontSize: 15, cursor: "pointer", lineHeight: 1 }}
        >{on ? "★" : "☆"}</button>
        <button
          onClick={(e) => { e.stopPropagation(); copyCitation(card); }}
          aria-label="출처 포함 인용 복사"
          style={{ position: "absolute", top: 46, right: 8, zIndex: 2, width: 34, height: 34, borderRadius: 999, border: `1px solid ${copiedCiteId === getCardId(card) ? "transparent" : t.brd}`, background: copiedCiteId === getCardId(card) ? t.cyan : (dark ? "rgba(13,17,23,0.72)" : "rgba(255,255,255,0.85)"), color: copiedCiteId === getCardId(card) ? "#000" : t.sub, fontSize: 13, cursor: "pointer", lineHeight: 1 }}
        >{copiedCiteId === getCardId(card) ? "✓" : "📋"}</button>
        <button
          onClick={async (e) => {
            e.stopPropagation();
            // 카드 공유 — Web Share API, 미지원 브라우저는 클립보드 폴백(📋과 같은 ✓ 피드백)
            const payload = { title: card.title || card.T || "SBTL 카드", text: `${card.title || card.T || ""} (${fmtDate(card.date || card.d)})`, url: card.url || card.primaryUrl || "" };
            try {
              if (navigator.share) await navigator.share(payload);
              else { await navigator.clipboard.writeText(`${payload.text}${payload.url ? ` ${payload.url}` : ""}`); setCopiedCiteId(getCardId(card)); setTimeout(() => setCopiedCiteId(null), 1200); }
            } catch { /* 사용자가 공유 시트를 닫은 경우 등 — 무시 */ }
          }}
          aria-label="카드 공유"
          style={{ position: "absolute", top: 84, right: 8, zIndex: 2, width: 34, height: 34, borderRadius: 999, border: `1px solid ${t.brd}`, background: dark ? "rgba(13,17,23,0.72)" : "rgba(255,255,255,0.85)", color: t.sub, fontSize: 13, cursor: "pointer", lineHeight: 1 }}
        >↗</button>
      </div>
    );
  };

  // 출처 각주 포함 인용 복사 — 보고서/카톡 붙여넣기용 플레인텍스트
  const copyCitation = (card) => {
    const srcs = Array.isArray(card.fact_sources) ? card.fact_sources.filter((s) => s && (s.source_quote || s.source_url)) : [];
    const lines = [
      `${card.title || card.T || ""} (${fmtDate(card.date || card.d)} · ${card.region || card.r || ""}${(card.source || card.src) ? ` · ${card.source || card.src}` : ""})`,
      card.fact ? String(card.fact) : "",
      srcs.length ? "근거:" : "",
      ...srcs.slice(0, 4).map((s) => `- "${String(s.source_quote || "").slice(0, 300)}" — ${s.source_name || "출처"}${s.source_url ? ` ${s.source_url}` : ""}`),
      cardImplicationText(card) ? `함의: ${cardImplicationText(card)}` : "",
      (card.url || card.primaryUrl) ? `원문: ${card.url || card.primaryUrl}` : "",
    ].filter(Boolean).join("\n");
    const id = getCardId(card);
    writeClipboard(lines, () => { setCopiedCiteId(id); setTimeout(() => setCopiedCiteId(null), 1500); });
  };

  // ---- 기업/키워드 프로필: 기간 필터와 무관한 전체 활동 통계 ----
  const profileStats = useMemo(() => {
    if (!profileTerm) return null;
    const all = kb.cards.filter((c) => cardMatchesProfileTerm(c, profileTerm)); // 필터와 동일 매처 — 통계·리스트 일치
    const ds = all.map((c) => String(c.d || c.date || "")).filter(Boolean).sort();
    const regionCount = {};
    let top = 0; let high = 0;
    all.forEach((c) => {
      const r = String(c.r || c.region || "GL");
      regionCount[r] = (regionCount[r] || 0) + 1;
      const s = String(c.s || c.signal || "").toLowerCase();
      if (s === "t" || s === "top") top += 1;
      else if (s === "h" || s === "high") high += 1;
    });
    return { total: all.length, first: ds[0] || "", last: ds[ds.length - 1] || "", regions: Object.entries(regionCount).sort((a, b) => b[1] - a[1]), top, high };
  }, [profileTerm, kb.cards]);
  const profileWatched = Boolean(profileTerm) && watchTerms.some((x) => x.toLowerCase() === String(profileTerm).toLowerCase());

  // ---- 카드 텍스트 자동링크 렌더러 — 기업 엔티티(→프로필, 실선)와 용어(→팝업, 점선)를
  // 함께 건다. 기업명은 프로필이 더 가치 있어 엔티티 매칭이 우선이고 남은 구간에 용어 적용.
  // StoryNewsItem이 memo라 참조가 안정적이어야 함 (데이터·테마 바뀔 때만 재생성).
  const glossaryMatcher = useMemo(() => buildGlossaryMatcher(kb.faq), [kb.faq]);
  const entityMatcher = useMemo(() => buildEntityMatcher(aliasNames), [aliasNames]);
  const openEntityProfile = useMemo(() => (group) => {
    // 프로필은 그룹 표기 중 카드 최다 히트 표기로 연다 — canonical(Samsung SDI) 고정이면
    // 카드가 국문 표기(삼성SDI)일 때 프로필이 비는 R6 교훈의 클라이언트판. 동점은 canonical.
    // 카운트는 경계 인식(termHitBoundary) — substring이면 짧은 ASCII 별칭(Xi)이
    // Flexibility 등에 오매칭돼 부풀려져 그 표기가 뽑히고, 프로필도 그 표기로 필터돼
    // 무관 카드로 가득 찬다. 선택과 프로필 필터가 같은 매처를 써야 카운트=실제 표시.
    let best = group.name; let bestN = -1;
    (group.spellings || [group.name]).forEach((sp) => {
      const n = kb.cards.reduce((a, c) => a + (cardMatchesProfileTerm(c, sp) ? 1 : 0), 0);
      if (n > bestN) { bestN = n; best = sp; }
    });
    setProfileTerm(best);
    setShowCount(60);
  }, [kb.cards]);
  const renderCardText = useMemo(() => {
    if (!glossaryMatcher && !entityMatcher) return null;
    const linkColor = T(dark).cyan;
    const glossarySeg = (str, keyBase) => {
      const parts = glossaryMatcher ? splitGlossaryText(str, glossaryMatcher) : null;
      if (!parts) return str;
      return parts.map((p, j) => p.entry
        ? <button key={`${keyBase}g${j}`} type="button" onClick={(e) => { e.stopPropagation(); setGlossaryPop({ ...p.entry, _term: p.term }); }} aria-label={`용어 설명: ${p.term}`} style={{ border: "none", background: "transparent", padding: 0, margin: 0, font: "inherit", color: "inherit", cursor: "pointer", borderBottom: `1px dotted ${linkColor}`, wordBreak: "keep-all" }}>{p.term}</button>
        : <span key={`${keyBase}s${j}`}>{p.str}</span>);
    };
    return (text) => {
      const eParts = entityMatcher ? splitGlossaryText(text, entityMatcher) : null;
      if (!eParts) return glossarySeg(text, "t");
      return eParts.map((p, i) => p.entry
        ? <button key={`e${i}`} type="button" onClick={(e) => { e.stopPropagation(); openEntityProfile(p.entry); }} aria-label={`프로필: ${p.entry.name}`} style={{ border: "none", background: "transparent", padding: 0, margin: 0, font: "inherit", color: "inherit", cursor: "pointer", borderBottom: `1px solid ${linkColor}`, wordBreak: "keep-all" }}>{p.term}</button>
        : <span key={`s${i}`}>{glossarySeg(p.str, i)}</span>);
    };
  }, [glossaryMatcher, entityMatcher, dark, openEntityProfile]);

  // 에이전틱 명령 seed — 강차장이 요청한 프로필/피드 필터를 마운트 후 소비.
  // (브리프 열람 seed는 R12부터 브리핑룸이 소비한다 — briefSeed)
  // 소비 즉시 부모의 seed를 비활성화(onAgentSeedConsumed)해야, NEWS를 떠났다 돌아와
  // NewsDesk가 리마운트될 때(로컬 ref 초기화) 옛 명령이 재생되지 않는다.
  const agentSeedRef = useRef(0);
  useEffect(() => {
    if (!agentSeed || !agentSeed.nonce || agentSeedRef.current === agentSeed.nonce) return;
    agentSeedRef.current = agentSeed.nonce;
    let applied = false;
    if (agentSeed.profileTerm) {
      setProfileTerm(agentSeed.profileTerm);
      setShowCount(60);
      applied = true;
    } else if (agentSeed.feedFilter) {
      // 피드 필터 seed — 명령은 필터 상태의 '선언'이다: 언급된 면은 적용하고 언급 없는
      // 축은 리셋한다. 남겨두면 이전에 켜둔 토글(예: TOP)이 잔존해, 응답은 "중국으로
      // 맞춰서"라는데 화면은 중국∩TOP이 되는 라벨-화면 불일치가 생긴다.
      const ff = agentSeed.feedFilter;
      setProfileTerm(null);
      setFilter(ff.region ? ff.region : ff.watch ? "watch" : "all");
      setSigFilter(ff.signal || null);
      setDateRange(ff.range != null && ff.range !== 0 ? ff.range : 0);
      setSearch(ff.search || "");
      setShowCount(60);
      applied = true;
    }
    if (applied && typeof onAgentSeedConsumed === "function") onAgentSeedConsumed();
  }, [agentSeed, onAgentSeedConsumed]);

  // 용어 시트가 열려 있는 동안: 배경 스크롤 잠금 + Escape로 닫기
  useEffect(() => {
    if (!glossaryPop) return undefined;
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const onKey = (e) => { if (e.key === "Escape") setGlossaryPop(null); };
    window.addEventListener("keydown", onKey);
    return () => { document.body.style.overflow = prevOverflow; window.removeEventListener("keydown", onKey); };
  }, [glossaryPop]);

  // ---- 내워치 새 카드 감지용 seen 스냅샷 ----
  // 워치 피드를 열람했거나 용어 목록이 바뀐 시점의 매칭 카드 id를 저장(최신 800장 창 — 읽는 쪽도 같은 창을 봐야 함).
  // 데이터 갱신(kb.cards 변경)만으로는 갱신하지 않아야 신규 카드가 '새것'으로 남는다.
  // 용어 변경 감지는 ref가 아니라 저장된 시그니처와 비교 — 리마운트·세션을 넘어도 유실되지 않는다.
  useEffect(() => {
    try {
      if (!watchTerms.length) {
        // 마지막 용어 제거: seen 상태를 정리하고 배지를 즉시 재계산 — 잔상·스테일 sig 방지.
        // 이후 재등록은 최초 사용과 동일하게 전체 기준선부터 시작한다.
        if (localStorage.getItem("sbtl_watch_seen") !== null || localStorage.getItem("sbtl_watch_seen_sig") !== null) {
          localStorage.removeItem("sbtl_watch_seen");
          localStorage.removeItem("sbtl_watch_seen_sig");
          if (typeof onWatchSeen === "function") onWatchSeen();
        }
        return;
      }
      if (!kb.cards.length) return;
      const termsSig = JSON.stringify(watchTerms);
      const storedSig = localStorage.getItem("sbtl_watch_seen_sig");
      const firstRun = localStorage.getItem("sbtl_watch_seen") === null;
      const termsChanged = storedSig !== null && storedSig !== termsSig;
      const windowIds = () => kb.cards.filter((c) => cardMatchesWatch(c, watchTerms)).slice(0, WATCH_SEEN_WINDOW).map((c) => getCardId(c)).filter(Boolean);
      // 전체 확인 처리는 '순수 내워치 뷰'에서만 — 시그널/기간/검색이 겹쳐 있으면 화면은
      // 교집합 서브셋인데 windowIds()는 매칭 전부라, 화면에 없던 카드까지 읽음 처리돼
      // 배지가 부당하게 꺼진다(워치룸 미리보기와 같은 원칙: 표시된 것만 확인).
      // 좁힌 뷰에서 본 카드는 보수적으로 미확인 유지 — 순수 뷰를 열면 그때 확인된다.
      const pureWatchView = filter === "watch" && !profileTerm && !sigFilter && !dateRange && !search.trim();
      if (pureWatchView || firstRun) {
        // 워치 피드를 '실제로 화면에서 보고 있을 때'(프로필 서브뷰 제외) 또는 최초 기준선: 현재 매칭 전부를 확인 처리
        localStorage.setItem("sbtl_watch_seen", JSON.stringify(windowIds()));
        localStorage.setItem("sbtl_watch_seen_sig", termsSig);
        if (typeof onWatchSeen === "function") onWatchSeen(); // AppContent 배지 즉시 재계산
      } else if (termsChanged) {
        // 용어 변경(열람 아님): 새 용어의 기존 이력만 확인 처리로 편입 — 기존 용어의 미확인 카드는 보존
        let prevTerms = [];
        try { const p = JSON.parse(storedSig); prevTerms = Array.isArray(p) ? p : []; } catch { prevTerms = String(storedSig).split("·"); } // 구형 sig 호환
        const prevLower = new Set(prevTerms.map((s) => String(s).toLowerCase()));
        const added = watchTerms.filter((x) => !prevLower.has(x.toLowerCase()));
        const seen = new Set(JSON.parse(localStorage.getItem("sbtl_watch_seen") || "[]"));
        if (added.length) {
          // 기존 용어와도 매칭되던 카드는 제외 — 겹치는 미확인 카드가 조용히 '확인됨' 되지 않도록
          kb.cards.filter((c) => cardMatchesWatch(c, added) && !cardMatchesWatch(c, prevTerms)).slice(0, WATCH_SEEN_WINDOW).forEach((c) => { const id = getCardId(c); if (id) seen.add(id); });
        }
        const keep = new Set(windowIds()); // 제거된 용어의 잔여 id 정리 + 창 상한 유지
        localStorage.setItem("sbtl_watch_seen", JSON.stringify([...seen].filter((id) => keep.has(id))));
        localStorage.setItem("sbtl_watch_seen_sig", termsSig);
        if (typeof onWatchSeen === "function") onWatchSeen();
      }
    } catch { /* localStorage 불가 환경은 배지 기능만 조용히 비활성 */ }
  }, [filter, profileTerm, sigFilter, dateRange, search, watchTerms, kb.cards, onWatchSeen]);

  // ---- 흐름 브리프: 현재 필터 조합 = 범위 ----
  const scopeActive = Boolean(profileTerm) || filter !== "all" || Boolean(sigFilter) || dateRange > 0 || Boolean(search.trim());
  const scopeLabel = [
    profileTerm ? `프로필(${profileTerm})` : (filter === "watch" ? `내워치(${watchTerms.slice(0, 4).join(", ")}${watchTerms.length > 4 ? "…" : ""})` : (filter !== "all" ? filter.toUpperCase() : null)),
    sigFilter && !profileTerm ? sigFilter.toUpperCase() : null, // 시그널 축도 범위의 일부 (프로필 모드는 시그널 미적용이라 제외)
    dateRange ? `최근 ${dateRange}일` : null,
    search.trim() && !profileTerm ? `"${search.trim()}"` : null,
  ].filter(Boolean).join(" × ") || "전체";
  const briefCards = cards.slice(0, 40);
  // 브리프는 생성 시점의 범위 지문(scopeKey)과 일치할 때만 렌더·복사 — 범위 변경 후 stale 서사에 새 라벨이 붙는 것 방지
  const scopeKey = [profileTerm || "", filter, sigFilter || "", dateRange, search.trim().toLowerCase(), filter === "watch" && !profileTerm ? watchTerms.join("·") : "", briefCards.length, briefCards.length ? getCardId(briefCards[0]) : "", briefCards.length ? getCardId(briefCards[briefCards.length - 1]) : ""].join("|");
  const briefMatch = brief && brief.scopeKey === scopeKey ? brief : null;
  const briefLoading = briefLoadingKey === scopeKey; // 현재 범위의 요청일 때만 로딩으로 취급
  const briefReqRef = useRef(0); // 최신 요청만 상태를 쓸 수 있다 — 늦게 도착한 이전 범위 응답이 새 브리프를 덮어쓰는 것 방지
  const buildBrief = async () => {
    const reqId = ++briefReqRef.current;
    setBriefLoadingKey(scopeKey); setBrief(null);
    try {
      const payload = {
        scopeLabel,
        cards: briefCards.map((c) => ({
          date: c.date || c.d || "", region: c.region || c.r || "", title: c.title || c.T || "",
          fact: c.fact || c.gate || c.g || "", implication: cardImplicationText(c),
          quote: (Array.isArray(c.fact_sources) && c.fact_sources[0]?.source_quote) || "",
          quoteSource: (Array.isArray(c.fact_sources) && c.fact_sources[0]?.source_name) || "",
        })),
      };
      const r = await fetch("/api/brief", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      const j = await r.json();
      if (reqId !== briefReqRef.current) return; // 그 사이 더 새 요청이 시작됨 — 이 응답은 폐기
      if (!j?.ok) throw new Error(j?.error || "brief-failed");
      setBrief({ ...j, scopeKey, scopeLabel, refs: briefCards.map((c, i) => ({ n: i + 1, title: c.title || c.T || "", date: c.date || c.d || "", url: c.url || c.primaryUrl || "" })) });
    } catch (e) {
      if (reqId !== briefReqRef.current) return;
      setBrief({ ok: false, error: String(e?.message || e), scopeKey });
    } finally { if (reqId === briefReqRef.current) setBriefLoadingKey(null); }
  };
  const copyBriefText = () => {
    if (!briefMatch?.narrative) return;
    const text = [
      `[SBTL 흐름 브리프] ${briefMatch.scopeLabel || scopeLabel} — ${kstToday()}`,
      "",
      briefMatch.narrative,
      ...(briefMatch.watch?.length ? ["", "지켜볼 것:", ...briefMatch.watch.map((w) => `- ${w}`)] : []),
      "",
      "출처 카드:",
      ...(briefMatch.refs || []).map((r) => `[${r.n}] ${r.title} (${r.date})${r.url ? ` ${r.url}` : ""}`),
    ].join("\n");
    writeClipboard(text, () => { setCopiedBrief(true); setTimeout(() => setCopiedBrief(false), 1600); });
  };

  // 주간 브리프 복사 — 수동 브리프와 동일한 출처 각주 포맷
  return (
    <div style={{ padding: "0 14px 110px", display: "flex", flexDirection: "column", gap: 12 }}>
      {profileTerm && (
        <div style={{ background: t.card2, borderRadius: 14, padding: 16, border: `1px solid ${t.cyan}` }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <button onClick={() => { setProfileTerm(null); setShowCount(60); }} aria-label="프로필 닫기" style={{ border: `1px solid ${t.brd}`, background: "transparent", color: t.tx, borderRadius: 8, width: 32, height: 32, fontSize: 15, cursor: "pointer", lineHeight: 1, flexShrink: 0 }}>←</button>
            <h2 style={{ fontSize: 19, fontWeight: 900, color: t.tx, margin: 0, flex: 1, minWidth: 0, lineHeight: 1.3, wordBreak: "keep-all", overflowWrap: "anywhere" }}>🏢 {profileTerm}</h2>
            <button onClick={() => { if (profileWatched) setWatchTerms(watchTerms.filter((x) => x.toLowerCase() !== String(profileTerm).toLowerCase())); else setWatchTerms([...watchTerms, profileTerm]); }} style={{ padding: "7px 11px", borderRadius: 999, border: `1px solid ${profileWatched ? "transparent" : t.brd}`, background: profileWatched ? t.cyan : "transparent", color: profileWatched ? "#000" : t.sub, fontSize: 10, fontWeight: 800, cursor: "pointer", whiteSpace: "nowrap", fontFamily: "'JetBrains Mono',monospace", flexShrink: 0 }}>{profileWatched ? "★ 워치 중" : "☆ 워치 추가"}</button>
          </div>
          {profileStats && profileStats.total > 0 ? (
            <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginTop: 12, fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>
              <span>카드 <b style={{ color: t.cyan }}>{profileStats.total}</b>장</span>
              <span>TOP {profileStats.top} · HIGH {profileStats.high}</span>
              <span>{fmtDate(profileStats.first)} ~ {fmtDate(profileStats.last)}</span>
              <span>{profileStats.regions.slice(0, 3).map(([r, n]) => `${r} ${n}`).join(" · ")}</span>
            </div>
          ) : (
            <div style={{ marginTop: 12, fontSize: 11, color: t.sub, lineHeight: 1.5 }}>이 용어와 매칭되는 카드가 아직 없습니다.</div>
          )}
          <div style={{ marginTop: 8, fontSize: 9, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>아래 타임라인은 최신순 · 기간 칩과 📝 브리프가 이 프로필 범위에 적용됩니다</div>
        </div>
      )}
      {!profileTerm && (
        /* 퀵 파인더 — 검색·필터를 피드 최상단 스티키로 (찾기 우선 구성) */
        <div style={{ position: "sticky", top: 0, zIndex: 20, background: t.bg, padding: "8px 0 8px", margin: "-10px 0 2px", borderBottom: `1px solid ${t.brd}` }}>
          <div ref={finderRef} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8, position: "relative" }}>
            <input type="text" value={search} onChange={(e) => { setSearch(e.target.value); setShowCount(60); setSuggestIdx(-1); setSuggestOpen(true); }} onKeyDown={onFinderKeyDown} placeholder="🔍 기업·키워드·이슈 검색" aria-label="카드 검색" role="combobox" aria-expanded={suggestOpen && finderSuggests.length > 0} aria-autocomplete="list" aria-controls="finder-suggest-list" style={{ flex: 1, padding: "11px 14px", borderRadius: 10, border: `1px solid ${t.brd}`, fontSize: 12.5, outline: "none", fontFamily: "inherit", background: t.card2, color: t.tx, boxSizing: "border-box" }} />
            {scopeActive && <div style={{ padding: "8px 12px", borderRadius: 8, background: cards.length === 0 ? "rgba(248,81,73,0.1)" : t.card, border: `1px solid ${cards.length === 0 ? "rgba(248,81,73,0.3)" : t.brd}`, fontSize: 11, fontWeight: 800, color: cards.length === 0 ? "#F85149" : t.cyan, fontFamily: "'JetBrains Mono',monospace", whiteSpace: "nowrap" }}>{cards.length}건</div>}
            {suggestOpen && finderSuggests.length > 0 && (
              <div id="finder-suggest-list" role="listbox" style={{ position: "absolute", top: "100%", left: 0, right: 0, zIndex: 30, background: t.card, border: `1px solid ${t.brd}`, borderRadius: 10, marginTop: 4, overflow: "hidden", boxShadow: "0 10px 26px rgba(0,0,0,0.4)" }}>
                {finderSuggests.map((s, i) => (
                  <button key={`${s.type}-${s.name}`} role="option" aria-selected={suggestIdx === i} onClick={() => pickSuggest(s)} onMouseEnter={() => setSuggestIdx(i)} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", width: "100%", padding: "10px 13px", border: "none", background: suggestIdx === i ? t.card2 : "transparent", color: t.tx, fontSize: 12, fontWeight: 600, cursor: "pointer", textAlign: "left" }}>
                    <span>{s.name}</span>
                    <span style={{ fontSize: 9, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>{s.type}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
          <div style={{ position: "relative" }}>
            <div style={{ display: "flex", gap: 4, overflowX: "auto", paddingBottom: 4, scrollbarWidth: "thin" }}>{regions.map((r) => { const label = r === "all" ? `ALL ${kb.cardCount}` : r === "watch" ? `★ 내워치${watchTerms.length ? ` ${watchTerms.length}` : ""}` : `${REG_FLAG[r] || ""} ${r}`; return <button key={r} onClick={() => { setFilter(r); setShowCount(60); }} style={{ background: filter === r ? t.cyan : t.card2, color: filter === r ? "#000" : t.sub, border: `1px solid ${filter === r ? "transparent" : t.brd}`, borderRadius: 999, padding: "9px 13px", minHeight: 40, fontSize: 10, fontWeight: 700, cursor: "pointer", whiteSpace: "nowrap", fontFamily: "'JetBrains Mono',monospace" }}>{label}</button>; })}</div>
            <div style={{ position: "absolute", right: 0, top: 0, bottom: 0, width: 32, background: `linear-gradient(to left, ${t.bg}, transparent)`, pointerEvents: "none" }} />
          </div>
          <div style={{ display: "flex", gap: 4, marginTop: 2, alignItems: "stretch" }}>
            {[{ v: 0, l: "전체 기간" }, { v: 7, l: "최근 7일" }, { v: 30, l: "최근 30일" }].map((opt) => <button key={opt.v} onClick={() => { setDateRange(opt.v); setShowCount(60); }} style={{ background: dateRange === opt.v ? t.cyan : t.card2, color: dateRange === opt.v ? "#000" : t.sub, border: `1px solid ${dateRange === opt.v ? "transparent" : t.brd}`, borderRadius: 999, padding: "7px 12px", fontSize: 10, fontWeight: 700, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>{opt.l}</button>)}
            <div style={{ width: 1, background: t.brd, margin: "3px 2px" }} />
            {/* 시그널 토글 — 지역/워치·기간과 결합되는 별도 축 (재탭으로 해제) */}
            {[{ v: "top", l: "TOP", c: "#F85149" }, { v: "high", l: "HIGH", c: "#D29922" }].map((opt) => { const on = sigFilter === opt.v; return <button key={opt.v} onClick={() => { setSigFilter(on ? null : opt.v); setShowCount(60); }} aria-pressed={on} style={{ background: on ? opt.c : t.card2, color: on ? "#fff" : t.sub, border: `1px solid ${on ? "transparent" : t.brd}`, borderRadius: 999, padding: "7px 12px", fontSize: 10, fontWeight: 800, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>{opt.l}</button>; })}
          </div>
          {cards.length === 0 && scopeActive && <div style={{ marginTop: 8, padding: 12, borderRadius: 10, background: t.card, border: `1px solid ${t.brd}`, textAlign: "center", fontSize: 11, color: t.sub }}>검색 결과가 없어요 — 다른 검색어나 필터를 시도해보세요</div>}
        </div>
      )}
      {!profileTerm && <div style={{ background: t.card2, borderRadius: 14, padding: 16, border: `1px solid ${t.brd}` }}><h2 style={{ fontSize: 22, fontWeight: 900, color: t.tx, margin: "0 0 6px", lineHeight: 1.25 }}>날짜별 시그널 피드</h2><p style={{ fontSize: 12, color: t.sub, margin: 0, lineHeight: 1.6 }}>최신 카드부터 날짜 기준으로 정렬했습니다. 같은 날짜 안에서는 중요도가 높은 이슈를 먼저 보여줍니다.</p></div>}
      {!profileTerm && <div style={{ background: t.card2, borderRadius: 14, padding: 16, border: `1px solid ${t.brd}` }}><div style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginBottom: 4 }}>EDITOR'S PICKS</div><h3 style={{ fontSize: 18, fontWeight: 900, color: t.tx, margin: "0 0 12px" }}>{highlightsIsToday ? "오늘의 핵심 카드" : "최신 핵심 카드"}</h3>{highlights.length ? <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>{highlights.map((card, i) => withStar(card, `${card.id || card.T || card.title}-${i}`, <StoryNewsItem card={card} dark={dark} onSubmitConsultation={onSubmitConsultation} consultationHint={consultSummaries[getCardId(card)] || null} coverImage={coverFor(card, i)} renderText={renderCardText} />))}</div> : <div style={{ fontSize: 12, color: t.sub, lineHeight: 1.6 }}>오늘 기준 등록된 뉴스카드가 아직 없습니다.</div>}</div>}
      {profileTerm && <div style={{ display: "flex", gap: 4 }}>{[{ v: 0, l: "전체 기간" }, { v: 7, l: "최근 7일" }, { v: 30, l: "최근 30일" }].map((opt) => <button key={opt.v} onClick={() => { setDateRange(opt.v); setShowCount(60); }} style={{ background: dateRange === opt.v ? t.cyan : t.card2, color: dateRange === opt.v ? "#000" : t.sub, border: `1px solid ${dateRange === opt.v ? "transparent" : t.brd}`, borderRadius: 999, padding: "7px 12px", fontSize: 10, fontWeight: 700, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>{opt.l}</button>)}</div>}
      {profileTerm && profileStats && profileStats.total > 0 && cards.length === 0 && (
        <div style={{ padding: 16, borderRadius: 10, background: t.card, border: `1px solid ${t.brd}`, textAlign: "center" }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: t.tx, marginBottom: 4 }}>선택한 기간에 해당하는 카드가 없습니다</div>
          <div style={{ fontSize: 11, color: t.sub, lineHeight: 1.6, marginBottom: 10 }}>이 프로필의 카드 {profileStats.total}장은 모두 그 이전 기간입니다.</div>
          <button onClick={() => { setDateRange(0); setShowCount(60); }} style={{ padding: "8px 14px", borderRadius: 8, border: "none", background: t.cyan, color: "#000", fontSize: 11, fontWeight: 800, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>전체 기간으로 보기</button>
        </div>
      )}
      {!profileTerm && filter === "watch" && (
        <div style={{ background: t.card2, borderRadius: 12, padding: "12px 14px", border: `1px solid ${t.brd}` }}>
          <div style={{ fontSize: 10, color: t.sub, fontFamily: "'JetBrains Mono',monospace", marginBottom: 8 }}>★ 내 워치 — 기업·키워드를 등록하면 해당 카드만 모아 봅니다 · 용어 옆 📊 = 프로필</div>
          <div style={{ display: "flex", gap: 6, marginBottom: watchTerms.length ? 8 : 0 }}>
            <input type="text" value={watchInput} onChange={(e) => setWatchInput(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") { const v = watchInput.trim(); if (v && !watchTerms.some((x) => x.toLowerCase() === v.toLowerCase())) setWatchTerms([...watchTerms, v]); setWatchInput(""); } }} placeholder="예: CATL, 전고체, 리튬..." aria-label="워치 용어 추가" style={{ flex: 1, padding: "9px 12px", borderRadius: 8, border: `1px solid ${t.brd}`, fontSize: 12, outline: "none", fontFamily: "inherit", background: t.bg, color: t.tx, boxSizing: "border-box" }} />
            <button onClick={() => { const v = watchInput.trim(); if (v && !watchTerms.some((x) => x.toLowerCase() === v.toLowerCase())) setWatchTerms([...watchTerms, v]); setWatchInput(""); }} style={{ padding: "9px 14px", borderRadius: 8, border: "none", background: t.cyan, color: "#000", fontSize: 11, fontWeight: 800, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>추가</button>
          </div>
          {watchTerms.length > 0 && <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>{watchTerms.map((term) => <span key={term} style={{ display: "inline-flex", alignItems: "center", gap: 6, background: t.bg, border: `1px solid ${t.brd}`, borderRadius: 999, padding: "5px 8px 5px 11px", fontSize: 11, fontWeight: 700, color: t.tx }}>{term}<button onClick={() => { setProfileTerm(term); setShowCount(60); }} aria-label={`${term} 프로필 보기`} style={{ border: "none", background: "transparent", color: t.cyan, fontSize: 12, cursor: "pointer", padding: 8, margin: -5, lineHeight: 1 }}>📊</button><button onClick={() => setWatchTerms(watchTerms.filter((x) => x !== term))} aria-label={`${term} 삭제`} style={{ border: "none", background: "transparent", color: t.sub, fontSize: 12, cursor: "pointer", padding: 8, margin: -5, lineHeight: 1 }}>✕</button></span>)}</div>}
          {watchTerms.length === 0 && <div style={{ fontSize: 11, color: t.sub, marginTop: 8, lineHeight: 1.5 }}>아직 등록된 용어가 없습니다. 위에 기업명이나 키워드를 입력해 보세요.</div>}
        </div>
      )}
      {scopeActive && cards.length >= 2 && (
        <div style={{ background: t.card2, borderRadius: 12, padding: "12px 14px", border: `1px solid ${briefMatch?.narrative ? t.cyan : t.brd}` }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
            <span style={{ fontSize: 12, fontWeight: 900, color: t.tx }}>📝 흐름 브리프</span>
            <span style={{ fontSize: 9, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>{scopeLabel} · 카드 {briefCards.length}장{cards.length > 40 ? " (최신 40장)" : ""}</span>
            {!briefMatch && <button onClick={buildBrief} disabled={briefLoading} style={{ marginLeft: "auto", padding: "7px 12px", borderRadius: 8, border: "none", background: briefLoading ? t.brd : t.cyan, color: "#000", fontSize: 10, fontWeight: 800, cursor: briefLoading ? "default" : "pointer", fontFamily: "'JetBrains Mono',monospace" }}>{briefLoading ? "엮는 중..." : "이 조합으로 만들기"}</button>}
            {briefMatch && <button onClick={() => setBrief(null)} style={{ marginLeft: "auto", padding: "6px 10px", borderRadius: 8, border: `1px solid ${t.brd}`, background: "transparent", color: t.sub, fontSize: 10, fontWeight: 800, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>닫기</button>}
          </div>
          {briefMatch && briefMatch.ok === false && <div style={{ marginTop: 10, fontSize: 11, color: "#F85149", lineHeight: 1.5 }}>브리프 생성에 실패했습니다 ({briefMatch.error}). <button onClick={buildBrief} style={{ border: "none", background: "transparent", color: t.cyan, fontSize: 11, fontWeight: 800, cursor: "pointer", padding: 0 }}>다시 시도</button></div>}
          {briefMatch?.narrative && (
            <div style={{ marginTop: 10 }}>
              <div style={{ fontSize: 12.5, color: t.tx, lineHeight: 1.75, paddingLeft: 10, borderLeft: `3px solid ${t.cyan}`, wordBreak: "keep-all" }}>{briefMatch.narrative}</div>
              {briefMatch.watch?.length > 0 && (
                <div style={{ marginTop: 10 }}>
                  <div style={{ fontSize: 10, fontWeight: 800, color: t.sub, marginBottom: 4, fontFamily: "'JetBrains Mono',monospace" }}>👁 지켜볼 것</div>
                  {briefMatch.watch.map((w, i) => <div key={i} style={{ fontSize: 11.5, color: t.tx, lineHeight: 1.6, paddingLeft: 8, borderLeft: `2px solid ${t.brd}`, marginBottom: 4, wordBreak: "keep-all" }}>{w}</div>)}
                </div>
              )}
              <div style={{ display: "flex", gap: 6, marginTop: 10 }}>
                <button onClick={copyBriefText} style={{ flex: 1, padding: "9px 12px", borderRadius: 8, border: `1px solid ${copiedBrief ? "transparent" : t.brd}`, background: copiedBrief ? t.cyan : "transparent", color: copiedBrief ? "#000" : t.cyan, fontSize: 11, fontWeight: 800, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>{copiedBrief ? "복사됨 ✓" : "브리프 복사 (출처 각주 포함)"}</button>
                <button onClick={buildBrief} disabled={briefLoading} style={{ padding: "9px 12px", borderRadius: 8, border: `1px solid ${t.brd}`, background: "transparent", color: t.sub, fontSize: 11, fontWeight: 800, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>{briefLoading ? "..." : "다시"}</button>
              </div>
              <div style={{ marginTop: 6, fontSize: 9, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>문장 끝 [n]은 아래 피드의 카드 순번(최신순) 인용입니다 · 복사 시 출처 목록이 각주로 붙습니다</div>
            </div>
          )}
        </div>
      )}
      {dates.map((date) => <div key={date}><div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}><span style={{ fontSize: 10, color: "#3a6090", fontFamily: "'JetBrains Mono',monospace" }}>{fmtDate(date)}</span><div style={{ flex: 1, height: 1, background: t.brd }} /></div><div style={{ display: "flex", flexDirection: "column", gap: 10 }}>{visible.filter((c) => (c.d || c.date) === date).map((card, i) => withStar(card, `${card.id || date}-${i}`, <StoryNewsItem card={card} dark={dark} onSubmitConsultation={onSubmitConsultation} consultationHint={consultSummaries[getCardId(card)] || null} coverImage={coverFor(card, i)} renderText={renderCardText} />))}</div></div>)}
      {visible.length < cards.length && <button onClick={() => setShowCount((prev) => prev + 60)} style={{ width: "100%", padding: 12, marginTop: 16, borderRadius: 10, border: `1px solid ${t.brd}`, background: t.card2, color: t.tx, fontWeight: 700, cursor: "pointer" }}>더 보기 ({Math.min(showCount, cards.length)} / {cards.length})</button>}
      {glossaryPop && (
        <div onClick={() => setGlossaryPop(null)} role="dialog" aria-modal="true" aria-label="용어 설명" style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.45)", zIndex: 60, display: "flex", alignItems: "flex-end", justifyContent: "center" }}>
          <div onClick={(e) => e.stopPropagation()} style={{ width: "100%", maxWidth: 480, maxHeight: "70vh", overflowY: "auto", overscrollBehavior: "contain", background: t.card2, borderRadius: "16px 16px 0 0", padding: "18px 16px calc(20px + env(safe-area-inset-bottom, 0px))", border: `1px solid ${t.brd}`, boxSizing: "border-box" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
              <span style={{ fontSize: 15, fontWeight: 900, color: t.tx, flex: 1 }}>📖 {glossaryPop._term || (Array.isArray(glossaryPop.k) && glossaryPop.k[0]) || "용어"}</span>
              {glossaryPop.category && <span style={{ fontSize: 9, fontWeight: 800, color: t.sub, border: `1px solid ${t.brd}`, borderRadius: 999, padding: "3px 8px", fontFamily: "'JetBrains Mono',monospace" }}>{String(glossaryPop.category).toUpperCase().replace(/_/g, " ")}</span>}
              <button autoFocus onClick={() => setGlossaryPop(null)} aria-label="닫기" style={{ border: "none", background: "transparent", color: t.sub, fontSize: 16, cursor: "pointer", padding: 10, margin: -6, lineHeight: 1 }}>✕</button>
            </div>
            <div style={{ fontSize: 12.5, color: t.tx, lineHeight: 1.75, wordBreak: "keep-all" }}>{glossaryPop.a}</div>
            {(() => { const term = glossaryPop._term || (Array.isArray(glossaryPop.k) && glossaryPop.k[0]) || ""; const kws = [term, ...(Array.isArray(glossaryPop.k) ? glossaryPop.k : [])].map((s) => String(s).toLowerCase()); const watched = watchTerms.some((x) => kws.includes(x.toLowerCase())); return term ? (
              <button onClick={() => { if (!watched) setWatchTerms([...watchTerms, term]); setGlossaryPop(null); }} style={{ marginTop: 14, width: "100%", padding: "10px 12px", borderRadius: 8, border: `1px solid ${watched ? "transparent" : t.brd}`, background: watched ? t.brd : "transparent", color: watched ? t.sub : t.cyan, fontSize: 11, fontWeight: 800, cursor: watched ? "default" : "pointer", fontFamily: "'JetBrains Mono',monospace" }}>{watched ? "★ 이미 내워치에 있습니다" : `☆ "${term}" 내워치에 추가`}</button>
            ) : null; })()}
          </div>
        </div>
      )}
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
  // 상담 seed는 1회성 — ChatBot이 시작하면 비운다. 남겨두면 탭 이동 후 복귀(재마운트)
  // 때 세션 복원(sbtl_chat_msgs)과 겹쳐 같은 상담이 다시 시작된다. nonce는 보존해
  // 이후 제출과의 단조 증가 비교가 유지되게 한다.
  const markConsultationConsumed = useMemo(() => () => setConsultationSeed((s) => (s.data ? { data: null, nonce: s.nonce } : s)), []);
  const [consultSummaries, setConsultSummaries] = useState(() => typeof window !== "undefined" ? getAllCardConsultationSummaries() : {});
  const kb = useKnowledgeBase(refreshKey, hardRefresh);
  // 내워치 새 카드 배지 — NewsDesk가 기록한 seen 스냅샷과 현재 카드를 비교.
  // NewsDesk가 스냅샷을 쓸 때 onWatchSeen으로 버전을 올려 같은 탭에 머물러도 배지가 즉시 꺼진다.
  const [watchSeenVersion, setWatchSeenVersion] = useState(0);
  const bumpWatchSeen = useMemo(() => () => setWatchSeenVersion((v) => v + 1), []);
  const watchNewCount = useMemo(() => {
    try {
      const seenRaw = localStorage.getItem("sbtl_watch_seen");
      if (seenRaw === null) return 0; // 스냅샷 생기기 전(첫 사용)에는 배지 없음
      const terms = JSON.parse(localStorage.getItem("sbtl_watch_terms") || "[]");
      if (!Array.isArray(terms) || !terms.length || !kb.cards.length) return 0;
      const seen = new Set(JSON.parse(seenRaw));
      // 쓰는 쪽과 동일한 최신 N장 창 안에서만 비교 — 창 밖 옛 카드가 영구 미확인으로 남는 것 방지
      const matches = [];
      for (const c of kb.cards) {
        if (cardMatchesWatch(c, terms)) {
          matches.push(c);
          if (matches.length >= WATCH_SEEN_WINDOW) break;
        }
      }
      return matches.filter((c) => !seen.has(getCardId(c))).length;
    } catch { return 0; }
  }, [kb.cards, tab, watchSeenVersion]); // eslint-disable-line react-hooks/exhaustive-deps
  // 기존 사용자 기준선: 워치 용어만 있고 seen 스냅샷이 없으면 NEWS 탭(NewsDesk) 진입 전에도 한 번 생성 —
  // 스냅샷 없이 데이터가 갱신되면 신규 카드가 first-run으로 묻혀 배지가 영영 안 뜨는 것 방지. NewsDesk와 동일한 창 시맨틱스.
  useEffect(() => {
    if (!kb.cards.length) return;
    try {
      if (localStorage.getItem("sbtl_watch_seen") !== null) return;
      const terms = JSON.parse(localStorage.getItem("sbtl_watch_terms") || "[]");
      if (!Array.isArray(terms) || !terms.length) return;
      const ids = kb.cards.filter((c) => cardMatchesWatch(c, terms)).slice(0, WATCH_SEEN_WINDOW).map((c) => getCardId(c)).filter(Boolean);
      localStorage.setItem("sbtl_watch_seen", JSON.stringify(ids));
      localStorage.setItem("sbtl_watch_seen_sig", JSON.stringify(terms));
      bumpWatchSeen();
    } catch { /* localStorage 불가 환경은 배지 기능만 조용히 비활성 */ }
  }, [kb.cards, bumpWatchSeen]);

  // ---- 주간 브리프 자동 생성 — 앱 접속 시 1회 시도 ----
  // 조건: 내워치 존재 + 최근 7일 매칭 카드 2장 이상 + 직전 생성 후 7일 경과.
  // 실패는 조용히 넘기고 다음 접속에서 재시도. 서버는 기존 /api/brief 재사용.
  const [weeklyBriefs, setWeeklyBriefs] = useState(() => (typeof window !== "undefined" ? readWeeklyBriefs() : []));
  const weeklyAttemptRef = useRef(false);
  const weeklyAttemptScopeRef = useRef(null); // 시도 플래그가 걸린 워치 범위 — 범위가 바뀌면 재시도 허용

  // ---- 에이전틱 명령 디스패처 — 강차장(챗)이 보낸 app_command를 앱 상태로 실행 ----
  // 챗은 chatbot 탭에서만 살아 있으므로 실행 시점에 NewsDesk는 언마운트 상태 —
  // 워치는 localStorage에 직접 쓰고(다음 NEWS 마운트가 fresh로 읽음), 화면 이동이
  // 필요한 명령은 newsSeed로 NewsDesk에 전달한다.
  const [newsSeed, setNewsSeed] = useState({ profileTerm: null, feedFilter: null, nonce: 0 });
  // 브리프 열람 seed — 브리핑룸(Watchroom)이 소비한다(R12: 선반이 NEWS→브리핑룸으로 이사).
  // open이면 선반을 펼치고 period/month/group/id로 호수를 지목한다.
  const [briefSeed, setBriefSeed] = useState({ open: false, period: null, month: null, group: null, specSig: null, id: null, nonce: 0 });
  const markBriefSeedConsumed = useMemo(() => () => setBriefSeed((s) => (s.open ? { ...s, open: false, period: null, month: null, group: null, specSig: null, id: null } : s)), []);
  // NewsDesk가 seed를 소비한 뒤 지시 내용을 비운다(nonce는 유지해 다음 명령의 증가와
  // 구분). 이렇게 해야 NEWS 재방문(NewsDesk 리마운트)에서 옛 프로필/선반이 재생되지 않는다.
  const markNewsSeedConsumed = useMemo(() => () => setNewsSeed((s) => (s.profileTerm || s.feedFilter ? { ...s, profileTerm: null, feedFilter: null } : s)), []);
  // 브리프 생성 실행부 — 패시브(접속 시 1회, 주간)와 강제 발행(brief_now 명령·워치룸 버튼,
  // 주간/월간)이 공유. force는 7일 주기 게이트만 우회하고 잠금·시그니처 가드·12주 캡은 유지.
  // 워치가 비어 있으면 거절 대신 '전체' 범위(창 내 시그널 상위 카드)로 폴백 — 온보딩을
  // 스킵한 유저(다수 예상)도 브리프를 경험하게 한다. 자동(패시브) 발행도 동일 폴백.
  const [weeklyGenerating, setWeeklyGenerating] = useState(false);
  // 강제 발행이 실패하면(예: 축 브리프에서 gemini 불안정 + groq 폴백 제외) 조용히 사라지는
  // 대신 사용자에게 보이는 메시지를 남긴다 — 챗·워치룸이 "만들게"라고 약속했는데 화면에
  // 아무것도 없는 상태를 방지(graceful degrade). 패시브(자동)는 조용히 넘어가도 무방.
  const [weeklyError, setWeeklyError] = useState(null);
  const runWeeklyBrief = useMemo(() => (opts = {}) => {
    const force = !!opts.force;
    // 달력월("2026-05", R11): 재료를 그 달로 한정하는 월간 계열 산출물. 락·보관·표시는
    // 월간 규약을 따르고, entry.month로 롤링 월간과 구별된다. 항상 force 경로(패시브 없음).
    const month = /^\d{4}-(0[1-9]|1[0-2])$/.test(String(opts.month || "")) ? opts.month : null;
    const period = month || opts.period === "monthly" ? "monthly" : "weekly";
    // 커스텀 조합(R14 빌더): 사용자가 고른 축 spec 배열이 오면 group="custom". spec은
    // entry에 함께 저장돼(spec_sig) 같은 조합만 쿨다운을 물린다. 항상 force(패시브 없음).
    const customSpec = normalizeCustomSpec(opts.customSpec); // 정규화·직렬화는 seed·게이트와 공용(spec_sig 일치 계약)
    const group = customSpec ? "custom" : opts.group === "region" ? "region" : opts.group === "theme" ? "theme" : null; // 구성(R11 지역별·R13 주제별·R14 커스텀)
    const windowDays = period === "monthly" ? 30 : 7;
    const inWindow = (c) => (month ? cardInMonth(c, month) : cardDateWithinDays(c, windowDays));
    if (!kb.cards.length) return;
    try {
      const rawTerms = JSON.parse(localStorage.getItem("sbtl_watch_terms") || "[]");
      // 커스텀은 항상 '전체' 창 풀 — 축을 직접 고르는 조합에 워치 필터가 겹치면 빌더 칩의
      // 카드 수 뱃지(전체 기준)와 실제 재료가 어긋난다. terms를 비워 전체 규약(R9,
      // terms_sig "[]")을 그대로 태운다 — scopeLabel·시그니처·풀 선택이 특례 없이 동작.
      // scopeAll(R15d): 라이브러리 호수의 '새 재료로 다시 발행' — 라이브러리는 전체 범위라
      // 재발행도 전체로 강제해야 같은 산출물의 갱신이 된다(워치 범위로 새면 다른 호수).
      const scopeAll = !!opts.scopeAll || !!customSpec;
      const terms = scopeAll ? [] : Array.isArray(rawTerms) ? rawTerms : [];
      const existing = readWeeklyBriefs();
      // 주기 판정은 '같은 범위의 주간호'만 본다 — 기간(월간호가 주간 발행을 막지 않게)에
      // 더해 범위까지 봐야 한다: 온보딩 스킵 → 자동 "주간 전체"(terms_sig "[]") 발행 →
      // 첫 워치 등록 시, 그 전체호가 충족으로 잡히면 개인화 내워치 브리프가 7일간 안 만들어진다.
      // (brief_now 쿨다운이 이미 terms_sig 범위 한정인 것과 같은 규약 — R7 교훈)
      // 상태에는 전체 목록을 그대로 반영한다(다른 탭의 월간·타범위 발행도 화면에 보이게).
      if (!force && !weeklyBriefDue(plainWeeklyEntries(existing).filter((e) => briefScopeMatches(e, terms)))) {
        // 다른 탭이 이미 발행했거나 항목 내용(read 등)을 갱신한 경우 — 화면에 반영.
        // 내용 전체 비교로 동일할 때만 이전 참조 유지 (보관함 ≤12항목이라 비용 무시 가능)
        setWeeklyBriefs((prev) => (JSON.stringify(prev) === JSON.stringify(existing) ? prev : existing));
        return;
      }
      const sigRank = { t: 3, h: 2, m: 1, i: 0 };
      // 전체 범위 풀은 정렬 없이 창 전체 — 축 선별(computeBriefAxes)이 이야기 단위로 고른다.
      // 워치 범위는 기존 flat 유지: 이미 주어(엔티티)가 고정된 좁은 범위라 축이 불필요하고,
      // 실측에서도 유일하게 처음부터 잘 되던 케이스다.
      const matched = terms.length
        ? kb.cards.filter((c) => cardMatchesWatch(c, terms) && inWindow(c)).slice(0, 40)
        : kb.cards.filter(inWindow);
      // 재료 미달 조기 종료 — 강제 발행(사용자가 버튼/명령으로 기다리는 중)은 조용히 죽지
      // 않는다: 게이트는 렌더 시점, 여기는 클릭 시점 창(cardDateWithinDays가 벽시계 기준)
      // 이라 KST 09시 경계에서 게이트 통과 후 재료가 빠질 수 있다(#173 graceful 규약).
      if (matched.length < 2) {
        if (force) setWeeklyError("재료가 부족해 브리프를 만들지 못했어 — 기간을 넓히거나 잠시 후 다시 시도해줘.");
        return;
      }
      // 크로스탭 잠금 — 동시에 뜬 두 탭이 '같은 산출물'을 중복 생성(LLM 이중 호출)하지 않도록.
      // 토큰(타임스탬프_난수)을 쓰고 fetch 직전에 소유권을 재확인한다: localStorage 쓰기는
      // 오리진 단위로 직렬화되므로 최종 토큰과 일치하는 탭은 정확히 하나다.
      // 락은 반드시 기간별 — 주간과 월간은 서로 다른 산출물이라 한 락을 공유하면, 접속 시
      // 패시브 주간 발행(R9로 빈 워치 유저도 자동 발행하므로 흔해졌다)이 도는 동안 들어온
      // 월간 수동 요청이 "만들게" 약속만 하고 조용히 폐기된다(force는 in-flight 가드도
      // 조용히 버리므로 사용자에겐 아무 일도 안 일어난 것처럼 보임).
      // 범위(scope)는 락 키에 넣지 않는다 — 워치 변경 중 겹침은 in-flight 시그니처 가드가
      // 낡은 결과를 버리고 bumpWatchSeen으로 현재 범위 재평가를 예약해 스스로 회복한다.
      // 락은 '산출물' 단위로 분리 — 달력월('5월호' 생성 중 '4월호')·구성(월간 vs 지역별
      // 월간)이 다르면 다른 산출물이라 막지 않는다. 쿨다운·보관이 이미 month·group으로
      // 구별되는데 락만 공유하면, 일반 월간 생성 중 들어온 지역별 월간 요청이 락 체크에서
      // 물러나며 "만들게" 약속 후 아무것도 안 나온다(force는 in-flight도 조용히 버림).
      // 커스텀은 spec까지 키에 넣지 않는다 — 조합이 달라도 같은 `_custom` 락(2분 TTL)을
      // 공유하는데, 커스텀은 수동 전용이라 동시 발행 자체가 연타이고 락이 그 연타를 막는
      // 것이 오히려 의도된 동작이다(범위를 락 키에 안 넣는 것과 같은 계열의 절충).
      const lockKey = `${WEEKLY_BRIEF_LOCK_KEY}_${period}${month ? `_${month}` : ""}${group ? `_${group}` : ""}`;
      const lockToken = `${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
      try {
        const rawLock = localStorage.getItem(lockKey);
        const lockAt = Number(String(rawLock || "").split("_")[0] || 0);
        if (rawLock && Date.now() - lockAt < WEEKLY_BRIEF_LOCK_TTL) return;
        localStorage.setItem(lockKey, lockToken);
      } catch { /* 잠금 불가 환경은 그대로 진행 */ }
      if (!force) weeklyAttemptRef.current = true;
      if (force) setWeeklyError(null); // 새 시도 시작 — 이전 실패 메시지 소거
      setWeeklyGenerating(true);
      const termsSigAtRequest = JSON.stringify(terms); // 빈 워치는 "[]" — 기존 시그니처 비교가 그대로 동작
      const periodLabel = month
        ? `${Number(month.slice(0, 4))}년 ${Number(month.slice(5))}월`
        : period === "monthly" ? "월간" : "주간";
      const scopeLabel = (terms.length
        ? `${periodLabel} 내워치(${terms.slice(0, 4).join(", ")}${terms.length > 4 ? "…" : ""})`
        : `${periodLabel} 전체`) + (group === "custom"
        ? ` · 커스텀(${customSpec.map((s) => s.key).slice(0, 3).join("·")}${customSpec.length > 3 ? "…" : ""})`
        : group === "region" ? " · 지역별" : group === "theme" ? " · 주제별" : "");
      (async () => {
        try {
          // 소유권 재확인 — check-then-set 사이에 같이 진입한 다른 탭이 토큰을 덮었으면 물러난다
          try {
            await new Promise((resolve) => setTimeout(resolve, 50));
            if (localStorage.getItem(lockKey) !== lockToken) return;
          } catch { /* 확인 불가 환경은 진행 */ }
          const toPayloadCard = (c) => ({
            date: c.date || c.d || "", region: c.region || c.r || "", title: c.title || c.T || "",
            fact: c.fact || c.gate || c.g || "", implication: cardImplicationText(c),
            quote: (Array.isArray(c.fact_sources) && c.fact_sources[0]?.source_quote) || "",
            quoteSource: (Array.isArray(c.fact_sources) && c.fact_sources[0]?.source_name) || "",
          });
          // 축 구성: 지역별(group=region)이면 카드 region 필드 기준 상위 지역이 축이 되고,
          // 전체 범위(워치 없음)면 축 시장이 '이야기가 되는 묶음'을 고른다. 워치 범위는
          // flat 유지(주어가 고정된 좁은 범위 — 단, 지역별 명시 요청은 워치 범위에도 적용).
          // 축이 서버 최소치(총 4장, need-axes-with-cards) 미달이면 flat(시그널 상위 40장)
          // 으로 폴백해 브리프는 반드시 나온다 — 축 payload가 400으로 거절되면 여기서
          // 조용히 실패하기 때문(flat이면 2장으로도 충분했을 상황).
          // briefCards는 [n] 인용 ↔ refs 대응의 정본 — 서버가 축 순서대로 전역 번호를
          // 붙이므로 flatMap 순서와 정확히 일치한다.
          let payload;
          let briefCards = matched;
          let axes = null;
          if (group === "custom") {
            // 사용자 선택 순서 그대로 — 정렬하지 않는다(순서가 곧 편집 의도). 겹침은
            // spec 순서 greedy 소진으로 배타화(computeCustomAxes 내부). 워치 용어 축은
            // 경계 인식 매칭(cardMatchesProfileTerm) — 빌더 칩 카운트·미리보기와 동일식이어야
            // 하고(삼자 일치), 짧은 ASCII 별칭(EVE·Xi)의 substring 오매칭을 막는다(Codex #185 R5).
            axes = computeCustomAxes(matched, customSpec, { maxPerAxis: 8, watchMatch: (c, term) => cardMatchesProfileTerm(c, term) });
          } else if (group === "region") {
            // 6리전 전부 — topK=4는 매달 두 지역을 떨궜다(실측: 2026-06 한국 30장 통째 탈락).
            // 축당 8장으로 총량을 다스린다(6×8≈48장, 서버 출력 상한 5000tok과 페어).
            axes = computeRegionAxes(matched, { topK: 6, maxPerAxis: 8 });
          } else if (group === "theme") {
            // 주제 사전 상위 6개(월별 적격 주제 실측 4~8개) — greedy 배타로 카드 중복 없음
            axes = computeThemeAxes(matched, { topK: 6, maxPerAxis: 8 });
          } else if (!terms.length) {
            const aliasEntities = await loadAliasEntities();
            // 월간 전체는 축 5개 — 한 달 200장+에서 4개 축은 폭이 좁다(사용자 피드백)
            axes = computeBriefAxes(matched, aliasEntities || {}, { topK: period === "monthly" ? 5 : 3 });
          }
          const axisCardTotal = (axes || []).reduce((a, ax) => a + ax.cards.length, 0);
          if (axes && axes.length && axisCardTotal >= 4) {
            briefCards = axes.flatMap((ax) => ax.cards);
            payload = { scopeLabel, axes: axes.map((ax) => ({ key: ax.key, cards: ax.cards.map(toPayloadCard) })) };
          } else if (group === "custom") {
            // 커스텀은 flat 폴백 금지 — '고른 축 조합'이 산출물 정체성이라, 축이 무너졌는데
            // 전체 창 시그널 상위 40장을 '커스텀(…)' 라벨·spec_sig로 발행하면 오표기다
            // (지역별·주제별의 폴백은 '그래도 그 기간 브리프'라는 정체성이 남지만 커스텀은 아님).
            // 빌더 게이트(렌더 시점)와 여기(클릭 시점)의 창이 벽시계 경계에서 어긋날 수 있어
            // 이 경로는 실재한다 — 정직하게 실패를 알리고 중단한다(락·스피너는 finally가 정리).
            setWeeklyError("고른 축의 재료가 부족해 브리프를 만들지 못했어 — 축을 바꾸거나 기간을 넓혀줘.");
            return;
          } else if (!terms.length || group) {
            const sigOrder = (c) => sigRank[String(c.s || c.signal || "i").toLowerCase()[0]] || 0;
            briefCards = matched.slice().sort((a, b) => sigOrder(b) - sigOrder(a)).slice(0, 40);
            payload = { scopeLabel, cards: briefCards.map(toPayloadCard) };
          } else {
            payload = { scopeLabel, cards: briefCards.map(toPayloadCard) };
          }
          const r = await fetch("/api/brief", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
          const j = await r.json().catch(() => null);
          if (!j?.ok || !j.narrative) {
            // 강제 발행 실패는 사용자에게 알린다(graceful degrade). unavailable(축 모드 gemini
            // 실패 등)은 일시적 안내로, 그 외는 일반 재시도 안내로. 패시브는 조용히 넘어간다.
            if (force) setWeeklyError(j?.unavailable
              ? "지금은 브리프를 만들 수 없어 — 생성 서버가 잠깐 붐비는 중이야. 잠시 후 다시 시도해줘."
              : "브리프 생성에 실패했어 — 잠시 후 다시 시도해줘.");
            return;
          }
          // 요청 비행 중 워치 목록이 바뀌었으면 낡은 목록 기준 브리프를 저장하지 않는다.
          // 패시브는 현재 목록으로 재평가를 예약하고, 강제 발행은 조용히 폐기(사용자가 다시 명령하면 됨).
          // 전체 범위(커스텀·scopeAll)는 스킵 — 풀이 워치와 무관이라 워치 변경이 결과를 낡게 하지 않는다.
          if (!scopeAll) try {
            const nowTerms = JSON.parse(localStorage.getItem("sbtl_watch_terms") || "[]");
            if (JSON.stringify(nowTerms) !== termsSigAtRequest) {
              if (!force) { weeklyAttemptRef.current = false; bumpWatchSeen(); }
              return;
            }
          } catch { /* 비교 불가 환경은 그대로 저장 */ }
          const entry = {
            id: `wb_${Date.now()}`,
            generated_at: kstToday(),
            scope_label: scopeLabel,
            period, // "weekly" | "monthly" — 쿨다운·표시가 기간별로 분리된다 (구 항목은 없음=주간 취급)
            // 달력월호("2026-05") — 롤링 월간 쿨다운·열람에서 별개 취급. source_month_count는
            // '이 서사가 본 그 달 재료 수'(R15d) — 카드 날짜가 사건일 기준이라 지난달 소급
            // 편입이 정상이므로, 앱이 현재 수와 비교해 낡음을 배지로 고백하는 데 쓴다.
            // 반드시 '자기 범위'의 풀로 센다(워치 범위 월호는 워치 매칭 수, 캡 없이) —
            // 전 월 카드로 세면 무관 카드 변동에 오발동하고 워치 소재 변동은 놓친다(Codex #184).
            ...(month ? { month, source_month_count: (terms.length
              ? kb.cards.filter((c) => cardMatchesWatch(c, terms) && cardInMonth(c, month))
              : kb.cards.filter((c) => cardInMonth(c, month))).length } : {}),
            ...(group ? { group } : {}), // "region"|"theme"|"custom" — 같은 기간이라도 구성이 다르면 다른 산출물
            // 커스텀 조합의 재현·비교용 — spec_sig가 '같은 조합' 판정의 정본(쿨다운·빌더 게이트).
            // 다른 조합의 커스텀호끼리는 서로 쿨다운을 물리지 않는다.
            ...(customSpec ? { axes_spec: customSpec, spec_sig: JSON.stringify(customSpec) } : {}),
            terms: terms.slice(0, 8),
            // 발행 시점 워치 전체 시그니처 — brief_now 쿨다운을 '같은 범위'에만 적용하기 위한 비교용.
            // (표시용 terms는 8개로 잘리지만 시그니처는 전체를 보존해 범위 변경을 정확히 감지)
            terms_sig: JSON.stringify(terms),
            narrative: j.narrative,
            watch: Array.isArray(j.watch) ? j.watch : [],
            // id는 각주 ☆ 저장(핀 보드 승격)의 열쇠 — getCardId 정본 체인이라 핀 보드가 같은 카드로 역매칭된다(R17b)
            refs: briefCards.map((c, i) => ({ n: i + 1, id: getCardId(c), title: c.title || c.T || "", date: c.date || c.d || "", url: c.url || c.primaryUrl || "" })), // 서버 전역 [n]과 동일 순서 (축 모드는 축 연결 순)
            read: false,
          };
          const fresh = readWeeklyBriefs(); // 저장 직전 재확인 (다른 탭 경합)
          if (!force && !weeklyBriefDue(plainWeeklyEntries(fresh).filter((e) => briefScopeMatches(e, terms)))) {
            setWeeklyBriefs(fresh); // 경합에서 진 탭도 승자 항목을 화면에 반영
            if (fresh.length) setWeeklyError(null); // 승자 브리프가 화면에 뜨면 낡은 실패 메시지 소거
            return;
          }
          const next = [entry, ...fresh].slice(0, WEEKLY_BRIEF_CAP);
          localStorage.setItem(WEEKLY_BRIEF_KEY, JSON.stringify(next));
          setWeeklyBriefs(next);
          // 브리프가 성공적으로 저장·표시됐으니 낡은 실패 메시지를 소거한다 — 새 브리프와 ⚠️가
          // 함께 뜨지 않게(force는 시작 시 이미 소거하지만, 패시브 성공은 여기서만 소거된다).
          setWeeklyError(null);
          // 강제 발행은 사용자가 지금 기다리는 중 — 완성본을 📮 선반(브리핑룸)에 바로 펼친다.
          // id로 '방금 만든 그 호수'를 고정한다: 락이 기간·달별로 분리돼 여러 발행이
          // 동시에 돌 수 있으므로, 기간만으로 고르면 뒤늦게 끝난 다른 호수가 앞에 꽂히며
          // 사용자가 방금 만든 호수에서 밀려난다(선반은 최신호 표시).
          if (force) setBriefSeed((s) => ({ open: true, period, month, group, specSig: customSpec ? JSON.stringify(customSpec) : null, id: entry.id, nonce: s.nonce + 1 }));
        } catch {
          // 네트워크 예외 등 — 강제 발행이면 사용자에게 알린다(패시브는 조용히 재시도)
          if (force) setWeeklyError("브리프 생성 중 네트워크 오류가 났어 — 잠시 후 다시 시도해줘.");
        }
        finally {
          setWeeklyGenerating(false);
          // 내 토큰일 때만 해제 — 소유권을 잃었으면 남(승자)의 잠금을 지우지 않는다
          try {
            if (localStorage.getItem(lockKey) === lockToken) localStorage.removeItem(lockKey);
          } catch { /* noop */ }
        }
      })();
    } catch { /* noop */ }
  }, [kb.cards, bumpWatchSeen]);
  const executeAppCommand = useMemo(() => (cmd) => {
    if (!cmd || !cmd.type) return;
    try {
      if ((cmd.type === "watch_add" || cmd.type === "watch_remove") && cmd.term) {
        const raw = JSON.parse(localStorage.getItem("sbtl_watch_terms") || "[]");
        const terms = Array.isArray(raw) ? raw : [];
        const exists = terms.some((x) => String(x).toLowerCase() === String(cmd.term).toLowerCase());
        const next = cmd.type === "watch_add"
          ? (exists ? terms : [...terms, cmd.term])
          : terms.filter((x) => String(x).toLowerCase() !== String(cmd.term).toLowerCase());
        const changed = next.length !== terms.length;
        localStorage.setItem("sbtl_watch_terms", JSON.stringify(next));
        // seen 스냅샷 동기화 — NewsDesk의 용어 변경 처리와 동일 규칙. NewsDesk는 챗 탭에서
        // 언마운트 상태라 여기서 직접 수행하지 않으면 배지가 새 용어의 과거 이력 전체를
        // 미확인으로 세거나(추가) 제거된 용어의 잔여 id를 창에 남긴다(삭제).
        const seenRaw = localStorage.getItem("sbtl_watch_seen");
        if (changed && seenRaw !== null) {
          if (!next.length) {
            // 마지막 용어 제거: NewsDesk의 빈 워치 정리와 동일 — 재등록은 first-run 기준선부터
            localStorage.removeItem("sbtl_watch_seen");
            localStorage.removeItem("sbtl_watch_seen_sig");
          } else if (kb.cards.length) {
            const seen = new Set(JSON.parse(seenRaw || "[]"));
            if (cmd.type === "watch_add") {
              // 새 용어의 기존 이력만 확인 처리로 편입 — 기존 용어와 겹치는 미확인 카드는 보존
              kb.cards.filter((c) => cardMatchesWatch(c, [cmd.term]) && !cardMatchesWatch(c, terms)).slice(0, WATCH_SEEN_WINDOW).forEach((c) => { const id = getCardId(c); if (id) seen.add(id); });
            }
            const keep = new Set(kb.cards.filter((c) => cardMatchesWatch(c, next)).slice(0, WATCH_SEEN_WINDOW).map((c) => getCardId(c)).filter(Boolean));
            localStorage.setItem("sbtl_watch_seen", JSON.stringify([...seen].filter((id) => keep.has(id))));
            localStorage.setItem("sbtl_watch_seen_sig", JSON.stringify(next));
          }
        } else if (changed && seenRaw === null && cmd.type === "watch_add" && kb.cards.length) {
          // 첫 워치 추가(스냅샷 없음): NewsDesk firstRun과 동일하게 현재 매칭 전부를 기준선으로.
          // 여기서 만들지 않으면 다음 카드 갱신 때 fallback 효과가 갱신분까지 '이미 봄'으로
          // 저장해 새 카드가 배지에 영영 안 잡힌다. cards 미로드면 기존 fallback 효과에 위임.
          const ids = kb.cards.filter((c) => cardMatchesWatch(c, next)).slice(0, WATCH_SEEN_WINDOW).map((c) => getCardId(c)).filter(Boolean);
          localStorage.setItem("sbtl_watch_seen", JSON.stringify(ids));
          localStorage.setItem("sbtl_watch_seen_sig", JSON.stringify(next));
        }
        setWatchSeenVersion((v) => v + 1); // 배지·주간 브리프 재평가 트리거
      } else if (cmd.type === "profile_open" && cmd.term) {
        setNewsSeed((s) => ({ profileTerm: cmd.term, feedFilter: null, nonce: s.nonce + 1 }));
        setTab("news");
      } else if (cmd.type === "weekly_show") {
        // 기간·달·구성을 명시한 열람("월간/5월/5월 지역별 브리프 보여줘")은 그 변형 호수를 연다 — 없으면 최신호 폴백.
        // R12: 브리프의 집은 브리핑룸 — 선반 seed를 올리고 브리핑룸으로 이동한다.
        setBriefSeed((s) => ({ open: true, period: cmd.period || null, month: cmd.month || null, group: cmd.group || null, specSig: null, id: null, nonce: s.nonce + 1 }));
        setTab("watchroom");
      } else if (cmd.type === "brief_now") {
        // 강제 발행: 선반을 먼저 열어 '만드는 중'을 보여주고, 완성되면 runWeeklyBrief가
        // seed를 한 번 더 올려 방금 만든 호수(id)를 자동 표시한다. (brief_empty_watch·
        // brief_no_material은 서버 응답만 있고 클라 동작 없음 — watch_absent와 같은 무동작 안전 분기)
        // 생성 전 선반 열기도 같은 기간·달을 박아둔다 — 요청한 호수의 기존 발행본을 보여주다가
        // 완성되면 위 완료 seed가 새 호수로 다시 고정한다(요청 내내 맥락 유지)
        // 커스텀은 specSig까지 — spec_sig가 '같은 조합' 판정의 정본인데 seed만 group으로
        // 뭉뚱그리면 다른 조합의 옛 커스텀호를 열고 읽음 처리한다(산출물 면 전파 규약).
        const preSig = (() => { const n = normalizeCustomSpec(cmd.customSpec); return n ? JSON.stringify(n) : null; })();
        setBriefSeed((s) => ({ open: true, period: cmd.period || null, month: cmd.month || null, group: cmd.group || null, specSig: preSig, id: null, nonce: s.nonce + 1 }));
        setTab("watchroom");
        // customSpec(R14 빌더)·scopeAll(R15d 재발행)은 그대로 관통 — runWeeklyBrief가 범위·spec 저장까지 담당
        runWeeklyBrief({ force: true, period: cmd.period, month: cmd.month, group: cmd.group, customSpec: cmd.customSpec, scopeAll: cmd.scopeAll });
      } else if (cmd.type === "feed_filter") {
        // 피드 필터 명령("중국 카드만 보여줘") — 지역/기간/시그널/내워치/검색어를 seed로
        setNewsSeed((s) => ({ profileTerm: null, weeklyOpen: false, feedFilter: { region: cmd.region || null, range: cmd.range ?? null, signal: cmd.signal || null, watch: !!cmd.watch, search: cmd.search || null }, nonce: s.nonce + 1 }));
        setTab("news");
      }
    } catch { /* noop */ }
  }, [kb.cards, runWeeklyBrief]);
  // 살아있는 다른 탭의 발행/read 갱신을 실시간 반영 — storage 이벤트는 브라우저가
  // 같은 오리진의 '다른' 탭에만 발화시키므로 자기 쓰기와는 충돌하지 않는다.
  useEffect(() => {
    const onStorage = (e) => {
      if (e.key !== null && e.key !== WEEKLY_BRIEF_KEY) return;
      const next = readWeeklyBriefs();
      setWeeklyBriefs((prev) => (JSON.stringify(prev) === JSON.stringify(next) ? prev : next));
    };
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);
  // onlyId를 주면 그 호수만 읽음 처리한다 — 기간 고정 열람("월간 브리프 보여줘")은 최신호가
  // 아닌 호수를 일부러 여는데, 전체를 읽음 처리하면 위에 있는 안 본 주간호의 NEW가 조용히
  // 사라진다. 인자 없이 부르면 기존대로 전체 처리(선반 토글은 최신호를 보여주므로 그대로).
  const markWeeklyBriefsRead = useMemo(() => (onlyId) => {
    try {
      const next = readWeeklyBriefs().map((e) => (!e.read && (!onlyId || e.id === onlyId) ? { ...e, read: true } : e));
      localStorage.setItem(WEEKLY_BRIEF_KEY, JSON.stringify(next));
      setWeeklyBriefs(next);
    } catch { /* noop */ }
  }, []);
  // 호수 삭제(R15b) — 선반 리셋의 정직한 경로(예전엔 devtools localStorage 조작뿐이었다).
  // 부수효과는 의도된 것: 삭제된 호수는 쿨다운·due 조회에서 자연히 빠지므로 같은 산출물을
  // 즉시 다시 만들 수 있고(삭제했으면 재발행 가능해야 정직), plain 주간을 지우면 다음
  // 접속 패시브가 다시 채운다. 라이브러리 채택본도 지워도 되는 이유 — 월 칩이 라이브러리
  // 폴백(⚡)으로 언제든 다시 채택한다.
  const deleteWeeklyBrief = useMemo(() => (id) => {
    try {
      const next = readWeeklyBriefs().filter((e) => e && e.id !== id);
      localStorage.setItem(WEEKLY_BRIEF_KEY, JSON.stringify(next));
      setWeeklyBriefs(next);
    } catch { /* noop */ }
  }, []);
  // 사전 생성 라이브러리 호수를 보관함에 채택(R13) — 월 칩이 라이브러리에서 열 때 1회 주입.
  // 이미 있으면(id 동일) 중복 주입하지 않고 최신 목록만 반영한다.
  const adoptLibraryEntry = useMemo(() => (entry) => {
    try {
      if (!entry || !entry.id || !entry.narrative) return;
      const fresh = readWeeklyBriefs();
      if (fresh.some((e) => e && e.id === entry.id)) { setWeeklyBriefs(fresh); return; }
      const next = [entry, ...fresh].slice(0, WEEKLY_BRIEF_CAP);
      localStorage.setItem(WEEKLY_BRIEF_KEY, JSON.stringify(next));
      setWeeklyBriefs(next);
    } catch { /* noop */ }
  }, []);
  useEffect(() => {
    // 세션 1회 시도 가드는 '같은 범위'에만 건다 — 범위가 바뀌면(첫 워치 등록 등) 다시 시도한다.
    // R9의 전체 범위 폴백 전에는 빈 워치가 생성 전 early-return이라 시도 플래그가 안 켜져서
    // "첫 워치 등록 시 즉시 발행"(R5 설계)이 동작했는데, 이제 전체호를 실제로 발행하며 플래그가
    // 켜지므로 명시적으로 리셋해줘야 그 동작이 유지된다(리로드 없이 개인화 브리프).
    let scopeSig = "[]";
    try { const v = JSON.parse(localStorage.getItem("sbtl_watch_terms") || "[]"); scopeSig = JSON.stringify(Array.isArray(v) ? v : []); } catch { /* noop */ }
    if (weeklyAttemptScopeRef.current !== scopeSig) {
      weeklyAttemptScopeRef.current = scopeSig;
      weeklyAttemptRef.current = false;
    }
    if (weeklyAttemptRef.current || !kb.cards.length) return;
    runWeeklyBrief({ force: false });
    // watchSeenVersion: 워치 용어 변경마다 명령 버스·워치룸이 onWatchSeen으로 올려주는 신호 —
    // 앱 로딩 후 처음 워치를 등록한 사용자도 리로드 없이 주간 브리프가 생성되도록 재평가 트리거로 쓴다.
  }, [kb.cards, watchSeenVersion, runWeeklyBrief]); // eslint-disable-line react-hooks/exhaustive-deps
  const { tracker, regionPolicy, loading: trackerLoading } = useTrackerData(refreshKey, hardRefresh);
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
      try { await clearBrowserCaches(); } catch (error) { console.error("Cache clear error:", error); }
    }
    setHardRefresh(nextHard);
    setRefreshPending(true);
    setRefreshKey(Date.now());
  };

  const handleSubmitConsultation = (card) => {
    if (!card) return;
    const recentOpenerIds = getRecentOpenerIds(5);
    const cardContext = buildCardConsultContext({ card, allCards: kb.cards, recentOpenerIds });
    if (!cardContext) return;
    const created = createConsultation({ card, openerCategory: cardContext.opener_category, openerIdUsed: null });
    if (!created) return;
    setConsultationSeed({ data: { consultationId: created.id, cardContext, card_meta: created.card_meta, opened_at: created.opened_at }, nonce: Date.now() });
    setConsultSummaries(getAllCardConsultationSummaries());
    setTab("chatbot");
  };

  if (kb.loading || trackerLoading) return <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "100vh", background: t.bg, color: t.sub }}>Loading...</div>;

  const headerTitle = { news: "날짜별 시그널 피드", chatbot: "강차장의 배터리 상담소", watchroom: "브리핑룸", archive: "자료실" }[tab];
  const headerSub = { news: `Cards ${kb.cardCount} · updated ${fmtDate(lastCardDate)} · live feed`, chatbot: "배터리·ESS 이슈를 빠르게 찾고 정리해주는 AI 데스크", watchroom: "브리프 · 내 워치 · 저장 카드가 모이는 곳", archive: `정책 ${tracker.meta.totalItems}건 · 용어 ${kb.faqCount}항목 · ${WEBTOON_COLLECTIONS.length}시리즈` }[tab] || `Cards ${kb.cardCount} · ESS · EV · Policy`;

  return (
    <div style={{ maxWidth: 480, margin: "0 auto", background: t.bg, minHeight: "100vh", fontFamily: "'Pretendard',-apple-system,sans-serif", position: "relative" }}>
      <style dangerouslySetInnerHTML={{ __html: `@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&display=swap');body{margin:0;background:${t.bg}}*{box-sizing:border-box}button:focus-visible,a:focus-visible,input:focus-visible{outline:2px solid #58A6FF;outline-offset:2px}.skip-link{position:absolute;left:-9999px;z-index:999;padding:12px 20px;background:#58A6FF;color:#000;text-decoration:none;font-weight:800;border-radius:8px;font-size:14px}.skip-link:focus{left:50%;transform:translateX(-50%);top:10px}button{transition:transform .06s ease,background-color .15s ease,border-color .15s ease,color .15s ease,opacity .15s ease}button:active:not(:disabled){transform:scale(.97)}@media (prefers-reduced-motion: reduce){button{transition:none}button:active:not(:disabled){transform:none}}` }} />
      <a href="#main-content" className="skip-link">메인 콘텐츠로 이동</a>
      <div style={{ background: "#161B26", padding: "14px 16px 16px", position: "relative", borderBottom: "1px solid #21293A" }}>
        <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: "linear-gradient(90deg,#58A6FF,#BC8CFF,#58A6FF)" }} />
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}><img src="/data/logo_light.png" alt="SBTL" style={{ height: 32, objectFit: "contain" }} onError={(e) => { e.currentTarget.style.display = "none"; }} /><div style={{ display: "flex", alignItems: "center", gap: 4, background: "#0B2A0B", borderRadius: 4, padding: "2px 7px" }}><div style={{ width: 5, height: 5, borderRadius: 3, background: "#3FB950" }} /><span style={{ fontSize: 9, color: "#3FB950", fontFamily: "'JetBrains Mono',monospace", fontWeight: 700 }}>LIVE</span></div></div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}><span style={{ fontSize: 10, color: "#7D8590", fontFamily: "'JetBrains Mono',monospace" }}>{kb.cardCount}</span><button onClick={() => void triggerRefresh("soft")} disabled={kb.loading || trackerLoading || refreshPending} title="최신 데이터 다시 불러오기" aria-label="Refresh latest data" style={{ background: "#21293A", border: "none", borderRadius: 8, minWidth: 44, minHeight: 44, display: "flex", alignItems: "center", justifyContent: "center", cursor: kb.loading || trackerLoading || refreshPending ? "not-allowed" : "pointer", fontSize: 14, color: "#E6EDF3", opacity: kb.loading || trackerLoading || refreshPending ? 0.45 : 1 }}>↻</button><button onClick={() => void triggerRefresh("hard")} disabled={kb.loading || trackerLoading || refreshPending} title="캐시까지 무시하고 강하게 다시 불러오기" aria-label="Hard refresh latest data" style={{ background: "#21293A", border: "1px solid rgba(248,81,73,0.35)", borderRadius: 8, minWidth: 44, minHeight: 44, display: "flex", alignItems: "center", justifyContent: "center", cursor: kb.loading || trackerLoading || refreshPending ? "not-allowed" : "pointer", fontSize: 14, color: "#F85149", opacity: kb.loading || trackerLoading || refreshPending ? 0.45 : 1 }}>⚡</button><button onClick={() => setDark(!dark)} aria-label={dark ? "Switch to light mode" : "Switch to dark mode"} style={{ background: "#21293A", border: "none", borderRadius: 8, minWidth: 44, minHeight: 44, display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", fontSize: 16 }}>{dark ? "☀️" : "🌙"}</button></div>
        </div>
        <div style={{ marginTop: 10 }}>{tab !== "all" && <h1 style={{ color: "#E6EDF3", fontSize: 18, fontWeight: 800, margin: 0 }}>{headerTitle}</h1>}<p style={{ color: "#7D8590", fontSize: 10, margin: "2px 0 0", fontFamily: "'JetBrains Mono',monospace" }}>{headerSub}</p>{refreshLabel && <p style={{ color: refreshLabel.includes("강력") ? "#F85149" : "#58A6FF", fontSize: 10, margin: "6px 0 0", fontFamily: "'JetBrains Mono',monospace" }}>{refreshLabel}</p>}</div>
      </div>
      <main id="main-content" role="main" aria-label="SBTL 콘텐츠 허브">
        {tab === "all" && <div style={{ paddingTop: 10 }}><TodayDashboard dark={dark} kb={kb} tracker={tracker} weeklyBriefs={weeklyBriefs} watchVersion={watchSeenVersion} onNav={setTab} onOpenProfile={(term) => { setNewsSeed((s) => ({ profileTerm: term, weeklyOpen: false, nonce: s.nonce + 1 })); setTab("news"); }} onFeedSearch={(q) => executeAppCommand({ type: "feed_filter", search: q })} onAppCommand={executeAppCommand} /></div>}
        {tab === "watchroom" && <div style={{ padding: "10px 16px 0" }}><Watchroom dark={dark} kb={kb} weeklyBriefs={weeklyBriefs} watchVersion={watchSeenVersion} onNav={setTab} onOpenProfile={(term) => { setNewsSeed((s) => ({ profileTerm: term, feedFilter: null, nonce: s.nonce + 1 })); setTab("news"); }} onWatchAdd={(term) => executeAppCommand({ type: "watch_add", term })} onWatchRemove={(term) => executeAppCommand({ type: "watch_remove", term })} onBriefNow={(period, extra) => executeAppCommand({ type: "brief_now", period, ...(extra || {}) })} onWatchSeen={bumpWatchSeen} onWatchFeed={() => executeAppCommand({ type: "feed_filter", watch: true })} weeklyGenerating={weeklyGenerating} weeklyError={weeklyError} onWeeklyBriefsRead={markWeeklyBriefsRead} briefSeed={briefSeed} onBriefSeedConsumed={markBriefSeedConsumed} onAdoptLibraryEntry={adoptLibraryEntry} onDeleteBrief={deleteWeeklyBrief} /></div>}
        {tab === "archive" && <div style={{ paddingTop: 10 }}><div style={{ padding: "0 16px", fontSize: 10, fontWeight: 800, letterSpacing: 1.1, color: "#7D8590", fontFamily: "'JetBrains Mono',monospace", margin: "4px 0 8px" }}>POLICY TRACKER — 정책 일정·규제</div><Tracker tracker={tracker} regionPolicy={regionPolicy} dark={dark} /><div style={{ padding: "0 16px", fontSize: 10, fontWeight: 800, letterSpacing: 1.1, color: "#7D8590", fontFamily: "'JetBrains Mono',monospace", margin: "18px 0 8px" }}>배터리교실 · 용어</div><WebtoonLibrary dark={dark} faq={kb.faq} faqError={kb.faqError} /></div>}
        {tab === "news" && <NewsDesk kb={kb} onSubmitConsultation={handleSubmitConsultation} consultSummaries={consultSummaries} dark={dark} onWatchSeen={bumpWatchSeen} agentSeed={newsSeed} onAgentSeedConsumed={markNewsSeedConsumed} />}
        {tab === "chatbot" && <ChatBot dark={dark} initialConsultation={consultationSeed.data} initialConsultationNonce={consultationSeed.nonce} onAppCommand={executeAppCommand} onConsultationConsumed={markConsultationConsumed} />}
      </main>
      <div style={{ position: "fixed", bottom: 0, left: "50%", transform: "translateX(-50%)", width: "100%", maxWidth: 480, background: dark ? t.card : "#fff", borderTop: `1px solid ${t.brd}`, display: "flex", paddingBottom: "env(safe-area-inset-bottom, 8px)" }} role="navigation" aria-label="Main navigation">
        {CATS.map((cat) => {
          const active = tab === cat.key;
          const badge = cat.key === "watchroom" && watchNewCount > 0; // 내워치 배지는 워치룸 탭에
          return <button key={cat.key} onClick={() => setTab(cat.key)} aria-label={badge ? `${cat.label}, 내워치 새 카드 ${watchNewCount}건` : `Maps to ${cat.label}`} aria-current={active ? "page" : undefined} style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 2, padding: "8px 0", minHeight: 56, cursor: "pointer", border: "none", background: "transparent", flex: 1, position: "relative" }}>{active && <div style={{ position: "absolute", top: 0, left: "50%", transform: "translateX(-50%)", width: 20, height: 2, borderRadius: 1, background: t.cyan }} />}<span style={{ fontSize: 22, lineHeight: 1, filter: active ? "none" : "grayscale(0.3) opacity(0.7)" }} aria-hidden="true">{cat.icon}</span><span style={{ fontSize: 9, fontWeight: active ? 700 : 500, color: active ? t.cyan : t.sub, fontFamily: "'JetBrains Mono',monospace" }}>{cat.label}</span>{badge && <span aria-hidden="true" style={{ position: "absolute", top: 5, left: "50%", transform: "translateX(7px)", background: "#F85149", color: "#fff", borderRadius: 999, fontSize: 8, fontWeight: 800, padding: "2px 5px", lineHeight: 1, fontFamily: "'JetBrains Mono',monospace" }}>{watchNewCount > 99 ? "99+" : watchNewCount}</span>}</button>;
        })}
      </div>
    </div>
  );
}

export default function App() {
  return (
    <ErrorBoundary dark>
      <AppContent />
    </ErrorBoundary>
  );
}
