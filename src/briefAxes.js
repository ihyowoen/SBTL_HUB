// ============================================================================
// 브리프 축 시장(cluster marketplace) — R10
// 넓은 범위(전체 주간/월간) 브리프는 '무관한 40장 나열'이 아니라 '이야기가 되는
// 축 2~4개'로 만든다. 네 생성기가 축 후보를 내고 같은 점수판에서 경쟁한다:
//   ① related 그래프 — 편집자가 명시한 카드 간 연결(인과 신뢰 최상, 슬롯 1개 보장)
//   ② 주체 엔티티 — 별칭 그룹이 '제목'에 등장(본문 언급은 노이즈라 제외)
//   ③ 테마 — 도메인 사전(기술·정책 축), 제목 한정
//   ④ 지역/국가 — 제목 국가 토큰(도메인 밀집일 때만 자연히 이긴다)
// 응집력 게이트: '이야기'가 아닌 '소재 버킷'(예: 온갖 충전 소식 모음)은 문단이
// 나열로 후퇴하므로 버린다 — topK는 상한일 뿐, 못 채우면 적게 쓴다.
// 실측 근거: 2026-07 동결 픽스처에서 미중 광물 에스컬레이션·LFP 지표 연쇄가
// 축으로 형성되고, 응집 없는 '충전 인프라' 버킷 문단이 나열로 붕괴함을 확인.
// ============================================================================

const dateOf = (c) => String(c.d || c.date || "").slice(0, 10);
const sigOf = (c) => String(c.s || c.signal || "i").toLowerCase()[0];
const idOf = (c) => c.id || c.draft_id || "";
const titleOf = (c) => String(c.title || c.T || "");
const SIG_RANK = { t: 3, h: 2, m: 1, i: 0 };

function hitBoundary(term, h) {
  const w = String(term).toLowerCase();
  if (!w) return false;
  if (!/^[\x00-\x7f]+$/.test(w)) return h.includes(w); // 한글 등 비ASCII는 부분 매칭(접사 결합 허용)
  let i = h.indexOf(w);
  while (i !== -1) {
    const b = h[i - 1], a = h[i + w.length];
    if ((!b || !/[a-z0-9]/.test(b)) && (!a || !/[a-z0-9]/.test(a))) return true;
    i = h.indexOf(w, i + 1);
  }
  return false;
}

// ① related 연결 성분 (3장 이상)
function genRelated(pool) {
  const inPool = new Set(pool.map(idOf));
  const parent = new Map([...inPool].map((i) => [i, i]));
  const find = (x) => { while (parent.get(x) !== x) { parent.set(x, parent.get(parent.get(x))); x = parent.get(x); } return x; };
  let edgeTotal = 0;
  for (const c of pool) {
    for (const r of (Array.isArray(c.related) ? c.related : [])) {
      if (!inPool.has(r)) continue;
      const a = find(idOf(c)), b = find(r);
      if (a !== b) parent.set(a, b);
      edgeTotal += 1;
    }
  }
  if (!edgeTotal) return [];
  const groups = new Map();
  for (const c of pool) { const r = find(idOf(c)); if (!groups.has(r)) groups.set(r, []); groups.get(r).push(c); }
  return [...groups.values()].filter((g) => g.length >= 3).map((g) => ({ source: "related", key: guessLabel(g), cards: g }));
}

const STOP = new Set(["배터리", "전기차", "이차전지", "글로벌", "한국", "중국", "미국", "유럽", "일본", "발표", "확대", "계획", "추진", "시장", "산업", "기업", "정부", "신규", "최대", "공장", "생산", "투자", "돌파", "체결", "공급", "가동", "완공", "규모"]);
function guessLabel(g) {
  const cnt = {};
  g.forEach((c) => new Set(titleOf(c).split(/[^A-Za-z가-힣0-9]+/).filter((w) => w.length >= 2 && !STOP.has(w) && !/^\d+$/.test(w))).forEach((w) => { cnt[w] = (cnt[w] || 0) + 1; }));
  const top = Object.entries(cnt).sort((a, b) => b[1] - a[1])[0];
  return top ? top[0] : "연관 흐름";
}

