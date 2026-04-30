import { useEffect, useMemo, useRef, useState } from 'react';
import { normalizeCard } from './normalizeCard';

// ============================================================================
// 배터리 상담소 재설계 Phase 1 (2026-04-19)
// ----------------------------------------------------------------------------
// 변경점:
//   - 버튼 wording: "이 카드로 계속 물어보기" → "📋 상담카드 제출"
//   - 버튼 상시 노출: 브리프(핵심만/콕짚기) 펴지 않아도 footer에 항상 있음
//   - callback: onAskChatbot(promptString) → onSubmitConsultation(rawCard)
// ----------------------------------------------------------------------------
// 2026-04-20: 상담 횟수 hint 제거 (per-browser localStorage 카운터라
// 다수 사용자 환경에선 의미 없고 혼란 유발. consultationHint prop은
// 호환성 위해 시그니처에 유지하되 렌더링 안 함.)
// 2026-04-30: 뉴스 이미지 UX 보정
//   - featured 카드는 magazine lead 유지
//   - 일반 뉴스 카드는 compact magazine 구조: 상단 와이드 이미지 + 하단 본문
//   - CSS background-image 대신 <img> + onError fallback chain 사용
//   - 이미지 실패/차단/지연 시 검정 패널 대신 branded gradient fallback 노출
// ============================================================================

const SIG_COLORS = { top: '#F85149', high: '#D29922', mid: '#388BFD', info: '#7D8590', t: '#F85149', h: '#D29922', m: '#388BFD', i: '#7D8590' };
const SIG_LABELS = { top: 'TOP', high: 'HIGH', mid: 'MID', info: 'INFO', t: 'TOP', h: 'HIGH', m: 'MID', i: 'INFO' };
const REG_FLAG = { US: '🇺🇸', KR: '🇰🇷', EU: '🇪🇺', CN: '🇨🇳', JP: '🇯🇵', GL: '🌐', NA: '🇺🇸', 'US/KR': '🇺🇸' };
const THINK_MS = 700;

