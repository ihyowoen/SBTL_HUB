// ============================================================================
// Layer 1: parseRequest — input → { action, topic, scope, rawMessage }
// ============================================================================
// Phase 2 신규. 기존 intent.js 대체.
//
// 3축 모델:
//   Axis A (action):  new_query | rephrase | analyze_card | follow_up
//   Axis B (topic):   faq_concept | news | policy | comparison | general | null
//   Axis C (scope):   region, date, entity (scope.js 재사용)
//
// 설계 원칙:
// - Frontend hint 최우선 존중 (suggestion 버튼에서 hint_action 오면 그대로 action 확정)
//   → U3 (Suggestion self-feeding) 해결 기반
// - 그 외는 message + context 기반 rule classify
// - 기존 intent.js의 D5/D7/D9 결함 해소:
//   · "왜 중요/의미/영향" → analyze_card (카드 컨텍스트 있을 때)
//   · "더 쉽게/짧게/예시로" → rephrase (직전 답변 있을 때)
//   · "방금 그/관련 더" → follow_up (root_turn 기반으로만 의미 있음)
//   · "feoc" 같은 키워드 중복 매치 (topic에서 단일 결정)
// ============================================================================

import { extractScope } from "./scope.js";

// ─── Topic 감지 regex (상호배타 우선순위) ──────────────────────────────────
// 우선순위: policy/comparison/news가 faq_concept보다 강함.
// "미국 정책 알려줘" 같은 조합에서 "알려줘"가 아닌 "정책"을 signal로 채택해야 함.
// faq_concept은 "뭐야/란/정의/개념" 같은 순수 개념 질의 + 짧은 질의 전제.
const TOPIC_PATTERNS = [
  {
    topic: "comparison",
    rx: /(비교|차이|vs|대비|어떤\s*게|뭐가\s*더|vs\.)/,
  },
  {
    topic: "policy",
    // regulatory·정책·일정 질의 (FAQ 개념어 feoc/ira 제거 — parseRequest에서 faq 키워드 사전 평가로 별도 처리)
    rx: /(정책|규제|시행|법안|언제|예정|일정|스케줄|battery\s*passport|meti|gx|macr|section\s*301)/,
  },
  {
    topic: "news",
    rx: /(최신|뉴스|소식|현황|지금|오늘|어제|그제|내일|모레|최근|이번|기사)/,
  },
  {
    topic: "faq_concept",
    // 순수 개념 질의 signal만. "알려줘/쉽게" 같은 generic request 제거 (다른 topic과 충돌).
    rx: /(뭐야|뭔가|뭔지|뭐지|무엇|란|이란|무슨\s*뜻|정의|개념)/,
  },
];

// Action hint regex (frontend hint 없을 때만 사용)
const RX_REPHRASE = /(다시\s*설명|더\s*쉽게|조금\s*더\s*쉽게|짧게|한\s*줄|한줄|예시로|초등학생|풀어서|쉽게\s*설명)/;
const RX_ANALYZE_CARD = /(왜\s*중요|중요한\s*이유|무슨\s*의미|파급|영향|why\s*important|심층|해설|이\s*카드|그\s*카드|저\s*카드|첫\s*번째|두\s*번째|세\s*번째|네\s*번째|1번|2번|3번|4번)/;
const RX_FOLLOW_UP = /(방금|직전|아까|관련해|관련.*더|중에서|중에\s|더\s*찾|더\s*보여|그\s*기사|다른\s*카드|관련\s*카드)/;

const VALID_ACTIONS = new Set(["new_query", "rephrase", "analyze_card", "follow_up"]);
const VALID_TOPICS = new Set(["faq_concept", "news", "policy", "comparison", "general"]);

function detectTopic(lowerMsg) {
  for (const { topic, rx } of TOPIC_PATTERNS) {
    if (rx.test(lowerMsg)) return topic;
  }
  return "general";
}

// FAQ 키워드 매칭이 성공할지 message 레벨에서 사전 평가.
// faq.json의 키워드 중 하나라도 message에 있으면 faq_concept으로 상향.
function hasFaqKeyword(lowerMsg, faq = []) {
  for (const f of faq) {
    const keys = f?.k || [];
    for (const k of keys) {
      const kl = String(k || "").toLowerCase();
      if (kl && lowerMsg.includes(kl)) return true;
    }
  }
  return false;
}

