// src/consultation/consultationStorage.js
// ============================================================================
// 배터리 상담소 localStorage 헬퍼 (Phase 1)
// ============================================================================
// Schema_version: 1
//
// 저장 구조:
//   sbtl_consult_v1: {
//     counter: 7,
//     consultations: [
//       {
//         id: 1,
//         card_id: "2026-04-16_KR_02",
//         card_meta: { title, region, date, cat, sub_cat, signal },
//         opened_at: "ISO",
//         last_active_at: "ISO",
//         messages: [
//           { role: "receipt", card_meta, opened_at },
//           { role: "assistant", content: "...", opener: true },
//           { role: "user", content: "..." },
//           ...
//         ],
//         opener_category: "kbattery",
//         opener_id_used: "kb-02",  // pool에서 inspired된 opener id (최근 배제용)
//         archived: false,
//       },
//       ...
//     ],
//     card_consultations: { "<card_id>": [1, 3, 7] },  // 역인덱스
//     schema_version: 1,
//   }
//
// 정책:
// - messages는 consultation당 최신 20턴만 유지 (초과 시 오래된 것부터 drop, archived=true).
// - card_meta는 접수 당시 snapshot. 카드 원본은 cards.json에서 card_id로 재조회.
// - counter는 유저별 단조 증가. UI 노출은 Phase 1에서 OFF (결정 4 기반).
// - quota 근접 시 오래된 consultation 통째로 drop (archive 레코드 유지, messages만 제거).
// ============================================================================

const STORAGE_KEY = "sbtl_consult_v1";
const MESSAGE_LIMIT_PER_CONSULTATION = 20;
const RECENT_OPENER_LOOKBACK = 5;
const QUOTA_SAFETY_BYTES = 4_500_000; // 5MB - safety margin

function nowISO() {
  return new Date().toISOString();
}

function emptyStore() {
  return {
    counter: 0,
    consultations: [],
    card_consultations: {},
    schema_version: 1,
  };
}

// ─── load (with validation + auto-recovery) ─────────────────────────────
function load() {
  if (typeof window === "undefined" || !window.localStorage) return emptyStore();
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return emptyStore();
    const parsed = JSON.parse(raw);

    // Schema version 체크 — 향후 migration
    if (parsed?.schema_version !== 1) {
      console.warn("[consultationStorage] schema mismatch, resetting");
      return emptyStore();
    }

    // 기본 shape 검증
    if (
      typeof parsed.counter !== "number" ||
      !Array.isArray(parsed.consultations) ||
      typeof parsed.card_consultations !== "object"
    ) {
      console.warn("[consultationStorage] shape invalid, resetting");
      return emptyStore();
    }

    // 깨진 entry 필터
    parsed.consultations = parsed.consultations.filter(
      (c) =>
        c &&
        typeof c.id === "number" &&
        typeof c.card_id === "string" &&
        c.card_id.length > 0 &&
        typeof c.opened_at === "string" &&
        Array.isArray(c.messages)
    );

    return parsed;
  } catch (e) {
    console.error("[consultationStorage] load failed", e);
    return emptyStore();
  }
}

// ─── save (with quota handling) ─────────────────────────────────────────
function save(store) {
  if (typeof window === "undefined" || !window.localStorage) return false;
  try {
    const json = JSON.stringify(store);
    if (json.length > QUOTA_SAFETY_BYTES) {
      // quota 근접 → 가장 오래된 non-archived 1개 messages drop
      const candidates = store.consultations
        .filter((c) => !c.archived && c.messages.length > 0)
        .sort((a, b) => String(a.last_active_at).localeCompare(String(b.last_active_at)));
      if (candidates.length) {
        const victim = candidates[0];
        victim.messages = [];
        victim.archived = true;
        console.warn(`[consultationStorage] quota ~${json.length}B, archived consultation #${victim.id}`);
        return save(store); // retry
      }
      // 더 잘라낼 게 없으면 실패
      console.error("[consultationStorage] quota exceeded, nothing to archive");
      return false;
    }
    window.localStorage.setItem(STORAGE_KEY, json);
    return true;
  } catch (e) {
    if (e?.name === "QuotaExceededError") {
      // 마지막 안전망 — 전체 archive-all
      console.warn("[consultationStorage] QuotaExceeded, archive-all fallback");
      store.consultations.forEach((c) => {
        c.archived = true;
        c.messages = [];
      });
      try {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
        return true;
      } catch (e2) {
        console.error("[consultationStorage] archive-all failed too", e2);
        return false;
      }
    }
    console.error("[consultationStorage] save failed", e);
    return false;
  }
}

// ─── public API ─────────────────────────────────────────────────────────

/**
 * 현재 store 반환 (read-only use).
 */
export function getStore() {
  return load();
}

/**
 * 특정 카드의 상담 summary 반환 (B안 footer hint용).
 * @returns {{count: number, latestDate: string|null}}
 */
