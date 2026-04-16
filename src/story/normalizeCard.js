export function getCardId(card, fallbackIndex = 0) {
  if (!card || typeof card !== 'object') return `card-${fallbackIndex}`;
  return (
    card.id ||
    card.news_id ||
    card.url ||
    (Array.isArray(card.urls) && card.urls[0]) ||
    `${getCardDate(card)}-${getCardTitle(card)}-${fallbackIndex}`
  );
}

export function getCardTitle(card) {
  return String(card?.title || card?.T || '').trim();
}

export function getCardSub(card) {
  return String(card?.sub || '').trim();
}

export function getCardFact(card) {
  return String(card?.fact || card?.summary || card?.sub || '').trim();
}

export function getCardGate(card) {
  return String(card?.gate || card?.g || card?.sub || '').trim();
}

export function getCardImplicationText(card) {
  if (Array.isArray(card?.implication)) {
    return card.implication.map((v) => String(v || '').trim()).filter(Boolean).join('\n\n');
  }
  return String(card?.implication || card?.g || '').trim();
}

export function getCardUrls(card) {
  if (Array.isArray(card?.urls)) {
    return card.urls.filter(Boolean).map((v) => String(v));
  }
  if (card?.url) return [String(card.url)];
  return [];
}

export function getCardPrimaryUrl(card) {
  return getCardUrls(card)[0] || '';
}

export function getCardSignal(card) {
  return String(card?.signal || card?.s || 'i').trim();
}

export function getCardRegion(card) {
  return String(card?.region || card?.r || 'GL').trim();
}

export function getCardDate(card) {
  return String(card?.date || card?.d || '').trim();
}

export function getCardSource(card) {
  return String(card?.source || card?.src || '').trim();
}

export function normalizeCard(card, fallbackIndex = 0) {
  return {
    id: getCardId(card, fallbackIndex),
    title: getCardTitle(card),
    sub: getCardSub(card),
    fact: getCardFact(card),
    gate: getCardGate(card),
    implicationText: getCardImplicationText(card),
    urls: getCardUrls(card),
    primaryUrl: getCardPrimaryUrl(card),
    signal: getCardSignal(card),
    region: getCardRegion(card),
    date: getCardDate(card),
    source: getCardSource(card),
    raw: card,
  };
}
