// ============================================================================
// appCommand — 에이전틱 명령 감지 (규칙 기반, LLM 무관)
// ----------------------------------------------------------------------------
// "CATL 내워치에 추가해줘" 같은 앱 조작 명령을 파이프라인 앞에서 감지해
// 클라이언트가 실행할 app_command 페이로드로 단락시킨다. 규칙 기반인 이유:
// 워치 목록을 바꾸는 조작은 LLM 오분류로 실행되면 안 되고, 감지 실패 시엔
// 그냥 일반 질의로 흘러가 검색 답변이 나오므로 실패 비용이 낮다.
// ============================================================================

import { matchAliasGroupNearestEnd } from "./common.js";

// 워치 변이는 localStorage를 즉시 바꾸므로 '명령'만 통과시켜야 한다. 동사 뒤에 명령형
// 어미(해줘·줘·해 등)만 오고 문장이 끝나는 형태로 앵커링 — "추가하면 뭐가 좋아?"·"삭제하면
// 어떻게 돼?" 같은 조건·의문형은 동사 뒤에 다른 말이 붙어 $에 걸리지 않아 배제된다.
// 비명령을 놓치면 그냥 검색으로 흘러가므로(실패 비용 낮음) 보수적으로 좁힌다.
// 종결부호에 물음표(?／？) 포함 — "추가해줄래?"·"보여줘?" 같은 정중한 요청형도 명령이다.
// 진짜 질문("추가하면 뭐가 좋아?")은 동사와 부호 사이에 절이 껴 앵커($)에서 여전히 걸러지므로
// ?를 허용해도 오탐이 늘지 않는다(명령형 어미 직후 종결이라는 조건이 실제 방어선).
const IMPERATIVE_TAIL = "(?:\\s*해)?\\s*(?:줘|주라|주세요|줄래|줄레|다오|라|주)?\\s*요?\\s*[.!~?？ㅎ]*\\s*$";
const CMD_WATCH_REMOVE = new RegExp(`(내\\s*)?워치(\\s*목록)?(에서)?\\s*(삭제|제거|빼|지워)${IMPERATIVE_TAIL}`);
// '다시'는 재추가 제안 칩("워치에 다시 추가해줘")이 다시 명령으로 걸리게
const CMD_WATCH_ADD = new RegExp(`(내\\s*)?워치(\\s*목록)?(에|에다)?\\s*(다시\\s*)?(추가|등록|넣어)${IMPERATIVE_TAIL}`);
// 프로필·주간브리프도 변이는 아니지만 파이프라인을 단락시켜 뷰를 열고 탭을 이동한다 —
// "프로필 보여주면 뭐가 좋아?"·"브리프 보여주는 조건이 뭐야" 같은 질문형이 답변 대신
// 화면을 바꿔버리면 안 되므로 워치와 동일하게 명령형 어미로 앵커링. '보여주면/보여주는'은
// 동사 뒤 '주면/주는'이 명령형 어미 집합에 없어 $에 안 걸려 배제된다.
const VIEW_TAIL = "(?:\\s*해)?\\s*(?:줘|주라|주세요|줄래|줄게|래|게|다오)?\\s*요?\\s*[.!~?？ㅎ]*\\s*$";
// 목적격 조사(을/를) 허용 — "프로필을 보여줘"·"브리프를 보여줘" 같은 자연스러운 입력도
// 명령으로. 앵커는 뒤 어미에 그대로 걸리므로 조사 허용이 질문형을 통과시키지 않는다.
const CMD_PROFILE = new RegExp(`프로필(?:을|를)?\\s*(보여|열어|띄워|볼|줘)${VIEW_TAIL}`);
// 기간 토큰 — 주간/월간에 더해 달력월("5월"·"2026년 4월"·"4월호", R11)을 인정한다.
// 숫자 분기가 먼저라 "월간"과 충돌하지 않고, '브리프'에 인접한 토큰만 읽는 원칙(R6·R9)은
// 그대로다. "지역별"은 구성 지시자 — 기간 토큰 앞뒤 어디든 허용("지역별 월간 브리프"·
// "5월 지역별 브리프"). 캡처: 1=지역별(앞) 2=기간 3=지역별(뒤).
const PERIOD_TOKEN = "((?:\\d{4}년\\s*)?\\d{1,2}월(?:호)?|주간|월간)";
const GROUP_TOKEN = "(지역\\s*별로?)?";
// 열람도 기간을 캡처 — "월간 브리프 보여줘"가 주간호를 열면 안 된다.
// 기간을 안 밝히면(그냥 "브리프 보여줘") period 없이 반환해 최신호를 그대로 연다.
const CMD_WEEKLY = new RegExp(`${GROUP_TOKEN}\\s*${PERIOD_TOKEN}?\\s*${GROUP_TOKEN}\\s*브리프(?:을|를)?\\s*(?:보여|열어|볼|줘|확인)${VIEW_TAIL}`);
// 강제 발행("지금 브리프 만들어줘"·"5월 지역별 브리프 만들어줘") — 열람(CMD_WEEKLY:
// 보여/열어…)과 동사가 달라 충돌 없음. 생성은 LLM 호출을 유발하므로 워치 변이와 같은
// 명령형 앵커를 적용(질문형 "만들면 뭐가 좋아?"는 검색으로). '월간'이면 재료 창 30일,
// 달력월이면 그 달 전체, 아니면 주간(7일).
const CMD_BRIEF_NOW = new RegExp(`${GROUP_TOKEN}\\s*${PERIOD_TOKEN}?\\s*${GROUP_TOKEN}\\s*브리프(?:을|를)?\\s*(?:지금\\s*|새로\\s*|다시\\s*|하나\\s*)*(?:만들어|만들|생성|발행|뽑아)${IMPERATIVE_TAIL}`);
const BRIEF_RECENT_MS = 10 * 60000; // 10분 내 발행본이 있으면 재생성 대신 열람으로