export function getCardConsultationSummary(cardId) {
  if (!cardId) return { count: 0, latestDate: null };
  const store = load();
  const ids = store.card_consultations[cardId] || [];
  if (!ids.length) return { count: 0, latestDate: null };

  const consultations = ids
    .map((id) => store.consultations.find((c) => c.id === id))
    .filter(Boolean);

  if (!consultations.length) return { count: 0, latestDate: null };

  const sorted = [...consultations].sort((a, b) =>
    String(b.opened_at).localeCompare(String(a.opened_at))
  );
  return {
    count: consultations.length,
    latestDate: sorted[0].opened_at,
  };
}

/**
 * 모든 카드에 대한 consultation summary 맵 (뉴스 탭 렌더 시 한 번에).
 * @returns {Object<card_id, {count, latestDate}>}
 */
export function getAllCardConsultationSummaries() {
  const store = load();
  const out = {};
  for (const [cardId, ids] of Object.entries(store.card_consultations)) {
    if (!Array.isArray(ids) || !ids.length) continue;
    const consultations = ids
      .map((id) => store.consultations.find((c) => c.id === id))
      .filter(Boolean);
    if (!consultations.length) continue;
    const sorted = [...consultations].sort((a, b) =>
      String(b.opened_at).localeCompare(String(a.opened_at))
    );
    out[cardId] = {
      count: consultations.length,
      latestDate: sorted[0].opened_at,
    };
  }
  return out;
}

/**
 * 최근 사용된 opener id 목록 (few-shot 중복 배제용).
 * @param {number} limit
 * @returns {string[]}
 */
export function getRecentOpenerIds(limit = RECENT_OPENER_LOOKBACK) {
  const store = load();
  const sorted = [...store.consultations].sort((a, b) =>
    String(b.opened_at).localeCompare(String(a.opened_at))
  );
  return sorted
    .slice(0, limit)
    .map((c) => c.opener_id_used)
    .filter(Boolean);
}

/**
 * 새 consultation 생성 — counter++, record 추가, receipt message 초기 삽입.
 * @param {object} params
 * @param {object} params.card  원본 카드 (id, title, region, date, cat, sub_cat, signal 추출)
 * @param {string} params.openerCategory
 * @param {string|null} params.openerIdUsed  pool에서 영감받은 opener id (옵션, fallback 케이스)
 * @returns {{id, opened_at, card_id, card_meta}} 신규 consultation 식별자
 */
export function createConsultation({ card, openerCategory = "default", openerIdUsed = null } = {}) {
  if (!card) return null;
  const store = load();

  const cardId =
    card.id ||
    (Array.isArray(card.urls) && card.urls[0]) ||
    card.url ||
    `${card.date || ""}-${card.title || ""}`;

  const opened_at = nowISO();
  const newId = (store.counter || 0) + 1;

  const card_meta = {
    title: card.title || card.T || "",
    sub: card.sub || "",
    region: card.region || card.r || "",
    date: card.date || card.d || "",
    cat: card.cat || "",
    sub_cat: card.sub_cat || "",
    signal: card.signal || card.s || "i",
  };

  const receiptMsg = {
    role: "receipt",
    card_meta,
    opened_at,
  };

  const newConsultation = {
    id: newId,
    card_id: cardId,
    card_meta,
    opened_at,
    last_active_at: opened_at,
    messages: [receiptMsg],
    opener_category: openerCategory,
    opener_id_used: openerIdUsed,
    archived: false,
  };

  store.counter = newId;
  store.consultations.push(newConsultation);
  if (!store.card_consultations[cardId]) store.card_consultations[cardId] = [];
  store.card_consultations[cardId].push(newId);

  save(store);

  return { id: newId, opened_at, card_id: cardId, card_meta };
}

/**
 * consultation에 message append (opener/user/assistant).
 * 20턴 초과 시 오래된 것부터 trim + archived=true.
 * @param {number} consultationId
 * @param {object} message  { role, content, ...meta }
 */
export function appendMessage(consultationId, message) {
  if (typeof consultationId !== "number" || !message) return false;
  const store = load();
  const target = store.consultations.find((c) => c.id === consultationId);
  if (!target) return false;

  target.messages.push({ ...message, at: nowISO() });
  target.last_active_at = nowISO();

  if (target.messages.length > MESSAGE_LIMIT_PER_CONSULTATION) {
    // receipt는 항상 맨 앞 유지 — 이후부터 trim
    const receipt = target.messages[0]?.role === "receipt" ? target.messages.shift() : null;
    while (target.messages.length > MESSAGE_LIMIT_PER_CONSULTATION - (receipt ? 1 : 0)) {
      target.messages.shift();
    }
    if (receipt) target.messages.unshift(receipt);
    target.archived = true; // trimming 발생 표시
  }

  return save(store);
}

/**
 * Phase 2 대비 — consultation 전체 반환 (reopen용).
 * Phase 1에서는 호출자 없음, 구현만 준비.
 */
export function getConsultationById(consultationId) {
  const store = load();
  return store.consultations.find((c) => c.id === consultationId) || null;
}

/**
 * 전체 삭제 (디버깅용, UI 노출 X).
 */
export function clearAll() {
  if (typeof window === "undefined" || !window.localStorage) return;
  window.localStorage.removeItem(STORAGE_KEY);
}
