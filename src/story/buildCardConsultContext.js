// src/story/buildCardConsultContext.js
// ============================================================================
// 상담 접수 시 LLM에 보낼 context 객체 생성.
// ============================================================================
// 배터리 상담소 재설계 Phase 1 (2026-04-19).
// 기존 buildCardConsultPrompt.js (prompt string 반환)를 대체한다.
//
// 책임:
//   1. 카드 정규화 (lean card — LLM injection surface 최소화)
//   2. 관련 카드 해석
//      - card.related (수동 큐레이션) 우선
//      - 없으면 weighted auto-retrieve (sub_cat 3 / entity 3 / cat 1 / region 1 / time decay)
//      - 결과 0개 허용 (opener가 카드 단독으로 생성됨)
//   3. Opener category 분류 (cardOpenerPool.classifyCard)
//   4. Few-shot opener 샘플 선택 (최근 배제)
//
// 반환: API POST body의 `consultation` 필드에 들어가는 구조화 객체.
// ============================================================================

import { normalizeCard, getCardId } from './normalizeCard';
import { classifyCard, extractEntities, pickFewShotExamples } from './cardOpenerPool';

// ─── weighted retrieve 상수 ──────────────────────────────────────────
const WEIGHT_SUB_CAT = 3;
const WEIGHT_ENTITY  = 3;
const WEIGHT_CAT     = 1;
const WEIGHT_REGION  = 1;
const RELATED_THRESHOLD = 3;       // 최소 점수 (미만은 drop)
const RELATED_TOP_N     = 2;       // 최대 인접 카드 수
const RELATED_HARD_CUT_DAYS = 365; // 1년 넘으면 무조건 skip

function parseDateSafe(s) {
  if (!s) return null;
  const cleaned = String(s).replace(/\./g, '-');
  const d = new Date(cleaned);
  return isNaN(d.getTime()) ? null : d;
}

function daysBetween(a, b) {
  const da = parseDateSafe(a);
  const db = parseDateSafe(b);
  if (!da || !db) return Infinity;
  return Math.abs((da.getTime() - db.getTime()) / (1000 * 60 * 60 * 24));
}

function timeDecay(days) {
  if (days <= 60) return 1.0;
  if (days <= 180) return 0.5;
  return 0.2;
}

// ─── weighted score 계산 ──────────────────────────────────────────────
// 각 후보 카드에 대해 anchor 카드 대비 연관도 점수 매김.
function scoreRelated(anchorCard, pool) {
  const anchorId = getCardId(anchorCard);
  const anchorEntities = extractEntities(anchorCard);
  const anchorCat      = String(anchorCard?.cat || '').toLowerCase();
  const anchorSubCat   = String(anchorCard?.sub_cat || '').toLowerCase();
  const anchorRegion   = String(anchorCard?.region || anchorCard?.r || '').toUpperCase();
  const anchorDate     = anchorCard?.date || anchorCard?.d;

  const scored = [];
  for (const candidate of pool) {
    if (!candidate) continue;
    const candId = getCardId(candidate);
    if (candId === anchorId) continue;

    const candDate = candidate.date || candidate.d;
    if (anchorDate && candDate) {
      const days = daysBetween(anchorDate, candDate);
      if (days > RELATED_HARD_CUT_DAYS) continue;  // 1년 이상 차이 → skip
    }

    let score = 0;
    const candCat      = String(candidate.cat || '').toLowerCase();
    const candSubCat   = String(candidate.sub_cat || '').toLowerCase();
    const candRegion   = String(candidate.region || candidate.r || '').toUpperCase();
    const candEntities = extractEntities(candidate);

    if (anchorSubCat && candSubCat && anchorSubCat === candSubCat) score += WEIGHT_SUB_CAT;
    if (anchorCat    && candCat    && anchorCat    === candCat)    score += WEIGHT_CAT;
    if (anchorRegion && candRegion && anchorRegion === candRegion) score += WEIGHT_REGION;

    // entity 겹침 — 하나라도 겹치면 점수 (누적 아님, 존재 기반)
    const entityOverlap = [...anchorEntities].some((e) => candEntities.has(e));
    if (entityOverlap) score += WEIGHT_ENTITY;

    // time decay 적용
    if (anchorDate && candDate) {
      const days = daysBetween(anchorDate, candDate);
      score = score * timeDecay(days);
    }

    if (score >= RELATED_THRESHOLD) {
      scored.push({ card: candidate, score, id: candId });
    }
  }

  scored.sort((a, b) => b.score - a.score);
  return scored.slice(0, RELATED_TOP_N).map((x) => x.card);
}

