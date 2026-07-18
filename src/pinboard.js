// ============================================================================
// 📌 핀 보드 → 🧠 마인드맵 (R15)
// ★저장 카드(sbtl_bookmarks, id 보존)를 노드로, 카드 사이의 실제 연결을 에지로
// 삼아 '내가 모은 조각'이 지도가 되게 한다. 에지는 신뢰 순 3종이고 같은 쌍에는
// 가장 강한 하나만 남긴다(겹치면 지도가 실타래가 된다):
//   ① related — 편집자가 카드에 명시한 인과 연결 (최상)
//   ② entity  — 같은 주체가 두 제목에 등장 (별칭 그룹, LINK_TYPES 한정)
//   ③ theme   — 같은 주제 사전 라벨에 함께 매칭 (최약, 점선 렌더)
// 레이아웃은 결정적(난수·시각 없음): 연결 성분별로 중심(최고 차수)+링 배치 후
// 성분 상자를 행으로 팩킹한다 — 같은 입력이면 항상 같은 지도.
// ============================================================================
// .js 명시 — vite는 무확장도 풀지만 유닛(순수 node ESM)은 확장자가 필수다
import { hitBoundary, LINK_TYPES, THEME_AXIS_KEYS, customAxisCandidates } from "./briefAxes.js";
// 북마크는 getCardId(id→news_id→url→urls[0]→date-title 폴백)로 저장된다 — 역매칭도
// 같은 규약이어야 id 없는 카드(news_id/url 식별)가 보드에서 고아로 오판되지 않는다(Codex #180).
import { getCardId } from "./story/normalizeCard.js";

const idOf = (c) => c.id || c.draft_id || "";
const titleOf = (c) => String(c.title || c.T || "");

export const PIN_GRAPH_MAX_NODES = 40; // 200개 보고함 전부 그리면 라벨이 죽는다 — 최신 40
const MAX_EDGES = 120;
// 핀의 60% 이상이 걸리는 엔티티/테마는 에지로 안 쓴다 — '배터리'급 범용 매칭은
// 모든 노드를 한 덩어리로 붙여 지도의 정보량을 0으로 만든다.
const GENERIC_RATIO = 0.6;

