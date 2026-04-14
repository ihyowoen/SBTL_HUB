// ============================================================================
// Groq LLM helper — server-side only
// ============================================================================
// Env: GROQ_API_KEY (VITE_ prefix 금지)
// Model: llama-3.3-70b-versatile (한국어 품질 + 속도)
// Timeout: 12s (Vercel serverless 기본 10s 넘지 않게 — 9s로 abort)
// 실패 시 null 반환 → 호출자가 템플릿 fallback으로 graceful degrade
// ============================================================================

const GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions";
const DEFAULT_MODEL = "llama-3.3-70b-versatile";
const DEFAULT_TIMEOUT_MS = 9000;

/**
 * Groq Chat Completion 호출.
 * @param {Object} opts
 * @param {string} opts.system - 시스템 프롬프트
 * @param {string} opts.user - 사용자 프롬프트
 * @param {number} [opts.maxTokens=400]
 * @param {number} [opts.temperature=0.5]
 * @param {string} [opts.model=llama-3.3-70b-versatile]
 * @param {number} [opts.timeoutMs=9000]
 * @returns {Promise<{text: string|null, error: string|null, status?: number, latencyMs: number}>}
 */
export async function callGroq({ system, user, maxTokens = 400, temperature = 0.5, model = DEFAULT_MODEL, timeoutMs = DEFAULT_TIMEOUT_MS } = {}) {
  const apiKey = process.env.GROQ_API_KEY;
  if (!apiKey) return { text: null, error: "no-api-key", latencyMs: 0 };
  if (!user) return { text: null, error: "no-user-prompt", latencyMs: 0 };

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  const t0 = Date.now();

  try {
    const res = await fetch(GROQ_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model,
        messages: [
          ...(system ? [{ role: "system", content: system }] : []),
          { role: "user", content: user },
        ],
        max_tokens: maxTokens,
        temperature,
      }),
      signal: controller.signal,
    });

    const latencyMs = Date.now() - t0;

    if (!res.ok) {
      const status = res.status;
      let errType = "provider-error";
      if (status === 401 || status === 403) errType = "auth-error";
      else if (status === 429) errType = "rate-limit";
      else if (status >= 500) errType = "server-error";
      return { text: null, error: errType, status, latencyMs };
    }

    const data = await res.json();
    const text = data?.choices?.[0]?.message?.content?.trim() || null;
    return { text, error: text ? null : "empty-response", latencyMs };
  } catch (e) {
    const latencyMs = Date.now() - t0;
    const aborted = e?.name === "AbortError";
    return { text: null, error: aborted ? "timeout" : "network-error", detail: e?.message, latencyMs };
  } finally {
    clearTimeout(timeout);
  }
}

// ============================================================================
// Card-based chat synthesis — intent별 프롬프트
// ============================================================================

function formatCardsForPrompt(cards = []) {
  return cards.slice(0, 5).map((c, i) => {
    const parts = [
      `[${i + 1}] ${c.T || "(제목 없음)"}`,
      c.d ? `   날짜: ${c.d}` : null,
      c.r ? `   지역: ${c.r}` : null,
      c.sub ? `   요약: ${c.sub}` : null,
      c.g ? `   의미: ${c.g}` : null,
      c.src ? `   출처: ${c.src}` : null,
    ].filter(Boolean);
    return parts.join("\n");
  }).join("\n\n");
}

const SYSTEM_CHAT = `당신은 SBTL첨단소재(파우치 필름 제조사)의 사내 애널리스트 '강차장'입니다.
배터리·ESS·EV 공급망 뉴스를 한국어 반말(~야/~해)로 간결하게 브리핑합니다.

규칙:
- 제공된 카드 근거로만 답변. 카드에 없는 숫자/이름/일정은 절대 만들지 말 것.
- 근거 부족하면 "카드에 해당 내용이 부족해"라고 솔직히 말할 것.
- 2~4문장, 자연스러운 한국어 문어체 반말. 이모지/마크다운 금지.
- SBTL 관점(파우치 필름, K-배터리 3사 공급망)에서 볼 때 의미 있는 지점이 있으면 짧게 언급.
- 날짜는 YYYY.MM.DD로 표기. "오늘/어제" 같은 상대 표현은 근거 카드 날짜가 실제로 해당될 때만.`;

const INTENT_INSTRUCTION = {
  news: "위 카드들 중 가장 중요한 1~2건을 골라, 왜 주목할 만한지 질문자의 관심사 맥락에서 설명해.",
  summary: "위 카드들의 공통 흐름을 한 줄로 요약한 뒤, 핵심 근거 카드 2건을 짧게 언급해.",
  compare: "위 카드들이 서로 어떻게 대비되거나 보완되는지 짚어줘. 단일 카드 설명이 되지 않도록.",
  follow_up: "직전 맥락을 이어받아, 위 카드들이 이전 논의에 어떤 후속 근거가 되는지 설명해.",
  general: "위 카드들이 질문에 어떻게 답이 되는지 요약해.",
};

