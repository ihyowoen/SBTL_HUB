import { useEffect, useMemo, useRef, useState } from 'react';
import { normalizeCard } from './normalizeCard';
import { buildCardConsultPrompt } from './buildCardConsultPrompt';

const SIG_COLORS = { top: '#F85149', high: '#D29922', mid: '#388BFD', info: '#7D8590', t: '#F85149', h: '#D29922', m: '#388BFD', i: '#7D8590' };
const SIG_LABELS = { top: 'TOP', high: 'HIGH', mid: 'MID', info: 'INFO', t: 'TOP', h: 'HIGH', m: 'MID', i: 'INFO' };
const REGION_FLAGS = { US: '🇺🇸', KR: '🇰🇷', EU: '🇪🇺', CN: '🇨🇳', JP: '🇯🇵', GL: '🌐', NA: '🇺🇸' };
const THINK_MS = 700;

function theme(dark = true) {
  return dark
    ? {
        card: '#161B26',
        card2: '#1C2333',
        tx: '#E6EDF3',
        sub: '#9198A1',
        brd: '#21293A',
        cyan: '#58A6FF',
        soft: 'rgba(255,255,255,0.03)',
        shadow: '0 10px 28px rgba(0,0,0,0.28)',
      }
    : {
        card: '#FFFFFF',
        card2: '#F8F9FC',
        tx: '#1A1A2A',
        sub: '#57606A',
        brd: '#E0E3EA',
        cyan: '#0969DA',
        soft: 'rgba(9,105,218,0.03)',
        shadow: '0 8px 20px rgba(0,0,0,0.08)',
      };
}

function fmtDate(date) {
  if (!date) return '-';
  const s = String(date).trim();
  const m = s.match(/^(\d{4})[.-](\d{2})[.-](\d{2})/);
  if (m) return `${m[1]}.${m[2]}.${m[3]}`;
  return s;
}

function uniqueLines(...values) {
  const seen = new Set();
  const out = [];
  values
    .map((value) => String(value || '').trim())
    .filter(Boolean)
    .forEach((value) => {
      const key = value.replace(/\s+/g, ' ').toLowerCase();
      if (seen.has(key)) return;
      seen.add(key);
      out.push(value);
    });
  return out;
}

function makeBriefLines(card, mode) {
  const summary = uniqueLines(card.fact, card.sub, card.gate);
  const insight = uniqueLines(card.implicationText, card.gate, card.fact);
  if (mode === 'summary') {
    return summary.slice(0, 2).map((line, idx) => (idx === 0 ? line : `중요한 건 ${line}`));
  }
  return insight.slice(0, 2).map((line, idx) => (idx === 0 ? `강차장 시선으로 보면 ${line}` : line));
}

function MetaPill({ children, dark }) {
  const t = theme(dark);
  return (
    <span style={{ fontSize: 10, color: t.sub, border: `1px solid ${t.brd}`, background: dark ? 'rgba(255,255,255,0.02)' : '#fff', padding: '5px 9px', borderRadius: 999 }}>
      {children}
    </span>
  );
}