// pins(sbtl_bookmarks 항목)를 kb.cards로 역매칭해 그래프를 만든다.
// 카드가 데이터 갱신으로 사라진 핀은 북마크의 title/date로 '고아 노드'가 된다
// (저장 자산은 데이터 교체보다 오래 산다 — 조용히 빼면 사용자의 수집이 증발).
export function buildPinGraph(pins, cards, aliasEntities) {
  const byId = new Map((cards || []).map((c) => [getCardId(c), c]));
  const nodes = (Array.isArray(pins) ? pins : []).slice(0, PIN_GRAPH_MAX_NODES).map((p) => {
    const card = byId.get(p.id) || null;
    return {
      id: p.id,
      title: card ? titleOf(card) : String(p.title || ""),
      date: String((card ? card.date || card.d : p.date) || ""),
      url: (card ? card.url || card.primaryUrl || (Array.isArray(card.urls) ? card.urls[0] : "") : p.url) || "",
      region: card ? String(card.region || card.r || "") : "",
      signal: card ? String(card.s || card.signal || "i").toLowerCase()[0] : "i",
      orphan: !card,
      card,
    };
  });
  const inBoard = new Map(nodes.map((n, i) => [n.id, i]));
  const edgeKey = (a, b) => (a < b ? `${a}|${b}` : `${b}|${a}`);
  const edges = new Map(); // key → {a, b, kind, label} — 먼저 넣은(강한) 것이 이긴다
  const addEdge = (a, b, kind, label) => {
    if (a === b) return;
    const k = edgeKey(a, b);
    if (!edges.has(k) && edges.size < MAX_EDGES) edges.set(k, { a, b, kind, label });
  };

  // ① related — 카드의 편집자 연결이 보드 안 다른 핀을 가리키면 에지
  for (const n of nodes) {
    if (!n.card) continue;
    for (const r of (Array.isArray(n.card.related) ? n.card.related : [])) {
      if (inBoard.has(r)) addEdge(n.id, r, "related", "편집자 연결");
    }
  }
  // 축 힌트 후보(R16) — 에지 dedupe(쌍당 강한 kind 하나)와 '무관하게' 그룹 멤버십을 따로
  // 기록한다: related가 같은 쌍의 entity/theme 에지를 삼켜도 힌트는 살아야 하고(Codex #185),
  // 주입 키는 canonical이 아니라 '멤버 제목 최다 히트 표기'여야 빌더의 substring 매처가
  // 실제로 그 카드들을 다시 찾는다(R6 교훈 — 소프트뱅크 제목에 SoftBank 키는 매칭 0).
  const hintCands = []; // {kind, label(표시=canonical), key(주입=최다 히트 표기), ids:Set}
  // ② entity — 별칭 그룹의 어느 표기든 제목에 등장하는 핀 쌍
  for (const [k, e] of Object.entries(aliasEntities || {})) {
    if (e && e.type && !LINK_TYPES.has(e.type)) continue;
    const name = (e && e.canonical) || k;
    const spellings = [name, ...(Array.isArray(e && e.aliases) ? e.aliases : [])].filter((s) => s && String(s).trim().length >= 2);
    const spellHits = new Map(); // 표기 → 히트 수 (주입 키 선택용)
    const hits = nodes.filter((n) => {
      const h = n.title.toLowerCase();
      let any = false;
      for (const s of spellings) {
        if (hitBoundary(String(s).toLowerCase(), h)) { spellHits.set(s, (spellHits.get(s) || 0) + 1); any = true; }
      }
      return any;
    });
    if (hits.length < 2 || hits.length > Math.max(2, Math.floor(nodes.length * GENERIC_RATIO))) continue;
    // 동률은 '긴 표기' 우선(R6 교훈) — canonical 제목엔 짧은 별칭도 항상 함께 히트해
    // 동률이 되는데(EVE Energy ⊃ EVE), 사전순으로 짧은 쪽을 고르면 워치 축의 substring
    // 매칭이 develop의 EVE 같은 오매칭을 끌어온다(Codex #185 R2). 짧은 별칭이 '더 많이'
    // 히트하면 그 표기가 실제 카드 표기이므로 그대로 선택이 정당하다.
    const bestSpelling = [...spellHits.entries()].sort((a, b) => b[1] - a[1] || String(b[0]).length - String(a[0]).length || String(a[0]).localeCompare(String(b[0])))[0]?.[0] || name;
    hintCands.push({ kind: "entity", label: name, key: bestSpelling, ids: new Set(hits.map((n) => n.id)) });
    for (let i = 0; i < hits.length; i++) for (let j = i + 1; j < hits.length; j++) addEdge(hits[i].id, hits[j].id, "entity", name);
  }
  // ③ theme — 주제 사전 매칭(제목 한정, customAxisCandidates 재사용으로 규약 단일화)
  for (const label of THEME_AXIS_KEYS) {
    const hits = customAxisCandidates(nodes.map((n) => ({ id: n.id, title: n.title })), "theme", label).map((c) => c.id);
    if (hits.length < 2 || hits.length > Math.max(2, Math.floor(nodes.length * GENERIC_RATIO))) continue;
    hintCands.push({ kind: "theme", label, key: label, ids: new Set(hits) });
    for (let i = 0; i < hits.length; i++) for (let j = i + 1; j < hits.length; j++) addEdge(hits[i], hits[j], "theme", label);
  }

  // 연결 성분 (union-find) — 성분 = 지도 위의 '이야기 덩어리'
  const parent = new Map(nodes.map((n) => [n.id, n.id]));
  const find = (x) => { while (parent.get(x) !== x) { parent.set(x, parent.get(parent.get(x))); x = parent.get(x); } return x; };
  for (const e of edges.values()) { const a = find(e.a), b = find(e.b); if (a !== b) parent.set(a, b); }
  const compOf = new Map();
  for (const n of nodes) {
    const root = find(n.id);
    if (!compOf.has(root)) compOf.set(root, []);
    compOf.get(root).push(n.id);
  }
  const degree = new Map(nodes.map((n) => [n.id, 0]));
  for (const e of edges.values()) { degree.set(e.a, (degree.get(e.a) || 0) + 1); degree.set(e.b, (degree.get(e.b) || 0) + 1); }
  // 성분 라벨 + 축 힌트(R16) — 힌트는 에지가 아니라 '후보 그룹과 성분 멤버의 교집합'으로
  // 센다: 에지는 쌍당 강한 kind 하나만 남기므로(related 우선) 같은 쌍의 entity/theme 근거가
  // 에지에서 지워질 수 있지만, 그룹 멤버십은 그와 무관한 사실이다(Codex #185). 이 힌트가
  // '이 묶음으로 브리프 만들기'의 빌더 spec 재료: entity → 워치 축(key=최다 히트 표기),
  // theme → 주제 축. related만으로 묶여 그룹 근거가 없는 성분(힌트 0)은 변환 불가가 정직.
  const components = [...compOf.values()].map((ids) => {
    const set = new Set(ids);
    const axisHints = hintCands
      .map((g) => ({ kind: g.kind, label: g.label, key: g.key, n: ids.reduce((a, id) => a + (g.ids.has(id) ? 1 : 0), 0) }))
      .filter((h) => h.n >= 2)
      .sort((x, y) => y.n - x.n || String(x.label).localeCompare(String(y.label)))
      .slice(0, 4);
    const top = axisHints[0];
    return { ids, label: ids.length > 1 ? (top ? top.label : "연결 묶음") : null, axisHints };
  }).sort((a, b) => b.ids.length - a.ids.length);

  return { nodes, edges: [...edges.values()], components, degree };
}