// 기간 토큰 해석 → {period, month}. 달력월은 연도 생략 시 올해, 아직 안 온 달이면
// 작년으로(7월에 "12월 브리프" = 2025-12). 달력월은 monthly 계열로 취급한다(재료 창이
// '최근 N일'이 아니라 그 달 전체라는 점만 다르고, 락·표시·보관은 월간 규약을 따른다).
function parsePeriodToken(tok) {
  if (!tok) return { period: null, month: null };
  if (tok === "월간") return { period: "monthly", month: null };
  if (tok === "주간") return { period: "weekly", month: null };
  const m = String(tok).match(/^(?:(\d{4})년\s*)?(\d{1,2})월/);
  if (!m) return { period: null, month: null };
  const mm = Number(m[2]);
  // 달 모양 토큰이 잡혔지만 1~12 밖이면(13월·0월) '파싱 불가'로 표시한다 — '토큰 없음'과
  // 구별해야 한다. 없음이면 주간(또는 지역별 월간)으로 폴백하지만, 잘못된 달을 같은
  // 폴백으로 넘기면 "13월 브리프 만들어줘"가 요청하지 않은 주간호를 조용히 발행한다.
  if (mm < 1 || mm > 12) return { period: null, month: null, invalid: true };
  const now = new Date();
  let year = m[1] ? Number(m[1]) : now.getUTCFullYear();
  if (!m[1] && mm > now.getUTCMonth() + 1) year -= 1;
  return { period: "monthly", month: `${year}-${String(mm).padStart(2, "0")}` };
}

// "2026-05" → "2026년 5월" (응답 문구·제안 칩용)
function monthKo(month) {
  const m = String(month || "").match(/^(\d{4})-(\d{2})$/);
  return m ? `${m[1]}년 ${Number(m[2])}월` : "그 달";
}

// App.jsx cardWatchHay와 동일 규칙 — 클라이언트가 이 term으로 substring 매칭하므로
// 여기서 같은 기준으로 세어야 표기 선택이 실제 화면 결과와 일치한다.
function cardHay(c) {
  return [c.T, c.title, c.sub, c.subtitle, c.fact, c.g, c.gate]
    .map((v) => String(v || "")).join(" ").toLowerCase();
}

