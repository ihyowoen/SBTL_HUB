const MODE_PROMPTS = {
  why: {
    system: `당신은 배터리·ESS·EV 산업 전문 애널리스트입니다.
주어진 뉴스 카드의 전략적 의미와 산업 파급 효과를 분석하세요.
- 배터리/ESS/EV 공급망·시장에 미치는 구조적 영향을 중심으로 서술
- 투자자·실무자가 주목해야 할 implication을 2~4줄로 압축
- 사실 나열보다 "왜 이게 중요한가"에 집중
- 한국어로 작성, 마크다운 없이 평문`,
    user: (card) => `뉴스 제목: ${card.T || ''}
부제: ${card.sub || ''}
내용: ${card.g || ''}
지역: ${card.r || ''} | 신호강도: ${card.s || ''}

이 뉴스가 배터리·ESS·EV 산업에 왜 중요한지 2~4줄로 설명해줘.`,
  },
  summary: {
    system: `당신은 해외 배터리·에너지 뉴스를 한국 독자에게 전달하는 전문 기자입니다.
주어진 뉴스 카드의 핵심 사실을 한국어로 요약하세요.
- 무슨 일이 일어났는지, 누가 관련됐는지, 언제·어디서인지 사실 중심
- 배경 해석이나 의견은 최소화, 팩트 전달에 집중
- 3~5줄 분량, 자연스러운 한국어 문체
- 한국어로 작성, 마크다운 없이 평문`,
    user: (card) => `뉴스 제목: ${card.T || ''}
부제: ${card.sub || ''}
내용: ${card.g || ''}
출처: ${card.src || ''} | 날짜: ${card.d || ''}

이 뉴스의 핵심 사실을 한국어로 3~5줄로 요약해줘.`,
  },
  analysis: {
    system: `당신은 배터리·ESS·EV 산업의 심층 분석을 수행하는 시니어 리서치 애널리스트입니다.
주어진 뉴스 카드를 바탕으로 심층 분석을 제공하세요.
- 배경과 맥락: 이 사건이 어떤 흐름의 일부인지
- 시장/산업 영향: 공급망, 가격, 경쟁 구도에 미치는 효과
- 주요 관전 포인트(watchpoints): 앞으로 무엇을 모니터링해야 하는지 2~3개
- SBTL 관점: 한국 배터리 기업·투자자 입장에서의 해석
- 5~8줄 분량, 구조적으로 서술
- 한국어로 작성, 마크다운 없이 평문`,
    user: (card) => `뉴스 제목: ${card.T || ''}
부제: ${card.sub || ''}
내용: ${card.g || ''}
지역: ${card.r || ''} | 신호강도: ${card.s || ''} | 출처: ${card.src || ''}

이 뉴스에 대한 심층 분석을 제공해줘. 배경, 시장 영향, 관전 포인트, SBTL 관점을 포함해서.`,
  },
};

async function callOpenAI(card, mode) {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) return null;

  const prompt = MODE_PROMPTS[mode];
  if (!prompt) return null;

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 12000);

  try {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages: [
          { role: 'system', content: prompt.system },
          { role: 'user', content: prompt.user(card) },
        ],
        max_tokens: 400,
        temperature: 0.7,
      }),
      signal: controller.signal,
    });

    if (!response.ok) return null;

    const data = await response.json();
    return data?.choices?.[0]?.message?.content?.trim() || null;
  } catch {
    return null;
  } finally {
    clearTimeout(timeout);
  }
}

export default async function handler(req, res) {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  // Cache: same card+mode combo is cacheable for 5 minutes
  res.setHeader('Cache-Control', 's-maxage=300, stale-while-revalidate=60');

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

    if (!['why', 'summary', 'analysis'].includes(mode)) {
      return res.status(400).json({ error: 'Invalid mode. Use: why, summary, or analysis' });
    }

    // Try OpenAI first; fall back to deterministic logic if unavailable
    const aiResult = await callOpenAI(card, mode);
    let result = aiResult;
    let source = 'ai';

    if (!result) {
      source = 'fallback';
      if (mode === 'why') {
        result = generateWhyImportant(card);
      } else if (mode === 'summary') {
        result = generateKoreanSummary(card);
      } else {
        result = generateDeepAnalysis(card);
      }
    }

    return res.status(200).json({ result, mode, source });
  } catch (error) {
    return res.status(500).json({
      error: 'ANALYSIS_ERROR',
      message: error.message,
      details: 'Failed to generate analysis'
    });
  }
}

// Fallback: clearly differentiated deterministic generators for each mode

