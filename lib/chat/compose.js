import { fmtDate, REGION_KR_LABEL, REGION_POLICY, toCardView, toLinkView } from "./common.js";
import { buildSuggestions } from "./suggestions.js";

function composeFromFaq(retrieval, sourceMode, confidence, debug, scope, externalLinks = []) {
  return {
    answer: retrieval?.faq?.answer || "관련 FAQ를 찾지 못했어.",
    answer_type: "general",
    source_mode: sourceMode,
    confidence,
    cards: [],
    external_links: externalLinks.map(toLinkView),
    suggestions: buildSuggestions("general", scope).map((label) => ({ label })),
    debug,
  };
}

function composePolicy(intent, retrieval, sourceMode, confidence, debug, scope) {
  const cards = (retrieval?.cards || []).slice(0, 4);
  const upcoming = retrieval?.policy?.upcoming || [];
  const regionKey = scope?.region || "";
  const regionLabel = regionKey ? (REGION_KR_LABEL[regionKey] || regionKey) : "";
  const hasExternal = debug?.external_link_count > 0;
  const weakPolicyEvidence = confidence < 0.75 || (!cards.length && !upcoming.length);

  // Get policy data from REGION_POLICY
  const policyData = regionKey ? REGION_POLICY[regionKey] : null;

  let answer = "";
  if (!regionKey) {
    answer = "어떤 지역 정책이 궁금해? 미국/유럽/한국/중국/일본 중 선택해줘.";
  } else {
    // Include policy overview if available
    if (policyData) {
      answer = `📋 ${regionLabel} 정책 핵심\n\n`;

      // Add top 3 policies
      const topPolicies = policyData.policies.slice(0, 3);
      for (const p of topPolicies) {
        answer += `▸ ${p.name}\n${p.desc}\n\n`;
      }

      // Add "why important"
      answer += `⚡ 왜 중요한가\n${policyData.why}\n`;

      // Add upcoming schedules if available
      if (upcoming.length) {
        answer += "\n\n📅 다가오는 일정";
        for (const item of upcoming.slice(0, 3)) {
          answer += `\n• ${fmtDate(item.dt)} — ${item.t}`;
        }
      }

      // Add watchpoints
      if (policyData.watchpoints && policyData.watchpoints.length) {
        answer += "\n\n👁 관전 포인트";
        for (const wp of policyData.watchpoints.slice(0, 3)) {
          answer += `\n• ${wp}`;
        }
      }
    } else {
      // Fallback if no policy data
      answer = weakPolicyEvidence
        ? `${regionLabel} 정책 관련 내부 근거가 제한적이라 참고 수준으로 정리할게.`
        : `${regionLabel} 정책 관련 핵심 흐름을 정리했어.`;
      if (upcoming.length) {
        answer += "\n\n📅 다가오는 일정";
        for (const item of upcoming.slice(0, 3)) {
          answer += `\n• ${fmtDate(item.dt)} — ${item.t}`;
        }
      }
      if (weakPolicyEvidence && hasExternal) {
        answer += "\n\n내부 정책 근거가 약해서 외부 링크도 함께 붙였어.";
      } else if (weakPolicyEvidence && !hasExternal) {
        answer += "\n\n확정형 판단보다는 추가 확인이 필요해.";
      }
    }
  }

  return {
    answer,
    answer_type: intent,
    source_mode: sourceMode,
    confidence,
    cards: cards.map(toCardView),
    external_links: [],
    suggestions: buildSuggestions(intent, scope).map((label) => ({ label })),
    debug,
  };
}

function composeCards(intent, retrieval, sourceMode, confidence, debug, scope, externalLinks = [], lowConfidence = false) {
  const cards = (retrieval?.cards || []).slice(0, 4);
  const regionLabel = scope?.region ? `${REGION_KR_LABEL[scope.region] || scope.region} ` : "";
  const dateLabel = scope?.date ? `${fmtDate(scope.date)} ` : "";

  let answer = "";
  if (intent === "news") {
    answer = dateLabel ? `${regionLabel}${dateLabel} 기준 핵심 뉴스야.` : `${regionLabel}핵심 뉴스야.`;
    if (cards.length) {
      const whyLines = cards.slice(0, 3).map((c) => c.g ? `• ${c.T}\n  → ${c.g}` : `• ${c.T}`).join("\n\n");
      answer += `\n\n${whyLines}`;
    }
  } else if (intent === "summary") {
    const lines = cards.slice(0, 3).map((c, i) => `${i + 1}. ${c.T}`).join("\n");
    answer = lines ? `핵심 3줄 요약이야.\n\n${lines}` : "요약할 내부 카드가 부족해.";
  } else if (intent === "compare") {
    const lines = cards.slice(0, 3).map((c, i) => `${i + 1}. ${c.T}`).join("\n");
    answer = lines ? `비교 관련 카드야.\n\n${lines}` : "비교할 내부 카드가 부족해.";
  } else if (intent === "follow_up") {
    answer = cards.length ? `방금 맥락 기준으로 관련 카드를 다시 정리했어.` : `직전 맥락 기준으로 추가 근거를 찾는 중이야.`;
  } else {
    answer = cards.length ? `관련 카드 ${cards.length}건을 찾았어.` : `딱 맞는 내부 결과가 바로 안 잡혔어.`;
  }

  let finalSourceMode = sourceMode;
  if (lowConfidence && sourceMode === "internal") {
    answer = externalLinks.length
      ? "내부 근거가 충분하지 않아. 외부 기사 링크도 함께 확인해줘."
      : "내부 근거가 충분하지 않아. 질문을 조금 더 구체화해주거나 외부 검색 모드로 다시 시도해줘.";
    finalSourceMode = externalLinks.length ? "hybrid" : "internal";
  }

  return {
    answer,
    answer_type: intent,
    source_mode: finalSourceMode,
    confidence,
    cards: cards.map(toCardView),
    external_links: externalLinks.map(toLinkView),
    suggestions: buildSuggestions(intent, scope).map((label) => ({ label })),
    debug,
  };
}

export function composeResponse({ intent, retrieval, sourceMode, confidence, debug, scope, externalLinks = [], lowConfidence = false }) {
  if (retrieval?.mode === "faq") {
    return composeFromFaq(retrieval, sourceMode, confidence, debug, scope, externalLinks);
  }
  if (intent === "policy") {
    const policyResponse = composePolicy(intent, retrieval, sourceMode, confidence, debug, scope);
    return { ...policyResponse, external_links: externalLinks.map(toLinkView) };
  }
  return composeCards(intent, retrieval, sourceMode, confidence, debug, scope, externalLinks, lowConfidence);
}
