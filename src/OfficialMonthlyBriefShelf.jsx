import { useEffect, useMemo, useState } from "react";
import { isOfficialMonthlyBrief, validateMonthlyBriefLibrary } from "../lib/brief/monthlyPublication.js";

function theme(dark) {
  return dark
    ? { card: "#161B26", card2: "#1C2333", tx: "#E6EDF3", sub: "#9198A1", brd: "#21293A", cyan: "#58A6FF", green: "#3FB950" }
    : { card: "#FFFFFF", card2: "#F8F9FC", tx: "#1A1A2A", sub: "#57606A", brd: "#E0E3EA", cyan: "#0969DA", green: "#1A7F37" };
}

function issueRank(a, b) {
  return String(b?.month || "").localeCompare(String(a?.month || ""))
    || Number(b?.revision || 0) - Number(a?.revision || 0)
    || String(b?.published_at || "").localeCompare(String(a?.published_at || ""));
}

function monthLabel(month) {
  const m = String(month || "").match(/^(\d{4})-(\d{2})$/);
  return m ? `${m[1]}.${m[2]}` : String(month || "");
}

export function officialMonthlyBriefShelfItems(library) {
  const ranked = (library?.items || []).filter(isOfficialMonthlyBrief).slice().sort(issueRank);
  const seenMonths = new Set();
  const items = ranked.filter((issue) => {
    const month = String(issue?.month || "");
    if (!month || seenMonths.has(month)) return false;
    seenMonths.add(month);
    return true;
  });
  return { latest: items[0] || null, archive: items.slice(1) };
}

export default function OfficialMonthlyBriefShelf({ dark = true, onOpen }) {
  const t = theme(dark);
  const [library, setLibrary] = useState(null);
  const [loadError, setLoadError] = useState(false);

  useEffect(() => {
    let alive = true;
    fetch("/data/monthly_briefs.json", { cache: "no-store" })
      .then((r) => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then((j) => {
        const errors = validateMonthlyBriefLibrary(j);
        if (errors.length) throw new Error(`invalid official library: ${errors[0]}`);
        if (alive) { setLibrary(j); setLoadError(false); }
      })
      .catch(() => { if (alive) { setLibrary({ items: [] }); setLoadError(true); } });
    return () => { alive = false; };
  }, []);

  const { latest, archive } = useMemo(() => officialMonthlyBriefShelfItems(library), [library]);
  const open = (month) => { if (month && typeof onOpen === "function") onOpen(month); };

  return (
    <section aria-label="OFFICIAL SBTL Monthly Brief" style={{ margin: "0 16px 12px", borderRadius: 14, padding: "13px 14px", background: t.card2, border: `1px solid ${latest ? t.cyan : t.brd}` }}>
      <div style={{ display: "flex", alignItems: "center", gap: 7, flexWrap: "wrap" }}>
        <span style={{ fontSize: 10, fontWeight: 900, letterSpacing: 1, color: t.cyan, fontFamily: "'JetBrains Mono',monospace" }}>🧭 OFFICIAL</span>
        <span style={{ fontSize: 9, fontWeight: 900, color: t.green, border: `1px solid ${t.green}`, borderRadius: 999, padding: "2px 6px", fontFamily: "'JetBrains Mono',monospace" }}>MONTHLY BRIEF</span>
      </div>

      {!library && !loadError && <div style={{ marginTop: 8, fontSize: 11, color: t.sub }}>공식 월간 브리프 확인 중…</div>}
      {loadError && <div style={{ marginTop: 8, fontSize: 11, color: t.sub, lineHeight: 1.6 }}>공식 월간 브리프 정본을 불러오지 못했습니다. 자동 분석으로 대체하지 않습니다.</div>}

      {library && !loadError && latest && (
        <>
          <button type="button" onClick={() => open(latest.month)} style={{ marginTop: 9, width: "100%", textAlign: "left", border: 0, padding: 0, background: "transparent", cursor: "pointer", fontFamily: "inherit" }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 10, alignItems: "flex-start" }}>
              <div style={{ minWidth: 0 }}>
                <div style={{ fontSize: 17, lineHeight: 1.3, fontWeight: 900, color: t.tx }}>SBTL Monthly Brief · {monthLabel(latest.month)}</div>
                <div style={{ marginTop: 5, fontSize: 11.5, lineHeight: 1.55, color: t.sub, wordBreak: "keep-all" }}>{latest.executive_diagnosis}</div>
              </div>
              <span style={{ flexShrink: 0, fontSize: 10, fontWeight: 900, color: t.cyan, paddingTop: 2 }}>보기 →</span>
            </div>
          </button>

          <div style={{ marginTop: 10, paddingTop: 9, borderTop: `1px solid ${t.brd}` }}>
            <div style={{ fontSize: 9, fontWeight: 900, letterSpacing: 0.8, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>ARCHIVE · 이전 공식호</div>
            {archive.length > 0
              ? <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 7 }}>{archive.map((issue) => <button key={issue.id} type="button" onClick={() => open(issue.month)} style={{ border: `1px solid ${t.brd}`, borderRadius: 999, padding: "5px 9px", background: t.card, color: t.tx, fontSize: 10, fontWeight: 800, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>{monthLabel(issue.month)}</button>)}</div>
              : <div style={{ marginTop: 5, fontSize: 10.5, color: t.sub }}>이전 공식호는 승인·발행되는 순서대로 여기에 쌓입니다.</div>}
          </div>
        </>
      )}

      {library && !loadError && !latest && <div style={{ marginTop: 8, fontSize: 11, color: t.sub }}>아직 승인·발행된 공식 월간 브리프가 없습니다.</div>}
    </section>
  );
}
