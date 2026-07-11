// ============================================================================
// appCommand — 에이전틱 명령 감지 (규칙 기반, LLM 무관)
// ----------------------------------------------------------------------------
// "CATL 내워치에 추가해줘" 같은 앱 조작 명령을 파이프라인 앞에서 감지해
// 클라이언트가 실행할 app_command 페이로드로 단락시킨다. 규칙 기반인 이유:
// 워치 목록을 바꾸는 조작은 LLM 오분류로 실행되면 안 되고, 감지 실패 시엔
// 그냥 일반 질의로 흘러가 검색 답변이 나오므로 실패 비용이 낮다.
// ============================================================================

import { matchAliasGroup } from "./common.js";

const CMD_WATCH_REMOVE = /(내\s*)?워치(\s*목록)?(에서)?\s*(삭제|제거|빼|지워)/;
const CMD_WATCH_ADD = /(내\s*)?워치(\s*목록)?(에|에다)?\s*(다시\s*)?(추가|등록|넣어)/; // '다시'는 재추가 제안 칩("워치에 다시 추가해줘")이 다시 명령으로 걸리게
const CMD_PROFILE = /프로필\s*(보여|열어|띄워|볼|줘)/;
const CMD_WEEKLY = /주간\s*브리프\s*(보여|열어|볼|줘|확인)/;

// App.jsx cardWatchHay와 동일 규칙 — 클라이언트가 이 term으로 substring 매칭하므로
// 여기서 같은 기준으로 세어야 표기 선택이 실제 화면 결과와 일치한다.
function cardHay(c) {
  return [c.T, c.title, c.sub, c.subtitle, c.fact, c.g, c.gate]
    .map((v) => String(v || "")).join(" ").toLowerCase();
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

// 명령의 대상 용어: 별칭 그룹 매치 시 데이터 기준 표현 선택, 없으면 조사 앞 명사구 캡처
function extractCommandTerm(message, aliasGroups, type, opts) {
  const group = matchAliasGroup(message, aliasGroups);
  if (group) return resolveGroupTerm(group, type, opts);
  const m = String(message || "").match(/^\s*(.+?)(?:을|를|도|은|는|이|가)?\s*(?:내\s*)?워치/);
  if (m && m[1]) {
    const t = m[1].replace(/["'`]/g, "").trim();
    if (t.length >= 2 && t.length <= 24) return t;
  }
  const p = String(message || "").match(/^\s*(.+?)(?:의|을|를)?\s*프로필/);
  if (p && p[1]) {
    const t = p[1].replace(/["'`]/g, "").trim();
    if (t.length >= 2 && t.length <= 24) return t;
  }
  return null;
}

export function detectAppCommand(message, aliasGroups = [], opts = {}) {
  const msg = String(message || "");
  if (!msg || msg.length > 80) return null; // 명령은 짧다 — 긴 문장은 일반 질의로
  if (CMD_WEEKLY.test(msg)) return { type: "weekly_show" };
  if (CMD_WATCH_REMOVE.test(msg)) {
    const term = extractCommandTerm(msg, aliasGroups, "watch_remove", opts);
    return term ? { type: "watch_remove", term } : null;
  }
  if (CMD_WATCH_ADD.test(msg)) {
    const term = extractCommandTerm(msg, aliasGroups, "watch_add", opts);
    return term ? { type: "watch_add", term } : null;
  }
  if (CMD_PROFILE.test(msg)) {
    const term = extractCommandTerm(msg, aliasGroups, "profile_open", opts);
    return term ? { type: "profile_open", term } : null;
  }
  return null;
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
  if (cmd.type === "profile_open") {
    return {
      answer: `${t} 프로필 열게 — NEWS 탭으로 이동할게. 활동 통계랑 타임라인, 그 범위 브리프까지 볼 수 있어.`,
      suggestions: [
        { label: `${t} 최근 소식 알려줘`, hint_action: "new_query", hint_topic: "news" },
        { label: `${t} 워치에 추가해줘` },
      ],
    };
  }
  // weekly_show
  return {
    answer: "주간 브리프 열어줄게 — NEWS 탭으로 이동할게. 아직 발행된 게 없으면 워치 등록 후 다음 접속 때 자동으로 만들어져.",
    suggestions: [
      { label: "오늘 핵심 카드", hint_action: "new_query", hint_topic: "news" },
    ],
  };
}