// brief_now 재료 게이트 전용 건초더미 — 반드시 클라이언트 cardWatchHay(App.jsx)와 동일
// 내용을 산출해야 한다. 서버 normalizeChatCard는 g에 함의(implication)를 넣지만 클라
// toCompatCard의 g는 gate(검증 유보문)를 넣어, 서버가 g를 그대로 쓰면 함의에만 있는 텀을
// 과다 집계한다(실데이터에서 "capex" 서버 3 vs 클라 1). 그러면 서버가 brief_now를 승인해도
// 클라 runWeeklyBrief가 matched<2로 조용히 종료 → "지금 만들게" 약속 후 아무것도 안 생김.
// gate·fact·제목 필드는 두 정규화 공식이 동일하므로, 발산하는 g만 빼면 카운트가 일치한다.
// (resolveGroupTerm이 쓰는 cardHay는 별개 목적이라 건드리지 않는다.)
function briefMaterialHay(c) {
  return [c.T, c.title, c.sub, c.subtitle, c.fact, c.gate]
    .map((v) => String(v || "")).join(" ").toLowerCase();
}

// 최근 N일 내 워치 매칭 카드 수 — brief_now의 재료 게이팅용. 재료가 없는데 "만들게"라고
// 거짓 약속하는 것을 방지한다. 컷오프는 클라이언트 생성기(App.jsx cardDateWithinDays:
// UTC 기준 Date.now()-N일)와 반드시 같은 식이어야 한다 — KST 시프트를 섞으면 UTC 15시
// 이후 서버 컷오프가 하루 앞서가, 경계 날짜 카드로 생성 가능한 워치를 서버가 거절한다.
function countRecentWatchMatches(cards, watchTerms, days = 7) {
  const lowers = (watchTerms || []).map((w) => String(w).toLowerCase()).filter(Boolean);
  if (!lowers.length) return 0;
  const cutoff = new Date(Date.now() - days * 86400000).toISOString().slice(0, 10);
  let n = 0;
  for (const c of cards || []) {
    const d = String(c.d || c.date || "").slice(0, 10);
    if (!d || d < cutoff) continue;
    const hay = briefMaterialHay(c);
    if (lowers.some((w) => hay.includes(w))) n += 1;
  }
  return n;
}

// 전체 범위(워치 없음) 재료 카운트 — 날짜 창만 본다. 컷오프 식은 위와 동일해야
// 클라이언트 생성기(cardDateWithinDays)와 승인/실행이 갈리지 않는다.
function countRecentCards(cards, days = 7) {
  const cutoff = new Date(Date.now() - days * 86400000).toISOString().slice(0, 10);
  let n = 0;
  for (const c of cards || []) {
    const d = String(c.d || c.date || "").slice(0, 10);
    if (d && d >= cutoff) n += 1;
  }
  return n;
}

// 달력월("2026-05") 재료 카운트 — 클라이언트 판정(src/briefAxes.js cardInMonth)과 같은
// 'YYYY-MM 접두' 규약이어야 서버 약속("만들게")과 클라 생성 결과가 일치한다.
// (서버 코드는 src/를 import하지 않아 규약을 중복 구현 — 형식 변경 시 양쪽을 함께.)
function countMonthCards(cards, month, watchTerms = null) {
  const lowers = Array.isArray(watchTerms) ? watchTerms.map((w) => String(w).toLowerCase()).filter(Boolean) : null;
  let n = 0;
  for (const c of cards || []) {
    if (String(c.d || c.date || "").slice(0, 7) !== month) continue;
    if (lowers && !lowers.some((w) => briefMaterialHay(c).includes(w))) continue;
    n += 1;
  }
  return n;
}

