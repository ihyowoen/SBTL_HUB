export function matchesMonthlyBriefRequest(item, requested) {
  if (!item || !requested?.month) return false;
  return item.month === requested.month;
}

export function selectMonthlyBrief(items = [], requested = null, selectedId = null) {
  const safe = Array.isArray(items) ? items : [];
  if (requested?.month) {
    const exact = safe.find((item) => matchesMonthlyBriefRequest(item, requested)) || null;
    return { issue: exact, requestMissing: !exact };
  }
  return {
    issue: safe.find((item) => item?.id === selectedId) || safe[0] || null,
    requestMissing: false,
  };
}
