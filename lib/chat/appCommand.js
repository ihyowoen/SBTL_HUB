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
const CMD_WEEKLY = new RegExp(`주간\\s*브리프(?:을|를)?\\s*(보여|열어|볼|줘|확인)${VIEW_TAIL}`);
// 강제 발행("지금 브리프 만들어줘") — 열람(CMD_WEEKLY: 보여/열어…)과 동사가 달라 충돌 없음.
// 생성은 LLM 호출을 유발하므로 워치 변이와 같은 명령형 앵커를 적용(질문형 "만들면 뭐가 좋아?"는 검색으로).
const CMD_BRIEF_NOW = new RegExp(`(주간\\s*)?브리프(?:을|를)?\\s*(?:지금\\s*|새로\\s*|다시\\s*|하나\\s*)*(만들어|만들|생성|발행|뽑아)${IMPERATIVE_TAIL}`);
const BRIEF_RECENT_MS = 10 * 60000; // 10분 내 발행본이 있으면 재생성 대신 열람으로

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
function detectFeedFilter(msg) {
  if (!CMD_FEED.test(msg)) return null;
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
  rest = rest
    .replace(/피드|카드|뉴스|소식|필터|좁혀|보여|열어|볼래|해줘|해줄래|주세요|주라|줄래|다오|줘|만|를|을|으로|로|는|은|요|해/g, " ")
    .replace(/[.!~?？\s]+/g, "");
  if (rest.length >= 2) return null; // 엔티티 등 실질 잔여 — 검색 파이프라인으로
  return { type: "feed_filter", ...facets };
}

export function detectAppCommand(message, aliasGroups = [], opts = {}) {
  const msg = String(message || "");
  if (!msg || msg.length > 80) return null; // 명령은 짧다 — 긴 문장은 일반 질의로
  if (CMD_BRIEF_NOW.test(msg)) {
    // 강제 발행은 LLM 호출 + 보관함 변이 — 정직 게이팅 3분기(빈 워치/재료 부족/방금 발행).
    const wt = opts.watchTerms || [];
    if (!wt.length) return { type: "brief_empty_watch" };
    const lastAt = Number(opts.lastBriefAt || 0);
    if (lastAt && Date.now() - lastAt < BRIEF_RECENT_MS) return { type: "weekly_show", reason: "recent_brief" };
    if (countRecentWatchMatches(opts.cards || [], wt, 7) < 2) return { type: "brief_no_material" };
    return { type: "brief_now" };
  }
  if (CMD_WEEKLY.test(msg)) return { type: "weekly_show" };
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
    return {
      answer: "응, 지금 만들게. 최근 7일 내워치 카드를 모아 정리하는 데 수십 초 걸려 — NEWS 📮 선반 열어놓을 테니 완성되면 맨 위에 꽂아둘게.",
      suggestions: [
        { label: "주간 브리프 보여줘" },
        { label: "내워치 관련 최근 소식 알려줘", hint_action: "new_query", hint_topic: "news" },
      ],
    };
  }
  if (cmd.type === "brief_empty_watch") {
    // 재료(워치) 없음 — 만들겠다고 거짓 약속하지 않고 등록을 안내
    return {
      answer: "지금 내워치가 비어 있어서 브리프 재료가 없어. 먼저 관심 기업이나 키워드를 등록해봐 — 등록되면 매주 자동으로도 만들어줘.",
      suggestions: [
        { label: "CATL 워치에 추가해줘" },
        { label: "오늘 핵심 카드", hint_action: "new_query", hint_topic: "news" },
      ],
    };
  }
  if (cmd.type === "brief_no_material") {
    return {
      answer: "최근 7일 사이 내워치에 걸린 카드가 2장이 안 돼서 이번엔 브리프감이 부족해. 워치를 조금 넓히거나, 새 카드가 쌓이면 다시 말해줘.",
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
  // weekly_show
  if (cmd.reason === "recent_brief") {
    return {
      answer: "방금 만든 브리프가 있어 — 새로 만드는 대신 바로 보여줄게. 다시 뽑고 싶으면 10분쯤 뒤에 말해줘.",
      suggestions: [
        { label: "내워치 관련 최근 소식 알려줘", hint_action: "new_query", hint_topic: "news" },
      ],
    };
  }
  return {
    answer: "주간 브리프 열어줄게 — NEWS 탭으로 이동할게. 아직 발행된 게 없으면 워치 등록 후 다음 접속 때 자동으로 만들어져.",
    suggestions: [
      { label: "오늘 핵심 카드", hint_action: "new_query", hint_topic: "news" },
    ],
  };
}
