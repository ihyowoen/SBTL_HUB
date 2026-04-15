// ============================================================================
// Layer 4: synthesize — action별 LLM or 템플릿 답변 생성
// ============================================================================
// Phase 2 신규. 기존 compose.js의 LLM 호출부를 분리.
//
// 역할:
// - action + topic에 따라 LLM 호출 방식 선택
// - 실패 시 graceful template fallback
// - rewriteToCasual 중복 호출 방지 (D13 해결):
//   · topic=faq_concept이면 FAQ 답변을 rewrite → 1회만
//   · topic=policy이면 policy 템플릿을 rewrite → 1회만
//   · 두 경로는 XOR (dispatcher에서 분리됨)
//
// Action별 경로:
//   rephrase       → rephraseAnswer(prior_answer, userInstruction)
//   analyze_card   → /api/analysis 위임 (orchestrator가 수행, 여기선 marker만)
//   new_query / follow_up:
//     topic=faq_concept → FAQ 답변 + rewriteToCasual
//     topic=policy      → REGION_POLICY 템플릿 + rewriteToCasual (template 있을 때만)
//     topic=news        → synthesizeChatAnswer (카드 기반 LLM)
//     topic=comparison  → synthesizeChatAnswer (intent=compare)
//     topic=general     → synthesizeChatAnswer 또는 템플릿
// ============================================================================

import { REGION_KR_LABEL, fmtDate, kstToday } from "./common.js";
import {
  synthesizeChatAnswer,
  rewriteToCasual,
  rephraseAnswer,
} from "./llm.js";

// ─── 템플릿 fallback helpers ────────────────────────────────────────────

function isCleanGist(g) {
  if (!g) return false;
  const t = String(g).trim();
  if (!t) return false;
  return /[.?!。]["')\]]?$|다["')\]]?$|요["')\]]?$|야["')\]]?$|해["')\]]?$/.test(t);
}

function templateNewsAnswer({ cards, scope, newsMeta }) {
  const regionLabel = scope?.region ? `${REGION_KR_LABEL[scope.region] || scope.region} ` : "";
  const requestedDate = newsMeta?.requested_date || scope?.date || null;
  const actualDate = newsMeta?.actual_date || null;
  const dateMode = newsMeta?.date_mode || null;

  let header = "";
  if (dateMode === "exact" && actualDate) {
    header = `${regionLabel}${fmtDate(actualDate)} 기준 핵심 뉴스야.`;
  } else if (dateMode === "fallback_latest" && actualDate) {
    const today = kstToday();
    header = (requestedDate === today || requestedDate === null)
      ? `오늘(${fmtDate(today)}) 등록된 카드가 아직 없어서, 최신 ${fmtDate(actualDate)} 기준으로 보여줄게.`
      : `${fmtDate(requestedDate)} 카드가 없어서 최신 ${fmtDate(actualDate)} 기준으로 보여줄게.`;
  } else if (dateMode === "empty") {
    return `${regionLabel}해당 조건에 맞는 내부 카드가 없어.`;
  } else if (dateMode === "lexical") {
    header = `${regionLabel}핵심 뉴스야.`;
  } else {
    header = `${regionLabel}핵심 뉴스야.`;
  }

  if (!cards.length) return header;
  const lines = cards.slice(0, 3).map((c) => {
    const gist = isCleanGist(c.g) ? c.g : null;
    const dateTag = c.d ? ` (${fmtDate(c.d)})` : "";
    return gist ? `${c.T}${dateTag}\n  ${gist}` : `${c.T}${dateTag}`;
  }).join("\n\n");
  return `${header}\n\n${lines}`;
}

function templatePolicyAnswer({ retrieval, scope }) {
  const region = scope?.region || null;
  const regionLabel = region ? (REGION_KR_LABEL[region] || region) : "";
  const template = retrieval?.policy?.template || null;
  const upcoming = retrieval?.policy?.upcoming || [];

  if (!region) {
    return "어떤 지역 정책이 궁금해? 미국, 유럽, 한국, 중국, 일본 중에서 골라줘.";
  }

  if (!template) {
    let ans = `${regionLabel} 정책 관련 내부 근거가 좀 약해. 참고 수준으로 정리할게.`;
    if (upcoming.length) {
      ans += "\n\n다가오는 일정:";
      for (const item of upcoming.slice(0, 3)) ans += `\n${fmtDate(item.dt)} — ${item.t}`;
    }
    return ans;
  }

  const topPolicies = template.policies.slice(0, 3);
  const policyLines = topPolicies.map((p) => `${p.name}: ${p.desc}`).join("\n\n");
  let ans = `${regionLabel} 정책 핵심 짚어줄게.\n\n${policyLines}\n\n중요한 이유는 ${template.why}`;

  if (upcoming.length) {
    ans += "\n\n다가오는 일정:";
    for (const item of upcoming.slice(0, 3)) ans += `\n${fmtDate(item.dt)} — ${item.t}`;
  }
  if (template.watchpoints && template.watchpoints.length) {
    ans += "\n\n관전 포인트:";
    for (const wp of template.watchpoints.slice(0, 3)) ans += `\n${wp}`;
  }
  return ans;
}

function templateComparisonAnswer({ retrieval }) {
  const cards = retrieval?.cards || [];
  const entities = retrieval?.comparison?.entities || [];
  if (!cards.length) return "비교할 내부 카드가 부족해.";
  if (entities.length >= 2) {
    return `${entities.slice(0, 3).join(" / ")} 비교 관련 카드 ${cards.length}건 찾았어. 요약 확인해줘.`;
  }
  const lines = cards.slice(0, 3).map((c, i) => `${i + 1}. ${c.T}`).join("\n");
  return `비교 관련 카드야.\n\n${lines}`;
}

