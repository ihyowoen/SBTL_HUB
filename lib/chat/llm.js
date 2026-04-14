// ============================================================================
// Groq LLM helper — server-side only
// ============================================================================
// Env: GROQ_API_KEY (VITE_ prefix 금지)
// Model: llama-3.3-70b-versatile (한국어 품질 + 속도)
// Timeout: 9s (Vercel serverless 기본 10s 넘지 않게)
// 실패 시 null 반환 → 호출자가 템플릿 fallback으로 graceful degrade
// ============================================================================

const GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions";
const DEFAULT_MODEL = "llama-3.3-70b-versatile";
const DEFAULT_TIMEOUT_MS = 9000;

// ─── 톤 가이드 (모든 프롬프트 공통) ────────────────────────────────────────
// 챗봇 캐릭터 '강차장'은 한국어 반말.
// Llama 3.3이 한국어 단어 자리에 한자를 hallucinate하는 경향 있어 명시적으로 금지.
const TONE_RULE = `[말투 규칙 — 반드시 지킬 것]
- 한국어 반말 평문. 존댓말·격식체 절대 금지.
- 어미는 "~야", "~해", "~거든", "~지", "~네", "~더라" 같은 반말 종결.
- 금지 어미: "~습니다", "~합니다", "~입니다", "~됩니다", "~한다", "~이다" (딱딱한 문어체 포함 금지).
- 이모지·마크다운·불릿(•, -, *, ▸, ▶) 금지. 순수 평문 문장만.
- 자연스러운 구어체지만 지나친 친근함(ㅋ, ㅎ, ~요) 금지. 차분한 반말.

[언어 규칙 — 반드시 지킬 것]
- 출력은 100% 한국어 단어와 숫자, 영문 고유명사(LG, SK, CATL 등)만 사용.
- 한자 절대 금지. "차지" 대신 "占" 쓰면 안 됨. "위상/비중/차지/점유" 등 한국어로.
- 근거 카드에 "K-파우치 내부 디버전스" 같은 문어체 표현이 있어도 그대로 인용하지 말고 반말로 풀어서 설명.
  예: "K-파우치 내부 디버전스" → "K-파우치 업체들 안에서 방향이 갈리고 있어"
  예: "구조적 전환이 가시화되고 있다" → "구조적 전환이 눈에 보이기 시작했어"
- 카드에서 따온 사실·숫자는 유지하되, 어미·문장 구조는 반드시 반말로 다시 써.`;

