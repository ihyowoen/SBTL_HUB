import { useEffect, useMemo, useRef, useState } from 'react';
import { normalizeCard } from './normalizeCard';

// ============================================================================
// 배터리 상담소 재설계 Phase 1 (2026-04-19)
// ----------------------------------------------------------------------------
// 변경점:
//   - 버튼 wording: "이 카드로 계속 물어보기" → "📋 상담카드 제출"
//   - 버튼 상시 노출: 브리프(핵심만/콕짚기) 펴지 않아도 footer에 항상 있음
//   - callback: onAskChatbot(promptString) → onSubmitConsultation(rawCard)
//   - consultationHint prop 추가: { count, latestDate } → "↘ 3번 상담 · 최근 4/19" 표시
// ============================================================================

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

// B안 footer용 — ISO datetime을 "M/D" 포맷으로 축약
function shortMD(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  if (isNaN(d.getTime())) return '';
  return `${d.getMonth() + 1}/${d.getDate()}`;
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

function SigPill({ sig, label }) {
  return (
    <span style={{ fontSize: 10, fontWeight: 900, color: '#fff', background: sig, padding: '5px 9px', borderRadius: 999 }}>
      {label}
    </span>
  );
}

function OverlayPill({ children }) {
  return (
    <span style={{ fontSize: 10, color: '#fff', background: 'rgba(0,0,0,0.55)', backdropFilter: 'blur(4px)', padding: '5px 9px', borderRadius: 999 }}>
      {children}
    </span>
  );
}

export default function StoryNewsItem({
  card,
  dark,
  onSubmitConsultation,
  coverImage = '',
  featured = false,
  consultationHint = null,
}) {
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

  const layout = hasCover && featured ? 'lead' : 'plain';

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

  const handleSubmit = () => {
    if (typeof onSubmitConsultation === 'function') {
      onSubmitConsultation(card);
    }
  };

  const footerPadding = layout === 'lead' ? '12px 16px 16px' : '0 16px 16px';

  return (
    <div style={{ background: t.card2, borderRadius: 16, border: `1px solid ${t.brd}`, overflow: 'hidden', boxShadow: t.shadow }}>
      <div style={{ height: 4, background: sig }} />

      {layout === 'lead' ? (
        <>
          <div style={{ position: 'relative', height: 140, background: `url(${coverImage}) center/cover no-repeat` }}>
            <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.28) 100%)' }} />
            <div style={{ position: 'absolute', top: 12, left: 12, right: 12, display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 10 }}>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                <SigPill sig={sig} label={sigLabel} />
                <OverlayPill>{regionFlag} {c.region}</OverlayPill>
                <OverlayPill>{fmtDate(c.date)}</OverlayPill>
              </div>
              {c.source ? <OverlayPill>{c.source}</OverlayPill> : null}
            </div>
          </div>
          <div style={{ padding: '14px 16px 4px' }}>
            <h3 style={{ margin: 0, color: t.tx, fontSize: 18, lineHeight: 1.36, fontWeight: 900 }}>{c.title || '제목 없음'}</h3>
            {c.sub ? <p style={{ margin: '8px 0 0', color: t.sub, fontSize: 12, lineHeight: 1.6 }}>{c.sub}</p> : null}
          </div>
        </>
      ) : (
        <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12 }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              <SigPill sig={sig} label={sigLabel} />
              <MetaPill dark={dark}>{regionFlag} {c.region}</MetaPill>
              <MetaPill dark={dark}>{fmtDate(c.date)}</MetaPill>
            </div>
            {c.source ? <span style={{ fontSize: 10, color: t.sub, textAlign: 'right', lineHeight: 1.4 }}>{c.source}</span> : null}
          </div>
          <div>
            <h3 style={{ margin: 0, color: t.tx, fontSize: 18, lineHeight: 1.36, fontWeight: 900 }}>{c.title || '제목 없음'}</h3>
            {c.sub ? <p style={{ margin: '8px 0 0', color: t.sub, fontSize: 12, lineHeight: 1.6 }}>{c.sub}</p> : null}
          </div>
        </div>
      )}

      <div style={{ padding: footerPadding, display: 'flex', flexDirection: 'column', gap: 10 }}>
        {/* Action row — 항상 노출 (상시 3개 버튼 + 조건부 원문/상담카드) */}
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
          <button onClick={() => openBrief('summary')} style={{ borderRadius: 999, border: '1px solid #58A6FF55', background: activeMode === 'summary' ? '#58A6FF' : 'transparent', color: activeMode === 'summary' ? '#000' : '#58A6FF', padding: '8px 12px', minHeight: '36px', fontSize: 11, fontWeight: 800, cursor: 'pointer', whiteSpace: 'nowrap' }}>핵심만 보면</button>
          <button onClick={() => openBrief('insight')} style={{ borderRadius: 999, border: '1px solid #A855F755', background: activeMode === 'insight' ? '#A855F7' : 'transparent', color: activeMode === 'insight' ? '#000' : '#A855F7', padding: '8px 12px', minHeight: '36px', fontSize: 11, fontWeight: 800, cursor: 'pointer', whiteSpace: 'nowrap' }}>강차장 콕 짚기</button>
          {c.primaryUrl ? (
            <button
              onClick={() => window.open(c.primaryUrl, '_blank', 'noopener,noreferrer')}
              style={{ borderRadius: 999, border: `1px solid ${t.brd}`, background: 'transparent', color: t.sub, padding: '8px 12px', minHeight: '36px', fontSize: 11, fontWeight: 700, cursor: 'pointer', whiteSpace: 'nowrap' }}
            >원문 ↗</button>
          ) : null}
          {/* 상담카드 제출 — 상시 노출, 우측 정렬 */}
          <button
            onClick={handleSubmit}
            aria-label="이 카드를 배터리 상담소에 제출"
            style={{
              marginLeft: 'auto',
              borderRadius: 999,
              border: `1px solid ${t.cyan}`,
              background: t.cyan,
              color: '#000',
              padding: '8px 14px',
              minHeight: '36px',
              fontSize: 11,
              fontWeight: 900,
              cursor: 'pointer',
              whiteSpace: 'nowrap',
            }}
          >📋 상담카드 제출</button>
        </div>

        {/* Brief panel — 핵심만/콕짚기 펼쳤을 때만 */}
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
          </div>
        ) : null}

        {/* B안 footer — 상담 이력 있을 때만 */}
        {consultationHint && consultationHint.count > 0 && (
          <div
            style={{
              marginTop: 2,
              paddingTop: 8,
              borderTop: `1px dashed ${t.brd}`,
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              fontSize: 10,
              color: t.sub,
              fontFamily: "'JetBrains Mono', monospace",
              fontWeight: 700,
            }}
          >
            <span aria-hidden="true">↘</span>
            <span>
              {consultationHint.count}번 상담
              {consultationHint.latestDate ? ` · 최근 ${shortMD(consultationHint.latestDate)}` : ''}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
