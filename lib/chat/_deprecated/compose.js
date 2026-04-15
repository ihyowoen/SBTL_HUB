import { fmtDate, kstToday, REGION_KR_LABEL, REGION_POLICY, toCardView, toLinkView } from "./common.js";
import { buildSuggestions } from "./suggestions.js";

function composeFromFaq(retrieval, sourceMode, confidence, debug, scope, externalLinks = []) {
  return {
    answer: retrieval?.faq?.answer || "관련 FAQ를 못 찾았어.",
    answer_type: "general",
    source_mode: sourceMode,
    confidence,
    cards: [],
    external_links: externalLinks.map(toLinkView),
    suggestions: buildSuggestions("general", scope).map((label) => ({ label })),
    debug,
  };
}

// 톤 통일 원칙:
// - 이모지/마크다운/불릿(•, ▸, *, #) 금지
// - 반말 평문. "~야/~해/~거든/~네/~더라" 같은 어미.
// - 존댓말(~습니다/~합니다/~입니다), 문어체(~한다/~이다) 금지.
// LLM 답변과 톤을 맞추기 위해 템플릿도 같은 규칙 적용.

function composePolicy(intent, retrieval, sourceMode, confidence, debug, scope) {
  const cards = (retrieval?.cards || []).slice(0, 4);
  const upcoming = retrieval?.policy?.upcoming || [];
  const regionKey = scope?.region || "";
  const regionLabel = regionKey ? (REGION_KR_LABEL[regionKey] || regionKey) : "";
  const hasExternal = debug?.external_link_count > 0;
  const weakPolicyEvidence = confidence < 0.75 || (!cards.length && !upcoming.length);

  const policyData = regionKey ? REGION_POLICY[regionKey] : null;

  let answer = "";
  if (!regionKey) {
    answer = "어떤 지역 정책이 궁금해? 미국, 유럽, 한국, 중국, 일본 중에서 골라줘.";
  } else if (policyData) {
    const topPolicies = policyData.policies.slice(0, 3);
    const policyLines = topPolicies
      .map((p) => `${p.name}: ${p.desc}`)
      .join("\n\n");

    // why 필드는 원문이 "~결정한다" 문어체라 그대로 두면 톤 깨짐.
    // LLM rewriteToCasual이 잡아주길 기대하되, 여기선 "중요한 이유는" 앞에 붙여 자연스럽게 연결.
    answer = `${regionLabel} 정책 핵심 짚어줄게.\n\n${policyLines}`;
    answer += `\n\n중요한 이유는 ${policyData.why}`;

    if (upcoming.length) {
      answer += "\n\n다가오는 일정:";
      for (const item of upcoming.slice(0, 3)) {
        answer += `\n${fmtDate(item.dt)} — ${item.t}`;
      }
    }

    if (policyData.watchpoints && policyData.watchpoints.length) {
      answer += "\n\n관전 포인트:";
      for (const wp of policyData.watchpoints.slice(0, 3)) {
        answer += `\n${wp}`;
      }
    }
  } else {
    answer = weakPolicyEvidence
      ? `${regionLabel} 정책 관련 내부 근거가 좀 약해. 참고 수준으로 정리할게.`
      : `${regionLabel} 정책 핵심 흐름 정리해줄게.`;
    if (upcoming.length) {
      answer += "\n\n다가오는 일정:";
      for (const item of upcoming.slice(0, 3)) {
        answer += `\n${fmtDate(item.dt)} — ${item.t}`;
      }
    }
    if (weakPolicyEvidence && hasExternal) {
      answer += "\n\n내부 근거가 부족해서 외부 링크도 같이 붙였어.";
    } else if (weakPolicyEvidence && !hasExternal) {
      answer += "\n\n확정적으로 판단하긴 어렵고 추가 확인이 필요해.";
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

// g 필드가 문장 중간에 잘린 경우 감지
function isCleanGist(g) {
  if (!g) return false;
  const t = String(g).trim();
  if (!t) return false;
  const endsCleanly = /[.?!。]["')\]]?$|다["')\]]?$|요["')\]]?$|야["')\]]?$|해["')\]]?$/.test(t);
  return endsCleanly;
}

function composeCards(intent, retrieval, sourceMode, confidence, debug, scope, externalLinks = [], lowConfidence = false) {
  const cards = (retrieval?.cards || []).slice(0, 4);
  const regionLabel = scope?.region ? `${REGION_KR_LABEL[scope.region] || scope.region} ` : "";
  const newsMeta = retrieval?.news_meta || null;

  let answer = "";
  if (intent === "news") {
    const requestedDate = newsMeta?.requested_date || scope?.date || null;
    const actualDate = newsMeta?.actual_date || null;
    const dateMode = newsMeta?.date_mode || null;

    if (dateMode === "exact" && actualDate) {
      answer = `${regionLabel}${fmtDate(actualDate)} 기준 핵심 뉴스야.`;
    } else if (dateMode === "fallback_latest" && actualDate) {
      const today = kstToday();
      if (requestedDate === today || requestedDate === null) {
        answer = `오늘(${fmtDate(today)}) 등록된 카드가 아직 없어서, 최신 ${fmtDate(actualDate)} 기준으로 보여줄게.`;
      } else {
        answer = `${fmtDate(requestedDate)} 카드가 없어서 최신 ${fmtDate(actualDate)} 기준으로 보여줄게.`;
      }
    } else if (dateMode === "empty") {
      answer = `${regionLabel}해당 조건에 맞는 내부 카드가 없어.`;
    } else if (dateMode === "lexical") {
      answer = `${regionLabel}핵심 뉴스야.`;
    } else {
      const dateLabel = scope?.date ? `${fmtDate(scope.date)} ` : "";
      answer = dateLabel ? `${regionLabel}${dateLabel}기준 핵심 뉴스야.` : `${regionLabel}핵심 뉴스야.`;
    }

    // 카드 목록은 LLM이 활성화되면 chat.js가 LLM 답변으로 override하고,
    // 여기서 만든 목록을 '근거 카드' 블록으로 뒤에 붙임. 이모지/불릿 없이 순수 라인만.
    if (cards.length) {
      const lines = cards.slice(0, 3).map((c) => {
        const gist = isCleanGist(c.g) ? c.g : null;
        const dateTag = c.d ? ` (${fmtDate(c.d)})` : "";
        return gist ? `${c.T}${dateTag}\n  ${gist}` : `${c.T}${dateTag}`;
      }).join("\n\n");
      answer += `\n\n${lines}`;
    }
  } else if (intent === "summary") {
    if (!cards.length) {
      answer = "요약할 내부 카드가 부족해.";
    } else {
      const lines = cards.slice(0, 3).map((c, i) => `${i + 1}. ${c.T}`).join("\n");
      answer = `핵심 3줄 요약이야.\n\n${lines}`;
    }
  } else if (intent === "compare") {
    if (!cards.length) {
      answer = "비교할 내부 카드가 부족해.";
    } else {
      const lines = cards.slice(0, 3).map((c, i) => `${i + 1}. ${c.T}`).join("\n");
      answer = `비교 관련 카드야.\n\n${lines}`;
    }
  } else if (intent === "follow_up") {
    answer = cards.length ? `방금 맥락 기준으로 관련 카드 다시 정리했어.` : `직전 맥락 기준으로 추가 근거 찾는 중이야.`;
  } else {
    answer = cards.length ? `관련 카드 ${cards.length}건 찾았어.` : `딱 맞는 내부 결과가 바로 안 잡혔어.`;
  }

  let finalSourceMode = sourceMode;
  if (lowConfidence && sourceMode === "internal") {
    answer = externalLinks.length
      ? "내부 근거가 부족해. 외부 기사 링크도 같이 확인해줘."
      : "내부 근거가 부족해. 질문을 좀 더 구체적으로 해주거나 외부 검색 모드로 다시 시도해줘.";
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
