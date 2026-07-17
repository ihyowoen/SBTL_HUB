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
  const byId = new Map((cards || []).map((c) => [idOf(c), c]));
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
  // ② entity — 별칭 그룹의 어느 표기든 제목에 등장하는 핀 쌍
  for (const [k, e] of Object.entries(aliasEntities || {})) {
    if (e && e.type && !LINK_TYPES.has(e.type)) continue;
    const name = (e && e.canonical) || k;
    const spellings = [name, ...(Array.isArray(e && e.aliases) ? e.aliases : [])].filter((s) => s && String(s).trim().length >= 2);
    const hits = nodes.filter((n) => { const h = n.title.toLowerCase(); return spellings.some((s) => hitBoundary(String(s).toLowerCase(), h)); });
    if (hits.length < 2 || hits.length > Math.max(2, Math.floor(nodes.length * GENERIC_RATIO))) continue;
    for (let i = 0; i < hits.length; i++) for (let j = i + 1; j < hits.length; j++) addEdge(hits[i].id, hits[j].id, "entity", name);
  }
  // ③ theme — 주제 사전 매칭(제목 한정, customAxisCandidates 재사용으로 규약 단일화)
  for (const label of THEME_AXIS_KEYS) {
    const hits = customAxisCandidates(nodes.map((n) => ({ id: n.id, title: n.title })), "theme", label).map((c) => c.id);
    if (hits.length < 2 || hits.length > Math.max(2, Math.floor(nodes.length * GENERIC_RATIO))) continue;
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
  // 성분 라벨 — 성분 내부 에지에서 최다 등장 라벨(엔티티·테마), 없으면 '연결 묶음'
  const components = [...compOf.values()].map((ids) => {
    const set = new Set(ids);
    const cnt = new Map();
    for (const e of edges.values()) {
      if (!set.has(e.a) || e.kind === "related") continue;
      cnt.set(e.label, (cnt.get(e.label) || 0) + 1);
    }
    const top = [...cnt.entries()].sort((x, y) => y[1] - x[1])[0];
    return { ids, label: ids.length > 1 ? (top ? top[0] : "연결 묶음") : null };
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
    const ringR = Math.max(56, NODE_R * 2 + (ring.length * (NODE_R * 2 + 26)) / (2 * Math.PI));
    const size = (ringR + NODE_R + 30) * 2;
    return {
      comp, ids, w: size + PAD, h: size + LABEL_H + PAD,
      place: () => [
        { id: ids[0], dx: 0, dy: 0 },
        ...ring.map((id, i) => {
          const ang = (2 * Math.PI * i) / ring.length - Math.PI / 2; // 12시부터 시계방향 — 결정적
          return { id, dx: Math.cos(ang) * ringR, dy: Math.sin(ang) * ringR };
        }),
      ],
    };
  });
  // 행 팩킹 — 큰 성분부터, 행 너비 초과 시 다음 행
  const placed = [];
  let x = 0, y = 0, rowH = 0, maxW = 0;
  for (const b of boxes) {
    if (x > 0 && x + b.w > width) { x = 0; y += rowH; rowH = 0; }
    const cx = x + b.w / 2, cy = y + (b.h - LABEL_H) / 2 + PAD / 2;
    for (const p of b.place()) {
      const n = byId.get(p.id);
      placed.push({ ...n, x: cx + p.dx, y: cy + p.dy, r: NODE_R + Math.min(6, (graph.degree.get(p.id) || 0) * 1.2), compLabel: b.comp.label, compSize: b.ids.length, isHub: b.ids.length > 1 && p.dx === 0 && p.dy === 0 });
      maxW = Math.max(maxW, cx + p.dx + NODE_R + 30);
    }
    x += b.w; rowH = Math.max(rowH, b.h);
  }
  const height = y + rowH;
  const pos = new Map(placed.map((n) => [n.id, n]));
  const edges = graph.edges.map((e) => ({ ...e, x1: pos.get(e.a)?.x, y1: pos.get(e.a)?.y, x2: pos.get(e.b)?.x, y2: pos.get(e.b)?.y })).filter((e) => e.x1 != null && e.x2 != null);
  return { nodes: placed, edges, width: Math.max(width, Math.ceil(maxW)), height: Math.max(height, 120) };
}