// ② 주체 엔티티 (제목 등장 한정)
const LINK_TYPES = new Set(["company", "company_division", "company_brand", "research_org", "industry_org", "government_agency", "person"]);
function genEntity(pool, aliasEntities) {
  const out = [];
  for (const [k, e] of Object.entries(aliasEntities || {})) {
    if (e && e.type && !LINK_TYPES.has(e.type)) continue;
    const spellings = [(e && e.canonical) || k, ...(Array.isArray(e && e.aliases) ? e.aliases : [])].filter((s) => s && String(s).trim().length >= 2);
    const hits = pool.filter((c) => { const h = titleOf(c).toLowerCase(); return spellings.some((s) => hitBoundary(s, h)); });
    if (hits.length >= 3 && new Set(hits.map(dateOf)).size >= 2) out.push({ source: "entity", key: (e && e.canonical) || k, cards: hits });
  }
  return out;
}

// ③ 테마 — 제목 한정 (sub까지 열면 '디지털 화폐 예산 집행' 카드가 충전 축에 섞이는 류의 오염)
const THEMES = [
  ["전고체", ["전고체", "반고체", "solid-state"]],
  ["나트륨이온", ["나트륨이온", "나트륨", "sodium-ion"]],
  ["LFP", ["lfp", "리튬인산철"]],
  ["ESS·BESS", ["ess", "bess", "배터리저장", "저장장치", "에너지저장"]],
  ["재활용·폐배터리", ["재활용", "폐배터리", "리사이클"]],
  ["관세·수출통제", ["관세", "수출통제", "수출규제", "제재", "1260h", "feoc"]],
  ["보조금·정책", ["보조금", "ira", "ampc", "세액공제", "인센티브"]],
  ["리튬·광물", ["리튬", "광산", "희토류", "니켈", "코발트", "흑연", "핵심광물", "텅스텐"]],
  ["수주·계약", ["수주", "공급계약", "장기공급", "오프테이크", "ppa", "입찰"]],
];
function genTheme(pool) {
  const out = [];
  for (const [label, keys] of THEMES) {
    const hits = pool.filter((c) => { const h = titleOf(c).toLowerCase(); return keys.some((s) => hitBoundary(s, h)); });
    if (hits.length >= 3 && new Set(hits.map(dateOf)).size >= 2) out.push({ source: "theme", key: label, cards: hits });
  }
  return out;
}

// ④ 지역/국가 — 제목 한정 (region 필드는 호주 등이 GL에 숨어 무용)
const COUNTRIES = ["호주", "칠레", "인도", "사우디", "브라질", "독일", "영국", "프랑스", "이탈리아", "스페인", "폴란드", "헝가리", "캐나다", "멕시코", "인도네시아", "베트남", "태국", "대만", "뉴질랜드"];
function genRegion(pool) {
  const out = [];
  for (const cc of COUNTRIES) {
    const hits = pool.filter((c) => titleOf(c).includes(cc));
    if (hits.length >= 3 && new Set(hits.map(dateOf)).size >= 2) out.push({ source: "region", key: cc, cards: hits });
  }
  return out;
}

const SOURCE_BONUS = { related: 3, entity: 1.5, theme: 1, region: 0.5 };
function score(ax) {
  const t = ax.cards.filter((c) => sigOf(c) === "t").length;
  const h = ax.cards.filter((c) => sigOf(c) === "h").length;
  const span = new Set(ax.cards.map(dateOf)).size;
  return t * 3 + h * 1 + ax.cards.length * 0.5 + span * 0.5 + (SOURCE_BONUS[ax.source] || 0);
}
function jaccard(a, b) {
  const A = new Set(a.cards.map(idOf)), B = new Set(b.cards.map(idOf));
  let inter = 0;
  for (const x of A) if (B.has(x)) inter += 1;
  return inter / Math.min(A.size, B.size);
}