function generateWhyImportant(card) {
  const { T, sub, g, r, s } = card;

  const regionContext = {
    US: 'FEOC·IRA 크레딧 구조와 공급망 전략에',
    EU: 'EU Battery Regulation·CBAM 규제 대응에',
    CN: '중국발 가격 경쟁과 공급망 통제력 변화에',
    KR: '국내 ESS 시장 성장과 정책 대응에',
    JP: '일본 GX 정책과 에너지 안보 전략에',
  };
  const context = regionContext[r] || '배터리·ESS·EV 밸류체인에';

  const signalNote = {
    t: '구조적 전환을 촉발할 수 있는 TOP 시그널입니다.',
    h: '단기 대응이 필요한 HIGH 임팩트 신호입니다.',
    m: '중기 관점에서 추적이 필요한 변수입니다.',
    i: '맥락 파악에 유용한 참고 정보입니다.',
  };

  // Extract implication-focused sentences from gist
  let implPart = '';
  if (g) {
    const sentences = g.split(/(?<=[.。])\s+/);
    const implSentences = sentences.filter((s) =>
      /(영향|의미|중요|전략|리스크|기회|경쟁|변화|핵심|주목|watch)/i.test(s)
    );
    implPart = implSentences.length ? implSentences.join(' ') : sentences[sentences.length - 1] || '';
  }

  const parts = [
    `⚡ 왜 중요한가`,
    `이 뉴스는 ${context} ${signalNote[s] || '중요한 변화를 나타냅니다.'}`,
    implPart || sub || '',
  ].filter(Boolean);

  return parts.join('\n');
}

function generateKoreanSummary(card) {
  const { T, sub, g, src, d } = card;

  // Factual part: content before "—" separator if present, otherwise full gist
  let factual = g || '';
  if (factual.includes('—')) {
    factual = factual.split('—')[0].trim();
  }

  const parts = [
    `📰 요약`,
    T || '',
    sub ? `${sub}` : '',
    factual ? `${factual}` : '',
    src ? `출처: ${src}${d ? ' · ' + d : ''}` : '',
  ].filter(Boolean);

  return parts.join('\n');
}

function generateDeepAnalysis(card) {
  const { T, sub, g, r, s, src } = card;

  const regionPerspective = {
    US: 'FEOC 준수 여부와 45X 크레딧 확보가 시장 접근을 좌우합니다. Section 301 관세와 맞물려 비중국 공급망 재편을 가속화합니다.',
    EU: 'Battery Regulation 여권 의무화(2027)와 CBAM 본격 시행을 앞두고 규제 준수 비용이 진입 장벽으로 작용합니다.',
    CN: '과잉설비 기반 저가 공세와 흑연·리튬 수출 통제가 맞물려 글로벌 공급망 재편의 핵심 변수입니다.',
    KR: 'ESS 안전기준 강화와 용량시장 입찰 확대가 국내 시장 구조를 바꾸고 있습니다. 수출 규제 대응과 내수 성장을 동시에 고려해야 합니다.',
    JP: 'GX 20조엔 투자와 METI 보조금이 ESS 시장을 본격 열고 있습니다. 계통유연성 조정력 수요가 구체화되고 있습니다.',
  };

  const signalDepth = {
    t: '구조적 전환 신호 — 업계 전반의 방향을 바꿀 수 있는 변화입니다. 즉각적인 전략 검토가 필요합니다.',
    h: '고임팩트 신호 — 단기(3~6개월) 내 대응 조치가 필요합니다.',
    m: '중기 관찰 대상 — 12개월 이상의 추세 변화로 연결될 수 있습니다.',
    i: '배경 정보 — 맥락 이해와 중장기 추적에 활용하세요.',
  };

  const watchpointByRegion = {
    US: ['MACR 기준 변화', 'Section 301 관세 갱신 여부', 'Treasury FEOC 가이드라인'],
    EU: ['Battery Passport 파일럿 일정', 'CBAM 전환기 종료 후 실제 부과', 'CRM Act 광물 목록 업데이트'],
    CN: ['흑연 수출허가 실제 운용', 'LFP 설비 과잉 조정 신호', '제3국 우회 수출 규모'],
    KR: ['ESS 안전기준 개정 시행일', '용량시장 입찰 결과', '배터리 여권 국내 적용 로드맵'],
    JP: ['METI 보조금 2차 공모 시기', 'GX 채권 집행 진도', '계통용 ESS 접속 규칙 개정'],
  };

  const wp = watchpointByRegion[r] || ['공급망 변화', '규제 동향', '시장 가격 추이'];

  const parts = [
    `🔍 분석`,
    g || sub || T,
    regionPerspective[r] ? `\n[지역 맥락] ${regionPerspective[r]}` : '',
    `\n[시그널 강도] ${signalDepth[s] || '추가 관찰이 필요합니다.'}`,
    `\n[관전 포인트]\n• ${wp.join('\n• ')}`,
    src ? `\n출처: ${src}` : '',
  ].filter(Boolean);

  return parts.join('\n');
}