// 결정적 레이아웃 — 성분별 중심+링, 성분 상자 행 팩킹. width에 맞춰 좌표를 돌려준다.
export function layoutPinGraph(graph, { width = 640 } = {}) {
  const NODE_R = 15;
  const LABEL_H = 26; // 노드 아래 라벨 공간
  const PAD = 18;
  const byId = new Map(graph.nodes.map((n) => [n.id, n]));
  const boxes = graph.components.map((comp) => {
    const ids = comp.ids.slice().sort((a, b) => (graph.degree.get(b) || 0) - (graph.degree.get(a) || 0) || String(a).localeCompare(String(b)));
    if (ids.length === 1) {
      return { comp, ids, w: NODE_R * 2 + PAD * 2 + 44, h: NODE_R * 2 + LABEL_H + PAD * 2, place: () => [{ id: ids[0], dx: 0, dy: 0 }] };
    }
    const ring = ids.slice(1);
    // 링 반지름·간격은 '라벨 폭'(10자 ≈ 90px)을 감안한다 — 노드 크기만 기준으로 하면
    // 허브·좌우 노드의 라벨이 같은 높이에서 수평으로 겹쳐 글자가 깨져 보인다(실사용 보고).
    // 라벨은 방사 방향(labelAng — 링 바깥쪽)으로 배치해 구조적으로 흩어지게 한다.
    const ringR = Math.max(88, NODE_R * 2 + (ring.length * (NODE_R * 2 + 56)) / (2 * Math.PI));
    const size = (ringR + NODE_R + 44) * 2;
    return {
      comp, ids, w: size + PAD, h: size + LABEL_H + PAD,
      place: () => [
        { id: ids[0], dx: 0, dy: 0 },
        ...ring.map((id, i) => {
          const ang = (2 * Math.PI * i) / ring.length - Math.PI / 2; // 12시부터 시계방향 — 결정적
          return { id, dx: Math.cos(ang) * ringR, dy: Math.sin(ang) * ringR, labelAng: ang };
        }),
      ],
    };
  });
  // 행 팩킹 — 큰 성분부터, 행 너비 초과 시 다음 행. 성분 기하(중심·반지름·인덱스)를
  // 함께 돌려줘 렌더러가 클러스터 배경(blob)·색상 팔레트를 결정적으로 입힐 수 있게 한다.
  const placed = [];
  const comps = [];
  let x = 0, y = 0, rowH = 0, maxW = 0;
  let ci = 0;
  for (const b of boxes) {
    if (x > 0 && x + b.w > width) { x = 0; y += rowH; rowH = 0; }
    const cx = x + b.w / 2, cy = y + (b.h - LABEL_H) / 2 + PAD / 2;
    const compIndex = ci++;
    let far = 0;
    for (const p of b.place()) {
      const n = byId.get(p.id);
      const r = NODE_R + Math.min(6, (graph.degree.get(p.id) || 0) * 1.2);
      placed.push({ ...n, x: cx + p.dx, y: cy + p.dy, r, compLabel: b.comp.label, compSize: b.ids.length, compIndex, isHub: b.ids.length > 1 && p.dx === 0 && p.dy === 0, labelAng: p.labelAng ?? null });
      far = Math.max(far, Math.hypot(p.dx, p.dy) + r);
      maxW = Math.max(maxW, cx + p.dx + NODE_R + 30);
    }
    comps.push({ index: compIndex, label: b.comp.label, size: b.ids.length, cx, cy, r: far + 12, axisHints: b.comp.axisHints || [] });
    x += b.w; rowH = Math.max(rowH, b.h);
  }
  const height = y + rowH;
  const pos = new Map(placed.map((n) => [n.id, n]));
  const edges = graph.edges.map((e) => ({ ...e, x1: pos.get(e.a)?.x, y1: pos.get(e.a)?.y, x2: pos.get(e.b)?.x, y2: pos.get(e.b)?.y, compIndex: pos.get(e.a)?.compIndex ?? 0 })).filter((e) => e.x1 != null && e.x2 != null);
  return { nodes: placed, edges, comps, width: Math.max(width, Math.ceil(maxW)), height: Math.max(height, 120) };
}
