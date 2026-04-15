// ============================================================================
// retrieve/policy.js — policy intent retrieval
// ============================================================================
// REGION_POLICY 템플릿 + tracker upcoming. region 없으면 빈 결과 반환
// (respond에서 반문 처리). lexical card 검색은 보조 근거로만.
// ============================================================================

import { REGION_POLICY } from "../common.js";
import { lexicalSearchCards } from "./shared.js";

const REGION_MAP = { US: "NA", KR: "KR", CN: "CN", EU: "EU", JP: "JP", GL: "GL" };

function getPolicyContext(scope = {}, tracker = { items: [] }) {
  const items = Array.isArray(tracker.items) ? tracker.items : [];
  const regionKey = scope.region ? REGION_MAP[scope.region] || scope.region : null;
  const upcoming = items
    .filter((i) => i.s === "UPCOMING" && (!regionKey || i.r === regionKey || i.r === scope.region))
    .sort((a, b) => String(a.dt || "").localeCompare(String(b.dt || "")))
    .slice(0, 4);
  return { upcoming, regionKey, totalItems: items.length };
}

export function retrievePolicy({ rawMessage, scope, data }) {
  const region = scope?.region || null;
  const policyTemplate = region ? REGION_POLICY[region] || null : null;
  const policyContext = getPolicyContext(scope || {}, data?.tracker);
  const cards = lexicalSearchCards(data?.cards || [], rawMessage, 4, scope || {});

  return {
    source: "policy",
    cards,
    policy: {
      ...policyContext,
      template: policyTemplate,
      region,
    },
    _reasons: [
      `policy_region:${region || "none"}`,
      `policy_template:${!!policyTemplate}`,
      `policy_upcoming:${policyContext.upcoming.length}`,
      `policy_cards:${cards.length}`,
    ],
  };
}