const IMAGE_POOLS = {
  POLICY: [
    'https://images.unsplash.com/photo-1589829085413-56de8ae18c73?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1521791136064-7986c2920216?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1450101499163-c8848c66ca85?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1447069387593-a5de0862481e?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1521790797524-b2497295b8a0?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1575517111478-7f6afd0973db?auto=format&fit=crop&w=600&q=80',
  ],
  FINANCE: [
    'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1633156189777-41d13d474421?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1535320971260-19f223a3176d?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1526303328184-c7e6c0c53462?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1454165205744-3b78555e5572?auto=format&fit=crop&w=600&q=80',
  ],
  FACTORY: [
    'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1565814329452-e1efa11c5b89?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1616423640778-28d1b53229bd?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1537462715879-360eeb61a0ad?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1504917595217-d4dc5ebe6122?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1542744095-2ad4870bf002?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1553152531-b98a2fc8d3bf?auto=format&fit=crop&w=600&q=80',
  ],
  AUTO: [
    'https://images.unsplash.com/photo-1560958089-b8a1929cea89?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1593941707882-a5bba14938c7?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1617704548623-340376564e68?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1580273916550-e323be2ae537?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1591836335805-4c0177757913?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?auto=format&fit=crop&w=600&q=80',
  ],
  BATTERY: [
    'https://images.unsplash.com/photo-1581092335397-9583eb92d232?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1620800615556-91eecfc5108f?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1558444479-c86e4efe22ef?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1594818379496-da1e345b0dc3?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1548333341-97d216272bb0?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=600&q=80',
  ],
  TECH: [
    'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1510511459019-5deeec7138db?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d?auto=format&fit=crop&w=600&q=80',
  ],
  MINING: [
    'https://images.unsplash.com/photo-1578319439584-104c94d37305?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1519452635265-7b1fbfd1e4e0?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1534067783941-51c9c23ecefd?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1502120963564-941551aa2900?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1523992527425-4198441fd3a4?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1581092160562-40aa08e78837?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1513828583688-c52646db42da?auto=format&fit=crop&w=600&q=80',
  ],
  RECYCLE: [
    'https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1604187351574-c7550fd415ca?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1533038590840-1cde6b66b721?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1516992654410-9309d4587e94?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1595273670150-bd0c3c392e46?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1517404212738-1976fe78ce50?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1591193022657-3932782fe24b?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1542601906970-30f95e5944b1?auto=format&fit=crop&w=600&q=80',
  ],
  GRID: [
    'https://images.unsplash.com/photo-1466611653911-95281773ad90?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1509391366360-fe19a7865821?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1548613053-2200ec27732a?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1516937941344-00b4e0337589?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1497435334941-8c899ee9e8e9?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1413882353051-789643878b4b?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1558444479-c86e4efe22ef?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?auto=format&fit=crop&w=600&q=80',
  ],
  DEFAULT: [
    'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1557683316-973673baf926?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1579546929518-9e396f3cc809?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1550684848-fac1c5b4e853?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1533035353720-f1c6a75cd8ab?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1510511459019-5deeec7138db?auto=format&fit=crop&w=600&q=80',
    'https://images.unsplash.com/photo-1444703686981-a3abbc4d4fe3?auto=format&fit=crop&w=600&q=80',
  ],
};

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
        shadow: '0 4px 20px rgba(0,0,0,0.3)',
      }
    : {
        card: '#FFFFFF',
        card2: '#FFFFFF',
        tx: '#1A1A2A',
        sub: '#57606A',
        brd: '#E0E3EA',
        cyan: '#0969DA',
        soft: 'rgba(9,105,218,0.03)',
        shadow: '0 4px 16px rgba(0,0,0,0.08)',
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

function hashSeed(value) {
  const seed = String(value || 'story-news-card');
  let hash = 0;
  for (let i = 0; i < seed.length; i += 1) {
    hash = (hash << 5) - hash + seed.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
}

function imageCategoryFor(card) {
  const text = [card?.id, card?.title, card?.T, card?.sub, card?.subtitle, card?.gate, card?.g, card?.source, card?.src, card?.region, card?.r]
    .filter(Boolean)
    .join(' ')
    .toLowerCase();

  if (/(재활용|리사이클|폐배터리|회수|재사용|재제조|순환|recycl|second life|reuse|black mass|블랙매스)/.test(text)) return 'RECYCLE';
  if (/(광산|광물|리튬|니켈|코발트|흑연|망간|채굴|제련|원자재|자원|희토류|rare earth|mineral|mining|graphite|lithium|nickel|cobalt)/.test(text)) return 'MINING';
  if (/(계통|전력망|재생에너지|태양광|풍력|변전소|ess|bess|grid|신재생|전력|유틸리티|송전|배전|storage|renewable|solar|wind)/.test(text)) return 'GRID';
  if (/(ira|feoc|crma|cbam|보조금|관세|규제|정부|정책|법안|재무부|백악관|세액공제|공시|입법|의회|산업부|환경부|mou|협력|tariff|subsidy|regulation|policy)/.test(text)) return 'POLICY';
  if (/(실적|이익|영업이익|매출|주가|투자|m&a|상장|자금|조달|금융|적자|흑자|ipo|margin|ebitda|funding|capex|재무|감가|손상|회계|계약|공급계약)/.test(text)) return 'FINANCE';
  if (/(공장|양산|생산|가동|캐파|capa|증설|설비|수율|라인|plant|factory|manufacturing|gigafactory|준공|착공|라인)/.test(text)) return 'FACTORY';
  if (/(테슬라|전기차|ev|완성차|현대차|기아|bmw|자동차|주행|포드|gm|폭스바겐|toyota|honda|충전|charging|dc 충전|46시리즈)/.test(text)) return 'AUTO';
  if (/(배터리|lfp|전고체|양극재|음극재|분리막|전해액|셀|니켈|코발트|흑연|catl|byd|엔솔|sdi|sk온|파우치|모듈)/.test(text)) return 'BATTERY';
  if (/(기술|r&d|특허|연구|개발|혁신|차세대|파일럿|테스트|ai|software|data|semiconductor|반도체)/.test(text)) return 'TECH';
  return 'DEFAULT';
}

function makeBriefLines(card, mode) {
  const summary = uniqueLines(card.fact, card.sub, card.gate, card.title);
  const insight = uniqueLines(card.implicationText, card.gate, card.fact);
  if (mode === 'summary') {
    return summary.slice(0, 2).map((line, idx) => (idx === 0 ? line : `중요한 건 ${line}`));
  }
  return insight.slice(0, 2).map((line, idx) => (idx === 0 ? `강차장 시선으로 보면 ${line}` : line));
}

function MetaPill({ children, dark, maxWidth }) {
  const t = theme(dark);
  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      fontSize: 10,
      color: t.sub,
      fontWeight: 700,
      background: dark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.04)',
      padding: '4px 8px',
      borderRadius: 6,
      maxWidth,
      whiteSpace: maxWidth ? 'nowrap' : 'normal',
      overflow: maxWidth ? 'hidden' : 'visible',
      textOverflow: maxWidth ? 'ellipsis' : 'clip',
    }}>
      {children}
    </span>
  );
}

