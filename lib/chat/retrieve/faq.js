// ============================================================================
// retrieve/faq.js — FAQ 우선 매칭 (topic=faq_concept 전용)
// ============================================================================
// D7 해결: FAQ 매치는 topic=faq_concept일 때만 수행 — 다른 topic에서 FAQ가
// retrieve에 끼어들어 중복 처리(D13)되는 경로 제거.
// D5 해결: intent와 FAQ 매치가 독립 작동하던 구조를 topic dispatch로 통일.
// ============================================================================

// 스코어 기반 (매칭된 키워드 수 최고값)
export function matchFaq(faq = [], query = "") {
  const l = String(query || "").toLowerCase();
  let best = { f: null, hits: 0 };
  for (const f of faq) {
    const hits = (f.k || []).filter((k) => l.includes(String(k).toLowerCase())).length;
    if (hits > best.hits) best = { f, hits };
  }
  if (best.f) return { answer: best.f.a, keywords: best.f.k || [], hits: best.hits };
  return null;
}

export function retrieveFaq({ rawMessage, data }) {
  const hit = matchFaq(data?.faq || [], rawMessage);
  if (hit) {
    return {
      source: "faq",
      faq: hit,
      cards: [],
      _reasons: [`faq_match_hits:${hit.hits}`],
    };
  }
  return {
    source: "none",
    faq: null,
    cards: [],
    _reasons: ["faq_no_match"],
  };
}