// 응집력 게이트 — '이야기' 판별. related·entity는 구조상 응집(편집 연결/주어 고정).
// theme·region 버킷은 다음 중 하나는 있어야 문단이 나열로 후퇴하지 않는다:
//   (a) 내부 related 엣지 ≥1 (편집자가 이 안에서 연결을 봄)
//   (b) t시그널 ≥2 (그 주의 굵직한 사건이 겹침 — 우연한 소재 일치가 아님)
//   (c) 같은 엔티티가 제목에 2회 이상 반복 (사실상 주체 축)
function isCohesive(ax, aliasEntities) {
  if (ax.source === "related" || ax.source === "entity") return true;
  const ids = new Set(ax.cards.map(idOf));
  const edges = ax.cards.reduce((a, c) => a + (Array.isArray(c.related) ? c.related.filter((r) => ids.has(r)).length : 0), 0);
  if (edges >= 1) return true;
  if (ax.cards.filter((c) => sigOf(c) === "t").length >= 2) return true;
  for (const [k, e] of Object.entries(aliasEntities || {})) {
    if (e && e.type && !LINK_TYPES.has(e.type)) continue;
    const spellings = [(e && e.canonical) || k, ...(Array.isArray(e && e.aliases) ? e.aliases : [])].filter(Boolean);
    let n = 0;
    for (const c of ax.cards) { const h = titleOf(c).toLowerCase(); if (spellings.some((s) => hitBoundary(s, h))) n += 1; if (n >= 2) return true; }
  }
  return false;
}

// 축 카드 정돈 — 시그널 상위 maxPerAxis장만 남기고 시간 오름차순(서사는 시간축)
function capAndOrderCards(cardsArr, maxPerAxis) {
  return cardsArr.slice()
    .sort((a, b) => (SIG_RANK[sigOf(b)] || 0) - (SIG_RANK[sigOf(a)] || 0)).slice(0, maxPerAxis)
    .sort((a, b) => dateOf(a).localeCompare(dateOf(b)));
}

// ---- R11: 달력월·지역별 구성 ----

// "2026-05" 형식의 달력월 판정 — 발행기(App.jsx)·워치룸 게이트가 같은 식을 쓴다.
// (챗 서버 게이트 lib/chat/appCommand.js의 countMonth*도 같은 startsWith 규약 — 서버는
// src/를 import하지 않으므로 중복 구현이며, 형식을 바꾸면 양쪽을 함께 바꿔야 한다.)
export function cardInMonth(c, month) {
  return String(c.date || c.d || "").slice(0, 7) === String(month || "");
}

// 카드 region 필드 코드 → 축 라벨. 봇 파이프라인 6리전 그대로이며, 소수(6장)인
// "US/KR" 류 콤보는 첫 코드 기준. 미지정·미지의 코드는 지역 축에서 제외.
const REGION_LABELS = { KR: "한국", CN: "중국", US: "미국", EU: "유럽", JP: "일본", GL: "글로벌" };
export function regionLabelOf(c) {
  const code = String(c.region || c.r || "").split("/")[0].trim().toUpperCase();
  return REGION_LABELS[code] || null;
}

// 지역별 구성 — 사용자가 명시 요청한 '의도적 정리'라 시장 경쟁·응집 게이트를 거치지
// 않는다(축 시장의 genRegion은 제목의 국가명 매칭이지만, 이쪽은 카드 region 필드가
// 정본이라 '인도/인도네시아' 류 오염이 없다). 카드 수 상위 topK개 지역, 축당
// maxPerAxis장. topK 기본 4 = 서버 MAX_AXES — 초과분은 서버가 조용히 잘라
// 클라 refs와 어긋나므로 여기서 맞춰 보낸다.
export function computeRegionAxes(pool, { topK = 4, maxPerAxis = 10, minPerAxis = 3 } = {}) {
  const groups = new Map();
  for (const c of pool) {
    const label = regionLabelOf(c);
    if (!label) continue;
    if (!groups.has(label)) groups.set(label, []);
    groups.get(label).push(c);
  }
  return [...groups.entries()]
    .filter(([, cards]) => cards.length >= minPerAxis)
    .sort((a, b) => b[1].length - a[1].length)
    .slice(0, topK)
    .map(([key, cards]) => ({ key, source: "regionField", cards: capAndOrderCards(cards, maxPerAxis) }));
}

