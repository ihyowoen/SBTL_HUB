// ============================================================================
// retrieve/comparison.js — comparison intent retrieval
// ============================================================================
// entity 2개 이상 추출해서 각각에 대한 카드를 모음. synthesize에서 LLM이 비교.
// entity 1개 이하면 일반 lexical fallback.
// ============================================================================

import { lexicalSearchCards } from "./shared.js";

// scope.entity_candidates에서 상위 N개 엔티티 추출 후 각 엔티티 별 카드 수집
function collectCardsPerEntity(cards, entities, scope, limitPerEntity = 2) {
  const perEntity = {};
  for (const e of entities) {
    const entityScope = { ...scope, entity: e, entity_candidates: [e] };
    const hits = lexicalSearchCards(cards, e, limitPerEntity, entityScope);
    if (hits.length) perEntity[e] = hits;
  }
  return perEntity;
}

export function retrieveComparison({ rawMessage, scope, data }) {
  const entities = Array.isArray(scope?.entity_candidates) ? scope.entity_candidates : [];

  if (entities.length >= 2) {
    const perEntity = collectCardsPerEntity(data?.cards || [], entities.slice(0, 3), scope || {}, 2);
    const merged = [];
    const seenUrls = new Set();
    for (const e of Object.keys(perEntity)) {
      for (const c of perEntity[e]) {
        const key = c.url || c.T;
        if (!seenUrls.has(key)) {
          seenUrls.add(key);
          merged.push(c);
        }
      }
    }
    return {
      source: "comparison",
      cards: merged.slice(0, 6),
      comparison: { entities: Object.keys(perEntity), per_entity: perEntity },
      _reasons: [`comparison_entities:${Object.keys(perEntity).length}`, `comparison_cards:${merged.length}`],
    };
  }

  // fallback: 일반 lexical 검색
  const cards = lexicalSearchCards(data?.cards || [], rawMessage, 4, scope || {});
  return {
    source: "comparison",
    cards,
    comparison: { entities: [], per_entity: {} },
    _reasons: ["comparison_insufficient_entities_fallback_lexical", `comparison_cards:${cards.length}`],
  };
}
