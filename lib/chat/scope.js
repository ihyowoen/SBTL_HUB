import { BRAVE_KEYWORDS, kstToday } from "./common.js";

export function detectRegion(txt = "") {
  const l = txt.toLowerCase();
  if (/(한국|국내|kr)/.test(l)) return "KR";
  if (/(미국|북미|us|america)/.test(l)) return "US";
  if (/(중국|cn|china)/.test(l)) return "CN";
  if (/(유럽|eu|europe)/.test(l)) return "EU";
  if (/(일본|jp|japan)/.test(l)) return "JP";
  return null;
}

export function detectDate(txt = "") {
  const m = txt.match(/(\d{4})[년.\-\/]?\s*(\d{1,2})[월.\-\/]?\s*(\d{1,2})/);
  if (m) {
    const y = m[1];
    const mo = m[2].padStart(2, "0");
    const d = m[3].padStart(2, "0");
    return `${y}.${mo}.${d}`;
  }
  if (/(오늘|금일)/.test(txt)) return kstToday();
  return null;
}

export function extractScope(message = "", context = {}) {
  const txt = String(message || "").trim();
  const l = txt.toLowerCase();
  const inferredRegion = detectRegion(txt);
  const keepContextRegion = /(방금|이전|직전|아까)/.test(l) && context?.region;
  const region = inferredRegion || (keepContextRegion ? context.region : null);
  const date = detectDate(txt) || context?.date || null;
  const externalIntent = BRAVE_KEYWORDS.test(l);

  const tokens = l
    .replace(/[?!.,:;()\[\]{}]/g, " ")
    .split(/\s+/)
    .filter((w) => w.length >= 2);
  const rawTokens = txt
    .replace(/[?!.,:;()\[\]{}]/g, " ")
    .split(/\s+/)
    .filter((w) => w.length >= 2);

  const stop = new Set([
    "오늘", "최근", "최신", "뉴스", "정책", "요약", "비교", "설명", "해줘", "찾아줘", "관련", "기사", "링크",
    "정리", "중심", "알려줘", "보여줘", "부탁", "그리고", "또", "지금", "이번", "외부",
  ]);
  const topicTokens = tokens.filter((w) => !stop.has(w)).slice(0, 8);
  const topic = topicTokens.join(" ") || null;

  const entityCandidates = new Set();
  for (const rt of rawTokens) {
    if (/[A-Z]/.test(rt) || /\d/.test(rt) || /[&+-]/.test(rt)) {
      entityCandidates.add(rt);
    }
  }
  for (let i = 0; i < topicTokens.length - 1; i++) {
    const a = topicTokens[i];
    const b = topicTokens[i + 1];
    if (a.length >= 2 && b.length >= 2) entityCandidates.add(`${a} ${b}`);
  }
  for (const tt of topicTokens) {
    if (tt.length >= 3) entityCandidates.add(tt);
  }

  const rankedEntities = [...entityCandidates]
    .map((v) => String(v).trim())
    .filter(Boolean)
    .sort((a, b) => b.length - a.length)
    .slice(0, 6);
  const entity = rankedEntities[0] || topicTokens[0] || null;

  return {
    region,
    date,
    topic,
    entity,
    entity_candidates: rankedEntities,
    topic_tokens: topicTokens,
    explicit_external: externalIntent,
  };
}
