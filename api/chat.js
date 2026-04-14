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
  if (!BRAVE_KEY) return { error: "auth-config", status: 0 };

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
      const status = response.status;
      if (status === 401 || status === 403) return { error: "auth-error", status };
      if (status === 429) return { error: "rate-limit", status };
      if (status >= 500) return { error: "server-error", status };
      return { error: "provider-error", status };
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
  } catch (err) {
    return { error: "network-error", status: 0, detail: err?.message };
  }
}

async function callAnalysisAPI(card, mode) {
  try {
    const response = await fetch(`${process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : 'http://localhost:3000'}/api/analysis`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ card, mode }),
    });
    if (!response.ok) return null;
    const data = await response.json();
    return data?.result || null;
  } catch {
    return null;
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

    // [D1-DIAG] 진단 로그 — Vercel serverless에서 loadKnowledge()가 public/data/*.json을
    // 실제로 읽는지 확인. cwd + 각 데이터셋 length를 Function Logs에 남기고, 응답 debug에도 포함.
    // 가설: process.cwd()가 /var/task이고 public/은 CDN으로 분리되어 카드=0이 될 가능성.
    // 이 블록은 원인 확정 후 제거 예정 (audit FIX_PROPOSAL D1).
    const _t0 = Date.now();
    const data = await loadKnowledge();
    const _t1 = Date.now();
    const _diag = {
      cwd: process.cwd(),
      cards_len: Array.isArray(data?.cards) ? data.cards.length : -1,
      faq_len: Array.isArray(data?.faq) ? data.faq.length : -1,
      tracker_len: Array.isArray(data?.tracker?.items) ? data.tracker.items.length : -1,
      load_ms: _t1 - _t0,
      vercel_url: process.env.VERCEL_URL || null,
    };
    console.log(`[chat-diag-D1] ${JSON.stringify(_diag)}`);

    const intent = classifyIntent(message, context);
    const scope = extractScope(message, context);

    // Handle analysis-type intents
    if (intent === "analysis_why" || intent === "analysis_summary" || intent === "analysis_deep") {
      const topCard = context?.last_cards?.[0];
      if (!topCard) {
        return stableError(res, 400, "분석할 카드가 없어. 먼저 뉴스나 정책을 검색해줘.", { error_code: "NO_CARD_FOR_ANALYSIS", diag: _diag });
      }
      const analysisMode = intent === "analysis_why" ? "why" : intent === "analysis_summary" ? "summary" : "analysis";
      const analysisResult = await callAnalysisAPI(topCard, analysisMode);

      if (!analysisResult) {
        return stableError(res, 500, "분석을 생성하지 못했어. 다시 시도해줘.", { error_code: "ANALYSIS_FAILED", diag: _diag });
      }

      return res.status(200).json({
        answer: analysisResult,
        answer_type: intent,
        source_mode: "internal",
        confidence: 1.0,
        cards: [topCard],
        external_links: [],
        suggestions: [{ label: "관련 카드 더 보여줘" }, { label: "다른 뉴스 검색" }],
        debug: {
          fallback_triggered: false,
          confidence_bucket: "high",
          analysis_mode: analysisMode,
          diag: _diag,
        },
      });
    }

    const retrieval = retrieveInternal({ message, intent, scope, data });
    const confidenceRes = scoreConfidence({ intent, retrieval, scope, context });
    const fallback = decideFallback({ scope, confidence: confidenceRes, retrieval });

    let externalLinks = [];
    let braveError = null;
    if (fallback.sourceMode !== "internal") {
      const ext = await fetchBraveResults(message);
      if (ext.error) {
        braveError = { type: ext.error, status: ext.status, detail: ext.detail };
      }
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
        brave_error: braveError,
        diag: _diag,
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
