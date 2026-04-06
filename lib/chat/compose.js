import { fmtDate, REGION_KR_LABEL, toCardView, toLinkView } from "./common.js";
import { buildSuggestions } from "./suggestions.js";

function composeFromFaq(retrieval, sourceMode, confidence, debug, scope) {
  return {
    answer: retrieval?.faq?.answer || "관련 FAQ를 찾지 못했어.",
    answer_type: "general",
    source_mode: sourceMode,
    confidence,
    cards: [],
    external_links: [],
    suggestions: buildSuggestions("general", scope).map((label) => ({ label })),
    debug,
  };
}

function composePolicy(intent, retrieval, sourceMode, confidence, debug, scope) {
  const cards = (retrieval?.cards || []).slice(0, 4);
  const upcoming = retrieval?.policy?.upcoming || [];
  const regionLabel = scope?.region ? (REGION_KR_LABEL[scope.region] || scope.region) : "";

  let answer = "";
  if (!scope?.region) {
    answer = "어떤 지역 정책이 궁금해? 미국/유럽/한국/중국/일본 중 선택해줘.";
  } else {
    answer = `${regionLabel} 정책 관련 핵심 흐름을 정리했어.`;
    if (upcoming.length) {
      answer += "\n\n📅 다가오는 일정";
      for (const item of upcoming.slice(0, 3)) {
        answer += `\n• ${fmtDate(item.dt)} — ${item.t}`;
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

function composeCards(intent, retrieval, sourceMode, confidence, debug, scope, externalLinks = []) {
  const cards = (retrieval?.cards || []).slice(0, 4);
  const regionLabel = scope?.region ? `${REGION_KR_LABEL[scope.region] || scope.region} ` : "";
  const dateLabel = scope?.date ? `${fmtDate(scope.date)} ` : "";

  let answer = "";
  if (intent === "news") {
    answer = `${regionLabel}${dateLabel}기준 핵심 뉴스야.`;
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

  return {
    answer,
    answer_type: intent,
    source_mode: sourceMode,
    confidence,
    cards: cards.map(toCardView),
    external_links: externalLinks.map(toLinkView),
    suggestions: buildSuggestions(intent, scope).map((label) => ({ label })),
    debug,
  };
}

export function composeResponse({ intent, retrieval, sourceMode, confidence, debug, scope, externalLinks = [] }) {
  if (retrieval?.mode === "faq") {
    return composeFromFaq(retrieval, sourceMode, confidence, debug, scope);
  }
  if (intent === "policy") {
    return composePolicy(intent, retrieval, sourceMode, confidence, debug, scope);
  }
  return composeCards(intent, retrieval, sourceMode, confidence, debug, scope, externalLinks);
}
