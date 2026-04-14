import { BRAVE_KEYWORDS, kstToday } from "./common.js";

export function detectRegion(txt = "") {
  const l = txt.toLowerCase();
  // 한글/영문 + 한자 약어 모두 매치
  if (/(한국|국내|한국어|한\b|韓|kr|korea)/.test(l)) return "KR";
  if (/(미국|북미|美|us|usa|america|north\s*america)/.test(l)) return "US";
  if (/(중국|中|cn|china|prc)/.test(l)) return "CN";
  if (/(유럽|eu|europe|유로존)/.test(l)) return "EU";
  if (/(일본|日|jp|japan)/.test(l)) return "JP";
  return null;
}

// KST 기준 N일 전/후 날짜를 "YYYY.MM.DD"로 반환
function kstDateOffset(daysOffset = 0) {
  const now = new Date();
  const kst = new Date(now.getTime() + (now.getTimezoneOffset() + 540) * 60000);
  kst.setDate(kst.getDate() + daysOffset);
  return `${kst.getFullYear()}.${String(kst.getMonth() + 1).padStart(2, "0")}.${String(kst.getDate()).padStart(2, "0")}`;
}

export function detectDate(txt = "") {
  // 1) YYYY.MM.DD / YYYY-MM-DD / YYYY년 MM월 DD일 등 절대 날짜
  const m = txt.match(/(\d{4})[년.\-\/]?\s*(\d{1,2})[월.\-\/]?\s*(\d{1,2})/);
  if (m) {
    const y = m[1];
    const mo = m[2].padStart(2, "0");
    const d = m[3].padStart(2, "0");
    return `${y}.${mo}.${d}`;
  }

  // 2) 상대 날짜 키워드 (KST 기준)
  if (/(그저께|그제|재작일)/.test(txt)) return kstDateOffset(-2);
  if (/(어제|전일|작일|yesterday)/.test(txt)) return kstDateOffset(-1);
  if (/(오늘|금일|today)/.test(txt)) return kstDateOffset(0);
  if (/(내일|명일|tomorrow)/.test(txt)) return kstDateOffset(1);
  if (/(모레|명후일)/.test(txt)) return kstDateOffset(2);

  // 3) "N일 전 / N days ago"
  const daysAgoKr = txt.match(/(\d{1,2})\s*일\s*전/);
  if (daysAgoKr) return kstDateOffset(-parseInt(daysAgoKr[1], 10));
  const daysAgoEn = txt.match(/(\d{1,2})\s*days?\s*ago/i);
  if (daysAgoEn) return kstDateOffset(-parseInt(daysAgoEn[1], 10));

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

  // stopword 확장 — 지역 대명사, 시점 대명사, 서술어 포함
  const stop = new Set([
    // 시점
    "오늘", "어제", "그제", "그저께", "내일", "모레", "최근", "최신", "지금", "이번", "요즘",
    // 질의 행위
    "뉴스", "정책", "요약", "비교", "설명", "해줘", "찾아줘", "알려줘", "보여줘", "부탁", "정리",
    // 연결어/부사
    "그리고", "또", "중심", "관련", "기사", "링크", "외부", "대해", "대한", "위해", "관한",
    // 서술어성 명사 — 엔티티 오분류 방지 (audit #25)
    "상황", "현황", "소식", "이슈", "동향", "전망", "영향", "의미",
    // 지역명 — region은 detectRegion에서 이미 분리, entity로 또 잡히면 노이즈
    "한국", "미국", "중국", "유럽", "일본", "북미",
  ]);
  const topicTokens = tokens.filter((w) => !stop.has(w)).slice(0, 8);
  const topic = topicTokens.join(" ") || null;

  // 엔티티 추출 — 대문자/숫자/특수문자 있는 토큰 우선
  const entityCandidates = new Set();
  for (const rt of rawTokens) {
    const ltRt = rt.toLowerCase();
    if (stop.has(ltRt)) continue;
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
