// 강차장 브리핑(R18) — 접속하면 앱이 먼저 말을 거는 제안 카드의 문장 구성기.
//
// 설계 원칙(사용자 통찰: "사람들은 처음엔 능동적이지 않다 — 제안을 계속 받고
// '생각보다 괜찮네?'를 느껴야 능동적으로 쓰기 시작한다"):
//  ① 보고 금지, 전부 제안 — 모든 줄에 한 탭 행동(cmd)이 붙는다. 행동 없는 정보
//     (카드 증가 수 등)는 헤더의 양념일 뿐, 그것만으로는 카드를 띄우지 않는다.
//  ② 약한 제안은 침묵보다 나쁘다 — 개인화 근거(워치·핀·브리프 상태) 있는 줄만,
//     최대 3줄. 내보낼 게 없으면 null(카드 숨김). 채움 제안은 무시를 학습시킨다.
//  ③ 콜드스타트 우선 — 워치가 없어도 첫날부터 제안이 간다(오늘의 TOP + 워치 등록).
//
// 순수·결정적: Date/난수 없음(pinboard 규약과 동일) — 시간·데이터는 전부 입력.
// cmd는 명령 버스(executeAppCommand) 객체 그대로거나 {type:"nav",tab}(렌더러가 onNav로).

// 표시용 제목 — 부제(" — " 뒤)만 떼고 원제목은 통째로 보여준다(중간 절단 "연 6.…"이
// 거슬린다는 사용자 지적 — HTML 흐름 텍스트라 줄바꿈이 자연스럽다). 극단적으로 길 때만
// 단어 경계에서 자른다(숫자·단어 중간 절단 금지).
export function trimKangTitle(s, n = 60) {
  const t = String(s || "").split(" — ")[0].trim();
  if (t.length <= n) return t;
  const cut = t.slice(0, n - 1);
  const sp = cut.lastIndexOf(" ");
  return (sp >= Math.ceil((n - 1) / 2) ? cut.slice(0, sp) : cut).trim() + "…";
}

// 검색 명령용 조각 — 표시용 절단(…)과 달리 원문에 없는 글자를 붙이면 부분 일치가
// 깨지므로, 반드시 원문 그대로의 접두 조각을 쓴다(E2E가 잡은 버그).
export function searchFrag(s, n = 24) {
  return String(s || "").split(" — ")[0].trim().slice(0, n).trim();
}

// 낡은 달력월호 고르기 — 같은 면(month·group·scope)당 '최신 호수만' 판단한다.
// 재발행으로 대체된 옛 호수까지 보면, 방금 재발행했는데도 옛 스냅샷 기준으로
// "N건 붙었어"를 계속 조르게 된다(Codex #190 R3). entries는 최신 우선 순서(선반 규약),
// monthCountOf(month)는 호출부가 주는 현재 풀 계산기(순수성 유지).
export function pickStaleBrief(entries, monthCountOf) {
  let best = null;
  const seenFacets = new Set();
  for (const e of Array.isArray(entries) ? entries : []) {
    if (!e || !e.month || e.group === "custom") continue;
    const scopeKey = e.terms_sig === "[]" || e.terms_sig == null ? "[]" : String(e.terms_sig);
    const facet = `${e.month}|${e.group || ""}|${scopeKey}`;
    if (seenFacets.has(facet)) continue; // 같은 면의 더 옛 호수 = 대체됨
    seenFacets.add(facet);
    if (typeof e.source_month_count !== "number") continue;
    if (scopeKey !== "[]") continue; // 전체 범위만 — 워치 범위는 풀이 달라 오발동(R15d 규약)
    const drift = monthCountOf(e.month) - e.source_month_count;
    if (drift > 0 && (!best || drift > best.drift)) best = { month: e.month, monthNum: Number(e.month.slice(5, 7)), drift, group: e.group || null };
  }
  return best;
}