function SigPill({ sig, label }) {
  return (
    <span style={{
      fontSize: 10,
      fontWeight: 900,
      color: '#fff',
      background: sig,
      padding: '4px 8px',
      borderRadius: 6,
      letterSpacing: '0.5px',
    }}>
      {label}
    </span>
  );
}

function OverlayPill({ children, maxWidth }) {
  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      fontSize: 10,
      fontWeight: 700,
      color: 'rgba(255,255,255,0.95)',
      background: 'rgba(0,0,0,0.48)',
      backdropFilter: 'blur(8px)',
      padding: '4px 8px',
      borderRadius: 6,
      maxWidth,
      whiteSpace: maxWidth ? 'nowrap' : 'normal',
      overflow: maxWidth ? 'hidden' : 'visible',
      textOverflow: maxWidth ? 'ellipsis' : 'clip',
    }}>
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
  // eslint-disable-next-line no-unused-vars
  consultationHint = null,
}) {
  const t = theme(dark);
  const c = useMemo(() => normalizeCard(card), [card]);
  const [activeMode, setActiveMode] = useState(null);
  const [thinkingMode, setThinkingMode] = useState(null);
  const timerRef = useRef(null);

  const signalKey = String(c.signal || 'info').toLowerCase();
  const sig = SIG_COLORS[signalKey] || SIG_COLORS.info;
  const sigLabel = SIG_LABELS[signalKey] || 'INFO';
  const regionFlag = REG_FLAG[c.region] || '🌐';
  const sourceText = c.source || card?.src || card?.source || '';
  const sourceUrl = c.primaryUrl || card?.primaryUrl || card?.primary_url || card?.url || (Array.isArray(card?.urls) ? card.urls[0] : '') || '';
  const layout = featured ? 'lead' : 'plain';
  const lines = activeMode ? makeBriefLines(c, activeMode) : [];

  const imageCategory = useMemo(() => imageCategoryFor({ ...card, ...c }), [card, c]);

  const imagePool = useMemo(() => {
    const pool = IMAGE_POOLS[imageCategory] || IMAGE_POOLS.DEFAULT;
    const candidates = featured && coverImage ? [coverImage, ...pool] : pool;
    return Array.from(new Set(candidates.filter(Boolean)));
  }, [imageCategory, featured, coverImage]);

  const imageStartIndex = useMemo(() => {
    const seed = [card?.id, c.date, c.title, c.source, imageCategory]
      .filter(Boolean)
      .join('|');
    return imagePool.length ? hashSeed(seed) % imagePool.length : 0;
  }, [card?.id, c.date, c.title, c.source, imageCategory, imagePool]);

  const [imageOffset, setImageOffset] = useState(0);
  const [imageLoaded, setImageLoaded] = useState(false);

  useEffect(() => {
    setImageOffset(0);
    setImageLoaded(false);
  }, [imageStartIndex, imageCategory]);

  const hasImageCandidate = imagePool.length > 0 && imageOffset < imagePool.length;
  const imageSrc = hasImageCandidate
    ? imagePool[(imageStartIndex + imageOffset) % imagePool.length]
    : null;

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
  const briefMode = thinkingMode || activeMode;
  const briefAccent = briefMode === 'summary' ? t.cyan : '#A855F7';

  const renderVisualImage = (height) => (
    <div
      style={{
        position: 'relative',
        height,
        overflow: 'hidden',
        background: `radial-gradient(circle at 15% 20%, ${sig}44, transparent 34%), linear-gradient(135deg, #172033, #1C2333 55%, #24314A)`,
      }}
    >
      {imageSrc ? (
        <img
          key={imageSrc}
          src={imageSrc}
          alt=""
          loading="lazy"
          decoding="async"
          onLoad={() => setImageLoaded(true)}
          onError={() => {
            setImageLoaded(false);
            setImageOffset((prev) => Math.min(prev + 1, imagePool.length));
          }}
          style={{
            position: 'absolute',
            inset: 0,
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            objectPosition: 'center',
            opacity: imageLoaded ? 1 : 0,
            transition: 'opacity 180ms ease',
          }}
        />
      ) : (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'rgba(255,255,255,0.72)',
            fontSize: 11,
            fontWeight: 900,
            letterSpacing: '0.08em',
            fontFamily: "'JetBrains Mono',monospace",
          }}
        >
          {imageCategory} SIGNAL
        </div>
      )}
    </div>
  );

  return (
    <div style={{ background: t.card2, borderRadius: 16, border: `1px solid ${t.brd}`, overflow: 'hidden', boxShadow: t.shadow, marginBottom: 12 }}>
      <div style={{ height: 4, background: sig }} />

      {layout === 'lead' ? (
        <div style={{ position: 'relative' }}>
          {renderVisualImage(240)}
          <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(180deg, rgba(0,0,0,0.08) 0%, rgba(0,0,0,0.38) 42%, rgba(13,17,23,0.95) 100%)' }} />
          <div style={{ position: 'absolute', top: 12, left: 14, right: 14, display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 10 }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              <SigPill sig={sig} label={sigLabel} />
              <OverlayPill>{regionFlag} {c.region}</OverlayPill>
              <OverlayPill>{fmtDate(c.date)}</OverlayPill>
            </div>
            {sourceText ? <OverlayPill maxWidth={100}>{sourceText}</OverlayPill> : null}
          </div>
          <div style={{ position: 'absolute', bottom: 16, left: 16, right: 16 }}>
            <h3 style={{ margin: 0, color: '#fff', fontSize: 20, lineHeight: 1.35, fontWeight: 900, textShadow: '0 2px 4px rgba(0,0,0,0.6)' }}>
              {c.title || card?.T || '제목 없음'}
            </h3>
            {c.sub ? (
              <p style={{ margin: '8px 0 0', color: 'rgba(255,255,255,0.86)', fontSize: 13, lineHeight: 1.5, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                {c.sub}
              </p>
            ) : null}
          </div>
        </div>
      ) : (
        <>
          <div style={{ position: 'relative' }}>
            {renderVisualImage(136)}
            <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(180deg, rgba(0,0,0,0.10) 0%, rgba(0,0,0,0.18) 48%, rgba(13,17,23,0.62) 100%)' }} />
            <div style={{ position: 'absolute', top: 10, left: 12, right: 12, display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 8 }}>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                <SigPill sig={sig} label={sigLabel} />
                <OverlayPill>{regionFlag} {c.region}</OverlayPill>
              </div>
              {sourceText ? <OverlayPill maxWidth={100}>{sourceText}</OverlayPill> : null}
            </div>
            <div style={{ position: 'absolute', bottom: 10, left: 12 }}>
              <OverlayPill>{fmtDate(c.date)}</OverlayPill>
            </div>
          </div>
          <div style={{ padding: 16 }}>
            <h3 style={{ margin: 0, color: t.tx, fontSize: 16, lineHeight: 1.4, fontWeight: 800, display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
              {c.title || card?.T || '제목 없음'}
            </h3>
            {c.sub ? (
              <p style={{ margin: '6px 0 0', color: t.sub, fontSize: 12, lineHeight: 1.5, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                {c.sub}
              </p>
            ) : null}
          </div>
        </>
      )}

      <div style={{ padding: footerPadding, display: 'flex', flexDirection: 'column', gap: 12 }}>
        {layout !== 'lead' && <div style={{ height: 1, background: t.brd, margin: '0 -16px' }} />}

        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ display: 'flex', gap: 6, flex: '1 1 100%' }}>
            <button
              type="button"
              onClick={() => openBrief('summary')}
              aria-pressed={activeMode === 'summary'}
              style={{ flex: 1, borderRadius: 8, border: activeMode === 'summary' ? `1px solid ${t.cyan}` : `1px solid ${t.brd}`, background: activeMode === 'summary' ? (dark ? 'rgba(88,166,255,0.15)' : 'rgba(9,105,218,0.1)') : 'transparent', color: activeMode === 'summary' ? t.cyan : t.sub, padding: '8px 10px', minHeight: '36px', fontSize: 12, fontWeight: 800, cursor: 'pointer', transition: 'all 0.2s', whiteSpace: 'nowrap' }}
            >
              이슈 브리핑
            </button>
            <button
              type="button"
              onClick={() => openBrief('insight')}
              aria-pressed={activeMode === 'insight'}
              style={{ flex: 1, borderRadius: 8, border: activeMode === 'insight' ? '1px solid #A855F7' : `1px solid ${t.brd}`, background: activeMode === 'insight' ? 'rgba(168,85,247,0.15)' : 'transparent', color: activeMode === 'insight' ? '#A855F7' : t.sub, padding: '8px 10px', minHeight: '36px', fontSize: 12, fontWeight: 800, cursor: 'pointer', transition: 'all 0.2s', whiteSpace: 'nowrap' }}
            >
              강차장 인사이트
            </button>
          </div>

          <div style={{ display: 'flex', gap: 6, flex: '1 1 100%', justifyContent: 'flex-end' }}>
            {sourceUrl && (
              <button
                type="button"
                onClick={() => window.open(sourceUrl, '_blank', 'noopener,noreferrer')}
                style={{ flex: 1, borderRadius: 8, border: `1px solid ${t.brd}`, background: t.card, color: t.tx, padding: '8px 14px', minHeight: '36px', fontSize: 12, fontWeight: 800, cursor: 'pointer', whiteSpace: 'nowrap', textAlign: 'center' }}
              >
                원문 ↗
              </button>
            )}
            <button
              type="button"
              onClick={handleSubmit}
              aria-label="이 카드를 배터리 상담소에 제출"
              style={{
                flex: sourceUrl ? 1 : 'none',
                width: sourceUrl ? 'auto' : '100%',
                borderRadius: 8,
                border: 'none',
                background: t.cyan,
                color: '#000',
                padding: '8px 16px',
                minHeight: '36px',
                fontSize: 12,
                fontWeight: 900,
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                boxShadow: `0 2px 8px ${dark ? 'rgba(88,166,255,0.3)' : 'rgba(9,105,218,0.3)'}`,
              }}
            >
              📋 상담카드 제출
            </button>
          </div>
        </div>

        {(thinkingMode || activeMode) && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 4, padding: 14, background: dark ? 'rgba(0,0,0,0.2)' : 'rgba(0,0,0,0.03)', borderRadius: 12, border: `1px solid ${t.brd}` }}>
            {thinkingMode ? (
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                <div style={{ flexShrink: 0, width: 32, height: 32, borderRadius: '50%', background: briefAccent, color: '#000', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13, fontWeight: 900 }}>강</div>
                <div style={{ flex: 1, background: t.card, borderRadius: '0 12px 12px 12px', border: `1px solid ${t.brd}`, padding: '12px 16px', color: t.sub, fontSize: 13, lineHeight: 1.6 }}>
                  정리 중...
                </div>
              </div>
            ) : lines.map((line, idx) => (
              <div key={`${activeMode}-${idx}`} style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                <div style={{ flexShrink: 0, width: 32, height: 32, borderRadius: '50%', background: briefAccent, color: '#000', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13, fontWeight: 900, boxShadow: `0 2px 6px ${briefMode === 'summary' ? 'rgba(88,166,255,0.4)' : 'rgba(168,85,247,0.4)'}` }}>강</div>
                <div style={{ flex: 1, background: t.card, borderRadius: '0 12px 12px 12px', border: `1px solid ${t.brd}`, padding: '12px 16px', color: t.tx, fontSize: 13, lineHeight: 1.65, wordBreak: 'keep-all', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                  {line}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
