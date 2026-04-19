// src/story/buildCardConsultContext.js
// ============================================================================
// Card Consult Context Builder
// ============================================================================
// 배터리 상담소 재설계 Phase 1 (2026-04-19).
//
// 역할: 카드 + cards.json(전체) → LLM에 넘길 구조화된 consultation context 생성.
//
// 출력 형태 (object):
// {
//   card: <leanCard>,                        // opener/후속 답변에서 인용 가능한 주 카드
//   related_cards: [<leanRelated>, ...],     // Hybrid(수동 curation + weighted retrieve) top 2
//   opener_category: <string>,               // classifyCard 결과
//   few_shot_examples: [{id, text}, ...],    // LLM voice anchor용 few-shot
//   data_fence: { enabled: true },           // injection 방어 marker
//   schema_version: 1,                       // Phase 2 대비
// }
//
// 관련 카드 선정 로직 (결정 확정):
//   1순위: card.related 배열(수동 큐레이션). resolveExplicitRelated.
//   2순위: auto-retrieve (scoreRelated) weighted score. 3점 이상, top 2.
//   상한: 총 2개.
// ============================================================================

import { classifyCard, extractEntities, pickFewShotExamples } from './cardOpenerPool';

const DAY_MS = 24 * 60 * 60 * 1000;

// ─── 카드 simple ID 추출 (related 필드 참조용) ─────────────────────────────
function getId(card) {
  if (!card) return null;
  return card.id || null;
}

// ─── 날짜 파싱 ─────────────────────────────────────────────────────────────
// cards.json 날짜 포맷: "2026-04-16" 또는 "2026.04.16". Date 생성자로 폴백.
function parseCardDate(raw) {
  if (!raw) return null;
  const normalized = String(raw).replace(/\./g, '-').trim();
  const d = new Date(normalized);
  if (isNaN(d.getTime())) return null;
  return d;
}

// ─── time decay weight ────────────────────────────────────────────────────
function timeDecayWeight(baseDate, otherDate) {
  if (!baseDate || !otherDate) return 0;
  const diffDays = Math.abs(baseDate.getTime() - otherDate.getTime()) / DAY_MS;
  if (diffDays > 365) return null;      // cutoff
  if (diffDays <= 60) return 1.0;
  if (diffDays <= 180) return 0.5;
  return 0.25;
}

// ─── weighted score ───────────────────────────────────────────────────────
// sub_cat 겹침: 3 / entity 겹침: 3 / cat 겹침: 1 / region 겹침: 1 / time decay multiplier
// threshold 3점 이상, top 2.
function scoreRelated(baseCard, other) {
  if (!baseCard || !other) return 0;
  if (getId(baseCard) === getId(other)) return 0;

  let score = 0;

  // sub_cat 겹침 (가장 강한 시그널)
  const baseSub = String(baseCard.sub_cat || '').trim().toLowerCase();
  const otherSub = String(other.sub_cat || '').trim().toLowerCase();
  if (baseSub && otherSub && baseSub === otherSub) {
    score += 3;
  }

  // entity 겹침
  const baseEntities = extractEntities(baseCard);
  const otherEntities = extractEntities(other);
  let entityOverlap = false;
  for (const e of baseEntities) {
    if (otherEntities.has(e)) { entityOverlap = true; break; }
  }
  if (entityOverlap) score += 3;

  // cat 겹침 (약한 시그널)
  const baseCat = String(baseCard.cat || '').trim().toLowerCase();
  const otherCat = String(other.cat || '').trim().toLowerCase();
  if (baseCat && otherCat && baseCat === otherCat) {
    score += 1;
  }

  // region 겹침
  const baseRegion = String(baseCard.region || baseCard.r || '').toUpperCase();
  const otherRegion = String(other.region || other.r || '').toUpperCase();
  if (baseRegion && otherRegion && baseRegion === otherRegion) {
    score += 1;
  }

  if (score < 3) return 0;

  // time decay multiplier
  const baseDate = parseCardDate(baseCard.date || baseCard.d);
  const otherDate = parseCardDate(other.date || other.d);
  const weight = timeDecayWeight(baseDate, otherDate);
  if (weight === null) return 0;

  return score * weight;
}

