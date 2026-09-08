import { useEffect, useMemo, useRef, useState } from "react";
import { isOfficialMonthlyBrief, validateMonthlyBriefLibrary } from "../lib/brief/monthlyPublication.js";
import { selectMonthlyBrief } from "./monthlyBriefSelection.js";

function theme(dark) {
  return dark
    ? { card: "#161B26", card2: "#1C2333", tx: "#E6EDF3", sub: "#9198A1", brd: "#21293A", cyan: "#58A6FF", green: "#3FB950", amber: "#D29922" }
    : { card: "#FFFFFF", card2: "#F8F9FC", tx: "#1A1A2A", sub: "#57606A", brd: "#E0E3EA", cyan: "#0969DA", green: "#1A7F37", amber: "#9A6700" };
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

function monthCount(cards, month) {
  if (!/^\d{4}-\d{2}$/.test(String(month || ""))) return null;
  return (cards || []).filter((c) => String(c?.date || c?.d || "").slice(0, 7) === month).length;
}

function refLinks(ids, refById, t) {
  const refs = (ids || []).map((id) => refById.get(id)).filter(Boolean);
  if (!refs.length) return null;
  return (
    <div style={{ display: "flex", gap: 5, flexWrap: "wrap", marginTop: 7 }}>
      {refs.map((r) => r.url
        ? <a key={r.id} href={r.url} target="_blank" rel="noreferrer" style={{ fontSize: 9.5, color: t.cyan, textDecoration: "none", border: `1px solid ${t.brd}`, borderRadius: 999, padding: "3px 7px", fontFamily: "'JetBrains Mono',monospace" }}>[{r.n}]</a>
        : <span key={r.id} style={{ fontSize: 9.5, color: t.sub, border: `1px solid ${t.brd}`, borderRadius: 999, padding: "3px 7px", fontFamily: "'JetBrains Mono',monospace" }}>[{r.n}]</span>)}
    </div>
  );
}

export default function MonthlyBriefPanel({ dark = true, cards = [], seed = null }) {
  const t = theme(dark);
  const rootRef = useRef(null);
  const [library, setLibrary] = useState(null);
  const [loadError, setLoadError] = useState(false);
  const [selectedId, setSelectedId] = useState(null);
  const [requested, setRequested] = useState(null);

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

  useEffect(() => {
    if (!seed || seed.view !== "monthly" || !seed.nonce) return;
    setRequested(seed.month ? { month: seed.month } : null);
    const timer = setTimeout(() => { try { rootRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }); } catch { /* noop */ } }, 60);
    return () => clearTimeout(timer);
  }, [seed?.nonce]);

  const items = useMemo(() => (library?.items || []).filter(isOfficialMonthlyBrief).slice().sort(issueRank), [library]);

  useEffect(() => {
    if (!items.length) { setSelectedId(null); return; }
    if (requested?.month) {
      const { issue } = selectMonthlyBrief(items, requested, selectedId);
      setSelectedId(issue?.id || null);
      return;
    }
    setSelectedId((cur) => items.some((it) => it.id === cur) ? cur : items[0].id);
  }, [items, requested]);

  const { issue: shown, requestMissing } = selectMonthlyBrief(items, requested, selectedId);
  const requestedLabel = requested?.month ? `${monthLabel(requested.month)} 월간 브리프` : "요청한 공식 월간 브리프";
  const refById = useMemo(() => new Map((shown?.refs || []).map((r) => [r.id, r])), [shown]);
  const nowMonthCount = shown ? monthCount(cards, shown.month) : null;
  const baselineCount = Number.isInteger(shown?.source_baseline?.source_month_count) ? shown.source_baseline.source_month_count : null;
  const drift = nowMonthCount != null && baselineCount != null ? nowMonthCount - baselineCount : 0;
  const shortSha = (v) => String(v || "").slice(0, 8);

  return (
    <section id="monthly-brief-panel" ref={rootRef} aria-label="SBTL 월간 브리프" style={{ scrollMarginTop: 12, marginTop: 16 }}>
      <div style={{ marginBottom: 8 }}>
        <div style={{ fontSize: 10, fontWeight: 900, letterSpacing: 1.1, color: t.cyan, fontFamily: "'JetBrains Mono',monospace" }}>🧭 OFFICIAL · SBTL MONTHLY BRIEF</div>
        <div style={{ fontSize: 10.5, color: t.sub, marginTop: 3, lineHeight: 1.55, wordBreak: "keep-all" }}>월간 전체를 Deep Dive하고 편집·Red Team·근거·용어 QC를 통과한 승인본만 표시합니다. 자동 빠른 분석과는 별도 정본입니다.</div>
      </div>

      {!library && !loadError && <div style={{ borderRadius: 12, padding: "13px 14px", background: t.card2, border: `1px solid ${t.brd}`, fontSize: 11, color: t.sub }}>공식 월간 브리프 확인 중…</div>}
      {loadError && <div style={{ borderRadius: 12, padding: "13px 14px", background: t.card2, border: `1px dashed ${t.brd}`, fontSize: 11, color: t.sub, lineHeight: 1.6 }}>SBTL Monthly Brief 정본을 불러오지 못했습니다. 자동 분석으로 대체하지 않습니다.</div>}
      {library && !loadError && requestMissing && (
        <div style={{ borderRadius: 12, padding: "14px", background: t.card2, border: `1px solid ${t.brd}` }}>
          <div style={{ fontSize: 13, fontWeight: 900, color: t.tx }}>편집 중 · {requestedLabel} 공식 발행본 없음</div>
          <div style={{ marginTop: 5, fontSize: 11, color: t.sub, lineHeight: 1.65, wordBreak: "keep-all" }}>요청한 월의 승인본이 없어서 다른 달이나 자동 분석으로 대체하지 않습니다. 승인 후 이 자리에 표시됩니다.</div>
        </div>
      )}
      {library && !loadError && !requested && items.length === 0 && (
        <div style={{ borderRadius: 12, padding: "14px", background: t.card2, border: `1px solid ${t.brd}` }}>
          <div style={{ fontSize: 13, fontWeight: 900, color: t.tx }}>편집 중 · 아직 공식 월간 브리프 없음</div>
          <div style={{ marginTop: 5, fontSize: 11, color: t.sub, lineHeight: 1.65, wordBreak: "keep-all" }}>SBTL Monthly Brief가 승인되기 전에는 자동으로 만들지 않습니다. 아래 빠른 분석은 조사·탐색용으로만 사용할 수 있습니다.</div>
        </div>
      )}

      {shown && (
        <div style={{ borderRadius: 14, padding: "14px", background: t.card2, border: `1px solid ${t.cyan}` }}>
          <div style={{ display: "flex", alignItems: "flex-start", gap: 8 }}>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: "flex", gap: 6, flexWrap: "wrap", alignItems: "center" }}>
                <span style={{ fontSize: 10, fontWeight: 900, color: "#000", background: t.cyan, borderRadius: 5, padding: "3px 7px", fontFamily: "'JetBrains Mono',monospace" }}>{monthLabel(shown.month)}</span>
                {shown.revision > 1 && <span style={{ fontSize: 9.5, fontWeight: 800, color: t.amber, border: `1px solid ${t.amber}`, borderRadius: 999, padding: "2px 7px", fontFamily: "'JetBrains Mono',monospace" }}>R{shown.revision}</span>}
                <span style={{ fontSize: 9.5, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>{shown.published_at} 발행</span>
              </div>
              <div style={{ marginTop: 7, fontSize: 16, fontWeight: 900, color: t.tx, lineHeight: 1.35, wordBreak: "keep-all" }}>{shown.title}</div>
            </div>
            <span title="4개 QC PASS + 승인" style={{ flexShrink: 0, fontSize: 9, fontWeight: 900, color: t.green, border: `1px solid ${t.green}`, borderRadius: 999, padding: "4px 8px", fontFamily: "'JetBrains Mono',monospace" }}>APPROVED</span>
          </div>

          {drift !== 0 && (
            <div style={{ marginTop: 10, borderRadius: 9, padding: "9px 10px", border: `1px dashed ${t.amber}`, fontSize: 10.5, color: t.sub, lineHeight: 1.6, wordBreak: "keep-all" }}>
              <b style={{ color: t.amber }}>편집 검토 필요</b> · 기준 월 카드가 발행 시점 {baselineCount}장 → 현재 {nowMonthCount}장({drift > 0 ? `+${drift}` : drift})으로 변했습니다. 공식본은 자동 재생성하지 않으며, 중요하면 편집 검토 후 revision으로 발행합니다.
            </div>
          )}

          <div style={{ marginTop: 12, borderRadius: 10, background: t.card, border: `1px solid ${t.brd}`, padding: "11px 12px" }}>
            <div style={{ fontSize: 9.5, fontWeight: 900, color: t.sub, letterSpacing: 0.8, fontFamily: "'JetBrains Mono',monospace" }}>핵심 진단</div>
            <div style={{ marginTop: 6, fontSize: 13, fontWeight: 700, color: t.tx, lineHeight: 1.75, wordBreak: "keep-all" }}>{shown.executive_diagnosis}</div>
          </div>

          <div style={{ marginTop: 10 }}>
            <div style={{ fontSize: 9.5, fontWeight: 900, color: t.sub, letterSpacing: 0.8, fontFamily: "'JetBrains Mono',monospace" }}>이번 달의 핵심 흐름 · {shown.key_flows?.length || 0}</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 7, marginTop: 6 }}>
              {(shown.key_flows || []).map((flow) => (
                <div key={flow.id} style={{ borderRadius: 10, background: t.card, border: `1px solid ${t.brd}`, padding: "10px 11px" }}>
                  <div style={{ fontSize: 12, fontWeight: 900, color: t.tx }}><span style={{ color: t.cyan, fontFamily: "'JetBrains Mono',monospace" }}>{flow.id}</span> · {flow.title}</div>
                  <div style={{ marginTop: 4, fontSize: 11.5, color: t.tx, lineHeight: 1.65, wordBreak: "keep-all" }}>{flow.summary}</div>
                  {refLinks(flow.card_ids, refById, t)}
                </div>
              ))}
            </div>
          </div>

          <div style={{ marginTop: 10, borderTop: `1px solid ${t.brd}`, paddingTop: 10 }}>
            <div style={{ fontSize: 9.5, fontWeight: 900, color: t.sub, letterSpacing: 0.8, fontFamily: "'JetBrains Mono',monospace" }}>무엇이 달라졌나</div>
            <div style={{ marginTop: 5, fontSize: 12, fontWeight: 700, color: t.tx, lineHeight: 1.7, wordBreak: "keep-all" }}>{shown.what_changed}</div>
          </div>

          {Array.isArray(shown.watch) && shown.watch.length > 0 && (
            <div style={{ marginTop: 10, borderTop: `1px dashed ${t.brd}`, paddingTop: 9 }}>
              <div style={{ fontSize: 9.5, fontWeight: 900, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>👁 NEXT WATCH</div>
              {shown.watch.map((w, i) => <div key={i} style={{ marginTop: 4, fontSize: 11, color: t.tx, lineHeight: 1.6, wordBreak: "keep-all" }}>· {w}</div>)}
            </div>
          )}

          <details style={{ marginTop: 10 }}>
            <summary style={{ cursor: "pointer", fontSize: 10, fontWeight: 800, color: t.sub, fontFamily: "'JetBrains Mono',monospace" }}>근거·QC·baseline 보기</summary>
            <div style={{ marginTop: 7, fontSize: 9.5, color: t.sub, lineHeight: 1.7, fontFamily: "'JetBrains Mono',monospace" }}>
              <div>source cards {shown.source_card_ids?.length || 0} · refs {shown.refs?.length || 0}</div>
              <div>main {shortSha(shown.source_baseline?.main_commit_sha)} · full {shortSha(shown.source_baseline?.full_blob_sha)}</div>
              <div>QC evidence/red-team/coherence/language = PASS · approval {shown.approval?.approved_at}</div>
            </div>
          </details>

          {items.length > 1 && (
            <div style={{ marginTop: 10, display: "flex", gap: 6, flexWrap: "wrap" }}>
              {items.map((it) => <button key={it.id} onClick={() => { setRequested(null); setSelectedId(it.id); }} aria-pressed={shown.id === it.id} style={{ borderRadius: 999, padding: "5px 9px", border: `1px solid ${shown.id === it.id ? t.cyan : t.brd}`, background: shown.id === it.id ? t.cyan : "transparent", color: shown.id === it.id ? "#000" : t.sub, fontSize: 9.5, fontWeight: 800, cursor: "pointer", fontFamily: "'JetBrains Mono',monospace" }}>{monthLabel(it.month)}{it.revision > 1 ? ` R${it.revision}` : ""}</button>)}
            </div>
          )}
        </div>
      )}
    </section>
  );
}