// 서사 → 섹션 배열 [{key, text}] — 리더 렌더용(R13). 【축】 문단을 섹션으로 분해하고,
// 축 없는 flat 서사는 key=null 단일(또는 문단별) 섹션으로 돌려준다. 모델이 문단 중간에
// 【】를 인용부호로 쓴 경우는 문단 '시작'의 마커만 축 헤더로 인정한다.
export function parseBriefSections(narrative) {
  const t = String(narrative || "").trim();
  if (!t) return [];
  return t.split(/\n{2,}/).map((s) => s.trim()).filter(Boolean).map((p) => {
    const m = p.match(/^【([^】]{1,40})】\s*/);
    return m ? { key: m[1], text: p.slice(m[0].length) } : { key: null, text: p };
  });
}

// 주제별 구성(R13) — genTheme의 주제 사전을 지역별처럼 '의도적 정리' 축으로 쓴다.
// 지역과 달리 한 카드가 여러 주제에 걸릴 수 있어(예: 리튬 수주 계약) greedy 소진으로
// 배타화한다: 카드 수 큰 주제부터 아직 안 쓰인 카드만 취해, 최종 [n] 인용·refs 대응이
// 깨지지 않게 같은 카드가 두 문단에 반복되지 않도록 한다. 사용자가 명시 요청한 구성이라
// 응집 게이트는 없다(축 시장의 genTheme는 후보 경쟁용으로 그대로 남는다).
export function computeThemeAxes(pool, { topK = 6, maxPerAxis = 8, minPerAxis = 3 } = {}) {
  const groups = [];
  for (const [label, keys] of THEMES) {
    const cs = pool.filter((c) => { const h = titleOf(c).toLowerCase(); return keys.some((k) => hitBoundary(k, h)); });
    if (cs.length >= minPerAxis) groups.push({ key: label, cards: cs });
  }
  groups.sort((a, b) => b.cards.length - a.cards.length);
  const used = new Set();
  const picked = [];
  for (const g of groups) {
    if (picked.length >= topK) break;
    const fresh = g.cards.filter((c) => !used.has(idOf(c)));
    if (fresh.length < minPerAxis) continue;
    const cards = capAndOrderCards(fresh, maxPerAxis);
    cards.forEach((c) => used.add(idOf(c)));
    picked.push({ key: g.key, source: "themeField", cards });
  }
  return picked;
}

// ---- R14: 커스텀 조합(브리프 빌더) ----

// 빌더 칩 선택지 — 지역 6 + 주제 9. 라벨이 곧 spec.key(축 제목·서버 【축】 마커)다.
export const REGION_AXIS_KEYS = Object.values(REGION_LABELS);
export const THEME_AXIS_KEYS = THEMES.map(([label]) => label);
const THEME_KEYWORDS = new Map(THEMES.map(([label, keys]) => [label, keys]));

// 한 축 선택지의 후보 카드 — computeCustomAxes와 빌더 칩 카드 수 뱃지가 같은 식을 쓴다
// (뱃지 수와 실제 발행 재료가 어긋나면 '21장이라더니 축이 빠졌다'는 정직성 문제가 된다.
//  단 뱃지는 단독 축 기준이고 발행은 선택 순서 greedy 소진 후라, 겹치는 축을 여럿 고르면
//  실제 축 카드는 뱃지보다 적을 수 있다 — 빌더 요약이 소진 후 수치를 다시 보여준다.)
// type "watch"(워치 용어 축)는 매칭식이 앱 소유(cardMatchesWatch — 별칭·건초더미 규약)라
// watchMatch 주입으로 받는다 — 이 모듈은 앱 의존 없이 순수하게 남는다.
export function customAxisCandidates(pool, type, key, watchMatch = null) {
  if (type === "region") return pool.filter((c) => regionLabelOf(c) === key);
  if (type === "watch") return typeof watchMatch === "function" ? pool.filter((c) => watchMatch(c, key)) : [];
  const keys = THEME_KEYWORDS.get(key);
  if (!keys) return [];
  return pool.filter((c) => { const h = titleOf(c).toLowerCase(); return keys.some((k) => hitBoundary(k, h)); });
}