// ─── card.related (수동 큐레이션) 해석 ────────────────────────────────────
function resolveExplicitRelated(card, allCards = []) {
  const relatedIds = Array.isArray(card?.related) ? card.related : [];
  if (!relatedIds.length) return [];
  const byId = new Map(allCards.map((c) => [getCardId(c), c]));
  return relatedIds
    .map((id) => byId.get(id))
    .filter(Boolean)
    .slice(0, RELATED_TOP_N);
}

// ─── Hybrid resolver ──────────────────────────────────────────────────────
// 1) card.related 우선 (수동 큐레이션 — cards.json 9.5% 커버, 품질 최고)
// 2) 비어있으면 weighted auto-retrieve
// 3) 결과 0개도 허용 (opener가 카드 단독 생성)
function resolveRelatedCards(card, allCards) {
  const explicit = resolveExplicitRelated(card, allCards);
  if (explicit.length) return explicit;
  return scoreRelated(card, allCards);
}

// ─── lean card (LLM 주입용) ──────────────────────────────────────────────
// injection surface 최소화를 위해 필요한 필드만. 원본 카드 전체를 LLM에 보내지 않음.
function leanCard(card) {
  if (!card) return null;
  const n = normalizeCard(card);
  return {
    id: getCardId(card),
    title: n.title,
    sub: n.sub,
    gate: card.gate || n.gate || '',
    fact: card.fact || '',
    implication: Array.isArray(card.implication)
      ? card.implication.filter(Boolean).map(String)
      : (card.implication ? [String(card.implication)] : []),
    cat: card.cat || '',
    sub_cat: card.sub_cat || '',
    region: n.region,
    date: n.date,
    signal: n.signal,
    source: n.source,
    source_tier: Number.isFinite(card.source_tier) ? card.source_tier : 2,
    primary_url: n.primaryUrl,
  };
}

// 관련 카드는 메타만 (본문 제외 — prompt 길이 절약 + injection surface 축소)
function leanRelated(card) {
  if (!card) return null;
  const n = normalizeCard(card);
  return {
    id: getCardId(card),
    title: n.title,
    sub: n.sub,
    cat: card.cat || '',
    sub_cat: card.sub_cat || '',
    region: n.region,
    date: n.date,
  };
}

// ============================================================================
// Main entry — 상담 접수 context 생성
// ============================================================================
/**
 * @param {object} opts
 * @param {object} opts.card            유저가 접수한 카드 (필수)
 * @param {Array}  opts.allCards        cards.json 전체 (related 해석용). 빈 배열 OK.
 * @param {Array}  opts.recentOpenerIds 최근 사용된 opener id (localStorage에서 공급). 배제용.
 * @returns {object|null} consultation context — POST body의 `consultation` 필드로 전달
 */
export function buildCardConsultContext({ card, allCards = [], recentOpenerIds = [] } = {}) {
  if (!card) return null;

  const category = classifyCard(card);
  const relatedCards = resolveRelatedCards(card, allCards);
  const fewShotExamples = pickFewShotExamples(category, recentOpenerIds, 3);

  return {
    card: leanCard(card),
    related_cards: relatedCards.map(leanRelated).filter(Boolean),
    opener_category: category,
    few_shot_examples: fewShotExamples,
    // data_fence: llm.js synthesizeCardConsult가 prompt 조립 시 데이터 영역에 fence 씨움
    data_fence: { enabled: true },
    // schema versioning — Phase 2에서 스키마 변경 시 migration
    schema_version: 1,
  };
}
