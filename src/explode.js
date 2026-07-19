// 뉴스 분해(R22) — 카드 하나를 몸통 삼아 거미다리(이웃)를 고르는 순수 선별기.
//
// 이웃 3종(신뢰 순):
//  ① 연관 — 중심 카드의 related가 가리키는 카드(편집자 정방향 연결)
//  ② 후속 — 자기 related로 '중심 카드를' 가리키는 뒤 카드(편집자 역방향 = 이어받음)
//  ③ 같은 주체 — 중심 '제목'에 등장한 별칭 그룹이 제목에 함께 등장(경계 매칭 —
//     본문 매칭은 노이즈, R10 주체 축 규약)
// 지도 자체(에지 종류·클러스터·배치)는 pinboard.js가 이 결과를 받아 그린다 — 여기는
// '어떤 카드를 판에 올릴지'만 정한다. 재중심(가지가 몸통이 되는 것)은 호출부가 이
// 함수를 새 중심으로 다시 부르면 된다. 순수·결정적: Date/난수 없음.
import { getCardId } from "./story/normalizeCard.js";
import { hitBoundary } from "./briefAxes.js";

const SIG_W = { t: 2, h: 1 };

// '같은 주체' 자격이 있는 별칭 타입 — 기업·기관·인물 계열만(R8b 엔티티 링크 화이트리스트
// 규약, Codex #198). 지명(place)·기술 용어(tech_term)·정책 용어(policy_term)는 주체가
// 아니라 소재라 다리로 쓰면 노이즈가 판을 덮는다(예: 제목의 'ESS'로 수백 장이 딸려옴).
// 타입 정보가 없는 구형(배열형) 항목은 허용(하위호환).
const SUBJECT_TYPES = new Set(["company", "company_division", "company_brand", "person", "research_org", "government_agency", "industry_org"]);

function aliasSpellings(v, key) {
  const arr = Array.isArray(v) ? v
    : v && typeof v === "object" ? [v.canonical, ...(Array.isArray(v.aliases) ? v.aliases : [])]
    : [];
  return [key, ...arr].map((s) => String(s || "")).filter(Boolean);
}

// 반환: [{ id, card, why }] — why는 상세 패널의 '어떻게 이어졌나' 표기용
// (지도 에지는 pinboard가 자체 계산 — 방향(후속) 정보만 여기서 보존된다)
export function pickNeighbors(centerCard, cards, aliasMap, { cap = 14 } = {}) {
  const centerId = getCardId(centerCard);
  if (!centerId || !Array.isArray(cards)) return [];
  const seen = new Set([centerId]);
  const out = [];
  const push = (c, why) => {
    if (out.length >= cap) return;
    const id = getCardId(c);
    if (!id || seen.has(id)) return;
    seen.add(id);
    out.push({ id, card: c, why });
  };
  const rel = new Set(Array.isArray(centerCard.related) ? centerCard.related : []);
  const byDateDesc = (a, b) => String(b.date || b.d || "").localeCompare(String(a.date || a.d || "")) || String(getCardId(a)).localeCompare(String(getCardId(b)));

  // ① 연관(정방향) — 편집자 연결이 가장 강한 다리
  if (rel.size) {
    cards.filter((c) => rel.has(getCardId(c))).sort(byDateDesc).forEach((c) => push(c, "연관 — 편집자 연결"));
  }
  // ② 후속(역방향) — 뒤 카드가 이 카드를 이어받음
  cards
    .filter((c) => Array.isArray(c.related) && c.related.includes(centerId))
    .sort(byDateDesc)
    .forEach((c) => push(c, "후속 — 이 카드를 이어받음"));
  // ③ 같은 주체 — 중심 제목의 별칭 그룹 공유(경계), 시그널·최신순으로 남은 자리 채움
  const title = String(centerCard.T || centerCard.title || "").toLowerCase();
  const groups = [];
  for (const [key, v] of Object.entries(aliasMap || {})) {
    const type = v && typeof v === "object" && !Array.isArray(v) ? v.type : null;
    if (type && !SUBJECT_TYPES.has(type)) continue; // 지명·기술·정책 용어는 주체가 아니다
    const spells = aliasSpellings(v, key);
    if (spells.some((s) => hitBoundary(s, title))) groups.push(spells);
  }
  if (groups.length && out.length < cap) {
    cards
      .filter((c) => {
        const id = getCardId(c);
        if (!id || seen.has(id)) return false;
        const tt = String(c.T || c.title || "").toLowerCase();
        return groups.some((sp) => sp.some((s) => hitBoundary(s, tt)));
      })
      .sort((a, b) => (SIG_W[a.s] || 0) < (SIG_W[b.s] || 0) ? 1 : (SIG_W[a.s] || 0) > (SIG_W[b.s] || 0) ? -1 : byDateDesc(a, b))
      .forEach((c) => push(c, "같은 주체"));
  }
  return out;
}

// 지도 입력(핀 배열) — 중심을 맨 앞에, pinboard 핀 스키마({id,title,date,url})로
export function explodePins(centerCard, neighbors) {
  const toPin = (c) => ({
    id: getCardId(c),
    title: String(c.T || c.title || ""),
    date: String(c.date || c.d || ""),
    url: String(c.url || c.primaryUrl || (Array.isArray(c.urls) ? c.urls[0] : "") || ""),
  });
  return [toPin(centerCard), ...neighbors.map((n) => toPin(n.card))];
}