// 커스텀 조합 — 사용자가 지역·주제 축을 직접 골라 배치한 브리프("내맘대로 짜깁기").
// spec: [{type:"region"|"theme", key}] 순서 배열. 선택 '순서'가 곧 서사 순서라
// 카드 수 정렬을 하지 않는다(지역별·주제별과 다른 점). 한 카드가 지역·주제 양쪽에
// 걸릴 수 있어 spec 순서대로 greedy 소진해 배타화한다 — computeThemeAxes와 같은
// 이유([n] 인용·refs 대응이 카드 중복으로 깨지지 않게). minPerAxis 미달 축은 탈락 —
// 빌더 UI가 사전에 카드 수를 보여주므로 여기 탈락은 '겹침 소진 후 부족'이 대부분이다.
export function computeCustomAxes(pool, spec, { maxPerAxis = 8, minPerAxis = 3, watchMatch = null } = {}) {
  const used = new Set();
  const picked = [];
  for (const s of Array.isArray(spec) ? spec : []) {
    if (picked.length >= 6) break; // 서버 MAX_AXES와 페어 — 초과분은 서버가 잘라 refs가 어긋난다
    const type = s && s.type === "region" ? "region" : s && s.type === "theme" ? "theme" : s && s.type === "watch" ? "watch" : null;
    const key = String((s && s.key) || "");
    if (!type || !key) continue;
    const fresh = customAxisCandidates(pool, type, key, watchMatch).filter((c) => !used.has(idOf(c)));
    if (fresh.length < minPerAxis) continue;
    const cards = capAndOrderCards(fresh, maxPerAxis);
    cards.forEach((c) => used.add(idOf(c)));
    picked.push({ key, source: type === "region" ? "customRegion" : type === "watch" ? "customWatch" : "customTheme", cards });
  }
  return picked;
}

// pool → 응집 축 최대 topK개 (축당 maxPerAxis장, 내부는 시간 오름차순 — 서사는 시간축)
export function computeBriefAxes(pool, aliasEntities, { topK = 3, maxPerAxis = 10 } = {}) {
  const cand = [...genRelated(pool), ...genEntity(pool, aliasEntities), ...genTheme(pool), ...genRegion(pool)]
    .map((ax) => ({ ...ax, score: score(ax) }))
    .sort((a, b) => b.score - a.score);
  const capAndOrder = (cardsArr) => capAndOrderCards(cardsArr, maxPerAxis);
  const picked = [];
  const used = new Set(); // greedy 카드 소진 — 같은 사건이 두 문단에 반복되지 않게
  const tryPick = (ax) => {
    if (ax._picked) return false;
    if (!isCohesive(ax, aliasEntities)) return false;
    const fresh = ax.cards.filter((c) => !used.has(idOf(c)));
    if (fresh.length < 3 || fresh.length / ax.cards.length < 0.6) return false;
    const cards = capAndOrder(fresh);
    cards.forEach((c) => used.add(idOf(c)));
    ax._picked = true;
    picked.push({ key: ax.key, source: ax.source, cards });
    return true;
  };
  const bestRelated = cand.find((ax) => ax.source === "related");
  if (bestRelated) tryPick(bestRelated); // 편집자 인과는 점수가 낮아도 한 슬롯 보장
  for (const ax of cand) {
    if (picked.length >= topK) break;
    if (ax._picked) continue;
    if (picked.some((p) => jaccard(p, ax) > 0.4)) continue;
    tryPick(ax);
  }
  return picked;
}