export default function StoryNewsItem({ card, dark, onAskChatbot, coverImage = '', featured = false }) {
  const t = theme(dark);
  const c = useMemo(() => normalizeCard(card), [card]);
  const [activeMode, setActiveMode] = useState(null);
  const [thinkingMode, setThinkingMode] = useState(null);
  const timerRef = useRef(null);
  const sig = SIG_COLORS[c.signal] || SIG_COLORS.info;
  const sigLabel = SIG_LABELS[c.signal] || 'INFO';
  const regionFlag = REGION_FLAGS[c.region] || '🌐';
  const hasCover = Boolean(coverImage);
  const lines = activeMode ? makeBriefLines(c, activeMode) : [];

  useEffect(() => () => {
    if (timerRef.current) window.clearTimeout(timerRef.current);
  }, []);

  const openBrief = (mode) => {
    if (activeMode === mode && !thinkingMode) {
      setActiveMode(null);
      return;
    }
    if (timerRef.current) window.clearTimeout(timerRef.current);
    setActiveMode(null);
    setThinkingMode(mode);
    timerRef.current = window.setTimeout(() => {
      setThinkingMode(null);
      setActiveMode(mode);
    }, THINK_MS);
  };

  return (
    <div style={{ background: t.card2, borderRadius: hasCover ? 24 : 22, border: `1px solid ${t.brd}`, overflow: 'hidden', boxShadow: t.shadow }}>
      <div style={{ height: 5, background: sig }} />

      {hasCover ? (
        <div style={{ position: 'relative', minHeight: featured ? 228 : 176, background: `url(${coverImage}) center/cover no-repeat` }}>
          <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(180deg, rgba(0,0,0,0.10) 0%, rgba(0,0,0,0.78) 100%)' }} />
          <div style={{ position: 'relative', zIndex: 1, minHeight: featured ? 228 : 176, padding: featured ? 18 : 16, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12 }}>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                <span style={{ fontSize: 10, fontWeight: 900, color: '#fff', background: sig, padding: '5px 9px', borderRadius: 999 }}>{sigLabel}</span>
                <span style={{ fontSize: 10, color: 'rgba(255,255,255,0.88)', border: '1px solid rgba(255,255,255,0.18)', background: 'rgba(0,0,0,0.16)', padding: '5px 9px', borderRadius: 999 }}>{regionFlag} {c.region}</span>
                <span style={{ fontSize: 10, color: 'rgba(255,255,255,0.88)', border: '1px solid rgba(255,255,255,0.18)', background: 'rgba(0,0,0,0.16)', padding: '5px 9px', borderRadius: 999 }}>{fmtDate(c.date)}</span>
              </div>
              {c.source ? <span style={{ fontSize: 10, color: 'rgba(255,255,255,0.72)', textAlign: 'right', lineHeight: 1.35 }}>{c.source}</span> : null}
            </div>

            <div>
              <h3 style={{ margin: 0, color: '#fff', fontSize: featured ? 23 : 19, lineHeight: 1.28, fontWeight: 900, textShadow: '0 2px 10px rgba(0,0,0,0.25)' }}>{c.title || '제목 없음'}</h3>
              {c.sub ? <p style={{ margin: '8px 0 0', color: 'rgba(255,255,255,0.80)', fontSize: 12, lineHeight: 1.58 }}>{c.sub}</p> : null}
            </div>
          </div>
        </div>
      ) : (
        <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12 }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              <span style={{ fontSize: 10, fontWeight: 900, color: '#fff', background: sig, padding: '5px 9px', borderRadius: 999 }}>{sigLabel}</span>
              <MetaPill dark={dark}>{regionFlag} {c.region}</MetaPill>
              <MetaPill dark={dark}>{fmtDate(c.date)}</MetaPill>
            </div>
            {c.source ? <span style={{ fontSize: 10, color: t.sub, textAlign: 'right', lineHeight: 1.4 }}>{c.source}</span> : null}
          </div>

          <div>
            <h3 style={{ margin: 0, color: t.tx, fontSize: 19, lineHeight: 1.34, fontWeight: 900 }}>{c.title || '제목 없음'}</h3>
            {c.sub ? <p style={{ margin: '8px 0 0', color: t.sub, fontSize: 12, lineHeight: 1.6 }}>{c.sub}</p> : null}
          </div>
        </div>
      )}

      <div style={{ padding: hasCover ? '14px 16px 16px' : '0 16px 16px', display: 'flex', flexDirection: 'column', gap: 12 }}>
        <div style={{ display: 'flex', gap: 8, overflowX: 'auto', paddingBottom: 2 }}>
          <button onClick={() => openBrief('summary')} style={{ borderRadius: 999, border: '1px solid #58A6FF55', background: activeMode === 'summary' ? '#58A6FF' : 'transparent', color: activeMode === 'summary' ? '#000' : '#58A6FF', padding: '9px 13px', minHeight: '40px', fontSize: 11, fontWeight: 800, cursor: 'pointer', whiteSpace: 'nowrap' }}>핵심만 보면</button>
          <button onClick={() => openBrief('insight')} style={{ borderRadius: 999, border: '1px solid #A855F755', background: activeMode === 'insight' ? '#A855F7' : 'transparent', color: activeMode === 'insight' ? '#000' : '#A855F7', padding: '9px 13px', minHeight: '40px', fontSize: 11, fontWeight: 800, cursor: 'pointer', whiteSpace: 'nowrap' }}>강차장 콕 짚기</button>
        </div>

        {(thinkingMode || activeMode) ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {thinkingMode ? (
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
                <div style={{ width: 28, height: 28, borderRadius: 14, background: dark ? '#111827' : '#EEF3FF', border: `1px solid ${t.brd}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 10, fontWeight: 900, color: t.cyan }}>강</div>
                <div style={{ maxWidth: '86%', background: t.card, borderRadius: '18px 18px 18px 6px', border: `1px solid ${t.brd}`, padding: '11px 14px', color: t.sub, fontSize: 13, lineHeight: 1.5 }}>...</div>
              </div>
            ) : lines.map((line, idx) => (
              <div key={`${activeMode}-${idx}`} style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
                <div style={{ width: 28, height: 28, borderRadius: 14, background: dark ? '#111827' : '#EEF3FF', border: `1px solid ${t.brd}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 10, fontWeight: 900, color: t.cyan }}>강</div>
                <div style={{ maxWidth: '86%', background: t.card, borderRadius: '18px 18px 18px 6px', border: `1px solid ${t.brd}`, padding: '11px 14px', color: t.tx, fontSize: 13, lineHeight: 1.68, wordBreak: 'keep-all' }}>{line}</div>
              </div>
            ))}

            {!thinkingMode && activeMode && onAskChatbot ? (
              <div style={{ paddingLeft: 36 }}>
                <button onClick={() => onAskChatbot(buildCardConsultPrompt(card))} style={{ borderRadius: 999, border: `1px solid ${t.brd}`, background: dark ? 'rgba(255,255,255,0.03)' : '#fff', color: t.tx, padding: '11px 14px', minHeight: '42px', fontSize: 11, fontWeight: 800, cursor: 'pointer' }}>이 카드로 계속 물어보기</button>
              </div>
            ) : null}
          </div>
        ) : null}

        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {c.primaryUrl ? <button onClick={() => window.open(c.primaryUrl, '_blank', 'noopener,noreferrer')} style={{ borderRadius: 12, border: `1px solid ${t.brd}`, background: 'transparent', color: t.tx, padding: '12px 14px', minHeight: '44px', fontSize: 12, fontWeight: 800, cursor: 'pointer' }}>원문 보기 ↗</button> : null}
        </div>
      </div>
    </div>
  );
}
