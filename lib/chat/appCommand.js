// ============================================================================
// appCommand — 에이전틱 명령 감지 (규칙 기반, LLM 무관)
// ----------------------------------------------------------------------------
// "CATL 내워치에 추가해줘" 같은 앱 조작 명령을 파이프라인 앞에서 감지해
// 클라이언트가 실행할 app_command 페이로드로 단락시킨다. 규칙 기반인 이유:
// 워치 목록을 바꾸는 조작은 LLM 오분류로 실행되면 안 되고, 감지 실패 시엔
// 그냥 일반 질의로 흘러가 검색 답변이 나오므로 실패 비용이 낮다.
// ============================================================================

import { matchAliasCanonical } from "./common.js";

const CMD_WATCH_REMOVE = /(내\s*)?워치(\s*목록)?(에서)?\s*(삭제|제거|빼|지워)/;
const CMD_WATCH_ADD = /(내\s*)?워치(\s*목록)?(에|에다)?\s*(추가|등록|넣어)/;
const CMD_PROFILE = /프로필\s*(보여|열어|띄워|볼|줘)/;
const CMD_WEEKLY = /주간\s*브리프\s*(보여|열어|볼|줘|확인)/;

// 명령의 대상 용어: 별칭 맵 canonical 우선("닝더시대"→CATL), 없으면 조사 앞 명사구 캡처
function extractCommandTerm(message, aliasGroups) {
  const canonical = matchAliasCanonical(message, aliasGroups);
  if (canonical) return canonical;
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

export function detectAppCommand(message, aliasGroups = []) {
  const msg = String(message || "");
  if (!msg || msg.length > 80) return null; // 명령은 짧다 — 긴 문장은 일반 질의로
  if (CMD_WEEKLY.test(msg)) return { type: "weekly_show" };
  if (CMD_WATCH_REMOVE.test(msg)) {
    const term = extractCommandTerm(msg, aliasGroups);
    return term ? { type: "watch_remove", term } : null;
  }
  if (CMD_WATCH_ADD.test(msg)) {
    const term = extractCommandTerm(msg, aliasGroups);
    return term ? { type: "watch_add", term } : null;
  }
  if (CMD_PROFILE.test(msg)) {
    const term = extractCommandTerm(msg, aliasGroups);
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
