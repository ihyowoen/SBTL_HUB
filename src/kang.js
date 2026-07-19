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
  // 개인화 줄이 없을 때만 TOP 폴백(콜드스타트·조용한 날) — 첫 만남엔 항상 보여줘
  // '괜찮네?'의 첫 경험을 만든다.
  if ((lines.length === 0 || i.gapDays == null) && i.topCard && i.topCard.title) {
    lines.push({
      text: `${i.gapDays == null ? "일단 " : ""}오늘 제일 큰 건 "${trimKangTitle(i.topCard.title)}"이야.`,
      chip: "TOP", cmd: { type: "feed_filter", signal: "top" },
    });
  }
  // 팁 한 줄(R18c) — 인사의 본체는 뉴스+기본 제안이고, 그 밑에 앱을 더 똑똑하게 쓰는
  // 길(브리프·지도·빌더·상담소·검색)로 이끄는 팁을 하루 하나씩 곁들인다(사용자 방향:
  // "여기선 뉴스를 던져주고 기본 제안을 줘 + 기능으로 이끄는 팁 하나"). 워치가 비면
  // 워치 팁 고정(가장 가치 있는 다음 걸음 — 고르기 칩은 브리핑룸에 상시 거주), 있으면
  // dayKey로 결정적 로테이션. 강요 없음 — 버튼 하나짜리 초대일 뿐.
  const TIPS = [
    { text: "지난 이야기들은 📮 브리프로 미리 만들어뒀어 — 월호부터 읽어봐.", chip: "브리프", cmd: { type: "weekly_show" } },
    { text: "🧠 지도를 켜면 카드 사이 연결이 보여 — 워치만 있어도 그려져.", chip: "지도", cmd: { type: "nav", tab: "watchroom" } },
    { text: "🧩 빌더로 워치·지역·주제를 골라 나만의 브리프를 짜깁을 수 있어.", chip: "빌더", cmd: { type: "nav", tab: "watchroom" } },
    { text: "궁금한 건 상담소에 말로 물어봐 — '중국 ESS 최근 소식' 이런 식으로.", chip: "상담소", cmd: { type: "nav", tab: "chatbot" } },
    { text: "피드 검색에 기업 이름을 치면 별칭·한영 표기까지 묶어서 찾아줘.", chip: "피드", cmd: { type: "nav", tab: "news" } },
  ];
  const tip = !i.hasWatch
    ? { text: "워치를 등록해두면 네 기준으로 골라줄게 — 브리핑룸에 한 탭 칩으로 만들어뒀어.", chip: "등록하러", cmd: { type: "nav", tab: "watchroom" } }
    : TIPS[Math.abs(Math.trunc(i.dayKey || 0)) % TIPS.length];

  if (!lines.length && !tip) return null; // 원칙② — 행동 없는 인사는 안 띄운다
  return { header, lines: lines.slice(0, 3), tip };
}