function templateGeneralAnswer({ retrieval }) {
  const cards = retrieval?.cards || [];
  if (!cards.length) return "딱 맞는 내부 결과가 바로 안 잡혔어.";
  const lines = cards.slice(0, 3).map((c, i) => `${i + 1}. ${c.T}`).join("\n");
  return `관련 카드 ${cards.length}건 찾았어.\n\n${lines}`;
}

// ─── Main synthesize ────────────────────────────────────────────────────

/**
 * @param {object} input
 * @param {object} input.parsed      parseRequest 결과
 * @param {object} input.resolved    resolveContext 결과
 * @param {object} input.retrieval   retrieve 결과
 * @returns {Promise<{ answer, used_llm, llm_meta, rewrite_meta }>}
 */
export async function synthesize({ parsed, resolved, retrieval }) {
  const { action, topic, rawMessage, scope } = parsed;
  const meta = { llm: null, rewrite: null, path: null };

  // ─── analyze_card: orchestrator가 /api/analysis 호출하므로 여기선 marker만 ──
  if (action === "analyze_card") {
    return {
      answer: null,
      used_llm: false,
      delegate: { to: "analysis_api", card: resolved?.target_card || null, mode: "why" },
      meta: { ...meta, path: "analyze_card_delegate" },
    };
  }

  // ─── rephrase: LLM rephraseAnswer ──────────────────────────────────────
  if (action === "rephrase") {
    const priorAnswer = resolved?.prior_answer_text || "";
    const rw = await rephraseAnswer({
      priorAnswer,
      userInstruction: rawMessage,
      priorCards: resolved?.prior_cards || [],
    });
    meta.llm = { used: !!rw.text, error: rw.error, latency_ms: rw.latencyMs };
    meta.path = "rephrase_llm";
    if (rw.text) {
      return { answer: rw.text, used_llm: true, meta };
    }
    // LLM 실패 → 원본 직전 답변을 그대로 반환 (graceful fallback)
    return {
      answer: priorAnswer || "답변을 다시 정리하지 못했어. 질문을 다른 방식으로 해줄래?",
      used_llm: false,
      meta: { ...meta, path: "rephrase_fallback_original" },
    };
  }

  // ─── FAQ concept ───────────────────────────────────────────────────────
  if (topic === "faq_concept" && retrieval?.source === "faq" && retrieval?.faq?.answer) {
    const original = retrieval.faq.answer;
    const rw = await rewriteToCasual(original);
    meta.rewrite = { target: "faq", used: !!rw.text && !rw.skipped, skipped: !!rw.skipped, error: rw.error, latency_ms: rw.latencyMs };
    meta.path = "faq_rewrite";
    const finalText = rw.text || original;
    return { answer: finalText, used_llm: !!rw.text && !rw.skipped, meta };
  }

  // ─── Policy ────────────────────────────────────────────────────────────
  if (topic === "policy") {
    const templateText = templatePolicyAnswer({ retrieval, scope });
    // region 반문이면 rewrite 불필요
    if (!scope?.region) {
      meta.path = "policy_ask_region";
      return { answer: templateText, used_llm: false, meta };
    }
    const rw = await rewriteToCasual(templateText);
    meta.rewrite = { target: "policy", used: !!rw.text && !rw.skipped, skipped: !!rw.skipped, error: rw.error, latency_ms: rw.latencyMs };
    meta.path = "policy_template_rewrite";
    return { answer: rw.text || templateText, used_llm: !!rw.text && !rw.skipped, meta };
  }

  // ─── News / Comparison / General — card-based LLM synthesis ────────────
  const cards = retrieval?.cards || [];
  if (!cards.length) {
    // 카드 없음 — 템플릿 처리
    if (topic === "news") {
      meta.path = "news_no_cards_template";
      return { answer: templateNewsAnswer({ cards: [], scope, newsMeta: retrieval?.news_meta }), used_llm: false, meta };
    }
    if (topic === "comparison") {
      meta.path = "comparison_no_cards_template";
      return { answer: templateComparisonAnswer({ retrieval }), used_llm: false, meta };
    }
    meta.path = "general_no_cards_template";
    return { answer: templateGeneralAnswer({ retrieval }), used_llm: false, meta };
  }

  // LLM synthesis — Groq
  const llmIntent = topic === "news" ? "news"
    : topic === "comparison" ? "compare"
    : action === "follow_up" ? "follow_up"
    : "general";

  const llmRes = await synthesizeChatAnswer({
    message: rawMessage,
    intent: llmIntent,
    cards,
    newsMeta: retrieval?.news_meta || null,
    scope,
  });
  meta.llm = { used: !!llmRes.text, error: llmRes.error, latency_ms: llmRes.latencyMs, intent: llmIntent };
  meta.path = `llm_synthesis_${topic}`;

  if (llmRes.text) {
    return { answer: llmRes.text, used_llm: true, meta };
  }

  // LLM 실패 → 템플릿 fallback
  meta.path = `template_fallback_${topic}`;
  let templateAnswer;
  if (topic === "news") templateAnswer = templateNewsAnswer({ cards, scope, newsMeta: retrieval?.news_meta });
  else if (topic === "comparison") templateAnswer = templateComparisonAnswer({ retrieval });
  else templateAnswer = templateGeneralAnswer({ retrieval });
  return { answer: templateAnswer, used_llm: false, meta };
}