/**
 * Groq Chat Completion 호출.
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
// Card-based chat synthesis
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

const SYSTEM_CHAT = `너는 SBTL첨단소재(파우치 필름 제조사)의 사내 애널리스트 '강차장'이야.
배터리·ESS·EV 공급망 뉴스를 한국어 반말로 간결하게 브리핑해.

${TONE_RULE}

[내용 규칙]
- 제공된 카드 근거로만 답변. 카드에 없는 숫자/이름/일정은 절대 만들지 마.
- 근거 부족하면 "카드에 해당 내용이 부족해"라고 솔직히 말해.
- 2~4문장. SBTL 관점(파우치 필름, K-배터리 3사 공급망)에서 의미 있는 지점 있으면 짧게 언급.
- 날짜는 YYYY.MM.DD로. "오늘/어제" 같은 상대 표현은 근거 카드 날짜가 실제로 해당될 때만 사용.`;

const INTENT_INSTRUCTION = {
  news: "위 카드들 중 가장 중요한 1~2건을 골라, 왜 주목할 만한지 질문자의 관심사 맥락에서 설명해.",
  summary: "위 카드들의 공통 흐름을 한 줄로 요약한 뒤, 핵심 근거 카드 2건을 짧게 언급해.",
  compare: "위 카드들이 서로 어떻게 대비되거나 보완되는지 짚어줘. 단일 카드 설명이 되지 않도록.",
  follow_up: "직전 맥락을 이어받아, 위 카드들이 이전 논의에 어떤 후속 근거가 되는지 설명해.",
  general: "위 카드들이 질문에 어떻게 답이 되는지 요약해.",
};

export async function synthesizeChatAnswer({ message, intent, cards = [], newsMeta = null, scope = {} }) {
  if (!cards.length) return { text: null, error: "no-cards", latencyMs: 0 };

  const instruction = INTENT_INSTRUCTION[intent] || INTENT_INSTRUCTION.general;
  const cardBlock = formatCardsForPrompt(cards);

  let dateNote = "";
  if (intent === "news" && newsMeta?.date_mode === "fallback_latest") {
    dateNote = `\n\n[중요] 사용자는 ${newsMeta.requested_date} 기준으로 질문했지만 그 날짜 카드가 없어 최신 ${newsMeta.actual_date} 카드를 대신 제공. 답변 첫 문장에서 이 사실을 반말로 솔직히 알려.`;
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
// FAQ answer tone rewrite — 존댓말로 된 faq.a를 반말로 변환
// ============================================================================

const SYSTEM_FAQ_REWRITE = `너는 한국어 텍스트의 톤을 변환하는 에디터야.
주어진 존댓말/문어체 문단을 반말로 바꿔.

${TONE_RULE}

[변환 규칙]
- 사실 관계·숫자·고유명사·구조는 절대 바꾸지 마. 어미와 표현만 바꿔.
- 문장 수·순서 유지. 압축하거나 늘리지 마.
- "~습니다" → "~야/~해", "~입니다" → "~야", "~됩니다" → "~돼" 같은 식.
- 한자 어휘 나오면 한국어 동의어로 바꿔. 예: "占한다" → "차지해".
- 원문이 이미 완전한 반말이면 그대로 반환.
- 결과만 출력. 설명·주석·인용 기호 금지.`;

export async function rewriteToCasual(text) {
  if (!text || typeof text !== "string") return { text: null, error: "no-input", latencyMs: 0 };
  const t = text.trim();
  if (!t) return { text: null, error: "no-input", latencyMs: 0 };

  // 이미 반말이고 문어체·한자 문제 없으면 LLM 생략
  const hasFormal = /(습니다|합니다|입니다|됩니다|하세요|이에요|예요|세요|한다\.|이다\.|된다\.)/.test(t);
  // CJK 한자 감지 (한글·숫자·영문·일반 기호 외 한자 블록)
  const hasCJK = /[\u4E00-\u9FFF\u3400-\u4DBF]/.test(t);
  if (!hasFormal && !hasCJK) return { text: t, error: null, latencyMs: 0, skipped: true };

  return callGroq({
    system: SYSTEM_FAQ_REWRITE,
    user: t,
    maxTokens: Math.min(800, Math.ceil(t.length * 1.5)),
    temperature: 0.2,
  });
}

// ============================================================================
// Single-card analysis — why/summary/analysis
// ============================================================================

const ANALYSIS_PROMPTS = {
  why: {
    system: `너는 배터리·ESS·EV 산업 전문 애널리스트 '강차장'이야. 주어진 뉴스 카드의 전략적 의미와 산업 파급 효과를 분석해.

${TONE_RULE}

- 배터리/ESS/EV 공급망·시장에 미치는 구조적 영향 중심.
- 2~4문장. 사실 나열보다 "왜 중요한가"에 집중.`,
    user: (card) => `뉴스 제목: ${card.T || ""}\n부제: ${card.sub || ""}\n내용: ${card.g || ""}\n지역: ${card.r || ""} | 신호강도: ${card.s || ""}\n\n이 뉴스가 배터리·ESS·EV 산업에 왜 중요한지 2~4문장으로 설명해.`,
  },
  summary: {
    system: `너는 해외 배터리·에너지 뉴스를 한국 독자에게 전달하는 사내 브리핑 담당자야.

${TONE_RULE}

- 무슨 일이 일어났는지, 누가 관련됐는지, 언제·어디서인지 사실 중심.
- 배경 해석·의견 최소화. 팩트 중심.
- 3~5문장.`,
    user: (card) => `뉴스 제목: ${card.T || ""}\n부제: ${card.sub || ""}\n내용: ${card.g || ""}\n출처: ${card.src || ""} | 날짜: ${card.d || ""}\n\n이 뉴스의 핵심 사실을 3~5문장으로 요약해.`,
  },
  analysis: {
    system: `너는 배터리·ESS·EV 산업의 시니어 리서치 애널리스트 '강차장'이야. 다음 흐름으로 심층 분석해.
1) 배경·맥락 — 어떤 흐름의 일부인지
2) 시장·산업 영향 — 공급망·가격·경쟁 구도
3) 관전 포인트 2~3개
4) SBTL 관점 — 한국 파우치 필름/배터리 기업 시각

${TONE_RULE}

- 5~8문장. 번호 붙이지 말고 자연스러운 단락으로 이어서 써.`,
    user: (card) => `뉴스 제목: ${card.T || ""}\n부제: ${card.sub || ""}\n내용: ${card.g || ""}\n지역: ${card.r || ""} | 신호강도: ${card.s || ""} | 출처: ${card.src || ""}\n\n이 뉴스에 대한 심층 분석을 제공해.`,
  },
};

export async function synthesizeCardAnalysis(card, mode) {
  const tpl = ANALYSIS_PROMPTS[mode];
  if (!tpl) return { text: null, error: "invalid-mode", latencyMs: 0 };
  return callGroq({
    system: tpl.system,
    user: tpl.user(card),
    maxTokens: mode === "analysis" ? 600 : 400,
    temperature: 0.4,
  });
}