// 입력(전부 호출부가 계산해 주입):
//   gapDays: null=첫 만남(이전 방문 기록 없음) | 0 | 1 | n
//   cardDelta: 지난 방문 이후 늘어난 카드 수(0이면 언급 안 함)
//   hasWatch, watchNew(미확인 수), watchTopTitle(미확인 중 최상위 제목)
//   pinFollow: { pinTitle, cardTitle } | null — 편집자 related가 저장 카드를 가리키는 새 카드
//   unreadBrief: { label, period, month, group } | null — 안 읽은 최신 호수
//   staleBrief: { monthNum, drift, month } | null — 발행 후 재료가 붙은 달력월호
//   topCard: { title } | null — 최근 7일 TOP 시그널
// 출력: { header, lines: [{ text, chip, cmd }] } | null
export function composeKangBriefing(inp) {
  const i = inp || {};
  const delta = i.cardDelta > 0 ? ` 그새 카드 ${i.cardDelta}장 들어왔어.` : "";
  const header =
    i.gapDays == null ? "처음이지? 강차장이야. 네가 없는 동안 내가 읽어둘게." :
    i.gapDays === 0 ? `또 왔네.${delta}` :
    i.gapDays === 1 ? `하루 만이네.${delta}` :
    `${i.gapDays}일 만이네.${delta}`;

  const lines = [];
  // 완료 인정(R20) — 지난 인사 이후 새로 해본 경험을 알아봐주고 다음 걸음을 잇는다
  // ("괜찮네?"의 순간을 만드는 인정 + 연결 제안). 후속 경험까지 이미 해봤으면 보드의
  // ✓가 대신 말하므로 조용히 생략. newlyDone은 호출부가 ack 스냅샷과 대조해 준다.
  const doneSet = new Set(Array.isArray(i.questsDone) ? i.questsDone : []);
  if (i.hasWatch) doneSet.add("watch_set");
  const newly = Array.isArray(i.newlyDone) ? i.newlyDone : [];
  for (const k of KANG_QUESTS) {
    if (!newly.includes(k)) continue;
    const f = ACK_FOLLOWUPS[k];
    if (!f || doneSet.has(f.follow)) continue;
    lines.push({ text: f.text, chip: f.chip, cmd: f.cmd });
    break; // 인정은 한 번에 하나만 — 줄줄이 칭찬은 금방 소음이 된다
  }
  // 우선순위: 개인화 강한 순 — 워치 > 핀 후속 > 안 읽은 브리프 > 낡은 월호
  if (i.hasWatch && i.watchNew > 0) {
    const top = i.watchTopTitle ? ` — 제일 큰 건 "${trimKangTitle(i.watchTopTitle)}"` : "";
    lines.push({
      text: `네 워치에서 새 카드 ${i.watchNew}건 걸렸어${top}.`,
      chip: "내 워치", cmd: { type: "feed_filter", watch: true },
    });
  }
  if (i.pinFollow && i.pinFollow.cardTitle) {
    lines.push({
      text: `네가 저장한 "${trimKangTitle(i.pinFollow.pinTitle, 20)}" 건, 후속 카드가 이어졌어.`,
      // 피드 검색은 제목 부분 일치 — 원문 접두 조각(searchFrag)이라 대상 카드가 반드시 걸린다
      chip: "후속 보기", cmd: { type: "feed_filter", search: searchFrag(i.pinFollow.cardTitle) },
    });
  }
  if (i.unreadBrief && i.unreadBrief.label) {
    lines.push({
      // id로 그 호수를 정확히 지목 — 면만 보내면 같은 면의 더 최신호가 대신 열리고
      // 읽음 처리도 그쪽에 붙는다(Codex #190). 면은 id 미발견 시 폴백용으로 유지.
      text: `${i.unreadBrief.label} 브리프 만들어뒀어 — 읽고 가.`,
      chip: "읽기", cmd: { type: "weekly_show", id: i.unreadBrief.id || null, period: i.unreadBrief.period || null, month: i.unreadBrief.month || null, group: i.unreadBrief.group || null },
    });
  }
  if (i.staleBrief && i.staleBrief.drift > 0) {
    lines.push({
      // group 보존 — 지역별/주제별 월호가 낡았는데 group 없이 보내면 일반 월호가 열려
      // 정작 낡은 그 호수(재발행 버튼이 있는 곳)에 못 간다(Codex #190).
      text: `${i.staleBrief.monthNum}월호에 발행 뒤 기사 ${i.staleBrief.drift}건이 더 붙었어 — 새 재료로 다시 뽑을 수 있어.`,
      chip: `${i.staleBrief.monthNum}월호`, cmd: { type: "weekly_show", period: "monthly", month: i.staleBrief.month || null, group: i.staleBrief.group || null },
    });
  }
  // 기본 제안 채움(R19b) — "말 하나밖에 안 해, 밑으로 쭉쭉 제안해야지"(사용자 지적).
  // 근거 줄 뒤에 오늘의 뉴스·워치 프로필 같은 기본 제안을 채워 최소 서너 줄을 유지한다.
  // 원칙②는 '근거 없는 채움 금지'에서 '기본 제안은 명시적으로 채움'으로 조정 —
  // 제안이 계속 와야 능동이 된다는 통찰이 우선(원칙① 전부-제안은 그대로).
  // 워치 후보 추천(R20 능동 제안) — 워치 카드들에 자주 같이 등장하는 엔티티를 한 탭
  // 등록으로 제안(동시등장 계산은 호출부, 명령 버스 watch_add 재사용). 추가하면 다음
  // 재계산에서 워치가 되어 줄이 자연 소멸 — 제안→행동→변화의 즉각 순환.
  if (i.watchSuggest && i.watchSuggest.term) {
    const n = i.watchSuggest.count > 0 ? ` (최근 한 달 ${i.watchSuggest.count}장)` : "";
    lines.push({
      text: `요즘 "${i.watchSuggest.term}" 얘기가 네 워치 카드에 자주 붙어 나와${n} — 워치에 넣을까?`,
      chip: "추가", cmd: { type: "watch_add", term: i.watchSuggest.term },
    });
  }
  const MAX_LINES = 5, FILL_TO = 4;
  // 근거 줄이 이미 인용한 카드 제목 — 채움(TOP·HIGH)이 같은 카드를 다시 권하지
  // 않게 한다(Codex #195: 워치 톱·핀 후속과의 중복까지 전부).
  const used = new Set();
  if (i.watchTopTitle) used.add(trimKangTitle(i.watchTopTitle));
  if (i.pinFollow && i.pinFollow.cardTitle) used.add(trimKangTitle(i.pinFollow.cardTitle));
  const topTrim = i.topCard && i.topCard.title ? trimKangTitle(i.topCard.title) : null;
  if (topTrim && lines.length < MAX_LINES && !used.has(topTrim)) {
    used.add(topTrim);
    lines.push({
      text: `${i.gapDays == null ? "일단 " : ""}오늘 제일 큰 건 "${topTrim}"이야.`,
      chip: "TOP", cmd: { type: "feed_filter", signal: "top" },
    });
  }
  if (i.watchProfile && i.watchProfile.term && lines.length < FILL_TO) {
    const f = i.watchProfile.fresh > 0 ? ` — 최근 7일 새 카드 ${i.watchProfile.fresh}건` : "";
    lines.push({
      text: `${i.watchProfile.term} 프로필도 열어봐${f}.`,
      chip: "프로필", cmd: { type: "profile_open", term: i.watchProfile.term },
    });
  }
  const extraTrim = i.extraCard && i.extraCard.title ? trimKangTitle(i.extraCard.title) : null;
  if (extraTrim && lines.length < FILL_TO && !used.has(extraTrim)) {
    lines.push({
      text: `"${extraTrim}"도 챙겨볼 만해.`,
      chip: "보기", cmd: { type: "feed_filter", search: searchFrag(i.extraCard.title) },
    });
  }
  // 퀘스트 보드(R19b) — 점 6개 대신 여정 전체를 '시현'한다(사용자: "퀘스트 시현을
  // 해주는 게 좋을 것 같아"): 완료는 ✓로, 미완료는 [해보기 →] 버튼으로 전부 보이게.
  // 전부 완료한 사용자에겐 보드 대신 기능 팁 로테이션 한 줄(ALL_TIPS)로 복귀.
  const dk = Math.abs(Math.trunc(i.dayKey || 0));
  const done = new Set(Array.isArray(i.questsDone) ? i.questsDone : []);
  const isDone = (k) => (k === "watch_set" ? !!i.hasWatch : done.has(k));
  const questItems = QUEST_DEFS.map((q) => ({ key: q.key, label: q.label, done: isDone(q.key), cmd: q.cmd }));
  const doneCount = questItems.filter((q) => q.done).length;
  const tip = doneCount >= QUEST_DEFS.length ? ALL_TIPS[dk % ALL_TIPS.length] : null;

  if (!lines.length && !tip && doneCount >= QUEST_DEFS.length) return null; // 원칙① — 행동 없는 인사는 안 띄운다
  return {
    header,
    lines: lines.slice(0, MAX_LINES),
    tip: tip ? { text: tip.text, chip: tip.chip, cmd: tip.cmd } : null,
    quest: { done: doneCount, total: QUEST_DEFS.length, items: questItems },
  };
}

