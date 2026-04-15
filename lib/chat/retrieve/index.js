// ============================================================================
// retrieve/index.js — Layer 3 dispatcher
// ============================================================================
// action + topic에 따라 retrieve 분기. rephrase/analyze_card는 retrieve skip
// (Layer 2 resolveContext의 resolved.prior_cards / target_card 재사용).
//
// Dispatch 표:
//   action=rephrase       → skip (resolved.prior_cards 그대로)
//   action=analyze_card   → skip (resolved.target_card 단일)
//   action=follow_up      → root topic 따라 dispatch
//   action=new_query      → topic 따라 dispatch
//
// topic dispatch:
//   faq_concept  → retrieveFaq
//   news         → retrieveNews
//   policy       → retrievePolicy
//   comparison   → retrieveComparison
//   general      → retrieveGeneral
// ============================================================================

import { retrieveFaq } from "./faq.js";
import { retrieveNews } from "./news.js";
import { retrievePolicy } from "./policy.js";
import { retrieveComparison } from "./comparison.js";
import { retrieveGeneral } from "./general.js";

function dispatchByTopic({ topic, rawMessage, scope, data }) {
  switch (topic) {
    case "faq_concept":
      return retrieveFaq({ rawMessage, data });
    case "news":
      return retrieveNews({ rawMessage, scope, data });
    case "policy":
      return retrievePolicy({ rawMessage, scope, data });
    case "comparison":
      return retrieveComparison({ rawMessage, scope, data });
    case "general":
    default:
      return retrieveGeneral({ rawMessage, scope, data });
  }
}

export function retrieve({ parsed, resolved, data }) {
  const { action, topic, rawMessage, scope } = parsed;

  // ─── rephrase: retrieve 하지 않음, 직전 cards 재사용 ───────────────────
  if (action === "rephrase") {
    return {
      source: "rephrase",
      cards: resolved?.prior_cards || [],
      _reasons: ["retrieve_skipped_rephrase"],
    };
  }

  // ─── analyze_card: 단일 카드 ───────────────────────────────────────────
  if (action === "analyze_card") {
    return {
      source: "analyze_card",
      cards: resolved?.target_card ? [resolved.target_card] : [],
      _reasons: ["retrieve_skipped_analyze_card"],
    };
  }

  // ─── follow_up: root topic 기준으로 재검색 (D11 해결) ──────────────────
  if (action === "follow_up") {
    // FAQ는 follow_up 대상 아님 (개념 질의는 한 번에 종결). follow_up에서 faq_concept이
    // 오면 general로 downgrade — rawMessage가 FAQ 키워드와 안 겹칠 가능성 큼.
    const effectiveTopic = topic === "faq_concept" ? "general" : topic;
    const res = dispatchByTopic({ topic: effectiveTopic, rawMessage, scope, data });
    // 새 카드가 없으면 prior_cards로 백업
    if (!res.cards?.length && resolved?.prior_cards?.length) {
      return {
        ...res,
        cards: resolved.prior_cards,
        _reasons: [...(res._reasons || []), "follow_up_fallback_prior_cards"],
      };
    }
    return { ...res, _reasons: [...(res._reasons || []), `follow_up_topic:${effectiveTopic}`] };
  }

  // ─── new_query: topic 기준 dispatch ─────────────────────────────────────
  return dispatchByTopic({ topic, rawMessage, scope, data });
}
