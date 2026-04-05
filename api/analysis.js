export default async function handler(req, res) {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { card, mode } = req.body;

    if (!card || !mode) {
      return res.status(400).json({ error: 'Card and mode required' });
    }

    // Generate different analysis based on mode
    let result = '';

    if (mode === 'why') {
      // 왜 중요한지: Relevance gate / implication block
      // Focus on strategic significance and implications for battery/ESS/EV/supply chain
      result = generateWhyImportant(card);
    } else if (mode === 'summary') {
      // 한국어 요약: Article-oriented Korean rendering
      // Focus on factual content summary
      result = generateKoreanSummary(card);
    } else if (mode === 'analysis') {
      // AI 해설: Deeper analysis block
      // Focus on context, background, meaning, and watchpoints
      result = generateDeepAnalysis(card);
    } else {
      return res.status(400).json({ error: 'Invalid mode. Use: why, summary, or analysis' });
    }

    return res.status(200).json({ result, mode });
  } catch (error) {
    return res.status(500).json({
      error: 'ANALYSIS_ERROR',
      message: error.message,
      details: 'Failed to generate analysis'
    });
  }
}

function generateWhyImportant(card) {
  // Strategic relevance and implication layer
  // Extract or synthesize implication-focused content

  const { T, sub, g, r, s, src } = card;

  // Build implication-focused analysis
  let analysis = '';

  // If gist has "—" separator, use the back part (implication)
  if (g && g.includes('—')) {
    const parts = g.split('—');
    analysis = parts.slice(1).join('—').trim();
  } else if (g) {
    // Use strategic keywords to extract implication-focused content
    const lines = g.split(/[.。]\s*/);
    const implLines = lines.filter(line =>
      /(중요|의미|영향|관점|watchpoint|watch|주목|핵심|리스크|기회|전략)/i.test(line)
    );

    if (implLines.length > 0) {
      analysis = implLines.join('. ').trim();
    } else {
      // Fallback: use latter portion
      analysis = g.slice(Math.floor(g.length * 0.5)).trim();
    }
  }

  // Add context based on region and signal
  const regionContext = {
    'US': '미국 시장과 K-배터리 전략에',
    'EU': 'EU 규제 대응과 시장 접근에',
    'CN': '중국 공급망과 가격 경쟁에',
    'KR': '국내 ESS 시장과 정책에',
    'JP': '일본 에너지 전환 정책에'
  };

  const context = regionContext[r] || '배터리/ESS/EV 산업에';

  if (s === 't' || s === 'h') {
    analysis = `⚡ 이 시그널은 ${context} 중요한 변화를 의미합니다.\n\n${analysis}`;
  }

  return analysis || sub || T;
}

function generateKoreanSummary(card) {
  // Article-oriented Korean rendering
  // Focus on factual content: what happened, when, where, who

  const { T, sub, g, src, d, r } = card;

  let summary = '';

  // Start with title as headline
  if (T) {
    summary += `**${T}**\n\n`;
  }

  // Add subtitle as lead
  if (sub) {
    summary += `${sub}\n\n`;
  }

  // Extract factual content from gist (before "—" if exists)
  if (g) {
    if (g.includes('—')) {
      const factual = g.split('—')[0].trim();
      summary += `📰 ${factual}`;
    } else {
      // Use front 60% as factual summary
      const factualPart = g.slice(0, Math.floor(g.length * 0.6)).trim();
      summary += `📰 ${factualPart}`;
    }
  }

  // Add source attribution
  if (src) {
    summary += `\n\n출처: ${src}`;
  }

  return summary;
}

function generateDeepAnalysis(card) {
  // Deeper on-demand analysis block
  // Combine context, background, meaning, and watchpoints

  const { T, sub, g, r, s, src, d } = card;

  let analysis = '';

  // Full gist as foundation
  if (g) {
    analysis = g;
  }

  // Add analytical framework based on signal level
  const signalContext = {
    't': '\n\n🎯 TOP 시그널 분석:\n이 뉴스는 업계 전체의 방향을 바꿀 수 있는 구조적 변화입니다.',
    'h': '\n\n🔍 HIGH 시그널 분석:\n단기적 대응이 필요한 중요 변수입니다.',
    'm': '\n\n📌 MID 시그널 분석:\n중기적 관점에서 주목할 필요가 있습니다.',
    'i': '\n\n💡 INFO 레벨:\n참고용 정보로, 맥락 이해에 도움이 됩니다.'
  };

  if (signalContext[s]) {
    analysis += signalContext[s];
  }

  // Add regional perspective
  const regionPerspective = {
    'US': '\n\n🇺🇸 미국 시장 관점:\nFEOC 규정과 IRA 크레딧 측면에서 공급망 전략을 재검토할 필요가 있습니다.',
    'EU': '\n\n🇪🇺 EU 규제 관점:\nBattery Regulation과 CBAM 준수 비용을 고려한 대응이 필요합니다.',
    'CN': '\n\n🇨🇳 중국 동향 관점:\n가격 경쟁과 공급망 통제력 변화를 면밀히 추적해야 합니다.',
    'KR': '\n\n🇰🇷 국내 정책 관점:\nESS 안전기준과 용량시장 입찰 전략에 반영이 필요합니다.',
    'JP': '\n\n🇯🇵 일본 시장 관점:\nGX 정책 방향과 보조금 활용 가능성을 검토할 필요가 있습니다.'
  };

  if (regionPerspective[r]) {
    analysis += regionPerspective[r];
  }

  return analysis || g || sub || T;
}
