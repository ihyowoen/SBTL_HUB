import { useMemo, useState } from 'react';
import { normalizeCard } from './normalizeCard';
import { buildCardConsultPrompt } from './buildCardConsultPrompt';

const SIG_COLORS = { top: '#F85149', high: '#D29922', mid: '#388BFD', info: '#7D8590', t: '#F85149', h: '#D29922', m: '#388BFD', i: '#7D8590' };
const SIG_LABELS = { top: 'TOP', high: 'HIGH', mid: 'MID', info: 'INFO', t: 'TOP', h: 'HIGH', m: 'MID', i: 'INFO' };
const REGION_FLAGS = { US: '🇺🇸', KR: '🇰🇷', EU: '🇪🇺', CN: '🇨🇳', JP: '🇯🇵', GL: '🌐', NA: '🇺🇸' };

function theme(dark = true) {
  return dark
    ? { card: '#161B26', card2: '#1C2333', tx: '#E6EDF3', sub: '#9198A1', brd: '#21293A', cyan: '#58A6FF', shadow: '0 6px 20px rgba(0,0,0,0.35)' }
    : { card: '#FFFFFF', card2: '#F8F9FC', tx: '#1A1A2A', sub: '#57606A', brd: '#E0E3EA', cyan: '#0969DA', shadow: '0 6px 20px rgba(0,0,0,0.08)' };
}

function fmtDate(date) {
  if (!date) return '-';
  const s = String(date).trim();
  const m = s.match(/^(\d{4})[.-](\d{2})[.-](\d{2})/);
  if (m) return `${m[1]}.${m[2]}.${m[3]}`;
  return s;
}

export default function StoryNewsItem({ card, dark, onAskChatbot }) {
  const t = theme(dark);
  const c = useMemo(() => normalizeCard(card), [card]);
  const [panel, setPanel] = useState(null);
  const sig = SIG_COLORS[c.signal] || SIG_COLORS.info;
  const sigLabel = SIG_LABELS[c.signal] || 'INFO';
  const regionFlag = REGION_FLAGS[c.region] || '🌐';
  const panelBody = panel === 'fact' ? c.fact : panel === 'gate' ? c.gate : panel === 'implication' ? c.implicationText : '';

  return (
    <div style={{ background: t.card2, borderRadius: 20, border: `1px solid ${t.brd}`, overflow: 'hidden', boxShadow: t.shadow }}>
      <div style={{ height: 4, background: sig }} />
      <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 12 }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 10 }}>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            <span style={{ fontSize: 10, fontWeight: 900, color: '#fff', background: sig, padding: '4px 8px', borderRadius: 999 }}>{sigLabel}</span>
            <span style={{ fontSize: 10, color: t.sub, border: `1px solid ${t.brd}`, padding: '4px 8px', borderRadius: 999 }}>{regionFlag} {c.region}</span>
            <span style={{ fontSize: 10, color: t.sub, border: `1px solid ${t.brd}`, padding: '4px 8px', borderRadius: 999 }}>{fmtDate(c.date)}</span>
          </div>
          {c.source ? <span style={{ fontSize: 10, color: t.sub }}>{c.source}</span> : null}
        </div>

        <div>
          <h3 style={{ margin: 0, color: t.tx, fontSize: 18, lineHeight: 1.35, fontWeight: 900 }}>{c.title || '제목 없음'}</h3>
          {c.sub ? <p style={{ margin: '8px 0 0', color: t.sub, fontSize: 12, lineHeight: 1.55 }}>{c.sub}</p> : null}
        </div>

        <div style={{ display: 'flex', gap: 8, overflowX: 'auto' }}>
          <button onClick={() => setPanel(panel === 'fact' ? null : 'fact')} style={{ borderRadius: 999, border: '1px solid #58A6FF55', background: panel === 'fact' ? '#58A6FF' : 'transparent', color: panel === 'fact' ? '#000' : '#58A6FF', padding: '8px 12px', minHeight: '40px', fontSize: 11, fontWeight: 800, cursor: 'pointer' }}>무슨 일이야?</button>
          <button onClick={() => setPanel(panel === 'gate' ? null : 'gate')} style={{ borderRadius: 999, border: '1px solid #D2992255', background: panel === 'gate' ? '#D29922' : 'transparent', color: panel === 'gate' ? '#000' : '#D29922', padding: '8px 12px', minHeight: '40px', fontSize: 11, fontWeight: 800, cursor: 'pointer' }}>그래서 어떻게 돼?</button>
          <button onClick={() => setPanel(panel === 'implication' ? null : 'implication')} style={{ borderRadius: 999, border: '1px solid #A855F755', background: panel === 'implication' ? '#A855F7' : 'transparent', color: panel === 'implication' ? '#000' : '#A855F7', padding: '8px 12px', minHeight: '40px', fontSize: 11, fontWeight: 800, cursor: 'pointer' }}>강차장 코멘트</button>
        </div>

        {panel ? <div style={{ background: t.card, borderRadius: 16, border: `1px solid ${t.brd}`, padding: 14, fontSize: 13, color: t.tx, lineHeight: 1.7, whiteSpace: 'pre-wrap', wordBreak: 'keep-all' }}>{panelBody || '아직 정리된 내용이 없습니다.'}</div> : null}

        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {c.primaryUrl ? <button onClick={() => window.open(c.primaryUrl, '_blank', 'noopener,noreferrer')} style={{ borderRadius: 12, border: `1px solid ${t.brd}`, background: 'transparent', color: t.tx, padding: '12px 14px', minHeight: '44px', fontSize: 12, fontWeight: 800, cursor: 'pointer' }}>원문 보기 ↗</button> : null}
          {onAskChatbot ? <button onClick={() => onAskChatbot(buildCardConsultPrompt(card))} style={{ borderRadius: 12, border: 'none', background: t.cyan, color: '#000', padding: '12px 14px', minHeight: '44px', fontSize: 12, fontWeight: 900, cursor: 'pointer', flex: 1 }}>강차장에게 상담하러 가기</button> : null}
        </div>
      </div>
    </div>
  );
}
