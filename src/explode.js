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
// 시그널 가중치 — 축약형(s: "t")과 원본 스키마(signal: "top") 모두 첫 글자로 정규화
// (App sigOrder와 같은 규약, Codex #198 R2 — 전체 단어에서 전부 0이 되면 같은 주체
// 다리가 날짜로만 잘려 옛 TOP이 새 MID에 밀린다).
const sigWeight = (c) => SIG_W[String((c && (c.s || c.signal)) || "").toLowerCase()[0]] || 0;

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
    cards.filter((c) => rel.has(getCardId(c))).sort(byDateDesc).forEach((c) => push(c, "연관 — 강차장 연결"));
  }
  // ② 역방향 연결 — 자기 related로 중심을 가리키는 카드. 방향이 역이라고 다 '후속'은
  // 아니다: 편집자는 시간 양방향으로 잇는다(실데이터에 중심보다 앞선 역링크 존재 —
  // Codex #198 R3). 날짜 비교로 후행만 '후속', 선행은 사실 그대로 '앞선 연결'.
  const centerDate = String(centerCard.date || centerCard.d || "");
  cards
    .filter((c) => Array.isArray(c.related) && c.related.includes(centerId))
    .sort(byDateDesc)
    .forEach((c) => push(c, String(c.date || c.d || "") > centerDate ? "후속 — 이 카드를 이어받음" : "앞선 연결 — 이 카드를 가리킴"));
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
      .sort((a, b) => sigWeight(b) - sigWeight(a) || byDateDesc(a, b))
      .forEach((c) => push(c, "같은 주체"));
  }
  return out;
}

// 보장 에지(Codex #198 R4) — 선별이 확정한 중심↔다리 관계를 buildPinGraph에 전달할
// 형태로. 같은 주체 다리는 entity, 편집자 연결 계열(연관·후속·앞선)은 related로 —
// 범용 엔티티 억제(핀 60%+)가 선별 이유를 지워 몸통이 고아로 보이는 것을 막는다.
export function ensureCenterEdges(centerId, neighbors) {
  return (Array.isArray(neighbors) ? neighbors : []).map((n) => ({
    a: centerId,
    b: n.id,
    kind: String(n.why || "").includes("주체") ? "entity" : "related",
    label: String(n.why || "").includes("주체") ? "같은 주체" : "강차장 연결",
  }));
}

// ---- R26: related_lineage 판독 — 편집자가 '왜 이었는지'를 다리 라벨로 ----
// 실측(전수 76장): 무결성은 완벽하나 reason의 71%가 영문·파이프라인 말투라 직표시
// 불가. 타입은 한국어 사전으로 매핑하고, 서술(anchor·reason)은 '한국어가 실리고
// 내부 용어가 없는' 통과분만 인용한다 — 걸러서 라벨만 남는 쪽이 오염보다 낫다.
const LINEAGE_BRIDGE_LABEL = {
  distinct_follow_up: "후속 실행 단계",
  program_lineage: "같은 프로그램",
};
const LINEAGE_META_RE = /baseline|stage|prompt|contract|audit|lineage|schema|pipeline|metadata|screen|collision|\bQC\b/i;

// 사용자 화면에 낼 수 있는 서술인가 — 아니면 null(생략이 정답)
export function lineageDisplayText(s) {
  const txt = String(s || "").trim();
  if (!txt || !/[가-힣]/.test(txt) || LINEAGE_META_RE.test(txt)) return null;
  return txt;
}

// 다리 하나의 편집자 서사 {label, quote|null} — 없으면 null(호출부는 기존 why 유지).
// 방향 규약: lineage는 '그 링크를 기록한 카드'가 소유한다 — ①연관(중심 related→다리)은
// 중심의 lineage, ②후속·앞선(다리 related→중심)은 다리의 lineage. related_ids가 상대를
// 지목할 때만 그 관계의 서사로 인정한다(다중 링크 대비).
export function bridgeLineage(centerCard, neighbor) {
  const centerId = getCardId(centerCard);
  const nbId = neighbor && neighbor.id;
  if (!centerId || !nbId) return null;
  const owns = (card, targetId) => {
    const rl = card && card.related_lineage;
    if (!rl || typeof rl !== "object") return null;
    const ids = Array.isArray(rl.related_ids) ? rl.related_ids : (Array.isArray(card.related) ? card.related : []);
    return ids.includes(targetId) ? rl : null;
  };
  const rl = owns(centerCard, nbId) || owns(neighbor.card, centerId);
  if (!rl) return null;
  const type = String(rl.relation_type || "");
  if (type === "new_unrelated_event") return null; // 독립 판정은 다리의 서사가 아니다
  const label = LINEAGE_BRIDGE_LABEL[type] || null;
  const quote = lineageDisplayText(rl.fresh_follow_up_anchor) || lineageDisplayText(rl.reason);
  return label || quote ? { label, quote } : null;
}

// 빈 지도 판정 — '대조했고 이을 게 없다'(편집 판정)와 '아직 대조 안 됨'을 구별한다.
// 독립 판정 카드(현 lineage 보유의 88%)가 이 뱃지의 재료 — 빈 지도가 정보가 된다.
export function emptyVerdict(centerCard) {
  const rl = centerCard && centerCard.related_lineage;
  if (rl && typeof rl === "object" && String(rl.relation_type) === "new_unrelated_event") {
    return "강차장이 다 대조했어요 — 이어진 사건 없음(독립 사건 판정)";
  }
  return null;
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