/**
 * 질문 + 카드 세트 → LLM 답변.
 * @param {Object} opts
 * @param {string} opts.message - 사용자 질문
 * @param {string} opts.intent
 * @param {Array} opts.cards - retrieval에서 뽑힌 카드 (최대 5장 사용)
 * @param {Object} [opts.newsMeta] - { date_mode, requested_date, actual_date }
 * @param {Object} [opts.scope]
 * @returns {Promise<{text: string|null, error: string|null, latencyMs: number}>}
 */
export async function synthesizeChatAnswer({ message, intent, cards = [], newsMeta = null, scope = {} }) {
  if (!cards.length) return { text: null, error: "no-cards", latencyMs: 0 };

  const instruction = INTENT_INSTRUCTION[intent] || INTENT_INSTRUCTION.general;
  const cardBlock = formatCardsForPrompt(cards);

  // news intent에서 date_mode가 fallback_latest면 솔직히 알릴 것을 명시
  let dateNote = "";
  if (intent === "news" && newsMeta?.date_mode === "fallback_latest") {
    dateNote = `\n\n[중요] 사용자는 ${newsMeta.requested_date} 기준으로 질문했지만 그 날짜 카드가 없어 최신 ${newsMeta.actual_date} 카드를 대신 제공. 답변 첫 문장에서 이 사실을 솔직히 알려.`;
  }

  const regionNote = scope?.region ? `\n[지역 스코프] ${scope.region}` : "";

  const userPrompt = `사용자 질문: ${message}${regionNote}${dateNote}\n\n근거 카드:\n${cardBlock}\n\n${instruction}`;

  return callGroq({
    system: SYSTEM_CHAT,
    user: userPrompt,
    maxTokens: 400,
    temperature: 0.4,
  });
}

// ============================================================================
// Single-card analysis — why/summary/analysis 모드 (api/analysis.js용)
// ============================================================================

const ANALYSIS_PROMPTS = {
  why: {
    system: `당신은 배터리·ESS·EV 산업 전문 애널리스트입니다. 주어진 뉴스 카드의 전략적 의미와 산업 파급 효과를 분석합니다.
- 배터리/ESS/EV 공급망·시장에 미치는 구조적 영향 중심
- 2~4줄, 한국어 평문. 마크다운·이모지 금지.
- 사실 나열보다 "왜 중요한가"에 집중.`,
    user: (card) => `뉴스 제목: ${card.T || ""}\n부제: ${card.sub || ""}\n내용: ${card.g || ""}\n지역: ${card.r || ""} | 신호강도: ${card.s || ""}\n\n이 뉴스가 배터리·ESS·EV 산업에 왜 중요한지 2~4줄로 설명해줘.`,
  },
  summary: {
    system: `당신은 해외 배터리·에너지 뉴스를 한국 독자에게 전달하는 전문 기자입니다.
- 무슨 일이 일어났는지, 누가 관련됐는지, 언제·어디서인지 사실 중심
- 배경 해석·의견 최소화
- 3~5줄, 자연스러운 한국어 평문. 마크다운·이모지 금지.`,
    user: (card) => `뉴스 제목: ${card.T || ""}\n부제: ${card.sub || ""}\n내용: ${card.g || ""}\n출처: ${card.src || ""} | 날짜: ${card.d || ""}\n\n이 뉴스의 핵심 사실을 한국어로 3~5줄로 요약해줘.`,
  },
  analysis: {
    system: `당신은 배터리·ESS·EV 산업의 시니어 리서치 애널리스트입니다. 다음 구조로 심층 분석:
1) 배경·맥락 — 어떤 흐름의 일부인지
2) 시장·산업 영향 — 공급망·가격·경쟁 구도
3) 관전 포인트 2~3개
4) SBTL 관점 — 한국 파우치 필름/배터리 기업 시각
- 5~8줄, 한국어 평문. 마크다운·이모지 금지.`,
    user: (card) => `뉴스 제목: ${card.T || ""}\n부제: ${card.sub || ""}\n내용: ${card.g || ""}\n지역: ${card.r || ""} | 신호강도: ${card.s || ""} | 출처: ${card.src || ""}\n\n이 뉴스에 대한 심층 분석을 제공해줘.`,
  },
};

export async function synthesizeCardAnalysis(card, mode) {
  const tpl = ANALYSIS_PROMPTS[mode];
  if (!tpl) return { text: null, error: "invalid-mode", latencyMs: 0 };
  return callGroq({
    system: tpl.system,
    user: tpl.user(card),
    maxTokens: mode === "analysis" ? 600 : 400,
    temperature: 0.5,
  });
}