// 별칭 그룹에서 클라이언트 매칭에 실제로 걸리는 표현을 선택.
// canonical을 그대로 쓰면 카드가 한글 표기일 때(예: 카드 "삼성SDI" vs canonical "Samsung SDI")
// 프로필·워치 필터가 전부 빗나간다 — 데이터 기준으로 고른다.
function resolveGroupTerm(group, type, { cards = [], watchTerms = [] } = {}) {
  // 삭제: 저장된 워치 목록에 있는 표기를 그대로 반환 — 클라이언트의 exact 비교와 일치
  if (type === "watch_remove") {
    const stored = watchTerms.find((w) => group.some((a) => String(a).toLowerCase() === String(w).toLowerCase()));
    if (stored) return stored;
  }
  // 추가·프로필: 카드 최다 히트 표현 (동점이면 그룹 앞 순서 = canonical 우선)
  const counts = new Array(group.length).fill(0);
  const lowers = group.map((a) => String(a).toLowerCase());
  for (const c of cards) {
    const hay = cardHay(c);
    lowers.forEach((a, i) => { if (hay.includes(a)) counts[i] += 1; });
  }
  let best = 0;
  for (let i = 1; i < group.length; i++) if (counts[i] > counts[best]) best = i;
  return group[best];
}

// 명령의 대상 용어: 명령 키워드(워치/프로필) '직전 구간'에서 키워드에 가장 가까운
// 엔티티를 고른다. 전체 메시지 최선두를 쓰면 "CATL 말고 BYD 워치에 추가"가 CATL로
// 오판되므로(부정 접두어 '말고' 포함), 키워드에 붙은 대상(BYD)을 우선한다.
// 별칭이 없으면 키워드 바로 앞 명사 토큰을 조사 제거 후 사용.
function extractCommandTerm(message, aliasGroups, type, opts) {
  const msg = String(message || "");
  const kw = type === "profile_open" ? "프로필" : "워치";
  const kwIdx = msg.indexOf(kw);
  const pre = kwIdx >= 0 ? msg.slice(0, kwIdx) : msg;
  const near = matchAliasGroupNearestEnd(pre, aliasGroups);
  if (near) return resolveGroupTerm(near, type, opts);
  // 별칭 미등재: 키워드 앞 '구 전체'를 대상으로(마지막 토큰만 쓰면 "전고체 배터리"→"배터리",
  // "solid state"→"state"로 잘린다). '내워치'의 '내'와 부정 접두 'X 말고'는 제거,
  // 끝 조사·따옴표 정리. 다단어 엔티티를 온전히 보존한다.
  const preClean = pre.replace(/\s*내\s*$/, "");
  const afterNeg = preClean.split(/\s*말고\s*/).pop() || ""; // "X 말고 Y" → Y
  const tok = afterNeg.trim()
    .replace(/(?:을|를|도|은|는|이|가|의)$/, "")
    .replace(/["'`]/g, "").trim();
  if (tok.length >= 2 && tok.length <= 24) return tok;
  return null;
}

// 피드 필터 명령 — "중국 카드만 보여줘"·"최근 7일로 좁혀줘"·"내워치 TOP만 보여줘".
// 지역/기간/시그널/내워치 4개 면(facet)만 다루고, 파싱 후 실질 잔여 텍스트(엔티티 등)가
// 남으면 null로 물러나 일반 검색이 처리하게 한다("CATL 카드 보여줘"는 검색으로).
const FEED_REGION = { "중국": "CN", "미국": "US", "북미": "NA", "한국": "KR", "유럽": "EU", "일본": "JP", "글로벌": "GL", "CN": "CN", "US": "US", "NA": "NA", "KR": "KR", "EU": "EU", "JP": "JP", "GL": "GL" };
const CMD_FEED = new RegExp(`(?:피드|카드|뉴스|소식)\\s*(?:만|를|을|으로|로)?\\s*(?:보여|열어|볼래|필터|좁혀)${VIEW_TAIL}`);
// 피드 명사 없이도 성립하는 면 전용 명령("내워치 TOP만 보여줘"·"최근 7일로 좁혀줘") —
// 열람 동사만 요구하고, 아래에서 면이 하나도 안 잡히면 물러난다("그거 보여줘"는 검색으로).
const CMD_FEED_VERB = new RegExp(`(?:만|를|을|으로|로)?\\s*(?:보여|열어|볼래|필터|좁혀)${VIEW_TAIL}`);
function detectFeedFilter(msg) {
  const hasNoun = CMD_FEED.test(msg);
  if (!hasNoun && !CMD_FEED_VERB.test(msg)) return null;
  const facets = {};
  let rest = msg;
  for (const [k, v] of Object.entries(FEED_REGION)) {
    if (rest.includes(k)) { facets.region = v; rest = rest.split(k).join(" "); break; }
  }
  const mR = rest.match(/최근\s*(7|30)\s*일/);
  if (mR) { facets.range = Number(mR[1]); rest = rest.replace(mR[0], " "); }
  else if (/일주일/.test(rest)) { facets.range = 7; rest = rest.replace(/일주일/g, " "); }
  else if (/한\s*달/.test(rest)) { facets.range = 30; rest = rest.replace(/한\s*달/g, " "); }
  if (/(top|톱|탑)/i.test(rest)) { facets.signal = "top"; rest = rest.replace(/top|톱|탑/gi, " "); }
  else if (/(high|하이)/i.test(rest)) { facets.signal = "high"; rest = rest.replace(/high|하이/gi, " "); }
  if (/내\s*워치/.test(rest)) { facets.watch = true; rest = rest.replace(/내\s*워치/g, " "); }
  if (!hasNoun && !Object.keys(facets).length) return null; // 명사도 면도 없으면 검색으로
  rest = rest
    .replace(/피드|카드|뉴스|소식|필터|좁혀|보여|열어|볼래|해줘|해줄래|주세요|주라|줄래|다오|줘|만|를|을|으로|로|는|은|요|해/g, " ")
    .replace(/[.!~?？\s]+/g, "");
  if (rest.length >= 2) return null; // 엔티티 등 실질 잔여 — 검색 파이프라인으로
  // 지역과 워치는 클라 피드에서 같은 축(단일 filter 상태)이라 겹치면 지역만 남긴다.
  // 시그널(TOP/HIGH)은 R8b부터 클라에 별도 축(sigFilter)이 생겨 지역/워치·기간과
  // 자유롭게 결합된다 — "중국 TOP만 보여줘"가 실제 교집합으로 적용되고 라벨과 일치.
  if (facets.region) delete facets.watch;
  return { type: "feed_filter", ...facets };
}

export function detectAppCommand(message, aliasGroups = [], opts = {}) {
  const msg = String(message || "");
  if (!msg || msg.length > 80) return null; // 명령은 짧다 — 긴 문장은 일반 질의로
  const briefNowMatch = msg.match(CMD_BRIEF_NOW);
  if (briefNowMatch) {
    // 강제 발행은 LLM 호출 + 보관함 변이 — 정직 게이팅(재료 부족/방금 발행).
    // 워치가 비어 있으면 거절하지 않고 '전체' 범위로 폴백한다(온보딩 스킵 유저가 다수 —
    // 워치 없이도 브리프를 경험하게). 범위·기간·구성은 응답 문구와 클라 생성기에 그대로 전달.
    const wt = opts.watchTerms || [];
    const parsedTok = parsePeriodToken(briefNowMatch[2]);
    // 잘못된 달(13월·0월)은 명령으로 처리하지 않고 검색으로 흘려보낸다 — 주간/월간으로
    // 조용히 폴백하면 사용자가 요청하지 않은 기간을 발행한다(감지 실패 비용은 낮다).
    if (parsedTok.invalid) return null;
    const { period: tokPeriod, month } = parsedTok;
    const group = briefNowMatch[1] || briefNowMatch[3] ? "region" : null;
    // 지역별 단독("지역별 브리프 만들어줘")은 월간 기본 — 7일 창은 지역 분포가 얇아
    // (실측: JP 주간 0~3장) 축이 잘 안 서고, '지역별 정리'의 의도 자체가 결산이다.
    const period = tokPeriod || (group ? "monthly" : "weekly");
    const days = period === "monthly" ? 30 : 7;
    const scope = wt.length ? "watch" : "all";
    // 쿨다운은 기간별 분리 — 주간 발행 직후의 월간 요청은 정당하다. 달력월·지역별 요청은
    // 쿨다운을 건너뛴다: last_*_brief_at은 '어느 호수'인지 모르는 단일 타임스탬프라
    // 6월호 직후의 "5월 브리프"를 부당하게 열람으로 강등시킨다(중복 방어는 클라 락 120초
    // + 명시 재요청은 정당한 재생성이라는 원칙으로 충분).
    const lastAt = Number((period === "monthly" ? opts.lastMonthlyBriefAt : opts.lastBriefAt) || 0);
    if (!month && !group && lastAt && Date.now() - lastAt < BRIEF_RECENT_MS) return { type: "weekly_show", reason: "recent_brief", period };
    const material = month
      ? countMonthCards(opts.cards || [], month, scope === "watch" ? wt : null)
      : scope === "watch" ? countRecentWatchMatches(opts.cards || [], wt, days) : countRecentCards(opts.cards || [], days);
    if (material < 2) return { type: "brief_no_material", scope, period, ...(month ? { month } : {}), ...(group ? { group } : {}) };
    return { type: "brief_now", scope, period, ...(month ? { month } : {}), ...(group ? { group } : {}) };
  }
  const weeklyShowMatch = msg.match(CMD_WEEKLY);
  if (weeklyShowMatch) {
    // 기간을 명시한 열람만 period를 실어 보낸다 — 없으면 클라가 최신호(기간 무관)를 연다.
    // group(지역별)도 발행과 동일하게 전파한다 — "5월 지역별 브리프 보여줘"에서 5월 일반호와
    // 5월 지역별호가 둘 다 있으면 클라가 요청한 지역별 변형을 정확히 골라야 한다(안 실으면
    // 먼저 매칭되는 아무 5월호나 열린다).
    const parsedShow = parsePeriodToken(weeklyShowMatch[2]);
    // 잘못된 달은 검색으로 — "13월 브리프 보여줘"가 엉뚱하게 최신호를 열지 않게(발행과 동일)
    if (parsedShow.invalid) return null;
    const { period, month } = parsedShow;
    const group = weeklyShowMatch[1] || weeklyShowMatch[3] ? "region" : null;
    if (!period && !month && !group) return { type: "weekly_show" };
    return { type: "weekly_show", ...(period ? { period } : {}), ...(month ? { month } : {}), ...(group ? { group } : {}) };
  }
  if (CMD_WATCH_REMOVE.test(msg)) {
    const term = extractCommandTerm(msg, aliasGroups, "watch_remove", opts);
    if (!term) return null;
    // 실제로 워치에 있는 용어만 삭제로 처리 — 없으면 '워치에 없음' 응답으로.
    // (클라이언트 삭제는 no-op인데 "뺐어"라고 거짓 보고하는 것 방지)
    const watched = (opts.watchTerms || []).some((w) => String(w).toLowerCase() === String(term).toLowerCase());
    return watched ? { type: "watch_remove", term } : { type: "watch_absent", term };
  }
  if (CMD_WATCH_ADD.test(msg)) {
    const term = extractCommandTerm(msg, aliasGroups, "watch_add", opts);
    return term ? { type: "watch_add", term } : null;
  }
  if (CMD_PROFILE.test(msg)) {
    const term = extractCommandTerm(msg, aliasGroups, "profile_open", opts);
    return term ? { type: "profile_open", term } : null;
  }
  const feed = detectFeedFilter(msg); // 마지막 순서 — 브리프/프로필 등 구체 명령이 우선
  if (feed) return feed;
  return null;
}

// feed_filter 면(facet)을 사람이 읽는 라벨로 — 응답 문구와 클라 표시에 공용
export function feedFilterLabel(cmd) {
  const regionName = { CN: "중국", US: "미국", NA: "북미", KR: "한국", EU: "유럽", JP: "일본", GL: "글로벌" };
  const parts = [];
  if (cmd.watch) parts.push("내워치");
  if (cmd.region) parts.push(regionName[cmd.region] || cmd.region);
  if (cmd.signal) parts.push(String(cmd.signal).toUpperCase());
  if (cmd.range) parts.push(`최근 ${cmd.range}일`);
  return parts.join(" · ");
}

// 반말 확인 응답 + 후속 제안 (제안 라벨 자체가 다시 명령으로 감지되는 체인)
export function appCommandResponse(cmd) {
  const t = cmd.term || "";
  if (cmd.type === "watch_add") {
    return {
      answer: `${t}, 내워치에 추가할게. NEWS 탭 ★ 내워치에서 모아볼 수 있고, 새 카드가 오면 배지로 알려줄게.`,
      suggestions: [
        { label: `${t} 프로필 보여줘` },
        { label: `${t} 최근 소식 알려줘`, hint_action: "new_query", hint_topic: "news" },
        { label: "주간 브리프 보여줘" },
      ],
    };
  }
  if (cmd.type === "watch_remove") {
    return {
      answer: `${t}, 워치에서 뺄게. 다시 보고 싶으면 언제든 추가해달라고 해.`,
      suggestions: [
        { label: `${t} 워치에 다시 추가해줘` },
        { label: "오늘 핵심 카드", hint_action: "new_query", hint_topic: "news" },
      ],
    };
  }
  if (cmd.type === "watch_absent") {
    // 워치에 없던 용어 삭제 요청 — 실제 변화 없음을 정직하게 알리고 추가를 제안
    return {
      answer: `${t}는 지금 내워치에 없어서 뺄 게 없었어. 넣어둘까?`,
      suggestions: [
        { label: `${t} 워치에 추가해줘` },
        { label: `${t} 프로필 보여줘` },
      ],
    };
  }
  if (cmd.type === "profile_open") {
    return {
      answer: `${t} 프로필 열게 — NEWS 탭으로 이동할게. 활동 통계랑 타임라인, 그 범위 브리프까지 볼 수 있어.`,
      suggestions: [
        { label: `${t} 최근 소식 알려줘`, hint_action: "new_query", hint_topic: "news" },
        { label: `${t} 워치에 추가해줘` },
      ],
    };
  }
  if (cmd.type === "brief_now") {
    const periodLabel = cmd.month ? monthKo(cmd.month) : cmd.period === "monthly" ? "월간" : "주간";
    const windowLabel = cmd.month ? `${monthKo(cmd.month)} 한 달` : cmd.period === "monthly" ? "최근 30일" : "최근 7일";
    const groupText = cmd.group === "region" ? " 지역별로 묶어서 정리할게." : "";
    const scopeText = cmd.scope === "all" ? `${windowLabel} 전체 카드(워치가 비어 있어서 전체 기준이야)` : `${windowLabel} 내워치 카드`;
    return {
      answer: `응, 지금 ${periodLabel} 브리프 만들게.${groupText} ${scopeText}를 모아 정리하는 데 수십 초 걸려 — NEWS 📮 선반 열어놓을 테니 완성되면 맨 위에 꽂아둘게.`,
      suggestions: [
        // 달력월을 만들었으면 다음 행동은 '지역별 변형'이나 '이전 달' — 발견 가능성을 칩으로
        cmd.month && cmd.group !== "region"
          ? { label: `${monthKo(cmd.month).replace(/^\d{4}년 /, "")} 지역별 브리프 만들어줘` }
          : { label: cmd.period === "monthly" ? "월간 브리프 보여줘" : "주간 브리프 보여줘" },
        { label: cmd.scope === "all" ? "CATL 워치에 추가해줘" : "내워치 관련 최근 소식 알려줘", hint_action: cmd.scope === "all" ? undefined : "new_query", hint_topic: cmd.scope === "all" ? undefined : "news" },
      ],
    };
  }
  if (cmd.type === "brief_no_material") {
    const windowLabel = cmd.month ? `${monthKo(cmd.month)}에는` : cmd.period === "monthly" ? "최근 30일 사이" : "최근 7일 사이";
    const scopeText = cmd.scope === "all" ? "전체 카드가" : "내워치에 걸린 카드가";
    return {
      answer: `${windowLabel} ${scopeText} 2장이 안 돼서 이번엔 브리프감이 부족해. ${cmd.month ? "다른 달로 해보거나, " : ""}${cmd.scope === "all" ? "새 카드가 쌓이면" : "워치를 조금 넓히거나, 새 카드가 쌓이면"} 다시 말해줘.`,
      suggestions: [
        { label: "내워치 관련 최근 소식 알려줘", hint_action: "new_query", hint_topic: "news" },
        { label: "오늘 핵심 카드", hint_action: "new_query", hint_topic: "news" },
      ],
    };
  }
  if (cmd.type === "feed_filter") {
    const label = feedFilterLabel(cmd);
    return {
      answer: label ? `응, 피드를 ${label}로 맞춰서 열게.` : "응, 피드 열어줄게.",
      suggestions: [
        { label: "내워치 카드만 보여줘" },
        { label: "오늘 핵심 카드", hint_action: "new_query", hint_topic: "news" },
      ],
    };
  }
  // weekly_show — period가 있으면 그 기간의 최신호를 여는 요청(문구도 기간을 그대로 반영)
  const showLabel = cmd.month ? monthKo(cmd.month) : cmd.period === "monthly" ? "월간" : cmd.period === "weekly" ? "주간" : "";
  if (cmd.reason === "recent_brief") {
    return {
      answer: `방금 만든 ${showLabel ? `${showLabel} ` : ""}브리프가 있어 — 새로 만드는 대신 바로 보여줄게. 다시 뽑고 싶으면 10분쯤 뒤에 말해줘.`,
      suggestions: [
        { label: "내워치 관련 최근 소식 알려줘", hint_action: "new_query", hint_topic: "news" },
      ],
    };
  }
  // 미발행 시 안내는 기간별로 갈린다 — 패시브 생성(runWeeklyBrief)은 period 없이 호출돼
  // '주간'만 만든다. 월간·달력월은 오직 명시 발행 명령·워치룸 버튼으로만 생긴다. 여기에
  // "다음 접속 때 자동으로 만들어져"라고 하면 오지 않을 자동 발행을 약속하는 셈이라 거짓말이 된다.
  if (cmd.month) {
    const shortMonth = monthKo(cmd.month).replace(/^\d{4}년 /, "");
    return {
      answer: `${monthKo(cmd.month)} 브리프 열어줄게 — NEWS 탭으로 이동할게. 그 달 호수가 아직 없으면 '${shortMonth} 브리프 만들어줘'라고 해주면 바로 만들게.`,
      suggestions: [
        { label: `${shortMonth} 브리프 만들어줘` },
        { label: "오늘 핵심 카드", hint_action: "new_query", hint_topic: "news" },
      ],
    };
  }
  if (cmd.period === "monthly") {
    return {
      answer: "월간 브리프 열어줄게 — NEWS 탭으로 이동할게. 월간은 자동 발행이 없어서, 아직 없으면 '월간 브리프 만들어줘'라고 해주면 바로 만들게.",
      suggestions: [
        { label: "월간 브리프 만들어줘" },
        { label: "오늘 핵심 카드", hint_action: "new_query", hint_topic: "news" },
      ],
    };
  }
  return {
    answer: `${showLabel || "최신"} 브리프 열어줄게 — NEWS 탭으로 이동할게. 아직 발행된 게 없으면 다음 접속 때 자동으로 만들어져.`,
    suggestions: [
      { label: "오늘 핵심 카드", hint_action: "new_query", hint_topic: "news" },
    ],
  };
}
