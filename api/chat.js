import { loadKnowledge, toLinkView } from "../lib/chat/common.js";
import { classifyIntent } from "../lib/chat/intent.js";
import { extractScope } from "../lib/chat/scope.js";
import { retrieveInternal } from "../lib/chat/retrieval.js";
import { scoreConfidence } from "../lib/chat/confidence.js";
import { decideFallback } from "../lib/chat/fallback.js";
import { composeResponse } from "../lib/chat/compose.js";

const BRAVE_SEARCH_SUFFIX = "battery ESS EV";

function setCors(res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
}

function stableError(res, status, message, debug = {}) {
  return res.status(status).json({
    answer: message,
    answer_type: "general",
    source_mode: "internal",
    confidence: 0,
    cards: [],
    external_links: [],
    suggestions: [{ label: "오늘 핵심 카드" }, { label: "최근 시그널 TOP" }],
    debug: {
      fallback_triggered: false,
      confidence_bucket: "low",
      ...debug,
    },
  });
}

async function fetchBraveResults(query) {
  const BRAVE_KEY = process.env.BRAVE_KEY || process.env.VITE_BRAVE_KEY;
  if (!BRAVE_KEY) return { error: "auth-config" };

  try {
    const url = `https://api.search.brave.com/res/v1/web/search?q=${encodeURIComponent(`${query} ${BRAVE_SEARCH_SUFFIX}`)}&count=4`;
    const response = await fetch(url, {
      headers: {
        Accept: "application/json",
        "X-Subscription-Token": BRAVE_KEY,
      },
    });

    if (!response.ok) {
      return { error: "provider-error" };
    }

    const data = await response.json();
    const results = data?.web?.results || [];
    return {
      results: results.slice(0, 4).map((r) => ({
        title: r.title || "",
        description: r.description || "",
        url: r.url || "",
      })),
    };
  } catch {
    return { error: "network-error" };
  }
}

export default async function handler(req, res) {
  setCors(res);

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  if (req.method !== "POST") {
    return stableError(res, 405, "Method not allowed", { error_code: "METHOD_NOT_ALLOWED" });
  }

  try {
    const message = String(req.body?.message || "").trim();
    const context = req.body?.context || {};

    if (!message) {
      return stableError(res, 400, "질문을 먼저 입력해줘.", { error_code: "MESSAGE_REQUIRED" });
    }

    const data = await loadKnowledge();
    const intent = classifyIntent(message, context);
    const scope = extractScope(message, context);
    const retrieval = retrieveInternal({ message, intent, scope, data });
    const confidenceRes = scoreConfidence({ intent, retrieval, scope, context });
    const fallback = decideFallback({ scope, confidence: confidenceRes, retrieval });

    let externalLinks = [];
    if (fallback.sourceMode !== "internal") {
      const ext = await fetchBraveResults(message);
      externalLinks = (ext?.results || []).map(toLinkView);
      if (!externalLinks.length && fallback.sourceMode === "external") {
        fallback.sourceMode = "hybrid";
      }
    }

    const response = composeResponse({
      intent,
      retrieval,
      sourceMode: fallback.sourceMode,
      confidence: Number(confidenceRes.score.toFixed(2)),
      debug: {
        fallback_triggered: fallback.fallbackTriggered,
        confidence_bucket: confidenceRes.bucket,
      },
      scope,
      externalLinks,
    });

    if (confidenceRes.bucket === "low" && response.source_mode === "internal") {
      response.answer = "내부 근거가 충분하지 않아. 외부 기사 링크도 함께 확인해줘.";
      response.source_mode = externalLinks.length ? "hybrid" : "internal";
      response.external_links = externalLinks;
    }

    return res.status(200).json(response);
  } catch (error) {
    return stableError(res, 500, "채팅 응답 생성 중 오류가 발생했어.", {
      error_code: "CHAT_ORCHESTRATION_ERROR",
      detail: error?.message || "unknown",
    });
  }
}