// 퀘스트 보드 정의(R19b) — 라벨·착지 한 곳에서. 지도·빌더는 딥링크(광고한 기능을
// 실제로 연다 — Codex #193 규약), 나머지는 해당 기능이 사는 탭으로.
const QUEST_DEFS = [
  { key: "watch_set", label: "워치 등록하기", cmd: { type: "nav", tab: "watchroom" } },
  { key: "brief_read", label: "📮 브리프 읽어보기", cmd: { type: "weekly_show" } },
  { key: "map_open", label: "🧠 지도 열어보기", cmd: { type: "room_view", view: "map" } },
  { key: "builder_publish", label: "🧩 빌더로 발행해보기", cmd: { type: "room_view", view: "builder" } },
  { key: "star_save", label: "☆ 카드 저장해보기", cmd: { type: "nav", tab: "news" } },
  { key: "chat_ask", label: "상담소에 물어보기", cmd: { type: "nav", tab: "chatbot" } },
];

// 완료 인정→다음 걸음(R20) — 방금 해본 경험을 알아봐주고, 자연스럽게 이어지는 미완
// 경험 하나를 권한다(후속까지 완료면 생략 — 보드 ✓가 대신 말한다).
const ACK_FOLLOWUPS = {
  watch_set: { follow: "map_open", text: "워치 등록했더라 — 이제 🧠 지도가 네 워치로도 그려져.", chip: "지도", cmd: { type: "room_view", view: "map" } },
  map_open: { follow: "star_save", text: "🧠 지도 켜봤더라? ☆로 카드를 모으면 지도가 더 진해져.", chip: "피드", cmd: { type: "nav", tab: "news" } },
  star_save: { follow: "map_open", text: "☆ 모으기 시작했네 — 지도에서 연결로 봐봐.", chip: "지도", cmd: { type: "room_view", view: "map" } },
  brief_read: { follow: "builder_publish", text: "📮 브리프 읽었더라 — 🧩 빌더로 네 조합도 만들어봐.", chip: "빌더", cmd: { type: "room_view", view: "builder" } },
  builder_publish: { follow: "chat_ask", text: "🧩 발행까지 해봤네! 궁금한 건 상담소에 말로 물어봐.", chip: "상담소", cmd: { type: "nav", tab: "chatbot" } },
  chat_ask: { follow: "brief_read", text: "상담소 써봤더라 — 📮 브리프도 읽어봐.", chip: "브리프", cmd: { type: "weekly_show" } },
};

