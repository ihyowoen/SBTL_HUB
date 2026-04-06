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

  const stop = new Set(["오늘", "최근", "최신", "뉴스", "정책", "요약", "비교", "설명", "해줘", "찾아줘", "관련", "기사", "링크"]);
  const topicTokens = tokens.filter((w) => !stop.has(w)).slice(0, 6);
  const topic = topicTokens.join(" ") || null;

  return {
    region,
    date,
    topic,
    entity: topicTokens[0] || null,
    explicit_external: externalIntent,
  };
}
