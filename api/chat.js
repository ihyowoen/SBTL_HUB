import { loadKnowledge, toLinkView } from "../lib/chat/common.js";
import { classifyIntent } from "../lib/chat/intent.js";
import { extractScope } from "../lib/chat/scope.js";
import { retrieveInternal } from "../lib/chat/retrieval.js";
import { scoreConfidence } from "../lib/chat/confidence.js";
import { decideFallback } from "../lib/chat/fallback.js";
import { composeResponse } from "../lib/chat/compose.js";

const BRAVE_SEARCH_SUFFIX = "battery ESS EV";
const BRAVE_FETCH_CANDIDATE_LIMIT = 8;
const TRUSTED_DOMAINS = [
  "bloomberg.com",
  "reuters.com",
  "ft.com",
  "wsj.com",
  "nikkei.com",
  "iea.org",
  "energy-storage.news",
  "pv-magazine.com",
  "koreaherald.com",
  "yna.co.kr",
  "korea.kr",
  "thelec.kr",
  "electrive.com",
];

function hostFromUrl(url = "") {
  try {
    return new URL(url).hostname.toLowerCase();
  } catch {
    return "";
  }
}

function normalizeText(v = "") {
  return String(v || "").toLowerCase();
}

function rankExternalLinks(query, links = []) {
  const tokens = normalizeText(query).replace(/[?!.,:;()\[\]{}]/g, " ").split(/\s+/).filter((w) => w.length >= 2);
  return links
    .map((item) => {
      const host = hostFromUrl(item.url);
      const trusted = TRUSTED_DOMAINS.some((d) => host === d || host.endsWith(`.${d}`));
      const text = `${normalizeText(item.title)} ${normalizeText(item.description)}`;
      const tokenHits = tokens.reduce((acc, t) => (text.includes(t) ? acc + 1 : acc), 0);
      const relevance = tokens.length ? tokenHits / tokens.length : 0;
      const trustBoost = trusted ? 0.35 : 0;
      const shortHostPenalty = host.length < 4 ? -0.2 : 0;
      const score = relevance + trustBoost + shortHostPenalty;
      return { ...item, _score: score, _relevance: relevance, _trusted: trusted };
    })
    .filter((item) => item._score >= 0.2)
    .sort((a, b) => b._score - a._score)
    .slice(0, 4)
    .map(({ _score, _relevance, _trusted, ...rest }) => rest);
}

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

function stabilizeSourceMode(sourceMode, retrieval, externalLinks) {
  const hasInternal = !!retrieval?.faq || (retrieval?.cards || []).length > 0;
  const hasExternal = (externalLinks || []).length > 0;
  if (sourceMode === "external" && !hasExternal) return hasInternal ? "internal" : "external";
  if (sourceMode === "hybrid" && !hasExternal) return hasInternal ? "internal" : "external";
  return sourceMode;
}

async function fetchBraveResults(query) {
  const BRAVE_KEY = process.env.BRAVE_KEY || process.env.VITE_BRAVE_KEY;
  if (!BRAVE_KEY) return { error: "auth-config" };

  try {
    const queryWithSuffix = [String(query || "").trim(), BRAVE_SEARCH_SUFFIX].filter(Boolean).join(" ");
    const url = `https://api.search.brave.com/res/v1/web/search?q=${encodeURIComponent(queryWithSuffix)}&count=${BRAVE_FETCH_CANDIDATE_LIMIT}`;
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
      results: results.map((r) => ({
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
      externalLinks = rankExternalLinks(message, (ext?.results || []).map(toLinkView));
    }

    const finalSourceMode = stabilizeSourceMode(fallback.sourceMode, retrieval, externalLinks);
    const response = composeResponse({
      intent,
      retrieval,
      sourceMode: finalSourceMode,
      confidence: Math.round(confidenceRes.score * 100) / 100,
      lowConfidence: confidenceRes.bucket === "low",
      debug: {
        fallback_triggered: fallback.fallbackTriggered,
        confidence_bucket: confidenceRes.bucket,
        fallback_reason: fallback.reason,
        external_link_count: externalLinks.length,
      },
      scope,
      externalLinks,
    });

    return res.status(200).json(response);
  } catch (error) {
    return stableError(res, 500, "채팅 응답 생성 중 오류가 발생했어.", {
      error_code: "CHAT_ORCHESTRATION_ERROR",
      detail: error?.message || "unknown",
    });
  }
}