// 퀘스트(R19) — 핵심 여정 6개. watch_set은 워치 존재로 유도, 나머지는 questsDone으로.
export const KANG_QUESTS = ["watch_set", "brief_read", "map_open", "builder_publish", "star_save", "chat_ask"];
const QUEST_TIPS = [
  { quest: "brief_read", text: "지난 이야기들은 📮 브리프로 미리 만들어뒀어 — 월호부터 읽어봐.", chip: "브리프", cmd: { type: "weekly_show" } },
  // 지도·빌더는 딥링크(room_view) — 탭 상단이 아니라 광고한 그 기능을 실제로 연다(Codex #193)
  { quest: "map_open", text: "🧠 지도를 켜면 카드 사이 연결이 보여 — 워치만 있어도 그려져.", chip: "지도", cmd: { type: "room_view", view: "map" } },
  { quest: "builder_publish", text: "🧩 빌더로 워치·지역·주제를 골라 나만의 브리프를 짜깁어봐.", chip: "빌더", cmd: { type: "room_view", view: "builder" } },
  { quest: "star_save", text: "마음에 든 카드는 ☆로 저장해봐 — 📌 핀 보드에 모이고 지도가 진해져.", chip: "피드", cmd: { type: "nav", tab: "news" } },
  { quest: "chat_ask", text: "궁금한 건 상담소에 말로 물어봐 — '중국 ESS 최근 소식' 이런 식으로.", chip: "상담소", cmd: { type: "nav", tab: "chatbot" } },
];
const ALL_TIPS = [
  ...QUEST_TIPS,
  { text: "피드 검색에 기업 이름을 치면 별칭·한영 표기까지 묶어서 찾아줘.", chip: "피드", cmd: { type: "nav", tab: "news" } },
];