function detectActionFromRules({ lowerMsg, hasLastTurn, hasCardContext }) {
  // rephrase — 직전 답변이 있어야 의미 있음
  if (RX_REPHRASE.test(lowerMsg)) {
    return hasLastTurn ? "rephrase" : "new_query";
  }
  // analyze_card — 카드 컨텍스트(selected or last_turn.cards[0])가 있어야 의미 있음
  if (RX_ANALYZE_CARD.test(lowerMsg)) {
    return hasCardContext ? "analyze_card" : "new_query";
  }
  // follow_up — 직전 턴이 있어야 의미 있음
  if (RX_FOLLOW_UP.test(lowerMsg)) {
    return hasLastTurn ? "follow_up" : "new_query";
  }
  return "new_query";
}

/**
 * @param {object} input
 * @param {string} input.message
 * @param {object} [input.context]      ChatContext (신규 protocol)
 * @param {object} [input.hint]         { action?, topic? } — frontend suggestion button에서 전달
 * @param {object} [input.data]         { faq } — faq 키워드 매칭 위해 선택적 주입
 * @returns {{ action, topic, scope, rawMessage, _reasons }}
 */
export function parseRequest({ message, context = {}, hint = {}, data = {} } = {}) {
  const rawMessage = String(message || "").trim();
  const lowerMsg = rawMessage.toLowerCase();

  const lastTurn = context?.last_turn || null;
  const rootTurn = context?.root_turn || null;
  const hasLastTurn = !!(lastTurn && (lastTurn.answer_text || (lastTurn.cards || []).length));
  const hasCardContext = !!(context?.selected_item_id || (lastTurn?.cards || []).length);

  // 1) Frontend hint 우선
  const hintAction = VALID_ACTIONS.has(hint?.action) ? hint.action : null;
  const hintTopic = VALID_TOPICS.has(hint?.topic) ? hint.topic : null;

  // 2) Action 결정
  let action = hintAction;
  const reasons = [];
  if (action) {
    reasons.push(`action_from_hint:${action}`);
    // hint가 왔지만 필수 context 부재면 new_query로 downgrade
    if (action === "rephrase" && !hasLastTurn) {
      action = "new_query";
      reasons.push("rephrase_downgraded_no_last_turn");
    } else if (action === "analyze_card" && !hasCardContext) {
      action = "new_query";
      reasons.push("analyze_card_downgraded_no_card_context");
    } else if (action === "follow_up" && !hasLastTurn) {
      action = "new_query";
      reasons.push("follow_up_downgraded_no_last_turn");
    }
  } else {
    action = detectActionFromRules({ lowerMsg, hasLastTurn, hasCardContext });
    reasons.push(`action_from_rules:${action}`);
  }

  // 3) Topic 결정
  let topic;
  if (hintTopic) {
    topic = hintTopic;
    reasons.push(`topic_from_hint:${topic}`);
  } else if (action === "follow_up" && rootTurn?.topic && VALID_TOPICS.has(rootTurn.topic)) {
    // follow_up은 root_turn.topic 계승 (D11 해결)
    topic = rootTurn.topic;
    reasons.push(`topic_inherited_from_root:${topic}`);
  } else if (action === "rephrase" && lastTurn?.topic && VALID_TOPICS.has(lastTurn.topic)) {
    // rephrase는 last_turn.topic 계승 (답변 재작성이므로)
    topic = lastTurn.topic;
    reasons.push(`topic_inherited_from_last:${topic}`);
  } else if (action === "analyze_card") {
    // analyze_card는 항상 단일 카드 분석 — topic 무관, news로 고정 (LLM prompt 선택용)
    topic = "news";
    reasons.push("topic_fixed_analyze_card:news");
  } else {
    // rule-based topic
    topic = detectTopic(lowerMsg);
    // 짧은 개념어 질의인데 faq.json 키워드 매치되면 faq_concept로 상향
    if (topic === "general" && rawMessage.length <= 30 && hasFaqKeyword(lowerMsg, data?.faq)) {
      topic = "faq_concept";
      reasons.push("topic_upgraded_faq_keyword_match");
    } else if (topic !== "faq_concept" && hasFaqKeyword(lowerMsg, data?.faq) && rawMessage.length <= 20) {
      // "FEOC 뭐야" 같은 짧은 질의가 policy regex에 걸려도 faq_concept 우선
      topic = "faq_concept";
      reasons.push("topic_overridden_faq_keyword_short_query");
    } else {
      reasons.push(`topic_from_rules:${topic}`);
    }
  }

  // 4) Scope 추출 (기존 scope.js 재사용)
  const scope = extractScope(rawMessage, {
    // 신규 ChatContext.region/date를 기존 scope.js 시그니처에 맞춤
    region: context?.region || null,
    date: context?.date || null,
  });

  return {
    action,
    topic,
    scope,
    rawMessage,
    _reasons: reasons,
  };
}