// ─── Explicit related 배열 resolve ───────────────────────────────────────
function resolveExplicitRelated(card, allCards, max = 2) {
  if (!card || !Array.isArray(card.related)) return [];
  const cardsById = new Map();
  for (const c of allCards) {
    const id = getId(c);
    if (id) cardsById.set(id, c);
  }
  const out = [];
  for (const relId of card.related) {
    const relCard = cardsById.get(relId);
    if (relCard) out.push(relCard);
    if (out.length >= max) break;
  }
  return out;
}

// ─── Auto retrieve (weighted top 2) ───────────────────────────────────────
function autoRetrieveRelated(card, allCards, max = 2) {
  if (!card || !Array.isArray(allCards)) return [];
  const scored = [];
  for (const other of allCards) {
    const s = scoreRelated(card, other);
    if (s > 0) scored.push({ card: other, score: s });
  }
  scored.sort((a, b) => b.score - a.score);
  return scored.slice(0, max).map((x) => x.card);
}

// ─── Hybrid resolver ──────────────────────────────────────────────────────
function resolveRelated(card, allCards, max = 2) {
  const explicit = resolveExplicitRelated(card, allCards, max);
  if (explicit.length >= max) return explicit;
  // explicit과 중복 제거하며 auto로 채움
  const seen = new Set(explicit.map(getId));
  const auto = autoRetrieveRelated(card, allCards, max);
  for (const a of auto) {
    const id = getId(a);
    if (!seen.has(id)) {
      explicit.push(a);
      seen.add(id);
      if (explicit.length >= max) break;
    }
  }
  return explicit;
}

// ─── Lean card (LLM injection surface 축소) ───────────────────────────────
// 원본 card object를 그대로 넘기지 않고, LLM이 참조해야 할 필드만 추출.
// 출력 field 고정 → 프롬프트에서도 고정된 key만 참조하게 해 드리프트 방지.
function leanCard(card) {
  if (!card) return null;
  return {
    id: getId(card),
    title: card.title || card.T || '',
    sub: card.sub || '',
    gate: card.gate || card.g || '',
    fact: card.fact || '',
    implication: Array.isArray(card.implication)
      ? card.implication.filter(Boolean).slice(0, 3)
      : (card.implication ? [String(card.implication)] : []),
    date: card.date || card.d || '',
    region: card.region || card.r || '',
    signal: card.signal || card.s || 'i',
    cat: card.cat || '',
    sub_cat: card.sub_cat || '',
    source: card.source || card.src || '',
    primary_url: Array.isArray(card.urls) ? (card.urls[0] || '') : (card.url || ''),
  };
}

// related는 title/date/region/sub만. 인용 fidelity 유지 + injection surface 최소화.
function leanRelated(card) {
  if (!card) return null;
  return {
    id: getId(card),
    title: card.title || card.T || '',
    sub: card.sub || '',
    date: card.date || card.d || '',
    region: card.region || card.r || '',
    signal: card.signal || card.s || 'i',
  };
}

// ─── Main export ──────────────────────────────────────────────────────────
/**
 * @param {object} params
 * @param {object} params.card - 원본 카드 객체 (UI에서 선택된 것)
 * @param {object[]} params.allCards - cards.json 전체 배열 (related 및 auto-retrieve용)
 * @param {string[]} [params.recentOpenerIds=[]] - 직전 opener id 목록 (중복 배제)
 * @returns {object|null} consultation context
 */
export function buildCardConsultContext({ card, allCards = [], recentOpenerIds = [] }) {
  if (!card || !card.title) return null;

  const opener_category = classifyCard(card);
  const related = resolveRelated(card, allCards, 2);
  const few_shot_examples = pickFewShotExamples(opener_category, recentOpenerIds, 3);

  return {
    card: leanCard(card),
    related_cards: related.map(leanRelated).filter(Boolean),
    opener_category,
    few_shot_examples,
    data_fence: { enabled: true },
    schema_version: 1,
  };
}
