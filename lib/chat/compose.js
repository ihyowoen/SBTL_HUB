import { fmtDate, kstToday, REGION_KR_LABEL, REGION_POLICY, toCardView, toLinkView } from "./common.js";
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

// g 필드가 문장 중간에 잘린 경우 감지 — 문장 부호 없이 끝나거나 따옴표만 남은 경우
function isCleanGist(g) {
  if (!g) return false;
  const t = String(g).trim();
  if (!t) return false;
  // 문장 종결: 한국어(다/요), 영문(.?!), 한문 마침표(。)
  const endsCleanly = /[.?!。]["')\]]?$|다["')\]]?$|요["')\]]?$/.test(t);
  return endsCleanly;
}

function composeCards(intent, retrieval, sourceMode, confidence, debug, scope, externalLinks = [], lowConfidence = false) {
  const cards = (retrieval?.cards || []).slice(0, 4);
  const regionLabel = scope?.region ? `${REGION_KR_LABEL[scope.region] || scope.region} ` : "";
  const newsMeta = retrieval?.news_meta || null;

  let answer = "";
  if (intent === "news") {
    // 날짜 라벨 결정: news_meta 있으면 실제 반영된 날짜 기준
    const requestedDate = newsMeta?.requested_date || scope?.date || null;
    const actualDate = newsMeta?.actual_date || null;
    const dateMode = newsMeta?.date_mode || null;

    // 헤더 문구 — 요청과 실제가 다르면 솔직히 알림
    if (dateMode === "exact" && actualDate) {
      answer = `${regionLabel}${fmtDate(actualDate)} 기준 핵심 뉴스야.`;
    } else if (dateMode === "fallback_latest" && actualDate) {
      // 오늘 요청인데 오늘 카드 없음 → 최신 날짜로 대체
      const today = kstToday();
      if (requestedDate === today || requestedDate === null) {
        answer = `오늘(${fmtDate(today)}) 등록된 카드가 아직 없어서, 최신 ${fmtDate(actualDate)} 기준으로 보여줄게.`;
      } else {
        answer = `${fmtDate(requestedDate)} 카드가 없어서 최신 ${fmtDate(actualDate)} 기준으로 보여줄게.`;
      }
    } else if (dateMode === "empty") {
      answer = `${regionLabel}해당 조건의 내부 카드가 없어.`;
    } else if (dateMode === "lexical") {
      answer = `${regionLabel}핵심 뉴스야.`;
    } else {
      // 메타 없는 경우 (retrieval 구버전 호환)
      const dateLabel = scope?.date ? `${fmtDate(scope.date)} ` : "";
      answer = dateLabel ? `${regionLabel}${dateLabel}기준 핵심 뉴스야.` : `${regionLabel}핵심 뉴스야.`;
    }

    if (cards.length) {
      const whyLines = cards.slice(0, 3).map((c) => {
        const gist = isCleanGist(c.g) ? c.g : null;
        const dateTag = c.d ? ` [${fmtDate(c.d)}]` : "";
        return gist ? `• ${c.T}${dateTag}\n  → ${gist}` : `• ${c.T}${dateTag}`;
      }).join("\n\n");
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
